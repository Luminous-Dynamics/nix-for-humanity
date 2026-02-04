//! End-to-end determinism test for the cognitive loop's genesis seeding.
//!
//! Verifies that two HdcLtcBridge instances initialized with the same genesis
//! phrase produce identical outputs when given identical inputs, and that a
//! different phrase yields divergent state.
//!
//! Also verifies that `CognitiveLoopService` with `genesis_phrase` set produces
//! identical cycle outputs and stats over 100 cycles.

use ndarray::Array1;
use symthaea::cognitive_loop::{CognitiveLoopConfig, CognitiveLoopService, TemporalBackend};
use symthaea::hdc_ltc_bridge::{HdcLtcBridge, HdcLtcBridgeConfig};
use symthaea_core::genesis::GenesisSeed;

const STEPS: usize = 50;
const DT: f32 = 0.02;

fn make_bridge(phrase: &str) -> HdcLtcBridge {
    let genesis = GenesisSeed::from_phrase(phrase);
    let config = HdcLtcBridgeConfig::default();
    HdcLtcBridge::from_genesis(config, &genesis)
}

fn deterministic_input(step: usize, dim: usize) -> Array1<f32> {
    // Pure function of step index — no randomness
    Array1::from_vec(
        (0..dim)
            .map(|i| ((step * 7 + i * 13) as f32 * 0.01).sin())
            .collect(),
    )
}

#[test]
fn same_genesis_produces_identical_outputs() {
    let phrase = "determinism-test-alpha";
    let mut a = make_bridge(phrase);
    let mut b = make_bridge(phrase);

    let dim = HdcLtcBridgeConfig::default().input_dim;

    for step in 0..STEPS {
        let input = deterministic_input(step, dim);
        let out_a = a.forward(&input, DT);
        let out_b = b.forward(&input, DT);

        assert_eq!(
            out_a, out_b,
            "Divergence at step {step}: outputs differ for same genesis phrase"
        );
    }

    // Final internal state must also match
    let state_a = a.read_state().unwrap();
    let state_b = b.read_state().unwrap();
    assert_eq!(state_a, state_b, "Final cached states differ");
}

#[test]
fn different_genesis_produces_different_state() {
    let mut same1 = make_bridge("phrase-one");
    let mut diff = make_bridge("phrase-two");

    let dim = HdcLtcBridgeConfig::default().input_dim;

    for step in 0..STEPS {
        let input = deterministic_input(step, dim);
        same1.forward(&input, DT);
        diff.forward(&input, DT);
    }

    let state_same = same1.read_state().unwrap();
    let state_diff = diff.read_state().unwrap();

    assert_ne!(
        state_same, state_diff,
        "Different genesis phrases must yield different final states"
    );
}

#[test]
fn genesis_determinism_across_fresh_instantiations() {
    // Build, run, collect output, drop — then do it again.
    // The two collected output sequences must be identical.
    let phrase = "reproducibility-proof";
    let dim = HdcLtcBridgeConfig::default().input_dim;

    let collect = || -> Vec<Vec<f32>> {
        let mut bridge = make_bridge(phrase);
        (0..STEPS)
            .map(|s| {
                let input = deterministic_input(s, dim);
                bridge.forward(&input, DT).to_vec()
            })
            .collect()
    };

    let run1 = collect();
    let run2 = collect();

    assert_eq!(run1, run2, "Two independent runs with same genesis must match exactly");
}

// =============================================================================
// COGNITIVE LOOP GENESIS DETERMINISM TESTS
// =============================================================================
// These tests verify that the full CognitiveLoopService produces identical
// behavior when initialized with the same genesis phrase.

const LOOP_CYCLES: usize = 100;

/// Deterministic input sequence for cognitive loop testing.
/// Uses step index to generate varied but reproducible text inputs.
fn deterministic_text_input(step: usize) -> &'static str {
    const INPUTS: &[&str] = &[
        "cause leads to effect",
        "pattern recognition emerges",
        "time flows forward",
        "learning from experience",
        "similarity implies relation",
        "actions have consequences",
        "before precedes after",
        "prediction reduces surprise",
        "attention focuses awareness",
        "memory preserves the past",
    ];
    INPUTS[step % INPUTS.len()]
}

/// Create a CognitiveLoopService with genesis phrase for determinism.
fn make_genesis_loop(phrase: &str, backend: TemporalBackend) -> CognitiveLoopService {
    let mut config = match backend {
        TemporalBackend::CfC => CognitiveLoopConfig::with_cfc(),
        TemporalBackend::HdcLtcUnified => CognitiveLoopConfig::with_hdc_ltc_unified(),
    };
    config.genesis_phrase = Some(phrase.to_string());
    // Disable async training to ensure deterministic weight updates
    config.async_training = false;
    CognitiveLoopService::new(config).expect("Failed to create genesis-seeded loop")
}

/// Snapshot of cycle output for comparison (excluding timing info).
#[derive(Debug, Clone, PartialEq)]
struct CycleSnapshot {
    output: Vec<f32>,
    prediction_error: f32,
    detected_primitives: Vec<String>,
    learning_occurred: bool,
}

impl CycleSnapshot {
    fn from_result(result: &symthaea::cognitive_loop::CycleResult) -> Self {
        Self {
            output: result.output.clone(),
            prediction_error: result.prediction_error,
            detected_primitives: result.detected_primitives.clone(),
            learning_occurred: result.learning_occurred,
        }
    }
}

/// Run the loop for N cycles and collect snapshots.
fn collect_cycle_snapshots(
    service: &mut CognitiveLoopService,
    cycles: usize,
) -> Vec<CycleSnapshot> {
    (0..cycles)
        .map(|step| {
            let input = deterministic_text_input(step);
            let result = service.cycle(input);
            CycleSnapshot::from_result(&result)
        })
        .collect()
}

#[test]
fn cognitive_loop_same_genesis_produces_identical_cycles_cfc() {
    let phrase = "cognitive-loop-determinism-cfc";

    let mut loop_a = make_genesis_loop(phrase, TemporalBackend::CfC);
    let mut loop_b = make_genesis_loop(phrase, TemporalBackend::CfC);

    let snapshots_a = collect_cycle_snapshots(&mut loop_a, LOOP_CYCLES);
    let snapshots_b = collect_cycle_snapshots(&mut loop_b, LOOP_CYCLES);

    // Compare each cycle
    for (i, (a, b)) in snapshots_a.iter().zip(snapshots_b.iter()).enumerate() {
        assert_eq!(
            a, b,
            "CfC loop diverged at cycle {i}: same genesis phrase must produce identical outputs"
        );
    }

    // Also verify stats match
    let stats_a = loop_a.stats();
    let stats_b = loop_b.stats();
    assert_eq!(
        stats_a.total_cycles, stats_b.total_cycles,
        "Total cycle counts differ"
    );
    // Use approximate comparison for floating-point stats
    let error_diff = (stats_a.avg_prediction_error - stats_b.avg_prediction_error).abs();
    assert!(
        error_diff < 1e-6,
        "Average prediction error differs: {} vs {} (diff: {})",
        stats_a.avg_prediction_error,
        stats_b.avg_prediction_error,
        error_diff
    );
}

#[test]
fn cognitive_loop_same_genesis_produces_identical_cycles_hdc_ltc() {
    let phrase = "cognitive-loop-determinism-hdc-ltc";

    let mut loop_a = make_genesis_loop(phrase, TemporalBackend::HdcLtcUnified);
    let mut loop_b = make_genesis_loop(phrase, TemporalBackend::HdcLtcUnified);

    let snapshots_a = collect_cycle_snapshots(&mut loop_a, LOOP_CYCLES);
    let snapshots_b = collect_cycle_snapshots(&mut loop_b, LOOP_CYCLES);

    for (i, (a, b)) in snapshots_a.iter().zip(snapshots_b.iter()).enumerate() {
        assert_eq!(
            a, b,
            "HdcLtc loop diverged at cycle {i}: same genesis phrase must produce identical outputs"
        );
    }
}

#[test]
fn cognitive_loop_different_genesis_produces_different_outputs() {
    let mut loop_a = make_genesis_loop("genesis-phrase-alpha", TemporalBackend::CfC);
    let mut loop_b = make_genesis_loop("genesis-phrase-beta", TemporalBackend::CfC);

    let snapshots_a = collect_cycle_snapshots(&mut loop_a, 20);
    let snapshots_b = collect_cycle_snapshots(&mut loop_b, 20);

    // At least some cycles should differ (likely most/all due to different weights)
    let differing_cycles = snapshots_a
        .iter()
        .zip(snapshots_b.iter())
        .filter(|(a, b)| a.output != b.output)
        .count();

    assert!(
        differing_cycles > 0,
        "Different genesis phrases must produce different outputs, but all 20 cycles matched"
    );
}

#[test]
fn cognitive_loop_genesis_determinism_across_instantiations() {
    // Create, run, collect, drop — then repeat. Results must match exactly.
    let phrase = "reproducibility-proof-loop";

    let collect = || -> Vec<CycleSnapshot> {
        let mut service = make_genesis_loop(phrase, TemporalBackend::CfC);
        collect_cycle_snapshots(&mut service, LOOP_CYCLES)
    };

    let run1 = collect();
    let run2 = collect();

    assert_eq!(
        run1, run2,
        "Two independent loop instantiations with same genesis must produce identical cycle history"
    );
}
