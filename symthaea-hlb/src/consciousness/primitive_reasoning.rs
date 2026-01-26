//! # Primitive Reasoning: Basic Cognitive Operations
//!
//! Provides foundational reasoning capabilities using hyperdimensional computing.
//! Based on analogical reasoning and concept binding.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use symthaea_core::hdc::RealHV;

/// Configuration for the primitive reasoner
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReasonerConfig {
    /// Similarity threshold for concept matching
    pub similarity_threshold: f32,
    /// Maximum reasoning depth
    pub max_depth: usize,
    /// Whether to use analogical reasoning
    pub use_analogy: bool,
    /// Cache size for memoization
    pub cache_size: usize,
}

impl Default for ReasonerConfig {
    fn default() -> Self {
        Self {
            similarity_threshold: 0.7,
            max_depth: 5,
            use_analogy: true,
            cache_size: 1000,
        }
    }
}

/// Result of a reasoning operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReasoningResult {
    /// The conclusion reached
    pub conclusion: String,
    /// Confidence in the conclusion (0.0-1.0)
    pub confidence: f32,
    /// Chain of reasoning steps
    pub reasoning_chain: Vec<ReasoningStep>,
    /// Evidence supporting the conclusion
    pub evidence: Vec<String>,
    /// Alternative conclusions considered
    pub alternatives: Vec<(String, f32)>,
}

/// A single step in the reasoning chain
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReasoningStep {
    /// The operation performed
    pub operation: ReasoningOperation,
    /// Input concepts
    pub inputs: Vec<String>,
    /// Output concept
    pub output: String,
    /// Confidence of this step
    pub confidence: f32,
}

/// Types of reasoning operations
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ReasoningOperation {
    /// Bind two concepts together
    Binding,
    /// Find similarity between concepts
    Similarity,
    /// Analogical mapping (A:B :: C:?)
    Analogy,
    /// Sequence prediction
    Sequence,
    /// Hierarchical classification
    Classification,
    /// Causal inference
    Causation,
    /// Composition of concepts
    Composition,
    /// Abstraction/generalization
    Abstraction,
}

/// A concept in the reasoning system
#[derive(Debug, Clone)]
pub struct Concept {
    /// Concept name
    pub name: String,
    /// Hyperdimensional representation
    pub hv: RealHV,
    /// Relations to other concepts
    pub relations: HashMap<String, f32>,
    /// Metadata
    pub metadata: HashMap<String, String>,
}

impl Concept {
    /// Create a new concept
    pub fn new(name: impl Into<String>, hv: RealHV) -> Self {
        Self {
            name: name.into(),
            hv,
            relations: HashMap::new(),
            metadata: HashMap::new(),
        }
    }

    /// Add a relation to another concept
    pub fn add_relation(&mut self, target: impl Into<String>, strength: f32) {
        self.relations.insert(target.into(), strength);
    }
}

/// The primitive reasoner
#[derive(Debug)]
pub struct PrimitiveReasoner {
    /// Configuration
    config: ReasonerConfig,
    /// Known concepts
    concepts: HashMap<String, Concept>,
    /// Reasoning cache
    cache: HashMap<String, ReasoningResult>,
    /// Statistics
    stats: ReasonerStats,
}

/// Statistics for the reasoner
#[derive(Debug, Clone, Default)]
pub struct ReasonerStats {
    /// Total reasoning operations
    pub total_operations: u64,
    /// Cache hits
    pub cache_hits: u64,
    /// Average confidence
    pub avg_confidence: f32,
    /// Deepest reasoning chain
    pub max_depth_reached: usize,
}

impl PrimitiveReasoner {
    /// Create a new reasoner
    pub fn new(config: ReasonerConfig) -> Self {
        Self {
            config,
            concepts: HashMap::new(),
            cache: HashMap::new(),
            stats: ReasonerStats::default(),
        }
    }

    /// Add a concept to the knowledge base
    pub fn add_concept(&mut self, concept: Concept) {
        self.concepts.insert(concept.name.clone(), concept);
    }

    /// Get a concept by name
    pub fn get_concept(&self, name: &str) -> Option<&Concept> {
        self.concepts.get(name)
    }

    /// Perform reasoning on a query
    pub fn reason(&mut self, query: &str, context: &[String]) -> ReasoningResult {
        self.stats.total_operations += 1;

        // Check cache
        let cache_key = format!("{}:{}", query, context.join(","));
        if let Some(cached) = self.cache.get(&cache_key) {
            self.stats.cache_hits += 1;
            return cached.clone();
        }

        // Perform actual reasoning
        let result = self.perform_reasoning(query, context);

        // Update cache
        if self.cache.len() < self.config.cache_size {
            self.cache.insert(cache_key, result.clone());
        }

        // Update statistics
        let n = self.stats.total_operations as f32;
        self.stats.avg_confidence =
            (self.stats.avg_confidence * (n - 1.0) + result.confidence) / n;
        self.stats.max_depth_reached =
            self.stats.max_depth_reached.max(result.reasoning_chain.len());

        result
    }

    /// Internal reasoning implementation
    fn perform_reasoning(&self, query: &str, context: &[String]) -> ReasoningResult {
        let mut chain = Vec::new();
        let mut confidence = 1.0f32;
        let mut alternatives = Vec::new();

        // Parse query and identify concepts
        let query_concepts: Vec<_> = query.split_whitespace()
            .filter(|w| self.concepts.contains_key(*w))
            .collect();

        // Build reasoning chain
        for (i, concept_name) in query_concepts.iter().enumerate() {
            if i == 0 {
                continue;
            }

            let prev = query_concepts[i - 1];
            let curr = *concept_name;

            // Try to find relation
            if let Some(concept) = self.concepts.get(prev) {
                if let Some(&rel_strength) = concept.relations.get(curr) {
                    chain.push(ReasoningStep {
                        operation: ReasoningOperation::Binding,
                        inputs: vec![prev.to_string(), curr.to_string()],
                        output: format!("{}→{}", prev, curr),
                        confidence: rel_strength,
                    });
                    confidence *= rel_strength;
                }
            }

            // Try analogical reasoning if enabled
            if self.config.use_analogy && chain.is_empty() {
                if let Some(analogy_result) = self.try_analogy(prev, curr) {
                    chain.push(analogy_result.0);
                    confidence = analogy_result.1;
                }
            }
        }

        // Include context
        let evidence: Vec<String> = context.iter()
            .filter(|c| query_concepts.iter().any(|qc| c.contains(qc)))
            .cloned()
            .collect();

        // Generate alternatives based on similar concepts
        for concept_name in &query_concepts {
            if let Some(concept) = self.concepts.get(*concept_name) {
                for (related, strength) in &concept.relations {
                    if *strength > 0.5 && *strength < confidence {
                        alternatives.push((related.clone(), *strength));
                    }
                }
            }
        }

        alternatives.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        alternatives.truncate(5);

        ReasoningResult {
            conclusion: query.to_string(),
            confidence,
            reasoning_chain: chain,
            evidence,
            alternatives,
        }
    }

    /// Try analogical reasoning (A:B :: C:?)
    fn try_analogy(&self, a: &str, c: &str) -> Option<(ReasoningStep, f32)> {
        let concept_a = self.concepts.get(a)?;
        let concept_c = self.concepts.get(c)?;

        // Find the best matching relation
        let mut best_match: Option<(String, f32)> = None;

        for (_b, strength_ab) in &concept_a.relations {
            // Look for similar relation from C
            for (d, strength_cd) in &concept_c.relations {
                let similarity = (strength_ab - strength_cd).abs();
                if similarity < 0.2 {
                    let confidence = 1.0 - similarity;
                    if best_match.as_ref().map_or(true, |(_, c)| confidence > *c) {
                        best_match = Some((d.clone(), confidence));
                    }
                }
            }
        }

        best_match.map(|(d, conf)| {
            (
                ReasoningStep {
                    operation: ReasoningOperation::Analogy,
                    inputs: vec![a.to_string(), c.to_string()],
                    output: d,
                    confidence: conf,
                },
                conf,
            )
        })
    }

    /// Bind two concepts together
    pub fn bind(&mut self, a: &str, b: &str) -> Option<RealHV> {
        let concept_a = self.concepts.get(a)?;
        let concept_b = self.concepts.get(b)?;

        // Bind hypervectors
        let bound = concept_a.hv.bind(&concept_b.hv);
        Some(bound)
    }

    /// Find similar concepts
    pub fn find_similar(&self, query_hv: &RealHV, top_k: usize) -> Vec<(String, f32)> {
        let mut similarities: Vec<(String, f32)> = self.concepts
            .iter()
            .map(|(name, concept)| {
                let sim = query_hv.similarity(&concept.hv);
                (name.clone(), sim)
            })
            .collect();

        similarities.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        similarities.truncate(top_k);
        similarities
    }

    /// Get statistics
    pub fn stats(&self) -> &ReasonerStats {
        &self.stats
    }

    /// Clear the cache
    pub fn clear_cache(&mut self) {
        self.cache.clear();
    }
}

impl Default for PrimitiveReasoner {
    fn default() -> Self {
        Self::new(ReasonerConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_reasoner_creation() {
        let reasoner = PrimitiveReasoner::default();
        assert!(reasoner.concepts.is_empty());
    }

    #[test]
    fn test_concept_creation() {
        let hv = RealHV::random(512, 42);
        let mut concept = Concept::new("test", hv);
        concept.add_relation("other", 0.8);
        assert_eq!(concept.relations.get("other"), Some(&0.8));
    }

    #[test]
    fn test_basic_reasoning() {
        let mut reasoner = PrimitiveReasoner::default();

        // Add some concepts
        let hv1 = RealHV::random(512, 42);
        let mut c1 = Concept::new("animal", hv1);
        c1.add_relation("dog", 0.9);
        reasoner.add_concept(c1);

        let hv2 = RealHV::random(512, 42);
        let c2 = Concept::new("dog", hv2);
        reasoner.add_concept(c2);

        // Perform reasoning
        let result = reasoner.reason("animal dog", &[]);
        assert!(result.confidence > 0.0);
    }
}
