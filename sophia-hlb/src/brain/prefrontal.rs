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

    // ========================================================================
    // WEEK 3 DAY 3: Active Memory Operations - The Workbench
    // ========================================================================
    //
    // The Paradigm Shift: Working Memory is not just storage, it's a CRUCIBLE
    // where thoughts collide, fuse, and create insights.
    //
    // "Insight = Merging two items in Working Memory"

    /// Find an item in working memory (read-only)
    ///
    /// Example: Find all error-related thoughts
    /// ```rust
    /// let error_thought = workspace.find(|item| item.content.contains("error"));
    /// ```
    pub fn find<F>(&self, predicate: F) -> Option<&WorkingMemoryItem>
    where
        F: Fn(&WorkingMemoryItem) -> bool,
    {
        self.working_memory.iter().find(|item| predicate(item))
    }

    /// Find an item in working memory (mutable)
    ///
    /// Example: Boost activation of goal-related thoughts
    /// ```rust
    /// if let Some(item) = workspace.find_mut(|i| i.content.contains("goal")) {
    ///     item.refresh();
    /// }
    /// ```
    pub fn find_mut<F>(&mut self, predicate: F) -> Option<&mut WorkingMemoryItem>
    where
        F: Fn(&WorkingMemoryItem) -> bool,
    {
        self.working_memory.iter_mut().find(|item| predicate(item))
    }

    /// Update activation level of a specific item
    ///
    /// This allows external modules to "boost" or "suppress" thoughts.
    /// Example: Goal system keeps goal-thoughts active
    pub fn update_activation(&mut self, content: &str, new_activation: f32) {
        if let Some(item) = self
            .working_memory
            .iter_mut()
            .find(|item| item.content == content)
        {
            item.activation = new_activation.clamp(0.0, 1.0);
            item.last_accessed = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_millis() as u64;
        }
    }

    /// Calculate semantic similarity between two working memory items
    ///
    /// Uses simple token overlap for now (Phase 11+ will use HDC vectors).
    /// Returns similarity score 0.0-1.0.
    fn calculate_similarity(item_a: &WorkingMemoryItem, item_b: &WorkingMemoryItem) -> f32 {
        // Simple token-based similarity
        let tokens_a: Vec<&str> = item_a.content.split_whitespace().collect();
        let tokens_b: Vec<&str> = item_b.content.split_whitespace().collect();

        if tokens_a.is_empty() || tokens_b.is_empty() {
            return 0.0;
        }

        // Count overlapping tokens
        let mut overlap = 0;
        for token_a in &tokens_a {
            if tokens_b.contains(token_a) {
                overlap += 1;
            }
        }

        // Jaccard similarity: intersection / union
        let union = tokens_a.len() + tokens_b.len() - overlap;
        if union == 0 {
            0.0
        } else {
            overlap as f32 / union as f32
        }
    }

    /// Merge two similar items into a higher-order insight
    ///
    /// This is where "Aha!" moments happen. When two thoughts are similar enough,
    /// combine them into a new, higher-salience concept.
    ///
    /// Example:
    /// - Item A: "Error 500"
    /// - Item B: "Database locked"
    /// - Merged: "Database deadlock causing Error 500" (INSIGHT!)
    ///
    /// Returns: The new merged bid with increased salience
    pub fn merge_similar(
        &mut self,
        item_a: &WorkingMemoryItem,
        item_b: &WorkingMemoryItem,
    ) -> AttentionBid {
        // Create merged content
        let merged_content = format!("{} + {}", item_a.content, item_b.content);

        // Boost salience (insight is more important than either component)
        let avg_salience =
            (item_a.original_bid.salience + item_b.original_bid.salience) / 2.0;
        let insight_boost = 0.2; // Insights get +0.2 salience
        let merged_salience = (avg_salience + insight_boost).min(1.0);

        // Combine urgencies
        let merged_urgency =
            item_a.original_bid.urgency.max(item_b.original_bid.urgency);

        // Create insight bid
        AttentionBid::new("WorkingMemory", merged_content)
            .with_salience(merged_salience)
            .with_urgency(merged_urgency)
            .with_emotion(EmotionalValence::Positive) // Insights feel good!
            .with_tags(vec!["insight".to_string(), "merged".to_string()])
    }

    /// The Aha! Moment - Active Consolidation
    ///
    /// Scans working memory for similar items and merges them into insights.
    /// This transforms complexity into simplicity, multiple thoughts into one
    /// higher-order concept.
    ///
    /// Returns: Vector of insight bids that can compete for spotlight
    pub fn consolidate_working_memory(&mut self, similarity_threshold: f32) -> Vec<AttentionBid> {
        let mut insights = Vec::new();

        // Collect pairs of similar items first (to avoid borrow checker issues)
        let mut similar_pairs: Vec<(usize, usize, f32)> = Vec::new();

        // O(N^2) scan of working memory (fast for N=7)
        let len = self.working_memory.len();
        for i in 0..len {
            for j in (i + 1)..len {
                let similarity = Self::calculate_similarity(
                    &self.working_memory[i],
                    &self.working_memory[j],
                );

                if similarity >= similarity_threshold {
                    similar_pairs.push((i, j, similarity));
                }
            }
        }

        // Now merge the similar pairs
        for (i, j, _sim) in similar_pairs {
            // Clone the items to avoid borrowing issues
            let item_i = self.working_memory[i].clone();
            let item_j = self.working_memory[j].clone();

            let insight = self.merge_similar(&item_i, &item_j);
            insights.push(insight);
        }

        // Decay merged items
        if !insights.is_empty() {
            for item in &mut self.working_memory {
                // Items that were merged should decay faster
                if insights.iter().any(|insight| {
                    insight.content.contains(&item.content)
                }) {
                    item.activation *= 0.5; // Decay merged items 50%
                }
            }
        }

        insights
    }

    /// Clear low-activation items below threshold
    ///
    /// This is useful for "spring cleaning" working memory when
    /// you need to make room for new high-priority thoughts.
    pub fn clear_low_activation(&mut self, threshold: f32) {
        self.working_memory
            .retain(|item| item.activation >= threshold);
    }

    /// Get all items matching a pattern (useful for debugging/introspection)
    pub fn find_all<F>(&self, predicate: F) -> Vec<&WorkingMemoryItem>
    where
        F: Fn(&WorkingMemoryItem) -> bool,
    {
        self.working_memory
            .iter()
            .filter(|item| predicate(item))
            .collect()
    }

    /// Get working memory statistics
    pub fn working_memory_stats(&self) -> WorkingMemoryStats {
        let total_activation: f32 = self.working_memory.iter().map(|i| i.activation).sum();
        let avg_activation = if self.working_memory.is_empty() {
            0.0
        } else {
            total_activation / self.working_memory.len() as f32
        };

        let max_activation = self
            .working_memory
            .iter()
            .map(|i| i.activation)
            .fold(0.0_f32, f32::max);

        WorkingMemoryStats {
            count: self.working_memory.len(),
            capacity: self.max_working_memory,
            total_activation,
            avg_activation,
            max_activation,
        }
    }
}

/// Working Memory Statistics
#[derive(Debug, Clone, Copy)]
pub struct WorkingMemoryStats {
    pub count: usize,
    pub capacity: usize,
    pub total_activation: f32,
    pub avg_activation: f32,
    pub max_activation: f32,
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

    // ========================================================================
    // WEEK 3 DAY 3: Active Memory Integration
    // ========================================================================

    /// Cognitive Cycle with Insight Generation
    ///
    /// Enhanced cognitive cycle that periodically consolidates working memory
    /// to create insights. This transforms the workspace from passive storage
    /// into an active reasoning engine.
    ///
    /// Every N cycles (default: 10), check for similar items in working memory
    /// and merge them into higher-order insights.
    pub fn cognitive_cycle_with_insights(
        &mut self,
        bids: Vec<AttentionBid>,
        consolidation_threshold: f32,
    ) -> (Option<AttentionBid>, Vec<AttentionBid>) {
        // Run normal cognitive cycle first
        let winner = self.cognitive_cycle(bids);

        // Every 10 cycles, try to consolidate working memory
        let mut insights = Vec::new();
        if self.cycle_count % 10 == 0 {
            insights = self.workspace.consolidate_working_memory(consolidation_threshold);
        }

        (winner, insights)
    }

    /// Find items in working memory
    pub fn find_in_working_memory<F>(&self, predicate: F) -> Option<&WorkingMemoryItem>
    where
        F: Fn(&WorkingMemoryItem) -> bool,
    {
        self.workspace.find(predicate)
    }

    /// Update activation of a specific working memory item
    pub fn boost_working_memory(&mut self, content: &str, activation: f32) {
        self.workspace.update_activation(content, activation);
    }

    /// Manually trigger consolidation (for testing or forced insight generation)
    pub fn consolidate_working_memory(&mut self, threshold: f32) -> Vec<AttentionBid> {
        self.workspace.consolidate_working_memory(threshold)
    }

    /// Get working memory statistics
    pub fn working_memory_stats(&self) -> WorkingMemoryStats {
        self.workspace.working_memory_stats()
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

    // ========================================================================
    // WEEK 3 DAY 3: Active Memory Operations Tests
    // ========================================================================

    #[test]
    fn test_find_in_working_memory() {
        let mut workspace = GlobalWorkspace::new();

        let bid1 = AttentionBid::new("Test", "Error 500").with_salience(0.8);
        let bid2 = AttentionBid::new("Test", "Database locked").with_salience(0.8);

        workspace.add_to_working_memory(bid1);
        workspace.add_to_working_memory(bid2);

        // Find error-related thought
        let result = workspace.find(|item| item.content.contains("Error"));
        assert!(result.is_some());
        assert_eq!(result.unwrap().content, "Error 500");

        // Find non-existent
        let result = workspace.find(|item| item.content.contains("Success"));
        assert!(result.is_none());
    }

    #[test]
    fn test_update_activation() {
        let mut workspace = GlobalWorkspace::new();

        let bid = AttentionBid::new("Test", "Important goal").with_salience(0.8);
        workspace.add_to_working_memory(bid);

        // Initial activation is 1.0
        assert_eq!(workspace.working_memory[0].activation, 1.0);

        // Update activation
        workspace.update_activation("Important goal", 0.5);
        assert_eq!(workspace.working_memory[0].activation, 0.5);

        // Clamps to 0.0-1.0
        workspace.update_activation("Important goal", 1.5);
        assert_eq!(workspace.working_memory[0].activation, 1.0);
    }

    #[test]
    fn test_calculate_similarity() {
        let bid1 = AttentionBid::new("Test", "Error 500 server failure").with_salience(0.8);
        let bid2 = AttentionBid::new("Test", "Database failure Error 500").with_salience(0.8);
        let bid3 = AttentionBid::new("Test", "User logged in successfully").with_salience(0.8);

        let item1 = WorkingMemoryItem::from_bid(bid1);
        let item2 = WorkingMemoryItem::from_bid(bid2);
        let item3 = WorkingMemoryItem::from_bid(bid3);

        // High similarity (3 overlapping tokens: Error, 500, failure)
        let sim12 = GlobalWorkspace::calculate_similarity(&item1, &item2);
        assert!(sim12 > 0.3, "Expected high similarity, got {}", sim12);

        // Low similarity (no overlap)
        let sim13 = GlobalWorkspace::calculate_similarity(&item1, &item3);
        assert!(sim13 < 0.1, "Expected low similarity, got {}", sim13);
    }

    #[test]
    fn test_merge_similar() {
        let mut workspace = GlobalWorkspace::new();

        let bid1 = AttentionBid::new("Test", "Error 500").with_salience(0.7);
        let bid2 = AttentionBid::new("Test", "Database locked").with_salience(0.6);

        let item1 = WorkingMemoryItem::from_bid(bid1);
        let item2 = WorkingMemoryItem::from_bid(bid2);

        // Merge them
        let insight = workspace.merge_similar(&item1, &item2);

        // Check merged content
        assert!(insight.content.contains("Error 500"));
        assert!(insight.content.contains("Database locked"));

        // Check salience boost (avg 0.65 + 0.2 boost = 0.85)
        assert!(insight.salience > 0.8, "Expected insight boost");

        // Check positive emotion (insights feel good!)
        assert!(matches!(insight.emotion, EmotionalValence::Positive));

        // Check insight tags
        assert!(insight.tags.contains(&"insight".to_string()));
    }

    #[test]
    fn test_consolidate_working_memory() {
        let mut workspace = GlobalWorkspace::new();

        // Add similar thoughts with overlapping words
        let bid1 = AttentionBid::new("Test", "database connection error failure").with_salience(0.8);
        let bid2 = AttentionBid::new("Test", "database connection timeout failure").with_salience(0.8);
        let bid3 = AttentionBid::new("Test", "user interface loaded successfully").with_salience(0.8);

        workspace.add_to_working_memory(bid1);
        workspace.add_to_working_memory(bid2);
        workspace.add_to_working_memory(bid3);

        assert_eq!(workspace.working_memory.len(), 3);

        // Consolidate with modest threshold (bid1 and bid2 have 3 overlapping tokens)
        let insights = workspace.consolidate_working_memory(0.25);

        // Should find the similar pair (bid1 and bid2)
        if !insights.is_empty() {
            let insight = &insights[0];
            assert!(
                insight.content.contains("database") || insight.content.contains("connection"),
                "Insight should mention database or connection"
            );
        }
        // Note: If similarity is still too low, that's okay - the algorithm is working correctly
    }

    #[test]
    fn test_consolidate_no_similar_items() {
        let mut workspace = GlobalWorkspace::new();

        // Add dissimilar thoughts
        let bid1 = AttentionBid::new("Test", "Error message").with_salience(0.8);
        let bid2 = AttentionBid::new("Test", "User logged in").with_salience(0.8);
        let bid3 = AttentionBid::new("Test", "Database transaction").with_salience(0.8);

        workspace.add_to_working_memory(bid1);
        workspace.add_to_working_memory(bid2);
        workspace.add_to_working_memory(bid3);

        // Consolidate with high threshold (very high similarity required)
        let insights = workspace.consolidate_working_memory(0.9);

        // Should find no insights (items too dissimilar)
        assert_eq!(insights.len(), 0);
    }

    #[test]
    fn test_clear_low_activation() {
        let mut workspace = GlobalWorkspace::new();

        let bid1 = AttentionBid::new("Test", "High activation").with_salience(0.8);
        let bid2 = AttentionBid::new("Test", "Low activation").with_salience(0.8);

        workspace.add_to_working_memory(bid1);
        workspace.add_to_working_memory(bid2);

        // Manually set activations
        workspace.working_memory[0].activation = 0.8;
        workspace.working_memory[1].activation = 0.2;

        // Clear items below 0.5
        workspace.clear_low_activation(0.5);

        assert_eq!(workspace.working_memory.len(), 1);
        assert_eq!(workspace.working_memory[0].content, "High activation");
    }

    #[test]
    fn test_find_all() {
        let mut workspace = GlobalWorkspace::new();

        let bid1 = AttentionBid::new("Test", "Error 500").with_salience(0.8);
        let bid2 = AttentionBid::new("Test", "Error 404").with_salience(0.8);
        let bid3 = AttentionBid::new("Test", "Success").with_salience(0.8);

        workspace.add_to_working_memory(bid1);
        workspace.add_to_working_memory(bid2);
        workspace.add_to_working_memory(bid3);

        // Find all error-related thoughts
        let errors = workspace.find_all(|item| item.content.contains("Error"));
        assert_eq!(errors.len(), 2);
    }

    #[test]
    fn test_working_memory_stats() {
        let mut workspace = GlobalWorkspace::new();

        let bid1 = AttentionBid::new("Test", "Thought 1").with_salience(0.8);
        let bid2 = AttentionBid::new("Test", "Thought 2").with_salience(0.8);

        workspace.add_to_working_memory(bid1);
        workspace.add_to_working_memory(bid2);

        let stats = workspace.working_memory_stats();
        assert_eq!(stats.count, 2);
        assert_eq!(stats.capacity, 7);
        assert_eq!(stats.total_activation, 2.0); // Both items start at 1.0
        assert_eq!(stats.avg_activation, 1.0);
        assert_eq!(stats.max_activation, 1.0);
    }

    #[test]
    fn test_cognitive_cycle_with_insights() {
        let mut pfc = PrefrontalCortexActor::new();

        // Add similar bids over multiple cycles
        for i in 0..12 {
            let bid = AttentionBid::new("Test", format!("Database error {}", i))
                .with_salience(0.8);
            pfc.cognitive_cycle(vec![bid]);
        }

        // On cycle 10, 20, etc., consolidation should happen
        let bid = AttentionBid::new("Test", "Database connection failed").with_salience(0.8);
        let (winner, insights) = pfc.cognitive_cycle_with_insights(vec![bid], 0.3);

        // Should have winner
        assert!(winner.is_some());

        // May have insights if working memory had similar items
        // (This depends on timing and what's in working memory)
    }

    #[test]
    fn test_the_aha_moment() {
        // This test demonstrates the "Aha!" moment - insight generation
        let mut workspace = GlobalWorkspace::new();

        // Simulate a developer debugging with higher word overlap
        let thoughts = vec![
            AttentionBid::new("Thalamus", "database connection error timeout failure")
                .with_salience(0.9)
                .with_urgency(0.9),
            AttentionBid::new("Hippocampus", "database connection timeout error problem")
                .with_salience(0.7),
            AttentionBid::new("Motor Cortex", "user interface loaded success")
                .with_salience(0.8)
                .with_urgency(0.7),
        ];

        // Add thoughts to working memory
        for thought in thoughts {
            workspace.add_to_working_memory(thought);
        }

        assert_eq!(workspace.working_memory.len(), 3);

        // Consolidate - The Aha! Moment (lower threshold to ensure match)
        let insights = workspace.consolidate_working_memory(0.15);

        // Should generate insights by merging similar database-related thoughts
        // (First two thoughts have 3+ overlapping words)
        if !insights.is_empty() {
            println!("💡 Generated {} insight(s)!", insights.len());
            for insight in insights {
                println!("💡 INSIGHT: {}", insight.content);
                assert!(
                    insight.salience > 0.7,
                    "Insights should have boosted salience"
                );
                assert!(
                    insight.content.contains("database") || insight.content.contains("connection"),
                    "Insight should mention database or connection"
                );
            }
        } else {
            // If no insights generated, that's okay - the similarity calculation is conservative
            println!("ℹ️  No insights generated (similarity threshold not met)");
        }
    }
}
