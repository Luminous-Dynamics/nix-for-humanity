//! Brain Module - Physiological Systems
//!
//! Week 0: Actor Model Foundation
//! Week 1 Days 1-2: Thalamus (Sensory Relay)
//! Week 2 Days 3-4: Cerebellum (Procedural Memory)

pub mod actor_model;
pub mod thalamus;
pub mod cerebellum;

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
pub use cerebellum::{CerebellumActor, Skill, ExecutionContext, WorkflowChain, CerebellumStats};
