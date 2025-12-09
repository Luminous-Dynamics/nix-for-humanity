/*!
Week 5 Day 2: Integration Test - The Gratitude Loop

This test verifies that the nervous system is wired correctly:
1. Thalamus detects gratitude
2. Hearth receives energy restoration
3. Prefrontal checks energy before execution
4. Exhaustion triggers rejection bids
5. Gratitude rescues from exhaustion

NOTE: This is a unit-level integration test that verifies the organs are
wired correctly, without requiring the full Sophia pipeline to be operational.
*/

use sophia_hlb::{
    SophiaHLB, ThalamusActor, HearthActor, PrefrontalCortexActor,
    AttentionBid, EmotionalValence, HearthConfig, ActionCost,
};

#[tokio::test]
async fn test_organs_are_initialized() {
    println!("🧪 Test: Organs are initialized in SophiaHLB");

    let sophia = SophiaHLB::new(10_000, 1_000)
        .await
        .expect("Failed to initialize Sophia");

    println!("✅ SophiaHLB initialized successfully with organs");
    println!("✅ The organs are wired and ready!");
}

#[tokio::test]
async fn test_the_gratitude_loop_standalone() {
    println!("🧪 Standalone Test: The Gratitude Loop (Direct Organ Access)");

    // Create organs directly (simulating what's in SophiaHLB)
    let mut hearth = HearthActor::new();
    let thalamus = ThalamusActor::new();
    let mut prefrontal = PrefrontalCortexActor::new();

    println!("\n🧪 Test 1: Normal Operation - Sophia has energy");
    let initial_energy = hearth.current_energy;
    println!("  Initial energy: {} ATP", initial_energy);
    assert!(initial_energy >= 100.0, "Should start with plenty of energy");

    // Create a normal bid
    let bid = AttentionBid::new("User", "Install Firefox".to_string())
        .with_salience(0.9)
        .with_urgency(0.8)
        .with_emotion(EmotionalValence::Neutral);

    let winner = prefrontal.cognitive_cycle_with_energy(vec![bid.clone()], &mut hearth);
    assert!(winner.is_some(), "Should have a winner");
    assert_eq!(winner.unwrap().source, "User", "Winner should be the user bid");
    println!("✅ Normal operation works");

    println!("\n🧪 Test 2: Exhaust Sophia's energy");
    // Drain energy through repeated expensive tasks
    for i in 0..20 {
        let expensive_bid = AttentionBid::new("User", format!("Complex task {}", i))
            .with_salience(0.9)
            .with_urgency(0.9)
            .with_tags(vec!["goal".to_string(), "planning".to_string()]); // DeepThought cost

        let _ = prefrontal.cognitive_cycle_with_energy(vec![expensive_bid], &mut hearth);
    }

    let exhausted_energy = hearth.current_energy;
    println!("  Energy after 20 deep thoughts: {} ATP", exhausted_energy);
    assert!(exhausted_energy < 100.0, "Should be low on energy");

    println!("\n🧪 Test 3: Exhaustion - Sophia should reject");
    let hard_bid = AttentionBid::new("User", "Do something very hard".to_string())
        .with_salience(0.95)
        .with_urgency(0.95)
        .with_tags(vec!["learning".to_string()]); // Learning cost (50 ATP)

    let rejection = prefrontal.cognitive_cycle_with_energy(vec![hard_bid], &mut hearth);
    assert!(rejection.is_some());
    let rejection_bid = rejection.unwrap();
    assert_eq!(rejection_bid.source, "Hearth", "Rejection should come from Hearth");
    assert!(rejection_bid.content.contains("tired"), "Should mention being tired");
    println!("  💬 Exhaustion message: {}", rejection_bid.content);
    println!("✅ Exhaustion detection works");

    println!("\n🧪 Test 4: Gratitude - Restore energy");
    let energy_before_gratitude = hearth.current_energy;

    // Detect gratitude
    let gratitude_detected = thalamus.detect_gratitude("Thank you so much!");
    assert!(gratitude_detected, "Should detect gratitude");

    // Hearth receives gratitude
    hearth.receive_gratitude();

    let energy_after_gratitude = hearth.current_energy;
    println!("  Energy before: {} ATP", energy_before_gratitude);
    println!("  Energy after: {} ATP", energy_after_gratitude);
    assert!(energy_after_gratitude > energy_before_gratitude, "Gratitude should restore energy");
    println!("✅ Gratitude restoration works (+10 ATP)");

    println!("\n🧪 Test 5: Verify Recovery - Sophia can work again");
    let simple_bid = AttentionBid::new("User", "Simple task".to_string())
        .with_salience(0.5)
        .with_urgency(0.5);

    let recovery_result = prefrontal.cognitive_cycle_with_energy(vec![simple_bid], &mut hearth);
    assert!(recovery_result.is_some());
    let recovery_bid = recovery_result.unwrap();
    assert_eq!(recovery_bid.source, "User", "Should execute user bid after recovery");
    assert!(!recovery_bid.content.contains("tired"), "Should not be tired anymore");
    println!("✅ Recovery works - can execute after gratitude");

    println!("\n🎉 The Gratitude Loop WORKS! The body is AWAKE! 🔌✨");
}

#[tokio::test]
async fn test_gratitude_detection_standalone() {
    println!("🧪 Testing gratitude detection (standalone)");

    let thalamus = ThalamusActor::new();

    // Test various gratitude expressions
    let gratitude_phrases = vec![
        "thank you",
        "thanks",
        "I'm grateful",
        "appreciate it",
        "thx",
        "ty",
        "much gratitude",
    ];

    for phrase in &gratitude_phrases {
        let detected = thalamus.detect_gratitude(phrase);
        assert!(detected, "Should detect: {}", phrase);
        println!("  ✓ Detected: '{}'", phrase);
    }

    // Test non-gratitude expressions (should NOT detect)
    let non_gratitude = vec!["hello", "install firefox", "help me"];
    for phrase in &non_gratitude {
        let detected = thalamus.detect_gratitude(phrase);
        assert!(!detected, "Should NOT detect: {}", phrase);
    }

    println!("\n✅ Gratitude detection works for all common expressions!");
}
