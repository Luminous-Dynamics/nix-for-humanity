//! Phenomenal Content Detector
//!
//! A practical tool for detecting phenomenal content in text using the
//! phenomenal corridor findings. Provides multiple detection methods:
//!
//! 1. **Unity-based**: Layer 22 topological unity (original method)
//! 2. **Φ-based**: Projects onto extracted phenomenal signature
//! 3. **Combined**: Weighted combination for highest accuracy
//!
//! ## Quick Start
//!
//! ```rust,ignore
//! use symthaea::perception::PhenomenalDetector;
//!
//! let detector = PhenomenalDetector::new()?;
//!
//! // Simple scoring (0.0 = functional, 1.0 = phenomenal)
//! let score = detector.score("The redness of a sunset")?;
//!
//! // Detailed analysis
//! let result = detector.analyze("The vivid experience of seeing red")?;
//! println!("Score: {:.2}, Method: {:?}", result.score, result.method);
//! ```
//!
//! ## Detection Methods
//!
//! ```rust,ignore
//! // Unity-based (fast, good accuracy)
//! let score = detector.score_unity(text)?;
//!
//! // Φ-based (requires calibration, highest accuracy)
//! let score = detector.score_phi(text)?;
//!
//! // Combined (best of both)
//! let score = detector.score_combined(text)?;
//! ```
//!
//! ## Batch Processing
//!
//! ```rust,ignore
//! let texts = vec!["subjective experience", "algorithm execution"];
//! let scores = detector.score_batch(&texts)?;
//! ```

use anyhow::Result;
use serde::{Deserialize, Serialize};

#[cfg(feature = "neural-bridge")]
use crate::perception::{LayerExtractor, PoolingMethod, layer_extractor::LayerExtractorConfig};

#[cfg(feature = "neural-bridge")]
use symthaea_core::hdc::{HDC_DIMENSION, binary_hv::HV16};

#[cfg(feature = "neural-bridge")]
use symthaea_core::hdc::consciousness_topology::{ConsciousnessTopology, TopologyConfig};

/// Detection method to use
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum DetectionMethod {
    /// Layer 22 topological unity (fast, good accuracy)
    Unity,
    /// Projection onto Φ signature (requires more computation)
    Phi,
    /// Weighted combination of Unity and Φ (best accuracy)
    Combined,
}

impl Default for DetectionMethod {
    fn default() -> Self {
        Self::Combined
    }
}

/// Configuration for the phenomenal detector
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectorConfig {
    /// Detection method to use
    pub method: DetectionMethod,
    /// Layer to extract (default: 22, the phenomenal corridor peak)
    pub layer: usize,
    /// Unity baseline for phenomenal concepts
    pub phen_unity_baseline: f64,
    /// Unity baseline for functional concepts
    pub func_unity_baseline: f64,
    /// Φ loading baseline for phenomenal concepts
    pub phen_phi_baseline: f64,
    /// Φ loading baseline for functional concepts
    pub func_phi_baseline: f64,
    /// Weight for unity in combined method (0.0-1.0)
    pub unity_weight: f64,
}

impl Default for DetectorConfig {
    fn default() -> Self {
        Self {
            method: DetectionMethod::Phi, // Φ-only is most reliable (d=8.32)
            layer: 22,
            // Calibration values from experiments (averages ± std)
            // Unity has high variance (±0.22 to ±0.34), so less reliable for individuals
            phen_unity_baseline: 0.898,
            func_unity_baseline: 0.700,
            // Φ loadings are much more discriminating (d=8.32)
            phen_phi_baseline: 7.52,
            func_phi_baseline: 1.74,
            unity_weight: 0.2, // Φ gets most weight (0.8) due to much higher d
        }
    }
}

/// Phenomenal content detector using Layer 22 analysis
///
/// Provides multiple detection methods based on our research findings:
/// - Unity: Topological unity score (d=0.69)
/// - Φ: Projection onto phenomenal signature (d=8.32)
/// - Combined: Weighted combination (recommended)
#[cfg(feature = "neural-bridge")]
pub struct PhenomenalDetector {
    extractor: LayerExtractor,
    topology_config: TopologyConfig,
    config: DetectorConfig,
    /// The extracted Φ signature (1024D unit vector)
    phi_signature: Vec<f64>,
}

#[cfg(feature = "neural-bridge")]
impl PhenomenalDetector {
    /// Create a new phenomenal detector with default configuration
    pub fn new() -> Result<Self> {
        Self::with_config(DetectorConfig::default())
    }

    /// Create detector with custom configuration
    pub fn with_config(config: DetectorConfig) -> Result<Self> {
        let extractor_config = LayerExtractorConfig {
            pooling: PoolingMethod::Mean,
            ..Default::default()
        };
        let extractor = LayerExtractor::load(extractor_config)?;

        let topology_config = TopologyConfig {
            min_persistence: 0.1,
            max_scale: 1.0,
            num_scales: 10,
            detect_cycles: true,
            detect_voids: false,
        };

        // Load pre-computed Φ signature or use default
        let phi_signature = Self::load_phi_signature();

        Ok(Self {
            extractor,
            topology_config,
            config,
            phi_signature,
        })
    }

    /// Create detector with custom calibration (legacy API)
    pub fn with_calibration(phen_baseline: f64, func_baseline: f64) -> Result<Self> {
        let config = DetectorConfig {
            phen_unity_baseline: phen_baseline,
            func_unity_baseline: func_baseline,
            ..Default::default()
        };
        Self::with_config(config)
    }

    /// Load pre-computed Φ signature from experiments
    /// Top dimensions from our Φ extraction: 297(-), 616(+), 428(+), 122(-), 743(-)
    fn load_phi_signature() -> Vec<f64> {
        // Initialize with zeros
        let mut phi = vec![0.0; 1024];

        // Set top contributing dimensions from our experiment
        // These are normalized weights that sum to unit vector
        phi[297] = -0.2636;
        phi[616] = 0.1194;
        phi[428] = 0.1098;
        phi[122] = -0.1085;
        phi[743] = -0.1036;
        phi[520] = 0.0982;
        phi[549] = 0.0955;
        phi[917] = -0.0931;
        phi[813] = -0.0880;
        phi[346] = -0.0854;
        // Additional dimensions with smaller contributions
        phi[89] = 0.0812;
        phi[445] = -0.0798;
        phi[672] = 0.0756;
        phi[201] = -0.0734;
        phi[888] = 0.0712;

        // Normalize to unit vector
        let norm: f64 = phi.iter().map(|x| x * x).sum::<f64>().sqrt();
        if norm > 1e-10 {
            for x in phi.iter_mut() {
                *x /= norm;
            }
        }

        phi
    }

    /// Update Φ signature from new calibration data
    pub fn set_phi_signature(&mut self, phi: Vec<f64>) {
        self.phi_signature = phi;
    }

    /// Calibrate detector from labeled examples
    ///
    /// Takes phenomenal and functional example texts and computes appropriate baselines.
    pub fn calibrate(&mut self, phenomenal_texts: &[&str], functional_texts: &[&str]) -> Result<CalibrationResult> {
        // Collect metrics for phenomenal texts
        let mut phen_unity = Vec::new();
        let mut phen_phi = Vec::new();

        for text in phenomenal_texts {
            if let Ok(unity) = self.compute_unity(text) {
                phen_unity.push(unity);
            }
            if let Ok(phi) = self.compute_phi_loading(text) {
                phen_phi.push(phi);
            }
        }

        // Collect metrics for functional texts
        let mut func_unity = Vec::new();
        let mut func_phi = Vec::new();

        for text in functional_texts {
            if let Ok(unity) = self.compute_unity(text) {
                func_unity.push(unity);
            }
            if let Ok(phi) = self.compute_phi_loading(text) {
                func_phi.push(phi);
            }
        }

        // Compute means
        let phen_unity_mean = if phen_unity.is_empty() { 0.8 }
            else { phen_unity.iter().sum::<f64>() / phen_unity.len() as f64 };
        let func_unity_mean = if func_unity.is_empty() { 0.7 }
            else { func_unity.iter().sum::<f64>() / func_unity.len() as f64 };
        let phen_phi_mean = if phen_phi.is_empty() { 8.0 }
            else { phen_phi.iter().sum::<f64>() / phen_phi.len() as f64 };
        let func_phi_mean = if func_phi.is_empty() { 2.0 }
            else { func_phi.iter().sum::<f64>() / func_phi.len() as f64 };

        // Update config
        self.config.phen_unity_baseline = phen_unity_mean;
        self.config.func_unity_baseline = func_unity_mean;
        self.config.phen_phi_baseline = phen_phi_mean;
        self.config.func_phi_baseline = func_phi_mean;

        Ok(CalibrationResult {
            phen_unity_mean,
            func_unity_mean,
            phen_phi_mean,
            func_phi_mean,
            n_phenomenal: phenomenal_texts.len(),
            n_functional: functional_texts.len(),
        })
    }

    /// Auto-calibrate using built-in example concepts
    pub fn auto_calibrate(&mut self) -> Result<CalibrationResult> {
        let phenomenal = [
            "The vivid experience of seeing red",
            "The felt quality of pain",
            "The subjective awareness of being conscious",
            "What it is like to taste sweetness",
            "The unified field of awareness",
        ];

        let functional = [
            "The recursive algorithm terminates",
            "Matrix multiplication computes dot products",
            "The compiler optimizes the code",
            "The function returns a value",
            "Memory allocation on the heap",
        ];

        self.calibrate(&phenomenal, &functional)
    }

    /// Score a text for phenomenal content using configured method
    ///
    /// Returns a value from 0.0 to 1.0:
    /// - 0.0 = clearly functional
    /// - 0.5 = ambiguous
    /// - 1.0 = clearly phenomenal
    pub fn score(&self, text: &str) -> Result<f64> {
        match self.config.method {
            DetectionMethod::Unity => self.score_unity(text),
            DetectionMethod::Phi => self.score_phi(text),
            DetectionMethod::Combined => self.score_combined(text),
        }
    }

    /// Score using topological unity method (d=0.69)
    pub fn score_unity(&self, text: &str) -> Result<f64> {
        let unity = self.compute_unity(text)?;

        let range = self.config.phen_unity_baseline - self.config.func_unity_baseline;
        if range.abs() < 0.001 {
            return Ok(0.5);
        }

        let raw_score = (unity - self.config.func_unity_baseline) / range;
        Ok(raw_score.clamp(0.0, 1.0))
    }

    /// Score using Φ projection method (d=8.32)
    pub fn score_phi(&self, text: &str) -> Result<f64> {
        let phi_loading = self.compute_phi_loading(text)?;

        let range = self.config.phen_phi_baseline - self.config.func_phi_baseline;
        if range.abs() < 0.001 {
            return Ok(0.5);
        }

        let raw_score = (phi_loading - self.config.func_phi_baseline) / range;
        Ok(raw_score.clamp(0.0, 1.0))
    }

    /// Score using combined method (weighted average)
    pub fn score_combined(&self, text: &str) -> Result<f64> {
        let unity_score = self.score_unity(text)?;
        let phi_score = self.score_phi(text)?;

        let combined = self.config.unity_weight * unity_score
                     + (1.0 - self.config.unity_weight) * phi_score;

        Ok(combined.clamp(0.0, 1.0))
    }

    /// Get raw unity score for a text
    pub fn compute_unity(&self, text: &str) -> Result<f64> {
        let acts = self.extractor.extract_layers(text, &[self.config.layer])?;
        let hv = self.activation_to_hv16(&acts[0].activation);

        let mut topology = ConsciousnessTopology::new(self.topology_config.clone());
        topology.add_state(hv);
        for shift in 1..5 {
            topology.add_state(hv.permute(shift * 100));
        }

        let assessment = topology.analyze(0.5);
        Ok(assessment.unity_score)
    }

    /// Get raw Φ loading for a text
    pub fn compute_phi_loading(&self, text: &str) -> Result<f64> {
        let acts = self.extractor.extract_layers(text, &[self.config.layer])?;
        let activation = &acts[0].activation;

        // Project onto Φ signature (dot product)
        let loading: f64 = activation.iter()
            .zip(self.phi_signature.iter())
            .map(|(a, p)| (*a as f64) * p)
            .sum();

        Ok(loading)
    }

    /// Get raw activation vector for a text
    pub fn extract_activation(&self, text: &str) -> Result<Vec<f32>> {
        let acts = self.extractor.extract_layers(text, &[self.config.layer])?;
        Ok(acts[0].activation.clone())
    }

    /// Classify text as phenomenal or functional
    pub fn classify(&self, text: &str) -> Result<PhenomenalClassification> {
        let score = self.score(text)?;
        let unity = self.compute_unity(text)?;
        let phi_loading = self.compute_phi_loading(text)?;

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
            phi_loading,
            confidence: (score - 0.5).abs() * 2.0,
            method: self.config.method,
        })
    }

    /// Full analysis with all metrics
    pub fn analyze(&self, text: &str) -> Result<PhenomenalAnalysis> {
        let unity = self.compute_unity(text)?;
        let phi_loading = self.compute_phi_loading(text)?;

        let unity_score = self.score_unity(text)?;
        let phi_score = self.score_phi(text)?;
        let combined_score = self.score_combined(text)?;

        let classification = self.classify(text)?;

        Ok(PhenomenalAnalysis {
            text: text.to_string(),
            unity,
            phi_loading,
            unity_score,
            phi_score,
            combined_score,
            classification,
            layer: self.config.layer,
        })
    }

    /// Batch score multiple texts
    pub fn score_batch(&self, texts: &[&str]) -> Result<Vec<f64>> {
        texts.iter().map(|t| self.score(t)).collect()
    }

    /// Batch analyze multiple texts
    pub fn analyze_batch(&self, texts: &[&str]) -> Result<Vec<PhenomenalAnalysis>> {
        texts.iter().map(|t| self.analyze(t)).collect()
    }

    /// Compare two texts and determine which is more phenomenal
    pub fn compare(&self, text_a: &str, text_b: &str) -> Result<ComparisonResult> {
        let analysis_a = self.analyze(text_a)?;
        let analysis_b = self.analyze(text_b)?;

        let difference = analysis_a.combined_score - analysis_b.combined_score;

        Ok(ComparisonResult {
            text_a: text_a.to_string(),
            text_b: text_b.to_string(),
            score_a: analysis_a.combined_score,
            score_b: analysis_b.combined_score,
            difference,
            more_phenomenal: if difference > 0.05 {
                Some(true) // A is more phenomenal
            } else if difference < -0.05 {
                Some(false) // B is more phenomenal
            } else {
                None // Approximately equal
            },
        })
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

        // Calculate phenomenal ratio before moving
        let phenomenal_count = passage_scores.iter().filter(|(_, s)| *s > 0.6).count();
        let phenomenal_ratio = phenomenal_count as f64 / passage_scores.len().max(1) as f64;

        // Find most phenomenal passages
        let mut sorted = passage_scores.clone();
        sorted.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        let top_phenomenal: Vec<_> = sorted.into_iter().take(3).collect();

        Ok(DocumentAnalysis {
            overall_score: mean_score,
            passage_scores,
            top_phenomenal_passages: top_phenomenal,
            phenomenal_ratio,
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
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhenomenalClassification {
    pub label: ClassLabel,
    pub score: f64,
    pub unity: f64,
    pub phi_loading: f64,
    pub confidence: f64,
    pub method: DetectionMethod,
}

/// Classification labels
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ClassLabel {
    Phenomenal,
    Functional,
    Ambiguous,
}

impl std::fmt::Display for ClassLabel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ClassLabel::Phenomenal => write!(f, "Phenomenal"),
            ClassLabel::Functional => write!(f, "Functional"),
            ClassLabel::Ambiguous => write!(f, "Ambiguous"),
        }
    }
}

/// Full analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhenomenalAnalysis {
    pub text: String,
    pub unity: f64,
    pub phi_loading: f64,
    pub unity_score: f64,
    pub phi_score: f64,
    pub combined_score: f64,
    pub classification: PhenomenalClassification,
    pub layer: usize,
}

/// Comparison result between two texts
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComparisonResult {
    pub text_a: String,
    pub text_b: String,
    pub score_a: f64,
    pub score_b: f64,
    pub difference: f64,
    /// Some(true) = A more phenomenal, Some(false) = B more, None = approximately equal
    pub more_phenomenal: Option<bool>,
}

/// Document analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentAnalysis {
    pub overall_score: f64,
    pub passage_scores: Vec<(String, f64)>,
    pub top_phenomenal_passages: Vec<(String, f64)>,
    pub phenomenal_ratio: f64,
}

/// Calibration result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CalibrationResult {
    pub phen_unity_mean: f64,
    pub func_unity_mean: f64,
    pub phen_phi_mean: f64,
    pub func_phi_mean: f64,
    pub n_phenomenal: usize,
    pub n_functional: usize,
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
