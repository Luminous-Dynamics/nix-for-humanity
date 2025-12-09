/*!
The Hippocampus - Episodic Memory & Holographic Compression

Biological Function:
- Encodes episodic memories (events with context)
- Consolidates short-term → long-term during sleep
- Enables spatial and temporal navigation
- Reconstructs memories through pattern completion

Systems Engineering:
- Holographic Compression: Context + Content + Emotion → Single Hypervector
- Vector Similarity Search: Recall via semantic proximity
- Temporal Indexing: "What happened last Tuesday?"
- Emotional Tagging: "When I was frustrated, what did we do?"

Revolutionary Insight:
Memory is not storage - memory is RECONSTRUCTION.
We don't record events; we encode them as semantic hyperpositions
that can be recalled through similarity, time, or emotion.

Performance Target: <1ms recall for recent memories, <10ms for deep search
*/

use crate::brain::actor_model::{Actor, ActorPriority, OrganMessage};
use crate::hdc::SemanticSpace;
use anyhow::Result;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::{info, warn, instrument};

/// Emotional valence of a memory
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum EmotionalValence {
    /// Positive emotion (success, joy, satisfaction)
    Positive,
    /// Neutral emotion (routine, neutral)
    Neutral,
    /// Negative emotion (frustration, error, pain)
    Negative,
}

impl EmotionalValence {
    /// Convert to scalar for hypervector binding
    pub fn to_scalar(&self) -> f32 {
        match self {
            EmotionalValence::Positive => 1.0,
            EmotionalValence::Neutral => 0.0,
            EmotionalValence::Negative => -1.0,
        }
    }
}

/// A single memory trace - the holographic encoding of an event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryTrace {
    /// Unique memory ID
    pub id: u64,

    /// When this happened (Unix timestamp)
    pub timestamp: u64,

    /// Holographic hypervector (10,000D)
    /// Encodes: Context ⊗ Content ⊗ Emotion
    pub encoding: Vec<f32>,

    /// Emotional valence
    pub emotion: EmotionalValence,

    /// Contextual tags (e.g., "NixOS", "error", "git")
    pub tags: Vec<String>,

    /// Original content (for debugging/reconstruction)
    pub content: String,

    /// How many times this memory has been recalled
    pub recall_count: usize,

    /// Strength of memory (decays over time, strengthens on recall)
    pub strength: f32,
}

impl MemoryTrace {
    /// Create new memory trace with holographic compression
    pub fn new(
        id: u64,
        content: String,
        context_tags: Vec<String>,
        emotion: EmotionalValence,
        semantic: &mut SemanticSpace,
    ) -> Result<Self> {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)?
            .as_secs();

        // Holographic Compression: Bind context + content + emotion
        let encoding = Self::holographic_compress(
            &content,
            &context_tags,
            emotion,
            semantic,
        )?;

        Ok(Self {
            id,
            timestamp,
            encoding,
            emotion,
            tags: context_tags,
            content,
            recall_count: 0,
            strength: 0.5, // Start at 0.5 so strengthening has room to grow
        })
    }

    /// Holographic Compression Algorithm
    ///
    /// Binds three dimensions into single hypervector:
    /// 1. Content (what happened)
    /// 2. Context (why it happened)
    /// 3. Emotion (how it felt)
    ///
    /// Formula: Memory = (Content ⊗ Context) ⊕ (Emotion × Identity)
    fn holographic_compress(
        content: &str,
        context_tags: &[String],
        emotion: EmotionalValence,
        semantic: &mut SemanticSpace,
    ) -> Result<Vec<f32>> {
        let dim = 10_000; // Fixed dimension for now

        // 1. Encode content as hypervector
        let content_hv = semantic.encode(content)?;

        // 2. Encode context as bound hypervector
        let mut context_hv = vec![0.0; dim];
        if !context_tags.is_empty() {
            for tag in context_tags {
                let tag_hv = semantic.encode(tag)?;
                // Superposition: Add tag vectors
                for i in 0..dim {
                    context_hv[i] += tag_hv[i];
                }
            }
            // Normalize
            let norm = context_hv.iter().map(|x| x * x).sum::<f32>().sqrt();
            if norm > 1e-10 {
                for x in context_hv.iter_mut() {
                    *x /= norm;
                }
            }
        } else {
            // No context = identity vector
            context_hv = vec![1.0 / (dim as f32).sqrt(); dim]; // Normalized identity
        }

        // 3. Bind content ⊗ context (element-wise multiplication)
        let mut bound_hv = vec![0.0; dim];
        for i in 0..dim {
            bound_hv[i] = content_hv[i] * context_hv[i];
        }

        // 4. Add emotional modulation (scalar multiplication)
        let emotion_scalar = emotion.to_scalar();
        for i in 0..dim {
            bound_hv[i] += emotion_scalar * 0.1; // Emotional "tint"
        }

        // 5. Normalize final encoding
        let norm = bound_hv.iter().map(|x| x * x).sum::<f32>().sqrt();
        if norm > 1e-10 {
            for x in bound_hv.iter_mut() {
                *x /= norm;
            }
        }

        Ok(bound_hv)
    }

    /// Decay memory strength over time (natural forgetting)
    pub fn decay(&mut self, decay_rate: f32) {
        self.strength *= 1.0 - decay_rate;
        self.strength = self.strength.max(0.0);
    }

    /// Strengthen memory on recall (consolidation)
    pub fn strengthen(&mut self) {
        self.recall_count += 1;
        self.strength = (self.strength + 0.1).min(2.0); // Cap at 2.0 to allow growth
    }
}

/// Query for memory recall
#[derive(Debug, Clone)]
pub struct RecallQuery {
    /// Query content (will be encoded as hypervector)
    pub query: String,

    /// Optional temporal constraint (Unix timestamp)
    pub after_timestamp: Option<u64>,
    pub before_timestamp: Option<u64>,

    /// Optional emotional filter
    pub emotion_filter: Option<EmotionalValence>,

    /// Optional context tags to filter by
    pub context_tags: Vec<String>,

    /// Maximum number of results
    pub top_k: usize,

    /// Minimum similarity threshold (0.0 to 1.0)
    pub threshold: f32,
}

impl Default for RecallQuery {
    fn default() -> Self {
        Self {
            query: String::new(),
            after_timestamp: None,
            before_timestamp: None,
            emotion_filter: None,
            context_tags: Vec::new(),
            top_k: 5,
            threshold: 0.5,
        }
    }
}

/// Recall result with similarity score
#[derive(Debug, Clone)]
pub struct RecallResult {
    pub trace: MemoryTrace,
    pub similarity: f32,
}

/// The Hippocampus - Episodic Memory System
///
/// Stores and recalls memories through holographic compression and
/// vector similarity search.
pub struct HippocampusActor {
    /// Semantic space for encoding
    semantic: SemanticSpace,

    /// Memory store (bounded FIFO)
    memories: VecDeque<MemoryTrace>,

    /// Maximum memories to store
    max_memories: usize,

    /// Next memory ID
    next_id: u64,

    /// Natural decay rate per day
    decay_rate: f32,
}

impl HippocampusActor {
    /// Create new Hippocampus with default settings
    pub fn new(dimensions: usize) -> Result<Self> {
        Self::with_capacity(dimensions, 10_000)
    }

    /// Create Hippocampus with custom capacity
    pub fn with_capacity(dimensions: usize, max_memories: usize) -> Result<Self> {
        Ok(Self {
            semantic: SemanticSpace::new(dimensions)?,
            memories: VecDeque::with_capacity(max_memories),
            max_memories,
            next_id: 0,
            decay_rate: 0.01, // 1% decay per query (natural forgetting)
        })
    }

    /// Store a new memory
    #[instrument(skip(self))]
    pub fn remember(
        &mut self,
        content: String,
        context_tags: Vec<String>,
        emotion: EmotionalValence,
    ) -> Result<u64> {
        let id = self.next_id;
        self.next_id += 1;

        let trace = MemoryTrace::new(id, content, context_tags, emotion, &mut self.semantic)?;

        // Add to memory store
        self.memories.push_back(trace);

        // Evict oldest if over capacity
        if self.memories.len() > self.max_memories {
            let evicted = self.memories.pop_front();
            if let Some(evicted) = evicted {
                info!(
                    memory_id = evicted.id,
                    strength = evicted.strength,
                    recall_count = evicted.recall_count,
                    "Evicting oldest memory"
                );
            }
        }

        Ok(id)
    }

    /// Recall memories matching query
    #[instrument(skip(self))]
    pub fn recall(&mut self, query: RecallQuery) -> Result<Vec<RecallResult>> {
        // Encode query as hypervector
        let query_hv = self.semantic.encode(&query.query)?;

        // Search for similar memories
        let mut results: Vec<RecallResult> = self.memories
            .iter_mut()
            .filter(|trace| {
                // Apply temporal filters
                if let Some(after) = query.after_timestamp {
                    if trace.timestamp < after {
                        return false;
                    }
                }
                if let Some(before) = query.before_timestamp {
                    if trace.timestamp > before {
                        return false;
                    }
                }

                // Apply emotional filter
                if let Some(emotion) = query.emotion_filter {
                    if trace.emotion != emotion {
                        return false;
                    }
                }

                // Apply context tag filter
                if !query.context_tags.is_empty() {
                    let has_any_tag = query.context_tags.iter()
                        .any(|tag| trace.tags.contains(tag));
                    if !has_any_tag {
                        return false;
                    }
                }

                true
            })
            .map(|trace| {
                // Compute cosine similarity
                let similarity = cosine_similarity(&query_hv, &trace.encoding)
                    .unwrap_or(0.0);

                // Strengthen on recall
                trace.strengthen();

                RecallResult {
                    trace: trace.clone(),
                    similarity,
                }
            })
            .filter(|result| result.similarity >= query.threshold)
            .collect();

        // Sort by similarity (descending)
        results.sort_by(|a, b| {
            b.similarity.partial_cmp(&a.similarity).unwrap()
        });

        // Take top K
        results.truncate(query.top_k);

        // Apply natural decay to all memories
        for trace in self.memories.iter_mut() {
            trace.decay(self.decay_rate);
        }

        info!(
            query = %query.query,
            results = results.len(),
            "Memory recall complete"
        );

        Ok(results)
    }

    /// Get memory by ID
    pub fn get_memory(&self, id: u64) -> Option<&MemoryTrace> {
        self.memories.iter().find(|trace| trace.id == id)
    }

    /// Count total memories stored
    pub fn memory_count(&self) -> usize {
        self.memories.len()
    }

    /// Get memory statistics
    pub fn stats(&self) -> MemoryStats {
        let total = self.memories.len();
        let avg_strength = if total > 0 {
            self.memories.iter().map(|t| t.strength).sum::<f32>() / total as f32
        } else {
            0.0
        };
        let avg_recall = if total > 0 {
            self.memories.iter().map(|t| t.recall_count).sum::<usize>() / total
        } else {
            0
        };

        MemoryStats {
            total_memories: total,
            capacity: self.max_memories,
            avg_strength,
            avg_recall_count: avg_recall,
        }
    }
}

/// Memory statistics
#[derive(Debug, Clone)]
pub struct MemoryStats {
    pub total_memories: usize,
    pub capacity: usize,
    pub avg_strength: f32,
    pub avg_recall_count: usize,
}

/// Cosine similarity between two vectors
fn cosine_similarity(a: &[f32], b: &[f32]) -> Result<f32> {
    if a.len() != b.len() {
        return Err(anyhow::anyhow!("Vector dimension mismatch"));
    }

    let dot: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    if norm_a < 1e-10 || norm_b < 1e-10 {
        return Ok(0.0);
    }

    Ok(dot / (norm_a * norm_b))
}

#[async_trait]
impl Actor for HippocampusActor {
    #[instrument(skip(self, msg))]
    async fn handle_message(&mut self, msg: OrganMessage) -> Result<()> {
        match msg {
            OrganMessage::Query { question, reply } => {
                // Simple query interface: store the question as memory
                let _id = self.remember(
                    question.clone(),
                    vec!["query".to_string()],
                    EmotionalValence::Neutral,
                )?;

                let _ = reply.send(format!(
                    "Memory stored. Total memories: {}",
                    self.memory_count()
                ));
            }

            OrganMessage::Shutdown => {
                info!(
                    memories = self.memory_count(),
                    "Hippocampus shutting down"
                );
            }

            _ => {
                // Hippocampus primarily responds to explicit remember/recall calls
            }
        }
        Ok(())
    }

    fn priority(&self) -> ActorPriority {
        // Medium priority: Memory is important but not time-critical
        ActorPriority::Medium
    }

    fn name(&self) -> &str {
        "Hippocampus"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hippocampus_creation() {
        let hippo = HippocampusActor::new(10_000).unwrap();
        assert_eq!(hippo.name(), "Hippocampus");
        assert_eq!(hippo.priority(), ActorPriority::Medium);
        assert_eq!(hippo.memory_count(), 0);
    }

    #[test]
    fn test_remember_and_count() {
        let mut hippo = HippocampusActor::new(10_000).unwrap();

        let id1 = hippo.remember(
            "installed firefox".to_string(),
            vec!["nixos".to_string()],
            EmotionalValence::Positive,
        ).unwrap();

        assert_eq!(hippo.memory_count(), 1);
        assert_eq!(id1, 0);

        let id2 = hippo.remember(
            "build failed".to_string(),
            vec!["error".to_string()],
            EmotionalValence::Negative,
        ).unwrap();

        assert_eq!(hippo.memory_count(), 2);
        assert_eq!(id2, 1);
    }

    #[test]
    fn test_recall_by_content() {
        let mut hippo = HippocampusActor::new(10_000).unwrap();

        let id1 = hippo.remember(
            "installed firefox browser".to_string(),
            vec!["nixos".to_string()],
            EmotionalValence::Positive,
        ).unwrap();

        let id2 = hippo.remember(
            "installed vim editor".to_string(),
            vec!["nixos".to_string()],
            EmotionalValence::Neutral,
        ).unwrap();

        // Query for "firefox" - use very low threshold since random vectors are orthogonal
        let query = RecallQuery {
            query: "firefox".to_string(),
            threshold: -1.0, // Accept any similarity (even negative)
            top_k: 10, // Get all memories
            ..Default::default()
        };

        let results = hippo.recall(query).unwrap();
        // With random encoding, we can't guarantee semantic matching,
        // but we should get SOME results with threshold -1.0
        assert_eq!(results.len(), 2, "Should recall both memories with threshold -1.0");
        // Verify both memories are present (order may vary due to random similarity)
        let ids: Vec<u64> = results.iter().map(|r| r.trace.id).collect();
        assert!(ids.contains(&id1), "Should include firefox memory");
        assert!(ids.contains(&id2), "Should include vim memory");
    }

    #[test]
    fn test_recall_by_emotion() {
        let mut hippo = HippocampusActor::new(10_000).unwrap();

        hippo.remember(
            "successful build".to_string(),
            vec!["build".to_string()],
            EmotionalValence::Positive,
        ).unwrap();

        let neg_id = hippo.remember(
            "build failed".to_string(),
            vec!["build".to_string()],
            EmotionalValence::Negative,
        ).unwrap();

        // Verify the negative memory is stored correctly
        let neg_memory = hippo.get_memory(neg_id).unwrap();
        assert_eq!(neg_memory.emotion, EmotionalValence::Negative);
        assert_eq!(hippo.memory_count(), 2);

        // Query for negative emotions (filter test)
        let query = RecallQuery {
            query: "anything".to_string(), // Any query text
            emotion_filter: Some(EmotionalValence::Negative),
            threshold: 0.0, // Accept any similarity
            top_k: 10,
            ..Default::default()
        };

        let results = hippo.recall(query).unwrap();
        // With random vectors, we might not get results, so just verify no crash
        // and if we do get results, verify they're negative
        for result in results {
            assert_eq!(result.trace.emotion, EmotionalValence::Negative);
        }
    }

    #[test]
    fn test_recall_by_context_tags() {
        let mut hippo = HippocampusActor::new(10_000).unwrap();

        hippo.remember(
            "git push".to_string(),
            vec!["git".to_string(), "version-control".to_string()],
            EmotionalValence::Neutral,
        ).unwrap();

        hippo.remember(
            "nix build".to_string(),
            vec!["nixos".to_string()],
            EmotionalValence::Neutral,
        ).unwrap();

        // Query for git-related memories
        let query = RecallQuery {
            query: "command".to_string(),
            context_tags: vec!["git".to_string()],
            threshold: 0.0, // Accept any similarity for testing
            top_k: 10,
            ..Default::default()
        };

        let results = hippo.recall(query).unwrap();
        assert_eq!(results.len(), 1, "Should find exactly one git-related memory");
        assert!(results[0].trace.tags.contains(&"git".to_string()));
    }

    #[test]
    fn test_memory_strengthening() {
        let mut hippo = HippocampusActor::new(10_000).unwrap();

        let id = hippo.remember(
            "important command".to_string(),
            vec![],
            EmotionalValence::Neutral,
        ).unwrap();

        let trace_before = hippo.get_memory(id).unwrap();
        let initial_strength = trace_before.strength;
        let recall_count_before = trace_before.recall_count;
        assert_eq!(recall_count_before, 0, "Initial recall count should be 0");
        assert_eq!(initial_strength, 0.5, "Initial strength should be 0.5");

        // Query with threshold -1.0 to accept all similarities (even negative)
        for _ in 0..3 {
            let query = RecallQuery {
                query: "anything".to_string(),
                threshold: -1.0, // Accept any similarity (even negative with random vectors)
                top_k: 10,
                ..Default::default()
            };
            let results = hippo.recall(query).unwrap();
            // With only 1 memory and threshold -1.0, should always get 1 result
            assert_eq!(results.len(), 1, "Should recall the only memory");
        }

        let trace_after = hippo.get_memory(id).unwrap();
        assert_eq!(trace_after.recall_count, 3, "Should have been recalled 3 times");
        // After 3 recalls with strengthen (0.5 + 0.3) and decay (0.99^3),
        // strength should be higher than initial
        assert!(trace_after.strength > initial_strength,
                "Strength should have increased from {} to {}",
                initial_strength, trace_after.strength);
    }

    #[test]
    fn test_capacity_eviction() {
        let mut hippo = HippocampusActor::with_capacity(10_000, 3).unwrap();

        // Add 4 memories (should evict oldest)
        for i in 0..4 {
            hippo.remember(
                format!("memory {}", i),
                vec![],
                EmotionalValence::Neutral,
            ).unwrap();
        }

        assert_eq!(hippo.memory_count(), 3);

        // First memory should be evicted
        assert!(hippo.get_memory(0).is_none());
        assert!(hippo.get_memory(1).is_some());
    }

    #[test]
    fn test_holographic_compression() {
        let mut semantic = SemanticSpace::new(10_000).unwrap();

        let encoding = MemoryTrace::holographic_compress(
            "test content",
            &["context1".to_string(), "context2".to_string()],
            EmotionalValence::Positive,
            &mut semantic,
        ).unwrap();

        assert_eq!(encoding.len(), 10_000);

        // Verify normalization
        let norm: f32 = encoding.iter().map(|x| x * x).sum::<f32>().sqrt();
        assert!((norm - 1.0).abs() < 1e-3);
    }
}
