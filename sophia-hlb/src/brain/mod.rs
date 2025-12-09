//! Brain Module - Physiological Systems
//!
//! Week 0: Actor Model Foundation
//! Future Weeks: Thalamus, Amygdala, Cerebellum, etc.

pub mod actor_model;

pub use actor_model::{
    Actor,
    ActorPriority,
    CognitiveRoute,
    Orchestrator,
    OrganMessage,
    Response,
    SharedVector,
};
