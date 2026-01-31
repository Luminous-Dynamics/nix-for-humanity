//! # Memory Module: Consciousness Persistence
//!
//! This module provides memory systems for consciousness persistence,
//! including episodic memory (hippocampus), conversation memory,
//! and memory consolidation systems.

pub mod coherence_tracker;
pub mod conversation_memory;
pub mod hippocampus;

// Re-export key types
pub use hippocampus::{
    HippocampusActor, MemoryTrace, RecallQuery, RecallResult,
    EmotionalValence, HippocampusStats,
};
