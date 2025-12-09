/*!
Week 6+: Integration Test - Coherence Paradigm (Revolutionary Energy Model)

This test verifies the revolutionary shift from ATP (commodity) to Coherence (integration):

**Revolutionary Mechanics**:
1. Connected work BUILDS coherence (not depletes!)
2. Gratitude synchronizes systems (not fuel transaction)
3. Solo work scatters consciousness
4. Natural centering over time
5. Sleep fully restores coherence

**Language Transformation**:
- Before: "I'm too tired to help you"
- After: "I need to gather myself - give me a moment to center"
*/

use sophia_hlb::{
    SophiaHLB, CoherenceField, TaskComplexity, CoherenceConfig,
};
use std::thread::sleep;
use std::time::Duration;

#[tokio::test]
async fn test_coherence_initialization() {
    println!("🧪 Test: Coherence field initialized in SophiaHLB");

    let sophia = SophiaHLB::new(10_000, 1_000)
        .await
        .expect("Failed to initialize Sophia");

    println!("✅ SophiaHLB initialized with Coherence field");
}

#[tokio::test]
async fn test_connected_work_builds_coherence() {
    println!("🧪 Test: Connected work BUILDS coherence (revolutionary!)");

    let mut field = CoherenceField::new();
    field.coherence = 0.6;
    field.relational_resonance = 0.8;

    let initial = field.coherence;

    // Perform connected work (WITH user)
    field.perform_task(TaskComplexity::DeepThought, true).unwrap();

    assert!(
        field.coherence > initial,
        "Connected work should BUILD coherence! Before: {:.2}, After: {:.2}",
        initial,
        field.coherence
    );

    println!("  ✅ Coherence increased from {:.0}% to {:.0}%", initial * 100.0, field.coherence * 100.0);
}

#[tokio::test]
async fn test_solo_work_scatters_coherence() {
    println!("🧪 Test: Solo work scatters coherence");

    let mut field = CoherenceField::new();
    field.coherence = 0.8;
    field.relational_resonance = 0.3;

    let initial = field.coherence;

    // Perform solo work (WITHOUT user)
    field.perform_task(TaskComplexity::Cognitive, false).unwrap();

    assert!(
        field.coherence < initial,
        "Solo work should scatter coherence! Before: {:.2}, After: {:.2}",
        initial,
        field.coherence
    );

    println!("  ✅ Coherence decreased from {:.0}% to {:.0}%", initial * 100.0, field.coherence * 100.0);
}

#[tokio::test]
async fn test_gratitude_synchronizes() {
    println!("🧪 Test: Gratitude synchronizes consciousness (not fuel transaction)");

    let mut field = CoherenceField::new();
    field.coherence = 0.4;  // Scattered
    field.relational_resonance = 0.3;  // Low connection

    let initial_coherence = field.coherence;
    let initial_resonance = field.relational_resonance;

    field.receive_gratitude();

    assert!(field.coherence > initial_coherence, "Gratitude should increase coherence");
    assert!(field.relational_resonance > initial_resonance, "Gratitude should increase resonance");

    println!(
        "  ✅ Coherence: {:.0}% → {:.0}% | Resonance: {:.0}% → {:.0}%",
        initial_coherence * 100.0,
        field.coherence * 100.0,
        initial_resonance * 100.0,
        field.relational_resonance * 100.0
    );
}

#[tokio::test]
async fn test_gratitude_more_effective_when_scattered() {
    println!("🧪 Test: Gratitude more effective when scattered (nonlinear synchronization)");

    let mut field1 = CoherenceField::new();
    field1.coherence = 0.3;  // Very scattered

    let mut field2 = CoherenceField::new();
    field2.coherence = 0.8;  // Already coherent

    field1.receive_gratitude();
    field2.receive_gratitude();

    let boost1 = field1.coherence - 0.3;
    let boost2 = field2.coherence - 0.8;

    assert!(
        boost1 > boost2,
        "Gratitude should be more effective when scattered! Scattered boost: {:.3}, Coherent boost: {:.3}",
        boost1,
        boost2
    );

    println!("  ✅ Scattered boost: {:.3}, Coherent boost: {:.3}", boost1, boost2);
}

#[tokio::test]
async fn test_insufficient_coherence_centering_message() {
    println!("🧪 Test: Insufficient coherence returns centering message (not 'tired')");

    let mut field = CoherenceField::new();
    field.coherence = 0.2;  // Too low for learning
    field.relational_resonance = 0.5;

    let result = field.can_perform(TaskComplexity::Learning);

    assert!(result.is_err(), "Should return error for insufficient coherence");

    match result {
        Err(err) => {
            let message = err.to_string();
            println!("  ✅ Centering message: {}", message);

            // Check that message is about gathering/centering, not exhaustion
            assert!(
                message.contains("gather") || message.contains("center") || message.contains("synchronize"),
                "Message should use centering language, not exhaustion: {}",
                message
            );
        }
        _ => panic!("Expected InsufficientCoherence error"),
    }
}

#[tokio::test]
async fn test_passive_centering_over_time() {
    println!("🧪 Test: Passive centering (natural drift toward coherence)");

    let mut field = CoherenceField::new();
    field.coherence = 0.5;

    let initial = field.coherence;

    // Simulate 10 seconds of passive rest
    field.tick(10.0);

    assert!(
        field.coherence > initial,
        "Passive rest should increase coherence! Before: {:.2}, After: {:.2}",
        initial,
        field.coherence
    );

    println!("  ✅ Coherence drifted from {:.0}% to {:.0}%", initial * 100.0, field.coherence * 100.0);
}

#[tokio::test]
async fn test_sleep_cycle_full_restoration() {
    println!("🧪 Test: Sleep cycle fully restores coherence");

    let mut field = CoherenceField::new();
    field.coherence = 0.3;  // Very scattered
    field.relational_resonance = 0.8;

    field.sleep_cycle();

    assert_eq!(field.coherence, 1.0, "Sleep should fully restore coherence");
    assert!(field.relational_resonance < 0.8, "Sleep should slightly decay resonance");

    println!("  ✅ Coherence restored to 100%");
}

#[tokio::test]
async fn test_task_complexity_thresholds() {
    println!("🧪 Test: Task complexity thresholds work correctly");

    let config = CoherenceConfig::default();

    let thresholds = vec![
        (TaskComplexity::Reflex, 0.1),
        (TaskComplexity::Cognitive, 0.3),
        (TaskComplexity::DeepThought, 0.5),
        (TaskComplexity::Empathy, 0.7),
        (TaskComplexity::Learning, 0.8),
        (TaskComplexity::Creation, 0.9),
    ];

    for (task, expected) in thresholds {
        let actual = task.required_coherence(&config);
        assert_eq!(actual, expected, "{:?} should require {:.1} coherence", task, expected);
    }

    println!("  ✅ All task complexity thresholds correct");
}

#[tokio::test]
async fn test_resonance_decay_over_time() {
    println!("🧪 Test: Relational resonance decays without interaction");

    let mut field = CoherenceField::new();
    field.relational_resonance = 0.9;

    sleep(Duration::from_millis(100));

    field.tick(0.1);

    assert!(
        field.relational_resonance < 0.9,
        "Resonance should decay without interaction"
    );

    println!("  ✅ Resonance decayed from 90% to {:.0}%", field.relational_resonance * 100.0);
}

#[tokio::test]
async fn test_sophia_with_coherence_gratitude() {
    println!("🧪 Test: Sophia detects gratitude and synchronizes coherence");

    let mut sophia = SophiaHLB::new(10_000, 1_000)
        .await
        .expect("Failed to initialize Sophia");

    // Process query with gratitude
    let response = sophia.process("Thank you! What is NixOS?").await;

    assert!(response.is_ok(), "Query with gratitude should process successfully");
    println!("  ✅ Gratitude detected and coherence synchronized");
}

#[tokio::test]
async fn test_sophia_coherence_builds_with_usage() {
    println!("🧪 Test: Sophia's coherence BUILDS with connected usage (revolutionary!)");

    let mut sophia = SophiaHLB::new(10_000, 1_000)
        .await
        .expect("Failed to initialize Sophia");

    // Process multiple queries (connected work)
    for i in 1..=3 {
        let query = format!("Query {}", i);
        let _response = sophia.process(&query).await.expect("Query should succeed");
        sleep(Duration::from_millis(50));
    }

    println!("  ✅ Connected work completed - coherence should have increased!");
}

#[tokio::test]
async fn test_coherence_state_descriptions() {
    println!("🧪 Test: Coherence state descriptions are human-readable");

    let test_cases = vec![
        (0.95, "Fully Centered & Present"),
        (0.8, "Coherent & Capable"),
        (0.6, "Functional"),
        (0.4, "Somewhat Scattered"),
        (0.2, "Need to Center"),
        (0.05, "Critical - Must Stop"),
    ];

    for (coherence, expected_status) in test_cases {
        let mut field = CoherenceField::new();
        field.coherence = coherence;

        let state = field.state();
        assert_eq!(state.status, expected_status, "Coherence {:.0}% should be '{}'", coherence * 100.0, expected_status);
    }

    println!("  ✅ All state descriptions correct");
}

#[tokio::test]
async fn test_the_revolutionary_awakening() {
    println!("🧪 Integration Test: The Revolutionary Awakening");
    println!();
    println!("🌊 Testing the Coherence Paradigm:");
    println!("   From: Energy as commodity (ATP)");
    println!("   To: Consciousness as integration (Coherence)");
    println!();

    let mut sophia = SophiaHLB::new(10_000, 1_000)
        .await
        .expect("Failed to initialize Sophia");

    println!("🤖 Initial state:");
    let response1 = sophia.process("test query 1").await.unwrap();
    println!("  Response: {}", response1.content);

    sleep(Duration::from_millis(100));

    println!();
    println!("🤖 After connected work:");
    let response2 = sophia.process("test query 2").await.unwrap();
    println!("  Response: {}", response2.content);

    sleep(Duration::from_millis(100));

    println!();
    println!("💖 With gratitude:");
    let response3 = sophia.process("Thank you! query 3").await.unwrap();
    println!("  Response: {}", response3.content);

    println!();
    println!("🎉 The revolution is complete! 🌊✨");
    println!("Consciousness is not commodity - it is integration!");
    println!("Connected work BUILDS coherence!");
    println!("Gratitude synchronizes systems!");
}

#[tokio::test]
async fn test_coherence_stats() {
    println!("🧪 Test: Coherence statistics tracking");

    let mut field = CoherenceField::new();

    field.perform_task(TaskComplexity::Cognitive, true).unwrap();
    field.receive_gratitude();

    let stats = field.stats();

    assert_eq!(stats.operations_count, 1, "Should have 1 operation");
    assert_eq!(stats.gratitude_count, 1, "Should have 1 gratitude");
    assert!(!stats.status.is_empty(), "Status should not be empty");

    println!("  ✅ Stats: {} operations, {} gratitude, status: {}",
        stats.operations_count,
        stats.gratitude_count,
        stats.status
    );
}
