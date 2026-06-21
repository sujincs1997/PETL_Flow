import os
import shutil
import traceback
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import geopandas as gpd
from ..celery_app import celery_app
from ..database import SessionLocal
from ..models.execution import Execution, Log
from ..models.workflow import Workflow
from .dag_executor import DAGExecutor
from ..nodes.registry import NodeRegistry
from ..config import settings

def get_cache_path(execution_id: str, node_key: str, port_name: str) -> str:
    directory = os.path.join(settings.INTERMEDIATE_STORAGE_PATH, str(execution_id))
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"{node_key}_{port_name}.parquet")

def save_dataframe(df: Any, path: str):
    """Save a Pandas DataFrame or GeoPandas GeoDataFrame as a Parquet file."""
    if isinstance(df, gpd.GeoDataFrame):
        df.to_parquet(path)
    elif isinstance(df, pd.DataFrame):
        # Check if it has a geometry column that is not parsed yet
        if "geometry" in df.columns:
            try:
                # Attempt conversion to GeoDataFrame if valid geometry present
                gdf = gpd.GeoDataFrame(df, geometry="geometry")
                gdf.to_parquet(path)
                return
            except Exception:
                pass
        df.to_parquet(path)
    else:
        raise TypeError("Data must be a Pandas DataFrame or GeoPandas GeoDataFrame.")

def load_dataframe(path: str) -> Any:
    """Load a Parquet file, resolving automatically as DataFrame or GeoDataFrame."""
    try:
        # GeoPandas read_parquet handles geoparquet metadata
        return gpd.read_parquet(path)
    except Exception:
        # Fall back to standard pandas
        return pd.read_parquet(path)


def run_workflow_execution(execution_id: str):
    """
    Main visual ETL pipeline executor.
    Can be run in Celery worker or in a local background thread.
    """
    db = SessionLocal()
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        db.close()
        return f"Execution {execution_id} not found."
    
    # Setup status to RUNNING
    execution.status = "RUNNING"
    execution.started_at = datetime.utcnow()
    db.commit()

    def write_log(message: str, level: str = "INFO", node_key: str = None):
        log_entry = Log(
            execution_id=execution.id,
            node_key=node_key,
            log_level=level,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()

    write_log("Starting workflow execution task.")
    
    # Set execution ID in environment so nodes (e.g. InspectorNode) can locate their cache directory
    os.environ["ETL_EXECUTION_ID"] = str(execution.id)
    
    try:
        workflow = db.query(Workflow).filter(Workflow.id == execution.workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow '{execution.workflow_id}' not found.")

        # Instantiate DAG executor
        executor = DAGExecutor(workflow.nodes, workflow.edges)
        is_valid, errors = executor.validate()
        if not is_valid:
            error_msg = f"DAG Validation Failed: {'; '.join(errors)}"
            write_log(error_msg, "ERROR")
            raise ValueError(error_msg)
            
        write_log("Workflow DAG validated successfully. Resolving execution sequence.")
        execution_order = executor.get_execution_order()
        write_log(f"Execution order resolved: {', '.join(execution_order)}")
        
        # Loop through nodes in topological order
        for node_key in execution_order:
            node = executor.nodes_dict[node_key]
            node_class = NodeRegistry.get_node_class(node.type)
            
            write_log(f"Executing node [{node.node_key}] of type '{node.type}'...", "INFO", node_key)
            
            # Load inputs from parquet cache
            inputs = {}
            incoming_edges = executor.get_node_inputs(node_key)
            for edge in incoming_edges:
                src = edge["source"]
                src_handle = edge["source_handle"]
                tgt_handle = edge["target_handle"]
                
                cache_file = get_cache_path(execution.id, src, src_handle)
                if not os.path.exists(cache_file):
                    raise FileNotFoundError(f"Input file not found for port '{tgt_handle}' on node '{node_key}'. Expected cache: {cache_file}")
                
                inputs[tgt_handle] = load_dataframe(cache_file)
            
            # Run node execution
            node_instance = node_class(node.node_key, node.config)
            
            # Node execution validation
            node_errors = node_instance.validate()
            if node_errors:
                raise ValueError(f"Node validation error: {'; '.join(node_errors)}")
                
            # Execute node logic
            outputs = node_instance.execute(inputs)
            
            # Save output ports to cache
            for out_port, out_df in outputs.items():
                if out_df is not None:
                    cache_file = get_cache_path(execution.id, node_key, out_port)
                    save_dataframe(out_df, cache_file)
                    
            write_log(f"Node [{node.node_key}] completed successfully.", "INFO", node_key)

        # Successful complete
        execution.status = "COMPLETED"
        execution.completed_at = datetime.utcnow()
        db.commit()
        write_log("Workflow completed successfully.")
        
    except Exception as e:
        error_msg = f"Execution failed: {str(e)}"
        tb = traceback.format_exc()
        print(tb) # print to system logs
        write_log(error_msg, "ERROR")
        write_log(f"Traceback:\n{tb}", "ERROR")
        
        execution.status = "FAILED"
        execution.completed_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()

# Celery Task Wrapper
@celery_app.task(name="execute_workflow_task", bind=True)
def execute_workflow_task(self, execution_id: str):
    run_workflow_execution(execution_id)
