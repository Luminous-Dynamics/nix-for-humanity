//! # Real-valued Phi Computation
//!
//! Continuous-valued integrated information (Φ) computation using
//! real-valued hypervectors and information geometry.

use symthaea_core::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Configuration for Phi computation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhiRealConfig {
    /// HDC dimension
    pub dimension: usize,
    /// Number of partition attempts
    pub num_partitions: usize,
    /// Minimum partition size
    pub min_partition_size: usize,
    /// Use approximation for large systems
    pub use_approximation: bool,
}

impl Default for PhiRealConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            num_partitions: 10,
            min_partition_size: 2,
            use_approximation: true,
        }
    }
}

/// Result of Phi computation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhiRealResult {
    /// Integrated information value
    pub phi: f64,
    /// Minimum information partition (MIP)
    pub mip: Option<(Vec<usize>, Vec<usize>)>,
    /// Component contributions
    pub contributions: HashMap<usize, f64>,
    /// Computation time in microseconds
    pub computation_time_us: u64,
    /// Method used
    pub method: String,
}

impl Default for PhiRealResult {
    fn default() -> Self {
        Self {
            phi: 0.0,
            mip: None,
            contributions: HashMap::new(),
            computation_time_us: 0,
            method: "default".to_string(),
        }
    }
}

/// Real-valued Phi calculator
pub struct PhiRealCalculator {
    config: PhiRealConfig,
    /// Cached transition probability matrices
    transition_cache: HashMap<usize, Vec<Vec<f64>>>,
}

impl PhiRealCalculator {
    /// Create new calculator
    pub fn new(config: PhiRealConfig) -> Self {
        Self {
            config,
            transition_cache: HashMap::new(),
        }
    }

    /// Calculate Phi for a set of hypervectors
    pub fn calculate(&mut self, states: &[RealHV]) -> PhiRealResult {
        let start = std::time::Instant::now();
        let n = states.len();

        if n < 2 {
            return PhiRealResult {
                phi: 0.0,
                mip: None,
                contributions: HashMap::new(),
                computation_time_us: start.elapsed().as_micros() as u64,
                method: "trivial".to_string(),
            };
        }

        // For large systems, use approximation
        if n > 20 && self.config.use_approximation {
            return self.calculate_approximate(states, start);
        }

        // Calculate mutual information matrix
        let mi_matrix = self.compute_mi_matrix(states);

        // Find minimum information partition
        let (phi, mip) = self.find_mip(&mi_matrix);

        // Calculate individual contributions
        let contributions = self.calculate_contributions(states, &mi_matrix);

        PhiRealResult {
            phi,
            mip: Some(mip),
            contributions,
            computation_time_us: start.elapsed().as_micros() as u64,
            method: "exact".to_string(),
        }
    }

    fn calculate_approximate(&self, states: &[RealHV], start: std::time::Instant) -> PhiRealResult {
        // Approximate phi using sampling and clustering
        let n = states.len();
        let sample_size = (n / 4).max(10).min(n);

        // Sample random partitions
        let mut best_phi = f64::MAX;
        let mut best_partition = (Vec::new(), Vec::new());

        for _ in 0..self.config.num_partitions {
            // Random bipartition
            let mut part_a: Vec<usize> = Vec::new();
            let mut part_b: Vec<usize> = Vec::new();

            for i in 0..n {
                if fastrand::bool() {
                    part_a.push(i);
                } else {
                    part_b.push(i);
                }
            }

            if part_a.is_empty() || part_b.is_empty() {
                continue;
            }

            // Calculate information loss for this partition
            let phi = self.partition_info_loss(states, &part_a, &part_b);

            if phi < best_phi {
                best_phi = phi;
                best_partition = (part_a, part_b);
            }
        }

        let mut contributions = HashMap::new();
        for (i, state) in states.iter().enumerate() {
            let magnitude = state.iter().map(|x| x * x).sum::<f32>().sqrt();
            contributions.insert(i, magnitude as f64 / n as f64);
        }

        PhiRealResult {
            phi: best_phi,
            mip: Some(best_partition),
            contributions,
            computation_time_us: start.elapsed().as_micros() as u64,
            method: "approximate".to_string(),
        }
    }

    fn compute_mi_matrix(&self, states: &[RealHV]) -> Vec<Vec<f64>> {
        let n = states.len();
        let mut mi = vec![vec![0.0; n]; n];

        for i in 0..n {
            for j in (i + 1)..n {
                // Approximate mutual information using correlation
                let sim = states[i].cosine_similarity(&states[j]);
                let mi_approx = if sim.abs() > 0.99 {
                    1.0
                } else if sim.abs() < 0.01 {
                    0.0
                } else {
                    -0.5 * (1.0 - sim * sim).ln() as f64
                };
                mi[i][j] = mi_approx;
                mi[j][i] = mi_approx;
            }
        }

        mi
    }

    fn find_mip(&self, mi_matrix: &[Vec<f64>]) -> (f64, (Vec<usize>, Vec<usize>)) {
        let n = mi_matrix.len();

        if n <= 1 {
            return (0.0, (vec![0], Vec::new()));
        }

        let mut min_phi = f64::MAX;
        let mut best_partition = (vec![0], (1..n).collect());

        // Try different partitions (for small n)
        let max_partitions = 2_usize.pow(n as u32 - 1).min(1000);

        for p in 1..max_partitions {
            let mut part_a = Vec::new();
            let mut part_b = Vec::new();

            for i in 0..n {
                if (p >> i) & 1 == 1 {
                    part_a.push(i);
                } else {
                    part_b.push(i);
                }
            }

            if part_a.is_empty() || part_b.is_empty() {
                continue;
            }

            // Calculate phi for this partition
            let mut cross_mi = 0.0;
            for &a in &part_a {
                for &b in &part_b {
                    cross_mi += mi_matrix[a][b];
                }
            }

            // Normalize
            let normalized_phi = cross_mi / (part_a.len() * part_b.len()) as f64;

            if normalized_phi < min_phi {
                min_phi = normalized_phi;
                best_partition = (part_a, part_b);
            }
        }

        (min_phi, best_partition)
    }

    fn partition_info_loss(&self, states: &[RealHV], part_a: &[usize], part_b: &[usize]) -> f64 {
        // Calculate information that crosses the partition
        let mut cross_info = 0.0;

        for &a in part_a {
            for &b in part_b {
                let sim = states[a].cosine_similarity(&states[b]).abs();
                cross_info += sim as f64;
            }
        }

        cross_info / (part_a.len() * part_b.len()) as f64
    }

    fn calculate_contributions(&self, states: &[RealHV], mi_matrix: &[Vec<f64>]) -> HashMap<usize, f64> {
        let n = states.len();
        let mut contributions = HashMap::new();

        for i in 0..n {
            // Contribution = sum of mutual information with all other elements
            let total_mi: f64 = mi_matrix[i].iter().sum();
            contributions.insert(i, total_mi / (n - 1) as f64);
        }

        contributions
    }
}

impl Default for PhiRealCalculator {
    fn default() -> Self {
        Self::new(PhiRealConfig::default())
    }
}

/// Phi computation with gradient tracking
pub struct DifferentiablePhiCalculator {
    base_calculator: PhiRealCalculator,
}

impl DifferentiablePhiCalculator {
    /// Create new differentiable calculator
    pub fn new(config: PhiRealConfig) -> Self {
        Self {
            base_calculator: PhiRealCalculator::new(config),
        }
    }

    /// Calculate phi with gradients
    pub fn calculate_with_gradient(&mut self, states: &[RealHV]) -> (PhiRealResult, Vec<RealHV>) {
        let result = self.base_calculator.calculate(states);

        // Approximate gradients via finite differences
        let epsilon = 0.001;
        let mut gradients = Vec::new();

        for (i, state) in states.iter().enumerate() {
            let mut grad = state.clone();
            for d in 0..state.len().min(100) {
                // Perturb
                let mut perturbed = states.to_vec();
                perturbed[i] = perturbed[i].clone();
                perturbed[i][d] += epsilon;

                let phi_plus = self.base_calculator.calculate(&perturbed).phi;
                grad[d] = ((phi_plus - result.phi) / epsilon) as f32;
            }
            gradients.push(grad);
        }

        (result, gradients)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_phi_calculation() {
        let mut calc = PhiRealCalculator::default();
        let states: Vec<RealHV> = (0..5)
            .map(|_| RealHV::random(512))
            .collect();

        let result = calc.calculate(&states);
        assert!(result.phi >= 0.0);
    }

    #[test]
    fn test_trivial_phi() {
        let mut calc = PhiRealCalculator::default();
        let states = vec![RealHV::random(512)];
        let result = calc.calculate(&states);
        assert_eq!(result.phi, 0.0);
    }
}
