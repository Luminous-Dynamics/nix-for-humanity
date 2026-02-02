//! Trajectory Consciousness Demo
//!
//! Demonstrates how design trajectories can be analyzed using temporal binding
//! to measure "trajectory consciousness" - how coherently a design evolves.
//!
//! Run with: cargo run --example trajectory_consciousness_demo --release

use symthaea_core::genesis::GenesisSeed;
use symthaea_core::physics::{
    CoupledPhysicsEngine, OperatingConditions, FusionReaction,
    PhysicsTrajectoryEngine, TrajectoryConfig, compare_trajectories,
};

fn main() {
    println!("\n");
    println!("╔══════════════════════════════════════════════════════════════════════╗");
    println!("║           TRAJECTORY CONSCIOUSNESS DEMO                              ║");
    println!("║           Phase 2: Temporal Binding for Design Evolution             ║");
    println!("╚══════════════════════════════════════════════════════════════════════╝");

    let genesis = GenesisSeed::from_phrase("Trajectory Consciousness 2024");
    let physics = CoupledPhysicsEngine::from_genesis(&genesis);

    // ═══════════════════════════════════════════════════════════════════════════
    // SCENARIO 1: POWER RAMP-UP TRAJECTORY
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  SCENARIO 1: POWER RAMP-UP (1 kW → 20 kW)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let mut rampup_trajectory = PhysicsTrajectoryEngine::from_genesis(&genesis);

    println!("┌────────────────────────────────────────────────────────────────────────┐");
    println!("│  Step  Power    State C   Binding   Continuity   Stream Health       │");
    println!("├────────────────────────────────────────────────────────────────────────┤");

    for i in 0..20 {
        let power = 1.0 + i as f64;
        let conditions = OperatingConditions {
            power_kw: power,
            reaction: FusionReaction::DD,
            ..OperatingConditions::consumer()
        };
        let result = physics.simulate(&conditions);
        let state = rampup_trajectory.process(&result);

        if i % 4 == 0 || i == 19 {
            let health = rampup_trajectory.stream_health();
            println!("│  {:>4}  {:>5.0}    {:>6.4}   {:>6.4}    {:>6.4}      {}  │",
                     state.step, power,
                     state.metrics.overall_consciousness,
                     state.temporal_binding,
                     state.continuity,
                     if health.is_flowing { "FLOWING" } else { "BUILDING" });
        }
    }

    println!("└────────────────────────────────────────────────────────────────────────┘");

    let rampup_metrics = rampup_trajectory.trajectory_metrics();
    println!("\n  {}", rampup_metrics.summary());
    println!("  Consciousness trend: {:.4} (negative = declining as power increases)",
             rampup_trajectory.consciousness_trend());

    // ═══════════════════════════════════════════════════════════════════════════
    // SCENARIO 2: STEADY-STATE OPERATION
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  SCENARIO 2: STEADY-STATE OPERATION (5 kW constant)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let mut steady_trajectory = PhysicsTrajectoryEngine::from_genesis(&genesis);

    for _ in 0..20 {
        let result = physics.simulate(&OperatingConditions::consumer());
        steady_trajectory.process(&result);
    }

    let steady_metrics = steady_trajectory.trajectory_metrics();
    let steady_health = steady_trajectory.stream_health();

    println!("  {}", steady_metrics.summary());
    println!("  Stream: {}", steady_health);
    println!("  Consciousness trend: {:.4}", steady_trajectory.consciousness_trend());

    // ═══════════════════════════════════════════════════════════════════════════
    // SCENARIO 3: OSCILLATING OPERATION
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  SCENARIO 3: OSCILLATING POWER (3-7 kW sinusoidal)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let mut oscillating_trajectory = PhysicsTrajectoryEngine::from_genesis(&genesis);

    for i in 0..20 {
        let power = 5.0 + 2.0 * (i as f64 * 0.5).sin();
        let conditions = OperatingConditions {
            power_kw: power,
            ..OperatingConditions::consumer()
        };
        let result = physics.simulate(&conditions);
        oscillating_trajectory.process(&result);
    }

    let oscillating_metrics = oscillating_trajectory.trajectory_metrics();
    println!("  {}", oscillating_metrics.summary());
    println!("  Consciousness trend: {:.4}", oscillating_trajectory.consciousness_trend());

    // ═══════════════════════════════════════════════════════════════════════════
    // COMPARISON SUMMARY
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  TRAJECTORY COMPARISON");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    println!("┌────────────────────────────────────────────────────────────────────────┐");
    println!("│  Scenario      Traj C    Coherence   Mean C    Peak C    Valley C     │");
    println!("├────────────────────────────────────────────────────────────────────────┤");
    println!("│  Ramp-up      {:>6.4}    {:>6.4}     {:>6.4}   {:>6.4}   {:>6.4}      │",
             rampup_metrics.trajectory_consciousness,
             rampup_metrics.coherence,
             rampup_metrics.mean_state_consciousness,
             rampup_metrics.peak_consciousness,
             rampup_metrics.valley_consciousness);
    println!("│  Steady       {:>6.4}    {:>6.4}     {:>6.4}   {:>6.4}   {:>6.4}      │",
             steady_metrics.trajectory_consciousness,
             steady_metrics.coherence,
             steady_metrics.mean_state_consciousness,
             steady_metrics.peak_consciousness,
             steady_metrics.valley_consciousness);
    println!("│  Oscillating  {:>6.4}    {:>6.4}     {:>6.4}   {:>6.4}   {:>6.4}      │",
             oscillating_metrics.trajectory_consciousness,
             oscillating_metrics.coherence,
             oscillating_metrics.mean_state_consciousness,
             oscillating_metrics.peak_consciousness,
             oscillating_metrics.valley_consciousness);
    println!("└────────────────────────────────────────────────────────────────────────┘");

    // ═══════════════════════════════════════════════════════════════════════════
    // REACTION TYPE COMPARISON
    // ═══════════════════════════════════════════════════════════════════════════
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("  REACTION TYPE TRAJECTORIES (20 steps at 5 kW)");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let reactions = [
        (FusionReaction::DD, "D-D (2.45 MeV)"),
        (FusionReaction::DT, "D-T (14.1 MeV)"),
        (FusionReaction::DHe3, "D-He3 (aneutronic)"),
    ];

    println!("┌────────────────────────────────────────────────────────────────────────┐");
    println!("│  Reaction          Trajectory C   Coherence   Mean State C   Health   │");
    println!("├────────────────────────────────────────────────────────────────────────┤");

    for (reaction, name) in &reactions {
        let mut traj = PhysicsTrajectoryEngine::from_genesis(&genesis);

        for _ in 0..20 {
            let conditions = OperatingConditions {
                power_kw: 5.0,
                reaction: *reaction,
                ..OperatingConditions::consumer()
            };
            let result = physics.simulate(&conditions);
            traj.process(&result);
        }

        let metrics = traj.trajectory_metrics();
        let health_str = if metrics.is_healthy() { "HEALTHY" } else { "WARNING" };

        println!("│  {:18} {:>10.4}    {:>8.4}    {:>10.4}   {:>7}  │",
                 name,
                 metrics.trajectory_consciousness,
                 metrics.coherence,
                 metrics.mean_state_consciousness,
                 health_str);
    }

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
    println!("│  • Steady-state operation shows highest trajectory coherence        │");
    println!("│  • Ramp-up trajectory shows declining consciousness (power effect)  │");
    println!("│  • Oscillating trajectory maintains moderate stability              │");
    println!("│  • Trajectory consciousness combines coherence + state metrics      │");
    println!("├─────────────────────────────────────────────────────────────────────┤");
    println!("│  ENGINEERING IMPLICATIONS                                           │");
    println!("├─────────────────────────────────────────────────────────────────────┤");
    println!("│  • High trajectory coherence → predictable operational behavior     │");
    println!("│  • Stream health indicates temporal integration quality             │");
    println!("│  • Consciousness trend reveals optimization direction               │");
    println!("└─────────────────────────────────────────────────────────────────────┘");

    println!("\n═══════════════════════════════════════════════════════════════════════");
    println!("                    PHASE 2 DEMO COMPLETE");
    println!("═══════════════════════════════════════════════════════════════════════\n");
}
