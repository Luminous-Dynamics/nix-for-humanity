// Test main for verifying backend compilation without Tauri GUI

use tracing::{info, Level};
use tracing_subscriber;

mod config;
mod nixos;
mod security;
mod state;

// Import command modules to ensure they compile
mod commands {
    pub mod config;
    pub mod packages;
    pub mod services;
    pub mod system;
    pub mod sacred;
    pub mod auth;
    
    // Re-export
    pub use config::*;
    pub use packages::*;
    pub use services::*;
    pub use system::*;
    pub use sacred::*;
    pub use auth::*;
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize logging
    tracing_subscriber::fmt()
        .with_max_level(Level::DEBUG)
        .init();
    
    info!("🌟 NixOS GUI Backend Test Starting...");
    
    // Test state initialization
    let state = state::AppState::new()?;
    info!("✅ State initialized successfully");
    
    // Test NixOS config reading (if available)
    match nixos::NixosConfig::read().await {
        Ok(config) => {
            info!("✅ Successfully read NixOS config from: {:?}", config.path);
            info!("   Is flake: {}", config.is_flake);
            info!("   Size: {} bytes", config.content.len());
        }
        Err(e) => {
            info!("ℹ️  Could not read NixOS config (expected in test): {}", e);
        }
    }
    
    // Test package manager
    info!("Testing package search...");
    match nixos::packages::PackageManager::search("test", Some(5)).await {
        Ok(result) => {
            info!("✅ Package search works! Found {} packages", result.total_count);
        }
        Err(e) => {
            info!("ℹ️  Package search not available: {}", e);
        }
    }
    
    // Test service manager
    info!("Testing service listing...");
    match nixos::services::ServiceManager::list_all().await {
        Ok(services) => {
            info!("✅ Service listing works! Found {} services", services.len());
        }
        Err(e) => {
            info!("ℹ️  Service listing not available: {}", e);
        }
    }
    
    // Test sacred features
    info!("Testing sacred features...");
    let intention = commands::sacred::Intention {
        text: "Test the backend compilation".to_string(),
        set_at: chrono::Utc::now(),
        duration_minutes: 60,
    };
    state.set_current_intention(intention).await;
    info!("✅ Sacred intention set");
    
    let coherence = state.get_coherence_level().await;
    info!("✅ Coherence level: {}", coherence);
    
    info!("");
    info!("🎉 Backend compilation test complete!");
    info!("All core modules compile successfully.");
    
    Ok(())
}