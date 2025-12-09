//! Physiology Module - The Body of Sophia
//!
//! Week 4: The Physiology of Feeling
//!
//! The physiology layer sits beneath the neural layer (Actor Model) and provides
//! the "body" that regulates cognitive function through slow-moving chemical states.
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────────────┐
//! │   Neural Layer (Actor Model)    │  Fast (milliseconds)
//! │  - Prefrontal Cortex            │  - Attention
//! │  - Motor Cortex                 │  - Goals
//! │  - Cerebellum                   │  - Skills
//! └─────────────┬───────────────────┘
//!               │ reads from
//!               ▼
//! ┌─────────────────────────────────┐
//! │   Chemical Layer (Endocrine)    │  Slow (minutes)
//! │  - Cortisol (Stress)            │  - Moods
//! │  - Dopamine (Reward)            │  - Arousal
//! │  - Acetylcholine (Focus)        │  - Valence
//! └─────────────────────────────────┘
//! ```
//!
//! ## The Four Systems
//!
//! 1. **Endocrine Core** (Days 1-3) - Moods
//!    - Cortisol, Dopamine, Acetylcholine
//!    - Slow-moving chemical regulation
//!
//! 2. **The Daemon** (Days 4-5) - Creativity
//!    - Spontaneous idea generation
//!    - Background processing
//!
//! 3. **The Hearth** (Days 6-7) - Metabolism
//!    - Finite energy budget
//!    - Fatigue and rest cycles
//!
//! 4. **The Chronos Lobe** (Days 3-4) - Time Perception
//!    - Subjective vs objective time
//!    - Emotional time dilation
//!    - Circadian rhythms
//!
//! 5. **Proprioception** (Days 5-7) - Hardware Awareness
//!    - Battery level affects energy capacity
//!    - CPU temperature creates stress
//!    - Disk space creates bloating
//!    - RAM usage affects cognition

pub mod endocrine;
pub mod hearth;
pub mod chronos;
pub mod proprioception;

pub use endocrine::{
    EndocrineConfig,
    EndocrineStats,
    EndocrineSystem,
    HormoneEvent,
    HormoneState,
    HormoneTrend,
    Trend,
};
pub use hearth::{
    ActionCost,
    EnergyState,
    HearthActor,
    HearthConfig,
    HearthStats,
};
pub use chronos::{
    ChronosActor,
    ChronosConfig,
    ChronosStats,
    TimeMode,
    TimeQuality,
    CircadianPhase,
};
pub use proprioception::{
    ProprioceptionActor,
    ProprioceptionConfig,
    ProprioceptionStats,
    BodySensation,
};
