//! # Physics Primitives: From Quarks to Chemistry
//!
//! This module implements a compositional physics hierarchy where higher-level
//! structures are **derived** from lower-level ones using HDC operations.
//!
//! ## The God Protocol Hierarchy
//!
//! ```text
//! Layer 3: CARBON ─────────────────────────────────────────────────────┐
//!          Bundle(6×Proton, 6×Neutron, 6×Electron)                     │ CHEMISTRY
//!                     ↑              ↑           ↑                     │
//! Layer 2: PROTON ────┼──── NEUTRON ─┼───────────┼─────────────────────┤
//!          Bundle(U,U,D)    Bundle(U,D,D)        │                     │ NUCLEAR
//!                 ↑              ↑               │                     │
//! Layer 1: UP_QUARK ─── DOWN_QUARK ─── ELECTRON ─┴─────────────────────┘ STANDARD
//!          (axiom)      (axiom)        (axiom)                           MODEL
//! ```
//!
//! ## Key Insight
//!
//! Instead of hardcoding elements as independent vectors, we **construct** them:
//! - Carbon-12: `Bundle(6×Proton, 6×Neutron, 6×Electron)`
//! - Carbon-14: `Bundle(6×Proton, 8×Neutron, 6×Electron)`
//!
//! This means Symthaea **understands** isotopes inherently—they share structure
//! but differ in neutron count.
//!
//! ## From Chemistry to Nuclear Physics
//!
//! If you only give her the periodic table, she can do chemistry (mix fluids).
//! With the Standard Model, she can reason about:
//! - Nuclear isomers (batteries storing energy in the nucleus)
//! - Radioactive decay (neutron → proton + electron + antineutrino)
//! - Fusion/fission (binding energy from mass defect)
//!
//! ## Usage
//!
//! ```rust,ignore
//! use symthaea_core::physics::{StandardModel, PeriodicTable};
//! use symthaea_core::genesis::GenesisSeed;
//!
//! let genesis = GenesisSeed::from_phrase("E=mc²");
//! let model = StandardModel::from_genesis(&genesis);
//! let table = PeriodicTable::from_model(&model, &genesis);
//!
//! // Carbon is COMPOSED, not memorized
//! let carbon = table.element(6);
//! let carbon_14 = table.isotope(6, 8); // 6 protons, 8 neutrons
//!
//! // They share structure
//! let similarity = carbon.similarity(&carbon_14);
//! assert!(similarity > 0.9, "Isotopes should be highly similar");
//! ```

mod standard_model;
mod hadrons;
mod periodic_table;
mod chemistry;
mod nuclear;
mod consciousness_bridge;
mod electron_nuclear_coupling;
mod phonon_dynamics;
mod inverse_search;
mod radiation_damage;
mod high_entropy_alloys;
mod advanced_materials;
mod spark_engine;
mod thermal_transport;
mod neutron_shielding;
mod geometry;
mod pulse_dynamics;

pub use standard_model::*;
pub use hadrons::*;
pub use periodic_table::*;
pub use chemistry::*;
pub use nuclear::*;
pub use consciousness_bridge::*;
pub use electron_nuclear_coupling::*;
pub use phonon_dynamics::*;
pub use inverse_search::*;
pub use radiation_damage::*;
pub use high_entropy_alloys::*;
pub use advanced_materials::*;
pub use spark_engine::*;
pub use thermal_transport::*;
pub use neutron_shielding::*;
pub use geometry::*;
pub use pulse_dynamics::*;
