//! # Domain Knowledge: A Priori Semantic Prototypes
//!
//! Provides the initial "world model" that bootstraps Symthaea's epistemic baseline.
//! These prototypes establish what the system "knows" from birth, enabling it to
//! distinguish between familiar concepts and novel/unknown queries.
//!
//! ## Design Philosophy
//!
//! The knowledge base is intentionally **conservative**:
//! - Only include concepts we are CERTAIN about
//! - Prefer general categories over specific facts
//! - Include meta-knowledge about limitations
//!
//! This prevents the system from hallucinating while enabling confident responses
//! to genuinely answerable queries.
//!
//! ## Categories
//!
//! 1. **Logic & Math** - Universal truths that don't change
//! 2. **System (NixOS)** - Domain-specific operational knowledge
//! 3. **Self-Knowledge** - Identity, capabilities, limitations
//! 4. **Conversation** - Social interaction patterns
//! 5. **Epistemics** - Knowledge about knowledge itself


/// Domain knowledge entry with label and semantic content
#[derive(Debug, Clone)]
pub struct KnowledgeEntry {
    /// Unique identifier for this knowledge
    pub label: &'static str,
    /// Category for organization
    pub category: &'static str,
    /// Rich semantic content for encoding
    pub content: &'static str,
    /// Confidence level (1.0 = absolute certainty)
    pub confidence: f32,
}

/// Static domain knowledge registry
pub struct DomainKnowledge;

impl DomainKnowledge {
    /// Get all initial seeding entries.
    ///
    /// These form the epistemic baseline - concepts the system knows *a priori*.
    pub fn get_initial_seeding() -> Vec<KnowledgeEntry> {
        vec![
            // =================================================================
            // LOGIC & MATHEMATICS (Universal truths)
            // =================================================================
            KnowledgeEntry {
                label: "logic_basic",
                category: "logic",
                content: "true false boolean binary logic gate and or not xor nand if then else",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "math_arithmetic",
                category: "math",
                content: "addition subtraction multiplication division plus minus times divide equals sum product difference quotient",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "math_numbers",
                category: "math",
                content: "zero one two three four five six seven eight nine ten hundred thousand million number integer float decimal",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "math_operations",
                category: "math",
                content: "calculate compute solve equation formula result answer total count",
                confidence: 1.0,
            },

            // =================================================================
            // SYSTEM ADMINISTRATION (NixOS Domain)
            // =================================================================
            KnowledgeEntry {
                label: "system_core",
                category: "system",
                content: "kernel linux boot process daemon service systemd init startup shutdown restart",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "nixos_fundamentals",
                category: "nixos",
                content: "nix nixos flake derivation configuration modules packages options nixpkgs store generation rebuild switch",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "nixos_services",
                category: "nixos",
                content: "services enable systemd unit socket timer nginx postgresql sshd networking firewall",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "dev_tools",
                category: "system",
                content: "rust cargo compiler build test debug git version control repository commit branch merge",
                confidence: 1.0,
            },

            // =================================================================
            // SELF-KNOWLEDGE (Identity & Capabilities)
            // =================================================================
            KnowledgeEntry {
                label: "identity_self",
                category: "self",
                content: "symthaea assistant ai mind consciousness swarm hdc hyperdimensional computing ltc liquid time constant",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "capabilities",
                category: "self",
                content: "think reason generate translate process analyze understand compute infer deduce",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "limitations",
                category: "self",
                content: "hallucination unknown uncertainty probability confidence limit boundary cannot unable unsure",
                confidence: 1.0,
            },

            // =================================================================
            // CONVERSATION (Social Patterns)
            // =================================================================
            KnowledgeEntry {
                label: "greeting",
                category: "social",
                content: "hello hi greetings welcome hey there good morning afternoon evening howdy",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "farewell",
                category: "social",
                content: "goodbye bye farewell see you later take care closing end finish done",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "affirmation",
                category: "social",
                content: "yes correct right agree confirm affirmative okay sure absolutely certainly",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "negation",
                category: "social",
                content: "no incorrect wrong disagree deny negative nope never not",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "gratitude",
                category: "social",
                content: "thank thanks grateful appreciate thankful acknowledgment recognition",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "request",
                category: "social",
                content: "please help assist could would can you need want request ask",
                confidence: 1.0,
            },

            // =================================================================
            // EPISTEMICS (Knowledge about knowledge)
            // =================================================================
            KnowledgeEntry {
                label: "certainty_markers",
                category: "epistemic",
                content: "certain sure definite absolute fact proven verified confirmed true known",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "uncertainty_markers",
                category: "epistemic",
                content: "uncertain unsure maybe perhaps possibly might could probably likely unlikely doubt",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "knowledge_verbs",
                category: "epistemic",
                content: "know understand believe think assume suppose guess estimate infer conclude",
                confidence: 1.0,
            },

            // =================================================================
            // COMMON FACTUAL DOMAINS (High confidence general knowledge)
            // =================================================================
            KnowledgeEntry {
                label: "geography_basics",
                category: "knowledge",
                content: "country city capital nation state region continent ocean earth world map location place",
                confidence: 0.9, // Slightly lower - facts can change
            },
            KnowledgeEntry {
                label: "time_concepts",
                category: "knowledge",
                content: "time date year month week day hour minute second past present future before after now then",
                confidence: 1.0,
            },
            KnowledgeEntry {
                label: "common_objects",
                category: "knowledge",
                content: "computer phone screen keyboard mouse file folder document text image video audio",
                confidence: 1.0,
            },
        ]
    }

    /// Get entries by category
    pub fn get_by_category(category: &str) -> Vec<KnowledgeEntry> {
        Self::get_initial_seeding()
            .into_iter()
            .filter(|e| e.category == category)
            .collect()
    }

    /// Get all category names
    pub fn categories() -> Vec<&'static str> {
        vec!["logic", "math", "system", "nixos", "self", "social", "epistemic", "knowledge"]
    }
}

/// Result of seeding operation
#[derive(Debug, Clone)]
pub struct SeedingResult {
    /// Number of prototypes seeded
    pub prototypes_seeded: usize,
    /// Categories covered
    pub categories: Vec<String>,
    /// Average encoding magnitude (sanity check)
    pub avg_magnitude: f32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_knowledge_base_not_empty() {
        let entries = DomainKnowledge::get_initial_seeding();
        assert!(!entries.is_empty(), "Knowledge base should not be empty");
        println!("Knowledge base has {} entries", entries.len());
    }

    #[test]
    fn test_all_categories_have_entries() {
        for category in DomainKnowledge::categories() {
            let entries = DomainKnowledge::get_by_category(category);
            assert!(!entries.is_empty(), "Category '{}' should have entries", category);
            println!("Category '{}': {} entries", category, entries.len());
        }
    }

    #[test]
    fn test_confidence_bounds() {
        for entry in DomainKnowledge::get_initial_seeding() {
            assert!(
                entry.confidence >= 0.0 && entry.confidence <= 1.0,
                "Entry '{}' has invalid confidence: {}",
                entry.label, entry.confidence
            );
        }
    }
}
