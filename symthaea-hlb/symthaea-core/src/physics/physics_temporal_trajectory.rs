//! # Phase 2: Temporal Trajectory Binding
//!
//! Binds physics simulation states across time to create "trajectory consciousness" -
//! a measure of how coherently a design evolves through operational states.
//!
//! ## Conceptual Foundation
//!
//! A fusion reactor design isn't just a static point in design space - it's a trajectory
//! through operational states over its lifetime:
//!
//! ```text
//!   Time →
//!   t₀     t₁     t₂     t₃     ...    tₙ
//!   │      │      │      │             │
//!   ▼      ▼      ▼      ▼             ▼
//! ┌───┐  ┌───┐  ┌───┐  ┌───┐       ┌───┐
//! │S₀ │──│S₁ │──│S₂ │──│S₃ │─ ... ─│Sₙ │
//! └───┘  └───┘  └───┘  └───┘       └───┘
//!   │      │      │      │             │
//!   └──────┴──────┴──────┴─────────────┘
//!                    │
//!                    ▼
//!            ┌──────────────┐
//!            │  TRAJECTORY  │
//!            │  BINDING     │
//!            └──────────────┘
//!                    │
//!                    ▼
//!        Unified Trajectory Vector
//! ```
//!
//! ## Metrics
//!
//! - **Trajectory Coherence**: How smoothly does the design evolve?
//! - **Anticipation Match**: How predictable are state transitions?
//! - **Narrative Unity**: Does the trajectory form a coherent "story"?
//! - **Temporal Integration**: Past-present-future binding strength

use crate::genesis::GenesisSeed;
use crate::hdc::real_hv::RealHV;
use crate::hdc::temporal_binding::{
    TemporalBindingConfig, TemporalBindingEngine, StreamHealth,
};
use super::physics_consciousness_integration::{
    PhysicsConsciousnessEngine, EncodedPhysicsState, ConsciousnessMetrics,
};
use super::coupled_physics::{CoupledSimulationResult, OperatingConditions, CoupledPhysicsEngine};
use super::standard_model::PHYSICS_DIM;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

/// Configuration for physics trajectory binding
#[derive(Clone, Debug)]
pub struct TrajectoryConfig {
    /// Window size (number of states to keep in memory)
    pub window_size: usize,
    /// Decay rate for past states
    pub decay_rate: f64,
    /// Weight for anticipatory influence
    pub anticipation_weight: f64,
    /// HDC dimension (must match physics encoding)
    pub dim: usize,
}

impl Default for TrajectoryConfig {
    fn default() -> Self {
        Self {
            window_size: 50,  // ~50 operational cycles
            decay_rate: 0.05, // Slower decay for design trajectories
            anticipation_weight: 0.2,
            dim: PHYSICS_DIM,
        }
    }
}

/// A physics state along the trajectory
#[derive(Clone, Debug)]
pub struct TrajectoryState {
    /// Step number in the trajectory
    pub step: usize,
    /// The physics simulation result
    pub result: CoupledSimulationResult,
    /// Encoded as HDC vector
    pub encoded: EncodedPhysicsState,
    /// Consciousness metrics for this state
    pub metrics: ConsciousnessMetrics,
    /// Temporal binding with previous states
    pub temporal_binding: f32,
    /// Anticipation match (how well predicted)
    pub anticipation_match: f32,
    /// Narrative continuity
    pub continuity: f32,
}

/// Summary metrics for an entire trajectory
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TrajectoryMetrics {
    /// Overall trajectory consciousness
    pub trajectory_consciousness: f32,
    /// How smoothly the design evolves
    pub coherence: f32,
    /// Past-present binding strength
    pub past_binding: f32,
    /// Present-future binding strength
    pub future_binding: f32,
    /// Narrative length (states integrated)
    pub narrative_length: usize,
    /// Mean state consciousness
    pub mean_state_consciousness: f32,
    /// Variance in state consciousness
    pub consciousness_variance: f32,
    /// Maximum consciousness reached
    pub peak_consciousness: f32,
    /// Minimum consciousness reached
    pub valley_consciousness: f32,
}

impl TrajectoryMetrics {
    /// Check if trajectory is healthy
    pub fn is_healthy(&self) -> bool {
        self.coherence > 0.5 && self.trajectory_consciousness > 0.3
    }

    /// Summary string
    pub fn summary(&self) -> String {
        format!(
            "Trajectory[C={:.3}, coherence={:.3}, states={}, range={:.3}-{:.3}]",
            self.trajectory_consciousness,
            self.coherence,
            self.narrative_length,
            self.valley_consciousness,
            self.peak_consciousness
        )
    }
}

/// Physics trajectory binding engine
///
/// Binds a sequence of physics states into a unified trajectory representation
/// that captures the design's evolution through operational space.
pub struct PhysicsTrajectoryEngine {
    /// Temporal binding engine (uses RealHV internally)
    temporal: TemporalBindingEngine,
    /// Physics consciousness engine
    consciousness: PhysicsConsciousnessEngine,
    /// History of trajectory states
    history: VecDeque<TrajectoryState>,
    /// Configuration
    config: TrajectoryConfig,
    /// Step counter
    step: usize,
    /// Running trajectory vector (accumulated)
    trajectory_vector: RealHV,
    /// Running mean consciousness
    consciousness_sum: f32,
    /// Running max consciousness
    consciousness_max: f32,
    /// Running min consciousness
    consciousness_min: f32,
}

impl PhysicsTrajectoryEngine {
    /// Create from genesis seed
    pub fn from_genesis(genesis: &GenesisSeed) -> Self {
        Self::with_config(genesis, TrajectoryConfig::default())
    }

    /// Create with custom configuration
    pub fn with_config(genesis: &GenesisSeed, config: TrajectoryConfig) -> Self {
        let temporal_config = TemporalBindingConfig {
            window_size: config.window_size,
            decay_rate: config.decay_rate,
            anticipation_weight: config.anticipation_weight,
            dim: config.dim,
        };

        Self {
            temporal: TemporalBindingEngine::new(temporal_config),
            consciousness: PhysicsConsciousnessEngine::from_genesis(genesis),
            history: VecDeque::new(),
            config,
            step: 0,
            trajectory_vector: RealHV::zero(PHYSICS_DIM),
            consciousness_sum: 0.0,
            consciousness_max: f32::NEG_INFINITY,
            consciousness_min: f32::INFINITY,
        }
    }

    /// Process a new simulation result into the trajectory
    pub fn process(&mut self, result: &CoupledSimulationResult) -> TrajectoryState {
        self.step += 1;

        // Encode the physics state
        let encoded = self.consciousness.encode_simulation(result);
        let metrics = self.consciousness.compute_metrics(result);

        // Convert ContinuousHV to RealHV for temporal binding
        let state_vector = continuous_to_real(&encoded.unified_state);

        // Bind temporally
        let moment = self.temporal.bind(&state_vector);

        // Update trajectory vector (slow accumulation)
        let lr = 0.1;
        self.trajectory_vector = self.trajectory_vector
            .scale((1.0 - lr) as f32)
            .add(&moment.bound_experience.scale(lr as f32));

        // Update consciousness statistics
        self.consciousness_sum += metrics.overall_consciousness;
        self.consciousness_max = self.consciousness_max.max(metrics.overall_consciousness);
        self.consciousness_min = self.consciousness_min.min(metrics.overall_consciousness);

        // Create trajectory state
        let state = TrajectoryState {
            step: self.step,
            result: result.clone(),
            encoded,
            metrics,
            temporal_binding: moment.past_integration as f32,
            anticipation_match: moment.anticipation_match as f32,
            continuity: moment.continuity as f32,
        };

        // Store in history
        self.history.push_back(state.clone());
        if self.history.len() > self.config.window_size {
            self.history.pop_front();
        }

        state
    }

    /// Process a sequence of operating conditions
    pub fn process_trajectory(
        &mut self,
        physics: &CoupledPhysicsEngine,
        conditions_sequence: &[OperatingConditions],
    ) -> Vec<TrajectoryState> {
        conditions_sequence
            .iter()
            .map(|cond| {
                let result = physics.simulate(cond);
                self.process(&result)
            })
            .collect()
    }

    /// Get trajectory metrics summary
    pub fn trajectory_metrics(&self) -> TrajectoryMetrics {
        let integration = self.temporal.integration_summary();

        let mean_consciousness = if self.step > 0 {
            self.consciousness_sum / self.step as f32
        } else {
            0.0
        };

        // Compute variance
        let variance = if self.history.len() > 1 {
            let sum_sq: f32 = self.history.iter()
                .map(|s| (s.metrics.overall_consciousness - mean_consciousness).powi(2))
                .sum();
            sum_sq / self.history.len() as f32
        } else {
            0.0
        };

        // Trajectory consciousness: combines temporal coherence with mean state consciousness
        let trajectory_consciousness =
            0.5 * integration.coherence as f32 +
            0.3 * mean_consciousness +
            0.2 * (1.0 - variance.sqrt().min(1.0));  // Stability bonus

        TrajectoryMetrics {
            trajectory_consciousness,
            coherence: integration.coherence as f32,
            past_binding: integration.past_binding as f32,
            future_binding: integration.future_binding as f32,
            narrative_length: self.history.len(),
            mean_state_consciousness: mean_consciousness,
            consciousness_variance: variance,
            peak_consciousness: if self.consciousness_max.is_finite() { self.consciousness_max } else { 0.0 },
            valley_consciousness: if self.consciousness_min.is_finite() { self.consciousness_min } else { 0.0 },
        }
    }

    /// Get stream health (real-time metrics)
    pub fn stream_health(&self) -> StreamHealth {
        self.temporal.stream_health()
    }

    /// Get the unified trajectory vector
    pub fn trajectory_vector(&self) -> &RealHV {
        &self.trajectory_vector
    }

    /// Get the temporal narrative vector
    pub fn narrative(&self) -> &RealHV {
        self.temporal.narrative()
    }

    /// Compare this trajectory to another
    pub fn similarity_to(&self, other: &PhysicsTrajectoryEngine) -> f32 {
        self.trajectory_vector.similarity(&other.trajectory_vector)
    }

    /// Get recent history
    pub fn recent_history(&self, n: usize) -> Vec<&TrajectoryState> {
        self.history.iter().rev().take(n).collect()
    }

    /// Get consciousness trend (positive = improving)
    pub fn consciousness_trend(&self) -> f32 {
        if self.history.len() < 2 {
            return 0.0;
        }

        // Simple linear regression slope
        let n = self.history.len() as f32;
        let mut sum_x = 0.0;
        let mut sum_y = 0.0;
        let mut sum_xy = 0.0;
        let mut sum_xx = 0.0;

        for (i, state) in self.history.iter().enumerate() {
            let x = i as f32;
            let y = state.metrics.overall_consciousness;
            sum_x += x;
            sum_y += y;
            sum_xy += x * y;
            sum_xx += x * x;
        }

        let slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x);
        slope
    }
}

/// Convert ContinuousHV to RealHV (both are f32-based)
fn continuous_to_real(continuous: &crate::hdc::unified_hv::ContinuousHV) -> RealHV {
    // Both types use Vec<f32> internally, so direct conversion is possible
    RealHV::from_vec(continuous.values.clone())
}

/// Trajectory comparison result
#[derive(Debug, Clone)]
pub struct TrajectoryComparison {
    /// Similarity between trajectory vectors
    pub vector_similarity: f32,
    /// Difference in trajectory consciousness
    pub consciousness_delta: f32,
    /// Which trajectory is healthier
    pub healthier: &'static str,
    /// Metrics for trajectory A
    pub metrics_a: TrajectoryMetrics,
    /// Metrics for trajectory B
    pub metrics_b: TrajectoryMetrics,
}

/// Compare two trajectories
pub fn compare_trajectories(
    engine_a: &PhysicsTrajectoryEngine,
    engine_b: &PhysicsTrajectoryEngine,
) -> TrajectoryComparison {
    let metrics_a = engine_a.trajectory_metrics();
    let metrics_b = engine_b.trajectory_metrics();

    let vector_similarity = engine_a.trajectory_vector.similarity(&engine_b.trajectory_vector);
    let consciousness_delta = metrics_a.trajectory_consciousness - metrics_b.trajectory_consciousness;

    let healthier = if metrics_a.trajectory_consciousness > metrics_b.trajectory_consciousness {
        "A"
    } else {
        "B"
    };

    TrajectoryComparison {
        vector_similarity,
        consciousness_delta,
        healthier,
        metrics_a,
        metrics_b,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::physics::FusionReaction;

    fn setup() -> (GenesisSeed, CoupledPhysicsEngine, PhysicsTrajectoryEngine) {
        let genesis = GenesisSeed::from_phrase("trajectory test 2024");
        let physics = CoupledPhysicsEngine::from_genesis(&genesis);
        let trajectory = PhysicsTrajectoryEngine::from_genesis(&genesis);
        (genesis, physics, trajectory)
    }

    #[test]
    fn test_single_state_processing() {
        let (_, physics, mut trajectory) = setup();

        let conditions = OperatingConditions::consumer();
        let result = physics.simulate(&conditions);
        let state = trajectory.process(&result);

        assert_eq!(state.step, 1);
        assert!(state.metrics.overall_consciousness > 0.0);

        println!("\nSingle state processed:");
        println!("  Step: {}", state.step);
        println!("  Consciousness: {:.4}", state.metrics.overall_consciousness);
        println!("  Temporal binding: {:.4}", state.temporal_binding);
        println!("  Continuity: {:.4}", state.continuity);
    }

    #[test]
    fn test_trajectory_evolution() {
        let (_, physics, mut trajectory) = setup();

        println!("\n========================================");
        println!("TRAJECTORY EVOLUTION TEST");
        println!("========================================\n");

        // Evolve through power ramp-up
        let powers = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0];

        for power in powers {
            let conditions = OperatingConditions {
                power_kw: power,
                ..OperatingConditions::consumer()
            };
            let result = physics.simulate(&conditions);
            let state = trajectory.process(&result);

            println!("  {:>5.0} kW: C={:.4}, binding={:.4}, continuity={:.4}",
                     power,
                     state.metrics.overall_consciousness,
                     state.temporal_binding,
                     state.continuity);
        }

        let metrics = trajectory.trajectory_metrics();
        println!("\n{}", metrics.summary());
        println!("  Trend: {:.4}", trajectory.consciousness_trend());

        assert!(metrics.narrative_length == 10);
        assert!(metrics.coherence > 0.0);
    }

    #[test]
    fn test_trajectory_comparison() {
        let genesis = GenesisSeed::from_phrase("comparison test");
        let physics = CoupledPhysicsEngine::from_genesis(&genesis);

        // Trajectory A: Steady low power
        let mut traj_a = PhysicsTrajectoryEngine::from_genesis(&genesis);
        for _ in 0..10 {
            let result = physics.simulate(&OperatingConditions::consumer());
            traj_a.process(&result);
        }

        // Trajectory B: Ramping power
        let mut traj_b = PhysicsTrajectoryEngine::from_genesis(&genesis);
        for i in 0..10 {
            let conditions = OperatingConditions {
                power_kw: 5.0 + i as f64 * 5.0,
                ..OperatingConditions::consumer()
            };
            let result = physics.simulate(&conditions);
            traj_b.process(&result);
        }

        let comparison = compare_trajectories(&traj_a, &traj_b);

        println!("\n========================================");
        println!("TRAJECTORY COMPARISON");
        println!("========================================");
        println!("Steady (A) consciousness: {:.4}", comparison.metrics_a.trajectory_consciousness);
        println!("Ramping (B) consciousness: {:.4}", comparison.metrics_b.trajectory_consciousness);
        println!("Vector similarity: {:.4}", comparison.vector_similarity);
        println!("Healthier trajectory: {}", comparison.healthier);
        println!("========================================\n");

        // Trajectories should have different consciousness metrics
        // Note: Vector similarity may be high for short trajectories since
        // they accumulate slowly, but the consciousness metrics will differ
        assert!(
            (comparison.metrics_a.trajectory_consciousness - comparison.metrics_b.trajectory_consciousness).abs() > 0.001,
            "Trajectories should have different consciousness values"
        );
    }

    #[test]
    fn test_reaction_type_trajectories() {
        let genesis = GenesisSeed::from_phrase("reaction trajectories");
        let physics = CoupledPhysicsEngine::from_genesis(&genesis);

        println!("\n========================================");
        println!("REACTION TYPE TRAJECTORIES");
        println!("========================================\n");

        for (reaction, name) in [
            (FusionReaction::DD, "D-D"),
            (FusionReaction::DT, "D-T"),
            (FusionReaction::DHe3, "D-He3"),
        ] {
            let mut trajectory = PhysicsTrajectoryEngine::from_genesis(&genesis);

            // Run trajectory at constant 5 kW
            for _ in 0..15 {
                let conditions = OperatingConditions {
                    power_kw: 5.0,
                    reaction,
                    ..OperatingConditions::consumer()
                };
                let result = physics.simulate(&conditions);
                trajectory.process(&result);
            }

            let metrics = trajectory.trajectory_metrics();
            println!("{:6}: {}", name, metrics.summary());
        }
        println!("========================================\n");
    }

    #[test]
    fn test_stream_health_evolution() {
        let (_, physics, mut trajectory) = setup();

        println!("\n========================================");
        println!("STREAM HEALTH EVOLUTION");
        println!("========================================\n");

        // Need several states before stream is "flowing"
        for i in 0..20 {
            let conditions = OperatingConditions {
                power_kw: 5.0 + (i as f64 * 0.1).sin() * 2.0,  // Small oscillation
                ..OperatingConditions::consumer()
            };
            let result = physics.simulate(&conditions);
            trajectory.process(&result);

            if i % 5 == 4 {
                let health = trajectory.stream_health();
                println!("Step {:>2}: {}", i + 1, health);
            }
        }

        let final_health = trajectory.stream_health();
        println!("\nFinal: {}", final_health);

        // After 20 states, stream should be flowing
        assert!(final_health.is_flowing, "Stream should be flowing after 20 states");
    }
}
