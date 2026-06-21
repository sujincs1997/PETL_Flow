# Automatically generated Custom Node. Do not edit.
from .base import BaseNode, NodeParameter, PortMetadata
from .registry import register_node
import pandas as pd
import geopandas as gpd

@register_node
class tester1(BaseNode):
    type = "tester1"
    name = "tester"
    category = "Transformations"
    description = ""
    
    parameters_schema = [
        NodeParameter(name='Uservalue', label='U1', type='str', default=None, required=True)
    ]
    
    inputs_schema = [
        PortMetadata(name="input", label="Input DataFrame", type="any")
    ]
    outputs_schema = [
        PortMetadata(name="output", label="Output DataFrame", type="any")
    ]

    def execute(self, input_data: dict) -> dict:
        input_df = input_data.get("input")
        # --- Start User Executable Code ---
        # input_df is loaded automatically
        # Write your code here and store the result in output_df
        output_df = input_df.copy()
        # --- End User Executable Code ---
        if 'output_df' not in locals() and 'output_df' not in globals():
            raise ValueError("Your custom script must assign results to the 'output_df' variable.")
        return {"output": locals().get('output_df')}
