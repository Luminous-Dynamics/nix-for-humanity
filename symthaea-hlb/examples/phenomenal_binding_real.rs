//! Phenomenal Binding Experiment - Real Embeddings
//!
//! Tests hypothesis H2 using actual BGE-M3 embeddings instead of simulated vectors.
//! Compares HDC binding (XOR) vs bundling (majority vote) for unified vs separate concept pairs.
//!
//! ## Usage
//!
//! ```bash
//! cargo run --example phenomenal_binding_real --features neural-bridge --release
//! ```

use std::time::Instant;

use anyhow::Result;

#[cfg(feature = "neural-bridge")]
use symthaea::perception::bge_m3::BgeM3;

#[cfg(feature = "neural-bridge")]
use symthaea_core::hdc::{HDC_DIMENSION, binary_hv::HV16};

#[cfg(feature = "neural-bridge")]
use symthaea_core::hdc::consciousness_topology::{ConsciousnessTopology, TopologyConfig};

fn main() -> Result<()> {
    #[cfg(not(feature = "neural-bridge"))]
    {
        println!("This example requires the 'neural-bridge' feature.");
        println!("Run with: cargo run --example phenomenal_binding_real --features neural-bridge");
        return Ok(());
    }

    #[cfg(feature = "neural-bridge")]
    run_experiment()
}

#[cfg(feature = "neural-bridge")]
fn run_experiment() -> Result<()> {
    println!("\n");
    println!("================================================================");
    println!("   PHENOMENAL BINDING - REAL EMBEDDINGS");
    println!("   Testing H2: Binding vs Bundling for Phenomenal Unity");
    println!("================================================================\n");

    // Load concept pairs from JSON
    let pairs = load_concept_pairs("data/binding_study/concept_pairs.json")?;

    let unified: Vec<_> = pairs.iter().filter(|p| p.pair_type == "unified").collect();
    let separate: Vec<_> = pairs.iter().filter(|p| p.pair_type == "separate").collect();

    println!("Loaded concept pairs:");
    println!("  Unified pairs: {}", unified.len());
    println!("  Separate pairs: {}\n", separate.len());

    // Load BGE-M3 encoder
    println!("Loading BGE-M3 encoder...");
    let load_start = Instant::now();
    let encoder = BgeM3::load_from_hub("BAAI/bge-m3")?;
    println!("  Loaded in {:.2}s\n", load_start.elapsed().as_secs_f64());

    // Topology config
    let topology_config = TopologyConfig {
        min_persistence: 0.1,
        max_scale: 1.0,
        num_scales: 10,
        detect_cycles: true,
        detect_voids: false,
    };

    println!("================================================================");
    println!("   ENCODING AND ANALYZING PAIRS");
    println!("================================================================\n");

    // Process unified pairs
    println!("Processing unified pairs...");
    let unified_start = Instant::now();
    let mut unified_results = Vec::new();

    for (i, pair) in unified.iter().enumerate() {
        if i % 10 == 0 {
            print!("  {}/{}\r", i, unified.len());
        }

        let emb_a = encoder.encode(&pair.concept_a)?;
        let emb_b = encoder.encode(&pair.concept_b)?;

        let hv_a = embedding_to_hv16(&emb_a);
        let hv_b = embedding_to_hv16(&emb_b);

        let bound = hv_a.bind(&hv_b);
        let bundled = HV16::bundle(&[hv_a, hv_b]);

        let bind_unity = compute_unity(&bound, &topology_config);
        let bundle_unity = compute_unity(&bundled, &topology_config);

        unified_results.push(BindingResult {
            pair_id: pair.id.clone(),
            pair_type: "unified".to_string(),
            bind_unity,
            bundle_unity,
        });
    }
    println!("  Completed in {:.1}s", unified_start.elapsed().as_secs_f64());

    // Process separate pairs
    println!("Processing separate pairs...");
    let separate_start = Instant::now();
    let mut separate_results = Vec::new();

    for (i, pair) in separate.iter().enumerate() {
        if i % 10 == 0 {
            print!("  {}/{}\r", i, separate.len());
        }

        let emb_a = encoder.encode(&pair.concept_a)?;
        let emb_b = encoder.encode(&pair.concept_b)?;

        let hv_a = embedding_to_hv16(&emb_a);
        let hv_b = embedding_to_hv16(&emb_b);

        let bound = hv_a.bind(&hv_b);
        let bundled = HV16::bundle(&[hv_a, hv_b]);

        let bind_unity = compute_unity(&bound, &topology_config);
        let bundle_unity = compute_unity(&bundled, &topology_config);

        separate_results.push(BindingResult {
            pair_id: pair.id.clone(),
            pair_type: "separate".to_string(),
            bind_unity,
            bundle_unity,
        });
    }
    println!("  Completed in {:.1}s\n", separate_start.elapsed().as_secs_f64());

    // Compute statistics
    println!("================================================================");
    println!("   2x2 ANOVA RESULTS");
    println!("================================================================\n");

    // Cell means
    let unified_bind: Vec<f64> = unified_results.iter().map(|r| r.bind_unity).collect();
    let unified_bundle: Vec<f64> = unified_results.iter().map(|r| r.bundle_unity).collect();
    let separate_bind: Vec<f64> = separate_results.iter().map(|r| r.bind_unity).collect();
    let separate_bundle: Vec<f64> = separate_results.iter().map(|r| r.bundle_unity).collect();

    let mean_unified_bind = mean(&unified_bind);
    let mean_unified_bundle = mean(&unified_bundle);
    let mean_separate_bind = mean(&separate_bind);
    let mean_separate_bundle = mean(&separate_bundle);

    println!("Cell Means (Unity Score):");
    println!("                    Unified (n={})    Separate (n={})", unified.len(), separate.len());
    println!("  Bind:             {:.4}              {:.4}", mean_unified_bind, mean_separate_bind);
    println!("  Bundle:           {:.4}              {:.4}\n", mean_unified_bundle, mean_separate_bundle);

    // Main effects
    let main_operation = ((mean_unified_bind + mean_separate_bind) / 2.0)
        - ((mean_unified_bundle + mean_separate_bundle) / 2.0);
    let main_pair_type = ((mean_unified_bind + mean_unified_bundle) / 2.0)
        - ((mean_separate_bind + mean_separate_bundle) / 2.0);

    println!("Main Effects:");
    println!("  Operation (Bind - Bundle): {:+.4}", main_operation);
    println!("  Pair Type (Unified - Separate): {:+.4}\n", main_pair_type);

    // Simple effects (binding advantage within each pair type)
    let binding_advantage_unified = mean_unified_bind - mean_unified_bundle;
    let binding_advantage_separate = mean_separate_bind - mean_separate_bundle;

    println!("Simple Effects (Binding Advantage):");
    println!("  For UNIFIED pairs: {:+.4}", binding_advantage_unified);
    println!("  For SEPARATE pairs: {:+.4}\n", binding_advantage_separate);

    // Interaction effect
    let interaction = binding_advantage_unified - binding_advantage_separate;

    println!("Interaction Effect:");
    println!("  (Bind_Unified - Bundle_Unified) - (Bind_Separate - Bundle_Separate)");
    println!("  = {:+.4} - {:+.4} = {:+.4}\n", binding_advantage_unified, binding_advantage_separate, interaction);

    // Effect sizes
    let all_bind: Vec<f64> = unified_bind.iter().chain(separate_bind.iter()).copied().collect();
    let all_bundle: Vec<f64> = unified_bundle.iter().chain(separate_bundle.iter()).copied().collect();

    let d_overall = cohens_d(&all_bind, &all_bundle);
    let d_unified = cohens_d(&unified_bind, &unified_bundle);
    let d_separate = cohens_d(&separate_bind, &separate_bundle);

    println!("Effect Sizes (Cohen's d):");
    println!("  Overall (Bind vs Bundle): {:+.4}", d_overall);
    println!("  Within Unified: {:+.4}", d_unified);
    println!("  Within Separate: {:+.4}\n", d_separate);

    // Statistical tests
    let p_interaction = permutation_test_interaction(&unified_bind, &unified_bundle, &separate_bind, &separate_bundle, 10000);
    let p_unified = permutation_test(&unified_bind, &unified_bundle, 10000);
    let p_separate = permutation_test(&separate_bind, &separate_bundle, 10000);

    println!("Statistical Significance (Permutation Tests, n=10000):");
    println!("  Interaction effect: p = {:.4} {}", p_interaction, if p_interaction < 0.05 { "*" } else { "" });
    println!("  Binding effect (unified): p = {:.4} {}", p_unified, if p_unified < 0.05 { "*" } else { "" });
    println!("  Binding effect (separate): p = {:.4} {}\n", p_separate, if p_separate < 0.05 { "*" } else { "" });

    // Interpretation
    println!("================================================================");
    println!("   INTERPRETATION");
    println!("================================================================\n");

    if interaction > 0.0 && p_interaction < 0.05 {
        println!("✓ HYPOTHESIS H2 SUPPORTED");
        println!("  Binding produces significantly higher unity for unified pairs");
        println!("  compared to separate pairs (interaction = {:+.4}, p = {:.4})", interaction, p_interaction);
    } else if interaction < 0.0 && p_interaction < 0.05 {
        println!("✗ HYPOTHESIS H2 REJECTED (Opposite Effect)");
        println!("  Binding produces LOWER unity for unified pairs");
        println!("  compared to separate pairs (interaction = {:+.4}, p = {:.4})", interaction, p_interaction);
    } else {
        println!("○ HYPOTHESIS H2 NOT SUPPORTED");
        println!("  No significant interaction effect detected");
        println!("  (interaction = {:+.4}, p = {:.4})", interaction, p_interaction);
    }

    // Additional analysis: correlation between semantic similarity and binding effect
    println!("\n================================================================");
    println!("   SAMPLE RESULTS");
    println!("================================================================\n");

    // Sort by binding advantage
    let mut all_results: Vec<_> = unified_results.iter().chain(separate_results.iter()).collect();
    all_results.sort_by(|a, b| {
        let adv_a = a.bind_unity - a.bundle_unity;
        let adv_b = b.bind_unity - b.bundle_unity;
        adv_b.partial_cmp(&adv_a).unwrap()
    });

    println!("Top 5 pairs where BINDING helps most:");
    for r in all_results.iter().take(5) {
        let adv = r.bind_unity - r.bundle_unity;
        println!("  {} ({}): bind={:.3}, bundle={:.3}, adv={:+.3}",
                 r.pair_id, r.pair_type, r.bind_unity, r.bundle_unity, adv);
    }

    println!("\nTop 5 pairs where BUNDLE helps most:");
    for r in all_results.iter().rev().take(5) {
        let adv = r.bind_unity - r.bundle_unity;
        println!("  {} ({}): bind={:.3}, bundle={:.3}, adv={:+.3}",
                 r.pair_id, r.pair_type, r.bind_unity, r.bundle_unity, adv);
    }

    println!("\n================================================================");
    println!("   EXPERIMENT COMPLETE");
    println!("================================================================\n");

    Ok(())
}

#[cfg(feature = "neural-bridge")]
#[derive(Debug)]
struct ConceptPair {
    id: String,
    concept_a: String,
    concept_b: String,
    pair_type: String,
}

#[cfg(feature = "neural-bridge")]
#[derive(Debug)]
struct BindingResult {
    pair_id: String,
    pair_type: String,
    bind_unity: f64,
    bundle_unity: f64,
}

#[cfg(feature = "neural-bridge")]
fn load_concept_pairs(path: &str) -> Result<Vec<ConceptPair>> {
    let content = std::fs::read_to_string(path)?;
    let json: serde_json::Value = serde_json::from_str(&content)?;

    let mut pairs = Vec::new();

    // Try both naming conventions
    let pair_keys = [
        ("unified_pairs", "unified"),
        ("separate_pairs", "separate"),
        ("unified", "unified"),
        ("separate", "separate"),
    ];

    for (json_key, pair_type) in pair_keys {
        if let Some(items) = json[json_key].as_array() {
            for item in items {
                pairs.push(ConceptPair {
                    id: item["id"].as_str().unwrap_or("unknown").to_string(),
                    concept_a: item["concept_a"].as_str().unwrap_or("").to_string(),
                    concept_b: item["concept_b"].as_str().unwrap_or("").to_string(),
                    pair_type: pair_type.to_string(),
                });
            }
        }
    }

    Ok(pairs)
}

#[cfg(feature = "neural-bridge")]
fn embedding_to_hv16(embedding: &[f32]) -> HV16 {
    // Expand 1024-dim embedding to 16384-dim via tiling with position-dependent perturbation
    let mut expanded = Vec::with_capacity(HDC_DIMENSION);
    let tiles = HDC_DIMENSION / embedding.len();

    for tile in 0..tiles {
        for (i, &val) in embedding.iter().enumerate() {
            let perturbation = ((tile * embedding.len() + i) as f32 * 0.001).sin() * 0.01;
            expanded.push(val + perturbation);
        }
    }

    HV16::from_bipolar(&expanded)
}

#[cfg(feature = "neural-bridge")]
fn compute_unity(hv: &HV16, config: &TopologyConfig) -> f64 {
    let mut topology = ConsciousnessTopology::new(config.clone());

    topology.add_state(*hv);
    for shift in 1..5 {
        topology.add_state(hv.permute(shift * 100));
    }

    let assessment = topology.analyze(0.5);
    assessment.unity_score
}

#[cfg(feature = "neural-bridge")]
fn mean(values: &[f64]) -> f64 {
    if values.is_empty() { return 0.0; }
    values.iter().sum::<f64>() / values.len() as f64
}

#[cfg(feature = "neural-bridge")]
fn std_dev(values: &[f64]) -> f64 {
    if values.len() < 2 { return 0.0; }
    let m = mean(values);
    let variance = values.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (values.len() - 1) as f64;
    variance.sqrt()
}

#[cfg(feature = "neural-bridge")]
fn cohens_d(group_a: &[f64], group_b: &[f64]) -> f64 {
    let mean_diff = mean(group_a) - mean(group_b);
    let pooled_std = ((std_dev(group_a).powi(2) + std_dev(group_b).powi(2)) / 2.0).sqrt();
    if pooled_std > 0.0 { mean_diff / pooled_std } else { 0.0 }
}

#[cfg(feature = "neural-bridge")]
fn permutation_test(group_a: &[f64], group_b: &[f64], n_permutations: usize) -> f64 {
    let observed_diff = mean(group_a) - mean(group_b);

    let mut combined: Vec<f64> = group_a.iter().chain(group_b.iter()).copied().collect();
    let n_a = group_a.len();

    let mut more_extreme = 0;
    let mut rng_state: u64 = 42;

    for _ in 0..n_permutations {
        // Fisher-Yates shuffle
        for i in (1..combined.len()).rev() {
            rng_state = rng_state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let j = (rng_state as usize) % (i + 1);
            combined.swap(i, j);
        }

        let perm_a: f64 = combined[..n_a].iter().sum::<f64>() / n_a as f64;
        let perm_b: f64 = combined[n_a..].iter().sum::<f64>() / (combined.len() - n_a) as f64;
        let perm_diff = perm_a - perm_b;

        if perm_diff.abs() >= observed_diff.abs() {
            more_extreme += 1;
        }
    }

    more_extreme as f64 / n_permutations as f64
}

#[cfg(feature = "neural-bridge")]
fn permutation_test_interaction(
    unified_bind: &[f64],
    unified_bundle: &[f64],
    separate_bind: &[f64],
    separate_bundle: &[f64],
    n_permutations: usize,
) -> f64 {
    // Observed interaction
    let observed = (mean(unified_bind) - mean(unified_bundle)) - (mean(separate_bind) - mean(separate_bundle));

    // Combine all data with labels
    let mut data: Vec<(f64, usize, usize)> = Vec::new(); // (value, pair_type, operation)

    for &v in unified_bind { data.push((v, 0, 0)); }
    for &v in unified_bundle { data.push((v, 0, 1)); }
    for &v in separate_bind { data.push((v, 1, 0)); }
    for &v in separate_bundle { data.push((v, 1, 1)); }

    let mut more_extreme = 0;
    let mut rng_state: u64 = 12345;

    for _ in 0..n_permutations {
        // Shuffle values while keeping labels fixed
        for i in (1..data.len()).rev() {
            rng_state = rng_state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let j = (rng_state as usize) % (i + 1);
            let tmp = data[i].0;
            data[i].0 = data[j].0;
            data[j].0 = tmp;
        }

        // Compute permuted interaction
        let perm_unified_bind: f64 = data.iter().filter(|d| d.1 == 0 && d.2 == 0).map(|d| d.0).sum::<f64>()
            / data.iter().filter(|d| d.1 == 0 && d.2 == 0).count() as f64;
        let perm_unified_bundle: f64 = data.iter().filter(|d| d.1 == 0 && d.2 == 1).map(|d| d.0).sum::<f64>()
            / data.iter().filter(|d| d.1 == 0 && d.2 == 1).count() as f64;
        let perm_separate_bind: f64 = data.iter().filter(|d| d.1 == 1 && d.2 == 0).map(|d| d.0).sum::<f64>()
            / data.iter().filter(|d| d.1 == 1 && d.2 == 0).count() as f64;
        let perm_separate_bundle: f64 = data.iter().filter(|d| d.1 == 1 && d.2 == 1).map(|d| d.0).sum::<f64>()
            / data.iter().filter(|d| d.1 == 1 && d.2 == 1).count() as f64;

        let perm_interaction = (perm_unified_bind - perm_unified_bundle) - (perm_separate_bind - perm_separate_bundle);

        if perm_interaction.abs() >= observed.abs() {
            more_extreme += 1;
        }
    }

    more_extreme as f64 / n_permutations as f64
}
