import geopandas as gpd
from typing import Dict, Any
from .base import BaseNode, NodeParameter, PortMetadata
from .registry import register_node
from shapely.validation import make_valid

@register_node
class CoordinateConverter(BaseNode):
    type = "CoordinateConverter"
    name = "Coordinate Converter"
    category = "GIS"
    description = "Reprojects a GeoDataFrame to a new coordinate reference system (CRS)."
    
    parameters_schema = [
        NodeParameter(
            name="target_crs",
            label="Target CRS (EPSG)",
            type="str",
            default="EPSG:4326",
            required=True,
            description="Target projection EPSG string, e.g. EPSG:3857, EPSG:4326 or UTM EPSG code"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Projected GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame is missing.")
            
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame to perform coordinate conversion.")
            
        target = self.params["target_crs"]
        
        # If the input doesn't have a CRS set, default to EPSG:4326 first
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
            
        projected = gdf.to_crs(target)
        return {"output": projected}


@register_node
class BufferNode(BaseNode):
    type = "BufferNode"
    name = "Spatial Buffer"
    category = "GIS"
    description = "Creates a buffer area around each geometry by a given distance."
    
    parameters_schema = [
        NodeParameter(
            name="distance",
            label="Buffer Distance",
            type="float",
            default=100.0,
            required=True,
            description="Distance in CRS units (meters for projected, degrees for geographic)"
        ),
        NodeParameter(
            name="single_geometry",
            label="Resolve as Single Geometry",
            type="bool",
            default=False,
            required=False,
            description="Dissolves buffers into a single union geometry"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Buffered GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame is missing.")
            
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame to perform buffer operations.")
            
        distance = self.params["distance"]
        single_geom = self.params["single_geometry"]
        
        buffered_gdf = gdf.copy()
        
        # Geopandas buffer returns a Series of geometries
        buffered_gdf[gdf.geometry.name] = gdf.geometry.buffer(distance)
        
        if single_geom:
            union_geom = buffered_gdf.geometry.unary_union
            buffered_gdf = gpd.GeoDataFrame(geometry=[union_geom], crs=gdf.crs)
            
        return {"output": buffered_gdf}


@register_node
class SpatialJoinNode(BaseNode):
    type = "SpatialJoinNode"
    name = "Spatial Join"
    category = "GIS"
    description = "Merges attributes of two GeoDataFrames based on their spatial relationship."
    
    parameters_schema = [
        NodeParameter(
            name="how",
            label="Join Operation",
            type="select",
            default="inner",
            options=["inner", "left", "right"],
            required=True
        ),
        NodeParameter(
            name="predicate",
            label="Spatial Predicate",
            type="select",
            default="intersects",
            options=["intersects", "within", "contains", "touches", "crosses", "overlaps"],
            required=True
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="left", label="Left GeoDataFrame", type="geopandas"),
        PortMetadata(name="right", label="Right GeoDataFrame", type="geopandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Joined GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf_left = input_data.get("left")
        gdf_right = input_data.get("right")
        
        if gdf_left is None or gdf_right is None:
            raise ValueError("Both 'left' and 'right' inputs must be connected.")
            
        if not isinstance(gdf_left, gpd.GeoDataFrame) or not isinstance(gdf_right, gpd.GeoDataFrame):
            raise TypeError("Both inputs must be GeoDataFrames for a spatial join.")
            
        how = self.params["how"]
        pred = self.params["predicate"]
        
        # Ensure alignment of CRS
        if gdf_left.crs != gdf_right.crs:
            gdf_right = gdf_right.to_crs(gdf_left.crs)
            
        joined = gpd.sjoin(gdf_left, gdf_right, how=how, predicate=pred)
        return {"output": joined}


@register_node
class PolygonCentroidNode(BaseNode):
    type = "PolygonCentroidNode"
    name = "Polygon Centroid"
    category = "GIS"
    description = "Calculates the center point (centroid) of polygon geometries."
    
    parameters_schema = []
    
    inputs_schema = [
        PortMetadata(name="input", label="Polygon GeoDataFrame", type="geopandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Centroid GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame is missing.")
            
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame to extract centroids.")
            
        centroids_gdf = gdf.copy()
        centroids_gdf[gdf.geometry.name] = gdf.geometry.centroid
        return {"output": centroids_gdf}


@register_node
class GeometryValidatorNode(BaseNode):
    type = "GeometryValidatorNode"
    name = "Geometry Validator"
    category = "GIS"
    description = "Checks geometry validity and repairs invalid geometries."
    
    parameters_schema = [
        NodeParameter(
            name="auto_repair",
            label="Auto Repair Invalid",
            type="bool",
            default=True,
            required=False
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="GeoDataFrame", type="geopandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Validated GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        gdf = input_data.get("input")
        if gdf is None:
            raise ValueError("Input GeoDataFrame is missing.")
            
        repair = self.params["auto_repair"]
        out_gdf = gdf.copy()
        
        if repair:
            out_gdf[gdf.geometry.name] = out_gdf.geometry.apply(lambda g: make_valid(g) if g and not g.is_valid else g)
        else:
            invalid_mask = ~out_gdf.geometry.is_valid
            if invalid_mask.any():
                raise ValueError(f"Found {invalid_mask.sum()} invalid geometries in input.")
                
        return {"output": out_gdf}


@register_node
class PointCreatorNode(BaseNode):
    type = "PointCreatorNode"
    name = "Create Points from XY"
    category = "GIS"
    description = "Converts coordinates (X/Y or Longitude/Latitude) from a DataFrame into Point geometries."
    
    parameters_schema = [
        NodeParameter(
            name="longitude_col",
            label="Longitude Column (X)",
            type="str",
            default="longitude",
            required=True
        ),
        NodeParameter(
            name="latitude_col",
            label="Latitude Column (Y)",
            type="str",
            default="latitude",
            required=True
        ),
        NodeParameter(
            name="crs",
            label="Coordinate Reference System (CRS)",
            type="str",
            default="EPSG:4326",
            required=True
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="DataFrame", type="pandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        df = input_data.get("input")
        if df is None:
            raise ValueError("Input DataFrame is missing.")
            
        lon_col = self.params["longitude_col"]
        lat_col = self.params["latitude_col"]
        crs_str = self.params["crs"]
        
        if lon_col not in df.columns or lat_col not in df.columns:
            raise ValueError(f"Longitude ({lon_col}) or Latitude ({lat_col}) column missing from input. Available: {list(df.columns)}")
            
        geom = gpd.points_from_xy(df[lon_col], df[lat_col])
        gdf = gpd.GeoDataFrame(df, geometry=geom, crs=crs_str)
        return {"output": gdf}


@register_node
class SpatialRelator(BaseNode):
    type = "SpatialRelator"
    name = "Spatial Relator"
    category = "GIS"
    description = "Determines spatial relationships between Base features and Candidate features, outputting base features with relationship count and match status."
    
    parameters_schema = [
        NodeParameter(
            name="spatial_relation",
            label="Spatial Relation",
            type="select",
            default="intersects",
            options=["intersects", "contains", "within", "touches", "crosses", "overlaps", "equals", "disjoint"],
            required=True
        ),
        NodeParameter(
            name="count_attribute",
            label="Count Attribute",
            type="str",
            default="_related_count",
            required=True,
            description="Attribute name to store the count of candidate matches"
        ),
        NodeParameter(
            name="matched_attribute",
            label="Matched Attribute",
            type="str",
            default="_matched",
            required=True,
            description="Attribute name to store the boolean match status"
        ),
        NodeParameter(
            name="candidate_attribute",
            label="Candidate Attribute to Carry",
            type="str",
            default="",
            required=False,
            description="Optional candidate column name to aggregate/carry over"
        ),
        NodeParameter(
            name="candidate_attribute_agg",
            label="Candidate Attribute Aggregation",
            type="select",
            default="first",
            options=["first", "list", "sum", "mean"],
            required=False,
            description="Method to aggregate candidate attribute (only active if Candidate Attribute is set)"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="base", label="Base GeoDataFrame", type="geopandas"),
        PortMetadata(name="candidate", label="Candidate GeoDataFrame", type="geopandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Related GeoDataFrame", type="geopandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        base_gdf = input_data.get("base")
        candidate_gdf = input_data.get("candidate")
        
        if base_gdf is None or candidate_gdf is None:
            raise ValueError("Both 'base' and 'candidate' inputs must be connected.")
            
        if not isinstance(base_gdf, gpd.GeoDataFrame) or not isinstance(candidate_gdf, gpd.GeoDataFrame):
            raise TypeError("Both inputs must be GeoDataFrames for spatial relation checking.")
            
        relation = self.params["spatial_relation"]
        count_attr = self.params["count_attribute"]
        matched_attr = self.params["matched_attribute"]
        candidate_attr = self.params.get("candidate_attribute", "")
        agg_method = self.params.get("candidate_attribute_agg", "first")
        
        # Ensure CRS matches
        if base_gdf.crs != candidate_gdf.crs:
            candidate_gdf = candidate_gdf.to_crs(base_gdf.crs)
            
        out_gdf = base_gdf.copy()
        
        # Save the original index name/type
        original_index = out_gdf.index.copy()
        original_index_name = out_gdf.index.name
        
        # Use a temporary sequential index to avoid issues with non-unique or custom indices during merge
        out_gdf = out_gdf.reset_index(drop=True)
        out_gdf.index.name = "_base_index_temp"
        base_reset = out_gdf.reset_index()
        
        # Perform left spatial join
        joined = gpd.sjoin(base_reset, candidate_gdf, how="left", predicate=relation)
        
        # Group by the temporary index
        grouped = joined.groupby("_base_index_temp")
        
        # Calculate count of candidate matches
        match_counts = grouped["index_right"].count()
        
        # Map counts and boolean flags back to out_gdf
        out_gdf[count_attr] = out_gdf.index.map(match_counts).fillna(0).astype(int)
        out_gdf[matched_attr] = out_gdf[count_attr] > 0
        
        # Optionally carry over candidate attribute
        if candidate_attr and candidate_attr in candidate_gdf.columns:
            if agg_method == "list":
                agg_values = grouped[candidate_attr].apply(lambda x: [v for v in x.dropna().unique()])
            elif agg_method == "sum":
                agg_values = grouped[candidate_attr].sum()
            elif agg_method == "mean":
                agg_values = grouped[candidate_attr].mean()
            else:  # "first"
                agg_values = grouped[candidate_attr].first()
                
            out_gdf[f"_candidate_{candidate_attr}"] = out_gdf.index.map(agg_values)
            
        # Restore the original index
        out_gdf.index = original_index
        out_gdf.index.name = original_index_name
        
        return {"output": out_gdf}


