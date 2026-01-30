//! # Beat Synchronization for Rap Synthesis
//!
//! This module provides beat-aware timing for rap/rhythmic speech synthesis.
//! It synchronizes phoneme timing with musical beats, creating rhythmic flow.
//!
//! ## Key Concepts
//!
//! - **BPM**: Beats per minute (tempo)
//! - **Beat Grid**: Regular time intervals for beat alignment
//! - **Swing**: Off-beat timing for groove feel
//! - **Flow Patterns**: Rhythmic templates for syllable placement

use serde::{Deserialize, Serialize};

/// Beat grid position
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct BeatPosition {
    /// Bar number (0-indexed)
    pub bar: u32,
    /// Beat within bar (0-3 for 4/4 time)
    pub beat: u8,
    /// Sub-beat division (0-3 for 16th notes)
    pub subdivision: u8,
    /// Absolute time in seconds
    pub time: f32,
}

impl BeatPosition {
    /// Create a beat position from absolute time
    pub fn from_time(time: f32, bpm: f32, beats_per_bar: u8) -> Self {
        let beat_duration = 60.0 / bpm;
        let total_beats = time / beat_duration;

        let bar = (total_beats / beats_per_bar as f32).floor() as u32;
        let beat_in_bar = (total_beats % beats_per_bar as f32).floor() as u8;
        let subdivision = ((total_beats.fract() * 4.0).floor() as u8).min(3);

        Self {
            bar,
            beat: beat_in_bar,
            subdivision,
            time,
        }
    }

    /// Convert to absolute time
    pub fn to_time(&self, bpm: f32, beats_per_bar: u8) -> f32 {
        let beat_duration = 60.0 / bpm;
        let total_beats = self.bar as f32 * beats_per_bar as f32
            + self.beat as f32
            + self.subdivision as f32 / 4.0;
        total_beats * beat_duration
    }

    /// Get the next beat position
    pub fn next_subdivision(&self, beats_per_bar: u8) -> Self {
        let mut new = *self;
        new.subdivision += 1;
        if new.subdivision >= 4 {
            new.subdivision = 0;
            new.beat += 1;
            if new.beat >= beats_per_bar {
                new.beat = 0;
                new.bar += 1;
            }
        }
        new
    }

    /// Check if this is on a strong beat (1 or 3 in 4/4)
    pub fn is_strong_beat(&self) -> bool {
        self.subdivision == 0 && (self.beat == 0 || self.beat == 2)
    }

    /// Check if this is on any beat (not subdivision)
    pub fn is_on_beat(&self) -> bool {
        self.subdivision == 0
    }
}

/// Swing feel configuration
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct SwingConfig {
    /// Swing amount (0.0 = straight, 0.5 = full triplet swing)
    pub amount: f32,
    /// Which subdivisions to swing (typically off-beats)
    pub swing_odd: bool,
}

impl Default for SwingConfig {
    fn default() -> Self {
        Self {
            amount: 0.0,
            swing_odd: true,
        }
    }
}

impl SwingConfig {
    /// Hip-hop style swing
    pub fn hip_hop() -> Self {
        Self {
            amount: 0.15,
            swing_odd: true,
        }
    }

    /// Jazz/blues triplet swing
    pub fn triplet() -> Self {
        Self {
            amount: 0.33,
            swing_odd: true,
        }
    }
}

/// Flow pattern - defines syllable placement within a bar
#[derive(Debug, Clone)]
pub struct FlowPattern {
    /// Name of the pattern
    pub name: String,
    /// Syllable positions as fractions of a bar (0.0 to 1.0)
    pub positions: Vec<f32>,
    /// Stress levels for each position (0.0 to 1.0)
    pub stresses: Vec<f32>,
    /// Duration multipliers for each position
    pub durations: Vec<f32>,
}

impl FlowPattern {
    /// Create a pattern that hits every 16th note
    pub fn sixteenth_notes() -> Self {
        let positions: Vec<f32> = (0..16).map(|i| i as f32 / 16.0).collect();
        let stresses = vec![
            1.0, 0.3, 0.5, 0.3,  // Beat 1
            0.8, 0.3, 0.5, 0.3,  // Beat 2
            1.0, 0.3, 0.5, 0.3,  // Beat 3
            0.8, 0.3, 0.5, 0.3,  // Beat 4
        ];
        let durations = vec![1.0; 16];

        Self {
            name: "16th Notes".to_string(),
            positions,
            stresses,
            durations,
        }
    }

    /// Classic hip-hop flow pattern
    pub fn boom_bap() -> Self {
        Self {
            name: "Boom Bap".to_string(),
            positions: vec![0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875],
            stresses: vec![1.0, 0.4, 0.7, 0.4, 0.9, 0.4, 0.7, 0.4],
            durations: vec![1.0, 0.8, 1.0, 0.8, 1.0, 0.8, 1.0, 0.8],
        }
    }

    /// Triplet flow (like Migos)
    pub fn triplet_flow() -> Self {
        let mut positions = Vec::new();
        let mut stresses = Vec::new();
        let mut durations = Vec::new();

        // 4 beats, 3 notes per beat = 12 positions
        for beat in 0..4 {
            for triplet in 0..3 {
                let pos = beat as f32 / 4.0 + triplet as f32 / 12.0;
                positions.push(pos);
                stresses.push(if triplet == 0 { 1.0 } else { 0.5 });
                durations.push(1.0);
            }
        }

        Self {
            name: "Triplet Flow".to_string(),
            positions,
            stresses,
            durations,
        }
    }

    /// Double-time flow
    pub fn double_time() -> Self {
        let positions: Vec<f32> = (0..32).map(|i| i as f32 / 32.0).collect();
        let stresses: Vec<f32> = (0..32)
            .map(|i| {
                if i % 8 == 0 { 1.0 }
                else if i % 4 == 0 { 0.7 }
                else if i % 2 == 0 { 0.5 }
                else { 0.3 }
            })
            .collect();
        let durations = vec![0.8; 32];

        Self {
            name: "Double Time".to_string(),
            positions,
            stresses,
            durations,
        }
    }

    /// Laid-back/lazy flow
    pub fn laid_back() -> Self {
        Self {
            name: "Laid Back".to_string(),
            positions: vec![0.05, 0.28, 0.55, 0.78], // Slightly behind the beat
            stresses: vec![0.9, 0.6, 0.8, 0.5],
            durations: vec![1.2, 1.0, 1.2, 1.0],
        }
    }

    /// Get number of syllables this pattern can hold
    pub fn syllable_count(&self) -> usize {
        self.positions.len()
    }
}

/// Beat synchronization engine
#[derive(Debug, Clone)]
pub struct BeatSync {
    /// Tempo in BPM
    pub bpm: f32,
    /// Beats per bar (typically 4)
    pub beats_per_bar: u8,
    /// Swing configuration
    pub swing: SwingConfig,
    /// Current beat position
    current_position: BeatPosition,
}

impl BeatSync {
    /// Create a new beat sync engine
    pub fn new(bpm: f32) -> Self {
        Self {
            bpm,
            beats_per_bar: 4,
            swing: SwingConfig::default(),
            current_position: BeatPosition {
                bar: 0,
                beat: 0,
                subdivision: 0,
                time: 0.0,
            },
        }
    }

    /// Create with hip-hop settings (90 BPM with swing)
    pub fn hip_hop() -> Self {
        Self {
            bpm: 90.0,
            beats_per_bar: 4,
            swing: SwingConfig::hip_hop(),
            current_position: BeatPosition {
                bar: 0,
                beat: 0,
                subdivision: 0,
                time: 0.0,
            },
        }
    }

    /// Create with trap settings (140 BPM, no swing)
    pub fn trap() -> Self {
        Self {
            bpm: 140.0,
            beats_per_bar: 4,
            swing: SwingConfig::default(),
            current_position: BeatPosition {
                bar: 0,
                beat: 0,
                subdivision: 0,
                time: 0.0,
            },
        }
    }

    /// Get duration of one beat in seconds
    pub fn beat_duration(&self) -> f32 {
        60.0 / self.bpm
    }

    /// Get duration of one bar in seconds
    pub fn bar_duration(&self) -> f32 {
        self.beat_duration() * self.beats_per_bar as f32
    }

    /// Get duration of one 16th note in seconds
    pub fn sixteenth_duration(&self) -> f32 {
        self.beat_duration() / 4.0
    }

    /// Apply swing to a time value
    pub fn apply_swing(&self, time: f32) -> f32 {
        if self.swing.amount == 0.0 {
            return time;
        }

        let pos = BeatPosition::from_time(time, self.bpm, self.beats_per_bar);

        // Only swing odd subdivisions (off-beats)
        if self.swing.swing_odd && pos.subdivision % 2 == 1 {
            let swing_delay = self.sixteenth_duration() * self.swing.amount;
            time + swing_delay
        } else {
            time
        }
    }

    /// Quantize a time to the nearest beat grid position
    pub fn quantize(&self, time: f32, grid_size: u8) -> f32 {
        let grid_duration = self.beat_duration() / grid_size as f32;
        let grid_position = (time / grid_duration).round();
        grid_position * grid_duration
    }

    /// Quantize to 16th note grid
    pub fn quantize_16th(&self, time: f32) -> f32 {
        self.quantize(time, 4)
    }

    /// Quantize to 8th note grid
    pub fn quantize_8th(&self, time: f32) -> f32 {
        self.quantize(time, 2)
    }

    /// Map syllables to beat positions using a flow pattern
    pub fn map_syllables(
        &self,
        syllables: &[String],
        pattern: &FlowPattern,
        start_bar: u32,
    ) -> Vec<SyllableTiming> {
        let mut timings = Vec::new();
        let pattern_len = pattern.positions.len();

        for (i, syllable) in syllables.iter().enumerate() {
            let pattern_idx = i % pattern_len;
            let bar_offset = i / pattern_len;

            let bar_start = (start_bar + bar_offset as u32) as f32 * self.bar_duration();
            let position_in_bar = pattern.positions[pattern_idx] * self.bar_duration();
            let raw_time = bar_start + position_in_bar;

            // Apply swing
            let time = self.apply_swing(raw_time);

            // Calculate duration (time until next syllable or end of bar)
            let next_time = if i + 1 < syllables.len() {
                let next_pattern_idx = (i + 1) % pattern_len;
                let next_bar_offset = (i + 1) / pattern_len;
                let next_bar_start = (start_bar + next_bar_offset as u32) as f32 * self.bar_duration();
                let next_position = pattern.positions[next_pattern_idx] * self.bar_duration();
                self.apply_swing(next_bar_start + next_position)
            } else {
                time + self.sixteenth_duration() * 2.0
            };

            let base_duration = (next_time - time) * pattern.durations[pattern_idx];

            timings.push(SyllableTiming {
                syllable: syllable.clone(),
                start_time: time,
                duration: base_duration.max(0.05), // Minimum duration
                stress: pattern.stresses[pattern_idx],
                beat_position: BeatPosition::from_time(time, self.bpm, self.beats_per_bar),
            });
        }

        timings
    }

    /// Get current position
    pub fn position(&self) -> BeatPosition {
        self.current_position
    }

    /// Advance to a specific time
    pub fn seek(&mut self, time: f32) {
        self.current_position = BeatPosition::from_time(time, self.bpm, self.beats_per_bar);
        self.current_position.time = time;
    }

    /// Advance by delta time
    pub fn advance(&mut self, delta: f32) {
        let new_time = self.current_position.time + delta;
        self.seek(new_time);
    }
}

impl Default for BeatSync {
    fn default() -> Self {
        Self::new(120.0) // Default 120 BPM
    }
}

/// Timing information for a syllable
#[derive(Debug, Clone)]
pub struct SyllableTiming {
    /// The syllable text
    pub syllable: String,
    /// Start time in seconds
    pub start_time: f32,
    /// Duration in seconds
    pub duration: f32,
    /// Stress level (0.0 to 1.0)
    pub stress: f32,
    /// Beat position
    pub beat_position: BeatPosition,
}

/// Breath/pause marker for natural flow
#[derive(Debug, Clone)]
pub struct BreathMarker {
    /// Time position
    pub time: f32,
    /// Duration of breath/pause
    pub duration: f32,
    /// Type of pause
    pub pause_type: PauseType,
}

/// Types of pauses in rap flow
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum PauseType {
    /// Quick breath between phrases
    Breath,
    /// Dramatic pause for emphasis
    Dramatic,
    /// Bar transition pause
    BarEnd,
    /// Verse transition
    VerseEnd,
}

impl BreathMarker {
    pub fn breath(time: f32) -> Self {
        Self {
            time,
            duration: 0.15,
            pause_type: PauseType::Breath,
        }
    }

    pub fn dramatic(time: f32) -> Self {
        Self {
            time,
            duration: 0.4,
            pause_type: PauseType::Dramatic,
        }
    }

    pub fn bar_end(time: f32) -> Self {
        Self {
            time,
            duration: 0.25,
            pause_type: PauseType::BarEnd,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_beat_position_from_time() {
        let pos = BeatPosition::from_time(2.5, 120.0, 4);
        // At 120 BPM, one beat = 0.5s, one bar = 2.0s
        // 2.5s = 1 bar + 1 beat
        assert_eq!(pos.bar, 1);
        assert_eq!(pos.beat, 1);
    }

    #[test]
    fn test_beat_position_to_time() {
        let pos = BeatPosition {
            bar: 1,
            beat: 2,
            subdivision: 0,
            time: 0.0,
        };
        let time = pos.to_time(120.0, 4);
        // 1 bar (2s) + 2 beats (1s) = 3s
        assert!((time - 3.0).abs() < 0.001);
    }

    #[test]
    fn test_beat_sync_quantize() {
        let sync = BeatSync::new(120.0);
        // At 120 BPM, 16th note = 0.125s
        let quantized = sync.quantize_16th(0.13);
        assert!((quantized - 0.125).abs() < 0.001);
    }

    #[test]
    fn test_flow_pattern_boom_bap() {
        let pattern = FlowPattern::boom_bap();
        assert_eq!(pattern.syllable_count(), 8);
        assert!(pattern.stresses[0] > pattern.stresses[1]); // First beat is strongest
    }

    #[test]
    fn test_syllable_mapping() {
        let sync = BeatSync::new(120.0);
        let pattern = FlowPattern::boom_bap();
        let syllables: Vec<String> = vec!["yo", "check", "the", "mic"]
            .into_iter()
            .map(String::from)
            .collect();

        let timings = sync.map_syllables(&syllables, &pattern, 0);

        assert_eq!(timings.len(), 4);
        assert!(timings[0].start_time < timings[1].start_time);
        assert!(timings[0].stress > timings[1].stress); // First syllable is on strong beat
    }

    #[test]
    fn test_swing() {
        let mut sync = BeatSync::new(120.0);
        sync.swing = SwingConfig::hip_hop();

        let straight = 0.125; // Off-beat 16th note
        let swung = sync.apply_swing(straight);

        assert!(swung > straight); // Swing delays off-beats
    }
}
