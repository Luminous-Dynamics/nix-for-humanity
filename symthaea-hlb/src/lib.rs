/*!
Symthaea: Holographic Liquid Brain

## Core Library with Fixed Imports

All modules now use symthaea_core for HDC primitives, eliminating
the previous circular dependency issues.

## Module Status
- ✅ Core: perception, hierarchical_cantor_ltc, mind, hdc, prelude
- ✅ Working: cfc, cognitive_loop, unified_ltc, learnable_ltc
- ✅ Partial: consciousness, memory, brain, language, physiology
- 🚧 Issues: Many modules have internal import issues that need resolution
*/

// ============================================================================
// Symthaea Facade (Primary Entry Point)
// ============================================================================
pub mod symthaea;
pub use symthaea::Symthaea;

// ============================================================================
// Core Modules (Stable, Verified Working)
// ============================================================================

// Perception: Multi-modal sensory processing
pub mod perception;

// Chronobiology: Time-dependent cognitive modulation
pub mod chronobiology;

// Hierarchical Cantor-LTC Network
pub mod hierarchical_cantor_ltc;

// Mind orchestration system
pub mod mind;

// Local HDC module - extends symthaea_core with additional modules
pub mod hdc;

// Minimal prelude
pub mod prelude;

// ============================================================================
// Standalone Module Files (Generally Stable)
// ============================================================================

// CfC (Closed-form Continuous-time) network
pub mod cfc;

// Cognitive loop for conscious processing
pub mod cognitive_loop;

// Unified LTC (Liquid Time-Constant) network
pub mod unified_ltc;

// Learnable LTC networks
pub mod learnable_ltc;

// Dynamics: attractor networks, temporal evolution
pub mod dynamics;

// ============================================================================
// Modules with Known Import Issues (Conditionally Compiled)
// Many of these have internal structural issues that need fixing
// ============================================================================

// Consciousness module (enabling - fixing dependencies)
pub mod consciousness;

// Memory systems (fixed and enabled)
pub mod memory;

// Brain regions (enabling - fixing errors)
pub mod brain;

// Soul module (enabled - self-contained)
pub mod soul;

// Language processing (enabled - core modules, advanced gated behind full_language)
pub mod language;

// School: learning (enabled - with stub lookahead when full feature disabled)
pub mod school;

// Physiology (enabled - social coherence and hormone modeling)
pub mod physiology;

// Voice (enabled - 0 errors)
pub mod voice;

// Resonant speech (enabled - 0 errors)
pub mod resonant_speech;

// Embeddings (enabling - self-contained module)
pub mod embeddings;

// Benchmarks (enabled - API fixes complete)
pub mod benchmarks;

// Integration (cfg-gated - needs significant API alignment)
// The integration module expects ExecutionStrategy as enum with variants
// (Lost, Curious, Confident, Autopilot) and other API differences
#[cfg(feature = "integration_module")]
pub mod integration;

// Action (depends on consciousness module - now enabled)
pub mod action;

// Partnership (enabled - 0 errors)
pub mod partnership;

// User state inference (enabled - 0 errors)
pub mod user_state_inference;

// Observability
#[cfg(feature = "observability_module")]
pub mod observability;

// Shell (enabled - language module provides NixErrorDiagnoser)
pub mod shell;

// Experience (enabled - md5 crate added)
pub mod experience;

// Wisdom (enabled - 0 errors)
pub mod wisdom;

// Mycelix (enabled - GIS, Kosmic Song, Dark Spot DHT)
pub mod mycelix;

// Swarm Intelligence (Hybrid Iroh + Holochain Architecture)
// Uses Iroh for real-time tensor streaming (<50ms) and Holochain for trust/identity
pub mod swarm;

// Safety (enabled - with stub implementations)
pub mod safety;

// Databases (enabled - types defined in mod.rs)
pub mod databases;

// Infrastructure (enabled - 0 errors)
pub mod infrastructure;

// Intelligence (enabled - 0 errors)
pub mod intelligence;

// Substrate (enabled - 0 errors)
pub mod substrate;

// GUI bridge (enabled - 0 errors)
pub mod gui_bridge;

// API
#[cfg(feature = "api_module")]
pub mod api;

// ============================================================================
// Re-exports for Convenience
// ============================================================================

// Re-export key types at crate root
pub use mind::{ContinuousMind, MindConfig, MindState};

// Re-export symthaea-core for direct access to HDC primitives
pub use symthaea_core;

// Re-export phi_engine for consciousness calculations
pub use symthaea_core::phi_engine;

// Re-export core module for primitives like ContinuousHV, HDC_DIMENSION
pub use symthaea_core::core;
