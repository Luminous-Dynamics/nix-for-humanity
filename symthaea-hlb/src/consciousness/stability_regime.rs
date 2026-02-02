//! # Stability Regime: CfC Neurons for Primitives
//!
//! Each primitive gets temporal dynamics via an `HdcLtcUnifiedNeuron`.
//! Three **stability regimes** (Crystallized, Plastic, Fluid) map to
//! primitive tiers, each with different attractor strengths and time constants.
//!
//! ## Regime Properties
//!
//! | Regime       | Tiers   | tau   | Attractor | Learning |
//! |-------------|---------|-------|-----------|----------|
//! | Crystallized | 0-3     | 0.05  | 0.95      | Minimal  |
//! | Plastic      | 4-6     | 0.5   | 0.5       | Hebbian+STDP |
//! | Fluid        | 7-8     | 5.0   | 0.15      | Contrastive |

use std::collections::{HashMap, VecDeque};

use ndarray::Array1;
use serde::{Deserialize, Serialize};

use symthaea_core::hdc::hdc_ltc_unified::{HdcLtcUnifiedNeuron, UnifiedConfig};
use symthaea_core::hdc::unified_hv::ContinuousHV;
use symthaea_core::hdc::primitive_system::{Primitive, PrimitiveSystem, PrimitiveTier};
use symthaea_core::hdc::compat::HVCompat;
use symthaea_core::hdc::HV16;

use crate::dynamics::cfc_coherence::{CfCCoherenceBridge, CoherenceConfig};
use crate::consciousness::primitive_consciousness::{
    PrimitiveConsciousnessState, ActivePrimitive, ActivationReason,
    ConsciousnessPrimitiveProcessor,
};

// =============================================================================
// STABILITY REGIME TYPES
// =============================================================================

/// The three stability regimes for CfC primitives
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum StabilityRegimeType {
    /// Tiers 0-3: Fast snap-back, near-fixed attractors
    Crystallized,
    /// Tiers 4-6: Balanced drift and stability
    Plastic,
    /// Tiers 7-8: Slow dynamics, context-driven exploration
    Fluid,
}

impl StabilityRegimeType {
    /// Map a primitive tier to its stability regime
    pub fn from_tier(tier: PrimitiveTier) -> Self {
        match tier {
            PrimitiveTier::NSM
            | PrimitiveTier::Mathematical
            | PrimitiveTier::Physical
            | PrimitiveTier::Geometric => StabilityRegimeType::Crystallized,

            PrimitiveTier::Strategic
            | PrimitiveTier::MetaCognitive
            | PrimitiveTier::Temporal => StabilityRegimeType::Plastic,

            PrimitiveTier::Compositional
            | PrimitiveTier::Consciousness => StabilityRegimeType::Fluid,
        }
    }
}

/// Parameters for a single stability regime
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegimeParams {
    /// Base time constant for CfC neuron
    pub tau_base: f32,
    /// Attractor strength: 0.0 = fully context-driven, 1.0 = fixed attractor
    pub attractor_strength: f32,
    /// Multiplier on base learning rate
    pub learning_rate_scale: f32,
    /// Similarity threshold to become active
    pub activation_threshold: f32,
    /// Similarity threshold to deactivate (lower than activation for hysteresis)
    pub deactivation_threshold: f32,
}

/// Configuration for the entire stability regime system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StabilityRegimeConfig {
    pub crystallized: RegimeParams,
    pub plastic: RegimeParams,
    pub fluid: RegimeParams,
    pub coherence_config: CoherenceConfig,
    /// Maximum simultaneously active primitives
    pub max_active: usize,
    /// History length per primitive
    pub history_len: usize,
}

impl Default for StabilityRegimeConfig {
    fn default() -> Self {
        Self {
            crystallized: RegimeParams {
                tau_base: 0.05,
                attractor_strength: 0.95,
                learning_rate_scale: 0.001,
                activation_threshold: 0.35,
                deactivation_threshold: 0.25,
            },
            plastic: RegimeParams {
                tau_base: 0.5,
                attractor_strength: 0.5,
                learning_rate_scale: 1.0,
                activation_threshold: 0.30,
                deactivation_threshold: 0.20,
            },
            fluid: RegimeParams {
                tau_base: 5.0,
                attractor_strength: 0.15,
                learning_rate_scale: 2.0,
                activation_threshold: 0.25,
                deactivation_threshold: 0.15,
            },
            coherence_config: CoherenceConfig::default(),
            max_active: 32,
            history_len: 64,
        }
    }
}

impl StabilityRegimeConfig {
    /// Get params for a given regime type
    pub fn params(&self, regime: StabilityRegimeType) -> &RegimeParams {
        match regime {
            StabilityRegimeType::Crystallized => &self.crystallized,
            StabilityRegimeType::Plastic => &self.plastic,
            StabilityRegimeType::Fluid => &self.fluid,
        }
    }
}

// =============================================================================
// CfC PRIMITIVE
// =============================================================================

/// A single primitive wrapped with CfC temporal dynamics
pub struct CfCPrimitive {
    /// The underlying primitive
    pub primitive: Primitive,
    /// Which stability regime this primitive belongs to
    pub regime: StabilityRegimeType,
    /// CfC neuron whose state is a ContinuousHV (16,384-D)
    pub neuron: HdcLtcUnifiedNeuron,
    /// Immutable attractor = primitive.encoding converted to continuous
    pub attractor: ContinuousHV,
    /// Current activation level (similarity between state and recent input)
    pub activation: f64,
    /// Whether this primitive is currently active in consciousness
    pub is_active: bool,
    /// History of (timestamp, activation)
    pub history: VecDeque<(f64, f64)>,
    /// How many steps this primitive has been continuously active
    pub active_duration: usize,
}

impl CfCPrimitive {
    /// Create a new CfC primitive from a base primitive
    pub fn new(primitive: Primitive, config: &StabilityRegimeConfig, seed: u64) -> Self {
        let regime = StabilityRegimeType::from_tier(primitive.tier);
        let params = config.params(regime);

        let unified_config = UnifiedConfig {
            tau_base: params.tau_base,
            backbone_tau: params.tau_base * 2.0,
            dimension: 16_384,
            learning_rate: config.coherence_config.base_learning_rate * params.learning_rate_scale,
            ..UnifiedConfig::default()
        };

        let mut neuron = HdcLtcUnifiedNeuron::new(unified_config, seed);

        // Convert primitive encoding to continuous space as the attractor
        let attractor = primitive.encoding.to_continuous_hv();

        // Initialize neuron state to the attractor
        neuron.set_state(attractor.clone());

        Self {
            primitive,
            regime,
            neuron,
            attractor,
            activation: 0.0,
            is_active: false,
            history: VecDeque::with_capacity(config.history_len),
            active_duration: 0,
        }
    }

    /// Evolve this primitive one time step.
    ///
    /// Blends the external input with the primitive's attractor based on
    /// `attractor_strength`, then uses closed-form CfC evolution.
    /// Returns the new activation level.
    pub fn evolve(&mut self, dt: f32, input: &ContinuousHV, params: &RegimeParams) -> f64 {
        // Blend input with attractor: blended = a*attractor + (1-a)*input
        let a = params.attractor_strength;
        let blended = ContinuousHV::weighted_bundle(
            &[&self.attractor, input],
            &[a, 1.0 - a],
        );

        // Closed-form CfC evolution (O(1) temporal jump)
        self.neuron.evolve_closed_form(dt, &blended);

        // Activation = how similar the neuron's state is to the input
        self.activation = self.neuron.state().similarity(input) as f64;
        self.activation
    }

    /// Apply learning based on the regime type
    pub fn learn(&mut self, input: &ContinuousHV, params: &RegimeParams, lr: f32) {
        let scaled_lr = lr * params.learning_rate_scale;

        match self.regime {
            StabilityRegimeType::Crystallized => {
                // Minimal Hebbian: reinforce attractor alignment
                self.neuron.hebbian_update(input, Some(scaled_lr));
            }
            StabilityRegimeType::Plastic => {
                // Hebbian + STDP for temporal learning
                self.neuron.hebbian_update(input, Some(scaled_lr));
                let state = self.neuron.state().clone();
                self.neuron.stdp_update(input, &state, 0.01, scaled_lr);
            }
            StabilityRegimeType::Fluid => {
                // Contrastive: push toward input, away from attractor
                self.neuron.contrastive_update(input, &self.attractor, scaled_lr);
            }
        }
    }

    /// Update activation/deactivation status with hysteresis
    pub fn update_active_status(&mut self, params: &RegimeParams) {
        if self.is_active {
            // Already active: deactivate only if below lower threshold
            if self.activation < params.deactivation_threshold as f64 {
                self.is_active = false;
                self.active_duration = 0;
            } else {
                self.active_duration += 1;
            }
        } else {
            // Not active: activate only if above higher threshold
            if self.activation >= params.activation_threshold as f64 {
                self.is_active = true;
                self.active_duration = 1;
            }
        }
    }

    /// Record activation in history
    pub fn record_history(&mut self, timestamp: f64, max_len: usize) {
        self.history.push_back((timestamp, self.activation));
        while self.history.len() > max_len {
            self.history.pop_front();
        }
    }

    /// Get the effective tau of this neuron for the given input
    pub fn effective_tau(&self, input: &ContinuousHV) -> f32 {
        self.neuron.effective_tau(input)
    }

    /// Similarity between current neuron state and attractor
    pub fn attractor_similarity(&self) -> f32 {
        self.neuron.state().similarity(&self.attractor)
    }
}

// =============================================================================
// STABILITY REGIME PROCESSOR
// =============================================================================

/// Main processor that wraps ConsciousnessPrimitiveProcessor with CfC dynamics
pub struct StabilityRegimeProcessor {
    /// CfC-wrapped primitives keyed by name
    primitives: HashMap<String, CfCPrimitive>,
    /// Configuration
    config: StabilityRegimeConfig,
    /// Coherence bridge for bidirectional feedback
    coherence_bridge: CfCCoherenceBridge,
    /// Inner processor for backward compatibility
    inner: ConsciousnessPrimitiveProcessor,
    /// Current consciousness state
    current_state: Option<PrimitiveConsciousnessState>,
    /// State history
    history: Vec<PrimitiveConsciousnessState>,
}

impl StabilityRegimeProcessor {
    /// Create a new processor with default config
    pub fn new() -> Self {
        Self::with_config(StabilityRegimeConfig::default())
    }

    /// Create a new processor with custom config
    pub fn with_config(config: StabilityRegimeConfig) -> Self {
        let inner = ConsciousnessPrimitiveProcessor::new();
        let coherence_bridge = CfCCoherenceBridge::new(config.coherence_config.clone());

        // Build CfC primitives from the primitive system
        let primitive_system = PrimitiveSystem::new();
        let all_tiers = [
            PrimitiveTier::NSM,
            PrimitiveTier::Mathematical,
            PrimitiveTier::Physical,
            PrimitiveTier::Geometric,
            PrimitiveTier::Strategic,
            PrimitiveTier::MetaCognitive,
            PrimitiveTier::Temporal,
            PrimitiveTier::Compositional,
            PrimitiveTier::Consciousness,
        ];

        let mut primitives = HashMap::new();
        let mut seed = 42u64;
        for tier in &all_tiers {
            for prim in primitive_system.get_tier(*tier) {
                let cfc = CfCPrimitive::new(prim.clone(), &config, seed);
                primitives.insert(prim.name.clone(), cfc);
                seed = seed.wrapping_add(7919); // prime increment for diverse seeds
            }
        }

        Self {
            primitives,
            config,
            coherence_bridge,
            inner,
            current_state: None,
            history: Vec::new(),
        }
    }

    /// Process a semantic input through all CfC primitives
    ///
    /// 1. Convert input to ContinuousHV
    /// 2. Evolve all primitives (closed-form, O(1) per primitive)
    /// 3. Activate/deactivate with hysteresis
    /// 4. Build PrimitiveConsciousnessState
    /// 5. Apply learning on active primitives
    /// 6. Update coherence bridge
    pub fn process_input(
        &mut self,
        input: &HV16,
        dt: f32,
        timestamp: f64,
    ) -> PrimitiveConsciousnessState {
        // 1. Convert input to continuous space
        let continuous_input = input.to_continuous_hv();

        // 2 & 3. Evolve all primitives and update activation status
        for cfc in self.primitives.values_mut() {
            let params = self.config.params(cfc.regime).clone();
            cfc.evolve(dt, &continuous_input, &params);
            cfc.update_active_status(&params);
            cfc.record_history(timestamp, self.config.history_len);
        }

        // 4. Build consciousness state from active primitives
        let mut state = PrimitiveConsciousnessState::new(timestamp);

        // Collect active primitives sorted by activation (descending)
        let mut active_cfcs: Vec<&CfCPrimitive> = self.primitives.values()
            .filter(|c| c.is_active)
            .collect();
        active_cfcs.sort_by(|a, b| b.activation.partial_cmp(&a.activation)
            .unwrap_or(std::cmp::Ordering::Equal));

        // Limit to max_active
        for cfc in active_cfcs.iter().take(self.config.max_active) {
            state.activate(
                cfc.primitive.clone(),
                cfc.activation,
                ActivationReason::BottomUp {
                    input_similarity: cfc.activation,
                },
            );
        }

        // Compute unified encoding
        state.compute_unified_encoding();

        // 5. Apply learning on active primitives
        let lr = self.coherence_bridge.effective_learning_rate();
        for cfc in self.primitives.values_mut() {
            if cfc.is_active {
                let params = self.config.params(cfc.regime).clone();
                cfc.learn(&continuous_input, &params, lr);
            }
        }

        // 6. Compute phi and update coherence bridge
        state.phi = self.estimate_phi(&state);

        // Collect tau values from active neurons for coherence
        let tau_vecs: Vec<Array1<f32>> = self.primitives.values()
            .filter(|c| c.is_active)
            .map(|c| {
                let tau = c.effective_tau(&continuous_input);
                Array1::from_vec(vec![tau])
            })
            .collect();

        if !tau_vecs.is_empty() {
            let tau_refs: Vec<&Array1<f32>> = tau_vecs.iter().collect();
            self.coherence_bridge.update(&tau_refs);

            // Add coherence contribution to phi
            state.phi += self.coherence_bridge.phi_contribution() as f64;
        }

        // Store history
        self.history.push(state.clone());
        if self.history.len() > 100 {
            self.history.remove(0);
        }
        self.current_state = Some(state.clone());

        state
    }

    /// Estimate phi for the given consciousness state
    fn estimate_phi(&self, state: &PrimitiveConsciousnessState) -> f64 {
        use symthaea_core::phi_engine::{PhiEngine, PhiMethod};

        let active = state.all_active();
        if active.is_empty() {
            return 0.0;
        }

        // Use CfC neuron states (not raw encodings) for richer phi computation
        let mut nodes = Vec::new();
        for ap in active.iter().take(8) {
            if let Some(cfc) = self.primitives.get(&ap.primitive.name) {
                nodes.push(cfc.neuron.state().clone());
            }
        }

        if nodes.len() < 2 {
            return (active.len() as f64).sqrt() * 0.1;
        }

        let engine = PhiEngine::new(PhiMethod::Auto);
        let result = engine.compute(&nodes);
        result.phi.min(1.0)
    }

    /// Get the current consciousness state
    pub fn current(&self) -> Option<&PrimitiveConsciousnessState> {
        self.current_state.as_ref()
    }

    /// Get state history
    pub fn history(&self) -> &[PrimitiveConsciousnessState] {
        &self.history
    }

    /// Access the inner ConsciousnessPrimitiveProcessor for backward compat
    pub fn inner(&self) -> &ConsciousnessPrimitiveProcessor {
        &self.inner
    }

    /// Mutable access to inner processor
    pub fn inner_mut(&mut self) -> &mut ConsciousnessPrimitiveProcessor {
        &mut self.inner
    }

    /// Get a CfC primitive by name
    pub fn get_cfc_primitive(&self, name: &str) -> Option<&CfCPrimitive> {
        self.primitives.get(name)
    }

    /// Get all CfC primitives
    pub fn cfc_primitives(&self) -> &HashMap<String, CfCPrimitive> {
        &self.primitives
    }

    /// Get the coherence bridge
    pub fn coherence_bridge(&self) -> &CfCCoherenceBridge {
        &self.coherence_bridge
    }

    /// Get the config
    pub fn config(&self) -> &StabilityRegimeConfig {
        &self.config
    }

    /// Count of currently active primitives
    pub fn active_count(&self) -> usize {
        self.primitives.values().filter(|c| c.is_active).count()
    }

    /// Get regime distribution of active primitives
    pub fn active_by_regime(&self) -> HashMap<StabilityRegimeType, usize> {
        let mut counts = HashMap::new();
        for cfc in self.primitives.values().filter(|c| c.is_active) {
            *counts.entry(cfc.regime).or_insert(0) += 1;
        }
        counts
    }
}

impl Default for StabilityRegimeProcessor {
    fn default() -> Self {
        Self::new()
    }
}

// =============================================================================
// TESTS
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    fn make_test_primitive(name: &str, tier: PrimitiveTier) -> Primitive {
        Primitive {
            name: name.to_string(),
            tier,
            domain: "test".to_string(),
            encoding: HV16::random(name.len() as u64 * 31 + tier as u64),
            definition: name.to_string(),
            is_base: true,
            derivation: None,
        }
    }

    #[test]
    fn test_regime_assignment() {
        use PrimitiveTier::*;
        let tiers = [
            (NSM, StabilityRegimeType::Crystallized),
            (Mathematical, StabilityRegimeType::Crystallized),
            (Physical, StabilityRegimeType::Crystallized),
            (Geometric, StabilityRegimeType::Crystallized),
            (Strategic, StabilityRegimeType::Plastic),
            (MetaCognitive, StabilityRegimeType::Plastic),
            (Temporal, StabilityRegimeType::Plastic),
            (Compositional, StabilityRegimeType::Fluid),
            (Consciousness, StabilityRegimeType::Fluid),
        ];
        for (tier, expected) in &tiers {
            assert_eq!(
                StabilityRegimeType::from_tier(*tier),
                *expected,
                "Tier {:?} should map to {:?}",
                tier,
                expected,
            );
        }
    }

    #[test]
    fn test_crystallized_snap_back() {
        let config = StabilityRegimeConfig::default();
        let prim = make_test_primitive("FORCE", PrimitiveTier::Physical);
        let mut cfc = CfCPrimitive::new(prim, &config, 42);
        let params = config.params(StabilityRegimeType::Crystallized);

        // Feed random input for 100 steps
        let random_input = ContinuousHV::random(16_384, 999);
        for _ in 0..100 {
            cfc.evolve(0.1, &random_input, params);
        }

        // Crystallized should snap back to attractor
        let sim = cfc.attractor_similarity();
        assert!(
            sim > 0.8,
            "Crystallized primitive should stay near attractor, got similarity={}",
            sim,
        );
    }

    #[test]
    fn test_plastic_drift() {
        let config = StabilityRegimeConfig::default();
        let prim = make_test_primitive("PLAN", PrimitiveTier::Strategic);
        let mut cfc = CfCPrimitive::new(prim, &config, 42);
        let params = config.params(StabilityRegimeType::Plastic);

        let initial_sim = cfc.attractor_similarity();

        // Feed consistent but different context
        let context = ContinuousHV::random(16_384, 777);
        for _ in 0..200 {
            cfc.evolve(0.1, &context, params);
        }

        let final_sim = cfc.attractor_similarity();
        // Plastic should drift: similarity to attractor should decrease
        assert!(
            final_sim < initial_sim,
            "Plastic primitive should drift from attractor: initial={}, final={}",
            initial_sim,
            final_sim,
        );
    }

    #[test]
    fn test_fluid_exploration() {
        let config = StabilityRegimeConfig::default();
        let prim = make_test_primitive("COMPOSE", PrimitiveTier::Compositional);
        let mut cfc = CfCPrimitive::new(prim, &config, 42);
        let params = config.params(StabilityRegimeType::Fluid);

        // Strong orthogonal input
        let input = ContinuousHV::random(16_384, 12345);
        for _ in 0..500 {
            cfc.evolve(0.1, &input, params);
        }

        let sim_to_input = cfc.neuron.state().similarity(&input);
        let sim_to_attractor = cfc.attractor_similarity();

        // Fluid should be more similar to input than attractor after many steps
        assert!(
            sim_to_input > sim_to_attractor,
            "Fluid primitive should track input: sim_input={}, sim_attractor={}",
            sim_to_input,
            sim_to_attractor,
        );
    }

    #[test]
    fn test_activation_hysteresis() {
        let config = StabilityRegimeConfig::default();
        let prim = make_test_primitive("TEST", PrimitiveTier::Physical);
        let mut cfc = CfCPrimitive::new(prim, &config, 42);
        let params = config.params(StabilityRegimeType::Crystallized);

        // Force activation
        cfc.activation = 0.5;
        cfc.update_active_status(params);
        assert!(cfc.is_active, "Should activate above threshold");

        // Set activation between deactivation and activation thresholds
        // For crystallized: activation_threshold=0.35, deactivation_threshold=0.25
        cfc.activation = 0.30;
        cfc.update_active_status(params);
        assert!(
            cfc.is_active,
            "Should remain active due to hysteresis (0.30 > deactivation_threshold 0.25)",
        );

        // Drop below deactivation threshold
        cfc.activation = 0.20;
        cfc.update_active_status(params);
        assert!(!cfc.is_active, "Should deactivate below deactivation threshold");
    }

    #[test]
    fn test_process_input_basic() {
        let mut processor = StabilityRegimeProcessor::new();
        let input = HV16::random(42);

        let state = processor.process_input(&input, 0.1, 0.0);
        // Should produce a valid state with phi >= 0
        assert!(state.phi >= 0.0, "Phi should be non-negative");
    }

    #[test]
    fn test_coherence_feedback() {
        let mut processor = StabilityRegimeProcessor::new();
        let input = HV16::random(42);

        // Run multiple steps
        for i in 0..10 {
            processor.process_input(&input, 0.1, i as f64 * 0.1);
        }

        // Coherence bridge should have been updated
        let coherence = processor.coherence_bridge().smoothed_coherence();
        // With consistent input, coherence should be > 0
        assert!(
            coherence >= 0.0,
            "Coherence should be non-negative, got {}",
            coherence,
        );
    }

    #[test]
    fn test_backward_compat() {
        let processor = StabilityRegimeProcessor::new();
        // Inner processor should work independently
        let stats = processor.inner().primitive_stats();
        assert!(stats.total_primitives > 0, "Inner processor should have primitives");
    }
}
