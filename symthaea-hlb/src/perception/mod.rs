//! Perception - Multi-modal sensory processing
//!
//! Provides video capture, physiological signal processing, and
//! temporal feature extraction for consciousness-aware perception.

pub mod physio;
pub mod video;
pub mod social_trust;

// Audio perception - Speech recognition via symthaea-stt
pub mod audio;

// Multi-modal integration (conditionally compiled)
#[cfg(feature = "full_perception")]
pub mod multi_modal;

#[cfg(feature = "full_perception")]
pub mod conscious_perception;

#[cfg(feature = "full_perception")]
pub mod resilience;
