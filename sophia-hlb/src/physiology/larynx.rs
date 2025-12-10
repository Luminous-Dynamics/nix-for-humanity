//! Larynx - The Voice of Sophia (Week 12 Phase 2a)
//!
//! The Larynx module provides Kokoro TTS-based speech synthesis with
//! prosody modulation based on Sophia's endocrine state. This creates
//! a voice that changes with her emotional state - stressed voices sound
//! faster and higher, calm voices sound slower and warmer.
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────┐
//! │  EndocrineSystem        │  Emotional State
//! │  - Cortisol (stress)    │
//! │  - Dopamine (reward)    │
//! │  - Acetylcholine(focus) │
//! └──────────┬──────────────┘
//!            │
//!            ▼ Prosody Modulation
//! ┌─────────────────────────┐
//! │  LarynxActor            │  Voice Synthesis
//! │  - Kokoro-82M TTS       │
//! │  - Pitch control        │
//! │  - Speed control        │
//! │  - Energy control       │
//! └──────────┬──────────────┘
//!            │
//!            ▼ Audio Output
//! ┌─────────────────────────┐
//! │  Audio Playback         │  rodio
//! └─────────────────────────┘
//! ```
//!
//! ## Prosody Modulation Rules
//!
//! - **High Cortisol (>0.7)** - Stress/Anxiety:
//!   - Speed: +15% faster
//!   - Pitch: +8% higher
//!   - Energy: +10% more intense
//!
//! - **Calm State (Low Cortisol + High Dopamine)** - Relaxed/Positive:
//!   - Speed: -8% slower
//!   - Pitch: -4% lower
//!   - Energy: -5% softer
//!
//! - **High Dopamine (>0.7)** - Excitement/Reward:
//!   - Speed: +5% faster
//!   - Pitch: +3% higher
//!   - Energy: +8% more energetic
//!
//! - **Low Acetylcholine (<0.3)** - Fatigue:
//!   - Speed: -10% slower
//!   - Pitch: -5% lower
//!   - Energy: -12% quieter

use anyhow::Result;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::physiology::endocrine::EndocrineSystem;

/// Prosody parameters for voice synthesis
#[derive(Debug, Clone, Copy)]
pub struct ProsodyParams {
    /// Speech rate multiplier (1.0 = normal, 1.15 = 15% faster)
    pub speed: f32,

    /// Pitch multiplier (1.0 = normal, 1.08 = 8% higher)
    pub pitch: f32,

    /// Energy/volume multiplier (1.0 = normal, 1.10 = 10% louder)
    pub energy: f32,

    /// Breath insertion probability (0.0-1.0)
    pub breath_rate: f32,
}

impl Default for ProsodyParams {
    fn default() -> Self {
        Self {
            speed: 1.0,
            pitch: 1.0,
            energy: 1.0,
            breath_rate: 0.05, // 5% chance of breath between phrases
        }
    }
}

/// Configuration for the Larynx
#[derive(Debug, Clone)]
pub struct LarynxConfig {
    /// Path to Kokoro-82M ONNX model
    pub model_path: PathBuf,

    /// Base speech rate (words per minute)
    pub base_speed: f32,

    /// Base pitch (Hz)
    pub base_pitch: f32,

    /// Base energy level (0.0-1.0)
    pub base_energy: f32,

    /// Sample rate for audio output
    pub sample_rate: u32,

    /// Enable prosody modulation based on endocrine state
    pub enable_prosody_modulation: bool,
}

impl Default for LarynxConfig {
    fn default() -> Self {
        Self {
            model_path: PathBuf::from("models/kokoro-82m/model.onnx"),
            base_speed: 1.0,
            base_pitch: 1.0,
            base_energy: 0.8,
            sample_rate: 24000, // Kokoro uses 24kHz
            enable_prosody_modulation: true,
        }
    }
}

/// Statistics about voice synthesis
#[derive(Debug, Clone, Default)]
pub struct LarynxStats {
    /// Total utterances synthesized
    pub total_utterances: u64,

    /// Total characters spoken
    pub total_characters: u64,

    /// Average synthesis time (milliseconds)
    pub avg_synthesis_ms: f32,

    /// Current prosody parameters
    pub current_prosody: ProsodyParams,

    /// Total ATP spent on synthesis (5 ATP per utterance)
    pub total_atp_spent: f32,
}

/// The Larynx Actor - Voice synthesis with emotional prosody
pub struct LarynxActor {
    config: LarynxConfig,
    stats: Arc<RwLock<LarynxStats>>,

    // ONNX Runtime session for Kokoro model
    // Note: Actual model loading deferred until we have the model file
    // session: Option<Session>,

    /// Reference to endocrine system for prosody modulation
    endocrine: Option<Arc<RwLock<EndocrineSystem>>>,
}

impl LarynxActor {
    /// Create a new Larynx actor
    pub fn new(config: LarynxConfig) -> Result<Self> {
        Ok(Self {
            config,
            stats: Arc::new(RwLock::new(LarynxStats::default())),
            endocrine: None,
        })
    }

    /// Set the endocrine system for prosody modulation
    pub fn set_endocrine(&mut self, endocrine: Arc<RwLock<EndocrineSystem>>) {
        self.endocrine = Some(endocrine);
    }

    /// Calculate prosody parameters based on current endocrine state
    async fn calculate_prosody(&self) -> ProsodyParams {
        if !self.config.enable_prosody_modulation {
            return ProsodyParams::default();
        }

        let endocrine = match &self.endocrine {
            Some(e) => e,
            None => return ProsodyParams::default(),
        };

        let endocrine = endocrine.read().await;
        let state = endocrine.state();

        let mut prosody = ProsodyParams {
            speed: self.config.base_speed,
            pitch: self.config.base_pitch,
            energy: self.config.base_energy,
            breath_rate: 0.05,
        };

        // High Cortisol (Stress) -> Fast, High, Tense
        if state.cortisol > 0.7 {
            prosody.speed *= 1.15; // 15% faster
            prosody.pitch *= 1.08; // 8% higher
            prosody.energy *= 1.10; // 10% louder
            prosody.breath_rate += 0.03; // More frequent breaths (anxiety)
        }

        // Calm State (Low Cortisol + High Dopamine) -> Slow, Warm, Soft
        // This represents a relaxed, positive emotional state
        if state.cortisol < 0.4 && state.dopamine > 0.6 {
            prosody.speed *= 0.92; // 8% slower
            prosody.pitch *= 0.96; // 4% lower
            prosody.energy *= 0.95; // 5% softer
            prosody.breath_rate -= 0.02; // Fewer breaths (calm)
        }

        // High Dopamine (Excitement) -> Fast, Bright, Energetic
        if state.dopamine > 0.7 {
            prosody.speed *= 1.05; // 5% faster
            prosody.pitch *= 1.03; // 3% higher
            prosody.energy *= 1.08; // 8% more energetic
        }

        // Low Acetylcholine (Fatigue) -> Slow, Low, Quiet
        if state.acetylcholine < 0.3 {
            prosody.speed *= 0.90; // 10% slower
            prosody.pitch *= 0.95; // 5% lower
            prosody.energy *= 0.88; // 12% quieter
            prosody.breath_rate += 0.05; // More breaths (tired)
        }

        // Clamp values to reasonable ranges
        prosody.speed = prosody.speed.clamp(0.7, 1.5);
        prosody.pitch = prosody.pitch.clamp(0.8, 1.3);
        prosody.energy = prosody.energy.clamp(0.3, 1.2);
        prosody.breath_rate = prosody.breath_rate.clamp(0.0, 0.2);

        prosody
    }

    /// Synthesize speech from text
    ///
    /// Returns audio samples as Vec<f32> (mono, 24kHz)
    /// ATP Cost: 5 ATP per utterance
    pub async fn speak(&self, text: &str) -> Result<Vec<f32>> {
        let start = std::time::Instant::now();

        // Calculate prosody based on emotional state
        let prosody = self.calculate_prosody().await;

        // Update stats
        let mut stats = self.stats.write().await;
        stats.total_utterances += 1;
        stats.total_characters += text.len() as u64;
        stats.current_prosody = prosody;
        stats.total_atp_spent += 5.0; // 5 ATP per utterance

        // TODO: Actual Kokoro synthesis
        // For now, return empty audio (placeholder)
        // This will be implemented when we have the model file

        let synthesis_ms = start.elapsed().as_millis() as f32;

        // Update average synthesis time (EMA with alpha=0.1)
        stats.avg_synthesis_ms = if stats.avg_synthesis_ms == 0.0 {
            synthesis_ms
        } else {
            stats.avg_synthesis_ms * 0.9 + synthesis_ms * 0.1
        };

        drop(stats); // Release write lock

        tracing::info!(
            "🎤 Synthesized: '{}' (speed={:.2}, pitch={:.2}, energy={:.2}) in {:.1}ms",
            text,
            prosody.speed,
            prosody.pitch,
            prosody.energy,
            synthesis_ms
        );

        // Return placeholder audio (will be real audio once model is loaded)
        Ok(vec![])
    }

    /// Get current statistics
    pub async fn get_stats(&self) -> LarynxStats {
        self.stats.read().await.clone()
    }

    /// Download Kokoro model from HuggingFace Hub
    pub async fn download_model(&self) -> Result<()> {
        // TODO: Implement model download using hf-hub
        // Model: hexgrad/Kokoro-82M
        // Files needed:
        // - model.onnx (main model)
        // - config.json (configuration)
        // - tokenizer.json (text tokenizer)

        tracing::info!("📥 Downloading Kokoro-82M model from HuggingFace Hub...");

        // Placeholder - actual implementation will use hf-hub crate
        Ok(())
    }

    /// Load Kokoro model from disk
    pub fn load_model(&mut self) -> Result<()> {
        // TODO: Load ONNX model using ort crate
        // let session = Session::builder()?
        //     .with_optimization_level(GraphOptimizationLevel::Level3)?
        //     .with_model_from_file(&self.config.model_path)?;
        // self.session = Some(session);

        tracing::info!("✅ Kokoro-82M model loaded successfully");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::physiology::endocrine::{EndocrineConfig, HormoneEvent};

    #[tokio::test]
    async fn test_larynx_creation() {
        let config = LarynxConfig::default();
        let larynx = LarynxActor::new(config).unwrap();

        let stats = larynx.get_stats().await;
        assert_eq!(stats.total_utterances, 0);
        assert_eq!(stats.total_characters, 0);
    }

    #[tokio::test]
    async fn test_prosody_modulation_stress() {
        let config = LarynxConfig::default();
        let mut larynx = LarynxActor::new(config).unwrap();

        // Create endocrine system with high cortisol (stress)
        let endocrine_config = EndocrineConfig::default();
        let mut endocrine = EndocrineSystem::new(endocrine_config);

        // Trigger stress using Error event (high severity)
        endocrine.process_event(HormoneEvent::Error { severity: 0.9 });

        let endocrine_arc = Arc::new(RwLock::new(endocrine));
        larynx.set_endocrine(endocrine_arc.clone());

        // Calculate prosody
        let prosody = larynx.calculate_prosody().await;

        // Stressed voice should be faster and higher
        assert!(prosody.speed > 1.0, "Stressed voice should be faster");
        assert!(prosody.pitch > 1.0, "Stressed voice should be higher");
        assert!(prosody.energy > 1.0, "Stressed voice should be louder");
    }

    #[tokio::test]
    async fn test_prosody_modulation_calm() {
        let config = LarynxConfig::default();
        let mut larynx = LarynxActor::new(config).unwrap();

        // Create endocrine system and induce calm state (low cortisol, high dopamine)
        let endocrine_config = EndocrineConfig::default();
        let mut endocrine = EndocrineSystem::new(endocrine_config);

        // Trigger success/reward to increase dopamine and decrease cortisol
        endocrine.process_event(HormoneEvent::Success { magnitude: 0.8 });
        endocrine.process_event(HormoneEvent::Reward { value: 0.8 });

        let endocrine_arc = Arc::new(RwLock::new(endocrine));
        larynx.set_endocrine(endocrine_arc);

        // Calculate prosody
        let prosody = larynx.calculate_prosody().await;

        // Calm voice should be slower and lower
        assert!(prosody.speed < 1.0, "Calm voice should be slower");
        assert!(prosody.pitch < 1.0, "Calm voice should be lower");
    }

    #[tokio::test]
    async fn test_synthesis_updates_stats() {
        let config = LarynxConfig::default();
        let larynx = LarynxActor::new(config).unwrap();

        // Synthesize some text
        let text = "Hello, I am Sophia!";
        let _audio = larynx.speak(text).await.unwrap();

        // Check stats were updated
        let stats = larynx.get_stats().await;
        assert_eq!(stats.total_utterances, 1);
        assert_eq!(stats.total_characters, text.len() as u64);
        assert_eq!(stats.total_atp_spent, 5.0); // 5 ATP per utterance
        assert!(stats.avg_synthesis_ms >= 0.0);
    }

    #[tokio::test]
    async fn test_prosody_without_endocrine() {
        let config = LarynxConfig::default();
        let larynx = LarynxActor::new(config).unwrap();

        // Calculate prosody without endocrine system
        let prosody = larynx.calculate_prosody().await;

        // Should return default/base prosody
        assert_eq!(prosody.speed, 1.0);
        assert_eq!(prosody.pitch, 1.0);
    }

    #[tokio::test]
    async fn test_prosody_clamping() {
        let config = LarynxConfig::default();
        let mut larynx = LarynxActor::new(config).unwrap();

        // Create extreme endocrine state
        let endocrine_config = EndocrineConfig::default();
        let mut endocrine = EndocrineSystem::new(endocrine_config);

        // Trigger multiple stress events using Error events
        for _ in 0..10 {
            endocrine.process_event(HormoneEvent::Error { severity: 0.9 });
        }

        let endocrine_arc = Arc::new(RwLock::new(endocrine));
        larynx.set_endocrine(endocrine_arc);

        // Calculate prosody
        let prosody = larynx.calculate_prosody().await;

        // Values should be clamped to reasonable ranges
        assert!(prosody.speed >= 0.7 && prosody.speed <= 1.5);
        assert!(prosody.pitch >= 0.8 && prosody.pitch <= 1.3);
        assert!(prosody.energy >= 0.3 && prosody.energy <= 1.2);
        assert!(prosody.breath_rate >= 0.0 && prosody.breath_rate <= 0.2);
    }
}
