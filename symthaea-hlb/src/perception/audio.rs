//! # Audio Perception - Speech Recognition Integration
//!
//! Integrates symthaea-stt (HDC + LTC speech recognition) with the
//! multi-modal perception pipeline.
//!
//! ## Architecture
//!
//! ```text
//! Audio (WAV/FLAC)
//!       │
//!       ▼
//! ┌─────────────────┐
//! │ AudioProjector  │ ← LTC temporal dynamics
//! │ (symthaea-stt)  │
//! └────────┬────────┘
//!          │ HV16 (2048-bit)
//!          ▼
//! ┌─────────────────┐
//! │ PhonemeDecoder  │ ← Hopfield associative memory
//! │                 │
//! └────────┬────────┘
//!          │ Phoneme sequence
//!          ▼
//! ┌─────────────────┐
//! │ Bridge to Core  │ ← HV16 → RealHV conversion
//! │                 │
//! └────────┬────────┘
//!          │
//!          ▼
//! PerceptionInput(Auditory)
//! ```

use std::path::Path;
use anyhow::{Result, anyhow};

// Re-define types locally when full_perception is not available
// This allows the audio module to work standalone

/// Types of sensory modalities (local copy for standalone use)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum ModalityType {
    /// Visual/image input
    Visual,
    /// Auditory/sound input
    Auditory,
    /// Textual input
    Textual,
}

/// Perception input (simplified for audio-only use)
#[derive(Debug, Clone)]
pub struct AudioInput {
    /// Input identifier
    pub id: String,
    /// Modality type
    pub modality: ModalityType,
    /// Embedded representation (as f32 vector)
    pub embedding: Option<Vec<f32>>,
    /// Confidence score
    pub confidence: f32,
    /// Metadata
    pub metadata: std::collections::HashMap<String, String>,
}

impl AudioInput {
    /// Create a new audio input
    pub fn new(id: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            modality: ModalityType::Auditory,
            embedding: None,
            confidence: 1.0,
            metadata: std::collections::HashMap::new(),
        }
    }

    /// Set embedding
    pub fn with_embedding(mut self, embedding: Vec<f32>) -> Self {
        self.embedding = Some(embedding);
        self
    }

    /// Add metadata
    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }
}

/// Audio perception configuration
#[derive(Debug, Clone)]
pub struct AudioPerceptionConfig {
    /// Path to trained phoneme prototypes
    pub prototypes_path: Option<String>,
    /// Sample rate for audio processing
    pub sample_rate: u32,
    /// Enable prosody analysis
    pub enable_prosody: bool,
    /// Confidence threshold for phoneme detection
    pub confidence_threshold: f32,
}

impl Default for AudioPerceptionConfig {
    fn default() -> Self {
        Self {
            prototypes_path: None,
            sample_rate: 16000,
            enable_prosody: true,
            confidence_threshold: 0.3,
        }
    }
}

/// Audio perception result
#[derive(Debug, Clone)]
pub struct AudioPerceptionResult {
    /// Decoded phonemes
    pub phonemes: Vec<String>,
    /// Per-frame confidence scores
    pub confidences: Vec<f32>,
    /// Prosody features (pitch, energy contour)
    pub prosody: Option<ProsodyFeatures>,
    /// Processing time in milliseconds
    pub processing_time_ms: f64,
    /// Number of frames processed
    pub num_frames: usize,
}

/// Prosody features extracted from audio
#[derive(Debug, Clone)]
pub struct ProsodyFeatures {
    /// Average pitch (Hz)
    pub avg_pitch: f32,
    /// Pitch variance
    pub pitch_variance: f32,
    /// Average energy
    pub avg_energy: f32,
    /// Speaking rate (phonemes per second)
    pub speaking_rate: f32,
}

/// Audio perception system - bridges symthaea-stt to perception pipeline
#[cfg(feature = "voice-stt")]
pub struct AudioPerception {
    config: AudioPerceptionConfig,
    projector: symthaea_stt::AudioProjector,
    decoder: symthaea_stt::PhonemeDecoder,
    has_prototypes: bool,
}

#[cfg(feature = "voice-stt")]
impl AudioPerception {
    /// Create a new audio perception system
    pub fn new(config: AudioPerceptionConfig) -> Result<Self> {
        let projector = symthaea_stt::AudioProjector::default_config();
        let mut decoder = symthaea_stt::PhonemeDecoder::new();
        let mut has_prototypes = false;

        // Load prototypes if available
        if let Some(ref path) = config.prototypes_path {
            if Path::new(path).exists() {
                let prototypes = symthaea_stt::TrainedPrototypes::load(path)
                    .context("Failed to load phoneme prototypes")?;
                decoder.load_prototypes(&prototypes.as_pairs());
                has_prototypes = true;
            }
        }

        Ok(Self {
            config,
            projector,
            decoder,
            has_prototypes,
        })
    }

    /// Process audio file and return perception input
    pub fn process_file(&mut self, path: &Path) -> Result<AudioInput> {
        let start = std::time::Instant::now();

        // Load audio
        let (samples, _sample_rate) = symthaea_stt::AudioFrontend::load_wav(path)
            .context("Failed to load audio file")?;

        // Project through LTC
        let hvs = self.projector.project(&samples);

        // Decode phonemes (if prototypes loaded)
        let (phonemes, confidences) = if self.has_prototypes {
            self.decoder.decode(&hvs)
        } else {
            (Vec::new(), Vec::new())
        };

        let processing_time = start.elapsed().as_secs_f64() * 1000.0;

        // Create combined HV from all frames (bundled representation)
        let combined_hv = symthaea_stt::bundle(&hvs);

        // Convert HV16 to continuous f32 embedding for perception pipeline
        // Use core dimension (16,384) for compatibility with symthaea-core
        let embedding = combined_hv.to_core_continuous();

        // Build audio input
        let mut input = AudioInput::new(
            path.file_name()
                .map(|s| s.to_string_lossy().to_string())
                .unwrap_or_else(|| "audio".to_string()),
        )
        .with_embedding(embedding);

        // Add metadata
        input = input
            .with_metadata("phonemes", phonemes.join(" "))
            .with_metadata("num_frames", hvs.len().to_string())
            .with_metadata("processing_time_ms", format!("{:.2}", processing_time));

        // Set confidence based on decoder average
        if !confidences.is_empty() {
            let avg_confidence = confidences.iter().sum::<f32>() / confidences.len() as f32;
            input.confidence = avg_confidence;
        }

        Ok(input)
    }

    /// Process raw audio samples
    pub fn process_samples(&mut self, samples: &[f32]) -> Result<AudioPerceptionResult> {
        let start = std::time::Instant::now();

        // Project through LTC
        let hvs = self.projector.project(samples);

        // Decode phonemes
        let (phonemes, confidences) = if self.has_prototypes {
            self.decoder.decode(&hvs)
        } else {
            (Vec::new(), Vec::new())
        };

        let processing_time = start.elapsed().as_secs_f64() * 1000.0;

        // Extract prosody if enabled
        let prosody = if self.config.enable_prosody {
            Some(self.extract_prosody(samples, &hvs))
        } else {
            None
        };

        Ok(AudioPerceptionResult {
            phonemes,
            confidences,
            prosody,
            processing_time_ms: processing_time,
            num_frames: hvs.len(),
        })
    }

    /// Extract prosody features from audio
    fn extract_prosody(&self, samples: &[f32], _hvs: &[symthaea_stt::HV16]) -> ProsodyFeatures {
        // Simple prosody extraction
        let energy: f32 = samples.iter().map(|x| x.abs()).sum::<f32>() / samples.len() as f32;

        // Count zero crossings as rough pitch proxy
        let mut zero_crossings = 0u32;
        for i in 1..samples.len() {
            if (samples[i-1] > 0.0) != (samples[i] > 0.0) {
                zero_crossings += 1;
            }
        }
        let zc_rate = zero_crossings as f32 / samples.len() as f32;
        let rough_pitch = zc_rate * self.config.sample_rate as f32 / 2.0;

        ProsodyFeatures {
            avg_pitch: rough_pitch,
            pitch_variance: 0.0, // Would need more sophisticated analysis
            avg_energy: energy,
            speaking_rate: 0.0, // Would need phoneme timing
        }
    }

    /// Check if prototypes are loaded
    pub fn has_prototypes(&self) -> bool {
        self.has_prototypes
    }
}

/// Stub implementation when voice-stt feature is not enabled
#[cfg(not(feature = "voice-stt"))]
#[allow(dead_code)] // Config reserved for feature-enabled mode
pub struct AudioPerception {
    config: AudioPerceptionConfig,
}

#[cfg(not(feature = "voice-stt"))]
impl AudioPerception {
    pub fn new(config: AudioPerceptionConfig) -> Result<Self> {
        Ok(Self { config })
    }

    pub fn process_file(&mut self, _path: &Path) -> Result<AudioInput> {
        Err(anyhow!("Audio perception requires 'voice-stt' feature"))
    }

    pub fn process_samples(&mut self, _samples: &[f32]) -> Result<AudioPerceptionResult> {
        Err(anyhow!("Audio perception requires 'voice-stt' feature"))
    }

    pub fn has_prototypes(&self) -> bool {
        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_audio_perception_config() {
        let config = AudioPerceptionConfig::default();
        assert_eq!(config.sample_rate, 16000);
        assert!(config.enable_prosody);
    }

    #[test]
    fn test_audio_input_creation() {
        let input = AudioInput::new("test");
        assert_eq!(input.modality, ModalityType::Auditory);
    }
}
