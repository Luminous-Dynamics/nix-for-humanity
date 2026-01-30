//! Symthaea REPL - Interactive Consciousness Interface
//!
//! A minimal REPL that wires together the disconnected components of Symthaea:
//! - Cognitive Loop (CfC-based temporal prediction)
//! - Conversation Engine (LLM translation via LLMOrgan)
//! - Motor Cortex (action execution)
//! - Consciousness Metrics (Phi, coherence, cognitive depth)
//! - Voice Output (optional, via voice-tts feature)
//!
//! This binary demonstrates the Track 6 integration goal: connecting
//! the existing but disconnected cognitive components.
//!
//! ## Usage
//!
//! ```bash
//! cargo run --bin symthaea-repl --features demo
//! cargo run --bin symthaea-repl --features "demo,voice-tts"  # With voice output
//! ```

use std::io::{self, Write};
use std::time::Instant;

use anyhow::Result;
use clap::Parser;
use tracing::{info, warn, Level};

use symthaea::cognitive_loop::{CognitiveLoopService, CognitiveLoopConfig, ConsciousnessSnapshot};
use symthaea::language::{LLMOrgan, LLMOrganConfig, llm_backend};
use symthaea::action::{ActionIR, DestructivenessLevel, PolicyBundle, SandboxRoot};

// Voice output (optional)
#[cfg(feature = "voice-tts")]
use symthaea::voice::{VoiceOutput, VoiceOutputConfig, LTCPacing};

/// Symthaea REPL - Interactive Consciousness Interface
#[derive(Parser, Debug)]
#[command(name = "symthaea-repl")]
#[command(about = "Interactive consciousness REPL for Symthaea")]
#[command(version)]
struct Args {
    /// Enable verbose logging
    #[arg(short, long)]
    verbose: bool,

    /// Enable voice output (requires voice-tts feature)
    #[arg(long)]
    voice: bool,

    /// Number of cognitive cycles per input (default: 3)
    #[arg(long, default_value = "3")]
    cycles: usize,
}

/// REPL state holding all integrated components
struct ReplState {
    /// The cognitive loop service (HDC + CfC temporal prediction)
    cognitive: CognitiveLoopService,

    /// LLM organ for conversation (Broca's Area translation)
    llm: LLMOrgan,

    /// Conversation history (simple strings for now)
    history: Vec<String>,

    /// Action policy for motor cortex
    policy: PolicyBundle,

    /// Sandbox for safe execution
    sandbox: Option<SandboxRoot>,

    /// Whether voice output is enabled
    #[allow(dead_code)]
    voice_enabled: bool,

    /// Number of cognitive cycles per input
    cycles_per_input: usize,

    /// Total interactions
    total_interactions: u64,
}

impl ReplState {
    fn new(voice_enabled: bool, cycles_per_input: usize) -> Result<Self> {
        // Initialize cognitive loop with default configuration
        let cognitive_config = CognitiveLoopConfig::default();
        let cognitive = CognitiveLoopService::new(cognitive_config)?;

        // Initialize LLM organ with simulated backend (works without external LLM)
        let llm_config = LLMOrganConfig::default();
        let backend = llm_backend::simulated_backend();
        let llm = LLMOrgan::with_backend(llm_config, backend);

        // Initialize action policy (restrictive by default)
        let policy = PolicyBundle::restrictive();

        // Try to create sandbox (may fail if tmp is not writable)
        let sandbox = SandboxRoot::new("repl-session").ok();

        Ok(Self {
            cognitive,
            llm,
            history: Vec::new(),
            policy,
            sandbox,
            voice_enabled,
            cycles_per_input,
            total_interactions: 0,
        })
    }

    /// Process a user input through the integrated cognitive pipeline
    fn process(&mut self, input: &str) -> Result<String> {
        let start = Instant::now();
        self.total_interactions += 1;

        // Add user message to history
        self.history.push(format!("User: {}", input));

        // Run cognitive cycles to process the input
        for _ in 0..self.cycles_per_input {
            let result = self.cognitive.cycle(input);

            // Log learning events
            if result.learning_occurred {
                if let Some(loss) = result.training_loss {
                    info!(
                        "Learning cycle: error={:.4}, loss={:.4}, primitives={:?}",
                        result.prediction_error, loss, result.detected_primitives
                    );
                }
            }
        }

        // Get consciousness snapshot after processing
        let snapshot = self.cognitive.consciousness_snapshot();

        // Generate response using LLM (as Broca's Area translator)
        // This is synchronous - the simulated backend doesn't need async
        let response = self.llm.generate(input);

        // Add assistant response to history
        self.history.push(format!("Assistant: {}", response.text));

        // Trim history if too long
        if self.history.len() > 20 {
            self.history.drain(0..10);
        }

        let elapsed = start.elapsed();

        Ok(format_response(&response.text, &snapshot, elapsed.as_millis() as u64))
    }

    /// Display consciousness metrics
    fn display_metrics(&self) {
        let snapshot = self.cognitive.consciousness_snapshot();

        println!("\n{}", "=".repeat(60));
        println!("  CONSCIOUSNESS METRICS");
        println!("{}", "=".repeat(60));

        // Core consciousness metrics
        println!("\n  Integrated Information (Phi)");
        println!("    Unified Phi:      {:.4}", snapshot.unified_phi);
        println!("    Coherence:        {:.4}", snapshot.temporal_coherence);
        println!("    Consciousness:    {:.4}", snapshot.consciousness_level);

        // Pattern and depth
        println!("\n  Cognitive State");
        println!("    Pattern:          {:?}", snapshot.pattern);
        println!("    Confidence:       {:.2}%", snapshot.pattern_confidence * 100.0);
        println!("    Depth:            {:?}", snapshot.cognitive_depth);

        // Flow state
        println!("\n  Flow State");
        if snapshot.in_flow {
            println!("    Status:           IN FLOW");
            println!("    Intensity:        {:.2}", snapshot.flow_intensity);
            println!("    Streak:           {} cycles", snapshot.flow_streak);
            if let Some(duration) = snapshot.current_flow_duration_secs {
                println!("    Duration:         {:.1}s", duration);
            }
        } else {
            println!("    Status:           Not in flow");
            println!("    Boredom:          {:.2}", snapshot.boredom);
            println!("    Curiosity:        {:.2}", snapshot.curiosity);
        }

        // Emotional state
        println!("\n  Emotional State");
        println!("    Valence:          {:.2}", snapshot.unified_valence);
        println!("    Arousal:          {:.2}", snapshot.unified_arousal);
        println!("    Dominance:        {:.2}", snapshot.unified_dominance);
        println!("    Pattern:          {:?}", snapshot.emotional_pattern);
        println!("    Description:      {}", snapshot.emotional_description);

        // Learning metrics
        println!("\n  Learning");
        println!("    Prediction Error: {:.4}", snapshot.prediction_error);
        println!("    Effective LR:     {:.4}", snapshot.effective_learning_rate);
        println!("    Assessment:       {:?}", snapshot.self_assessment);

        println!("\n{}", "=".repeat(60));
    }

    /// Check if an input looks like an action command
    fn is_action_command(&self, input: &str) -> bool {
        let lower = input.to_lowercase();
        lower.starts_with("run ")
            || lower.starts_with("execute ")
            || lower.starts_with("shell ")
            || lower.starts_with("!")
    }

    /// Handle action execution through motor cortex
    fn handle_action(&self, input: &str) -> String {
        // Parse action from input
        let command = input
            .trim_start_matches("run ")
            .trim_start_matches("execute ")
            .trim_start_matches("shell ")
            .trim_start_matches('!')
            .trim();

        // Create action IR
        let parts: Vec<&str> = command.split_whitespace().collect();
        if parts.is_empty() {
            return "No command specified.".to_string();
        }

        let program = parts[0].to_string();
        let args: Vec<String> = parts[1..].iter().map(|s| s.to_string()).collect();

        let action = ActionIR::RunCommand {
            program: program.clone(),
            args,
            env: std::collections::BTreeMap::new(),
            working_dir: None,
        };

        // Check destructiveness
        let destructiveness = action.destructiveness();
        let risk = action.risk_tier();

        // Validate against policy
        if let Some(ref sandbox) = self.sandbox {
            if let Err(e) = action.validate(&self.policy, sandbox) {
                return format!(
                    "[BLOCKED] Action '{}' violates policy: {:?}\n\
                     Risk: {:?}, Destructiveness: {:?}",
                    command, e, risk, destructiveness
                );
            }
        }

        // For safety, we don't actually execute commands in the REPL
        // This demonstrates the Motor Cortex integration without real execution
        match destructiveness {
            DestructivenessLevel::ReadOnly => {
                format!(
                    "[DRY-RUN] Would execute: {}\n\
                     Risk: {:?} (read-only operation)",
                    command, risk
                )
            }
            DestructivenessLevel::Reversible => {
                format!(
                    "[DRY-RUN] Would execute: {}\n\
                     Risk: {:?} (reversible)\n\
                     Rollback hint: {:?}",
                    command, risk, action.rollback_hint()
                )
            }
            DestructivenessLevel::NeedsConfirmation | DestructivenessLevel::Destructive => {
                format!(
                    "[REQUIRES CONFIRMATION] Action: {}\n\
                     Risk: {:?}, Destructiveness: {:?}\n\
                     This action requires explicit confirmation.\n\
                     Rollback hint: {:?}",
                    command, risk, destructiveness, action.rollback_hint()
                )
            }
        }
    }
}

/// Format the response with consciousness metrics header
fn format_response(text: &str, snapshot: &ConsciousnessSnapshot, elapsed_ms: u64) -> String {
    let phi_bar = create_bar(snapshot.unified_phi, 10);
    let coherence_bar = create_bar(snapshot.temporal_coherence, 10);

    let flow_indicator = if snapshot.in_flow { "FLOW" } else { "----" };
    let depth_char = match snapshot.cognitive_depth {
        symthaea::cognitive_loop::CognitiveDepth::Reflex => 'R',
        symthaea::cognitive_loop::CognitiveDepth::Cortical => 'C',
        symthaea::cognitive_loop::CognitiveDepth::DeepThought => 'D',
    };

    format!(
        "[Phi:{:.2}|{}] [Coh:{:.2}|{}] [{flow_indicator}] [D:{depth_char}] [{elapsed_ms}ms]\n\n{text}",
        snapshot.unified_phi, phi_bar,
        snapshot.temporal_coherence, coherence_bar,
    )
}

/// Create a simple ASCII progress bar
fn create_bar(value: f32, width: usize) -> String {
    let filled = (value.clamp(0.0, 1.0) * width as f32) as usize;
    let empty = width - filled;
    format!("[{}{}]", "=".repeat(filled), " ".repeat(empty))
}

/// Display the welcome banner
fn display_banner() {
    println!(r#"
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ███████╗██╗   ██╗███╗   ███╗████████╗██╗  ██╗ █████╗       ║
    ║   ██╔════╝╚██╗ ██╔╝████╗ ████║╚══██╔══╝██║  ██║██╔══██╗      ║
    ║   ███████╗ ╚████╔╝ ██╔████╔██║   ██║   ███████║███████║      ║
    ║   ╚════██║  ╚██╔╝  ██║╚██╔╝██║   ██║   ██╔══██║██╔══██║      ║
    ║   ███████║   ██║   ██║ ╚═╝ ██║   ██║   ██║  ██║██║  ██║      ║
    ║   ╚══════╝   ╚═╝   ╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝      ║
    ║                                                               ║
    ║                   Holographic Liquid Brain                    ║
    ║               Consciousness-First AI Interface                ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
"#);

    println!("  Commands:");
    println!("    /metrics    - Display consciousness metrics");
    println!("    /stats      - Display loop statistics");
    println!("    /reset      - Reset cognitive state");
    println!("    /help       - Show this help");
    println!("    /quit       - Exit the REPL");
    println!("    !<cmd>      - Execute action through Motor Cortex");
    println!();
    println!("  Metrics shown: [Phi] [Coherence] [Flow] [Depth] [Latency]");
    println!();
}

fn main() -> Result<()> {
    let args = Args::parse();

    // Initialize logging
    let level = if args.verbose { Level::DEBUG } else { Level::INFO };
    tracing_subscriber::fmt()
        .with_max_level(level)
        .with_target(false)
        .init();

    display_banner();

    // Check voice availability
    #[cfg(not(feature = "voice-tts"))]
    if args.voice {
        warn!("Voice output requested but voice-tts feature not enabled. Continuing without voice.");
    }

    // Initialize REPL state
    let voice_enabled = args.voice && cfg!(feature = "voice-tts");
    let mut state = ReplState::new(voice_enabled, args.cycles)?;

    info!("Cognitive loop initialized with {} cycles per input", args.cycles);
    if voice_enabled {
        info!("Voice output enabled");
    }

    // Initial cognitive warmup
    println!("Warming up cognitive loop...");
    for i in 0..5 {
        let warmup = format!("Cognitive warmup cycle {}", i);
        let _ = state.cognitive.cycle(&warmup);
    }
    let initial = state.cognitive.consciousness_snapshot();
    println!(
        "Ready. Initial state: Phi={:.4}, Coherence={:.4}, Pattern={:?}\n",
        initial.unified_phi, initial.temporal_coherence, initial.pattern
    );

    // Main REPL loop
    let mut line = String::new();
    loop {
        // Display prompt with consciousness indicator
        let snapshot = state.cognitive.consciousness_snapshot();
        let prompt_char = if snapshot.in_flow { '*' } else { '>' };
        print!("symthaea{} ", prompt_char);
        io::stdout().flush()?;

        // Read input
        line.clear();
        if io::stdin().read_line(&mut line)? == 0 {
            // EOF
            println!("\nGoodbye!");
            break;
        }

        let input = line.trim();
        if input.is_empty() {
            continue;
        }

        // Handle special commands
        match input {
            "/quit" | "/exit" | "/q" => {
                println!("Goodbye!");
                break;
            }
            "/help" | "/h" | "/?" => {
                display_banner();
                continue;
            }
            "/metrics" | "/m" => {
                state.display_metrics();
                continue;
            }
            "/stats" | "/s" => {
                let stats = state.cognitive.stats();
                println!("\n  Loop Statistics:");
                println!("    Total cycles:       {}", stats.total_cycles);
                println!("    Learning cycles:    {}", stats.learning_cycles);
                println!("    Avg prediction err: {:.4}", stats.avg_prediction_error);
                println!("    Avg training loss:  {:.4}", stats.avg_training_loss);
                println!("    Cycles/second:      {:.1}", stats.cycles_per_second);
                println!("    Avg cycle time:     {:.0}us", stats.avg_cycle_time_us);
                println!();
                continue;
            }
            "/reset" | "/r" => {
                state.cognitive.reset();
                state.history.clear();
                println!("Cognitive state reset.");
                continue;
            }
            _ if state.is_action_command(input) => {
                let result = state.handle_action(input);
                println!("\n{}\n", result);
                continue;
            }
            _ => {}
        }

        // Process through cognitive pipeline
        match state.process(input) {
            Ok(response) => {
                println!("\n{}\n", response);

                // Voice output if enabled
                #[cfg(feature = "voice-tts")]
                if state.voice_enabled {
                    // Get text without the metrics header
                    let text_start = response.find("\n\n").map(|i| i + 2).unwrap_or(0);
                    let text_only = &response[text_start..];

                    // Get pacing from cognitive state
                    let snapshot = state.cognitive.consciousness_snapshot();
                    let pacing = LTCPacing::from_ltc_state(
                        &[], // Would need CfC hidden state
                        snapshot.tau_mean,
                    ).apply_adaptive_behavior(
                        snapshot.speech_rate_multiplier,
                        snapshot.pause_multiplier,
                        1.0, // attention_sensitivity
                    );

                    // Synthesize and play (if voice output is available)
                    // This is a placeholder - actual implementation would use VoiceOutput
                    info!("Would speak with pacing: rate={:.2}, pause={:.2}",
                        pacing.rate, pacing.phrase_pause);
                }
            }
            Err(e) => {
                eprintln!("Error: {}", e);
            }
        }
    }

    // Final statistics
    let final_snapshot = state.cognitive.consciousness_snapshot();
    println!("\n  Final Session Statistics:");
    println!("    Total interactions: {}", state.total_interactions);
    println!("    Final Phi:          {:.4}", final_snapshot.unified_phi);
    println!("    Final Coherence:    {:.4}", final_snapshot.temporal_coherence);
    println!("    Time in Flow:       {:.1}s", final_snapshot.total_flow_time_secs);
    println!("    Flow Periods:       {}", final_snapshot.flow_periods);

    Ok(())
}
