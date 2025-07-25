use crate::nixos::services::{ServiceManager, Service};
use crate::security::Permission;
use crate::state::AppState;
use tauri::State;
use tracing::info;

#[tauri::command]
pub async fn list_services(
    state: State<'_, AppState>,
) -> Result<Vec<Service>, String> {
    info!("📋 Listing system services");
    
    // Check permissions
    state.check_permission(Permission::ViewSystemInfo)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // List services
    let services = ServiceManager::list_all()
        .await
        .map_err(|e| format!("Failed to list services: {}", e))?;
    
    info!("✨ Found {} services", services.len());
    Ok(services)
}

#[tauri::command]
pub async fn get_service_status(
    name: String,
    state: State<'_, AppState>,
) -> Result<Service, String> {
    info!("🔍 Getting status for service: {}", name);
    
    // Check permissions
    state.check_permission(Permission::ViewSystemInfo)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Get service status
    let service = ServiceManager::get_status(&name)
        .await
        .map_err(|e| format!("Failed to get service status: {}", e))?;
    
    Ok(service)
}

#[tauri::command]
pub async fn start_service(
    name: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("▶️ Starting service: {}", name);
    
    // Check permissions
    state.check_permission(Permission::ManageServices)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Check authentication
    if !state.is_authenticated().await {
        return Err("Authentication required to manage services".to_string());
    }
    
    // Sacred pause before starting
    state.emit_event("service-operation", &serde_json::json!({
        "service": name,
        "operation": "start",
        "status": "preparing"
    })).ok();
    
    // Start service
    let result = ServiceManager::start(&name)
        .await
        .map_err(|e| format!("Failed to start service: {}", e))?;
    
    // Emit success event
    state.emit_event("service-started", &serde_json::json!({
        "service": name,
        "message": result
    })).ok();
    
    Ok(result)
}

#[tauri::command]
pub async fn stop_service(
    name: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("⏹️ Stopping service: {}", name);
    
    // Check permissions
    state.check_permission(Permission::ManageServices)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Check authentication
    if !state.is_authenticated().await {
        return Err("Authentication required to manage services".to_string());
    }
    
    // Sacred pause before stopping
    state.emit_event("service-operation", &serde_json::json!({
        "service": name,
        "operation": "stop",
        "status": "preparing"
    })).ok();
    
    // Stop service
    let result = ServiceManager::stop(&name)
        .await
        .map_err(|e| format!("Failed to stop service: {}", e))?;
    
    // Emit success event
    state.emit_event("service-stopped", &serde_json::json!({
        "service": name,
        "message": result
    })).ok();
    
    Ok(result)
}

#[tauri::command]
pub async fn enable_service(
    name: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("🔓 Enabling service: {}", name);
    
    // Check permissions
    state.check_permission(Permission::ManageServices)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Check authentication
    if !state.is_authenticated().await {
        return Err("Authentication required to manage services".to_string());
    }
    
    // Enable service
    let result = ServiceManager::enable(&name)
        .await
        .map_err(|e| format!("Failed to enable service: {}", e))?;
    
    // Emit success event
    state.emit_event("service-enabled", &serde_json::json!({
        "service": name,
        "message": result
    })).ok();
    
    Ok(result)
}

#[tauri::command]
pub async fn disable_service(
    name: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    info!("🔒 Disabling service: {}", name);
    
    // Check permissions
    state.check_permission(Permission::ManageServices)
        .map_err(|e| format!("Permission denied: {}", e))?;
    
    // Check authentication
    if !state.is_authenticated().await {
        return Err("Authentication required to manage services".to_string());
    }
    
    // Disable service
    let result = ServiceManager::disable(&name)
        .await
        .map_err(|e| format!("Failed to disable service: {}", e))?;
    
    // Emit success event
    state.emit_event("service-disabled", &serde_json::json!({
        "service": name,
        "message": result
    })).ok();
    
    Ok(result)
}