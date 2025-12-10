//! Week 12: Perception & Tool Creation - Giving Sophia Senses
//!
//! This module provides sensory capabilities for Sophia:
//! - Visual perception (images)
//! - Code perception (understanding source code)
//! - Enhanced proprioception (system state awareness)
//!
//! Foundation for tool usage and tool creation capabilities.

pub mod visual;
pub mod code;

pub use visual::{VisualCortex, VisualFeatures};
pub use code::{CodePerceptionCortex, ProjectStructure, RustCodeSemantics, CodeQualityAnalysis};
