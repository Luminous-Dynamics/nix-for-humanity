#!/usr/bin/env python3
"""
AST-Based Configuration Generator - The Sacred Scribe

This module generates NixOS configurations using the AST parser foundation,
ensuring grammatically perfect and semantically coherent configurations.
It represents the evolution from template-based generation to true understanding.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json

# Import our foundations
from .nix_ast_parser import NixASTParser, ASTNode, get_parser
from ..knowledge.nix_knowledge_graph import NixKnowledgeGraph, NodeType, EdgeType
from ..knowledge.graph_interface import GraphInterface, QueryType

logger = logging.getLogger(__name__)


@dataclass
class ConfigIntent:
    """Represents the user's intent for configuration"""
    action: str  # 'add', 'remove', 'modify', 'enable', 'disable'
    target: str  # What to configure (package, service, etc.)
    properties: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigChange:
    """Represents a change to be made to the configuration"""
    path: str  # Attribute path (e.g., "services.nginx.enable")
    value: Any  # New value
    operation: str  # 'set', 'append', 'remove'
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


class ASTConfigGenerator:
    """
    The Sacred Scribe - Generates configurations with grammatical truth.
    
    This class uses the AST parser and knowledge graph to generate
    configurations that are not just syntactically correct, but
    semantically coherent with the existing system.
    """
    
    def __init__(self, parser: Optional[NixASTParser] = None,
                 knowledge_graph: Optional[NixKnowledgeGraph] = None):
        """
        Initialize the AST-based config generator.
        
        Args:
            parser: Optional AST parser instance
            knowledge_graph: Optional knowledge graph instance
        """
        self.parser = parser or get_parser()
        if not self.parser:
            raise RuntimeError("AST parser required for config generation")
        
        # Initialize or create knowledge graph
        if knowledge_graph:
            self.knowledge_graph = knowledge_graph
        else:
            self.knowledge_graph = NixKnowledgeGraph(self.parser)
        
        # Create graph interface for safe queries
        self.graph_interface = GraphInterface(self.knowledge_graph)
        
        # Current configuration AST
        self.current_ast = None
        self.current_file = None
        
        logger.info("✨ AST-based ConfigGenerator initialized")
    
    def load_configuration(self, file_path: Union[str, Path]) -> bool:
        """
        Load an existing configuration file.
        
        Args:
            file_path: Path to configuration.nix
            
        Returns:
            True if successful
        """
        file_path = Path(file_path)
        
        # Parse the configuration
        self.current_ast = self.parser.parse_file(file_path)
        if not self.current_ast:
            logger.error(f"Failed to parse {file_path}")
            return False
        
        self.current_file = file_path
        
        # Build knowledge graph from the configuration
        self.knowledge_graph.build_from_file(file_path)
        
        logger.info(f"✅ Loaded configuration from {file_path}")
        logger.info(f"   Graph: {len(self.knowledge_graph.nodes)} nodes, "
                   f"{len(self.knowledge_graph.edges)} edges")
        
        return True
    
    def analyze_intent(self, query: str) -> ConfigIntent:
        """
        Analyze user's natural language query to determine intent.
        
        Args:
            query: Natural language query
            
        Returns:
            ConfigIntent representing the user's goal
        """
        query_lower = query.lower()
        
        # Simple pattern matching (would use NLP in production)
        if "install" in query_lower or "add" in query_lower:
            action = "add"
        elif "remove" in query_lower or "uninstall" in query_lower:
            action = "remove"
        elif "enable" in query_lower:
            action = "enable"
        elif "disable" in query_lower:
            action = "disable"
        else:
            action = "modify"
        
        # Extract target (simplified)
        target = self._extract_target(query)
        
        # Extract properties
        properties = self._extract_properties(query)
        
        return ConfigIntent(
            action=action,
            target=target,
            properties=properties,
            context={"original_query": query}
        )
    
    def generate_changes(self, intent: ConfigIntent) -> List[ConfigChange]:
        """
        Generate configuration changes based on intent.
        
        This method uses the knowledge graph to understand dependencies
        and generate coherent changes.
        
        Args:
            intent: The user's configuration intent
            
        Returns:
            List of configuration changes to apply
        """
        changes = []
        
        # Query the knowledge graph for context
        if intent.action == "add" and "package" in intent.target:
            changes.extend(self._generate_package_changes(intent))
        elif intent.action == "enable" and "service" in intent.target:
            changes.extend(self._generate_service_changes(intent))
        elif intent.action == "add" and "user" in intent.target:
            changes.extend(self._generate_user_changes(intent))
        else:
            # Default to simple attribute setting
            changes.append(self._generate_simple_change(intent))
        
        # Check for conflicts and dependencies
        changes = self._resolve_dependencies(changes)
        
        return changes
    
    def apply_changes(self, changes: List[ConfigChange]) -> str:
        """
        Apply changes to the current configuration AST.
        
        Args:
            changes: List of changes to apply
            
        Returns:
            Modified Nix configuration as string
        """
        if not self.current_ast:
            logger.error("No configuration loaded")
            return ""
        
        # Get the original source
        source = self.current_ast.text
        
        for change in changes:
            logger.info(f"Applying change: {change.path} = {change.value}")
            
            # Use the AST parser to safely modify the configuration
            if change.operation == "set":
                source = self._apply_set_operation(source, change)
            elif change.operation == "append":
                source = self._apply_append_operation(source, change)
            elif change.operation == "remove":
                source = self._apply_remove_operation(source, change)
        
        # Validate the result
        new_ast = self.parser.parse(source)
        if not new_ast:
            logger.error("Generated invalid configuration")
            return self.current_ast.text
        
        # Validate syntax
        is_valid, errors = self.parser.validate_syntax(source)
        if not is_valid:
            logger.error(f"Syntax errors in generated config: {errors}")
            return self.current_ast.text
        
        return source
    
    def _generate_package_changes(self, intent: ConfigIntent) -> List[ConfigChange]:
        """Generate changes for package operations"""
        changes = []
        package_name = intent.properties.get("name", intent.target.replace("package:", ""))
        
        if intent.action == "add":
            # Check if package already exists
            result = self.graph_interface.query(
                QueryType.FIND_PACKAGES,
                pattern=package_name
            )
            
            packages = result.data if isinstance(result.data, list) else result.data.get('packages', [])
            if result.success and package_name in [p.get('name', p) if isinstance(p, dict) else p for p in packages]:
                logger.info(f"Package {package_name} already installed")
                return []
            
            # Add to systemPackages
            changes.append(ConfigChange(
                path="environment.systemPackages",
                value=package_name,
                operation="append"
            ))
            
            # Check for common dependencies
            if package_name == "docker":
                changes.append(ConfigChange(
                    path="virtualisation.docker.enable",
                    value="true",
                    operation="set"
                ))
        
        return changes
    
    def _generate_service_changes(self, intent: ConfigIntent) -> List[ConfigChange]:
        """Generate changes for service operations"""
        changes = []
        service_name = intent.properties.get("name", intent.target.replace("service:", ""))
        
        if intent.action == "enable":
            # Main service enable
            changes.append(ConfigChange(
                path=f"services.{service_name}.enable",
                value="true",
                operation="set"
            ))
            
            # Check for required dependencies
            if service_name == "nginx":
                changes.append(ConfigChange(
                    path="networking.firewall.allowedTCPPorts",
                    value="80",
                    operation="append"
                ))
                changes.append(ConfigChange(
                    path="networking.firewall.allowedTCPPorts",
                    value="443",
                    operation="append"
                ))
        
        return changes
    
    def _generate_user_changes(self, intent: ConfigIntent) -> List[ConfigChange]:
        """Generate changes for user operations"""
        changes = []
        username = intent.properties.get("name", intent.target.replace("user:", ""))
        
        if intent.action == "add":
            # Create user with common defaults
            changes.append(ConfigChange(
                path=f"users.users.{username}",
                value={
                    "isNormalUser": True,
                    "extraGroups": ["wheel"],
                    "shell": "pkgs.bash"
                },
                operation="set"
            ))
        
        return changes
    
    def _generate_simple_change(self, intent: ConfigIntent) -> ConfigChange:
        """Generate a simple attribute change"""
        return ConfigChange(
            path=intent.target,
            value=intent.properties.get("value", "true"),
            operation="set"
        )
    
    def _resolve_dependencies(self, changes: List[ConfigChange]) -> List[ConfigChange]:
        """
        Resolve dependencies and conflicts in changes.
        
        Uses the knowledge graph to understand relationships.
        """
        resolved = []
        
        for change in changes:
            # Query graph for conflicts
            conflicts = self._check_conflicts(change)
            if conflicts:
                logger.warning(f"Change {change.path} conflicts with: {conflicts}")
                # Could prompt user or auto-resolve
            
            # Query graph for dependencies
            deps = self._check_dependencies(change)
            for dep in deps:
                if dep not in [c.path for c in resolved]:
                    resolved.append(ConfigChange(
                        path=dep,
                        value="true",
                        operation="set"
                    ))
            
            resolved.append(change)
        
        return resolved
    
    def _check_conflicts(self, change: ConfigChange) -> List[str]:
        """Check for conflicts using the knowledge graph"""
        # This would query the graph for conflicting services/packages
        # For now, return empty list
        return []
    
    def _check_dependencies(self, change: ConfigChange) -> List[str]:
        """Check for dependencies using the knowledge graph"""
        # This would query the graph for required dependencies
        # For now, return empty list
        return []
    
    def _apply_set_operation(self, source: str, change: ConfigChange) -> str:
        """Apply a set operation to the configuration"""
        # Parse current AST
        ast = self.parser.parse(source)
        
        # Find or create the attribute path
        # This is simplified - real implementation would traverse and modify AST
        if isinstance(change.value, dict):
            value_str = self._dict_to_nix(change.value)
        elif isinstance(change.value, bool):
            value_str = "true" if change.value else "false"
        elif isinstance(change.value, str):
            if change.value in ["true", "false"]:
                value_str = change.value
            else:
                value_str = f'"{change.value}"'
        else:
            value_str = str(change.value)
        
        # Simple approach: append to configuration
        # Real implementation would modify AST properly
        lines = source.split('\n')
        
        # Find where to insert (before final })
        insert_idx = len(lines) - 1
        for i in range(len(lines) - 1, -1, -1):
            if '}' in lines[i]:
                insert_idx = i
                break
        
        # Insert the new configuration
        indent = "  "
        new_line = f"{indent}{change.path} = {value_str};"
        lines.insert(insert_idx, new_line)
        
        return '\n'.join(lines)
    
    def _apply_append_operation(self, source: str, change: ConfigChange) -> str:
        """Apply an append operation to a list"""
        # This would find the list in the AST and append to it
        # For now, use simple approach
        return self._apply_set_operation(source, change)
    
    def _apply_remove_operation(self, source: str, change: ConfigChange) -> str:
        """Apply a remove operation"""
        # This would find and remove from the AST
        # For now, comment out the line
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if change.path in line:
                lines[i] = f"  # {line.strip()}  # Removed by ConfigGenerator"
        return '\n'.join(lines)
    
    def _extract_target(self, query: str) -> str:
        """Extract the target from a query"""
        # Simple keyword extraction
        if "nginx" in query.lower():
            return "service:nginx"
        elif "docker" in query.lower():
            return "package:docker"
        elif "firefox" in query.lower():
            return "package:firefox"
        elif "user" in query.lower():
            return "user:newuser"
        else:
            return "unknown"
    
    def _extract_properties(self, query: str) -> Dict[str, Any]:
        """Extract properties from a query"""
        properties = {}
        
        # Extract quoted strings as values
        import re
        quotes = re.findall(r'"([^"]*)"', query)
        if quotes:
            properties["value"] = quotes[0]
        
        # Extract names
        words = query.split()
        for i, word in enumerate(words):
            if word in ["called", "named"] and i + 1 < len(words):
                properties["name"] = words[i + 1]
        
        return properties
    
    def _dict_to_nix(self, d: Dict[str, Any]) -> str:
        """Convert a Python dict to Nix attribute set syntax"""
        lines = ["{"]
        for key, value in d.items():
            if isinstance(value, bool):
                val_str = "true" if value else "false"
            elif isinstance(value, str):
                val_str = f'"{value}"'
            elif isinstance(value, list):
                val_str = f"[ {' '.join(str(v) for v in value)} ]"
            else:
                val_str = str(value)
            lines.append(f"    {key} = {val_str};")
        lines.append("  }")
        return '\n'.join(lines)
    
    def validate_configuration(self, config: str) -> tuple[bool, List[str]]:
        """
        Validate a configuration using AST parser.
        
        Args:
            config: Nix configuration string
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        return self.parser.validate_syntax(config)
    
    def get_suggestions(self, partial_config: str) -> List[str]:
        """
        Get suggestions for incomplete configurations.
        
        Uses the knowledge graph to suggest completions.
        """
        suggestions = []
        
        # Parse what we have
        ast = self.parser.parse(partial_config)
        if not ast:
            return []
        
        # Find incomplete attribute paths
        # This would analyze the AST for incomplete expressions
        # and use the graph to suggest completions
        
        return suggestions