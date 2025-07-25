use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::process::Command;
use tracing::{info, debug, warn};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Package {
    pub name: String,
    pub version: String,
    pub description: Option<String>,
    pub installed: bool,
    pub channel: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PackageSearchResult {
    pub packages: Vec<Package>,
    pub total_count: usize,
    pub search_time_ms: u64,
}

pub struct PackageManager;

impl PackageManager {
    /// Search for packages with sacred awareness
    pub async fn search(query: &str, limit: Option<usize>) -> Result<PackageSearchResult> {
        info!("🔍 Searching for packages matching: {}", query);
        let start = std::time::Instant::now();
        
        // Use nix search for package discovery
        let mut cmd = Command::new("nix");
        cmd.arg("search")
            .arg("nixpkgs")
            .arg(query)
            .arg("--json");
        
        let output = cmd.output()
            .await
            .context("Failed to run nix search")?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("Package search failed: {}", stderr));
        }
        
        // Parse JSON output
        let stdout = String::from_utf8_lossy(&output.stdout);
        let search_results: HashMap<String, serde_json::Value> = 
            serde_json::from_str(&stdout)
                .context("Failed to parse search results")?;
        
        // Get list of installed packages for comparison
        let installed_packages = Self::get_installed_package_names().await?;
        
        // Convert to our package format
        let mut packages: Vec<Package> = search_results
            .into_iter()
            .map(|(attr_path, details)| {
                let name = attr_path.split('.').last().unwrap_or(&attr_path).to_string();
                let version = details["version"]
                    .as_str()
                    .unwrap_or("unknown")
                    .to_string();
                let description = details["description"]
                    .as_str()
                    .map(|s| s.to_string());
                let installed = installed_packages.contains(&name);
                
                Package {
                    name,
                    version,
                    description,
                    installed,
                    channel: Some("nixpkgs".to_string()),
                }
            })
            .collect();
        
        // Sort by relevance (installed first, then alphabetical)
        packages.sort_by(|a, b| {
            match (a.installed, b.installed) {
                (true, false) => std::cmp::Ordering::Less,
                (false, true) => std::cmp::Ordering::Greater,
                _ => a.name.cmp(&b.name),
            }
        });
        
        // Apply limit if specified
        let total_count = packages.len();
        if let Some(limit) = limit {
            packages.truncate(limit);
        }
        
        let search_time_ms = start.elapsed().as_millis() as u64;
        info!("✨ Found {} packages in {}ms", total_count, search_time_ms);
        
        Ok(PackageSearchResult {
            packages,
            total_count,
            search_time_ms,
        })
    }
    
    /// List installed packages with sacred reverence
    pub async fn list_installed() -> Result<Vec<Package>> {
        info!("📦 Listing installed packages with gratitude...");
        
        // Use nix-env to list user packages
        let output = Command::new("nix-env")
            .arg("-q")
            .arg("--json")
            .output()
            .await
            .context("Failed to list installed packages")?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            warn!("Failed to list user packages: {}", stderr);
            // Continue with system packages
        }
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        let user_packages: Vec<serde_json::Value> = 
            serde_json::from_str(&stdout).unwrap_or_default();
        
        // Also get system packages
        let system_packages = Self::get_system_packages().await?;
        
        // Combine and deduplicate
        let mut all_packages = Vec::new();
        
        // Add user packages
        for pkg in user_packages {
            if let Some(name) = pkg["name"].as_str() {
                all_packages.push(Package {
                    name: name.to_string(),
                    version: pkg["version"].as_str().unwrap_or("unknown").to_string(),
                    description: pkg["meta"]["description"].as_str().map(|s| s.to_string()),
                    installed: true,
                    channel: Some("user".to_string()),
                });
            }
        }
        
        // Add system packages
        all_packages.extend(system_packages);
        
        // Sort alphabetically
        all_packages.sort_by(|a, b| a.name.cmp(&b.name));
        
        info!("✨ Found {} installed packages", all_packages.len());
        Ok(all_packages)
    }
    
    /// Install a package with sacred intention
    pub async fn install(package_name: &str, use_flakes: bool) -> Result<String> {
        info!("📥 Installing package '{}' with sacred intention...", package_name);
        
        // Validate package name
        if package_name.is_empty() || package_name.contains(';') || package_name.contains('&') {
            return Err(anyhow::anyhow!("Invalid package name"));
        }
        
        let mut cmd = Command::new("nix-env");
        cmd.arg("-iA");
        
        if use_flakes {
            cmd.arg(format!("nixpkgs#{}", package_name));
        } else {
            cmd.arg(format!("nixpkgs.{}", package_name));
        }
        
        info!("🧘 Taking sacred pause before installation...");
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        
        let output = cmd.output()
            .await
            .context("Failed to run package installation")?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        
        if !output.status.success() {
            if stderr.contains("permission denied") {
                return Err(anyhow::anyhow!("Permission denied. Try with elevated privileges."));
            }
            return Err(anyhow::anyhow!("Installation failed: {}", stderr));
        }
        
        info!("✨ Package '{}' installed successfully", package_name);
        Ok(format!("Package '{}' installed with grace\n\n{}", package_name, stdout))
    }
    
    /// Remove a package with mindful consideration
    pub async fn remove(package_name: &str) -> Result<String> {
        info!("🗑️ Removing package '{}' with mindful consideration...", package_name);
        
        // Validate package name
        if package_name.is_empty() || package_name.contains(';') || package_name.contains('&') {
            return Err(anyhow::anyhow!("Invalid package name"));
        }
        
        // Check if package is actually installed
        let installed = Self::get_installed_package_names().await?;
        if !installed.contains(&package_name.to_string()) {
            return Err(anyhow::anyhow!("Package '{}' is not installed", package_name));
        }
        
        let mut cmd = Command::new("nix-env");
        cmd.arg("-e").arg(package_name);
        
        info!("🧘 Taking sacred pause before removal...");
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        
        let output = cmd.output()
            .await
            .context("Failed to run package removal")?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        
        if !output.status.success() {
            return Err(anyhow::anyhow!("Removal failed: {}", stderr));
        }
        
        info!("✨ Package '{}' removed with gratitude", package_name);
        Ok(format!("Package '{}' removed peacefully\n\n{}", package_name, stdout))
    }
    
    /// Get list of installed package names
    async fn get_installed_package_names() -> Result<Vec<String>> {
        let output = Command::new("nix-env")
            .arg("-q")
            .arg("--no-name")
            .output()
            .await?;
        
        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            Ok(stdout.lines().map(|s| s.to_string()).collect())
        } else {
            Ok(vec![])
        }
    }
    
    /// Get system packages from configuration
    async fn get_system_packages() -> Result<Vec<Package>> {
        // This would parse /etc/nixos/configuration.nix to find systemPackages
        // For now, return empty vec
        Ok(vec![])
    }
}