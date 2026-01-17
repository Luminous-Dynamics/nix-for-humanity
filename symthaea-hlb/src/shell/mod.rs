//! Shell Module - Command Interface
//!
//! Provides a rich, consciousness-aware command shell interface including:
//! - Alias management and expansion
//! - Epistemic overlays for uncertainty
//! - Error explanation with context
//! - Flake environment management
//! - Keybindings and theming
//! - Notifications and service state
//! - Syntax highlighting
//! - Undo/redo operations
//! - What-if speculation

use serde::{Deserialize, Serialize};

pub mod aliases;
pub mod epistemic_overlay;
pub mod error_explainer;
pub mod flake_context;
pub mod keybindings;
pub mod notifications;
pub mod service_state;
pub mod syntax_highlight;
pub mod theming;
pub mod undo;
pub mod whatif;

// Re-export commonly used types
pub use aliases::{AliasManager, Alias};
pub use epistemic_overlay::{OverlayPosition, OverlayType, EpistemicStyle};
pub use undo::{UndoAction, ActionType, ActionData};
pub use whatif::WhatIfResult;

/// Shell configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShellConfig {
    /// History size
    pub history_size: usize,
    /// Enable suggestions
    pub suggestions_enabled: bool,
    /// Enable syntax highlighting
    pub syntax_highlighting: bool,
    /// Enable epistemic overlays
    pub epistemic_overlays: bool,
    /// Theme name
    pub theme: String,
    /// Undo stack size
    pub undo_stack_size: usize,
}

impl Default for ShellConfig {
    fn default() -> Self {
        Self {
            history_size: 1000,
            suggestions_enabled: true,
            syntax_highlighting: true,
            epistemic_overlays: true,
            theme: "consciousness-dark".to_string(),
            undo_stack_size: 100,
        }
    }
}
