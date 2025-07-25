use anyhow::{bail, Result};
use crate::nix::{NixCommand, Operation};

/// Validate that a command is safe to execute
pub fn validate_command(command: &NixCommand) -> Result<()> {
    // Check for dangerous patterns in arguments
    for arg in &command.args {
        if contains_dangerous_pattern(arg) {
            bail!("Potentially dangerous command pattern detected");
        }
    }

    // Validate based on operation type
    match &command.operation {
        Operation::Install | Operation::Remove => {
            // Ensure package names are valid
            for arg in &command.args {
                if !is_valid_package_name(arg) {
                    bail!("Invalid package name: {}", arg);
                }
            }
        }
        Operation::Update => {
            // Update operations need extra validation
            if command.args.iter().any(|a| a.contains("--rollback")) {
                // Rollback requires confirmation
                bail!("Rollback operations require explicit confirmation");
            }
        }
        _ => {}
    }

    Ok(())
}

fn contains_dangerous_pattern(s: &str) -> bool {
    let dangerous_patterns = [
        "..", // Path traversal
        "$(", // Command substitution
        "${", // Variable expansion
        "`",  // Command substitution
        "&&", // Command chaining
        "||", // Command chaining
        ";",  // Command separator
        "|",  // Pipe
        ">",  // Redirect
        "<",  // Redirect
    ];

    dangerous_patterns.iter().any(|pattern| s.contains(pattern))
}

fn is_valid_package_name(name: &str) -> bool {
    // Package names should be alphanumeric with hyphens, dots, underscores
    name.chars().all(|c| {
        c.is_alphanumeric() || c == '-' || c == '.' || c == '_'
    })
}