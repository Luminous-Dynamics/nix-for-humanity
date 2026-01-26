//! # Universal Semantics: Cross-Domain Semantic Understanding
//!
//! Provides universal semantic representations that work across
//! different domains, modalities, and languages using hyperdimensional
//! computing principles.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use symthaea_core::hdc::RealHV;

// Re-export SemanticPrime from symthaea_core for compatibility
pub use symthaea_core::hdc::universal_semantics::SemanticPrime;

/// Configuration for universal semantics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UniversalSemanticsConfig {
    /// Embedding dimension
    pub dimension: usize,
    /// Number of semantic domains
    pub num_domains: usize,
    /// Enable cross-domain transfer
    pub cross_domain_enabled: bool,
    /// Similarity threshold for matching
    pub similarity_threshold: f32,
}

impl Default for UniversalSemanticsConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            num_domains: 8,
            cross_domain_enabled: true,
            similarity_threshold: 0.7,
        }
    }
}

/// A semantic domain
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SemanticDomain {
    /// Natural language text
    Language,
    /// Visual/image content
    Visual,
    /// Audio/sound content
    Audio,
    /// Numerical/mathematical
    Mathematical,
    /// Spatial/geometric
    Spatial,
    /// Temporal/time-based
    Temporal,
    /// Emotional/affective
    Emotional,
    /// Abstract concepts
    Abstract,
}

/// A universal semantic concept
#[derive(Debug, Clone)]
pub struct SemanticConcept {
    /// Unique identifier
    pub id: String,
    /// Concept name
    pub name: String,
    /// Universal embedding (domain-agnostic)
    pub universal_embedding: RealHV,
    /// Domain-specific embeddings
    pub domain_embeddings: HashMap<SemanticDomain, RealHV>,
    /// Related concepts (by similarity)
    pub related: Vec<(String, f32)>,
    /// Source domain
    pub source_domain: SemanticDomain,
    /// Confidence
    pub confidence: f32,
}

impl SemanticConcept {
    /// Create a new concept
    pub fn new(id: impl Into<String>, name: impl Into<String>, domain: SemanticDomain, embedding: RealHV) -> Self {
        let universal = embedding.clone();
        let mut domain_embeddings = HashMap::new();
        domain_embeddings.insert(domain, embedding);

        Self {
            id: id.into(),
            name: name.into(),
            universal_embedding: universal,
            domain_embeddings,
            related: Vec::new(),
            source_domain: domain,
            confidence: 1.0,
        }
    }

    /// Add domain-specific embedding
    pub fn add_domain_embedding(&mut self, domain: SemanticDomain, embedding: RealHV) {
        self.domain_embeddings.insert(domain, embedding.clone());
        // Update universal embedding
        let n = self.domain_embeddings.len() as f32;
        self.universal_embedding = self.universal_embedding.bundle(&[embedding.scale(1.0 / n)]);
    }

    /// Get similarity to another concept
    pub fn similarity(&self, other: &SemanticConcept) -> f32 {
        self.universal_embedding.cosine_similarity(&other.universal_embedding)
    }
}

/// Result of semantic search
#[derive(Debug, Clone)]
pub struct SemanticSearchResult {
    /// Found concepts
    pub concepts: Vec<(SemanticConcept, f32)>,
    /// Query embedding
    pub query_embedding: RealHV,
    /// Search domain
    pub domain: Option<SemanticDomain>,
}

/// The universal semantics system
#[derive(Debug)]
pub struct UniversalSemantics {
    /// Configuration
    config: UniversalSemanticsConfig,
    /// Domain basis vectors
    domain_bases: HashMap<SemanticDomain, RealHV>,
    /// Stored concepts
    concepts: HashMap<String, SemanticConcept>,
    /// Cross-domain mapping weights
    domain_mappings: HashMap<(SemanticDomain, SemanticDomain), RealHV>,
    /// Statistics
    stats: UniversalSemanticsStats,
}

/// Statistics for universal semantics
#[derive(Debug, Clone, Default)]
pub struct UniversalSemanticsStats {
    /// Concepts stored
    pub concepts_stored: u64,
    /// Searches performed
    pub searches: u64,
    /// Cross-domain transfers
    pub cross_domain_transfers: u64,
    /// Average similarity score
    pub avg_similarity: f32,
}

impl UniversalSemantics {
    /// Create a new universal semantics system
    pub fn new(config: UniversalSemanticsConfig) -> Self {
        let dim = config.dimension;

        // Initialize domain bases
        let mut domain_bases = HashMap::new();
        for domain in [
            SemanticDomain::Language,
            SemanticDomain::Visual,
            SemanticDomain::Audio,
            SemanticDomain::Mathematical,
            SemanticDomain::Spatial,
            SemanticDomain::Temporal,
            SemanticDomain::Emotional,
            SemanticDomain::Abstract,
        ] {
            domain_bases.insert(domain, RealHV::random(dim));
        }

        Self {
            config,
            domain_bases,
            concepts: HashMap::new(),
            domain_mappings: HashMap::new(),
            stats: UniversalSemanticsStats::default(),
        }
    }

    /// Add a concept
    pub fn add_concept(&mut self, concept: SemanticConcept) {
        self.stats.concepts_stored += 1;
        self.concepts.insert(concept.id.clone(), concept);
    }

    /// Create a concept from text
    pub fn create_from_text(&mut self, id: impl Into<String>, text: &str) -> SemanticConcept {
        let embedding = self.encode_text(text);
        let concept = SemanticConcept::new(id, text, SemanticDomain::Language, embedding);
        self.add_concept(concept.clone());
        concept
    }

    /// Encode text to embedding
    pub fn encode_text(&self, text: &str) -> RealHV {
        let mut values = vec![0.0f32; self.config.dimension];

        // Simple encoding based on character positions
        for (i, c) in text.chars().enumerate() {
            let idx = (c as usize + i * 7) % self.config.dimension;
            values[idx] += 1.0;
        }

        // Add word-level features
        for (i, word) in text.split_whitespace().enumerate() {
            let word_hash = word.bytes().fold(0usize, |acc, b| acc.wrapping_add(b as usize * 31));
            let idx = word_hash % self.config.dimension;
            values[idx] += (i + 1) as f32 * 0.1;
        }

        // Normalize
        let magnitude: f32 = values.iter().map(|v| v * v).sum::<f32>().sqrt();
        if magnitude > 0.0 {
            for v in values.iter_mut() {
                *v /= magnitude;
            }
        }

        // Bind with language domain basis
        let text_hv = RealHV::from_slice(&values);
        if let Some(basis) = self.domain_bases.get(&SemanticDomain::Language) {
            text_hv.bind(basis)
        } else {
            text_hv
        }
    }

    /// Search for similar concepts
    pub fn search(&mut self, query: &RealHV, domain: Option<SemanticDomain>) -> SemanticSearchResult {
        self.stats.searches += 1;

        let mut results: Vec<_> = self.concepts.values()
            .map(|concept| {
                let embedding = domain
                    .and_then(|d| concept.domain_embeddings.get(&d))
                    .unwrap_or(&concept.universal_embedding);

                let similarity = query.cosine_similarity(embedding);
                (concept.clone(), similarity)
            })
            .filter(|(_, sim)| *sim >= self.config.similarity_threshold)
            .collect();

        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        // Update statistics
        if let Some((_, best_sim)) = results.first() {
            let n = self.stats.searches as f32;
            self.stats.avg_similarity = (self.stats.avg_similarity * (n - 1.0) + best_sim) / n;
        }

        SemanticSearchResult {
            concepts: results,
            query_embedding: query.clone(),
            domain,
        }
    }

    /// Transfer concept to another domain
    pub fn transfer_domain(&mut self, concept: &mut SemanticConcept, target_domain: SemanticDomain) {
        if !self.config.cross_domain_enabled {
            return;
        }

        self.stats.cross_domain_transfers += 1;

        // Get or create mapping
        let key = (concept.source_domain, target_domain);
        let mapping = self.domain_mappings.entry(key).or_insert_with(|| {
            RealHV::random(self.config.dimension)
        });

        // Apply mapping
        let transferred = concept.universal_embedding.bind(mapping);
        concept.add_domain_embedding(target_domain, transferred);
    }

    /// Get domain basis
    pub fn domain_basis(&self, domain: SemanticDomain) -> Option<&RealHV> {
        self.domain_bases.get(&domain)
    }

    /// Get concept by ID
    pub fn get_concept(&self, id: &str) -> Option<&SemanticConcept> {
        self.concepts.get(id)
    }

    /// Get all concepts
    pub fn concepts(&self) -> impl Iterator<Item = &SemanticConcept> {
        self.concepts.values()
    }

    /// Get statistics
    pub fn stats(&self) -> &UniversalSemanticsStats {
        &self.stats
    }
}

impl Default for UniversalSemantics {
    fn default() -> Self {
        Self::new(UniversalSemanticsConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_universal_semantics_creation() {
        let us = UniversalSemantics::default();
        assert_eq!(us.concepts.len(), 0);
    }

    #[test]
    fn test_concept_creation() {
        let mut us = UniversalSemantics::default();
        let concept = us.create_from_text("c1", "Hello world");

        assert_eq!(concept.source_domain, SemanticDomain::Language);
        assert_eq!(us.stats.concepts_stored, 1);
    }

    #[test]
    fn test_semantic_search() {
        let mut us = UniversalSemantics::default();

        us.create_from_text("c1", "cat");
        us.create_from_text("c2", "dog");
        us.create_from_text("c3", "kitten");

        let query = us.encode_text("cat");
        let results = us.search(&query, None);

        assert!(!results.concepts.is_empty());
    }

    #[test]
    fn test_domain_transfer() {
        let mut us = UniversalSemantics::default();
        let mut concept = us.create_from_text("c1", "happy");

        us.transfer_domain(&mut concept, SemanticDomain::Emotional);

        assert!(concept.domain_embeddings.contains_key(&SemanticDomain::Emotional));
    }

    #[test]
    fn test_concept_similarity() {
        let mut us = UniversalSemantics::default();

        let c1 = us.create_from_text("c1", "hello");
        let c2 = us.create_from_text("c2", "hello world");

        let similarity = c1.similarity(&c2);
        // Similar texts should have some similarity
        assert!(similarity > 0.0);
    }
}
