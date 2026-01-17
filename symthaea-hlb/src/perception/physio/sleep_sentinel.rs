//! Sleep Sentinel - Consciousness State Detection via LTC Dynamics
//!
//! ## Project Hypnos: Computational Biomarker for Consciousness
//!
//! This module implements a dual-channel LTC architecture that detects
//! consciousness states (wake vs sleep stages) from EEG signals.
//!
//! ## Architecture
//!
//! ```text
//! Fpz-Cz (Frontal)  ─┬─► [Frontal LTC]  ─┬─► [Global Integrator] ─► State
//!                    │                    │
//! Pz-Oz (Occipital) ─┴─► [Occipital LTC] ─┘
//!                              ▲
//!                              │
//!                    Synchronization Measure (Φ proxy)
//! ```
//!
//! ## Key Insight
//!
//! Different sleep stages have distinct integration signatures:
//!
//! - **Wake**: High complexity, low global synchronization → Medium Φ
//! - **N1/N2**: Variable, transitional
//! - **N3 (Deep)**: Delta waves, HIGH global synchronization → HIGH Φ
//! - **REM**: High complexity, LOW integration (paradox!) → LOW Φ
//!
//! The REM paradox is KEY: The brain is active but disconnected.
//! Standard statistics see "activity". Φ captures "integration".
//!
//! ## Why LTC Wins Here
//!
//! EEG is continuous dynamics. Transformers would discretize into windows,
//! losing the phase relationships that define synchronization. The LTC's
//! adaptive τ (time constant) naturally tracks the dominant frequency,
//! and cross-channel coherence emerges from the integrator dynamics.

use crate::unified_ltc::{UnifiedLTC, UnifiedLTCConfig, LearningAlgorithm};
use super::SleepStage;
use std::collections::VecDeque;

/// Configuration for Sleep Sentinel
#[derive(Debug, Clone)]
pub struct SleepSentinelConfig {
    /// Number of neurons in local LTCs (frontal/occipital)
    pub local_neurons: usize,
    /// Number of neurons in global integrator
    pub global_neurons: usize,
    /// Timestep in milliseconds
    pub dt_ms: f32,
    /// Integration window size in samples
    pub integration_window: usize,
    /// Base time constant (should match EEG frequency range)
    pub tau_base: f32,
    /// Minimum time constant
    pub tau_min: f32,
    /// Maximum time constant
    pub tau_max: f32,
    /// Learning rate for online adaptation
    pub learning_rate: f32,
    /// Number of steps per epoch
    pub steps_per_epoch: usize,
    /// Complexity threshold for wake detection
    pub complexity_threshold: f32,
    /// Synchrony threshold for deep sleep detection
    pub synchrony_threshold: f32,
}

impl Default for SleepSentinelConfig {
    fn default() -> Self {
        Self {
            local_neurons: 64,      // Small but sufficient
            global_neurons: 128,    // Larger for integration
            dt_ms: 10.0,            // 100 Hz effective rate
            integration_window: 300, // 3 seconds at 100 Hz
            tau_base: 100.0,        // 100ms base (10 Hz sensitivity)
            tau_min: 10.0,          // 10ms min (100 Hz - gamma)
            tau_max: 1000.0,        // 1s max (1 Hz - delta)
            learning_rate: 0.001,
            steps_per_epoch: 3000,  // 30 seconds at 100 Hz
            complexity_threshold: 0.6,
            synchrony_threshold: 0.7,
        }
    }
}

/// Detected consciousness state
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ConsciousnessState {
    /// Awake, alert
    Awake,
    /// Light sleep (N1/N2)
    LightSleep,
    /// Deep sleep (N3) - HIGH integration
    DeepSleep,
    /// REM sleep - HIGH activity, LOW integration
    REM,
    /// Uncertain/transitional
    Transitional,
}

impl ConsciousnessState {
    /// Convert to predicted sleep stage
    pub fn to_sleep_stage(&self) -> SleepStage {
        match self {
            ConsciousnessState::Awake => SleepStage::Wake,
            ConsciousnessState::LightSleep => SleepStage::N2, // Conservative
            ConsciousnessState::DeepSleep => SleepStage::N3,
            ConsciousnessState::REM => SleepStage::REM,
            ConsciousnessState::Transitional => SleepStage::N1,
        }
    }

    pub fn name(&self) -> &'static str {
        match self {
            ConsciousnessState::Awake => "Awake",
            ConsciousnessState::LightSleep => "Light Sleep",
            ConsciousnessState::DeepSleep => "Deep Sleep",
            ConsciousnessState::REM => "REM",
            ConsciousnessState::Transitional => "Transitional",
        }
    }
}

/// Integration metrics (Φ proxy)
#[derive(Debug, Clone)]
pub struct IntegrationMetrics {
    /// Complexity (entropy) of combined signal
    pub complexity: f32,
    /// Synchronization between frontal and occipital
    pub synchrony: f32,
    /// Causal influence from frontal to occipital
    pub frontal_to_occipital: f32,
    /// Causal influence from occipital to frontal
    pub occipital_to_frontal: f32,
    /// Global integration measure (our Φ proxy)
    pub phi_proxy: f32,
    /// Dominant frequency estimate
    pub dominant_freq_hz: f32,
    /// State trajectory variance
    pub trajectory_variance: f32,
}

impl Default for IntegrationMetrics {
    fn default() -> Self {
        Self {
            complexity: 0.5,
            synchrony: 0.5,
            frontal_to_occipital: 0.5,
            occipital_to_frontal: 0.5,
            phi_proxy: 0.5,
            dominant_freq_hz: 10.0,
            trajectory_variance: 0.1,
        }
    }
}

/// Sleep Sentinel - Dual-channel LTC for consciousness detection
pub struct SleepSentinel {
    /// Configuration
    config: SleepSentinelConfig,
    /// Frontal cortex LTC (Fpz-Cz)
    frontal_ltc: UnifiedLTC,
    /// Occipital cortex LTC (Pz-Oz)
    occipital_ltc: UnifiedLTC,
    /// Global integrator LTC
    integrator_ltc: UnifiedLTC,
    /// Recent frontal states (for metrics)
    frontal_history: VecDeque<Vec<f32>>,
    /// Recent occipital states (for metrics)
    occipital_history: VecDeque<Vec<f32>>,
    /// Recent integrator states (for metrics)
    integrator_history: VecDeque<Vec<f32>>,
    /// Sample counter
    sample_count: u64,
    /// Current integration metrics
    current_metrics: IntegrationMetrics,
    /// Running statistics
    stats: SleepSentinelStats,
}

/// Running statistics
#[derive(Debug, Clone, Default)]
pub struct SleepSentinelStats {
    pub epochs_processed: u64,
    pub samples_processed: u64,
    pub predictions: Vec<(ConsciousnessState, SleepStage)>, // (predicted, actual)
    pub accuracy_history: Vec<f32>,
}

impl SleepSentinel {
    /// Create new Sleep Sentinel
    pub fn new(config: SleepSentinelConfig) -> Self {
        // Create frontal LTC (tracks Fpz-Cz dynamics)
        let mut frontal_config = UnifiedLTCConfig::scalar(
            config.local_neurons,
            1,  // Single channel input
            config.local_neurons, // Full state output
        );
        frontal_config.dt = config.dt_ms / 1000.0;
        frontal_config.tau_base = config.tau_base / 1000.0;
        frontal_config.tau_min = config.tau_min / 1000.0;
        frontal_config.tau_max = config.tau_max / 1000.0;
        frontal_config.learning = LearningAlgorithm::None; // Inference only

        // Create occipital LTC (tracks Pz-Oz dynamics)
        let occipital_config = frontal_config.clone();

        // Create integrator LTC (combines both)
        let mut integrator_config = UnifiedLTCConfig::scalar(
            config.global_neurons,
            config.local_neurons * 2, // Both local states
            config.global_neurons,
        );
        integrator_config.dt = config.dt_ms / 1000.0;
        integrator_config.tau_base = config.tau_base / 1000.0 * 2.0; // Slower for integration
        integrator_config.tau_min = config.tau_min / 1000.0;
        integrator_config.tau_max = config.tau_max / 1000.0 * 2.0;
        integrator_config.learning = LearningAlgorithm::None;

        let frontal_ltc = UnifiedLTC::new(frontal_config).expect("Failed to create frontal LTC");
        let occipital_ltc = UnifiedLTC::new(occipital_config).expect("Failed to create occipital LTC");
        let integrator_ltc = UnifiedLTC::new(integrator_config).expect("Failed to create integrator LTC");

        Self {
            config,
            frontal_ltc,
            occipital_ltc,
            integrator_ltc,
            frontal_history: VecDeque::with_capacity(500),
            occipital_history: VecDeque::with_capacity(500),
            integrator_history: VecDeque::with_capacity(500),
            sample_count: 0,
            current_metrics: IntegrationMetrics::default(),
            stats: SleepSentinelStats::default(),
        }
    }

    /// Process a single sample pair (frontal, occipital)
    pub fn process_sample(&mut self, frontal: f32, occipital: f32) -> ConsciousnessState {
        // Normalize inputs to [-1, 1] range (assume microvolts)
        let frontal_norm = (frontal / 100.0).clamp(-1.0, 1.0);
        let occipital_norm = (occipital / 100.0).clamp(-1.0, 1.0);

        // Step frontal LTC
        let (frontal_out, _) = self.frontal_ltc.forward(&[frontal_norm])
            .expect("Frontal forward failed");

        // Step occipital LTC
        let (occipital_out, _) = self.occipital_ltc.forward(&[occipital_norm])
            .expect("Occipital forward failed");

        // Combine states for integrator
        let mut combined = Vec::with_capacity(self.config.local_neurons * 2);
        combined.extend_from_slice(&frontal_out[..self.config.local_neurons.min(frontal_out.len())]);
        combined.extend_from_slice(&occipital_out[..self.config.local_neurons.min(occipital_out.len())]);

        // Pad if necessary
        while combined.len() < self.config.local_neurons * 2 {
            combined.push(0.0);
        }

        // Step integrator
        let (integrator_out, _) = self.integrator_ltc.forward(&combined)
            .expect("Integrator forward failed");

        // Record history
        self.frontal_history.push_back(frontal_out);
        self.occipital_history.push_back(occipital_out);
        self.integrator_history.push_back(integrator_out);

        // Trim history
        while self.frontal_history.len() > self.config.integration_window {
            self.frontal_history.pop_front();
            self.occipital_history.pop_front();
            self.integrator_history.pop_front();
        }

        self.sample_count += 1;
        self.stats.samples_processed += 1;

        // Update metrics periodically (every 10 samples for efficiency)
        if self.sample_count % 10 == 0 && self.frontal_history.len() >= 50 {
            self.update_metrics();
        }

        // Classify state
        self.classify_state()
    }

    /// Update integration metrics from history
    fn update_metrics(&mut self) {
        if self.frontal_history.len() < 50 {
            return;
        }

        let n = self.frontal_history.len();

        // 1. Compute complexity (variance of integrator state)
        let integrator_mean: Vec<f32> = (0..self.config.global_neurons)
            .map(|i| {
                self.integrator_history.iter()
                    .map(|s| s.get(i).copied().unwrap_or(0.0))
                    .sum::<f32>() / n as f32
            })
            .collect();

        let variance: f32 = self.integrator_history.iter()
            .map(|s| {
                s.iter()
                    .zip(integrator_mean.iter())
                    .map(|(x, m)| (x - m).powi(2))
                    .sum::<f32>()
            })
            .sum::<f32>() / (n * self.config.global_neurons) as f32;

        self.current_metrics.complexity = (variance * 10.0).min(1.0);
        self.current_metrics.trajectory_variance = variance;

        // 2. Compute synchrony (correlation between frontal and occipital)
        let mut correlation = 0.0;
        let mut frontal_var = 0.0;
        let mut occipital_var = 0.0;

        // Use first component as representative
        let frontal_mean: f32 = self.frontal_history.iter()
            .map(|s| s.get(0).copied().unwrap_or(0.0))
            .sum::<f32>() / n as f32;
        let occipital_mean: f32 = self.occipital_history.iter()
            .map(|s| s.get(0).copied().unwrap_or(0.0))
            .sum::<f32>() / n as f32;

        for (f, o) in self.frontal_history.iter().zip(self.occipital_history.iter()) {
            let f_val = f.get(0).copied().unwrap_or(0.0) - frontal_mean;
            let o_val = o.get(0).copied().unwrap_or(0.0) - occipital_mean;
            correlation += f_val * o_val;
            frontal_var += f_val * f_val;
            occipital_var += o_val * o_val;
        }

        let denom = (frontal_var * occipital_var).sqrt();
        self.current_metrics.synchrony = if denom > 1e-6 {
            ((correlation / denom) + 1.0) / 2.0 // Normalize to [0, 1]
        } else {
            0.5
        };

        // 3. Estimate causal influence (simplified: lagged correlation)
        let lag = 5; // ~50ms lag at 100Hz
        if n > lag {
            // Frontal → Occipital
            let mut causal_fo = 0.0;
            for i in lag..n {
                let f_prev = self.frontal_history.iter().nth(i - lag)
                    .and_then(|s| s.get(0).copied()).unwrap_or(0.0);
                let o_curr = self.occipital_history.iter().nth(i)
                    .and_then(|s| s.get(0).copied()).unwrap_or(0.0);
                causal_fo += (f_prev - frontal_mean) * (o_curr - occipital_mean);
            }

            // Occipital → Frontal
            let mut causal_of = 0.0;
            for i in lag..n {
                let o_prev = self.occipital_history.iter().nth(i - lag)
                    .and_then(|s| s.get(0).copied()).unwrap_or(0.0);
                let f_curr = self.frontal_history.iter().nth(i)
                    .and_then(|s| s.get(0).copied()).unwrap_or(0.0);
                causal_of += (o_prev - occipital_mean) * (f_curr - frontal_mean);
            }

            let count = (n - lag) as f32;
            self.current_metrics.frontal_to_occipital = ((causal_fo / count).tanh() + 1.0) / 2.0;
            self.current_metrics.occipital_to_frontal = ((causal_of / count).tanh() + 1.0) / 2.0;
        }

        // 4. Compute Φ proxy (integration = synchrony * bidirectional causality)
        let bidirectional = (self.current_metrics.frontal_to_occipital
            + self.current_metrics.occipital_to_frontal) / 2.0;
        self.current_metrics.phi_proxy = self.current_metrics.synchrony * bidirectional;

        // 5. Estimate dominant frequency from zero crossings
        let mut crossings = 0;
        let mut prev_val = self.integrator_history.front()
            .and_then(|s| s.get(0).copied()).unwrap_or(0.0);
        for state in self.integrator_history.iter().skip(1) {
            let val = state.get(0).copied().unwrap_or(0.0);
            if (val > 0.0) != (prev_val > 0.0) {
                crossings += 1;
            }
            prev_val = val;
        }
        let duration_sec = n as f32 * self.config.dt_ms / 1000.0;
        self.current_metrics.dominant_freq_hz = if duration_sec > 0.0 {
            crossings as f32 / (2.0 * duration_sec)
        } else {
            10.0
        };
    }

    /// Classify consciousness state based on metrics
    fn classify_state(&self) -> ConsciousnessState {
        let m = &self.current_metrics;

        // Decision logic based on IIT-inspired principles:
        //
        // Wake: High complexity (desynchronized alpha/beta)
        // Deep Sleep: High synchrony, low complexity (synchronized delta)
        // REM: High complexity but LOW integration (paradox!)
        // Light Sleep: In between

        // Simple thresholding (can be trained/tuned)
        let high_complexity = m.complexity > self.config.complexity_threshold;
        let high_synchrony = m.synchrony > self.config.synchrony_threshold;
        let high_phi = m.phi_proxy > 0.5;
        let low_freq = m.dominant_freq_hz < 8.0;
        let high_freq = m.dominant_freq_hz > 12.0;

        // Classification rules
        if high_complexity && high_freq && !high_synchrony {
            // Active brain, desynchronized → Wake
            ConsciousnessState::Awake
        } else if high_synchrony && low_freq && high_phi {
            // Synchronized delta, high integration → Deep Sleep
            ConsciousnessState::DeepSleep
        } else if high_complexity && !high_phi && !high_synchrony {
            // Active but disconnected → REM (the paradox!)
            ConsciousnessState::REM
        } else if m.complexity > 0.3 && m.synchrony > 0.4 {
            // Moderate everything → Light Sleep
            ConsciousnessState::LightSleep
        } else {
            // Uncertain
            ConsciousnessState::Transitional
        }
    }

    /// Process a full 30-second epoch
    pub fn process_epoch(
        &mut self,
        frontal_data: &[f64],
        occipital_data: &[f64],
    ) -> (ConsciousnessState, IntegrationMetrics) {
        // Reset history for clean epoch
        self.frontal_history.clear();
        self.occipital_history.clear();
        self.integrator_history.clear();

        // Reset LTC states
        self.frontal_ltc.reset();
        self.occipital_ltc.reset();
        self.integrator_ltc.reset();

        // Subsample to match our effective rate
        let target_samples = self.config.steps_per_epoch;
        let step = frontal_data.len().max(1) / target_samples.max(1);
        let step = step.max(1);

        let mut last_state = ConsciousnessState::Transitional;

        for i in (0..frontal_data.len()).step_by(step) {
            let f = frontal_data[i] as f32;
            let o = occipital_data.get(i).copied().unwrap_or(0.0) as f32;
            last_state = self.process_sample(f, o);
        }

        self.stats.epochs_processed += 1;

        (last_state, self.current_metrics.clone())
    }

    /// Train on labeled epoch
    pub fn train_epoch(
        &mut self,
        frontal_data: &[f64],
        occipital_data: &[f64],
        actual_stage: SleepStage,
    ) -> (ConsciousnessState, bool) {
        let (predicted_state, _metrics) = self.process_epoch(frontal_data, occipital_data);
        let predicted_stage = predicted_state.to_sleep_stage();

        let correct = predicted_stage == actual_stage;
        self.stats.predictions.push((predicted_state, actual_stage));

        // TODO: Online learning via threshold adjustment
        // For now, just record for analysis

        (predicted_state, correct)
    }

    /// Get current integration metrics
    pub fn metrics(&self) -> &IntegrationMetrics {
        &self.current_metrics
    }

    /// Get statistics
    pub fn stats(&self) -> &SleepSentinelStats {
        &self.stats
    }

    /// Calculate overall accuracy
    pub fn accuracy(&self) -> f32 {
        if self.stats.predictions.is_empty() {
            return 0.0;
        }

        let correct = self.stats.predictions.iter()
            .filter(|(pred, actual)| pred.to_sleep_stage() == *actual)
            .count();

        correct as f32 / self.stats.predictions.len() as f32
    }

    /// Get per-class accuracy
    pub fn per_class_accuracy(&self) -> Vec<(SleepStage, f32, usize)> {
        let stages = [
            SleepStage::Wake,
            SleepStage::N1,
            SleepStage::N2,
            SleepStage::N3,
            SleepStage::REM,
        ];

        stages.iter().map(|&stage| {
            let samples: Vec<_> = self.stats.predictions.iter()
                .filter(|(_, actual)| *actual == stage)
                .collect();

            let correct = samples.iter()
                .filter(|(pred, _)| pred.to_sleep_stage() == stage)
                .count();

            let accuracy = if samples.is_empty() {
                0.0
            } else {
                correct as f32 / samples.len() as f32
            };

            (stage, accuracy, samples.len())
        }).collect()
    }

    /// Reset all state
    pub fn reset(&mut self) {
        self.frontal_ltc.reset();
        self.occipital_ltc.reset();
        self.integrator_ltc.reset();
        self.frontal_history.clear();
        self.occipital_history.clear();
        self.integrator_history.clear();
        self.sample_count = 0;
        self.current_metrics = IntegrationMetrics::default();
    }

    /// Get summary string
    pub fn summary(&self) -> String {
        format!(
            "Sleep Sentinel Summary:\n\
             Epochs: {}\n\
             Samples: {}\n\
             Accuracy: {:.1}%\n\n\
             Per-class:\n{}",
            self.stats.epochs_processed,
            self.stats.samples_processed,
            self.accuracy() * 100.0,
            self.per_class_accuracy().iter()
                .map(|(stage, acc, n)| format!("  {}: {:.1}% (n={})", stage.name(), acc * 100.0, n))
                .collect::<Vec<_>>()
                .join("\n")
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::f64::consts::PI;

    /// Generate synthetic EEG-like signal
    fn generate_synthetic_eeg(
        stage: SleepStage,
        sample_rate: f64,
        duration_sec: f64,
    ) -> (Vec<f64>, Vec<f64>) {
        let n = (sample_rate * duration_sec) as usize;
        let mut frontal = Vec::with_capacity(n);
        let mut occipital = Vec::with_capacity(n);

        for i in 0..n {
            let t = i as f64 / sample_rate;

            // Base signals depend on stage
            let (f, o) = match stage {
                SleepStage::Wake => {
                    // High-freq, desynchronized alpha/beta
                    let alpha = 30.0 * (2.0 * PI * 10.0 * t).sin();
                    let beta = 15.0 * (2.0 * PI * 20.0 * t).sin();
                    // Different phases for frontal/occipital
                    (
                        alpha + beta + 10.0 * (t * 31.4).sin(),
                        alpha * 0.8 + beta * 1.2 + 10.0 * (t * 28.3).sin(),
                    )
                }
                SleepStage::N3 => {
                    // Synchronized delta waves
                    let delta = 75.0 * (2.0 * PI * 2.0 * t).sin();
                    // Highly correlated between channels
                    (delta, delta * 0.95 + 5.0 * (t * 12.5).sin())
                }
                SleepStage::REM => {
                    // High activity but desynchronized (like wake but different)
                    let mixed = 25.0 * (2.0 * PI * 8.0 * t).sin()
                        + 20.0 * (2.0 * PI * 15.0 * t).sin();
                    // Very different between channels
                    (
                        mixed + 15.0 * (t * 47.1).sin(),
                        mixed * 0.6 + 25.0 * (t * 33.2).sin(),
                    )
                }
                _ => {
                    // Light sleep - intermediate
                    let theta = 40.0 * (2.0 * PI * 6.0 * t).sin();
                    (
                        theta + 10.0 * (t * 25.0).sin(),
                        theta * 0.7 + 15.0 * (t * 22.0).sin(),
                    )
                }
            };

            // Add noise
            let noise_f = 5.0 * ((i as f64 * 0.1234).sin() * (i as f64 * 0.5678).cos());
            let noise_o = 5.0 * ((i as f64 * 0.2345).sin() * (i as f64 * 0.6789).cos());

            frontal.push(f + noise_f);
            occipital.push(o + noise_o);
        }

        (frontal, occipital)
    }

    #[test]
    fn test_sentinel_creation() {
        let config = SleepSentinelConfig::default();
        let sentinel = SleepSentinel::new(config);
        assert_eq!(sentinel.stats.epochs_processed, 0);
    }

    #[test]
    fn test_wake_detection() {
        let config = SleepSentinelConfig::default();
        let mut sentinel = SleepSentinel::new(config);

        let (frontal, occipital) = generate_synthetic_eeg(SleepStage::Wake, 100.0, 30.0);
        let (state, metrics) = sentinel.process_epoch(&frontal, &occipital);

        println!("Wake detection: {:?}", state);
        println!("Metrics: complexity={:.2}, synchrony={:.2}, phi={:.2}, freq={:.1}Hz",
            metrics.complexity, metrics.synchrony, metrics.phi_proxy, metrics.dominant_freq_hz);

        // Wake should have high complexity, lower synchrony
        assert!(metrics.complexity > 0.3, "Wake should have complexity > 0.3");
    }

    #[test]
    fn test_deep_sleep_detection() {
        let config = SleepSentinelConfig::default();
        let mut sentinel = SleepSentinel::new(config);

        let (frontal, occipital) = generate_synthetic_eeg(SleepStage::N3, 100.0, 30.0);
        let (state, metrics) = sentinel.process_epoch(&frontal, &occipital);

        println!("Deep sleep detection: {:?}", state);
        println!("Metrics: complexity={:.2}, synchrony={:.2}, phi={:.2}, freq={:.1}Hz",
            metrics.complexity, metrics.synchrony, metrics.phi_proxy, metrics.dominant_freq_hz);

        // Deep sleep should have high synchrony
        assert!(metrics.synchrony > 0.5, "Deep sleep should have synchrony > 0.5");
    }

    #[test]
    fn test_rem_paradox() {
        let config = SleepSentinelConfig::default();
        let mut sentinel = SleepSentinel::new(config);

        let (frontal, occipital) = generate_synthetic_eeg(SleepStage::REM, 100.0, 30.0);
        let (_state, metrics) = sentinel.process_epoch(&frontal, &occipital);

        println!("REM detection: complexity={:.2}, synchrony={:.2}, phi={:.2}",
            metrics.complexity, metrics.synchrony, metrics.phi_proxy);

        // REM paradox: high complexity but low integration
        // This is what makes it interesting!
        assert!(metrics.complexity > 0.2, "REM should have some complexity");
    }

    #[test]
    fn test_discrimination() {
        let config = SleepSentinelConfig::default();
        let mut sentinel = SleepSentinel::new(config);

        // Test that different stages produce different metrics
        let stages = [SleepStage::Wake, SleepStage::N3, SleepStage::REM];
        let mut results = Vec::new();

        for stage in &stages {
            sentinel.reset();
            let (frontal, occipital) = generate_synthetic_eeg(*stage, 100.0, 30.0);
            let (_, metrics) = sentinel.process_epoch(&frontal, &occipital);
            results.push((*stage, metrics.complexity, metrics.synchrony, metrics.phi_proxy));
        }

        println!("\nStage Discrimination:");
        for (stage, c, s, p) in &results {
            println!("  {:?}: complexity={:.2}, synchrony={:.2}, phi={:.2}", stage, c, s, p);
        }

        // Verify stages are distinguishable
        // Deep sleep should have highest synchrony
        let n3_sync = results.iter().find(|(s, _, _, _)| *s == SleepStage::N3).unwrap().2;
        let wake_sync = results.iter().find(|(s, _, _, _)| *s == SleepStage::Wake).unwrap().2;
        assert!(n3_sync > wake_sync, "Deep sleep should have higher synchrony than wake");
    }
}
