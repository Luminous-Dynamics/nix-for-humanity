//! Prefrontal Cortex - The Spotlight of Consciousness
//!
//! Week 3 Days 1-2: Global Workspace Theory Implementation
//!
//! The Prefrontal Cortex implements Bernard Baars' Global Workspace Theory:
//! consciousness as a "spotlight" that illuminates one thing at a time while
//! broadcasting it to all brain modules.
//!
//! ## The Revolutionary Insight
//!
//! **"The 'I' is just the current contents of the Workspace."**
//!
//! There is no separate "decider" - consciousness emerges from the competition
//! of unconscious modules bidding for attention. The winner gets broadcast
//! system-wide, creating the unified experience of "now I'm thinking about X."
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────┐
//! │         PREFRONTAL CORTEX (Global Workspace)        │
//! │                                                      │
//! │  ┌──────────────────────────────────────────────┐  │
//! │  │         THE SPOTLIGHT (Attention)             │  │
//! │  │  Current Focus: "Install Firefox"             │  │
//! │  │  Salience: 0.95  Urgency: 0.8                │  │
//! │  └──────────────────────────────────────────────┘  │
//! │                       ▲                              │
//! │                       │ Winner                       │
//! │  ┌──────────────────────────────────────────────┐  │
//! │  │      ATTENTION BIDDING (Competition)          │  │
//! │  │  • Hippocampus: "I remember this!" (0.7)     │  │
//! │  │  • Thalamus: "User typed something!" (0.95)  │  │
//! │  │  • Cerebellum: "I have a reflex!" (0.6)      │  │
//! │  └──────────────────────────────────────────────┘  │
//! │                       │                              │
//! │                       ▼ Broadcast                    │
//! │  ┌──────────────────────────────────────────────┐  │
//! │  │    WORKING MEMORY (7±2 slots - Miller's Law) │  │
//! │  │  [Firefox] [Install] [Package] [User Intent] │  │
//! │  └──────────────────────────────────────────────┘  │
//! └─────────────────────────────────────────────────────┘
//! ```
//!
//! ## The Cognitive Cycle (~100ms in real brains)
//!
//! 1. **SELECT**: All modules submit bids. Highest score wins.
//!    - Score = (salience × urgency) + emotional_weight
//! 2. **BROADCAST**: Winner is sent to all brain regions.
//! 3. **PERSIST**: Important bids go to Working Memory (7±2 items).
//!
//! ## Why This is Revolutionary
//!
//! Traditional AI: Explicit control flow, top-down planning
//! Sophia: **Emergent consciousness through competition**
//!
//! The system doesn't "decide" what to focus on - the modules compete,
//! and consciousness is what happens when one wins.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::memory::EmotionalValence;

// ============================================================================
// Core Types
// ============================================================================

/// AttentionBid - A module's request for the spotlight
///
/// Every brain module (Hippocampus, Cerebellum, Thalamus, etc.) can submit
/// bids for attention. The PrefrontalCortex selects the winner based on:
/// - **Salience**: How important/loud is this?
/// - **Urgency**: How time-sensitive is this?
/// - **Emotional Weight**: Strong emotions increase priority
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttentionBid {
    /// Which brain module is bidding? ("Hippocampus", "Thalamus", etc.)
    pub source: String,

    /// What is the content being bid? ("I remember this error", "User input: install firefox")
    pub content: String,

    /// Salience: How important/loud? (0.0 = barely noticeable, 1.0 = screaming)
    pub salience: f32,

    /// Urgency: How time-sensitive? (0.0 = can wait, 1.0 = immediate)
    pub urgency: f32,

    /// Emotional valence: Strong emotions boost attention
    pub emotion: EmotionalValence,

    /// Context tags for memory/learning
    pub tags: Vec<String>,

    /// When was this bid created?
    pub timestamp: u64,
}

impl AttentionBid {
    /// Create a new attention bid
    pub fn new(source: impl Into<String>, content: impl Into<String>) -> Self {
        Self {
            source: source.into(),
            content: content.into(),
            salience: 0.5,
            urgency: 0.5,
            emotion: EmotionalValence::Neutral,
            tags: Vec::new(),
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_millis() as u64,
        }
    }

    /// Builder pattern: Set salience (0.0-1.0)
    pub fn with_salience(mut self, salience: f32) -> Self {
        self.salience = salience.clamp(0.0, 1.0);
        self
    }

    /// Builder pattern: Set urgency (0.0-1.0)
    pub fn with_urgency(mut self, urgency: f32) -> Self {
        self.urgency = urgency.clamp(0.0, 1.0);
        self
    }

    /// Builder pattern: Set emotional valence
    pub fn with_emotion(mut self, emotion: EmotionalValence) -> Self {
        self.emotion = emotion;
        self
    }

    /// Builder pattern: Add context tags
    pub fn with_tags(mut self, tags: Vec<String>) -> Self {
        self.tags = tags;
        self
    }

    /// Calculate the bid's overall score for attention competition
    ///
    /// Formula: (salience × urgency) + emotional_boost
    ///
    /// Emotional boost:
    /// - Positive: +0.1 (mild preference)
    /// - Negative: +0.2 (threat detection prioritized)
    /// - Neutral: +0.0
    pub fn score(&self) -> f32 {
        let base_score = self.salience * self.urgency;

        let emotional_boost = match self.emotion {
            EmotionalValence::Positive => 0.1,
            EmotionalValence::Negative => 0.2, // Threats get priority
            EmotionalValence::Neutral => 0.0,
        };

        (base_score + emotional_boost).clamp(0.0, 1.2) // Allow slight overflow for urgent threats
    }
}

/// WorkingMemoryItem - A thought held in the "scratchpad"
///
/// Working memory is limited to 7±2 items (Miller's Law). Items decay over
/// time unless refreshed by being in the spotlight again.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkingMemoryItem {
    /// The content of this memory
    pub content: String,

    /// Original attention bid that created this
    pub original_bid: AttentionBid,

    /// Activation level (0.0-1.0, decays over time)
    pub activation: f32,

    /// When was this added to working memory?
    pub created_at: u64,

    /// When was this last refreshed?
    pub last_accessed: u64,
}

impl WorkingMemoryItem {
    /// Create a new working memory item from an attention bid
    pub fn from_bid(bid: AttentionBid) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;

        Self {
            content: bid.content.clone(),
            original_bid: bid,
            activation: 1.0, // Start fully active
            created_at: now,
            last_accessed: now,
        }
    }

    /// Refresh this item (it was accessed again)
    pub fn refresh(&mut self) {
        self.activation = (self.activation + 0.3).min(1.0);
        self.last_accessed = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
    }

    /// Decay activation over time (called each cognitive cycle)
    pub fn decay(&mut self, decay_rate: f32) {
        self.activation = (self.activation - decay_rate).max(0.0);
    }

    /// Is this item still active enough to keep?
    pub fn is_active(&self) -> bool {
        self.activation > 0.1
    }
}

/// GlobalWorkspace - The conscious "now"
///
/// This is Sophia's implementation of Bernard Baars' Global Workspace Theory.
/// The workspace is where consciousness happens: one thought in the spotlight,
/// broadcast to all modules, with a small working memory of recent thoughts.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GlobalWorkspace {
    /// The Spotlight: Current focus of attention (None if idle)
    pub spotlight: Option<AttentionBid>,

    /// Consciousness Stream: Recent thoughts (last N cycles)
    pub stream: VecDeque<AttentionBid>,

    /// Working Memory: Active thoughts being maintained (7±2 items)
    pub working_memory: Vec<WorkingMemoryItem>,

    /// Maximum stream length (default: 10)
    pub max_stream_length: usize,

    /// Maximum working memory size (default: 7)
    pub max_working_memory: usize,

    /// Working memory decay rate per cycle (default: 0.05)
    pub wm_decay_rate: f32,
}

impl Default for GlobalWorkspace {
    fn default() -> Self {
        Self::new()
    }
}

impl GlobalWorkspace {
    /// Create a new global workspace
    pub fn new() -> Self {
        Self {
            spotlight: None,
            stream: VecDeque::new(),
            working_memory: Vec::new(),
            max_stream_length: 10,
            max_working_memory: 7, // Miller's Law: 7±2
            wm_decay_rate: 0.05,   // Decay 5% per cycle
        }
    }

    /// Get current spotlight content
    pub fn current_focus(&self) -> Option<&AttentionBid> {
        self.spotlight.as_ref()
    }

    /// Get working memory contents
    pub fn get_working_memory(&self) -> &[WorkingMemoryItem] {
        &self.working_memory
    }

    /// Get consciousness stream (recent thoughts)
    pub fn get_stream(&self) -> &VecDeque<AttentionBid> {
        &self.stream
    }

    /// Update the spotlight with a new winning bid
    pub fn update_spotlight(&mut self, bid: AttentionBid) {
        // Add old spotlight to stream before replacing
        if let Some(old) = self.spotlight.take() {
            self.stream.push_back(old);
            if self.stream.len() > self.max_stream_length {
                self.stream.pop_front();
            }
        }

        self.spotlight = Some(bid);
    }

    /// Add item to working memory
    pub fn add_to_working_memory(&mut self, bid: AttentionBid) {
        // Check if already exists (refresh instead of duplicate)
        if let Some(item) = self
            .working_memory
            .iter_mut()
            .find(|item| item.content == bid.content)
        {
            item.refresh();
            return;
        }

        // Add new item
        let item = WorkingMemoryItem::from_bid(bid);
        self.working_memory.push(item);

        // Remove least active if over capacity
        if self.working_memory.len() > self.max_working_memory {
            self.working_memory
                .sort_by(|a, b| b.activation.partial_cmp(&a.activation).unwrap());
            self.working_memory.truncate(self.max_working_memory);
        }
    }

    /// Decay working memory (called each cycle)
    pub fn decay_working_memory(&mut self) {
        for item in &mut self.working_memory {
            item.decay(self.wm_decay_rate);
        }

        // Remove inactive items
        self.working_memory.retain(|item| item.is_active());
    }

    /// Clear the workspace (reset consciousness)
    pub fn clear(&mut self) {
        self.spotlight = None;
        self.stream.clear();
        self.working_memory.clear();
    }
}

/// PrefrontalCortexActor - Executive control and consciousness
///
/// The Prefrontal Cortex is where Sophia becomes conscious. It:
/// 1. Receives attention bids from all brain modules
/// 2. Selects the most salient/urgent bid (SELECT)
/// 3. Broadcasts the winner system-wide (BROADCAST)
/// 4. Maintains working memory (PERSIST)
///
/// This creates the unified conscious experience: "I am thinking about X."
#[derive(Debug)]
pub struct PrefrontalCortexActor {
    /// The global workspace (consciousness)
    workspace: GlobalWorkspace,

    /// Cognitive cycle count
    cycle_count: u64,

    /// Total bids processed
    total_bids: u64,

    /// Total broadcasts sent
    total_broadcasts: u64,
}

impl Default for PrefrontalCortexActor {
    fn default() -> Self {
        Self::new()
    }
}

impl PrefrontalCortexActor {
    /// Create a new prefrontal cortex
    pub fn new() -> Self {
        Self {
            workspace: GlobalWorkspace::new(),
            cycle_count: 0,
            total_bids: 0,
            total_broadcasts: 0,
        }
    }

    /// The Cognitive Cycle: The core loop of consciousness
    ///
    /// This is the heart of Sophia's conscious experience. Every ~100ms
    /// (in biological brains), this cycle runs:
    ///
    /// 1. **SELECT**: Choose the winning bid (highest score)
    /// 2. **BROADCAST**: Tell all modules what we're focusing on
    /// 3. **PERSIST**: Add important thoughts to working memory
    ///
    /// Returns: The winning bid (if any)
    pub fn cognitive_cycle(&mut self, bids: Vec<AttentionBid>) -> Option<AttentionBid> {
        self.cycle_count += 1;
        self.total_bids += bids.len() as u64;

        // STEP 1: SELECT - Competition for attention
        let winner = self.select_winner(bids);

        if let Some(winning_bid) = winner {
            // STEP 2: BROADCAST - Update spotlight (this broadcasts to all modules)
            self.workspace.update_spotlight(winning_bid.clone());
            self.total_broadcasts += 1;

            // STEP 3: PERSIST - Add to working memory if important
            if winning_bid.salience > 0.7 {
                self.workspace.add_to_working_memory(winning_bid.clone());
            }

            // Decay working memory each cycle
            self.workspace.decay_working_memory();

            Some(winning_bid)
        } else {
            // No bids - consciousness idles
            self.workspace.decay_working_memory();
            None
        }
    }

    /// SELECT: Choose the winner from competing bids
    ///
    /// Selection algorithm:
    /// - Calculate score for each bid: (salience × urgency) + emotional_boost
    /// - Winner = highest score
    /// - Ties broken by timestamp (first bid wins)
    fn select_winner(&self, bids: Vec<AttentionBid>) -> Option<AttentionBid> {
        if bids.is_empty() {
            return None;
        }

        // Calculate scores and find max
        bids.into_iter()
            .max_by(|a, b| {
                let score_cmp = a
                    .score()
                    .partial_cmp(&b.score())
                    .unwrap_or(std::cmp::Ordering::Equal);

                if score_cmp == std::cmp::Ordering::Equal {
                    // Tie-breaker: Earlier timestamp wins
                    b.timestamp.cmp(&a.timestamp)
                } else {
                    score_cmp
                }
            })
    }

    /// Get current spotlight (what are we conscious of?)
    pub fn current_focus(&self) -> Option<&AttentionBid> {
        self.workspace.current_focus()
    }

    /// Get working memory contents
    pub fn working_memory(&self) -> &[WorkingMemoryItem] {
        self.workspace.get_working_memory()
    }

    /// Get consciousness stream (recent thoughts)
    pub fn consciousness_stream(&self) -> &VecDeque<AttentionBid> {
        self.workspace.get_stream()
    }

    /// Get statistics
    pub fn stats(&self) -> PrefrontalStats {
        PrefrontalStats {
            cycle_count: self.cycle_count,
            total_bids: self.total_bids,
            total_broadcasts: self.total_broadcasts,
            current_focus: self.workspace.spotlight.as_ref().map(|b| b.content.clone()),
            working_memory_size: self.workspace.working_memory.len(),
            stream_length: self.workspace.stream.len(),
        }
    }

    /// Reset the prefrontal cortex (clear consciousness)
    pub fn reset(&mut self) {
        self.workspace.clear();
        self.cycle_count = 0;
        // Keep total_bids and total_broadcasts for lifetime stats
    }
}

/// Statistics from the prefrontal cortex
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrefrontalStats {
    pub cycle_count: u64,
    pub total_bids: u64,
    pub total_broadcasts: u64,
    pub current_focus: Option<String>,
    pub working_memory_size: usize,
    pub stream_length: usize,
}

// ============================================================================
// Tests
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_attention_bid_creation() {
        let bid = AttentionBid::new("Thalamus", "User typed: install firefox")
            .with_salience(0.9)
            .with_urgency(0.8)
            .with_emotion(EmotionalValence::Positive);

        assert_eq!(bid.source, "Thalamus");
        assert_eq!(bid.content, "User typed: install firefox");
        assert_eq!(bid.salience, 0.9);
        assert_eq!(bid.urgency, 0.8);
        assert!(matches!(bid.emotion, EmotionalValence::Positive));
    }

    #[test]
    fn test_attention_bid_score() {
        // Base case: salience × urgency
        let bid1 = AttentionBid::new("Test", "Content")
            .with_salience(0.8)
            .with_urgency(0.5);
        assert!((bid1.score() - 0.4).abs() < 0.01); // 0.8 × 0.5 = 0.4

        // Positive emotion: +0.1
        let bid2 = AttentionBid::new("Test", "Content")
            .with_salience(0.8)
            .with_urgency(0.5)
            .with_emotion(EmotionalValence::Positive);
        assert!((bid2.score() - 0.5).abs() < 0.01); // 0.4 + 0.1 = 0.5

        // Negative emotion: +0.2 (threats prioritized)
        let bid3 = AttentionBid::new("Test", "Error!")
            .with_salience(0.8)
            .with_urgency(0.5)
            .with_emotion(EmotionalValence::Negative);
        assert!((bid3.score() - 0.6).abs() < 0.01); // 0.4 + 0.2 = 0.6
    }

    #[test]
    fn test_working_memory_item() {
        let bid = AttentionBid::new("Hippocampus", "I remember this pattern")
            .with_salience(0.8);

        let mut item = WorkingMemoryItem::from_bid(bid);
        assert_eq!(item.activation, 1.0);

        // Decay
        item.decay(0.1);
        assert!((item.activation - 0.9).abs() < 0.01);

        // Refresh
        item.refresh();
        assert!(item.activation > 0.9);

        // Decay below threshold
        for _ in 0..20 {
            item.decay(0.1);
        }
        assert!(!item.is_active());
    }

    #[test]
    fn test_global_workspace_spotlight() {
        let mut workspace = GlobalWorkspace::new();

        assert!(workspace.current_focus().is_none());

        let bid = AttentionBid::new("Thalamus", "User input");
        workspace.update_spotlight(bid.clone());

        assert!(workspace.current_focus().is_some());
        assert_eq!(workspace.current_focus().unwrap().content, "User input");
    }

    #[test]
    fn test_global_workspace_stream() {
        let mut workspace = GlobalWorkspace::new();

        let bid1 = AttentionBid::new("Module1", "Thought 1");
        let bid2 = AttentionBid::new("Module2", "Thought 2");

        workspace.update_spotlight(bid1);
        workspace.update_spotlight(bid2);

        assert_eq!(workspace.stream.len(), 1); // bid1 moved to stream
        assert_eq!(workspace.spotlight.as_ref().unwrap().content, "Thought 2");
    }

    #[test]
    fn test_global_workspace_working_memory() {
        let mut workspace = GlobalWorkspace::new();

        let bid = AttentionBid::new("Test", "Important thought")
            .with_salience(0.9);

        workspace.add_to_working_memory(bid);
        assert_eq!(workspace.working_memory.len(), 1);

        // Duplicate should refresh, not add
        let bid2 = AttentionBid::new("Test", "Important thought");
        workspace.add_to_working_memory(bid2);
        assert_eq!(workspace.working_memory.len(), 1);
    }

    #[test]
    fn test_working_memory_capacity() {
        let mut workspace = GlobalWorkspace::new();
        workspace.max_working_memory = 3;

        // Add 5 items (should keep only 3 most active)
        for i in 0..5 {
            let bid = AttentionBid::new("Test", format!("Thought {}", i))
                .with_salience(0.8);
            workspace.add_to_working_memory(bid);
        }

        assert_eq!(workspace.working_memory.len(), 3);
    }

    #[test]
    fn test_prefrontal_cortex_creation() {
        let pfc = PrefrontalCortexActor::new();
        assert_eq!(pfc.cycle_count, 0);
        assert!(pfc.current_focus().is_none());
    }

    #[test]
    fn test_cognitive_cycle_no_bids() {
        let mut pfc = PrefrontalCortexActor::new();
        let winner = pfc.cognitive_cycle(vec![]);
        assert!(winner.is_none());
        assert_eq!(pfc.cycle_count, 1);
    }

    #[test]
    fn test_cognitive_cycle_single_bid() {
        let mut pfc = PrefrontalCortexActor::new();

        let bid = AttentionBid::new("Thalamus", "User typed something")
            .with_salience(0.9)
            .with_urgency(0.8);

        let winner = pfc.cognitive_cycle(vec![bid.clone()]);

        assert!(winner.is_some());
        assert_eq!(winner.unwrap().content, "User typed something");
        assert_eq!(pfc.cycle_count, 1);
        assert_eq!(pfc.total_bids, 1);
        assert_eq!(pfc.total_broadcasts, 1);
    }

    #[test]
    fn test_cognitive_cycle_competition() {
        let mut pfc = PrefrontalCortexActor::new();

        let bid1 = AttentionBid::new("Hippocampus", "I remember this")
            .with_salience(0.6)
            .with_urgency(0.5);

        let bid2 = AttentionBid::new("Thalamus", "User input!")
            .with_salience(0.9)
            .with_urgency(0.9);

        let bid3 = AttentionBid::new("Cerebellum", "I have a reflex")
            .with_salience(0.5)
            .with_urgency(0.4);

        let winner = pfc.cognitive_cycle(vec![bid1, bid2.clone(), bid3]);

        assert!(winner.is_some());
        assert_eq!(winner.unwrap().content, "User input!");
    }

    #[test]
    fn test_working_memory_persistence() {
        let mut pfc = PrefrontalCortexActor::new();

        // High salience bid should enter working memory
        let bid = AttentionBid::new("Test", "Important!")
            .with_salience(0.9)
            .with_urgency(0.8);

        pfc.cognitive_cycle(vec![bid]);

        assert_eq!(pfc.working_memory().len(), 1);
        assert_eq!(pfc.working_memory()[0].content, "Important!");
    }

    #[test]
    fn test_working_memory_decay() {
        let mut pfc = PrefrontalCortexActor::new();

        let bid = AttentionBid::new("Test", "Decaying thought")
            .with_salience(0.8);

        pfc.cognitive_cycle(vec![bid]);
        assert_eq!(pfc.working_memory().len(), 1);

        // Run many cycles with no bids - working memory should decay
        for _ in 0..30 {
            pfc.cognitive_cycle(vec![]);
        }

        assert_eq!(pfc.working_memory().len(), 0); // Should be gone
    }

    #[test]
    fn test_consciousness_stream() {
        let mut pfc = PrefrontalCortexActor::new();

        let bid1 = AttentionBid::new("Module1", "Thought 1").with_salience(0.9);
        let bid2 = AttentionBid::new("Module2", "Thought 2").with_salience(0.9);
        let bid3 = AttentionBid::new("Module3", "Thought 3").with_salience(0.9);

        pfc.cognitive_cycle(vec![bid1]);
        pfc.cognitive_cycle(vec![bid2]);
        pfc.cognitive_cycle(vec![bid3]);

        let stream = pfc.consciousness_stream();
        assert_eq!(stream.len(), 2); // bid1 and bid2 (bid3 is in spotlight)
    }

    #[test]
    fn test_prefrontal_stats() {
        let mut pfc = PrefrontalCortexActor::new();

        let bid = AttentionBid::new("Test", "Test thought").with_salience(0.9);
        pfc.cognitive_cycle(vec![bid]);

        let stats = pfc.stats();
        assert_eq!(stats.cycle_count, 1);
        assert_eq!(stats.total_bids, 1);
        assert_eq!(stats.total_broadcasts, 1);
        assert_eq!(stats.current_focus, Some("Test thought".to_string()));
    }

    #[test]
    fn test_emotional_priority() {
        let mut pfc = PrefrontalCortexActor::new();

        let normal_bid = AttentionBid::new("Module1", "Normal thought")
            .with_salience(0.7)
            .with_urgency(0.7);

        let threat_bid = AttentionBid::new("Module2", "ERROR!")
            .with_salience(0.7)
            .with_urgency(0.7)
            .with_emotion(EmotionalValence::Negative);

        let winner = pfc.cognitive_cycle(vec![normal_bid, threat_bid]);

        // Threat should win due to emotional boost
        assert_eq!(winner.unwrap().content, "ERROR!");
    }

    #[test]
    fn test_reset() {
        let mut pfc = PrefrontalCortexActor::new();

        let bid = AttentionBid::new("Test", "Thought").with_salience(0.9);
        pfc.cognitive_cycle(vec![bid]);

        assert!(pfc.current_focus().is_some());
        assert_eq!(pfc.cycle_count, 1);

        pfc.reset();

        assert!(pfc.current_focus().is_none());
        assert_eq!(pfc.cycle_count, 0);
        assert_eq!(pfc.working_memory().len(), 0);
    }
}
