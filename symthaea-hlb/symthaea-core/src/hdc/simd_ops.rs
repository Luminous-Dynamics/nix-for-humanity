//! SIMD-Optimized Operations for Binary Hypervectors
//!
//! This module provides high-performance implementations of HV16 operations
//! using explicit SIMD intrinsics for maximum throughput.
//!
//! # Performance Targets
//! - `bind` (XOR): 5-10ns (vs ~80ns scalar)
//! - `similarity` (popcount): 10-20ns (vs ~160ns scalar)
//! - `bundle` (majority vote): 50-100ns (vs ~1000ns scalar)
//!
//! # Architecture Support
//! - AVX2 (x86_64): 256-bit operations
//! - SSE4.1 (x86_64): 128-bit operations (fallback)
//! - Portable: Safe fallback using auto-vectorization hints

#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

/// SIMD-optimized XOR (bind) operation for 2048 bytes
///
/// Uses AVX2 when available for 8x throughput improvement.
///
/// # Safety
/// Requires proper alignment and assumes input arrays are exactly 2048 bytes.
#[inline]
#[cfg(target_arch = "x86_64")]
pub fn bind_simd(a: &[u8; 2048], b: &[u8; 2048]) -> [u8; 2048] {
    let mut result = [0u8; 2048];

    // Try AVX2 first (256-bit = 32 bytes per operation)
    if is_x86_feature_detected!("avx2") {
        unsafe { bind_avx2(a, b, &mut result) };
    }
    // Fall back to SSE4.1 (128-bit = 16 bytes per operation)
    else if is_x86_feature_detected!("sse4.1") {
        unsafe { bind_sse41(a, b, &mut result) };
    }
    // Scalar fallback with manual unrolling
    else {
        bind_scalar_unrolled(a, b, &mut result);
    }

    result
}

/// AVX2 implementation of XOR (32 bytes per iteration = 64 iterations for 2048 bytes)
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2")]
#[inline]
unsafe fn bind_avx2(a: &[u8; 2048], b: &[u8; 2048], result: &mut [u8; 2048]) {
    let a_ptr = a.as_ptr() as *const __m256i;
    let b_ptr = b.as_ptr() as *const __m256i;
    let r_ptr = result.as_mut_ptr() as *mut __m256i;

    // 2048 bytes / 32 bytes = 64 iterations
    // Unroll by 4 for better instruction-level parallelism
    for i in (0..64).step_by(4) {
        let a0 = _mm256_loadu_si256(a_ptr.add(i));
        let b0 = _mm256_loadu_si256(b_ptr.add(i));
        let a1 = _mm256_loadu_si256(a_ptr.add(i + 1));
        let b1 = _mm256_loadu_si256(b_ptr.add(i + 1));
        let a2 = _mm256_loadu_si256(a_ptr.add(i + 2));
        let b2 = _mm256_loadu_si256(b_ptr.add(i + 2));
        let a3 = _mm256_loadu_si256(a_ptr.add(i + 3));
        let b3 = _mm256_loadu_si256(b_ptr.add(i + 3));

        let r0 = _mm256_xor_si256(a0, b0);
        let r1 = _mm256_xor_si256(a1, b1);
        let r2 = _mm256_xor_si256(a2, b2);
        let r3 = _mm256_xor_si256(a3, b3);

        _mm256_storeu_si256(r_ptr.add(i), r0);
        _mm256_storeu_si256(r_ptr.add(i + 1), r1);
        _mm256_storeu_si256(r_ptr.add(i + 2), r2);
        _mm256_storeu_si256(r_ptr.add(i + 3), r3);
    }
}

/// SSE4.1 implementation of XOR (16 bytes per iteration = 128 iterations for 2048 bytes)
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "sse4.1")]
#[inline]
unsafe fn bind_sse41(a: &[u8; 2048], b: &[u8; 2048], result: &mut [u8; 2048]) {
    let a_ptr = a.as_ptr() as *const __m128i;
    let b_ptr = b.as_ptr() as *const __m128i;
    let r_ptr = result.as_mut_ptr() as *mut __m128i;

    // 2048 bytes / 16 bytes = 128 iterations
    // Unroll by 4
    for i in (0..128).step_by(4) {
        let a0 = _mm_loadu_si128(a_ptr.add(i));
        let b0 = _mm_loadu_si128(b_ptr.add(i));
        let a1 = _mm_loadu_si128(a_ptr.add(i + 1));
        let b1 = _mm_loadu_si128(b_ptr.add(i + 1));
        let a2 = _mm_loadu_si128(a_ptr.add(i + 2));
        let b2 = _mm_loadu_si128(b_ptr.add(i + 2));
        let a3 = _mm_loadu_si128(a_ptr.add(i + 3));
        let b3 = _mm_loadu_si128(b_ptr.add(i + 3));

        let r0 = _mm_xor_si128(a0, b0);
        let r1 = _mm_xor_si128(a1, b1);
        let r2 = _mm_xor_si128(a2, b2);
        let r3 = _mm_xor_si128(a3, b3);

        _mm_storeu_si128(r_ptr.add(i), r0);
        _mm_storeu_si128(r_ptr.add(i + 1), r1);
        _mm_storeu_si128(r_ptr.add(i + 2), r2);
        _mm_storeu_si128(r_ptr.add(i + 3), r3);
    }
}

/// Scalar fallback with manual unrolling for auto-vectorization
#[inline]
fn bind_scalar_unrolled(a: &[u8; 2048], b: &[u8; 2048], result: &mut [u8; 2048]) {
    // Process 8 bytes at a time using u64 for better auto-vectorization.
    // Use unaligned loads/stores because the byte arrays are not guaranteed to be 8-byte aligned.
    use std::ptr::{read_unaligned, write_unaligned};

    let a_ptr = a.as_ptr() as *const u64;
    let b_ptr = b.as_ptr() as *const u64;
    let r_ptr = result.as_mut_ptr() as *mut u64;

    unsafe {
        for i in (0..256).step_by(4) {
            let a0 = read_unaligned(a_ptr.add(i));
            let b0 = read_unaligned(b_ptr.add(i));
            let a1 = read_unaligned(a_ptr.add(i + 1));
            let b1 = read_unaligned(b_ptr.add(i + 1));
            let a2 = read_unaligned(a_ptr.add(i + 2));
            let b2 = read_unaligned(b_ptr.add(i + 2));
            let a3 = read_unaligned(a_ptr.add(i + 3));
            let b3 = read_unaligned(b_ptr.add(i + 3));

            write_unaligned(r_ptr.add(i), a0 ^ b0);
            write_unaligned(r_ptr.add(i + 1), a1 ^ b1);
            write_unaligned(r_ptr.add(i + 2), a2 ^ b2);
            write_unaligned(r_ptr.add(i + 3), a3 ^ b3);
        }
    }
}

/// SIMD-optimized population count (Hamming weight) for similarity calculation
///
/// Returns the number of matching bits between two 2048-byte arrays.
///
/// Uses AVX2 with POPCNT for maximum throughput.
#[inline]
#[cfg(target_arch = "x86_64")]
pub fn matching_bits_simd(a: &[u8; 2048], b: &[u8; 2048]) -> u32 {
    if is_x86_feature_detected!("avx2") && is_x86_feature_detected!("popcnt") {
        unsafe { matching_bits_avx2_popcnt(a, b) }
    } else if is_x86_feature_detected!("popcnt") {
        matching_bits_popcnt(a, b)
    } else {
        matching_bits_scalar(a, b)
    }
}

/// AVX2 + POPCNT implementation
/// XOR bytes together, then count zero bits (matching = ~xor)
/// Uses read_unaligned for safety with potentially unaligned data
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2", enable = "popcnt")]
#[inline]
unsafe fn matching_bits_avx2_popcnt(a: &[u8; 2048], b: &[u8; 2048]) -> u32 {
    use std::ptr::read_unaligned;

    let a_ptr = a.as_ptr() as *const u64;
    let b_ptr = b.as_ptr() as *const u64;

    let mut total: u64 = 0;

    // 2048 bytes / 8 bytes = 256 u64s
    // Process 4 at a time for ILP
    // Use read_unaligned for safety (HV16 should be aligned, but be defensive)
    for i in (0..256).step_by(4) {
        let xor0 = read_unaligned(a_ptr.add(i)) ^ read_unaligned(b_ptr.add(i));
        let xor1 = read_unaligned(a_ptr.add(i + 1)) ^ read_unaligned(b_ptr.add(i + 1));
        let xor2 = read_unaligned(a_ptr.add(i + 2)) ^ read_unaligned(b_ptr.add(i + 2));
        let xor3 = read_unaligned(a_ptr.add(i + 3)) ^ read_unaligned(b_ptr.add(i + 3));

        // Count DIFFERING bits (popcount of XOR)
        // Matching = total bits - differing
        total += _popcnt64(xor0 as i64) as u64;
        total += _popcnt64(xor1 as i64) as u64;
        total += _popcnt64(xor2 as i64) as u64;
        total += _popcnt64(xor3 as i64) as u64;
    }

    // Total bits - differing bits = matching bits
    (16_384 - total) as u32
}

/// POPCNT-only implementation (fallback when AVX2 not available)
#[cfg(target_arch = "x86_64")]
fn matching_bits_popcnt(a: &[u8; 2048], b: &[u8; 2048]) -> u32 {
    use std::ptr::read_unaligned;

    let a_ptr = a.as_ptr() as *const u64;
    let b_ptr = b.as_ptr() as *const u64;
    let mut differing: u64 = 0;

    unsafe {
        for i in (0..256).step_by(4) {
            let xor0 = read_unaligned(a_ptr.add(i)) ^ read_unaligned(b_ptr.add(i));
            let xor1 = read_unaligned(a_ptr.add(i + 1)) ^ read_unaligned(b_ptr.add(i + 1));
            let xor2 = read_unaligned(a_ptr.add(i + 2)) ^ read_unaligned(b_ptr.add(i + 2));
            let xor3 = read_unaligned(a_ptr.add(i + 3)) ^ read_unaligned(b_ptr.add(i + 3));

            differing += xor0.count_ones() as u64;
            differing += xor1.count_ones() as u64;
            differing += xor2.count_ones() as u64;
            differing += xor3.count_ones() as u64;
        }
    }

    (16_384 - differing) as u32
}

/// Scalar fallback implementation
#[inline]
fn matching_bits_scalar(a: &[u8; 2048], b: &[u8; 2048]) -> u32 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (!(x ^ y)).count_ones())
        .sum()
}

/// SIMD-optimized NOT (invert) operation
#[inline]
#[cfg(target_arch = "x86_64")]
pub fn invert_simd(a: &[u8; 2048]) -> [u8; 2048] {
    let mut result = [0u8; 2048];

    if is_x86_feature_detected!("avx2") {
        unsafe { invert_avx2(a, &mut result) };
    } else if is_x86_feature_detected!("sse4.1") {
        unsafe { invert_sse41(a, &mut result) };
    } else {
        invert_scalar(a, &mut result);
    }

    result
}

/// AVX2 implementation of NOT
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2")]
#[inline]
unsafe fn invert_avx2(a: &[u8; 2048], result: &mut [u8; 2048]) {
    let a_ptr = a.as_ptr() as *const __m256i;
    let r_ptr = result.as_mut_ptr() as *mut __m256i;
    let ones = _mm256_set1_epi8(-1i8); // All 1s

    for i in (0..64).step_by(4) {
        let a0 = _mm256_loadu_si256(a_ptr.add(i));
        let a1 = _mm256_loadu_si256(a_ptr.add(i + 1));
        let a2 = _mm256_loadu_si256(a_ptr.add(i + 2));
        let a3 = _mm256_loadu_si256(a_ptr.add(i + 3));

        // XOR with all 1s = NOT
        let r0 = _mm256_xor_si256(a0, ones);
        let r1 = _mm256_xor_si256(a1, ones);
        let r2 = _mm256_xor_si256(a2, ones);
        let r3 = _mm256_xor_si256(a3, ones);

        _mm256_storeu_si256(r_ptr.add(i), r0);
        _mm256_storeu_si256(r_ptr.add(i + 1), r1);
        _mm256_storeu_si256(r_ptr.add(i + 2), r2);
        _mm256_storeu_si256(r_ptr.add(i + 3), r3);
    }
}

/// SSE4.1 implementation of NOT
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "sse4.1")]
#[inline]
unsafe fn invert_sse41(a: &[u8; 2048], result: &mut [u8; 2048]) {
    let a_ptr = a.as_ptr() as *const __m128i;
    let r_ptr = result.as_mut_ptr() as *mut __m128i;
    let ones = _mm_set1_epi8(-1i8);

    for i in (0..128).step_by(4) {
        let a0 = _mm_loadu_si128(a_ptr.add(i));
        let a1 = _mm_loadu_si128(a_ptr.add(i + 1));
        let a2 = _mm_loadu_si128(a_ptr.add(i + 2));
        let a3 = _mm_loadu_si128(a_ptr.add(i + 3));

        let r0 = _mm_xor_si128(a0, ones);
        let r1 = _mm_xor_si128(a1, ones);
        let r2 = _mm_xor_si128(a2, ones);
        let r3 = _mm_xor_si128(a3, ones);

        _mm_storeu_si128(r_ptr.add(i), r0);
        _mm_storeu_si128(r_ptr.add(i + 1), r1);
        _mm_storeu_si128(r_ptr.add(i + 2), r2);
        _mm_storeu_si128(r_ptr.add(i + 3), r3);
    }
}

/// Scalar fallback for NOT
#[inline]
fn invert_scalar(a: &[u8; 2048], result: &mut [u8; 2048]) {
    use std::ptr::{read_unaligned, write_unaligned};

    let a_ptr = a.as_ptr() as *const u64;
    let r_ptr = result.as_mut_ptr() as *mut u64;

    unsafe {
        for i in (0..256).step_by(4) {
            let a0 = read_unaligned(a_ptr.add(i));
            let a1 = read_unaligned(a_ptr.add(i + 1));
            let a2 = read_unaligned(a_ptr.add(i + 2));
            let a3 = read_unaligned(a_ptr.add(i + 3));

            write_unaligned(r_ptr.add(i), !a0);
            write_unaligned(r_ptr.add(i + 1), !a1);
            write_unaligned(r_ptr.add(i + 2), !a2);
            write_unaligned(r_ptr.add(i + 3), !a3);
        }
    }
}

/// SIMD-optimized Hamming distance
#[inline]
#[cfg(target_arch = "x86_64")]
pub fn hamming_distance_simd(a: &[u8; 2048], b: &[u8; 2048]) -> u32 {
    // Matching bits + hamming distance = total bits
    // So hamming = total - matching
    16_384 - matching_bits_simd(a, b)
}

// Non-x86_64 fallback implementations
#[cfg(not(target_arch = "x86_64"))]
pub fn bind_simd(a: &[u8; 2048], b: &[u8; 2048]) -> [u8; 2048] {
    let mut result = [0u8; 2048];
    for i in 0..2048 {
        result[i] = a[i] ^ b[i];
    }
    result
}

#[cfg(not(target_arch = "x86_64"))]
pub fn matching_bits_simd(a: &[u8; 2048], b: &[u8; 2048]) -> u32 {
    matching_bits_scalar(a, b)
}

#[cfg(not(target_arch = "x86_64"))]
pub fn invert_simd(a: &[u8; 2048]) -> [u8; 2048] {
    let mut result = [0u8; 2048];
    for i in 0..2048 {
        result[i] = !a[i];
    }
    result
}

#[cfg(not(target_arch = "x86_64"))]
pub fn hamming_distance_simd(a: &[u8; 2048], b: &[u8; 2048]) -> u32 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (x ^ y).count_ones())
        .sum()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hdc::binary_hv::HV16;

    #[test]
    fn test_bind_simd_matches_scalar() {
        let a = HV16::random(42);
        let b = HV16::random(43);

        // SIMD version
        let simd_result = bind_simd(&a.0, &b.0);

        // Scalar version (original)
        let scalar_result = a.bind(&b);

        assert_eq!(simd_result, scalar_result.0, "SIMD bind must match scalar bind");
    }

    #[test]
    fn test_matching_bits_simd_matches_scalar() {
        let a = HV16::random(42);
        let b = HV16::random(43);

        // SIMD version
        let simd_matching = matching_bits_simd(&a.0, &b.0);

        // Scalar version (via similarity * DIM)
        let scalar_similarity = a.similarity(&b);
        let scalar_matching = (scalar_similarity * HV16::DIM as f32) as u32;

        // Allow small rounding difference
        let diff = (simd_matching as i32 - scalar_matching as i32).abs();
        assert!(diff <= 1, "SIMD matching bits must match scalar: {} vs {}",
                simd_matching, scalar_matching);
    }

    #[test]
    fn test_invert_simd_matches_scalar() {
        let a = HV16::random(42);

        // SIMD version
        let simd_result = invert_simd(&a.0);

        // Scalar version
        let scalar_result = a.invert();

        assert_eq!(simd_result, scalar_result.0, "SIMD invert must match scalar invert");
    }

    #[test]
    fn test_hamming_distance_simd_matches_scalar() {
        let a = HV16::random(42);
        let b = HV16::random(43);

        // SIMD version
        let simd_dist = hamming_distance_simd(&a.0, &b.0);

        // Scalar version
        let scalar_dist = a.hamming_distance(&b);

        assert_eq!(simd_dist, scalar_dist, "SIMD hamming distance must match scalar");
    }

    #[test]
    fn test_simd_self_similarity() {
        let a = HV16::random(42);

        let matching = matching_bits_simd(&a.0, &a.0);
        assert_eq!(matching, 16_384, "Self-matching should be all bits");

        let distance = hamming_distance_simd(&a.0, &a.0);
        assert_eq!(distance, 0, "Self-distance should be zero");
    }

    #[test]
    fn test_simd_inverse_properties() {
        let a = HV16::random(42);
        let inv = invert_simd(&a.0);

        // XOR with inverse should be all 1s
        let xor_result = bind_simd(&a.0, &inv);
        for byte in xor_result.iter() {
            assert_eq!(*byte, 0xFF, "XOR with inverse should be all 1s");
        }

        // Hamming distance to inverse should be maximum
        let dist = hamming_distance_simd(&a.0, &inv);
        assert_eq!(dist, 16_384, "Distance to inverse should be maximum");
    }

    #[test]
    #[ignore = "benchmark test - run with cargo test --release -- --ignored"]
    fn bench_simd_vs_scalar() {
        use std::time::Instant;
        use std::hint::black_box;

        let a = HV16::random(1);
        let b = HV16::random(2);
        let iterations = 1_000_000;

        // Benchmark SIMD bind
        let start = Instant::now();
        for _ in 0..iterations {
            black_box(bind_simd(black_box(&a.0), black_box(&b.0)));
        }
        let simd_bind_ns = start.elapsed().as_nanos() / iterations;

        // Benchmark scalar bind (using explicit scalar method)
        let start = Instant::now();
        for _ in 0..iterations {
            black_box(a.bind_scalar(black_box(&b)));
        }
        let scalar_bind_ns = start.elapsed().as_nanos() / iterations;

        // Benchmark SIMD similarity
        let start = Instant::now();
        for _ in 0..iterations {
            black_box(matching_bits_simd(black_box(&a.0), black_box(&b.0)));
        }
        let simd_sim_ns = start.elapsed().as_nanos() / iterations;

        // Benchmark scalar similarity (using explicit scalar method)
        let start = Instant::now();
        for _ in 0..iterations {
            black_box(a.similarity_scalar(black_box(&b)));
        }
        let scalar_sim_ns = start.elapsed().as_nanos() / iterations;

        println!("\n📊 SIMD vs Scalar Performance:");
        println!("  Bind:       SIMD {}ns vs Scalar {}ns ({:.1}x speedup)",
                 simd_bind_ns, scalar_bind_ns,
                 scalar_bind_ns as f64 / simd_bind_ns.max(1) as f64);
        println!("  Similarity: SIMD {}ns vs Scalar {}ns ({:.1}x speedup)",
                 simd_sim_ns, scalar_sim_ns,
                 scalar_sim_ns as f64 / simd_sim_ns.max(1) as f64);

        // Assert meaningful speedup in release mode
        #[cfg(not(debug_assertions))]
        {
            assert!(simd_bind_ns < scalar_bind_ns,
                    "SIMD bind should be faster than scalar");
            assert!(simd_sim_ns < scalar_sim_ns,
                    "SIMD similarity should be faster than scalar");
        }
    }
}
