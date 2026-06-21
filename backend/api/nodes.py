import os
import importlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.auth import RoleChecker
from backend.schemas.workflow import CustomNodeBuilderSchema
from backend.nodes.registry import NodeRegistry
from typing import List, Dict, Any

router = APIRouter(prefix="/nodes", tags=["nodes"])

check_developer_or_above = RoleChecker(["Admin", "Developer"])
check_viewer_or_above = RoleChecker(["Admin", "Developer", "Analyst", "Viewer"])

@router.get("", response_model=List[Dict[str, Any]])
def list_available_nodes(current_user: Any = Depends(check_viewer_or_above)):
    """List all registered ETL and GIS nodes metadata for UI canvas generation."""
    nodes = NodeRegistry.list_nodes()
    return [node.get_metadata().dict() for node in nodes]


@router.post("/custom", status_code=status.HTTP_201_CREATED)
def create_custom_node(
    payload: CustomNodeBuilderSchema,
    current_user: Any = Depends(check_developer_or_above)
):
    """
    Code Generator Endpoint.
    Automatically generates a Python class file from visual designer configuration,
    saves it, and registers it dynamically in the execution engine.
    """
    type_name = payload.type
    name = payload.name
    category = payload.category
    desc = payload.description
    user_code = payload.code

    # Build Pydantic NodeParameter strings
    params_str_list = []
    for param in payload.parameters:
        p_name = param.get("name")
        p_label = param.get("label", p_name)
        p_type = param.get("type", "str")
        p_default = param.get("default", None)
        p_req = param.get("required", True)
        
        default_val = f"'{p_default}'" if isinstance(p_default, str) else str(p_default)
        if p_default is None:
            default_val = "None"
            
        params_str_list.append(
            f"        NodeParameter(name='{p_name}', label='{p_label}', type='{p_type}', default={default_val}, required={str(p_req)})"
        )
    
    params_code_block = ",\n".join(params_str_list)

    # Build input/output port metadata strings
    inputs_str_list = [f'        PortMetadata(name="{i}", label="{i}", type="any")' for i in payload.inputs]
    outputs_str_list = [f'        PortMetadata(name="{o}", label="{o}", type="any")' for o in payload.outputs]
    
    inputs_code_block = ",\n".join(inputs_str_list) if inputs_str_list else ""
    outputs_code_block = ",\n".join(outputs_str_list) if outputs_str_list else ""

    # Clean indentation for user execution body
    indented_user_code = "\n".join([f"        {line}" for line in user_code.splitlines()])

    # Node template file contents
    template = f"""# Automatically generated Custom Node. Do not edit.
from .base import BaseNode, NodeParameter, PortMetadata
from .registry import register_node
import pandas as pd
import geopandas as gpd

@register_node
class {type_name}(BaseNode):
    type = "{type_name}"
    name = "{name}"
    category = "{category}"
    description = "{desc}"
    
    parameters_schema = [
{params_code_block}
    ]
    
    inputs_schema = [
{inputs_code_block}
    ]
    outputs_schema = [
{outputs_code_block}
    ]

    def execute(self, input_data: dict) -> dict:
        # Execution environment variables
        local_vars = {{
            "inputs_dict": input_data,
            "outputs_dict": {{}},
            "pd": pd,
            "gpd": gpd
        }}
        
        # Backwards compatibility for old scripts expecting input_df / output_df
        if "input" in input_data:
            local_vars["input_df"] = input_data["input"]
        local_vars["output_df"] = None
        
        # Run user code
        exec(
            \"\"\"{user_code}\"\"\",
            {{}},
            local_vars
        )
        
        outputs = local_vars.get("outputs_dict", {{}})
        
        # Backwards compatibility fallback
        if not outputs and local_vars.get("output_df") is not None:
            outputs["output"] = local_vars["output_df"]
            
        return outputs
"""

    # Write class out to a custom nodes module
    custom_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to backend/
    parent_dir = os.path.dirname(custom_dir)
    file_path = os.path.join(parent_dir, "nodes", f"custom_{type_name.lower()}.py")

    try:
        with open(file_path, "w") as f:
            f.write(template)
            
        # Dynamically load module to trigger @register_node decorator
        spec = importlib.util.spec_from_file_location(f"backend.nodes.custom_{type_name.lower()}", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Verify node got loaded into registry
        NodeRegistry.get_node_class(type_name)
        
    except Exception as e:
        # Cleanup file if write or loading fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to compile or register custom node. Details: {e}"
        )

    return {"status": "success", "message": f"Custom node '{type_name}' successfully compiled and registered."}
