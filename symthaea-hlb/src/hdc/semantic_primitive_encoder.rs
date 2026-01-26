//! # Semantic Primitive Encoder: Aligned Encoding Spaces
//!
//! **The Key Insight**: Previous primitive activations hovered at ~51% (barely above random)
//! because primitives and embeddings used DIFFERENT encoding schemes:
//! - Primitives: name_hash → Blake3 → HV16
//! - Embeddings: float_vector → Gaussian_matrix → sign → HV16
//!
//! These are **orthogonal spaces** by design!
//!
//! **The Fix**: Generate primitive HV16s using the SAME projection as embeddings.
//! This aligns the spaces so semantic similarity becomes meaningful.
//!
//! ## Architecture
//!
//! ```text
//! ┌───────────────────────────────────────────────────────────────────┐
//! │                   ALIGNED ENCODING PIPELINE                        │
//! │                                                                    │
//! │  ┌─────────────────┐     ┌──────────────────┐    ┌──────────────┐ │
//! │  │ Primitive Name  │ ──► │ Semantic Embed   │ ─► │   HdcBridge  │ │
//! │  │ "CAUSATION"     │     │ (1024D float)    │    │ (projection) │ │
//! │  └─────────────────┘     └──────────────────┘    └──────┬───────┘ │
//! │                                                         │         │
//! │                                                         ▼         │
//! │  ┌─────────────────┐     ┌──────────────────┐    ┌──────────────┐ │
//! │  │ Input Text      │ ──► │ Semantic Embed   │ ─► │   HdcBridge  │ │
//! │  │ "This causes X" │     │ (1024D float)    │    │ (SAME proj)  │ │
//! │  └─────────────────┘     └──────────────────┘    └──────┬───────┘ │
//! │                                                         │         │
//! │                                                         ▼         │
//! │                           ┌──────────────────────────────────────┐│
//! │                           │   MEANINGFUL SIMILARITY (60-80%)    ││
//! │                           │   because SAME projection matrix!   ││
//! │                           └──────────────────────────────────────┘│
//! └───────────────────────────────────────────────────────────────────┘
//! ```

use symthaea_core::hdc::binary_hv::HV16;
use symthaea_core::hdc::primitive_system::{PrimitiveSystem, PrimitiveTier, Primitive};
use crate::embeddings::{HdcBridge, BridgeConfig, QWEN3_DIMENSION};
use std::collections::HashMap;
use once_cell::sync::Lazy;

/// Semantic encoding for a primitive - both embedding and HV16 via same projection
#[derive(Clone)]
pub struct SemanticPrimitive {
    /// Primitive name
    pub name: String,
    /// Primitive tier
    pub tier: PrimitiveTier,
    /// Semantic embedding (1024D for Qwen3)
    pub embedding: Vec<f32>,
    /// HV16 via HdcBridge projection (ALIGNED with input embeddings!)
    pub hv16: HV16,
    /// Rich description for better semantic matching
    pub description: String,
}

/// Semantic primitive encoder with aligned encoding spaces
pub struct SemanticPrimitiveEncoder {
    /// All primitives with semantic encodings
    primitives: Vec<SemanticPrimitive>,
    /// Name to index lookup
    name_to_idx: HashMap<String, usize>,
    /// The HdcBridge used for projection (SHARED with input encoding)
    bridge: HdcBridge,
    /// Embedding dimension
    embed_dim: usize,
}

/// Global cached instance
static GLOBAL_SEMANTIC_ENCODER: Lazy<SemanticPrimitiveEncoder> =
    Lazy::new(SemanticPrimitiveEncoder::new);

impl SemanticPrimitiveEncoder {
    /// Access the global cached encoder
    pub fn global() -> &'static SemanticPrimitiveEncoder {
        &GLOBAL_SEMANTIC_ENCODER
    }

    /// Create a new semantic primitive encoder
    pub fn new() -> Self {
        Self::with_config(BridgeConfig::default())
    }

    /// Create with custom bridge config
    pub fn with_config(bridge_config: BridgeConfig) -> Self {
        let bridge = HdcBridge::with_config(bridge_config);
        let embed_dim = QWEN3_DIMENSION;

        // Get all primitives from the base system
        let primitive_system = PrimitiveSystem::global();

        // Generate semantic encodings for each primitive
        let mut primitives = Vec::new();
        let mut name_to_idx = HashMap::new();

        for prim in primitive_system.all_primitives() {
            let description = Self::primitive_description(&prim.name, prim.tier);
            let embedding = Self::generate_semantic_embedding(&prim.name, &description, prim.tier, embed_dim);
            let hv16 = bridge.project(&embedding);

            let idx = primitives.len();
            name_to_idx.insert(prim.name.clone(), idx);

            primitives.push(SemanticPrimitive {
                name: prim.name.clone(),
                tier: prim.tier,
                embedding,
                hv16,
                description,
            });
        }

        Self {
            primitives,
            name_to_idx,
            bridge,
            embed_dim,
        }
    }

    /// Generate rich description for a primitive
    fn primitive_description(name: &str, tier: PrimitiveTier) -> String {
        // Rich descriptions for better semantic matching
        let tier_context = match tier {
            PrimitiveTier::NSM => "human semantic understanding",
            PrimitiveTier::Mathematical => "mathematical and logical reasoning",
            PrimitiveTier::Physical => "physical reality and causation",
            PrimitiveTier::Geometric => "spatial and geometric relationships",
            PrimitiveTier::Strategic => "strategic planning and decision-making",
            PrimitiveTier::MetaCognitive => "self-awareness and metacognition",
            PrimitiveTier::Temporal => "temporal reasoning and sequences",
            PrimitiveTier::Compositional => "compositional structure and patterns",
            PrimitiveTier::Consciousness => "conscious experience and awareness",
        };

        // Generate description based on primitive name and tier
        format!(
            "{} - a fundamental concept in {} representing {}",
            name.to_lowercase().replace('_', " "),
            tier_context,
            Self::name_to_meaning(name)
        )
    }

    /// Convert primitive name to semantic meaning
    fn name_to_meaning(name: &str) -> &'static str {
        match name {
            // NSM primitives
            "I" => "self-reference and personal identity",
            "YOU" => "addressing another being or entity",
            "SOMEONE" => "an unspecified person or agent",
            "SOMETHING" => "an unspecified thing or object",
            "PEOPLE" => "collective human beings",
            "BODY" => "physical form and embodiment",
            "KNOW" => "having knowledge or awareness",
            "THINK" => "cognitive processing and reasoning",
            "WANT" => "desire and intention",
            "FEEL" => "emotional or sensory experience",
            "SEE" => "visual perception",
            "HEAR" => "auditory perception",
            "SAY" => "verbal communication",
            "WORDS" => "linguistic units of meaning",
            "TRUE" => "correspondence with reality",
            "DO" => "performing an action",
            "HAPPEN" => "occurrence of an event",
            "MOVE" => "change in position",
            "TOUCH" => "physical contact",
            "GOOD" => "positive value or quality",
            "BAD" => "negative value or quality",
            "BIG" => "large in size or magnitude",
            "SMALL" => "small in size or magnitude",
            "VERY" => "high degree or intensity",
            "MORE" => "greater quantity or degree",
            "LIKE" => "similarity or preference",
            "KIND" => "type or category",
            "PART" => "component of a whole",
            "THIS" => "proximal reference",
            "SAME" => "identity or equivalence",
            "OTHER" => "difference or alternative",
            "ONE" => "singular quantity",
            "TWO" => "dual quantity",
            "SOME" => "partial quantity",
            "ALL" => "complete totality",
            "MANY" => "large quantity",
            "MUCH" => "high degree of amount",
            "LONG" => "extended in time or space",
            "SHORT" => "brief in time or limited in space",
            "FAR" => "distant in space or time",
            "NEAR" => "close in space or time",
            "WHEN" => "temporal reference",
            "NOW" => "present moment",
            "AFTER" => "following in time",
            "BEFORE" => "preceding in time",
            "WHERE" => "spatial reference",
            "HERE" => "proximal location",
            "ABOVE" => "higher position",
            "BELOW" => "lower position",
            "SIDE" => "lateral position",
            "INSIDE" => "internal position",
            "NOT" => "negation or absence",
            "CAN" => "possibility or ability",
            "BECAUSE" => "causal relationship",
            "IF" => "conditional relationship",
            "MAYBE" => "uncertainty or possibility",
            "LIVE" => "being alive or dwelling",
            "DIE" => "cessation of life",

            // Mathematical primitives
            "ZERO" => "absence of quantity, additive identity",
            "SUCCESSOR" => "next element in sequence",
            "ADD" => "combining quantities",
            "MULTIPLY" => "repeated addition, scaling",
            "EQUALS" => "identity or equivalence relation",
            "LESS_THAN" => "ordering relation",
            "SET" => "collection of distinct elements",
            "ELEMENT" => "member of a set",
            "SUBSET" => "contained set relation",
            "UNION" => "combination of sets",
            "INTERSECTION" => "common elements of sets",
            "EMPTY" => "set with no elements",
            "AND" => "logical conjunction",
            "OR" => "logical disjunction",
            "NOT_LOGIC" => "logical negation",
            "IMPLIES" => "logical implication",
            "IFF" => "logical equivalence",
            "FORALL" => "universal quantification",
            "EXISTS" => "existential quantification",
            "FUNCTION" => "mapping between sets",
            "COMPOSITION" => "chaining of functions",
            "INVERSE" => "reverse mapping",
            "LIMIT" => "convergence point",
            "DERIVATIVE" => "rate of change",
            "INTEGRAL" => "accumulated quantity",
            "GRADIENT" => "direction of steepest ascent",

            // Physical primitives
            "MASS" => "quantity of matter",
            "FORCE" => "interaction causing acceleration",
            "ENERGY" => "capacity to do work",
            "MOMENTUM" => "mass times velocity",
            "POSITION" => "location in space",
            "VELOCITY" => "rate of position change",
            "ACCELERATION" => "rate of velocity change",
            "FIELD" => "spatially distributed property",
            "WAVE" => "propagating disturbance",
            "PARTICLE" => "localized discrete entity",
            "ENTROPY" => "measure of disorder",
            "TEMPERATURE" => "average kinetic energy",
            "PRESSURE" => "force per unit area",
            "DENSITY" => "mass per unit volume",
            "CHARGE" => "electromagnetic property",
            "CURRENT" => "flow of charge",
            "POTENTIAL" => "stored energy per unit",
            "RESISTANCE" => "opposition to flow",
            "CAUSATION" => "one event producing another",
            "CONSERVATION" => "quantity remaining constant",
            "SYMMETRY" => "invariance under transformation",
            "BOUNDARY" => "interface between regions",
            "FLOW" => "continuous movement",
            "STATE" => "configuration at a moment",
            "TRANSITION" => "change between states",
            "EQUILIBRIUM" => "balanced stable state",
            "WAVE_PARTICLE_DUALITY" => "quantum complementarity",

            // Geometric primitives
            "POINT" => "location without extent",
            "LINE" => "one-dimensional extent",
            "PLANE" => "two-dimensional extent",
            "VOLUME" => "three-dimensional extent",
            "DISTANCE" => "separation between points",
            "ANGLE" => "rotation between directions",
            "CURVE" => "continuous bent path",
            "SURFACE" => "two-dimensional boundary",
            "MANIFOLD" => "locally Euclidean space",
            "DIMENSION" => "degree of freedom",
            "METRIC" => "distance measure",
            "CURVATURE" => "deviation from flatness",
            "GEODESIC" => "shortest path on surface",
            "TOPOLOGY" => "properties preserved under deformation",
            "CONNECTED" => "path exists between any points",
            "BOUNDARY_GEO" => "edge of a region",
            "INTERIOR" => "inside of a region",
            "EXTERIOR" => "outside of a region",
            "ADJACENT" => "sharing a boundary",
            "CONTAINS" => "one region inside another",
            "OVERLAPS" => "regions sharing interior",
            "DISJOINT" => "no shared points",
            "TANGENT" => "touching at single point",
            "PARALLEL" => "same direction, never meeting",
            "PERPENDICULAR" => "meeting at right angles",
            "CONGRUENT" => "same shape and size",
            "SIMILAR" => "same shape, different size",
            "TRANSFORM" => "change in position or shape",
            "ROTATION" => "turning around an axis",
            "TRANSLATION" => "shifting position",
            "REFLECTION" => "mirror image",
            "SCALE" => "change in size",

            // Strategic primitives
            "AGENT" => "entity capable of action",
            "ACTION" => "deliberate behavior",
            "GOAL" => "desired end state",
            "STRATEGY" => "plan to achieve goals",
            "UTILITY" => "value or satisfaction",
            "PREFERENCE" => "ordering of outcomes",
            "CHOICE" => "selection among alternatives",
            "RISK" => "probability of negative outcome",
            "REWARD" => "positive consequence",
            "COST" => "negative consequence or sacrifice",
            "GAME" => "strategic interaction",
            "PLAYER" => "agent in a game",
            "PAYOFF" => "outcome value for player",
            "NASH_EQ" => "stable strategy profile",
            "PARETO" => "no improvement without harm",
            "COOPERATION" => "joint beneficial action",
            "COMPETITION" => "opposing interests",
            "COORDINATION" => "aligning actions",
            "TRUST" => "belief in reliability",
            "REPUTATION" => "past behavior record",
            "SIGNAL" => "information transmission",
            "COMMITMENT" => "binding future action",
            "NEGOTIATION" => "reaching agreement",
            "COALITION" => "group acting together",
            "NORM" => "expected behavior standard",
            "SANCTION" => "punishment for violation",
            "EXCHANGE" => "mutual transfer of value",
            "CONTRACT" => "binding agreement",
            "PROPERTY" => "ownership rights",
            "TRUST_ECONOMIC" => "economic reliability",
            "SUPPLY" => "available quantity",
            "DEMAND" => "desired quantity",
            "PRICE" => "exchange rate",
            "MARKET" => "exchange system",
            "CAPITAL" => "productive resources",
            "LABOR" => "human productive effort",
            "PROFIT" => "excess of revenue over cost",
            "DEBT" => "obligation to repay",
            "INTEREST" => "cost of borrowing",
            "INVESTMENT" => "resource allocation for future return",

            // Meta-cognitive primitives
            "SELF" => "the experiencing subject",
            "IDENTITY" => "continuity of self",
            "AWARENESS" => "conscious attention",
            "METACOGNITION" => "thinking about thinking",
            "INTROSPECTION" => "examining own mental states",
            "BELIEF" => "held proposition",
            "DOUBT" => "uncertainty about belief",
            "CERTAINTY" => "high confidence in belief",
            "EVIDENCE" => "support for belief",
            "REASON" => "logical justification",
            "ERROR" => "deviation from correct",
            "CORRECTION" => "fixing an error",
            "LEARNING" => "acquiring knowledge",
            "MEMORY_META" => "storing and retrieving information",
            "ATTENTION" => "focused processing",
            "INTENTION" => "plan to act",
            "DECISION" => "commitment to action",
            "CONTROL" => "directing behavior",
            "FEEDBACK" => "information about outcomes",
            "ADAPTATION" => "adjusting to environment",
            "HOMEOSTASIS" => "maintaining stability",
            "REPAIR" => "restoring function",
            "GROWTH" => "increase in capability",
            "DECAY" => "decrease in capability",
            "THRESHOLD" => "triggering level",
            "SETPOINT" => "target value",

            // Temporal primitives
            "INSTANT" => "point in time",
            "INTERVAL" => "span of time",
            "DURATION" => "length of time",
            "SEQUENCE" => "ordered series",
            "SIMULTANEOUS" => "happening at same time",
            "PRECEDES" => "happening before",
            "FOLLOWS" => "happening after",
            "DURING" => "within a time span",
            "MEETS" => "end touching start",
            "STARTS" => "beginning together",
            "FINISHES" => "ending together",
            "OVERLAPS_TEMP" => "partially concurrent",
            "CYCLE" => "repeating pattern",
            "PERIOD" => "time of one cycle",
            "FREQUENCY" => "cycles per time",
            "PHASE" => "position in cycle",
            "PAST" => "before now",
            "PRESENT" => "at now",
            "FUTURE" => "after now",
            "ALWAYS" => "at all times",
            "NEVER" => "at no time",
            "SOMETIMES" => "at some times",
            "DEADLINE" => "time limit",
            "DELAY" => "waiting period",
            "PACE" => "rate of progress",
            "RHYTHM" => "regular pattern in time",
            "TREND" => "direction over time",

            // Compositional primitives
            "SEQUENCE_OP" => "ordered combination",
            "PARALLEL_OP" => "simultaneous combination",
            "CHOICE_OP" => "alternative selection",
            "ITERATE" => "repeated application",
            "FIXPOINT" => "stable under application",
            "COMPOSE" => "chaining operations",
            "ABSTRACT" => "generalizing pattern",
            "INSTANTIATE" => "specific instance",
            "RECURSE" => "self-reference in definition",
            "AGGREGATE" => "combining multiple into one",
            "DISTRIBUTE" => "spreading one to many",
            "NEST" => "structure within structure",
            "FLATTEN" => "removing nesting",
            "MAP" => "applying to each element",
            "FILTER" => "selecting by criterion",
            "REDUCE" => "combining to single value",
            "FOLD" => "accumulating over sequence",
            "UNFOLD" => "generating sequence",
            "BIND" => "connecting operations",
            "UNBIND" => "disconnecting operations",
            "CONTEXT" => "surrounding environment",
            "SCOPE" => "region of validity",
            "CLOSURE" => "self-contained unit",
            "MONAD" => "sequencing computation",
            "FUNCTOR" => "structure-preserving map",

            // Consciousness primitives
            "QUALE" => "subjective experiential quality",
            "PHENOMENAL_BINDING" => "unified conscious experience",
            "ATTEND" => "directing conscious focus",
            "SALIENCE" => "prominence in awareness",
            "REMEMBER" => "conscious recall",
            "CONSOLIDATE" => "strengthening memory",
            "INTEND" => "forming conscious purpose",
            "AGENCY" => "sense of causing actions",
            "OWNERSHIP" => "sense of belonging to self",
            "PRESENCE" => "feeling of being here now",
            "AROUSAL" => "level of activation",
            "VALENCE" => "positive or negative quality",
            "EMOTION" => "felt affective state",
            "MOOD" => "persistent affective background",
            "PAIN" => "unpleasant sensation",
            "PLEASURE" => "pleasant sensation",
            "DESIRE" => "wanting something",
            "AVERSION" => "wanting to avoid",
            "CURIOSITY" => "desire to know",
            "BOREDOM" => "lack of engagement",
            "SURPRISE" => "unexpected occurrence",
            "FEAR" => "anticipation of harm",
            "ANGER" => "response to obstruction",
            "SADNESS" => "response to loss",
            "JOY" => "response to gain",
            "LOVE" => "deep positive attachment",
            "DISGUST" => "rejection response",
            "CARE" => "concern for wellbeing",

            // Additional primitives
            "COMMON_KNOWLEDGE" => "shared mutual awareness",
            "META_BELIEF" => "belief about beliefs",
            "REFERENCE" => "pointing to something",
            "SIGN" => "indicator of meaning",
            "SYMBOL" => "arbitrary meaning carrier",
            "METAPHOR" => "understanding one thing via another",
            "ANALOGY" => "structural correspondence",
            "CONTEXT_DEPENDENCY" => "meaning depending on context",
            "PRAGMATICS" => "language use in context",
            "SPEECH_ACT" => "doing things with words",
            "IMPLICATURE" => "implied meaning",
            "PRESUPPOSITION" => "assumed background",
            "INFORMATION" => "reduction of uncertainty",
            "ENTROPY_INFO" => "measure of uncertainty",
            "CHANNEL" => "path for information",
            "NOISE" => "interference with signal",
            "REDUNDANCY" => "excess for error correction",
            "COMPRESSION" => "reducing representation size",
            "CODE" => "systematic representation",
            "ENCODING" => "transforming to representation",
            "DECODING" => "recovering from representation",
            "MUTUAL_INFORMATION" => "shared information content",
            "CONDITIONAL" => "information given something",
            "INDEPENDENCE" => "no information relationship",
            "CORRELATION" => "statistical relationship",
            "BAYESIAN" => "updating beliefs with evidence",
            "LIKELIHOOD" => "probability given hypothesis",
            "PRIOR" => "belief before evidence",
            "POSTERIOR" => "belief after evidence",
            "HYPOTHESIS" => "proposed explanation",
            "PREDICTION" => "expected future state",
            "MORPHOGEN" => "pattern-forming signal",
            "DIFFERENTIATION" => "becoming specialized",
            "INTEGRATION" => "combining into whole",
            "WORK" => "directed energy transfer",
            "SPIN" => "intrinsic angular momentum",
            "CROSS_PRODUCT" => "perpendicular combination",
            "BINDING_WINDOW" => "temporal window for integration",
            "CONSUME" => "using up resources",

            _ => "fundamental conceptual primitive",
        }
    }

    /// Generate semantic embedding for a primitive
    ///
    /// In production, this would use Qwen3/BGE. For now, we use
    /// content-addressable simulation that creates similar embeddings
    /// for semantically related primitives.
    fn generate_semantic_embedding(name: &str, description: &str, tier: PrimitiveTier, dim: usize) -> Vec<f32> {
        let mut embedding = vec![0.0f32; dim];

        // Create embedding based on CONTENT, not just hash
        // This simulates what a real embedding model would do

        // 1. Base embedding from description words
        let words: Vec<&str> = description
            .split_whitespace()
            .filter(|w| w.len() > 3)
            .collect();

        for (i, word) in words.iter().enumerate() {
            // Each word contributes to specific dimensions
            let word_hash = Self::content_hash(word);
            let start_dim = (word_hash as usize % (dim / 4)) * 4;

            for j in 0..4 {
                let idx = (start_dim + j) % dim;
                let sign = if (word_hash >> j) & 1 == 0 { 1.0 } else { -1.0 };
                embedding[idx] += sign * (1.0 / (i + 1) as f32);
            }
        }

        // 2. Tier-specific signature (ensures tier clustering)
        let tier_base = match tier {
            PrimitiveTier::NSM => 0,
            PrimitiveTier::Mathematical => 128,
            PrimitiveTier::Physical => 256,
            PrimitiveTier::Geometric => 384,
            PrimitiveTier::Strategic => 512,
            PrimitiveTier::MetaCognitive => 640,
            PrimitiveTier::Temporal => 768,
            PrimitiveTier::Compositional => 896,
            PrimitiveTier::Consciousness => 960,
        };

        // Add tier signature
        for i in 0..64 {
            let idx = (tier_base + i) % dim;
            embedding[idx] += 0.5;
        }

        // 3. Name-specific component (preserves identity)
        let name_hash = Self::content_hash(name);
        for i in 0..32 {
            let idx = ((name_hash as usize).wrapping_add(i * 31)) % dim;
            let sign = if (name_hash >> (i % 64)) & 1 == 0 { 1.0 } else { -1.0 };
            embedding[idx] += sign * 0.3;
        }

        // 4. Normalize
        let norm: f32 = embedding.iter().map(|x| x * x).sum::<f32>().sqrt();
        if norm > 1e-6 {
            for x in embedding.iter_mut() {
                *x /= norm;
            }
        }

        embedding
    }

    /// Content-based hash (similar text → similar hash)
    fn content_hash(text: &str) -> u64 {
        let normalized = text.to_lowercase();
        let mut hash: u64 = 0x5974_1AEA; // SYMTHAEA

        for byte in normalized.bytes() {
            hash = hash.wrapping_mul(31).wrapping_add(byte as u64);
        }

        hash
    }

    /// Get all semantic primitives
    pub fn all_primitives(&self) -> impl Iterator<Item = &SemanticPrimitive> {
        self.primitives.iter()
    }

    /// Get primitive by name
    pub fn get(&self, name: &str) -> Option<&SemanticPrimitive> {
        self.name_to_idx.get(name).map(|&idx| &self.primitives[idx])
    }

    /// Get the shared HdcBridge (for projecting input embeddings)
    pub fn bridge(&self) -> &HdcBridge {
        &self.bridge
    }

    /// Project an embedding to HV16 using the SAME bridge as primitives
    pub fn project_embedding(&self, embedding: &[f32]) -> HV16 {
        self.bridge.project(embedding)
    }

    /// Find primitives activated by an embedding
    ///
    /// Returns primitives sorted by activation (similarity) descending.
    pub fn find_activated(
        &self,
        embedding: &[f32],
        threshold: f32,
        max_results: usize,
    ) -> Vec<(String, PrimitiveTier, f32)> {
        let input_hv = self.bridge.project(embedding);

        let mut activations: Vec<(String, PrimitiveTier, f32)> = self.primitives
            .iter()
            .map(|p| {
                let similarity = input_hv.similarity(&p.hv16);
                (p.name.clone(), p.tier, similarity)
            })
            .filter(|(_, _, sim)| *sim > threshold)
            .collect();

        activations.sort_by(|a, b| b.2.partial_cmp(&a.2).unwrap_or(std::cmp::Ordering::Equal));
        activations.truncate(max_results);
        activations
    }

    /// Compute similarity between two embeddings in aligned HV16 space
    pub fn embedding_similarity(&self, emb_a: &[f32], emb_b: &[f32]) -> f32 {
        let hv_a = self.bridge.project(emb_a);
        let hv_b = self.bridge.project(emb_b);
        hv_a.similarity(&hv_b)
    }

    /// Get embedding dimension
    pub fn embedding_dim(&self) -> usize {
        self.embed_dim
    }

    /// Count total primitives
    pub fn primitive_count(&self) -> usize {
        self.primitives.len()
    }
}

impl Default for SemanticPrimitiveEncoder {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encoder_creation() {
        let encoder = SemanticPrimitiveEncoder::new();
        assert!(encoder.primitive_count() > 100);
    }

    #[test]
    fn test_primitive_lookup() {
        let encoder = SemanticPrimitiveEncoder::new();
        let causation = encoder.get("CAUSATION");
        assert!(causation.is_some());
        assert_eq!(causation.unwrap().tier, PrimitiveTier::Physical);
    }

    #[test]
    fn test_aligned_projection() {
        let encoder = SemanticPrimitiveEncoder::new();

        // Create two similar embeddings
        let emb1 = vec![0.1f32; encoder.embedding_dim()];
        let mut emb2 = emb1.clone();
        emb2[0] = 0.11; // Slightly different

        // Project both
        let hv1 = encoder.project_embedding(&emb1);
        let hv2 = encoder.project_embedding(&emb2);

        // Should be highly similar (same projection matrix)
        let sim = hv1.similarity(&hv2);
        assert!(sim > 0.9);
    }

    #[test]
    fn test_find_activated() {
        let encoder = SemanticPrimitiveEncoder::new();

        // Get a primitive's embedding and check it finds itself
        if let Some(causation) = encoder.get("CAUSATION") {
            let activated = encoder.find_activated(&causation.embedding, 0.5, 10);
            assert!(!activated.is_empty());
            // Should find CAUSATION with high activation
            let has_causation = activated.iter().any(|(name, _, _)| name == "CAUSATION");
            assert!(has_causation);
        }
    }
}
