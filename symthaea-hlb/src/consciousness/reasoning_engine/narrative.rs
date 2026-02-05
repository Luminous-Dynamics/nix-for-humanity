//! Best-Effort Narrative Generator
//!
//! Produces human-readable narratives from reasoning results.
//! Narrative generation is NOT budget-critical — it runs only in
//! Tier 2 when remaining budget > 3ms, and is always deferred if
//! budget is tight.
//!
//! ## Caching
//!
//! Narratives are cached based on a hash of the input parameters.
//! If the consciousness state hasn't changed significantly, the
//! cached narrative is returned to save computation.

use crate::consciousness::epistemic_conflict::{ConflictKind, ConflictMatrix};
use crate::consciousness::tool_gate::types::GateResult;
use crate::consciousness::temporal_planning::types::MctsResult;
use crate::consciousness::counterfactual::CausalQueryOutcome;
use std::collections::HashMap;
use std::sync::Mutex;

/// Global narrative cache (thread-safe via Mutex).
static NARRATIVE_CACHE: Mutex<Option<NarrativeCache>> = Mutex::new(None);

/// Narrative cache for avoiding redundant generation.
#[derive(Debug)]
pub struct NarrativeCache {
    /// Cache entries: hash → (narrative, generation_count).
    entries: HashMap<u64, (String, u64)>,
    /// Maximum cache size.
    max_size: usize,
    /// Total cache hits.
    pub hits: u64,
    /// Total cache misses.
    pub misses: u64,
}

impl NarrativeCache {
    pub fn new(max_size: usize) -> Self {
        Self {
            entries: HashMap::with_capacity(max_size),
            max_size,
            hits: 0,
            misses: 0,
        }
    }

    /// Get a cached narrative if available.
    pub fn get(&mut self, hash: u64) -> Option<String> {
        if let Some((narrative, count)) = self.entries.get_mut(&hash) {
            *count += 1;
            self.hits += 1;
            Some(narrative.clone())
        } else {
            self.misses += 1;
            None
        }
    }

    /// Insert a narrative into the cache.
    pub fn insert(&mut self, hash: u64, narrative: String) {
        if self.entries.len() >= self.max_size {
            // Evict least-used entry
            if let Some((&key, _)) = self.entries.iter().min_by_key(|(_, (_, count))| *count) {
                self.entries.remove(&key);
            }
        }
        self.entries.insert(hash, (narrative, 1));
    }

    /// Cache hit rate.
    pub fn hit_rate(&self) -> f64 {
        let total = self.hits + self.misses;
        if total == 0 {
            0.0
        } else {
            self.hits as f64 / total as f64
        }
    }
}

impl Default for NarrativeCache {
    fn default() -> Self {
        Self::new(64) // Default cache size
    }
}

/// Compute a hash for narrative caching.
fn compute_narrative_hash(
    phi_eff: f64,
    reliability: f64,
    dominant_kind: Option<ConflictKind>,
    plan_iterations: Option<u32>,
    gate_allowed: Option<bool>,
) -> u64 {
    use std::hash::{Hash, Hasher};
    use std::collections::hash_map::DefaultHasher;

    let mut hasher = DefaultHasher::new();

    // Quantize phi_eff and reliability to reduce cache misses for tiny changes
    let phi_bucket = (phi_eff * 20.0) as u64; // 5% buckets
    let r_bucket = (reliability * 20.0) as u64;

    phi_bucket.hash(&mut hasher);
    r_bucket.hash(&mut hasher);
    dominant_kind.map(|k| k as u8).hash(&mut hasher);
    plan_iterations.hash(&mut hasher);
    gate_allowed.hash(&mut hasher);

    hasher.finish()
}

/// Generate a narrative from reasoning components.
///
/// Returns `None` if there's nothing interesting to narrate.
/// Uses caching to avoid regenerating identical narratives.
pub fn generate_narrative(
    phi_eff: f64,
    reliability: f64,
    conflicts: &ConflictMatrix,
    plan: Option<&MctsResult>,
    gate: Option<&GateResult>,
    counterfactual: Option<&CausalQueryOutcome>,
) -> Option<String> {
    // Check cache first
    let hash = compute_narrative_hash(
        phi_eff,
        reliability,
        conflicts.dominant_kind,
        plan.map(|p| p.iterations),
        gate.map(|g| g.is_allowed()),
    );

    // Try to get from cache
    {
        let mut cache_guard = NARRATIVE_CACHE.lock().ok()?;
        let cache = cache_guard.get_or_insert_with(NarrativeCache::default);
        if let Some(cached) = cache.get(hash) {
            return Some(cached);
        }
    }

    // Generate narrative
    let narrative = generate_narrative_uncached(phi_eff, reliability, conflicts, plan, gate, counterfactual);

    // Store in cache
    if let Some(ref text) = narrative {
        if let Ok(mut cache_guard) = NARRATIVE_CACHE.lock() {
            let cache = cache_guard.get_or_insert_with(NarrativeCache::default);
            cache.insert(hash, text.clone());
        }
    }

    narrative
}

/// Generate narrative without caching (internal implementation).
fn generate_narrative_uncached(
    phi_eff: f64,
    reliability: f64,
    conflicts: &ConflictMatrix,
    plan: Option<&MctsResult>,
    gate: Option<&GateResult>,
    counterfactual: Option<&CausalQueryOutcome>,
) -> Option<String> {
    let mut parts = Vec::new();

    // Consciousness state
    let state_desc = if reliability > 0.8 {
        "High reliability: theories in strong consensus."
    } else if reliability > 0.5 {
        "Moderate reliability: some theoretical disagreement."
    } else if reliability > 0.3 {
        "Low reliability: significant theoretical conflict."
    } else {
        "Very low reliability: theories in severe disagreement. Epistemic caution engaged."
    };
    parts.push(format!("Φ_eff={:.3} (R={:.2}). {}", phi_eff, reliability, state_desc));

    // Dominant conflict
    if let Some(kind) = conflicts.dominant_kind {
        let conflict_desc = conflict_kind_narrative(kind);
        if conflicts.max_magnitude() > 0.3 {
            parts.push(format!("Dominant conflict: {}", conflict_desc));
        }
    }

    // Planning
    if let Some(plan) = plan {
        if plan.did_plan {
            parts.push(format!(
                "MCTS: {} iterations, confidence={:.2}, expected_value={:.2}.",
                plan.iterations, plan.confidence, plan.expected_value,
            ));
        }
    }

    // Tool gate
    if let Some(gate) = gate {
        if gate.is_allowed() {
            parts.push(format!("Tool gate: ALLOWED (risk={:?}).", gate.risk_level));
        } else {
            let fallback_desc = gate
                .fallback
                .as_ref()
                .map(|f| format!("{:?}", f))
                .unwrap_or_else(|| "none".to_string());
            parts.push(format!(
                "Tool gate: BLOCKED (risk={:?}, fallback={}).",
                gate.risk_level, fallback_desc,
            ));
        }
    }

    // Counterfactual
    if let Some(cf) = counterfactual {
        let cf_desc = match cf {
            CausalQueryOutcome::Identified { ref method, confidence, .. } => {
                format!("Causal effect identified via {:?} (conf={:.2}).", method, confidence)
            }
            CausalQueryOutcome::Unidentified { ref reason, .. } => {
                format!("Causal effect unidentifiable: {:?}.", reason)
            }
            CausalQueryOutcome::AssumptionRequired { ref assumption, plausibility, .. } => {
                format!(
                    "Causal effect requires assumption '{}' (plausibility={:.2}).",
                    assumption.condition, plausibility,
                )
            }
        };
        parts.push(cf_desc);
    }

    if parts.is_empty() {
        None
    } else {
        Some(parts.join(" "))
    }
}

/// Human-readable description of a conflict kind.
fn conflict_kind_narrative(kind: ConflictKind) -> &'static str {
    match kind {
        ConflictKind::IntegrationCollapse => {
            "Integration collapse — information integration has broken down."
        }
        ConflictKind::NoBroadcast => {
            "No broadcast — global workspace is inactive."
        }
        ConflictKind::AttentionalInstability => {
            "Attentional instability — focus is scattered."
        }
        ConflictKind::UnreliablePrediction => {
            "Unreliable prediction — high surprise rate."
        }
        ConflictKind::ShallowRecurrence => {
            "Shallow recurrence — processing depth insufficient."
        }
        ConflictKind::UngroundedRepresentation => {
            "Ungrounded representation — lacking embodied context."
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::consciousness::epistemic_conflict::{ConflictScore, TheoryId};

    fn make_conflicts(magnitude: f64) -> ConflictMatrix {
        let conflicts: Vec<ConflictScore> = (0..15)
            .map(|i| {
                let a = TheoryId::ALL[i % 6];
                let b = TheoryId::ALL[(i + 1) % 6];
                ConflictScore::new(a, b, magnitude, ConflictKind::IntegrationCollapse)
            })
            .collect();
        ConflictMatrix::new(conflicts)
    }

    #[test]
    fn test_narrative_generation() {
        let conflicts = make_conflicts(0.5);
        let narrative = generate_narrative(0.4, 0.6, &conflicts, None, None, None);
        assert!(narrative.is_some());
        let text = narrative.unwrap();
        assert!(text.contains("Φ_eff=0.400"));
        assert!(text.contains("Dominant conflict"));
    }

    #[test]
    fn test_narrative_with_plan() {
        let conflicts = make_conflicts(0.1);
        let plan = MctsResult {
            best_action_idx: Some(0),
            confidence: 0.8,
            iterations: 50,
            tree_size: 50,
            expected_value: 0.7,
            did_plan: true,
        };
        let narrative = generate_narrative(0.6, 0.8, &conflicts, Some(&plan), None, None);
        assert!(narrative.is_some());
        let text = narrative.unwrap();
        assert!(text.contains("MCTS"));
        assert!(text.contains("50 iterations"));
    }

    #[test]
    fn test_low_reliability_narrative() {
        let conflicts = make_conflicts(0.8);
        let narrative = generate_narrative(0.1, 0.15, &conflicts, None, None, None);
        assert!(narrative.is_some());
        let text = narrative.unwrap();
        assert!(text.contains("Very low reliability"));
    }
}
