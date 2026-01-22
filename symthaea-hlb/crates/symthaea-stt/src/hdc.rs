//! Hyperdimensional Computing (HDC) primitives
//!
//! This module implements 2048-bit binary hypervectors with:
//! - BLAKE3-based random projection for deterministic encoding
//! - XOR binding for associative memory
//! - Majority voting for bundling/superposition

use blake3::Hasher;
use serde::{Deserialize, Serialize};
use std::fmt;

/// Hypervector dimension (bits)
pub const HDC_DIM: usize = 2048;

/// Number of u128 words to store the hypervector
pub const HDC_WORDS: usize = HDC_DIM / 128;

/// A 2048-bit binary hypervector stored as 16 x u128
#[derive(Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct HV16 {
    /// The 16 u128 words comprising the 2048-bit vector
    pub words: [u128; HDC_WORDS],
}

impl Default for HV16 {
    fn default() -> Self {
        Self::zero()
    }
}

impl fmt::Debug for HV16 {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let ones = self.popcount();
        write!(f, "HV16[popcount={}/{}]", ones, HDC_DIM)
    }
}

impl HV16 {
    /// Create a zero hypervector
    pub fn zero() -> Self {
        Self { words: [0u128; HDC_WORDS] }
    }

    /// Create a random hypervector from a seed string using BLAKE3
    pub fn random(seed: &str) -> Self {
        let mut hasher = Hasher::new();
        hasher.update(seed.as_bytes());
        let mut output = [0u8; HDC_WORDS * 16];
        hasher.finalize_xof().fill(&mut output);

        let mut words = [0u128; HDC_WORDS];
        for (i, chunk) in output.chunks_exact(16).enumerate() {
            words[i] = u128::from_le_bytes(chunk.try_into().unwrap());
        }

        Self { words }
    }

    /// Create a hypervector from raw bytes (256 bytes = 2048 bits)
    pub fn from_bytes(bytes: &[u8; 256]) -> Self {
        let mut words = [0u128; HDC_WORDS];
        for (i, chunk) in bytes.chunks_exact(16).enumerate() {
            words[i] = u128::from_le_bytes(chunk.try_into().unwrap());
        }
        Self { words }
    }

    /// Convert to raw bytes
    pub fn to_bytes(&self) -> [u8; 256] {
        let mut bytes = [0u8; 256];
        for (i, &word) in self.words.iter().enumerate() {
            bytes[i * 16..(i + 1) * 16].copy_from_slice(&word.to_le_bytes());
        }
        bytes
    }

    /// XOR binding: associates two hypervectors
    /// Binding is its own inverse: bind(bind(A, B), B) = A
    #[inline]
    pub fn bind(&self, other: &Self) -> Self {
        let mut result = Self::zero();
        for i in 0..HDC_WORDS {
            result.words[i] = self.words[i] ^ other.words[i];
        }
        result
    }

    /// XOR in-place
    #[inline]
    pub fn bind_mut(&mut self, other: &Self) {
        for i in 0..HDC_WORDS {
            self.words[i] ^= other.words[i];
        }
    }

    /// Population count (number of 1-bits)
    #[inline]
    pub fn popcount(&self) -> u32 {
        self.words.iter().map(|w| w.count_ones()).sum()
    }

    /// Hamming distance between two hypervectors
    #[inline]
    pub fn hamming(&self, other: &Self) -> u32 {
        self.bind(other).popcount()
    }

    /// Normalized similarity: 1.0 = identical, 0.0 = orthogonal, -1.0 = opposite
    /// Maps Hamming distance to [-1, 1] range
    #[inline]
    pub fn similarity(&self, other: &Self) -> f32 {
        let hamming = self.hamming(other) as f32;
        1.0 - (2.0 * hamming / HDC_DIM as f32)
    }

    /// Cosine-like similarity in [0, 1] range
    #[inline]
    pub fn cosine_similarity(&self, other: &Self) -> f32 {
        (self.similarity(other) + 1.0) / 2.0
    }

    /// Circular shift (permutation) - used for sequence encoding
    pub fn rotate(&self, amount: i32) -> Self {
        if amount == 0 {
            return *self;
        }

        let mut result = Self::zero();
        let shift = amount.rem_euclid(HDC_DIM as i32) as usize;

        // For each bit position, compute its source
        for dst_bit in 0..HDC_DIM {
            let src_bit = (dst_bit + HDC_DIM - shift) % HDC_DIM;

            let src_word = src_bit / 128;
            let src_offset = src_bit % 128;
            let dst_word = dst_bit / 128;
            let dst_offset = dst_bit % 128;

            if (self.words[src_word] >> src_offset) & 1 == 1 {
                result.words[dst_word] |= 1u128 << dst_offset;
            }
        }

        result
    }

    /// Flip all bits (NOT operation)
    pub fn flip(&self) -> Self {
        let mut result = Self::zero();
        for i in 0..HDC_WORDS {
            result.words[i] = !self.words[i];
        }
        result
    }

    /// Check if approximately equal (similarity above threshold)
    pub fn approx_eq(&self, other: &Self, threshold: f32) -> bool {
        self.similarity(other) >= threshold
    }
}

/// Accumulator for majority-vote bundling
#[derive(Clone, Debug)]
pub struct BundleAccumulator {
    /// Per-bit counters
    counts: [i32; HDC_DIM],
    /// Number of vectors accumulated
    n: usize,
}

impl Default for BundleAccumulator {
    fn default() -> Self {
        Self::new()
    }
}

impl BundleAccumulator {
    /// Create a new empty accumulator
    pub fn new() -> Self {
        Self {
            counts: [0; HDC_DIM],
            n: 0,
        }
    }

    /// Add a hypervector to the accumulator
    pub fn add(&mut self, hv: &HV16) {
        for i in 0..HDC_DIM {
            let word_idx = i / 128;
            let bit_idx = i % 128;
            let bit = ((hv.words[word_idx] >> bit_idx) & 1) as i32;
            self.counts[i] += if bit == 1 { 1 } else { -1 };
        }
        self.n += 1;
    }

    /// Add a weighted hypervector
    pub fn add_weighted(&mut self, hv: &HV16, weight: f32) {
        let w = weight as i32;
        for i in 0..HDC_DIM {
            let word_idx = i / 128;
            let bit_idx = i % 128;
            let bit = ((hv.words[word_idx] >> bit_idx) & 1) as i32;
            self.counts[i] += if bit == 1 { w } else { -w };
        }
        self.n += 1;
    }

    /// Finalize to a hypervector using majority voting
    pub fn finalize(&self) -> HV16 {
        let mut result = HV16::zero();
        for i in 0..HDC_DIM {
            if self.counts[i] > 0 {
                let word_idx = i / 128;
                let bit_idx = i % 128;
                result.words[word_idx] |= 1u128 << bit_idx;
            }
        }
        result
    }

    /// Number of vectors accumulated
    pub fn count(&self) -> usize {
        self.n
    }

    /// Clear the accumulator
    pub fn clear(&mut self) {
        self.counts = [0; HDC_DIM];
        self.n = 0;
    }
}

/// Bundle multiple hypervectors using majority voting
pub fn bundle(hvs: &[HV16]) -> HV16 {
    if hvs.is_empty() {
        return HV16::zero();
    }
    if hvs.len() == 1 {
        return hvs[0];
    }

    let mut acc = BundleAccumulator::new();
    for hv in hvs {
        acc.add(hv);
    }
    acc.finalize()
}

/// Bundle with weights
pub fn weighted_bundle(hvs: &[(HV16, f32)]) -> HV16 {
    if hvs.is_empty() {
        return HV16::zero();
    }

    let mut acc = BundleAccumulator::new();
    for (hv, weight) in hvs {
        acc.add_weighted(hv, *weight);
    }
    acc.finalize()
}

/// Encode a sequence of hypervectors using rotation + binding
/// Position 0 is unrotated, position 1 is rotated by 1, etc.
pub fn encode_sequence(hvs: &[HV16]) -> HV16 {
    if hvs.is_empty() {
        return HV16::zero();
    }

    let mut acc = BundleAccumulator::new();
    for (i, hv) in hvs.iter().enumerate() {
        acc.add(&hv.rotate(i as i32));
    }
    acc.finalize()
}

/// N-gram encoder: binds rotated hypervectors
pub fn encode_ngram(hvs: &[HV16]) -> HV16 {
    if hvs.is_empty() {
        return HV16::zero();
    }

    let mut result = hvs[0];
    for (i, hv) in hvs.iter().enumerate().skip(1) {
        result = result.bind(&hv.rotate(i as i32));
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_random_deterministic() {
        let a = HV16::random("test");
        let b = HV16::random("test");
        assert_eq!(a, b);
    }

    #[test]
    fn test_random_orthogonal() {
        let a = HV16::random("apple");
        let b = HV16::random("banana");
        // Random vectors should be approximately orthogonal (sim ~ 0)
        let sim = a.similarity(&b);
        assert!(sim.abs() < 0.1, "sim = {}", sim);
    }

    #[test]
    fn test_bind_inverse() {
        let a = HV16::random("A");
        let b = HV16::random("B");
        let bound = a.bind(&b);
        let recovered = bound.bind(&b);
        assert_eq!(a, recovered);
    }

    #[test]
    fn test_bundle_similarity() {
        let a = HV16::random("A");
        let b = HV16::random("B");
        let c = HV16::random("C");
        let bundled = bundle(&[a, b, c]);

        // Bundle should be similar to all constituents
        assert!(bundled.similarity(&a) > 0.3);
        assert!(bundled.similarity(&b) > 0.3);
        assert!(bundled.similarity(&c) > 0.3);
    }

    #[test]
    fn test_popcount() {
        let zero = HV16::zero();
        assert_eq!(zero.popcount(), 0);

        let random = HV16::random("test");
        // Random vector should have ~50% ones
        let pop = random.popcount();
        assert!(pop > 900 && pop < 1150, "popcount = {}", pop);
    }
}
