//! Fast JSON and Nix expression parsing with SIMD optimization

use serde_json::{Value, Map};
use std::collections::HashMap;
use anyhow::{Result, anyhow};

/// Fast JSON parser with optional SIMD acceleration
pub struct FastJsonParser {
    #[cfg(feature = "simd")]
    simd_parser: simdjson::Parser,
}

impl FastJsonParser {
    pub fn new() -> Self {
        FastJsonParser {
            #[cfg(feature = "simd")]
            simd_parser: simdjson::Parser::default(),
        }
    }

    /// Parse JSON with SIMD if available
    #[cfg(feature = "simd")]
    pub fn parse(&mut self, json_str: &str) -> Result<Value> {
        // Use SIMD parser
        let borrowed = self.simd_parser.parse(json_str.as_bytes())?;
        
        // Convert to serde_json::Value
        let value = serde_json::to_value(borrowed)?;
        Ok(value)
    }

    #[cfg(not(feature = "simd"))]
    pub fn parse(&mut self, json_str: &str) -> Result<Value> {
        // Fallback to standard parser
        let value = serde_json::from_str(json_str)?;
        Ok(value)
    }

    /// Extract packages from Nix search JSON
    pub fn parse_packages(&mut self, json_str: &str) -> Result<Vec<Package>> {
        let json = self.parse(json_str)?;
        let mut packages = Vec::new();

        if let Value::Object(map) = json {
            for (attr, info) in map {
                if let Value::Object(pkg_info) = info {
                    let package = Package {
                        attribute: attr.clone(),
                        name: extract_string(&pkg_info, "pname").unwrap_or(attr),
                        version: extract_string(&pkg_info, "version").unwrap_or_default(),
                        description: extract_string(&pkg_info, "description").unwrap_or_default(),
                        homepage: extract_string(&pkg_info, "homepage"),
                        license: extract_license(&pkg_info),
                        platforms: extract_platforms(&pkg_info),
                    };
                    packages.push(package);
                }
            }
        }

        Ok(packages)
    }

    /// Parse generation list from nixos-rebuild
    pub fn parse_generations(&mut self, json_str: &str) -> Result<Vec<Generation>> {
        let json = self.parse(json_str)?;
        let mut generations = Vec::new();

        if let Value::Array(arr) = json {
            for item in arr {
                if let Value::Object(gen) = item {
                    let generation = Generation {
                        number: extract_number(&gen, "generation").unwrap_or(0) as u32,
                        date: extract_string(&gen, "date").unwrap_or_default(),
                        current: extract_bool(&gen, "current").unwrap_or(false),
                        nixos_version: extract_string(&gen, "nixosVersion"),
                        kernel_version: extract_string(&gen, "kernelVersion"),
                        configuration_revision: extract_string(&gen, "configurationRevision"),
                    };
                    generations.push(generation);
                }
            }
        }

        Ok(generations)
    }

    /// Parse flake metadata
    pub fn parse_flake_info(&mut self, json_str: &str) -> Result<FlakeInfo> {
        let json = self.parse(json_str)?;
        
        if let Value::Object(map) = json {
            Ok(FlakeInfo {
                url: extract_string(&map, "url").unwrap_or_default(),
                locked: extract_object(&map, "locked"),
                original: extract_object(&map, "original"),
                last_modified: extract_number(&map, "lastModified"),
                revision: extract_string(&map, "revision"),
                outputs: extract_outputs(&map),
            })
        } else {
            Err(anyhow!("Invalid flake info JSON"))
        }
    }
}

/// Package information
#[derive(Debug, Clone)]
pub struct Package {
    pub attribute: String,
    pub name: String,
    pub version: String,
    pub description: String,
    pub homepage: Option<String>,
    pub license: Option<String>,
    pub platforms: Vec<String>,
}

/// System generation
#[derive(Debug, Clone)]
pub struct Generation {
    pub number: u32,
    pub date: String,
    pub current: bool,
    pub nixos_version: Option<String>,
    pub kernel_version: Option<String>,
    pub configuration_revision: Option<String>,
}

/// Flake information
#[derive(Debug, Clone)]
pub struct FlakeInfo {
    pub url: String,
    pub locked: Option<Map<String, Value>>,
    pub original: Option<Map<String, Value>>,
    pub last_modified: Option<i64>,
    pub revision: Option<String>,
    pub outputs: Vec<String>,
}

/// Nix expression parser
pub struct NixExprParser {
    // Would implement actual Nix expression parsing
    // For now, handles simple patterns
}

impl NixExprParser {
    pub fn new() -> Self {
        NixExprParser {}
    }

    /// Parse a simple Nix attribute path
    pub fn parse_attribute_path(&self, path: &str) -> Vec<String> {
        path.split('.')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect()
    }

    /// Parse package specification (name, version, etc.)
    pub fn parse_package_spec(&self, spec: &str) -> PackageSpec {
        // Handle patterns like "firefox@123.0" or "python3.pkgs.numpy"
        let parts: Vec<&str> = spec.split('@').collect();
        let name = parts[0].to_string();
        let version = parts.get(1).map(|v| v.to_string());

        PackageSpec {
            name,
            version,
            attribute: None,
        }
    }

    /// Parse flake reference
    pub fn parse_flake_ref(&self, ref_str: &str) -> Result<FlakeRef> {
        // Parse patterns like "github:owner/repo#package"
        if let Some((url, fragment)) = ref_str.split_once('#') {
            Ok(FlakeRef {
                url: url.to_string(),
                fragment: Some(fragment.to_string()),
            })
        } else {
            Ok(FlakeRef {
                url: ref_str.to_string(),
                fragment: None,
            })
        }
    }

    /// Extract configuration options from text
    pub fn extract_options(&self, text: &str) -> Vec<ConfigOption> {
        let mut options = Vec::new();
        
        for line in text.lines() {
            if line.contains('=') {
                if let Some((key, value)) = line.split_once('=') {
                    let key = key.trim().to_string();
                    let value = value.trim().trim_end_matches(';').to_string();
                    
                    options.push(ConfigOption {
                        path: key.clone(),
                        value: value.clone(),
                        type_hint: guess_type(&value),
                        description: None,
                    });
                }
            }
        }

        options
    }
}

/// Package specification
#[derive(Debug, Clone)]
pub struct PackageSpec {
    pub name: String,
    pub version: Option<String>,
    pub attribute: Option<String>,
}

/// Flake reference
#[derive(Debug, Clone)]
pub struct FlakeRef {
    pub url: String,
    pub fragment: Option<String>,
}

/// Configuration option
#[derive(Debug, Clone)]
pub struct ConfigOption {
    pub path: String,
    pub value: String,
    pub type_hint: String,
    pub description: Option<String>,
}

/// Output format optimizer
pub struct OutputFormatter {
    compact: bool,
    colorize: bool,
}

impl OutputFormatter {
    pub fn new(compact: bool, colorize: bool) -> Self {
        OutputFormatter { compact, colorize }
    }

    /// Format packages for display
    pub fn format_packages(&self, packages: &[Package]) -> String {
        if self.compact {
            packages.iter()
                .map(|p| format!("{} ({})", p.name, p.version))
                .collect::<Vec<_>>()
                .join(", ")
        } else {
            packages.iter()
                .map(|p| format!(
                    "* {} ({})\n  {}\n",
                    if self.colorize {
                        format!("\x1b[1;32m{}\x1b[0m", p.name)
                    } else {
                        p.name.clone()
                    },
                    p.version,
                    p.description
                ))
                .collect::<Vec<_>>()
                .join("\n")
        }
    }

    /// Format error messages
    pub fn format_error(&self, error: &str) -> String {
        if self.colorize {
            format!("\x1b[1;31mError:\x1b[0m {}", error)
        } else {
            format!("Error: {}", error)
        }
    }

    /// Format success messages
    pub fn format_success(&self, message: &str) -> String {
        if self.colorize {
            format!("\x1b[1;32m✓\x1b[0m {}", message)
        } else {
            format!("✓ {}", message)
        }
    }
}

// Helper functions

fn extract_string(map: &Map<String, Value>, key: &str) -> Option<String> {
    map.get(key).and_then(|v| v.as_str()).map(|s| s.to_string())
}

fn extract_number(map: &Map<String, Value>, key: &str) -> Option<i64> {
    map.get(key).and_then(|v| v.as_i64())
}

fn extract_bool(map: &Map<String, Value>, key: &str) -> Option<bool> {
    map.get(key).and_then(|v| v.as_bool())
}

fn extract_object(map: &Map<String, Value>, key: &str) -> Option<Map<String, Value>> {
    map.get(key).and_then(|v| v.as_object()).cloned()
}

fn extract_license(map: &Map<String, Value>) -> Option<String> {
    if let Some(meta) = map.get("meta").and_then(|v| v.as_object()) {
        if let Some(license) = meta.get("license") {
            if let Some(name) = license.as_str() {
                return Some(name.to_string());
            }
            if let Some(obj) = license.as_object() {
                return extract_string(obj, "spdxId")
                    .or_else(|| extract_string(obj, "fullName"));
            }
        }
    }
    None
}

fn extract_platforms(map: &Map<String, Value>) -> Vec<String> {
    if let Some(meta) = map.get("meta").and_then(|v| v.as_object()) {
        if let Some(platforms) = meta.get("platforms").and_then(|v| v.as_array()) {
            return platforms.iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect();
        }
    }
    Vec::new()
}

fn extract_outputs(map: &Map<String, Value>) -> Vec<String> {
    if let Some(outputs) = map.get("outputs").and_then(|v| v.as_object()) {
        return outputs.keys().cloned().collect();
    }
    Vec::new()
}

fn guess_type(value: &str) -> String {
    if value == "true" || value == "false" {
        "bool".to_string()
    } else if value.starts_with('"') && value.ends_with('"') {
        "string".to_string()
    } else if value.starts_with('[') && value.ends_with(']') {
        "list".to_string()
    } else if value.starts_with('{') && value.ends_with('}') {
        "attrset".to_string()
    } else if value.parse::<i64>().is_ok() {
        "int".to_string()
    } else if value.parse::<f64>().is_ok() {
        "float".to_string()
    } else {
        "unknown".to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_packages() {
        let json = r#"{
            "firefox": {
                "pname": "firefox",
                "version": "123.0",
                "meta": {
                    "description": "Web browser",
                    "license": { "spdxId": "MPL-2.0" }
                }
            }
        }"#;

        let mut parser = FastJsonParser::new();
        let packages = parser.parse_packages(json).unwrap();
        
        assert_eq!(packages.len(), 1);
        assert_eq!(packages[0].name, "firefox");
        assert_eq!(packages[0].version, "123.0");
    }

    #[test]
    fn test_parse_attribute_path() {
        let parser = NixExprParser::new();
        let path = parser.parse_attribute_path("python3.pkgs.numpy");
        
        assert_eq!(path, vec!["python3", "pkgs", "numpy"]);
    }

    #[test]
    fn test_format_output() {
        let formatter = OutputFormatter::new(false, false);
        let packages = vec![
            Package {
                attribute: "firefox".to_string(),
                name: "firefox".to_string(),
                version: "123.0".to_string(),
                description: "Web browser".to_string(),
                homepage: None,
                license: None,
                platforms: vec![],
            }
        ];

        let output = formatter.format_packages(&packages);
        assert!(output.contains("firefox"));
        assert!(output.contains("123.0"));
        assert!(output.contains("Web browser"));
    }
}