import importlib
import inspect
import os
import pkgutil
from typing import Dict, Type, List, Any
from .base import BaseNode

class NodeRegistry:
    _registry: Dict[str, Type[BaseNode]] = {}

    @classmethod
    def register(cls, node_class: Type[BaseNode]):
        """Register a node class."""
        if not issubclass(node_class, BaseNode):
            raise ValueError(f"Class {node_class.__name__} must inherit from BaseNode.")
        
        # Don't register abstract base classes
        if node_class.type == "BaseNode":
            return node_class
            
        cls._registry[node_class.type] = node_class
        return node_class

    @classmethod
    def get_node_class(cls, node_type: str) -> Type[BaseNode]:
        """Retrieve a node class by its type name."""
        if node_type not in cls._registry:
            # Force auto-discovery if registry is empty
            if not cls._registry:
                cls.discover_all()
            if node_type not in cls._registry:
                raise KeyError(f"Node type '{node_type}' not found in registry.")
        return cls._registry[node_type]

    @classmethod
    def list_nodes(cls) -> List[Type[BaseNode]]:
        """List all registered node classes."""
        if not cls._registry:
            cls.discover_all()
        return list(cls._registry.values())

    @classmethod
    def discover_all(cls):
        """Auto-discover all nodes in the nodes/ directory."""
        # Standard modules to import to register nodes
        modules = ['readers', 'writers', 'transformations', 'gis', 'inspector']
        for module_name in modules:
            try:
                importlib.import_module(f"backend.nodes.{module_name}")
            except ImportError as e:
                # Logging can go here
                print(f"Failed to auto-discover nodes in {module_name}: {e}")

        # Scan other modules inside nodes package
        import backend.nodes as nodes_pkg
        package = nodes_pkg
        for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            if not is_pkg:
                try:
                    importlib.import_module(module_name)
                except Exception:
                    pass

        # Inspect all subclasses of BaseNode
        def get_all_subclasses(cls_target):
            all_subclasses = []
            for subclass in cls_target.__subclasses__():
                all_subclasses.append(subclass)
                all_subclasses.extend(get_all_subclasses(subclass))
            return all_subclasses

        for subclass in get_all_subclasses(BaseNode):
            if subclass.type != "BaseNode" and subclass.type != "CustomNode":
                cls._registry[subclass.type] = subclass

# Decorator to manually register custom plugins
def register_node(cls):
    return NodeRegistry.register(cls)
