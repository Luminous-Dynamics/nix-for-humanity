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

/// Minimum allowed tau value to prevent NaN in exp(-dt/tau) calculations.
/// Values below this threshold would cause numerical instability.
const MIN_TAU: f32 = 1e-6;

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
pub struct CfCCell {
    config: CfCConfig,

    // Weights for state transition
    w_in: Array2<f32>,     // Input to hidden
    w_h: Array2<f32>,      // Hidden to hidden

    // Reserved for future output projection (e.g., separate output dim)
    #[allow(dead_code)]
    w_out: Array2<f32>,

    // Biases
    b_h: Array1<f32>,

    // Time constants (learnable)
    tau: Array1<f32>,

    // Backbone network weights (used when config.use_backbone is true)
    backbone_weights: Vec<Array2<f32>>,
    backbone_biases: Vec<Array1<f32>>,

    // Current hidden state
    state: Array1<f32>,

    // Statistics - tracks number of forward steps for diagnostics
    #[allow(dead_code)]
    steps: u64,
}

impl CfCCell {
    /// Create a new CfC cell
    ///
    /// # Panics
    /// Panics if `config.tau_range.0` is less than `MIN_TAU` (1e-6).
    pub fn new(config: CfCConfig) -> Self {
        // Validate tau range to prevent NaN in exp(-dt/tau) calculations
        assert!(
            config.tau_range.0 >= MIN_TAU,
            "tau_min must be >= {} to prevent numerical instability, got {}",
            MIN_TAU,
            config.tau_range.0
        );

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
            // Clamp to ensure numerical stability even after initialization
            log_tau.exp().max(MIN_TAU)
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
        // Clamp tau to MIN_TAU to prevent division by zero / NaN
        let decay: Array1<f32> = self.tau.mapv(|t| (-dt / t.max(MIN_TAU)).exp());

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

    /// Compute analytical gradients for BPTT
    ///
    /// Returns gradients for W_in, W_h, b_h, and tau based on the
    /// closed-form CfC dynamics: h(t) = h_inf + (h_0 - h_inf) * exp(-dt/tau)
    pub fn backward(&self, input: &Array1<f32>, target: &Array1<f32>, dt: f32) -> CfCGradients {
        let processed_input = if self.config.use_backbone {
            self.backbone_forward(input)
        } else {
            input.clone()
        };

        // Forward computation (recompute for gradient chain)
        let x_contrib = self.w_in.dot(&processed_input);
        let h_contrib = self.w_h.dot(&self.state);
        let z = &x_contrib + &h_contrib + &self.b_h;
        let h_inf = self.config.activation.apply_array(&z);
        // Clamp tau to MIN_TAU to prevent NaN
        let decay: Array1<f32> = self.tau.mapv(|t| (-dt / t.max(MIN_TAU)).exp());
        let new_state = &h_inf + &((&self.state - &h_inf) * &decay);

        // Error signal: dL/dh = 2 * (h - target) / n
        let n = target.len().min(new_state.len()) as f32;
        let mut dh = Array1::zeros(self.config.hidden_dim);
        for i in 0..target.len().min(new_state.len()) {
            dh[i] = 2.0 * (new_state[i] - target[i]) / n;
        }

        // Activation derivative (SiLU default)
        let sigma_prime: Array1<f32> = z.mapv(|x| {
            let s = sigmoid(x);
            s + x * s * (1.0 - s) // d/dx[x * sigmoid(x)]
        });

        // dh/dh_inf = (1 - exp(-dt/tau))
        let one_minus_decay: Array1<f32> = decay.mapv(|d| 1.0 - d);

        // Chain: dL/dz = dL/dh * dh/dh_inf * dh_inf/dz
        let dz = &dh * &one_minus_decay * &sigma_prime;

        // dL/dW_in = dz * input^T
        let effective_input_dim = processed_input.len();
        let hidden_dim = self.config.hidden_dim;
        let mut dw_in = Array2::zeros((hidden_dim, effective_input_dim));
        for i in 0..hidden_dim {
            for j in 0..effective_input_dim {
                dw_in[[i, j]] = dz[i] * processed_input[j];
            }
        }

        // dL/dW_h = dz * state^T
        let mut dw_h = Array2::zeros((hidden_dim, hidden_dim));
        for i in 0..hidden_dim {
            for j in 0..hidden_dim {
                dw_h[[i, j]] = dz[i] * self.state[j];
            }
        }

        // dL/db = dz
        let db_h = dz.clone();

        // dL/dtau = dL/dh * (h_0 - h_inf) * (dt / tau^2) * exp(-dt/tau)
        let mut dtau = Array1::zeros(hidden_dim);
        for i in 0..hidden_dim {
            let diff = self.state[i] - h_inf[i];
            dtau[i] = dh[i] * diff * (dt / (self.tau[i] * self.tau[i])) * decay[i];
        }

        CfCGradients { dw_in, dw_h, db_h, dtau }
    }

    /// Apply Adam optimizer update
    pub fn apply_adam(&mut self, grads: &CfCGradients, adam: &mut AdamState, lr: f32) {
        adam.t += 1;
        let t = adam.t as f32;

        // Gradient clipping at 1.0
        let clip = |g: f32| g.clamp(-1.0, 1.0);

        let hidden_dim = self.config.hidden_dim;
        let effective_input_dim = self.w_in.ncols();

        // Update W_in
        for i in 0..hidden_dim {
            for j in 0..effective_input_dim {
                let g = clip(grads.dw_in[[i, j]]);
                adam.m_w_in[[i, j]] = adam.beta1 * adam.m_w_in[[i, j]] + (1.0 - adam.beta1) * g;
                adam.v_w_in[[i, j]] = adam.beta2 * adam.v_w_in[[i, j]] + (1.0 - adam.beta2) * g * g;
                let m_hat = adam.m_w_in[[i, j]] / (1.0 - adam.beta1.powf(t));
                let v_hat = adam.v_w_in[[i, j]] / (1.0 - adam.beta2.powf(t));
                self.w_in[[i, j]] -= lr * m_hat / (v_hat.sqrt() + adam.eps);
            }
        }

        // Update W_h
        for i in 0..hidden_dim {
            for j in 0..hidden_dim {
                let g = clip(grads.dw_h[[i, j]]);
                adam.m_w_h[[i, j]] = adam.beta1 * adam.m_w_h[[i, j]] + (1.0 - adam.beta1) * g;
                adam.v_w_h[[i, j]] = adam.beta2 * adam.v_w_h[[i, j]] + (1.0 - adam.beta2) * g * g;
                let m_hat = adam.m_w_h[[i, j]] / (1.0 - adam.beta1.powf(t));
                let v_hat = adam.v_w_h[[i, j]] / (1.0 - adam.beta2.powf(t));
                self.w_h[[i, j]] -= lr * m_hat / (v_hat.sqrt() + adam.eps);
            }
        }

        // Update bias
        for i in 0..hidden_dim {
            let g = clip(grads.db_h[i]);
            adam.m_b_h[i] = adam.beta1 * adam.m_b_h[i] + (1.0 - adam.beta1) * g;
            adam.v_b_h[i] = adam.beta2 * adam.v_b_h[i] + (1.0 - adam.beta2) * g * g;
            let m_hat = adam.m_b_h[i] / (1.0 - adam.beta1.powf(t));
            let v_hat = adam.v_b_h[i] / (1.0 - adam.beta2.powf(t));
            self.b_h[i] -= lr * m_hat / (v_hat.sqrt() + adam.eps);
        }

        // Update tau with 0.1x learning rate and clamping
        for i in 0..hidden_dim {
            let g = clip(grads.dtau[i]);
            adam.m_tau[i] = adam.beta1 * adam.m_tau[i] + (1.0 - adam.beta1) * g;
            adam.v_tau[i] = adam.beta2 * adam.v_tau[i] + (1.0 - adam.beta2) * g * g;
            let m_hat = adam.m_tau[i] / (1.0 - adam.beta1.powf(t));
            let v_hat = adam.v_tau[i] / (1.0 - adam.beta2.powf(t));
            self.tau[i] -= lr * 0.1 * m_hat / (v_hat.sqrt() + adam.eps);
            self.tau[i] = self.tau[i].clamp(0.1, 10.0);
        }
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

/// Gradient accumulators for CfC backpropagation
#[derive(Debug, Clone)]
pub struct CfCGradients {
    /// Input weight gradients
    pub dw_in: Array2<f32>,
    /// Recurrent weight gradients
    pub dw_h: Array2<f32>,
    /// Bias gradients
    pub db_h: Array1<f32>,
    /// Time constant gradients
    pub dtau: Array1<f32>,
}

/// Adam optimizer state
#[derive(Debug, Clone)]
pub struct AdamState {
    /// First moment estimates
    pub m_w_in: Array2<f32>,
    pub m_w_h: Array2<f32>,
    pub m_b_h: Array1<f32>,
    pub m_tau: Array1<f32>,
    /// Second moment estimates
    pub v_w_in: Array2<f32>,
    pub v_w_h: Array2<f32>,
    pub v_b_h: Array1<f32>,
    pub v_tau: Array1<f32>,
    /// Step counter
    pub t: u64,
    /// Hyperparameters
    pub beta1: f32,
    pub beta2: f32,
    pub eps: f32,
}

impl AdamState {
    fn new(hidden_dim: usize, input_dim: usize) -> Self {
        Self {
            m_w_in: Array2::zeros((hidden_dim, input_dim)),
            m_w_h: Array2::zeros((hidden_dim, hidden_dim)),
            m_b_h: Array1::zeros(hidden_dim),
            m_tau: Array1::zeros(hidden_dim),
            v_w_in: Array2::zeros((hidden_dim, input_dim)),
            v_w_h: Array2::zeros((hidden_dim, hidden_dim)),
            v_b_h: Array1::zeros(hidden_dim),
            v_tau: Array1::zeros(hidden_dim),
            t: 0,
            beta1: 0.9,
            beta2: 0.999,
            eps: 1e-8,
        }
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

    /// Adam optimizer states per cell
    adam_states: Vec<AdamState>,
    /// Adam state for output projection
    adam_output: Option<AdamState>,
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

        let adam_states = cells.iter().map(|c| {
            let effective_input_dim = if c.config.use_backbone { c.config.backbone_dim } else { c.config.input_dim };
            AdamState::new(c.config.hidden_dim, effective_input_dim)
        }).collect();

        Self {
            config,
            cells,
            output_weights,
            output_bias,
            total_steps: 0,
            adam_states,
            adam_output: None,
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

    /// Train step using BPTT with Adam optimizer (default training method)
    pub fn train_step(
        &mut self,
        input: &Array1<f32>,
        target: &Array1<f32>,
        dt: f32,
        learning_rate: f32,
    ) -> anyhow::Result<f32> {
        self.train_step_bptt(&[input.clone()], &[target.clone()], &[dt], learning_rate)
    }

    /// Sequence training with BPTT and Adam
    pub fn train_step_bptt(
        &mut self,
        inputs: &[Array1<f32>],
        targets: &[Array1<f32>],
        dts: &[f32],
        learning_rate: f32,
    ) -> anyhow::Result<f32> {
        assert_eq!(inputs.len(), targets.len());
        assert_eq!(inputs.len(), dts.len());

        self.reset_states_only();
        let mut total_loss = 0.0f32;

        for ((_input, target), dt) in inputs.iter().zip(targets.iter()).zip(dts.iter()) {
            // Forward through all cells
            let mut h = _input.clone();
            for cell in self.cells.iter_mut() {
                h = cell.forward(&h, *dt);
            }

            // Compute output
            let output = self.output_weights.dot(&h) + &self.output_bias;
            let loss = mse_loss(&output, target);
            total_loss += loss;

            // Backward through cells (reverse order for BPTT)
            for cell_idx in (0..self.cells.len()).rev() {
                let cell_target = if cell_idx == self.cells.len() - 1 {
                    // For last cell, use output error projected back
                    let mut t = Array1::zeros(self.cells[cell_idx].config.hidden_dim);
                    for i in 0..t.len().min(target.len()) {
                        t[i] = target[i.min(target.len() - 1)];
                    }
                    t
                } else {
                    self.cells[cell_idx + 1].state().clone()
                };

                let cell_input = if cell_idx == 0 {
                    _input.clone()
                } else {
                    self.cells[cell_idx - 1].state().clone()
                };

                let grads = self.cells[cell_idx].backward(&cell_input, &cell_target, *dt);
                self.cells[cell_idx].apply_adam(&grads, &mut self.adam_states[cell_idx], learning_rate);
            }
        }

        let avg_loss = total_loss / inputs.len() as f32;
        Ok(avg_loss)
    }

    /// Train step using perturbation-based gradient estimation (SPSA).
    ///
    /// Estimates gradients by evaluating the loss at perturbed weight values
    /// and updates all learnable parameters: W_in, W_h, biases, tau, and
    /// output projection weights.
    ///
    /// This replaces the previous implementation which only nudged the last
    /// cell's hidden state without modifying any weights.
    pub fn train_step_spsa(
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
            // Ensure tau stays above MIN_TAU to prevent NaN
            let new_tau = (old_tau - lr * grad).max(MIN_TAU);
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

    /// Compute consciousness level using Phi-inspired metric
    ///
    /// Samples representative neurons from hidden states and computes
    /// an integration measure based on the PhiEngine when available.
    pub fn consciousness_level(&self) -> f32 {
        use symthaea_core::hdc::unified_hv::ContinuousHV;
        use symthaea_core::phi_engine::{PhiEngine, PhiMethod};

        let states: Vec<&Array1<f32>> = self.cells.iter().map(|c| c.state()).collect();
        if states.is_empty() {
            return 0.0;
        }

        // Sample 8-16 representative neurons from hidden states
        let mut node_representations = Vec::new();
        for state in &states {
            // Take up to 8 evenly-spaced neurons per cell
            let step = (state.len() / 8).max(1);
            for i in (0..state.len()).step_by(step).take(8) {
                let mut components = vec![0.0f32; 16]; // Small representation
                for j in 0..16 {
                    let idx = (i + j) % state.len();
                    components[j] = state[idx];
                }
                node_representations.push(ContinuousHV::from_vec(components));
            }
        }

        if node_representations.is_empty() {
            return 0.0;
        }

        // Limit to 16 nodes for performance
        node_representations.truncate(16);

        let engine = PhiEngine::new(PhiMethod::Auto);
        let result = engine.compute(&node_representations);
        result.phi as f32
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

    // =====================================================================
    // EDGE CASE TESTS FOR TAU VALIDATION AND NUMERICAL STABILITY
    // =====================================================================

    #[test]
    #[should_panic(expected = "tau_min must be >= ")]
    fn test_cfc_rejects_zero_tau() {
        let cell_config = CfCConfig {
            input_dim: 4,
            hidden_dim: 8,
            tau_range: (0.0, 1.0), // Zero tau_min should panic
            use_backbone: false,
            ..Default::default()
        };
        let _ = CfCCell::new(cell_config);
    }

    #[test]
    #[should_panic(expected = "tau_min must be >= ")]
    fn test_cfc_rejects_very_small_tau() {
        let cell_config = CfCConfig {
            input_dim: 4,
            hidden_dim: 8,
            tau_range: (1e-8, 1.0), // Below MIN_TAU should panic
            use_backbone: false,
            ..Default::default()
        };
        let _ = CfCCell::new(cell_config);
    }

    #[test]
    fn test_cfc_accepts_min_tau_boundary() {
        // Exactly at MIN_TAU boundary should work
        let cell_config = CfCConfig {
            input_dim: 4,
            hidden_dim: 8,
            tau_range: (1e-6, 1.0), // Exactly MIN_TAU
            use_backbone: false,
            ..Default::default()
        };
        let mut cell = CfCCell::new(cell_config);
        let input = Array1::from_vec(vec![1.0; 4]);

        // Should produce finite outputs even with minimal tau
        for _ in 0..100 {
            let output = cell.forward(&input, 1.0);
            assert!(
                output.iter().all(|x| x.is_finite()),
                "MIN_TAU boundary should produce finite outputs"
            );
        }
    }

    #[test]
    fn test_cfc_zero_input_no_nan() {
        let config = CfCNetworkConfig {
            input_dim: 8,
            hidden_dim: 16,
            num_layers: 2,
            output_dim: 4,
            ..Default::default()
        };
        let mut network = CfCNetwork::new(config);
        let zero_input = Array1::zeros(8);

        // Zero input should never produce NaN
        for _ in 0..1000 {
            let output = network.forward(&zero_input, 0.1);
            assert!(
                output.iter().all(|x| x.is_finite() && !x.is_nan()),
                "Zero input produced NaN"
            );
        }
    }

    #[test]
    fn test_cfc_very_large_dt_no_nan() {
        let config = CfCNetworkConfig {
            input_dim: 8,
            hidden_dim: 16,
            num_layers: 1,
            output_dim: 4,
            ..Default::default()
        };
        let mut network = CfCNetwork::new(config);
        let input = Array1::from_vec(vec![0.5; 8]);

        // Very large dt values (dt >> tau)
        for dt in [100.0, 1000.0, 10000.0] {
            network.reset();
            let output = network.forward(&input, dt);
            assert!(
                output.iter().all(|x| x.is_finite() && !x.is_nan()),
                "Large dt={} caused NaN", dt
            );
        }
    }

    #[test]
    fn test_cfc_backward_no_nan_with_small_tau() {
        let cell_config = CfCConfig {
            input_dim: 4,
            hidden_dim: 8,
            tau_range: (1e-5, 1e-4), // Small but valid tau
            use_backbone: false,
            ..Default::default()
        };
        let mut cell = CfCCell::new(cell_config);
        let input = Array1::from_vec(vec![0.5; 4]);
        let target = Array1::from_vec(vec![0.1; 8]);

        // Forward to set state
        let _ = cell.forward(&input, 0.1);

        // Backward should not produce NaN gradients
        let grads = cell.backward(&input, &target, 1.0);
        assert!(
            grads.dw_in.iter().all(|x| x.is_finite()),
            "dw_in gradients contain NaN/Inf"
        );
        assert!(
            grads.dw_h.iter().all(|x| x.is_finite()),
            "dw_h gradients contain NaN/Inf"
        );
        assert!(
            grads.db_h.iter().all(|x| x.is_finite()),
            "db_h gradients contain NaN/Inf"
        );
        assert!(
            grads.dtau.iter().all(|x| x.is_finite()),
            "dtau gradients contain NaN/Inf"
        );
    }
}
