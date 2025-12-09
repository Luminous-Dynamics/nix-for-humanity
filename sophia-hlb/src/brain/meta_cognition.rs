//! Meta-Cognition Module - The Monitor
//!
//! Week 3 Days 6-7: The Loop That Watches The Loop
//!
//! Meta-Cognition is second-order awareness: Sophia observing her own thinking.
//!
//! Key Capabilities:
//! - Measure cognitive state (decay velocity, conflict, insight rate, goal velocity)
//! - Detect pathological patterns (thrashing, fixation, confusion)
//! - Generate regulatory bids to adjust system parameters
//! - Self-tune hyperparameters based on mental state
//!
//! This gives Sophia the ability to realize she is confused, stuck, or distracted,
//! and to correct her own cognitive trajectory.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

/// Cognitive metrics derived from workspace history
///
/// These are second-order measurements: not what Sophia is thinking about,
/// but HOW she is thinking.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CognitiveMetrics {
    /// Decay velocity: How fast are thoughts dying?
    /// - High (>0.7): Distracted, thoughts fleeting, can't maintain focus
    /// - Medium (0.3-0.7): Normal churn, healthy turnover
    /// - Low (<0.3): Fixated, stuck on one thought, obsessive
    pub decay_velocity: f32,

    /// Conflict ratio: How many bids are fighting for top spot?
    /// - High (>0.7): High competition, many thoughts competing
    /// - Medium (0.3-0.7): Moderate competition, normal attention
    /// - Low (<0.3): Low competition, clear winner or empty mind
    pub conflict_ratio: f32,

    /// Insight rate: Are we generating new consolidated ideas?
    /// - High (>0.5): Creative, generating insights from conflicts
    /// - Medium (0.2-0.5): Normal insight generation
    /// - Low (<0.2): Stagnant, not consolidating, not learning
    pub insight_rate: f32,

    /// Goal velocity: Are goals completing or stalling?
    /// - High (>0.5): Goals completing rapidly
    /// - Medium (0.2-0.5): Normal goal progress
    /// - Low (<0.2): Goals stalling, not making progress
    pub goal_velocity: f32,

    /// Overall cognitive health score (0.0-1.0)
    /// Derived from weighted combination of metrics
    pub health_score: f32,
}

impl CognitiveMetrics {
    /// Create metrics with all values at 0.5 (neutral)
    pub fn neutral() -> Self {
        Self {
            decay_velocity: 0.5,
            conflict_ratio: 0.5,
            insight_rate: 0.5,
            goal_velocity: 0.5,
            health_score: 0.5,
        }
    }

    /// Calculate overall cognitive health score
    ///
    /// Ideal state:
    /// - Moderate decay velocity (0.4-0.6)
    /// - Moderate conflict (0.3-0.6)
    /// - High insight rate (>0.4)
    /// - Moderate to high goal velocity (>0.3)
    pub fn calculate_health(&mut self) {
        let mut health = 0.0;
        let mut weight_sum = 0.0;

        // Decay velocity: Ideal range 0.4-0.6 (not too fast, not too slow)
        let decay_health = if self.decay_velocity < 0.4 {
            self.decay_velocity / 0.4 // 0.0-1.0 as we approach 0.4
        } else if self.decay_velocity > 0.6 {
            1.0 - ((self.decay_velocity - 0.6) / 0.4).min(1.0)
        } else {
            1.0 // Perfect range
        };
        health += decay_health * 2.0;
        weight_sum += 2.0;

        // Conflict ratio: Ideal range 0.3-0.6 (healthy competition)
        let conflict_health = if self.conflict_ratio < 0.3 {
            self.conflict_ratio / 0.3
        } else if self.conflict_ratio > 0.6 {
            1.0 - ((self.conflict_ratio - 0.6) / 0.4).min(1.0)
        } else {
            1.0
        };
        health += conflict_health * 1.5;
        weight_sum += 1.5;

        // Insight rate: Higher is better (up to 0.8)
        let insight_health = (self.insight_rate / 0.8).min(1.0);
        health += insight_health * 2.5;
        weight_sum += 2.5;

        // Goal velocity: Higher is better (up to 0.7)
        let goal_health = (self.goal_velocity / 0.7).min(1.0);
        health += goal_health * 2.0;
        weight_sum += 2.0;

        self.health_score = health / weight_sum;
    }

    /// Detect if in thrashing state (high decay + low goal velocity)
    pub fn is_thrashing(&self) -> bool {
        self.decay_velocity > 0.75 && self.goal_velocity < 0.2
    }

    /// Detect if in fixation state (near-zero decay)
    pub fn is_fixated(&self) -> bool {
        self.decay_velocity < 0.1
    }

    /// Detect if in confusion state (high conflict + low insight)
    pub fn is_confused(&self) -> bool {
        self.conflict_ratio > 0.7 && self.insight_rate < 0.2
    }

    /// Detect if in stagnation state (low insight + low goal velocity)
    pub fn is_stagnant(&self) -> bool {
        self.insight_rate < 0.15 && self.goal_velocity < 0.15
    }

    /// Get human-readable state description
    pub fn state_description(&self) -> String {
        if self.is_thrashing() {
            "Thrashing: Jumping between thoughts without completing goals".to_string()
        } else if self.is_fixated() {
            "Fixated: Stuck on one thought, unable to shift attention".to_string()
        } else if self.is_confused() {
            "Confused: High mental noise, not generating insights".to_string()
        } else if self.is_stagnant() {
            "Stagnant: Not learning or making progress".to_string()
        } else if self.health_score > 0.7 {
            "Optimal: Healthy cognitive function".to_string()
        } else if self.health_score > 0.5 {
            "Good: Normal cognitive function".to_string()
        } else if self.health_score > 0.3 {
            "Suboptimal: Some cognitive issues".to_string()
        } else {
            "Poor: Significant cognitive dysfunction".to_string()
        }
    }
}

/// Regulatory action to adjust system parameters
///
/// Unlike regular AttentionBids that are about the world,
/// Regulatory Bids are about the Mind itself.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RegulatoryAction {
    /// Increase consolidation threshold (reduce insight generation)
    ReduceInsightSensitivity,

    /// Decrease consolidation threshold (increase insight generation)
    IncreaseInsightSensitivity,

    /// Increase decay rate (thoughts fade faster)
    IncreaseDecayRate,

    /// Decrease decay rate (thoughts persist longer)
    DecreaseDecayRate,

    /// Increase conflict threshold (reduce attention switching)
    IncreaseFocusPersistence,

    /// Decrease conflict threshold (allow easier switching)
    DecreaseFocusPersistence,

    /// Force context switch (break fixation)
    ForceContextSwitch,

    /// Reduce input sensitivity (filter noise)
    ReduceNoiseSensitivity,

    /// Increase input sensitivity (capture more detail)
    IncreaseInputSensitivity,
}

impl RegulatoryAction {
    /// Get human-readable description of action
    pub fn description(&self) -> &str {
        match self {
            Self::ReduceInsightSensitivity => "Reduce insight sensitivity (higher threshold)",
            Self::IncreaseInsightSensitivity => "Increase insight sensitivity (lower threshold)",
            Self::IncreaseDecayRate => "Speed up thought decay (reduce persistence)",
            Self::DecreaseDecayRate => "Slow down thought decay (increase persistence)",
            Self::IncreaseFocusPersistence => "Increase focus persistence (resist switching)",
            Self::DecreaseFocusPersistence => "Decrease focus persistence (allow switching)",
            Self::ForceContextSwitch => "Force context switch (break fixation)",
            Self::ReduceNoiseSensitivity => "Reduce noise sensitivity (filter input)",
            Self::IncreaseInputSensitivity => "Increase input sensitivity (capture detail)",
        }
    }

    /// Get the intent for this action as a string
    pub fn intent(&self) -> String {
        format!("🧠 Meta: {}", self.description())
    }
}

/// Regulatory bid: A bid to change how the mind works
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegulatoryBid {
    /// The regulatory action to take
    pub action: RegulatoryAction,

    /// Priority for this regulatory action (0.0-1.0)
    pub priority: f32,

    /// Reason for this regulatory action
    pub reason: String,
}

impl RegulatoryBid {
    /// Create a new regulatory bid
    pub fn new(action: RegulatoryAction, priority: f32, reason: impl Into<String>) -> Self {
        Self {
            action,
            priority: priority.clamp(0.0, 1.0),
            reason: reason.into(),
        }
    }
}

/// Configuration for meta-cognition monitoring
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaCognitionConfig {
    /// Minimum number of cognitive cycles before metrics are valid
    pub warmup_cycles: usize,

    /// How many cycles to include in decay velocity calculation
    pub decay_window_size: usize,

    /// How many cycles to include in conflict ratio calculation
    pub conflict_window_size: usize,

    /// How many cycles to include in insight rate calculation
    pub insight_window_size: usize,

    /// How many cycles to include in goal velocity calculation
    pub goal_window_size: usize,

    /// Threshold for triggering regulatory actions
    pub intervention_threshold: f32,
}

impl Default for MetaCognitionConfig {
    fn default() -> Self {
        Self {
            warmup_cycles: 10,
            decay_window_size: 20,
            conflict_window_size: 15,
            insight_window_size: 30,
            goal_window_size: 25,
            intervention_threshold: 0.7, // Intervene when pathology confidence > 0.7
        }
    }
}

/// Meta-Cognition Monitor: The loop that watches the loop
///
/// This tracks cognitive metrics over time and generates regulatory bids
/// when pathological patterns are detected.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaCognitionMonitor {
    /// Configuration
    config: MetaCognitionConfig,

    /// Current cognitive metrics
    metrics: CognitiveMetrics,

    /// History of decay velocities (for trend detection)
    decay_history: VecDeque<f32>,

    /// History of conflict ratios
    conflict_history: VecDeque<f32>,

    /// History of insight rates
    insight_history: VecDeque<f32>,

    /// History of goal velocities
    goal_history: VecDeque<f32>,

    /// Number of cognitive cycles observed
    cycle_count: u64,

    /// Number of regulatory interventions made
    intervention_count: u64,
}

impl MetaCognitionMonitor {
    /// Create a new meta-cognition monitor
    pub fn new(config: MetaCognitionConfig) -> Self {
        Self {
            config,
            metrics: CognitiveMetrics::neutral(),
            decay_history: VecDeque::new(),
            conflict_history: VecDeque::new(),
            insight_history: VecDeque::new(),
            goal_history: VecDeque::new(),
            cycle_count: 0,
            intervention_count: 0,
        }
    }

    /// Create with default configuration
    pub fn default() -> Self {
        Self::new(MetaCognitionConfig::default())
    }

    /// Update metrics with new observations
    ///
    /// Call this after each cognitive cycle to update the Monitor's
    /// understanding of Sophia's mental state.
    pub fn update_metrics(
        &mut self,
        decay_velocity: f32,
        conflict_ratio: f32,
        insight_rate: f32,
        goal_velocity: f32,
    ) {
        self.cycle_count += 1;

        // Add to history
        self.decay_history.push_back(decay_velocity);
        self.conflict_history.push_back(conflict_ratio);
        self.insight_history.push_back(insight_rate);
        self.goal_history.push_back(goal_velocity);

        // Trim history to window size
        while self.decay_history.len() > self.config.decay_window_size {
            self.decay_history.pop_front();
        }
        while self.conflict_history.len() > self.config.conflict_window_size {
            self.conflict_history.pop_front();
        }
        while self.insight_history.len() > self.config.insight_window_size {
            self.insight_history.pop_front();
        }
        while self.goal_history.len() > self.config.goal_window_size {
            self.goal_history.pop_front();
        }

        // Calculate average metrics from history
        self.metrics.decay_velocity = self.decay_history.iter().sum::<f32>()
            / self.decay_history.len() as f32;
        self.metrics.conflict_ratio = self.conflict_history.iter().sum::<f32>()
            / self.conflict_history.len() as f32;
        self.metrics.insight_rate = self.insight_history.iter().sum::<f32>()
            / self.insight_history.len() as f32;
        self.metrics.goal_velocity = self.goal_history.iter().sum::<f32>()
            / self.goal_history.len() as f32;

        // Calculate health score
        self.metrics.calculate_health();
    }

    /// Get current cognitive metrics
    pub fn metrics(&self) -> &CognitiveMetrics {
        &self.metrics
    }

    /// Check if metrics are valid (past warmup period)
    pub fn is_ready(&self) -> bool {
        self.cycle_count >= self.config.warmup_cycles as u64
    }

    /// Generate regulatory bids if pathological patterns detected
    ///
    /// Returns a list of regulatory bids to inject into the attention competition.
    /// These bids will compete with regular bids and, if they win, will adjust
    /// system parameters to correct cognitive dysfunction.
    pub fn check_for_interventions(&mut self) -> Vec<RegulatoryBid> {
        let mut bids = Vec::new();

        // Don't intervene until we have enough data
        if !self.is_ready() {
            return bids;
        }

        // Detect Thrashing: High decay + Low goal velocity
        if self.metrics.is_thrashing() {
            self.intervention_count += 1;
            bids.push(RegulatoryBid::new(
                RegulatoryAction::DecreaseDecayRate,
                0.85, // High priority - thrashing is severe
                format!(
                    "Thrashing detected: decay={:.2}, goal_velocity={:.2}",
                    self.metrics.decay_velocity,
                    self.metrics.goal_velocity
                ),
            ));
            bids.push(RegulatoryBid::new(
                RegulatoryAction::IncreaseFocusPersistence,
                0.80,
                "Reduce context switching to help complete goals".to_string(),
            ));
        }

        // Detect Fixation: Near-zero decay
        if self.metrics.is_fixated() {
            self.intervention_count += 1;
            bids.push(RegulatoryBid::new(
                RegulatoryAction::ForceContextSwitch,
                0.90, // Very high priority - fixation prevents new input
                format!(
                    "Fixation detected: decay={:.2}",
                    self.metrics.decay_velocity
                ),
            ));
            bids.push(RegulatoryBid::new(
                RegulatoryAction::IncreaseDecayRate,
                0.75,
                "Speed up thought decay to allow new inputs".to_string(),
            ));
        }

        // Detect Confusion: High conflict + Low insight
        if self.metrics.is_confused() {
            self.intervention_count += 1;
            bids.push(RegulatoryBid::new(
                RegulatoryAction::IncreaseInsightSensitivity,
                0.80,
                format!(
                    "Confusion detected: conflict={:.2}, insight={:.2}",
                    self.metrics.conflict_ratio,
                    self.metrics.insight_rate
                ),
            ));
            bids.push(RegulatoryBid::new(
                RegulatoryAction::ReduceNoiseSensitivity,
                0.70,
                "Filter input noise to reduce conflict".to_string(),
            ));
        }

        // Detect Stagnation: Low insight + Low goal velocity
        if self.metrics.is_stagnant() {
            self.intervention_count += 1;
            bids.push(RegulatoryBid::new(
                RegulatoryAction::IncreaseInsightSensitivity,
                0.75,
                format!(
                    "Stagnation detected: insight={:.2}, goal_velocity={:.2}",
                    self.metrics.insight_rate,
                    self.metrics.goal_velocity
                ),
            ));
            bids.push(RegulatoryBid::new(
                RegulatoryAction::IncreaseInputSensitivity,
                0.65,
                "Increase sensitivity to capture new information".to_string(),
            ));
        }

        bids
    }

    /// Get statistics about the monitor
    pub fn stats(&self) -> MonitorStats {
        MonitorStats {
            cycle_count: self.cycle_count,
            intervention_count: self.intervention_count,
            current_health: self.metrics.health_score,
            is_ready: self.is_ready(),
        }
    }
}

/// Statistics about meta-cognition monitoring
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitorStats {
    /// Total cognitive cycles observed
    pub cycle_count: u64,

    /// Total regulatory interventions made
    pub intervention_count: u64,

    /// Current cognitive health score (0.0-1.0)
    pub current_health: f32,

    /// Whether monitor has enough data for valid metrics
    pub is_ready: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cognitive_metrics_neutral() {
        let metrics = CognitiveMetrics::neutral();
        assert_eq!(metrics.decay_velocity, 0.5);
        assert_eq!(metrics.conflict_ratio, 0.5);
        assert_eq!(metrics.insight_rate, 0.5);
        assert_eq!(metrics.goal_velocity, 0.5);
    }

    #[test]
    fn test_cognitive_metrics_health_calculation() {
        let mut metrics = CognitiveMetrics {
            decay_velocity: 0.5,  // Ideal
            conflict_ratio: 0.4,  // Ideal
            insight_rate: 0.6,    // Good
            goal_velocity: 0.5,   // Good
            health_score: 0.0,
        };
        metrics.calculate_health();
        assert!(metrics.health_score > 0.8); // Should be healthy
    }

    #[test]
    fn test_cognitive_metrics_thrashing_detection() {
        let metrics = CognitiveMetrics {
            decay_velocity: 0.9,  // Very high
            conflict_ratio: 0.5,
            insight_rate: 0.3,
            goal_velocity: 0.1,   // Very low
            health_score: 0.0,
        };
        assert!(metrics.is_thrashing());
    }

    #[test]
    fn test_cognitive_metrics_fixation_detection() {
        let metrics = CognitiveMetrics {
            decay_velocity: 0.05, // Near zero
            conflict_ratio: 0.2,
            insight_rate: 0.3,
            goal_velocity: 0.4,
            health_score: 0.0,
        };
        assert!(metrics.is_fixated());
    }

    #[test]
    fn test_cognitive_metrics_confusion_detection() {
        let metrics = CognitiveMetrics {
            decay_velocity: 0.5,
            conflict_ratio: 0.8,  // Very high
            insight_rate: 0.1,    // Very low
            goal_velocity: 0.3,
            health_score: 0.0,
        };
        assert!(metrics.is_confused());
    }

    #[test]
    fn test_cognitive_metrics_stagnation_detection() {
        let metrics = CognitiveMetrics {
            decay_velocity: 0.4,
            conflict_ratio: 0.3,
            insight_rate: 0.1,    // Very low
            goal_velocity: 0.1,   // Very low
            health_score: 0.0,
        };
        assert!(metrics.is_stagnant());
    }

    #[test]
    fn test_regulatory_action_descriptions() {
        let action = RegulatoryAction::IncreaseDecayRate;
        assert!(action.description().contains("decay"));

        let intent = action.intent();
        assert!(intent.starts_with("🧠 Meta:"));
    }

    #[test]
    fn test_regulatory_bid_creation() {
        let bid = RegulatoryBid::new(
            RegulatoryAction::ForceContextSwitch,
            0.9,
            "Fixation detected",
        );
        assert_eq!(bid.priority, 0.9);
        assert!(bid.reason.contains("Fixation"));
    }

    #[test]
    fn test_monitor_creation() {
        let monitor = MetaCognitionMonitor::default();
        assert_eq!(monitor.cycle_count, 0);
        assert_eq!(monitor.intervention_count, 0);
        assert!(!monitor.is_ready()); // Not ready until warmup
    }

    #[test]
    fn test_monitor_warmup() {
        let mut monitor = MetaCognitionMonitor::default();

        // Update metrics 5 times (less than warmup)
        for _ in 0..5 {
            monitor.update_metrics(0.5, 0.5, 0.5, 0.5);
        }
        assert!(!monitor.is_ready());

        // Update 10 more times (past warmup)
        for _ in 0..10 {
            monitor.update_metrics(0.5, 0.5, 0.5, 0.5);
        }
        assert!(monitor.is_ready());
    }

    #[test]
    fn test_monitor_metrics_averaging() {
        let mut monitor = MetaCognitionMonitor::default();

        // Add 20 cycles with varying decay
        for i in 0..20 {
            let decay = if i < 10 { 0.3 } else { 0.7 };
            monitor.update_metrics(decay, 0.5, 0.5, 0.5);
        }

        // Average should be 0.5
        let metrics = monitor.metrics();
        assert!((metrics.decay_velocity - 0.5).abs() < 0.01);
    }

    #[test]
    fn test_monitor_thrashing_intervention() {
        let mut monitor = MetaCognitionMonitor::default();

        // Warmup with normal values
        for _ in 0..10 {
            monitor.update_metrics(0.5, 0.5, 0.5, 0.5);
        }

        // Create thrashing condition
        for _ in 0..20 {
            monitor.update_metrics(0.9, 0.5, 0.3, 0.1);
        }

        let interventions = monitor.check_for_interventions();
        assert!(!interventions.is_empty());

        // Should suggest decreasing decay rate
        assert!(interventions.iter().any(|b| matches!(
            b.action,
            RegulatoryAction::DecreaseDecayRate
        )));
    }

    #[test]
    fn test_monitor_fixation_intervention() {
        let mut monitor = MetaCognitionMonitor::default();

        // Warmup
        for _ in 0..10 {
            monitor.update_metrics(0.5, 0.5, 0.5, 0.5);
        }

        // Create fixation condition
        for _ in 0..20 {
            monitor.update_metrics(0.05, 0.2, 0.3, 0.4);
        }

        let interventions = monitor.check_for_interventions();
        assert!(!interventions.is_empty());

        // Should suggest forcing context switch
        assert!(interventions.iter().any(|b| matches!(
            b.action,
            RegulatoryAction::ForceContextSwitch
        )));
    }

    #[test]
    fn test_monitor_stats() {
        let mut monitor = MetaCognitionMonitor::default();

        for _ in 0..15 {
            monitor.update_metrics(0.5, 0.5, 0.5, 0.5);
        }

        let stats = monitor.stats();
        assert_eq!(stats.cycle_count, 15);
        assert!(stats.is_ready);
    }
}
