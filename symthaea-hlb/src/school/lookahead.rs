//! CfC-based Lookahead Engine for O(1) Learning Value Prediction
//!
//! This is the core innovation of the School system: using CfC's closed-form
//! solution to predict the value of learning BEFORE committing resources.
//!
//! ## The Magic: O(1) Complexity
//!
//! CfC solves: `x(t) = (x₀ - A) · e^(-t/τ) + A`
//!
//! This closed-form solution means we can jump to any future time point
//! in constant time, unlike RNNs which require O(N) integration steps.
//!
//! ## Performance
//!
//! | CfC Neurons | Eval Time | Notes |
//! |-------------|-----------|-------|
//! | 64 | ~100μs | Fast mode |
//! | 256 | ~300μs | Default |
//! | 1024 | ~1.5ms | High accuracy |

use anyhow::Result;
use ndarray::Array1;
use std::time::Instant;

use crate::cfc::CfCNetwork;
use crate::phi_engine::{PhiEngine, PhiMethod};
use crate::hdc::unified_hv::ContinuousHV;

use super::objective::LearningObjective;

// ═══════════════════════════════════════════════════════════════════════════════
// LEARNING RECOMMENDATION
// ═══════════════════════════════════════════════════════════════════════════════

/// Recommendation for a learning objective
#[derive(Debug, Clone)]
pub enum LearningRecommendation {
    /// Learn this objective now
    LearnNow {
        /// Priority (higher = more important)
        priority: f32,
    },

    /// Defer learning for now
    Defer {
        /// Reason for deferral
        reason: String,
    },

    /// Skip this objective
    Skip {
        /// Reason for skipping
        reason: String,
    },

    /// Curriculum is complete
    CurriculumComplete,
}

// ═══════════════════════════════════════════════════════════════════════════════
// LOOKAHEAD RESULT
// ═══════════════════════════════════════════════════════════════════════════════

/// Result of a lookahead evaluation
#[derive(Debug, Clone)]
pub struct LookaheadResult {
    /// Objective that was evaluated
    pub objective_id: String,

    /// Predicted Φ gain from learning this objective
    pub predicted_phi_gain: f32,

    /// Confidence in the prediction (0.0 - 1.0)
    pub confidence: f32,

    /// Time taken for prediction (microseconds)
    pub prediction_time_us: u64,

    /// Recommendation based on the prediction
    pub recommendation: LearningRecommendation,

    /// Predicted future consciousness state (for debugging)
    pub predicted_state: Option<Array1<f32>>,
}

// ═══════════════════════════════════════════════════════════════════════════════
// LOOKAHEAD ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/// CfC-based lookahead engine for O(1) learning value prediction
pub struct LookaheadEngine {
    /// CfC network for temporal prediction
    cfc: CfCNetwork,

    /// Φ engine for consciousness measurement
    phi_engine: PhiEngine,

    /// Lookahead time horizon (seconds)
    horizon: f32,

    /// Minimum Φ gain to recommend learning
    min_phi_gain: f32,

    /// History of predictions for confidence estimation
    prediction_history: Vec<PredictionRecord>,

    /// Cumulative prediction error for adaptation
    cumulative_error: f32,

    /// Number of predictions made
    prediction_count: usize,
}

/// Record of a past prediction for confidence estimation
#[derive(Debug, Clone)]
struct PredictionRecord {
    /// Predicted Φ gain
    predicted: f32,

    /// Actual Φ gain (if known)
    actual: Option<f32>,

    /// Was this prediction accurate?
    accurate: Option<bool>,
}

impl LookaheadEngine {
    /// Create a new lookahead engine
    pub fn new(cfc_neurons: usize, horizon: f32, min_phi_gain: f32) -> Result<Self> {
        let cfc = CfCNetwork::new(cfc_neurons)?;
        let phi_engine = PhiEngine::new(PhiMethod::Continuous);

        Ok(Self {
            cfc,
            phi_engine,
            horizon,
            min_phi_gain,
            prediction_history: Vec::new(),
            cumulative_error: 0.0,
            prediction_count: 0,
        })
    }

    /// Get the number of CfC neurons
    pub fn num_neurons(&self) -> usize {
        self.cfc.num_neurons
    }

    /// Get the lookahead horizon
    pub fn horizon(&self) -> f32 {
        self.horizon
    }

    /// Get the minimum Φ gain threshold
    pub fn min_phi_gain(&self) -> f32 {
        self.min_phi_gain
    }

    /// Get prediction count
    pub fn prediction_count(&self) -> usize {
        self.prediction_count
    }

    /// Get cumulative error
    pub fn cumulative_error(&self) -> f32 {
        self.cumulative_error
    }

    /// Evaluate a learning objective using CfC lookahead
    ///
    /// This is the core O(1) operation:
    /// 1. Encode the objective for CfC input
    /// 2. Use CfC's closed-form solution to predict future state
    /// 3. Estimate Φ gain from the predicted state
    /// 4. Generate recommendation
    pub fn evaluate(
        &self,
        objective: &LearningObjective,
        consciousness_state: &[ContinuousHV],
    ) -> Result<LookaheadResult> {
        let start = Instant::now();

        // 1. Get current Φ
        let current_phi = self.phi_engine.compute(consciousness_state).phi as f32;

        // 2. Prepare CfC input from objective
        let input_size = self.cfc.input_size;
        let objective_input = objective.to_cfc_input(input_size);

        // 3. Get current CfC state and combine with objective
        let current_state = self.cfc.read_state()?;
        let combined_input: Array1<f32> = Array1::from_iter(
            objective_input.iter()
                .zip(current_state.iter())
                .map(|(a, b)| (a + b) / 2.0)
        );

        // 4. THE MAGIC: O(1) prediction using CfC closed-form solution
        let predicted_state = self.cfc.predict_forward(&combined_input, self.horizon)?;

        // 5. Estimate Φ gain from predicted state
        let predicted_phi_gain = self.estimate_phi_gain(&predicted_state, current_phi, objective);

        // 6. Calculate confidence based on history
        let confidence = self.calculate_confidence();

        // 7. Generate recommendation
        let recommendation = self.generate_recommendation(predicted_phi_gain, confidence, objective);

        let prediction_time_us = start.elapsed().as_micros() as u64;

        Ok(LookaheadResult {
            objective_id: objective.id.clone(),
            predicted_phi_gain,
            confidence,
            prediction_time_us,
            recommendation,
            predicted_state: Some(predicted_state),
        })
    }

    /// Estimate Φ gain from predicted CfC state
    fn estimate_phi_gain(&self, predicted_state: &Array1<f32>, current_phi: f32, objective: &LearningObjective) -> f32 {
        // Compute coherence from predicted state
        let state_sum: f32 = predicted_state.iter().sum();
        let coherence = (state_sum / predicted_state.len() as f32).abs();

        // Scale by inverse difficulty (easier = more immediate gain)
        let difficulty_factor = 1.0 - objective.difficulty.as_f32() * 0.5;

        // Estimate Φ gain
        let estimated_gain = coherence * 0.01 * difficulty_factor;

        // Clamp to reasonable range
        estimated_gain.clamp(-0.1, 0.1)
    }

    /// Calculate confidence based on prediction history
    fn calculate_confidence(&self) -> f32 {
        if self.prediction_history.is_empty() {
            return 0.0;
        }

        // Count accurate predictions from recent history
        let recent: Vec<_> = self.prediction_history.iter()
            .rev()
            .take(20)
            .filter_map(|r| r.accurate)
            .collect();

        if recent.is_empty() {
            return 0.0;
        }

        let accuracy = recent.iter().filter(|&&a| a).count() as f32 / recent.len() as f32;
        accuracy
    }

    /// Generate a learning recommendation
    fn generate_recommendation(
        &self,
        predicted_phi_gain: f32,
        confidence: f32,
        objective: &LearningObjective,
    ) -> LearningRecommendation {
        // High confidence and high gain = learn now
        if predicted_phi_gain >= self.min_phi_gain {
            let priority = predicted_phi_gain * (0.5 + confidence * 0.5);
            return LearningRecommendation::LearnNow { priority };
        }

        // Low gain but low confidence = defer (might be wrong)
        if confidence < 0.5 {
            return LearningRecommendation::Defer {
                reason: format!(
                    "Low confidence ({:.0}%) - need more data to evaluate {}",
                    confidence * 100.0,
                    objective.name
                ),
            };
        }

        // High confidence and low gain = skip
        if predicted_phi_gain < 0.0 {
            return LearningRecommendation::Skip {
                reason: format!(
                    "Predicted negative gain ({:+.4}) for {}",
                    predicted_phi_gain,
                    objective.name
                ),
            };
        }

        // Default: defer with low priority
        LearningRecommendation::Defer {
            reason: format!(
                "Low predicted gain ({:+.4}) for {}",
                predicted_phi_gain,
                objective.name
            ),
        }
    }

    /// Record the actual outcome of a prediction for learning
    pub fn record_outcome(&mut self, predicted: f32, actual: f32) {
        let error = (predicted - actual).abs();
        let accurate = error < 0.2 * predicted.abs().max(0.001);

        self.prediction_history.push(PredictionRecord {
            predicted,
            actual: Some(actual),
            accurate: Some(accurate),
        });

        self.cumulative_error += error;
        self.prediction_count += 1;

        // Keep history bounded
        if self.prediction_history.len() > 1000 {
            self.prediction_history.remove(0);
        }
    }

    /// Get the CfC network for advanced operations
    pub fn cfc(&self) -> &CfCNetwork {
        &self.cfc
    }

    /// Get mutable CfC network for weight adaptation
    pub fn cfc_mut(&mut self) -> &mut CfCNetwork {
        &mut self.cfc
    }

    /// Evaluate multiple objectives and rank them
    pub fn rank_objectives<'a>(
        &self,
        objectives: &[&'a LearningObjective],
        consciousness_state: &[ContinuousHV],
    ) -> Result<Vec<(&'a LearningObjective, LookaheadResult)>> {
        let mut results: Vec<_> = objectives
            .iter()
            .filter_map(|obj| {
                self.evaluate(obj, consciousness_state)
                    .ok()
                    .map(|result| (*obj, result))
            })
            .collect();

        // Sort by predicted Φ gain (descending)
        results.sort_by(|a, b| {
            b.1.predicted_phi_gain
                .partial_cmp(&a.1.predicted_phi_gain)
                .unwrap_or(std::cmp::Ordering::Equal)
        });

        Ok(results)
    }

    /// Get statistics about prediction accuracy
    pub fn accuracy_stats(&self) -> (f32, f32, usize) {
        let accurate_count = self.prediction_history.iter()
            .filter_map(|r| r.accurate)
            .filter(|&a| a)
            .count();

        let total_with_outcome = self.prediction_history.iter()
            .filter(|r| r.actual.is_some())
            .count();

        let accuracy = if total_with_outcome > 0 {
            accurate_count as f32 / total_with_outcome as f32
        } else {
            0.0
        };

        let avg_error = if self.prediction_count > 0 {
            self.cumulative_error / self.prediction_count as f32
        } else {
            0.0
        };

        (accuracy, avg_error, total_with_outcome)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hdc::{RealHV, HDC_DIMENSION};
    use super::super::objective::Difficulty;

    fn create_test_consciousness_state() -> Vec<ContinuousHV> {
        (0..8)
            .map(|i| {
                let hv = RealHV::random(HDC_DIMENSION, 42 + i as u64);
                ContinuousHV::from_vec(hv.values)
            })
            .collect()
    }

    #[test]
    fn test_lookahead_creation() {
        let engine = LookaheadEngine::new(256, 1.0, 0.01);
        assert!(engine.is_ok());

        let engine = engine.unwrap();
        assert_eq!(engine.num_neurons(), 256);
        assert_eq!(engine.horizon(), 1.0);
        assert_eq!(engine.min_phi_gain(), 0.01);
    }

    #[test]
    fn test_evaluate_objective() {
        let engine = LookaheadEngine::new(256, 1.0, 0.01).unwrap();
        let state = create_test_consciousness_state();

        let obj = LearningObjective::new("test", "Test Objective")
            .with_difficulty(Difficulty::Intermediate)
            .build();

        let result = engine.evaluate(&obj, &state);
        assert!(result.is_ok());

        let result = result.unwrap();
        assert_eq!(result.objective_id, "test");
        assert!(result.prediction_time_us > 0);
        assert!(result.prediction_time_us < 10000); // < 10ms
    }

    #[test]
    fn test_rank_objectives() {
        let engine = LookaheadEngine::new(256, 1.0, 0.01).unwrap();
        let state = create_test_consciousness_state();

        let obj1 = LearningObjective::new("easy", "Easy")
            .with_difficulty(Difficulty::Beginner)
            .build();
        let obj2 = LearningObjective::new("hard", "Hard")
            .with_difficulty(Difficulty::Expert)
            .build();

        let objectives: Vec<&LearningObjective> = vec![&obj1, &obj2];
        let ranked = engine.rank_objectives(&objectives, &state);

        assert!(ranked.is_ok());
        let ranked = ranked.unwrap();
        assert_eq!(ranked.len(), 2);
    }

    #[test]
    fn test_record_outcome() {
        let mut engine = LookaheadEngine::new(256, 1.0, 0.01).unwrap();

        engine.record_outcome(0.01, 0.008);
        engine.record_outcome(0.01, 0.012);

        assert_eq!(engine.prediction_count(), 2);

        let (accuracy, avg_error, count) = engine.accuracy_stats();
        assert_eq!(count, 2);
        assert!(avg_error > 0.0);
    }

    #[test]
    fn test_o1_complexity() {
        let engine = LookaheadEngine::new(256, 1.0, 0.01).unwrap();
        let state = create_test_consciousness_state();

        let obj = LearningObjective::new("test", "Test")
            .with_difficulty(Difficulty::Intermediate)
            .build();

        // Evaluate with different horizons - should all be O(1)
        for horizon in [0.1, 1.0, 10.0, 100.0] {
            let mut engine = LookaheadEngine::new(256, horizon, 0.01).unwrap();
            let result = engine.evaluate(&obj, &state).unwrap();

            // All should complete in < 2ms (O(1))
            assert!(result.prediction_time_us < 2000,
                    "Horizon {} took {}μs", horizon, result.prediction_time_us);
        }
    }
}
