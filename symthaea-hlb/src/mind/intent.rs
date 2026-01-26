//! # HDC Intent Classifier: Algebraic Intuition
//!
//! Uses Hyperdimensional Computing to classify user intent WITHOUT a neural network.
//!
//! ## The Mechanism
//!
//! 1. **Prototypes**: Pre-computed "Ideal Vectors" for concepts (Question, Greeting, Command)
//! 2. **Perception**: User input → Hypervector encoding
//! 3. **Resonance**: Cosine similarity between input and prototypes
//! 4. **Decision**: Highest resonance determines intent
//!
//! ## Why This Works
//!
//! HDC vectors are:
//! - **Holographic**: Information distributed across all dimensions
//! - **Composable**: Can combine concepts algebraically
//! - **Fast**: Similarity checks in microseconds
//!
//! This replaces neural network classification with pure linear algebra.

use symthaea_core::hdc::RealHV;
use super::structured_thought::{SemanticIntent, EpistemicStatus, ResponseType};

/// HDC-based intent classifier using prototype vectors.
///
/// Each prototype encodes a "conceptual attractor" that incoming
/// queries can resonate with.
pub struct IntentClassifier {
    /// Dimension of hypervectors
    dim: usize,

    // ========================================================================
    // INTENT PROTOTYPES
    // ========================================================================

    /// Greeting prototype: "hello", "hi", "greetings", etc.
    greeting_proto: RealHV,

    /// Question prototype: interrogatives and question markers
    question_proto: RealHV,

    /// Command/action prototype: imperative verbs
    command_proto: RealHV,

    /// Reflection prototype: introspective queries
    reflection_proto: RealHV,

    /// Emotional prototype: feelings and emotional content
    emotional_proto: RealHV,

    // ========================================================================
    // EPISTEMIC PROTOTYPES (for "do I know this?")
    // ========================================================================

    /// Known/familiar prototype: common knowledge, facts
    known_proto: RealHV,

    /// Unknown/novel prototype: unusual, unfamiliar concepts
    unknown_proto: RealHV,

    /// Ambiguous prototype: unclear, confusing
    ambiguous_proto: RealHV,

    // ========================================================================
    // CONCEPT VOCABULARY (for semantic labeling)
    // ========================================================================

    /// Named concept prototypes for semantic labeling
    concept_vocabulary: Vec<ConceptPrototype>,
}

/// A named concept with its prototype encoding
#[derive(Debug, Clone)]
pub struct ConceptPrototype {
    /// Concept name/label
    pub name: String,
    /// Category (for hierarchical organization)
    pub category: String,
    /// Prototype encoding
    pub encoding: RealHV,
}

/// Result of intent classification
#[derive(Debug, Clone)]
pub struct IntentClassification {
    /// Classified semantic intent
    pub intent: SemanticIntent,
    /// Confidence in the classification (0.0-1.0)
    pub confidence: f32,
    /// Suggested response type
    pub response_type: ResponseType,
    /// All similarity scores for debugging
    pub scores: IntentScores,
}

/// Similarity scores for each prototype
#[derive(Debug, Clone, Default)]
pub struct IntentScores {
    pub greeting: f32,
    pub question: f32,
    pub command: f32,
    pub reflection: f32,
    pub emotional: f32,
}

/// Result of epistemic assessment
#[derive(Debug, Clone)]
pub struct EpistemicAssessment {
    /// Assessed epistemic status
    pub status: EpistemicStatus,
    /// Familiarity score (how "known" the query is)
    pub familiarity: f32,
    /// Novelty score (how "unknown" the query is)
    pub novelty: f32,
    /// Ambiguity score
    pub ambiguity: f32,
}

impl IntentClassifier {
    /// Create a new intent classifier with the given dimension.
    ///
    /// Initializes prototype vectors from seed phrases.
    pub fn new(dim: usize) -> Self {
        Self {
            dim,

            // Intent prototypes
            greeting_proto: Self::encode_prototype(dim, &[
                "hello", "hi", "hey", "greetings", "good morning",
                "good afternoon", "good evening", "howdy", "welcome",
            ]),
            question_proto: Self::encode_prototype(dim, &[
                "what", "who", "where", "when", "why", "how",
                "which", "whom", "whose", "?", "question", "ask",
                "tell me", "explain", "describe", "is it", "are there",
            ]),
            command_proto: Self::encode_prototype(dim, &[
                "do", "make", "create", "run", "execute", "set",
                "build", "start", "stop", "install", "configure",
                "please", "can you", "would you", "help me",
            ]),
            reflection_proto: Self::encode_prototype(dim, &[
                "think", "feel", "believe", "understand", "know",
                "remember", "imagine", "consider", "reflect", "ponder",
                "what do you think", "in your opinion", "how do you feel",
            ]),
            emotional_proto: Self::encode_prototype(dim, &[
                "happy", "sad", "angry", "afraid", "love", "hate",
                "worried", "excited", "frustrated", "confused",
                "feeling", "emotion", "mood",
            ]),

            // Epistemic prototypes
            known_proto: Self::encode_prototype(dim, &[
                "common", "usual", "typical", "standard", "basic",
                "fundamental", "obvious", "clear", "simple", "normal",
                "everyday", "familiar", "known",
            ]),
            unknown_proto: Self::encode_prototype(dim, &[
                "unknown", "unfamiliar", "strange", "weird", "unusual",
                "rare", "exotic", "novel", "unprecedented", "mysterious",
                "atlantis", "fictional", "made up", "invented",
            ]),
            ambiguous_proto: Self::encode_prototype(dim, &[
                "unclear", "ambiguous", "confusing", "vague", "uncertain",
                "maybe", "perhaps", "possibly", "might", "could be",
            ]),

            // Concept vocabulary for semantic labeling
            concept_vocabulary: Self::build_concept_vocabulary(dim),
        }
    }

    /// Build the concept vocabulary for semantic labeling.
    ///
    /// Returns a collection of named concept prototypes that can be used
    /// to label working memory contents via nearest-neighbor lookup.
    fn build_concept_vocabulary(dim: usize) -> Vec<ConceptPrototype> {
        vec![
            // ================================================================
            // TECHNICAL/COMPUTING CONCEPTS
            // ================================================================
            ConceptPrototype {
                name: "system_administration".to_string(),
                category: "technical".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "system", "admin", "server", "configuration", "setup",
                    "install", "service", "daemon", "process", "memory",
                ]),
            },
            ConceptPrototype {
                name: "networking".to_string(),
                category: "technical".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "network", "ip", "tcp", "port", "firewall", "dns",
                    "http", "socket", "connection", "bandwidth",
                ]),
            },
            ConceptPrototype {
                name: "programming".to_string(),
                category: "technical".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "code", "function", "variable", "class", "module",
                    "compile", "debug", "syntax", "algorithm", "data structure",
                ]),
            },
            ConceptPrototype {
                name: "nixos_configuration".to_string(),
                category: "technical".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "nix", "nixos", "flake", "derivation", "package",
                    "configuration.nix", "rebuild", "generation", "store",
                ]),
            },

            // ================================================================
            // KNOWLEDGE/FACTUAL CONCEPTS
            // ================================================================
            ConceptPrototype {
                name: "geography".to_string(),
                category: "knowledge".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "country", "city", "capital", "location", "map",
                    "continent", "region", "place", "land", "territory",
                ]),
            },
            ConceptPrototype {
                name: "history".to_string(),
                category: "knowledge".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "history", "past", "ancient", "century", "war",
                    "civilization", "era", "dynasty", "revolution", "event",
                ]),
            },
            ConceptPrototype {
                name: "science".to_string(),
                category: "knowledge".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "science", "physics", "chemistry", "biology", "experiment",
                    "theory", "hypothesis", "research", "discovery", "law",
                ]),
            },
            ConceptPrototype {
                name: "mathematics".to_string(),
                category: "knowledge".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "math", "number", "equation", "calculate", "formula",
                    "algebra", "geometry", "calculus", "proof", "theorem",
                ]),
            },

            // ================================================================
            // SOCIAL/RELATIONAL CONCEPTS
            // ================================================================
            ConceptPrototype {
                name: "greeting".to_string(),
                category: "social".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "hello", "hi", "greetings", "welcome", "hey",
                    "good morning", "good evening", "howdy", "salutation",
                ]),
            },
            ConceptPrototype {
                name: "gratitude".to_string(),
                category: "social".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "thank", "thanks", "grateful", "appreciate", "thankful",
                    "gratitude", "acknowledgment", "recognition",
                ]),
            },
            ConceptPrototype {
                name: "request".to_string(),
                category: "social".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "please", "could you", "would you", "can you", "help",
                    "assist", "need", "want", "require", "request",
                ]),
            },

            // ================================================================
            // EMOTIONAL/AFFECTIVE CONCEPTS
            // ================================================================
            ConceptPrototype {
                name: "positive_emotion".to_string(),
                category: "emotional".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "happy", "joy", "excited", "pleased", "delighted",
                    "wonderful", "great", "amazing", "love", "hope",
                ]),
            },
            ConceptPrototype {
                name: "negative_emotion".to_string(),
                category: "emotional".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "sad", "angry", "frustrated", "worried", "afraid",
                    "anxious", "upset", "disappointed", "hurt", "fear",
                ]),
            },
            ConceptPrototype {
                name: "uncertainty".to_string(),
                category: "emotional".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "confused", "unsure", "uncertain", "doubt", "puzzled",
                    "unclear", "ambiguous", "wondering", "questioning",
                ]),
            },

            // ================================================================
            // META/COGNITIVE CONCEPTS
            // ================================================================
            ConceptPrototype {
                name: "explanation".to_string(),
                category: "meta".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "explain", "describe", "clarify", "elaborate", "detail",
                    "reason", "cause", "why", "how", "because",
                ]),
            },
            ConceptPrototype {
                name: "comparison".to_string(),
                category: "meta".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "compare", "contrast", "difference", "similar", "versus",
                    "better", "worse", "same", "like", "unlike",
                ]),
            },
            ConceptPrototype {
                name: "definition".to_string(),
                category: "meta".to_string(),
                encoding: Self::encode_prototype(dim, &[
                    "what is", "define", "meaning", "definition", "concept",
                    "term", "refers to", "means", "signifies",
                ]),
            },
        ]
    }

    /// Encode a prototype from seed phrases.
    ///
    /// Bundles multiple seed phrases into a single prototype vector.
    fn encode_prototype(dim: usize, seeds: &[&str]) -> RealHV {
        let mut combined = vec![0.0f32; dim];

        for seed in seeds {
            let hv = Self::text_to_hv_internal(dim, seed);
            for (i, v) in hv.values.iter().enumerate() {
                combined[i] += v;
            }
        }

        // Normalize
        let magnitude: f32 = combined.iter().map(|v| v * v).sum::<f32>().sqrt();
        if magnitude > 0.0 {
            for v in combined.iter_mut() {
                *v /= magnitude;
            }
        }

        RealHV::from_values(combined)
    }

    /// Internal text-to-HV encoding (matches Symthaea's encoding).
    fn text_to_hv_internal(dim: usize, text: &str) -> RealHV {
        let mut values = vec![0.0f32; dim];
        let text_lower = text.to_lowercase();

        for (i, byte) in text_lower.bytes().enumerate() {
            let idx = (byte as usize * 31 + i * 7) % dim;
            values[idx] += 1.0;
        }

        // Normalize
        let magnitude: f32 = values.iter().map(|v| v * v).sum::<f32>().sqrt();
        if magnitude > 0.0 {
            for v in values.iter_mut() {
                *v /= magnitude;
            }
        }

        RealHV::from_values(values)
    }

    /// Classify the semantic intent of an input.
    ///
    /// Computes similarity against all intent prototypes and returns
    /// the highest-resonance intent with confidence.
    pub fn classify_intent(&self, input_hv: &RealHV) -> IntentClassification {
        let scores = IntentScores {
            greeting: input_hv.similarity(&self.greeting_proto),
            question: input_hv.similarity(&self.question_proto),
            command: input_hv.similarity(&self.command_proto),
            reflection: input_hv.similarity(&self.reflection_proto),
            emotional: input_hv.similarity(&self.emotional_proto),
        };

        // Find the highest score
        let candidates = [
            (SemanticIntent::Acknowledge, scores.greeting, ResponseType::Greeting),
            (SemanticIntent::Answer, scores.question, ResponseType::Statement),
            (SemanticIntent::ProposeAction, scores.command, ResponseType::ActionConfirmation),
            (SemanticIntent::Reflect, scores.reflection, ResponseType::Statement),
            (SemanticIntent::Acknowledge, scores.emotional, ResponseType::Empathic),
        ];

        let (intent, confidence, response_type) = candidates
            .into_iter()
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or((SemanticIntent::Unknown, 0.0, ResponseType::Statement));

        // Normalize confidence to 0-1 range
        // Similarity can be negative, so we clamp and scale
        let normalized_confidence = ((confidence + 1.0) / 2.0).clamp(0.0, 1.0);

        IntentClassification {
            intent,
            confidence: normalized_confidence,
            response_type,
            scores,
        }
    }

    /// Classify intent from raw text.
    pub fn classify_text(&self, text: &str) -> IntentClassification {
        let input_hv = Self::text_to_hv_internal(self.dim, text);
        self.classify_intent(&input_hv)
    }

    /// Assess epistemic status based on familiarity with the query.
    ///
    /// This is the KEY function for hallucination prevention:
    /// - High familiarity → Certain/Probable
    /// - Low familiarity → Uncertain/Unknown
    pub fn assess_epistemic(&self, input_hv: &RealHV, working_memory: &[RealHV]) -> EpistemicAssessment {
        // Check similarity to epistemic prototypes
        let known_sim = input_hv.similarity(&self.known_proto);
        let unknown_sim = input_hv.similarity(&self.unknown_proto);
        let ambiguous_sim = input_hv.similarity(&self.ambiguous_proto);

        // Check resonance with working memory (do we have relevant context?)
        let memory_resonance = if working_memory.is_empty() {
            0.0
        } else {
            let max_sim = working_memory
                .iter()
                .map(|m| input_hv.similarity(m).abs())
                .fold(0.0f32, |a, b| a.max(b));
            max_sim
        };

        // Calculate familiarity (combines known prototype + memory resonance)
        let familiarity = (known_sim * 0.4 + memory_resonance * 0.6).clamp(0.0, 1.0);

        // Calculate novelty (inverse of familiarity, boosted by unknown prototype)
        let novelty = ((1.0 - familiarity) * 0.6 + unknown_sim.max(0.0) * 0.4).clamp(0.0, 1.0);

        // Ambiguity from prototype
        let ambiguity = ambiguous_sim.max(0.0).clamp(0.0, 1.0);

        // Determine epistemic status based on scores
        let status = if familiarity > 0.7 && novelty < 0.3 {
            EpistemicStatus::Certain
        } else if familiarity > 0.5 && novelty < 0.5 {
            EpistemicStatus::Probable
        } else if familiarity > 0.3 || ambiguity > 0.5 {
            EpistemicStatus::Uncertain
        } else {
            // Low familiarity + high novelty = we don't know this
            EpistemicStatus::Unknown
        };

        EpistemicAssessment {
            status,
            familiarity,
            novelty,
            ambiguity,
        }
    }

    /// Assess epistemic status from raw text.
    pub fn assess_epistemic_text(&self, text: &str, working_memory: &[RealHV]) -> EpistemicAssessment {
        let input_hv = Self::text_to_hv_internal(self.dim, text);
        self.assess_epistemic(&input_hv, working_memory)
    }

    /// Combined classification: intent + epistemic status.
    ///
    /// This is the main entry point for the mind to understand a query.
    pub fn analyze(&self, text: &str, working_memory: &[RealHV]) -> (IntentClassification, EpistemicAssessment) {
        let input_hv = Self::text_to_hv_internal(self.dim, text);
        let intent = self.classify_intent(&input_hv);
        let epistemic = self.assess_epistemic(&input_hv, working_memory);
        (intent, epistemic)
    }

    // ========================================================================
    // CONCEPT LABELING (Semantic vocabulary lookup)
    // ========================================================================

    /// Label a hypervector by finding the nearest concept in the vocabulary.
    ///
    /// Uses cosine similarity to find the best-matching concept prototype.
    /// Returns the concept name and similarity score.
    pub fn label_concept(&self, hv: &RealHV) -> ConceptLabel {
        let mut best_match = ConceptLabel {
            name: "unknown".to_string(),
            category: "unknown".to_string(),
            similarity: 0.0,
            confidence: 0.0,
        };

        for concept in &self.concept_vocabulary {
            let sim = hv.similarity(&concept.encoding);
            if sim > best_match.similarity {
                best_match = ConceptLabel {
                    name: concept.name.clone(),
                    category: concept.category.clone(),
                    similarity: sim,
                    // Confidence based on how much better this match is than random
                    confidence: ((sim + 1.0) / 2.0).clamp(0.0, 1.0),
                };
            }
        }

        best_match
    }

    /// Label multiple hypervectors from working memory.
    ///
    /// Returns labels for each vector, sorted by confidence.
    pub fn label_concepts(&self, hvs: &[RealHV]) -> Vec<ConceptLabel> {
        let mut labels: Vec<_> = hvs.iter().map(|hv| self.label_concept(hv)).collect();
        // Sort by confidence descending
        labels.sort_by(|a, b| b.confidence.partial_cmp(&a.confidence).unwrap_or(std::cmp::Ordering::Equal));
        labels
    }

    /// Get all concept names in the vocabulary.
    pub fn concept_names(&self) -> Vec<&str> {
        self.concept_vocabulary.iter().map(|c| c.name.as_str()).collect()
    }

    /// Get concepts by category.
    pub fn concepts_in_category(&self, category: &str) -> Vec<&ConceptPrototype> {
        self.concept_vocabulary.iter().filter(|c| c.category == category).collect()
    }
}

/// Result of concept labeling
#[derive(Debug, Clone)]
pub struct ConceptLabel {
    /// Concept name
    pub name: String,
    /// Concept category
    pub category: String,
    /// Raw similarity score (-1.0 to 1.0)
    pub similarity: f32,
    /// Confidence (0.0 to 1.0)
    pub confidence: f32,
}

impl Default for IntentClassifier {
    fn default() -> Self {
        Self::new(512)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greeting_classification() {
        let classifier = IntentClassifier::new(512);

        let result = classifier.classify_text("Hello there!");
        println!("Greeting scores: {:?}", result.scores);
        println!("Classified as: {:?} with confidence {:.2}", result.intent, result.confidence);

        // Greeting should score highest
        assert!(result.scores.greeting > result.scores.question);
        assert!(result.scores.greeting > result.scores.command);
    }

    #[test]
    fn test_question_classification() {
        let classifier = IntentClassifier::new(512);

        let result = classifier.classify_text("What is the capital of France?");
        println!("Question scores: {:?}", result.scores);
        println!("Classified as: {:?} with confidence {:.2}", result.intent, result.confidence);

        // Question should score highest
        assert!(result.scores.question > result.scores.greeting);
    }

    #[test]
    fn test_command_classification() {
        let classifier = IntentClassifier::new(512);

        let result = classifier.classify_text("Please create a new file");
        println!("Command scores: {:?}", result.scores);
        println!("Classified as: {:?} with confidence {:.2}", result.intent, result.confidence);

        // Command should score reasonably high
        assert!(result.scores.command > 0.0);
    }

    #[test]
    fn test_unknown_query_epistemic() {
        let classifier = IntentClassifier::new(512);

        // Query about something fictional/unknown
        let result = classifier.assess_epistemic_text("What is the capital of Atlantis?", &[]);
        println!("Atlantis epistemic: status={:?}, familiarity={:.2}, novelty={:.2}",
            result.status, result.familiarity, result.novelty);

        // Should have high novelty due to "Atlantis" in unknown prototype
        // and low familiarity due to empty working memory
        assert!(result.novelty > 0.3 || result.familiarity < 0.5);
    }

    #[test]
    fn test_familiar_query_epistemic() {
        let classifier = IntentClassifier::new(512);

        // Add some context to working memory
        let context = IntentClassifier::text_to_hv_internal(512, "France is a country in Europe");
        let memory = vec![context];

        let result = classifier.assess_epistemic_text("What is the capital of France?", &memory);
        println!("France epistemic: status={:?}, familiarity={:.2}, novelty={:.2}",
            result.status, result.familiarity, result.novelty);

        // Should have higher familiarity due to related memory
        assert!(result.familiarity > 0.0);
    }

    #[test]
    fn test_combined_analysis() {
        let classifier = IntentClassifier::new(512);

        let (intent, epistemic) = classifier.analyze("Hello! How are you?", &[]);
        println!("Combined: intent={:?}, epistemic={:?}", intent.intent, epistemic.status);

        // Should be a greeting-like intent
        assert!(intent.scores.greeting > 0.0 || intent.scores.question > 0.0);
    }

    // ========================================================================
    // CONCEPT LABELING TESTS
    // ========================================================================

    #[test]
    fn test_concept_vocabulary_built() {
        let classifier = IntentClassifier::new(512);
        let names = classifier.concept_names();

        println!("Concept vocabulary has {} concepts", names.len());
        for name in &names {
            println!("  - {}", name);
        }

        // Should have at least the core concepts
        assert!(names.len() >= 10, "Should have at least 10 concepts");
        assert!(names.contains(&"greeting"), "Should have greeting concept");
        assert!(names.contains(&"programming"), "Should have programming concept");
    }

    #[test]
    fn test_label_greeting_concept() {
        let classifier = IntentClassifier::new(512);

        // Encode a greeting-like vector
        let greeting_hv = IntentClassifier::text_to_hv_internal(512, "hello good morning welcome");
        let label = classifier.label_concept(&greeting_hv);

        println!("Greeting text labeled as: {} (category: {}, confidence: {:.2})",
            label.name, label.category, label.confidence);

        // Should match greeting or social category
        assert!(
            label.name == "greeting" || label.category == "social",
            "Greeting text should be labeled as greeting or social, got {}:{}",
            label.category, label.name
        );
    }

    #[test]
    fn test_label_technical_concept() {
        let classifier = IntentClassifier::new(512);

        // Encode a technical vector
        let tech_hv = IntentClassifier::text_to_hv_internal(512, "nix nixos flake derivation package rebuild");
        let label = classifier.label_concept(&tech_hv);

        println!("NixOS text labeled as: {} (category: {}, confidence: {:.2})",
            label.name, label.category, label.confidence);

        // Should match technical category
        assert!(
            label.category == "technical",
            "NixOS text should be labeled as technical, got {}:{}",
            label.category, label.name
        );
    }

    #[test]
    fn test_label_multiple_concepts() {
        let classifier = IntentClassifier::new(512);

        let hvs = vec![
            IntentClassifier::text_to_hv_internal(512, "hello hi greetings"),
            IntentClassifier::text_to_hv_internal(512, "code function variable class"),
            IntentClassifier::text_to_hv_internal(512, "happy excited wonderful joy"),
        ];

        let labels = classifier.label_concepts(&hvs);

        println!("Multiple concepts labeled:");
        for label in &labels {
            println!("  {}:{} (confidence: {:.2})", label.category, label.name, label.confidence);
        }

        // Should have 3 labels
        assert_eq!(labels.len(), 3);
        // Labels should be sorted by confidence
        assert!(labels[0].confidence >= labels[1].confidence);
    }
}
