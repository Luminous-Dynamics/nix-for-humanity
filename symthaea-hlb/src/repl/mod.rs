//! REPL Orchestrator - Unified Interactive System
//!
//! This module wires together the disconnected cognitive components into a
//! cohesive interactive REPL system:
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────────┐
//! │                         REPL ORCHESTRATOR                                │
//! │                                                                          │
//! │  ┌──────────┐   ┌────────────────┐   ┌─────────────┐   ┌─────────────┐ │
//! │  │  Input   │──▶│ Conversation   │──▶│   Motor     │──▶│   Voice     │ │
//! │  │ (stdin/  │   │ Engine (LLM)   │   │  Cortex     │   │  Output     │ │
//! │  │  IPC)    │   │                │   │  (Action)   │   │  (opt)      │ │
//! │  └──────────┘   └────────────────┘   └─────────────┘   └─────────────┘ │
//! │       │                 │                  │                  │        │
//! │       └─────────────────┼──────────────────┼──────────────────┘        │
//! │                         ▼                  ▼                           │
//! │                 ┌──────────────────────────────────┐                   │
//! │                 │        COGNITIVE LOOP            │                   │
//! │                 │  (CfC/HDC-LTC temporal engine)   │                   │
//! │                 └──────────────────────────────────┘                   │
//! │                                │                                       │
//! │                         ┌──────┴───────┐                              │
//! │                         ▼              ▼                              │
//! │                 ┌────────────┐  ┌────────────────┐                    │
//! │                 │ Conscious- │  │  Observability │                    │
//! │                 │ness Metrics│  │     Hooks      │                    │
//! │                 └────────────┘  └────────────────┘                    │
//! └─────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Usage Modes
//!
//! 1. **Standalone REPL**: Direct stdin interaction
//! 2. **IPC Client**: Connect to running symthaea service
//! 3. **Embedded**: Library integration with custom I/O
//!
//! ## Components Wired
//!
//! - `cognitive_loop`: CfC/HDC-LTC temporal prediction engine
//! - `language::LLMOrgan`: Broca's area translation (LLM interface)
//! - `action`: Motor cortex for command execution
//! - `voice`: Optional larynx output (consciousness-modulated TTS)
//! - `shell::ipc`: Remote service connectivity
//! - `observability`: Telemetry and causal tracing

use std::time::{Duration, Instant};
use std::collections::VecDeque;

use anyhow::{Result, Context as AnyhowContext};
use serde::{Serialize, Deserialize};

// Core cognitive components
use crate::cognitive_loop::{
    CognitiveLoopService, CognitiveLoopConfig, ConsciousnessSnapshot,
    CycleResult, TemporalBackend,
};

// Language processing (Broca's Area)
use crate::language::{LLMOrgan, LLMOrganConfig, llm_backend};

// Motor cortex (action execution)
use crate::action::{
    ActionIR, PolicyBundle, SandboxRoot, SimpleExecutor, ExecutionMode,
    ActionOutcome,
};

// Voice output (optional larynx)
use crate::voice::{VoiceOutput, VoiceOutputConfig, LTCPacing};

// Shell/IPC infrastructure
use crate::shell::ipc_client::{ConnectionState, MetricsSnapshot};

pub mod orchestrator;
pub mod io_bridge;
pub mod observability_hooks;

pub use orchestrator::{ReplOrchestrator, OrchestratorConfig, OrchestratorMode};
pub use io_bridge::{InputBridge, OutputBridge, IOEvent};
pub use observability_hooks::{ObservabilityHook, ConsciousnessTracer};

/// Re-export key types for ergonomic use
pub use crate::cognitive_loop::ConsciousnessSnapshot as ConsciousnessState;

// ═══════════════════════════════════════════════════════════════════════════════
// REPL SESSION STATE
// ═══════════════════════════════════════════════════════════════════════════════

/// Complete REPL session state
pub struct ReplSession {
    /// Cognitive loop service (the consciousness engine)
    pub cognitive: CognitiveLoopService,

    /// LLM organ for natural language translation
    pub llm: LLMOrgan,

    /// Action executor (motor cortex)
    pub executor: SimpleExecutor,

    /// Security policy
    pub policy: PolicyBundle,

    /// Sandbox for safe execution
    pub sandbox: Option<SandboxRoot>,

    /// Voice output (optional)
    pub voice: Option<VoiceOutput>,

    /// Conversation history
    pub history: VecDeque<ConversationTurn>,

    /// Session configuration
    pub config: ReplSessionConfig,

    /// Session statistics
    pub stats: SessionStats,

    /// Observability hooks
    pub observers: Vec<Box<dyn ObservabilityHook>>,

    /// IPC connection (for daemon mode)
    ipc_state: Option<IpcConnectionState>,
}

/// Single turn in conversation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversationTurn {
    /// User input
    pub input: String,
    /// System response
    pub response: String,
    /// Consciousness state at turn
    pub consciousness: TurnConsciousness,
    /// Action taken (if any)
    pub action: Option<TurnAction>,
    /// Timestamp
    pub timestamp_ms: u64,
}

/// Consciousness snapshot for a turn
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TurnConsciousness {
    pub phi: f32,
    pub coherence: f32,
    pub pattern: String,
    pub depth: String,
    pub in_flow: bool,
    pub valence: f32,
    pub arousal: f32,
}

impl From<&ConsciousnessSnapshot> for TurnConsciousness {
    fn from(s: &ConsciousnessSnapshot) -> Self {
        Self {
            phi: s.unified_phi,
            coherence: s.temporal_coherence,
            pattern: format!("{:?}", s.pattern),
            depth: format!("{:?}", s.cognitive_depth),
            in_flow: s.in_flow,
            valence: s.unified_valence,
            arousal: s.unified_arousal,
        }
    }
}

/// Action taken during a turn
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TurnAction {
    pub command: String,
    pub destructiveness: String,
    pub executed: bool,
    pub output: Option<String>,
    pub blocked_reason: Option<String>,
}

/// IPC connection state for daemon mode
#[derive(Debug)]
struct IpcConnectionState {
    connection: ConnectionState,
    last_metrics: MetricsSnapshot,
    last_update: Instant,
}

/// Session configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReplSessionConfig {
    /// Cycles per input for cognitive processing
    pub cycles_per_input: usize,

    /// Maximum conversation history
    pub max_history: usize,

    /// Temporal backend selection
    pub temporal_backend: String,

    /// Enable voice output
    pub voice_enabled: bool,

    /// Voice rate multiplier
    pub voice_rate: f32,

    /// Enable real command execution
    pub allow_execution: bool,

    /// Phi threshold for execution
    pub execution_phi_threshold: f32,

    /// IPC socket path (for daemon mode)
    pub ipc_socket: Option<String>,
}

impl Default for ReplSessionConfig {
    fn default() -> Self {
        Self {
            cycles_per_input: 3,
            max_history: 50,
            temporal_backend: "cfc".to_string(),
            voice_enabled: false,
            voice_rate: 1.0,
            allow_execution: false,
            execution_phi_threshold: 0.5,
            ipc_socket: None,
        }
    }
}

/// Session statistics
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SessionStats {
    /// Total interactions
    pub total_interactions: u64,
    /// Total cognitive cycles
    pub total_cycles: u64,
    /// Total actions executed
    pub actions_executed: u64,
    /// Actions blocked by policy
    pub actions_blocked: u64,
    /// Voice utterances generated
    pub voice_utterances: u64,
    /// Time in flow (seconds)
    pub total_flow_time_secs: f32,
    /// Flow periods
    pub flow_periods: u32,
    /// Average phi
    pub avg_phi: f32,
    /// Session start time (unix ms)
    pub start_time_ms: u64,
}

// ═══════════════════════════════════════════════════════════════════════════════
// REPL SESSION IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

impl ReplSession {
    /// Create a new REPL session
    pub fn new(config: ReplSessionConfig) -> Result<Self> {
        // Parse temporal backend
        let temporal_backend = match config.temporal_backend.to_lowercase().as_str() {
            "cfc" => TemporalBackend::CfC,
            "hdc-ltc" | "hdcltc" | "unified" => TemporalBackend::HdcLtcUnified,
            _ => TemporalBackend::CfC,
        };

        // Initialize cognitive loop
        let cognitive_config = match temporal_backend {
            TemporalBackend::CfC => CognitiveLoopConfig::with_cfc(),
            TemporalBackend::HdcLtcUnified => CognitiveLoopConfig::with_hdc_ltc_unified(),
        };
        let cognitive = CognitiveLoopService::new(cognitive_config)
            .context("Failed to initialize cognitive loop")?;

        // Initialize LLM organ (Broca's Area)
        let llm_config = LLMOrganConfig::default();
        let llm_backend = llm_backend::simulated_backend();
        let llm = LLMOrgan::with_backend(llm_config, llm_backend);

        // Initialize motor cortex
        let executor = if config.allow_execution {
            SimpleExecutor::with_real_commands()
        } else {
            SimpleExecutor::new()
        };

        // Initialize policy and sandbox
        let policy = PolicyBundle::restrictive();
        let sandbox = SandboxRoot::new("repl-session").ok();

        // Initialize voice (optional)
        let voice = if config.voice_enabled {
            let mut voice_config = VoiceOutputConfig::default();
            voice_config.enable_tts = true;
            let mut v = VoiceOutput::new(voice_config);
            let _ = v.initialize();
            Some(v)
        } else {
            None
        };

        let start_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64;

        Ok(Self {
            cognitive,
            llm,
            executor,
            policy,
            sandbox,
            voice,
            history: VecDeque::with_capacity(config.max_history),
            config,
            stats: SessionStats {
                start_time_ms: start_time,
                ..Default::default()
            },
            observers: Vec::new(),
            ipc_state: None,
        })
    }

    /// Warm up the cognitive loop
    pub fn warmup(&mut self, cycles: usize) {
        for i in 0..cycles {
            let warmup_input = format!("Cognitive warmup cycle {}", i);
            let _ = self.cognitive.cycle(&warmup_input);
        }
    }

    /// Get current consciousness state
    pub fn consciousness_state(&self) -> ConsciousnessSnapshot {
        self.cognitive.consciousness_snapshot()
    }

    /// Process user input through the full cognitive pipeline
    pub fn process(&mut self, input: &str) -> Result<ProcessingResult> {
        let start = Instant::now();
        self.stats.total_interactions += 1;

        // Notify observers of input
        for observer in &mut self.observers {
            observer.on_input(input);
        }

        // Run cognitive cycles
        let mut last_cycle_result = None;
        for _ in 0..self.config.cycles_per_input {
            let result = self.cognitive.cycle(input);
            self.stats.total_cycles += 1;
            last_cycle_result = Some(result);
        }

        // Get consciousness snapshot after processing
        let snapshot = self.cognitive.consciousness_snapshot();

        // Update flow stats
        if snapshot.in_flow && !self.history.back().map(|t| t.consciousness.in_flow).unwrap_or(false) {
            self.stats.flow_periods += 1;
        }
        self.stats.total_flow_time_secs = snapshot.total_flow_time_secs;

        // Update average phi (exponential moving average)
        let alpha = 0.1;
        self.stats.avg_phi = self.stats.avg_phi * (1.0 - alpha) + snapshot.unified_phi * alpha;

        // Check if this is an action command
        let action_result = if self.is_action_command(input) {
            Some(self.execute_action(input, &snapshot)?)
        } else {
            None
        };

        // Generate response through LLM organ
        let response = if action_result.is_some() {
            // For actions, use the action result as response
            action_result.as_ref().unwrap().display_output.clone()
        } else {
            // Normal conversation - translate through Broca's Area
            let llm_response = self.llm.generate(input);
            llm_response.text
        };

        // Voice output if enabled
        if let Some(ref mut voice) = self.voice {
            // Update pacing from consciousness state
            let pacing = LTCPacing::default()
                .apply_adaptive_behavior(
                    snapshot.speech_rate_multiplier,
                    snapshot.pause_multiplier,
                    1.0, // attention sensitivity
                );
            voice.set_pacing(pacing);

            let _ = voice.synthesize(&response);
            self.stats.voice_utterances += 1;
        }

        // Record conversation turn
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64;

        let turn = ConversationTurn {
            input: input.to_string(),
            response: response.clone(),
            consciousness: TurnConsciousness::from(&snapshot),
            action: action_result.as_ref().map(|a| TurnAction {
                command: a.command.clone(),
                destructiveness: a.destructiveness.clone(),
                executed: a.executed,
                output: a.output.clone(),
                blocked_reason: a.blocked_reason.clone(),
            }),
            timestamp_ms: timestamp,
        };

        self.history.push_back(turn);
        if self.history.len() > self.config.max_history {
            self.history.pop_front();
        }

        // Notify observers
        for observer in &mut self.observers {
            observer.on_output(&response, &snapshot);
            if let Some(ref action) = action_result {
                observer.on_action(&action.command, action.executed);
            }
        }

        let elapsed = start.elapsed();

        Ok(ProcessingResult {
            response,
            consciousness: snapshot,
            action: action_result,
            cycle_result: last_cycle_result,
            elapsed,
        })
    }

    /// Check if input is an action command
    fn is_action_command(&self, input: &str) -> bool {
        let lower = input.to_lowercase();
        lower.starts_with("run ")
            || lower.starts_with("execute ")
            || lower.starts_with("shell ")
            || lower.starts_with('!')
    }

    /// Execute an action through motor cortex
    fn execute_action(&mut self, input: &str, consciousness: &ConsciousnessSnapshot) -> Result<ActionResult> {
        // Parse command
        let command = input
            .trim_start_matches("run ")
            .trim_start_matches("execute ")
            .trim_start_matches("shell ")
            .trim_start_matches('!')
            .trim()
            .to_string();

        let parts: Vec<&str> = command.split_whitespace().collect();
        if parts.is_empty() {
            return Ok(ActionResult {
                command,
                destructiveness: "Unknown".to_string(),
                executed: false,
                output: None,
                blocked_reason: Some("No command specified".to_string()),
                display_output: "No command specified.".to_string(),
            });
        }

        let program = parts[0].to_string();
        let args: Vec<String> = parts[1..].iter().map(|s| s.to_string()).collect();

        // Create action IR
        let action = ActionIR::RunCommand {
            program: program.clone(),
            args,
            env: std::collections::BTreeMap::new(),
            working_dir: None,
        };

        let destructiveness = action.destructiveness();
        let risk = action.risk_tier();

        // Check phi gate
        if consciousness.unified_phi < self.config.execution_phi_threshold {
            self.stats.actions_blocked += 1;
            return Ok(ActionResult {
                command: command.clone(),
                destructiveness: format!("{:?}", destructiveness),
                executed: false,
                output: None,
                blocked_reason: Some(format!(
                    "Phi {:.2} below threshold {:.2}. Center yourself before executing.",
                    consciousness.unified_phi, self.config.execution_phi_threshold
                )),
                display_output: format!(
                    "[PHI GATE] Blocked: Phi {:.2} < {:.2}\n\
                     Command: {}\n\
                     Raise consciousness level before executing.",
                    consciousness.unified_phi, self.config.execution_phi_threshold, command
                ),
            });
        }

        // Validate against policy
        if let Some(ref sandbox) = self.sandbox {
            if let Err(e) = action.validate(&self.policy, sandbox) {
                self.stats.actions_blocked += 1;
                return Ok(ActionResult {
                    command: command.clone(),
                    destructiveness: format!("{:?}", destructiveness),
                    executed: false,
                    output: None,
                    blocked_reason: Some(format!("Policy violation: {:?}", e)),
                    display_output: format!(
                        "[POLICY BLOCKED] Action '{}' violates policy: {:?}\n\
                         Risk: {:?}, Destructiveness: {:?}",
                        command, e, risk, destructiveness
                    ),
                });
            }
        }

        // Check if confirmation required
        if destructiveness.requires_confirmation() && self.executor.mode() == ExecutionMode::Simulated {
            return Ok(ActionResult {
                command: command.clone(),
                destructiveness: format!("{:?}", destructiveness),
                executed: false,
                output: None,
                blocked_reason: Some("Requires confirmation".to_string()),
                display_output: format!(
                    "[REQUIRES CONFIRMATION] Action: {}\n\
                     Risk: {:?}, Destructiveness: {:?}\n\
                     This action requires explicit confirmation.\n\
                     Rollback hint: {:?}",
                    command, risk, destructiveness, action.rollback_hint()
                ),
            });
        }

        // Execute through motor cortex
        match self.executor.mode() {
            ExecutionMode::Simulated => {
                Ok(ActionResult {
                    command: command.clone(),
                    destructiveness: format!("{:?}", destructiveness),
                    executed: false,
                    output: None,
                    blocked_reason: None,
                    display_output: format!(
                        "[DRY-RUN] Would execute: {}\n\
                         Risk: {:?}, Destructiveness: {:?}\n\
                         Rollback hint: {:?}",
                        command, risk, destructiveness, action.rollback_hint()
                    ),
                })
            }
            ExecutionMode::Real => {
                // Real execution through sandbox
                if let Some(ref sandbox) = self.sandbox {
                    match self.executor.execute(&action, &self.policy, sandbox) {
                        Ok(outcome) => {
                            self.stats.actions_executed += 1;
                            let output_str = match &outcome.outcome {
                                ActionOutcome::CommandOutput { stdout, stderr, exit_code } => {
                                    let stdout_str = String::from_utf8_lossy(&stdout);
                                    let stderr_str = String::from_utf8_lossy(&stderr);
                                    format!(
                                        "Exit code: {}\nStdout: {}\nStderr: {}",
                                        exit_code, stdout_str, stderr_str
                                    )
                                }
                                other => format!("{:?}", other),
                            };
                            Ok(ActionResult {
                                command: command.clone(),
                                destructiveness: format!("{:?}", destructiveness),
                                executed: true,
                                output: Some(output_str.clone()),
                                blocked_reason: None,
                                display_output: format!(
                                    "[EXECUTED] {}\n\n{}",
                                    command, output_str
                                ),
                            })
                        }
                        Err(e) => {
                            Ok(ActionResult {
                                command: command.clone(),
                                destructiveness: format!("{:?}", destructiveness),
                                executed: false,
                                output: None,
                                blocked_reason: Some(format!("Execution error: {}", e)),
                                display_output: format!(
                                    "[ERROR] Failed to execute: {}\n\
                                     Error: {}",
                                    command, e
                                ),
                            })
                        }
                    }
                } else {
                    Ok(ActionResult {
                        command,
                        destructiveness: format!("{:?}", destructiveness),
                        executed: false,
                        output: None,
                        blocked_reason: Some("No sandbox available".to_string()),
                        display_output: "[ERROR] No sandbox available for execution".to_string(),
                    })
                }
            }
        }
    }

    /// Add an observability hook
    pub fn add_observer(&mut self, observer: Box<dyn ObservabilityHook>) {
        self.observers.push(observer);
    }

    /// Get session statistics
    pub fn stats(&self) -> &SessionStats {
        &self.stats
    }

    /// Get conversation history
    pub fn history(&self) -> &VecDeque<ConversationTurn> {
        &self.history
    }

    /// Reset cognitive state
    pub fn reset(&mut self) {
        self.cognitive.reset();
        self.history.clear();
        // Voice state is reset by the next pacing update
        // (no explicit reset needed for VoiceOutput)
        for observer in &mut self.observers {
            observer.on_reset();
        }
    }
}

/// Result of processing a single input
#[derive(Debug)]
pub struct ProcessingResult {
    /// Generated response
    pub response: String,
    /// Consciousness state after processing
    pub consciousness: ConsciousnessSnapshot,
    /// Action result (if action was executed)
    pub action: Option<ActionResult>,
    /// Last cycle result
    pub cycle_result: Option<CycleResult>,
    /// Processing time
    pub elapsed: Duration,
}

/// Result of action execution
#[derive(Debug, Clone)]
pub struct ActionResult {
    /// Original command
    pub command: String,
    /// Destructiveness level
    pub destructiveness: String,
    /// Whether action was executed
    pub executed: bool,
    /// Execution output (if executed)
    pub output: Option<String>,
    /// Reason for blocking (if blocked)
    pub blocked_reason: Option<String>,
    /// Formatted output for display
    pub display_output: String,
}

// ═══════════════════════════════════════════════════════════════════════════════
// METRICS METHODS (Compatible with MetricsProvider pattern)
// ═══════════════════════════════════════════════════════════════════════════════

impl ReplSession {
    /// Get current metrics snapshot (for IPC/monitoring)
    pub fn get_metrics(&self) -> MetricsSnapshot {
        let snapshot = self.consciousness_state();
        let stats = self.cognitive.stats();
        let uptime = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64 - self.stats.start_time_ms;

        MetricsSnapshot {
            phi: snapshot.unified_phi as f64,
            coherence: snapshot.temporal_coherence as f64,
            is_conscious: snapshot.unified_phi > 0.5,
            cognitive_depth: format!("{:?}", snapshot.cognitive_depth),
            strategy: stats.current_strategy.clone(),
            in_flow: snapshot.in_flow,
            prediction_error: snapshot.prediction_error,
            emotional_valence: snapshot.unified_valence,
            emotional_arousal: snapshot.unified_arousal,
            timestamp_ms: uptime,
            uptime_secs: (uptime / 1000) as u64,
            total_cycles: self.stats.total_cycles,
            consciousness_level: snapshot.consciousness_level as f64,
            latency_ms: 0,
        }
    }

    /// Get Phi value
    pub fn phi(&self) -> f64 {
        self.consciousness_state().unified_phi as f64
    }

    /// Get coherence value
    pub fn coherence(&self) -> f64 {
        self.consciousness_state().temporal_coherence as f64
    }

    /// Check if conscious (Phi > 0.5)
    pub fn is_conscious(&self) -> bool {
        self.consciousness_state().unified_phi > 0.5
    }

    /// Get current cognitive depth
    pub fn cognitive_depth_str(&self) -> String {
        format!("{:?}", self.consciousness_state().cognitive_depth)
    }

    /// Get current response strategy
    pub fn current_strategy(&self) -> String {
        self.cognitive.stats().current_strategy.clone()
    }

    /// Check if in flow state
    pub fn in_flow(&self) -> bool {
        self.consciousness_state().in_flow
    }

    /// Get session uptime in seconds
    pub fn uptime_secs(&self) -> u64 {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64;
        (now - self.stats.start_time_ms) / 1000
    }

    /// Get total cognitive cycles
    pub fn total_cycles(&self) -> u64 {
        self.stats.total_cycles
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_session_creation() {
        let config = ReplSessionConfig::default();
        let session = ReplSession::new(config);
        assert!(session.is_ok());
    }

    #[test]
    fn test_session_warmup() {
        let config = ReplSessionConfig::default();
        let mut session = ReplSession::new(config).unwrap();
        session.warmup(5);
        assert!(session.stats.total_cycles == 0); // Warmup doesn't count
    }

    #[test]
    fn test_action_detection() {
        let config = ReplSessionConfig::default();
        let session = ReplSession::new(config).unwrap();

        assert!(session.is_action_command("!ls"));
        assert!(session.is_action_command("run echo hello"));
        assert!(session.is_action_command("execute pwd"));
        assert!(!session.is_action_command("hello world"));
    }

    #[test]
    fn test_process_conversation() {
        let config = ReplSessionConfig::default();
        let mut session = ReplSession::new(config).unwrap();

        let result = session.process("Hello, Symthaea");
        assert!(result.is_ok());

        let result = result.unwrap();
        assert!(!result.response.is_empty());
        assert!(session.history.len() == 1);
    }
}
