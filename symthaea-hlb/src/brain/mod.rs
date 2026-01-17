//! Brain module - neural architecture components
//!
//! This module provides brain-inspired components including:
//! - Prefrontal cortex (executive functions, working memory)
//! - Actor model (concurrent neural processing)
//! - Social coherence (theory of mind, cooperation)
//! - Various bridge modules for integration

pub mod affective_bridge;
pub mod actor_model;
pub mod consciousness_bridge;
pub mod dark_spot_actor;
pub mod hippocampus_bridge;
pub mod prefrontal;
pub mod social_coherence;

// Re-export key types
pub use prefrontal::{PrefrontalCortex, PrefrontalConfig, WorkingMemoryItem, PlannedAction, ExecutiveDecision};
pub use actor_model::{ActorSystem, Actor, ActorId, ActorRole, ActorMessage, MessageType};
pub use social_coherence::{SocialCoherence, SocialCoherenceConfig, MentalModel, Relationship, RelationshipType};
