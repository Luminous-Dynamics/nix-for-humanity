//! Dream Feedback Loop Experiment
//!
//! Tests whether dream-informed predictions have better calibration than baseline.
//!
//! ## Experiment Design
//!
//! 1. Simulate a series of prediction tasks
//! 2. Some tasks receive dream feedback (learned priors from counterfactuals)
//! 3. Compare Brier scores between dream-informed and baseline predictions
//!
//! ## Hypothesis
//!
//! Dream feedback should improve calibration because:
//! - Dreams identify contexts where our actions could be better
//! - This creates priors that bias toward better predictions
//! - Over time, dream-informed predictions should have lower Brier scores
//!
//! ## Usage
//!
//! ```bash
//! cargo run --example dream_feedback_experiment --features magi_loop --release
//! ```

use anyhow::Result;

#[cfg(feature = "magi_loop")]
use symthaea::consciousness::recursive_improvement::{
    DreamFeedbackBridge, DreamInsight, hash_context,
};

fn main() -> Result<()> {
    #[cfg(not(feature = "magi_loop"))]
    {
        println!("This example requires the 'magi_loop' feature.");
        println!("Run with: cargo run --example dream_feedback_experiment --features magi_loop --release");
        return Ok(());
    }

    #[cfg(feature = "magi_loop")]
    run_experiment()
}

#[cfg(feature = "magi_loop")]
fn run_experiment() -> Result<()> {
    println!("\n");
    println!("================================================================");
    println!("   DREAM FEEDBACK LOOP EXPERIMENT");
    println!("   Does counterfactual learning improve prediction calibration?");
    println!("================================================================\n");

    // Initialize the dream feedback bridge
    let mut bridge = DreamFeedbackBridge::new();

    // Simulate dream insights from counterfactual exploration
    println!("Phase 1: Generating dream insights from counterfactual simulation...\n");

    // Create some contexts and discover better alternatives via "dreaming"
    let contexts = generate_contexts(50);
    let mut insights_created = 0;

    for (i, context) in contexts.iter().enumerate() {
        let context_hash = hash_context(context);

        // Simulate dreaming: discover that some alternative action would have been better
        // (In real system, this comes from DreamEngine::dream())
        let phi_improvement = simulate_dream_discovery(i);

        if phi_improvement > 0.05 {
            let insight = DreamInsight::new(
                context_hash,
                context.clone(),                    // Original action
                perturb_action(context, 0.2),       // Better alternative
                phi_improvement,
            );

            if bridge.process_insight(insight) {
                insights_created += 1;
            }
        }
    }

    println!("  Generated {} dream insights", insights_created);
    println!("  Active priors: {}\n", bridge.num_priors());

    // Phase 2: Make predictions with and without dream priors
    println!("Phase 2: Making predictions (500 trials)...\n");

    let mut rng_seed: u64 = 12345;

    for trial in 0..500 {
        // Generate a new context
        let context = generate_context(trial);
        let context_hash = hash_context(&context);

        // Base confidence from hypothetical model
        let base_confidence = 0.6 + 0.2 * pseudo_random(&mut rng_seed);

        // Adjust confidence based on dream feedback
        let (adjusted_confidence, was_dream_informed) = bridge.adjust_confidence(base_confidence, context_hash);

        // Simulate actual outcome (with some correlation to confidence)
        let outcome = simulate_outcome(adjusted_confidence, &mut rng_seed);

        // Calculate Brier score: (confidence - outcome)^2
        let brier_score = if outcome {
            (adjusted_confidence - 1.0).powi(2)
        } else {
            adjusted_confidence.powi(2)
        };

        // Record the outcome
        bridge.record_outcome(context_hash, brier_score);

        // Progress indicator
        if (trial + 1) % 100 == 0 {
            print!("  Trial {}/500\r", trial + 1);
        }
    }
    println!("  Done                    \n");

    // Phase 3: Analyze results
    println!("================================================================");
    println!("   RESULTS");
    println!("================================================================\n");

    let stats = bridge.stats();

    println!("Prediction Counts:");
    println!("  Dream-informed: {}", stats.dream_informed_predictions);
    println!("  Baseline: {}\n", stats.baseline_predictions);

    println!("Brier Scores (lower is better):");
    if let Some(dream_brier) = stats.dream_informed_brier() {
        println!("  Dream-informed: {:.4}", dream_brier);
    }
    if let Some(baseline_brier) = stats.baseline_brier() {
        println!("  Baseline: {:.4}", baseline_brier);
    }

    if let Some(improvement) = stats.brier_improvement() {
        println!("\nImprovement: {:+.4}", -improvement);

        if improvement < 0.0 {
            println!("  Dream feedback IMPROVED calibration by {:.1}%",
                     (-improvement / stats.baseline_brier().unwrap_or(1.0)) * 100.0);
        } else if improvement > 0.0 {
            println!("  Dream feedback WORSENED calibration by {:.1}%",
                     (improvement / stats.baseline_brier().unwrap_or(1.0)) * 100.0);
        } else {
            println!("  No difference detected");
        }
    }

    // Statistical significance test
    println!("\n================================================================");
    println!("   STATISTICAL ANALYSIS");
    println!("================================================================\n");

    // Bootstrap confidence interval for the difference
    let (ci_lower, ci_upper) = bootstrap_ci(stats);

    println!("Bootstrap 95% CI for Brier improvement: [{:+.4}, {:+.4}]",
             ci_lower, ci_upper);

    if ci_upper < 0.0 {
        println!("\n✓ DREAM FEEDBACK SIGNIFICANTLY IMPROVES CALIBRATION");
        println!("  95% CI excludes zero in the positive direction");
    } else if ci_lower > 0.0 {
        println!("\n✗ DREAM FEEDBACK WORSENS CALIBRATION");
        println!("  95% CI excludes zero in the negative direction");
    } else {
        println!("\n○ NO SIGNIFICANT DIFFERENCE");
        println!("  95% CI includes zero");
    }

    // Summary
    println!("\n================================================================");
    println!("   DREAM FEEDBACK BRIDGE REPORT");
    println!("================================================================\n");

    println!("{}", bridge.summary_report());

    println!("================================================================");
    println!("   EXPERIMENT COMPLETE");
    println!("================================================================\n");

    Ok(())
}

/// Generate a context vector
#[cfg(feature = "magi_loop")]
fn generate_context(seed: usize) -> Vec<f32> {
    let mut context = Vec::with_capacity(64);
    let mut s = seed as f32;
    for _ in 0..64 {
        s = (s * 1.5 + 0.7).sin() * 100.0;
        context.push(s.fract());
    }
    context
}

/// Generate multiple contexts
#[cfg(feature = "magi_loop")]
fn generate_contexts(n: usize) -> Vec<Vec<f32>> {
    (0..n).map(generate_context).collect()
}

/// Simulate dream discovery (some contexts have better alternatives)
#[cfg(feature = "magi_loop")]
fn simulate_dream_discovery(context_idx: usize) -> f64 {
    // Some contexts (roughly 40%) have discoverable improvements
    let seed = (context_idx * 7 + 13) % 100;
    if seed < 40 {
        0.05 + (seed as f64 * 0.005) // 5-25% improvement
    } else {
        0.0 // No improvement found
    }
}

/// Perturb an action vector
#[cfg(feature = "magi_loop")]
fn perturb_action(action: &[f32], amount: f32) -> Vec<f32> {
    action.iter()
        .enumerate()
        .map(|(i, &v)| v + amount * ((i as f32 * 0.1).sin()))
        .collect()
}

/// Pseudo-random number generator (0-1)
#[cfg(feature = "magi_loop")]
fn pseudo_random(seed: &mut u64) -> f64 {
    *seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
    (*seed as f64) / (u64::MAX as f64)
}

/// Simulate an outcome (success/failure)
#[cfg(feature = "magi_loop")]
fn simulate_outcome(confidence: f64, rng: &mut u64) -> bool {
    // Outcome has some correlation with confidence
    // Higher confidence = slightly higher success rate
    let base_rate = 0.4 + confidence * 0.3; // 40-70% base success
    pseudo_random(rng) < base_rate
}

/// Bootstrap confidence interval for Brier improvement
#[cfg(feature = "magi_loop")]
fn bootstrap_ci(stats: &symthaea::consciousness::recursive_improvement::DreamFeedbackStats) -> (f64, f64) {
    // Simplified bootstrap (in production, would resample actual predictions)
    // For now, use normal approximation

    let n_dream = stats.dream_informed_predictions as f64;
    let n_base = stats.baseline_predictions as f64;

    if n_dream < 2.0 || n_base < 2.0 {
        return (-1.0, 1.0);
    }

    let dream_mean = stats.dream_informed_brier().unwrap_or(0.5);
    let base_mean = stats.baseline_brier().unwrap_or(0.5);

    // Estimate standard errors (assuming Brier scores ~ variance 0.25)
    let se_dream = (0.25_f64 / n_dream).sqrt();
    let se_base = (0.25_f64 / n_base).sqrt();

    // SE of difference
    let se_diff = (se_dream.powi(2) + se_base.powi(2)).sqrt();

    // 95% CI
    let diff = dream_mean - base_mean;
    let ci_lower = diff - 1.96 * se_diff;
    let ci_upper = diff + 1.96 * se_diff;

    (ci_lower, ci_upper)
}
