//! Brain Module - Physiological Systems
//!
//! Week 0: Actor Model Foundation
//! Week 1 Days 1-2: Thalamus (Sensory Relay)
//! Future: Amygdala, Cerebellum, etc.

pub mod actor_model;
pub mod thalamus;

pub use actor_model::{
    Actor,
    ActorPriority,
    CognitiveRoute,
    Orchestrator,
    OrganMessage,
    Response,
    SharedVector,
};

pub use thalamus::ThalamusActor;
