//! Physiological Signal Processing
//!
//! This module provides tools for processing physiological signals:
//! - EDF file parsing (European Data Format)
//! - Sleep stage classification
//! - Consciousness state detection
//!
//! ## Project Hypnos
//!
//! The SleepSentinel uses LTC dynamics to detect consciousness states
//! from EEG signals, validating Symthaea's architecture on real clinical data.
//!
//! NOTE: sleep_sentinel temporarily disabled - depends on unified_ltc.
//! The benchmark example (examples/sleep_stage_benchmark.rs) is self-contained.

pub mod edf_loader;
pub mod entropy;  // Permutation Entropy for consciousness detection
// pub mod sleep_sentinel;  // Disabled: requires unified_ltc module

pub use edf_loader::{EdfFile, EdfSignal, SleepAnnotation, SleepStage};
pub use entropy::{permutation_entropy_order3, permutation_entropy_order4, weighted_permutation_entropy};
// pub use sleep_sentinel::{SleepSentinel, ConsciousnessState, SleepSentinelConfig};
