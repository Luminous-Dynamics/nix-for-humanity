//! Perception - Multi-modal sensory processing
//!
//! Provides video capture, physiological signal processing, and
//! temporal feature extraction for consciousness-aware perception.
//!
//! ## Neural Bridge (LLM as Semantic Sensor)
//!
//! The [`neural_bridge`] module implements the "Hyperdimensional Probe" -
//! a trained linear projection that maps LLM internal activations directly
//! to Symthaea's 16,384-dimensional HDC space.
//!
//! Instead of treating the LLM as a "Conversation Partner" (Text -> Text),
//! we treat it as a "Semantic Sensor" (Activations -> Vectors).

pub mod physio;
pub mod video;
pub mod social_trust;

// Audio perception - Speech recognition via symthaea-stt
pub mod audio;

// Semantic encoding - Text/embedding -> HDC projection
pub mod semantic_encoder;
pub use semantic_encoder::{SemanticEncoder, JLProjector, NGramEncoder};

// Neural Bridge - LLM activation -> HDC direct projection
pub mod neural_bridge;
pub use neural_bridge::NeuralBridge;

// Neural Bridge Consciousness Probe - Topological analysis of LLM representations
pub mod neural_bridge_consciousness_probe;
pub use neural_bridge_consciousness_probe::{
    ConsciousnessProbe, ConceptCorpus, Concept, ConceptProbeResult,
    ClassComparisonResult, ClassStatistics, ProbeConfig,
};

#[cfg(feature = "neural-bridge")]
pub use neural_bridge_consciousness_probe::ConsciousnessProbeV2;

// Layer-wise activation extraction for transformer models
#[cfg(feature = "neural-bridge")]
pub mod layer_extractor;

#[cfg(feature = "neural-bridge")]
pub use layer_extractor::{LayerExtractor, LayerActivation, AllLayerActivations, PoolingMethod};

// Epistemic Semantic Vectors - HDC with uncertainty metadata
pub mod epistemic_vector;
pub use epistemic_vector::{EpistemicSemanticVector, UncertaintySource};

// BGE-M3 Embedding Model (pure Rust via Candle)
#[cfg(feature = "neural-bridge")]
pub mod bge_m3;

// Neural Bridge v2 - Complete text → HDC pipeline
#[cfg(feature = "neural-bridge")]
pub mod neural_bridge_v2;

#[cfg(feature = "neural-bridge")]
pub use neural_bridge_v2::{NeuralBridgeV2, NeuralBridgeV2Builder, NeuralBridgeV2Config};

// Multi-modal integration (conditionally compiled)
#[cfg(feature = "full_perception")]
pub mod multi_modal;

#[cfg(feature = "full_perception")]
pub mod conscious_perception;

#[cfg(feature = "full_perception")]
pub mod resilience;
