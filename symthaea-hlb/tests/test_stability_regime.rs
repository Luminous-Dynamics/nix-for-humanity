//! Integration tests for the Stability Regime system

use symthaea::consciousness::stability_regime::{
    StabilityRegimeType, StabilityRegimeConfig, CfCPrimitive, StabilityRegimeProcessor,
};
use symthaea::consciousness::primitive_consciousness::ConsciousnessPrimitiveProcessor;
use symthaea_core::hdc::primitive_system::{Primitive, PrimitiveTier};
use symthaea_core::hdc::unified_hv::ContinuousHV;
use symthaea_core::hdc::HV16;

fn make_prim(name: &str, tier: PrimitiveTier) -> Primitive {
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
fn test_crystallized_more_stable_than_fluid() {
    let config = StabilityRegimeConfig::default();

    let prim_c = make_prim("FORCE", PrimitiveTier::Physical);
    let prim_f = make_prim("COMPOSE_X", PrimitiveTier::Compositional);
    let mut cfc_c = CfCPrimitive::new(prim_c, &config, 42);
    let mut cfc_f = CfCPrimitive::new(prim_f, &config, 42);
    let params_c = config.params(StabilityRegimeType::Crystallized);
    let params_f = config.params(StabilityRegimeType::Fluid);

    let random_input = ContinuousHV::random(16_384, 999);
    for _ in 0..100 {
        cfc_c.evolve(0.1, &random_input, params_c);
        cfc_f.evolve(0.1, &random_input, params_f);
    }

    let sim_c = cfc_c.attractor_similarity();
    let sim_f = cfc_f.attractor_similarity();
    assert!(
        sim_c >= sim_f,
        "Crystallized ({}) should be at least as stable as Fluid ({})",
        sim_c, sim_f,
    );
}

#[test]
fn test_plastic_drift() {
    let config = StabilityRegimeConfig::default();
    let prim = make_prim("PLAN", PrimitiveTier::Strategic);
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
fn test_fluid_drifts_more_than_crystallized() {
    let config = StabilityRegimeConfig::default();

    let prim_c = make_prim("MASS", PrimitiveTier::Physical);
    let prim_f = make_prim("AWARE", PrimitiveTier::Consciousness);
    let mut cfc_c = CfCPrimitive::new(prim_c, &config, 42);
    let mut cfc_f = CfCPrimitive::new(prim_f, &config, 42);
    let params_c = config.params(StabilityRegimeType::Crystallized);
    let params_f = config.params(StabilityRegimeType::Fluid);

    let initial_c = cfc_c.attractor_similarity();
    let initial_f = cfc_f.attractor_similarity();

    let input = ContinuousHV::random(16_384, 12345);
    for _ in 0..200 {
        cfc_c.evolve(0.1, &input, params_c);
        cfc_f.evolve(0.1, &input, params_f);
    }

    let drift_c = initial_c - cfc_c.attractor_similarity();
    let drift_f = initial_f - cfc_f.attractor_similarity();

    assert!(
        drift_f >= drift_c,
        "Fluid drift ({}) should >= crystallized drift ({})",
        drift_f, drift_c,
    );
}

#[test]
fn test_activation_hysteresis() {
    let config = StabilityRegimeConfig::default();
    let prim = make_prim("TEST", PrimitiveTier::Physical);
    let mut cfc = CfCPrimitive::new(prim, &config, 42);
    let params = config.params(StabilityRegimeType::Crystallized);

    cfc.activation = 0.5;
    cfc.update_active_status(params);
    assert!(cfc.is_active);

    cfc.activation = 0.30;
    cfc.update_active_status(params);
    assert!(cfc.is_active, "Should stay active in hysteresis band");

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

    let mut inner_only = ConsciousnessPrimitiveProcessor::new();
    let input = HV16::random(99);
    let state = inner_only.process_input(&input, 0.0);
    assert!(state.phi >= 0.0);
}
