//! # Continuous Mind: The Integrated Consciousness System
//!
//! Provides the main orchestration layer for the conscious AI system,
//! integrating perception, reasoning, memory, and action into a unified
//! continuous-time cognitive architecture.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use symthaea_core::hdc::RealHV;

/// Configuration for the continuous mind
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MindConfig {
    /// Embedding dimension
    pub dimension: usize,
    /// Tick rate (Hz)
    pub tick_rate: f32,
    /// Working memory capacity
    pub working_memory_capacity: usize,
    /// Enable consciousness monitoring
    pub consciousness_monitoring: bool,
    /// Enable learning
    pub learning_enabled: bool,
    /// Learning rate
    pub learning_rate: f32,
    /// Minimum consciousness threshold for action
    pub min_consciousness: f64,
}

impl Default for MindConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            tick_rate: 10.0,
            working_memory_capacity: 7,
            consciousness_monitoring: true,
            learning_enabled: true,
            learning_rate: 0.01,
            min_consciousness: 0.1,
        }
    }
}

/// Current state of the mind
#[derive(Debug, Clone)]
pub struct MindState {
    /// Current consciousness level (phi) - integrated information measure
    pub consciousness_level: f64,
    /// Phi value (alias for consciousness_level for API compatibility)
    pub phi: f64,
    /// Meta-awareness / self-monitoring level
    pub meta_awareness: f64,
    /// Cognitive load (0.0 = idle, 1.0 = max)
    pub cognitive_load: f64,
    /// Current emotional valence (-1 to 1)
    pub emotional_valence: f32,
    /// Current arousal level (0 to 1)
    pub arousal: f32,
    /// Current focus/attention target
    pub attention_focus: Option<String>,
    /// Active goals
    pub active_goals: Vec<String>,
    /// Current thought embedding
    pub current_thought: RealHV,
    /// Is the mind active
    pub is_active: bool,
    /// Whether the mind considers itself conscious
    pub is_conscious: bool,
    /// Tick count (total cognitive cycles)
    pub tick: u64,
    /// Total cognitive cycles (alias for tick for API compatibility)
    pub total_cycles: u64,
    /// Time since awakening in milliseconds
    pub time_awake_ms: u64,
    /// Working memory utilization
    pub memory_utilization: f32,
    /// Processing latency (ms)
    pub processing_latency_ms: f64,
}

impl Default for MindState {
    fn default() -> Self {
        Self {
            consciousness_level: 0.5,
            phi: 0.5,
            meta_awareness: 0.0,
            cognitive_load: 0.0,
            emotional_valence: 0.0,
            arousal: 0.5,
            attention_focus: None,
            active_goals: Vec::new(),
            current_thought: RealHV::zero(512),
            is_active: false,
            is_conscious: false,
            tick: 0,
            total_cycles: 0,
            time_awake_ms: 0,
            memory_utilization: 0.0,
            processing_latency_ms: 0.0,
        }
    }
}

/// Input to the mind
#[derive(Debug, Clone)]
pub struct MindInput {
    /// Input type
    pub input_type: InputType,
    /// Content embedding
    pub content: RealHV,
    /// Priority
    pub priority: f32,
    /// Metadata
    pub metadata: HashMap<String, String>,
}

/// Type of input
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InputType {
    /// Sensory perception
    Perception,
    /// Language/text
    Language,
    /// Internal thought
    Thought,
    /// Goal/intention
    Goal,
    /// Memory recall
    Memory,
    /// Feedback signal
    Feedback,
}

/// Output from the mind
#[derive(Debug, Clone)]
pub struct MindOutput {
    /// Output type
    pub output_type: OutputType,
    /// Content
    pub content: String,
    /// Embedding representation
    pub embedding: RealHV,
    /// Confidence
    pub confidence: f32,
    /// Associated emotion
    pub emotional_tone: f32,
}

/// Type of output
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OutputType {
    /// Verbal response
    Speech,
    /// Internal thought
    Thought,
    /// Motor action
    Action,
    /// Attention shift
    Attention,
    /// Memory storage
    Memorize,
}

/// The continuous mind system
pub struct ContinuousMind {
    /// Configuration
    config: MindConfig,
    /// Current state
    state: MindState,
    /// Working memory
    working_memory: Vec<RealHV>,
    /// Goal stack
    goals: Vec<Goal>,
    /// Input queue
    input_queue: Vec<MindInput>,
    /// Statistics
    stats: MindStats,
    /// Time of awakening
    awaken_time: std::time::Instant,
    /// Shutdown has been requested
    shutdown_requested: bool,
}

/// A goal in the goal stack
#[derive(Debug, Clone)]
pub struct Goal {
    /// Goal ID
    pub id: String,
    /// Goal description
    pub description: String,
    /// Goal embedding
    pub embedding: RealHV,
    /// Priority
    pub priority: f32,
    /// Progress (0-1)
    pub progress: f32,
    /// Is active
    pub is_active: bool,
}

/// Statistics for the mind
#[derive(Debug, Clone, Default)]
pub struct MindStats {
    /// Total ticks
    pub total_ticks: u64,
    /// Inputs processed
    pub inputs_processed: u64,
    /// Outputs generated
    pub outputs_generated: u64,
    /// Goals completed
    pub goals_completed: u64,
    /// Average consciousness level
    pub avg_consciousness: f64,
    /// Peak consciousness level
    pub peak_consciousness: f64,
}

impl ContinuousMind {
    /// Create a new continuous mind
    pub fn new(config: MindConfig) -> Self {
        let dim = config.dimension;
        Self {
            config,
            state: MindState {
                current_thought: RealHV::zero(dim),
                ..Default::default()
            },
            working_memory: Vec::new(),
            goals: Vec::new(),
            input_queue: Vec::new(),
            stats: MindStats::default(),
            awaken_time: std::time::Instant::now(),
            shutdown_requested: false,
        }
    }

    /// Process one tick of the mind
    pub fn tick(&mut self) -> Option<MindOutput> {
        let start = std::time::Instant::now();

        self.state.tick += 1;
        self.stats.total_ticks += 1;

        // Process inputs
        self.process_inputs();

        // Update consciousness level
        self.update_consciousness();

        // Process goals
        self.process_goals();

        // Generate output if appropriate
        let output = self.generate_output();

        // Update state
        self.state.processing_latency_ms = start.elapsed().as_secs_f64() * 1000.0;
        self.state.memory_utilization =
            self.working_memory.len() as f32 / self.config.working_memory_capacity as f32;

        // Update statistics
        self.stats.avg_consciousness =
            (self.stats.avg_consciousness * (self.stats.total_ticks - 1) as f64
                + self.state.consciousness_level) / self.stats.total_ticks as f64;

        if self.state.consciousness_level > self.stats.peak_consciousness {
            self.stats.peak_consciousness = self.state.consciousness_level;
        }

        output
    }

    /// Process queued inputs
    fn process_inputs(&mut self) {
        // Sort by priority
        self.input_queue.sort_by(|a, b| b.priority.partial_cmp(&a.priority).unwrap());

        // Process top inputs
        while let Some(input) = self.input_queue.pop() {
            self.stats.inputs_processed += 1;

            // Add to working memory
            if self.working_memory.len() < self.config.working_memory_capacity {
                self.working_memory.push(input.content.clone());
            } else {
                // Replace oldest item
                self.working_memory.remove(0);
                self.working_memory.push(input.content.clone());
            }

            // Update current thought
            self.state.current_thought = self.state.current_thought.bind(&input.content);

            // Handle specific input types
            match input.input_type {
                InputType::Goal => {
                    let goal = Goal {
                        id: format!("goal_{}", self.goals.len()),
                        description: input.metadata.get("description").cloned().unwrap_or_default(),
                        embedding: self.state.current_thought.clone(),
                        priority: input.priority,
                        progress: 0.0,
                        is_active: true,
                    };
                    self.goals.push(goal);
                }
                InputType::Feedback => {
                    // Adjust emotional state based on feedback
                    if let Some(valence_str) = input.metadata.get("valence") {
                        if let Ok(valence) = valence_str.parse::<f32>() {
                            self.state.emotional_valence =
                                (self.state.emotional_valence + valence * 0.3).clamp(-1.0, 1.0);
                        }
                    }
                }
                _ => {}
            }
        }
    }

    /// Update consciousness level
    fn update_consciousness(&mut self) {
        // Simple IIT-inspired phi calculation
        // Based on working memory integration
        if self.working_memory.is_empty() {
            self.state.consciousness_level = 0.1;
            return;
        }

        let mut total_integration = 0.0;
        for i in 0..self.working_memory.len() {
            for j in (i + 1)..self.working_memory.len() {
                let similarity = self.working_memory[i].similarity(&self.working_memory[j]);
                total_integration += (1.0 - similarity.abs()) as f64;
            }
        }

        let pairs = self.working_memory.len() * (self.working_memory.len() - 1) / 2;
        if pairs > 0 {
            self.state.consciousness_level = (total_integration / pairs as f64).clamp(0.0, 1.0);
        }
    }

    /// Process active goals
    fn process_goals(&mut self) {
        for goal in self.goals.iter_mut() {
            if !goal.is_active {
                continue;
            }

            // Simulate progress based on consciousness and effort
            let progress_increment = self.state.consciousness_level as f32 * 0.01;
            goal.progress = (goal.progress + progress_increment).min(1.0);

            if goal.progress >= 1.0 {
                goal.is_active = false;
                self.stats.goals_completed += 1;
            }
        }

        // Update active goals list
        self.state.active_goals = self.goals.iter()
            .filter(|g| g.is_active)
            .map(|g| g.id.clone())
            .collect();
    }

    /// Generate output if appropriate
    fn generate_output(&mut self) -> Option<MindOutput> {
        // Only generate output if consciousness is above threshold
        if self.state.consciousness_level < self.config.min_consciousness {
            return None;
        }

        // Generate thought output periodically
        if self.state.tick % 10 == 0 && !self.working_memory.is_empty() {
            self.stats.outputs_generated += 1;

            return Some(MindOutput {
                output_type: OutputType::Thought,
                content: format!("Thinking about {} items in working memory", self.working_memory.len()),
                embedding: self.state.current_thought.clone(),
                confidence: self.state.consciousness_level as f32,
                emotional_tone: self.state.emotional_valence,
            });
        }

        None
    }

    /// Add input to the mind
    pub fn input(&mut self, input: MindInput) {
        self.input_queue.push(input);
    }

    /// Add a perception input
    pub fn perceive(&mut self, content: RealHV) {
        self.input(MindInput {
            input_type: InputType::Perception,
            content,
            priority: 0.5,
            metadata: HashMap::new(),
        });
    }

    /// Set a goal
    pub fn set_goal(&mut self, description: impl Into<String>, embedding: RealHV, priority: f32) {
        let mut metadata = HashMap::new();
        metadata.insert("description".to_string(), description.into());

        self.input(MindInput {
            input_type: InputType::Goal,
            content: embedding,
            priority,
            metadata,
        });
    }

    /// Activate the mind
    pub fn activate(&mut self) {
        self.state.is_active = true;
    }

    /// Deactivate the mind
    pub fn deactivate(&mut self) {
        self.state.is_active = false;
    }

    /// Get current state
    pub fn state(&self) -> &MindState {
        &self.state
    }

    /// Get configuration
    pub fn config(&self) -> &MindConfig {
        &self.config
    }

    /// Get statistics
    pub fn stats(&self) -> &MindStats {
        &self.stats
    }

    /// Get working memory contents
    pub fn working_memory(&self) -> &[RealHV] {
        &self.working_memory
    }

    /// Get active goals
    pub fn active_goals(&self) -> Vec<&Goal> {
        self.goals.iter().filter(|g| g.is_active).collect()
    }

    /// Awaken the mind - start consciousness processing
    pub fn awaken(&mut self) {
        self.state.is_active = true;
        self.state.is_conscious = true;
        // Record awakening time
        self.awaken_time = std::time::Instant::now();
    }

    /// Get a snapshot of the current mind state
    pub fn snapshot(&self) -> MindState {
        let mut state = self.state.clone();
        // Synchronize alias fields
        state.phi = state.consciousness_level;
        state.total_cycles = state.tick;
        state.time_awake_ms = self.awaken_time.elapsed().as_millis() as u64;
        // Compute meta-awareness from processing metrics
        state.meta_awareness = (state.consciousness_level * 0.7
            + state.memory_utilization as f64 * 0.3).min(1.0);
        // Compute cognitive load from memory and processing
        state.cognitive_load = state.memory_utilization as f64;
        // Determine consciousness threshold
        state.is_conscious = state.consciousness_level >= self.config.min_consciousness;
        state
    }

    /// Request graceful shutdown of the mind
    pub fn request_shutdown(&mut self) {
        self.state.is_active = false;
        self.state.is_conscious = false;
        self.shutdown_requested = true;
    }

    /// Check if shutdown was requested
    pub fn is_shutdown_requested(&self) -> bool {
        self.shutdown_requested
    }
}

impl Default for ContinuousMind {
    fn default() -> Self {
        Self::new(MindConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mind_creation() {
        let mind = ContinuousMind::default();
        assert_eq!(mind.state.tick, 0);
        assert!(!mind.state.is_active);
    }

    #[test]
    fn test_mind_tick() {
        let mut mind = ContinuousMind::default();
        mind.activate();
        mind.tick();
        assert_eq!(mind.state.tick, 1);
    }

    #[test]
    fn test_perception() {
        let mut mind = ContinuousMind::default();
        mind.perceive(RealHV::random(512, 42));
        mind.tick();
        assert_eq!(mind.working_memory.len(), 1);
    }

    #[test]
    fn test_goal_setting() {
        let mut mind = ContinuousMind::default();
        mind.set_goal("Test goal", RealHV::random(512, 42), 1.0);
        mind.tick();
        assert!(!mind.active_goals().is_empty());
    }

    #[test]
    fn test_consciousness_update() {
        let mut mind = ContinuousMind::default();

        // Add multiple diverse items to working memory (different seeds for diversity)
        for i in 0..5 {
            mind.perceive(RealHV::random(512, 42 + i as u64));
        }

        for _ in 0..5 {
            mind.tick();
        }

        // Consciousness should be non-zero with items in memory
        assert!(mind.state.consciousness_level > 0.0);
    }
}
