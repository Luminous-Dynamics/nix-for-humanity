//! Audio frontend and feature extraction
//!
//! This module provides:
//! - WAV file loading
//! - Mel spectrogram extraction (using rustfft for O(n log n) performance)
//! - LTC-based audio projection to HDC space

use crate::hdc::HV16;
use crate::ltc::{LtcCell, LtcConfig};
use rustfft::{FftPlanner, num_complex::Complex};
use std::f32::consts::PI;
use std::path::Path;
use std::sync::Arc;

/// Audio frontend configuration
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct AudioConfig {
    /// Sample rate (Hz)
    pub sample_rate: u32,
    /// Frame duration (seconds)
    pub frame_duration: f32,
    /// Hop duration (seconds)
    pub hop_duration: f32,
    /// Number of mel filterbank channels
    pub n_mels: usize,
    /// Minimum frequency for mel filterbank
    pub f_min: f32,
    /// Maximum frequency for mel filterbank
    pub f_max: f32,
    /// FFT size
    pub n_fft: usize,
}

impl Default for AudioConfig {
    fn default() -> Self {
        Self {
            sample_rate: 16000,
            frame_duration: 0.025, // 25ms frames
            hop_duration: 0.010,   // 10ms hop
            n_mels: 40,
            f_min: 80.0,
            f_max: 7600.0,
            n_fft: 512,
        }
    }
}

/// Audio frontend for feature extraction
pub struct AudioFrontend {
    config: AudioConfig,
    /// Mel filterbank weights
    mel_filters: Vec<Vec<f32>>,
    /// Hann window
    window: Vec<f32>,
    /// Cached FFT instance
    fft: Arc<dyn rustfft::Fft<f32>>,
    /// Scratch buffer for FFT
    scratch: Vec<Complex<f32>>,
}

impl AudioFrontend {
    /// Create a new audio frontend
    pub fn new(config: AudioConfig) -> Self {
        let mel_filters = Self::create_mel_filterbank(&config);
        let frame_samples = (config.sample_rate as f32 * config.frame_duration) as usize;
        let window = Self::hann_window(frame_samples);

        // Create FFT planner and cache the FFT instance
        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_forward(config.n_fft);
        let scratch = vec![Complex::new(0.0, 0.0); fft.get_inplace_scratch_len()];

        Self {
            config,
            mel_filters,
            window,
            fft,
            scratch,
        }
    }

    /// Load audio from any supported format (WAV, FLAC)
    pub fn load_audio<P: AsRef<Path>>(path: P) -> std::io::Result<(Vec<f32>, u32)> {
        let path = path.as_ref();
        let ext = path.extension()
            .and_then(|e| e.to_str())
            .map(|e| e.to_lowercase())
            .unwrap_or_default();

        match ext.as_str() {
            "wav" => Self::load_wav(path),
            "flac" => Self::load_flac(path),
            _ => Err(std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                format!("Unsupported audio format: {}", ext)
            ))
        }
    }

    /// Load audio from WAV file
    pub fn load_wav<P: AsRef<Path>>(path: P) -> std::io::Result<(Vec<f32>, u32)> {
        let reader = hound::WavReader::open(path)
            .map_err(|e| std::io::Error::other(e.to_string()))?;
        let spec = reader.spec();
        let sample_rate = spec.sample_rate;

        let samples: Vec<f32> = match spec.sample_format {
            hound::SampleFormat::Float => {
                reader.into_samples::<f32>()
                    .filter_map(|s| s.ok())
                    .collect()
            }
            hound::SampleFormat::Int => {
                let max = (1 << (spec.bits_per_sample - 1)) as f32;
                reader.into_samples::<i32>()
                    .filter_map(|s| s.ok())
                    .map(|s| s as f32 / max)
                    .collect()
            }
        };

        // Convert to mono if stereo
        let mono = if spec.channels == 2 {
            samples.chunks(2)
                .map(|c| (c[0] + c.get(1).copied().unwrap_or(0.0)) / 2.0)
                .collect()
        } else {
            samples
        };

        Ok((mono, sample_rate))
    }

    /// Load audio from FLAC file
    pub fn load_flac<P: AsRef<Path>>(path: P) -> std::io::Result<(Vec<f32>, u32)> {
        let mut reader = claxon::FlacReader::open(path)
            .map_err(|e| std::io::Error::other(e.to_string()))?;

        let info = reader.streaminfo();
        let sample_rate = info.sample_rate;
        let channels = info.channels as usize;
        let bits = info.bits_per_sample;
        let max = (1i64 << (bits - 1)) as f32;

        let samples: Vec<f32> = reader.samples()
            .filter_map(|s| s.ok())
            .map(|s| s as f32 / max)
            .collect();

        // Convert to mono if stereo
        let mono = if channels == 2 {
            samples.chunks(2)
                .map(|c| (c[0] + c.get(1).copied().unwrap_or(0.0)) / 2.0)
                .collect()
        } else if channels > 2 {
            // Mix all channels
            samples.chunks(channels)
                .map(|c| c.iter().sum::<f32>() / channels as f32)
                .collect()
        } else {
            samples
        };

        Ok((mono, sample_rate))
    }

    /// Extract mel spectrogram features
    pub fn extract_features(&mut self, audio: &[f32]) -> Vec<Vec<f32>> {
        let frame_samples = (self.config.sample_rate as f32 * self.config.frame_duration) as usize;
        let hop_samples = (self.config.sample_rate as f32 * self.config.hop_duration) as usize;

        let mut features = Vec::new();
        let mut pos = 0;

        while pos + frame_samples <= audio.len() {
            let frame = &audio[pos..pos + frame_samples];
            let mel = self.compute_mel_frame(frame);
            features.push(mel);
            pos += hop_samples;
        }

        features
    }

    /// Compute mel features for a single frame
    fn compute_mel_frame(&mut self, frame: &[f32]) -> Vec<f32> {
        // Apply window
        let windowed: Vec<f32> = frame.iter()
            .zip(self.window.iter())
            .map(|(&s, &w)| s * w)
            .collect();

        // Compute power spectrum using FFT (O(n log n))
        let power_spectrum = self.compute_power_spectrum(&windowed);

        // Apply mel filterbank
        let mut mel = vec![0.0; self.config.n_mels];
        for (i, filter) in self.mel_filters.iter().enumerate() {
            let energy = filter.iter()
                .zip(power_spectrum.iter())
                .map(|(&f, &p)| f * p)
                .sum::<f32>()
                .max(1e-10);

            // Log-mel with normalization:
            // Raw log values are typically in range [-20, 0] for speech
            // We normalize to approximately [-1, 1] range for stable LTC dynamics
            // Formula: (ln(energy) + 10) / 10  maps [-20, 0] -> [-1, 1]
            mel[i] = (energy.ln() + 10.0) / 10.0;
        }

        mel
    }

    /// Compute power spectrum using rustfft (O(n log n))
    fn compute_power_spectrum(&mut self, frame: &[f32]) -> Vec<f32> {
        let n = self.config.n_fft;

        // Zero-pad frame into complex buffer
        let mut buffer: Vec<Complex<f32>> = frame.iter()
            .map(|&s| Complex::new(s, 0.0))
            .chain(std::iter::repeat(Complex::new(0.0, 0.0)))
            .take(n)
            .collect();

        // Perform FFT in-place
        self.fft.process_with_scratch(&mut buffer, &mut self.scratch);

        // Compute power spectrum (first half + DC)
        buffer.iter()
            .take(n / 2 + 1)
            .map(|c| (c.re * c.re + c.im * c.im) / n as f32)
            .collect()
    }

    /// Create Hann window
    fn hann_window(size: usize) -> Vec<f32> {
        (0..size)
            .map(|i| 0.5 * (1.0 - (2.0 * PI * i as f32 / (size - 1) as f32).cos()))
            .collect()
    }

    /// Create mel filterbank
    fn create_mel_filterbank(config: &AudioConfig) -> Vec<Vec<f32>> {
        let n_fft_bins = config.n_fft / 2 + 1;

        // Convert Hz to mel scale
        let hz_to_mel = |hz: f32| 2595.0 * (1.0 + hz / 700.0).log10();
        let mel_to_hz = |mel: f32| 700.0 * (10.0_f32.powf(mel / 2595.0) - 1.0);

        let mel_min = hz_to_mel(config.f_min);
        let mel_max = hz_to_mel(config.f_max);

        // Create mel points
        let mel_points: Vec<f32> = (0..=config.n_mels + 1)
            .map(|i| mel_min + (mel_max - mel_min) * i as f32 / (config.n_mels + 1) as f32)
            .collect();

        // Convert back to Hz and then to FFT bin indices
        let hz_points: Vec<f32> = mel_points.iter().map(|&m| mel_to_hz(m)).collect();
        let bin_points: Vec<usize> = hz_points.iter()
            .map(|&hz| ((hz * config.n_fft as f32 / config.sample_rate as f32) as usize)
                .min(n_fft_bins - 1))
            .collect();

        // Create triangular filters
        let mut filters = Vec::with_capacity(config.n_mels);

        for m in 0..config.n_mels {
            let mut filter = vec![0.0; n_fft_bins];
            let left = bin_points[m];
            let center = bin_points[m + 1];
            let right = bin_points[m + 2];

            // Rising slope
            for k in left..center {
                if center > left {
                    filter[k] = (k - left) as f32 / (center - left) as f32;
                }
            }

            // Falling slope
            for k in center..=right {
                if right > center {
                    filter[k] = (right - k) as f32 / (right - center) as f32;
                }
            }

            filters.push(filter);
        }

        filters
    }

    /// Get configuration
    pub fn config(&self) -> &AudioConfig {
        &self.config
    }
}

/// Audio projector: LTC + HDC encoding
pub struct AudioProjector {
    /// Audio frontend
    frontend: AudioFrontend,
    /// LTC cells
    ltc: LtcCell,
    /// Frame duration
    frame_duration: f32,
}

impl AudioProjector {
    /// Create a new audio projector
    pub fn new(audio_config: AudioConfig, ltc_config: LtcConfig) -> Self {
        let frame_duration = audio_config.hop_duration;
        let frontend = AudioFrontend::new(audio_config);
        let ltc = LtcCell::new(40, ltc_config); // 40 mel features

        Self {
            frontend,
            ltc,
            frame_duration,
        }
    }

    /// Create with default configuration
    pub fn default_config() -> Self {
        Self::new(AudioConfig::default(), LtcConfig::default())
    }

    /// Reset projector state
    pub fn reset(&mut self) {
        self.ltc.reset();
    }

    /// Project audio to sequence of HDC hypervectors with TEMPORAL CONTEXT
    ///
    /// Uses a 5-frame sliding window with permutation-based position encoding:
    /// `HV = bundle(perm(f-2), perm(f-1), f, perm(f+1), perm(f+2))`
    ///
    /// This captures phoneme trajectories and eliminates frame-to-frame oscillation.
    pub fn project(&mut self, audio: &[f32]) -> Vec<HV16> {
        self.reset();

        let features = self.frontend.extract_features(audio);
        if features.is_empty() {
            return Vec::new();
        }

        // First pass: encode all individual frames
        let mut frame_hvs = Vec::with_capacity(features.len());
        let mut prev_state = vec![0.0; self.ltc.hidden_size()];

        for feature in &features {
            let state = self.ltc.forward(feature, self.frame_duration).to_vec();
            let hv = Self::state_to_hv_static(&state, &prev_state);
            frame_hvs.push(hv);
            prev_state = state;
        }

        // Second pass: temporal windowing with permutation-based position encoding
        // Window size = 7 (center frame ± 3) for ~70ms context at 10ms hop
        const WINDOW_HALF: usize = 3;
        let mut hvs = Vec::with_capacity(frame_hvs.len());

        for center_idx in 0..frame_hvs.len() {
            let context_hv = Self::bundle_temporal_window(&frame_hvs, center_idx, WINDOW_HALF);
            hvs.push(context_hv);
        }

        hvs
    }

    /// Bundle a temporal window of frames with position-specific permutations
    ///
    /// Position encoding: Each position gets a unique rotation amount.
    /// This preserves temporal order information in the bundle.
    /// Center frame is weighted more heavily (appears twice in bundle).
    fn bundle_temporal_window(frame_hvs: &[HV16], center: usize, half_width: usize) -> HV16 {
        use crate::hdc::BundleAccumulator;

        let mut acc = BundleAccumulator::new();

        // Position rotations for 7-frame window: distinct values
        // Larger rotations for frames further from center
        const POSITION_ROTATIONS: [i32; 7] = [-768, -512, -256, 0, 256, 512, 768];
        let half = half_width as i32;

        for (pos_idx, offset) in (-half..=half).enumerate() {
            let frame_idx = center as i32 + offset;

            // Handle boundary conditions: clamp to valid range
            let frame_idx = frame_idx.clamp(0, frame_hvs.len() as i32 - 1) as usize;

            let frame_hv = &frame_hvs[frame_idx];

            // Apply position-specific rotation
            let rotated = frame_hv.rotate(POSITION_ROTATIONS[pos_idx]);

            // Add to bundle - center frame gets double weight
            acc.add(&rotated);
            if offset == 0 {
                acc.add(&rotated); // Extra weight for center
            }
        }

        acc.finalize()
    }

    /// Project audio and also return salience values (with temporal context)
    pub fn project_with_salience(&mut self, audio: &[f32]) -> (Vec<HV16>, Vec<f32>) {
        self.reset();

        let features = self.frontend.extract_features(audio);
        if features.is_empty() {
            return (Vec::new(), Vec::new());
        }

        // First pass: encode all individual frames and compute saliences
        let mut frame_hvs = Vec::with_capacity(features.len());
        let mut saliences = Vec::with_capacity(features.len());
        let mut prev_state = vec![0.0; self.ltc.hidden_size()];

        for feature in &features {
            let state = self.ltc.forward(feature, self.frame_duration).to_vec();
            let salience = self.ltc.compute_salience(&prev_state);

            let hv = Self::state_to_hv_static(&state, &prev_state);
            frame_hvs.push(hv);
            saliences.push(salience);

            prev_state = state;
        }

        // Second pass: temporal windowing (same as project())
        const WINDOW_HALF: usize = 3;
        let mut hvs = Vec::with_capacity(frame_hvs.len());

        for center_idx in 0..frame_hvs.len() {
            let context_hv = Self::bundle_temporal_window(&frame_hvs, center_idx, WINDOW_HALF);
            hvs.push(context_hv);
        }

        (hvs, saliences)
    }

    /// Convert LTC state to hypervector using STATE + VELOCITY encoding
    ///
    /// Encodes both position (h) and velocity (dh/dt) in phase space.
    /// Sign-based encoding for robustness.
    fn state_to_hv_static(state: &[f32], prev_state: &[f32]) -> HV16 {
        let mut hv = HV16::zero();
        let n_dims = state.len();

        // Part 1: Encode STATE (position in phase space)
        for (dim_idx, &val) in state.iter().enumerate() {
            if val.abs() < 0.05 {
                continue;
            }

            let basis = Self::get_dim_basis(dim_idx);
            let rotated = if val > 0.0 {
                basis
            } else {
                basis.rotate(1024)
            };

            for w in 0..16 {
                hv.words[w] ^= rotated.words[w];
            }
        }

        // Part 2: Encode VELOCITY (change from previous state)
        for (dim_idx, &val) in state.iter().enumerate() {
            let prev_val = prev_state.get(dim_idx).copied().unwrap_or(0.0);
            let delta = val - prev_val;

            if delta.abs() < 0.03 {
                continue;
            }

            let basis = Self::get_dim_basis(n_dims + dim_idx);
            let rotated = if delta > 0.0 {
                basis
            } else {
                basis.rotate(1024)
            };

            for w in 0..16 {
                hv.words[w] ^= rotated.words[w];
            }
        }

        hv
    }

    /// Hybrid encoding: combines MEL spectral features with LTC dynamics
    ///
    /// This preserves raw frequency information (for formants, voicing)
    /// while adding temporal dynamics from LTC.
    fn hybrid_mel_ltc_hv(mel_features: &[f32], state: &[f32], prev_state: &[f32]) -> HV16 {
        let mut hv = HV16::zero();
        let _n_mel = mel_features.len();
        let n_ltc = state.len();

        // Part 1: Encode MEL features directly (preserves spectral detail)
        // Use different basis offset to avoid collision with LTC encoding
        const MEL_BASIS_OFFSET: usize = 256;
        for (bin_idx, &val) in mel_features.iter().enumerate() {
            // Skip low energy bins
            if val < 0.1 {
                continue;
            }

            let basis = Self::get_dim_basis(MEL_BASIS_OFFSET + bin_idx);

            // 3-level encoding: low, medium, high energy
            let rotation = if val > 0.6 {
                512   // High energy
            } else if val > 0.3 {
                0     // Medium energy
            } else {
                -512  // Low energy
            };

            let rotated = basis.rotate(rotation);
            for w in 0..16 {
                hv.words[w] ^= rotated.words[w];
            }
        }

        // Part 2: Encode LTC STATE for temporal dynamics
        for (dim_idx, &val) in state.iter().enumerate() {
            if val.abs() < 0.05 {
                continue;
            }

            let basis = Self::get_dim_basis(dim_idx);
            let rotated = if val > 0.0 { basis } else { basis.rotate(1024) };
            for w in 0..16 {
                hv.words[w] ^= rotated.words[w];
            }
        }

        // Part 3: Encode LTC VELOCITY for trajectory direction
        for (dim_idx, &val) in state.iter().enumerate() {
            let prev_val = prev_state.get(dim_idx).copied().unwrap_or(0.0);
            let delta = val - prev_val;
            if delta.abs() < 0.03 {
                continue;
            }

            let basis = Self::get_dim_basis(n_ltc + dim_idx);
            let rotated = if delta > 0.0 { basis } else { basis.rotate(1024) };
            for w in 0..16 {
                hv.words[w] ^= rotated.words[w];
            }
        }

        hv
    }

    /// Get a deterministic pseudo-random basis HV for a dimension
    fn get_dim_basis(dim: usize) -> HV16 {
        // Use dimension index as seed for deterministic random pattern
        let mut hasher = blake3::Hasher::new();
        hasher.update(&dim.to_le_bytes());
        let mut output = [0u8; 256];
        hasher.finalize_xof().fill(&mut output);
        HV16::from_bytes(&output)
    }

    /// Get LTC state
    pub fn state(&self) -> &[f32] {
        self.ltc.state()
    }

    /// Get current tau values
    pub fn tau(&self) -> &[f32] {
        self.ltc.tau()
    }

    /// Get frontend reference
    pub fn frontend(&self) -> &AudioFrontend {
        &self.frontend
    }
}

/// Prosody features
#[derive(Debug, Clone, Default)]
pub struct ProsodyFeatures {
    /// Pitch (F0) in Hz
    pub pitch: f32,
    /// Energy (RMS)
    pub energy: f32,
    /// Speaking rate estimate
    pub rate: f32,
}

impl ProsodyFeatures {
    /// Extract prosody from audio frame
    pub fn extract(audio: &[f32], sample_rate: u32) -> Self {
        let energy = (audio.iter().map(|&x| x * x).sum::<f32>() / audio.len() as f32).sqrt();

        // Simple autocorrelation-based pitch detection
        let pitch = Self::detect_pitch(audio, sample_rate);

        // Rate estimated from zero-crossing rate
        let zcr = audio.windows(2)
            .filter(|w| (w[0] >= 0.0) != (w[1] >= 0.0))
            .count() as f32 / audio.len() as f32;
        let rate = zcr * sample_rate as f32 / 2.0;

        Self { pitch, energy, rate }
    }

    fn detect_pitch(audio: &[f32], sample_rate: u32) -> f32 {
        let min_lag = sample_rate as usize / 500; // Max 500 Hz
        let max_lag = sample_rate as usize / 50;  // Min 50 Hz

        if audio.len() < max_lag * 2 {
            return 0.0;
        }

        let mut best_lag = 0;
        let mut best_corr = 0.0;

        for lag in min_lag..max_lag.min(audio.len() / 2) {
            let mut corr = 0.0;
            for i in 0..audio.len() - lag {
                corr += audio[i] * audio[i + lag];
            }
            if corr > best_corr {
                best_corr = corr;
                best_lag = lag;
            }
        }

        if best_lag > 0 {
            sample_rate as f32 / best_lag as f32
        } else {
            0.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hann_window() {
        let window = AudioFrontend::hann_window(100);
        assert_eq!(window.len(), 100);
        assert!((window[0] - 0.0).abs() < 0.01);
        assert!((window[50] - 1.0).abs() < 0.01);
    }

    #[test]
    fn test_mel_filterbank() {
        let config = AudioConfig::default();
        let filters = AudioFrontend::create_mel_filterbank(&config);
        assert_eq!(filters.len(), config.n_mels);

        // Each filter should have the right size
        for filter in &filters {
            assert_eq!(filter.len(), config.n_fft / 2 + 1);
        }
    }

    #[test]
    fn test_audio_projector() {
        let mut projector = AudioProjector::default_config();

        // Create test audio (1 second of sine wave)
        let sample_rate = 16000;
        let audio: Vec<f32> = (0..sample_rate)
            .map(|i| (2.0 * PI * 440.0 * i as f32 / sample_rate as f32).sin())
            .collect();

        let hvs = projector.project(&audio);

        // Should produce approximately 100 frames (1s / 10ms)
        assert!(hvs.len() > 80 && hvs.len() < 120, "frames = {}", hvs.len());
    }

    #[test]
    fn test_prosody_extraction() {
        let sample_rate = 16000;
        let audio: Vec<f32> = (0..1600)
            .map(|i| (2.0 * PI * 200.0 * i as f32 / sample_rate as f32).sin())
            .collect();

        let prosody = ProsodyFeatures::extract(&audio, sample_rate);

        assert!(prosody.energy > 0.0);
        // Pitch should be around 200 Hz
        assert!(prosody.pitch > 150.0 && prosody.pitch < 250.0,
                "pitch = {}", prosody.pitch);
    }
}
