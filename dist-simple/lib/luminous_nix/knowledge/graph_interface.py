"""
GraphInterface - Safe Portal to the Knowledge Graph

This module provides a safe, controlled interface for plugins and other
components to query the knowledge graph. It ensures that access is
read-only and queries are bounded to prevent resource exhaustion.

Part of Phase B: GraphRAG Foundation.
"""

import logging
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass
from enum import Enum

from .nix_knowledge_graph import NixKnowledgeGraph, GraphNode, GraphEdge, NodeType, EdgeType

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries supported"""
    # Node queries
    FIND_NODE = "find_node"
    FIND_NODES_BY_TYPE = "find_nodes_by_type"
    GET_NODE_PROPERTIES = "get_node_properties"
    
    # Relationship queries
    GET_DEPENDENCIES = "get_dependencies"
    GET_DEPENDENTS = "get_dependents"
    GET_RELATED = "get_related"
    
    # Path queries
    FIND_PATH = "find_path"
    GET_SUBGRAPH = "get_subgraph"
    
    # Semantic queries
    FIND_PACKAGES = "find_packages"
    FIND_SERVICES = "find_services"
    CHECK_CONFLICTS = "check_conflicts"
    
    # Analysis queries
    GET_STATISTICS = "get_statistics"
    ANALYZE_IMPACT = "analyze_impact"


@dataclass
class QueryResult:
    """Result of a graph query"""
    success: bool
    data: Any
    error: Optional[str] = None
    query_time_ms: float = 0.0
    nodes_examined: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'query_time_ms': self.query_time_ms,
            'nodes_examined': self.nodes_examined
        }


class GraphInterface:
    """
    Safe interface to the knowledge graph for plugins and external components.
    
    This class provides read-only access with resource limits to ensure
    safe querying of the knowledge graph.
    """
    
    def __init__(self, graph: NixKnowledgeGraph, max_depth: int = 5, max_results: int = 100):
        """
        Initialize the graph interface.
        
        Args:
            graph: The knowledge graph to interface with
            max_depth: Maximum depth for graph traversal queries
            max_results: Maximum number of results to return
        """
        self.graph = graph
        self.max_depth = max_depth
        self.max_results = max_results
        
        logger.info(f"GraphInterface initialized (max_depth={max_depth}, max_results={max_results})")
    
    def query(self, query_type: QueryType, **params) -> QueryResult:
        """
        Execute a query against the knowledge graph.
        
        Args:
            query_type: Type of query to execute
            **params: Query parameters
            
        Returns:
            QueryResult with the query results
        """
        import time
        start_time = time.time()
        
        try:
            # Route to appropriate handler
            if query_type == QueryType.FIND_NODE:
                result = self._find_node(**params)
            elif query_type == QueryType.FIND_NODES_BY_TYPE:
                result = self._find_nodes_by_type(**params)
            elif query_type == QueryType.GET_NODE_PROPERTIES:
                result = self._get_node_properties(**params)
            elif query_type == QueryType.GET_DEPENDENCIES:
                result = self._get_dependencies(**params)
            elif query_type == QueryType.GET_DEPENDENTS:
                result = self._get_dependents(**params)
            elif query_type == QueryType.GET_RELATED:
                result = self._get_related(**params)
            elif query_type == QueryType.FIND_PATH:
                result = self._find_path(**params)
            elif query_type == QueryType.GET_SUBGRAPH:
                result = self._get_subgraph(**params)
            elif query_type == QueryType.FIND_PACKAGES:
                result = self._find_packages(**params)
            elif query_type == QueryType.FIND_SERVICES:
                result = self._find_services(**params)
            elif query_type == QueryType.CHECK_CONFLICTS:
                result = self._check_conflicts(**params)
            elif query_type == QueryType.GET_STATISTICS:
                result = self._get_statistics(**params)
            elif query_type == QueryType.ANALYZE_IMPACT:
                result = self._analyze_impact(**params)
            else:
                raise ValueError(f"Unknown query type: {query_type}")
            
            query_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                success=True,
                data=result,
                query_time_ms=query_time
            )
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            query_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                success=False,
                data=None,
                error=str(e),
                query_time_ms=query_time
            )
    
    def natural_language_query(self, query: str) -> QueryResult:
        """
        Process a natural language query.
        
        This is a simplified version - a full implementation would use
        NLP to parse the query and map it to graph operations.
        
        Args:
            query: Natural language query
            
        Returns:
            QueryResult with the answer
        """
        query_lower = query.lower()
        
        # Simple pattern matching for common queries
        if "what packages" in query_lower or "list packages" in query_lower:
            return self.query(QueryType.FIND_PACKAGES)
        elif "what services" in query_lower or "list services" in query_lower:
            return self.query(QueryType.FIND_SERVICES)
        elif "depends on" in query_lower:
            # Extract package/service name
            parts = query_lower.split("depends on")
            if len(parts) == 2:
                target = parts[1].strip()
                return self.query(QueryType.GET_DEPENDENTS, name=target)
        elif "dependencies of" in query_lower:
            # Extract package/service name
            parts = query_lower.split("dependencies of")
            if len(parts) == 2:
                target = parts[1].strip()
                node = self.graph.find_node_by_name(target)
                if node:
                    return self.query(QueryType.GET_DEPENDENCIES, node_id=node.id)
        elif "conflict" in query_lower:
            return self.query(QueryType.CHECK_CONFLICTS)
        elif "statistics" in query_lower or "stats" in query_lower:
            return self.query(QueryType.GET_STATISTICS)
        
        # Default response
        return QueryResult(
            success=False,
            data=None,
            error=f"Could not understand query: {query}"
        )
    
    # === Query Handlers ===
    
    def _find_node(self, name: str, node_type: Optional[str] = None) -> Optional[Dict]:
        """Find a node by name"""
        node_type_enum = NodeType[node_type.upper()] if node_type else None
        node = self.graph.find_node_by_name(name, node_type_enum)
        
        if node:
            return node.to_dict()
        return None
    
    def _find_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Find all nodes of a type"""
        try:
            node_type_enum = NodeType[node_type.upper()]
            nodes = self.graph.find_nodes_by_type(node_type_enum)
            
            # Limit results
            nodes = nodes[:self.max_results]
            
            return [node.to_dict() for node in nodes]
        except KeyError:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def _get_node_properties(self, node_id: str) -> Optional[Dict]:
        """Get properties of a node"""
        if node_id in self.graph.nodes:
            return self.graph.nodes[node_id].properties
        return None
    
    def _get_dependencies(self, node_id: str) -> List[Dict]:
        """Get dependencies of a node"""
        deps = self.graph.get_dependencies(node_id)
        
        # Limit results
        deps = deps[:self.max_results]
        
        return [dep.to_dict() for dep in deps]
    
    def _get_dependents(self, node_id: str = None, name: str = None) -> List[Dict]:
        """Get nodes that depend on this node"""
        if name and not node_id:
            node = self.graph.find_node_by_name(name)
            if node:
                node_id = node.id
        
        if not node_id:
            return []
        
        deps = self.graph.get_dependents(node_id)
        
        # Limit results
        deps = deps[:self.max_results]
        
        return [dep.to_dict() for dep in deps]
    
    def _get_related(self, node_id: str, edge_type: Optional[str] = None) -> List[Dict]:
        """Get related nodes"""
        related = []
        
        # Filter by edge type if specified
        edge_type_enum = EdgeType[edge_type.upper()] if edge_type else None
        
        for edge in self.graph.edges:
            if edge.source_id == node_id:
                if not edge_type_enum or edge.type == edge_type_enum:
                    if edge.target_id in self.graph.nodes:
                        related.append({
                            'node': self.graph.nodes[edge.target_id].to_dict(),
                            'relationship': edge.type.value
                        })
        
        # Limit results
        return related[:self.max_results]
    
    def _find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find path between nodes"""
        path = self.graph.find_path(source_id, target_id)
        
        if path and len(path) <= self.max_depth:
            return path
        elif path:
            return path[:self.max_depth] + ["... (truncated)"]
        
        return None
    
    def _get_subgraph(self, node_id: str, depth: int = 1) -> Dict:
        """Get subgraph around a node"""
        # Limit depth
        depth = min(depth, self.max_depth)
        
        nodes, edges = self.graph.get_subgraph(node_id, depth)
        
        # Limit results
        nodes = list(nodes)[:self.max_results]
        edges = edges[:self.max_results]
        
        return {
            'nodes': [node.to_dict() for node in nodes],
            'edges': [edge.to_dict() for edge in edges]
        }
    
    def _find_packages(self, pattern: Optional[str] = None) -> List[Dict]:
        """Find packages in the configuration"""
        packages = self.graph.find_nodes_by_type(NodeType.PACKAGE)
        
        # Filter by pattern if provided
        if pattern:
            pattern_lower = pattern.lower()
            packages = [p for p in packages if pattern_lower in p.name.lower()]
        
        # Limit results
        packages = packages[:self.max_results]
        
        return [p.to_dict() for p in packages]
    
    def _find_services(self, enabled_only: bool = False) -> List[Dict]:
        """Find services in the configuration"""
        services = self.graph.find_nodes_by_type(NodeType.SERVICE)
        
        # Filter by enabled status if requested
        if enabled_only:
            services = [s for s in services if s.properties.get('enabled', False)]
        
        # Limit results
        services = services[:self.max_results]
        
        return [s.to_dict() for s in services]
    
    def _check_conflicts(self) -> List[Dict]:
        """Check for potential conflicts in the configuration"""
        conflicts = []
        
        # Check for conflicting services
        # This is a simplified example - real implementation would be more sophisticated
        services = self.graph.find_nodes_by_type(NodeType.SERVICE)
        
        # Example: Check for services that shouldn't run together
        conflicting_pairs = [
            ("nginx", "apache"),
            ("mysql", "postgresql"),
            ("firewall", "iptables")
        ]
        
        for service1, service2 in conflicting_pairs:
            s1 = next((s for s in services if service1 in s.name.lower()), None)
            s2 = next((s for s in services if service2 in s.name.lower()), None)
            
            if s1 and s2:
                if s1.properties.get('enabled') and s2.properties.get('enabled'):
                    conflicts.append({
                        'type': 'service_conflict',
                        'services': [s1.name, s2.name],
                        'severity': 'high',
                        'message': f"Services {s1.name} and {s2.name} may conflict"
                    })
        
        return conflicts
    
    def _get_statistics(self) -> Dict:
        """Get graph statistics"""
        return self.graph.get_statistics()
    
    def _analyze_impact(self, node_id: str) -> Dict:
        """Analyze the impact of changing a node"""
        if node_id not in self.graph.nodes:
            return {'error': 'Node not found'}
        
        node = self.graph.nodes[node_id]
        
        # Get all dependent nodes
        dependents = self.graph.get_dependents(node_id)
        
        # Get subgraph to understand local impact
        affected_nodes, affected_edges = self.graph.get_subgraph(node_id, 2)
        
        return {
            'node': node.to_dict(),
            'direct_dependents': len(dependents),
            'affected_nodes': len(affected_nodes),
            'affected_edges': len(affected_edges),
            'dependents': [d.to_dict() for d in dependents[:10]],  # Limit for readability
            'impact_assessment': self._assess_impact_level(len(dependents), len(affected_nodes))
        }
    
    def _assess_impact_level(self, dependents: int, affected: int) -> str:
        """Assess the impact level of a change"""
        if affected == 0:
            return "none"
        elif affected <= 3:
            return "low"
        elif affected <= 10:
            return "medium"
        else:
            return "high"
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Perform semantic search over the graph.
        
        This is a placeholder for future vector-based semantic search.
        Currently does simple text matching.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of matching nodes
        """
        query_lower = query.lower()
        results = []
        
        # Search through all nodes
        for node in self.graph.nodes.values():
            score = 0.0
            
            # Check name match
            if query_lower in node.name.lower():
                score += 1.0
            
            # Check property matches
            for key, value in node.properties.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 0.5
            
            if score > 0:
                results.append({
                    'node': node.to_dict(),
                    'score': score
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:min(top_k, self.max_results)]