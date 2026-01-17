//! HDC - Hyperdimensional Computing Module
//!
//! Core HDC/VSA primitives and consciousness-related computations.
//! Re-exports fundamental types from symthaea-core for unified API.

// ═══════════════════════════════════════════════════════════════════════════════
// RE-EXPORTS FROM SYMTHAEA-CORE
// ═══════════════════════════════════════════════════════════════════════════════

// Core HDC types from symthaea-core
pub use symthaea_core::hdc::{
    // Binary hypervectors
    binary_hv::HV16,
    // Unified hypervector types
    unified_hv::{ContinuousHV, BinaryHV, HV, HDC_DIMENSION},
    // Real-valued hypervectors
    real_hv::RealHV,
    // Primitive system
    primitive_system::{PrimitiveSystem, Primitive, PrimitiveTier},
    // Tiered Phi calculation
    TieredPhi,
    // Native similarity with PackedBipolar
    PackedBipolar, NativeSimilarityIndex,
};

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
// LOCAL MODULES - Subdirectory modules
// ═══════════════════════════════════════════════════════════════════════════════
pub mod arithmetic;
pub mod consciousness;
pub mod tiered_phi;
pub mod phi;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Core HDC modules
// ═══════════════════════════════════════════════════════════════════════════════
pub mod hdc_trait;
pub mod native_similarity;
pub mod simd_ops;
pub mod hd_ltc_codec;
pub mod hdc_ltc_neuron;
pub mod text_encoder;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Consciousness/Phi computation
// ═══════════════════════════════════════════════════════════════════════════════
pub mod relational_consciousness;
pub mod consciousness_topology_generators;
pub mod phi_real;
pub mod meta_consciousness;
pub mod global_workspace;
pub mod consciousness_integration;
pub mod arithmetic_engine;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Cincinnati consciousness architecture
// ═══════════════════════════════════════════════════════════════════════════════
pub mod cincinnati_network;
pub mod cincinnati_enhanced;
pub mod cincinnati_advanced;
pub mod cincinnati_ltc;
pub mod gwt_cincinnati_integration;
pub mod universal_semantics;

// Re-exports for Cincinnati LTC and Universal Semantics
pub use cincinnati_ltc::{CincinnatiLTC, CincinnatiLTCConfig, LTCLayer, LTCNeuronState};
pub use universal_semantics::{UniversalSemantics, UniversalSemanticsConfig, SemanticConcept, SemanticDomain, SemanticSearchResult};

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Consciousness integration
// ═══════════════════════════════════════════════════════════════════════════════
pub mod conscious_learning;
pub mod consciousness_advanced_cognition;
pub mod consciousness_complete_being;
pub mod consciousness_cross_integration;
pub mod consciousness_feedback_dynamics;
pub mod consciousness_integration_demo;
pub mod consciousness_metacognition;
pub mod consciousness_persistence;
pub mod consciousness_streaming;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Semantic processing
// ═══════════════════════════════════════════════════════════════════════════════
pub mod semantic_encoder;
pub mod semantic_decoder;
pub mod semantic_primitive_encoder;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Learning and adaptation
// ═══════════════════════════════════════════════════════════════════════════════
pub mod adaptive_learning_signals;
pub mod cycle_detector;
pub mod counterfactual_dreams;
pub mod self_improvement_integration;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Perception and attention
// ═══════════════════════════════════════════════════════════════════════════════
pub mod cross_modal_attention_router;
pub mod emotional_depth;
pub mod predictive_encoder;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Infrastructure
// ═══════════════════════════════════════════════════════════════════════════════
pub mod ecosystem_bridge;
pub mod infrastructure_bridge;
pub mod reservoir;
pub mod ltc_generative_core;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Meta-cognition
// ═══════════════════════════════════════════════════════════════════════════════
pub mod meta_conscious_conversation;
pub mod primitive_dashboard;
pub mod unified_conscious_being;
pub mod unified_understanding;
pub mod full_stack_consciousness;

// ═══════════════════════════════════════════════════════════════════════════════
// LOCAL MODULES - Testing
// ═══════════════════════════════════════════════════════════════════════════════
#[cfg(test)]
pub mod proptest_hdc;

// ═══════════════════════════════════════════════════════════════════════════════
// RE-EXPORTS FROM LOCAL MODULES
// ═══════════════════════════════════════════════════════════════════════════════
pub use hdc_trait::*;
pub use tiered_phi::*;

// Re-export key types for backward compatibility
pub use symthaea_core::hdc::binary_hv as binary_hv;
pub use symthaea_core::hdc::unified_hv as unified_hv;
pub use symthaea_core::hdc::real_hv as real_hv;
pub use symthaea_core::hdc::primitive_system as primitive_system;

// Re-exports from new consciousness/HDC modules
pub use consciousness_topology_generators::{ConsciousnessTopology, TopologyType, TopologyGenerator};
pub use phi_real::{PhiRealCalculator, PhiRealResult, PhiRealConfig};
pub use relational_consciousness::{RelationalConsciousness, RelationType, RelationalNode};
pub use meta_consciousness::{MetaConsciousness, MetaLevel, StrangeLoop, SelfModel};
pub use global_workspace::{GlobalWorkspace, Coalition, Broadcast, GlobalWorkspaceConfig};
pub use hdc_ltc_neuron::{HdcLtcNeuron, HdcLtcLayer, HdcLtcNetwork, HdcLtcNeuronConfig};
pub use text_encoder::{TextEncoder, TextEncoderConfig, TextEncodingResult, SemanticHash};
pub use consciousness_integration::*;
pub use arithmetic_engine::*;
