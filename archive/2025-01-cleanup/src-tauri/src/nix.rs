use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NixCommand {
    pub operation: Operation,
    pub args: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum Operation {
    Install,
    Remove,
    Update,
    Search,
    Info,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CommandResult {
    pub success: bool,
    pub output: String,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    pub nixos_version: String,
    pub kernel_version: String,
    pub architecture: String,
    pub total_packages: usize,
}

pub async fn get_system_info() -> Result<SystemInfo> {
    // Get NixOS version
    let nixos_version = Command::new("nixos-version")
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_else(|_| "Unknown".to_string());

    // Get kernel version
    let kernel_version = Command::new("uname")
        .arg("-r")
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_else(|_| "Unknown".to_string());

    // Get architecture
    let architecture = Command::new("uname")
        .arg("-m")
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
        .unwrap_or_else(|_| "Unknown".to_string());

    Ok(SystemInfo {
        nixos_version,
        kernel_version,
        architecture,
        total_packages: 0, // TODO: Count installed packages
    })
}

pub async fn execute_command(command: NixCommand) -> Result<CommandResult> {
    // Build the actual command based on operation
    let (program, args) = match command.operation {
        Operation::Install => ("nix-env", vec!["-iA".to_string()]),
        Operation::Remove => ("nix-env", vec!["-e".to_string()]),
        Operation::Update => ("nixos-rebuild", vec!["switch".to_string()]),
        Operation::Search => ("nix", vec!["search".to_string()]),
        Operation::Info => ("nix-env", vec!["-qa".to_string()]),
    };

    let mut full_args = args;
    full_args.extend(command.args);

    // Execute command
    let output = Command::new(program)
        .args(&full_args)
        .output()?;

    Ok(CommandResult {
        success: output.status.success(),
        output: String::from_utf8_lossy(&output.stdout).to_string(),
        error: if output.status.success() {
            None
        } else {
            Some(String::from_utf8_lossy(&output.stderr).to_string())
        },
    })
}