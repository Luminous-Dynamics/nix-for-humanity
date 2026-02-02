//! Integration tests for the Stability Regime system

use symthaea::consciousness::stability_regime::{
    StabilityRegimeType, StabilityRegimeConfig, CfCPrimitive, StabilityRegimeProcessor,
};
use symthaea::consciousness::primitive_consciousness::ConsciousnessPrimitiveProcessor;
use symthaea_core::hdc::primitive_system::PrimitiveTier;
use symthaea_core::hdc::unified_hv::ContinuousHV;
use symthaea_core::hdc::HV16;

#[test]
fn test_regime_assignment_all_tiers() {
    let mappings = [
        (PrimitiveTier::NSM, StabilityRegimeType::Crystallized),
        (PrimitiveTier::Mathematical, StabilityRegimeType::Crystallized),
        (PrimitiveTier::Physical, StabilityRegimeType::Crystallized),
        (PrimitiveTier::Geometric, StabilityRegimeType::Crystallized),
        (PrimitiveTier::Strategic, StabilityRegimeType::Plastic),
        (PrimitiveTier::MetaCognitive, StabilityRegimeType::Plastic),
        (PrimitiveTier::Temporal, StabilityRegimeType::Plastic),
        (PrimitiveTier::Compositional, StabilityRegimeType::Fluid),
        (PrimitiveTier::Consciousness, StabilityRegimeType::Fluid),
    ];

    for (tier, expected) in &mappings {
        assert_eq!(
            StabilityRegimeType::from_tier(*tier),
            *expected,
            "Tier {:?} should be {:?}",
            tier,
            expected,
        );
    }
}

#[test]
fn test_crystallized_snap_back() {
    let config = StabilityRegimeConfig::default();
    let prim = symthaea_core::hdc::primitive_system::Primitive {
        name: "FORCE".to_string(),
        tier: PrimitiveTier::Physical,
        domain: "physical".to_string(),
        encoding: HV16::random(42),
        definition: "Force".to_string(),
        is_base: true,
        derivation: None,
    };
    let mut cfc = CfCPrimitive::new(prim, &config, 42);
    let params = config.params(StabilityRegimeType::Crystallized);

    let random_input = ContinuousHV::random(16_384, 999);
    for _ in 0..100 {
        cfc.evolve(0.1, &random_input, params);
    }

    assert!(
        cfc.attractor_similarity() > 0.8,
        "Crystallized should snap back, got {}",
        cfc.attractor_similarity(),
    );
}

#[test]
fn test_plastic_drift() {
    let config = StabilityRegimeConfig::default();
    let prim = symthaea_core::hdc::primitive_system::Primitive {
        name: "PLAN".to_string(),
        tier: PrimitiveTier::Strategic,
        domain: "strategic".to_string(),
        encoding: HV16::random(42),
        definition: "Plan".to_string(),
        is_base: true,
        derivation: None,
    };
    let mut cfc = CfCPrimitive::new(prim, &config, 42);
    let params = config.params(StabilityRegimeType::Plastic);

    let initial_sim = cfc.attractor_similarity();
    let context = ContinuousHV::random(16_384, 777);
    for _ in 0..200 {
        cfc.evolve(0.1, &context, params);
    }

    assert!(
        cfc.attractor_similarity() < initial_sim,
        "Plastic should drift: {} -> {}",
        initial_sim,
        cfc.attractor_similarity(),
    );
}

#[test]
fn test_fluid_exploration() {
    let config = StabilityRegimeConfig::default();
    let prim = symthaea_core::hdc::primitive_system::Primitive {
        name: "COMPOSE".to_string(),
        tier: PrimitiveTier::Compositional,
        domain: "compositional".to_string(),
        encoding: HV16::random(42),
        definition: "Compose".to_string(),
        is_base: true,
        derivation: None,
    };
    let mut cfc = CfCPrimitive::new(prim, &config, 42);
    let params = config.params(StabilityRegimeType::Fluid);

    let input = ContinuousHV::random(16_384, 12345);
    for _ in 0..500 {
        cfc.evolve(0.1, &input, params);
    }

    let sim_input = cfc.neuron.state().similarity(&input);
    let sim_attractor = cfc.attractor_similarity();
    assert!(
        sim_input > sim_attractor,
        "Fluid should track input: input={}, attractor={}",
        sim_input,
        sim_attractor,
    );
}

#[test]
fn test_activation_hysteresis() {
    let config = StabilityRegimeConfig::default();
    let prim = symthaea_core::hdc::primitive_system::Primitive {
        name: "TEST".to_string(),
        tier: PrimitiveTier::Physical,
        domain: "test".to_string(),
        encoding: HV16::random(42),
        definition: "Test".to_string(),
        is_base: true,
        derivation: None,
    };
    let mut cfc = CfCPrimitive::new(prim, &config, 42);
    let params = config.params(StabilityRegimeType::Crystallized);

    // Activate
    cfc.activation = 0.5;
    cfc.update_active_status(params);
    assert!(cfc.is_active);

    // In hysteresis band
    cfc.activation = 0.30;
    cfc.update_active_status(params);
    assert!(cfc.is_active, "Should stay active in hysteresis band");

    // Below deactivation
    cfc.activation = 0.20;
    cfc.update_active_status(params);
    assert!(!cfc.is_active, "Should deactivate below threshold");
}

#[test]
fn test_process_input_basic() {
    let mut processor = StabilityRegimeProcessor::new();
    let input = HV16::random(42);

    let state = processor.process_input(&input, 0.1, 0.0);
    assert!(state.phi >= 0.0);
}

#[test]
fn test_coherence_feedback() {
    let mut processor = StabilityRegimeProcessor::new();
    let input = HV16::random(42);

    for i in 0..10 {
        processor.process_input(&input, 0.1, i as f64 * 0.1);
    }

    let lr = processor.coherence_bridge().effective_learning_rate();
    assert!(lr > 0.0, "Learning rate should be positive, got {}", lr);
}

#[test]
fn test_backward_compat() {
    let processor = StabilityRegimeProcessor::new();
    let stats = processor.inner().primitive_stats();
    assert!(stats.total_primitives > 0);

    // Inner processor should work independently
    let mut inner_only = ConsciousnessPrimitiveProcessor::new();
    let input = HV16::random(99);
    let state = inner_only.process_input(&input, 0.0);
    assert!(state.phi >= 0.0);
}
