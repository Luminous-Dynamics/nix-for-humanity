//! Tree-sitter based Nix Parser
//!
//! Provides proper AST-based parsing of Nix expressions and configurations
//! using tree-sitter-nix for accurate syntax analysis.
//!
//! ## Features
//!
//! - Full Nix expression parsing
//! - Attribute set extraction
//! - Option path resolution
//! - Import tracking
//! - Error recovery and reporting
//!
//! ## Example
//!
//! ```rust,ignore
//! use symthaea::language::nix_parser::NixParser;
//!
//! let parser = NixParser::new();
//! let result = parser.parse(r#"
//!     { config, pkgs, ... }: {
//!       services.nginx.enable = true;
//!       environment.systemPackages = with pkgs; [ vim git ];
//!     }
//! "#)?;
//!
//! for option in result.options() {
//!     println!("{} = {:?}", option.path, option.value);
//! }
//! ```

use std::collections::HashMap;
use tree_sitter::{Parser, Node, Tree};

/// Nix AST Parser using tree-sitter
pub struct NixParser {
    parser: Parser,
}

/// Parsed Nix configuration
#[derive(Debug, Clone)]
pub struct NixConfig {
    /// Extracted options (path -> value)
    pub options: Vec<NixOption>,

    /// Import statements found
    pub imports: Vec<String>,

    /// Module arguments (config, pkgs, lib, etc.)
    pub module_args: Vec<String>,

    /// Raw AST for advanced queries
    tree: Option<Tree>,

    /// Source text for node extraction
    source: String,

    /// Parse errors encountered
    pub errors: Vec<NixParseError>,
}

/// A single Nix option/attribute
#[derive(Debug, Clone)]
pub struct NixOption {
    /// Dot-separated path (e.g., "services.nginx.enable")
    pub path: String,

    /// The value as a string representation
    pub value: NixValue,

    /// Line number in source (1-indexed)
    pub line: usize,

    /// Column number in source (1-indexed)
    pub column: usize,

    /// Raw source text of the value
    pub raw_value: String,
}

/// Typed Nix value
#[derive(Debug, Clone)]
pub enum NixValue {
    /// Boolean (true/false)
    Bool(bool),

    /// Integer
    Int(i64),

    /// String (quoted or multiline)
    String(String),

    /// Path (/path/to/file or ./relative)
    Path(String),

    /// List of values [ ... ]
    List(Vec<NixValue>),

    /// Attribute set { ... }
    AttrSet(HashMap<String, NixValue>),

    /// Function application (e.g., pkgs.firefox)
    Apply(String),

    /// With expression (with pkgs; [...])
    With { scope: String, body: Box<NixValue> },

    /// Null value
    Null,

    /// Unknown/complex expression
    Expression(String),
}

/// Parse error information
#[derive(Debug, Clone)]
pub struct NixParseError {
    /// Error message
    pub message: String,

    /// Line number (1-indexed)
    pub line: usize,

    /// Column number (1-indexed)
    pub column: usize,

    /// Error severity
    pub severity: ErrorSeverity,
}

/// Error severity levels
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorSeverity {
    /// Syntax error that prevents parsing
    Error,

    /// Potential issue but parseable
    Warning,

    /// Informational only
    Info,
}

impl NixParser {
    /// Create a new Nix parser
    pub fn new() -> Self {
        let mut parser = Parser::new();
        // Set the Nix language for parsing
        parser.set_language(&tree_sitter_nix::LANGUAGE.into())
            .expect("Failed to set Nix language for tree-sitter parser");
        Self { parser }
    }

    /// Parse Nix source code
    pub fn parse(&mut self, source: &str) -> Result<NixConfig, NixParseError> {
        let tree = self.parser.parse(source, None)
            .ok_or_else(|| NixParseError {
                message: "Failed to parse Nix source".to_string(),
                line: 1,
                column: 1,
                severity: ErrorSeverity::Error,
            })?;

        let root = tree.root_node();
        let mut config = NixConfig {
            options: Vec::new(),
            imports: Vec::new(),
            module_args: Vec::new(),
            tree: Some(tree.clone()),
            source: source.to_string(),
            errors: Vec::new(),
        };

        // Collect syntax errors
        Self::collect_errors(&root, source, &mut config.errors);

        // Extract module arguments from function definition
        self.extract_module_args(&root, source, &mut config);

        // Extract imports
        self.extract_imports(&root, source, &mut config);

        // Extract options from attribute sets
        self.extract_options(&root, source, "", &mut config);

        Ok(config)
    }

    /// Collect syntax errors from tree
    fn collect_errors(node: &Node, source: &str, errors: &mut Vec<NixParseError>) {
        if node.is_error() {
            let start = node.start_position();
            errors.push(NixParseError {
                message: format!(
                    "Syntax error near: {}",
                    &source[node.byte_range()].chars().take(50).collect::<String>()
                ),
                line: start.row + 1,
                column: start.column + 1,
                severity: ErrorSeverity::Error,
            });
        }

        if node.is_missing() {
            let start = node.start_position();
            errors.push(NixParseError {
                message: format!("Missing expected token: {}", node.kind()),
                line: start.row + 1,
                column: start.column + 1,
                severity: ErrorSeverity::Error,
            });
        }

        // Recurse into children
        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            Self::collect_errors(&child, source, errors);
        }
    }

    /// Extract module arguments from function definition
    fn extract_module_args(&self, node: &Node, source: &str, config: &mut NixConfig) {
        // Look for function definition pattern: { config, pkgs, ... }: body
        if node.kind() == "function_expression" {
            let mut cursor = node.walk();
            for child in node.children(&mut cursor) {
                if child.kind() == "formals" {
                    let mut formal_cursor = child.walk();
                    for formal in child.children(&mut formal_cursor) {
                        if formal.kind() == "formal" {
                            // Extract identifier
                            if let Some(id) = formal.child_by_field_name("name") {
                                config.module_args.push(
                                    source[id.byte_range()].to_string()
                                );
                            }
                        } else if formal.kind() == "identifier" {
                            config.module_args.push(
                                source[formal.byte_range()].to_string()
                            );
                        }
                    }
                }
            }
        }

        // Recurse to find function expressions
        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            self.extract_module_args(&child, source, config);
        }
    }

    /// Extract import statements
    fn extract_imports(&self, node: &Node, source: &str, config: &mut NixConfig) {
        // Look for imports = [ ... ] pattern
        if node.kind() == "binding" {
            if let Some(attr_path) = node.child_by_field_name("attrpath") {
                let path_text = source[attr_path.byte_range()].to_string();
                if path_text == "imports" {
                    if let Some(value) = node.child_by_field_name("expression") {
                        self.extract_import_paths(&value, source, config);
                    }
                }
            }
        }

        // Recurse
        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            self.extract_imports(&child, source, config);
        }
    }

    /// Extract paths from import list
    fn extract_import_paths(&self, node: &Node, source: &str, config: &mut NixConfig) {
        if node.kind() == "path_expression" || node.kind() == "path" {
            config.imports.push(source[node.byte_range()].to_string());
        }

        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            self.extract_import_paths(&child, source, config);
        }
    }

    /// Extract options from attribute sets
    fn extract_options(&self, node: &Node, source: &str, prefix: &str, config: &mut NixConfig) {
        if node.kind() == "binding" {
            if let Some(attr_path) = node.child_by_field_name("attrpath") {
                let path_text = source[attr_path.byte_range()].to_string();
                let full_path = if prefix.is_empty() {
                    path_text.clone()
                } else {
                    format!("{}.{}", prefix, path_text)
                };

                // Skip imports (handled separately)
                if path_text == "imports" {
                    return;
                }

                if let Some(value_node) = node.child_by_field_name("expression") {
                    let start = node.start_position();
                    let raw_value = source[value_node.byte_range()].to_string();
                    let value = self.parse_value(&value_node, source);

                    // If it's an attrset, recurse into it
                    if value_node.kind() == "attrset_expression" {
                        self.extract_options(&value_node, source, &full_path, config);
                    } else {
                        config.options.push(NixOption {
                            path: full_path,
                            value,
                            line: start.row + 1,
                            column: start.column + 1,
                            raw_value,
                        });
                    }
                }
            }
        }

        // Recurse into children
        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            self.extract_options(&child, source, prefix, config);
        }
    }

    /// Parse a value node into NixValue
    fn parse_value(&self, node: &Node, source: &str) -> NixValue {
        match node.kind() {
            "integer_expression" => {
                let text = source[node.byte_range()].trim();
                text.parse::<i64>()
                    .map(NixValue::Int)
                    .unwrap_or(NixValue::Expression(text.to_string()))
            }

            "true" => NixValue::Bool(true),
            "false" => NixValue::Bool(false),
            "null" => NixValue::Null,

            "string_expression" | "indented_string_expression" => {
                let text = source[node.byte_range()].to_string();
                // Remove quotes
                let unquoted = text.trim_matches('"')
                    .trim_start_matches("''")
                    .trim_end_matches("''")
                    .to_string();
                NixValue::String(unquoted)
            }

            "path_expression" | "path" => {
                NixValue::Path(source[node.byte_range()].to_string())
            }

            "list_expression" => {
                let mut items = Vec::new();
                let mut cursor = node.walk();
                for child in node.children(&mut cursor) {
                    if child.kind() != "[" && child.kind() != "]" {
                        items.push(self.parse_value(&child, source));
                    }
                }
                NixValue::List(items)
            }

            "attrset_expression" | "rec_attrset_expression" => {
                let mut attrs = HashMap::new();
                let mut cursor = node.walk();
                for child in node.children(&mut cursor) {
                    if child.kind() == "binding" {
                        if let Some(path) = child.child_by_field_name("attrpath") {
                            let key = source[path.byte_range()].to_string();
                            if let Some(val) = child.child_by_field_name("expression") {
                                attrs.insert(key, self.parse_value(&val, source));
                            }
                        }
                    }
                }
                NixValue::AttrSet(attrs)
            }

            "with_expression" => {
                let scope = node.child_by_field_name("environment")
                    .map(|n| source[n.byte_range()].to_string())
                    .unwrap_or_default();
                let body = node.child_by_field_name("body")
                    .map(|n| self.parse_value(&n, source))
                    .unwrap_or(NixValue::Null);
                NixValue::With {
                    scope,
                    body: Box::new(body),
                }
            }

            "select_expression" | "apply_expression" => {
                NixValue::Apply(source[node.byte_range()].to_string())
            }

            // In tree-sitter-nix 0.3+, true/false/null are parsed as variable_expression
            // We need to check the text content to identify boolean/null literals
            "variable_expression" | "identifier" => {
                let text = source[node.byte_range()].trim();
                match text {
                    "true" => NixValue::Bool(true),
                    "false" => NixValue::Bool(false),
                    "null" => NixValue::Null,
                    _ => NixValue::Apply(text.to_string())
                }
            }

            _ => NixValue::Expression(source[node.byte_range()].to_string())
        }
    }

    /// Check if source has syntax errors
    pub fn has_errors(&mut self, source: &str) -> bool {
        if let Some(tree) = self.parser.parse(source, None) {
            tree.root_node().has_error()
        } else {
            true
        }
    }

    /// Get syntax errors only (quick check)
    pub fn get_errors(&mut self, source: &str) -> Vec<NixParseError> {
        match self.parse(source) {
            Ok(config) => config.errors,
            Err(e) => vec![e],
        }
    }
}

impl Default for NixParser {
    fn default() -> Self {
        Self::new()
    }
}

impl NixConfig {
    /// Get all option paths
    pub fn option_paths(&self) -> Vec<&str> {
        self.options.iter().map(|o| o.path.as_str()).collect()
    }

    /// Find option by path
    pub fn get_option(&self, path: &str) -> Option<&NixOption> {
        self.options.iter().find(|o| o.path == path)
    }

    /// Check if an option exists
    pub fn has_option(&self, path: &str) -> bool {
        self.options.iter().any(|o| o.path == path)
    }

    /// Get all options under a prefix
    pub fn options_under(&self, prefix: &str) -> Vec<&NixOption> {
        self.options.iter()
            .filter(|o| o.path.starts_with(prefix))
            .collect()
    }

    /// Check if parse had errors
    pub fn has_errors(&self) -> bool {
        !self.errors.is_empty()
    }
}

impl NixValue {
    /// Check if value is truthy
    pub fn is_truthy(&self) -> bool {
        match self {
            NixValue::Bool(b) => *b,
            NixValue::Null => false,
            NixValue::String(s) => !s.is_empty(),
            NixValue::List(l) => !l.is_empty(),
            NixValue::AttrSet(a) => !a.is_empty(),
            _ => true,
        }
    }

    /// Get as boolean
    pub fn as_bool(&self) -> Option<bool> {
        match self {
            NixValue::Bool(b) => Some(*b),
            _ => None,
        }
    }

    /// Get as string
    pub fn as_string(&self) -> Option<&str> {
        match self {
            NixValue::String(s) => Some(s),
            NixValue::Path(p) => Some(p),
            _ => None,
        }
    }

    /// Get as list
    pub fn as_list(&self) -> Option<&[NixValue]> {
        match self {
            NixValue::List(l) => Some(l),
            _ => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_config() {
        let mut parser = NixParser::new();
        let result = parser.parse(r#"
            { config, pkgs, ... }: {
                services.nginx.enable = true;
                networking.hostName = "myhost";
            }
        "#);

        assert!(result.is_ok());
        let config = result.unwrap();

        assert!(config.module_args.contains(&"config".to_string()));
        assert!(config.module_args.contains(&"pkgs".to_string()));
    }

    #[test]
    fn test_parse_system_packages() {
        let mut parser = NixParser::new();
        let result = parser.parse(r#"
            { pkgs, ... }: {
                environment.systemPackages = with pkgs; [
                    vim
                    git
                    firefox
                ];
            }
        "#);

        assert!(result.is_ok());
        let config = result.unwrap();

        let pkg_option = config.get_option("environment.systemPackages");
        assert!(pkg_option.is_some());
    }

    #[test]
    fn test_parse_imports() {
        let mut parser = NixParser::new();
        let result = parser.parse(r#"
            { ... }: {
                imports = [
                    ./hardware-configuration.nix
                    ./networking.nix
                ];
            }
        "#);

        assert!(result.is_ok());
        let config = result.unwrap();

        assert!(!config.imports.is_empty());
    }

    #[test]
    fn test_error_detection() {
        let mut parser = NixParser::new();
        let result = parser.parse(r#"
            { ... }: {
                services.nginx.enable = true
                # Missing semicolon above
                networking.hostName = "test";
            }
        "#);

        // Should still parse but report errors
        assert!(result.is_ok());
        let config = result.unwrap();
        assert!(config.has_errors());
    }

    #[test]
    fn test_value_types() {
        let mut parser = NixParser::new();
        let result = parser.parse(r#"
            {
                boolVal = true;
                intVal = 42;
                strVal = "hello";
                pathVal = ./path;
                nullVal = null;
            }
        "#);

        assert!(result.is_ok(), "Parse should succeed");
        let config = result.unwrap();

        if let Some(opt) = config.get_option("boolVal") {
            assert!(matches!(opt.value, NixValue::Bool(true)));
        }

        if let Some(opt) = config.get_option("intVal") {
            assert!(matches!(opt.value, NixValue::Int(42)));
        }

        if let Some(opt) = config.get_option("nullVal") {
            assert!(matches!(opt.value, NixValue::Null));
        }
    }
}
