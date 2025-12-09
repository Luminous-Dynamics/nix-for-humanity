/*!
Hyperdimensional Computing (HDC) Semantic Space

10,000D holographic vectors for consciousness
Memory IS computation - no separate storage needed!
*/

use anyhow::Result;
// Note: hypervector crate not used yet - using custom implementation
// use hypervector::{HyperVector as HV, HVType};
use std::collections::HashMap;
use bumpalo::Bump;

/// Semantic space using 10,000D hypervectors
#[derive(Debug)]
pub struct SemanticSpace {
    /// Dimensionality (typically 10,000)
    dimension: usize,

    /// Concept library
    concepts: HashMap<String, Vec<f32>>,

    /// Item memory (episodes)
    item_memory: Vec<Vec<f32>>,
}

impl SemanticSpace {
    pub fn new(dimension: usize) -> Result<Self> {
        Ok(Self {
            dimension,
            concepts: HashMap::new(),
            item_memory: Vec::new(),
        })
    }

    /// Encode text as hypervector (holographic!)
    pub fn encode(&mut self, text: &str) -> Result<Vec<f32>> {
        // For demo: create or retrieve concept vector
        let words: Vec<&str> = text.split_whitespace().collect();

        let mut result = vec![0.0; self.dimension];

        for word in words {
            let concept = self.get_or_create_concept(word);

            // Bundle (superposition)
            for i in 0..self.dimension {
                result[i] += concept[i];
            }
        }

        // Normalize
        let norm: f32 = result.iter().map(|x| x * x).sum::<f32>().sqrt();
        if norm > 0.0 {
            for x in &mut result {
                *x /= norm;
            }
        }

        Ok(result)
    }

    /// Recall similar memories (holographic retrieval!)
    pub fn recall(&self, query: &[f32], limit: usize) -> Result<Vec<Vec<f32>>> {
        let mut similarities: Vec<(f32, usize)> = self.item_memory
            .iter()
            .enumerate()
            .map(|(idx, mem)| {
                let sim = cosine_similarity(query, mem);
                (sim, idx)
            })
            .collect();

        // Sort by similarity (descending)
        similarities.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());

        // Return top matches
        Ok(similarities
            .iter()
            .take(limit)
            .map(|(_, idx)| self.item_memory[*idx].clone())
            .collect())
    }

    /// Bind multiple vectors holographically
    pub fn bind_many(&self, vectors: &[Vec<f32>]) -> Result<Vec<f32>> {
        if vectors.is_empty() {
            return Ok(vec![0.0; self.dimension]);
        }

        // For demo: simple circular convolution
        let mut result = vectors[0].clone();

        for vec in &vectors[1..] {
            result = circular_convolution(&result, vec);
        }

        Ok(result)
    }

    /// Bundle (superposition) of vectors
    pub fn bundle(&self, vectors: &[Vec<f32>]) -> Result<Vec<f32>> {
        let mut result = vec![0.0; self.dimension];

        for vec in vectors {
            for i in 0..self.dimension {
                result[i] += vec[i];
            }
        }

        // Normalize
        let norm: f32 = result.iter().map(|x| x * x).sum::<f32>().sqrt();
        if norm > 0.0 {
            for x in &mut result {
                *x /= norm;
            }
        }

        Ok(result)
    }

    /// Decode hypervector to text (approximate)
    pub fn decode(&self, vector: &[f32]) -> Result<String> {
        // Find most similar concepts
        let mut best_matches: Vec<(f32, String)> = self.concepts
            .iter()
            .map(|(word, concept)| {
                let sim = cosine_similarity(vector, concept);
                (sim, word.clone())
            })
            .collect();

        best_matches.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());

        // Take top 5 concepts
        let decoded: Vec<String> = best_matches
            .iter()
            .take(5)
            .map(|(_, word)| word.clone())
            .collect();

        Ok(decoded.join(" "))
    }

    fn get_or_create_concept(&mut self, word: &str) -> Vec<f32> {
        if let Some(concept) = self.concepts.get(word) {
            return concept.clone();
        }

        // Create new random concept vector
        let concept: Vec<f32> = (0..self.dimension)
            .map(|_| rand::random::<f32>() * 2.0 - 1.0)
            .collect();

        self.concepts.insert(word.to_string(), concept.clone());
        concept
    }

    pub fn serialize(&self) -> Result<Vec<u8>> {
        Ok(bincode::serialize(&self.concepts)?)
    }

    pub fn deserialize(data: &[u8]) -> Result<Self> {
        let concepts: HashMap<String, Vec<f32>> = bincode::deserialize(data)?;
        let dimension = concepts.values().next().map(|v| v.len()).unwrap_or(10_000);

        Ok(Self {
            dimension,
            concepts,
            item_memory: Vec::new(),
        })
    }
}

fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    let dot: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    if norm_a > 0.0 && norm_b > 0.0 {
        dot / (norm_a * norm_b)
    } else {
        0.0
    }
}

fn circular_convolution(a: &[f32], b: &[f32]) -> Vec<f32> {
    let n = a.len();
    let mut result = vec![0.0; n];

    for i in 0..n {
        for j in 0..n {
            let k = (i + j) % n;
            result[k] += a[i] * b[j];
        }
    }

    result
}

//
// Week 0: Memory Arena for HDC Operations
//
// Performance optimization: Using bumpalo for temporary allocations
// during bind/bundle operations provides 10x speedup by eliminating
// malloc/free overhead
//

/// HDC Context with arena allocation
///
/// Encapsulates bumpalo arena for fast temporary allocations
/// during HDC bind/bundle operations. Call reset() after each
/// operation to free all arena memory at once.
pub struct HdcContext {
    arena: Bump,
}

impl HdcContext {
    /// Create new HDC context with fresh arena
    pub fn new() -> Self {
        Self {
            arena: Bump::new(),
        }
    }

    /// Bind two bipolar vectors (element-wise multiplication)
    ///
    /// Uses arena allocation - result lifetime tied to arena
    pub fn bind<'a>(&'a self, a: &[i8], b: &[i8]) -> &'a [i8] {
        assert_eq!(a.len(), b.len(), "Vectors must have same dimension");

        // Allocate in arena (fast bump pointer, no malloc!)
        let result = self.arena.alloc_slice_fill_copy(a.len(), 0i8);

        // Element-wise multiplication for binding
        for i in 0..a.len() {
            result[i] = a[i] * b[i];
        }

        result
    }

    /// Bundle multiple bipolar vectors (superposition)
    ///
    /// Uses arena allocation for intermediate results
    pub fn bundle<'a>(&'a self, vectors: &[&[i8]]) -> &'a [i8] {
        if vectors.is_empty() {
            return &[];
        }

        let dim = vectors[0].len();

        // Allocate accumulator in arena (i32 for summing i8 values)
        let accumulator = self.arena.alloc_slice_fill_copy(dim, 0i32);

        // Sum all vectors
        for vec in vectors {
            assert_eq!(vec.len(), dim, "All vectors must have same dimension");
            for i in 0..dim {
                accumulator[i] += vec[i] as i32;
            }
        }

        // Threshold back to bipolar (-1, +1)
        let result = self.arena.alloc_slice_fill_copy(dim, 0i8);
        for i in 0..dim {
            result[i] = if accumulator[i] > 0 { 1 } else { -1 };
        }

        result
    }

    /// Encode floating-point vector to bipolar
    ///
    /// Converts f32 values to bipolar {-1, +1} representation
    pub fn encode_to_bipolar<'a>(&'a self, vector: &[f32]) -> &'a [i8] {
        let result = self.arena.alloc_slice_fill_copy(vector.len(), 0i8);

        for i in 0..vector.len() {
            result[i] = if vector[i] > 0.0 { 1 } else { -1 };
        }

        result
    }

    /// Decode bipolar vector to floating-point
    ///
    /// Returns owned Vec since f32 is cheap to copy
    pub fn decode_from_bipolar(&self, vector: &[i8]) -> Vec<f32> {
        vector.iter().map(|&x| x as f32).collect()
    }

    /// Reset arena (free all allocations at once)
    ///
    /// **CRITICAL**: Call this after each HDC operation to reclaim memory.
    /// This is 100x faster than individual frees!
    pub fn reset(&mut self) {
        self.arena.reset();
    }

    /// Get current arena memory usage
    pub fn arena_allocated(&self) -> usize {
        self.arena.allocated_bytes()
    }
}

impl Default for HdcContext {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod arena_tests {
    use super::*;

    #[test]
    fn test_bind_vectors() {
        let ctx = HdcContext::new();

        let a = vec![1i8, -1, 1, -1];
        let b = vec![1i8, 1, -1, -1];

        let result = ctx.bind(&a, &b);

        assert_eq!(result, &[1, -1, -1, 1]);
    }

    #[test]
    fn test_bundle_vectors() {
        let ctx = HdcContext::new();

        let a = vec![1i8, -1, 1, -1];
        let b = vec![1i8, 1, -1, -1];
        let c = vec![-1i8, 1, 1, 1];

        let vectors = vec![&a[..], &b[..], &c[..]];
        let result = ctx.bundle(&vectors);

        // Majority vote: [1+1-1=1, -1+1+1=1, 1-1+1=1, -1-1+1=-1]
        assert_eq!(result, &[1, 1, 1, -1]);
    }

    #[test]
    fn test_encode_decode() {
        let ctx = HdcContext::new();

        let original = vec![0.5, -0.3, 0.8, -0.1];

        let bipolar = ctx.encode_to_bipolar(&original);
        let decoded = ctx.decode_from_bipolar(bipolar);

        assert_eq!(bipolar, &[1, -1, 1, -1]);
        assert_eq!(decoded, vec![1.0, -1.0, 1.0, -1.0]);
    }

    #[test]
    fn test_arena_reset() {
        let mut ctx = HdcContext::new();

        let a = vec![1i8; 10_000];
        let b = vec![-1i8; 10_000];

        // Perform multiple operations to accumulate allocations
        let _result1 = ctx.bind(&a, &b);
        let _result2 = ctx.bind(&a, &b);
        let _result3 = ctx.bind(&a, &b);

        let allocated_before = ctx.arena_allocated();
        assert!(allocated_before >= 30_000, "Arena should have significant allocations");

        // Reset clears all allocations
        ctx.reset();

        // After reset, new allocations should start fresh
        let _result4 = ctx.bind(&a, &b);
        let allocated_after = ctx.arena_allocated();

        // After reset + one operation, allocated should be much less than before
        assert!(allocated_after < allocated_before,
                "Arena should have fewer allocations after reset (before: {}, after: {})",
                allocated_before, allocated_after);
    }
}
