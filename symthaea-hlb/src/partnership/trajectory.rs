use symthaea_core::hdc::relational_consciousness::RelationshipStage;
use serde::{Deserialize, Serialize};

/// A single observation along the relationship trajectory.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrajectoryPoint {
    pub time: f64,
    pub stage: RelationshipStage,
    pub phi_dyad: f64,
}

/// Summary of how a relationship is evolving.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrendSummary {
    pub phi_delta: f64,
    pub stages_visited: Vec<RelationshipStage>,
}

/// Simple in-memory relationship trajectory.
#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct RelationshipTrajectory {
    points: Vec<TrajectoryPoint>,
}

impl RelationshipTrajectory {
    /// Record a new trajectory point.
    pub fn record(&mut self, time: f64, stage: RelationshipStage, phi_dyad: f64) {
        self.points.push(TrajectoryPoint {
            time,
            stage,
            phi_dyad,
        });
    }

    /// Get the latest point, if any.
    pub fn latest(&self) -> Option<&TrajectoryPoint> {
        self.points.last()
    }

    /// Compute a very simple trend summary (first vs last Φ and stages visited).
    pub fn trend(&self) -> Option<TrendSummary> {
        if self.points.len() < 2 {
            return None;
        }

        let first = &self.points[0];
        let last = self.points.last().unwrap();

        let phi_delta = last.phi_dyad - first.phi_dyad;
        let stages_visited = self.points.iter().map(|p| p.stage).collect();

        Some(TrendSummary {
            phi_delta,
            stages_visited,
        })
    }

    /// Get all recorded points.
    pub fn points(&self) -> &[TrajectoryPoint] {
        &self.points
    }
}

