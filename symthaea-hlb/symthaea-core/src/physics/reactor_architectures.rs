//! # Alternative Reactor Architectures for LCF
//!
//! The original Spark Engine uses a solid-state 3-layer design with HEA shell.
//! This module explores alternative architectures that sidestep key challenges:
//!
//! ## Challenges Addressed
//!
//! | Challenge                    | Original Design   | Alternative Solutions          |
//! |------------------------------|-------------------|--------------------------------|
//! | 14.1 MeV neutron damage      | HEA "Wolverine"   | Aneutronic D-He3, flowing Pb   |
//! | Impractical X-ray trigger    | XFEL required     | E-beam, piezo, electrolysis    |
//! | Fuel loading complexity      | Pd deuteride      | Flowing D2 gas, liquid target  |
//! | Thermal management           | Passive/Galinstan | Active liquid metal cooling    |
//! | Scaling across power levels  | Different designs | Modular cell architecture      |
//!
//! ## Architecture Overview
//!
//! ```text
//! ARCHITECTURE          TRIGGER         FUEL           NEUTRONS      SCALING
//! ─────────────────────────────────────────────────────────────────────────────
//! Spark v1 (original)   X-ray          Pd deuteride   D-D/D-T       Fixed size
//! FlowReactor           E-beam         Flowing Pd     D-D           Linear
//! AneutronicCore        Piezo/Laser    He3 + D2 gas   ~None         Modular
//! PulsedElectrolysis    Electrolysis   D2O + Pd       D-D           Simple
//! MoltenSalt            Thermal        Molten FLiBe   D-T           Large
//! ModularCell           Any            Configurable   Any           Arbitrary
//! ```

use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

use super::trigger_systems::{
    ExtendedTriggerMethod, TriggerSystemSpec, TriggerSystemLibrary,
    estimate_fusion_yield, FusionYieldEstimate,
};
use super::radiation_damage::FusionReaction;

/// Reactor architecture type
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ReactorArchitecture {
    /// Original Spark Engine (solid HEA shell, Galinstan core)
    SparkV1,
    /// Flowing liquid metal target (self-renewing)
    FlowReactor,
    /// Aneutronic D-He3 (minimal neutron damage)
    AneutronicCore,
    /// Pulsed electrolysis (simplest setup)
    PulsedElectrolysis,
    /// Molten salt (FLiBe-based, for D-T)
    MoltenSalt,
    /// Modular cell architecture (scalable)
    ModularCell,
    /// Magnetized target fusion hybrid
    MagnetizedTarget,
}

/// Fuel system specification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuelSystem {
    /// Primary fuel (D, T, He3)
    pub primary_fuel: FuelType,
    /// Secondary fuel (if hybrid)
    pub secondary_fuel: Option<FuelType>,
    /// Fuel state (gas, liquid, solid, plasma)
    pub state: FuelState,
    /// Host material (for solid-state)
    pub host_material: Option<String>,
    /// Operating pressure (atm)
    pub pressure_atm: f64,
    /// Operating temperature (K)
    pub temperature_k: f64,
    /// Fuel flow rate (if flowing, g/s)
    pub flow_rate_g_s: Option<f64>,
    /// Fuel loading ratio (D/Metal for deuterides)
    pub loading_ratio: Option<f64>,
}

/// Fuel types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum FuelType {
    Deuterium,
    Tritium,
    Helium3,
    Protium,
    DeuteriumTritium,  // 50-50 mix
}

impl FuelType {
    pub fn atomic_mass(&self) -> f64 {
        match self {
            FuelType::Protium => 1.008,
            FuelType::Deuterium => 2.014,
            FuelType::Tritium => 3.016,
            FuelType::Helium3 => 3.016,
            FuelType::DeuteriumTritium => 2.515, // Average
        }
    }

    pub fn cost_per_gram_usd(&self) -> f64 {
        match self {
            FuelType::Protium => 0.0001,     // Essentially free
            FuelType::Deuterium => 0.01,     // $10/kg from seawater
            FuelType::Tritium => 30_000.0,   // $30,000/g (breeder required)
            FuelType::Helium3 => 1_000_000.0, // $1M/g (lunar mining needed)
            FuelType::DeuteriumTritium => 15_000.0, // Average
        }
    }

    pub fn availability(&self) -> &'static str {
        match self {
            FuelType::Protium => "Unlimited (water)",
            FuelType::Deuterium => "Unlimited (seawater 0.015%)",
            FuelType::Tritium => "Scarce (breed from Li)",
            FuelType::Helium3 => "Extremely rare (lunar regolith)",
            FuelType::DeuteriumTritium => "Limited by tritium",
        }
    }
}

/// Fuel physical state
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum FuelState {
    Gas,
    Liquid,
    Solid,
    Plasma,
    Dissolved,  // In liquid metal or molten salt
}

/// Cooling system specification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoolingSystem {
    /// Cooling method
    pub method: CoolingMethod,
    /// Coolant material
    pub coolant: String,
    /// Coolant inlet temperature (K)
    pub inlet_temp_k: f64,
    /// Coolant outlet temperature (K)
    pub outlet_temp_k: f64,
    /// Flow rate (kg/s)
    pub flow_rate_kg_s: f64,
    /// Heat transfer coefficient (W/m²·K)
    pub htc: f64,
}

/// Cooling methods
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CoolingMethod {
    Passive,        // Natural convection
    ForcedAir,      // Fan cooling
    WaterLoop,      // Water jacket
    LiquidMetal,    // NaK, PbLi, Galinstan
    HeatPipe,       // Passive high-flux
    MoltenSalt,     // FLiBe, FLiNaK
    DirectConversion, // MHD or thermionic (for charged particles)
}

/// Shielding system specification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShieldingSystem {
    /// Primary shielding material
    pub primary_material: String,
    /// Primary thickness (m)
    pub primary_thickness_m: f64,
    /// Secondary shielding (if layered)
    pub secondary_material: Option<String>,
    /// Secondary thickness (m)
    pub secondary_thickness_m: Option<f64>,
    /// Total mass (kg)
    pub total_mass_kg: f64,
    /// Attenuation factor
    pub attenuation_factor: f64,
}

/// Complete reactor architecture specification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReactorSpec {
    /// Architecture name
    pub name: String,
    /// Architecture type
    pub architecture: ReactorArchitecture,
    /// Fusion reaction(s)
    pub reactions: Vec<FusionReaction>,
    /// Trigger system
    pub trigger: TriggerSystemSpec,
    /// Fuel system
    pub fuel: FuelSystem,
    /// Cooling system
    pub cooling: CoolingSystem,
    /// Shielding system
    pub shielding: ShieldingSystem,
    /// Target power output (W)
    pub power_w: f64,
    /// Overall dimensions (m³)
    pub volume_m3: f64,
    /// Total system mass (kg)
    pub mass_kg: f64,
    /// Estimated cost (USD)
    pub cost_usd: f64,
    /// Expected lifetime (years)
    pub lifetime_years: f64,
    /// Technology readiness level
    pub trl: u8,
    /// Key advantages
    pub advantages: Vec<String>,
    /// Key challenges
    pub challenges: Vec<String>,
    /// Estimated fusion yield
    pub yield_estimate: FusionYieldEstimate,
}

/// Reactor design parameters
#[derive(Debug, Clone)]
pub struct ReactorDesignParams {
    /// Target power output (W)
    pub target_power_w: f64,
    /// Target lifetime (years)
    pub target_lifetime_years: f64,
    /// Maximum cost (USD)
    pub max_cost_usd: f64,
    /// Maximum volume (m³)
    pub max_volume_m3: f64,
    /// Maximum mass (kg)
    pub max_mass_kg: f64,
    /// Acceptable neutron reactions
    pub allow_neutrons: bool,
    /// TRL requirement
    pub min_trl: u8,
}

impl Default for ReactorDesignParams {
    fn default() -> Self {
        Self {
            target_power_w: 10_000.0,  // 10 kW
            target_lifetime_years: 20.0,
            max_cost_usd: 100_000.0,
            max_volume_m3: 1.0,
            max_mass_kg: 1000.0,
            allow_neutrons: true,
            min_trl: 4,
        }
    }
}

impl ReactorDesignParams {
    /// Consumer household unit
    pub fn consumer() -> Self {
        Self {
            target_power_w: 5_000.0,
            target_lifetime_years: 25.0,
            max_cost_usd: 50_000.0,
            max_volume_m3: 0.5,
            max_mass_kg: 500.0,
            allow_neutrons: false,  // Consumer wants aneutronic
            min_trl: 6,
        }
    }

    /// Research prototype
    pub fn prototype() -> Self {
        Self {
            target_power_w: 100.0,
            target_lifetime_years: 1.0,
            max_cost_usd: 500_000.0,
            max_volume_m3: 10.0,
            max_mass_kg: 5000.0,
            allow_neutrons: true,
            min_trl: 3,
        }
    }

    /// Industrial power plant
    pub fn industrial() -> Self {
        Self {
            target_power_w: 100_000_000.0,  // 100 MW
            target_lifetime_years: 40.0,
            max_cost_usd: 1_000_000_000.0,
            max_volume_m3: 10_000.0,
            max_mass_kg: 10_000_000.0,
            allow_neutrons: true,
            min_trl: 5,
        }
    }
}

/// Reactor architecture designer
pub struct ReactorDesigner {
    trigger_library: TriggerSystemLibrary,
}

impl ReactorDesigner {
    pub fn new() -> Self {
        Self {
            trigger_library: TriggerSystemLibrary::new(),
        }
    }

    /// Design optimal reactor for given parameters
    pub fn design(&self, params: &ReactorDesignParams) -> ReactorSpec {
        // Select architecture based on constraints
        let architecture = self.select_architecture(params);

        // Design the reactor
        match architecture {
            ReactorArchitecture::SparkV1 => self.design_spark_v1(params),
            ReactorArchitecture::FlowReactor => self.design_flow_reactor(params),
            ReactorArchitecture::AneutronicCore => self.design_aneutronic(params),
            ReactorArchitecture::PulsedElectrolysis => self.design_electrolysis(params),
            ReactorArchitecture::MoltenSalt => self.design_molten_salt(params),
            ReactorArchitecture::ModularCell => self.design_modular(params),
            ReactorArchitecture::MagnetizedTarget => self.design_magnetized(params),
        }
    }

    /// Select best architecture for given constraints
    fn select_architecture(&self, params: &ReactorDesignParams) -> ReactorArchitecture {
        // Decision tree for architecture selection
        if !params.allow_neutrons {
            // Aneutronic required
            return ReactorArchitecture::AneutronicCore;
        }

        if params.target_power_w < 1000.0 {
            // Very small: electrolysis or modular
            if params.max_cost_usd < 10_000.0 {
                return ReactorArchitecture::PulsedElectrolysis;
            } else {
                return ReactorArchitecture::ModularCell;
            }
        }

        if params.target_power_w > 10_000_000.0 {
            // Large scale: molten salt for high power
            return ReactorArchitecture::MoltenSalt;
        }

        if params.target_lifetime_years > 30.0 {
            // Long lifetime: flow reactor for self-renewal
            return ReactorArchitecture::FlowReactor;
        }

        // Default to original Spark design
        ReactorArchitecture::SparkV1
    }

    /// Design original Spark v1 architecture
    fn design_spark_v1(&self, params: &ReactorDesignParams) -> ReactorSpec {
        let reaction = if params.target_power_w > 100_000.0 {
            FusionReaction::DT
        } else {
            FusionReaction::DD
        };

        // Select trigger for power scale
        let trigger = self.trigger_library.optimal_for_power(params.target_power_w).clone();

        // Calculate dimensions
        let power_density = 50_000.0; // W/m³ for solid-state
        let core_volume = params.target_power_w / power_density;
        let core_radius = (3.0 * core_volume / (4.0 * PI)).powf(1.0/3.0);
        let shell_thickness = 0.01 + core_radius * 0.2;
        let total_radius = core_radius + shell_thickness + 0.05; // +5cm shielding

        let fuel = FuelSystem {
            primary_fuel: FuelType::Deuterium,
            secondary_fuel: if reaction == FusionReaction::DT {
                Some(FuelType::Tritium)
            } else {
                None
            },
            state: FuelState::Solid,
            host_material: Some("TiVZrNbPd HEA".to_string()),
            pressure_atm: 1.0,
            temperature_k: 350.0,
            flow_rate_g_s: None,
            loading_ratio: Some(0.7),
        };

        let cooling = CoolingSystem {
            method: if params.target_power_w > 100_000.0 {
                CoolingMethod::LiquidMetal
            } else {
                CoolingMethod::Passive
            },
            coolant: "Galinstan".to_string(),
            inlet_temp_k: 300.0,
            outlet_temp_k: 350.0,
            flow_rate_kg_s: params.target_power_w / 50_000.0,
            htc: 10_000.0,
        };

        let neutron_energy = reaction.neutron_energy_mev().unwrap_or(2.45);
        let shielding_thickness = if neutron_energy > 10.0 { 0.5 } else { 0.2 };

        let shielding = ShieldingSystem {
            primary_material: "Borated polyethylene".to_string(),
            primary_thickness_m: shielding_thickness,
            secondary_material: Some("Lead".to_string()),
            secondary_thickness_m: Some(0.02),
            total_mass_kg: 4.0 * PI * total_radius.powi(2) * shielding_thickness * 1000.0,
            attenuation_factor: (-shielding_thickness * 10.0).exp(),
        };

        let volume = 4.0/3.0 * PI * total_radius.powi(3);
        let mass = shielding.total_mass_kg + core_volume * 12000.0; // Pd density

        let yield_estimate = estimate_fusion_yield(&trigger, core_volume * 12000.0 * 1000.0, 0.7);

        ReactorSpec {
            name: format!("Spark v1 ({:.1}kW)", params.target_power_w / 1000.0),
            architecture: ReactorArchitecture::SparkV1,
            reactions: vec![reaction],
            trigger,
            fuel,
            cooling,
            shielding,
            power_w: params.target_power_w,
            volume_m3: volume,
            mass_kg: mass,
            cost_usd: 50_000.0 + params.target_power_w * 5.0,
            lifetime_years: 20.0,
            trl: 4,
            advantages: vec![
                "Compact solid-state design".to_string(),
                "Self-healing HEA shell".to_string(),
                "Proven materials".to_string(),
            ],
            challenges: vec![
                "Requires X-ray or e-beam trigger".to_string(),
                "Neutron damage accumulation".to_string(),
                "Limited fuel lifetime".to_string(),
            ],
            yield_estimate,
        }
    }

    /// Design flowing liquid metal reactor
    fn design_flow_reactor(&self, params: &ReactorDesignParams) -> ReactorSpec {
        // Flowing Pb-Li eutectic with dissolved deuterium
        let trigger = self.trigger_library.systems.iter()
            .find(|s| s.method == ExtendedTriggerMethod::ElectronBeam)
            .unwrap()
            .clone();

        let core_volume = params.target_power_w / 30_000.0; // Lower power density for flowing
        let pipe_diameter = 0.1; // 10cm pipe
        let pipe_length = core_volume / (PI * (pipe_diameter / 2.0_f64).powi(2));

        let fuel = FuelSystem {
            primary_fuel: FuelType::Deuterium,
            secondary_fuel: None,
            state: FuelState::Dissolved,
            host_material: Some("Pb-17Li eutectic".to_string()),
            pressure_atm: 5.0,
            temperature_k: 600.0,
            flow_rate_g_s: Some(params.target_power_w / 10.0), // ~100g/s per kW
            loading_ratio: Some(0.001), // Much lower in liquid
        };

        let cooling = CoolingSystem {
            method: CoolingMethod::LiquidMetal,
            coolant: "Pb-17Li (self-cooling)".to_string(),
            inlet_temp_k: 550.0,
            outlet_temp_k: 650.0,
            flow_rate_kg_s: fuel.flow_rate_g_s.unwrap_or(100.0) / 1000.0,
            htc: 50_000.0,
        };

        let shielding = ShieldingSystem {
            primary_material: "Pb-17Li self-shielding + steel".to_string(),
            primary_thickness_m: 0.3,
            secondary_material: None,
            secondary_thickness_m: None,
            total_mass_kg: 500.0 + params.target_power_w * 0.1,
            attenuation_factor: 1e-4,
        };

        let volume = pipe_length * PI * 0.5_f64.powi(2) + 1.0; // Pipe + equipment
        let mass = 1000.0 + params.target_power_w * 0.5;

        let yield_estimate = estimate_fusion_yield(&trigger, mass * 0.1, 0.001);

        ReactorSpec {
            name: format!("FlowReactor ({:.1}kW)", params.target_power_w / 1000.0),
            architecture: ReactorArchitecture::FlowReactor,
            reactions: vec![FusionReaction::DD],
            trigger,
            fuel,
            cooling,
            shielding,
            power_w: params.target_power_w,
            volume_m3: volume,
            mass_kg: mass,
            cost_usd: 200_000.0 + params.target_power_w * 10.0,
            lifetime_years: 50.0, // Very long - flowing target is self-renewing
            trl: 3,
            advantages: vec![
                "Self-renewing target (indefinite lifetime)".to_string(),
                "Pb-Li provides self-shielding".to_string(),
                "Can breed tritium from Li".to_string(),
                "Continuous fuel processing possible".to_string(),
            ],
            challenges: vec![
                "Complex plumbing system".to_string(),
                "Pb-Li handling at 600K".to_string(),
                "Lower D concentration than solid".to_string(),
                "Corrosion management".to_string(),
            ],
            yield_estimate,
        }
    }

    /// Design aneutronic D-He3 reactor
    fn design_aneutronic(&self, params: &ReactorDesignParams) -> ReactorSpec {
        // Aneutronic requires higher temperatures/energies
        // Use piezo phonon + laser for multi-mode trigger
        let trigger = self.trigger_library.systems.iter()
            .find(|s| s.method == ExtendedTriggerMethod::LaserBremsstrahlung)
            .unwrap()
            .clone();

        let fuel = FuelSystem {
            primary_fuel: FuelType::Deuterium,
            secondary_fuel: Some(FuelType::Helium3),
            state: FuelState::Gas,
            host_material: None,
            pressure_atm: 100.0, // High pressure gas target
            temperature_k: 1000.0, // Elevated temperature
            flow_rate_g_s: Some(0.01),
            loading_ratio: None,
        };

        // Direct conversion for charged particles (protons from D-He3)
        let cooling = CoolingSystem {
            method: CoolingMethod::DirectConversion,
            coolant: "MHD channel".to_string(),
            inlet_temp_k: 800.0,
            outlet_temp_k: 1200.0,
            flow_rate_kg_s: 0.0, // No coolant flow - direct conversion
            htc: 100_000.0, // High HTC for direct energy extraction
        };

        // Minimal shielding - aneutronic!
        let shielding = ShieldingSystem {
            primary_material: "Aluminum (structural only)".to_string(),
            primary_thickness_m: 0.01,
            secondary_material: None,
            secondary_thickness_m: None,
            total_mass_kg: 50.0,
            attenuation_factor: 1.0, // Not needed
        };

        let volume = 0.1 + params.target_power_w / 100_000.0;
        let mass = 100.0 + params.target_power_w * 0.01;

        // He3 cost dominates
        let he3_consumption_g_year = params.target_power_w * 3.15e7 / (18.3e6 * 1.6e-13 * 6.022e23);
        let fuel_cost_year = he3_consumption_g_year * FuelType::Helium3.cost_per_gram_usd();

        let yield_estimate = estimate_fusion_yield(&trigger, 10.0, 0.5);

        ReactorSpec {
            name: format!("AneutronicCore D-He3 ({:.1}kW)", params.target_power_w / 1000.0),
            architecture: ReactorArchitecture::AneutronicCore,
            reactions: vec![FusionReaction::DHe3],
            trigger,
            fuel,
            cooling,
            shielding,
            power_w: params.target_power_w,
            volume_m3: volume,
            mass_kg: mass,
            cost_usd: 500_000.0 + fuel_cost_year * 10.0, // Include 10yr fuel cost
            lifetime_years: 100.0, // No neutron damage
            trl: 2, // Very early stage
            advantages: vec![
                "No neutron damage to structure".to_string(),
                "Minimal shielding required".to_string(),
                "Direct energy conversion possible (>60% efficiency)".to_string(),
                "Safe for consumer deployment".to_string(),
                "Indefinite structural lifetime".to_string(),
            ],
            challenges: vec![
                "He3 extremely expensive ($1M/g)".to_string(),
                "Higher ignition temperature required".to_string(),
                "Lower cross-section than D-T".to_string(),
                "Side D-D reactions produce some neutrons".to_string(),
            ],
            yield_estimate,
        }
    }

    /// Design pulsed electrolysis reactor (simplest)
    fn design_electrolysis(&self, params: &ReactorDesignParams) -> ReactorSpec {
        let trigger = self.trigger_library.systems.iter()
            .find(|s| s.method == ExtendedTriggerMethod::PulsedElectrolysis)
            .unwrap()
            .clone();

        let fuel = FuelSystem {
            primary_fuel: FuelType::Deuterium,
            secondary_fuel: None,
            state: FuelState::Dissolved,
            host_material: Some("Pd cathode in D2O".to_string()),
            pressure_atm: 1.0,
            temperature_k: 350.0, // Slightly elevated
            flow_rate_g_s: None,
            loading_ratio: Some(0.9), // High loading via electrolysis
        };

        let cooling = CoolingSystem {
            method: CoolingMethod::WaterLoop,
            coolant: "D2O (electrolyte)".to_string(),
            inlet_temp_k: 300.0,
            outlet_temp_k: 350.0,
            flow_rate_kg_s: 0.1,
            htc: 5000.0,
        };

        let shielding = ShieldingSystem {
            primary_material: "Water + borated plastic".to_string(),
            primary_thickness_m: 0.2,
            secondary_material: None,
            secondary_thickness_m: None,
            total_mass_kg: 100.0,
            attenuation_factor: 0.1,
        };

        let yield_estimate = estimate_fusion_yield(&trigger, 100.0, 0.9);

        ReactorSpec {
            name: format!("PulsedElectrolysis ({:.0}W)", params.target_power_w),
            architecture: ReactorArchitecture::PulsedElectrolysis,
            reactions: vec![FusionReaction::DD],
            trigger,
            fuel,
            cooling,
            shielding,
            power_w: params.target_power_w,
            volume_m3: 0.05, // Very compact
            mass_kg: 50.0,
            cost_usd: 5_000.0, // Very cheap
            lifetime_years: 5.0, // Limited by cathode degradation
            trl: 5, // Some experimental validation
            advantages: vec![
                "Extremely simple setup".to_string(),
                "Very low cost (<$5K)".to_string(),
                "Self-loading fuel".to_string(),
                "Desktop scale".to_string(),
            ],
            challenges: vec![
                "Low power output (typically <100W)".to_string(),
                "Controversial physics (reproducibility issues)".to_string(),
                "Cathode degradation".to_string(),
                "Difficult to scale up".to_string(),
            ],
            yield_estimate,
        }
    }

    /// Design molten salt reactor (for large scale)
    fn design_molten_salt(&self, params: &ReactorDesignParams) -> ReactorSpec {
        let trigger = self.trigger_library.systems.iter()
            .find(|s| s.method == ExtendedTriggerMethod::CompactXRay)
            .unwrap()
            .clone();

        let fuel = FuelSystem {
            primary_fuel: FuelType::DeuteriumTritium,
            secondary_fuel: None,
            state: FuelState::Dissolved,
            host_material: Some("FLiBe molten salt".to_string()),
            pressure_atm: 1.0,
            temperature_k: 900.0, // High temp for molten salt
            flow_rate_g_s: Some(params.target_power_w / 100.0),
            loading_ratio: Some(0.01),
        };

        let cooling = CoolingSystem {
            method: CoolingMethod::MoltenSalt,
            coolant: "FLiBe".to_string(),
            inlet_temp_k: 800.0,
            outlet_temp_k: 1000.0,
            flow_rate_kg_s: params.target_power_w / 200_000.0,
            htc: 30_000.0,
        };

        // Need significant shielding for D-T
        let shielding = ShieldingSystem {
            primary_material: "FLiBe (Li breeds T) + steel".to_string(),
            primary_thickness_m: 1.0,
            secondary_material: Some("Concrete".to_string()),
            secondary_thickness_m: Some(2.0),
            total_mass_kg: 100_000.0 + params.target_power_w * 0.1,
            attenuation_factor: 1e-6,
        };

        let volume = params.target_power_w / 10_000.0; // 10 kW/m³
        let mass = 10_000.0 + params.target_power_w * 0.2;

        let yield_estimate = estimate_fusion_yield(&trigger, mass * 0.01, 0.01);

        ReactorSpec {
            name: format!("MoltenSalt ({:.0}MW)", params.target_power_w / 1_000_000.0),
            architecture: ReactorArchitecture::MoltenSalt,
            reactions: vec![FusionReaction::DT],
            trigger,
            fuel,
            cooling,
            shielding,
            power_w: params.target_power_w,
            volume_m3: volume,
            mass_kg: mass,
            cost_usd: 10_000_000.0 + params.target_power_w * 1.0,
            lifetime_years: 40.0,
            trl: 3,
            advantages: vec![
                "High power density".to_string(),
                "Self-healing liquid core".to_string(),
                "Tritium breeding from Li".to_string(),
                "High temperature operation".to_string(),
            ],
            challenges: vec![
                "14.1 MeV neutron damage to structure".to_string(),
                "Tritium handling complexity".to_string(),
                "High temperature materials".to_string(),
                "Regulatory complexity".to_string(),
            ],
            yield_estimate,
        }
    }

    /// Design modular cell architecture (scalable)
    fn design_modular(&self, params: &ReactorDesignParams) -> ReactorSpec {
        // Each cell produces ~100W
        let cell_power = 100.0;
        let num_cells = (params.target_power_w / cell_power).ceil() as usize;

        let trigger = self.trigger_library.systems.iter()
            .find(|s| s.method == ExtendedTriggerMethod::PiezoPhonon)
            .unwrap()
            .clone();

        let fuel = FuelSystem {
            primary_fuel: FuelType::Deuterium,
            secondary_fuel: None,
            state: FuelState::Solid,
            host_material: Some("Pd nano-powder".to_string()),
            pressure_atm: 10.0,
            temperature_k: 400.0,
            flow_rate_g_s: None,
            loading_ratio: Some(0.8),
        };

        let cooling = CoolingSystem {
            method: CoolingMethod::HeatPipe,
            coolant: "Na heat pipe".to_string(),
            inlet_temp_k: 350.0,
            outlet_temp_k: 400.0,
            flow_rate_kg_s: 0.0, // Passive heat pipe
            htc: 20_000.0,
        };

        // Shared shielding for cell array
        let shielding = ShieldingSystem {
            primary_material: "Borated water".to_string(),
            primary_thickness_m: 0.3,
            secondary_material: None,
            secondary_thickness_m: None,
            total_mass_kg: 200.0 + (num_cells as f64) * 5.0,
            attenuation_factor: 0.01,
        };

        // Each cell is ~10cm cube
        let cell_volume = 0.001; // 1 liter
        let volume = (num_cells as f64) * cell_volume * 2.0; // 2x for spacing

        let cell_mass = 0.5; // 500g per cell
        let mass = (num_cells as f64) * cell_mass + shielding.total_mass_kg;

        let cell_cost = 500.0; // $500 per cell at scale
        let cost = (num_cells as f64) * cell_cost + 10_000.0; // + base cost

        let yield_estimate = estimate_fusion_yield(&trigger, cell_mass * 500.0, 0.8);

        ReactorSpec {
            name: format!("ModularCell {}x ({:.1}kW)",
                         num_cells, params.target_power_w / 1000.0),
            architecture: ReactorArchitecture::ModularCell,
            reactions: vec![FusionReaction::DD],
            trigger,
            fuel,
            cooling,
            shielding,
            power_w: params.target_power_w,
            volume_m3: volume,
            mass_kg: mass,
            cost_usd: cost,
            lifetime_years: 15.0,
            trl: 4,
            advantages: vec![
                "Arbitrary scaling (1W to 1MW+)".to_string(),
                "Graceful degradation (cell failure)".to_string(),
                "Mass production potential".to_string(),
                "Easy replacement/maintenance".to_string(),
                "Fault tolerant design".to_string(),
            ],
            challenges: vec![
                "Cell synchronization".to_string(),
                "Heat pipe thermal limits".to_string(),
                "Individual cell reliability".to_string(),
                "Complex manufacturing".to_string(),
            ],
            yield_estimate,
        }
    }

    /// Design magnetized target fusion hybrid
    fn design_magnetized(&self, params: &ReactorDesignParams) -> ReactorSpec {
        // MTF uses magnetic compression of plasma target
        let trigger = self.trigger_library.systems.iter()
            .find(|s| s.method == ExtendedTriggerMethod::LaserBremsstrahlung)
            .unwrap()
            .clone();

        let fuel = FuelSystem {
            primary_fuel: FuelType::DeuteriumTritium,
            secondary_fuel: None,
            state: FuelState::Plasma,
            host_material: None,
            pressure_atm: 0.001, // Low pressure plasma
            temperature_k: 10_000_000.0, // 10 keV plasma
            flow_rate_g_s: Some(0.001),
            loading_ratio: None,
        };

        let cooling = CoolingSystem {
            method: CoolingMethod::LiquidMetal,
            coolant: "Pb-Li liner (also compressor)".to_string(),
            inlet_temp_k: 600.0,
            outlet_temp_k: 800.0,
            flow_rate_kg_s: params.target_power_w / 100_000.0,
            htc: 50_000.0,
        };

        let shielding = ShieldingSystem {
            primary_material: "Pb-Li blanket".to_string(),
            primary_thickness_m: 0.8,
            secondary_material: Some("Concrete".to_string()),
            secondary_thickness_m: Some(1.5),
            total_mass_kg: 5000.0 + params.target_power_w * 0.05,
            attenuation_factor: 1e-5,
        };

        let volume = 10.0 + params.target_power_w / 50_000.0;
        let mass = 5000.0 + params.target_power_w * 0.1;

        let yield_estimate = estimate_fusion_yield(&trigger, 10.0, 0.5);

        ReactorSpec {
            name: format!("MagnetizedTarget ({:.1}MW)", params.target_power_w / 1_000_000.0),
            architecture: ReactorArchitecture::MagnetizedTarget,
            reactions: vec![FusionReaction::DT],
            trigger,
            fuel,
            cooling,
            shielding,
            power_w: params.target_power_w,
            volume_m3: volume,
            mass_kg: mass,
            cost_usd: 50_000_000.0 + params.target_power_w * 0.5,
            lifetime_years: 30.0,
            trl: 3,
            advantages: vec![
                "Lower magnetic field than tokamak".to_string(),
                "Pulsed operation (simpler magnets)".to_string(),
                "Liquid liner provides shielding".to_string(),
                "Tritium breeding integrated".to_string(),
            ],
            challenges: vec![
                "Plasma instabilities".to_string(),
                "Repetition rate limited by liner".to_string(),
                "D-T neutron damage".to_string(),
                "Complex pulsed power system".to_string(),
            ],
            yield_estimate,
        }
    }

    /// Compare all architectures for given parameters
    pub fn compare_all(&self, params: &ReactorDesignParams) -> Vec<ReactorSpec> {
        let architectures = [
            ReactorArchitecture::SparkV1,
            ReactorArchitecture::FlowReactor,
            ReactorArchitecture::AneutronicCore,
            ReactorArchitecture::PulsedElectrolysis,
            ReactorArchitecture::MoltenSalt,
            ReactorArchitecture::ModularCell,
            ReactorArchitecture::MagnetizedTarget,
        ];

        architectures.iter()
            .map(|arch| {
                let mut p = params.clone();
                // Override architecture selection
                match arch {
                    ReactorArchitecture::SparkV1 => self.design_spark_v1(&p),
                    ReactorArchitecture::FlowReactor => self.design_flow_reactor(&p),
                    ReactorArchitecture::AneutronicCore => {
                        p.allow_neutrons = false;
                        self.design_aneutronic(&p)
                    },
                    ReactorArchitecture::PulsedElectrolysis => self.design_electrolysis(&p),
                    ReactorArchitecture::MoltenSalt => self.design_molten_salt(&p),
                    ReactorArchitecture::ModularCell => self.design_modular(&p),
                    ReactorArchitecture::MagnetizedTarget => self.design_magnetized(&p),
                }
            })
            .collect()
    }

    /// Rank architectures by weighted score
    pub fn rank(&self, params: &ReactorDesignParams) -> Vec<(ReactorSpec, f64)> {
        let specs = self.compare_all(params);

        let mut scored: Vec<_> = specs.into_iter().map(|spec| {
            let score = self.score_architecture(&spec, params);
            (spec, score)
        }).collect();

        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        scored
    }

    /// Score an architecture against parameters
    fn score_architecture(&self, spec: &ReactorSpec, params: &ReactorDesignParams) -> f64 {
        let mut score = 0.0;
        let mut penalties = 0.0;

        // TRL bonus (0-30 points)
        if spec.trl >= params.min_trl {
            score += (spec.trl as f64) * 3.0;
        } else {
            penalties += 50.0;
        }

        // Cost score (0-25 points)
        if spec.cost_usd <= params.max_cost_usd {
            score += 25.0 * (1.0 - spec.cost_usd / params.max_cost_usd);
        } else {
            penalties += 30.0 * (spec.cost_usd / params.max_cost_usd - 1.0);
        }

        // Volume score (0-15 points)
        if spec.volume_m3 <= params.max_volume_m3 {
            score += 15.0 * (1.0 - spec.volume_m3 / params.max_volume_m3);
        } else {
            penalties += 20.0 * (spec.volume_m3 / params.max_volume_m3 - 1.0);
        }

        // Mass score (0-15 points)
        if spec.mass_kg <= params.max_mass_kg {
            score += 15.0 * (1.0 - spec.mass_kg / params.max_mass_kg);
        } else {
            penalties += 20.0 * (spec.mass_kg / params.max_mass_kg - 1.0);
        }

        // Lifetime score (0-15 points)
        let lifetime_ratio = spec.lifetime_years / params.target_lifetime_years;
        score += 15.0 * lifetime_ratio.min(2.0) / 2.0;

        // Neutron penalty (if not allowed)
        if !params.allow_neutrons {
            match spec.architecture {
                ReactorArchitecture::AneutronicCore => score += 20.0,
                _ => penalties += 40.0,
            }
        }

        (score - penalties).max(0.0)
    }
}

impl Default for ReactorDesigner {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_designer_creation() {
        let designer = ReactorDesigner::new();
        assert!(!designer.trigger_library.systems.is_empty());
    }

    #[test]
    fn test_architecture_selection() {
        let designer = ReactorDesigner::new();

        // Consumer: should select aneutronic (no neutrons allowed)
        let consumer = ReactorDesignParams::consumer();
        let spec = designer.design(&consumer);
        assert_eq!(spec.architecture, ReactorArchitecture::AneutronicCore);

        // Prototype: small power, low cost → electrolysis
        let proto = ReactorDesignParams {
            target_power_w: 100.0,
            max_cost_usd: 5_000.0,
            allow_neutrons: true,
            ..Default::default()
        };
        let spec = designer.design(&proto);
        assert_eq!(spec.architecture, ReactorArchitecture::PulsedElectrolysis);
    }

    #[test]
    fn test_compare_all() {
        let designer = ReactorDesigner::new();
        let params = ReactorDesignParams::default();

        let specs = designer.compare_all(&params);
        assert_eq!(specs.len(), 7);

        for spec in &specs {
            assert!(spec.power_w > 0.0);
            assert!(spec.mass_kg > 0.0);
        }
    }

    #[test]
    fn test_ranking() {
        let designer = ReactorDesigner::new();
        let params = ReactorDesignParams::default();

        let ranked = designer.rank(&params);
        assert!(!ranked.is_empty());

        // Scores should be in descending order
        for i in 1..ranked.len() {
            assert!(ranked[i-1].1 >= ranked[i].1);
        }
    }

    #[test]
    fn test_modular_scaling() {
        let designer = ReactorDesigner::new();

        // Test different power levels
        for power in [100.0, 1000.0, 10_000.0, 100_000.0] {
            let params = ReactorDesignParams {
                target_power_w: power,
                ..Default::default()
            };
            let spec = designer.design_modular(&params);

            // Power should scale approximately linearly
            assert!((spec.power_w - power).abs() < power * 0.1);
        }
    }
}
