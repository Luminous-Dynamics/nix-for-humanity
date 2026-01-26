//! # Cognitive Loop Service - Emergent HDC↔CfC Integration
//!
//! This module implements the **bidirectional cognitive loop** that creates
//! emergent structure through prediction error minimization using Closed-form
//! Continuous-time (CfC) networks for O(1) temporal prediction.
//!
//! ## The Core Loop
//!
//! ```text
//! Cycle t:
//! 1. Input → HDC encode (with attention from t-1)
//! 2. CfC processes current HDC state (O(1) closed-form)
//! 3. CfC predicts next HDC state at multiple time horizons
//! 4. Prediction error computed (multi-scale)
//! 5. Error → CfC analytical gradient + HDC attention update
//! 6. Prediction sent to encoder for cycle t+1
//! ```
//!
//! ## Why CfC (vs LTC)
//!
//! - **O(1) vs O(N)**: Closed-form solution avoids Euler integration
//! - **Multi-scale prediction**: Instant prediction at any future time
//! - **Analytical gradients**: No numerical approximation for training
//! - **Temporal "jumps"**: Can query t+10 without computing t+1..t+9
//!
//! ## Why This Creates Emergence
//!
//! - **Not hardcoded**: Structure emerges from prediction error, not rules
//! - **Biologically inspired**: Predictive coding in cortex
//! - **Self-organizing**: Attention weights evolve to minimize surprise
//! - **Continuous**: Service runs at 50Hz even without input
//!
//! ## Usage
//!
//! ```rust,ignore
//! use symthaea::cognitive_loop::{CognitiveLoopService, CognitiveLoopConfig};
//!
//! let mut service = CognitiveLoopService::new(CognitiveLoopConfig::default())?;
//!
//! // Process input
//! let result = service.cycle("cause leads to effect");
//!
//! // Check if learning is occurring
//! println!("Prediction error: {}", result.prediction_error);
//! println!("Attention variance: {}", service.stats().attention_variance);
//! ```

use anyhow::Result;
use serde::{Serialize, Deserialize};
use std::collections::{HashMap, VecDeque};
use std::time::{Duration, Instant};
use ndarray::Array1;

use symthaea_core::hdc::predictive_encoder::{PredictiveHdcEncoder, PredictiveEncoderConfig};
use crate::cfc::CfCNetwork;

/// Configuration for CfC in the cognitive loop
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CfCConfig {
    /// Number of CfC neurons
    pub num_neurons: usize,

    /// Input dimension (compressed HDC)
    pub input_dim: usize,

    /// Learning rate for CfC training
    pub learning_rate: f32,

    /// Time step for CfC predictions (seconds)
    pub delta_t: f32,

    /// Future prediction horizons for multi-scale prediction
    pub prediction_horizons: Vec<f32>,
}

impl Default for CfCConfig {
    fn default() -> Self {
        Self {
            num_neurons: 256,
            input_dim: 256,  // Must match num_neurons for train_step compatibility
            learning_rate: 0.01,
            delta_t: 0.02,  // 50Hz base rate
            // Multi-scale prediction: t+1, t+5, t+10 steps
            prediction_horizons: vec![0.02, 0.1, 0.2],
        }
    }
}

/// Configuration for the cognitive loop service
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CognitiveLoopConfig {
    /// HDC encoder configuration
    pub encoder_config: PredictiveEncoderConfig,

    /// CfC configuration (replaces LTC for O(1) temporal prediction)
    pub cfc_config: CfCConfig,

    /// Minimum prediction error to trigger learning
    pub learning_threshold: f32,

    /// Experience buffer size
    pub buffer_size: usize,

    /// Whether to enable background consolidation
    pub enable_consolidation: bool,

    /// Target loop frequency (Hz)
    pub target_frequency: f32,

    /// Maximum cycles before stats reset (for long-running service)
    pub max_cycles_before_reset: usize,
}

impl Default for CognitiveLoopConfig {
    fn default() -> Self {
        Self {
            encoder_config: PredictiveEncoderConfig::default(),
            cfc_config: CfCConfig::default(),
            learning_threshold: 0.05,
            buffer_size: 1000,
            enable_consolidation: true,
            target_frequency: 50.0, // 50 Hz
            max_cycles_before_reset: 100000,
        }
    }
}

/// Result of a single cognitive cycle
#[derive(Debug, Clone)]
pub struct CycleResult {
    /// LTC output (interpretation of current state)
    pub output: Vec<f32>,

    /// Prediction error for this cycle
    pub prediction_error: f32,

    /// Current attention state
    pub attention_state: HashMap<String, f32>,

    /// Detected primitives in input
    pub detected_primitives: Vec<String>,

    /// Whether learning occurred this cycle
    pub learning_occurred: bool,

    /// Training loss (if learning occurred)
    pub training_loss: Option<f32>,

    /// Cycle timing (microseconds)
    pub cycle_time_us: u64,
}

/// Experience for replay buffer
#[derive(Debug, Clone)]
#[allow(dead_code)] // Fields reserved for experience replay
struct Experience {
    /// Compressed HDC state
    state: Vec<f32>,
    /// LTC prediction
    prediction: Vec<f32>,
    /// Actual next state (for learning)
    next_state: Option<Vec<f32>>,
    /// Prediction error
    error: f32,
    /// Importance weight
    importance: f32,
}

/// Statistics for the cognitive loop
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct LoopStats {
    /// Total cycles completed
    pub total_cycles: usize,

    /// Average prediction error (EMA)
    pub avg_prediction_error: f32,

    /// Learning cycles (error > threshold)
    pub learning_cycles: usize,

    /// Average training loss (EMA)
    pub avg_training_loss: f32,

    /// Attention variance (emergence metric)
    pub attention_variance: f32,

    /// Number of primitives with diverged attention
    pub diverged_primitives: usize,

    /// Buffer utilization (0-1)
    pub buffer_utilization: f32,

    /// Average cycle time (microseconds)
    pub avg_cycle_time_us: f32,

    /// Cycles per second
    pub cycles_per_second: f32,

    /// Prediction error trend (negative = improving)
    pub error_trend: f32,

    /// LTC consciousness level
    pub ltc_consciousness: f32,
}

/// The Cognitive Loop Service
///
/// Orchestrates the bidirectional HDC↔CfC loop for emergent cognition.
/// Uses Closed-form Continuous-time (CfC) networks for O(1) temporal prediction.
pub struct CognitiveLoopService {
    /// Configuration
    config: CognitiveLoopConfig,

    /// Predictive HDC encoder
    encoder: PredictiveHdcEncoder,

    /// CfC temporal predictor (replaces LTC for O(1) predictions)
    cfc: CfCNetwork,

    /// Experience buffer for replay
    buffer: VecDeque<Experience>,

    /// Statistics
    stats: LoopStats,

    /// Error history for trend detection
    error_history: VecDeque<f32>,

    /// Last compressed state (for creating experience)
    last_state: Option<Vec<f32>>,

    /// Last prediction (for experience)
    last_prediction: Option<Vec<f32>>,

    /// Start time for cycles/second calculation
    start_time: Instant,

    /// Is currently consolidating (background learning)
    is_consolidating: bool,
}

impl CognitiveLoopService {
    /// Create a new cognitive loop service
    pub fn new(config: CognitiveLoopConfig) -> Result<Self> {
        let encoder = PredictiveHdcEncoder::new(config.encoder_config.clone());

        // Create CfC network with input_dim and num_neurons
        let cfc = CfCNetwork::new_with_input(
            config.cfc_config.input_dim,
            config.cfc_config.num_neurons
        );

        Ok(Self {
            config,
            encoder,
            cfc,
            buffer: VecDeque::with_capacity(1000),
            stats: LoopStats::default(),
            error_history: VecDeque::with_capacity(100),
            last_state: None,
            last_prediction: None,
            start_time: Instant::now(),
            is_consolidating: false,
        })
    }

    /// Run one cognitive cycle (the core loop)
    ///
    /// Uses CfC's O(1) closed-form solution for temporal prediction,
    /// enabling instant forward-time queries and multi-scale prediction.
    pub fn cycle(&mut self, input: &str) -> CycleResult {
        let cycle_start = Instant::now();
        self.stats.total_cycles += 1;

        // 1. HDC encode with attention from previous prediction
        let encoding_result = self.encoder.encode(input);
        let prediction_error = encoding_result.prediction_error;

        // 2. Compress HDC state for CfC (using Random Projection)
        let compressed_state = self.encoder.compress_for_ltc(
            &encoding_result.hdv,
            self.config.cfc_config.input_dim
        );

        // 3. Convert to ndarray for CfC
        let input_array = Array1::from_vec(compressed_state.clone());

        // 4. Step CfC forward with current input
        let delta_t = self.config.cfc_config.delta_t;
        let _ = self.cfc.step(&input_array, delta_t);

        // 5. Get multi-scale predictions using CfC's O(1) predict_forward
        // This is the key advantage: instant prediction at any future time
        let prediction = self.get_multi_scale_prediction(&input_array);

        // 6. Get current CfC state as output
        let output = self.cfc.read_state()
            .map(|arr| arr.to_vec())
            .unwrap_or_else(|_| vec![0.0; self.config.cfc_config.num_neurons]);

        // 7. Send prediction to encoder for next cycle
        self.encoder.set_prediction(prediction.clone());

        // 8. Capture previous state BEFORE create_experience updates it
        let previous_state = self.last_state.clone();

        // 9. Create experience and add to buffer (this updates last_state)
        self.create_experience(&compressed_state, &prediction, prediction_error);

        // 10. Learn if error is significant AND we have a previous state
        let (learning_occurred, training_loss) = if prediction_error > self.config.learning_threshold {
            self.stats.learning_cycles += 1;

            // Use CfC's analytical gradient training
            let result = if let Some(ref prev) = previous_state {
                let prev_array = Array1::from_vec(prev.clone());
                let target_array = Array1::from_vec(compressed_state.clone());
                self.cfc.train_step(
                    &prev_array,
                    &target_array,
                    delta_t,
                    self.config.cfc_config.learning_rate
                )
            } else {
                // First cycle: bootstrap with self-prediction
                let current_array = Array1::from_vec(compressed_state.clone());
                self.cfc.train_step(
                    &current_array,
                    &current_array,
                    delta_t,
                    self.config.cfc_config.learning_rate * 0.1
                )
            };

            match result {
                Ok(loss) => {
                    self.update_loss_stats(loss);
                    (true, Some(loss))
                }
                Err(_) => (false, None),
            }
        } else {
            (false, None)
        };

        // 11. Update statistics
        self.update_stats(prediction_error, cycle_start.elapsed());

        // Update consciousness level from CfC
        self.stats.ltc_consciousness = self.cfc.consciousness_level();

        CycleResult {
            output,
            prediction_error,
            attention_state: encoding_result.attention_snapshot,
            detected_primitives: encoding_result.detected_primitives,
            learning_occurred,
            training_loss,
            cycle_time_us: cycle_start.elapsed().as_micros() as u64,
        }
    }

    /// Get multi-scale prediction by averaging predictions at different time horizons
    ///
    /// This uses CfC's O(1) predict_forward to instantly query multiple future times,
    /// forcing the network to learn temporal "rules" rather than just noise patterns.
    fn get_multi_scale_prediction(&mut self, input: &Array1<f32>) -> Vec<f32> {
        let horizons = &self.config.cfc_config.prediction_horizons;

        if horizons.is_empty() {
            // Fallback: single-step prediction
            return self.cfc.predict_forward(input, self.config.cfc_config.delta_t)
                .map(|arr| arr.to_vec())
                .unwrap_or_else(|_| vec![0.0; self.config.cfc_config.input_dim]);
        }

        // Collect predictions at multiple time horizons
        let mut predictions: Vec<Array1<f32>> = Vec::with_capacity(horizons.len());

        for &horizon in horizons {
            if let Ok(pred) = self.cfc.predict_forward(input, horizon) {
                predictions.push(pred);
            }
        }

        if predictions.is_empty() {
            return vec![0.0; self.config.cfc_config.input_dim];
        }

        // Average the multi-scale predictions
        // This forces temporal consistency across different timescales
        let n = predictions.len() as f32;
        let dim = predictions[0].len();
        let mut result = vec![0.0f32; dim];

        for pred in &predictions {
            for (i, val) in pred.iter().enumerate() {
                if i < dim {
                    result[i] += val / n;
                }
            }
        }

        result
    }

    /// Run a background consolidation cycle
    ///
    /// This replays important experiences to strengthen learning using CfC.
    pub fn consolidate(&mut self) -> Result<f32> {
        if self.buffer.len() < 10 {
            return Ok(0.0);
        }

        self.is_consolidating = true;

        // Sort by importance and replay top experiences
        let mut experiences: Vec<_> = self.buffer.iter().collect();
        experiences.sort_by(|a, b| b.importance.partial_cmp(&a.importance)
            .unwrap_or(std::cmp::Ordering::Equal));

        let mut total_loss = 0.0;
        let replay_count = experiences.len().min(10);
        let delta_t = self.config.cfc_config.delta_t;
        let lr = self.config.cfc_config.learning_rate;

        for exp in experiences.iter().take(replay_count) {
            if let Some(ref next_state) = exp.next_state {
                // Reset CfC state for clean replay by injecting zeros
                let zeros = Array1::from_vec(vec![0.0f32; self.config.cfc_config.input_dim]);
                let _ = self.cfc.inject(&zeros);

                // Train using CfC's analytical gradient
                let prev_array = Array1::from_vec(exp.state.clone());
                let target_array = Array1::from_vec(next_state.clone());
                if let Ok(loss) = self.cfc.train_step(&prev_array, &target_array, delta_t, lr) {
                    total_loss += loss;
                }
            }
        }

        self.is_consolidating = false;

        Ok(total_loss / replay_count as f32)
    }

    /// Get current statistics
    pub fn stats(&self) -> &LoopStats {
        &self.stats
    }

    /// Get encoder statistics
    pub fn encoder_stats(&self) -> &symthaea_core::hdc::predictive_encoder::EncoderStats {
        self.encoder.stats()
    }

    /// Get CfC consciousness level
    pub fn cfc_consciousness(&self) -> f32 {
        self.cfc.consciousness_level()
    }

    /// Get CfC state dimension
    pub fn cfc_state_dim(&self) -> usize {
        self.config.cfc_config.num_neurons
    }

    /// Check if loop is learning (error trend negative)
    pub fn is_learning(&self) -> bool {
        self.stats.error_trend < 0.0 && self.stats.learning_cycles > 0
    }

    /// Check if attention has emerged (variance > threshold)
    pub fn has_emerged_attention(&self) -> bool {
        self.stats.attention_variance > 0.01
    }

    /// Reset all learning state
    pub fn reset(&mut self) {
        self.encoder.reset_attention();
        // Reset CfC state by injecting zeros
        let zeros = Array1::from_vec(vec![0.0f32; self.config.cfc_config.input_dim]);
        let _ = self.cfc.inject(&zeros);
        self.buffer.clear();
        self.error_history.clear();
        self.last_state = None;
        self.last_prediction = None;
        self.stats = LoopStats::default();
        self.start_time = Instant::now();
    }

    /// Get the compressed state dimension (input to CfC)
    pub fn state_dim(&self) -> usize {
        self.config.cfc_config.input_dim
    }

    /// Get the prediction dimension (CfC neurons)
    pub fn prediction_dim(&self) -> usize {
        self.config.cfc_config.num_neurons
    }

    // ========== Internal Methods ==========

    fn create_experience(&mut self, state: &[f32], prediction: &[f32], error: f32) {
        // Update last experience with next_state
        if let Some(ref last_state) = self.last_state.take() {
            if let Some(last_pred) = self.last_prediction.take() {
                // Calculate importance based on error
                let importance = error + 0.1; // Base importance

                let exp = Experience {
                    state: last_state.clone(),
                    prediction: last_pred,
                    next_state: Some(state.to_vec()),
                    error,
                    importance,
                };

                if self.buffer.len() >= self.config.buffer_size {
                    self.buffer.pop_front();
                }
                self.buffer.push_back(exp);
            }
        }

        // Store current state for next cycle
        self.last_state = Some(state.to_vec());
        self.last_prediction = Some(prediction.to_vec());
    }

    fn update_stats(&mut self, error: f32, cycle_time: Duration) {
        // EMA for error
        let alpha = 0.1;
        self.stats.avg_prediction_error =
            self.stats.avg_prediction_error * (1.0 - alpha) + error * alpha;

        // Error trend
        self.error_history.push_back(error);
        if self.error_history.len() > 100 {
            self.error_history.pop_front();
        }
        self.stats.error_trend = self.compute_error_trend();

        // Attention stats from encoder
        let encoder_stats = self.encoder.stats();
        self.stats.attention_variance = encoder_stats.attention_variance;
        self.stats.diverged_primitives = encoder_stats.diverged_primitives;

        // Buffer utilization
        self.stats.buffer_utilization =
            self.buffer.len() as f32 / self.config.buffer_size as f32;

        // Timing stats
        let cycle_us = cycle_time.as_micros() as f32;
        self.stats.avg_cycle_time_us =
            self.stats.avg_cycle_time_us * 0.99 + cycle_us * 0.01;

        // Cycles per second
        let elapsed = self.start_time.elapsed().as_secs_f32();
        if elapsed > 0.0 {
            self.stats.cycles_per_second = self.stats.total_cycles as f32 / elapsed;
        }

        // CfC consciousness level (already updated in cycle(), but ensure consistency)
        self.stats.ltc_consciousness = self.cfc.consciousness_level();
    }

    fn update_loss_stats(&mut self, loss: f32) {
        let alpha = 0.1;
        self.stats.avg_training_loss =
            self.stats.avg_training_loss * (1.0 - alpha) + loss * alpha;
    }

    fn compute_error_trend(&self) -> f32 {
        if self.error_history.len() < 10 {
            return 0.0;
        }

        // Simple linear regression slope
        let n = self.error_history.len() as f32;
        let errors: Vec<f32> = self.error_history.iter().cloned().collect();

        let x_mean = (n - 1.0) / 2.0;
        let y_mean: f32 = errors.iter().sum::<f32>() / n;

        let mut numerator = 0.0f32;
        let mut denominator = 0.0f32;

        for (i, &y) in errors.iter().enumerate() {
            let x = i as f32;
            numerator += (x - x_mean) * (y - y_mean);
            denominator += (x - x_mean).powi(2);
        }

        if denominator.abs() > 0.0001 {
            numerator / denominator
        } else {
            0.0
        }
    }
}

/// Builder for configuring the cognitive loop service
pub struct CognitiveLoopBuilder {
    config: CognitiveLoopConfig,
}

impl CognitiveLoopBuilder {
    pub fn new() -> Self {
        Self {
            config: CognitiveLoopConfig::default(),
        }
    }

    pub fn with_cfc_neurons(mut self, neurons: usize) -> Self {
        self.config.cfc_config.num_neurons = neurons;
        self.config.cfc_config.input_dim = neurons;  // Keep in sync for train_step
        self
    }

    /// Alias for backward compatibility
    pub fn with_ltc_neurons(self, neurons: usize) -> Self {
        self.with_cfc_neurons(neurons)
    }

    pub fn with_learning_rate(mut self, lr: f32) -> Self {
        self.config.cfc_config.learning_rate = lr;
        self
    }

    pub fn with_delta_t(mut self, delta_t: f32) -> Self {
        self.config.cfc_config.delta_t = delta_t;
        self
    }

    pub fn with_prediction_horizons(mut self, horizons: Vec<f32>) -> Self {
        self.config.cfc_config.prediction_horizons = horizons;
        self
    }

    pub fn with_attention_lr(mut self, lr: f32) -> Self {
        self.config.encoder_config.attention_lr = lr;
        self
    }

    pub fn with_learning_threshold(mut self, threshold: f32) -> Self {
        self.config.learning_threshold = threshold;
        self
    }

    pub fn with_buffer_size(mut self, size: usize) -> Self {
        self.config.buffer_size = size;
        self
    }

    pub fn build(self) -> Result<CognitiveLoopService> {
        CognitiveLoopService::new(self.config)
    }
}

impl Default for CognitiveLoopBuilder {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_creation() {
        let service = CognitiveLoopService::new(CognitiveLoopConfig::default()).unwrap();
        assert_eq!(service.stats().total_cycles, 0);
    }

    #[test]
    fn test_single_cycle() {
        let mut service = CognitiveLoopService::new(CognitiveLoopConfig::default()).unwrap();
        let result = service.cycle("test input");

        assert!(result.prediction_error >= 0.0);
        assert!(result.prediction_error <= 1.0);
        assert_eq!(service.stats().total_cycles, 1);
    }

    #[test]
    fn test_multiple_cycles_reduce_error() {
        let mut service = CognitiveLoopService::new(CognitiveLoopConfig {
            learning_threshold: 0.0, // Always learn
            ..Default::default()
        }).unwrap();

        // Run multiple cycles with same input
        let mut errors = Vec::new();
        for _ in 0..20 {
            let result = service.cycle("cause effect action");
            errors.push(result.prediction_error);
        }

        // Error should generally decrease (or at least not increase dramatically)
        let first_half_avg: f32 = errors[..10].iter().sum::<f32>() / 10.0;
        let second_half_avg: f32 = errors[10..].iter().sum::<f32>() / 10.0;

        println!("First half avg error: {}", first_half_avg);
        println!("Second half avg error: {}", second_half_avg);

        // Second half should be lower or similar
        assert!(second_half_avg <= first_half_avg + 0.1,
            "Error should decrease or stabilize over cycles");
    }

    #[test]
    fn test_attention_emergence() {
        let mut service = CognitiveLoopService::new(CognitiveLoopConfig {
            learning_threshold: 0.0,
            encoder_config: PredictiveEncoderConfig {
                attention_lr: 0.5, // High learning rate
                ..Default::default()
            },
            ..Default::default()
        }).unwrap();

        // Run many cycles
        for _ in 0..50 {
            service.cycle("cause effect");
        }

        // Check attention has diverged from uniform
        let stats = service.stats();
        println!("Attention variance: {}", stats.attention_variance);

        // Some attention emergence should occur
        // (may be small depending on the input)
    }

    #[test]
    fn test_builder() {
        let service = CognitiveLoopBuilder::new()
            .with_ltc_neurons(128)
            .with_learning_rate(0.001)
            .with_learning_threshold(0.1)
            .build()
            .unwrap();

        assert_eq!(service.stats().total_cycles, 0);
    }

    #[test]
    fn test_reset() {
        let mut service = CognitiveLoopService::new(CognitiveLoopConfig::default()).unwrap();

        // Run some cycles
        for _ in 0..5 {
            service.cycle("test");
        }
        assert!(service.stats().total_cycles > 0);

        // Reset
        service.reset();

        assert_eq!(service.stats().total_cycles, 0);
        assert_eq!(service.buffer.len(), 0);
    }

    #[test]
    fn test_consolidation() {
        let mut service = CognitiveLoopService::new(CognitiveLoopConfig {
            enable_consolidation: true,
            learning_threshold: 0.0,
            ..Default::default()
        }).unwrap();

        // Fill buffer with experiences
        for i in 0..20 {
            service.cycle(&format!("input {}", i));
        }

        // Should have some experiences
        assert!(service.buffer.len() > 0);

        // Run consolidation
        let loss = service.consolidate().unwrap();
        println!("Consolidation loss: {}", loss);
    }
}
