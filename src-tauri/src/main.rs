// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct NixCommand {
    command: String,
    args: Vec<String>,
    dry_run: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct CommandResult {
    success: bool,
    output: String,
    error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct SacredCommand {
    command: String,
    args: Vec<String>,
    dry_run: bool,
    action: String,
    mantra: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct SacredIntent {
    action: String,
    mantra: String,
    confirmed: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
struct SacredResult {
    success: bool,
    message: String,
    output: Option<String>,
    error: Option<String>,
    mantra: String,
    requires_confirmation: Option<bool>,
    warning: Option<String>,
    command: Option<String>,
}

// Execute a NixOS command with safety controls
#[tauri::command]
async fn execute_nix_command(command: NixCommand) -> Result<CommandResult, String> {
    // Safety check: Only allow whitelisted commands
    let allowed_commands = vec![
        "nix", 
        "nix-env", 
        "nixos-rebuild", 
        "nix-channel",
        "nix-collect-garbage",
        "nix-store",
        "systemctl",
        "journalctl",
        "nixos-version"
    ];
    if !allowed_commands.contains(&command.command.as_str()) {
        return Err(format!("Command '{}' is not allowed", command.command));
    }

    // Build the command
    let mut cmd = Command::new(&command.command);
    for arg in &command.args {
        cmd.arg(arg);
    }

    // Add --dry-run if requested
    if command.dry_run {
        cmd.arg("--dry-run");
    }

    // Execute the command
    match cmd.output() {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            
            Ok(CommandResult {
                success: output.status.success(),
                output: stdout,
                error: if stderr.is_empty() { None } else { Some(stderr) },
            })
        }
        Err(e) => Err(format!("Failed to execute command: {}", e)),
    }
}

// Search for packages in nixpkgs
#[tauri::command]
async fn search_packages(query: String) -> Result<Vec<String>, String> {
    let output = Command::new("nix")
        .args(&["search", "nixpkgs", &query, "--json"])
        .output()
        .map_err(|e| format!("Search failed: {}", e))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        // Parse JSON and extract package names
        // For now, return raw output
        Ok(vec![stdout.to_string()])
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

// Get system information
#[tauri::command]
async fn get_system_info() -> Result<serde_json::Value, String> {
    let info = serde_json::json!({
        "os": "NixOS",
        "version": get_nixos_version().await?,
        "architecture": std::env::consts::ARCH,
    });
    Ok(info)
}

async fn get_nixos_version() -> Result<String, String> {
    let output = Command::new("nixos-version")
        .output()
        .map_err(|e| format!("Failed to get NixOS version: {}", e))?;
    
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

// Execute a sacred NixOS command with mindful intention
#[tauri::command]
async fn execute_sacred_command(command: SacredCommand, intent: SacredIntent) -> Result<SacredResult, String> {
    // Sacred commands require deeper validation
    let sacred_commands = vec![
        "nix", "nix-env", "nixos-rebuild", "nix-channel",
        "nix-collect-garbage", "nix-store", "systemctl",
        "journalctl", "nixos-version", "nix-shell", "home-manager"
    ];
    
    if !sacred_commands.contains(&command.command.as_str()) {
        return Err(format!("Command '{}' is not allowed in sacred space", command.command));
    }
    
    // Check if this is a dangerous action that needs confirmation
    let dangerous_actions = vec!["shutdown", "reboot", "garbage-collect", "rebuild"];
    if dangerous_actions.contains(&intent.action.as_str()) && intent.confirmed != Some(true) {
        return Ok(SacredResult {
            success: false,
            message: "This action requires mindful confirmation".to_string(),
            output: None,
            error: None,
            mantra: "Sacred boundaries protect us".to_string(),
            requires_confirmation: Some(true),
            warning: Some(get_sacred_warning(&intent.action)),
            command: Some(format!("{} {}", command.command, command.args.join(" "))),
        });
    }
    
    // Build the command with sacred intention
    let mut cmd = Command::new(&command.command);
    for arg in &command.args {
        cmd.arg(arg);
    }
    
    if command.dry_run {
        cmd.arg("--dry-run");
    }
    
    // Execute with mindfulness
    match cmd.output() {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            
            if output.status.success() {
                Ok(SacredResult {
                    success: true,
                    message: format!("✅ {}", get_success_message(&intent.action)),
                    output: Some(stdout),
                    error: None,
                    mantra: intent.mantra,
                    requires_confirmation: None,
                    warning: None,
                    command: None,
                })
            } else {
                Ok(SacredResult {
                    success: false,
                    message: "The command did not complete as expected".to_string(),
                    output: Some(stdout),
                    error: Some(stderr),
                    mantra: "Every error is a teacher".to_string(),
                    requires_confirmation: None,
                    warning: None,
                    command: None,
                })
            }
        }
        Err(e) => Err(format!("Failed to execute command: {}", e)),
    }
}

fn get_sacred_warning(action: &str) -> String {
    match action {
        "shutdown" => "This will turn off your computer. All unsaved work will be lost.".to_string(),
        "reboot" => "This will restart your computer. All applications will close.".to_string(),
        "garbage-collect" => "This will delete old system generations permanently.".to_string(),
        "rebuild" => "This will change your system configuration.".to_string(),
        _ => "This action requires careful consideration.".to_string(),
    }
}

fn get_success_message(action: &str) -> String {
    match action {
        "install" => "Package installed successfully".to_string(),
        "remove" => "Package removed successfully".to_string(),
        "update" => "System updated successfully".to_string(),
        "search" => "Search completed".to_string(),
        "info" => "Information retrieved".to_string(),
        _ => "Command completed successfully".to_string(),
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            execute_nix_command,
            execute_sacred_command,
            search_packages,
            get_system_info
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}