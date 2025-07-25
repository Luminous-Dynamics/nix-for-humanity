// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use anyhow::Result;
use serde::{Deserialize, Serialize};
use tauri::Manager;

mod commands;
mod nlp;
mod nix;
mod security;

use commands::*;

#[derive(Debug, Serialize, Deserialize)]
struct AppState {
    #[serde(skip)]
    nlp_engine: nlp::NLPEngine,
}

fn main() {
    tracing_subscriber::fmt::init();

    tauri::Builder::default()
        .setup(|app| {
            // Initialize NLP engine
            let nlp_engine = nlp::NLPEngine::new()?;
            
            // Store in app state
            app.manage(AppState { nlp_engine });
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            process_natural_language,
            get_system_info,
            execute_nix_command,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// Natural language processing command
#[tauri::command]
async fn process_natural_language(
    input: String,
    state: tauri::State<'_, AppState>,
) -> Result<nlp::Intent, String> {
    state.nlp_engine
        .process(&input)
        .await
        .map_err(|e| e.to_string())
}

// Get system information
#[tauri::command]
async fn get_system_info() -> Result<nix::SystemInfo, String> {
    nix::get_system_info()
        .await
        .map_err(|e| e.to_string())
}

// Execute Nix command (with security checks)
#[tauri::command]
async fn execute_nix_command(
    command: nix::NixCommand,
) -> Result<nix::CommandResult, String> {
    // Security validation
    security::validate_command(&command)
        .map_err(|e| format!("Security check failed: {}", e))?;
    
    // Execute in sandbox
    nix::execute_command(command)
        .await
        .map_err(|e| e.to_string())
}