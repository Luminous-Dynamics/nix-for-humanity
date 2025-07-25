/// Tauri command handlers for NixOS GUI
/// Each command follows consciousness-first principles

pub mod config;
pub mod packages;
pub mod services;
pub mod system;
pub mod sacred;
pub mod auth;

// Re-export all commands
pub use config::*;
pub use packages::*;
pub use services::*;
pub use system::*;
pub use sacred::*;
pub use auth::*;