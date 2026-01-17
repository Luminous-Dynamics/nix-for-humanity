//! Physiology module - biological/hormonal systems
//!
//! Models the physiological aspects of consciousness:
//! - Coherence field (synchronization/integration)
//! - Endocrine system (hormonal influences)

pub mod coherence;
pub mod endocrine;

// Re-exports for convenience
pub use coherence::{CoherenceField, CoherenceConfig, CoherenceState};
pub use endocrine::HormoneState;
