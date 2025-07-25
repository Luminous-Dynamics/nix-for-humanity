use anyhow::{Result, Context};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::os::unix::fs::{PermissionsExt, MetadataExt};
use tokio::fs;
use tokio::process::Command;
use tracing::{info, warn, debug};

pub mod packages;
pub mod services;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NixosConfig {
    pub content: String,
    pub path: PathBuf,
    pub last_modified: DateTime<Utc>,
    pub is_flake: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub is_valid: bool,
    pub warnings: Vec<String>,
    pub errors: Vec<String>,
    pub suggestions: Vec<String>,
}

impl NixosConfig {
    /// Read the current NixOS configuration with sacred awareness
    pub async fn read() -> Result<Self> {
        info!("📖 Reading NixOS configuration with reverence...");
        
        // Sacred paths to check
        let sacred_paths = vec![
            "/etc/nixos/flake.nix",
            "/etc/nixos/configuration.nix",
            // Also check user's config directory
            &format!("{}/.config/nixos/configuration.nix", std::env::var("HOME").unwrap_or_default()),
        ];
        
        // Find the first existing configuration
        let mut found_config = None;
        for path_str in sacred_paths {
            let path = Path::new(path_str);
            if path.exists() {
                debug!("Found configuration at: {}", path_str);
                let is_flake = path_str.ends_with("flake.nix");
                found_config = Some((path, is_flake));
                break;
            }
        }
        
        let (path, is_flake) = found_config
            .ok_or_else(|| anyhow::anyhow!("No NixOS configuration found in sacred paths"))?;
        
        // Check if we have permission to read
        let metadata = fs::metadata(path)
            .await
            .context("Failed to read file metadata")?;
        
        let permissions = metadata.permissions();
        let mode = permissions.mode();
        
        // Check if file is readable (by owner, group, or others)
        if mode & 0o444 == 0 {
            warn!("Configuration file has restrictive permissions: {:o}", mode);
        }
        
        // Read with sacred pause awareness
        info!("🧘 Taking a breath before reading sacred configuration...");
        let content = fs::read_to_string(path)
            .await
            .with_context(|| format!("Failed to read configuration from {:?}", path))?;
        
        let last_modified = metadata.modified()
            .context("Failed to get modification time")?
            .into();
        
        // Calculate file size for awareness
        let size_kb = metadata.len() as f64 / 1024.0;
        info!("✨ Configuration read successfully ({:.2} KB)", size_kb);
        
        Ok(Self {
            content,
            path: path.to_path_buf(),
            last_modified,
            is_flake,
        })
    }
    
    /// Validate a NixOS configuration with deep awareness
    pub async fn validate(content: &str) -> Result<ValidationResult> {
        info!("🔍 Validating configuration with sacred attention...");
        
        let mut result = ValidationResult {
            is_valid: true,
            warnings: vec![],
            errors: vec![],
            suggestions: vec![],
        };
        
        // Step 1: Basic syntax validation
        let temp_path = format!("/tmp/nixos-gui-validate-{}.nix", 
            chrono::Utc::now().timestamp_nanos());
        
        fs::write(&temp_path, content)
            .await
            .context("Failed to write temporary file")?;
        
        // Parse check
        let parse_output = Command::new("nix-instantiate")
            .arg("--parse")
            .arg(&temp_path)
            .output()
            .await
            .context("Failed to run nix-instantiate")?;
        
        if !parse_output.status.success() {
            result.is_valid = false;
            let error = String::from_utf8_lossy(&parse_output.stderr);
            result.errors.push(format!("Syntax error: {}", error.trim()));
        }
        
        // Step 2: Evaluation check (if syntax is valid)
        if result.is_valid {
            let eval_output = Command::new("nix-instantiate")
                .arg("--eval")
                .arg("--strict")
                .arg("--json")
                .arg(&temp_path)
                .arg("-A")
                .arg("system")
                .output()
                .await;
            
            if let Ok(output) = eval_output {
                if !output.status.success() {
                    let error = String::from_utf8_lossy(&output.stderr);
                    if error.contains("error:") {
                        result.warnings.push(format!("Evaluation warning: {}", error.trim()));
                    }
                }
            }
        }
        
        // Step 3: Sacred configuration checks
        self.check_sacred_patterns(content, &mut result);
        
        // Step 4: Security checks
        self.check_security_patterns(content, &mut result);
        
        // Step 5: Best practices
        self.check_best_practices(content, &mut result);
        
        // Clean up with awareness
        let _ = fs::remove_file(&temp_path).await;
        
        if result.is_valid {
            info!("✅ Configuration passes validation with {} warnings", result.warnings.len());
        } else {
            warn!("❌ Configuration has {} errors", result.errors.len());
        }
        
        Ok(result)
    }
    
    /// Check for sacred patterns and consciousness-first practices
    fn check_sacred_patterns(&self, content: &str, result: &mut ValidationResult) {
        // Check for system.stateVersion
        if !content.contains("system.stateVersion") {
            result.errors.push(
                "Missing system.stateVersion - this is essential for system stability".to_string()
            );
            result.is_valid = false;
        }
        
        // Check for basic imports
        if !content.contains("imports") && !content.contains("flake") {
            result.warnings.push(
                "No imports detected - consider modularizing your configuration".to_string()
            );
        }
        
        // Suggest sacred pauses in boot
        if content.contains("boot.") && !content.contains("boot.initrd.preDeviceCommands") {
            result.suggestions.push(
                "Consider adding a sacred boot message with boot.initrd.preDeviceCommands".to_string()
            );
        }
    }
    
    /// Check for security issues
    fn check_security_patterns(&self, content: &str, result: &mut ValidationResult) {
        // Check for hardcoded passwords
        if content.contains("password = \"") || content.contains("hashedPassword = \"\"") {
            result.errors.push(
                "Detected hardcoded password - use hashedPassword or passwordFile instead".to_string()
            );
            result.is_valid = false;
        }
        
        // Check for insecure services
        if content.contains("services.telnet.enable = true") {
            result.warnings.push(
                "Telnet is insecure - consider using SSH instead".to_string()
            );
        }
        
        // Check firewall
        if !content.contains("networking.firewall") {
            result.suggestions.push(
                "No firewall configuration detected - consider enabling with networking.firewall.enable".to_string()
            );
        }
    }
    
    /// Check for best practices
    fn check_best_practices(&self, content: &str, result: &mut ValidationResult) {
        // X11 vs Wayland
        if content.contains("services.xserver.enable = true") && 
           !content.contains("wayland") {
            result.suggestions.push(
                "Consider Wayland for better security and performance: services.xserver.displayManager.gdm.wayland = true".to_string()
            );
        }
        
        // Auto-upgrade
        if !content.contains("system.autoUpgrade") {
            result.suggestions.push(
                "Consider enabling automatic security updates with system.autoUpgrade".to_string()
            );
        }
        
        // Documentation
        if !content.contains("documentation.") {
            result.suggestions.push(
                "Enable documentation with documentation.enable = true for better system understanding".to_string()
            );
        }
        
        // Nix experimental features
        if content.contains("nix.settings.experimental-features") {
            result.warnings.push(
                "Using experimental Nix features - these may change in future releases".to_string()
            );
        }
    }
    
    /// Save configuration with sacred backup and verification
    pub async fn save(content: &str, path: Option<&str>) -> Result<()> {
        info!("💾 Saving NixOS configuration with sacred care...");
        
        let target_path = path.unwrap_or("/etc/nixos/configuration.nix");
        
        // First validate the content
        let validation = Self::validate(content).await?;
        if !validation.is_valid {
            return Err(anyhow::anyhow!(
                "Cannot save invalid configuration: {:?}", 
                validation.errors
            ));
        }
        
        // Check if we need sudo
        let needs_sudo = !Self::can_write_path(target_path).await;
        if needs_sudo {
            info!("🔐 Elevated privileges required for {}", target_path);
        }
        
        // Create atomic write operation
        let temp_path = format!("{}.tmp.{}", target_path, chrono::Utc::now().timestamp_nanos());
        
        // Write to temporary file first
        fs::write(&temp_path, content)
            .await
            .with_context(|| format!("Failed to write temporary file: {}", temp_path))?;
        
        // Set proper permissions (readable by all, writable by owner)
        let chmod_cmd = if needs_sudo {
            Command::new("sudo")
                .arg("chmod")
                .arg("644")
                .arg(&temp_path)
                .status()
                .await
        } else {
            Command::new("chmod")
                .arg("644")
                .arg(&temp_path)
                .status()
                .await
        };
        
        chmod_cmd.context("Failed to set file permissions")?;
        
        // Perform atomic rename with sacred pause
        info!("🧘 Taking a sacred pause before committing changes...");
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        
        let rename_result = if needs_sudo {
            Command::new("sudo")
                .arg("mv")
                .arg(&temp_path)
                .arg(target_path)
                .status()
                .await
        } else {
            // Try direct rename first
            match fs::rename(&temp_path, target_path).await {
                Ok(_) => Ok(std::process::ExitStatus::from_raw(0)),
                Err(_) => {
                    // Fallback to mv command
                    Command::new("mv")
                        .arg(&temp_path)
                        .arg(target_path)
                        .status()
                        .await
                }
            }
        };
        
        match rename_result {
            Ok(status) if status.success() => {
                info!("✨ Configuration saved successfully to {}", target_path);
                Ok(())
            }
            Ok(status) => {
                // Clean up temp file
                let _ = fs::remove_file(&temp_path).await;
                Err(anyhow::anyhow!("Failed to save configuration: mv exited with {}", status))
            }
            Err(e) => {
                // Clean up temp file
                let _ = fs::remove_file(&temp_path).await;
                Err(anyhow::anyhow!("Failed to save configuration: {}", e))
            }
        }
    }
    
    /// Check if we can write to a path
    async fn can_write_path(path: &str) -> bool {
        match fs::metadata(path).await {
            Ok(metadata) => {
                let uid = unsafe { libc::getuid() };
                let gid = unsafe { libc::getgid() };
                let mode = metadata.permissions().mode();
                
                // Check owner write
                if metadata.uid() == uid && (mode & 0o200) != 0 {
                    return true;
                }
                
                // Check group write
                if metadata.gid() == gid && (mode & 0o020) != 0 {
                    return true;
                }
                
                // Check other write (not recommended but check anyway)
                if (mode & 0o002) != 0 {
                    return true;
                }
                
                false
            }
            Err(_) => {
                // If file doesn't exist, check parent directory
                if let Some(parent) = Path::new(path).parent() {
                    if let Ok(parent_metadata) = fs::metadata(parent).await {
                        let uid = unsafe { libc::getuid() };
                        let mode = parent_metadata.permissions().mode();
                        return parent_metadata.uid() == uid && (mode & 0o200) != 0;
                    }
                }
                false
            }
        }
    }
    
    /// Create a backup of current configuration
    pub async fn create_backup() -> Result<String> {
        info!("Creating configuration backup...");
        
        let timestamp = Utc::now().format("%Y%m%d_%H%M%S");
        let backup_dir = "/etc/nixos/backups";
        
        // Create backup directory if it doesn't exist
        fs::create_dir_all(backup_dir)
            .await
            .context("Failed to create backup directory")?;
        
        let config = Self::read().await?;
        let backup_path = format!("{}/configuration_{}.nix", backup_dir, timestamp);
        
        fs::write(&backup_path, &config.content)
            .await
            .context("Failed to write backup")?;
        
        info!("Backup created: {}", backup_path);
        Ok(backup_path)
    }
    
    /// Rebuild NixOS system with sacred awareness and progress tracking
    pub async fn rebuild(
        operation: &str,
        flake: Option<&str>,
        show_trace: bool,
    ) -> Result<String> {
        info!("🔨 Beginning sacred system rebuild: {}", operation);
        
        // Validate operation
        let valid_operations = ["switch", "boot", "test", "dry-build", "dry-run", "build"];
        if !valid_operations.contains(&operation) {
            return Err(anyhow::anyhow!("Invalid rebuild operation: {}", operation));
        }
        
        // Check if we need sudo (switch and boot require root)
        let needs_sudo = matches!(operation, "switch" | "boot");
        
        let mut cmd = if needs_sudo {
            let mut c = Command::new("sudo");
            c.arg("nixos-rebuild");
            c
        } else {
            Command::new("nixos-rebuild")
        };
        
        cmd.arg(operation);
        
        // Add flake support
        if let Some(flake_ref) = flake {
            cmd.arg("--flake").arg(flake_ref);
        }
        
        // Add verbosity for progress tracking
        cmd.arg("-v");
        
        if show_trace {
            cmd.arg("--show-trace");
        }
        
        // Add build options for better output
        cmd.arg("--option").arg("build-cores").arg("0");  // Use all cores
        cmd.arg("--option").arg("max-jobs").arg("auto");  // Automatic job control
        
        // Set environment for better output
        cmd.env("NIX_PAGER", "");  // Disable pager
        cmd.env("NO_COLOR", "0");   // Keep colors
        
        info!("🧘 Entering sacred build space...");
        info!("This may take time. Practice patience and presence.");
        
        // For dry-run operations, just execute and return
        if operation.contains("dry") {
            let output = cmd.output()
                .await
                .context("Failed to run nixos-rebuild")?;
            
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            
            if !output.status.success() {
                return Err(anyhow::anyhow!("Dry run failed:\n{}", stderr));
            }
            
            return Ok(format!("=== Dry Run Results ===\n{}\n{}", stdout, stderr));
        }
        
        // For real operations, use spawn for real-time output
        let mut child = cmd
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn()
            .context("Failed to spawn nixos-rebuild")?;
        
        // Collect output
        let output = child.wait_with_output()
            .await
            .context("Failed to wait for nixos-rebuild")?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        
        if !output.status.success() {
            warn!("❌ Rebuild failed with status: {:?}", output.status);
            
            // Parse common errors for better messages
            let error_msg = if stderr.contains("permission denied") {
                "Permission denied. This operation requires root privileges."
            } else if stderr.contains("build of") && stderr.contains("failed") {
                "Build failed. Check the error output for details."
            } else if stderr.contains("out of memory") {
                "Build ran out of memory. Try closing other applications."
            } else {
                "Build failed. See error output below."
            };
            
            return Err(anyhow::anyhow!("{}\n\n{}", error_msg, stderr));
        }
        
        // Success!
        info!("✨ Rebuild completed successfully!");
        
        let success_msg = match operation {
            "switch" => "🌟 System configuration switched! Changes are now active.",
            "boot" => "🌙 Boot configuration updated. Changes will apply on next reboot.",
            "test" => "🧪 Test configuration activated. This is temporary.",
            "build" => "🏗️ Configuration built successfully. No activation performed.",
            _ => "✅ Operation completed successfully.",
        };
        
        Ok(format!("{}\n\n=== Build Output ===\n{}\n{}", success_msg, stdout, stderr))
    }
}