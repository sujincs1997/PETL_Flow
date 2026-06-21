import pandas as pd
import geopandas as gpd
from typing import Dict, Any
from .base import BaseNode, NodeParameter, PortMetadata
from .registry import register_node

@register_node
class AttributeFilter(BaseNode):
    type = "AttributeFilter"
    name = "Attribute Filter"
    category = "Transformations"
    description = "Filters a DataFrame based on a query expression."
    
    parameters_schema = [
        NodeParameter(
            name="query",
            label="Filter Query",
            type="str",
            required=True,
            description="Pandas query string, e.g. age > 30 and city == 'Boston'"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="Input", type="any")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Filtered Output", type="any")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        df = input_data.get("input")
        if df is None:
            raise ValueError("Input data missing.")
            
        query = self.params["query"]
        filtered_df = df.query(query)
        
        # Preserve GeoDataFrame class if relevant
        if isinstance(df, gpd.GeoDataFrame):
            filtered_df = gpd.GeoDataFrame(filtered_df, geometry=df.geometry.name, crs=df.crs)
            
        return {"output": filtered_df}


@register_node
class JoinNode(BaseNode):
    type = "JoinNode"
    name = "Tabular Join"
    category = "Transformations"
    description = "Performs an inner, left, right, or outer join on two DataFrames."
    
    parameters_schema = [
        NodeParameter(
            name="how",
            label="Join Type",
            type="select",
            default="left",
            options=["left", "right", "inner", "outer"],
            required=True
        ),
        NodeParameter(
            name="left_on",
            label="Left Key Column",
            type="str",
            required=True
        ),
        NodeParameter(
            name="right_on",
            label="Right Key Column",
            type="str",
            required=True
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="left", label="Left Input", type="pandas"),
        PortMetadata(name="right", label="Right Input", type="pandas")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Joined Output", type="pandas")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        df_left = input_data.get("left")
        df_right = input_data.get("right")
        
        if df_left is None or df_right is None:
            raise ValueError("Both 'left' and 'right' inputs must be connected.")
            
        how = self.params["how"]
        left_on = self.params["left_on"]
        right_on = self.params["right_on"]
        
        joined = pd.merge(df_left, df_right, how=how, left_on=left_on, right_on=right_on)
        return {"output": joined}


@register_node
class RenameColumns(BaseNode):
    type = "RenameColumns"
    name = "Rename Columns"
    category = "Transformations"
    description = "Renames specific columns of a DataFrame."
    
    parameters_schema = [
        NodeParameter(
            name="mapping",
            label="Columns Mapping",
            type="str",
            required=True,
            description="JSON object mapping old to new names, e.g. {'old_col': 'new_col'}"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="Input", type="any")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Renamed Output", type="any")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        df = input_data.get("input")
        if df is None:
            raise ValueError("Input data missing.")
            
        import json
        mapping_str = self.params["mapping"]
        try:
            mapping = json.loads(mapping_str.replace("'", '"'))
        except Exception as e:
            raise ValueError(f"Invalid column mapping JSON format: {e}")
            
        renamed_df = df.rename(columns=mapping)
        if isinstance(df, gpd.GeoDataFrame):
            renamed_df = gpd.GeoDataFrame(renamed_df, geometry=df.geometry.name, crs=df.crs)
            
        return {"output": renamed_df}


@register_node
class PythonScriptNode(BaseNode):
    type = "PythonScriptNode"
    name = "Python Script"
    category = "Transformations"
    description = "Executes custom Python code on the inputs. Use 'inputs_dict' to read inputs and write results to 'outputs_dict'."
    
    parameters_schema = [
        NodeParameter(
            name="code",
            label="Python Code",
            type="python",
            default="# Read inputs from inputs_dict['port_name']\n# Write results to outputs_dict['port_name']\nif 'input' in inputs_dict:\n    outputs_dict['output'] = inputs_dict['input'].copy()\n",
            required=True
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="Input", type="any")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Script Output", type="any")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        code_str = self.params["code"]
        
        # Execution environment variables
        local_vars = {
            "inputs_dict": input_data,
            "outputs_dict": {},
            "pd": pd,
            "gpd": gpd
        }
        
        # Backwards compatibility
        if "input" in input_data:
            local_vars["input_df"] = input_data["input"]
        local_vars["output_df"] = None
        
        # Run code safely in local scope
        exec(code_str, {}, local_vars)
        
        outputs = local_vars.get("outputs_dict", {})
        
        # Backwards compatibility fallback
        if not outputs and local_vars.get("output_df") is not None:
            outputs["output"] = local_vars["output_df"]
            
        return outputs


@register_node
class AttributeCreator(BaseNode):
    type = "AttributeCreator"
    name = "Attribute Creator"
    category = "Transformations"
    description = "Adds new attributes or updates existing attributes with constant values or python expressions."
    
    parameters_schema = [
        NodeParameter(
            name="attributes",
            label="Attributes (JSON)",
            type="str",
            default='{"new_column": 10, "label": "\'Region: \' + name"}',
            required=True,
            description="JSON object mapping attribute names to constant values or Python expressions. Example: {\"new_col\": 10, \"label\": \"'Region: ' + name\"}"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="Input", type="any")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Output", type="any")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        df = input_data.get("input")
        if df is None:
            raise ValueError("Input data missing.")
            
        import ast
        attr_str = self.params["attributes"]
        try:
            attr_dict = ast.literal_eval(attr_str)
        except Exception as e:
            raise ValueError(f"Invalid attributes dictionary format: {e}")
            
        out_df = df.copy()
        for col_name, expr in attr_dict.items():
            if not isinstance(expr, str):
                out_df[col_name] = expr
            else:
                if (expr.startswith("'") and expr.endswith("'")) or (expr.startswith('"') and expr.endswith('"')):
                    out_df[col_name] = expr[1:-1]
                else:
                    try:
                        out_df[col_name] = out_df.eval(expr)
                    except Exception:
                        def eval_row(row):
                            row_dict = row.to_dict()
                            try:
                                return eval(expr, {}, row_dict)
                            except Exception:
                                return None
                        out_df[col_name] = out_df.apply(eval_row, axis=1)
                        
        if isinstance(df, gpd.GeoDataFrame):
            out_df = gpd.GeoDataFrame(out_df, geometry=df.geometry.name, crs=df.crs)
            
        return {"output": out_df}


@register_node
class FeatureMergerNode(BaseNode):
    type = "FeatureMergerNode"
    name = "Feature Merger"
    category = "Transformations"
    description = "Merges attributes from a Supplier to a Requestor based on a common key, splitting outputs by success."
    
    parameters_schema = [
        NodeParameter(
            name="join_on",
            label="Join Key Column",
            type="str",
            required=True,
            description="Column name that exists in both Requestor and Supplier"
        )
    ]
    
    inputs_schema = [
        PortMetadata(name="requestor", label="Requestor", type="any"),
        PortMetadata(name="supplier", label="Supplier", type="any")
    ]
    
    outputs_schema = [
        PortMetadata(name="merged", label="Merged", type="any"),
        PortMetadata(name="unmerged_requestor", label="Unmerged Requestor", type="any")
    ]

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        req_df = input_data.get("requestor")
        sup_df = input_data.get("supplier")
        
        if req_df is None:
            raise ValueError("FeatureMerger requires at least the 'requestor' input.")
            
        if sup_df is None:
            # If no supplier, everything is unmerged
            return {"merged": None, "unmerged_requestor": req_df}
            
        join_on = self.params["join_on"]
        
        # We do a left join with an indicator to separate merged from unmerged
        merged_all = pd.merge(req_df, sup_df, on=join_on, how="left", indicator=True)
        
        merged = merged_all[merged_all['_merge'] == 'both'].drop(columns=['_merge'])
        unmerged = merged_all[merged_all['_merge'] == 'left_only'].drop(columns=['_merge'])
        
        # Preserve GeoDataFrame if the original requestor was a GeoDataFrame
        if isinstance(req_df, gpd.GeoDataFrame):
            merged = gpd.GeoDataFrame(merged, geometry=req_df.geometry.name, crs=req_df.crs)
            unmerged = gpd.GeoDataFrame(unmerged, geometry=req_df.geometry.name, crs=req_df.crs)
            
        return {
            "merged": merged if not merged.empty else None,
            "unmerged_requestor": unmerged if not unmerged.empty else None
        }

