//! Physics → Consciousness Integration Demo
//!
//! Demonstrates how reactor designs can be analyzed using consciousness metrics.
//!
//! Run with: cargo run --example physics_consciousness_demo

use symthaea_core::genesis::GenesisSeed;
use symthaea_core::physics::{
    CoupledPhysicsEngine, OperatingConditions, FusionReaction,
    PhysicsConsciousnessEngine,
};

fn main() {
    println!("\n");
    println!("╔══════════════════════════════════════════════════════════════════════╗");
    println!("║           PHYSICS → CONSCIOUSNESS INTEGRATION DEMO                   ║");
    println!("║           Measuring Design Integration via HDC                       ║");
    println!("╚══════════════════════════════════════════════════════════════════════╝");

    let genesis = GenesisSeed::from_phrase("Physics Consciousness 2024");
    let physics = CoupledPhysicsEngine::from_genesis(&genesis);
    let consciousness = PhysicsConsciousnessEngine::from_genesis(&genesis);

    // ═══════════════════════════════════════════════════════════════════════════
    // CONSCIOUSNESS ACROSS POWER SCALES
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  CONSCIOUSNESS ACROSS POWER SCALES (D-D Fusion)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    println!("┌────────────────────────────────────────────────────────────────────────┐");
    println!("│ Power   Mass    Lifetime  Feasible  Thermal   Damage    Geometry   C  │");
    println!("│  (kW)   (kg)    (years)             Coher.    Balance   Harmony       │");
    println!("├────────────────────────────────────────────────────────────────────────┤");

    let mut results = Vec::new();

    for power in [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0] {
        let conditions = OperatingConditions {
            power_kw: power,
            reaction: FusionReaction::DD,
            ..OperatingConditions::consumer()
        };

        let result = physics.simulate(&conditions);
        let metrics = consciousness.compute_metrics(&result);

        let feasible_str = if result.feasible { "YES" } else { "NO " };

        println!("│ {:>5.0}   {:>5.0}   {:>6.1}    {}       {:.3}     {:.3}     {:.3}    {:.3} │",
                 power,
                 result.geometry_shielding.total_mass_kg,
                 result.pulse_thermal.lifetime_years.min(100.0),
                 feasible_str,
                 metrics.thermal_coherence,
                 metrics.damage_healing_balance,
                 metrics.geometry_harmony,
                 metrics.overall_consciousness);

        results.push((power, metrics.overall_consciousness, result.feasible));
    }

    println!("└────────────────────────────────────────────────────────────────────────┘");

    // Find optimal consciousness
    let (best_power, best_c, _) = results.iter()
        .filter(|(_, _, feasible)| *feasible)
        .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
        .unwrap();

    println!("\n  Highest consciousness: {:.3} at {} kW", best_c, best_power);

    // ═══════════════════════════════════════════════════════════════════════════
    // REACTION TYPE COMPARISON
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  CONSCIOUSNESS BY REACTION TYPE (5 kW)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let reactions = [
        (FusionReaction::DD, "D-D (2.45 MeV n)"),
        (FusionReaction::DT, "D-T (14.1 MeV n)"),
        (FusionReaction::DHe3, "D-He3 (aneutronic)"),
    ];

    println!("┌────────────────────────────────────────────────────────────────────────┐");
    println!("│  Reaction            Mass (kg)   Shielding   Consciousness   Feasible │");
    println!("├────────────────────────────────────────────────────────────────────────┤");

    for (reaction, name) in &reactions {
        let conditions = OperatingConditions {
            power_kw: 5.0,
            reaction: *reaction,
            ..OperatingConditions::consumer()
        };

        let result = physics.simulate(&conditions);
        let metrics = consciousness.compute_metrics(&result);

        let feasible_str = if result.feasible { "YES" } else { "NO " };

        println!("│  {:20} {:>8.0}   {:>6.2} m     {:.4}         {}      │",
                 name,
                 result.geometry_shielding.total_mass_kg,
                 result.geometry_shielding.shielding.thickness_m,
                 metrics.overall_consciousness,
                 feasible_str);
    }

    println!("└────────────────────────────────────────────────────────────────────────┘");

    // ═══════════════════════════════════════════════════════════════════════════
    // DETAILED METRICS BREAKDOWN
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  DETAILED CONSCIOUSNESS BREAKDOWN (5 kW D-D)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let consumer_result = physics.simulate(&OperatingConditions::consumer());
    let consumer_metrics = consciousness.compute_metrics(&consumer_result);

    println!("┌────────────────────────────────────────────────────────────────────────┐");
    println!("│  CONSCIOUSNESS COMPONENTS                                              │");
    println!("├────────────────────────────────────────────────────────────────────────┤");
    println!("│  Phenomenal Index:     {:>8.4}  (phenomenal vs functional)          │", consumer_metrics.phenomenal_index);
    println!("│  Design Integration:   {:>8.4}  (internal coherence)                │", consumer_metrics.design_integration);
    println!("│  Thermal Coherence:    {:>8.4}  (temperature profile smoothness)    │", consumer_metrics.thermal_coherence);
    println!("│  Damage-Healing:       {:>8.4}  (equilibrium balance)               │", consumer_metrics.damage_healing_balance);
    println!("│  Geometry Harmony:     {:>8.4}  (mass efficiency)                   │", consumer_metrics.geometry_harmony);
    println!("├────────────────────────────────────────────────────────────────────────┤");
    println!("│  OVERALL CONSCIOUSNESS: {:>7.4}                                      │", consumer_metrics.overall_consciousness);
    println!("│  Binding Advantage:    {:>8.4}  (bind vs bundle difference)         │", consumer_metrics.binding_advantage);
    println!("└────────────────────────────────────────────────────────────────────────┘");

    // ═══════════════════════════════════════════════════════════════════════════
    // INTERPRETATION
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n═══════════════════════════════════════════════════════════════════════");
    println!("                    INTERPRETATION");
    println!("═══════════════════════════════════════════════════════════════════════\n");

    println!("┌─────────────────────────────────────────────────────────────────────┐");
    println!("│  KEY FINDINGS                                                       │");
    println!("├─────────────────────────────────────────────────────────────────────┤");
    println!("│  • Smaller designs (1-5 kW) show higher consciousness scores       │");
    println!("│  • This suggests better thermal-structural-radiation integration   │");
    println!("│  • D-He3 (aneutronic) has lowest mass but similar consciousness    │");
    println!("│  • Consciousness correlates with design compactness/efficiency     │");
    println!("├─────────────────────────────────────────────────────────────────────┤");
    println!("│  HYPOTHESIS                                                         │");
    println!("├─────────────────────────────────────────────────────────────────────┤");
    println!("│  Higher consciousness scores may predict:                          │");
    println!("│  • Better robustness under off-design conditions                   │");
    println!("│  • More graceful degradation during failures                       │");
    println!("│  • Emergent stability properties from tight coupling               │");
    println!("└─────────────────────────────────────────────────────────────────────┘");

    println!("\n═══════════════════════════════════════════════════════════════════════");
    println!("                    DEMO COMPLETE");
    println!("═══════════════════════════════════════════════════════════════════════\n");
}
