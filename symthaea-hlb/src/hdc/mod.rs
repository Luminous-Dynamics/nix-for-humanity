//! HDC - Hyperdimensional Computing Module
//!
//! Core HDC/VSA primitives and consciousness-related computations.
//! Re-exports fundamental types from symthaea-core for unified API.
//!
//! # Architecture
//! This module provides:
//! - Re-exports from symthaea-core for basic HDC operations
//! - Local extensions for consciousness-specific computations
//! - Unified API for HDC operations across the library

#![allow(unused_imports)]

// ═══════════════════════════════════════════════════════════════════════════════
// RE-EXPORTS FROM SYMTHAEA-CORE - Core Types
// ═══════════════════════════════════════════════════════════════════════════════

// Core HDC types from symthaea-core
pub use symthaea_core::hdc::{
    // Binary hypervectors
    binary_hv::HV16,
    // Unified hypervector types
    unified_hv::{ContinuousHV, BinaryHV, HV, HDC_DIMENSION},
    // Real-valued hypervectors
    real_hv::RealHV,
    // LTC neuron count constants
    LTC_NEURONS,
    // Primitive system
    primitive_system::{PrimitiveSystem, Primitive, PrimitiveTier},
    // Tiered Phi calculation
    TieredPhi,
    // Native similarity with PackedBipolar
    PackedBipolar, NativeSimilarityIndex,
    // Causal types
    CausalDirection,
    // HDC context for arena-based operations
    HdcContext,
};

// Re-export native_similarity module for tests
pub use symthaea_core::hdc::native_similarity;

// Re-export HDC_DIMENSION at module level for convenience
pub const HDC_DIM: usize = symthaea_core::hdc::unified_hv::HDC_DIMENSION;

// Phi engine types from symthaea-core
pub use symthaea_core::phi_engine::{
    PhiEngine, PhiMethod, PhiResult, PhiCalculator,
};

// Observability types from symthaea-core
pub use symthaea_core::observability::{
    SharedObserver, Observer, NoOpObserver, no_op_observer,
    PhiComponents, PhiMeasurementEvent,
};

// ═══════════════════════════════════════════════════════════════════════════════
// RE-EXPORTS FROM SYMTHAEA-CORE - Full Modules
// ═══════════════════════════════════════════════════════════════════════════════

// Re-export entire modules for compatibility
pub use symthaea_core::hdc::hebbian;
pub use symthaea_core::hdc::adaptive_topology;
pub use symthaea_core::hdc::sleep_and_altered_states;
pub use symthaea_core::hdc::causal_mind;
pub use symthaea_core::hdc::cross_modal_binding;
pub use symthaea_core::hdc::unified_cognitive_core;
pub use symthaea_core::hdc::collective_consciousness;
pub use symthaea_core::hdc::grounded_understanding;
pub use symthaea_core::hdc::predictive_coding;
pub use symthaea_core::hdc::simd_hv16;
pub use symthaea_core::hdc::binary_hv;
pub use symthaea_core::hdc::unified_hv;
pub use symthaea_core::hdc::real_hv;
pub use symthaea_core::hdc::primitive_system;
pub use symthaea_core::hdc::simd_ops;
pub use symthaea_core::hdc::consciousness_integration;
pub use symthaea_core::hdc::consciousness_topology_generators;
pub use symthaea_core::hdc::spectral_connectivity;
pub use symthaea_core::hdc::global_workspace;
pub use symthaea_core::hdc::meta_consciousness;
pub use symthaea_core::hdc::relational_consciousness;
pub use symthaea_core::hdc::text_encoder;
pub use symthaea_core::hdc::semantic_encoder;
pub use symthaea_core::hdc::semantic_decoder;
pub use symthaea_core::hdc::reservoir;
pub use symthaea_core::hdc::cincinnati_ltc;
pub use symthaea_core::hdc::cincinnati_enhanced;
pub use symthaea_core::hdc::cincinnati_advanced;
pub use symthaea_core::hdc::cincinnati_network;
pub use symthaea_core::hdc::gwt_cincinnati_integration;
pub use symthaea_core::hdc::universal_semantics;
pub use symthaea_core::hdc::tiered_phi as core_tiered_phi;
pub use symthaea_core::hdc::arithmetic_engine;
pub use symthaea_core::hdc::consciousness_persistence as core_consciousness_persistence;
pub use symthaea_core::hdc::conscious_learning as core_conscious_learning;
pub use symthaea_core::hdc::adaptive_learning_signals as core_adaptive_learning;
pub use symthaea_core::hdc::unified_understanding as core_unified_understanding;
pub use symthaea_core::hdc::full_stack_consciousness as core_full_stack;
pub use symthaea_core::hdc::unified_conscious_being as core_unified_being;
pub use symthaea_core::hdc::ecosystem_bridge as core_ecosystem_bridge;
pub use symthaea_core::hdc::predictive_encoder as core_predictive_encoder;
pub use symthaea_core::hdc::emotional_depth as core_emotional_depth;
pub use symthaea_core::hdc::cross_modal_attention_router as core_attention_router;
pub use symthaea_core::hdc::consciousness_streaming as core_streaming;
pub use symthaea_core::hdc::consciousness_metacognition as core_metacognition;
pub use symthaea_core::hdc::counterfactual_dreams as core_counterfactual;
pub use symthaea_core::hdc::self_improvement_integration as core_self_improvement;
pub use symthaea_core::hdc::consciousness_advanced_cognition as core_advanced_cognition;
pub use symthaea_core::hdc::consciousness_complete_being as core_complete_being;
pub use symthaea_core::hdc::consciousness_cross_integration as core_cross_integration;
pub use symthaea_core::hdc::consciousness_feedback_dynamics as core_feedback_dynamics;
pub use symthaea_core::hdc::hdc_ltc_unified as core_hdc_ltc_unified;

// Re-export unified HDC-LTC types (revolutionary closed-form dynamics)
pub use symthaea_core::hdc::hdc_ltc_unified::{
    HdcLtcUnifiedNeuron, HdcLtcUnifiedNetwork,
    UnifiedConfig, UnifiedNetworkConfig,
    UnifiedActivation, UnifiedNeuronStats, UnifiedNetworkStats,
};

// Re-export from causal_mind
pub use symthaea_core::hdc::causal_mind::{CausalDiscoveryResult, CausalFeatures};

// Re-export SemanticPrime
pub use symthaea_core::hdc::universal_semantics::SemanticPrime;

// ═══════════════════════════════════════════════════════════════════════════════
// RE-EXPORTS - Convenience Types (only types that exist)
// ═══════════════════════════════════════════════════════════════════════════════

// Re-exports from symthaea-core consciousness modules
pub use symthaea_core::hdc::consciousness_topology_generators::{ConsciousnessTopology, TopologyType};
pub use symthaea_core::hdc::relational_consciousness::RelationalConsciousness;
pub use symthaea_core::hdc::meta_consciousness::MetaConsciousness;
pub use symthaea_core::hdc::global_workspace::GlobalWorkspace;
pub use symthaea_core::hdc::text_encoder::{TextEncoder, TextEncoderConfig};

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Subdirectory modules (stable)
// ═══════════════════════════════════════════════════════════════════════════════
pub mod arithmetic;
pub mod consciousness;
pub mod tiered_phi;
pub mod phi;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Testing
// ═══════════════════════════════════════════════════════════════════════════════
#[cfg(test)]
pub mod proptest_hdc;
