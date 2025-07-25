use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::process::Command;
use tracing::{info, debug, warn};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Service {
    pub name: String,
    pub status: ServiceStatus,
    pub enabled: bool,
    pub description: Option<String>,
    pub active_state: String,
    pub sub_state: String,
    pub memory_usage: Option<u64>,
    pub cpu_usage: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ServiceStatus {
    Active,
    Inactive,
    Failed,
    Activating,
    Deactivating,
    Reloading,
    Unknown,
}

impl From<&str> for ServiceStatus {
    fn from(s: &str) -> Self {
        match s {
            "active" => ServiceStatus::Active,
            "inactive" => ServiceStatus::Inactive,
            "failed" => ServiceStatus::Failed,
            "activating" => ServiceStatus::Activating,
            "deactivating" => ServiceStatus::Deactivating,
            "reloading" => ServiceStatus::Reloading,
            _ => ServiceStatus::Unknown,
        }
    }
}

pub struct ServiceManager;

impl ServiceManager {
    /// List all systemd services with sacred awareness
    pub async fn list_all() -> Result<Vec<Service>> {
        info!("📋 Listing system services with reverence...");
        
        // Get list of all units
        let output = Command::new("systemctl")
            .arg("list-units")
            .arg("--type=service")
            .arg("--all")
            .arg("--no-pager")
            .arg("--no-legend")
            .arg("--output=json")
            .output()
            .await
            .context("Failed to list systemd services")?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("Failed to list services: {}", stderr));
        }
        
        // Parse output
        let stdout = String::from_utf8_lossy(&output.stdout);
        let services = Self::parse_service_list(&stdout)?;
        
        info!("✨ Found {} services", services.len());
        Ok(services)
    }
    
    /// Get detailed status of a specific service
    pub async fn get_status(service_name: &str) -> Result<Service> {
        info!("🔍 Checking status of service: {}", service_name);
        
        // Validate service name
        if !Self::is_valid_service_name(service_name) {
            return Err(anyhow::anyhow!("Invalid service name"));
        }
        
        // Get service status
        let output = Command::new("systemctl")
            .arg("show")
            .arg(service_name)
            .arg("--no-pager")
            .output()
            .await
            .context("Failed to get service status")?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        let properties = Self::parse_service_properties(&stdout);
        
        // Extract key properties
        let active_state = properties.get("ActiveState").unwrap_or(&"unknown".to_string()).clone();
        let sub_state = properties.get("SubState").unwrap_or(&"unknown".to_string()).clone();
        let description = properties.get("Description").cloned();
        let load_state = properties.get("LoadState").unwrap_or(&"not-found".to_string()).clone();
        
        if load_state == "not-found" {
            return Err(anyhow::anyhow!("Service '{}' not found", service_name));
        }
        
        let status = ServiceStatus::from(active_state.as_str());
        let enabled = Self::is_service_enabled(service_name).await?;
        
        // Try to get resource usage
        let memory_usage = properties.get("MemoryCurrent")
            .and_then(|s| s.parse::<u64>().ok());
        
        Ok(Service {
            name: service_name.to_string(),
            status,
            enabled,
            description,
            active_state,
            sub_state,
            memory_usage,
            cpu_usage: None, // Would need cgroup data
        })
    }
    
    /// Start a service with sacred intention
    pub async fn start(service_name: &str) -> Result<String> {
        info!("▶️ Starting service '{}' with sacred intention...", service_name);
        
        if !Self::is_valid_service_name(service_name) {
            return Err(anyhow::anyhow!("Invalid service name"));
        }
        
        // Check current status first
        let status = Self::get_status(service_name).await?;
        if status.status == ServiceStatus::Active {
            return Ok(format!("Service '{}' is already active", service_name));
        }
        
        info!("🧘 Taking sacred pause before service activation...");
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        
        let output = Command::new("sudo")
            .arg("systemctl")
            .arg("start")
            .arg(service_name)
            .output()
            .await
            .context("Failed to start service")?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("Failed to start service: {}", stderr));
        }
        
        // Wait a moment for service to start
        tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
        
        // Verify it started
        let new_status = Self::get_status(service_name).await?;
        if new_status.status == ServiceStatus::Active {
            info!("✨ Service '{}' started successfully", service_name);
            Ok(format!("Service '{}' is now active and running", service_name))
        } else {
            warn!("⚠️ Service '{}' may not have started properly", service_name);
            Ok(format!("Service '{}' start command issued, current state: {}", 
                service_name, new_status.active_state))
        }
    }
    
    /// Stop a service with mindful consideration
    pub async fn stop(service_name: &str) -> Result<String> {
        info!("⏹️ Stopping service '{}' with mindful consideration...", service_name);
        
        if !Self::is_valid_service_name(service_name) {
            return Err(anyhow::anyhow!("Invalid service name"));
        }
        
        // Check if it's safe to stop
        if Self::is_critical_service(service_name) {
            return Err(anyhow::anyhow!(
                "Service '{}' is critical to system operation. Stopping it may cause system instability.", 
                service_name
            ));
        }
        
        info!("🧘 Taking sacred pause before service deactivation...");
        tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        
        let output = Command::new("sudo")
            .arg("systemctl")
            .arg("stop")
            .arg(service_name)
            .output()
            .await
            .context("Failed to stop service")?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("Failed to stop service: {}", stderr));
        }
        
        info!("✨ Service '{}' stopped peacefully", service_name);
        Ok(format!("Service '{}' has been stopped", service_name))
    }
    
    /// Enable a service with future awareness
    pub async fn enable(service_name: &str) -> Result<String> {
        info!("🔓 Enabling service '{}' for future boots...", service_name);
        
        if !Self::is_valid_service_name(service_name) {
            return Err(anyhow::anyhow!("Invalid service name"));
        }
        
        let output = Command::new("sudo")
            .arg("systemctl")
            .arg("enable")
            .arg(service_name)
            .output()
            .await
            .context("Failed to enable service")?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("Failed to enable service: {}", stderr));
        }
        
        info!("✨ Service '{}' enabled for automatic start", service_name);
        Ok(format!("Service '{}' will start automatically on boot", service_name))
    }
    
    /// Disable a service with conscious choice
    pub async fn disable(service_name: &str) -> Result<String> {
        info!("🔒 Disabling service '{}' from automatic start...", service_name);
        
        if !Self::is_valid_service_name(service_name) {
            return Err(anyhow::anyhow!("Invalid service name"));
        }
        
        if Self::is_critical_service(service_name) {
            return Err(anyhow::anyhow!(
                "Service '{}' is critical and should not be disabled", 
                service_name
            ));
        }
        
        let output = Command::new("sudo")
            .arg("systemctl")
            .arg("disable")
            .arg(service_name)
            .output()
            .await
            .context("Failed to disable service")?;
        
        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("Failed to disable service: {}", stderr));
        }
        
        info!("✨ Service '{}' disabled from automatic start", service_name);
        Ok(format!("Service '{}' will not start automatically on boot", service_name))
    }
    
    // Helper functions
    
    fn is_valid_service_name(name: &str) -> bool {
        !name.is_empty() && 
        !name.contains("..") && 
        !name.contains("/") &&
        !name.contains(";") &&
        !name.contains("&") &&
        !name.contains("|") &&
        !name.contains("$")
    }
    
    fn is_critical_service(name: &str) -> bool {
        const CRITICAL_SERVICES: &[&str] = &[
            "systemd-journald",
            "systemd-logind", 
            "dbus",
            "systemd-networkd",
            "NetworkManager",
            "sshd",
            "systemd-resolved",
        ];
        
        CRITICAL_SERVICES.contains(&name) || 
        name.starts_with("systemd-") ||
        name == "init.scope"
    }
    
    async fn is_service_enabled(service_name: &str) -> Result<bool> {
        let output = Command::new("systemctl")
            .arg("is-enabled")
            .arg(service_name)
            .output()
            .await?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.trim() == "enabled" || stdout.trim() == "static")
    }
    
    fn parse_service_list(output: &str) -> Result<Vec<Service>> {
        let mut services = Vec::new();
        
        for line in output.lines() {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 4 {
                let name = parts[0].trim_end_matches(".service");
                let load_state = parts[1];
                let active_state = parts[2];
                let sub_state = parts[3];
                let description = parts[4..].join(" ");
                
                if load_state == "loaded" {
                    services.push(Service {
                        name: name.to_string(),
                        status: ServiceStatus::from(active_state),
                        enabled: false, // Will be filled later if needed
                        description: Some(description),
                        active_state: active_state.to_string(),
                        sub_state: sub_state.to_string(),
                        memory_usage: None,
                        cpu_usage: None,
                    });
                }
            }
        }
        
        Ok(services)
    }
    
    fn parse_service_properties(output: &str) -> HashMap<String, String> {
        let mut properties = HashMap::new();
        
        for line in output.lines() {
            if let Some((key, value)) = line.split_once('=') {
                properties.insert(key.to_string(), value.to_string());
            }
        }
        
        properties
    }
}