/*!
Symthaea: Holographic Liquid Brain

## Core Library with Fixed Imports

All modules now use symthaea_core for HDC primitives, eliminating
the previous circular dependency issues.
*/

#![allow(dead_code, unused_variables, unused_imports)]

// Stable perception module (contains physio for EEG processing and video for rhythm detection)
pub mod perception;

// Hierarchical Cantor-LTC Network (required by perception/video)
pub mod hierarchical_cantor_ltc;

// Mind orchestration system
pub mod mind;

// Re-export key types at crate root for convenience
pub use mind::{ContinuousMind, MindConfig, MindState};

// Minimal prelude
pub mod prelude;

// Re-export symthaea-core for direct access to HDC primitives
pub use symthaea_core;

// Re-export hdc module at crate root for examples/backwards compatibility
pub use symthaea_core::hdc;
