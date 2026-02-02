//! End-to-end determinism test for the cognitive loop's genesis seeding.
//!
//! Verifies that two HdcLtcBridge instances initialized with the same genesis
//! phrase produce identical outputs when given identical inputs, and that a
//! different phrase yields divergent state.

use ndarray::Array1;
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
