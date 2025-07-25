use crate::state::AppState;
use chrono::{DateTime, Utc, Duration};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tauri::State;
use tokio::sync::Mutex;
use tracing::info;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Intention {
    pub text: String,
    pub set_at: DateTime<Utc>,
    pub duration_minutes: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SacredPause {
    pub duration_seconds: i64,
    pub message: Option<String>,
    pub breathing_rhythm: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoherenceLevel {
    pub current: f64,  // 0.0 to 1.0
    pub target: f64,
    pub trend: String, // "rising", "stable", "falling"
    pub factors: Vec<CoherenceFactor>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoherenceFactor {
    pub name: String,
    pub impact: f64,
    pub suggestion: Option<String>,
}

/// Set an intention for the current session
#[tauri::command]
pub async fn set_intention(
    text: String,
    duration_minutes: Option<i64>,
    state: State<'_, AppState>,
) -> Result<Intention, String> {
    info!("🎯 Setting sacred intention: {}", text);
    
    let intention = Intention {
        text: text.clone(),
        set_at: Utc::now(),
        duration_minutes: duration_minutes.unwrap_or(60),
    };
    
    // Store intention in app state
    state.set_current_intention(intention.clone()).await;
    
    // Emit event for UI
    state.emit_event("intention-set", &intention)?;
    
    info!("✨ Intention crystallized in the digital field");
    Ok(intention)
}

/// Initiate a sacred pause
#[tauri::command]
pub async fn take_sacred_pause(
    duration_seconds: Option<i64>,
    state: State<'_, AppState>,
) -> Result<SacredPause, String> {
    let duration = duration_seconds.unwrap_or(30);
    info!("⏸️ Initiating {}-second sacred pause...", duration);
    
    let pause = SacredPause {
        duration_seconds: duration,
        message: Some(match duration {
            0..=30 => "Take a breath. You are here now.".to_string(),
            31..=60 => "Rest in this moment. Let clarity emerge.".to_string(),
            61..=180 => "Deep pause. Integration in progress.".to_string(),
            _ => "Extended sacred pause. Honor this time.".to_string(),
        }),
        breathing_rhythm: Some("4-7-8".to_string()), // Inhale-Hold-Exhale
    };
    
    // Emit pause event
    state.emit_event("sacred-pause-started", &pause)?;
    
    // Set a timer to emit completion
    let state_clone = state.inner().clone();
    let pause_clone = pause.clone();
    tokio::spawn(async move {
        tokio::time::sleep(tokio::time::Duration::from_secs(duration as u64)).await;
        let _ = state_clone.emit_event("sacred-pause-complete", &pause_clone);
        info!("🌟 Sacred pause completed");
    });
    
    Ok(pause)
}

/// Get current coherence level
#[tauri::command]
pub async fn get_coherence_level(
    state: State<'_, AppState>,
) -> Result<CoherenceLevel, String> {
    info!("📊 Calculating system coherence...");
    
    // Calculate coherence based on various factors
    let uptime = state.get_uptime_minutes().await;
    let active_tasks = state.get_active_task_count().await;
    let last_pause = state.get_minutes_since_last_pause().await;
    let has_intention = state.has_active_intention().await;
    
    let mut factors = vec![];
    let mut total_coherence = 0.5; // Base coherence
    
    // Factor: Intention setting
    if has_intention {
        total_coherence += 0.1;
        factors.push(CoherenceFactor {
            name: "Active Intention".to_string(),
            impact: 0.1,
            suggestion: None,
        });
    } else {
        factors.push(CoherenceFactor {
            name: "No Intention Set".to_string(),
            impact: -0.1,
            suggestion: Some("Set an intention to increase focus".to_string()),
        });
    }
    
    // Factor: Regular pauses
    if last_pause < 30.0 {
        total_coherence += 0.15;
        factors.push(CoherenceFactor {
            name: "Recent Sacred Pause".to_string(),
            impact: 0.15,
            suggestion: None,
        });
    } else if last_pause > 90.0 {
        total_coherence -= 0.1;
        factors.push(CoherenceFactor {
            name: "Extended Focus Period".to_string(),
            impact: -0.1,
            suggestion: Some("Consider taking a sacred pause".to_string()),
        });
    }
    
    // Factor: Task load
    let task_impact = match active_tasks {
        0 => {
            factors.push(CoherenceFactor {
                name: "Clear Task Space".to_string(),
                impact: 0.1,
                suggestion: None,
            });
            0.1
        }
        1..=3 => {
            factors.push(CoherenceFactor {
                name: "Optimal Task Load".to_string(),
                impact: 0.15,
                suggestion: None,
            });
            0.15
        }
        4..=6 => {
            factors.push(CoherenceFactor {
                name: "Moderate Task Load".to_string(),
                impact: 0.0,
                suggestion: Some("Consider prioritizing tasks".to_string()),
            });
            0.0
        }
        _ => {
            factors.push(CoherenceFactor {
                name: "High Task Load".to_string(),
                impact: -0.2,
                suggestion: Some("Too many parallel tasks. Simplify.".to_string()),
            });
            -0.2
        }
    };
    total_coherence += task_impact;
    
    // Factor: Session duration
    let session_impact = match uptime {
        0.0..=30.0 => 0.1,  // Fresh start
        30.0..=120.0 => 0.15, // Optimal flow
        120.0..=240.0 => 0.0, // Extended session
        _ => -0.1, // Too long without break
    };
    
    total_coherence += session_impact;
    
    // Clamp between 0 and 1
    total_coherence = total_coherence.max(0.0).min(1.0);
    
    // Determine trend
    let previous = state.get_previous_coherence().await;
    let trend = if (total_coherence - previous).abs() < 0.05 {
        "stable"
    } else if total_coherence > previous {
        "rising"
    } else {
        "falling"
    }.to_string();
    
    // Store current coherence
    state.set_coherence(total_coherence).await;
    
    Ok(CoherenceLevel {
        current: total_coherence,
        target: 0.88, // Sacred target
        trend,
        factors,
    })
}