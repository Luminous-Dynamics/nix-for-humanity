//! Core types for the Web Research Integration module.
//!
//! These are scaffolded type definitions that allow other parts of the
//! Symthaea codebase to reference web research types. Methods return
//! reasonable defaults; real implementation will replace the stubs.

use std::collections::HashMap;

// ============================================================================
// Enums
// ============================================================================

/// Source type for research material
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub enum ResearchSource {
    /// General web sources
    #[default]
    Web,
    /// Official documentation (language docs, API docs, etc.)
    Documentation,
    /// Academic papers and preprints (arXiv, PubMed, etc.)
    Academic,
}

impl ResearchSource {
    /// Human-readable label for this source type
    pub fn label(&self) -> &'static str {
        match self {
            Self::Web => "Web",
            Self::Documentation => "Documentation",
            Self::Academic => "Academic",
        }
    }
}

/// Status of a research operation
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub enum ResearchStatus {
    /// Research completed successfully with results
    #[default]
    Success,
    /// Query returned no relevant results
    NoResults,
    /// An error occurred during research
    Error,
    /// Request was rate-limited by the source
    RateLimited,
}

impl ResearchStatus {
    /// Whether the status represents a successful outcome
    pub fn is_success(&self) -> bool {
        matches!(self, Self::Success)
    }

    /// Whether the status represents a retriable failure
    pub fn is_retriable(&self) -> bool {
        matches!(self, Self::RateLimited)
    }
}

/// Epistemic status of a verified claim
///
/// Ranges from high confidence to known false, with gradations
/// for uncertainty and insufficient evidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub enum EpistemicStatus {
    /// Claim is well-supported by multiple reliable sources
    HighConfidence,
    /// Claim is supported but with some caveats
    #[default]
    ModerateConfidence,
    /// Claim has limited supporting evidence
    LowConfidence,
    /// Not enough information to assess the claim
    InsufficientEvidence,
    /// Sources actively contradict the claim
    Contradicted,
    /// Claim is demonstrably false
    False,
}

impl EpistemicStatus {
    /// Numeric confidence score (0.0 - 1.0) for this status level
    pub fn confidence_score(&self) -> f32 {
        match self {
            Self::HighConfidence => 0.95,
            Self::ModerateConfidence => 0.70,
            Self::LowConfidence => 0.40,
            Self::InsufficientEvidence => 0.20,
            Self::Contradicted => 0.10,
            Self::False => 0.0,
        }
    }

    /// Suggested hedge phrase when presenting a claim at this level
    pub fn hedge_phrase(&self) -> &'static str {
        match self {
            Self::HighConfidence => "According to multiple reliable sources,",
            Self::ModerateConfidence => "Evidence suggests that",
            Self::LowConfidence => "Some sources indicate that",
            Self::InsufficientEvidence => "I have limited information, but",
            Self::Contradicted => "Sources disagree, however",
            Self::False => "This appears to be incorrect;",
        }
    }
}

// ============================================================================
// Core Structs
// ============================================================================

/// A query to perform web research
#[derive(Debug, Clone, Default)]
pub struct WebResearchQuery {
    /// The natural-language query text
    pub query: String,
    /// Preferred source types (empty means all)
    pub preferred_sources: Vec<ResearchSource>,
    /// Maximum number of results to return
    pub max_results: usize,
    /// Minimum relevance score (0.0 - 1.0) for inclusion
    pub min_relevance: f32,
    /// Optional domain restrictions (e.g. "rust-lang.org")
    pub domain_filter: Vec<String>,
}

impl WebResearchQuery {
    /// Create a new query with sensible defaults
    pub fn new(query: impl Into<String>) -> Self {
        Self {
            query: query.into(),
            preferred_sources: Vec::new(),
            max_results: 10,
            min_relevance: 0.3,
            domain_filter: Vec::new(),
        }
    }

    /// Set the maximum number of results
    pub fn with_max_results(mut self, n: usize) -> Self {
        self.max_results = n;
        self
    }

    /// Restrict to specific source types
    pub fn with_sources(mut self, sources: Vec<ResearchSource>) -> Self {
        self.preferred_sources = sources;
        self
    }

    /// Set minimum relevance threshold
    pub fn with_min_relevance(mut self, threshold: f32) -> Self {
        self.min_relevance = threshold.clamp(0.0, 1.0);
        self
    }
}

/// A single research result with source, content, and relevance
#[derive(Debug, Clone, Default)]
pub struct WebResearchResult {
    /// Title of the source page or document
    pub title: String,
    /// URL of the source
    pub url: String,
    /// Extracted content (clean text, not raw HTML)
    pub content: String,
    /// Short summary of the content
    pub summary: String,
    /// Source type classification
    pub source_type: ResearchSource,
    /// Relevance score (0.0 - 1.0) relative to the query
    pub relevance: f32,
    /// Overall confidence score (0.0 - 1.0)
    pub confidence: f32,
    /// Epistemic status after verification
    pub epistemic_status: EpistemicStatus,
    /// Status of the research operation
    pub status: ResearchStatus,
    /// Individual verified claims extracted from this result
    pub claims: Vec<VerifiedClaim>,
}

impl WebResearchResult {
    /// Create an empty result with the given status
    pub fn with_status(status: ResearchStatus) -> Self {
        Self {
            status,
            ..Default::default()
        }
    }

    /// Whether this result has usable content
    pub fn has_content(&self) -> bool {
        self.status.is_success() && !self.content.is_empty()
    }
}

/// A claim extracted from research, with epistemic verification
#[derive(Debug, Clone, Default)]
pub struct VerifiedClaim {
    /// The claim text
    pub text: String,
    /// Epistemic status of this claim
    pub status: EpistemicStatus,
    /// Confidence score (0.0 - 1.0)
    pub confidence: f32,
    /// Sources supporting this claim
    pub supporting_sources: Vec<String>,
    /// Sources contradicting this claim
    pub contradicting_sources: Vec<String>,
    /// Suggested hedge phrase for presenting this claim
    pub hedge: String,
}

impl VerifiedClaim {
    /// Create a new unverified claim
    pub fn new(text: impl Into<String>) -> Self {
        Self {
            text: text.into(),
            status: EpistemicStatus::InsufficientEvidence,
            confidence: 0.0,
            supporting_sources: Vec::new(),
            contradicting_sources: Vec::new(),
            hedge: EpistemicStatus::InsufficientEvidence.hedge_phrase().to_string(),
        }
    }
}

/// Configuration for the web research system
#[derive(Debug, Clone)]
pub struct WebResearchConfig {
    /// Maximum concurrent requests
    pub max_concurrent_requests: usize,
    /// Request timeout in milliseconds
    pub request_timeout_ms: u64,
    /// Maximum content length to process per page (bytes)
    pub max_content_length: usize,
    /// User agent string for HTTP requests
    pub user_agent: String,
    /// Enable epistemic verification of claims
    pub verify_claims: bool,
    /// Minimum confidence threshold for including results
    pub confidence_threshold: f32,
    /// Enable meta-learning (self-improving verification)
    pub meta_learning_enabled: bool,
    /// Source credibility scores (domain -> score)
    pub source_credibility: HashMap<String, f32>,
}

impl Default for WebResearchConfig {
    fn default() -> Self {
        Self {
            max_concurrent_requests: 5,
            request_timeout_ms: 10_000,
            max_content_length: 100_000,
            user_agent: "Symthaea-HLB/0.2 (Epistemic Research Agent)".to_string(),
            verify_claims: true,
            confidence_threshold: 0.3,
            meta_learning_enabled: false,
            source_credibility: HashMap::new(),
        }
    }
}

impl WebResearchConfig {
    /// Create a new config with defaults
    pub fn new() -> Self {
        Self::default()
    }

    /// Enable meta-learning
    pub fn with_meta_learning(mut self) -> Self {
        self.meta_learning_enabled = true;
        self
    }
}

/// Result of integrating research into the knowledge graph
#[derive(Debug, Clone, Default)]
pub struct IntegrationResult {
    /// Number of claims successfully integrated
    pub claims_integrated: usize,
    /// Number of new nodes added to the knowledge graph
    pub nodes_added: usize,
    /// Number of new edges added to the knowledge graph
    pub edges_added: usize,
    /// Phi value before integration
    pub phi_before: f64,
    /// Phi value after integration
    pub phi_after: f64,
    /// Consciousness improvement (phi_after - phi_before)
    pub phi_gain: f64,
}

impl IntegrationResult {
    /// Whether the integration improved consciousness (positive phi gain)
    pub fn improved_consciousness(&self) -> bool {
        self.phi_gain > 0.0
    }
}

/// Outcome of a verification for meta-learning tracking
#[derive(Debug, Clone, Default)]
pub struct VerificationOutcome {
    /// The claim that was verified
    pub claim: String,
    /// Source domain
    pub source_domain: String,
    /// Source type
    pub source_type: ResearchSource,
    /// Whether verification was correct (ground truth)
    pub was_correct: bool,
    /// Predicted confidence at verification time
    pub predicted_confidence: f32,
    /// Topic/domain of the claim
    pub domain: String,
}

// ============================================================================
// Stub Structs for Orchestrators (future implementation)
// ============================================================================

/// Web researcher orchestrator (stub)
///
/// Coordinates the full research pipeline: query planning, fetching,
/// extraction, verification, and integration.
#[derive(Debug)]
pub struct WebResearcher {
    /// Configuration
    #[allow(dead_code)]
    config: WebResearchConfig,
}

impl WebResearcher {
    /// Create a new web researcher with default configuration
    pub fn new() -> anyhow::Result<Self> {
        Ok(Self {
            config: WebResearchConfig::default(),
        })
    }

    /// Create a new web researcher with the given configuration
    pub fn with_config(config: WebResearchConfig) -> Self {
        Self { config }
    }

    /// Research and verify a query (stub - not yet implemented)
    pub async fn research_and_verify(&self, _query: &str) -> anyhow::Result<WebResearchResult> {
        unimplemented!(
            "WebResearcher::research_and_verify is scaffolded; \
             full implementation pending in src/web_research/researcher.rs"
        )
    }
}

impl Default for WebResearcher {
    fn default() -> Self {
        Self {
            config: WebResearchConfig::default(),
        }
    }
}

/// Epistemic verifier (stub)
///
/// Verifies claims against multiple sources and assigns epistemic status.
#[derive(Debug, Default)]
pub struct EpistemicVerifier {
    #[allow(dead_code)]
    _private: (),
}

impl EpistemicVerifier {
    /// Create a new epistemic verifier
    pub fn new() -> Self {
        Self::default()
    }

    /// Verify a claim (stub - not yet implemented)
    pub fn verify_claim(
        &self,
        _claim: &str,
        _sources: &[WebResearchResult],
    ) -> VerifiedClaim {
        unimplemented!(
            "EpistemicVerifier::verify_claim is scaffolded; \
             full implementation pending in src/web_research/verifier.rs"
        )
    }
}

/// Knowledge integrator (stub)
///
/// Integrates verified research results into the knowledge graph,
/// measuring phi gain from the integration.
#[derive(Debug, Default)]
pub struct KnowledgeIntegrator {
    #[allow(dead_code)]
    _private: (),
}

impl KnowledgeIntegrator {
    /// Create a new knowledge integrator
    pub fn new() -> Self {
        Self::default()
    }

    /// Integrate a research result into the knowledge graph (stub)
    pub async fn integrate(
        &mut self,
        _result: WebResearchResult,
    ) -> anyhow::Result<IntegrationResult> {
        unimplemented!(
            "KnowledgeIntegrator::integrate is scaffolded; \
             full implementation pending in src/web_research/integrator.rs"
        )
    }
}

/// Epistemic learner for meta-learning (stub)
///
/// Tracks verification outcomes and learns source trustworthiness
/// per domain, developing expertise over time.
#[derive(Debug, Default)]
pub struct EpistemicLearner {
    #[allow(dead_code)]
    _private: (),
}

impl EpistemicLearner {
    /// Create a new epistemic learner
    pub fn new() -> Self {
        Self::default()
    }

    /// Record a verification outcome for learning (stub)
    pub fn record_outcome(&mut self, _outcome: VerificationOutcome) -> anyhow::Result<()> {
        unimplemented!(
            "EpistemicLearner::record_outcome is scaffolded; \
             full implementation pending in src/web_research/meta_learning.rs"
        )
    }
}
