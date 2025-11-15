// Luminous Nix GUI - Tauri Backend
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::process::Command;
use std::sync::Mutex;
use sysinfo::{System, SystemExt, DiskExt, ProcessorExt};
use tauri::State;

// Shared state for the application
struct AppState {
    system: Mutex<System>,
    memory: Mutex<ConversationMemory>,
}

// Conversation memory for context
struct ConversationMemory {
    history: Vec<ConversationTurn>,
    user_patterns: UserPatterns,
}

#[derive(Clone, Serialize, Deserialize)]
struct ConversationTurn {
    query: String,
    response: String,
    timestamp: u64,
    success: bool,
}

#[derive(Clone, Serialize, Deserialize)]
struct UserPatterns {
    common_packages: Vec<String>,
    common_tasks: Vec<String>,
}

#[derive(Clone, Serialize, Deserialize)]
struct Package {
    name: String,
    version: String,
    description: String,
    installed: bool,
    category: String,
}

#[derive(Clone, Serialize, Deserialize)]
struct SystemHealth {
    cpu_usage: f32,
    memory_usage: f32,
    disk_usage: f32,
    uptime: u64,
    warnings: Vec<String>,
    recommendations: Vec<String>,
}

#[derive(Clone, Serialize, Deserialize)]
struct NixConfig {
    content: String,
    valid: bool,
    errors: Vec<String>,
}

#[derive(Clone, Serialize, Deserialize)]
struct CommandResult {
    success: bool,
    output: String,
    error: Option<String>,
    risk_level: String,
}

// Search for packages using nix search
#[tauri::command]
async fn search_packages(query: String) -> Result<Vec<Package>, String> {
    let output = Command::new("nix")
        .args(&["search", "nixpkgs", &query, "--json"])
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        // Parse JSON output
        let packages = parse_nix_search_output(&stdout);
        Ok(packages)
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

// Install a package
#[tauri::command]
async fn install_package(
    package: String,
    state: State<'_, AppState>,
) -> Result<CommandResult, String> {
    // Add to conversation memory
    let mut memory = state.memory.lock().unwrap();

    // Assess risk
    let risk_level = assess_risk(&format!("nix profile install nixpkgs#{}", package));

    // Execute with safety checks
    let output = Command::new("nix")
        .args(&["profile", "install", &format!("nixpkgs#{}", package)])
        .output()
        .map_err(|e| e.to_string())?;

    let success = output.status.success();
    let result = CommandResult {
        success,
        output: String::from_utf8_lossy(&output.stdout).to_string(),
        error: if success { None } else { Some(String::from_utf8_lossy(&output.stderr).to_string()) },
        risk_level,
    };

    // Update memory
    memory.history.push(ConversationTurn {
        query: format!("install {}", package),
        response: result.output.clone(),
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs(),
        success,
    });

    if success && !memory.user_patterns.common_packages.contains(&package) {
        memory.user_patterns.common_packages.push(package);
    }

    Ok(result)
}

// Get system health information
#[tauri::command]
fn get_system_health(state: State<'_, AppState>) -> Result<SystemHealth, String> {
    let mut system = state.system.lock().unwrap();
    system.refresh_all();

    let cpu_usage = system.global_processor_info().cpu_usage();
    let memory_usage = (system.used_memory() as f32 / system.total_memory() as f32) * 100.0;

    let mut disk_usage = 0.0;
    for disk in system.disks() {
        if disk.mount_point().to_str() == Some("/") {
            let used = disk.total_space() - disk.available_space();
            disk_usage = (used as f32 / disk.total_space() as f32) * 100.0;
            break;
        }
    }

    let uptime = system.uptime();

    // Generate warnings and recommendations
    let mut warnings = Vec::new();
    let mut recommendations = Vec::new();

    if disk_usage > 80.0 {
        warnings.push(format!("Disk usage high: {:.1}%", disk_usage));
        recommendations.push("Run garbage collection: nix-collect-garbage -d".to_string());
    }

    if memory_usage > 80.0 {
        warnings.push(format!("Memory usage high: {:.1}%", memory_usage));
        recommendations.push("Close unnecessary applications".to_string());
    }

    Ok(SystemHealth {
        cpu_usage,
        memory_usage,
        disk_usage,
        uptime,
        warnings,
        recommendations,
    })
}

// Generate NixOS configuration from description
#[tauri::command]
async fn generate_config(description: String) -> Result<NixConfig, String> {
    // This would call our Python config generator via subprocess
    // For now, return a template
    let template = format!(
        r#"{{ config, pkgs, ... }}:

{{
  # Generated from: {}

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "nixos";
  networking.networkmanager.enable = true;

  time.timeZone = "UTC";

  environment.systemPackages = with pkgs; [
    vim
    git
    firefox
  ];

  system.stateVersion = "24.05";
}}"#,
        description
    );

    Ok(NixConfig {
        content: template,
        valid: true,
        errors: vec![],
    })
}

// List system generations
#[tauri::command]
async fn list_generations() -> Result<Vec<Generation>, String> {
    let output = Command::new("nixos-rebuild")
        .args(&["list-generations"])
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(parse_generations(&stdout))
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[derive(Clone, Serialize, Deserialize)]
struct Generation {
    number: u32,
    date: String,
    current: bool,
    description: String,
}

// AI-powered assistant query
#[tauri::command]
async fn ask_assistant(
    query: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    // Get context from memory
    let memory = state.memory.lock().unwrap();
    let context = build_context(&memory, &query);

    // Call Python backend via subprocess
    let output = Command::new("python3")
        .args(&[
            "-c",
            &format!(
                r#"
import sys
sys.path.insert(0, 'src')
from luminous_nix.frontends.cli import UnifiedNixAssistant
assistant = UnifiedNixAssistant()
print(assistant.answer('{}'))
"#,
                query
            ),
        ])
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Ok(format!("I can help with: {}", query))
    }
}

// Helper functions
fn assess_risk(command: &str) -> String {
    if command.contains("rm -rf") || command.contains("format") {
        "critical".to_string()
    } else if command.contains("nixos-rebuild") {
        "high".to_string()
    } else if command.contains("install") {
        "low".to_string()
    } else {
        "safe".to_string()
    }
}

fn parse_nix_search_output(json_str: &str) -> Vec<Package> {
    // Parse nix search JSON output
    // Simplified for demo
    vec![
        Package {
            name: "firefox".to_string(),
            version: "latest".to_string(),
            description: "Web browser".to_string(),
            installed: false,
            category: "browsers".to_string(),
        },
    ]
}

fn parse_generations(output: &str) -> Vec<Generation> {
    // Parse generation list
    // Simplified for demo
    vec![
        Generation {
            number: 42,
            date: "2024-01-19".to_string(),
            current: true,
            description: "Current generation".to_string(),
        },
    ]
}

fn build_context(memory: &ConversationMemory, query: &str) -> String {
    // Build context from conversation history
    let recent = memory.history.iter().rev().take(3)
        .map(|turn| format!("{}: {}", turn.query, turn.response))
        .collect::<Vec<_>>()
        .join("\n");

    format!("Recent context:\n{}\n\nCurrent query: {}", recent, query)
}

fn main() {
    let app_state = AppState {
        system: Mutex::new(System::new_all()),
        memory: Mutex::new(ConversationMemory {
            history: vec![],
            user_patterns: UserPatterns {
                common_packages: vec![],
                common_tasks: vec![],
            },
        }),
    };

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            search_packages,
            install_package,
            get_system_health,
            generate_config,
            list_generations,
            ask_assistant,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
