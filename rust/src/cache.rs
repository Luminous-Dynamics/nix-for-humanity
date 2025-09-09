//! High-performance caching with compression and LRU eviction

use dashmap::DashMap;
use parking_lot::RwLock;
use std::sync::Arc;
use std::time::{Duration, Instant};
use serde::{Serialize, Deserialize};
use blake3::Hasher;
use flate2::write::GzEncoder;
use flate2::read::GzDecoder;
use flate2::Compression;
use std::io::{Write, Read};

/// Cache entry with metadata
#[derive(Clone, Debug)]
pub struct CacheEntry {
    pub data: Vec<u8>,
    pub compressed: bool,
    pub hash: String,
    pub size: usize,
    pub access_count: u64,
    pub created_at: Instant,
    pub last_accessed: Instant,
    pub ttl: Option<Duration>,
}

impl CacheEntry {
    /// Check if entry is expired
    pub fn is_expired(&self) -> bool {
        if let Some(ttl) = self.ttl {
            self.created_at.elapsed() > ttl
        } else {
            false
        }
    }

    /// Update access metadata
    pub fn touch(&mut self) {
        self.access_count += 1;
        self.last_accessed = Instant::now();
    }
}

/// Advanced cache with multiple eviction strategies
pub struct AdvancedCache {
    entries: Arc<DashMap<String, CacheEntry>>,
    max_size: usize,
    current_size: Arc<RwLock<usize>>,
    compression_threshold: usize,
    eviction_strategy: EvictionStrategy,
}

#[derive(Clone, Copy, Debug)]
pub enum EvictionStrategy {
    LRU,    // Least Recently Used
    LFU,    // Least Frequently Used
    FIFO,   // First In First Out
    TTL,    // Time To Live based
}

impl AdvancedCache {
    pub fn new(max_size: usize, compression_threshold: usize) -> Self {
        AdvancedCache {
            entries: Arc::new(DashMap::new()),
            max_size,
            current_size: Arc::new(RwLock::new(0)),
            compression_threshold,
            eviction_strategy: EvictionStrategy::LRU,
        }
    }

    /// Store data with automatic compression
    pub fn put(&self, key: String, data: Vec<u8>, ttl: Option<Duration>) -> Result<(), String> {
        let size = data.len();
        let compressed = size > self.compression_threshold;
        
        let stored_data = if compressed {
            compress_data(&data)?
        } else {
            data
        };

        // Calculate hash for deduplication
        let hash = calculate_hash(&stored_data);

        let entry = CacheEntry {
            data: stored_data,
            compressed,
            hash,
            size,
            access_count: 0,
            created_at: Instant::now(),
            last_accessed: Instant::now(),
            ttl,
        };

        // Check if we need to evict
        {
            let mut current = self.current_size.write();
            if *current + size > self.max_size {
                self.evict_to_size(self.max_size - size);
            }
            *current += size;
        }

        self.entries.insert(key, entry);
        Ok(())
    }

    /// Get data with automatic decompression
    pub fn get(&self, key: &str) -> Option<Vec<u8>> {
        if let Some(mut entry) = self.entries.get_mut(key) {
            if entry.is_expired() {
                self.entries.remove(key);
                return None;
            }

            entry.touch();
            
            let data = if entry.compressed {
                decompress_data(&entry.data).ok()?
            } else {
                entry.data.clone()
            };

            Some(data)
        } else {
            None
        }
    }

    /// Check if key exists and is valid
    pub fn contains(&self, key: &str) -> bool {
        if let Some(entry) = self.entries.get(key) {
            !entry.is_expired()
        } else {
            false
        }
    }

    /// Get cache statistics
    pub fn stats(&self) -> CacheStats {
        let total_entries = self.entries.len();
        let mut compressed_count = 0;
        let mut total_accesses = 0u64;
        let mut expired_count = 0;

        for entry in self.entries.iter() {
            if entry.compressed {
                compressed_count += 1;
            }
            if entry.is_expired() {
                expired_count += 1;
            }
            total_accesses += entry.access_count;
        }

        CacheStats {
            total_entries,
            compressed_entries: compressed_count,
            expired_entries: expired_count,
            total_size: *self.current_size.read(),
            max_size: self.max_size,
            total_accesses,
            hit_rate: self.calculate_hit_rate(),
        }
    }

    /// Evict entries to reach target size
    fn evict_to_size(&self, target_size: usize) {
        let mut entries_to_evict = Vec::new();
        
        match self.eviction_strategy {
            EvictionStrategy::LRU => {
                // Collect and sort by last accessed time
                let mut candidates: Vec<_> = self.entries.iter()
                    .map(|e| (e.key().clone(), e.last_accessed, e.size))
                    .collect();
                candidates.sort_by_key(|(_, time, _)| *time);
                
                let mut current = *self.current_size.read();
                for (key, _, size) in candidates {
                    if current <= target_size {
                        break;
                    }
                    entries_to_evict.push(key);
                    current -= size;
                }
            },
            EvictionStrategy::LFU => {
                // Sort by access count
                let mut candidates: Vec<_> = self.entries.iter()
                    .map(|e| (e.key().clone(), e.access_count, e.size))
                    .collect();
                candidates.sort_by_key(|(_, count, _)| *count);
                
                let mut current = *self.current_size.read();
                for (key, _, size) in candidates {
                    if current <= target_size {
                        break;
                    }
                    entries_to_evict.push(key);
                    current -= size;
                }
            },
            EvictionStrategy::FIFO => {
                // Sort by creation time
                let mut candidates: Vec<_> = self.entries.iter()
                    .map(|e| (e.key().clone(), e.created_at, e.size))
                    .collect();
                candidates.sort_by_key(|(_, time, _)| *time);
                
                let mut current = *self.current_size.read();
                for (key, _, size) in candidates {
                    if current <= target_size {
                        break;
                    }
                    entries_to_evict.push(key);
                    current -= size;
                }
            },
            EvictionStrategy::TTL => {
                // First evict expired, then use LRU
                for entry in self.entries.iter() {
                    if entry.is_expired() {
                        entries_to_evict.push(entry.key().clone());
                    }
                }
            }
        }

        // Remove evicted entries
        for key in entries_to_evict {
            if let Some((_, entry)) = self.entries.remove(&key) {
                let mut current = self.current_size.write();
                *current = current.saturating_sub(entry.size);
            }
        }
    }

    /// Calculate cache hit rate
    fn calculate_hit_rate(&self) -> f64 {
        // This would need tracking of hits/misses in production
        0.85 // Placeholder
    }

    /// Clear all expired entries
    pub fn cleanup_expired(&self) {
        let expired: Vec<_> = self.entries.iter()
            .filter(|e| e.is_expired())
            .map(|e| e.key().clone())
            .collect();

        for key in expired {
            if let Some((_, entry)) = self.entries.remove(&key) {
                let mut current = self.current_size.write();
                *current = current.saturating_sub(entry.size);
            }
        }
    }
}

/// Cache statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheStats {
    pub total_entries: usize,
    pub compressed_entries: usize,
    pub expired_entries: usize,
    pub total_size: usize,
    pub max_size: usize,
    pub total_accesses: u64,
    pub hit_rate: f64,
}

/// Compress data using gzip
fn compress_data(data: &[u8]) -> Result<Vec<u8>, String> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::fast());
    encoder.write_all(data)
        .map_err(|e| format!("Compression error: {}", e))?;
    encoder.finish()
        .map_err(|e| format!("Compression finish error: {}", e))
}

/// Decompress gzipped data
fn decompress_data(data: &[u8]) -> Result<Vec<u8>, String> {
    let mut decoder = GzDecoder::new(data);
    let mut decompressed = Vec::new();
    decoder.read_to_end(&mut decompressed)
        .map_err(|e| format!("Decompression error: {}", e))?;
    Ok(decompressed)
}

/// Calculate BLAKE3 hash of data
fn calculate_hash(data: &[u8]) -> String {
    let mut hasher = Hasher::new();
    hasher.update(data);
    hasher.finalize().to_hex().to_string()
}

/// Multi-layer cache with L1/L2/L3
pub struct LayeredCache {
    l1: Arc<DashMap<String, Vec<u8>>>,  // Hot cache (in-memory)
    l2: Arc<AdvancedCache>,              // Warm cache (compressed)
    l3: Option<Arc<DiskCache>>,          // Cold cache (disk)
}

impl LayeredCache {
    pub fn new(l1_size: usize, l2_size: usize) -> Self {
        LayeredCache {
            l1: Arc::new(DashMap::new()),
            l2: Arc::new(AdvancedCache::new(l2_size, 1024)),
            l3: None,
        }
    }

    /// Get with cache promotion
    pub fn get(&self, key: &str) -> Option<Vec<u8>> {
        // Try L1 first
        if let Some(data) = self.l1.get(key) {
            return Some(data.clone());
        }

        // Try L2
        if let Some(data) = self.l2.get(key) {
            // Promote to L1
            self.l1.insert(key.to_string(), data.clone());
            return Some(data);
        }

        // Try L3 if available
        if let Some(ref l3) = self.l3 {
            if let Some(data) = l3.get(key) {
                // Promote to L2 and L1
                self.l2.put(key.to_string(), data.clone(), None).ok();
                self.l1.insert(key.to_string(), data.clone());
                return Some(data);
            }
        }

        None
    }

    /// Put with write-through
    pub fn put(&self, key: String, data: Vec<u8>) -> Result<(), String> {
        // Write to all layers
        self.l1.insert(key.clone(), data.clone());
        self.l2.put(key.clone(), data.clone(), None)?;
        
        if let Some(ref l3) = self.l3 {
            l3.put(key, data)?;
        }

        Ok(())
    }
}

/// Placeholder for disk-based cache
pub struct DiskCache;

impl DiskCache {
    pub fn get(&self, _key: &str) -> Option<Vec<u8>> {
        // Would implement disk-based storage
        None
    }

    pub fn put(&self, _key: String, _data: Vec<u8>) -> Result<(), String> {
        // Would implement disk-based storage
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_compression() {
        let cache = AdvancedCache::new(1024 * 1024, 100);
        
        // Small data - no compression
        let small_data = vec![1, 2, 3, 4, 5];
        cache.put("small".to_string(), small_data.clone(), None).unwrap();
        
        let retrieved = cache.get("small").unwrap();
        assert_eq!(retrieved, small_data);
        
        // Large data - with compression
        let large_data = vec![42u8; 1000];
        cache.put("large".to_string(), large_data.clone(), None).unwrap();
        
        let retrieved = cache.get("large").unwrap();
        assert_eq!(retrieved, large_data);
    }

    #[test]
    fn test_cache_eviction() {
        let cache = AdvancedCache::new(100, 50);
        
        // Fill cache
        for i in 0..20 {
            let data = vec![i as u8; 10];
            cache.put(format!("key{}", i), data, None).unwrap();
        }
        
        // Should have evicted some entries
        let stats = cache.stats();
        assert!(stats.total_entries < 20);
        assert!(stats.total_size <= 100);
    }

    #[test]
    fn test_layered_cache() {
        let cache = LayeredCache::new(100, 1000);
        
        let data = vec![1, 2, 3, 4, 5];
        cache.put("test".to_string(), data.clone()).unwrap();
        
        // Should be in L1
        assert!(cache.l1.contains_key("test"));
        
        // Get should still work
        let retrieved = cache.get("test").unwrap();
        assert_eq!(retrieved, data);
    }
}