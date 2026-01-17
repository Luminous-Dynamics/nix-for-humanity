//! # Cincinnati LTC: Liquid Time-Constant Networks for Consciousness
//!
//! Integrates Liquid Time-Constant (LTC) neural networks with the Cincinnati
//! consciousness architecture for continuous-time cognitive processing.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use crate::hdc::RealHV;

/// Configuration for Cincinnati LTC
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CincinnatiLTCConfig {
    /// Number of LTC neurons
    pub num_neurons: usize,
    /// Input dimension
    pub input_dim: usize,
    /// Output dimension
    pub output_dim: usize,
    /// Time constant range
    pub tau_range: (f32, f32),
    /// Integration step size
    pub dt: f32,
    /// Enable consciousness integration
    pub consciousness_enabled: bool,
}

impl Default for CincinnatiLTCConfig {
    fn default() -> Self {
        Self {
            num_neurons: 128,
            input_dim: 512,
            output_dim: 512,
            tau_range: (0.1, 10.0),
            dt: 0.01,
            consciousness_enabled: true,
        }
    }
}

/// State of an LTC neuron
#[derive(Debug, Clone)]
pub struct LTCNeuronState {
    /// Hidden state
    pub hidden: f32,
    /// Time constant (tau)
    pub tau: f32,
    /// Sensitivity parameter
    pub sensitivity: f32,
    /// Bias
    pub bias: f32,
}

impl LTCNeuronState {
    /// Create a new neuron state
    pub fn new(tau: f32) -> Self {
        Self {
            hidden: 0.0,
            tau,
            sensitivity: 1.0,
            bias: 0.0,
        }
    }

    /// Update the neuron state
    pub fn update(&mut self, input: f32, dt: f32) {
        // LTC dynamics: dh/dt = (1/tau) * (-h + f(input))
        let f_input = (input * self.sensitivity + self.bias).tanh();
        let dh = (1.0 / self.tau) * (-self.hidden + f_input);
        self.hidden += dh * dt;
    }
}

/// A layer of LTC neurons
#[derive(Debug)]
pub struct LTCLayer {
    /// Neuron states
    neurons: Vec<LTCNeuronState>,
    /// Input weights
    weights_in: Vec<Vec<f32>>,
    /// Recurrent weights
    weights_rec: Vec<Vec<f32>>,
    /// Configuration
    config: CincinnatiLTCConfig,
}

impl LTCLayer {
    /// Create a new LTC layer
    pub fn new(config: CincinnatiLTCConfig) -> Self {
        let mut neurons = Vec::with_capacity(config.num_neurons);
        let mut rng = rand::thread_rng();

        for i in 0..config.num_neurons {
            let tau = config.tau_range.0 +
                (i as f32 / config.num_neurons as f32) * (config.tau_range.1 - config.tau_range.0);
            neurons.push(LTCNeuronState::new(tau));
        }

        // Initialize weights
        let weights_in = (0..config.num_neurons)
            .map(|_| (0..config.input_dim)
                .map(|_| (rand::random::<f32>() - 0.5) * 0.1)
                .collect())
            .collect();

        let weights_rec = (0..config.num_neurons)
            .map(|_| (0..config.num_neurons)
                .map(|_| (rand::random::<f32>() - 0.5) * 0.1)
                .collect())
            .collect();

        Self {
            neurons,
            weights_in,
            weights_rec,
            config,
        }
    }

    /// Forward pass through the layer
    pub fn forward(&mut self, input: &[f32]) -> Vec<f32> {
        let num_neurons = self.neurons.len();

        // Get current hidden states
        let current_hidden: Vec<f32> = self.neurons.iter().map(|n| n.hidden).collect();

        // Update each neuron
        for i in 0..num_neurons {
            // Compute input contribution
            let mut total_input = 0.0;

            // Input weights
            for (j, &x) in input.iter().enumerate().take(self.config.input_dim) {
                if j < self.weights_in[i].len() {
                    total_input += self.weights_in[i][j] * x;
                }
            }

            // Recurrent weights
            for j in 0..num_neurons {
                total_input += self.weights_rec[i][j] * current_hidden[j];
            }

            self.neurons[i].update(total_input, self.config.dt);
        }

        self.neurons.iter().map(|n| n.hidden).collect()
    }

    /// Get hidden states
    pub fn hidden_states(&self) -> Vec<f32> {
        self.neurons.iter().map(|n| n.hidden).collect()
    }

    /// Reset hidden states
    pub fn reset(&mut self) {
        for neuron in &mut self.neurons {
            neuron.hidden = 0.0;
        }
    }
}

/// The Cincinnati LTC network
#[derive(Debug)]
pub struct CincinnatiLTC {
    /// Configuration
    config: CincinnatiLTCConfig,
    /// LTC layers
    layers: Vec<LTCLayer>,
    /// Consciousness integration weights
    consciousness_weights: Vec<f32>,
    /// Current consciousness level
    consciousness_level: f64,
    /// Statistics
    stats: CincinnatiLTCStats,
}

/// Statistics for Cincinnati LTC
#[derive(Debug, Clone, Default)]
pub struct CincinnatiLTCStats {
    /// Total forward passes
    pub forward_passes: u64,
    /// Total time simulated
    pub total_time: f64,
    /// Average hidden state magnitude
    pub avg_hidden_magnitude: f32,
    /// Peak consciousness level
    pub peak_consciousness: f64,
}

impl CincinnatiLTC {
    /// Create a new Cincinnati LTC network
    pub fn new(config: CincinnatiLTCConfig) -> Self {
        let layer = LTCLayer::new(config.clone());
        let consciousness_weights = vec![1.0 / config.num_neurons as f32; config.num_neurons];

        Self {
            config,
            layers: vec![layer],
            consciousness_weights,
            consciousness_level: 0.0,
            stats: CincinnatiLTCStats::default(),
        }
    }

    /// Forward pass through the network
    pub fn forward(&mut self, input: &RealHV) -> RealHV {
        self.stats.forward_passes += 1;

        let input_slice = input.as_slice();
        let mut current = input_slice.to_vec();

        // Process through layers
        for layer in &mut self.layers {
            current = layer.forward(&current);
        }

        // Update consciousness level if enabled
        if self.config.consciousness_enabled {
            self.update_consciousness(&current);
        }

        // Pad or truncate to output dimension
        current.resize(self.config.output_dim, 0.0);

        // Update statistics
        let magnitude: f32 = current.iter().map(|v| v * v).sum::<f32>().sqrt();
        let n = self.stats.forward_passes as f32;
        self.stats.avg_hidden_magnitude =
            (self.stats.avg_hidden_magnitude * (n - 1.0) + magnitude) / n;

        RealHV::from_slice(&current)
    }

    /// Update consciousness level based on network state
    fn update_consciousness(&mut self, hidden: &[f32]) {
        // Simple phi approximation: information integration
        let mut total = 0.0f64;

        for (i, &h) in hidden.iter().enumerate() {
            if i < self.consciousness_weights.len() {
                total += (h * self.consciousness_weights[i]) as f64;
            }
        }

        // Integrate over time
        self.consciousness_level = 0.9 * self.consciousness_level + 0.1 * total.abs();

        if self.consciousness_level > self.stats.peak_consciousness {
            self.stats.peak_consciousness = self.consciousness_level;
        }
    }

    /// Step the network by dt
    pub fn step(&mut self, input: &RealHV) -> RealHV {
        self.stats.total_time += self.config.dt as f64;
        self.forward(input)
    }

    /// Get current consciousness level
    pub fn consciousness_level(&self) -> f64 {
        self.consciousness_level
    }

    /// Get hidden states
    pub fn hidden_states(&self) -> Vec<f32> {
        if let Some(layer) = self.layers.first() {
            layer.hidden_states()
        } else {
            Vec::new()
        }
    }

    /// Reset the network
    pub fn reset(&mut self) {
        for layer in &mut self.layers {
            layer.reset();
        }
        self.consciousness_level = 0.0;
    }

    /// Get statistics
    pub fn stats(&self) -> &CincinnatiLTCStats {
        &self.stats
    }
}

impl Default for CincinnatiLTC {
    fn default() -> Self {
        Self::new(CincinnatiLTCConfig::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ltc_neuron() {
        let mut neuron = LTCNeuronState::new(1.0);
        neuron.update(1.0, 0.01);
        assert!(neuron.hidden != 0.0);
    }

    #[test]
    fn test_ltc_layer() {
        let config = CincinnatiLTCConfig {
            num_neurons: 16,
            input_dim: 8,
            ..Default::default()
        };
        let mut layer = LTCLayer::new(config);

        let input = vec![0.5f32; 8];
        let output = layer.forward(&input);

        assert_eq!(output.len(), 16);
    }

    #[test]
    fn test_cincinnati_ltc() {
        let mut ltc = CincinnatiLTC::default();
        let input = RealHV::random(512);

        let output = ltc.forward(&input);
        assert_eq!(output.dimension(), 512);
    }

    #[test]
    fn test_consciousness_integration() {
        let mut ltc = CincinnatiLTC::default();

        // Run several steps
        for _ in 0..100 {
            ltc.step(&RealHV::random(512));
        }

        // Consciousness should have accumulated
        assert!(ltc.consciousness_level() > 0.0);
    }
}
