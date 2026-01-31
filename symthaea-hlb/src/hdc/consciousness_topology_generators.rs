//! # Consciousness Topology Generators
//!
//! Generates and manipulates network topologies for consciousness computation.
//! Different topologies affect information integration (Phi) and processing.

use symthaea_core::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Type of network topology
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TopologyType {
    /// Fully connected (all-to-all)
    FullyConnected,
    /// Small-world network
    SmallWorld,
    /// Scale-free network
    ScaleFree,
    /// Hierarchical/modular
    Hierarchical,
    /// Ring/circular
    Ring,
    /// Grid/lattice
    Grid,
    /// Random Erdos-Renyi
    Random,
    /// Layered feedforward
    Layered,
    /// Custom topology
    Custom,
}

/// A consciousness-aware network topology
#[derive(Debug, Clone)]
pub struct ConsciousnessTopology {
    /// Topology type
    pub topology_type: TopologyType,
    /// Number of nodes
    pub num_nodes: usize,
    /// Adjacency matrix (sparse representation)
    pub connections: HashMap<(usize, usize), f32>,
    /// Node embeddings
    pub node_embeddings: Vec<RealHV>,
    /// Clustering coefficient
    pub clustering: f32,
    /// Average path length
    pub avg_path_length: f32,
    /// Integration metric
    pub phi_estimate: f64,
}

impl ConsciousnessTopology {
    /// Create new topology
    pub fn new(topology_type: TopologyType, num_nodes: usize, dimension: usize) -> Self {
        let node_embeddings = (0..num_nodes)
            .map(|_| RealHV::random(dimension))
            .collect();

        let mut topology = Self {
            topology_type,
            num_nodes,
            connections: HashMap::new(),
            node_embeddings,
            clustering: 0.0,
            avg_path_length: 0.0,
            phi_estimate: 0.0,
        };

        topology.generate_connections();
        topology.compute_metrics();

        topology
    }

    /// Generate connections based on topology type
    fn generate_connections(&mut self) {
        match self.topology_type {
            TopologyType::FullyConnected => self.generate_fully_connected(),
            TopologyType::Ring => self.generate_ring(),
            TopologyType::Grid => self.generate_grid(),
            TopologyType::SmallWorld => self.generate_small_world(),
            TopologyType::Hierarchical => self.generate_hierarchical(),
            TopologyType::Random => self.generate_random(0.3),
            TopologyType::ScaleFree => self.generate_scale_free(),
            TopologyType::Layered => self.generate_layered(),
            TopologyType::Custom => {} // No auto-generation
        }
    }

    fn generate_fully_connected(&mut self) {
        for i in 0..self.num_nodes {
            for j in 0..self.num_nodes {
                if i != j {
                    self.connections.insert((i, j), 1.0);
                }
            }
        }
    }

    fn generate_ring(&mut self) {
        for i in 0..self.num_nodes {
            let next = (i + 1) % self.num_nodes;
            self.connections.insert((i, next), 1.0);
            self.connections.insert((next, i), 1.0);
        }
    }

    fn generate_grid(&mut self) {
        let side = (self.num_nodes as f64).sqrt() as usize;
        for i in 0..self.num_nodes {
            let row = i / side;
            let col = i % side;

            // Right neighbor
            if col + 1 < side {
                self.connections.insert((i, i + 1), 1.0);
                self.connections.insert((i + 1, i), 1.0);
            }
            // Bottom neighbor
            if row + 1 < side && i + side < self.num_nodes {
                self.connections.insert((i, i + side), 1.0);
                self.connections.insert((i + side, i), 1.0);
            }
        }
    }

    fn generate_small_world(&mut self) {
        // Start with ring
        self.generate_ring();

        // Add extra connections for each node (k nearest neighbors)
        let k = 2;
        for i in 0..self.num_nodes {
            for d in 2..=k {
                let next = (i + d) % self.num_nodes;
                let prev = (i + self.num_nodes - d) % self.num_nodes;
                self.connections.insert((i, next), 0.8);
                self.connections.insert((next, i), 0.8);
                self.connections.insert((i, prev), 0.8);
                self.connections.insert((prev, i), 0.8);
            }
        }

        // Rewire some edges (simplified)
        let rewire_prob = 0.1;
        let mut to_add = Vec::new();
        for &(from, to) in self.connections.keys() {
            if fastrand::f32() < rewire_prob {
                // Rewire to random node
                let new_to = fastrand::usize(0..self.num_nodes);
                if new_to != from && !self.connections.contains_key(&(from, new_to)) {
                    to_add.push(((from, new_to), 0.5));
                }
            }
        }
        for ((from, to), weight) in to_add {
            self.connections.insert((from, to), weight);
        }
    }

    fn generate_hierarchical(&mut self) {
        // Create hierarchical structure with levels
        let levels = 3;
        let nodes_per_level = self.num_nodes / levels;

        for level in 0..levels {
            let start = level * nodes_per_level;
            let end = start + nodes_per_level;

            // Connect within level (sparse)
            for i in start..end {
                for j in (i + 1)..end {
                    if fastrand::f32() < 0.3 {
                        self.connections.insert((i, j), 0.8);
                        self.connections.insert((j, i), 0.8);
                    }
                }
            }

            // Connect to next level
            if level + 1 < levels {
                let next_start = (level + 1) * nodes_per_level;
                for i in start..end {
                    let target = next_start + (i - start) % nodes_per_level;
                    self.connections.insert((i, target), 1.0);
                    self.connections.insert((target, i), 0.5);
                }
            }
        }
    }

    fn generate_random(&mut self, probability: f32) {
        for i in 0..self.num_nodes {
            for j in (i + 1)..self.num_nodes {
                if fastrand::f32() < probability {
                    self.connections.insert((i, j), 1.0);
                    self.connections.insert((j, i), 1.0);
                }
            }
        }
    }

    fn generate_scale_free(&mut self) {
        // Barabási–Albert model (simplified)
        let m = 2; // edges to add per new node

        // Start with a small clique
        for i in 0..m {
            for j in 0..m {
                if i != j {
                    self.connections.insert((i, j), 1.0);
                }
            }
        }

        // Degrees for preferential attachment
        let mut degrees: Vec<usize> = (0..self.num_nodes).map(|i| if i < m { m - 1 } else { 0 }).collect();

        for new_node in m..self.num_nodes {
            // Preferential attachment
            let total_degree: usize = degrees.iter().sum();
            let mut added = 0;

            while added < m {
                let r = fastrand::usize(0..total_degree.max(1));
                let mut cumulative = 0;
                for target in 0..new_node {
                    cumulative += degrees[target];
                    if cumulative > r && !self.connections.contains_key(&(new_node, target)) {
                        self.connections.insert((new_node, target), 1.0);
                        self.connections.insert((target, new_node), 1.0);
                        degrees[new_node] += 1;
                        degrees[target] += 1;
                        added += 1;
                        break;
                    }
                }
                if total_degree == 0 {
                    break;
                }
            }
        }
    }

    fn generate_layered(&mut self) {
        let num_layers = 4;
        let nodes_per_layer = self.num_nodes / num_layers;

        for layer in 0..(num_layers - 1) {
            let start = layer * nodes_per_layer;
            let next_start = (layer + 1) * nodes_per_layer;

            for i in start..(start + nodes_per_layer) {
                for j in next_start..(next_start + nodes_per_layer) {
                    if fastrand::f32() < 0.5 {
                        self.connections.insert((i, j), 1.0);
                    }
                }
            }
        }
    }

    /// Compute topology metrics
    fn compute_metrics(&mut self) {
        self.clustering = self.compute_clustering();
        self.avg_path_length = self.compute_avg_path_length();
        self.phi_estimate = self.estimate_phi();
    }

    fn compute_clustering(&self) -> f32 {
        // Local clustering coefficient average
        let mut total_clustering = 0.0;
        let mut count = 0;

        for node in 0..self.num_nodes {
            let neighbors: Vec<usize> = (0..self.num_nodes)
                .filter(|&j| j != node && self.connections.contains_key(&(node, j)))
                .collect();

            if neighbors.len() < 2 {
                continue;
            }

            let mut triangles = 0;
            for (i, &n1) in neighbors.iter().enumerate() {
                for &n2 in neighbors.iter().skip(i + 1) {
                    if self.connections.contains_key(&(n1, n2)) {
                        triangles += 1;
                    }
                }
            }

            let possible = neighbors.len() * (neighbors.len() - 1) / 2;
            if possible > 0 {
                total_clustering += triangles as f32 / possible as f32;
                count += 1;
            }
        }

        if count > 0 {
            total_clustering / count as f32
        } else {
            0.0
        }
    }

    fn compute_avg_path_length(&self) -> f32 {
        // Simplified: just use connectivity
        let total_edges = self.connections.len();
        if self.num_nodes > 1 {
            (self.num_nodes as f32).log2() / (total_edges as f32 / self.num_nodes as f32).max(1.0)
        } else {
            0.0
        }
    }

    fn estimate_phi(&self) -> f64 {
        // Rough phi estimate based on topology
        let connectivity = self.connections.len() as f64 / (self.num_nodes * self.num_nodes) as f64;
        let clustering_factor = self.clustering as f64;

        // Phi is higher with balanced connectivity and high clustering
        connectivity * clustering_factor * (1.0 - connectivity.abs())
    }

    /// Get connection weight
    pub fn get_connection(&self, from: usize, to: usize) -> Option<f32> {
        self.connections.get(&(from, to)).copied()
    }

    /// Set connection weight
    pub fn set_connection(&mut self, from: usize, to: usize, weight: f32) {
        self.connections.insert((from, to), weight);
    }

    /// Get neighbors of a node
    pub fn neighbors(&self, node: usize) -> Vec<usize> {
        self.connections.keys()
            .filter(|(from, _)| *from == node)
            .map(|(_, to)| *to)
            .collect()
    }
}

/// Generator for consciousness topologies
pub struct TopologyGenerator {
    dimension: usize,
}

impl TopologyGenerator {
    /// Create new generator
    pub fn new(dimension: usize) -> Self {
        Self { dimension }
    }

    /// Generate topology of specified type
    pub fn generate(&self, topology_type: TopologyType, num_nodes: usize) -> ConsciousnessTopology {
        ConsciousnessTopology::new(topology_type, num_nodes, self.dimension)
    }

    /// Find optimal topology for target phi
    pub fn find_optimal(&self, target_phi: f64, num_nodes: usize) -> ConsciousnessTopology {
        let types = [
            TopologyType::FullyConnected,
            TopologyType::SmallWorld,
            TopologyType::Hierarchical,
            TopologyType::ScaleFree,
        ];

        types.iter()
            .map(|&t| self.generate(t, num_nodes))
            .min_by(|a, b| {
                let diff_a = (a.phi_estimate - target_phi).abs();
                let diff_b = (b.phi_estimate - target_phi).abs();
                diff_a.partial_cmp(&diff_b).unwrap_or(std::cmp::Ordering::Equal)
            })
            .unwrap()
    }
}

impl Default for TopologyGenerator {
    fn default() -> Self {
        Self::new(512)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_topology_generation() {
        let topo = ConsciousnessTopology::new(TopologyType::Ring, 10, 512);
        assert_eq!(topo.num_nodes, 10);
        assert!(topo.connections.len() > 0);
    }

    #[test]
    fn test_small_world() {
        let topo = ConsciousnessTopology::new(TopologyType::SmallWorld, 20, 512);
        assert!(topo.clustering > 0.0);
    }
}
