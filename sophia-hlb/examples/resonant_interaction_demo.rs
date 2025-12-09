// Resonant Interaction Demo - v0.2
//
// Demonstrates UserState inference + Resonant Speech integration
// Shows how the system adapts voice based on observable context

use sophia_hlb::resonant_speech::SimpleResonantEngine;
use sophia_hlb::resonant_interaction::{
    InteractionContext, advise_and_speak, handle_mode_command,
};
use sophia_hlb::user_state_inference::{ContextKind, RecentEvents, UserStateInference};
use std::time::Duration;

fn main() {
    println!("🌊 Sophia Resonant Interaction Demo - v0.2\n");
    println!("Demonstrating UserState inference + adaptive voice\n");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let engine = SimpleResonantEngine::new();

    // Demo 1: Panic mode (error burst triggers High cognitive load)
    demo_panic_mode(&engine);

    // Demo 2: Calm focus (long session triggers Low cognitive load)
    demo_calm_focus(&engine);

    // Demo 3: Explicit mode switching
    demo_mode_switching(&engine);

    // Demo 4: Urgency hint detection
    demo_urgency_detection(&engine);

    // Demo 5: Context-based temporal frame inference
    demo_context_inference(&engine);
}

fn demo_panic_mode(engine: &SimpleResonantEngine) {
    println!("📋 Demo 1: Panic Mode (Error Burst → High Cognitive Load)\n");

    // Simulate error burst scenario
    let mut events = RecentEvents::new();
    events.errors_last_5m = 5; // Multiple errors recently
    events.undos_last_10m = 3; // Thrashing
    events.session_duration = Duration::from_secs(10 * 60); // 10 minutes

    let inference = UserStateInference::with_events(events);

    let mut context = InteractionContext::new(ContextKind::ErrorHandling);
    context.user_state_inference = inference;

    let query = "fix this boot failure now!";
    let utterance = advise_and_speak(query, &mut context, engine).unwrap();

    println!("Query: \"{}\"\n", query);
    println!("Inferred State:");
    println!("  - Cognitive Load: High (5 errors in 5 min)");
    println!("  - Context: ErrorHandling → Micro temporal frame");
    println!("  - Urgency: Detected from 'now!'\n");

    println!("Utterance:\n{}\n", utterance.text);
    println!("Tags: {:?}\n", utterance.tags);
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_calm_focus(engine: &SimpleResonantEngine) {
    println!("📋 Demo 2: Calm Focus (Long Session → Low Cognitive Load)\n");

    // Simulate calm, focused session
    let mut events = RecentEvents::new();
    events.session_duration = Duration::from_secs(45 * 60); // 45 minutes
    events.time_since_last_command = Duration::from_secs(120); // 2 min idle
    events.errors_last_5m = 0; // No errors
    events.suggestions_accepted = 12; // High trust
    events.suggestions_rejected = 2;

    let inference = UserStateInference::with_events(events);

    let mut context = InteractionContext::new(ContextKind::Review);
    context.user_state_inference = inference;

    let query = "show me my knowledge actualization progress";
    let utterance = advise_and_speak(query, &mut context, engine).unwrap();

    println!("Query: \"{}\"\n", query);
    println!("Inferred State:");
    println!("  - Cognitive Load: Low (calm 45min session)");
    println!("  - Trust: 0.82 (12 accepts / 2 rejects)");
    println!("  - Context: Review → Macro temporal frame\n");

    println!("Utterance:\n{}\n", utterance.text);
    println!("Tags: {:?}\n", utterance.tags);
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_mode_switching(engine: &SimpleResonantEngine) {
    println!("📋 Demo 3: Explicit Mode Switching\n");

    let mut context = InteractionContext::new(ContextKind::DevWork);

    // User types "/mode coach"
    println!("User types: /mode coach\n");
    let response = handle_mode_command(&mut context, "/mode coach");
    println!("System: {}\n", response.unwrap());

    let query = "help me think through this architecture decision";
    let utterance = advise_and_speak(query, &mut context, engine).unwrap();

    println!("Query: \"{}\"\n", query);
    println!("Active Mode: Coach (explicitly set)\n");
    println!("Utterance:\n{}\n", utterance.text);
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_urgency_detection(engine: &SimpleResonantEngine) {
    println!("📋 Demo 4: Urgency Hint Detection\n");

    let mut context = InteractionContext::new(ContextKind::DevWork);

    // Query with urgency markers
    let query = "urgent: production is down, need rollback now!";

    println!("Query: \"{}\"\n", query);
    context.extract_urgency_hint(query);
    println!("Detected urgency from keywords: 'urgent', 'now'\n");

    let utterance = advise_and_speak(query, &mut context, engine).unwrap();

    println!("Utterance adapts to urgency:\n{}\n", utterance.text);
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_context_inference(engine: &SimpleResonantEngine) {
    println!("📋 Demo 5: Context-Based Temporal Frame Inference\n");

    // Different contexts infer different temporal frames
    let contexts = vec![
        (ContextKind::ErrorHandling, "Micro"),
        (ContextKind::DevWork, "Meso"),
        (ContextKind::Planning, "Macro"),
    ];

    for (kind, expected_frame) in contexts {
        let context = InteractionContext::new(kind);
        println!("{:?} → TemporalFrame::{}", kind, expected_frame);
    }

    println!("\nThis means:");
    println!("  - ErrorHandling gets terse, action-first voice (Micro)");
    println!("  - DevWork gets collaborative, arc-aware voice (Meso)");
    println!("  - Planning gets zoomed-out, reflective voice (Macro)\n");

    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    // Show example of Planning context
    let mut context = InteractionContext::new(ContextKind::Planning);
    let query = "what should we focus on for Q2?";

    let utterance = advise_and_speak(query, &mut context, engine).unwrap();

    println!("Planning query: \"{}\"\n", query);
    println!("Macro-framed response:\n{}\n", utterance.text);
}
