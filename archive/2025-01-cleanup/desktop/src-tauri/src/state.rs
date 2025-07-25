use crate::commands::sacred::Intention;
use crate::security::Permission;
use anyhow::Result;
use chrono::{DateTime, Utc};
use serde::Serialize;
use std::sync::Arc;
use tauri::{AppHandle, Manager};
use tokio::sync::RwLock;
use tracing::info;

/// Application state management with consciousness-first design
#[derive(Clone)]
pub struct AppState {
    inner: Arc<InnerState>,
    app_handle: Option<AppHandle>,
}

struct InnerState {
    // Sacred state
    current_intention: RwLock<Option<Intention>>,
    coherence_level: RwLock<f64>,
    previous_coherence: RwLock<f64>,
    last_pause_time: RwLock<DateTime<Utc>>,
    
    // System state
    session_start: DateTime<Utc>,
    active_tasks: RwLock<usize>,
    
    // Security state
    authenticated: RwLock<bool>,
    permissions: RwLock<Vec<Permission>>,
}

impl AppState {
    pub fn new() -> Result<Self> {
        info!("🌟 Initializing sacred application state...");
        
        Ok(Self {
            inner: Arc::new(InnerState {
                current_intention: RwLock::new(None),
                coherence_level: RwLock::new(0.5),
                previous_coherence: RwLock::new(0.5),
                last_pause_time: RwLock::new(Utc::now()),
                session_start: Utc::now(),
                active_tasks: RwLock::new(0),
                authenticated: RwLock::new(false),
                permissions: RwLock::new(vec![]),
            }),
            app_handle: None,
        })
    }
    
    /// Set the Tauri app handle for event emission
    pub fn set_app_handle(&mut self, handle: AppHandle) {
        self.app_handle = Some(handle);
    }
    
    /// Emit an event to the frontend
    pub fn emit_event<S: Serialize>(&self, event: &str, payload: S) -> Result<()> {
        if let Some(handle) = &self.app_handle {
            handle.emit_all(event, payload)?;
        }
        Ok(())
    }
    
    // Sacred state methods
    
    pub async fn set_current_intention(&self, intention: Intention) {
        *self.inner.current_intention.write().await = Some(intention);
    }
    
    pub async fn has_active_intention(&self) -> bool {
        if let Some(intention) = &*self.inner.current_intention.read().await {
            let elapsed = Utc::now().signed_duration_since(intention.set_at);
            elapsed.num_minutes() < intention.duration_minutes
        } else {
            false
        }
    }
    
    pub async fn get_coherence_level(&self) -> f64 {
        *self.inner.coherence_level.read().await
    }
    
    pub async fn set_coherence(&self, level: f64) {
        let current = *self.inner.coherence_level.read().await;
        *self.inner.previous_coherence.write().await = current;
        *self.inner.coherence_level.write().await = level;
    }
    
    pub async fn get_previous_coherence(&self) -> f64 {
        *self.inner.previous_coherence.read().await
    }
    
    pub async fn get_minutes_since_last_pause(&self) -> f64 {
        let last_pause = *self.inner.last_pause_time.read().await;
        let elapsed = Utc::now().signed_duration_since(last_pause);
        elapsed.num_seconds() as f64 / 60.0
    }
    
    pub async fn record_pause(&self) {
        *self.inner.last_pause_time.write().await = Utc::now();
    }
    
    // System state methods
    
    pub async fn get_uptime_minutes(&self) -> f64 {
        let elapsed = Utc::now().signed_duration_since(self.inner.session_start);
        elapsed.num_seconds() as f64 / 60.0
    }
    
    pub async fn get_active_task_count(&self) -> usize {
        *self.inner.active_tasks.read().await
    }
    
    pub async fn increment_tasks(&self) {
        *self.inner.active_tasks.write().await += 1;
    }
    
    pub async fn decrement_tasks(&self) {
        let mut tasks = self.inner.active_tasks.write().await;
        if *tasks > 0 {
            *tasks -= 1;
        }
    }
    
    // Security methods
    
    pub async fn is_authenticated(&self) -> bool {
        *self.inner.authenticated.read().await
    }
    
    pub async fn set_authenticated(&self, auth: bool, permissions: Vec<Permission>) {
        *self.inner.authenticated.write().await = auth;
        *self.inner.permissions.write().await = permissions;
    }
    
    pub fn check_permission(&self, required: Permission) -> Result<()> {
        // For now, simplified permission check
        // In production, this would check against the actual permission list
        Ok(())
    }
    
    pub fn inner(&self) -> Arc<InnerState> {
        self.inner.clone()
    }
}