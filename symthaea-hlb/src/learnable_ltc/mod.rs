//! Learnable Liquid Time-Constant (LTC) Neural Networks
//!
//! Implementation of continuous-time recurrent neural networks with learnable
//! time constants, inspired by neural ODE solvers and biological neural dynamics.
//!
//! LTC networks excel at:
//! - Temporal pattern recognition
//! - Continuous-time dynamics modeling
//! - Adaptive time-scale learning
//!
//! ## References
//! - Hasani et al. (2020): "Liquid Time-constant Networks"
//! - Chen et al. (2018): "Neural Ordinary Differential Equations"

use anyhow::Result;
use rand::Rng;
use serde::{Deserialize, Serialize};

/// Configuration for a Learnable LTC network
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearnableLTCConfig {
    /// Number of LTC neurons
    pub num_neurons: usize,

    /// Input dimension
    pub input_dim: usize,

    /// Output dimension
    pub output_dim: usize,

    /// Number of integration steps per forward pass
    pub num_steps: usize,

    /// Time step for ODE integration (dt)
    pub dt: f32,

    /// Learning rate for weight updates
    pub learning_rate: f32,

    /// Time constant bounds (min, max)
    pub tau_bounds: (f32, f32),

    /// Noise scale for exploration
    pub noise_scale: f32,

    /// Whether to use layer normalization
    pub use_layer_norm: bool,

    /// Backbone type (e.g., "dense", "sparse")
    pub backbone: String,
}

impl Default for LearnableLTCConfig {
    fn default() -> Self {
        Self {
            num_neurons: 256,
            input_dim: 64,
            output_dim: 32,
            num_steps: 50,
            dt: 0.01,
            learning_rate: 0.001,
            tau_bounds: (0.1, 10.0),
            noise_scale: 0.01,
            use_layer_norm: true,
            backbone: "dense".to_string(),
        }
    }
}

/// LTC Neural State
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct LTCState {
    /// Hidden state of neurons
    pub hidden: Vec<f32>,

    /// Time constants per neuron
    pub tau: Vec<f32>,

    /// Current time
    pub time: f32,
}

impl LTCState {
    /// Create a new state with zeros
    pub fn zeros(num_neurons: usize) -> Self {
        Self {
            hidden: vec![0.0; num_neurons],
            tau: vec![1.0; num_neurons],
            time: 0.0,
        }
    }

    /// Create with random initialization
    pub fn random(num_neurons: usize, seed: u64) -> Self {
        use rand::SeedableRng;
        let mut rng = rand_chacha::ChaCha8Rng::seed_from_u64(seed);

        let hidden: Vec<f32> = (0..num_neurons)
            .map(|_| rng.gen_range(-0.1..0.1))
            .collect();

        let tau: Vec<f32> = (0..num_neurons)
            .map(|_| rng.gen_range(0.5..2.0))
            .collect();

        Self {
            hidden,
            tau,
            time: 0.0,
        }
    }
}

/// Learnable Liquid Time-Constant Neural Network
#[derive(Serialize, Deserialize)]
pub struct LearnableLTC {
    /// Configuration
    config: LearnableLTCConfig,

    /// Input weights (num_neurons x input_dim)
    w_in: Vec<f32>,

    /// Recurrent weights (num_neurons x num_neurons)
    w_rec: Vec<f32>,

    /// Output weights (output_dim x num_neurons)
    w_out: Vec<f32>,

    /// Input bias
    b_in: Vec<f32>,

    /// Recurrent bias
    b_rec: Vec<f32>,

    /// Output bias
    b_out: Vec<f32>,

    /// Learnable time constants
    tau: Vec<f32>,

    /// Learnable time constant sensitivities (how tau responds to input)
    tau_sens: Vec<f32>,

    /// Current state
    #[serde(skip)]
    state: LTCState,

    /// Layer norm parameters (gamma, beta) if enabled
    layer_norm_gamma: Vec<f32>,
    layer_norm_beta: Vec<f32>,
}

impl LearnableLTC {
    /// Create a new LTC network
    pub fn new(config: LearnableLTCConfig) -> Result<Self> {
        let n = config.num_neurons;
        let i = config.input_dim;
        let o = config.output_dim;

        // Xavier initialization
        let init_scale_in = (6.0 / (n + i) as f32).sqrt();
        let init_scale_rec = (6.0 / (n + n) as f32).sqrt();
        let init_scale_out = (6.0 / (o + n) as f32).sqrt();

        let mut rng = rand::thread_rng();

        // Initialize weights
        let w_in: Vec<f32> = (0..(n * i))
            .map(|_| rng.gen_range(-init_scale_in..init_scale_in))
            .collect();

        let w_rec: Vec<f32> = (0..(n * n))
            .map(|_| rng.gen_range(-init_scale_rec..init_scale_rec))
            .collect();

        let w_out: Vec<f32> = (0..(o * n))
            .map(|_| rng.gen_range(-init_scale_out..init_scale_out))
            .collect();

        // Initialize time constants
        let tau: Vec<f32> = (0..n)
            .map(|_| rng.gen_range(config.tau_bounds.0..config.tau_bounds.1))
            .collect();

        let tau_sens: Vec<f32> = (0..n)
            .map(|_| rng.gen_range(0.0..0.1))
            .collect();

        // Layer norm parameters
        let layer_norm_gamma = vec![1.0; n];
        let layer_norm_beta = vec![0.0; n];

        Ok(Self {
            config: config.clone(),
            w_in,
            w_rec,
            w_out,
            b_in: vec![0.0; n],
            b_rec: vec![0.0; n],
            b_out: vec![0.0; o],
            tau,
            tau_sens,
            state: LTCState::zeros(n),
            layer_norm_gamma,
            layer_norm_beta,
        })
    }

    /// Forward pass through the LTC network
    ///
    /// Returns (output, final_state)
    pub fn forward(&mut self, input: &[f32]) -> Result<(Vec<f32>, LTCState)> {
        let n = self.config.num_neurons;
        let dt = self.config.dt;

        // Ensure input dimension matches
        if input.len() != self.config.input_dim {
            anyhow::bail!(
                "Input dimension mismatch: expected {}, got {}",
                self.config.input_dim,
                input.len()
            );
        }

        // Compute input contribution: W_in * x + b_in
        let mut input_contrib = vec![0.0; n];
        for j in 0..n {
            for k in 0..self.config.input_dim {
                input_contrib[j] += self.w_in[j * self.config.input_dim + k] * input[k];
            }
            input_contrib[j] += self.b_in[j];
        }

        // ODE integration (Euler method for simplicity)
        for _ in 0..self.config.num_steps {
            // Compute recurrent contribution: W_rec * h + b_rec
            let mut rec_contrib = vec![0.0; n];
            for j in 0..n {
                for k in 0..n {
                    rec_contrib[j] += self.w_rec[j * n + k] * self.state.hidden[k];
                }
                rec_contrib[j] += self.b_rec[j];
            }

            // Compute effective time constant (input-dependent)
            let mut effective_tau = vec![0.0; n];
            for j in 0..n {
                // tau can be modulated by input strength
                let input_strength: f32 = input_contrib[j].abs();
                effective_tau[j] = self.tau[j] * (1.0 + self.tau_sens[j] * input_strength);
                // Clamp to bounds
                effective_tau[j] = effective_tau[j].clamp(
                    self.config.tau_bounds.0,
                    self.config.tau_bounds.1,
                );
            }

            // LTC dynamics: dh/dt = (1/tau) * (-h + f(input + recurrent))
            for j in 0..n {
                let activation = (input_contrib[j] + rec_contrib[j]).tanh();
                let dh = (1.0 / effective_tau[j]) * (-self.state.hidden[j] + activation);
                self.state.hidden[j] += dh * dt;
            }

            // Optional layer normalization
            if self.config.use_layer_norm {
                self.apply_layer_norm();
            }

            self.state.time += dt;
        }

        // Compute output: W_out * h + b_out
        let mut output = vec![0.0; self.config.output_dim];
        for j in 0..self.config.output_dim {
            for k in 0..n {
                output[j] += self.w_out[j * n + k] * self.state.hidden[k];
            }
            output[j] += self.b_out[j];
        }

        Ok((output, self.state.clone()))
    }

    /// Apply layer normalization to hidden state
    fn apply_layer_norm(&mut self) {
        let n = self.config.num_neurons;

        // Compute mean and variance
        let mean: f32 = self.state.hidden.iter().sum::<f32>() / n as f32;
        let var: f32 = self.state.hidden
            .iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f32>()
            / n as f32;

        let std = (var + 1e-5).sqrt();

        // Normalize and apply learned parameters
        for j in 0..n {
            let normalized = (self.state.hidden[j] - mean) / std;
            self.state.hidden[j] = self.layer_norm_gamma[j] * normalized + self.layer_norm_beta[j];
        }
    }

    /// Reset the network state
    pub fn reset(&mut self) {
        self.state = LTCState::zeros(self.config.num_neurons);
    }

    /// Reset with random state
    pub fn reset_random(&mut self, seed: u64) {
        self.state = LTCState::random(self.config.num_neurons, seed);
    }

    /// Get current state
    pub fn state(&self) -> &LTCState {
        &self.state
    }

    /// Get configuration
    pub fn config(&self) -> &LearnableLTCConfig {
        &self.config
    }

    /// Get time constants
    pub fn time_constants(&self) -> &[f32] {
        &self.tau
    }

    /// Compute gradients for learning (simplified placeholder)
    pub fn backward(&mut self, _loss: f32) -> Result<()> {
        // Placeholder for backpropagation through time
        // In a full implementation, this would compute gradients and update weights
        Ok(())
    }

    /// Step the optimizer (update weights based on gradients)
    pub fn optimizer_step(&mut self) {
        // Placeholder for optimizer step
        // In a full implementation, this would apply gradient updates
    }

    /// Zero gradients before backward pass
    pub fn zero_grad(&mut self) {
        // Placeholder for zeroing gradients
    }

    /// Reset network state (alias for reset for API compatibility)
    pub fn reset_state(&mut self) {
        self.reset();
    }

    /// Train step: forward pass, compute loss, backward pass, optimizer step
    pub fn train_step(&mut self, input: &[f32], target: &[f32]) -> Result<f32> {
        // Forward pass
        let (output, _state) = self.forward(input)?;

        // Compute MSE loss
        let loss: f32 = output.iter()
            .zip(target.iter())
            .map(|(o, t)| (o - t).powi(2))
            .sum::<f32>() / output.len() as f32;

        // Backward pass and optimizer step (placeholder implementation)
        self.zero_grad();
        self.backward(loss)?;
        self.optimizer_step();

        Ok(loss)
    }

    /// Get tau distribution statistics: (mean, std, min, max)
    pub fn get_tau_distribution(&self) -> (f32, f32, f32, f32) {
        let n = self.tau.len() as f32;
        if n == 0.0 {
            return (0.0, 0.0, 0.0, 0.0);
        }

        let mean = self.tau.iter().sum::<f32>() / n;
        let variance = self.tau.iter()
            .map(|&t| (t - mean).powi(2))
            .sum::<f32>() / n;
        let std = variance.sqrt();
        let min = self.tau.iter().cloned().fold(f32::INFINITY, f32::min);
        let max = self.tau.iter().cloned().fold(f32::NEG_INFINITY, f32::max);

        (mean, std, min, max)
    }
}

impl std::fmt::Debug for LearnableLTC {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("LearnableLTC")
            .field("config", &self.config)
            .field("num_weights", &(self.w_in.len() + self.w_rec.len() + self.w_out.len()))
            .field("state_time", &self.state.time)
            .finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ltc_creation() {
        let config = LearnableLTCConfig::default();
        let ltc = LearnableLTC::new(config).unwrap();
        assert_eq!(ltc.config.num_neurons, 256);
    }

    #[test]
    fn test_ltc_forward() {
        let config = LearnableLTCConfig {
            num_neurons: 32,
            input_dim: 8,
            output_dim: 4,
            num_steps: 10,
            ..Default::default()
        };
        let mut ltc = LearnableLTC::new(config).unwrap();

        let input = vec![0.1; 8];
        let (output, state) = ltc.forward(&input).unwrap();

        assert_eq!(output.len(), 4);
        assert_eq!(state.hidden.len(), 32);
    }

    #[test]
    fn test_ltc_reset() {
        let config = LearnableLTCConfig {
            num_neurons: 16,
            input_dim: 4,
            output_dim: 2,
            num_steps: 5,
            ..Default::default()
        };
        let mut ltc = LearnableLTC::new(config).unwrap();

        // Run forward
        let input = vec![0.5; 4];
        ltc.forward(&input).unwrap();

        // Reset and check state is zeroed
        ltc.reset();
        assert!(ltc.state.hidden.iter().all(|&x| x == 0.0));
    }
}
