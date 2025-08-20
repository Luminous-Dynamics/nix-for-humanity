#!/usr/bin/env python3
"""
AST-Enhanced Error Intelligence - The Sacred Healer

This module enhances error intelligence with AST-based understanding,
transforming it from a translator of symptoms into a true healer that
understands the deep structure of what went wrong and how to recover.

This represents the evolution from surface-level pattern matching to
deep structural understanding of errors in their grammatical context.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

# Import our foundations
from .nix_ast_parser import NixASTParser, ASTNode, get_parser
from ..knowledge.nix_knowledge_graph import NixKnowledgeGraph, NodeType
from ..knowledge.graph_interface import GraphInterface, QueryType
from .error_intelligence import ErrorType as ErrorCategory, ErrorAnalysis as AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class ASTErrorContext:
    """Rich context about an error's location in the AST"""
    error_node: Optional[ASTNode] = None
    parent_node: Optional[ASTNode] = None
    siblings: List[ASTNode] = field(default_factory=list)
    attribute_path: Optional[str] = None
    scope_type: Optional[str] = None  # 'package', 'service', 'module', etc.
    related_entities: List[Dict[str, Any]] = field(default_factory=list)


@dataclass 
class HealingPath:
    """A path to healing - not just a fix, but understanding"""
    diagnosis: str  # What's actually wrong (deep understanding)
    healing_steps: List[str]  # Steps to recovery
    preventive_wisdom: str  # How to avoid this in future
    confidence: float  # How confident we are in this path
    ast_changes: Optional[List[Dict[str, Any]]] = None  # Specific AST modifications


class ASTErrorIntelligence:
    """
    The Sacred Healer - Understands errors through grammatical truth.
    
    This class enhances error intelligence by using the AST parser and
    knowledge graph to provide deep, contextual understanding of errors
    and their healing paths.
    """
    
    def __init__(self, parser: Optional[NixASTParser] = None,
                 knowledge_graph: Optional[NixKnowledgeGraph] = None):
        """
        Initialize AST-enhanced error intelligence.
        
        Args:
            parser: Optional AST parser instance
            knowledge_graph: Optional knowledge graph instance
        """
        self.parser = parser or get_parser()
        if not self.parser:
            logger.warning("AST parser not available - using basic error intelligence")
        
        # Initialize or create knowledge graph
        if knowledge_graph:
            self.knowledge_graph = knowledge_graph
        else:
            self.knowledge_graph = NixKnowledgeGraph(self.parser) if self.parser else None
        
        # Create graph interface for safe queries
        self.graph_interface = GraphInterface(self.knowledge_graph) if self.knowledge_graph else None
        
        # Pattern database for common errors
        self.error_patterns = self._build_error_patterns()
        
        logger.info("✨ AST-enhanced ErrorIntelligence initialized")
    
    def analyze_error(self, error_message: str) -> Dict[str, Any]:
        """
        Standard interface for error analysis - wraps AST analysis.
        
        Provides compatibility with the base ErrorIntelligence interface.
        """
        healing = self.analyze_error_with_ast(error_message)
        
        # Convert HealingPath to standard format
        return {
            'category': 'CONFIGURATION',  # Default category
            'suggestions': healing.healing_steps,
            'diagnosis': healing.diagnosis,
            'confidence': healing.confidence,
            'preventive_wisdom': healing.preventive_wisdom,
            'ast_enhanced': True
        }
    
    def analyze_error_with_ast(self, error_message: str, 
                               config_file: Optional[Path] = None) -> HealingPath:
        """
        Analyze an error with deep AST understanding.
        
        Args:
            error_message: The error message to analyze
            config_file: Optional configuration file for context
            
        Returns:
            HealingPath with deep understanding and recovery steps
        """
        # Extract error location if present
        location = self._extract_error_location(error_message)
        
        # Get AST context if we have a file and location
        ast_context = None
        if config_file and location and self.parser:
            ast_context = self._get_ast_context(config_file, location)
        
        # Perform deep analysis
        if ast_context and ast_context.error_node:
            return self._analyze_with_context(error_message, ast_context)
        else:
            return self._analyze_without_context(error_message)
    
    def _extract_error_location(self, error_message: str) -> Optional[Tuple[int, int]]:
        """
        Extract line and column from error message.
        
        Returns:
            Tuple of (line, column) or None
        """
        # Common patterns for error locations
        patterns = [
            r'at line (\d+), column (\d+)',
            r'line (\d+):(\d+)',
            r'(\d+):(\d+):',
            r'line (\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                if len(match.groups()) == 2:
                    return (int(match.group(1)), int(match.group(2)))
                elif len(match.groups()) == 1:
                    return (int(match.group(1)), 0)
        
        return None
    
    def _get_ast_context(self, config_file: Path, 
                        location: Tuple[int, int]) -> ASTErrorContext:
        """
        Get rich AST context for an error location.
        
        Args:
            config_file: Configuration file path
            location: (line, column) tuple
            
        Returns:
            ASTErrorContext with rich contextual information
        """
        context = ASTErrorContext()
        
        # Parse the file
        ast = self.parser.parse_file(config_file)
        if not ast:
            return context
        
        # Find the node at the error location
        error_node = self.parser.get_error_location(ast, location[0])
        if not error_node:
            return context
        
        context.error_node = error_node
        
        # Get parent context
        context.parent_node = self._find_parent_node(ast, error_node)
        
        # Determine scope type
        context.scope_type = self._determine_scope_type(error_node, context.parent_node)
        
        # Extract attribute path if in an attribute set
        context.attribute_path = self._extract_attribute_path(error_node)
        
        # Query knowledge graph for related entities
        if self.graph_interface and context.attribute_path:
            context.related_entities = self._query_related_entities(context.attribute_path)
        
        return context
    
    def _analyze_with_context(self, error_message: str, 
                             context: ASTErrorContext) -> HealingPath:
        """
        Analyze error with rich AST context.
        
        This is where the magic happens - we understand the error
        not just as text, but in its grammatical and semantic context.
        """
        # Identify error category
        category = self._categorize_error(error_message)
        
        # Build diagnosis based on context
        diagnosis = self._build_contextual_diagnosis(error_message, context, category)
        
        # Generate healing steps based on understanding
        healing_steps = self._generate_healing_steps(diagnosis, context, category)
        
        # Provide preventive wisdom
        preventive_wisdom = self._generate_preventive_wisdom(category, context)
        
        # Calculate confidence based on context quality
        confidence = self._calculate_confidence(context)
        
        # Generate AST changes if applicable
        ast_changes = self._generate_ast_changes(context, category)
        
        return HealingPath(
            diagnosis=diagnosis,
            healing_steps=healing_steps,
            preventive_wisdom=preventive_wisdom,
            confidence=confidence,
            ast_changes=ast_changes
        )
    
    def _analyze_without_context(self, error_message: str) -> HealingPath:
        """
        Fallback analysis without AST context.
        
        Uses pattern matching and heuristics.
        """
        category = self._categorize_error(error_message)
        
        # Use pattern-based diagnosis
        diagnosis = self._pattern_based_diagnosis(error_message, category)
        
        # Generic healing steps
        healing_steps = self._generic_healing_steps(category)
        
        # Generic wisdom
        preventive_wisdom = "Consider using 'nixos-rebuild test' before 'switch' to catch errors early."
        
        return HealingPath(
            diagnosis=diagnosis,
            healing_steps=healing_steps,
            preventive_wisdom=preventive_wisdom,
            confidence=0.5,
            ast_changes=None
        )
    
    def _categorize_error(self, error_message: str) -> ErrorCategory:
        """Categorize the error type"""
        error_lower = error_message.lower()
        
        if "undefined variable" in error_lower or "not found" in error_lower:
            return ErrorCategory.MISSING_PACKAGE  # Closest match
        elif "syntax error" in error_lower or "unexpected" in error_lower:
            return ErrorCategory.SYNTAX_ERROR
        elif "type error" in error_lower or "expected" in error_lower:
            return ErrorCategory.SYNTAX_ERROR  # Treat as syntax issue
        elif "permission" in error_lower or "access denied" in error_lower:
            return ErrorCategory.PERMISSION_DENIED
        elif "hash" in error_lower:
            return ErrorCategory.HASH_MISMATCH
        elif "network" in error_lower or "download" in error_lower:
            return ErrorCategory.NETWORK_ERROR
        elif "build" in error_lower or "compilation" in error_lower:
            return ErrorCategory.BUILD_FAILURE
        else:
            return ErrorCategory.SYNTAX_ERROR  # Default fallback
    
    def _build_contextual_diagnosis(self, error_message: str,
                                   context: ASTErrorContext,
                                   category: ErrorCategory) -> str:
        """
        Build a rich diagnosis using AST context.
        
        This is where we translate from "what went wrong" to
        "what this means in your configuration".
        """
        if not context.error_node:
            return f"Error in configuration: {error_message}"
        
        # Start with location context
        diagnosis_parts = []
        
        # Describe where we are
        if context.scope_type:
            diagnosis_parts.append(f"In your {context.scope_type} configuration")
        
        if context.attribute_path:
            diagnosis_parts.append(f"at '{context.attribute_path}'")
        
        # Describe what went wrong in context
        if category == ErrorCategory.MISSING_PACKAGE:
            var_name = self._extract_variable_name(error_message)
            if var_name:
                diagnosis_parts.append(f"the variable '{var_name}' is not defined in this scope")
                
                # Check if it might be a typo
                if context.parent_node:
                    similar = self._find_similar_variables(var_name, context.parent_node)
                    if similar:
                        diagnosis_parts.append(f"(did you mean '{similar[0]}'?)")
        
        elif category == ErrorCategory.SYNTAX_ERROR:
            diagnosis_parts.append("there's a syntax error")
            if ";" in error_message:
                diagnosis_parts.append("(missing semicolon?)")
            elif "}" in error_message or "{" in error_message:
                diagnosis_parts.append("(unmatched brackets?)")
        
        # Add entity relationships if known
        if context.related_entities:
            diagnosis_parts.append(f"This affects {len(context.related_entities)} related components")
        
        return ". ".join(diagnosis_parts) + "."
    
    def _generate_healing_steps(self, diagnosis: str,
                               context: ASTErrorContext,
                               category: ErrorCategory) -> List[str]:
        """
        Generate specific healing steps based on deep understanding.
        
        These aren't generic fixes - they're specific to the context.
        """
        steps = []
        
        if category == ErrorCategory.MISSING_PACKAGE:
            var_name = self._extract_variable_name(diagnosis)
            if var_name:
                # Specific steps for undefined variable
                steps.append(f"Option 1: Define '{var_name}' in your configuration")
                steps.append(f"  Add: let {var_name} = <value>; in ... before using it")
                
                # If it's a package
                if "pkgs." in var_name or context.scope_type == "package":
                    steps.append(f"Option 2: Add to function arguments")
                    steps.append(f"  Change: {{ config, pkgs, ... }}: to include '{var_name}'")
                
                # Check for typos
                if context.parent_node:
                    similar = self._find_similar_variables(var_name, context.parent_node)
                    if similar:
                        steps.append(f"Option 3: Fix the typo")
                        steps.append(f"  Change: '{var_name}' to '{similar[0]}'")
        
        elif category == ErrorCategory.SYNTAX_ERROR:
            if context.attribute_path:
                steps.append(f"Check the type of '{context.attribute_path}'")
                steps.append("Use 'nix repl' to inspect the expected type:")
                steps.append(f"  nix repl '<nixpkgs>'")
                steps.append(f"  :t {context.attribute_path}")
        
        elif category == ErrorCategory.SYNTAX_ERROR:
            if context.error_node:
                steps.append(f"Check line {context.error_node.start_point[0]}")
                steps.append("Common fixes:")
                steps.append("  • Ensure all statements end with ';'")
                steps.append("  • Check that all { have matching }")
                steps.append("  • Verify string quotes are matched")
        
        # Add validation step
        steps.append("\nValidate your fix:")
        steps.append("  nixos-rebuild test")
        
        return steps
    
    def _generate_preventive_wisdom(self, category: ErrorCategory,
                                   context: ASTErrorContext) -> str:
        """
        Generate wisdom to prevent future occurrences.
        
        This is teaching, not just fixing.
        """
        if category == ErrorCategory.MISSING_PACKAGE:
            return ("💡 Wisdom: In Nix, all variables must be explicitly defined or passed as arguments. "
                   "Use 'let ... in' for local bindings or add to function parameters for external dependencies.")
        
        elif category == ErrorCategory.SYNTAX_ERROR:
            return ("💡 Wisdom: Nix is strongly typed. Each option expects a specific type "
                   "(string, list, boolean, etc.). Check the NixOS manual or use "
                   "'nixos-option' to see the expected type.")
        
        elif category == ErrorCategory.SYNTAX_ERROR:
            return ("💡 Wisdom: Nix syntax requires semicolons after attribute definitions "
                   "and careful bracket matching. Consider using an editor with Nix "
                   "syntax highlighting to catch these early.")
        
        else:
            return ("💡 Wisdom: Regular testing with 'nixos-rebuild test' helps catch "
                   "errors before they affect your system.")
    
    def _generate_ast_changes(self, context: ASTErrorContext,
                             category: ErrorCategory) -> Optional[List[Dict[str, Any]]]:
        """
        Generate specific AST modifications to fix the error.
        
        This is the power of AST understanding - we can suggest
        precise, surgical fixes.
        """
        if not context.error_node:
            return None
        
        changes = []
        
        if category == ErrorCategory.MISSING_PACKAGE:
            # Suggest adding a let binding
            changes.append({
                'operation': 'insert',
                'location': 'before_error',
                'ast_type': 'let_binding',
                'content': f'let {self._extract_variable_name("")} = ""; in'
            })
        
        elif category == ErrorCategory.SYNTAX_ERROR:
            # Suggest adding missing semicolon
            if ";" in str(context.error_node):
                changes.append({
                    'operation': 'append',
                    'location': 'end_of_line',
                    'content': ';'
                })
        
        return changes if changes else None
    
    def _calculate_confidence(self, context: ASTErrorContext) -> float:
        """Calculate confidence in our analysis based on context quality"""
        confidence = 0.5  # Base confidence
        
        if context.error_node:
            confidence += 0.2
        if context.parent_node:
            confidence += 0.1
        if context.attribute_path:
            confidence += 0.1
        if context.related_entities:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    # Helper methods
    
    def _find_parent_node(self, ast: ASTNode, target: ASTNode) -> Optional[ASTNode]:
        """Find the parent of a target node in the AST"""
        # Simple BFS to find parent
        queue = [(ast, None)]
        while queue:
            current, parent = queue.pop(0)
            if current == target:
                return parent
            for child in current.children:
                queue.append((child, current))
        return None
    
    def _determine_scope_type(self, node: ASTNode, 
                             parent: Optional[ASTNode]) -> Optional[str]:
        """Determine what kind of configuration scope we're in"""
        if not node:
            return None
        
        # Check the node text for clues
        text = node.text.lower()
        if "package" in text:
            return "package"
        elif "service" in text:
            return "service"
        elif "user" in text:
            return "user"
        elif "network" in text:
            return "network"
        elif "boot" in text:
            return "boot"
        
        return None
    
    def _extract_attribute_path(self, node: ASTNode) -> Optional[str]:
        """Extract the attribute path from a node"""
        if node.type == "attrpath":
            return node.text
        
        # Look for attrpath in children
        for child in node.children:
            if child.type == "attrpath":
                return child.text
        
        return None
    
    def _query_related_entities(self, attribute_path: str) -> List[Dict[str, Any]]:
        """Query knowledge graph for related entities"""
        if not self.graph_interface:
            return []
        
        # Query for dependencies
        result = self.graph_interface.query(
            QueryType.GET_DEPENDENCIES,
            node_id=attribute_path
        )
        
        if result.success:
            return result.data
        return []
    
    def _extract_variable_name(self, text: str) -> Optional[str]:
        """Extract variable name from error message"""
        patterns = [
            r"variable '([^']+)'",
            r"undefined variable '([^']+)'",
            r"attribute '([^']+)'",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def _find_similar_variables(self, var_name: str, 
                               scope: ASTNode) -> List[str]:
        """Find similar variable names in scope (for typo detection)"""
        # This would traverse the scope looking for similar names
        # Using edit distance or similar algorithm
        # Simplified for now
        return []
    
    def _extract_type_info(self, error_message: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract expected and actual types from error message"""
        match = re.search(r"expected (.+) but got (.+)", error_message)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def _pattern_based_diagnosis(self, error_message: str, 
                                category: ErrorCategory) -> str:
        """Fallback pattern-based diagnosis"""
        if category == ErrorCategory.MISSING_PACKAGE:
            return "A variable or attribute is not defined in the current scope."
        elif category == ErrorCategory.SYNTAX_ERROR:
            return "The value type doesn't match what's expected."
        elif category == ErrorCategory.SYNTAX_ERROR:
            return "There's a syntax error in your configuration."
        else:
            return f"Configuration error: {error_message[:100]}..."
    
    def _generic_healing_steps(self, category: ErrorCategory) -> List[str]:
        """Generic healing steps when we don't have context"""
        if category == ErrorCategory.MISSING_PACKAGE:
            return [
                "Check that all variables are defined",
                "Ensure required imports are present",
                "Verify function arguments include needed parameters"
            ]
        elif category == ErrorCategory.SYNTAX_ERROR:
            return [
                "Check the expected type in NixOS options",
                "Ensure values match their required types",
                "Use 'nixos-option' to inspect option types"
            ]
        else:
            return [
                "Review the error location",
                "Check NixOS manual for correct syntax",
                "Test with 'nixos-rebuild test'"
            ]
    
    def _build_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Build a database of common error patterns"""
        return {
            "undefined_variable": {
                "patterns": [
                    r"undefined variable '([^']+)'",
                    r"attribute '([^']+)' missing"
                ],
                "category": ErrorCategory.MISSING_PACKAGE
            },
            "type_mismatch": {
                "patterns": [
                    r"expected (.+) but got (.+)",
                    r"value is (.+) while a (.+) was expected"
                ],
                "category": ErrorCategory.SYNTAX_ERROR
            },
            "syntax_error": {
                "patterns": [
                    r"syntax error",
                    r"unexpected (.+)",
                    r"expecting (.+)"
                ],
                "category": ErrorCategory.SYNTAX_ERROR
            }
        }