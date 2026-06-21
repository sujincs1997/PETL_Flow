import networkx as nx
from typing import Dict, Any, List, Tuple
from ..nodes.registry import NodeRegistry
from ..models.workflow import Node, Edge

class DAGExecutor:
    def __init__(self, nodes: List[Node], edges: List[Edge]):
        self.nodes_dict = {n.node_key: n for n in nodes}
        self.edges = edges
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        g = nx.DiGraph()
        # Add all nodes
        for node_key in self.nodes_dict:
            g.add_node(node_key)
        # Add all edges
        for edge in self.edges:
            g.add_edge(edge.source_node, edge.target_node, source_handle=edge.source_handle, target_handle=edge.target_handle)
        return g

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate if the graph is a directed acyclic graph and all nodes are registered."""
        errors = []
        
        # 1. Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            errors.append(f"Circular dependency detected. Cycles: {cycles}")
            
        # 2. Check for missing classes in registry
        for node_key, node in self.nodes_dict.items():
            try:
                NodeRegistry.get_node_class(node.type)
            except KeyError:
                errors.append(f"Node '{node_key}' uses unknown type '{node.type}'.")
                
        # 3. Check for port configurations (dangling inputs/outputs, types mismatch if possible)
        # For simplicity, we skip complex type matching, but check for topological paths
        return len(errors) == 0, errors

    def get_execution_order(self) -> List[str]:
        """Returns the topological sort order of the node keys."""
        return list(nx.topological_sort(self.graph))

    def get_node_inputs(self, node_key: str) -> List[Dict[str, Any]]:
        """Get input details (source, source_handle, target_handle) for a node."""
        inputs = []
        for u, v, data in self.graph.in_edges(node_key, data=True):
            inputs.append({
                "source": u,
                "source_handle": data.get("source_handle", "output"),
                "target_handle": data.get("target_handle", "input")
            })
        return inputs
