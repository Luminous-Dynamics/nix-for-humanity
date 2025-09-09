//! Query and command optimization for maximum performance

use std::collections::HashMap;
use regex::Regex;
use once_cell::sync::Lazy;

/// Query optimizer for NixOS commands
pub struct QueryOptimizer {
    patterns: Vec<OptimizationPattern>,
    cache_hints: HashMap<String, CacheHint>,
}

impl QueryOptimizer {
    pub fn new() -> Self {
        QueryOptimizer {
            patterns: build_optimization_patterns(),
            cache_hints: build_cache_hints(),
        }
    }

    /// Optimize a user query for better performance
    pub fn optimize_query(&self, query: &str) -> OptimizedQuery {
        let mut optimized = OptimizedQuery {
            original: query.to_string(),
            normalized: normalize_query(query),
            intent: detect_intent(query),
            entities: extract_entities(query),
            cache_key: None,
            json_output: should_use_json(query),
            parallel_safe: is_parallel_safe(query),
            estimated_time_ms: estimate_time(query),
        };

        // Apply optimization patterns
        for pattern in &self.patterns {
            if pattern.regex.is_match(&optimized.normalized) {
                optimized.normalized = pattern.regex
                    .replace(&optimized.normalized, &pattern.replacement)
                    .to_string();
                
                if let Some(hint) = &pattern.cache_hint {
                    optimized.cache_key = Some(generate_cache_key(&optimized.normalized));
                }
            }
        }

        optimized
    }

    /// Suggest alternative queries for better results
    pub fn suggest_alternatives(&self, query: &str) -> Vec<String> {
        let mut suggestions = Vec::new();

        // Common typo corrections
        if query.contains("instal") {
            suggestions.push(query.replace("instal", "install"));
        }
        if query.contains("uninstal") {
            suggestions.push(query.replace("uninstal", "uninstall"));
        }

        // Suggest more specific queries
        if query == "browser" {
            suggestions.push("install firefox".to_string());
            suggestions.push("install chromium".to_string());
            suggestions.push("search browser".to_string());
        }

        // Suggest using package sets
        if query.contains("python library") {
            let lib_name = query.replace("install python library", "").trim().to_string();
            suggestions.push(format!("install python3.pkgs.{}", lib_name));
        }

        suggestions
    }

    /// Get cache hint for a query
    pub fn get_cache_hint(&self, query: &str) -> Option<&CacheHint> {
        for (pattern, hint) in &self.cache_hints {
            if query.contains(pattern) {
                return Some(hint);
            }
        }
        None
    }
}

/// Optimized query with metadata
#[derive(Debug, Clone)]
pub struct OptimizedQuery {
    pub original: String,
    pub normalized: String,
    pub intent: Intent,
    pub entities: Vec<Entity>,
    pub cache_key: Option<String>,
    pub json_output: bool,
    pub parallel_safe: bool,
    pub estimated_time_ms: u32,
}

/// User intent
#[derive(Debug, Clone, PartialEq)]
pub enum Intent {
    Install,
    Uninstall,
    Search,
    List,
    Update,
    Configure,
    Query,
    Help,
    Unknown,
}

/// Extracted entity
#[derive(Debug, Clone)]
pub struct Entity {
    pub entity_type: EntityType,
    pub value: String,
    pub confidence: f32,
}

#[derive(Debug, Clone, PartialEq)]
pub enum EntityType {
    Package,
    Service,
    Option,
    File,
    Command,
}

/// Cache hint for optimization
#[derive(Debug, Clone)]
pub struct CacheHint {
    pub ttl_seconds: u64,
    pub cache_level: CacheLevel,
    pub invalidation_triggers: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum CacheLevel {
    L1Memory,    // Hot cache
    L2Compressed, // Warm cache
    L3Disk,      // Cold cache
    NoCache,     // Don't cache
}

/// Optimization pattern
struct OptimizationPattern {
    regex: Regex,
    replacement: String,
    cache_hint: Option<CacheLevel>,
}

/// Command optimizer for Nix commands
pub struct CommandOptimizer {
    flags_map: HashMap<String, Vec<String>>,
}

impl CommandOptimizer {
    pub fn new() -> Self {
        CommandOptimizer {
            flags_map: build_flags_map(),
        }
    }

    /// Optimize a Nix command for performance
    pub fn optimize_command(&self, mut cmd: Vec<String>) -> Vec<String> {
        if cmd.is_empty() {
            return cmd;
        }

        let command = cmd[0].clone();
        
        // Add JSON output flag if applicable
        if should_add_json_flag(&command) && !cmd.contains(&"--json".to_string()) {
            cmd.push("--json".to_string());
        }

        // Add performance flags
        if let Some(flags) = self.flags_map.get(command.as_str()) {
            for flag in flags {
                if !cmd.contains(flag) {
                    cmd.push(flag.clone());
                }
            }
        }

        // Optimize specific commands
        match command.as_str() {
            "nix-env" => {
                // Use nix profile instead when possible
                if cmd.contains(&"-iA".to_string()) {
                    // Convert to nix profile install
                    let mut new_cmd = vec!["nix".to_string(), "profile".to_string(), "install".to_string()];
                    if let Some(pkg_idx) = cmd.iter().position(|s| s == "-iA") {
                        if pkg_idx + 1 < cmd.len() {
                            new_cmd.push(format!("nixpkgs#{}", cmd[pkg_idx + 1]));
                        }
                    }
                    return new_cmd;
                }
            },
            "nix-channel" => {
                // Add --no-net flag for list operations
                if cmd.contains(&"--list".to_string()) && !cmd.contains(&"--no-net".to_string()) {
                    cmd.push("--no-net".to_string());
                }
            },
            _ => {}
        }

        cmd
    }

    /// Batch multiple commands for efficiency
    pub fn batch_commands(&self, commands: Vec<Vec<String>>) -> Vec<BatchedCommand> {
        let mut batches = Vec::new();
        let mut current_batch = Vec::new();
        let mut current_type = None;

        for cmd in commands {
            if cmd.is_empty() {
                continue;
            }

            let cmd_type = classify_command(&cmd[0]);
            
            if current_type.is_none() {
                current_type = Some(cmd_type.clone());
            }

            if Some(&cmd_type) == current_type.as_ref() && can_batch(&cmd_type) {
                current_batch.push(cmd);
            } else {
                if !current_batch.is_empty() {
                    batches.push(BatchedCommand {
                        commands: current_batch.clone(),
                        parallel: can_parallelize(&current_type.as_ref().unwrap()),
                    });
                }
                current_batch = vec![cmd];
                current_type = Some(cmd_type);
            }
        }

        if !current_batch.is_empty() {
            batches.push(BatchedCommand {
                commands: current_batch,
                parallel: can_parallelize(&current_type.as_ref().unwrap()),
            });
        }

        batches
    }
}

/// Batched commands for execution
#[derive(Debug, Clone)]
pub struct BatchedCommand {
    pub commands: Vec<Vec<String>>,
    pub parallel: bool,
}

#[derive(Debug, Clone, PartialEq)]
enum CommandType {
    Query,
    Mutation,
    System,
}

// Helper functions

fn normalize_query(query: &str) -> String {
    query.trim()
        .to_lowercase()
        .replace("please", "")
        .replace("could you", "")
        .replace("can you", "")
        .replace("i want to", "")
        .replace("i need to", "")
        .replace("  ", " ")
        .trim()
        .to_string()
}

fn detect_intent(query: &str) -> Intent {
    let normalized = query.to_lowercase();
    
    if normalized.contains("install") || normalized.contains("add") {
        Intent::Install
    } else if normalized.contains("uninstall") || normalized.contains("remove") {
        Intent::Uninstall
    } else if normalized.contains("search") || normalized.contains("find") {
        Intent::Search
    } else if normalized.contains("list") || normalized.contains("show") {
        Intent::List
    } else if normalized.contains("update") || normalized.contains("upgrade") {
        Intent::Update
    } else if normalized.contains("config") || normalized.contains("setup") {
        Intent::Configure
    } else if normalized.contains("help") || normalized.contains("how") {
        Intent::Help
    } else if normalized.contains("what") || normalized.contains("info") {
        Intent::Query
    } else {
        Intent::Unknown
    }
}

fn extract_entities(query: &str) -> Vec<Entity> {
    let mut entities = Vec::new();
    let words: Vec<&str> = query.split_whitespace().collect();
    
    for (i, word) in words.iter().enumerate() {
        // Package names (simple heuristic)
        if i > 0 && (words[i-1] == "install" || words[i-1] == "search") {
            entities.push(Entity {
                entity_type: EntityType::Package,
                value: word.to_string(),
                confidence: 0.9,
            });
        }
        
        // Service names
        if word.ends_with(".service") || (i > 0 && words[i-1] == "service") {
            entities.push(Entity {
                entity_type: EntityType::Service,
                value: word.replace(".service", ""),
                confidence: 0.8,
            });
        }
    }
    
    entities
}

fn should_use_json(query: &str) -> bool {
    query.contains("search") || 
    query.contains("list") || 
    query.contains("info") ||
    query.contains("show")
}

fn is_parallel_safe(query: &str) -> bool {
    !query.contains("install") && 
    !query.contains("uninstall") &&
    !query.contains("update") &&
    !query.contains("switch")
}

fn estimate_time(query: &str) -> u32 {
    if query.contains("search") {
        500 // ms
    } else if query.contains("list") {
        200
    } else if query.contains("install") {
        5000
    } else if query.contains("update") {
        10000
    } else {
        1000
    }
}

fn generate_cache_key(query: &str) -> String {
    use blake3::Hasher;
    let mut hasher = Hasher::new();
    hasher.update(query.as_bytes());
    hasher.finalize().to_hex()[..16].to_string()
}

fn build_optimization_patterns() -> Vec<OptimizationPattern> {
    vec![
        OptimizationPattern {
            regex: Regex::new(r"search for (.+)").unwrap(),
            replacement: "search $1".to_string(),
            cache_hint: Some(CacheLevel::L1Memory),
        },
        OptimizationPattern {
            regex: Regex::new(r"find (.+) package").unwrap(),
            replacement: "search $1".to_string(),
            cache_hint: Some(CacheLevel::L1Memory),
        },
    ]
}

fn build_cache_hints() -> HashMap<String, CacheHint> {
    let mut hints = HashMap::new();
    
    hints.insert("search".to_string(), CacheHint {
        ttl_seconds: 3600,
        cache_level: CacheLevel::L1Memory,
        invalidation_triggers: vec!["update".to_string()],
    });
    
    hints.insert("list".to_string(), CacheHint {
        ttl_seconds: 300,
        cache_level: CacheLevel::L2Compressed,
        invalidation_triggers: vec!["install".to_string(), "uninstall".to_string()],
    });
    
    hints
}

fn build_flags_map() -> HashMap<String, Vec<String>> {
    let mut map = HashMap::new();
    
    map.insert("nix".to_string(), vec![
        "--extra-experimental-features".to_string(),
        "nix-command flakes".to_string(),
    ]);
    
    map.insert("nix-env".to_string(), vec![
        "--prebuilt-only".to_string(),
    ]);
    
    map
}

fn should_add_json_flag(command: &str) -> bool {
    matches!(command, "nix" | "nix-env" | "nixos-rebuild")
}

fn classify_command(command: &str) -> CommandType {
    match command {
        "nix" | "nix-env" | "nix-channel" => CommandType::Query,
        "nixos-rebuild" | "nix-collect-garbage" => CommandType::System,
        _ => CommandType::Mutation,
    }
}

fn can_batch(cmd_type: &CommandType) -> bool {
    matches!(cmd_type, CommandType::Query)
}

fn can_parallelize(cmd_type: &CommandType) -> bool {
    matches!(cmd_type, CommandType::Query)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_query_optimization() {
        let optimizer = QueryOptimizer::new();
        let optimized = optimizer.optimize_query("please search for firefox browser");
        
        assert_eq!(optimized.intent, Intent::Search);
        assert!(optimized.json_output);
        assert!(optimized.parallel_safe);
    }

    #[test]
    fn test_command_optimization() {
        let optimizer = CommandOptimizer::new();
        let cmd = vec!["nix".to_string(), "search".to_string(), "firefox".to_string()];
        let optimized = optimizer.optimize_command(cmd);
        
        assert!(optimized.contains(&"--json".to_string()));
    }

    #[test]
    fn test_entity_extraction() {
        let entities = extract_entities("install firefox and chromium");
        
        assert_eq!(entities.len(), 2);
        assert_eq!(entities[0].value, "firefox");
        assert_eq!(entities[1].value, "and"); // Simple extraction, would need improvement
    }
}