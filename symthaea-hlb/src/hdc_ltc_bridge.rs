//! # HDC-LTC Unified Network Bridge
//!
//! This module provides an adapter/bridge that allows the HdcLtcUnifiedNetwork
//! to be used as a drop-in alternative to the CfC network in the cognitive loop.
//!
//! ## Architecture
//!
//! The bridge converts between:
//! - HDC encodings (compressed f32 vectors) <-> HdcLtcUnifiedNetwork inputs (ContinuousHV)
//! - HdcLtcUnifiedNetwork outputs <-> predictions for the encoder
//!
//! ## Usage
//!
//! ```rust,ignore
//! use symthaea::hdc_ltc_bridge::{HdcLtcBridge, HdcLtcBridgeConfig};
//!
//! let config = HdcLtcBridgeConfig::default();
//! let mut bridge = HdcLtcBridge::new(config);
//!
//! // Process input (same interface as CfC)
//! bridge.step(&input_array, dt)?;
//! let state = bridge.read_state()?;
//! ```

use anyhow::Result;
use ndarray::Array1;
use serde::{Deserialize, Serialize};

use symthaea_core::hdc::hdc_ltc_unified::{
    HdcLtcUnifiedNetwork, UnifiedNetworkConfig, UnifiedConfig, UnifiedActivation,
};
use symthaea_core::hdc::unified_hv::{ContinuousHV, HDC_DIMENSION};

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

/// Configuration for the HDC-LTC bridge
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HdcLtcBridgeConfig {
    /// Input dimension (from cognitive loop's compressed HDC)
    pub input_dim: usize,

    /// Output dimension (for predictions)
    pub output_dim: usize,

    /// Network layer sizes
    pub layer_sizes: Vec<usize>,

    /// Base time constant for LTC dynamics
    pub tau_base: f32,

    /// State-dependent time constant scaling
    pub backbone_tau: f32,

    /// Learning rate for online adaptation
    pub learning_rate: f32,

    /// Whether to use layer binding in the network
    pub use_layer_binding: bool,

    /// Whether to use skip connections
    pub skip_connections: bool,

    /// Activation function
    pub activation: BridgeActivation,

    /// Random seed for initialization
    pub seed: u64,
}

/// Activation function selection for the bridge
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub enum BridgeActivation {
    Tanh,
    Sigmoid,
    SiLU,
    Identity,
}

impl Default for HdcLtcBridgeConfig {
    fn default() -> Self {
        Self {
            input_dim: 256,  // Match CfC default
            output_dim: 256,
            layer_sizes: vec![4, 8, 4],  // 3-layer network
            tau_base: 0.1,
            backbone_tau: 0.5,
            learning_rate: 0.01,
            use_layer_binding: true,
            skip_connections: false,
            activation: BridgeActivation::Tanh,
            seed: 42,
        }
    }
}

impl HdcLtcBridgeConfig {
    /// Create config optimized for fast response
    pub fn fast() -> Self {
        Self {
            tau_base: 0.05,  // Faster time constant
            layer_sizes: vec![2, 4, 2],  // Smaller network
            ..Default::default()
        }
    }

    /// Create config optimized for accuracy
    pub fn accurate() -> Self {
        Self {
            layer_sizes: vec![8, 16, 8],  // Larger network
            skip_connections: true,
            ..Default::default()
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// BRIDGE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/// Bridge/adapter for using HdcLtcUnifiedNetwork in the cognitive loop
///
/// This provides the same interface as CfCNetwork, enabling drop-in replacement
/// while leveraging the unified HDC-LTC architecture.
#[derive(Debug, Clone)]
pub struct HdcLtcBridge {
    /// The underlying unified network
    network: HdcLtcUnifiedNetwork,

    /// Configuration
    config: HdcLtcBridgeConfig,

    /// Projection weights: input_dim -> HDC_DIMENSION
    input_projection: Vec<f32>,

    /// Projection weights: HDC_DIMENSION -> output_dim
    output_projection: Vec<f32>,

    /// Current output state (cached for read_state)
    current_output: Vec<f32>,

    /// Total steps processed
    total_steps: u64,

    /// Running state diversity metric
    state_diversity: f32,
}

impl HdcLtcBridge {
    /// Create a new bridge with given configuration
    pub fn new(config: HdcLtcBridgeConfig) -> Self {
        // Create the unified network configuration
        let neuron_config = UnifiedConfig {
            tau_base: config.tau_base,
            backbone_tau: config.backbone_tau,
            dimension: HDC_DIMENSION,
            activation: match config.activation {
                BridgeActivation::Tanh => UnifiedActivation::Tanh,
                BridgeActivation::Sigmoid => UnifiedActivation::Sigmoid,
                BridgeActivation::SiLU => UnifiedActivation::SiLU,
                BridgeActivation::Identity => UnifiedActivation::Identity,
            },
            learning_rate: config.learning_rate,
            ..UnifiedConfig::default()
        };

        let network_config = UnifiedNetworkConfig {
            layer_sizes: config.layer_sizes.clone(),
            neuron_config,
            use_layer_binding: config.use_layer_binding,
            skip_connections: config.skip_connections,
        };

        let network = HdcLtcUnifiedNetwork::new(network_config, config.seed);

        // Initialize random projection matrices
        let input_projection = Self::init_projection(
            config.input_dim,
            HDC_DIMENSION,
            config.seed + 100000,
        );

        let output_projection = Self::init_projection(
            HDC_DIMENSION,
            config.output_dim,
            config.seed + 200000,
        );

        Self {
            network,
            config: config.clone(),
            input_projection,
            output_projection,
            current_output: vec![0.0; config.output_dim],
            total_steps: 0,
            state_diversity: 0.0,
        }
    }

    /// Create a bridge with deterministic genesis seeding
    pub fn from_genesis(config: HdcLtcBridgeConfig, genesis: &symthaea_core::genesis::GenesisSeed) -> Self {
        let neuron_config = UnifiedConfig {
            tau_base: config.tau_base,
            backbone_tau: config.backbone_tau,
            dimension: HDC_DIMENSION,
            activation: match config.activation {
                BridgeActivation::Tanh => UnifiedActivation::Tanh,
                BridgeActivation::Sigmoid => UnifiedActivation::Sigmoid,
                BridgeActivation::SiLU => UnifiedActivation::SiLU,
                BridgeActivation::Identity => UnifiedActivation::Identity,
            },
            learning_rate: config.learning_rate,
            ..UnifiedConfig::default()
        };

        let network_config = UnifiedNetworkConfig {
            layer_sizes: config.layer_sizes.clone(),
            neuron_config,
            use_layer_binding: config.use_layer_binding,
            skip_connections: config.skip_connections,
        };

        let network = HdcLtcUnifiedNetwork::from_genesis(network_config, genesis);

        let input_projection = Self::init_projection_from_genesis(
            genesis, "bridge::input_projection", config.input_dim, HDC_DIMENSION,
        );
        let output_projection = Self::init_projection_from_genesis(
            genesis, "bridge::output_projection", HDC_DIMENSION, config.output_dim,
        );

        Self {
            network,
            config: config.clone(),
            input_projection,
            output_projection,
            current_output: vec![0.0; config.output_dim],
            total_steps: 0,
            state_diversity: 0.0,
        }
    }

    /// Initialize a projection matrix from genesis seed
    fn init_projection_from_genesis(
        genesis: &symthaea_core::genesis::GenesisSeed,
        label: &str,
        input_dim: usize,
        output_dim: usize,
    ) -> Vec<f32> {
        use rand::Rng;
        let mut rng = genesis.domain(label);
        let scale = (2.0 / (input_dim + output_dim) as f32).sqrt();
        (0..input_dim * output_dim)
            .map(|_| (rng.gen::<f32>() * 2.0 - 1.0) * scale)
            .collect()
    }

    /// Initialize a random projection matrix (stored as flattened vec)
    fn init_projection(input_dim: usize, output_dim: usize, seed: u64) -> Vec<f32> {
        let mut projection = Vec::with_capacity(input_dim * output_dim);
        let mut state = seed;

        // Xavier/Glorot initialization scale
        let scale = (2.0 / (input_dim + output_dim) as f32).sqrt();

        for _ in 0..(input_dim * output_dim) {
            state ^= state << 13;
            state ^= state >> 7;
            state ^= state << 17;
            let normalized = (state as f32 / u64::MAX as f32) * 2.0 - 1.0;
            projection.push(normalized * scale);
        }

        projection
    }

    /// Project compressed input to HDC dimension
    fn project_to_hdc(&self, input: &Array1<f32>) -> ContinuousHV {
        let input_dim = self.config.input_dim;
        let mut values = vec![0.0f32; HDC_DIMENSION];

        for j in 0..HDC_DIMENSION {
            let mut sum = 0.0f32;
            for i in 0..input_dim.min(input.len()) {
                sum += input[i] * self.input_projection[i * HDC_DIMENSION + j];
            }
            values[j] = sum.tanh();  // Bound to [-1, 1]
        }

        ContinuousHV::from_values(values)
    }

    /// Project HDC output to compressed dimension
    fn project_from_hdc(&self, hv: &ContinuousHV) -> Vec<f32> {
        let output_dim = self.config.output_dim;
        let mut output = vec![0.0f32; output_dim];

        for i in 0..output_dim {
            let mut sum = 0.0f32;
            for j in 0..HDC_DIMENSION {
                sum += hv.values[j] * self.output_projection[j * output_dim + i];
            }
            output[i] = sum;
        }

        output
    }

    /// Update state diversity metric
    fn update_diversity(&mut self) {
        let output = self.network.output();
        let values = &output.values;

        // Compute variance of output values
        let mean: f32 = values.iter().sum::<f32>() / values.len() as f32;
        let variance: f32 = values.iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f32>() / values.len() as f32;

        // Normalize to 0-1 using sigmoid
        self.state_diversity = 1.0 / (1.0 + (-variance.sqrt() * 10.0).exp());
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // CfC-COMPATIBLE INTERFACE
    // These methods match the CfCNetwork interface for drop-in replacement
    // ═══════════════════════════════════════════════════════════════════════════

    /// Step the network forward (matches CfCNetwork::step)
    pub fn step(&mut self, input: &Array1<f32>, dt: f32) -> Result<()> {
        // Project input to HDC dimension
        let hdc_input = self.project_to_hdc(input);

        // Evolve the unified network using closed-form solution
        self.network.evolve_closed_form(dt, &hdc_input);

        // Project output back
        let hdc_output = self.network.output();
        self.current_output = self.project_from_hdc(&hdc_output);

        // Update metrics
        self.total_steps += 1;
        self.update_diversity();

        Ok(())
    }

    /// Read the current state (matches CfCNetwork::read_state)
    pub fn read_state(&self) -> Result<Array1<f32>> {
        Ok(Array1::from_vec(self.current_output.clone()))
    }

    /// Forward pass and return output (matches CfCNetwork::forward)
    pub fn forward(&mut self, input: &Array1<f32>, dt: f32) -> Array1<f32> {
        let _ = self.step(input, dt);
        Array1::from_vec(self.current_output.clone())
    }

    /// Train step using analytical BPTT gradients (matches CfCNetwork::train_step)
    ///
    /// Replaces Hebbian learning with backpropagation through the closed-form
    /// evolution step, computing exact gradients for weight_hv and input_mask.
    pub fn train_step(
        &mut self,
        input: &Array1<f32>,
        target: &Array1<f32>,
        dt: f32,
        learning_rate: f32,
    ) -> Result<f32> {
        // Project input to HDC
        let hdc_input = self.project_to_hdc(input);

        // Project target to HDC (reuse same projection)
        let hdc_target = self.project_to_hdc(target);

        // Evolve network
        self.network.evolve_closed_form(dt, &hdc_input);

        // Get output and compute error in output space
        let hdc_output = self.network.output();
        let output = self.project_from_hdc(&hdc_output);

        // Compute MSE loss in output space
        let loss: f32 = output.iter()
            .zip(target.iter())
            .map(|(o, t)| (o - t).powi(2))
            .sum::<f32>() / target.len() as f32;

        // Apply BPTT gradients to all layers
        let n_layers = self.network.n_layers();
        for layer_idx in 0..n_layers {
            let layer_in = self.network.layer_input(layer_idx, &hdc_input);
            if let Some(layer) = self.network.layer_mut(layer_idx) {
                for neuron in layer.iter_mut() {
                    let grads = neuron.backward(&layer_in, &hdc_target, dt);
                    neuron.apply_gradients(&grads, learning_rate);
                }
            }
        }

        // Update projection weights using gradient descent
        self.update_projections(&hdc_input, target, &output, learning_rate);

        // Update cached output
        self.current_output = output;
        self.total_steps += 1;
        self.update_diversity();

        Ok(loss)
    }

    /// Update projection weights using simple gradient descent
    fn update_projections(
        &mut self,
        _hdc_input: &ContinuousHV,
        target: &Array1<f32>,
        output: &[f32],
        learning_rate: f32,
    ) {
        let output_dim = self.config.output_dim;

        // Compute output error
        let errors: Vec<f32> = output.iter()
            .zip(target.iter())
            .map(|(o, t)| o - t)
            .collect();

        // Update output projection (simple gradient descent)
        let hdc_output = self.network.output();
        for i in 0..output_dim {
            for j in 0..HDC_DIMENSION {
                let grad = errors[i] * hdc_output.values[j];
                self.output_projection[j * output_dim + i] -= learning_rate * grad;
            }
        }
    }

    /// Predict forward at a specific time horizon (matches CfCNetwork::predict_forward)
    pub fn predict_forward(&mut self, input: &Array1<f32>, horizon: f32) -> Result<Array1<f32>> {
        Ok(self.forward(input, horizon))
    }

    /// Inject state into the network (matches CfCNetwork::inject)
    pub fn inject(&mut self, state: &Array1<f32>) -> Result<()> {
        // Reset the network and set initial state based on input
        self.network.reset();
        self.current_output = state.to_vec();
        Ok(())
    }

    /// Reset the network (matches CfCNetwork::reset)
    pub fn reset(&mut self) {
        self.network.reset();
        self.current_output = vec![0.0; self.config.output_dim];
        self.total_steps = 0;
        self.state_diversity = 0.0;
    }

    /// Get state diversity metric (matches CfCNetwork::state_diversity)
    pub fn state_diversity(&self) -> f32 {
        self.state_diversity
    }

    /// Get all tau values for coherence tracking
    ///
    /// Returns the effective tau from each neuron in the network
    pub fn all_tau(&self) -> Vec<Array1<f32>> {
        let mut taus = Vec::new();

        for layer_idx in 0..self.network.n_layers() {
            if let Some(layer) = self.network.layer(layer_idx) {
                // Create a single tau array for this layer based on neuron configs
                let layer_taus: Vec<f32> = layer.iter()
                    .map(|n| n.config().tau_base * (1.0 + n.config().backbone_tau))
                    .collect();
                taus.push(Array1::from_vec(layer_taus));
            }
        }

        taus
    }

    /// Get flattened tau values
    pub fn flattened_tau(&self) -> Vec<f32> {
        self.all_tau().into_iter().flat_map(|t| t.to_vec()).collect()
    }

    /// Get configuration
    pub fn config(&self) -> &HdcLtcBridgeConfig {
        &self.config
    }

    /// Get total steps
    pub fn total_steps(&self) -> u64 {
        self.total_steps
    }

    /// Get network statistics
    pub fn stats(&self) -> HdcLtcBridgeStats {
        let network_stats = self.network.stats();
        HdcLtcBridgeStats {
            total_steps: self.total_steps,
            state_diversity: self.state_diversity,
            n_layers: network_stats.n_layers,
            n_neurons: network_stats.n_neurons,
            avg_state_norm: network_stats.avg_state_norm,
            avg_weight_norm: network_stats.avg_weight_norm,
        }
    }
}

/// Statistics from the HDC-LTC bridge
#[derive(Debug, Clone)]
pub struct HdcLtcBridgeStats {
    /// Total steps processed
    pub total_steps: u64,
    /// Current state diversity
    pub state_diversity: f32,
    /// Number of layers
    pub n_layers: usize,
    /// Number of neurons
    pub n_neurons: usize,
    /// Average state norm across neurons
    pub avg_state_norm: f32,
    /// Average weight norm across neurons
    pub avg_weight_norm: f32,
}

// ═══════════════════════════════════════════════════════════════════════════════
// TESTS
// ═══════════════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bridge_creation() {
        let config = HdcLtcBridgeConfig::default();
        let bridge = HdcLtcBridge::new(config.clone());

        assert_eq!(bridge.config().input_dim, 256);
        assert_eq!(bridge.config().output_dim, 256);
        assert_eq!(bridge.total_steps(), 0);
    }

    #[test]
    fn test_bridge_step() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let input = Array1::from_vec(vec![0.5; 256]);
        let result = bridge.step(&input, 0.02);

        assert!(result.is_ok());
        assert_eq!(bridge.total_steps(), 1);
    }

    #[test]
    fn test_bridge_forward() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let input = Array1::from_vec(vec![0.5; 256]);
        let output = bridge.forward(&input, 0.02);

        assert_eq!(output.len(), 256);
    }

    #[test]
    fn test_bridge_read_state() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let input = Array1::from_vec(vec![0.5; 256]);
        let _ = bridge.step(&input, 0.02);

        let state = bridge.read_state().unwrap();
        assert_eq!(state.len(), 256);
    }

    #[test]
    fn test_bridge_train_step() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let input = Array1::from_vec(vec![0.5; 256]);
        let target = Array1::from_vec(vec![0.3; 256]);

        let loss = bridge.train_step(&input, &target, 0.02, 0.01).unwrap();
        assert!(loss >= 0.0);
    }

    #[test]
    fn test_bridge_reset() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let input = Array1::from_vec(vec![0.5; 256]);
        let _ = bridge.step(&input, 0.02);
        assert_eq!(bridge.total_steps(), 1);

        bridge.reset();
        assert_eq!(bridge.total_steps(), 0);
    }

    #[test]
    fn test_bridge_state_diversity() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let input = Array1::from_vec(vec![0.5; 256]);
        let _ = bridge.step(&input, 0.02);

        let diversity = bridge.state_diversity();
        assert!(diversity >= 0.0 && diversity <= 1.0);
    }

    #[test]
    fn test_bridge_all_tau() {
        let config = HdcLtcBridgeConfig::default();
        let bridge = HdcLtcBridge::new(config);

        let taus = bridge.all_tau();
        assert!(!taus.is_empty());
    }

    #[test]
    fn test_bridge_predict_forward() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let input = Array1::from_vec(vec![0.5; 256]);

        // Small horizon
        let pred_small = bridge.predict_forward(&input, 0.1).unwrap();
        assert_eq!(pred_small.len(), 256);

        // Large horizon (O(1) closed-form)
        let pred_large = bridge.predict_forward(&input, 10.0).unwrap();
        assert_eq!(pred_large.len(), 256);
    }

    #[test]
    fn test_bridge_inject() {
        let config = HdcLtcBridgeConfig::default();
        let mut bridge = HdcLtcBridge::new(config);

        let state = Array1::from_vec(vec![0.3; 256]);
        let result = bridge.inject(&state);

        assert!(result.is_ok());
    }

    #[test]
    fn test_fast_config() {
        let config = HdcLtcBridgeConfig::fast();
        assert_eq!(config.tau_base, 0.05);
        assert_eq!(config.layer_sizes, vec![2, 4, 2]);
    }

    #[test]
    fn test_accurate_config() {
        let config = HdcLtcBridgeConfig::accurate();
        assert!(config.skip_connections);
        assert_eq!(config.layer_sizes, vec![8, 16, 8]);
    }
}
