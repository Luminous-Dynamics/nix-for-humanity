use crate::nixos::{NixosConfig, ValidationResult};
use crate::security::Permission;
use crate::state::AppState;
use serde::{Deserialize, Serialize};
use tauri::State;
use tracing::{info, warn};

#[derive(Debug, Serialize, Deserialize)]
pub struct ConfigResponse {
    pub content: String,
    pub path: String,
    pub last_modified: String,
    pub is_flake: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SaveConfigRequest {
    pub content: String,
    pub path: Option<String>,
    pub create_backup: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RebuildRequest {
    pub operation: String, // "switch", "boot", "test", "dry-build"
    pub flake: Option<String>,
    pub show_trace: bool,
}

/// Get the current NixOS configuration
#[tauri::command]
pub async fn get_configuration(
    state: State<'_, AppState>,
) -> Result<ConfigResponse, String> {
    info!("📖 Reading NixOS configuration with reverence...");
    
    // Check permissions
    state.check_permission(Permission::ReadConfig)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Read configuration
    let config = NixosConfig::read()
        .await
        .map_err(|e| format!("Failed to read configuration: {}", e))?;
    
    Ok(ConfigResponse {
        content: config.content,
        path: config.path.to_string_lossy().to_string(),
        last_modified: config.last_modified.to_rfc3339(),
        is_flake: config.is_flake,
    })
}

/// Validate NixOS configuration
#[tauri::command]
pub async fn validate_configuration(
    content: String,
    state: State<'_, AppState>,
) -> Result<ValidationResult, String> {
    info!("🔍 Validating configuration with careful attention...");
    
    // Check permissions
    state.check_permission(Permission::ValidateConfig)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Create temporary file for validation
    let result = NixosConfig::validate(&content)
        .await
        .map_err(|e| format!("Validation failed: {}", e))?;
    
    if !result.is_valid {
        warn!("⚠️ Configuration has issues: {:?}", result.errors);
    } else {
        info!("✅ Configuration is valid and harmonious");
    }
    
    Ok(result)
}

/// Save NixOS configuration with sacred backup
#[tauri::command]
pub async fn save_configuration(
    request: SaveConfigRequest,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("💾 Saving configuration with sacred intention...");
    
    // Check permissions
    state.check_permission(Permission::WriteConfig)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Validate before saving
    let validation = NixosConfig::validate(&request.content)
        .await
        .map_err(|e| format!("Pre-save validation failed: {}", e))?;
    
    if !validation.is_valid {
        return Err("Cannot save invalid configuration".to_string());
    }
    
    // Create backup if requested
    if request.create_backup {
        info!("📦 Creating sacred backup before changes...");
        NixosConfig::create_backup()
            .await
            .map_err(|e| format!("Backup failed: {}", e))?;
    }
    
    // Save configuration
    NixosConfig::save(&request.content, request.path.as_deref())
        .await
        .map_err(|e| format!("Save failed: {}", e))?;
    
    info!("✨ Configuration saved successfully");
    Ok("Configuration saved with grace".to_string())
}

/// Rebuild NixOS system with mindful process
#[tauri::command]
pub async fn rebuild_system(
    request: RebuildRequest,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("🔨 Beginning sacred system rebuild: {}", request.operation);
    
    // Check permissions - rebuild requires elevated privileges
    state.check_permission(Permission::RebuildSystem)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Emit event for UI to show sacred pause
    state.emit_event("rebuild-starting", &request)?;
    
    // Perform rebuild
    let output = NixosConfig::rebuild(
        &request.operation,
        request.flake.as_deref(),
        request.show_trace,
    )
    .await
    .map_err(|e| format!("Rebuild failed: {}", e))?;
    
    // Emit completion event
    state.emit_event("rebuild-complete", &output)?;
    
    info!("🌟 System rebuild completed successfully");
    Ok(output)
}