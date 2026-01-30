//! Phenomenal Binding Experiment
//!
//! This example demonstrates Research Direction 2: Testing whether HDC binding (XOR)
//! produces representations with higher topological integration than bundling
//! (majority vote) for concept pairs humans report as phenomenally unified.
//!
//! ## Hypothesis (H2)
//!
//! HDC binding (⊗) produces representations with higher topological integration
//! (lower component count, higher unity score) than bundling (⊕), specifically
//! for concept pairs humans report as phenomenally unified.
//!
//! ## Experimental Design
//!
//! 2x2 Factorial ANOVA:
//! - Factor 1: Operation (Bind vs Bundle)
//! - Factor 2: Pair Type (Unified vs Separate)
//! - Key test: Interaction effect (binding specifically helps unified pairs)
//!
//! ## Usage
//!
//! ```bash
//! cargo run --example phenomenal_binding_experiment
//! ```

use std::path::Path;

use symthaea_core::hdc::binary_hv::HV16;
use symthaea_core::hdc::consciousness_topology::{
    BettiNumbers, ConsciousnessTopology, TopologyConfig,
};

/// Type of concept pair
#[derive(Debug, Clone, Copy, PartialEq)]
enum PairType {
    Unified,
    Separate,
}

/// A concept pair for the experiment
#[derive(Debug, Clone)]
struct ConceptPair {
    id: String,
    concept_a: String,
    concept_b: String,
    pair_type: PairType,
    hv_a: HV16,
    hv_b: HV16,
}

/// Result of comparing bind vs bundle for one pair
#[derive(Debug, Clone)]
struct ComparisonResult {
    pair_id: String,
    pair_type: PairType,
    bind_unity: f64,
    bundle_unity: f64,
    unity_advantage: f64,
    bind_beta_0: usize,
    bundle_beta_0: usize,
}

/// Cell means for 2x2 ANOVA
#[derive(Debug)]
struct CellMeans {
    bind_unified: f64,
    bind_separate: f64,
    bundle_unified: f64,
    bundle_separate: f64,
    n_unified: usize,
    n_separate: usize,
}

fn main() {
    println!("\n");
    println!("================================================================");
    println!("   PHENOMENAL BINDING EXPERIMENT");
    println!("   Research Direction 2: HDC Binding vs Bundling");
    println!("================================================================\n");

    // Check if data file exists
    let pairs_path = Path::new("data/binding_study/concept_pairs.json");
    if !pairs_path.exists() {
        println!("NOTE: Concept pairs file not found. Using simulated pairs.\n");
    }

    // Create concept pairs (in production, load from JSON)
    let unified_pairs = create_unified_pairs();
    let separate_pairs = create_separate_pairs();

    let mut all_pairs = unified_pairs.clone();
    all_pairs.extend(separate_pairs.clone());

    println!("Experiment Setup:");
    println!("  Unified pairs: {}", unified_pairs.len());
    println!("  Separate pairs: {}", separate_pairs.len());
    println!("  Total pairs: {}\n", all_pairs.len());

    // Run the experiment
    println!("Running experiment...\n");
    let results: Vec<ComparisonResult> = all_pairs.iter().map(|pair| compare_operations(pair)).collect();

    // Compute cell means for 2x2 ANOVA
    let cell_means = compute_cell_means(&results);

    // Display cell means
    println!("================================================================");
    println!("   CELL MEANS (Unity Score)");
    println!("================================================================\n");

    println!("                 Unified (n={})    Separate (n={})",
             cell_means.n_unified, cell_means.n_separate);
    println!("  Bind:          {:.4}              {:.4}",
             cell_means.bind_unified, cell_means.bind_separate);
    println!("  Bundle:        {:.4}              {:.4}\n",
             cell_means.bundle_unified, cell_means.bundle_separate);

    // Compute effects
    let bind_mean = (cell_means.bind_unified + cell_means.bind_separate) / 2.0;
    let bundle_mean = (cell_means.bundle_unified + cell_means.bundle_separate) / 2.0;
    let main_effect_operation = bind_mean - bundle_mean;

    let unified_mean = (cell_means.bind_unified + cell_means.bundle_unified) / 2.0;
    let separate_mean = (cell_means.bind_separate + cell_means.bundle_separate) / 2.0;
    let main_effect_pair_type = unified_mean - separate_mean;

    // Interaction effect: Does binding's advantage depend on pair type?
    let bind_advantage_unified = cell_means.bind_unified - cell_means.bundle_unified;
    let bind_advantage_separate = cell_means.bind_separate - cell_means.bundle_separate;
    let interaction = bind_advantage_unified - bind_advantage_separate;

    println!("================================================================");
    println!("   ANOVA RESULTS");
    println!("================================================================\n");

    println!("Main Effects:");
    println!("  Operation (Bind - Bundle): {:.4}", main_effect_operation);
    println!("  Pair Type (Unified - Separate): {:.4}\n", main_effect_pair_type);

    println!("Simple Effects:");
    println!("  Binding advantage for UNIFIED pairs: {:.4}", bind_advantage_unified);
    println!("  Binding advantage for SEPARATE pairs: {:.4}\n", bind_advantage_separate);

    println!("Interaction Effect:");
    println!("  (Bind_Unified - Bundle_Unified) - (Bind_Separate - Bundle_Separate)");
    println!("  = {:.4} - {:.4} = {:.4}\n",
             bind_advantage_unified, bind_advantage_separate, interaction);

    // Effect size calculations
    let all_unity: Vec<f64> = results
        .iter()
        .flat_map(|r| vec![r.bind_unity, r.bundle_unity])
        .collect();
    let variance = compute_variance(&all_unity);
    let std_dev = variance.sqrt().max(0.001);

    let cohens_d_overall = main_effect_operation / std_dev;
    let cohens_d_unified = bind_advantage_unified / std_dev;
    let cohens_d_separate = bind_advantage_separate / std_dev;

    println!("Effect Sizes (Cohen's d):");
    println!("  Overall binding advantage: {:.4}", cohens_d_overall);
    println!("  Binding advantage (unified): {:.4}", cohens_d_unified);
    println!("  Binding advantage (separate): {:.4}\n", cohens_d_separate);

    // Simplified F-test for interaction
    let mse = variance.max(0.001);
    let f_interaction = (interaction.powi(2) * results.len() as f64) / mse;
    let interaction_significant = f_interaction > 3.84; // Approximate critical F

    println!("Interaction Test:");
    println!("  F-statistic: {:.4}", f_interaction);
    println!("  Significant (F > 3.84): {}\n", if interaction_significant { "Yes" } else { "No" });

    // Interpretation
    println!("================================================================");
    println!("   INTERPRETATION");
    println!("================================================================\n");

    if interaction_significant && interaction > 0.0 {
        println!("HYPOTHESIS H2 SUPPORTED:");
        println!("The interaction effect is SIGNIFICANT and POSITIVE.");
        println!("Binding provides a larger unity advantage for UNIFIED pairs");
        println!("({:.4}) than for SEPARATE pairs ({:.4}).",
                 bind_advantage_unified, bind_advantage_separate);
        println!("\nThis suggests that HDC binding (XOR) captures something");
        println!("meaningful about phenomenal unity that bundling does not.\n");
    } else if interaction_significant && interaction < 0.0 {
        println!("UNEXPECTED RESULT:");
        println!("The interaction effect is significant but NEGATIVE.");
        println!("Binding provides MORE advantage for SEPARATE pairs.");
        println!("This is opposite to hypothesis H2 prediction.\n");
    } else if main_effect_operation > 0.0 && cohens_d_overall.abs() > 0.2 {
        println!("PARTIAL SUPPORT:");
        println!("No significant interaction, but binding shows an overall");
        println!("advantage (d = {:.4}) regardless of pair type.", cohens_d_overall);
        println!("Binding creates more unified representations in general,");
        println!("but this effect is not specific to phenomenally unified pairs.\n");
    } else {
        println!("HYPOTHESIS H2 NOT SUPPORTED:");
        println!("No significant interaction effect detected.");
        println!("Binding's effect on unity does not depend on whether");
        println!("concept pairs are phenomenally unified or separate.\n");
    }

    // Sample individual results
    println!("================================================================");
    println!("   SAMPLE RESULTS");
    println!("================================================================\n");

    println!("Top 5 UNIFIED pairs by binding advantage:");
    let mut unified_results: Vec<_> = results.iter()
        .filter(|r| r.pair_type == PairType::Unified)
        .collect();
    unified_results.sort_by(|a, b| b.unity_advantage.partial_cmp(&a.unity_advantage).unwrap());
    for r in unified_results.iter().take(5) {
        println!("  {} - Bind: {:.4}, Bundle: {:.4}, Advantage: {:.4}",
                 r.pair_id, r.bind_unity, r.bundle_unity, r.unity_advantage);
    }

    println!("\nTop 5 SEPARATE pairs by binding advantage:");
    let mut separate_results: Vec<_> = results.iter()
        .filter(|r| r.pair_type == PairType::Separate)
        .collect();
    separate_results.sort_by(|a, b| b.unity_advantage.partial_cmp(&a.unity_advantage).unwrap());
    for r in separate_results.iter().take(5) {
        println!("  {} - Bind: {:.4}, Bundle: {:.4}, Advantage: {:.4}",
                 r.pair_id, r.bind_unity, r.bundle_unity, r.unity_advantage);
    }

    println!("\n================================================================");
    println!("   EXPERIMENT COMPLETE");
    println!("================================================================\n");
    println!("Note: This experiment uses simulated concept vectors.");
    println!("In production, vectors would be derived from semantic");
    println!("embeddings or LLM activations via the Neural Bridge.\n");
}

/// Create unified concept pairs
fn create_unified_pairs() -> Vec<ConceptPair> {
    let pairs_data = vec![
        ("red", "apple", "red_apple"),
        ("loud", "crash", "loud_crash"),
        ("soft", "fur", "soft_fur"),
        ("sweet", "strawberry", "sweet_strawberry"),
        ("warm", "sunlight", "warm_sunlight"),
        ("sharp", "pain", "sharp_pain"),
        ("blue", "sky", "blue_sky"),
        ("cold", "ice", "cold_ice"),
        ("bright", "light", "bright_light"),
        ("deep", "voice", "deep_voice"),
        ("smooth", "silk", "smooth_silk"),
        ("fragrant", "rose", "fragrant_rose"),
        ("bitter", "coffee", "bitter_coffee"),
        ("heavy", "stone", "heavy_stone"),
        ("green", "grass", "green_grass"),
    ];

    pairs_data
        .into_iter()
        .enumerate()
        .map(|(i, (a, b, id))| {
            let seed_a = hash_concept(a);
            let seed_b = hash_concept(b);
            ConceptPair {
                id: id.to_string(),
                concept_a: a.to_string(),
                concept_b: b.to_string(),
                pair_type: PairType::Unified,
                hv_a: HV16::random(seed_a + i as u64),
                hv_b: HV16::random(seed_b + i as u64),
            }
        })
        .collect()
}

/// Create separate concept pairs
fn create_separate_pairs() -> Vec<ConceptPair> {
    let pairs_data = vec![
        ("red", "mailbox", "red_mailbox"),
        ("loud", "background", "loud_background"),
        ("cold", "thought", "cold_thought"),
        ("bright", "memory", "bright_memory"),
        ("sweet", "distance", "sweet_distance"),
        ("heavy", "silence", "heavy_silence"),
        ("sharp", "idea", "sharp_idea"),
        ("warm", "number", "warm_number"),
        ("soft", "logic", "soft_logic"),
        ("blue", "argument", "blue_argument"),
        ("rough", "calculation", "rough_calculation"),
        ("deep", "question", "deep_question"),
        ("bitter", "theory", "bitter_theory"),
        ("green", "decision", "green_decision"),
        ("smooth", "schedule", "smooth_schedule"),
    ];

    pairs_data
        .into_iter()
        .enumerate()
        .map(|(i, (a, b, id))| {
            let seed_a = hash_concept(a) + 5000;
            let seed_b = hash_concept(b) + 5000;
            ConceptPair {
                id: id.to_string(),
                concept_a: a.to_string(),
                concept_b: b.to_string(),
                pair_type: PairType::Separate,
                hv_a: HV16::random(seed_a + i as u64),
                hv_b: HV16::random(seed_b + i as u64),
            }
        })
        .collect()
}

/// Hash concept text to u64 for deterministic seeding
fn hash_concept(text: &str) -> u64 {
    text.bytes().fold(0u64, |acc, b| acc.wrapping_mul(31).wrapping_add(b as u64))
}

/// Compare bind vs bundle for a concept pair
fn compare_operations(pair: &ConceptPair) -> ComparisonResult {
    // Compute bound representation (XOR)
    let bound = pair.hv_a.bind(&pair.hv_b);

    // Compute bundled representation (majority vote)
    let bundled = HV16::bundle(&[pair.hv_a, pair.hv_b]);

    // Analyze topology for both
    let bind_assessment = analyze_topology(&bound);
    let bundle_assessment = analyze_topology(&bundled);

    ComparisonResult {
        pair_id: pair.id.clone(),
        pair_type: pair.pair_type,
        bind_unity: bind_assessment.0,
        bundle_unity: bundle_assessment.0,
        unity_advantage: bind_assessment.0 - bundle_assessment.0,
        bind_beta_0: bind_assessment.1,
        bundle_beta_0: bundle_assessment.1,
    }
}

/// Analyze topology for an HDC vector
/// Returns (unity_score, beta_0)
fn analyze_topology(hv: &HV16) -> (f64, usize) {
    let config = TopologyConfig {
        min_persistence: 0.1,
        max_scale: 1.0,
        num_scales: 10,
        detect_cycles: true,
        detect_voids: true,
    };

    let mut topology = ConsciousnessTopology::new(config);

    // Add main vector and permuted variations
    topology.add_state(*hv);
    for shift in 1..5 {
        topology.add_state(hv.permute(shift * 100));
    }

    let assessment = topology.analyze(0.5);
    (assessment.unity_score, assessment.betti.beta_0)
}

/// Compute cell means for 2x2 ANOVA
fn compute_cell_means(results: &[ComparisonResult]) -> CellMeans {
    let unified: Vec<_> = results.iter().filter(|r| r.pair_type == PairType::Unified).collect();
    let separate: Vec<_> = results.iter().filter(|r| r.pair_type == PairType::Separate).collect();

    let bind_unified = mean(unified.iter().map(|r| r.bind_unity));
    let bundle_unified = mean(unified.iter().map(|r| r.bundle_unity));
    let bind_separate = mean(separate.iter().map(|r| r.bind_unity));
    let bundle_separate = mean(separate.iter().map(|r| r.bundle_unity));

    CellMeans {
        bind_unified,
        bind_separate,
        bundle_unified,
        bundle_separate,
        n_unified: unified.len(),
        n_separate: separate.len(),
    }
}

/// Compute mean of an iterator
fn mean<I: Iterator<Item = f64>>(iter: I) -> f64 {
    let values: Vec<f64> = iter.collect();
    if values.is_empty() {
        return 0.0;
    }
    values.iter().sum::<f64>() / values.len() as f64
}

/// Compute variance of a slice
fn compute_variance(values: &[f64]) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    let m = values.iter().sum::<f64>() / values.len() as f64;
    values.iter().map(|x| (x - m).powi(2)).sum::<f64>() / values.len() as f64
}
