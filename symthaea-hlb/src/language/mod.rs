//! Language module - natural language processing and generation

pub mod consciousness_prompts;
pub mod emotional_core;
pub mod enhanced_consciousness;
pub mod generative_thought_engine;
pub mod learning_persistence;
pub mod llm_organ;
pub mod meta_conscious_llm_bridge;
pub mod multi_theory_consciousness;
pub mod nix_parser;
pub mod phi_monitor;
pub mod semantic_enrichment;

// Re-exports
pub use emotional_core::{EmotionalCore, EmotionalCoreConfig, EmotionalAnalysis, EmotionalResponse};
pub use llm_organ::{LLMOrgan, LLMOrganConfig, ConversationMessage, MessageRole, LLMGenerationResult, LLMQuery, QueryType};
