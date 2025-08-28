"""
NixASTParser - The Sacred Reader of Declarative Truth

This module provides the foundation for all Nix code understanding and manipulation
through tree-sitter's grammatically perfect parsing. It transforms text into structure,
enabling safe, precise, and intelligent operations on Nix configurations.

This is Phase A-Prime: The Declarative Agent Foundation.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum

try:
    import tree_sitter
    from tree_sitter import Language, Parser, Node, Tree
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logging.warning("tree-sitter not available - AST parsing disabled")

logger = logging.getLogger(__name__)


class NixNodeType(Enum):
    """Common Nix AST node types"""
    # Literals
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    PATH = "path"
    BOOLEAN = "bool"
    NULL = "null"
    
    # Identifiers
    IDENTIFIER = "identifier"
    ATTRIBUTE = "attrpath"
    
    # Collections
    LIST = "list"
    ATTRSET = "attrset"
    REC_ATTRSET = "rec_attrset"
    
    # Functions
    FUNCTION = "function"
    LAMBDA = "lambda"
    APPLY = "apply"
    
    # Let expressions
    LET = "let"
    IN = "in"
    BINDING = "binding"
    
    # Conditionals
    IF = "if"
    THEN = "then"
    ELSE = "else"
    
    # With expressions
    WITH = "with"
    
    # Import/inherit
    IMPORT = "import"
    INHERIT = "inherit"
    
    # Comments
    COMMENT = "comment"
    
    # Root
    SOURCE_FILE = "source_file"


@dataclass
class ASTNode:
    """
    Wrapper for tree-sitter nodes with convenience methods.
    
    This provides a more Pythonic interface to the tree-sitter AST.
    """
    node: Any  # tree_sitter.Node
    source_code: str
    
    @property
    def type(self) -> str:
        """Get the node type"""
        return self.node.type if self.node else "unknown"
    
    @property
    def text(self) -> str:
        """Get the text content of this node"""
        if not self.node:
            return ""
        start = self.node.start_byte
        end = self.node.end_byte
        return self.source_code[start:end]
    
    @property
    def start_point(self) -> Tuple[int, int]:
        """Get the starting line and column"""
        if not self.node:
            return (0, 0)
        return (self.node.start_point.row, self.node.start_point.column)
    
    @property
    def end_point(self) -> Tuple[int, int]:
        """Get the ending line and column"""
        if not self.node:
            return (0, 0)
        return (self.node.end_point.row, self.node.end_point.column)
    
    @property
    def children(self) -> List['ASTNode']:
        """Get child nodes"""
        if not self.node:
            return []
        return [ASTNode(child, self.source_code) for child in self.node.children]
    
    @property
    def named_children(self) -> List['ASTNode']:
        """Get named child nodes (excluding whitespace, etc.)"""
        if not self.node:
            return []
        return [ASTNode(child, self.source_code) for child in self.node.named_children]
    
    def find_children_by_type(self, node_type: Union[str, NixNodeType]) -> List['ASTNode']:
        """Find all children of a specific type"""
        if isinstance(node_type, NixNodeType):
            node_type = node_type.value
        return [child for child in self.children if child.type == node_type]
    
    def find_descendants_by_type(self, node_type: Union[str, NixNodeType]) -> List['ASTNode']:
        """Recursively find all descendants of a specific type"""
        if isinstance(node_type, NixNodeType):
            node_type = node_type.value
        
        results = []
        to_visit = [self]
        
        while to_visit:
            current = to_visit.pop(0)
            if current.type == node_type:
                results.append(current)
            to_visit.extend(current.children)
        
        return results
    
    def get_attribute_value(self, attr_name: str) -> Optional['ASTNode']:
        """Get the value of an attribute in an attribute set"""
        if self.type not in ["attrset", "rec_attrset"]:
            return None
        
        for binding in self.find_children_by_type("binding"):
            # Get the attribute name from the binding
            attr_path = binding.find_children_by_type("attrpath")
            if attr_path and attr_path[0].text == attr_name:
                # Return the value part of the binding
                for child in binding.children:
                    if child.type not in ["attrpath", "=", ";"]:
                        return child
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AST node to a dictionary representation"""
        return {
            'type': self.type,
            'text': self.text,
            'start': self.start_point,
            'end': self.end_point,
            'children': [child.to_dict() for child in self.named_children]
        }


class NixASTParser:
    """
    The Sacred Reader - Parses Nix code into Abstract Syntax Trees.
    
    This class provides the foundation for all intelligent Nix code operations.
    It ensures that we work with the true structure of the code, not just text.
    """
    
    def __init__(self, grammar_path: Optional[Path] = None):
        """
        Initialize the NixASTParser.
        
        Args:
            grammar_path: Optional path to the tree-sitter-nix grammar file.
                         If not provided, attempts to find it automatically.
        """
        self.parser = None
        self.language = None
        
        if not TREE_SITTER_AVAILABLE:
            logger.error("tree-sitter is not installed! AST parsing unavailable.")
            return
        
        # Initialize the parser
        self._initialize_parser(grammar_path)
    
    def _initialize_parser(self, grammar_path: Optional[Path] = None):
        """Initialize the tree-sitter parser with the Nix grammar"""
        try:
            # Try to load the Nix grammar
            if grammar_path and grammar_path.exists():
                # Load from provided path
                Language.build_library(
                    str(grammar_path.parent / 'build' / 'nix.so'),
                    [str(grammar_path)]
                )
                self.language = Language(str(grammar_path.parent / 'build' / 'nix.so'), 'nix')
            else:
                # Try to import tree_sitter_nix if available as a package
                try:
                    import tree_sitter_nix
                    # tree_sitter_nix.language() returns a PyCapsule that needs wrapping
                    self.language = Language(tree_sitter_nix.language())
                except ImportError:
                    # Fallback: try to find pre-built grammar
                    logger.warning("tree-sitter-nix not found, attempting fallback...")
                    # This would need to be configured based on system setup
                    return
            
            # Create parser
            self.parser = Parser()
            # Use the language property instead of set_language method
            self.parser.language = self.language
            
            logger.info("✅ NixASTParser initialized with tree-sitter grammar")
            
        except Exception as e:
            logger.error(f"Failed to initialize tree-sitter parser: {e}")
            self.parser = None
            self.language = None
    
    def parse(self, code: str) -> Optional[ASTNode]:
        """
        Parse Nix code into an AST.
        
        Args:
            code: The Nix code to parse
            
        Returns:
            ASTNode representing the root of the AST, or None if parsing failed
        """
        if not self.parser:
            logger.error("Parser not initialized")
            return None
        
        try:
            # Parse the code
            tree = self.parser.parse(bytes(code, 'utf-8'))
            
            # Wrap in our ASTNode class
            return ASTNode(tree.root_node, code)
            
        except Exception as e:
            logger.error(f"Failed to parse Nix code: {e}")
            return None
    
    def parse_file(self, file_path: Union[str, Path]) -> Optional[ASTNode]:
        """
        Parse a Nix file into an AST.
        
        Args:
            file_path: Path to the Nix file
            
        Returns:
            ASTNode representing the root of the AST, or None if parsing failed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            code = file_path.read_text()
            return self.parse(code)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def find_nodes_by_type(self, ast: ASTNode, node_type: Union[str, NixNodeType]) -> List[ASTNode]:
        """
        Find all nodes of a specific type in the AST.
        
        Args:
            ast: The root AST node
            node_type: The type of nodes to find
            
        Returns:
            List of ASTNode objects matching the type
        """
        if isinstance(node_type, NixNodeType):
            node_type = node_type.value
        
        return ast.find_descendants_by_type(node_type)
    
    def get_node_text(self, node: ASTNode) -> str:
        """
        Get the text content of a node.
        
        Args:
            node: The AST node
            
        Returns:
            The text content of the node
        """
        return node.text
    
    def validate_syntax(self, code: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate Nix code syntax.
        
        Args:
            code: The Nix code to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not self.parser:
            return False, [{"message": "Parser not initialized", "line": 0, "column": 0}]
        
        try:
            tree = self.parser.parse(bytes(code, 'utf-8'))
            
            # Check for ERROR nodes (tree-sitter's way of marking syntax errors)
            errors = []
            self._find_errors(tree.root_node, code, errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [{"message": str(e), "line": 0, "column": 0}]
    
    def _find_errors(self, node, source_code: str, errors: List[Dict[str, Any]]):
        """Recursively find ERROR nodes in the tree"""
        if node.type == 'ERROR':
            errors.append({
                'message': f"Syntax error at {node.start_point}",
                'line': node.start_point[0] + 1,  # Convert to 1-based
                'column': node.start_point[1],
                'text': source_code[node.start_byte:node.end_byte]
            })
        
        for child in node.children:
            self._find_errors(child, source_code, errors)
    
    def extract_imports(self, ast: ASTNode) -> List[str]:
        """
        Extract all import statements from a Nix file.
        
        Args:
            ast: The root AST node
            
        Returns:
            List of imported paths
        """
        imports = []
        import_nodes = self.find_nodes_by_type(ast, NixNodeType.IMPORT)
        
        for import_node in import_nodes:
            # The import expression usually has the path as a child
            for child in import_node.children:
                if child.type in ["path", "string"]:
                    imports.append(child.text.strip('"'))
        
        return imports
    
    def extract_packages(self, ast: ASTNode) -> List[str]:
        """
        Extract package names from environment.systemPackages.
        
        Args:
            ast: The root AST node
            
        Returns:
            List of package names
        """
        packages = []
        
        # Look for environment.systemPackages
        # This is a simplified version - real implementation would be more robust
        for node in ast.find_descendants_by_type("attrpath"):
            if "environment.systemPackages" in node.text:
                # Find the associated list
                parent = node  # Would need to traverse up to binding
                # Then find the list value
                # Extract package names from the list
                pass  # Simplified for now
        
        return packages
    
    def find_attribute(self, ast: ASTNode, attribute_path: str) -> Optional[ASTNode]:
        """
        Find a specific attribute in the configuration.
        
        Args:
            ast: The root AST node
            attribute_path: Dot-separated attribute path (e.g., "services.nginx.enable")
            
        Returns:
            The ASTNode for the attribute value, or None if not found
        """
        # Split the path
        parts = attribute_path.split('.')
        
        # Start from root
        current = ast
        
        for part in parts:
            # Look for the attribute in the current scope
            found = False
            for binding in current.find_children_by_type("binding"):
                attr_path = binding.find_children_by_type("attrpath")
                if attr_path and part in attr_path[0].text:
                    # Move to the value of this binding
                    for child in binding.children:
                        if child.type not in ["attrpath", "=", ";"]:
                            current = child
                            found = True
                            break
                    if found:
                        break
            
            if not found:
                return None
        
        return current
    
    def modify_attribute(self, ast: ASTNode, attribute_path: str, new_value: str) -> str:
        """
        Modify an attribute value in the AST.
        
        This is the foundation of the Declarative Agent - safe AST manipulation.
        
        Args:
            ast: The root AST node
            attribute_path: Dot-separated attribute path
            new_value: New value as Nix code
            
        Returns:
            Modified Nix code
        """
        # Find the attribute node
        attr_node = self.find_attribute(ast, attribute_path)
        
        if not attr_node:
            logger.warning(f"Attribute {attribute_path} not found")
            return ast.source_code
        
        # Get the original code
        code = ast.source_code
        
        # Replace the old value with the new value
        start = attr_node.node.start_byte
        end = attr_node.node.end_byte
        
        modified_code = code[:start] + new_value + code[end:]
        
        # Validate the modified code
        is_valid, errors = self.validate_syntax(modified_code)
        
        if not is_valid:
            logger.error(f"Modified code has syntax errors: {errors}")
            return ast.source_code
        
        return modified_code
    
    def pretty_print(self, ast: ASTNode, indent: int = 0) -> str:
        """
        Pretty-print an AST for debugging.
        
        Args:
            ast: The AST node to print
            indent: Current indentation level
            
        Returns:
            Formatted string representation of the AST
        """
        lines = []
        indent_str = "  " * indent
        
        # Print current node
        lines.append(f"{indent_str}{ast.type}: {repr(ast.text[:50] if len(ast.text) > 50 else ast.text)}")
        
        # Print children
        for child in ast.named_children:
            lines.append(self.pretty_print(child, indent + 1))
        
        return "\n".join(lines)
    
    def generate_nix_code(self, ast: ASTNode) -> str:
        """
        Generate Nix code from an AST.
        
        This enables programmatic construction of Nix configurations.
        
        Args:
            ast: The AST to convert to code
            
        Returns:
            Generated Nix code
        """
        # For now, just return the text
        # A full implementation would reconstruct with proper formatting
        return ast.text
    
    def get_error_location(self, ast: ASTNode, error_line: int) -> Optional[ASTNode]:
        """
        Find the AST node at a specific line number.
        
        This is useful for error intelligence - mapping error messages to AST nodes.
        
        Args:
            ast: The root AST node
            error_line: Line number (1-based)
            
        Returns:
            The AST node at that line, or None
        """
        # Convert to 0-based
        error_line -= 1
        
        # Find the node at this line
        def find_at_line(node: ASTNode) -> Optional[ASTNode]:
            start_line, _ = node.start_point
            end_line, _ = node.end_point
            
            if start_line <= error_line <= end_line:
                # Check children for more specific match
                for child in node.children:
                    child_match = find_at_line(child)
                    if child_match:
                        return child_match
                return node
            return None
        
        return find_at_line(ast)


# Singleton instance for convenient access
_parser_instance = None


def get_parser() -> Optional[NixASTParser]:
    """Get or create the singleton parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = NixASTParser()
    return _parser_instance if _parser_instance.parser else None


def reset_parser():
    """Reset the parser (mainly for testing)"""
    global _parser_instance
    _parser_instance = None