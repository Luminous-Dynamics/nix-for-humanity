//! Web Research Integration Module (Scaffolded)
//!
//! This module provides web research capabilities for grounding
//! Symthaea's responses in real-time information. Currently scaffolded
//! with type definitions; implementation to follow.
//!
//! # Architecture
//!
//! The full module will contain:
//! - `types.rs`          - Core types (Source, Claim, Query, Config, etc.)
//! - `extractor.rs`      - HTML to clean text extraction
//! - `verifier.rs`       - Epistemic verification engine
//! - `researcher.rs`     - Research orchestrator
//! - `integrator.rs`     - Knowledge graph integration
//! - `meta_learning.rs`  - Self-improving verification
//!
//! Currently only `types.rs` is provided as a scaffold so that other
//! modules can reference web research types without compilation errors.

pub mod types;

// Re-export key types for ergonomic access
pub use types::*;
