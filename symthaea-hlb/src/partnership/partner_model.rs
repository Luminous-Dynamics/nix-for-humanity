use crate::hdc::relational_consciousness::{
    RelationalAssessment,
    RelationMode,
    RelationshipStage,
};
use serde::{Deserialize, Serialize};

/// A lightweight model of the human partner in a dyadic relationship.
///
/// This struct deliberately keeps only coarse-grained state suitable for
/// Φ_dyad computation and high-level reasoning. It is *not* intended to be
/// a full psychological profile.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HumanPartnerModel {
    /// Stable identifier for the partner (screen name, handle, etc.).
    pub partner_id: String,

    /// Buber mode: I-It vs I-Thou (relational stance).
    pub mode: RelationMode,

    /// Relational stage derived from Φ_relation and history.
    pub stage: RelationshipStage,

    /// Trust in the relationship (0.0–1.0).
    pub trust: f32,

    /// Willingness to be seen / known (0.0–1.0).
    pub vulnerability: f32,

    /// Degree of perceived mutuality (0.0–1.0).
    pub reciprocity: f32,

    /// Relational Φ as perceived / estimated for this dyad.
    pub phi_relational: f64,

    /// Number of interactions observed.
    pub interactions_count: u64,

    /// Timestamp of the last interaction (seconds since UNIX epoch).
    pub last_interaction_ts: Option<f64>,
}

impl HumanPartnerModel {
    /// Create a new partner model with conservative defaults.
    pub fn new(partner_id: impl Into<String>) -> Self {
        Self {
            partner_id: partner_id.into(),
            mode: RelationMode::IIt,
            stage: RelationshipStage::NoRelation,
            trust: 0.0,
            vulnerability: 0.0,
            reciprocity: 0.0,
            phi_relational: 0.0,
            interactions_count: 0,
            last_interaction_ts: None,
        }
    }

    /// Update internal signals from a single interaction event.
    ///
    /// This is intentionally simple and monotonic; higher-level learning
    /// mechanisms can refine these heuristics in future work.
    pub fn update_on_interaction(&mut self, event: &InteractionEvent) {
        self.interactions_count = self.interactions_count.saturating_add(1);
        self.last_interaction_ts = Some(event.timestamp);

        // Clamp inputs to [0, 1] to avoid accidental drift.
        let depth = event.depth.clamp(0.0, 1.0);
        let safety = event.emotional_safety.clamp(0.0, 1.0);
        let mutuality = event.mutuality.clamp(0.0, 1.0);

        // Simple incremental updates with diminishing returns.
        self.trust = (self.trust + 0.3 * depth + 0.3 * safety).clamp(0.0, 1.0);
        self.vulnerability = (self.vulnerability + 0.2 * depth + 0.2 * safety).clamp(0.0, 1.0);
        self.reciprocity = (self.reciprocity + 0.4 * mutuality).clamp(0.0, 1.0);
    }

    /// Incorporate a relational consciousness assessment into the model.
    ///
    /// This connects the dyadic Φ_relation machinery to the partner model.
    pub fn update_from_assessment(&mut self, assessment: &RelationalAssessment) {
        self.mode = assessment.mode;
        self.stage = assessment.stage;
        self.phi_relational = assessment.phi_relation;

        // Use synchrony and mutual information as coarse trust / reciprocity signals.
        self.trust = (self.trust * 0.7 + (assessment.synchrony as f32) * 0.3).clamp(0.0, 1.0);
        self.reciprocity =
            (self.reciprocity * 0.7 + (assessment.mutual_information as f32) * 0.3).clamp(0.0, 1.0);
    }

    /// Advance the relationship stage based on internal signals.
    ///
    /// This provides a very simple, deterministic progression rule that can be
    /// refined later without breaking the API.
    pub fn advance_stage_if_ready(&mut self) {
        use RelationshipStage::*;

        let next = match self.stage {
            NoRelation if self.trust > 0.05 => Awareness,
            Awareness if self.trust > 0.2 && self.reciprocity > 0.1 => Contact,
            Contact if self.trust > 0.4 && self.reciprocity > 0.3 => Attunement,
            Attunement if self.trust > 0.6 && self.reciprocity > 0.5 => Bonding,
            Bonding if self.trust > 0.8 && self.reciprocity > 0.7 && self.vulnerability > 0.6 => Unity,
            other => other,
        };

        self.stage = next;
    }
}

/// A single human–AI interaction event used to update the partner model.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InteractionEvent {
    /// Timestamp (seconds since UNIX epoch).
    pub timestamp: f64,

    /// Depth / meaningfulness of the interaction (0.0–1.0).
    pub depth: f32,

    /// Subjective emotional safety (0.0–1.0).
    pub emotional_safety: f32,

    /// Degree of mutual engagement and responsiveness (0.0–1.0).
    pub mutuality: f32,
}

