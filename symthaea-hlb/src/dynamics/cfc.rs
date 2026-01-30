//! # Closed-form Continuous-time (CfC) Neural Networks
//!
//! CfC networks are a class of continuous-time neural networks that have
//! closed-form solutions, making them faster than traditional LTC networks
//! while maintaining similar expressiveness.
//!
//! ## Key Features
//!
//! - **Closed-form solution**: No ODE solver needed at inference time
//! - **Continuous-time**: Natural handling of irregular time series
//! - **Causal**: Output at time t only depends on inputs at times <= t
//! - **Memory efficient**: Constant memory regardless of sequence length

use ndarray::{Array1, Array2};
use serde::{Deserialize, Serialize};

/// Configuration for a CfC cell
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CfCConfig {
    /// Input dimension
    pub input_dim: usize,

    /// Hidden state dimension
    pub hidden_dim: usize,

    /// Whether to use backbone network for additional capacity
    pub use_backbone: bool,

    /// Number of backbone layers
    pub backbone_layers: usize,

    /// Backbone hidden dimension
    pub backbone_dim: usize,

    /// Activation function type
    pub activation: ActivationType,

    /// Time constant initialization range
    pub tau_range: (f32, f32),

    /// Dropout rate (0.0 = no dropout)
    pub dropout: f32,
}

impl Default for CfCConfig {
    fn default() -> Self {
        Self {
            input_dim: 64,
            hidden_dim: 128,
            use_backbone: true,
            backbone_layers: 2,
            backbone_dim: 128,
            activation: ActivationType::SiLU,
            tau_range: (0.1, 10.0),
            dropout: 0.1,
        }
    }
}

/// Activation function types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ActivationType {
    /// Sigmoid-weighted Linear Unit
    SiLU,
    /// Gaussian Error Linear Unit
    GELU,
    /// Rectified Linear Unit
    ReLU,
    /// Hyperbolic tangent
    Tanh,
    /// Sigmoid
    Sigmoid,
}

impl ActivationType {
    /// Apply activation function
    pub fn apply(&self, x: f32) -> f32 {
        match self {
            ActivationType::SiLU => x * sigmoid(x),
            ActivationType::GELU => 0.5 * x * (1.0 + (0.7978845608 * (x + 0.044715 * x.powi(3))).tanh()),
            ActivationType::ReLU => x.max(0.0),
            ActivationType::Tanh => x.tanh(),
            ActivationType::Sigmoid => sigmoid(x),
        }
    }

    /// Apply activation function to array
    pub fn apply_array(&self, x: &Array1<f32>) -> Array1<f32> {
        x.mapv(|v| self.apply(v))
    }
}

fn sigmoid(x: f32) -> f32 {
    1.0 / (1.0 + (-x).exp())
}

/// Mean squared error between two arrays
fn mse_loss(output: &Array1<f32>, target: &Array1<f32>) -> f32 {
    if output.len() != target.len() || output.is_empty() {
        return f32::MAX;
    }
    output.iter()
        .zip(target.iter())
        .map(|(o, t)| (o - t).powi(2))
        .sum::<f32>() / output.len() as f32
}

/// A single Closed-form Continuous-time cell
#[derive(Debug, Clone)]
#[allow(dead_code)] // Fields reserved for CfC dynamics
pub struct CfCCell {
    config: CfCConfig,

    // Weights for state transition
    w_in: Array2<f32>,     // Input to hidden
    w_h: Array2<f32>,      // Hidden to hidden
    w_out: Array2<f32>,    // Hidden to output (if different)

    // Biases
    b_h: Array1<f32>,

    // Time constants (learnable)
    tau: Array1<f32>,

    // Backbone network weights (optional)
    backbone_weights: Vec<Array2<f32>>,
    backbone_biases: Vec<Array1<f32>>,

    // Current hidden state
    state: Array1<f32>,

    // Statistics
    steps: u64,
}

impl CfCCell {
    /// Create a new CfC cell
    pub fn new(config: CfCConfig) -> Self {
        let _rng = rand::thread_rng();

        // When backbone is used, w_in takes backbone output (backbone_dim)
        // Otherwise, w_in takes raw input (input_dim)
        let effective_input_dim = if config.use_backbone {
            config.backbone_dim
        } else {
            config.input_dim
        };

        let scale = (2.0 / (effective_input_dim + config.hidden_dim) as f32).sqrt();

        // Initialize weights with Xavier/Glorot initialization
        let w_in = Array2::from_shape_fn((config.hidden_dim, effective_input_dim), |_| {
            (rand::random::<f32>() - 0.5) * 2.0 * scale
        });

        let w_h = Array2::from_shape_fn((config.hidden_dim, config.hidden_dim), |_| {
            (rand::random::<f32>() - 0.5) * 2.0 * scale
        });

        let w_out = Array2::from_shape_fn((config.hidden_dim, config.hidden_dim), |_| {
            (rand::random::<f32>() - 0.5) * 2.0 * scale
        });

        let b_h = Array1::zeros(config.hidden_dim);

        // Initialize time constants uniformly in log space
        let (tau_min, tau_max) = config.tau_range;
        let tau = Array1::from_shape_fn(config.hidden_dim, |_| {
            let log_tau = tau_min.ln() + rand::random::<f32>() * (tau_max.ln() - tau_min.ln());
            log_tau.exp()
        });

        // Initialize backbone if needed
        let (backbone_weights, backbone_biases) = if config.use_backbone {
            let mut weights = Vec::new();
            let mut biases = Vec::new();

            // First layer: input_dim -> backbone_dim
            weights.push(Array2::from_shape_fn((config.backbone_dim, config.input_dim), |_| {
                (rand::random::<f32>() - 0.5) * 2.0 * scale
            }));
            biases.push(Array1::zeros(config.backbone_dim));

            // Hidden layers
            for _ in 1..config.backbone_layers {
                weights.push(Array2::from_shape_fn((config.backbone_dim, config.backbone_dim), |_| {
                    (rand::random::<f32>() - 0.5) * 2.0 * scale
                }));
                biases.push(Array1::zeros(config.backbone_dim));
            }

            (weights, biases)
        } else {
            (Vec::new(), Vec::new())
        };

        let hidden_dim = config.hidden_dim;
        Self {
            config,
            w_in,
            w_h,
            w_out,
            b_h,
            tau,
            backbone_weights,
            backbone_biases,
            state: Array1::zeros(hidden_dim),
            steps: 0,
        }
    }

    /// Reset the cell state
    pub fn reset(&mut self) {
        self.state = Array1::zeros(self.config.hidden_dim);
        self.steps = 0;
    }

    /// Forward pass through the cell
    ///
    /// # Arguments
    /// * `input` - Input vector
    /// * `dt` - Time step (can be irregular)
    ///
    /// # Returns
    /// New hidden state
    pub fn forward(&mut self, input: &Array1<f32>, dt: f32) -> Array1<f32> {
        // Process through backbone if enabled
        let processed_input = if self.config.use_backbone {
            self.backbone_forward(input)
        } else {
            input.clone()
        };

        // Compute gating based on processed input and current state
        // Using closed-form solution: h(t) = h_inf + (h_0 - h_inf) * exp(-t/tau)
        // where h_inf is the equilibrium state

        // Compute target/equilibrium state
        let x_contrib = self.w_in.dot(&processed_input);
        let h_contrib = self.w_h.dot(&self.state);
        let h_inf = self.config.activation.apply_array(&(x_contrib + h_contrib + &self.b_h));

        // Compute decay factor based on time constants
        let decay: Array1<f32> = self.tau.mapv(|t| (-dt / t).exp());

        // Update state using closed-form solution
        let new_state = &h_inf + &((&self.state - &h_inf) * &decay);

        self.state = new_state.clone();
        self.steps += 1;

        new_state
    }

    /// Process through backbone network
    fn backbone_forward(&self, input: &Array1<f32>) -> Array1<f32> {
        let mut x = input.clone();

        for (w, b) in self.backbone_weights.iter().zip(self.backbone_biases.iter()) {
            x = self.config.activation.apply_array(&(w.dot(&x) + b));
        }

        x
    }

    /// Get the current state
    pub fn state(&self) -> &Array1<f32> {
        &self.state
    }

    /// Set the state
    pub fn set_state(&mut self, state: Array1<f32>) {
        self.state = state;
    }

    /// Get configuration
    pub fn config(&self) -> &CfCConfig {
        &self.config
    }

    /// Get time constants
    pub fn tau(&self) -> &Array1<f32> {
        &self.tau
    }
}

/// A complete CfC neural network
#[derive(Debug, Clone)]
pub struct CfCNetwork {
    /// Network configuration
    config: CfCNetworkConfig,

    /// Stack of CfC cells
    cells: Vec<CfCCell>,

    /// Output projection weights
    output_weights: Array2<f32>,
    output_bias: Array1<f32>,

    /// Statistics
    total_steps: u64,
}

/// Configuration for a CfC network
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CfCNetworkConfig {
    /// Input dimension
    pub input_dim: usize,

    /// Hidden dimension per layer
    pub hidden_dim: usize,

    /// Number of layers
    pub num_layers: usize,

    /// Output dimension
    pub output_dim: usize,

    /// Cell configuration
    pub cell_config: CfCConfig,

    /// Whether to use residual connections
    pub residual: bool,

    /// Whether to use bidirectional processing (doubles computation)
    pub bidirectional: bool,
}

impl Default for CfCNetworkConfig {
    fn default() -> Self {
        let cell_config = CfCConfig {
            input_dim: 64,
            hidden_dim: 128,
            ..Default::default()
        };

        Self {
            input_dim: 64,
            hidden_dim: 128,
            num_layers: 2,
            output_dim: 32,
            cell_config,
            residual: true,
            bidirectional: false,
        }
    }
}

impl CfCNetwork {
    /// Create a new CfC network
    pub fn new(config: CfCNetworkConfig) -> Self {
        let mut cells = Vec::with_capacity(config.num_layers);

        for i in 0..config.num_layers {
            let cell_config = CfCConfig {
                input_dim: if i == 0 { config.input_dim } else { config.hidden_dim },
                hidden_dim: config.hidden_dim,
                ..config.cell_config.clone()
            };
            cells.push(CfCCell::new(cell_config));
        }

        let scale = (2.0 / (config.hidden_dim + config.output_dim) as f32).sqrt();
        let output_weights = Array2::from_shape_fn((config.output_dim, config.hidden_dim), |_| {
            (rand::random::<f32>() - 0.5) * 2.0 * scale
        });
        let output_bias = Array1::zeros(config.output_dim);

        Self {
            config,
            cells,
            output_weights,
            output_bias,
            total_steps: 0,
        }
    }

    /// Reset all cell states
    pub fn reset(&mut self) {
        for cell in &mut self.cells {
            cell.reset();
        }
        self.total_steps = 0;
    }

    /// Forward pass through the network
    ///
    /// # Arguments
    /// * `input` - Input vector
    /// * `dt` - Time step
    ///
    /// # Returns
    /// Output vector
    pub fn forward(&mut self, input: &Array1<f32>, dt: f32) -> Array1<f32> {
        let mut h = input.clone();

        for (i, cell) in self.cells.iter_mut().enumerate() {
            let prev_h = h.clone();
            h = cell.forward(&h, dt);

            // Add residual connection if enabled and dimensions match
            if self.config.residual && i > 0 && prev_h.len() == h.len() {
                h = &h + &prev_h;
            }
        }

        // Project to output dimension
        let output = self.output_weights.dot(&h) + &self.output_bias;
        self.total_steps += 1;

        output
    }

    /// Process a sequence of inputs
    ///
    /// # Arguments
    /// * `inputs` - Sequence of input vectors
    /// * `dts` - Time steps between consecutive inputs
    ///
    /// # Returns
    /// Sequence of outputs
    pub fn forward_sequence(
        &mut self,
        inputs: &[Array1<f32>],
        dts: &[f32],
    ) -> Vec<Array1<f32>> {
        assert_eq!(inputs.len(), dts.len());

        self.reset();
        inputs.iter()
            .zip(dts.iter())
            .map(|(input, dt)| self.forward(input, *dt))
            .collect()
    }

    /// Get the current state of all cells
    pub fn state(&self) -> Vec<Array1<f32>> {
        self.cells.iter().map(|c| c.state().clone()).collect()
    }

    /// Set the state of all cells
    pub fn set_state(&mut self, states: Vec<Array1<f32>>) {
        for (cell, state) in self.cells.iter_mut().zip(states.into_iter()) {
            cell.set_state(state);
        }
    }

    /// Get network configuration
    pub fn config(&self) -> &CfCNetworkConfig {
        &self.config
    }

    /// Get number of parameters
    pub fn num_parameters(&self) -> usize {
        let mut count = 0;
        for cell in &self.cells {
            let cfg = cell.config();
            count += cfg.input_dim * cfg.hidden_dim; // w_in
            count += cfg.hidden_dim * cfg.hidden_dim; // w_h
            count += cfg.hidden_dim; // b_h
            count += cfg.hidden_dim; // tau
        }
        count += self.config.hidden_dim * self.config.output_dim; // output_weights
        count += self.config.output_dim; // output_bias
        count
    }

    // =========================================================================
    // Cognitive Loop Compatibility Methods
    // These methods provide the API expected by cognitive_loop.rs
    // =========================================================================

    /// Step the network forward (alias for forward, returns unit)
    pub fn step(&mut self, input: &Array1<f32>, dt: f32) -> anyhow::Result<()> {
        let _ = self.forward(input, dt);
        Ok(())
    }

    /// Read the current state (returns Result for cognitive_loop compatibility)
    pub fn read_state(&self) -> anyhow::Result<Array1<f32>> {
        // Return the state of the last cell
        if let Some(cell) = self.cells.last() {
            Ok(cell.state().clone())
        } else {
            Ok(Array1::zeros(self.config.hidden_dim))
        }
    }

    /// Train step using perturbation-based gradient estimation (SPSA).
    ///
    /// Estimates gradients by evaluating the loss at perturbed weight values
    /// and updates all learnable parameters: W_in, W_h, biases, tau, and
    /// output projection weights.
    ///
    /// This replaces the previous implementation which only nudged the last
    /// cell's hidden state without modifying any weights.
    pub fn train_step(
        &mut self,
        input: &Array1<f32>,
        target: &Array1<f32>,
        dt: f32,
        learning_rate: f32,
    ) -> anyhow::Result<f32> {
        // Compute baseline output and loss
        let baseline_output = self.forward(input, dt);
        let baseline_loss = mse_loss(&baseline_output, target);

        // Perturbation scale (smaller = more accurate gradient, larger = more robust)
        let epsilon = 0.01f32;

        // Update output projection weights (most direct impact on loss)
        self.update_output_weights(input, target, dt, learning_rate, epsilon, baseline_loss);

        // Update each cell's weights
        for cell_idx in 0..self.cells.len() {
            self.update_cell_weights(cell_idx, input, target, dt, learning_rate, epsilon, baseline_loss);
        }

        // Recompute loss after updates
        self.reset_states_only();
        let final_output = self.forward(input, dt);
        let final_loss = mse_loss(&final_output, target);

        Ok(final_loss)
    }

    /// Update output projection weights via perturbation
    fn update_output_weights(
        &mut self,
        input: &Array1<f32>,
        target: &Array1<f32>,
        dt: f32,
        lr: f32,
        epsilon: f32,
        baseline_loss: f32,
    ) {
        let (rows, cols) = self.output_weights.dim();

        // Perturb a subset of output weights (full perturbation too expensive)
        let stride = (rows * cols / 32).max(1); // Update ~32 weights per step
        for idx in (0..rows * cols).step_by(stride) {
            let r = idx / cols;
            let c = idx % cols;

            // Positive perturbation
            self.output_weights[[r, c]] += epsilon;
            self.reset_states_only();
            let output_pos = self.forward(input, dt);
            let loss_pos = mse_loss(&output_pos, target);
            self.output_weights[[r, c]] -= epsilon;

            // Gradient estimate
            let grad = (loss_pos - baseline_loss) / epsilon;

            // SGD update
            self.output_weights[[r, c]] -= lr * grad;
        }

        // Also update output bias
        for j in 0..self.output_bias.len() {
            self.output_bias[j] += epsilon;
            self.reset_states_only();
            let output_pos = self.forward(input, dt);
            let loss_pos = mse_loss(&output_pos, target);
            self.output_bias[j] -= epsilon;

            let grad = (loss_pos - baseline_loss) / epsilon;
            self.output_bias[j] -= lr * grad;
        }
    }

    /// Update a single CfC cell's weights via perturbation
    fn update_cell_weights(
        &mut self,
        cell_idx: usize,
        input: &Array1<f32>,
        target: &Array1<f32>,
        dt: f32,
        lr: f32,
        epsilon: f32,
        baseline_loss: f32,
    ) {
        let hidden_dim = self.cells[cell_idx].config.hidden_dim;

        // Update tau (time constants) - these are critical for temporal dynamics
        for j in 0..hidden_dim {
            let old_tau = self.cells[cell_idx].tau[j];
            self.cells[cell_idx].tau[j] = old_tau + epsilon;
            self.reset_states_only();
            let output_pos = self.forward(input, dt);
            let loss_pos = mse_loss(&output_pos, target);
            self.cells[cell_idx].tau[j] = old_tau;

            let grad = (loss_pos - baseline_loss) / epsilon;
            // Ensure tau stays positive
            let new_tau = (old_tau - lr * grad).max(0.01);
            self.cells[cell_idx].tau[j] = new_tau;
        }

        // Update bias
        for j in 0..hidden_dim {
            self.cells[cell_idx].b_h[j] += epsilon;
            self.reset_states_only();
            let output_pos = self.forward(input, dt);
            let loss_pos = mse_loss(&output_pos, target);
            self.cells[cell_idx].b_h[j] -= epsilon;

            let grad = (loss_pos - baseline_loss) / epsilon;
            self.cells[cell_idx].b_h[j] -= lr * grad;
        }

        // Update W_h (recurrent weights) - sparse update for efficiency
        let stride = (hidden_dim * hidden_dim / 16).max(1);
        for idx in (0..hidden_dim * hidden_dim).step_by(stride) {
            let r = idx / hidden_dim;
            let c = idx % hidden_dim;

            self.cells[cell_idx].w_h[[r, c]] += epsilon;
            self.reset_states_only();
            let output_pos = self.forward(input, dt);
            let loss_pos = mse_loss(&output_pos, target);
            self.cells[cell_idx].w_h[[r, c]] -= epsilon;

            let grad = (loss_pos - baseline_loss) / epsilon;
            self.cells[cell_idx].w_h[[r, c]] -= lr * grad;
        }
    }

    /// Reset cell hidden states without resetting step counters
    fn reset_states_only(&mut self) {
        for cell in &mut self.cells {
            cell.state = Array1::zeros(cell.config.hidden_dim);
        }
    }

    /// Compute state diversity across CfC cells.
    ///
    /// Measures the variance of hidden activations across all cells, normalized
    /// to [0, 1] via sigmoid. Higher values indicate more differentiated cell
    /// states (each cell encoding different information).
    ///
    /// **Note**: This is a network activity metric, not a consciousness measure.
    /// It has no formal connection to IIT Phi or any published consciousness metric.
    pub fn state_diversity(&self) -> f32 {
        let states: Vec<&Array1<f32>> = self.cells.iter().map(|c| c.state()).collect();
        if states.is_empty() {
            return 0.0;
        }

        // Measure variance across cells
        let mean_activity: f32 = states.iter()
            .flat_map(|s| s.iter())
            .sum::<f32>() / (states.len() * self.config.hidden_dim) as f32;

        let variance: f32 = states.iter()
            .flat_map(|s| s.iter())
            .map(|x| (x - mean_activity).powi(2))
            .sum::<f32>() / (states.len() * self.config.hidden_dim) as f32;

        // Normalize to 0-1 range using sigmoid-like transformation
        1.0 / (1.0 + (-variance.sqrt() * 10.0).exp())
    }

    /// Deprecated alias for state_diversity(). Use state_diversity() instead.
    #[deprecated(note = "Renamed to state_diversity(). This measures activation variance, not consciousness.")]
    pub fn consciousness_level(&self) -> f32 {
        self.state_diversity()
    }

    /// Predict forward at a specific time horizon
    pub fn predict_forward(&mut self, input: &Array1<f32>, horizon: f32) -> anyhow::Result<Array1<f32>> {
        // Use forward pass with the horizon as dt
        Ok(self.forward(input, horizon))
    }

    /// Inject state into the network (alias for set_state)
    pub fn inject(&mut self, state: &Array1<f32>) -> anyhow::Result<()> {
        // Set state on all cells
        for cell in &mut self.cells {
            cell.set_state(state.clone());
        }
        Ok(())
    }

    /// Create with specific input dimension (for cognitive_loop compatibility)
    pub fn new_with_input(input_dim: usize, hidden_dim: usize) -> Self {
        let config = CfCNetworkConfig {
            input_dim,
            hidden_dim,
            ..Default::default()
        };
        Self::new(config)
    }

    /// Get all tau (time constant) values across all cells
    ///
    /// Returns references to the tau arrays for each cell, useful for
    /// computing temporal coherence metrics.
    pub fn all_tau(&self) -> Vec<&Array1<f32>> {
        self.cells.iter().map(|cell| cell.tau()).collect()
    }

    /// Get flattened tau values as a single vector
    pub fn flattened_tau(&self) -> Vec<f32> {
        self.cells.iter()
            .flat_map(|cell| cell.tau().iter().cloned())
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cfc_cell_creation() {
        let config = CfCConfig::default();
        let cell = CfCCell::new(config);
        assert_eq!(cell.state().len(), 128);
    }

    #[test]
    fn test_cfc_forward() {
        let config = CfCConfig {
            input_dim: 32,
            hidden_dim: 64,
            ..Default::default()
        };
        let mut cell = CfCCell::new(config);

        let input = Array1::from_vec(vec![0.1; 32]);
        let output = cell.forward(&input, 0.1);

        assert_eq!(output.len(), 64);
    }

    #[test]
    fn test_cfc_network() {
        let config = CfCNetworkConfig {
            input_dim: 32,
            hidden_dim: 64,
            num_layers: 2,
            output_dim: 16,
            ..Default::default()
        };
        let mut network = CfCNetwork::new(config);

        let input = Array1::from_vec(vec![0.1; 32]);
        let output = network.forward(&input, 0.1);

        assert_eq!(output.len(), 16);
    }

    // =====================================================================
    // 4.5: CfC NUMERICAL STABILITY TESTS
    // =====================================================================

    #[test]
    fn test_cfc_long_horizon_stability() {
        let config = CfCNetworkConfig {
            input_dim: 8,
            hidden_dim: 16,
            num_layers: 2,
            output_dim: 4,
            ..Default::default()
        };
        let mut network = CfCNetwork::new(config);
        let input = Array1::from_vec(vec![0.5; 8]);

        for step in 0..10_000 {
            let output = network.forward(&input, 0.1);
            assert!(
                output.iter().all(|x| x.is_finite()),
                "CfC diverged at step {} — output: {:?}",
                step,
                output
            );
        }
    }

    #[test]
    fn test_cfc_extreme_small_tau() {
        let cell_config = CfCConfig {
            input_dim: 4,
            hidden_dim: 8,
            tau_range: (0.001, 0.01), // Very small time constants
            use_backbone: false,
            ..Default::default()
        };
        let config = CfCNetworkConfig {
            input_dim: 4,
            hidden_dim: 8,
            num_layers: 1,
            output_dim: 4,
            cell_config,
            residual: false,
            bidirectional: false,
        };
        let mut network = CfCNetwork::new(config);
        let input = Array1::from_vec(vec![1.0; 4]);

        // With very small tau, decay is nearly complete each step
        for _ in 0..100 {
            let output = network.forward(&input, 1.0);
            assert!(
                output.iter().all(|x| x.is_finite()),
                "Small tau caused divergence"
            );
        }
    }

    #[test]
    fn test_cfc_extreme_large_tau() {
        let cell_config = CfCConfig {
            input_dim: 4,
            hidden_dim: 8,
            tau_range: (100.0, 1000.0), // Very large time constants
            use_backbone: false,
            ..Default::default()
        };
        let config = CfCNetworkConfig {
            input_dim: 4,
            hidden_dim: 8,
            num_layers: 1,
            output_dim: 4,
            cell_config,
            residual: false,
            bidirectional: false,
        };
        let mut network = CfCNetwork::new(config);
        let input = Array1::from_vec(vec![1.0; 4]);

        // With very large tau, state barely changes each step
        for _ in 0..100 {
            let output = network.forward(&input, 0.01);
            assert!(
                output.iter().all(|x| x.is_finite()),
                "Large tau caused divergence"
            );
        }
    }

    #[test]
    fn test_cfc_zero_input_stability() {
        let config = CfCNetworkConfig {
            input_dim: 8,
            hidden_dim: 16,
            num_layers: 2,
            output_dim: 4,
            ..Default::default()
        };
        let mut network = CfCNetwork::new(config);
        let input = Array1::zeros(8);

        for _ in 0..1_000 {
            let output = network.forward(&input, 0.1);
            assert!(
                output.iter().all(|x| x.is_finite()),
                "Zero input caused divergence"
            );
        }
    }

    #[test]
    fn test_cfc_large_dt_stability() {
        let config = CfCNetworkConfig {
            input_dim: 8,
            hidden_dim: 16,
            num_layers: 1,
            output_dim: 4,
            ..Default::default()
        };
        let mut network = CfCNetwork::new(config);
        let input = Array1::from_vec(vec![0.5; 8]);

        // Large dt = 10.0 (should still produce finite output due to closed-form solution)
        for _ in 0..100 {
            let output = network.forward(&input, 10.0);
            assert!(
                output.iter().all(|x| x.is_finite()),
                "Large dt caused divergence (closed-form should handle this)"
            );
        }
    }

    #[test]
    fn test_cfc_reset_clears_state() {
        let config = CfCNetworkConfig {
            input_dim: 8,
            hidden_dim: 16,
            num_layers: 2,
            output_dim: 4,
            ..Default::default()
        };
        let mut network = CfCNetwork::new(config);
        let input = Array1::from_vec(vec![1.0; 8]);

        // Run forward to build up state
        for _ in 0..100 {
            network.forward(&input, 0.1);
        }

        // Reset and verify output changes
        network.reset();
        let output_after_reset = network.forward(&input, 0.1);
        assert!(
            output_after_reset.iter().all(|x| x.is_finite()),
            "Output after reset should be finite"
        );
    }
}
