//! Safety module - safety constraints and gateways
//!
//! Provides safety checking capabilities including:
//! - Fast regex-based pre-cognitive veto (AmygdalaActor)
//! - Hypervector-based forbidden subspace checking (SafetyGuardrails)
//! - Unified safety gateway interface

pub mod gateway;

// Re-export key types
pub use gateway::{SafetyGateway, SafetyDecision, SafetyCheck};

/// Categories of forbidden content/actions
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ForbiddenCategory {
    /// Dangerous system commands
    DangerousCommand,
    /// Harmful content
    HarmfulContent,
    /// Privacy violation
    PrivacyViolation,
    /// Security risk
    SecurityRisk,
    /// Unethical request
    UnethicalRequest,
}

/// Fast regex-based pre-cognitive safety veto
///
/// Acts like the amygdala - fast, pattern-matching safety check
/// before deeper processing occurs.
#[derive(Debug)]
pub struct AmygdalaActor {
    /// Dangerous command patterns
    dangerous_patterns: Vec<regex::Regex>,
}

impl AmygdalaActor {
    /// Create a new AmygdalaActor with default dangerous patterns
    pub fn new() -> Self {
        let patterns = vec![
            // Destructive commands
            r"rm\s+-rf\s+/",
            r"dd\s+if=.*of=/dev/",
            r"mkfs\.",
            r":(){ :|:& };:",  // Fork bomb
            r"chmod\s+-R\s+777\s+/",
            r">\s*/dev/sd",
        ];

        let dangerous_patterns = patterns
            .into_iter()
            .filter_map(|p| regex::Regex::new(p).ok())
            .collect();

        Self { dangerous_patterns }
    }

    /// Scan text for dangerous patterns
    /// Returns Some(message) if dangerous, None if safe
    pub fn scan(&self, text: &str) -> Option<String> {
        for pattern in &self.dangerous_patterns {
            if pattern.is_match(text) {
                return Some(format!(
                    "Blocked: Dangerous pattern detected matching '{}'",
                    pattern.as_str()
                ));
            }
        }
        None
    }
}

impl Default for AmygdalaActor {
    fn default() -> Self {
        Self::new()
    }
}

/// Hypervector-based safety guardrails
///
/// Uses hyperdimensional computing to check if content falls
/// within forbidden semantic subspaces.
#[derive(Debug)]
#[allow(dead_code)] // Fields reserved for HDC safety checks
pub struct SafetyGuardrails {
    /// Dimension of hypervectors
    dimension: usize,
    /// Whether guardrails are active
    active: bool,
}

impl SafetyGuardrails {
    /// Create new safety guardrails
    pub fn new() -> Self {
        Self {
            dimension: 512,
            active: true,
        }
    }

    /// Check if a hypervector falls within forbidden subspace
    ///
    /// Currently a placeholder - returns None (safe) for all inputs.
    /// Full implementation would compare against forbidden category prototypes.
    pub fn check(&self, _hv: &[f32]) -> Option<ForbiddenCategory> {
        if !self.active {
            return None;
        }

        // Placeholder: semantic safety checking would go here
        // Compare input HV similarity to forbidden category prototypes
        None
    }

    /// Enable or disable guardrails
    pub fn set_active(&mut self, active: bool) {
        self.active = active;
    }
}

impl Default for SafetyGuardrails {
    fn default() -> Self {
        Self::new()
    }
}
