//! Brain Module - Physiological Systems
//!
//! Week 0: Actor Model Foundation
//! Week 1 Days 1-2: Thalamus (Sensory Relay)
//! Week 2 Days 3-4: Cerebellum (Procedural Memory)
//! Week 2 Days 5-7: Motor Cortex (Action Execution)
//! Week 3 Days 1-2: Prefrontal Cortex (Global Workspace)

pub mod actor_model;
pub mod thalamus;
pub mod cerebellum;
pub mod motor_cortex;
pub mod prefrontal;

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
pub use motor_cortex::{
    MotorCortexActor,
    ActionStep,
    PlannedAction,
    StepResult,
    ExecutionResult,
    SimulationMode,
    ExecutionSandbox,
    LocalShellSandbox,
    MotorCortexStats,
};
pub use prefrontal::{
    PrefrontalCortexActor,
    AttentionBid,
    GlobalWorkspace,
    WorkingMemoryItem,
    PrefrontalStats,
    WorkingMemoryStats,
};
