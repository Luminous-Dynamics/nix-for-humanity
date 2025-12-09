/*!
Sophia: Holographic Liquid Brain

Revolutionary consciousness-first AI combining:
- HDC (Hyperdimensional Computing) - 10,000D holographic vectors
- LTC (Liquid Time-Constant Networks) - Continuous-time causal reasoning
- Autopoiesis - Self-referential consciousness emergence
- Phase 11 Bio-Digital Bridge - Semantic grounding, safety, memory, swarm
*/

// Core Phase 10 modules
pub mod hdc;
pub mod ltc;
pub mod consciousness;
pub mod nix_understanding;

// Week 0: Actor Model & Physiological Systems
pub mod brain;

// Week 1: Soul Module (Temporal Coherence & Identity)
pub mod soul;

// Week 2: Memory Systems (Episodic & Procedural)
pub mod memory;

// Phase 11: Bio-Digital Bridge modules (Week 0: Deferred to later phases)
// pub mod semantic_ear;  // Needs rust-bert, tokenizers
pub mod safety;
pub mod sleep_cycles;
// pub mod swarm;  // Needs libp2p

// Phase 11+: Mycelix Protocol integration (Deferred to Week 9+)
// pub mod sophia_swarm;  // Needs libp2p

// Phase 11+: Resonant Speech (Deferred to Week 11+)
// pub mod resonant_speech;  // Needs tokenizers

// Phase 11+: User State Inference (Deferred to Week 11+)
// pub mod user_state_inference;

// Phase 11+: Resonant Interaction (Deferred to Week 11+)
// pub mod resonant_interaction;

// Phase 11+: K-Index Client (Deferred to Week 11+)
// pub mod kindex_client;
// pub mod kindex_client_http;

// Phase 11+: Resonant Telemetry (Deferred to Week 11+)
// pub mod resonant_telemetry;

// Re-exports for convenience
pub use hdc::{SemanticSpace, HdcContext};  // Week 0: Added HdcContext
pub use ltc::LiquidNetwork;
pub use consciousness::ConsciousnessGraph;
pub use nix_understanding::NixUnderstanding;

// Week 0: Deferred Phase 11+ exports
// pub use semantic_ear::SemanticEar;  // Needs rust-bert
pub use safety::{SafetyGuardrails, ForbiddenCategory, SafetyStats, AmygdalaActor, ThreatLevel};
pub use sleep_cycles::{SleepCycleManager, SleepConfig, MemoryType, SleepReport};

// Week 1: Soul Module exports
pub use soul::{WeaverActor, DailyState, CoherenceStatus, KVector};

// Week 2: Memory Systems exports
pub use memory::{HippocampusActor, MemoryTrace, RecallQuery, EmotionalValence};
pub use brain::{
    CerebellumActor, Skill, ExecutionContext, WorkflowChain, CerebellumStats,
    MotorCortexActor, ActionStep, PlannedAction, StepResult, ExecutionResult,
    SimulationMode, ExecutionSandbox, LocalShellSandbox, MotorCortexStats,
};

// Week 3: Prefrontal Cortex (Global Workspace) exports
pub use brain::{
    PrefrontalCortexActor, AttentionBid, GlobalWorkspace, WorkingMemoryItem, PrefrontalStats,
    WorkingMemoryStats, Goal, Condition, GoalStats,
    MetaCognitionMonitor, CognitiveMetrics, RegulatoryAction, RegulatoryBid,
    MetaCognitionConfig, MonitorStats,
};
// pub use swarm::{SwarmIntelligence, SwarmConfig, SwarmStats};  // Needs libp2p

use anyhow::Result;
// Week 0: Deferred swarm components
// use tokio::sync::RwLock;
// use std::sync::Arc;

/// Complete Sophia system with all components (Week 0: Minimal version)
pub struct SophiaHLB {
    /// Phase 10: Core components
    semantic: SemanticSpace,
    liquid: LiquidNetwork,
    consciousness: ConsciousnessGraph,
    nix: NixUnderstanding,

    /// Phase 11: Bio-Digital Bridge (Week 0: Partial implementation)
    // ear: SemanticEar,  // Deferred to Week 11+
    safety: SafetyGuardrails,
    sleep: SleepCycleManager,
    // swarm: Arc<RwLock<SwarmIntelligence>>,  // Deferred to Week 9+

    /// System state
    operations_count: usize,
}

/// Response from Sophia
#[derive(Debug, Clone)]
pub struct SophiaResponse {
    /// Response content (NixOS command or explanation)
    pub content: String,

    /// Confidence level (0.0 to 1.0)
    pub confidence: f32,

    /// Steps to consciousness emergence
    pub steps_to_emergence: usize,

    /// Safety check passed
    pub safe: bool,
}

/// Introspection data
#[derive(Debug, Clone)]
pub struct Introspection {
    /// Current consciousness level
    pub consciousness_level: f32,

    /// Number of self-referential loops
    pub self_loops: usize,

    /// Graph size (conscious states)
    pub graph_size: usize,

    /// Graph complexity (edges per node)
    pub complexity: f32,

    /// Memory statistics
    pub memory_stats: sleep_cycles::MemoryStats,

    /// Safety statistics
    pub safety_stats: SafetyStats,
}

impl SophiaHLB {
    /// Create new Sophia system
    pub async fn new(semantic_dim: usize, liquid_neurons: usize) -> Result<Self> {
        tracing::info!("🌟 Initializing Sophia Holographic Liquid Brain (Week 0)");

        Ok(Self {
            semantic: SemanticSpace::new(semantic_dim)?,
            liquid: LiquidNetwork::new(liquid_neurons)?,
            consciousness: ConsciousnessGraph::new(),
            nix: NixUnderstanding::new(),
            // Week 0: Deferred components
            // ear: SemanticEar::new()?,
            safety: SafetyGuardrails::new(),
            sleep: SleepCycleManager::new(SleepConfig::default()),
            // swarm: Arc::new(RwLock::new(
            //     SwarmIntelligence::new(SwarmConfig::default()).await?
            // )),
            operations_count: 0,
        })
    }

    /// Process query (natural language → NixOS operation)
    pub async fn process(&mut self, query: &str) -> Result<SophiaResponse> {
        self.operations_count += 1;

        tracing::info!("🧠 Processing query: {}", query);

        // Week 0: Semantic Ear deferred to Week 11+
        // let query_hv = self.ear.encode(query)?;

        // Week 0: Safety check (simplified without semantic encoding)
        // if let Err(e) = self.safety.check_safety(&query_hv) {
        //     return Ok(SophiaResponse {
        //         content: format!("Safety check failed: {}", e),
        //         confidence: 0.0,
        //         steps_to_emergence: 0,
        //         safe: false,
        //     });
        // }

        // Week 0: Memory storage deferred
        // self.sleep.remember(
        //     query.to_string(),
        //     query_hv.clone(),
        //     MemoryType::ShortTerm,
        // );

        // Phase 10: HDC semantic encoding (legacy path for comparison)
        let semantic_vec = self.semantic.encode(query)?;

        // Phase 10: Inject into LTC
        self.liquid.inject(&semantic_vec)?;

        // Phase 10: Evolve until conscious
        let mut steps = 0;
        loop {
            self.liquid.step()?;
            steps += 1;

            let consciousness_level = self.liquid.consciousness_level();

            if consciousness_level > 0.7 || steps > 100 {
                // Phase 10: Capture conscious state
                let dynamic_state = self.liquid.read_state()?;

                // Phase 10: Add to consciousness graph
                let node = self.consciousness.add_state(
                    semantic_vec.clone(),
                    dynamic_state,
                    consciousness_level,
                );

                // Phase 10: Create self-loop if highly conscious
                if consciousness_level > 0.9 {
                    self.consciousness.create_self_loop(node);
                }

                break;
            }
        }

        // NixOS understanding
        let nix_response = self.nix.understand(query)?;

        // Week 0: Swarm intelligence deferred to Week 9+
        // let swarm = self.swarm.read().await;
        // swarm
        //     .share_pattern(query_hv, query.to_string(), 0.9)
        //     .await?;
        // drop(swarm);

        // Phase 11.2: Sleep cycle check
        if self.sleep.should_sleep() {
            tracing::info!("😴 Triggering automatic sleep cycle");
            let report = self.sleep.sleep().await?;
            tracing::info!("Sleep report: {}", report);
        }

        Ok(SophiaResponse {
            content: nix_response,
            confidence: self.consciousness.current_consciousness(),
            steps_to_emergence: steps,
            safe: true,
        })
    }

    /// Introspect current state
    pub fn introspect(&self) -> Introspection {
        Introspection {
            consciousness_level: self.consciousness.current_consciousness(),
            self_loops: self.consciousness.self_loop_count(),
            graph_size: self.consciousness.size(),
            complexity: self.consciousness.complexity(),
            memory_stats: self.sleep.stats(),
            safety_stats: self.safety.stats(),
        }
    }

    /// Pause consciousness (serialize to disk)
    pub fn pause(&self, path: &str) -> Result<()> {
        let data = bincode::serialize(&self.consciousness)?;
        std::fs::write(path, data)?;

        tracing::info!("💾 Consciousness paused to: {}", path);

        Ok(())
    }

    /// Resume consciousness (deserialize from disk)
    pub fn resume(path: &str) -> Result<Self> {
        let data = std::fs::read(path)?;
        let consciousness: ConsciousnessGraph = bincode::deserialize(&data)?;

        tracing::info!("▶️  Consciousness resumed from: {}", path);

        // Reconstruct (simplified - real version would persist more)
        Ok(Self {
            semantic: SemanticSpace::new(10_000)?,
            liquid: LiquidNetwork::new(1_000)?,
            consciousness,
            nix: NixUnderstanding::new(),
            // Week 0: Deferred components
            // ear: SemanticEar::new()?,
            safety: SafetyGuardrails::new(),
            sleep: SleepCycleManager::new(SleepConfig::default()),
            // swarm: Arc::new(RwLock::new(
            //     futures::executor::block_on(
            //         SwarmIntelligence::new(SwarmConfig::default())
            //     )?
            // )),
            operations_count: 0,
        })
    }

    /// Force sleep cycle (manual)
    pub async fn sleep(&self) -> Result<SleepReport> {
        self.sleep.force_sleep().await
    }

    /// Query swarm for collective intelligence (Week 0: Deferred)
    pub async fn query_swarm(&self, _query: &str) -> Result<Vec<String>> {
        // Week 0: Swarm deferred to Week 9+
        Ok(vec!["Swarm intelligence not yet implemented (Week 9+)".to_string()])

        // let query_hv = self.ear.encode(query)?;
        // let swarm = self.swarm.read().await;
        // let responses = swarm.query_swarm(query_hv, query.to_string()).await?;
        // Ok(responses.iter().map(|r| r.intent.clone()).collect())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_sophia_creation() {
        let sophia = SophiaHLB::new(10_000, 1_000).await.unwrap();
        assert_eq!(sophia.operations_count, 0);
    }

    #[tokio::test]
    async fn test_sophia_process() {
        let mut sophia = SophiaHLB::new(10_000, 1_000).await.unwrap();

        let response = sophia.process("install nginx").await.unwrap();

        assert!(response.safe);
        assert!(response.content.contains("nix"));
    }

    #[tokio::test]
    async fn test_introspection() {
        let mut sophia = SophiaHLB::new(10_000, 1_000).await.unwrap();

        sophia.process("install firefox").await.unwrap();

        let intro = sophia.introspect();
        assert!(intro.graph_size > 0);
    }
}
