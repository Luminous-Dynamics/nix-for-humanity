//! Language module - natural language processing and generation
//!
//! Core language capabilities including:
//! - Emotional analysis and response generation
//! - LLM orchestration
//! - Domain-agnostic plugin system
//! - NixOS configuration parsing (via plugin)
//! - Consciousness monitoring

// Core working modules
pub mod consciousness_prompts;
pub mod domain_plugin;
pub mod emotional_core;
pub mod llm_backend;
pub mod llm_organ;
pub mod nix_parser;
pub mod phi_monitor;

// Modules needing HDC submodules that don't exist yet (cfg-gated)
#[cfg(feature = "full_language")]
pub mod generative_thought_engine;
#[cfg(feature = "full_language")]
pub mod learning_persistence;
#[cfg(feature = "full_language")]
pub mod meta_conscious_llm_bridge;

// Enhanced modules (need API alignment - cfg-gated)
#[cfg(feature = "full_language")]
pub mod enhanced_consciousness;
#[cfg(feature = "full_language")]
pub mod multi_theory_consciousness;
#[cfg(feature = "full_language")]
pub mod semantic_enrichment;

// Re-exports
pub use domain_plugin::{DomainPlugin, Entity, RiskLevel, ErrorLocation, IntentPrototypes, DomainPrompts, ValidationResult, PluginRegistry, GenericPlugin};
pub use domain_plugin::ErrorDiagnosis as DomainErrorDiagnosis;
pub use emotional_core::{EmotionalCore, EmotionalCoreConfig, EmotionalAnalysis, EmotionalResponse};
pub use llm_organ::{LLMOrgan, LLMOrganConfig, ConversationMessage, MessageRole, LLMGenerationResult, LLMQuery, QueryType, TRANSLATION_SYSTEM_PROMPT};
pub use nix_parser::{NixParser, NixConfig, NixOption, NixValue};
// Export backend module for creating custom backends
pub use llm_backend::{OllamaBackend, SimulatedBackend, LLMBackend, default_backend, simulated_backend};

// ============================================================================
// NixOS Error Diagnoser (for shell module integration)
// ============================================================================

/// Categories of NixOS errors
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NixErrorCategory {
    /// Evaluation errors (undefined variables, type errors)
    Evaluation,
    /// Build failures
    Build,
    /// Conflicting options or packages
    Conflict,
    /// Missing resources (packages, files)
    MissingResource,
    /// Permission errors
    Permission,
    /// Flake-specific errors
    Flake,
    /// Unknown error
    Unknown,
}

impl NixErrorCategory {
    /// Get the category name as a string
    pub fn name(&self) -> &'static str {
        match self {
            Self::Evaluation => "Evaluation Error",
            Self::Build => "Build Error",
            Self::Conflict => "Conflict Error",
            Self::MissingResource => "Missing Resource",
            Self::Permission => "Permission Error",
            Self::Flake => "Flake Error",
            Self::Unknown => "Unknown Error",
        }
    }
}

/// Specific types of NixOS errors
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NixErrorType {
    /// Missing semicolon
    MissingSemicolon,
    /// Undefined variable
    UndefinedVariable(String),
    /// Type mismatch
    TypeMismatch { expected: String, found: String },
    /// Missing attribute
    MissingAttribute(String),
    /// Package not found
    PackageNotFound(String),
    /// Build failed
    BuildFailed(String),
    /// Infinite recursion
    InfiniteRecursion,
    /// Hash mismatch
    HashMismatch,
    /// Network error
    NetworkError(String),
    /// Other error
    Other(String),
}

impl NixErrorType {
    /// Get the error type name as a string
    pub fn name(&self) -> &str {
        match self {
            Self::MissingSemicolon => "Missing Semicolon",
            Self::UndefinedVariable(_v) => "Undefined Variable",
            Self::TypeMismatch { .. } => "Type Mismatch",
            Self::MissingAttribute(_) => "Missing Attribute",
            Self::PackageNotFound(_) => "Package Not Found",
            Self::BuildFailed(_) => "Build Failed",
            Self::InfiniteRecursion => "Infinite Recursion",
            Self::HashMismatch => "Hash Mismatch",
            Self::NetworkError(_) => "Network Error",
            Self::Other(_) => "Error",
        }
    }
}

/// Risk level for suggested fixes
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Default)]
pub enum FixRiskLevel {
    /// Safe to apply automatically
    #[default]
    Safe,
    /// Low risk, review recommended
    Low,
    /// Medium risk, careful review needed
    Medium,
    /// High risk, manual intervention recommended
    High,
    /// Critical risk, expert review required
    Critical,
}

/// A suggested fix for an error
#[derive(Debug, Clone)]
pub struct SuggestedFix {
    /// Description of what this fix does
    pub description: String,
    /// Command to run (if applicable)
    pub command: Option<String>,
    /// Risk level of applying this fix
    pub risk: FixRiskLevel,
    /// Confidence that this fix will work (0.0-1.0)
    pub confidence: f32,
    /// Whether this is the primary/recommended fix
    pub primary: bool,
}

/// Diagnosis result from error analysis
#[derive(Debug, Clone)]
pub struct ErrorDiagnosis {
    /// Error category
    pub category: NixErrorCategory,
    /// Specific error type
    pub error_type: NixErrorType,
    /// Human-readable explanation
    pub explanation: String,
    /// Likely causes (ordered by probability)
    pub likely_causes: Vec<String>,
    /// Suggested fixes
    pub fixes: Vec<SuggestedFix>,
    /// File location if known
    pub location: Option<String>,
    /// Affected configuration paths
    pub affected_configs: Vec<String>,
    /// Confidence in diagnosis (0.0-1.0)
    pub confidence: f32,
}

/// NixOS error diagnoser
#[derive(Debug)]
pub struct NixErrorDiagnoser {
    /// Known error patterns
    patterns: Vec<ErrorPattern>,
}

#[derive(Debug)]
struct ErrorPattern {
    regex: regex::Regex,
    category: NixErrorCategory,
    explanation_template: String,
}

impl NixErrorDiagnoser {
    /// Create a new error diagnoser
    pub fn new() -> Self {
        let patterns = vec![
            ErrorPattern {
                regex: regex::Regex::new(r"error: syntax error, unexpected").unwrap(),
                category: NixErrorCategory::Evaluation,
                explanation_template: "Syntax error in Nix expression".to_string(),
            },
            ErrorPattern {
                regex: regex::Regex::new(r"undefined variable '(\w+)'").unwrap(),
                category: NixErrorCategory::Evaluation,
                explanation_template: "Variable is not defined in scope".to_string(),
            },
            ErrorPattern {
                regex: regex::Regex::new(r"attribute '(\w+)' missing").unwrap(),
                category: NixErrorCategory::Evaluation,
                explanation_template: "Required attribute is missing".to_string(),
            },
            ErrorPattern {
                regex: regex::Regex::new(r"error: hash mismatch").unwrap(),
                category: NixErrorCategory::Build,
                explanation_template: "Downloaded file hash doesn't match expected".to_string(),
            },
            ErrorPattern {
                regex: regex::Regex::new(r"builder.*failed").unwrap(),
                category: NixErrorCategory::Build,
                explanation_template: "Package build process failed".to_string(),
            },
            ErrorPattern {
                regex: regex::Regex::new(r"permission denied").unwrap(),
                category: NixErrorCategory::Permission,
                explanation_template: "Insufficient permissions for this operation".to_string(),
            },
            ErrorPattern {
                regex: regex::Regex::new(r"flake.*error|error.*flake").unwrap(),
                category: NixErrorCategory::Flake,
                explanation_template: "Flake configuration error".to_string(),
            },
        ];

        Self { patterns }
    }

    /// Diagnose an error from output text
    pub fn diagnose(&self, error_text: &str) -> ErrorDiagnosis {
        for pattern in &self.patterns {
            if pattern.regex.is_match(error_text) {
                return ErrorDiagnosis {
                    category: pattern.category,
                    error_type: NixErrorType::Other(error_text.lines().next().unwrap_or("").to_string()),
                    explanation: pattern.explanation_template.clone(),
                    likely_causes: vec!["See error message for details".to_string()],
                    fixes: vec![],
                    location: self.extract_location(error_text),
                    affected_configs: vec![],
                    confidence: 0.70,
                };
            }
        }

        // Default unknown error
        ErrorDiagnosis {
            category: NixErrorCategory::Unknown,
            error_type: NixErrorType::Other(error_text.lines().next().unwrap_or("Unknown error").to_string()),
            explanation: "Could not automatically diagnose this error".to_string(),
            likely_causes: vec!["Error pattern not recognized".to_string()],
            fixes: vec![],
            location: self.extract_location(error_text),
            affected_configs: vec![],
            confidence: 0.20,
        }
    }

    /// Extract file location from error text
    fn extract_location(&self, error_text: &str) -> Option<String> {
        // Look for patterns like "at /path/to/file.nix:123:45"
        let location_re = regex::Regex::new(r"at\s+(/[^:]+):(\d+):(\d+)").ok()?;
        if let Some(caps) = location_re.captures(error_text) {
            return Some(format!("{}:{}:{}", &caps[1], &caps[2], &caps[3]));
        }
        None
    }
}

impl Default for NixErrorDiagnoser {
    fn default() -> Self {
        Self::new()
    }
}

// ============================================================================
// CONSCIOUSNESS LANGUAGE TYPES (for integration_module compatibility)
// ============================================================================
// The integration module expects these types for conscious language processing.
// These are stub implementations to enable module compilation.

use symthaea_core::hdc::RealHV;

/// Consciousness state level for language processing
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum ConsciousnessStateLevel {
    /// Minimal awareness
    #[default]
    Dormant,
    /// Basic reactive awareness
    Reactive,
    /// Active processing awareness
    Active,
    /// Deep reflective awareness
    Reflective,
    /// Full metacognitive awareness
    Metacognitive,
}

/// Consciousness quadrant for integrated processing
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum ConsciousnessQuadrant {
    /// Analytical/logical processing
    #[default]
    Analytical,
    /// Intuitive/pattern processing
    Intuitive,
    /// Emotional/affective processing
    Emotional,
    /// Somatic/embodied processing
    Somatic,
}

/// Execution strategy type for NixOS commands
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum ExecutionStrategyType {
    /// Direct execution
    #[default]
    Direct,
    /// Staged/phased execution
    Staged,
    /// Dry-run first
    DryRun,
    /// Interactive confirmation
    Interactive,
    /// Batch execution
    Batch,
}

/// Execution strategy with parameters
#[derive(Debug, Clone, Default)]
pub struct ExecutionStrategy {
    /// Strategy type
    pub strategy_type: ExecutionStrategyType,
    /// Risk level assessment
    pub risk_level: FixRiskLevel,
    /// Confidence in strategy
    pub confidence: f32,
    /// Required confirmations
    pub confirmations_needed: usize,
    /// Rollback plan available
    pub has_rollback: bool,
}

impl ExecutionStrategy {
    /// Create a safe default strategy
    pub fn safe_default() -> Self {
        Self {
            strategy_type: ExecutionStrategyType::DryRun,
            risk_level: FixRiskLevel::Safe,
            confidence: 0.95,
            confirmations_needed: 0,
            has_rollback: true,
        }
    }
}

/// A clarifying question to gather more information
#[derive(Debug, Clone)]
pub struct ClarifyingQuestion {
    /// The question text
    pub question: String,
    /// Why this question matters
    pub rationale: String,
    /// Possible answer options (if applicable)
    pub options: Vec<String>,
    /// Priority of this question
    pub priority: u8,
    /// Default answer if user skips
    pub default: Option<String>,
}

/// Understanding of NixOS-specific intent
#[derive(Debug, Clone, Default)]
pub struct NixOSIntent {
    /// Primary action (install, remove, configure, etc.)
    pub action: String,
    /// Target packages or options
    pub targets: Vec<String>,
    /// Configuration scope (user, system, flake)
    pub scope: String,
    /// Whether this is a query or mutation
    pub is_query: bool,
    /// Confidence in intent recognition
    pub confidence: f32,
}

/// Understanding result for NixOS queries
#[derive(Debug, Clone, Default)]
pub struct NixOSUnderstanding {
    /// Recognized intent
    pub intent: NixOSIntent,
    /// Extracted entities (packages, options, paths)
    pub entities: Vec<String>,
    /// Relevant context
    pub context: String,
    /// Any ambiguities detected
    pub ambiguities: Vec<String>,
    /// Suggested clarifications
    pub clarifications: Vec<ClarifyingQuestion>,
}

/// Feedback from action execution
#[derive(Debug, Clone)]
pub struct ActionOutcomeFeedback {
    /// Whether the action succeeded
    pub success: bool,
    /// Execution time in milliseconds
    pub execution_time_ms: u64,
    /// User satisfaction (if provided)
    pub user_satisfaction: Option<f32>,
    /// Any errors encountered
    pub errors: Vec<String>,
    /// Lessons learned
    pub lessons: Vec<String>,
}

impl Default for ActionOutcomeFeedback {
    fn default() -> Self {
        Self {
            success: true,
            execution_time_ms: 0,
            user_satisfaction: None,
            errors: Vec::new(),
            lessons: Vec::new(),
        }
    }
}

/// Result from conscious understanding process
#[derive(Debug, Clone)]
pub struct ConsciousUnderstandingResult {
    /// NixOS-specific understanding
    pub nixos: NixOSUnderstanding,
    /// Emotional context
    pub emotional_context: Option<EmotionalAnalysis>,
    /// Consciousness state during processing
    pub consciousness_state: ConsciousnessStateLevel,
    /// Active quadrants
    pub active_quadrants: Vec<ConsciousnessQuadrant>,
    /// Embedding representation
    pub embedding: Option<RealHV>,
    /// Processing confidence
    pub confidence: f32,
    /// Recommended strategy
    pub recommended_strategy: ExecutionStrategy,
}

impl Default for ConsciousUnderstandingResult {
    fn default() -> Self {
        Self {
            nixos: NixOSUnderstanding::default(),
            emotional_context: None,
            consciousness_state: ConsciousnessStateLevel::Active,
            active_quadrants: vec![ConsciousnessQuadrant::Analytical],
            embedding: None,
            confidence: 0.5,
            recommended_strategy: ExecutionStrategy::safe_default(),
        }
    }
}

/// Configuration for consciousness language core
#[derive(Debug, Clone)]
pub struct ConsciousnessLanguageConfig {
    /// Embedding dimension
    pub dimension: usize,
    /// Enable emotional processing
    pub emotional_enabled: bool,
    /// Enable metacognitive reflection
    pub metacognition_enabled: bool,
    /// LLM configuration
    pub llm_config: LLMOrganConfig,
    /// Minimum confidence threshold
    pub confidence_threshold: f32,
}

impl Default for ConsciousnessLanguageConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            emotional_enabled: true,
            metacognition_enabled: true,
            llm_config: LLMOrganConfig::default(),
            confidence_threshold: 0.6,
        }
    }
}

/// Core consciousness language processor
#[derive(Debug)]
#[allow(dead_code)] // Fields reserved for language processing
pub struct ConsciousnessLanguageCore {
    /// Configuration
    config: ConsciousnessLanguageConfig,
    /// LLM organ for generation
    llm: LLMOrgan,
    /// Emotional processor
    emotional: EmotionalCore,
    /// Current consciousness state
    state: ConsciousnessStateLevel,
    /// Error diagnoser
    diagnoser: NixErrorDiagnoser,
}

impl ConsciousnessLanguageCore {
    /// Create a new consciousness language core
    pub fn new(config: ConsciousnessLanguageConfig) -> Self {
        Self {
            llm: LLMOrgan::new(config.llm_config.clone()),
            emotional: EmotionalCore::new(EmotionalCoreConfig::default()),
            state: ConsciousnessStateLevel::Active,
            diagnoser: NixErrorDiagnoser::new(),
            config,
        }
    }

    /// Process input with consciousness awareness
    pub fn understand(&mut self, input: &str) -> ConsciousUnderstandingResult {
        // Basic understanding flow
        let emotional_context = if self.config.emotional_enabled {
            Some(self.emotional.analyze(input))
        } else {
            None
        };

        // Extract NixOS intent (simplified)
        let intent = self.extract_nixos_intent(input);

        let nixos = NixOSUnderstanding {
            intent,
            entities: self.extract_entities(input),
            context: input.to_string(),
            ambiguities: Vec::new(),
            clarifications: Vec::new(),
        };

        ConsciousUnderstandingResult {
            nixos,
            emotional_context,
            consciousness_state: self.state,
            active_quadrants: vec![ConsciousnessQuadrant::Analytical],
            embedding: None,
            confidence: 0.75,
            recommended_strategy: ExecutionStrategy::safe_default(),
        }
    }

    /// Extract NixOS intent from text
    fn extract_nixos_intent(&self, text: &str) -> NixOSIntent {
        let lower = text.to_lowercase();

        let (action, is_query) = if lower.contains("install") {
            ("install".to_string(), false)
        } else if lower.contains("remove") || lower.contains("uninstall") {
            ("remove".to_string(), false)
        } else if lower.contains("search") || lower.contains("find") {
            ("search".to_string(), true)
        } else if lower.contains("update") || lower.contains("upgrade") {
            ("update".to_string(), false)
        } else if lower.contains("configure") || lower.contains("setup") {
            ("configure".to_string(), false)
        } else if lower.contains("list") || lower.contains("show") {
            ("list".to_string(), true)
        } else {
            ("unknown".to_string(), true)
        };

        NixOSIntent {
            action,
            targets: self.extract_entities(text),
            scope: "system".to_string(),
            is_query,
            confidence: 0.7,
        }
    }

    /// Extract entities (packages, options) from text
    fn extract_entities(&self, text: &str) -> Vec<String> {
        // Simple word extraction - would use NLP in production
        text.split_whitespace()
            .filter(|w| w.len() > 2 && !["the", "and", "for", "with", "from", "install", "remove", "search"].contains(w))
            .map(|s| s.to_string())
            .collect()
    }

    /// Diagnose an error with consciousness awareness
    pub fn diagnose_error(&self, error: &str) -> ErrorDiagnosis {
        self.diagnoser.diagnose(error)
    }

    /// Get current consciousness state
    pub fn consciousness_state(&self) -> ConsciousnessStateLevel {
        self.state
    }

    /// Set consciousness state
    pub fn set_consciousness_state(&mut self, state: ConsciousnessStateLevel) {
        self.state = state;
    }

    /// Process feedback to improve
    pub fn process_feedback(&mut self, _feedback: ActionOutcomeFeedback) {
        // Would update internal models based on feedback
        // Stub implementation
    }
}

impl Default for ConsciousnessLanguageCore {
    fn default() -> Self {
        Self::new(ConsciousnessLanguageConfig::default())
    }
}

// Note: Types defined above are automatically public since they're
// declared with `pub`. No need for re-export.
