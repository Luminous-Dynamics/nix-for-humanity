use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub sacred_mode: bool,
    pub coherence_target: f64,
    pub pause_reminder_minutes: i64,
    pub theme: Theme,
    pub notifications: NotificationSettings,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Theme {
    pub mode: ThemeMode,
    pub sacred_colors: bool,
    pub animations: bool,
    pub transparency: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ThemeMode {
    Light,
    Dark,
    Auto,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NotificationSettings {
    pub enabled: bool,
    pub sacred_pauses: bool,
    pub rebuild_status: bool,
    pub coherence_updates: bool,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            sacred_mode: true,
            coherence_target: 0.88,
            pause_reminder_minutes: 45,
            theme: Theme {
                mode: ThemeMode::Dark,
                sacred_colors: true,
                animations: true,
                transparency: 0.95,
            },
            notifications: NotificationSettings {
                enabled: true,
                sacred_pauses: true,
                rebuild_status: true,
                coherence_updates: false,
            },
        }
    }
}