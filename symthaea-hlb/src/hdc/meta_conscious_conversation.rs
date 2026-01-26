//! Meta-Conscious Conversation Core
//!
//! A small helper that ties together:
//! - `TextEncoder` + `PrimitiveSystem` (text → HDC bipolar vector)
//! - `MetaConsciousness` (HV16 components → Φ and meta-Φ)
//!
//! This is intended as a reusable seam for building conversational
//! experiences around the meta-consciousness engine without having to
//! manually wire encoding and component replication each time.

use anyhow::Result;

use symthaea_core::hdc::binary_hv::HV16;
use symthaea_core::hdc::meta_consciousness::{MetaConsciousness, MetaConfig, MetaConsciousnessState};
use symthaea_core::hdc::primitive_system::PrimitiveSystem;
use symthaea_core::hdc::text_encoder::{TextEncoder, TextEncoderConfig};

/// Core meta-conscious conversation helper.
///
/// This type is deliberately small and focused: it does not manage
/// long-term memory, LLMs, or rich dialogue logic. It only provides
/// a reliable path:
///
/// `&str` → HDC encoding → HV16 components → `MetaConsciousnessState`.
pub struct MetaConversationCore {
    /// Text encoder for natural language → bipolar HDC vectors.
    encoder: TextEncoder,
    /// Primitive system for canonical encodings of key concepts.
    primitives: PrimitiveSystem,
    /// Meta-consciousness engine.
    meta: MetaConsciousness,
    /// Number of HV16 components to construct from each text encoding.
    num_components: usize,
}

impl MetaConversationCore {
    /// Create a new core with default encoder and meta-consciousness configs.
    ///
    /// `num_components` controls how many HV16 components are constructed
    /// from the encoded text when reflecting (at least 1).
    pub fn new(num_components: usize) -> Result<Self> {
        Self::with_configs(
            num_components,
            TextEncoderConfig::default(),
            MetaConfig::default(),
        )
    }

    /// Create a new core with explicit encoder and meta-consciousness configs.
    pub fn with_configs(
        num_components: usize,
        encoder_config: TextEncoderConfig,
        meta_config: MetaConfig,
    ) -> Result<Self> {
        let nc = num_components.max(1);
        let encoder = TextEncoder::new(encoder_config)?;
        let primitives = PrimitiveSystem::new();
        let meta = MetaConsciousness::new(nc, meta_config);

        Ok(Self {
            encoder,
            primitives,
            meta,
            num_components: nc,
        })
    }

    /// Reflect on a single text input and return the current meta-conscious state.
    ///
    /// Steps:
    /// - Encode text with primitives (for better grounding where available).
    /// - Convert bipolar i8 encoding to f32.
    /// - Construct `num_components` identical HV16 components.
    /// - Call `MetaConsciousness::meta_reflect` on the component slice.
    pub fn reflect_on_text(&mut self, text: &str) -> Result<MetaConsciousnessState> {
        // Encode text into bipolar i8 vector.
        let encoded_i8 = self.encoder.encode_with_primitives(text, &self.primitives)?;

        // Convert to f32 bipolar representation for HV16.
        let encoded_f32 = self.encoder.to_f32(&encoded_i8);
        let hv = HV16::from_bipolar(&encoded_f32);

        // Replicate into the requested number of components.
        let components: Vec<HV16> = (0..self.num_components).map(|_| hv).collect();

        Ok(self.meta.meta_reflect(&components))
    }

    /// Access the underlying `MetaConsciousness` for advanced operations
    /// (e.g., `introspect`, `deep_introspect`, `predict_my_future`).
    pub fn meta(&self) -> &MetaConsciousness {
        &self.meta
    }

    /// Mutable access to the underlying `MetaConsciousness`.
    pub fn meta_mut(&mut self) -> &mut MetaConsciousness {
        &mut self.meta
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_reflect_on_text_produces_non_negative_phi() {
        let mut core = MetaConversationCore::new(4).expect("core should initialize");

        let state = core
            .reflect_on_text("Consciousness reflecting on itself is meta-consciousness.")
            .expect("reflection should succeed");

        assert!(state.phi >= 0.0);
        assert!(state.meta_phi >= 0.0);
        assert!(
            !state.explanation.is_empty(),
            "meta-conscious state should include an explanation"
        );
    }
}

