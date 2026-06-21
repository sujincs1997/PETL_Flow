from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class NodeParameter(BaseModel):
    name: str
    label: str
    type: str  # str, int, float, bool, select, column_select, sql, python
    default: Any = None
    required: bool = True
    options: Optional[List[str]] = None  # for select fields
    description: Optional[str] = None

class PortMetadata(BaseModel):
    name: str
    label: str
    type: str  # e.g., 'pandas', 'geopandas', 'any'

class NodeMetadata(BaseModel):
    type: str
    name: str
    category: str  # Readers, Writers, Transformations, GIS, Network Analysis
    description: str
    parameters: List[NodeParameter]
    inputs: List[PortMetadata] = [PortMetadata(name="input", label="Input", type="any")]
    outputs: List[PortMetadata] = [PortMetadata(name="output", label="Output", type="any")]

class BaseNode:
    """
    Base class for all ETL nodes.
    Each subclass represents a visual block in the workflow.
    """
    type: str = "BaseNode"
    name: str = "Base Node"
    category: str = "General"
    description: str = ""
    parameters_schema: List[NodeParameter] = []
    inputs_schema: List[PortMetadata] = [PortMetadata(name="input", label="Input", type="any")]
    outputs_schema: List[PortMetadata] = [PortMetadata(name="output", label="Output", type="any")]

    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.id = node_id
        self.config = config
        self.params = self._validate_params()

    def _validate_params(self) -> Dict[str, Any]:
        """Validate config parameters against the parameters_schema."""
        validated = {}
        for param in self.parameters_schema:
            val = self.config.get(param.name, param.default)
            if param.required and val is None:
                raise ValueError(f"Parameter '{param.name}' is required for node '{self.name}' ({self.id}).")
            
            # Simple type conversions
            if val is not None:
                if param.type == "int":
                    val = int(val)
                elif param.type == "float":
                    val = float(val)
                elif param.type == "bool":
                    val = bool(val)
            validated[param.name] = val
        return validated

    def validate(self) -> List[str]:
        """
        Validate node configuration and input data expectations.
        Returns a list of error messages (empty if valid).
        """
        errors = []
        try:
            self._validate_params()
        except Exception as e:
            errors.append(str(e))
        return errors

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the processing logic of the node.
        
        Args:
            input_data: Dictionary mapping input port names (e.g. 'input') to data objects (Pandas, GeoPandas DataFrame).
            
        Returns:
            Dictionary mapping output port names (e.g. 'output') to processing results.
        """
        raise NotImplementedError("Subclasses must implement execute().")

    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """Return metadata representing the node in JSON schema format for the UI."""
        return NodeMetadata(
            type=cls.type,
            name=cls.name,
            category=cls.category,
            description=cls.description,
            parameters=cls.parameters_schema,
            inputs=cls.inputs_schema,
            outputs=cls.outputs_schema
        )
