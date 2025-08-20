"""
NixKnowledgeGraph - The Sacred Map of Configuration Space

This module builds a semantic knowledge graph from Nix configurations using
the AST parser foundation. It transforms structured syntax into queryable
knowledge, enabling GraphRAG capabilities for intelligent configuration
understanding and manipulation.

This is Phase B: GraphRAG Foundation.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib

# Import our AST parser foundation
from ..core.nix_ast_parser import NixASTParser, ASTNode, NixNodeType, get_parser

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the knowledge graph"""
    # Configuration entities
    PACKAGE = "package"
    SERVICE = "service"
    MODULE = "module"
    OPTION = "option"
    USER = "user"
    
    # System entities
    SYSTEM = "system"
    HARDWARE = "hardware"
    NETWORK = "network"
    FILESYSTEM = "filesystem"
    
    # Relationships
    IMPORT = "import"
    DEPENDENCY = "dependency"
    OVERRIDE = "override"
    
    # Values
    VALUE = "value"
    ATTRIBUTE = "attribute"
    FUNCTION = "function"


class EdgeType(Enum):
    """Types of edges (relationships) in the knowledge graph"""
    # Structural relationships
    HAS = "has"
    CONTAINS = "contains"
    IMPORTS = "imports"
    EXTENDS = "extends"
    OVERRIDES = "overrides"
    
    # Dependency relationships
    DEPENDS_ON = "depends_on"
    PROVIDES = "provides"
    REQUIRES = "requires"
    CONFLICTS_WITH = "conflicts_with"
    
    # Configuration relationships
    ENABLES = "enables"
    CONFIGURES = "configures"
    DEFINES = "defines"
    USES = "uses"
    
    # Value relationships
    EQUALS = "equals"
    REFERENCES = "references"
    INHERITS = "inherits"


@dataclass
class GraphNode:
    """A node in the knowledge graph"""
    id: str
    type: NodeType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    ast_node: Optional[ASTNode] = None
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, GraphNode):
            return self.id == other.id
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'properties': self.properties,
            'source_file': self.source_file,
            'source_line': self.source_line
        }


@dataclass
class GraphEdge:
    """An edge (relationship) in the knowledge graph"""
    source_id: str
    target_id: str
    type: EdgeType
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.source_id, self.target_id, self.type))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'source': self.source_id,
            'target': self.target_id,
            'type': self.type.value,
            'properties': self.properties
        }


class NixKnowledgeGraph:
    """
    The Sacred Map - Builds and queries a knowledge graph from Nix configurations.
    
    This class transforms AST structures into semantic knowledge, enabling
    intelligent queries and understanding of the configuration space.
    """
    
    def __init__(self, parser: Optional[NixASTParser] = None):
        """
        Initialize the knowledge graph.
        
        Args:
            parser: Optional NixASTParser instance. Creates one if not provided.
        """
        self.parser = parser or get_parser()
        if not self.parser:
            logger.error("No parser available - tree-sitter not configured")
            raise RuntimeError("NixASTParser required for knowledge graph")
        
        # Graph storage
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.node_index: Dict[NodeType, Set[str]] = defaultdict(set)
        self.edge_index: Dict[EdgeType, List[GraphEdge]] = defaultdict(list)
        
        # Caches for performance
        self._adjacency_cache: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_adjacency_cache: Dict[str, Set[str]] = defaultdict(set)
        
        logger.info("🌐 NixKnowledgeGraph initialized")
    
    def build_from_file(self, file_path: Union[str, Path]) -> bool:
        """
        Build knowledge graph from a Nix file.
        
        Args:
            file_path: Path to the Nix configuration file
            
        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        logger.info(f"Building graph from {file_path}")
        
        # Parse the file
        ast = self.parser.parse_file(file_path)
        if not ast:
            logger.error(f"Failed to parse {file_path}")
            return False
        
        # Create root system node
        system_id = self._generate_id("system", str(file_path))
        system_node = GraphNode(
            id=system_id,
            type=NodeType.SYSTEM,
            name=file_path.stem,
            properties={'file': str(file_path)},
            source_file=str(file_path)
        )
        self._add_node(system_node)
        
        # Process the AST
        self._process_ast(ast, system_node, str(file_path))
        
        # Build caches
        self._rebuild_caches()
        
        logger.info(f"✅ Graph built: {len(self.nodes)} nodes, {len(self.edges)} edges")
        return True
    
    def build_from_directory(self, dir_path: Union[str, Path]) -> bool:
        """
        Build knowledge graph from all Nix files in a directory.
        
        Args:
            dir_path: Path to directory containing Nix files
            
        Returns:
            True if successful, False otherwise
        """
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            logger.error(f"Directory not found: {dir_path}")
            return False
        
        # Find all Nix files
        nix_files = list(dir_path.glob("**/*.nix"))
        logger.info(f"Found {len(nix_files)} Nix files in {dir_path}")
        
        # Build from each file
        success_count = 0
        for nix_file in nix_files:
            if self.build_from_file(nix_file):
                success_count += 1
        
        logger.info(f"✅ Processed {success_count}/{len(nix_files)} files")
        return success_count > 0
    
    def _process_ast(self, ast: ASTNode, parent_node: GraphNode, source_file: str):
        """
        Process an AST node and build graph elements.
        
        Args:
            ast: The AST node to process
            parent_node: Parent node in the graph
            source_file: Source file path
        """
        # Process based on node type (using actual tree-sitter-nix grammar names)
        if ast.type in ["attrset_expression", "rec_attrset_expression"]:
            self._process_attrset(ast, parent_node, source_file)
        elif ast.type in ["list_expression"]:
            self._process_list(ast, parent_node, source_file)
        elif ast.type == "binding":
            self._process_binding(ast, parent_node, source_file)
        elif ast.type == "binding_set":
            # Process all bindings in a binding set
            for binding in ast.children:
                if binding.type == "binding":
                    self._process_binding(binding, parent_node, source_file)
        elif ast.type in ["function_expression", "lambda_expression"]:
            self._process_function(ast, parent_node, source_file)
        elif ast.type in ["let_expression"]:
            self._process_let(ast, parent_node, source_file)
        elif ast.type == "import":
            self._process_import(ast, parent_node, source_file)
        
        # Recursively process children
        for child in ast.named_children:
            self._process_ast(child, parent_node, source_file)
    
    def _process_attrset(self, ast: ASTNode, parent_node: GraphNode, source_file: str):
        """Process an attribute set"""
        # First look for binding_set child
        binding_sets = ast.find_children_by_type("binding_set")
        
        # Process all bindings in binding sets
        for binding_set in binding_sets:
            for binding in binding_set.children:
                if binding.type != "binding":
                    continue
                    
                attr_path = self._get_attr_path(binding)
                
                if not attr_path:
                    continue
                
                # Detect common patterns
                if attr_path.startswith("environment.systemPackages"):
                    self._process_packages(binding, parent_node, source_file)
                elif attr_path.startswith("services."):
                    self._process_service(binding, parent_node, source_file, attr_path)
                elif attr_path.startswith("users.users."):
                    self._process_user(binding, parent_node, source_file, attr_path)
                elif attr_path.startswith("networking."):
                    self._process_network(binding, parent_node, source_file, attr_path)
                elif attr_path == "imports":
                    self._process_imports_list(binding, parent_node, source_file)
    
    def _process_packages(self, binding: ASTNode, parent_node: GraphNode, source_file: str):
        """Process environment.systemPackages"""
        # Find the list of packages - could be list_expression or with_expression
        for child in binding.children:
            if child.type == "list_expression":
                # Direct list
                for item in child.children:
                    if item.type in ["variable_expression", "identifier"]:
                        # Get the actual package name
                        pkg_name = item.text if item.type == "identifier" else item.text
                        if pkg_name and pkg_name not in ["[", "]", ","]:
                            # Create package node
                            package_id = self._generate_id("package", pkg_name)
                            package_node = GraphNode(
                                id=package_id,
                                type=NodeType.PACKAGE,
                                name=pkg_name,
                                source_file=source_file,
                                source_line=item.start_point[0]
                            )
                            self._add_node(package_node)
                            
                            # Create edge: system HAS package
                            edge = GraphEdge(
                                source_id=parent_node.id,
                                target_id=package_id,
                                type=EdgeType.HAS
                            )
                            self._add_edge(edge)
            elif child.type == "with_expression":
                # with pkgs; [ ... ] pattern
                # Find the list inside the with expression
                for subchild in child.children:
                    if subchild.type == "list_expression":
                        for item in subchild.children:
                            if item.type in ["variable_expression", "identifier"]:
                                pkg_name = item.text
                                if pkg_name and pkg_name not in ["[", "]", ","]:
                                    # Create package node
                                    package_id = self._generate_id("package", pkg_name)
                                    package_node = GraphNode(
                                        id=package_id,
                                        type=NodeType.PACKAGE,
                                        name=pkg_name,
                                        source_file=source_file,
                                        source_line=item.start_point[0]
                                    )
                                    self._add_node(package_node)
                                    
                                    # Create edge: system HAS package
                                    edge = GraphEdge(
                                        source_id=parent_node.id,
                                        target_id=package_id,
                                        type=EdgeType.HAS
                                    )
                                    self._add_edge(edge)
    
    def _process_service(self, binding: ASTNode, parent_node: GraphNode, source_file: str, attr_path: str):
        """Process a service configuration"""
        # Extract service name
        parts = attr_path.split('.')
        if len(parts) >= 2:
            service_name = parts[1]
            
            # Create service node
            service_id = self._generate_id("service", service_name)
            service_node = GraphNode(
                id=service_id,
                type=NodeType.SERVICE,
                name=service_name,
                properties={'path': attr_path},
                source_file=source_file,
                source_line=binding.start_point[0]
            )
            self._add_node(service_node)
            
            # Create edge: system CONFIGURES service
            edge = GraphEdge(
                source_id=parent_node.id,
                target_id=service_id,
                type=EdgeType.CONFIGURES
            )
            self._add_edge(edge)
            
            # Process service options
            self._process_service_options(binding, service_node, source_file)
    
    def _process_service_options(self, binding: ASTNode, service_node: GraphNode, source_file: str):
        """Process options within a service configuration"""
        # Look for enable = true/false
        for child in binding.children:
            if child.type in ["attrset", "rec_attrset"]:
                for sub_binding in child.find_children_by_type("binding"):
                    attr = self._get_attr_path(sub_binding)
                    if attr == "enable":
                        # Get the value
                        value = self._get_binding_value(sub_binding)
                        if value:
                            service_node.properties['enabled'] = value == "true"
    
    def _process_user(self, binding: ASTNode, parent_node: GraphNode, source_file: str, attr_path: str):
        """Process a user configuration"""
        # Extract username
        parts = attr_path.split('.')
        if len(parts) >= 3:
            username = parts[2]
            
            # Create user node
            user_id = self._generate_id("user", username)
            user_node = GraphNode(
                id=user_id,
                type=NodeType.USER,
                name=username,
                properties={'path': attr_path},
                source_file=source_file,
                source_line=binding.start_point[0]
            )
            self._add_node(user_node)
            
            # Create edge: system HAS user
            edge = GraphEdge(
                source_id=parent_node.id,
                target_id=user_id,
                type=EdgeType.HAS
            )
            self._add_edge(edge)
    
    def _process_network(self, binding: ASTNode, parent_node: GraphNode, source_file: str, attr_path: str):
        """Process network configuration"""
        # Create network node if not exists
        network_id = self._generate_id("network", "main")
        if network_id not in self.nodes:
            network_node = GraphNode(
                id=network_id,
                type=NodeType.NETWORK,
                name="Network Configuration",
                source_file=source_file
            )
            self._add_node(network_node)
            
            # Create edge: system HAS network
            edge = GraphEdge(
                source_id=parent_node.id,
                target_id=network_id,
                type=EdgeType.HAS
            )
            self._add_edge(edge)
    
    def _process_imports_list(self, binding: ASTNode, parent_node: GraphNode, source_file: str):
        """Process imports list"""
        for child in binding.children:
            if child.type == "list":
                for item in child.children:
                    if item.type in ["path", "string"]:
                        import_path = item.text.strip('"')
                        
                        # Create module node
                        module_id = self._generate_id("module", import_path)
                        module_node = GraphNode(
                            id=module_id,
                            type=NodeType.MODULE,
                            name=import_path,
                            properties={'path': import_path},
                            source_file=source_file,
                            source_line=item.start_point[0]
                        )
                        self._add_node(module_node)
                        
                        # Create edge: system IMPORTS module
                        edge = GraphEdge(
                            source_id=parent_node.id,
                            target_id=module_id,
                            type=EdgeType.IMPORTS
                        )
                        self._add_edge(edge)
    
    def _process_list(self, ast: ASTNode, parent_node: GraphNode, source_file: str):
        """Process a list node"""
        # Lists are handled in context by parent processors
        pass
    
    def _process_binding(self, ast: ASTNode, parent_node: GraphNode, source_file: str):
        """Process a binding node"""
        # Bindings are handled by parent processors
        pass
    
    def _process_function(self, ast: ASTNode, parent_node: GraphNode, source_file: str):
        """Process a function node"""
        # Create function node
        func_id = self._generate_id("function", f"func_{ast.start_point}")
        func_node = GraphNode(
            id=func_id,
            type=NodeType.FUNCTION,
            name=f"Function at line {ast.start_point[0]}",
            source_file=source_file,
            source_line=ast.start_point[0],
            ast_node=ast
        )
        self._add_node(func_node)
        
        # Create edge: parent CONTAINS function
        edge = GraphEdge(
            source_id=parent_node.id,
            target_id=func_id,
            type=EdgeType.CONTAINS
        )
        self._add_edge(edge)
    
    def _process_let(self, ast: ASTNode, parent_node: GraphNode, source_file: str):
        """Process a let expression"""
        # Process bindings in let
        for child in ast.children:
            if child.type == "binding":
                self._process_ast(child, parent_node, source_file)
    
    def _process_import(self, ast: ASTNode, parent_node: GraphNode, source_file: str):
        """Process an import expression"""
        # Find the imported path
        for child in ast.children:
            if child.type in ["path", "string"]:
                import_path = child.text.strip('"')
                
                # Create import node
                import_id = self._generate_id("import", import_path)
                import_node = GraphNode(
                    id=import_id,
                    type=NodeType.IMPORT,
                    name=import_path,
                    properties={'path': import_path},
                    source_file=source_file,
                    source_line=ast.start_point[0]
                )
                self._add_node(import_node)
                
                # Create edge: parent IMPORTS import
                edge = GraphEdge(
                    source_id=parent_node.id,
                    target_id=import_id,
                    type=EdgeType.IMPORTS
                )
                self._add_edge(edge)
    
    # === Utility Methods ===
    
    def _get_attr_path(self, binding: ASTNode) -> Optional[str]:
        """Extract attribute path from a binding"""
        for child in binding.children:
            if child.type == "attrpath":
                return child.text
        return None
    
    def _get_binding_value(self, binding: ASTNode) -> Optional[str]:
        """Extract value from a binding"""
        found_equals = False
        for child in binding.children:
            if child.text == "=":
                found_equals = True
            elif found_equals and child.text != ";":
                return child.text
        return None
    
    def _generate_id(self, type_prefix: str, name: str) -> str:
        """Generate a unique ID for a graph node"""
        # Use hash for consistency
        content = f"{type_prefix}:{name}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _add_node(self, node: GraphNode):
        """Add a node to the graph"""
        if node.id not in self.nodes:
            self.nodes[node.id] = node
            self.node_index[node.type].add(node.id)
    
    def _add_edge(self, edge: GraphEdge):
        """Add an edge to the graph"""
        self.edges.append(edge)
        self.edge_index[edge.type].append(edge)
        
        # Update adjacency caches
        self._adjacency_cache[edge.source_id].add(edge.target_id)
        self._reverse_adjacency_cache[edge.target_id].add(edge.source_id)
    
    def _rebuild_caches(self):
        """Rebuild adjacency caches"""
        self._adjacency_cache.clear()
        self._reverse_adjacency_cache.clear()
        
        for edge in self.edges:
            self._adjacency_cache[edge.source_id].add(edge.target_id)
            self._reverse_adjacency_cache[edge.target_id].add(edge.source_id)
    
    # === Query Methods ===
    
    def find_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """Find all nodes of a specific type"""
        node_ids = self.node_index.get(node_type, set())
        return [self.nodes[nid] for nid in node_ids]
    
    def find_node_by_name(self, name: str, node_type: Optional[NodeType] = None) -> Optional[GraphNode]:
        """Find a node by name"""
        for node in self.nodes.values():
            if node.name == name:
                if node_type is None or node.type == node_type:
                    return node
        return None
    
    def get_dependencies(self, node_id: str) -> List[GraphNode]:
        """Get all dependencies of a node"""
        dependencies = []
        for edge in self.edges:
            if edge.source_id == node_id and edge.type in [EdgeType.DEPENDS_ON, EdgeType.REQUIRES, EdgeType.IMPORTS]:
                if edge.target_id in self.nodes:
                    dependencies.append(self.nodes[edge.target_id])
        return dependencies
    
    def get_dependents(self, node_id: str) -> List[GraphNode]:
        """Get all nodes that depend on this node"""
        dependents = []
        for edge in self.edges:
            if edge.target_id == node_id and edge.type in [EdgeType.DEPENDS_ON, EdgeType.REQUIRES]:
                if edge.source_id in self.nodes:
                    dependents.append(self.nodes[edge.source_id])
        return dependents
    
    def find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find a path between two nodes using BFS"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        if source_id == target_id:
            return [source_id]
        
        # BFS
        queue = [(source_id, [source_id])]
        visited = {source_id}
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self._adjacency_cache.get(current, set()):
                if neighbor == target_id:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_subgraph(self, node_id: str, depth: int = 1) -> Tuple[Set[GraphNode], List[GraphEdge]]:
        """Get a subgraph centered on a node"""
        if node_id not in self.nodes:
            return set(), []
        
        # BFS to find nodes within depth
        nodes_to_include = {node_id}
        current_level = {node_id}
        
        for _ in range(depth):
            next_level = set()
            for nid in current_level:
                # Add forward neighbors
                next_level.update(self._adjacency_cache.get(nid, set()))
                # Add reverse neighbors
                next_level.update(self._reverse_adjacency_cache.get(nid, set()))
            
            nodes_to_include.update(next_level)
            current_level = next_level
        
        # Get nodes
        subgraph_nodes = {self.nodes[nid] for nid in nodes_to_include if nid in self.nodes}
        
        # Get edges between these nodes
        subgraph_edges = [
            edge for edge in self.edges
            if edge.source_id in nodes_to_include and edge.target_id in nodes_to_include
        ]
        
        return subgraph_nodes, subgraph_edges
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization"""
        return {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges],
            'statistics': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'node_types': {
                    node_type.value: len(self.node_index[node_type])
                    for node_type in NodeType
                },
                'edge_types': {
                    edge_type.value: len(self.edge_index[edge_type])
                    for edge_type in EdgeType
                }
            }
        }
    
    def export_to_json(self, file_path: Union[str, Path]):
        """Export graph to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': {
                node_type.value: len(self.node_index[node_type])
                for node_type in NodeType
            },
            'edge_types': {
                edge_type.value: len(self.edge_index[edge_type])
                for edge_type in EdgeType
            },
            'average_degree': len(self.edges) * 2 / len(self.nodes) if self.nodes else 0,
            'connected_components': self._count_connected_components()
        }
    
    def _count_connected_components(self) -> int:
        """Count the number of connected components in the graph"""
        visited = set()
        components = 0
        
        for node_id in self.nodes:
            if node_id not in visited:
                components += 1
                # DFS to mark all connected nodes
                stack = [node_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        stack.extend(self._adjacency_cache.get(current, set()))
                        stack.extend(self._reverse_adjacency_cache.get(current, set()))
        
        return components