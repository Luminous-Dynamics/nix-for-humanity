//! Utility functions for the mind system.

use symthaea_core::hdc::RealHV;

/// Permute (circular shift) a RealHV vector to create variation.
///
/// Used in dream processing to generate creative insights
/// by rotating the vector's dimensions.
pub(crate) fn permute_hv(hv: &RealHV, shift: usize) -> RealHV {
    let n = hv.values.len();
    if n == 0 || shift == 0 {
        return hv.clone();
    }
    let effective_shift = shift % n;
    let mut new_values = vec![0.0f32; n];
    for i in 0..n {
        new_values[(i + effective_shift) % n] = hv.values[i];
    }
    RealHV::from_values(new_values)
}
