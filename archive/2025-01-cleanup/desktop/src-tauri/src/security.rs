use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Permission {
    ReadConfig,
    WriteConfig,
    ValidateConfig,
    RebuildSystem,
    ManagePackages,
    ManageServices,
    ViewSystemInfo,
    ModifySystemSettings,
}

impl Permission {
    pub fn description(&self) -> &'static str {
        match self {
            Self::ReadConfig => "Read NixOS configuration files",
            Self::WriteConfig => "Modify NixOS configuration files",
            Self::ValidateConfig => "Validate configuration syntax",
            Self::RebuildSystem => "Rebuild and switch NixOS system",
            Self::ManagePackages => "Install, update, or remove packages",
            Self::ManageServices => "Start, stop, or configure services",
            Self::ViewSystemInfo => "View system information and statistics",
            Self::ModifySystemSettings => "Modify critical system settings",
        }
    }
    
    pub fn requires_sudo(&self) -> bool {
        matches!(self, 
            Self::WriteConfig | 
            Self::RebuildSystem | 
            Self::ManagePackages | 
            Self::ManageServices |
            Self::ModifySystemSettings
        )
    }
}