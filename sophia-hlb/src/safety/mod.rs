//! Safety Module - Multi-Layer Defense Systems
//!
//! Week 1 Days 3-4: Amygdala (Visceral Safety) - Fast regex-based pre-cognitive defense
//! Phase 10/11: SafetyGuardrails (Semantic Safety) - HDC-based hypervector safety
//! Future: Digital Thymus (Immune System), Semantic T-Cells

pub mod amygdala;
pub mod guardrails;

pub use amygdala::{AmygdalaActor, ThreatLevel};
pub use guardrails::{SafetyGuardrails, ForbiddenCategory, SafetyStats};
