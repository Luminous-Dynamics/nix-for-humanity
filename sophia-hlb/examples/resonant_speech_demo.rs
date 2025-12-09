// Resonant Speech Engine Demo
//
// Demonstrates all 5 v0.1 templates in action

use sophia_hlb::resonant_speech::*;
use uuid::Uuid;

fn main() {
    println!("🌊 Sophia Resonant Speech Engine - v0.1 Demo\n");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let engine = SimpleResonantEngine::new();

    // Demo 1: Urgent fix (Technician + Micro + High load)
    demo_urgent_fix(&engine);

    // Demo 2: Project work (CoAuthor + Meso + Medium load)
    demo_project_work(&engine);

    // Demo 3: Reflection (Coach + Macro + Low load)
    demo_reflection(&engine);

    // Demo 4: Controversial suggestion
    demo_controversial(&engine);

    // Demo 5: Governance decision
    demo_governance(&engine);

    // Demo 6: Voice channel adaptation
    demo_voice_channel(&engine);
}

fn demo_urgent_fix(engine: &SimpleResonantEngine) {
    println!("📋 Demo 1: Urgent Fix (Technician + Micro + High Load)\n");

    let ctx = ResonantContext {
        user_state: UserState {
            cognitive_load: CognitiveLoad::High,
            trust_in_sophia: 0.5,
            locale: "en-US".to_string(),
        },
        relationship: RelationshipProfile {
            primary: RelationshipMode::Technician,
            secondary: None,
            weight_primary: 1.0,
        },
        temporal_frame: TemporalFrame::Micro,
        suggestion_decision: SuggestionDecision {
            kind: SuggestionDecisionKind::AutoApply,
            reason: "High confidence fix".to_string(),
            claim_id: Some(Uuid::new_v4()),
        },
        channel: OutputChannel::Terminal,
        action_summary: "Regenerate your NixOS hardware config and rebuild".to_string(),
        reason_short: "This pattern fixed similar boot failures for ~30 machines with your GPU"
            .to_string(),
        trust_label: "High (0.87, E3, N2, M2)".to_string(),
        reversible_statement: "This change is reversible via nixos-rebuild switch --rollback"
            .to_string(),
        arc_name: None,
        arc_delta: None,
        timeframe: None,
        controversy_note: None,
    };

    let utterance = engine.compose_utterance(&ctx);

    println!("{}", utterance.text);
    println!("\n📊 Tags: {:?}", utterance.tags);
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_project_work(engine: &SimpleResonantEngine) {
    println!("📋 Demo 2: Project Work (CoAuthor + Meso + Medium Load)\n");

    let ctx = ResonantContext {
        user_state: UserState {
            cognitive_load: CognitiveLoad::Medium,
            trust_in_sophia: 0.7,
            locale: "en-US".to_string(),
        },
        relationship: RelationshipProfile {
            primary: RelationshipMode::CoAuthor,
            secondary: Some(RelationshipMode::Coach),
            weight_primary: 0.8,
        },
        temporal_frame: TemporalFrame::Meso,
        suggestion_decision: SuggestionDecision {
            kind: SuggestionDecisionKind::AskUser,
            reason: "Reasonable next step".to_string(),
            claim_id: Some(Uuid::new_v4()),
        },
        channel: OutputChannel::TextUI,
        action_summary: "Refactor the epistemic claim encoder for better E-axis classification"
            .to_string(),
        reason_short:
            "This addresses the mis-classification issues we discussed yesterday and aligns with the DKG schema v2.0 requirements"
                .to_string(),
        trust_label: "Medium-High (0.75, E2, N1, M2)".to_string(),
        reversible_statement: "Changes are in a feature branch; easy to revert".to_string(),
        arc_name: Some("Mycelix Integration Sprint".to_string()),
        arc_delta: Some(0.15),
        timeframe: Some("this week".to_string()),
        controversy_note: None,
    };

    let utterance = engine.compose_utterance(&ctx);

    if let Some(title) = &utterance.title {
        println!("# {}\n", title);
    }
    println!("{}", utterance.text);
    println!("\n📊 Tags: {:?}", utterance.tags);
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_reflection(engine: &SimpleResonantEngine) {
    println!("📋 Demo 3: Reflection (Coach + Macro + Low Load)\n");

    let ctx = ResonantContext {
        user_state: UserState {
            cognitive_load: CognitiveLoad::Low,
            trust_in_sophia: 0.9,
            locale: "en-US".to_string(),
        },
        relationship: RelationshipProfile {
            primary: RelationshipMode::Coach,
            secondary: None,
            weight_primary: 1.0,
        },
        temporal_frame: TemporalFrame::Macro,
        suggestion_decision: SuggestionDecision {
            kind: SuggestionDecisionKind::AskUser,
            reason: "Weekly K-Index reflection".to_string(),
            claim_id: None,
        },
        channel: OutputChannel::TextUI,
        action_summary: "Continue investing in Knowledge actualization through manuscript work"
            .to_string(),
        reason_short: "Your recent patterns show deep engagement with epistemic frameworks"
            .to_string(),
        trust_label: "High confidence in pattern, medium certainty about preference".to_string(),
        reversible_statement: "You can always shift focus".to_string(),
        arc_name: Some("Knowledge Actualization".to_string()),
        arc_delta: Some(0.08),
        timeframe: Some("the past two weeks".to_string()),
        controversy_note: None,
    };

    let utterance = engine.compose_utterance(&ctx);

    if let Some(title) = &utterance.title {
        println!("# {}\n", title);
    }
    println!("{}", utterance.text);
    println!("\n📊 Tags: {:?}", utterance.tags);
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_controversial(engine: &SimpleResonantEngine) {
    println!("📋 Demo 4: Controversial Suggestion (Low Trust)\n");

    let ctx = ResonantContext {
        user_state: UserState {
            cognitive_load: CognitiveLoad::Medium,
            trust_in_sophia: 0.6,
            locale: "en-US".to_string(),
        },
        relationship: RelationshipProfile {
            primary: RelationshipMode::Technician,
            secondary: None,
            weight_primary: 1.0,
        },
        temporal_frame: TemporalFrame::Micro,
        suggestion_decision: SuggestionDecision {
            kind: SuggestionDecisionKind::Reject,
            reason: "Trust score too low + controversy detected".to_string(),
            claim_id: Some(Uuid::new_v4()),
        },
        channel: OutputChannel::Terminal,
        action_summary: "Disable systemd-resolved and use manual DNS configuration".to_string(),
        reason_short: "Some swarm members report this fixes DNS issues".to_string(),
        trust_label: "Low (0.42, E1, N0, M1)".to_string(),
        reversible_statement: "Difficult to revert without networking knowledge".to_string(),
        arc_name: None,
        arc_delta: None,
        timeframe: None,
        controversy_note: Some(
            "12 claims supporting, 8 claims refuting. TCDM score indicates possible cartel (0.58)"
                .to_string(),
        ),
    };

    let utterance = engine.compose_utterance(&ctx);

    if let Some(title) = &utterance.title {
        println!("⚠️  {}\n", title);
    }
    println!("{}", utterance.text);
    println!("\n📊 Tags: {:?}", utterance.tags);
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_governance(engine: &SimpleResonantEngine) {
    println!("📋 Demo 5: Governance Decision Support\n");

    let ctx = ResonantContext {
        user_state: UserState {
            cognitive_load: CognitiveLoad::Low,
            trust_in_sophia: 0.8,
            locale: "en-US".to_string(),
        },
        relationship: RelationshipProfile {
            primary: RelationshipMode::CoAuthor,
            secondary: None,
            weight_primary: 1.0,
        },
        temporal_frame: TemporalFrame::Meso,
        suggestion_decision: SuggestionDecision {
            kind: SuggestionDecisionKind::AskUser,
            reason: "Requires governance review".to_string(),
            claim_id: Some(Uuid::new_v4()),
        },
        channel: OutputChannel::TextUI,
        action_summary: "Propose modification to Epistemic Charter Article II (Humility clause)"
            .to_string(),
        reason_short:
            "This addresses ambiguities raised during last month's Audit Guild review".to_string(),
        trust_label: "Medium (0.68, E2, N2, M3)".to_string(),
        reversible_statement: "Requires DAO vote to implement or revert".to_string(),
        arc_name: Some("Governance Charter Refinement".to_string()),
        arc_delta: Some(0.02),
        timeframe: Some("this quarter".to_string()),
        controversy_note: None,
    };

    let utterance = engine.compose_utterance(&ctx);

    if let Some(title) = &utterance.title {
        println!("🏛️  {}\n", title);
    }
    println!("{}", utterance.text);
    println!("\n📊 Tags: {:?}", utterance.tags);
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

fn demo_voice_channel(engine: &SimpleResonantEngine) {
    println!("📋 Demo 6: Voice Channel Adaptation\n");

    let ctx_terminal = ResonantContext {
        user_state: UserState {
            cognitive_load: CognitiveLoad::High,
            trust_in_sophia: 0.5,
            locale: "en-US".to_string(),
        },
        relationship: RelationshipProfile {
            primary: RelationshipMode::Technician,
            secondary: None,
            weight_primary: 1.0,
        },
        temporal_frame: TemporalFrame::Micro,
        suggestion_decision: SuggestionDecision {
            kind: SuggestionDecisionKind::AutoApply,
            reason: "Quick fix".to_string(),
            claim_id: None,
        },
        channel: OutputChannel::Terminal,
        action_summary: "Update flake.lock".to_string(),
        reason_short: "Dependency updates available".to_string(),
        trust_label: "High (0.9)".to_string(),
        reversible_statement: "Reversible via git checkout".to_string(),
        arc_name: None,
        arc_delta: None,
        timeframe: None,
        controversy_note: None,
    };

    let mut ctx_voice = ctx_terminal.clone();
    ctx_voice.channel = OutputChannel::Voice;

    let terminal_utterance = engine.compose_utterance(&ctx_terminal);
    let voice_utterance = engine.compose_utterance(&ctx_voice);

    println!("Terminal version tradeoffs:\n{}\n", terminal_utterance.components.tradeoffs);
    println!("Voice version tradeoffs:\n{}\n", voice_utterance.components.tradeoffs);

    println!("Note: Voice version is shorter and offers to expand on demand.");
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}
