use crate::nixos::packages::{PackageManager, Package};
use crate::security::Permission;
use crate::state::AppState;
use tauri::State;
use tracing::info;

#[tauri::command]
pub async fn search_packages(
    query: String,
    state: State<'_, AppState>,
) -> Result<Vec<Package>, String> {
    info!("🔍 Searching packages for: {}", query);
    
    // Check permissions
    state.check_permission(Permission::ViewSystemInfo)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Validate query
    if query.len() < 2 {
        return Err("Search query must be at least 2 characters".to_string());
    }
    
    if query.len() > 100 {
        return Err("Search query too long".to_string());
    }
    
    // Perform search with limit
    let result = PackageManager::search(&query, Some(50))
        .await
        .map_err(|e| format!("Package search failed: {}", e))?;
    
    // Update task count
    state.increment_tasks().await;
    
    Ok(result.packages)
}

#[tauri::command]
pub async fn install_package(
    name: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("📦 Installing package: {}", name);
    
    // Check permissions
    state.check_permission(Permission::ManagePackages)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Check authentication
    if !state.is_authenticated().await {
        return Err("Authentication required for package installation".to_string());
    }
    
    // Sacred pause before installation
    info!("🧘 Taking sacred pause before package installation...");
    state.emit_event("sacred-pause", &serde_json::json!({
        "duration": 2,
        "message": "Preparing to install package..."
    })).ok();
    
    // Install package
    let result = PackageManager::install(&name, false)
        .await
        .map_err(|e| format!("Installation failed: {}", e))?;
    
    // Emit success event
    state.emit_event("package-installed", &serde_json::json!({
        "name": name,
        "message": result
    })).ok();
    
    Ok(result)
}

#[tauri::command]
pub async fn remove_package(
    name: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("🗑️ Removing package: {}", name);
    
    // Check permissions
    state.check_permission(Permission::ManagePackages)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Check authentication
    if !state.is_authenticated().await {
        return Err("Authentication required for package removal".to_string());
    }
    
    // Confirm critical packages
    let critical_packages = ["nixos-rebuild", "nix", "systemd", "kernel"];
    if critical_packages.contains(&name.as_str()) {
        return Err(format!("Cannot remove critical system package: {}", name));
    }
    
    // Remove package
    let result = PackageManager::remove(&name)
        .await
        .map_err(|e| format!("Removal failed: {}", e))?;
    
    // Emit success event
    state.emit_event("package-removed", &serde_json::json!({
        "name": name,
        "message": result
    })).ok();
    
    Ok(result)
}

#[tauri::command]
pub async fn list_installed_packages(
    state: State<'_, AppState>,
) -> Result<Vec<Package>, String> {
    info!("📋 Listing installed packages");
    
    // Check permissions
    state.check_permission(Permission::ViewSystemInfo)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // List packages
    let packages = PackageManager::list_installed()
        .await
        .map_err(|e| format!("Failed to list packages: {}", e))?;
    
    info!("✨ Found {} installed packages", packages.len());
    Ok(packages)
}