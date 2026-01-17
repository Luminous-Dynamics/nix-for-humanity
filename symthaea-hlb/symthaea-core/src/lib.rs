pub mod hdc;
pub mod phi_engine;
pub mod core;
pub mod observability;

// Convenience re-exports for external users
pub use hdc::unified_hv::{ContinuousHV, BinaryHV, HV, HDC_DIMENSION};
pub use phi_engine::{
    PhiEngine,
    PhiMethod,
    PhiResult,
    PhiCalculator,
    ContinuousPhiCalculator,
};
// Note: UnifiedConsciousnessPipeline, ConsciousMoment, and PipelineConfig are
// not available in symthaea-core (requires full consciousness module)
pub use core::{
    ConsciousnessTopology,
    TopologyType,
};

