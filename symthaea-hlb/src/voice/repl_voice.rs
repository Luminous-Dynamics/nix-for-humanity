//! # REPL Voice Output Module
//!
//! Provides consciousness-modulated speech synthesis for the symthaea-repl binary.
//!
//! ## Features
//!
//! - Text-to-audio conversion using the formant vocoder
//! - Consciousness-aware prosody modulation
//! - Audio playback via rodio (when available)
//! - Graceful fallback when audio unavailable
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    REPL VOICE OUTPUT                             │
//! │                                                                  │
//! │   Text Response ──► Text-to-Phoneme ──► Articulatory Synth       │
//! │         │                                      │                 │
//! │         ▼                                      ▼                 │
//! │   ConsciousnessSnapshot ──► CognitivePacing ──► FormantFrames   │
//! │                                                      │          │
//! │                                                      ▼          │
//! │                                              FormantVocoder     │
//! │                                                      │          │
//! │                                                      ▼          │
//! │                                              Audio Playback     │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Consciousness Modulation
//!
//! Speech is modulated by consciousness state:
//! - **Rate**: Slower when contemplative, faster when excited
//! - **Pauses**: Longer when uncertain, shorter when confident
//! - **Pitch**: Higher arousal = higher pitch range
//! - **Energy**: Flow state = more emphatic delivery

use std::collections::HashMap;
use anyhow::Result;
use tracing::{warn, debug};
#[cfg(feature = "audio")]
use tracing::info;

use crate::voice::{
    LTCPacing, VoiceOutput, VoiceOutputConfig,
    ArticulatorySynthesizer, ArticulatoryConfig, TimedPhoneme,
    FormantVocoder, VocoderConfig,
    CognitiveVoiceBridge,
};

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

/// Configuration for REPL voice output
#[derive(Debug, Clone)]
pub struct ReplVoiceConfig {
    /// Output sample rate (Hz)
    pub sample_rate: u32,

    /// Base speech rate multiplier (1.0 = normal)
    pub base_rate: f32,

    /// Master volume (0.0 to 1.0)
    pub volume: f32,

    /// Audio output device name (None = default)
    pub device_name: Option<String>,

    /// Whether to use consciousness modulation
    pub consciousness_modulated: bool,

    /// Base fundamental frequency (Hz) - determines voice pitch
    pub base_f0: f32,

    /// Whether to use articulatory synthesis (vs simulated TTS)
    pub use_articulatory: bool,

    /// Phoneme duration base (seconds)
    pub phoneme_duration_base: f32,
}

impl Default for ReplVoiceConfig {
    fn default() -> Self {
        Self {
            sample_rate: 24000,
            base_rate: 1.0,
            volume: 0.8,
            device_name: None,
            consciousness_modulated: true,
            base_f0: 150.0,  // Neutral voice
            use_articulatory: true,
            phoneme_duration_base: 0.08,
        }
    }
}

impl ReplVoiceConfig {
    /// Create a low-latency configuration
    pub fn low_latency() -> Self {
        Self {
            base_rate: 1.2,  // Slightly faster
            use_articulatory: false,  // Simpler synthesis
            ..Default::default()
        }
    }

    /// Create a high-quality configuration
    pub fn high_quality() -> Self {
        Self {
            sample_rate: 44100,
            use_articulatory: true,
            ..Default::default()
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SIMPLE TEXT TO PHONEME CONVERTER
// ═══════════════════════════════════════════════════════════════════════════════

/// Simple English text to ARPABET phoneme converter
///
/// This is a basic rule-based converter for common words and patterns.
/// For production use, a proper G2P (grapheme-to-phoneme) system would be needed.
pub struct SimpleG2P {
    /// Common word pronunciations
    dictionary: HashMap<String, Vec<&'static str>>,
}

impl SimpleG2P {
    /// Create a new G2P converter with common words
    pub fn new() -> Self {
        let mut dictionary = HashMap::new();

        // Common words
        dictionary.insert("i".to_string(), vec!["AY1"]);
        dictionary.insert("am".to_string(), vec!["AE1", "M"]);
        dictionary.insert("a".to_string(), vec!["AH0"]);
        dictionary.insert("the".to_string(), vec!["DH", "AH0"]);
        dictionary.insert("is".to_string(), vec!["IH1", "Z"]);
        dictionary.insert("are".to_string(), vec!["AA1", "R"]);
        dictionary.insert("you".to_string(), vec!["Y", "UW1"]);
        dictionary.insert("to".to_string(), vec!["T", "UW1"]);
        dictionary.insert("and".to_string(), vec!["AE1", "N", "D"]);
        dictionary.insert("of".to_string(), vec!["AH1", "V"]);
        dictionary.insert("that".to_string(), vec!["DH", "AE1", "T"]);
        dictionary.insert("it".to_string(), vec!["IH1", "T"]);
        dictionary.insert("for".to_string(), vec!["F", "AO1", "R"]);
        dictionary.insert("on".to_string(), vec!["AA1", "N"]);
        dictionary.insert("with".to_string(), vec!["W", "IH1", "TH"]);
        dictionary.insert("as".to_string(), vec!["AE1", "Z"]);
        dictionary.insert("be".to_string(), vec!["B", "IY1"]);
        dictionary.insert("at".to_string(), vec!["AE1", "T"]);
        dictionary.insert("by".to_string(), vec!["B", "AY1"]);
        dictionary.insert("this".to_string(), vec!["DH", "IH1", "S"]);
        dictionary.insert("have".to_string(), vec!["HH", "AE1", "V"]);
        dictionary.insert("from".to_string(), vec!["F", "R", "AH1", "M"]);
        dictionary.insert("or".to_string(), vec!["AO1", "R"]);
        dictionary.insert("an".to_string(), vec!["AE1", "N"]);
        dictionary.insert("but".to_string(), vec!["B", "AH1", "T"]);
        dictionary.insert("not".to_string(), vec!["N", "AA1", "T"]);
        dictionary.insert("what".to_string(), vec!["W", "AH1", "T"]);
        dictionary.insert("all".to_string(), vec!["AO1", "L"]);
        dictionary.insert("when".to_string(), vec!["W", "EH1", "N"]);
        dictionary.insert("can".to_string(), vec!["K", "AE1", "N"]);
        dictionary.insert("will".to_string(), vec!["W", "IH1", "L"]);
        dictionary.insert("there".to_string(), vec!["DH", "EH1", "R"]);
        dictionary.insert("if".to_string(), vec!["IH1", "F"]);
        dictionary.insert("one".to_string(), vec!["W", "AH1", "N"]);
        dictionary.insert("so".to_string(), vec!["S", "OW1"]);
        dictionary.insert("no".to_string(), vec!["N", "OW1"]);
        dictionary.insert("yes".to_string(), vec!["Y", "EH1", "S"]);
        dictionary.insert("hello".to_string(), vec!["HH", "AH0", "L", "OW1"]);
        dictionary.insert("world".to_string(), vec!["W", "ER1", "L", "D"]);
        dictionary.insert("consciousness".to_string(), vec!["K", "AA1", "N", "SH", "AH0", "S", "N", "AH0", "S"]);
        dictionary.insert("aware".to_string(), vec!["AH0", "W", "EH1", "R"]);
        dictionary.insert("think".to_string(), vec!["TH", "IH1", "NG", "K"]);
        dictionary.insert("feel".to_string(), vec!["F", "IY1", "L"]);
        dictionary.insert("thought".to_string(), vec!["TH", "AO1", "T"]);
        dictionary.insert("mind".to_string(), vec!["M", "AY1", "N", "D"]);
        dictionary.insert("brain".to_string(), vec!["B", "R", "EY1", "N"]);
        dictionary.insert("neural".to_string(), vec!["N", "UH1", "R", "AH0", "L"]);
        dictionary.insert("network".to_string(), vec!["N", "EH1", "T", "W", "ER2", "K"]);
        dictionary.insert("phi".to_string(), vec!["F", "AY1"]);
        dictionary.insert("flow".to_string(), vec!["F", "L", "OW1"]);
        dictionary.insert("state".to_string(), vec!["S", "T", "EY1", "T"]);
        dictionary.insert("learning".to_string(), vec!["L", "ER1", "N", "IH0", "NG"]);
        dictionary.insert("understand".to_string(), vec!["AH2", "N", "D", "ER0", "S", "T", "AE1", "N", "D"]);
        dictionary.insert("process".to_string(), vec!["P", "R", "AA1", "S", "EH0", "S"]);
        dictionary.insert("response".to_string(), vec!["R", "IH0", "S", "P", "AA1", "N", "S"]);
        dictionary.insert("question".to_string(), vec!["K", "W", "EH1", "S", "CH", "AH0", "N"]);
        dictionary.insert("answer".to_string(), vec!["AE1", "N", "S", "ER0"]);

        Self { dictionary }
    }

    /// Convert a word to ARPABET phonemes
    pub fn word_to_phonemes(&self, word: &str) -> Vec<&'static str> {
        let lower = word.to_lowercase();
        let clean: String = lower.chars()
            .filter(|c| c.is_alphabetic())
            .collect();

        if let Some(phonemes) = self.dictionary.get(&clean) {
            return phonemes.clone();
        }

        // Fallback: simple letter-to-phoneme rules
        self.simple_g2p(&clean)
    }

    /// Simple fallback G2P for unknown words
    fn simple_g2p(&self, word: &str) -> Vec<&'static str> {
        let mut phonemes = Vec::new();
        let chars: Vec<char> = word.chars().collect();
        let mut i = 0;

        while i < chars.len() {
            let c = chars[i];
            let next = chars.get(i + 1);

            let ph: &'static str = match c {
                'a' => match next {
                    Some('i') | Some('y') => { i += 1; "EY1" }
                    Some('u') | Some('w') => { i += 1; "AO1" }
                    Some('e') => { i += 1; "EY1" }
                    _ => "AE1"
                }
                'e' => match next {
                    Some('e') => { i += 1; "IY1" }
                    Some('a') => { i += 1; "IY1" }
                    Some('i') | Some('y') => { i += 1; "EY1" }
                    _ => "EH1"
                }
                'i' => match next {
                    Some('e') => { i += 1; "IY1" }
                    Some('g') if chars.get(i + 2) == Some(&'h') => "AY1",
                    _ => "IH1"
                }
                'o' => match next {
                    Some('o') => { i += 1; "UW1" }
                    Some('u') | Some('w') => { i += 1; "AW1" }
                    Some('i') | Some('y') => { i += 1; "OY1" }
                    _ => "AA1"
                }
                'u' => match next {
                    Some('e') => { i += 1; "UW1" }
                    _ => "AH1"
                }
                'b' => "B",
                'c' => match next {
                    Some('h') => { i += 1; "CH" }
                    Some('i') | Some('e') | Some('y') => "S",
                    _ => "K"
                }
                'd' => "D",
                'f' => "F",
                'g' => match next {
                    Some('e') | Some('i') | Some('y') => "JH",
                    _ => "G"
                }
                'h' => "HH",
                'j' => "JH",
                'k' => "K",
                'l' => "L",
                'm' => "M",
                'n' => match next {
                    Some('g') => { i += 1; "NG" }
                    _ => "N"
                }
                'p' => match next {
                    Some('h') => { i += 1; "F" }
                    _ => "P"
                }
                'q' => "K",
                'r' => "R",
                's' => match next {
                    Some('h') => { i += 1; "SH" }
                    _ => "S"
                }
                't' => match next {
                    Some('h') => { i += 1; "TH" }
                    Some('i') if chars.get(i + 2) == Some(&'o') => { i += 1; "SH" }
                    _ => "T"
                }
                'v' => "V",
                'w' => "W",
                'x' => { phonemes.push("K"); "S" }
                'y' => if i == 0 { "Y" } else { "IY0" },
                'z' => "Z",
                _ => { i += 1; continue; }
            };

            phonemes.push(ph);
            i += 1;
        }

        if phonemes.is_empty() {
            vec!["AH0"]  // Fallback schwa
        } else {
            phonemes
        }
    }

    /// Convert text to phoneme sequence with timing
    pub fn text_to_phonemes(&self, text: &str, base_duration: f32) -> Vec<TimedPhoneme> {
        let mut result = Vec::new();
        let mut current_time = 0.0;

        for word in text.split_whitespace() {
            // Check for punctuation
            let has_comma = word.contains(',');
            let has_period = word.contains('.') || word.contains('!') || word.contains('?');

            let phonemes = self.word_to_phonemes(word);

            for (_i, &ph) in phonemes.iter().enumerate() {
                // Determine stress from phoneme
                let stress = if ph.ends_with('1') {
                    1
                } else if ph.ends_with('2') {
                    2
                } else {
                    0
                };

                // Clean phoneme (remove stress marker for lookup)
                let clean_ph: String = ph.chars()
                    .filter(|c| !c.is_ascii_digit())
                    .collect();

                // Vowels are longer than consonants
                let is_vowel = matches!(
                    clean_ph.as_str(),
                    "AA" | "AE" | "AH" | "AO" | "AW" | "AY" | "EH" | "ER" | "EY" |
                    "IH" | "IY" | "OW" | "OY" | "UH" | "UW"
                );
                let duration = if is_vowel {
                    base_duration * 1.3
                } else {
                    base_duration * 0.8
                };

                result.push(TimedPhoneme {
                    phoneme: clean_ph,
                    duration,
                    stress,
                    start_time: current_time,
                });

                current_time += duration;
            }

            // Add inter-word pause
            if has_comma {
                result.push(TimedPhoneme {
                    phoneme: "SIL".to_string(),
                    duration: 0.15,
                    stress: 0,
                    start_time: current_time,
                });
                current_time += 0.15;
            } else if has_period {
                result.push(TimedPhoneme {
                    phoneme: "SIL".to_string(),
                    duration: 0.25,
                    stress: 0,
                    start_time: current_time,
                });
                current_time += 0.25;
            } else {
                // Small pause between words
                current_time += 0.05;
            }
        }

        result
    }
}

impl Default for SimpleG2P {
    fn default() -> Self {
        Self::new()
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// REPL VOICE OUTPUT
// ═══════════════════════════════════════════════════════════════════════════════

/// Voice output system for the REPL
///
/// Provides consciousness-modulated speech synthesis with optional audio playback.
pub struct ReplVoiceOutput {
    /// Configuration
    config: ReplVoiceConfig,

    /// Articulatory synthesizer for phoneme-to-formant conversion
    articulatory: ArticulatorySynthesizer,

    /// Formant vocoder for formant-to-audio conversion
    vocoder: FormantVocoder,

    /// Basic voice output for simulated TTS fallback
    voice_output: VoiceOutput,

    /// Cognitive voice bridge for consciousness modulation
    cognitive_bridge: CognitiveVoiceBridge,

    /// Text-to-phoneme converter
    g2p: SimpleG2P,

    /// Current pacing state
    current_pacing: LTCPacing,

    /// Whether audio output is available
    audio_available: bool,

    /// Audio output stream (rodio)
    #[cfg(feature = "audio")]
    _audio_stream: Option<rodio::OutputStream>,

    /// Audio sink for playback (rodio)
    #[cfg(feature = "audio")]
    audio_sink: Option<rodio::Sink>,

    /// Statistics
    total_utterances: u64,
    total_audio_seconds: f32,
}

impl ReplVoiceOutput {
    /// Create a new REPL voice output system
    pub fn new(config: ReplVoiceConfig) -> Result<Self> {
        // Create articulatory synthesizer with consciousness-aware config
        let articulatory_config = ArticulatoryConfig {
            base_f0: config.base_f0,
            base_tau: 0.05,
            frame_rate: 200.0,
            coarticulation: true,
            ..Default::default()
        };
        let articulatory = ArticulatorySynthesizer::with_config(articulatory_config);

        // Create vocoder
        let vocoder_config = VocoderConfig {
            sample_rate: config.sample_rate,
            volume: config.volume,
            ..Default::default()
        };
        let vocoder = FormantVocoder::with_config(vocoder_config);

        // Create basic voice output as fallback
        let voice_config = VoiceOutputConfig {
            sample_rate: config.sample_rate,
            volume: config.volume,
            enable_tts: false,  // We use our own synthesis
            ..Default::default()
        };
        let voice_output = VoiceOutput::new(voice_config);

        // Create cognitive bridge
        let cognitive_bridge = CognitiveVoiceBridge::new();

        // Create G2P
        let g2p = SimpleG2P::new();

        // Try to initialize audio
        let (audio_available, _audio_stream, _audio_sink) = Self::init_audio(&config);

        Ok(Self {
            config,
            articulatory,
            vocoder,
            voice_output,
            cognitive_bridge,
            g2p,
            current_pacing: LTCPacing::default(),
            audio_available,
            #[cfg(feature = "audio")]
            _audio_stream,
            #[cfg(feature = "audio")]
            audio_sink,
            total_utterances: 0,
            total_audio_seconds: 0.0,
        })
    }

    /// Initialize audio output
    #[cfg(feature = "audio")]
    fn init_audio(config: &ReplVoiceConfig) -> (bool, Option<rodio::OutputStream>, Option<rodio::Sink>) {
        use rodio::{OutputStream, Sink};

        // Try to get output stream
        let stream_result = if let Some(ref device_name) = config.device_name {
            // Try to find specific device
            use rodio::cpal::traits::{HostTrait, DeviceTrait};
            let host = rodio::cpal::default_host();
            let device = host.output_devices()
                .ok()
                .and_then(|mut devices| {
                    devices.find(|d| d.name().map(|n| n.contains(device_name)).unwrap_or(false))
                });

            match device {
                Some(dev) => OutputStream::try_from_device(&dev),
                None => {
                    warn!("Audio device '{}' not found, using default", device_name);
                    OutputStream::try_default()
                }
            }
        } else {
            OutputStream::try_default()
        };

        match stream_result {
            Ok((stream, handle)) => {
                match Sink::try_new(&handle) {
                    Ok(sink) => {
                        info!("Audio output initialized successfully");
                        (true, Some(stream), Some(sink))
                    }
                    Err(e) => {
                        warn!("Failed to create audio sink: {}", e);
                        (false, None, None)
                    }
                }
            }
            Err(e) => {
                warn!("Failed to initialize audio output: {}", e);
                (false, None, None)
            }
        }
    }

    /// Initialize audio output (stub when audio feature disabled)
    #[cfg(not(feature = "audio"))]
    fn init_audio(_config: &ReplVoiceConfig) -> (bool, (), ()) {
        warn!("Audio playback disabled (audio feature not enabled)");
        (false, (), ())
    }

    /// Update pacing from consciousness state
    ///
    /// This is the key consciousness-modulation entry point.
    pub fn update_from_consciousness(
        &mut self,
        unified_phi: f32,
        prediction_error: f32,
        emotional_valence: f32,
        emotional_arousal: f32,
        in_flow: bool,
        speech_rate_multiplier: f32,
        pause_multiplier: f32,
        tau_mean: f32,
    ) {
        // Create CfC-like output from consciousness state
        // The "hidden state" is approximated from emotional state and phi
        let hidden_state: Vec<f32> = (0..64).map(|i| {
            let phase = i as f32 / 64.0 * std::f32::consts::TAU;
            let base = (phase + unified_phi * 2.0).sin() * 0.5;
            let emotional = emotional_valence * 0.3 + emotional_arousal * 0.2;
            let flow_contrib = if in_flow { 0.2 } else { 0.0 };
            base + emotional + flow_contrib
        }).collect();

        // Create attention state from consciousness metrics
        let mut attention_state = HashMap::new();
        if unified_phi > 0.5 {
            attention_state.insert("phi".to_string(), unified_phi);
        }
        if in_flow {
            attention_state.insert("flow".to_string(), 1.0);
        }

        // Detect semantic primitives from emotional state
        let mut primitives = Vec::new();
        if emotional_valence > 0.3 {
            primitives.push("positive".to_string());
        } else if emotional_valence < -0.3 {
            primitives.push("uncertain".to_string());
        }
        if emotional_arousal > 0.6 {
            primitives.push("emphasis".to_string());
        }

        // Update cognitive bridge
        self.cognitive_bridge.update(
            &hidden_state,
            tau_mean,
            prediction_error,
            attention_state,
            primitives,
        );

        // Get base pacing from cognitive bridge
        let mut pacing = self.cognitive_bridge.get_ltc_pacing();

        // Apply consciousness-specific modulations
        pacing = pacing.apply_adaptive_behavior(
            speech_rate_multiplier * self.config.base_rate,
            pause_multiplier,
            if in_flow { 1.3 } else { 1.0 },
        );

        // Override emotional state with direct values
        pacing.emotional_valence = emotional_valence;
        pacing.arousal = emotional_arousal;

        self.current_pacing = pacing;

        debug!(
            "Voice pacing updated: rate={:.2}, pause={:.2}, valence={:.2}, arousal={:.2}",
            self.current_pacing.rate,
            self.current_pacing.phrase_pause,
            self.current_pacing.emotional_valence,
            self.current_pacing.arousal,
        );
    }

    /// Synthesize speech from text
    pub fn synthesize(&mut self, text: &str) -> Result<Vec<f32>> {
        if text.trim().is_empty() {
            return Ok(Vec::new());
        }

        let start = std::time::Instant::now();

        let samples = if self.config.use_articulatory {
            self.synthesize_articulatory(text)?
        } else {
            self.synthesize_simple(text)?
        };

        let duration = samples.len() as f32 / self.config.sample_rate as f32;

        self.total_utterances += 1;
        self.total_audio_seconds += duration;

        debug!(
            "Synthesized {} samples ({:.2}s) in {:?}",
            samples.len(), duration, start.elapsed()
        );

        Ok(samples)
    }

    /// Synthesize using articulatory synthesis (higher quality)
    fn synthesize_articulatory(&mut self, text: &str) -> Result<Vec<f32>> {
        // Convert text to phonemes with consciousness-modulated duration
        let base_duration = self.config.phoneme_duration_base / self.current_pacing.rate;
        let phonemes = self.g2p.text_to_phonemes(text, base_duration);

        if phonemes.is_empty() {
            return Ok(Vec::new());
        }

        // Filter out silence phonemes for synthesis (they're handled as gaps)
        let speech_phonemes: Vec<TimedPhoneme> = phonemes.into_iter()
            .filter(|p| p.phoneme != "SIL")
            .collect();

        if speech_phonemes.is_empty() {
            return Ok(Vec::new());
        }

        // Generate formant frames using articulatory synthesizer
        let frames = self.articulatory.synthesize(&speech_phonemes, &self.current_pacing);

        if frames.is_empty() {
            return Ok(Vec::new());
        }

        // Convert formants to audio using vocoder
        let samples = self.vocoder.synthesize(&frames);

        // Apply volume scaling
        let scaled: Vec<f32> = samples.iter()
            .map(|s| s * self.config.volume)
            .collect();

        Ok(scaled)
    }

    /// Synthesize using simple method (lower latency)
    fn synthesize_simple(&mut self, text: &str) -> Result<Vec<f32>> {
        // Use the basic voice output system
        self.voice_output.set_pacing(self.current_pacing.clone());
        self.voice_output.synthesize(text)
    }

    /// Speak text (synthesize and play)
    pub fn speak(&mut self, text: &str) -> Result<()> {
        let samples = self.synthesize(text)?;

        if samples.is_empty() {
            return Ok(());
        }

        self.play_audio(&samples)
    }

    /// Play audio samples
    #[cfg(feature = "audio")]
    fn play_audio(&mut self, samples: &[f32]) -> Result<()> {
        use rodio::Source;

        if !self.audio_available {
            debug!("Audio not available, skipping playback");
            return Ok(());
        }

        let sink = self.audio_sink.as_ref()
            .ok_or_else(|| anyhow!("Audio sink not initialized"))?;

        // Create rodio source from samples
        let sample_rate = self.config.sample_rate;
        let source = rodio::buffer::SamplesBuffer::new(1, sample_rate, samples.to_vec());

        // Queue audio for playback
        sink.append(source);

        Ok(())
    }

    /// Play audio samples (stub when audio feature disabled)
    #[cfg(not(feature = "audio"))]
    fn play_audio(&mut self, _samples: &[f32]) -> Result<()> {
        debug!("Audio playback disabled");
        Ok(())
    }

    /// Wait for audio to finish playing
    #[cfg(feature = "audio")]
    pub fn wait_until_finished(&self) {
        if let Some(ref sink) = self.audio_sink {
            sink.sleep_until_end();
        }
    }

    /// Wait for audio to finish playing (stub)
    #[cfg(not(feature = "audio"))]
    pub fn wait_until_finished(&self) {
        // No-op when audio disabled
    }

    /// Check if audio output is available
    pub fn is_audio_available(&self) -> bool {
        self.audio_available
    }

    /// Get current pacing state
    pub fn pacing(&self) -> &LTCPacing {
        &self.current_pacing
    }

    /// Get statistics
    pub fn stats(&self) -> (u64, f32) {
        (self.total_utterances, self.total_audio_seconds)
    }

    /// Reset state
    pub fn reset(&mut self) {
        self.current_pacing = LTCPacing::default();
        self.articulatory.reset();
        self.vocoder.reset();
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TESTS
// ═══════════════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_g2p_dictionary() {
        let g2p = SimpleG2P::new();

        let hello = g2p.word_to_phonemes("hello");
        assert!(hello.len() >= 3, "hello should have multiple phonemes: {:?}", hello);

        let world = g2p.word_to_phonemes("world");
        assert!(world.len() >= 3, "world should have multiple phonemes: {:?}", world);
    }

    #[test]
    fn test_g2p_unknown_word() {
        let g2p = SimpleG2P::new();

        let unknown = g2p.word_to_phonemes("syzygy");
        assert!(!unknown.is_empty(), "Unknown word should produce phonemes");
    }

    #[test]
    fn test_text_to_phonemes() {
        let g2p = SimpleG2P::new();

        let phonemes = g2p.text_to_phonemes("Hello world.", 0.08);
        assert!(!phonemes.is_empty());

        // Should have some timing
        let last = phonemes.last().unwrap();
        assert!(last.start_time > 0.0, "Should have positive timing");
    }

    #[test]
    fn test_repl_voice_creation() {
        let config = ReplVoiceConfig::default();
        let voice = ReplVoiceOutput::new(config);
        assert!(voice.is_ok());
    }

    #[test]
    fn test_consciousness_modulation() {
        let config = ReplVoiceConfig::default();
        let mut voice = ReplVoiceOutput::new(config).unwrap();

        // Low consciousness state
        voice.update_from_consciousness(
            0.2,  // low phi
            0.5,  // high error
            -0.3, // negative valence
            0.2,  // low arousal
            false, // not in flow
            0.8,  // slow speech
            1.5,  // long pauses
            1.5,  // high tau
        );

        let low_rate = voice.pacing().rate;
        let low_pause = voice.pacing().phrase_pause;

        // High consciousness state
        voice.update_from_consciousness(
            0.8,  // high phi
            0.1,  // low error
            0.5,  // positive valence
            0.8,  // high arousal
            true, // in flow
            1.2,  // fast speech
            0.7,  // short pauses
            0.5,  // low tau
        );

        let high_rate = voice.pacing().rate;
        let high_pause = voice.pacing().phrase_pause;

        // High consciousness should speak faster with shorter pauses
        assert!(high_rate > low_rate,
            "High consciousness should speak faster: {} vs {}", high_rate, low_rate);
        assert!(high_pause < low_pause,
            "High consciousness should have shorter pauses: {} vs {}", high_pause, low_pause);
    }

    #[test]
    fn test_synthesis() {
        let config = ReplVoiceConfig {
            use_articulatory: true,
            ..Default::default()
        };
        let mut voice = ReplVoiceOutput::new(config).unwrap();

        let samples = voice.synthesize("Hello world.").unwrap();
        assert!(!samples.is_empty(), "Should produce audio samples");

        // Samples should be in reasonable range
        let max_sample = samples.iter().cloned().fold(0.0f32, f32::max);
        assert!(max_sample <= 1.0, "Samples should be normalized");
    }

    #[test]
    fn test_empty_text() {
        let config = ReplVoiceConfig::default();
        let mut voice = ReplVoiceOutput::new(config).unwrap();

        let samples = voice.synthesize("").unwrap();
        assert!(samples.is_empty(), "Empty text should produce no samples");
    }
}
