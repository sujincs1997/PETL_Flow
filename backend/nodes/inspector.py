import json
import os
import pandas as pd
import geopandas as gpd
import numpy as np
from typing import Dict, Any, List
from .base import BaseNode, NodeParameter, PortMetadata
from .registry import register_node
from ..config import settings


@register_node
class InspectorNode(BaseNode):
    """
    FME-style Inspector Node.
    Intercepts data flowing through the pipeline, produces a rich analysis
    report (schema, geometry info, statistics, null analysis, sample rows),
    saves it as JSON, and passes data through unchanged.
    """
    type = "InspectorNode"
    name = "Inspector"
    category = "Quality"
    description = (
        "Inspects data flowing through the pipeline without modifying it. "
        "Produces a detailed report including schema, geometry info, "
        "statistics, null analysis, and sample data rows. "
        "Similar to the Inspector transformer in FME."
    )

    parameters_schema = [
        NodeParameter(
            name="report_label",
            label="Report Label",
            type="str",
            default="Inspection Report",
            required=False,
            description="Custom label for the inspection report"
        ),
        NodeParameter(
            name="sample_rows",
            label="Sample Rows",
            type="int",
            default=10,
            required=False,
            description="Number of sample rows to include in the report (head)"
        ),
        NodeParameter(
            name="include_statistics",
            label="Include Statistics",
            type="bool",
            default=True,
            required=False,
            description="Whether to compute column-level statistics"
        ),
    ]

    inputs_schema = [
        PortMetadata(name="input", label="Input Data", type="any")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Output Data (Passthrough)", type="any")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        df = input_data.get("input")
        if df is None:
            raise ValueError("Inspector: No data received on 'input' port.")

        report = self._build_report(df)

        # Save report as JSON to intermediate cache
        self._save_report(report)

        # Passthrough — return data unchanged
        return {"output": df}

    def _build_report(self, df: Any) -> Dict[str, Any]:
        """Build a comprehensive inspection report."""
        report: Dict[str, Any] = {
            "label": self.params.get("report_label", "Inspection Report"),
            "node_id": self.id,
        }

        is_geodf = isinstance(df, gpd.GeoDataFrame)
        sample_rows = max(1, int(self.params.get("sample_rows", 10)))
        include_stats = self.params.get("include_statistics", True)

        # --- Overview ---
        memory_bytes = df.memory_usage(deep=True).sum()
        report["overview"] = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage_mb": round(memory_bytes / (1024 * 1024), 3),
            "is_geodataframe": is_geodf,
            "data_type": "GeoDataFrame" if is_geodf else "DataFrame",
        }

        # --- Schema ---
        schema_entries = []
        for col in df.columns:
            non_null = int(df[col].notna().sum())
            null_count = int(df[col].isna().sum())
            total = len(df)
            schema_entries.append({
                "column": col,
                "dtype": str(df[col].dtype),
                "non_null_count": non_null,
                "null_count": null_count,
                "null_pct": round((null_count / total) * 100, 2) if total > 0 else 0.0,
            })
        report["schema"] = schema_entries

        # --- Geometry Info (GeoDataFrame only) ---
        if is_geodf:
            report["geometry"] = self._analyze_geometry(df)
        else:
            report["geometry"] = None

        # --- Statistics ---
        if include_stats:
            report["statistics"] = self._compute_statistics(df, is_geodf)
        else:
            report["statistics"] = None

        # --- Sample Data ---
        report["sample_data"] = self._get_sample_data(df, sample_rows, is_geodf)

        return report

    def _analyze_geometry(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Analyze geometry column of a GeoDataFrame."""
        geom_info: Dict[str, Any] = {}

        geom_col = gdf.geometry.name if gdf.geometry is not None else None
        geom_info["geometry_column"] = geom_col

        # CRS
        crs = gdf.crs
        if crs:
            geom_info["crs"] = str(crs)
            geom_info["crs_name"] = crs.name if hasattr(crs, 'name') else str(crs)
            try:
                geom_info["crs_epsg"] = crs.to_epsg()
            except Exception:
                geom_info["crs_epsg"] = None
        else:
            geom_info["crs"] = None
            geom_info["crs_name"] = None
            geom_info["crs_epsg"] = None

        # Geometry types
        if geom_col and geom_col in gdf.columns:
            geom_series = gdf[geom_col]
            valid_geom = geom_series.dropna()

            geom_types = valid_geom.geom_type.value_counts().to_dict()
            geom_info["geometry_types"] = {str(k): int(v) for k, v in geom_types.items()}
            geom_info["total_with_geometry"] = int(len(valid_geom))
            geom_info["empty_geometry_count"] = int(valid_geom.is_empty.sum())

            # Bounding box
            try:
                bounds = valid_geom.total_bounds  # [minx, miny, maxx, maxy]
                geom_info["bounding_box"] = {
                    "minx": _safe_float(bounds[0]),
                    "miny": _safe_float(bounds[1]),
                    "maxx": _safe_float(bounds[2]),
                    "maxy": _safe_float(bounds[3]),
                }
            except Exception:
                geom_info["bounding_box"] = None
        else:
            geom_info["geometry_types"] = {}
            geom_info["total_with_geometry"] = 0
            geom_info["empty_geometry_count"] = 0
            geom_info["bounding_box"] = None

        return geom_info

    def _compute_statistics(self, df: Any, is_geodf: bool) -> Dict[str, Any]:
        """Compute per-column statistics."""
        stats: Dict[str, Any] = {"numeric": [], "categorical": []}

        # Exclude geometry column from stats
        columns = [c for c in df.columns if not (is_geodf and c == df.geometry.name)]

        for col in columns:
            series = df[col]

            if pd.api.types.is_numeric_dtype(series):
                desc = series.describe()
                stats["numeric"].append({
                    "column": col,
                    "min": _safe_float(desc.get("min")),
                    "max": _safe_float(desc.get("max")),
                    "mean": _safe_float(desc.get("mean")),
                    "std": _safe_float(desc.get("std")),
                    "median": _safe_float(series.median()),
                    "25th_pct": _safe_float(desc.get("25%")),
                    "75th_pct": _safe_float(desc.get("75%")),
                })
            elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
                unique_count = int(series.nunique())
                top_values = (
                    series.value_counts()
                    .head(5)
                    .to_dict()
                )
                stats["categorical"].append({
                    "column": col,
                    "unique_count": unique_count,
                    "top_values": {str(k): int(v) for k, v in top_values.items()},
                })

        return stats

    def _get_sample_data(self, df: Any, n: int, is_geodf: bool) -> Dict[str, Any]:
        """Get head and tail sample rows."""
        # Convert geometry to WKT for JSON serialization
        sample_df = df.copy()
        if is_geodf and sample_df.geometry is not None:
            geom_col = sample_df.geometry.name
            if geom_col in sample_df.columns:
                # Avoid pandas apply on GeoSeries to prevent NumPy 2.0 copy=False ValueError
                wkt_geoms = []
                for g in sample_df[geom_col]:
                    wkt_geoms.append(g.wkt if getattr(g, 'is_empty', False) is False and g is not None else None)
                sample_df[geom_col] = wkt_geoms
                sample_df = pd.DataFrame(sample_df)

        head_rows = sample_df.head(n)
        tail_n = min(5, len(df))
        tail_rows = sample_df.tail(tail_n)

        return {
            "head": _df_to_json_records(head_rows),
            "tail": _df_to_json_records(tail_rows),
            "columns": list(df.columns),
        }

    def _save_report(self, report: Dict[str, Any]):
        """Save the inspection report JSON to the intermediate storage directory."""
        # The execution engine sets an environment variable or we use a convention:
        # The report is saved to {INTERMEDIATE_STORAGE_PATH}/{execution_id}/{node_key}_inspection.json
        # We use the node_id which is the node_key from the workflow
        exec_id = os.environ.get("ETL_EXECUTION_ID", "unknown")
        directory = os.path.join(settings.INTERMEDIATE_STORAGE_PATH, exec_id)
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{self.id}_inspection.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)


def _safe_float(val: Any) -> Any:
    """Convert numpy/pandas numeric types to Python float, handling NaN/Inf."""
    if val is None:
        return None
    try:
        fval = float(val)
        if np.isnan(fval) or np.isinf(fval):
            return None
        return round(fval, 6)
    except (TypeError, ValueError):
        return None


def _df_to_json_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert a DataFrame to a list of JSON-serializable dicts."""
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                record[col] = None
            elif isinstance(val, (np.integer,)):
                record[col] = int(val)
            elif isinstance(val, (np.floating,)):
                record[col] = float(val)
            elif isinstance(val, np.bool_):
                record[col] = bool(val)
            else:
                record[col] = str(val) if not isinstance(val, (str, int, float, bool)) else val
        records.append(record)
    return records
