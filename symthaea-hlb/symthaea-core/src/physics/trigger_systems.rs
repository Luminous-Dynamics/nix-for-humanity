//! # Alternative Trigger Systems for Lattice Confinement Fusion
//!
//! The original Spark Engine design calls for 0.1nm femtosecond X-rays,
//! which requires synchrotron/XFEL-class equipment. This module explores
//! practical alternatives that could enable desktop-scale LCF reactors.
//!
//! ## The Trigger Problem
//!
//! LCF requires:
//! 1. Loading deuterium into a metal lattice (Pd, Ti, Ni, etc.)
//! 2. Creating transient high-density D-D proximity
//! 3. Triggering fusion via lattice phonons + external excitation
//!
//! The challenge: How to provide enough localized energy to overcome
//! the Coulomb barrier without massive equipment?
//!
//! ## Alternative Approaches
//!
//! ```text
//! Approach              Equipment Cost    TRL    Trigger Rate    Notes
//! ─────────────────────────────────────────────────────────────────────
//! XFEL X-ray            $1B+              9      Hz-kHz          Reference
//! Electron Beam         $10K-100K         7      MHz             Compact
//! Laser Bremsstrahlung  $50K-500K         5      kHz             Tunable
//! NEEC Cascade          $100K-1M          3      Hz-kHz          Novel
//! Piezo Phonon          $1K-10K           6      MHz             Simplest
//! Pulsed Electrolysis   $1K-50K           7      Hz              Proven
//! Muon Catalysis        $10M+             4      Low             Exotic
//! ```

use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

/// Extended trigger method taxonomy
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ExtendedTriggerMethod {
    // === Electromagnetic ===
    /// Synchrotron/XFEL hard X-ray (reference, impractical)
    XfelXRay,
    /// Compact X-ray tube with Bremsstrahlung spectrum
    CompactXRay,
    /// Laser-driven inverse Compton X-ray source
    LaserCompton,
    /// Laser-driven Bremsstrahlung (target conversion)
    LaserBremsstrahlung,
    /// Direct UV/VUV laser (for NEEC-mediated)
    DirectLaser,

    // === Particle Beam ===
    /// Electron beam direct irradiation
    ElectronBeam,
    /// Proton beam (for recoil-induced fusion)
    ProtonBeam,
    /// Deuteron beam (beam-target fusion hybrid)
    DeuteronBeam,

    // === Nuclear/Exotic ===
    /// NEEC cascade through Th-229m or similar isomer
    NeecCascade,
    /// Muon-catalyzed fusion (μCF)
    MuonCatalysis,
    /// Pyroelectric crystal neutron source
    PyroelectricNeutron,

    // === Mechanical/Acoustic ===
    /// Piezoelectric phonon injection
    PiezoPhonon,
    /// Ultrasonic cavitation (sonofusion-inspired)
    Ultrasonic,
    /// Shock compression (dynamic loading)
    ShockCompression,

    // === Electrochemical ===
    /// Pulsed electrolysis (Fleischmann-Pons style, refined)
    PulsedElectrolysis,
    /// Glow discharge plasma electrolysis
    GlowDischarge,
    /// Supercritical water electrolysis
    SupercriticalElectrolysis,

    // === Thermal ===
    /// Rapid thermal cycling
    ThermalCycling,
    /// Laser ablation heating
    LaserAblation,
}

/// Technology Readiness Level (NASA scale 1-9)
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct TRL(pub u8);

impl TRL {
    pub fn basic_principles() -> Self { TRL(1) }
    pub fn technology_concept() -> Self { TRL(2) }
    pub fn proof_of_concept() -> Self { TRL(3) }
    pub fn lab_validation() -> Self { TRL(4) }
    pub fn lab_demonstration() -> Self { TRL(5) }
    pub fn prototype_demo() -> Self { TRL(6) }
    pub fn system_demo() -> Self { TRL(7) }
    pub fn qualified() -> Self { TRL(8) }
    pub fn proven() -> Self { TRL(9) }

    pub fn description(&self) -> &'static str {
        match self.0 {
            1 => "Basic principles observed",
            2 => "Technology concept formulated",
            3 => "Proof of concept",
            4 => "Lab validation",
            5 => "Lab-scale demonstration",
            6 => "Prototype demonstration",
            7 => "System demonstration",
            8 => "System qualified",
            9 => "Flight/operation proven",
            _ => "Unknown",
        }
    }
}

/// Equipment cost category
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CostCategory {
    /// < $10K - Hobbyist/maker accessible
    Maker,
    /// $10K - $100K - University lab scale
    LabScale,
    /// $100K - $1M - Research facility
    Research,
    /// $1M - $100M - Major facility
    MajorFacility,
    /// > $100M - National/international facility
    NationalFacility,
}

impl CostCategory {
    pub fn range_usd(&self) -> (f64, f64) {
        match self {
            CostCategory::Maker => (1_000.0, 10_000.0),
            CostCategory::LabScale => (10_000.0, 100_000.0),
            CostCategory::Research => (100_000.0, 1_000_000.0),
            CostCategory::MajorFacility => (1_000_000.0, 100_000_000.0),
            CostCategory::NationalFacility => (100_000_000.0, 10_000_000_000.0),
        }
    }

    pub fn median_usd(&self) -> f64 {
        let (low, high) = self.range_usd();
        (low * high).sqrt() // Geometric mean
    }
}

/// Complete trigger system specification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TriggerSystemSpec {
    /// Trigger method
    pub method: ExtendedTriggerMethod,
    /// Human-readable name
    pub name: String,
    /// Detailed description
    pub description: String,
    /// Technology readiness level
    pub trl: TRL,
    /// Equipment cost category
    pub cost: CostCategory,
    /// Estimated cost in USD
    pub cost_estimate_usd: f64,
    /// Maximum trigger repetition rate (Hz)
    pub max_rep_rate_hz: f64,
    /// Energy delivered per trigger (J)
    pub energy_per_trigger_j: f64,
    /// Electrical-to-trigger efficiency
    pub wall_plug_efficiency: f64,
    /// Physical footprint (m³)
    pub footprint_m3: f64,
    /// Key advantages
    pub advantages: Vec<String>,
    /// Key challenges/limitations
    pub challenges: Vec<String>,
    /// Physics model for trigger effectiveness
    pub physics: TriggerPhysics,
}

/// Physics model for trigger effectiveness
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TriggerPhysics {
    /// Primary energy deposition mechanism
    pub mechanism: EnergyDepositionMechanism,
    /// Characteristic penetration depth in Pd (μm)
    pub penetration_depth_um: f64,
    /// Energy deposition profile (exponential decay constant)
    pub deposition_profile_um: f64,
    /// Phonon generation efficiency (0-1)
    pub phonon_efficiency: f64,
    /// Estimated screening enhancement factor
    pub screening_factor: f64,
    /// Theoretical trigger-to-fusion conversion efficiency
    pub conversion_efficiency: f64,
}

/// How energy is deposited into the lattice
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum EnergyDepositionMechanism {
    /// Photoelectric absorption (X-ray)
    Photoelectric,
    /// Compton scattering (hard X-ray/gamma)
    Compton,
    /// Electronic stopping (charged particles)
    ElectronicStopping,
    /// Nuclear stopping (heavy ions)
    NuclearStopping,
    /// Direct phonon injection (acoustic)
    PhononInjection,
    /// Electrochemical (ion transport)
    Electrochemical,
    /// Thermal conduction
    Thermal,
    /// Nuclear recoil (neutrons, muons)
    NuclearRecoil,
}

/// Trigger system library with all alternatives
pub struct TriggerSystemLibrary {
    pub systems: Vec<TriggerSystemSpec>,
}

impl TriggerSystemLibrary {
    /// Initialize library with all known trigger systems
    pub fn new() -> Self {
        let mut systems = Vec::new();

        // === Reference: XFEL X-ray ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::XfelXRay,
            name: "XFEL Hard X-ray".to_string(),
            description: "Free-electron laser producing coherent, femtosecond X-ray pulses. \
                         Current reference design but requires billion-dollar facilities.".to_string(),
            trl: TRL::proven(),
            cost: CostCategory::NationalFacility,
            cost_estimate_usd: 1_000_000_000.0,
            max_rep_rate_hz: 27_000.0, // European XFEL
            energy_per_trigger_j: 0.001, // ~1 mJ per pulse
            wall_plug_efficiency: 1e-6, // Extremely inefficient
            footprint_m3: 1_000_000.0, // 3.4 km tunnel
            advantages: vec![
                "Highest peak brilliance".to_string(),
                "Tunable wavelength".to_string(),
                "Proven technology".to_string(),
                "Femtosecond time resolution".to_string(),
            ],
            challenges: vec![
                "Cost: >$1B".to_string(),
                "Size: kilometers".to_string(),
                "Not portable".to_string(),
                "Limited access".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::Photoelectric,
                penetration_depth_um: 10.0, // ~10 keV X-rays in Pd
                deposition_profile_um: 5.0,
                phonon_efficiency: 0.3, // Good coupling to lattice
                screening_factor: 50.0, // High due to coherent excitation
                conversion_efficiency: 1e-6, // Theoretical
            },
        });

        // === Electron Beam ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::ElectronBeam,
            name: "Compact Electron Beam".to_string(),
            description: "Desktop-scale electron gun (10-100 keV) directly irradiating \
                         deuterated target. Electrons deposit energy via electronic stopping, \
                         generating phonons and local heating.".to_string(),
            trl: TRL::system_demo(),
            cost: CostCategory::LabScale,
            cost_estimate_usd: 50_000.0,
            max_rep_rate_hz: 1_000_000.0, // MHz pulsing possible
            energy_per_trigger_j: 1e-6, // μJ per pulse
            wall_plug_efficiency: 0.3, // Reasonable efficiency
            footprint_m3: 0.1, // Desktop
            advantages: vec![
                "Compact and affordable".to_string(),
                "High rep rate (MHz)".to_string(),
                "Direct energy deposition".to_string(),
                "Well-understood technology".to_string(),
                "Tunable energy (1-100 keV)".to_string(),
            ],
            challenges: vec![
                "Limited penetration depth".to_string(),
                "Vacuum required".to_string(),
                "Surface damage over time".to_string(),
                "Bremsstrahlung X-ray generation".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::ElectronicStopping,
                penetration_depth_um: 5.0, // 50 keV electrons in Pd
                deposition_profile_um: 2.0,
                phonon_efficiency: 0.5, // Good phonon generation
                screening_factor: 20.0, // Moderate screening enhancement
                conversion_efficiency: 1e-8,
            },
        });

        // === Laser Bremsstrahlung ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::LaserBremsstrahlung,
            name: "Laser-Driven Bremsstrahlung X-ray".to_string(),
            description: "High-intensity laser (>10^18 W/cm²) focused on high-Z target \
                         generates hot electrons that produce Bremsstrahlung X-rays. \
                         Compact alternative to synchrotrons.".to_string(),
            trl: TRL::lab_demonstration(),
            cost: CostCategory::Research,
            cost_estimate_usd: 300_000.0,
            max_rep_rate_hz: 1000.0, // kHz lasers available
            energy_per_trigger_j: 0.01, // 10 mJ X-ray yield
            wall_plug_efficiency: 1e-4, // Low conversion
            footprint_m3: 5.0, // Optical table + laser
            advantages: vec![
                "Desktop X-ray source".to_string(),
                "Tunable spectrum".to_string(),
                "Ultra-short pulses possible".to_string(),
                "No accelerator needed".to_string(),
            ],
            challenges: vec![
                "Low conversion efficiency".to_string(),
                "Target debris".to_string(),
                "Laser maintenance".to_string(),
                "Broad spectrum (not monochromatic)".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::Photoelectric,
                penetration_depth_um: 20.0, // Broad spectrum
                deposition_profile_um: 10.0,
                phonon_efficiency: 0.2,
                screening_factor: 30.0,
                conversion_efficiency: 1e-7,
            },
        });

        // === NEEC Cascade ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::NeecCascade,
            name: "NEEC Cascade via Th-229m".to_string(),
            description: "Uses Thorium-229m's uniquely low nuclear transition (8.28 eV, VUV) \
                         as an intermediary. VUV laser excites Th-229m, which then transfers \
                         energy to nearby D nuclei through lattice phonons. Requires Th-doped \
                         deuteride target.".to_string(),
            trl: TRL::proof_of_concept(),
            cost: CostCategory::Research,
            cost_estimate_usd: 500_000.0,
            max_rep_rate_hz: 10_000.0, // Limited by Th-229m lifetime
            energy_per_trigger_j: 1e-9, // nJ photon, amplified by nuclear
            wall_plug_efficiency: 0.01, // Potentially high
            footprint_m3: 1.0, // VUV laser system
            advantages: vec![
                "Nuclear-scale energy from optical photon".to_string(),
                "Highly selective excitation".to_string(),
                "Potential for very high efficiency".to_string(),
                "Novel physics pathway".to_string(),
            ],
            challenges: vec![
                "Th-229 availability/cost".to_string(),
                "VUV laser technology immature".to_string(),
                "Nuclear-lattice coupling unproven".to_string(),
                "Regulatory hurdles (thorium)".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::NuclearRecoil,
                penetration_depth_um: 1000.0, // VUV absorbed at surface, energy propagates
                deposition_profile_um: 100.0,
                phonon_efficiency: 0.8, // High if coupling works
                screening_factor: 100.0, // Potentially very high
                conversion_efficiency: 1e-5, // Speculative but promising
            },
        });

        // === Piezoelectric Phonon Injection ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::PiezoPhonon,
            name: "Piezoelectric Phonon Injection".to_string(),
            description: "High-frequency piezoelectric transducers (MHz-GHz) mechanically \
                         coupled to deuteride lattice. Generates coherent phonon waves that \
                         create transient D-D proximity enhancement.".to_string(),
            trl: TRL::prototype_demo(),
            cost: CostCategory::Maker,
            cost_estimate_usd: 5_000.0,
            max_rep_rate_hz: 1_000_000_000.0, // GHz
            energy_per_trigger_j: 1e-9, // nJ acoustic energy
            wall_plug_efficiency: 0.5, // Piezo efficiency
            footprint_m3: 0.001, // Tiny
            advantages: vec![
                "Extremely simple and cheap".to_string(),
                "No vacuum required".to_string(),
                "GHz repetition rates".to_string(),
                "Direct phonon generation".to_string(),
                "Scalable array designs".to_string(),
            ],
            challenges: vec![
                "Low energy per pulse".to_string(),
                "Acoustic impedance matching".to_string(),
                "Heating at high power".to_string(),
                "Unknown fusion coupling".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::PhononInjection,
                penetration_depth_um: 1000.0, // Acoustic waves propagate
                deposition_profile_um: 500.0,
                phonon_efficiency: 1.0, // Direct phonon generation
                screening_factor: 5.0, // Lower than ionizing radiation
                conversion_efficiency: 1e-10, // Low but compensated by rate
            },
        });

        // === Pulsed Electrolysis ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::PulsedElectrolysis,
            name: "Pulsed Electrolysis Loading".to_string(),
            description: "Refined Fleischmann-Pons approach: Pulsed electrolysis in D2O \
                         creates dynamic deuterium loading/unloading cycles in Pd cathode. \
                         Pulsing creates transient high-loading states with enhanced screening.".to_string(),
            trl: TRL::system_demo(),
            cost: CostCategory::Maker,
            cost_estimate_usd: 2_000.0,
            max_rep_rate_hz: 100.0, // Limited by electrochemistry
            energy_per_trigger_j: 0.1, // 100 mJ electrical
            wall_plug_efficiency: 0.01, // Most goes to electrolysis
            footprint_m3: 0.01, // Benchtop
            advantages: vec![
                "Simplest possible setup".to_string(),
                "Self-loading of deuterium".to_string(),
                "Proven to produce excess heat (disputed)".to_string(),
                "No exotic materials".to_string(),
            ],
            challenges: vec![
                "Controversial physics".to_string(),
                "Poor reproducibility historically".to_string(),
                "Slow trigger rate".to_string(),
                "Material degradation".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::Electrochemical,
                penetration_depth_um: 100.0, // D loading depth
                deposition_profile_um: 50.0,
                phonon_efficiency: 0.1, // Indirect
                screening_factor: 10.0, // Loading-dependent
                conversion_efficiency: 1e-9,
            },
        });

        // === Ultrasonic Cavitation ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::Ultrasonic,
            name: "Ultrasonic Cavitation".to_string(),
            description: "High-power ultrasound in deuterated liquid (D2O or organic) creates \
                         collapsing cavitation bubbles with extreme transient temperatures and \
                         pressures. Sonofusion-inspired but with solid target immersed.".to_string(),
            trl: TRL::lab_validation(),
            cost: CostCategory::LabScale,
            cost_estimate_usd: 20_000.0,
            max_rep_rate_hz: 100_000.0, // Acoustic frequency
            energy_per_trigger_j: 1e-6, // Per bubble collapse
            wall_plug_efficiency: 0.1,
            footprint_m3: 0.1,
            advantages: vec![
                "Creates extreme local conditions".to_string(),
                "Self-focusing energy".to_string(),
                "Continuous operation possible".to_string(),
                "No vacuum needed".to_string(),
            ],
            challenges: vec![
                "Sonofusion claims disputed".to_string(),
                "Difficult to control/measure".to_string(),
                "Erosion of target".to_string(),
                "Complex fluid dynamics".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::PhononInjection,
                penetration_depth_um: 10.0, // Bubble collapse is localized
                deposition_profile_um: 5.0,
                phonon_efficiency: 0.3,
                screening_factor: 15.0, // High-pressure screening
                conversion_efficiency: 1e-9,
            },
        });

        // === Glow Discharge ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::GlowDischarge,
            name: "Glow Discharge Plasma".to_string(),
            description: "Low-pressure D2 gas plasma with Pd cathode. Energetic D+ ions \
                         (100 eV - 1 keV) implant into cathode while cathode heating drives \
                         loading. Combines ion implantation with thermal effects.".to_string(),
            trl: TRL::prototype_demo(),
            cost: CostCategory::LabScale,
            cost_estimate_usd: 15_000.0,
            max_rep_rate_hz: 1000.0, // Pulsed discharge
            energy_per_trigger_j: 0.01,
            wall_plug_efficiency: 0.05,
            footprint_m3: 0.1,
            advantages: vec![
                "Ion implantation + loading".to_string(),
                "Creates defects (D trapping sites)".to_string(),
                "Continuous or pulsed operation".to_string(),
                "Observable excess heat reports".to_string(),
            ],
            challenges: vec![
                "Cathode sputtering".to_string(),
                "Plasma instabilities".to_string(),
                "Contamination issues".to_string(),
                "Limited ion energy".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::NuclearStopping,
                penetration_depth_um: 0.1, // Shallow implantation
                deposition_profile_um: 0.05,
                phonon_efficiency: 0.4,
                screening_factor: 25.0, // Ion channeling effects
                conversion_efficiency: 1e-8,
            },
        });

        // === Muon Catalysis (exotic) ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::MuonCatalysis,
            name: "Muon-Catalyzed Fusion Hybrid".to_string(),
            description: "Muons replace electrons in D-D molecules, reducing internuclear \
                         distance by factor of 207. Enables fusion at room temperature. \
                         Limited by muon sticking and production cost.".to_string(),
            trl: TRL::lab_validation(),
            cost: CostCategory::MajorFacility,
            cost_estimate_usd: 10_000_000.0,
            max_rep_rate_hz: 1.0, // Muon lifetime limited
            energy_per_trigger_j: 17.6e6 * 1.6e-19, // D-T fusion energy
            wall_plug_efficiency: 1e-6, // Muon production expensive
            footprint_m3: 100.0, // Accelerator + target
            advantages: vec![
                "Proven fusion mechanism".to_string(),
                "Room temperature operation".to_string(),
                "~150 fusions per muon".to_string(),
                "Well-understood physics".to_string(),
            ],
            challenges: vec![
                "Muon production requires accelerator".to_string(),
                "Alpha sticking limits yield".to_string(),
                "Energy breakeven difficult".to_string(),
                "Short muon lifetime (2.2 μs)".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::NuclearRecoil,
                penetration_depth_um: 1000.0, // Muons penetrate deeply
                deposition_profile_um: 500.0,
                phonon_efficiency: 0.1, // Not phonon-mediated
                screening_factor: 207.0, // Mass ratio screening
                conversion_efficiency: 1.0, // Near-certain fusion per capture
            },
        });

        // === Compact X-ray Tube ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::CompactXRay,
            name: "Compact X-ray Tube".to_string(),
            description: "Standard medical/industrial X-ray tube (30-150 kVp) producing \
                         Bremsstrahlung + characteristic X-rays. Not coherent or ultrafast \
                         but readily available and well-understood.".to_string(),
            trl: TRL::proven(),
            cost: CostCategory::LabScale,
            cost_estimate_usd: 30_000.0,
            max_rep_rate_hz: 1000.0, // Pulsed tubes
            energy_per_trigger_j: 0.1, // Integrated pulse energy
            wall_plug_efficiency: 0.01, // X-ray generation efficiency
            footprint_m3: 0.1,
            advantages: vec![
                "Proven, available technology".to_string(),
                "No R&D needed".to_string(),
                "Regulatory framework exists".to_string(),
                "Serviceable parts".to_string(),
            ],
            challenges: vec![
                "Not coherent".to_string(),
                "Broad spectrum".to_string(),
                "Limited peak intensity".to_string(),
                "Shielding required".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::Photoelectric,
                penetration_depth_um: 100.0, // Depending on spectrum
                deposition_profile_um: 50.0,
                phonon_efficiency: 0.2,
                screening_factor: 15.0,
                conversion_efficiency: 1e-9,
            },
        });

        // === Thermal Cycling ===
        systems.push(TriggerSystemSpec {
            method: ExtendedTriggerMethod::ThermalCycling,
            name: "Rapid Thermal Cycling".to_string(),
            description: "Cyclic heating/cooling of deuterated metal creates expansion/ \
                         contraction that modulates D-D spacing and generates thermal phonons. \
                         Simplest possible trigger but low energy density.".to_string(),
            trl: TRL::system_demo(),
            cost: CostCategory::Maker,
            cost_estimate_usd: 1_000.0,
            max_rep_rate_hz: 10.0, // Thermal mass limited
            energy_per_trigger_j: 1.0, // Heating energy
            wall_plug_efficiency: 0.9, // Resistive heating efficient
            footprint_m3: 0.01,
            advantages: vec![
                "Absolute simplest trigger".to_string(),
                "No special equipment".to_string(),
                "Easy to control".to_string(),
                "Inherent temperature monitoring".to_string(),
            ],
            challenges: vec![
                "Slow cycle time".to_string(),
                "Thermal stress on materials".to_string(),
                "Low peak excitation".to_string(),
                "Deuterium desorption at high T".to_string(),
            ],
            physics: TriggerPhysics {
                mechanism: EnergyDepositionMechanism::Thermal,
                penetration_depth_um: 10000.0, // Bulk heating
                deposition_profile_um: 5000.0,
                phonon_efficiency: 0.9, // Thermal = phonons
                screening_factor: 2.0, // Minimal enhancement
                conversion_efficiency: 1e-12,
            },
        });

        Self { systems }
    }

    /// Find systems meeting specific criteria
    pub fn filter(&self, criteria: &TriggerCriteria) -> Vec<&TriggerSystemSpec> {
        self.systems.iter().filter(|sys| {
            // TRL filter
            if let Some(min_trl) = criteria.min_trl {
                if sys.trl.0 < min_trl { return false; }
            }

            // Cost filter
            if let Some(max_cost) = criteria.max_cost_usd {
                if sys.cost_estimate_usd > max_cost { return false; }
            }

            // Rep rate filter
            if let Some(min_rate) = criteria.min_rep_rate_hz {
                if sys.max_rep_rate_hz < min_rate { return false; }
            }

            // Footprint filter
            if let Some(max_footprint) = criteria.max_footprint_m3 {
                if sys.footprint_m3 > max_footprint { return false; }
            }

            true
        }).collect()
    }

    /// Rank systems by a weighted score
    pub fn rank(&self, weights: &TriggerWeights) -> Vec<(&TriggerSystemSpec, f64)> {
        let mut scored: Vec<_> = self.systems.iter().map(|sys| {
            let score = self.compute_score(sys, weights);
            (sys, score)
        }).collect();

        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        scored
    }

    /// Compute weighted score for a system
    fn compute_score(&self, sys: &TriggerSystemSpec, weights: &TriggerWeights) -> f64 {
        // Normalize each factor to 0-1 scale

        // TRL: higher is better
        let trl_score = sys.trl.0 as f64 / 9.0;

        // Cost: lower is better (log scale)
        let cost_score = 1.0 - (sys.cost_estimate_usd.ln() / 25.0).clamp(0.0, 1.0);

        // Rep rate: higher is better (log scale)
        let rate_score = (sys.max_rep_rate_hz.ln() / 25.0).clamp(0.0, 1.0);

        // Efficiency: higher is better
        let efficiency_score = (sys.wall_plug_efficiency.ln() + 10.0) / 10.0;

        // Footprint: smaller is better (log scale)
        let footprint_score = 1.0 - (sys.footprint_m3.ln() + 5.0) / 20.0;

        // Conversion efficiency: higher is better (log scale)
        let conversion_score = (sys.physics.conversion_efficiency.log10() + 12.0) / 12.0;

        // Phonon efficiency: higher is better for LCF
        let phonon_score = sys.physics.phonon_efficiency as f64;

        // Weighted sum
        weights.trl * trl_score
            + weights.cost * cost_score
            + weights.rep_rate * rate_score
            + weights.efficiency * efficiency_score
            + weights.footprint * footprint_score
            + weights.conversion * conversion_score
            + weights.phonon * phonon_score
    }

    /// Get optimal trigger for specific power scale
    pub fn optimal_for_power(&self, target_power_w: f64) -> &TriggerSystemSpec {
        // Different triggers optimal at different scales
        if target_power_w < 100.0 {
            // Sub-100W: piezo or thermal cycling
            self.systems.iter()
                .find(|s| s.method == ExtendedTriggerMethod::PiezoPhonon)
                .unwrap_or(&self.systems[0])
        } else if target_power_w < 10_000.0 {
            // 100W - 10kW: electron beam or glow discharge
            self.systems.iter()
                .find(|s| s.method == ExtendedTriggerMethod::ElectronBeam)
                .unwrap_or(&self.systems[0])
        } else if target_power_w < 1_000_000.0 {
            // 10kW - 1MW: laser bremsstrahlung or compact X-ray
            self.systems.iter()
                .find(|s| s.method == ExtendedTriggerMethod::LaserBremsstrahlung)
                .unwrap_or(&self.systems[0])
        } else {
            // >1MW: NEEC or muon catalysis for theoretical high gain
            self.systems.iter()
                .find(|s| s.method == ExtendedTriggerMethod::NeecCascade)
                .unwrap_or(&self.systems[0])
        }
    }
}

impl Default for TriggerSystemLibrary {
    fn default() -> Self {
        Self::new()
    }
}

/// Criteria for filtering trigger systems
#[derive(Debug, Clone, Default)]
pub struct TriggerCriteria {
    pub min_trl: Option<u8>,
    pub max_cost_usd: Option<f64>,
    pub min_rep_rate_hz: Option<f64>,
    pub max_footprint_m3: Option<f64>,
}

/// Weights for ranking trigger systems
#[derive(Debug, Clone)]
pub struct TriggerWeights {
    pub trl: f64,
    pub cost: f64,
    pub rep_rate: f64,
    pub efficiency: f64,
    pub footprint: f64,
    pub conversion: f64,
    pub phonon: f64,
}

impl Default for TriggerWeights {
    fn default() -> Self {
        Self {
            trl: 1.0,
            cost: 1.5,      // Cost is important
            rep_rate: 0.8,
            efficiency: 1.0,
            footprint: 1.2, // Compactness important
            conversion: 1.5, // Conversion critical
            phonon: 1.0,
        }
    }
}

impl TriggerWeights {
    /// Weights optimized for desktop/maker scale
    pub fn desktop() -> Self {
        Self {
            trl: 1.5,       // Want proven tech
            cost: 2.0,      // Cost critical
            rep_rate: 0.5,
            efficiency: 0.8,
            footprint: 2.0, // Must be small
            conversion: 1.0,
            phonon: 1.2,
        }
    }

    /// Weights for research/prototype
    pub fn research() -> Self {
        Self {
            trl: 0.5,       // OK with less proven
            cost: 0.8,
            rep_rate: 1.0,
            efficiency: 1.0,
            footprint: 0.5,
            conversion: 2.0, // Want best performance
            phonon: 1.5,
        }
    }

    /// Weights for industrial/power generation
    pub fn industrial() -> Self {
        Self {
            trl: 2.0,       // Must be reliable
            cost: 1.0,
            rep_rate: 1.5,  // Throughput matters
            efficiency: 2.0, // Efficiency critical at scale
            footprint: 0.3,
            conversion: 1.5,
            phonon: 0.8,
        }
    }
}

/// Estimate fusion yield for a trigger system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FusionYieldEstimate {
    /// Trigger system used
    pub trigger: ExtendedTriggerMethod,
    /// Reactions per second estimate
    pub reactions_per_second: f64,
    /// Thermal power output (W)
    pub thermal_power_w: f64,
    /// Q factor (fusion power / input power)
    pub q_factor: f64,
    /// Confidence level (0-1)
    pub confidence: f64,
    /// Notes on calculation
    pub notes: String,
}

/// Estimate fusion yield from a trigger system
pub fn estimate_fusion_yield(
    sys: &TriggerSystemSpec,
    target_mass_g: f64,
    d_loading_ratio: f64,  // D/Pd ratio
) -> FusionYieldEstimate {
    // Number of D atoms in target
    // Assume Pd: 106.4 g/mol, so moles = mass / 106.4
    let pd_moles = target_mass_g / 106.4;
    let d_atoms = pd_moles * d_loading_ratio * 6.022e23;

    // D-D pairs that could fuse (rough estimate)
    let d_pairs = d_atoms * d_loading_ratio / 2.0;

    // Trigger volume fraction
    let trigger_volume = PI * (sys.physics.penetration_depth_um * 1e-4).powi(2)
                        * sys.physics.deposition_profile_um * 1e-4; // cm³
    let target_volume = target_mass_g / 12.0; // Pd density ~12 g/cm³
    let volume_fraction = (trigger_volume / target_volume).min(1.0);

    // Affected D pairs per trigger
    let affected_pairs = d_pairs * volume_fraction;

    // Fusion probability per affected pair per trigger
    // Base rate from conversion efficiency, enhanced by screening
    let base_prob = sys.physics.conversion_efficiency;
    let screening_enhancement = sys.physics.screening_factor;
    let phonon_factor = 1.0 + sys.physics.phonon_efficiency as f64 * 10.0;

    let fusion_prob = base_prob * screening_enhancement * phonon_factor;

    // Fusions per trigger
    let fusions_per_trigger = affected_pairs * fusion_prob;

    // Fusions per second (at max rep rate)
    let fusions_per_second = fusions_per_trigger * sys.max_rep_rate_hz;

    // Energy per D-D fusion: ~3.65 MeV average (D-D has two branches)
    let mev_per_fusion = 3.65;
    let j_per_fusion = mev_per_fusion * 1.6e-13;

    let thermal_power_w = fusions_per_second * j_per_fusion;

    // Input power estimate
    let input_power_w = sys.energy_per_trigger_j * sys.max_rep_rate_hz
                       / sys.wall_plug_efficiency;

    let q_factor = if input_power_w > 0.0 {
        thermal_power_w / input_power_w
    } else {
        0.0
    };

    // Confidence based on TRL and mechanism understanding
    let confidence = match sys.method {
        ExtendedTriggerMethod::MuonCatalysis => 0.9, // Well-understood
        ExtendedTriggerMethod::XfelXRay => 0.7,
        ExtendedTriggerMethod::ElectronBeam => 0.5,
        ExtendedTriggerMethod::PulsedElectrolysis => 0.3,
        ExtendedTriggerMethod::NeecCascade => 0.2,
        _ => 0.4,
    };

    FusionYieldEstimate {
        trigger: sys.method,
        reactions_per_second: fusions_per_second,
        thermal_power_w,
        q_factor,
        confidence,
        notes: format!(
            "Estimated for {:.1}g Pd at D/Pd={:.2}. \
             Affected volume: {:.2e} cm³, pairs: {:.2e}, prob/pair: {:.2e}",
            target_mass_g, d_loading_ratio, trigger_volume, affected_pairs, fusion_prob
        ),
    }
}

/// Compare all trigger systems for a given configuration
pub fn compare_triggers(target_mass_g: f64, d_loading: f64) -> Vec<FusionYieldEstimate> {
    let library = TriggerSystemLibrary::new();
    let mut estimates: Vec<_> = library.systems.iter()
        .map(|sys| estimate_fusion_yield(sys, target_mass_g, d_loading))
        .collect();

    estimates.sort_by(|a, b| {
        b.q_factor.partial_cmp(&a.q_factor).unwrap_or(std::cmp::Ordering::Equal)
    });

    estimates
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_library_creation() {
        let lib = TriggerSystemLibrary::new();
        assert!(lib.systems.len() >= 10, "Should have multiple trigger systems");
    }

    #[test]
    fn test_filter_by_cost() {
        let lib = TriggerSystemLibrary::new();
        let cheap = lib.filter(&TriggerCriteria {
            max_cost_usd: Some(50_000.0),
            ..Default::default()
        });

        assert!(!cheap.is_empty(), "Should find cheap triggers");
        for sys in cheap {
            assert!(sys.cost_estimate_usd <= 50_000.0);
        }
    }

    #[test]
    fn test_filter_by_trl() {
        let lib = TriggerSystemLibrary::new();
        let proven = lib.filter(&TriggerCriteria {
            min_trl: Some(7),
            ..Default::default()
        });

        assert!(!proven.is_empty(), "Should find proven triggers");
        for sys in proven {
            assert!(sys.trl.0 >= 7);
        }
    }

    #[test]
    fn test_ranking() {
        let lib = TriggerSystemLibrary::new();
        let ranked = lib.rank(&TriggerWeights::desktop());

        // Desktop ranking should favor cheap, compact options
        let top = &ranked[0].0;
        assert!(
            top.cost_estimate_usd < 100_000.0,
            "Desktop top pick should be affordable"
        );
    }

    #[test]
    fn test_fusion_yield_estimate() {
        let lib = TriggerSystemLibrary::new();
        let ebeam = lib.systems.iter()
            .find(|s| s.method == ExtendedTriggerMethod::ElectronBeam)
            .unwrap();

        let estimate = estimate_fusion_yield(ebeam, 10.0, 0.7);

        assert!(estimate.reactions_per_second >= 0.0);
        assert!(estimate.thermal_power_w >= 0.0);
        assert!(estimate.confidence > 0.0 && estimate.confidence <= 1.0);
    }

    #[test]
    fn test_optimal_for_power_scale() {
        let lib = TriggerSystemLibrary::new();

        let low_power = lib.optimal_for_power(10.0);
        let mid_power = lib.optimal_for_power(5_000.0);
        let high_power = lib.optimal_for_power(100_000.0);

        // Should return different systems at different scales
        assert_eq!(low_power.method, ExtendedTriggerMethod::PiezoPhonon);
        assert_eq!(mid_power.method, ExtendedTriggerMethod::ElectronBeam);
    }

    #[test]
    fn test_compare_all_triggers() {
        let estimates = compare_triggers(10.0, 0.7);
        assert!(!estimates.is_empty());

        // Should be sorted by Q factor
        for i in 1..estimates.len() {
            assert!(estimates[i-1].q_factor >= estimates[i].q_factor);
        }
    }
}
