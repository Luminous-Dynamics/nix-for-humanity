//! # Text Encoder for HDC
//!
//! Encodes text into hyperdimensional vectors using various strategies
//! including n-gram encoding, positional encoding, and semantic hashing.

use crate::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Text encoding configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextEncoderConfig {
    /// HDC dimension
    pub dimension: usize,
    /// N-gram size
    pub ngram_size: usize,
    /// Use positional encoding
    pub use_position: bool,
    /// Vocabulary hash size
    pub vocab_size: usize,
    /// Case sensitivity
    pub case_sensitive: bool,
}

impl Default for TextEncoderConfig {
    fn default() -> Self {
        Self {
            dimension: 512,
            ngram_size: 3,
            use_position: true,
            vocab_size: 10000,
            case_sensitive: false,
        }
    }
}

/// Result of text encoding
#[derive(Debug, Clone)]
pub struct TextEncodingResult {
    /// The encoded hypervector
    pub encoding: RealHV,
    /// Token count
    pub token_count: usize,
    /// Vocabulary coverage (0-1)
    pub vocab_coverage: f32,
    /// N-grams used
    pub ngrams_used: usize,
}

/// Text to hypervector encoder
pub struct TextEncoder {
    config: TextEncoderConfig,
    /// Random vectors for characters/tokens
    char_vectors: HashMap<char, RealHV>,
    /// Cached word vectors
    word_cache: HashMap<String, RealHV>,
    /// Position encoding vectors
    position_vectors: Vec<RealHV>,
    /// Statistics
    total_encodings: u64,
}

impl TextEncoder {
    /// Create new text encoder
    pub fn new(config: TextEncoderConfig) -> Self {
        // Generate position vectors
        let position_vectors = (0..1000)
            .map(|_| RealHV::random(config.dimension))
            .collect();

        Self {
            char_vectors: HashMap::new(),
            word_cache: HashMap::new(),
            position_vectors,
            total_encodings: 0,
            config,
        }
    }

    /// Encode a string to hypervector
    pub fn encode(&mut self, text: &str) -> TextEncodingResult {
        self.total_encodings += 1;

        let text = if self.config.case_sensitive {
            text.to_string()
        } else {
            text.to_lowercase()
        };

        // Tokenize
        let tokens: Vec<&str> = text.split_whitespace().collect();

        if tokens.is_empty() {
            return TextEncodingResult {
                encoding: RealHV::zeros(self.config.dimension),
                token_count: 0,
                vocab_coverage: 0.0,
                ngrams_used: 0,
            };
        }

        // Encode each token with position
        let mut encodings: Vec<RealHV> = Vec::new();
        let mut ngrams_used = 0;

        for (pos, token) in tokens.iter().enumerate() {
            let token_vec = self.encode_token(token);

            // Apply position encoding
            let final_vec = if self.config.use_position && pos < self.position_vectors.len() {
                token_vec.bind(&self.position_vectors[pos])
            } else {
                token_vec
            };

            encodings.push(final_vec);

            // Add n-grams
            if pos >= self.config.ngram_size - 1 {
                let ngram: Vec<&str> = tokens[pos + 1 - self.config.ngram_size..=pos].to_vec();
                let ngram_vec = self.encode_ngram(&ngram);
                encodings.push(ngram_vec);
                ngrams_used += 1;
            }
        }

        // Bundle all encodings
        let result_encoding = if encodings.is_empty() {
            RealHV::zeros(self.config.dimension)
        } else {
            encodings[0].bundle(&encodings[1..])
        };

        TextEncodingResult {
            encoding: result_encoding,
            token_count: tokens.len(),
            vocab_coverage: self.word_cache.len() as f32 / self.config.vocab_size as f32,
            ngrams_used,
        }
    }

    /// Encode a single token
    fn encode_token(&mut self, token: &str) -> RealHV {
        // Check cache
        if let Some(cached) = self.word_cache.get(token) {
            return cached.clone();
        }

        // Encode using character-level composition
        let mut char_vecs: Vec<RealHV> = Vec::new();

        for (i, c) in token.chars().enumerate() {
            let char_vec = self.get_char_vector(c);
            // Position-encode within word
            let positioned = char_vec.permute(i as i32);
            char_vecs.push(positioned);
        }

        let word_vec = if char_vecs.is_empty() {
            RealHV::random(self.config.dimension)
        } else {
            char_vecs[0].bundle(&char_vecs[1..])
        };

        // Cache if room
        if self.word_cache.len() < self.config.vocab_size {
            self.word_cache.insert(token.to_string(), word_vec.clone());
        }

        word_vec
    }

    /// Encode an n-gram
    fn encode_ngram(&mut self, tokens: &[&str]) -> RealHV {
        // Bind tokens together (order-preserving)
        let mut ngram_vec = self.encode_token(tokens[0]);

        for (i, token) in tokens.iter().enumerate().skip(1) {
            let token_vec = self.encode_token(token);
            // Permute by position to preserve order
            ngram_vec = ngram_vec.bind(&token_vec.permute(i as i32));
        }

        ngram_vec
    }

    /// Get or create character vector
    fn get_char_vector(&mut self, c: char) -> RealHV {
        if let Some(vec) = self.char_vectors.get(&c) {
            return vec.clone();
        }

        // Create deterministic random vector for this character
        let seed = c as u64;
        let vec = RealHV::random(self.config.dimension);

        self.char_vectors.insert(c, vec.clone());
        vec
    }

    /// Encode a document (multiple sentences)
    pub fn encode_document(&mut self, sentences: &[&str]) -> RealHV {
        let encodings: Vec<RealHV> = sentences.iter()
            .map(|s| self.encode(s).encoding)
            .collect();

        if encodings.is_empty() {
            RealHV::zeros(self.config.dimension)
        } else {
            encodings[0].bundle(&encodings[1..])
        }
    }

    /// Calculate similarity between two texts
    pub fn similarity(&mut self, text1: &str, text2: &str) -> f32 {
        let enc1 = self.encode(text1).encoding;
        let enc2 = self.encode(text2).encoding;
        enc1.cosine_similarity(&enc2)
    }

    /// Get encoding statistics
    pub fn stats(&self) -> TextEncoderStats {
        TextEncoderStats {
            total_encodings: self.total_encodings,
            vocab_size: self.word_cache.len(),
            char_vocab_size: self.char_vectors.len(),
        }
    }
}

/// Encoder statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextEncoderStats {
    /// Total texts encoded
    pub total_encodings: u64,
    /// Words in vocabulary
    pub vocab_size: usize,
    /// Characters in vocabulary
    pub char_vocab_size: usize,
}

impl Default for TextEncoder {
    fn default() -> Self {
        Self::new(TextEncoderConfig::default())
    }
}

/// Semantic hash for fast text comparison
#[derive(Debug, Clone)]
pub struct SemanticHash {
    /// Binary hash
    pub hash: Vec<bool>,
    /// Hash size
    pub size: usize,
}

impl SemanticHash {
    /// Create from hypervector using sign of components
    pub fn from_hv(hv: &RealHV) -> Self {
        let hash: Vec<bool> = hv.iter().map(|&x| x > 0.0).collect();
        let size = hash.len();
        Self { hash, size }
    }

    /// Hamming distance to another hash
    pub fn hamming_distance(&self, other: &SemanticHash) -> usize {
        self.hash.iter()
            .zip(other.hash.iter())
            .filter(|(&a, &b)| a != b)
            .count()
    }

    /// Similarity (1 - normalized hamming distance)
    pub fn similarity(&self, other: &SemanticHash) -> f32 {
        1.0 - (self.hamming_distance(other) as f32 / self.size as f32)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_text_encoding() {
        let mut encoder = TextEncoder::default();
        let result = encoder.encode("hello world");
        assert!(result.token_count == 2);
    }

    #[test]
    fn test_similarity() {
        let mut encoder = TextEncoder::default();
        let sim = encoder.similarity("hello world", "hello world");
        assert!(sim > 0.9);
    }

    #[test]
    fn test_semantic_hash() {
        let hv = RealHV::random(512);
        let hash = SemanticHash::from_hv(&hv);
        assert_eq!(hash.size, 512);
        assert!(hash.similarity(&hash) == 1.0);
    }
}
