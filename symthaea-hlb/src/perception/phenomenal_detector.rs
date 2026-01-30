//! Phenomenal Content Detector
//!
//! A practical tool for detecting phenomenal content in text using the
//! phenomenal corridor findings. Uses Layer 22 topological unity as the
//! primary signal.
//!
//! ## Usage
//!
//! ```rust
//! use symthaea::perception::PhenomenalDetector;
//!
//! let detector = PhenomenalDetector::new()?;
//! let score = detector.score("The redness of a sunset");
//! println!("Phenomenality: {:.2}", score);  // Higher = more phenomenal
//! ```

use anyhow::Result;

#[cfg(feature = "neural-bridge")]
use crate::perception::{LayerExtractor, PoolingMethod, layer_extractor::LayerExtractorConfig};

#[cfg(feature = "neural-bridge")]
use symthaea_core::hdc::{HDC_DIMENSION, binary_hv::HV16};

#[cfg(feature = "neural-bridge")]
use symthaea_core::hdc::consciousness_topology::{ConsciousnessTopology, TopologyConfig};

/// Phenomenal content detector using Layer 22 topological analysis
#[cfg(feature = "neural-bridge")]
pub struct PhenomenalDetector {
    extractor: LayerExtractor,
    topology_config: TopologyConfig,
    /// Calibration: mean unity for phenomenal concepts
    phen_baseline: f64,
    /// Calibration: mean unity for functional concepts
    func_baseline: f64,
}

#[cfg(feature = "neural-bridge")]
impl PhenomenalDetector {
    /// Create a new phenomenal detector with default calibration
    pub fn new() -> Result<Self> {
        let config = LayerExtractorConfig {
            pooling: PoolingMethod::Mean,
            ..Default::default()
        };
        let extractor = LayerExtractor::load(config)?;

        let topology_config = TopologyConfig {
            min_persistence: 0.1,
            max_scale: 1.0,
            num_scales: 10,
            detect_cycles: true,
            detect_voids: false,
        };

        Ok(Self {
            extractor,
            topology_config,
            // Calibration values from experiments
            phen_baseline: 0.889,  // From fine-grained corridor analysis
            func_baseline: 0.725,
        })
    }

    /// Create detector with custom calibration
    pub fn with_calibration(phen_baseline: f64, func_baseline: f64) -> Result<Self> {
        let mut detector = Self::new()?;
        detector.phen_baseline = phen_baseline;
        detector.func_baseline = func_baseline;
        Ok(detector)
    }

    /// Score a text for phenomenal content
    ///
    /// Returns a value from 0.0 to 1.0:
    /// - 0.0 = clearly functional
    /// - 0.5 = ambiguous
    /// - 1.0 = clearly phenomenal
    pub fn score(&self, text: &str) -> Result<f64> {
        let unity = self.compute_unity(text)?;

        // Linear interpolation between baselines
        let range = self.phen_baseline - self.func_baseline;
        if range.abs() < 0.001 {
            return Ok(0.5);
        }

        let raw_score = (unity - self.func_baseline) / range;
        Ok(raw_score.clamp(0.0, 1.0))
    }

    /// Get raw unity score for a text
    pub fn compute_unity(&self, text: &str) -> Result<f64> {
        // Extract Layer 22 activations
        let acts = self.extractor.extract_layers(text, &[22])?;
        let hv = self.activation_to_hv16(&acts[0].activation);

        // Compute topology
        let mut topology = ConsciousnessTopology::new(self.topology_config.clone());
        topology.add_state(hv);
        for shift in 1..5 {
            topology.add_state(hv.permute(shift * 100));
        }

        let assessment = topology.analyze(0.5);
        Ok(assessment.unity_score)
    }

    /// Classify text as phenomenal or functional
    pub fn classify(&self, text: &str) -> Result<PhenomenalClassification> {
        let score = self.score(text)?;
        let unity = self.compute_unity(text)?;

        let label = if score > 0.65 {
            ClassLabel::Phenomenal
        } else if score < 0.35 {
            ClassLabel::Functional
        } else {
            ClassLabel::Ambiguous
        };

        Ok(PhenomenalClassification {
            label,
            score,
            unity,
            confidence: (score - 0.5).abs() * 2.0,
        })
    }

    /// Batch score multiple texts
    pub fn score_batch(&self, texts: &[&str]) -> Result<Vec<f64>> {
        texts.iter().map(|t| self.score(t)).collect()
    }

    /// Analyze a document and identify phenomenal passages
    pub fn analyze_document(&self, text: &str) -> Result<DocumentAnalysis> {
        // Split into sentences (simple split)
        let sentences: Vec<&str> = text.split(|c| c == '.' || c == '!' || c == '?')
            .map(|s| s.trim())
            .filter(|s| !s.is_empty())
            .collect();

        let mut passage_scores: Vec<(String, f64)> = Vec::new();
        let mut total_score = 0.0;

        for sentence in &sentences {
            let score = self.score(sentence)?;
            passage_scores.push((sentence.to_string(), score));
            total_score += score;
        }

        let mean_score = if sentences.is_empty() { 0.5 } else { total_score / sentences.len() as f64 };

        // Find most phenomenal passages
        let mut sorted = passage_scores.clone();
        sorted.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        let top_phenomenal: Vec<_> = sorted.into_iter().take(3).collect();

        Ok(DocumentAnalysis {
            overall_score: mean_score,
            passage_scores,
            top_phenomenal_passages: top_phenomenal,
            phenomenal_ratio: passage_scores.iter().filter(|(_, s)| *s > 0.6).count() as f64
                             / passage_scores.len().max(1) as f64,
        })
    }

    fn activation_to_hv16(&self, activation: &[f32]) -> HV16 {
        let mut expanded = Vec::with_capacity(HDC_DIMENSION);
        let tiles = HDC_DIMENSION / activation.len();
        let remainder = HDC_DIMENSION % activation.len();

        for tile in 0..tiles {
            for (i, &val) in activation.iter().enumerate() {
                let perturbation = ((tile * activation.len() + i) as f32 * 0.001).sin() * 0.01;
                expanded.push(val + perturbation);
            }
        }

        for i in 0..remainder {
            expanded.push(activation[i]);
        }

        HV16::from_bipolar(&expanded)
    }
}

/// Classification result
#[derive(Debug, Clone)]
pub struct PhenomenalClassification {
    pub label: ClassLabel,
    pub score: f64,
    pub unity: f64,
    pub confidence: f64,
}

/// Classification labels
#[derive(Debug, Clone, PartialEq)]
pub enum ClassLabel {
    Phenomenal,
    Functional,
    Ambiguous,
}

/// Document analysis result
#[derive(Debug, Clone)]
pub struct DocumentAnalysis {
    pub overall_score: f64,
    pub passage_scores: Vec<(String, f64)>,
    pub top_phenomenal_passages: Vec<(String, f64)>,
    pub phenomenal_ratio: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[ignore] // Requires model loading
    fn test_detector_creation() {
        let detector = PhenomenalDetector::new();
        assert!(detector.is_ok());
    }

    #[test]
    #[ignore] // Requires model loading
    fn test_phenomenal_scoring() {
        let detector = PhenomenalDetector::new().unwrap();

        // Clearly phenomenal
        let phen_score = detector.score("The vivid redness of the sunset filled my awareness").unwrap();

        // Clearly functional
        let func_score = detector.score("The recursive algorithm terminates in O(n log n) time").unwrap();

        // Phenomenal should score higher
        assert!(phen_score > func_score, "Phenomenal: {}, Functional: {}", phen_score, func_score);
    }
}
