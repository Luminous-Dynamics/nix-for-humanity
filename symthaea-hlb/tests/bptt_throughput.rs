//! BPTT throughput benchmark for CfC networks.
//!
//! Marked `#[ignore]` so it doesn't run in CI.
//! Run with: cargo test -p symthaea --release --test bptt_throughput -- --ignored --nocapture

use ndarray::Array1;
use std::time::Instant;
use symthaea::dynamics::cfc::{
    ActivationType, CfCConfig, CfCNetwork, CfCNetworkConfig,
};
use symthaea_core::genesis::GenesisSeed;

fn make_config() -> CfCNetworkConfig {
    let cell_config = CfCConfig {
        input_dim: 32,
        hidden_dim: 64,
        use_backbone: true,
        backbone_layers: 2,
        backbone_dim: 64,
        activation: ActivationType::SiLU,
        tau_range: (0.1, 10.0),
        dropout: 0.0,
    };
    CfCNetworkConfig {
        input_dim: 32,
        hidden_dim: 64,
        num_layers: 2,
        output_dim: 16,
        cell_config,
        residual: true,
        bidirectional: false,
    }
}

/// Generate random training samples (input, target, dt).
fn generate_samples(n: usize) -> (Vec<Array1<f32>>, Vec<Array1<f32>>, Vec<f32>) {
    let inputs: Vec<Array1<f32>> = (0..n)
        .map(|i| {
            Array1::from_vec((0..32).map(|j| ((i * 7 + j) as f32 * 0.01).sin()).collect())
        })
        .collect();
    let targets: Vec<Array1<f32>> = (0..n)
        .map(|i| {
            Array1::from_vec((0..16).map(|j| ((i * 3 + j + 1) as f32 * 0.02).cos()).collect())
        })
        .collect();
    let dts: Vec<f32> = (0..n).map(|i| 0.01 + (i as f32 * 0.001)).collect();
    (inputs, targets, dts)
}

#[test]
#[ignore]
fn bptt_throughput_random_init() {
    let config = make_config();
    let mut net = CfCNetwork::new(config.clone());

    println!("\n========== BPTT Throughput Benchmark ==========");
    println!("Network: input=32, hidden=64, output=16, layers=2, backbone=yes");
    println!("Parameters: {}", net.num_parameters());

    let (inputs, targets, dts) = generate_samples(100);
    let n_steps = 100;

    // --- Forward-only benchmark ---
    net.reset();
    let t0 = Instant::now();
    for i in 0..n_steps {
        let _ = net.forward(&inputs[i % inputs.len()], dts[i % dts.len()]);
    }
    let fwd_elapsed = t0.elapsed();
    let fwd_us = fwd_elapsed.as_micros() as f64 / n_steps as f64;
    println!("\n[Random Init] Forward-only:");
    println!("  Total: {:.2?} for {} steps", fwd_elapsed, n_steps);
    println!("  Per step: {:.1} us", fwd_us);
    println!("  Steps/sec: {:.0}", 1_000_000.0 / fwd_us);

    // --- BPTT training benchmark ---
    net.reset();
    let t0 = Instant::now();
    let mut total_loss = 0.0f32;
    for i in 0..n_steps {
        let idx = i % inputs.len();
        let loss = net
            .train_step_bptt(
                &[inputs[idx].clone()],
                &[targets[idx].clone()],
                &[dts[idx]],
                0.001,
            )
            .unwrap();
        total_loss += loss;
    }
    let bptt_elapsed = t0.elapsed();
    let bptt_us = bptt_elapsed.as_micros() as f64 / n_steps as f64;
    println!("\n[Random Init] BPTT training:");
    println!("  Total: {:.2?} for {} steps", bptt_elapsed, n_steps);
    println!("  Per step: {:.1} us", bptt_us);
    println!("  Steps/sec: {:.0}", 1_000_000.0 / bptt_us);
    println!("  Avg loss: {:.6}", total_loss / n_steps as f32);
    println!(
        "  Real-time feasible (<1ms/step): {}",
        if bptt_us < 1000.0 { "YES" } else { "NO" }
    );

    println!("\n================================================");
}

#[test]
#[ignore]
fn bptt_throughput_genesis_init() {
    let config = make_config();
    let genesis = GenesisSeed::from_phrase("benchmark-seed-2026");
    let mut net = CfCNetwork::from_genesis(config.clone(), &genesis, "bench");

    println!("\n========= BPTT Throughput (Genesis Init) =========");
    println!("Network: input=32, hidden=64, output=16, layers=2, backbone=yes");
    println!("Parameters: {}", net.num_parameters());

    let (inputs, targets, dts) = generate_samples(100);
    let n_steps = 100;

    // --- Forward-only benchmark ---
    net.reset();
    let t0 = Instant::now();
    for i in 0..n_steps {
        let _ = net.forward(&inputs[i % inputs.len()], dts[i % dts.len()]);
    }
    let fwd_elapsed = t0.elapsed();
    let fwd_us = fwd_elapsed.as_micros() as f64 / n_steps as f64;
    println!("\n[Genesis Init] Forward-only:");
    println!("  Total: {:.2?} for {} steps", fwd_elapsed, n_steps);
    println!("  Per step: {:.1} us", fwd_us);
    println!("  Steps/sec: {:.0}", 1_000_000.0 / fwd_us);

    // --- BPTT training benchmark ---
    net.reset();
    let t0 = Instant::now();
    let mut total_loss = 0.0f32;
    for i in 0..n_steps {
        let idx = i % inputs.len();
        let loss = net
            .train_step_bptt(
                &[inputs[idx].clone()],
                &[targets[idx].clone()],
                &[dts[idx]],
                0.001,
            )
            .unwrap();
        total_loss += loss;
    }
    let bptt_elapsed = t0.elapsed();
    let bptt_us = bptt_elapsed.as_micros() as f64 / n_steps as f64;
    println!("\n[Genesis Init] BPTT training:");
    println!("  Total: {:.2?} for {} steps", bptt_elapsed, n_steps);
    println!("  Per step: {:.1} us", bptt_us);
    println!("  Steps/sec: {:.0}", 1_000_000.0 / bptt_us);
    println!("  Avg loss: {:.6}", total_loss / n_steps as f32);
    println!(
        "  Real-time feasible (<1ms/step): {}",
        if bptt_us < 1000.0 { "YES" } else { "NO" }
    );

    println!("\n==================================================");
}
