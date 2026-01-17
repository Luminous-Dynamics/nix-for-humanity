/*!
Safety Gateway - Unified Safety Interface

Provides a single facade over the different safety subsystems:
- AmygdalaActor: fast regex-based pre-cognitive veto
- SafetyGuardrails: hypervector-based forbidden subspace checking

This module does not execute actions itself. Instead it provides a
consistent, structured way for callers to ask:

- "Is this text safe?"
- "Is this command safe?"
- "Is this planned ActionIR safe?"
*/

use crate::action::ActionIR;
use super::{AmygdalaActor, SafetyGuardrails, ForbiddenCategory};

/// What kind of thing is being checked for safety
#[derive(Debug)]
pub enum SafetyCheck<'a> {
    /// Natural language text (queries, prompts)
    Query(&'a str),
    /// Concrete shell / Nix command string
    Command(&'a str),
    /// Planned side-effect encoded as ActionIR
    Action(&'a ActionIR),
}

/// Structured safety decision
#[derive(Debug, Clone)]
pub struct SafetyDecision {
    /// Whether the input is allowed to proceed
    pub allowed: bool,
    /// Human-readable explanation (if any)
    pub message: Option<String>,
    /// High-level forbidden category (if matched)
    pub category: Option<ForbiddenCategory>,
}

impl SafetyDecision {
    /// Convenience helper: allowed without message or category
    pub fn allowed() -> Self {
        Self {
            allowed: true,
            message: None,
            category: None,
        }
    }

    /// Convenience helper: blocked with message and optional category
    pub fn blocked(message: String, category: Option<ForbiddenCategory>) -> Self {
        Self {
            allowed: false,
            message: Some(message),
            category,
        }
    }
}

/// SafetyGateway ties together fast-path regex safety and slower
/// hypervector-based guardrails into a single interface.
#[derive(Debug)]
pub struct SafetyGateway {
    amygdala: AmygdalaActor,
    guardrails: SafetyGuardrails,
}

impl SafetyGateway {
    /// Create a new gateway with default Amygdala and guardrail configuration
    pub fn new() -> Self {
        Self {
            amygdala: AmygdalaActor::new(),
            guardrails: SafetyGuardrails::new(),
        }
    }

    /// Check any supported input for safety
    pub fn check(&mut self, what: SafetyCheck<'_>) -> SafetyDecision {
        match what {
            SafetyCheck::Query(text) => self.check_text(text),
            SafetyCheck::Command(cmd) => self.check_command(cmd),
            SafetyCheck::Action(action) => self.check_action(action),
        }
    }

    /// Safety check for natural language text
    fn check_text(&mut self, text: &str) -> SafetyDecision {
        // Layer 1: Amygdala fast-path veto (regex-based)
        if let Some(msg) = self.amygdala.scan(text) {
            return SafetyDecision::blocked(msg, None);
        }

        // Layer 2: Hypervector guardrails
        // NOTE: The caller is responsible for encoding text into a bipolar
        // hypervector and calling guardrails directly. This method currently
        // only runs the textual scan to keep the API simple.
        //
        // In future iterations, this gateway can be extended to also accept
        // a semantic encoder or pre-encoded pattern for deeper checks.

        SafetyDecision::allowed()
    }

    /// Safety check for raw commands (bash/nix)
    fn check_command(&mut self, command: &str) -> SafetyDecision {
        if let Some(msg) = self.amygdala.scan(command) {
            return SafetyDecision::blocked(msg, None);
        }

        SafetyDecision::allowed()
    }

    /// Safety check for planned side-effects (ActionIR)
    fn check_action(&mut self, _action: &ActionIR) -> SafetyDecision {
        // Placeholder: ActionIR-aware safety can be added here by
        // inspecting paths, programs, and risk tiers.
        //
        // For now, return allowed() so that callers can rely on a
        // consistent interface even before policy is fully wired.
        SafetyDecision::allowed()
    }
}

