use crate::security::Permission;
use crate::state::AppState;
use serde::{Deserialize, Serialize};
use tauri::State;

#[derive(Debug, Serialize, Deserialize)]
pub struct AuthRequest {
    pub username: String,
    pub password: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AuthResponse {
    pub success: bool,
    pub token: Option<String>,
    pub permissions: Vec<Permission>,
}

#[tauri::command]
pub async fn authenticate(
    request: AuthRequest,
    state: State<'_, AppState>,
) -> Result<AuthResponse, String> {
    // TODO: Implement proper authentication
    // For now, this is a placeholder that checks for sudo capability
    
    if request.username == "admin" {
        let permissions = vec![
            Permission::ReadConfig,
            Permission::WriteConfig,
            Permission::ValidateConfig,
            Permission::RebuildSystem,
            Permission::ManagePackages,
            Permission::ManageServices,
            Permission::ViewSystemInfo,
        ];
        
        state.set_authenticated(true, permissions.clone()).await;
        
        Ok(AuthResponse {
            success: true,
            token: Some("sacred-token".to_string()),
            permissions,
        })
    } else {
        Ok(AuthResponse {
            success: false,
            token: None,
            permissions: vec![],
        })
    }
}

#[tauri::command]
pub async fn check_permissions(
    state: State<'_, AppState>,
) -> Result<Vec<Permission>, String> {
    // TODO: Return actual user permissions
    Ok(vec![Permission::ReadConfig, Permission::ViewSystemInfo])
}