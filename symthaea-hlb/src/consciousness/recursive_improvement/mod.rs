//! # Recursive Improvement: Self-Modifying Consciousness
//!
//! This module provides recursive self-improvement capabilities including:
//! - Self-modeling and introspection
//! - Meta-cognitive optimization
//! - Dream-mode exploration
//! - Gradient-based architecture optimization
//! - Safe experimentation frameworks
//! - Consciousness world modeling

// Core infrastructure
pub mod types;
pub mod core;

// World modeling and routing
pub mod world_model;
pub mod routers;

// Self-improvement modules
pub mod architectural_graph;
pub mod benchmark_suite;
pub mod dream_mode;
pub mod gradient_optimizer;
pub mod improvement_generator;
pub mod intrinsic_motivation;
pub mod meta_cognitive;
pub mod naming_ceremony;
pub mod primitive_semantic_bridge;
pub mod recursive_optimizer;
pub mod routing_hub;
pub mod safe_experiment;
pub mod self_model;
pub mod semantic_bridge;

// Re-export key types from submodules
pub use types::{
    instant_now, calculate_trend,
    SemanticInput, InputModality, ActionContext, TimeWindow,
};

pub use core::{
    ComponentId, BottleneckType, Bottleneck, ImprovementType,
    MonitorConfig, ComponentMetrics, PerformanceMonitor, AccuracyMetric,
};

pub use world_model::{
    LatentConsciousnessState, ConsciousnessAction, ActionType,
    ConsciousnessStateDelta, ConsciousnessTransition,
    WorldModelConfig, WorldModelStats, ConsciousnessWorldModel,
};

pub use routers::{
    RoutingDecision, RouterType, ConsciousnessRouter,
    DirectRouter, PhiMaximizingRouter, ExploratoryRouter, ConsolidatingRouter,
};

// Re-export from individual modules
pub use self_model::{SelfModel, SelfModelConfig};
pub use meta_cognitive::{MetaCognitive, MetaCognitiveState};
pub use dream_mode::{DreamMode, DreamConfig};
pub use gradient_optimizer::{GradientOptimizer, OptimizationConfig};
pub use improvement_generator::{ImprovementGenerator, Improvement};
pub use intrinsic_motivation::{IntrinsicMotivation, MotivationConfig};
pub use recursive_optimizer::{RecursiveOptimizer, OptimizationResult};
pub use safe_experiment::{SafeExperiment, ExperimentConfig, ExperimentResult};
pub use architectural_graph::{ArchitecturalGraph, ArchNode, ArchEdge};
pub use benchmark_suite::{BenchmarkSuite, BenchmarkResult};
pub use routing_hub::{RoutingHub, RoutingConfig};
pub use semantic_bridge::{SemanticBridge, SemanticBridgeConfig};
pub use primitive_semantic_bridge::PrimitiveSemanticBridge;
pub use naming_ceremony::{NamingCeremony, NamingConfig};
