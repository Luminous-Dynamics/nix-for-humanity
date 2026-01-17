//! Standard Benchmark Suite
//!
//! Main benchmark suite (~30 min) covering core capabilities.
//! Reference: BENCHMARKING_STRATEGY.md Section 36
//!
//! ## Included Benchmarks
//!
//! - HDC operations (comprehensive)
//! - Φ on 8 standard topologies
//! - Temporal reasoning
//! - Scalability tests
//!
//! ## Usage
//!
//! ```bash
//! cargo bench --bench standard
//! ```

use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};
use symthaea::hdc::{
    consciousness_topology_generators::ConsciousnessTopology,
    phi_real::RealPhiCalculator,
    phi_resonant::ResonantPhiCalculator,
    HV16, HDC_DIMENSION,
};
use symthaea::consciousness::temporal_primitives::{
    TemporalReasoner, TemporalInterval, AllenRelation, TemporalConfig,
};

// =============================================================================
// HDC COMPREHENSIVE
// =============================================================================

fn bench_hdc_comprehensive(c: &mut Criterion) {
    let mut group = c.benchmark_group("std_hdc");
    group.sample_size(100);

    let hv1 = HV16::random(42);
    let hv2 = HV16::random(43);

    // All core operations
    group.bench_function("bind", |b| {
        b.iter(|| black_box(hv1.bind(&hv2)))
    });

    group.bench_function("similarity", |b| {
        b.iter(|| black_box(hv1.similarity(&hv2)))
    });

    group.bench_function("hamming_distance", |b| {
        b.iter(|| black_box(hv1.hamming_distance(&hv2)))
    });

    group.bench_function("popcount", |b| {
        b.iter(|| black_box(hv1.popcount()))
    });

    // Bundle scaling
    for size in [2, 5, 10, 20] {
        let hvs: Vec<HV16> = (0..size).map(|i| HV16::random(i)).collect();
        group.bench_with_input(
            BenchmarkId::new("bundle", size),
            &hvs,
            |b, hvs| b.iter(|| black_box(HV16::bundle(hvs))),
        );
    }

    // Permute scaling
    for steps in [1, 10, 100] {
        group.bench_with_input(
            BenchmarkId::new("permute", steps),
            &steps,
            |b, &steps| b.iter(|| black_box(hv1.permute(steps))),
        );
    }

    group.finish();
}

// =============================================================================
// STANDARD TOPOLOGIES (8)
// =============================================================================

fn bench_standard_topologies(c: &mut Criterion) {
    let mut group = c.benchmark_group("std_topologies");
    group.sample_size(50);

    let calc = RealPhiCalculator::new();

    let topologies = vec![
        ("Ring", ConsciousnessTopology::ring(8, HDC_DIMENSION, 42)),
        ("Torus", ConsciousnessTopology::torus(3, 3, HDC_DIMENSION, 42)),
        ("Dense", ConsciousnessTopology::dense_network(8, HDC_DIMENSION, None, 42)),
        ("Lattice", ConsciousnessTopology::lattice(8, HDC_DIMENSION, 42)),
        ("Modular", ConsciousnessTopology::modular(8, HDC_DIMENSION, 2, 42)),
        ("Line", ConsciousnessTopology::line(8, HDC_DIMENSION, 42)),
        ("Star", ConsciousnessTopology::star(8, HDC_DIMENSION, 42)),
        ("Random", ConsciousnessTopology::random(8, HDC_DIMENSION, 42)),
    ];

    for (name, topo) in topologies {
        group.bench_function(name, |b| {
            b.iter(|| black_box(calc.compute(&topo.node_representations)))
        });
    }

    group.finish();
}

// =============================================================================
// TEMPORAL REASONING
// =============================================================================

fn bench_temporal_reasoning(c: &mut Criterion) {
    let mut group = c.benchmark_group("std_temporal");
    group.sample_size(100);

    let config = TemporalConfig::default();
    let reasoner = TemporalReasoner::new(config.clone());

    let interval_a = TemporalInterval::new("A", 0.0, 1.0).unwrap();
    let interval_b = TemporalInterval::new("B", 1.5, 2.5).unwrap();

    group.bench_function("compute_relation", |b| {
        b.iter(|| black_box(reasoner.compute_relation(&interval_a, &interval_b)))
    });

    group.bench_function("compose_relations", |b| {
        b.iter(|| black_box(reasoner.compose(AllenRelation::Precedes, AllenRelation::Precedes)))
    });

    group.bench_function("encode_relation", |b| {
        b.iter(|| black_box(reasoner.encode_relation(AllenRelation::Overlaps)))
    });

    group.bench_function("encode_statement", |b| {
        b.iter(|| black_box(reasoner.encode_statement(&interval_a, AllenRelation::Precedes, &interval_b)))
    });

    group.finish();
}

// =============================================================================
// SCALABILITY
// =============================================================================

fn bench_scalability(c: &mut Criterion) {
    let mut group = c.benchmark_group("std_scalability");
    group.sample_size(20);

    // HV16 search scalability
    let query = HV16::random(42);

    for size in [100, 1000, 5000] {
        let corpus: Vec<HV16> = (0..size).map(|i| HV16::random(i as u64)).collect();
        group.throughput(Throughput::Elements(size as u64));

        group.bench_with_input(
            BenchmarkId::new("linear_search", size),
            &corpus,
            |b, corpus| {
                b.iter(|| {
                    let max_sim = corpus.iter()
                        .map(|hv| query.similarity(hv))
                        .max_by(|a, b| a.partial_cmp(b).unwrap());
                    black_box(max_sim)
                })
            },
        );
    }

    // Φ scaling
    let calc = ResonantPhiCalculator::fast();
    for n_nodes in [8, 16, 32] {
        group.bench_with_input(
            BenchmarkId::new("phi_ring", n_nodes),
            &n_nodes,
            |b, &n| {
                let topo = ConsciousnessTopology::ring(n, HDC_DIMENSION, 42);
                b.iter(|| black_box(calc.compute(&topo.node_representations)))
            },
        );
    }

    group.finish();
}

// =============================================================================
// HYPERCUBE DIMENSION SCALING
// =============================================================================

fn bench_hypercube_scaling(c: &mut Criterion) {
    let mut group = c.benchmark_group("std_hypercube");
    group.sample_size(30);

    let calc = RealPhiCalculator::new();

    for dim in 3..=5 {
        let n_nodes = 1 << dim;
        group.throughput(Throughput::Elements(n_nodes as u64));

        group.bench_with_input(
            BenchmarkId::new("dimension", format!("{}D", dim)),
            &dim,
            |b, &d| {
                let topo = ConsciousnessTopology::hypercube(d, HDC_DIMENSION, 42);
                b.iter(|| black_box(calc.compute(&topo.node_representations)))
            },
        );
    }

    group.finish();
}

// =============================================================================
// CRITERION CONFIGURATION
// =============================================================================

criterion_group!(
    standard_benches,
    bench_hdc_comprehensive,
    bench_standard_topologies,
    bench_temporal_reasoning,
    bench_scalability,
    bench_hypercube_scaling,
);

criterion_main!(standard_benches);
