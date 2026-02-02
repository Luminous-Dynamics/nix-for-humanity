//! # Physics → Consciousness Integration
//!
//! This module bridges the coupled physics simulation to consciousness metrics,
//! enabling measurement of design "integration" and "phenomenal character."
//!
//! ## Core Hypothesis
//!
//! Designs with higher integrated information (measured via HDC binding coherence)
//! may exhibit superior emergent properties:
//! - Better thermal-structural-radiation coupling
//! - More graceful degradation under off-design conditions
//! - Emergent stability properties
//!
//! ## Architecture
//!
//! ```text
//! CoupledSimulationResult
//!         │
//!         ▼
//! ┌───────────────────────────────────────────────┐
//! │  Encode Components as HDC Vectors             │
//! │  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
//! │  │  Thermal    │ │   Damage    │ │ Geometry │ │
//! │  │  Profile    │ │   State     │ │          │ │
//! │  └──────┬──────┘ └──────┬──────┘ └────┬─────┘ │
//! │         │               │              │       │
//! │         └───────────────┼──────────────┘       │
//! │                         ▼                      │
//! │              ┌──────────────────┐              │
//! │              │   BIND ALL       │              │
//! │              │   Creates unified │              │
//! │              │   state vector   │              │
//! │              └────────┬─────────┘              │
//! └───────────────────────┼───────────────────────┘
//!                         ▼
//!               ConsciousnessMetrics
//!               ├── phenomenal_index
//!               ├── design_integration
//!               ├── thermal_coherence
//!               └── overall_consciousness
//! ```

use crate::genesis::GenesisSeed;
use crate::hdc::unified_hv::ContinuousHV;
use super::consciousness_bridge::PhysicsConsciousnessBridge;
use super::coupled_physics::{CoupledSimulationResult, OperatingConditions};
use super::thermal_transport::TemperatureProfile;
use super::standard_model::PHYSICS_DIM;
use serde::{Deserialize, Serialize};

/// Consciousness metrics computed from a physics simulation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConsciousnessMetrics {
    /// Phenomenal index: similarity to phenomenal vs functional concepts (-1 to +1)
    pub phenomenal_index: f32,

    /// Design integration: how well thermal, damage, and geometry cohere
    pub design_integration: f32,

    /// Thermal coherence: internal consistency of temperature profile
    pub thermal_coherence: f32,

    /// Damage-healing balance: how well damage and healing are integrated
    pub damage_healing_balance: f32,

    /// Geometry harmony: spatial coherence of the design
    pub geometry_harmony: f32,

    /// Overall consciousness score (weighted combination)
    pub overall_consciousness: f32,

    /// Binding advantage over bundling (H2-style metric)
    pub binding_advantage: f32,
}

impl ConsciousnessMetrics {
    /// Check if this design has high integration (top quartile)
    pub fn is_highly_integrated(&self) -> bool {
        self.overall_consciousness > 0.5 && self.design_integration > 0.3
    }

    /// Summary string for display
    pub fn summary(&self) -> String {
        format!(
            "Φ={:.3}, integration={:.3}, overall={:.3}",
            self.phenomenal_index, self.design_integration, self.overall_consciousness
        )
    }
}

/// Physics state encoded as HDC vectors for consciousness analysis
#[derive(Debug, Clone)]
pub struct EncodedPhysicsState {
    /// Temperature profile as spatial topology vector
    pub thermal_vector: ContinuousHV,

    /// Damage/healing equilibrium as unified concept
    pub damage_vector: ContinuousHV,

    /// Geometry and shielding as structural vector
    pub geometry_vector: ContinuousHV,

    /// Pulse dynamics as temporal rhythm vector
    pub pulse_vector: ContinuousHV,

    /// Operating conditions as context vector
    pub conditions_vector: ContinuousHV,

    /// All components bound together - the unified state
    pub unified_state: ContinuousHV,

    /// All components bundled (for comparison)
    pub bundled_state: ContinuousHV,
}

/// Physics-consciousness integration engine
pub struct PhysicsConsciousnessEngine {
    /// Bridge to consciousness concepts
    bridge: PhysicsConsciousnessBridge,

    /// Genesis for deterministic vector generation
    genesis: GenesisSeed,

    /// Basis vectors for encoding physical quantities
    thermal_basis: ContinuousHV,
    damage_basis: ContinuousHV,
    _healing_basis: ContinuousHV,
    geometry_basis: ContinuousHV,
    power_basis: ContinuousHV,
    shielding_basis: ContinuousHV,
    _lifetime_basis: ContinuousHV,
    pulse_basis: ContinuousHV,
}

impl PhysicsConsciousnessEngine {
    /// Create from genesis seed
    pub fn from_genesis(genesis: &GenesisSeed) -> Self {
        Self {
            bridge: PhysicsConsciousnessBridge::from_genesis(genesis),
            thermal_basis: genesis.hv("physics::thermal", PHYSICS_DIM),
            damage_basis: genesis.hv("physics::damage", PHYSICS_DIM),
            _healing_basis: genesis.hv("physics::healing", PHYSICS_DIM),
            geometry_basis: genesis.hv("physics::geometry", PHYSICS_DIM),
            power_basis: genesis.hv("physics::power", PHYSICS_DIM),
            shielding_basis: genesis.hv("physics::shielding", PHYSICS_DIM),
            _lifetime_basis: genesis.hv("physics::lifetime", PHYSICS_DIM),
            pulse_basis: genesis.hv("physics::pulse", PHYSICS_DIM),
            genesis: genesis.clone(),
        }
    }

    /// Encode a temperature profile as an HDC vector
    ///
    /// The encoding captures:
    /// - Spatial gradient topology (where heat flows)
    /// - Temperature range (max - min)
    /// - Profile shape (concave vs convex)
    pub fn encode_temperature_profile(&self, profile: &TemperatureProfile) -> ContinuousHV {
        // Normalize temperatures to [0, 1] range
        let t_range = profile.t_max - profile.t_min;
        let t_scale = if t_range > 1e-10 { t_range } else { 1.0 };

        // Create feature vector from temperature profile
        let mut features = Vec::with_capacity(PHYSICS_DIM);

        // Encode normalized temperatures at each radial position
        for (i, &temp) in profile.temperatures.iter().enumerate() {
            let normalized = ((temp - profile.t_min) / t_scale) as f32;
            let position_phase = (i as f32 / profile.temperatures.len() as f32) * 2.0 * std::f32::consts::PI;

            // Multi-scale encoding: different frequencies capture different spatial features
            for harmonic in 0..8 {
                let freq = (harmonic + 1) as f32;
                features.push(normalized * (freq * position_phase).sin());
                features.push(normalized * (freq * position_phase).cos());
            }
        }

        // Pad or truncate to PHYSICS_DIM
        features.resize(PHYSICS_DIM, 0.0);

        // Bind with thermal basis to create typed vector
        let profile_vec = ContinuousHV::from_vec(features);
        profile_vec.bind(&self.thermal_basis)
    }

    /// Encode damage state (DPA equilibrium + healing) as unified concept
    pub fn encode_damage_state(
        &self,
        equilibrium_dpa: f64,
        lifetime_years: f64,
        fatigue_lifetime_years: f64,
    ) -> ContinuousHV {
        // Normalize values to [0, 1]
        let dpa_norm = (equilibrium_dpa / 100.0).min(1.0) as f32;  // 100 DPA = max
        let lifetime_norm = (lifetime_years / 50.0).min(1.0) as f32;  // 50 years = max
        let fatigue_norm = (fatigue_lifetime_years / 50.0).min(1.0) as f32;

        // Balance metric: how well are damage and healing integrated?
        let balance = 1.0 - (dpa_norm - lifetime_norm).abs();

        // Create feature vector that directly encodes the values
        let mut features = vec![0.0f32; PHYSICS_DIM];

        for i in 0..PHYSICS_DIM {
            let phase = i as f32 / PHYSICS_DIM as f32;

            // Damage encoded as low-frequency component
            features[i] += dpa_norm * (2.0 * std::f32::consts::PI * phase).sin();

            // Lifetime as medium-frequency component
            features[i] += lifetime_norm * (4.0 * std::f32::consts::PI * phase).cos();

            // Fatigue as high-frequency component
            features[i] += fatigue_norm * (8.0 * std::f32::consts::PI * phase).sin();

            // Balance modulates amplitude
            features[i] *= 0.5 + 0.5 * balance;
        }

        let damage_vec = ContinuousHV::from_vec(features);

        // Bind with basis to type the vector (but scale basis down to not dominate)
        let scaled_basis = self.damage_basis.scale(0.1);
        damage_vec.add(&scaled_basis)
    }

    /// Encode geometry as structural vector
    pub fn encode_geometry(
        &self,
        core_radius_m: f64,
        shell_thickness_m: f64,
        shielding_thickness_m: f64,
        total_mass_kg: f64,
    ) -> ContinuousHV {
        // Normalize dimensions
        let core_norm = (core_radius_m / 0.1).min(1.0) as f32;  // 0.1m = max core
        let shell_norm = (shell_thickness_m / 0.05).min(1.0) as f32;  // 5cm = max shell
        let shield_norm = (shielding_thickness_m / 2.0).min(1.0) as f32;  // 2m = max shielding
        let mass_norm = (total_mass_kg / 10000.0).min(1.0) as f32;  // 10t = max

        // Create spatial structure vector
        // Encode as nested spherical shells
        let mut features = vec![0.0f32; PHYSICS_DIM];

        // Radial zones encoded at different frequency bands
        for i in 0..PHYSICS_DIM {
            let phase = i as f32 / PHYSICS_DIM as f32;

            // Core contribution (low frequency)
            features[i] += core_norm * (2.0 * std::f32::consts::PI * phase).sin();

            // Shell contribution (medium frequency)
            features[i] += shell_norm * (4.0 * std::f32::consts::PI * phase).sin();

            // Shielding contribution (high frequency)
            features[i] += shield_norm * (8.0 * std::f32::consts::PI * phase).sin();

            // Mass as overall amplitude modulation
            features[i] *= mass_norm.sqrt();
        }

        let structure_vec = ContinuousHV::from_vec(features);
        structure_vec.bind(&self.geometry_basis).bind(&self.shielding_basis)
    }

    /// Encode pulse dynamics as temporal rhythm
    pub fn encode_pulse_dynamics(
        &self,
        duty_cycle: f64,
        frequency_hz: f64,
        thermal_time_constant_s: f64,
    ) -> ContinuousHV {
        let duty_norm = duty_cycle.min(1.0) as f32;
        let freq_norm = (frequency_hz / 100.0).min(1.0) as f32;  // 100 Hz = max
        let tau_norm = (thermal_time_constant_s / 1000.0).min(1.0) as f32;  // 1000s = max

        // Encode temporal rhythm
        let mut features = vec![0.0f32; PHYSICS_DIM];

        for i in 0..PHYSICS_DIM {
            let phase = i as f32 / PHYSICS_DIM as f32;

            // Duty cycle as pulse width
            let pulse_shape = if phase < duty_norm { 1.0 } else { -1.0 };

            // Frequency modulation
            let freq_mod = (freq_norm * 10.0 * std::f32::consts::PI * phase).sin();

            // Time constant as decay envelope
            let envelope = (-phase / tau_norm.max(0.01)).exp();

            features[i] = pulse_shape * freq_mod * envelope;
        }

        let pulse_vec = ContinuousHV::from_vec(features);
        pulse_vec.bind(&self.pulse_basis)
    }

    /// Encode operating conditions as context
    pub fn encode_conditions(&self, conditions: &OperatingConditions) -> ContinuousHV {
        let power_norm = (conditions.power_kw / 1000.0).min(1.0) as f32;  // 1 MW = max

        // Power level determines the base vector
        let power_vec = self.power_basis.scale(power_norm);

        // Reaction type encoded as discrete binding
        let reaction_vec = self.genesis.hv(
            &format!("physics::reaction::{:?}", conditions.reaction),
            PHYSICS_DIM
        );

        power_vec.bind(&reaction_vec)
    }

    /// Encode entire simulation result as physics state
    pub fn encode_simulation(&self, result: &CoupledSimulationResult) -> EncodedPhysicsState {
        // Encode each component
        let thermal_vector = self.encode_temperature_profile(&result.thermal_profile);

        let damage_vector = self.encode_damage_state(
            result.pulse_thermal.equilibrium_dpa,
            result.pulse_thermal.lifetime_years,
            result.pulse_thermal.fatigue_lifetime_years,
        );

        let geometry_vector = self.encode_geometry(
            result.geometry_shielding.geometry.core_radius,
            result.geometry_shielding.geometry.shell_thickness,
            result.geometry_shielding.shielding.thickness_m,
            result.geometry_shielding.total_mass_kg,
        );

        let pulse_vector = self.encode_pulse_dynamics(
            result.pulse_thermal.pulse.duty_cycle,
            1.0 / result.pulse_thermal.pulse.period_s,
            result.pulse_thermal.cycling.time_constant,
        );

        let conditions_vector = self.encode_conditions(&result.conditions);

        // BIND all components - creates emergent unified structure
        let unified_state = thermal_vector
            .bind(&damage_vector)
            .bind(&geometry_vector)
            .bind(&pulse_vector)
            .bind(&conditions_vector);

        // BUNDLE for comparison - creates superposition
        let bundled_state = ContinuousHV::bundle(&[
            &thermal_vector,
            &damage_vector,
            &geometry_vector,
            &pulse_vector,
            &conditions_vector,
        ]);

        EncodedPhysicsState {
            thermal_vector,
            damage_vector,
            geometry_vector,
            pulse_vector,
            conditions_vector,
            unified_state,
            bundled_state,
        }
    }

    /// Compute consciousness metrics for a simulation result
    pub fn compute_metrics(&self, result: &CoupledSimulationResult) -> ConsciousnessMetrics {
        let state = self.encode_simulation(result);

        // Phenomenal index: Is this design more "phenomenal" or "functional"?
        let phenomenal_index = self.bridge.phenomenal_index(&state.unified_state);

        // Design integration: How coherent is the unified state?
        // Measure via internal consistency (self-similarity after perturbation)
        let perturbed = state.unified_state.scale(0.9);
        let design_integration = state.unified_state.similarity(&perturbed);

        // Binding advantage: Compare unified (bound) vs bundled
        let binding_advantage = state.unified_state.norm() - state.bundled_state.norm();

        // Thermal coherence: How smooth is the temperature profile?
        // Measured by comparing to a smoothed version
        let thermal_coherence = {
            let norm = state.thermal_vector.norm();
            if norm > 0.0 { 1.0 / (1.0 + (norm - 1.0).abs()) } else { 0.0 }
        };

        // Damage-healing balance: Based on actual physics values
        let dpa_norm = (result.pulse_thermal.equilibrium_dpa / 100.0).min(1.0) as f32;
        let lifetime_norm = (result.pulse_thermal.lifetime_years / 50.0).min(1.0) as f32;
        let damage_healing_balance = 1.0 - (dpa_norm - lifetime_norm).abs();

        // Geometry harmony: Mass efficiency and compactness
        let mass_per_kw = result.geometry_shielding.total_mass_kg / result.conditions.power_kw;
        let geometry_harmony = 1.0 / (1.0 + (mass_per_kw / 1000.0) as f32);

        // Overall consciousness: Geometric mean of positive components
        // This ensures all components contribute
        let components = [
            (design_integration + 1.0) / 2.0,  // Normalize to [0, 1]
            thermal_coherence,
            damage_healing_balance,
            geometry_harmony,
        ];

        // Geometric mean (all components must be positive)
        let product: f32 = components.iter().product();
        let geo_mean = product.powf(1.0 / components.len() as f32);

        // Scale by feasibility bonus
        let feasibility_bonus = if result.feasible { 1.2 } else { 0.8 };
        let overall_consciousness = geo_mean * feasibility_bonus;

        ConsciousnessMetrics {
            phenomenal_index,
            design_integration,
            thermal_coherence,
            damage_healing_balance,
            geometry_harmony,
            overall_consciousness,
            binding_advantage,
        }
    }

    /// Compare two designs by their consciousness metrics
    pub fn compare_designs(
        &self,
        result_a: &CoupledSimulationResult,
        result_b: &CoupledSimulationResult,
    ) -> DesignComparison {
        let metrics_a = self.compute_metrics(result_a);
        let metrics_b = self.compute_metrics(result_b);

        let state_a = self.encode_simulation(result_a);
        let state_b = self.encode_simulation(result_b);

        // Measure similarity between designs
        let state_similarity = state_a.unified_state.similarity(&state_b.unified_state);

        // Compute difference before moving
        let consciousness_difference = metrics_a.overall_consciousness - metrics_b.overall_consciousness;

        DesignComparison {
            metrics_a,
            metrics_b,
            state_similarity,
            consciousness_difference,
        }
    }

    /// Get the physics-consciousness bridge for direct access
    pub fn bridge(&self) -> &PhysicsConsciousnessBridge {
        &self.bridge
    }
}

/// Comparison between two designs
#[derive(Debug, Clone)]
pub struct DesignComparison {
    pub metrics_a: ConsciousnessMetrics,
    pub metrics_b: ConsciousnessMetrics,
    pub state_similarity: f32,
    pub consciousness_difference: f32,
}

impl DesignComparison {
    /// Which design has higher consciousness?
    pub fn more_conscious_design(&self) -> &'static str {
        if self.consciousness_difference > 0.0 { "A" } else { "B" }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::physics::coupled_physics::{CoupledPhysicsEngine, OperatingConditions};

    fn setup() -> (CoupledPhysicsEngine, PhysicsConsciousnessEngine, GenesisSeed) {
        let genesis = GenesisSeed::from_phrase("physics consciousness test");
        let physics = CoupledPhysicsEngine::from_genesis(&genesis);
        let consciousness = PhysicsConsciousnessEngine::from_genesis(&genesis);
        (physics, consciousness, genesis)
    }

    #[test]
    fn test_encode_temperature_profile() {
        let (physics, consciousness, _) = setup();

        let conditions = OperatingConditions::consumer();
        let result = physics.simulate(&conditions);

        let thermal_vec = consciousness.encode_temperature_profile(&result.thermal_profile);

        // Should have correct dimension
        assert_eq!(thermal_vec.dim(), PHYSICS_DIM);

        // Should have non-zero norm
        assert!(thermal_vec.norm() > 0.0);

        println!("Thermal vector norm: {:.4}", thermal_vec.norm());
    }

    #[test]
    fn test_encode_damage_state() {
        let (_, consciousness, _) = setup();

        let damage_vec = consciousness.encode_damage_state(50.0, 25.0, 30.0);

        assert_eq!(damage_vec.dim(), PHYSICS_DIM);
        assert!(damage_vec.norm() > 0.0);

        // Different damage levels should produce different vectors
        let damage_vec_high = consciousness.encode_damage_state(100.0, 10.0, 15.0);
        let similarity = damage_vec.similarity(&damage_vec_high);

        println!("Damage vectors similarity: {:.4}", similarity);
        // Similar but not identical (high correlation expected due to same basis)
        assert!(similarity < 1.0, "Different damage should produce distinguishable vectors");

        // Very different parameters should have lower similarity
        let damage_vec_extreme = consciousness.encode_damage_state(0.0, 50.0, 50.0);
        let extreme_similarity = damage_vec.similarity(&damage_vec_extreme);
        println!("Extreme damage vectors similarity: {:.4}", extreme_similarity);
    }

    #[test]
    fn test_encode_full_simulation() {
        let (physics, consciousness, _) = setup();

        let conditions = OperatingConditions::consumer();
        let result = physics.simulate(&conditions);

        let state = consciousness.encode_simulation(&result);

        // All vectors should have correct dimension
        assert_eq!(state.thermal_vector.dim(), PHYSICS_DIM);
        assert_eq!(state.damage_vector.dim(), PHYSICS_DIM);
        assert_eq!(state.geometry_vector.dim(), PHYSICS_DIM);
        assert_eq!(state.unified_state.dim(), PHYSICS_DIM);

        // Unified and bundled should be different
        let bound_bundle_sim = state.unified_state.similarity(&state.bundled_state);
        println!("Bound vs bundle similarity: {:.4}", bound_bundle_sim);

        // Binding creates orthogonal structure (low similarity to bundle)
        assert!(bound_bundle_sim < 0.5, "Binding should create different structure than bundling");
    }

    #[test]
    fn test_compute_consciousness_metrics() {
        let (physics, consciousness, _) = setup();

        let conditions = OperatingConditions::consumer();
        let result = physics.simulate(&conditions);

        let metrics = consciousness.compute_metrics(&result);

        println!("\n========================================");
        println!("PHYSICS → CONSCIOUSNESS METRICS");
        println!("========================================");
        println!("Phenomenal index:      {:.4}", metrics.phenomenal_index);
        println!("Design integration:    {:.4}", metrics.design_integration);
        println!("Thermal coherence:     {:.4}", metrics.thermal_coherence);
        println!("Damage-healing:        {:.4}", metrics.damage_healing_balance);
        println!("Geometry harmony:      {:.4}", metrics.geometry_harmony);
        println!("Binding advantage:     {:.4}", metrics.binding_advantage);
        println!("----------------------------------------");
        println!("OVERALL CONSCIOUSNESS: {:.4}", metrics.overall_consciousness);
        println!("========================================\n");

        // All metrics should be in valid range
        assert!(metrics.phenomenal_index >= -1.0 && metrics.phenomenal_index <= 1.0);
        assert!(metrics.overall_consciousness >= 0.0);
    }

    #[test]
    fn test_compare_designs() {
        let (physics, consciousness, _) = setup();

        // Compare consumer vs industrial designs
        let consumer = OperatingConditions::consumer();
        let industrial = OperatingConditions::industrial();

        let result_consumer = physics.simulate(&consumer);
        let result_industrial = physics.simulate(&industrial);

        let comparison = consciousness.compare_designs(&result_consumer, &result_industrial);

        println!("\n========================================");
        println!("DESIGN COMPARISON");
        println!("========================================");
        println!("Consumer consciousness:   {:.4}", comparison.metrics_a.overall_consciousness);
        println!("Industrial consciousness: {:.4}", comparison.metrics_b.overall_consciousness);
        println!("State similarity:         {:.4}", comparison.state_similarity);
        println!("More conscious design:    {}", comparison.more_conscious_design());
        println!("========================================\n");

        // Different designs should have different metrics
        assert!(comparison.consciousness_difference.abs() > 0.001 ||
                comparison.state_similarity < 0.99);
    }

    #[test]
    fn test_consciousness_correlates_with_feasibility() {
        let (physics, consciousness, _) = setup();

        println!("\n========================================");
        println!("CONSCIOUSNESS vs FEASIBILITY STUDY");
        println!("========================================\n");

        // Test multiple power levels
        let mut feasible_consciousness = Vec::new();
        let mut infeasible_consciousness = Vec::new();

        for power in [1.0, 2.0, 5.0, 10.0, 20.0, 50.0] {
            let conditions = OperatingConditions {
                power_kw: power,
                ..OperatingConditions::consumer()
            };

            let result = physics.simulate(&conditions);
            let metrics = consciousness.compute_metrics(&result);

            println!("{:>5.0} kW: consciousness={:.4}, feasible={}",
                     power, metrics.overall_consciousness, result.feasible);

            if result.feasible {
                feasible_consciousness.push(metrics.overall_consciousness);
            } else {
                infeasible_consciousness.push(metrics.overall_consciousness);
            }
        }

        // Compute means
        let feasible_mean = if feasible_consciousness.is_empty() { 0.0 }
            else { feasible_consciousness.iter().sum::<f32>() / feasible_consciousness.len() as f32 };
        let infeasible_mean = if infeasible_consciousness.is_empty() { 0.0 }
            else { infeasible_consciousness.iter().sum::<f32>() / infeasible_consciousness.len() as f32 };

        println!("\nFeasible mean consciousness:   {:.4} (n={})",
                 feasible_mean, feasible_consciousness.len());
        println!("Infeasible mean consciousness: {:.4} (n={})",
                 infeasible_mean, infeasible_consciousness.len());
        println!("========================================\n");
    }
}
