"""
SemanticQueryEngine - Natural Language Understanding for Graph Queries

This module provides semantic query capabilities over the knowledge graph,
translating natural language questions into graph operations and synthesizing
human-readable answers from graph data.

Part of Phase B: GraphRAG Foundation.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .graph_interface import GraphInterface, QueryResult, QueryType
from .nix_knowledge_graph import NixKnowledgeGraph, NodeType

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""

    # Information queries
    LIST = "list"  # List entities
    FIND = "find"  # Find specific entity
    DESCRIBE = "describe"  # Describe entity

    # Relationship queries
    DEPENDENCIES = "dependencies"  # What depends on X
    DEPENDENTS = "dependents"  # What X depends on
    RELATED = "related"  # Related entities
    PATH = "path"  # Path between entities

    # Analysis queries
    ANALYZE = "analyze"  # Analyze configuration
    CONFLICTS = "conflicts"  # Find conflicts
    IMPACT = "impact"  # Impact analysis
    STATISTICS = "statistics"  # Graph statistics

    # Comparison queries
    COMPARE = "compare"  # Compare entities
    DIFFERENCE = "difference"  # Find differences

    # Unknown
    UNKNOWN = "unknown"


@dataclass
class SemanticQuery:
    """A parsed semantic query"""

    raw_query: str
    intent: IntentType
    entities: list[str]
    entity_types: list[NodeType]
    filters: dict[str, Any]
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "raw_query": self.raw_query,
            "intent": self.intent.value,
            "entities": self.entities,
            "entity_types": [t.value for t in self.entity_types],
            "filters": self.filters,
            "confidence": self.confidence,
        }


class SemanticQueryEngine:
    """
    Engine for processing natural language queries over the knowledge graph.

    This class translates natural language into graph operations and
    synthesizes human-readable responses from graph data.
    """

    def __init__(
        self, graph: NixKnowledgeGraph, interface: GraphInterface | None = None
    ):
        """
        Initialize the semantic query engine.

        Args:
            graph: The knowledge graph
            interface: Optional GraphInterface (creates one if not provided)
        """
        self.graph = graph
        self.interface = interface or GraphInterface(graph)

        # Intent patterns
        self._init_patterns()

        logger.info("🧠 SemanticQueryEngine initialized")

    def _init_patterns(self):
        """Initialize regex patterns for intent recognition"""
        self.intent_patterns = {
            IntentType.LIST: [
                r"list\s+(?:all\s+)?(.+)",
                r"show\s+(?:me\s+)?(?:all\s+)?(.+)",
                r"what\s+(.+)\s+(?:are|do)",
                r"which\s+(.+)\s+(?:are|do)",
            ],
            IntentType.FIND: [
                r"find\s+(.+)",
                r"search\s+(?:for\s+)?(.+)",
                r"locate\s+(.+)",
                r"where\s+is\s+(.+)",
            ],
            IntentType.DESCRIBE: [
                r"describe\s+(.+)",
                r"tell\s+me\s+about\s+(.+)",
                r"what\s+is\s+(.+)",
                r"explain\s+(.+)",
            ],
            IntentType.DEPENDENCIES: [
                r"(?:what\s+)?(?:are\s+)?(?:the\s+)?dependencies\s+(?:of\s+)?(.+)",
                r"what\s+does\s+(.+)\s+depend\s+on",
                r"(.+)\s+dependencies",
            ],
            IntentType.DEPENDENTS: [
                r"what\s+depends\s+on\s+(.+)",
                r"(?:what\s+)?uses\s+(.+)",
                r"(.+)\s+dependents",
            ],
            IntentType.RELATED: [
                r"(?:what\s+is\s+)?related\s+to\s+(.+)",
                r"(.+)\s+relationships",
                r"connected\s+to\s+(.+)",
            ],
            IntentType.PATH: [
                r"path\s+(?:from\s+)?(.+)\s+to\s+(.+)",
                r"how\s+(?:does\s+)?(.+)\s+(?:connect|relate)\s+to\s+(.+)",
                r"connection\s+between\s+(.+)\s+and\s+(.+)",
            ],
            IntentType.ANALYZE: [
                r"analyze\s+(.+)",
                r"check\s+(.+)",
                r"verify\s+(.+)",
                r"validate\s+(.+)",
            ],
            IntentType.CONFLICTS: [
                r"(?:find\s+)?conflicts",
                r"(?:check\s+)?(?:for\s+)?conflicts",
                r"conflicting\s+(.+)",
                r"incompatible\s+(.+)",
            ],
            IntentType.IMPACT: [
                r"impact\s+(?:of\s+)?(?:changing\s+)?(.+)",
                r"what\s+(?:would\s+)?happen\s+if\s+(?:I\s+)?(?:change|remove|disable)\s+(.+)",
                r"affected\s+by\s+(.+)",
            ],
            IntentType.STATISTICS: [r"statistics", r"stats", r"summary", r"overview"],
        }

        # Entity type patterns
        self.entity_patterns = {
            NodeType.PACKAGE: ["package", "packages", "pkg", "pkgs"],
            NodeType.SERVICE: ["service", "services", "svc", "svcs"],
            NodeType.MODULE: ["module", "modules", "mod", "mods"],
            NodeType.USER: ["user", "users"],
            NodeType.NETWORK: ["network", "networking", "net"],
            NodeType.OPTION: [
                "option",
                "options",
                "setting",
                "settings",
                "config",
                "configuration",
            ],
        }

    def query(self, query: str) -> tuple[QueryResult, str]:
        """
        Process a natural language query.

        Args:
            query: Natural language query

        Returns:
            Tuple of (QueryResult, human_readable_answer)
        """
        # Parse the query
        semantic_query = self._parse_query(query)

        logger.info(f"Parsed query: {semantic_query.to_dict()}")

        # Execute based on intent
        if semantic_query.intent == IntentType.LIST:
            return self._handle_list(semantic_query)
        if semantic_query.intent == IntentType.FIND:
            return self._handle_find(semantic_query)
        if semantic_query.intent == IntentType.DESCRIBE:
            return self._handle_describe(semantic_query)
        if semantic_query.intent == IntentType.DEPENDENCIES:
            return self._handle_dependencies(semantic_query)
        if semantic_query.intent == IntentType.DEPENDENTS:
            return self._handle_dependents(semantic_query)
        if semantic_query.intent == IntentType.RELATED:
            return self._handle_related(semantic_query)
        if semantic_query.intent == IntentType.PATH:
            return self._handle_path(semantic_query)
        if semantic_query.intent == IntentType.ANALYZE:
            return self._handle_analyze(semantic_query)
        if semantic_query.intent == IntentType.CONFLICTS:
            return self._handle_conflicts(semantic_query)
        if semantic_query.intent == IntentType.IMPACT:
            return self._handle_impact(semantic_query)
        if semantic_query.intent == IntentType.STATISTICS:
            return self._handle_statistics(semantic_query)
        return self._handle_unknown(semantic_query)

    def _parse_query(self, query: str) -> SemanticQuery:
        """Parse a natural language query into a semantic query"""
        query_lower = query.lower().strip()

        # Detect intent
        intent = IntentType.UNKNOWN
        entities = []
        confidence = 0.0

        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, query_lower)
                if match:
                    intent = intent_type
                    entities = list(match.groups())
                    confidence = 0.8  # Base confidence
                    break
            if intent != IntentType.UNKNOWN:
                break

        # Detect entity types
        entity_types = []
        for entity_type, keywords in self.entity_patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    entity_types.append(entity_type)
                    confidence += 0.1
                    break

        # Extract filters
        filters = {}
        if "enabled" in query_lower:
            filters["enabled"] = True
        if "disabled" in query_lower:
            filters["enabled"] = False

        return SemanticQuery(
            raw_query=query,
            intent=intent,
            entities=entities,
            entity_types=entity_types,
            filters=filters,
            confidence=min(confidence, 1.0),
        )

    # === Intent Handlers ===

    def _handle_list(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle LIST intent"""
        # Determine what to list
        if NodeType.PACKAGE in query.entity_types:
            result = self.interface.query(QueryType.FIND_PACKAGES)
            answer = self._format_package_list(result.data if result.success else [])
        elif NodeType.SERVICE in query.entity_types:
            result = self.interface.query(
                QueryType.FIND_SERVICES,
                enabled_only=query.filters.get("enabled", False),
            )
            answer = self._format_service_list(result.data if result.success else [])
        else:
            # Default to listing everything
            result = self.interface.query(QueryType.GET_STATISTICS)
            answer = self._format_statistics(result.data if result.success else {})

        return result, answer

    def _handle_find(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle FIND intent"""
        if not query.entities:
            result = QueryResult(False, None, "No entity specified to find")
            return result, "Please specify what you want to find."

        entity_name = query.entities[0]

        # Try to find the entity
        node_type = query.entity_types[0] if query.entity_types else None
        result = self.interface.query(
            QueryType.FIND_NODE,
            name=entity_name,
            node_type=node_type.value if node_type else None,
        )

        if result.success and result.data:
            answer = f"Found {result.data['type']}: {result.data['name']}"
            if result.data.get("properties"):
                answer += f"\nProperties: {result.data['properties']}"
        else:
            answer = f"Could not find '{entity_name}'"

            # Try semantic search as fallback
            search_results = self.interface.semantic_search(entity_name, top_k=3)
            if search_results:
                answer += "\n\nDid you mean:"
                for r in search_results:
                    answer += f"\n  - {r['node']['name']} ({r['node']['type']})"

        return result, answer

    def _handle_describe(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle DESCRIBE intent"""
        if not query.entities:
            result = QueryResult(False, None, "No entity specified to describe")
            return result, "Please specify what you want to describe."

        entity_name = query.entities[0]

        # Find the entity
        node = self.graph.find_node_by_name(entity_name)
        if not node:
            result = QueryResult(False, None, f"Entity '{entity_name}' not found")
            return result, f"I couldn't find '{entity_name}' in the configuration."

        # Get comprehensive information
        dependencies = self.graph.get_dependencies(node.id)
        dependents = self.graph.get_dependents(node.id)

        answer = f"📦 {node.type.value.title()}: {node.name}\n"
        answer += f"{'=' * 40}\n"

        if node.properties:
            answer += "\n📋 Properties:\n"
            for key, value in node.properties.items():
                answer += f"  • {key}: {value}\n"

        if dependencies:
            answer += f"\n⬇️ Dependencies ({len(dependencies)}):\n"
            for dep in dependencies[:5]:
                answer += f"  • {dep.name} ({dep.type.value})\n"
            if len(dependencies) > 5:
                answer += f"  ... and {len(dependencies) - 5} more\n"

        if dependents:
            answer += f"\n⬆️ Dependents ({len(dependents)}):\n"
            for dep in dependents[:5]:
                answer += f"  • {dep.name} ({dep.type.value})\n"
            if len(dependents) > 5:
                answer += f"  ... and {len(dependents) - 5} more\n"

        if node.source_file:
            answer += f"\n📄 Source: {node.source_file}"
            if node.source_line:
                answer += f" (line {node.source_line})"

        result = QueryResult(True, node.to_dict())
        return result, answer

    def _handle_dependencies(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle DEPENDENCIES intent"""
        if not query.entities:
            result = QueryResult(False, None, "No entity specified")
            return result, "Please specify what you want to check dependencies for."

        entity_name = query.entities[0]

        # Find the entity
        node = self.graph.find_node_by_name(entity_name)
        if not node:
            result = QueryResult(False, None, f"Entity '{entity_name}' not found")
            return result, f"I couldn't find '{entity_name}' in the configuration."

        # Get dependencies
        result = self.interface.query(QueryType.GET_DEPENDENCIES, node_id=node.id)

        if result.success and result.data:
            answer = f"Dependencies of {entity_name}:\n"
            for dep in result.data:
                answer += f"  • {dep['name']} ({dep['type']})\n"
        else:
            answer = f"{entity_name} has no dependencies."

        return result, answer

    def _handle_dependents(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle DEPENDENTS intent"""
        if not query.entities:
            result = QueryResult(False, None, "No entity specified")
            return result, "Please specify what you want to check dependents for."

        entity_name = query.entities[0]

        # Get dependents
        result = self.interface.query(QueryType.GET_DEPENDENTS, name=entity_name)

        if result.success and result.data:
            answer = f"Entities that depend on {entity_name}:\n"
            for dep in result.data:
                answer += f"  • {dep['name']} ({dep['type']})\n"
        else:
            answer = f"Nothing depends on {entity_name}."

        return result, answer

    def _handle_related(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle RELATED intent"""
        if not query.entities:
            result = QueryResult(False, None, "No entity specified")
            return result, "Please specify what you want to find related entities for."

        entity_name = query.entities[0]

        # Find the entity
        node = self.graph.find_node_by_name(entity_name)
        if not node:
            result = QueryResult(False, None, f"Entity '{entity_name}' not found")
            return result, f"I couldn't find '{entity_name}' in the configuration."

        # Get related entities
        result = self.interface.query(QueryType.GET_RELATED, node_id=node.id)

        if result.success and result.data:
            answer = f"Entities related to {entity_name}:\n"
            for rel in result.data:
                answer += f"  • {rel['node']['name']} ({rel['relationship']})\n"
        else:
            answer = f"No related entities found for {entity_name}."

        return result, answer

    def _handle_path(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle PATH intent"""
        if len(query.entities) < 2:
            result = QueryResult(False, None, "Need two entities for path finding")
            return result, "Please specify two entities to find a path between."

        source_name = query.entities[0]
        target_name = query.entities[1]

        # Find the entities
        source = self.graph.find_node_by_name(source_name)
        target = self.graph.find_node_by_name(target_name)

        if not source:
            result = QueryResult(False, None, f"Source '{source_name}' not found")
            return result, f"I couldn't find '{source_name}' in the configuration."

        if not target:
            result = QueryResult(False, None, f"Target '{target_name}' not found")
            return result, f"I couldn't find '{target_name}' in the configuration."

        # Find path
        result = self.interface.query(
            QueryType.FIND_PATH, source_id=source.id, target_id=target.id
        )

        if result.success and result.data:
            path = result.data
            answer = f"Path from {source_name} to {target_name}:\n"
            for i, node_id in enumerate(path):
                if node_id in self.graph.nodes:
                    node = self.graph.nodes[node_id]
                    answer += f"  {i+1}. {node.name} ({node.type.value})\n"
                else:
                    answer += f"  {i+1}. {node_id}\n"
        else:
            answer = f"No path found between {source_name} and {target_name}."

        return result, answer

    def _handle_analyze(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle ANALYZE intent"""
        # General configuration analysis
        stats = self.graph.get_statistics()
        conflicts = self.interface.query(QueryType.CHECK_CONFLICTS)

        answer = "📊 Configuration Analysis\n"
        answer += "=" * 40 + "\n\n"

        # Statistics
        answer += "📈 Statistics:\n"
        answer += f"  • Total nodes: {stats['total_nodes']}\n"
        answer += f"  • Total edges: {stats['total_edges']}\n"
        answer += f"  • Connected components: {stats['connected_components']}\n"

        # Node breakdown
        answer += "\n📦 Components:\n"
        for node_type, count in stats["node_types"].items():
            if count > 0:
                answer += f"  • {node_type}: {count}\n"

        # Conflicts
        if conflicts.success and conflicts.data:
            answer += f"\n⚠️ Potential Conflicts ({len(conflicts.data)}):\n"
            for conflict in conflicts.data[:3]:
                answer += f"  • {conflict['message']}\n"
        else:
            answer += "\n✅ No conflicts detected\n"

        result = QueryResult(True, {"statistics": stats, "conflicts": conflicts.data})
        return result, answer

    def _handle_conflicts(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle CONFLICTS intent"""
        result = self.interface.query(QueryType.CHECK_CONFLICTS)

        if result.success and result.data:
            answer = f"⚠️ Found {len(result.data)} potential conflict(s):\n\n"
            for i, conflict in enumerate(result.data, 1):
                answer += f"{i}. {conflict['type'].replace('_', ' ').title()}\n"
                answer += f"   {conflict['message']}\n"
                answer += f"   Severity: {conflict['severity']}\n\n"
        else:
            answer = "✅ No conflicts detected in the configuration."

        return result, answer

    def _handle_impact(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle IMPACT intent"""
        if not query.entities:
            result = QueryResult(False, None, "No entity specified")
            return result, "Please specify what you want to analyze the impact of."

        entity_name = query.entities[0]

        # Find the entity
        node = self.graph.find_node_by_name(entity_name)
        if not node:
            result = QueryResult(False, None, f"Entity '{entity_name}' not found")
            return result, f"I couldn't find '{entity_name}' in the configuration."

        # Analyze impact
        result = self.interface.query(QueryType.ANALYZE_IMPACT, node_id=node.id)

        if result.success and result.data:
            impact = result.data
            answer = f"🎯 Impact Analysis for {entity_name}\n"
            answer += "=" * 40 + "\n\n"
            answer += f"Impact Level: {impact['impact_assessment'].upper()}\n\n"
            answer += "📊 Metrics:\n"
            answer += f"  • Direct dependents: {impact['direct_dependents']}\n"
            answer += f"  • Affected nodes: {impact['affected_nodes']}\n"
            answer += f"  • Affected edges: {impact['affected_edges']}\n"

            if impact["dependents"]:
                answer += "\n📦 Directly affected:\n"
                for dep in impact["dependents"][:5]:
                    answer += f"  • {dep['name']} ({dep['type']})\n"
        else:
            answer = f"Could not analyze impact for {entity_name}."

        return result, answer

    def _handle_statistics(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle STATISTICS intent"""
        result = self.interface.query(QueryType.GET_STATISTICS)

        if result.success:
            answer = self._format_statistics(result.data)
        else:
            answer = "Could not retrieve statistics."

        return result, answer

    def _handle_unknown(self, query: SemanticQuery) -> tuple[QueryResult, str]:
        """Handle UNKNOWN intent"""
        # Try semantic search as fallback
        search_results = self.interface.semantic_search(query.raw_query, top_k=5)

        if search_results:
            answer = (
                "I'm not sure what you're asking, but here are some related items:\n\n"
            )
            for r in search_results:
                answer += f"  • {r['node']['name']} ({r['node']['type']}) - score: {r['score']:.2f}\n"
            answer += "\nTry rephrasing your question or use commands like:\n"
            answer += "  • 'list packages'\n"
            answer += "  • 'describe <entity>'\n"
            answer += "  • 'what depends on <entity>'\n"
        else:
            answer = "I couldn't understand your query. Try commands like:\n"
            answer += "  • 'list packages' - Show all packages\n"
            answer += "  • 'list services' - Show all services\n"
            answer += "  • 'describe nginx' - Describe a specific entity\n"
            answer += "  • 'dependencies of firefox' - Show dependencies\n"
            answer += "  • 'what depends on systemd' - Show dependents\n"
            answer += "  • 'check conflicts' - Find configuration conflicts\n"
            answer += "  • 'statistics' - Show graph statistics\n"

        result = QueryResult(False, search_results, "Unknown query intent")
        return result, answer

    # === Formatting Helpers ===

    def _format_package_list(self, packages: list[dict]) -> str:
        """Format a list of packages"""
        if not packages:
            return "No packages found in the configuration."

        answer = f"📦 Packages ({len(packages)}):\n"
        for pkg in packages[:20]:  # Limit display
            answer += f"  • {pkg['name']}\n"

        if len(packages) > 20:
            answer += f"  ... and {len(packages) - 20} more\n"

        return answer

    def _format_service_list(self, services: list[dict]) -> str:
        """Format a list of services"""
        if not services:
            return "No services found in the configuration."

        answer = f"🔧 Services ({len(services)}):\n"
        for svc in services[:20]:  # Limit display
            status = "✅" if svc.get("properties", {}).get("enabled") else "❌"
            answer += f"  {status} {svc['name']}\n"

        if len(services) > 20:
            answer += f"  ... and {len(services) - 20} more\n"

        return answer

    def _format_statistics(self, stats: dict) -> str:
        """Format statistics"""
        answer = "📊 Knowledge Graph Statistics\n"
        answer += "=" * 40 + "\n\n"

        answer += "📈 Overall:\n"
        answer += f"  • Total nodes: {stats.get('total_nodes', 0)}\n"
        answer += f"  • Total edges: {stats.get('total_edges', 0)}\n"
        answer += f"  • Average degree: {stats.get('average_degree', 0):.2f}\n"
        answer += f"  • Connected components: {stats.get('connected_components', 0)}\n"

        if "node_types" in stats:
            answer += "\n📦 Node Types:\n"
            for node_type, count in stats["node_types"].items():
                if count > 0:
                    answer += f"  • {node_type}: {count}\n"

        if "edge_types" in stats:
            answer += "\n🔗 Edge Types:\n"
            for edge_type, count in stats["edge_types"].items():
                if count > 0:
                    answer += f"  • {edge_type}: {count}\n"

        return answer
