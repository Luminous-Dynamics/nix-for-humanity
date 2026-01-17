//! # LLM Organ: Large Language Model Integration
//!
//! Provides integration with large language models for:
//! - Text generation and completion
//! - Question answering
//! - Reasoning and analysis
//! - Conversation management

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, VecDeque};
use crate::hdc::RealHV;

/// Configuration for LLM organ
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMOrganConfig {
    /// Embedding dimension for internal representations
    pub dimension: usize,
    /// Maximum context length
    pub max_context_length: usize,
    /// Temperature for generation
    pub temperature: f32,
    /// Top-p sampling parameter
    pub top_p: f32,
    /// Maximum generation length
    pub max_generation_length: usize,
    /// Enable conversation memory
    pub memory_enabled: bool,
    /// Model identifier (for external LLM)
    pub model_id: String,
}

impl Default for LLMOrganConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            max_context_length: 4096,
            temperature: 0.7,
            top_p: 0.9,
            max_generation_length: 1024,
            memory_enabled: true,
            model_id: "local".to_string(),
        }
    }
}

/// A message in a conversation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversationMessage {
    /// Role (user, assistant, system)
    pub role: MessageRole,
    /// Message content
    pub content: String,
    /// Timestamp
    pub timestamp: u64,
    /// Embedding representation
    #[serde(skip)]
    pub embedding: Option<RealHV>,
}

/// Role in conversation
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MessageRole {
    /// System instructions
    System,
    /// User input
    User,
    /// Assistant response
    Assistant,
    /// Function/tool call
    Function,
}

impl ConversationMessage {
    /// Create a new message
    pub fn new(role: MessageRole, content: impl Into<String>) -> Self {
        Self {
            role,
            content: content.into(),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64,
            embedding: None,
        }
    }

    /// Create user message
    pub fn user(content: impl Into<String>) -> Self {
        Self::new(MessageRole::User, content)
    }

    /// Create assistant message
    pub fn assistant(content: impl Into<String>) -> Self {
        Self::new(MessageRole::Assistant, content)
    }

    /// Create system message
    pub fn system(content: impl Into<String>) -> Self {
        Self::new(MessageRole::System, content)
    }
}

/// LLM generation result
#[derive(Debug, Clone)]
pub struct LLMGenerationResult {
    /// Generated text
    pub text: String,
    /// Confidence/probability
    pub confidence: f32,
    /// Tokens generated
    pub tokens_generated: usize,
    /// Generation time (ms)
    pub generation_time_ms: f64,
    /// Embedding of generated text
    pub embedding: RealHV,
    /// Finish reason
    pub finish_reason: FinishReason,
}

/// Reason for finishing generation
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum FinishReason {
    /// Reached end of sequence
    EndOfSequence,
    /// Reached max length
    MaxLength,
    /// Stop token encountered
    StopToken,
    /// Error occurred
    Error,
}

/// Query for the LLM
#[derive(Debug, Clone)]
pub struct LLMQuery {
    /// Query type
    pub query_type: QueryType,
    /// Query content
    pub content: String,
    /// Context/history
    pub context: Vec<ConversationMessage>,
    /// System prompt
    pub system_prompt: Option<String>,
    /// Parameters override
    pub params: Option<LLMQueryParams>,
}

/// Type of query
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum QueryType {
    /// Open-ended generation
    Generation,
    /// Question answering
    QA,
    /// Summarization
    Summarization,
    /// Analysis/reasoning
    Analysis,
    /// Code generation
    Code,
    /// Conversation
    Conversation,
}

/// Query parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMQueryParams {
    /// Temperature override
    pub temperature: Option<f32>,
    /// Max length override
    pub max_length: Option<usize>,
    /// Stop sequences
    pub stop_sequences: Vec<String>,
}

/// The LLM organ system
#[derive(Debug)]
pub struct LLMOrgan {
    /// Configuration
    config: LLMOrganConfig,
    /// Conversation history
    conversation_history: VecDeque<ConversationMessage>,
    /// Text embeddings cache
    embedding_cache: HashMap<String, RealHV>,
    /// Statistics
    stats: LLMOrganStats,
}

/// Statistics for LLM organ
#[derive(Debug, Clone, Default)]
pub struct LLMOrganStats {
    /// Total queries processed
    pub queries_processed: u64,
    /// Total tokens generated
    pub tokens_generated: u64,
    /// Average generation time (ms)
    pub avg_generation_time_ms: f64,
    /// Cache hits
    pub cache_hits: u64,
    /// Errors encountered
    pub errors: u64,
}

impl LLMOrgan {
    /// Create a new LLM organ
    pub fn new(config: LLMOrganConfig) -> Self {
        Self {
            config,
            conversation_history: VecDeque::new(),
            embedding_cache: HashMap::new(),
            stats: LLMOrganStats::default(),
        }
    }

    /// Process a query
    pub fn query(&mut self, query: LLMQuery) -> LLMGenerationResult {
        let start = std::time::Instant::now();
        self.stats.queries_processed += 1;

        // In a real implementation, this would call an actual LLM
        // For now, provide a simulated response

        let response = match query.query_type {
            QueryType::QA => self.simulate_qa(&query.content),
            QueryType::Summarization => self.simulate_summarize(&query.content),
            QueryType::Analysis => self.simulate_analysis(&query.content),
            QueryType::Code => self.simulate_code(&query.content),
            QueryType::Conversation | QueryType::Generation => self.simulate_generation(&query.content),
        };

        let tokens_generated = response.split_whitespace().count();
        self.stats.tokens_generated += tokens_generated as u64;

        let generation_time = start.elapsed().as_secs_f64() * 1000.0;
        let n = self.stats.queries_processed as f64;
        self.stats.avg_generation_time_ms =
            (self.stats.avg_generation_time_ms * (n - 1.0) + generation_time) / n;

        // Create embedding for response
        let embedding = self.text_to_embedding(&response);

        // Add to conversation history
        if self.config.memory_enabled {
            self.conversation_history.push_back(ConversationMessage::user(&query.content));
            self.conversation_history.push_back(ConversationMessage::assistant(&response));

            // Trim history if too long
            while self.conversation_history.len() > 100 {
                self.conversation_history.pop_front();
            }
        }

        LLMGenerationResult {
            text: response,
            confidence: 0.85,
            tokens_generated,
            generation_time_ms: generation_time,
            embedding,
            finish_reason: FinishReason::EndOfSequence,
        }
    }

    /// Simulate QA response
    fn simulate_qa(&self, question: &str) -> String {
        format!("Based on my understanding, here is the answer to '{}': This would require connection to an actual LLM for accurate responses.", question)
    }

    /// Simulate summarization
    fn simulate_summarize(&self, text: &str) -> String {
        let words: Vec<_> = text.split_whitespace().take(20).collect();
        format!("Summary: {}...", words.join(" "))
    }

    /// Simulate analysis
    fn simulate_analysis(&self, content: &str) -> String {
        format!("Analysis of the provided content: The text discusses topics related to {}. Further analysis would require an actual LLM.",
            content.split_whitespace().take(5).collect::<Vec<_>>().join(" "))
    }

    /// Simulate code generation
    fn simulate_code(&self, prompt: &str) -> String {
        format!("// Generated code for: {}\n// Note: Actual code generation requires LLM connection\nfn example() {{\n    // Implementation here\n}}", prompt)
    }

    /// Simulate general generation
    fn simulate_generation(&self, prompt: &str) -> String {
        format!("Continuing from '{}': This is a simulated response. Connect to an actual LLM for real generation capabilities.", prompt)
    }

    /// Convert text to embedding
    fn text_to_embedding(&mut self, text: &str) -> RealHV {
        // Check cache
        if let Some(cached) = self.embedding_cache.get(text) {
            self.stats.cache_hits += 1;
            return cached.clone();
        }

        // Simple hash-based embedding (would use actual embedding model in production)
        let mut values = vec![0.0f32; self.config.dimension];

        for (i, c) in text.chars().enumerate() {
            let idx = (c as usize + i) % self.config.dimension;
            values[idx] += 1.0;
        }

        // Normalize
        let magnitude: f32 = values.iter().map(|v| v * v).sum::<f32>().sqrt();
        if magnitude > 0.0 {
            for v in values.iter_mut() {
                *v /= magnitude;
            }
        }

        let embedding = RealHV::from_slice(&values);

        // Cache
        if self.embedding_cache.len() < 1000 {
            self.embedding_cache.insert(text.to_string(), embedding.clone());
        }

        embedding
    }

    /// Generate text continuation
    pub fn generate(&mut self, prompt: &str) -> LLMGenerationResult {
        self.query(LLMQuery {
            query_type: QueryType::Generation,
            content: prompt.to_string(),
            context: Vec::new(),
            system_prompt: None,
            params: None,
        })
    }

    /// Answer a question
    pub fn answer(&mut self, question: &str) -> LLMGenerationResult {
        self.query(LLMQuery {
            query_type: QueryType::QA,
            content: question.to_string(),
            context: Vec::new(),
            system_prompt: None,
            params: None,
        })
    }

    /// Summarize text
    pub fn summarize(&mut self, text: &str) -> LLMGenerationResult {
        self.query(LLMQuery {
            query_type: QueryType::Summarization,
            content: text.to_string(),
            context: Vec::new(),
            system_prompt: None,
            params: None,
        })
    }

    /// Get conversation history
    pub fn conversation_history(&self) -> &VecDeque<ConversationMessage> {
        &self.conversation_history
    }

    /// Clear conversation history
    pub fn clear_history(&mut self) {
        self.conversation_history.clear();
    }

    /// Get statistics
    pub fn stats(&self) -> &LLMOrganStats {
        &self.stats
    }
}

impl Default for LLMOrgan {
    fn default() -> Self {
        Self::new(LLMOrganConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_llm_organ_creation() {
        let organ = LLMOrgan::default();
        assert_eq!(organ.stats.queries_processed, 0);
    }

    #[test]
    fn test_generation() {
        let mut organ = LLMOrgan::default();
        let result = organ.generate("Hello, world!");

        assert!(!result.text.is_empty());
        assert_eq!(organ.stats.queries_processed, 1);
    }

    #[test]
    fn test_qa() {
        let mut organ = LLMOrgan::default();
        let result = organ.answer("What is consciousness?");

        assert!(!result.text.is_empty());
        assert!(result.text.contains("answer"));
    }

    #[test]
    fn test_summarization() {
        let mut organ = LLMOrgan::default();
        let result = organ.summarize("This is a long text that needs to be summarized into a shorter form.");

        assert!(result.text.contains("Summary"));
    }

    #[test]
    fn test_conversation_memory() {
        let mut organ = LLMOrgan::default();
        organ.generate("First message");
        organ.generate("Second message");

        assert!(organ.conversation_history.len() >= 4);
    }
}
