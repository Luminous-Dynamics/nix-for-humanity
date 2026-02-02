//! # Coupled Multi-Physics Simulation
//!
//! Integrates all physics modules into a unified simulation:
//! - Thermal ↔ Damage: Temperature affects healing rates
//! - Geometry ↔ Shielding: Joint optimization for form factor
//! - Pulse ↔ Thermal: Fatigue and cycling analysis
//!
//! ## Coupling Diagram
//!
//! ```text
//!                    ┌─────────────────────────────────────┐
//!                    │       COUPLED PHYSICS ENGINE        │
//!                    └─────────────────────────────────────┘
//!                                     │
//!          ┌──────────────────────────┼──────────────────────────┐
//!          ▼                          ▼                          ▼
//!    ┌───────────┐             ┌───────────┐             ┌───────────┐
//!    │  THERMAL  │◄───────────►│  DAMAGE   │◄───────────►│   PULSE   │
//!    │ Transport │  T→healing  │Accumulation│  duty→DPA  │ Dynamics  │
//!    └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
//!          │                         │                         │
//!          ▼                         ▼                         ▼
//!    ┌───────────┐             ┌───────────┐             ┌───────────┐
//!    │ GEOMETRY  │◄───────────►│ SHIELDING │             │  FATIGUE  │
//!    │   Form    │  S/V ratio  │ Thickness │             │  Cycles   │
//!    └───────────┘             └───────────┘             └───────────┘
//! ```

use crate::genesis::GenesisSeed;
use super::radiation_damage::FusionReaction;
use super::thermal_transport::{ThermalProperties, LayerGeometry, ThermalTransport, TemperatureProfile};
use super::neutron_shielding::{NeutronShielding, OptimalShielding};
use super::geometry::{GeometryOptimizer, GeometryWeights, EngineGeometry};
use super::pulse_dynamics::{PulseDynamics, PulseProfile, ThermalCycling};
use super::high_entropy_alloys::HEADesigner;
use super::advanced_materials::AdvancedMaterials;

/// Operating conditions for coupled simulation
#[derive(Debug, Clone)]
pub struct OperatingConditions {
    /// Target average power (kW)
    pub power_kw: f64,
    /// Fusion reaction type
    pub reaction: FusionReaction,
    /// Ambient temperature (K)
    pub ambient_temp_k: f64,
    /// Convection coefficient (W/m²·K)
    pub h_convection: f64,
    /// Target lifetime (years)
    pub target_lifetime_years: f64,
    /// Maximum allowable dose rate (mSv/hr)
    pub max_dose_rate: f64,
}

impl OperatingConditions {
    /// Consumer unit defaults (5 kW, 25 year lifetime)
    pub fn consumer() -> Self {
        Self {
            power_kw: 5.0,
            reaction: FusionReaction::DD,
            ambient_temp_k: 300.0,
            h_convection: 25.0,
            target_lifetime_years: 25.0,
            max_dose_rate: 0.001,
        }
    }

    /// Industrial unit defaults (100 MW, 40 year lifetime)
    /// Uses liquid metal cooling (NaK or PbLi) for high heat flux
    pub fn industrial() -> Self {
        Self {
            power_kw: 100_000.0,
            reaction: FusionReaction::DT,
            ambient_temp_k: 350.0,
            h_convection: 50_000.0,  // Liquid metal cooling (NaK/PbLi)
            target_lifetime_years: 40.0,
            max_dose_rate: 0.025,
        }
    }

    /// Industrial unit with D-D (less challenging neutrons)
    pub fn industrial_dd() -> Self {
        Self {
            power_kw: 100_000.0,
            reaction: FusionReaction::DD,
            ambient_temp_k: 350.0,
            h_convection: 20_000.0,  // Water cooling sufficient for D-D
            target_lifetime_years: 40.0,
            max_dose_rate: 0.025,
        }
    }

    /// Research prototype (50 kW, 10 year lifetime)
    pub fn prototype() -> Self {
        Self {
            power_kw: 50.0,
            reaction: FusionReaction::DD,
            ambient_temp_k: 300.0,
            h_convection: 100.0,
            target_lifetime_years: 10.0,
            max_dose_rate: 0.01,
        }
    }

    /// D-He3 aneutronic consumer unit (5 kW)
    /// Nearly zero neutron production - minimal shielding required
    pub fn aneutronic_consumer() -> Self {
        Self {
            power_kw: 5.0,
            reaction: FusionReaction::DHe3,
            ambient_temp_k: 300.0,
            h_convection: 25.0,
            target_lifetime_years: 30.0,
            max_dose_rate: 0.0001, // Much stricter - should be easy to meet
        }
    }

    /// D-He3 aneutronic industrial (100 MW)
    /// Aneutronic but requires higher ignition temperature
    pub fn aneutronic_industrial() -> Self {
        Self {
            power_kw: 100_000.0,
            reaction: FusionReaction::DHe3,
            ambient_temp_k: 350.0,
            h_convection: 20_000.0,
            target_lifetime_years: 40.0,
            max_dose_rate: 0.001,
        }
    }
}

/// Temperature-dependent healing rate model
#[derive(Debug, Clone)]
pub struct ThermalDamageCoupling {
    /// Base healing rate at reference temperature (DPA/s)
    pub base_healing_rate: f64,
    /// Reference temperature (K)
    pub reference_temp_k: f64,
    /// Activation energy for healing (eV)
    pub activation_energy_ev: f64,
}

impl ThermalDamageCoupling {
    /// Default for HEA materials
    pub fn hea_default() -> Self {
        Self {
            base_healing_rate: 1e-8,
            reference_temp_k: 600.0,
            activation_energy_ev: 0.5,
        }
    }

    /// Calculate effective healing rate at given temperature profile
    pub fn effective_healing_rate(&self, profile: &TemperatureProfile) -> f64 {
        let kb = 8.617e-5; // Boltzmann constant in eV/K
        let avg_temp = (profile.t_max + profile.t_shell_outer) / 2.0;

        // Arrhenius equation
        let rate_factor = (
            -self.activation_energy_ev / kb *
            (1.0 / avg_temp - 1.0 / self.reference_temp_k)
        ).exp();

        self.base_healing_rate * rate_factor
    }
}

/// Geometry and shielding optimization result
#[derive(Debug, Clone)]
pub struct GeometryShieldingResult {
    /// Optimized geometry
    pub geometry: EngineGeometry,
    /// Shielding result
    pub shielding: OptimalShielding,
    /// Total system mass (kg)
    pub total_mass_kg: f64,
    /// Shielding thickness (m)
    pub shielding_thickness_m: f64,
}

/// Pulse and thermal cycling result
#[derive(Debug, Clone)]
pub struct PulseThermalResult {
    /// Optimized pulse profile
    pub pulse: PulseProfile,
    /// Thermal cycling analysis
    pub cycling: ThermalCycling,
    /// Equilibrium DPA level
    pub equilibrium_dpa: f64,
    /// Estimated lifetime from damage (years)
    pub lifetime_years: f64,
    /// Fatigue lifetime (years)
    pub fatigue_lifetime_years: f64,
    /// Limiting factor description
    pub limiting_factor: String,
}

/// Complete coupled simulation result
#[derive(Debug, Clone)]
pub struct CoupledSimulationResult {
    /// Operating conditions used
    pub conditions: OperatingConditions,
    /// Shell material name
    pub shell_material: String,
    /// Interface material name
    pub interface_material: String,
    /// Core material name
    pub core_material: String,
    /// Temperature profile
    pub thermal_profile: TemperatureProfile,
    /// Effective healing rate
    pub effective_healing_rate: f64,
    /// Geometry and shielding
    pub geometry_shielding: GeometryShieldingResult,
    /// Pulse and thermal cycling
    pub pulse_thermal: PulseThermalResult,
    /// Overall feasibility
    pub feasible: bool,
    /// Limiting factors
    pub limiting_factors: Vec<String>,
    /// Recommendations
    pub recommendations: Vec<String>,
}

/// Coupled multi-physics simulation engine
pub struct CoupledPhysicsEngine {
    _genesis: GenesisSeed,
    thermal: ThermalTransport,
    shielding: NeutronShielding,
    geometry: GeometryOptimizer,
    _pulse: PulseDynamics,
    _hea: HEADesigner,
    _materials: AdvancedMaterials,
}

impl CoupledPhysicsEngine {
    /// Create from genesis seed
    pub fn from_genesis(genesis: &GenesisSeed) -> Self {
        Self {
            _genesis: genesis.clone(),
            thermal: ThermalTransport::from_genesis(genesis),
            shielding: NeutronShielding::from_genesis(genesis),
            geometry: GeometryOptimizer::from_genesis(genesis),
            _pulse: PulseDynamics::from_genesis(genesis),
            _hea: HEADesigner::from_genesis(genesis),
            _materials: AdvancedMaterials::from_genesis(genesis),
        }
    }

    /// Run complete coupled simulation
    pub fn simulate(&self, conditions: &OperatingConditions) -> CoupledSimulationResult {
        // Step 1: Select materials based on operating conditions
        let (shell, interface, core) = self.select_materials(conditions);

        // Step 2: Optimize geometry and shielding jointly
        let geo_shield = self.optimize_geometry_shielding(conditions);

        // Step 3: Calculate thermal profile
        let thermal_profile = self.calculate_thermal_profile(
            conditions,
            &shell,
            &interface,
            &core,
            &geo_shield.geometry,
        );

        // Step 4: Calculate temperature-dependent healing
        let coupling = ThermalDamageCoupling::hea_default();
        let effective_healing = coupling.effective_healing_rate(&thermal_profile);

        // Step 5: Optimize pulse with thermal coupling
        let pulse_thermal = self.optimize_pulse_thermal(
            conditions,
            effective_healing,
            &thermal_profile,
        );

        // Step 6: Assess feasibility
        let (feasible, limiting_factors, recommendations) = self.assess_feasibility(
            conditions,
            &thermal_profile,
            &geo_shield,
            &pulse_thermal,
        );

        CoupledSimulationResult {
            conditions: conditions.clone(),
            shell_material: shell.name.clone(),
            interface_material: interface.name.clone(),
            core_material: core.name.clone(),
            thermal_profile,
            effective_healing_rate: effective_healing,
            geometry_shielding: geo_shield,
            pulse_thermal,
            feasible,
            limiting_factors,
            recommendations,
        }
    }

    /// Select optimal materials for conditions
    fn select_materials(
        &self,
        conditions: &OperatingConditions,
    ) -> (ThermalProperties, ThermalProperties, ThermalProperties) {
        // For high-power DT, use MAX phase shell
        let shell = if conditions.power_kw > 10_000.0
            && conditions.reaction == FusionReaction::DT {
            ThermalProperties::max_phase()
        } else {
            ThermalProperties::hea_shell()
        };

        let interface = ThermalProperties::nano_laminate();
        let core = ThermalProperties::galinstan();

        (shell, interface, core)
    }

    /// Optimize geometry and shielding jointly
    fn optimize_geometry_shielding(
        &self,
        conditions: &OperatingConditions,
    ) -> GeometryShieldingResult {
        // Geometry weights for different applications
        let weights = if conditions.power_kw < 50.0 {
            GeometryWeights::consumer()
        } else {
            GeometryWeights::industrial()
        };

        // Power density estimation
        // Industrial scale needs lower power density for thermal management
        let power_density = if conditions.power_kw < 100.0 {
            50.0 // kW/m³ for consumer (compact, lower heat load)
        } else if conditions.power_kw < 10_000.0 {
            30.0 // kW/m³ for research/mid-scale
        } else {
            10.0 // kW/m³ for industrial (larger, better cooling)
        };

        let geometry_opt = self.geometry.optimize(conditions.power_kw, power_density, &weights);
        let geometry = geometry_opt.geometry;

        // Shielding optimization - scale limits based on application
        let distance = geometry.outer_radius;

        // D-T neutrons (14.1 MeV) need much more shielding than D-D (2.45 MeV)
        // Industrial scale also allows for larger shielding budgets
        let (max_thickness, max_mass) = match (conditions.reaction, conditions.power_kw > 1000.0) {
            (FusionReaction::DT, true) => (3.0, 20000.0),   // Industrial D-T: 3m, 20 t/m²
            (FusionReaction::DT, false) => (2.0, 10000.0),  // Consumer D-T: 2m, 10 t/m²
            (FusionReaction::DD, true) => (1.5, 10000.0),   // Industrial D-D: 1.5m
            (FusionReaction::DD, false) => (1.0, 5000.0),   // Consumer D-D: 1m
            (FusionReaction::DHe3, _) => (0.5, 2000.0),     // Aneutronic: minimal
            (FusionReaction::DdProton, _) => (0.5, 2000.0), // Aneutronic branch
        };

        let shielding = self.shielding.optimize_shielding(
            conditions.reaction,
            conditions.power_kw,
            distance,
            max_thickness,
            max_mass,
        );

        // Calculate total mass
        let shell_volume = geometry.shell_volume();
        let shell_density = 7200.0; // HEA kg/m³
        let shell_mass = shell_volume * shell_density;

        let shielding_area = 4.0 * std::f64::consts::PI * geometry.outer_radius.powi(2);
        let shielding_mass = shielding.mass_per_area * shielding_area;

        let core_volume = (4.0 / 3.0) * std::f64::consts::PI * geometry.core_radius.powi(3);
        let core_mass = core_volume * 6440.0; // Galinstan

        GeometryShieldingResult {
            geometry,
            shielding,
            total_mass_kg: shell_mass + shielding_mass + core_mass,
            shielding_thickness_m: max_thickness.min(1.0),
        }
    }

    /// Calculate thermal profile
    fn calculate_thermal_profile(
        &self,
        conditions: &OperatingConditions,
        shell: &ThermalProperties,
        interface: &ThermalProperties,
        core: &ThermalProperties,
        geometry: &EngineGeometry,
    ) -> TemperatureProfile {
        let interface_outer = geometry.core_radius + geometry.interface_thickness;
        let shell_outer = interface_outer + geometry.shell_thickness;

        let core_geom = LayerGeometry::sphere(0.0, geometry.core_radius);
        let interface_geom = LayerGeometry::sphere(
            geometry.core_radius,
            interface_outer,
        );
        let shell_geom = LayerGeometry::sphere(
            interface_outer,
            shell_outer,
        );

        self.thermal.steady_state_profile(
            conditions.power_kw * 1000.0,
            shell, &shell_geom,
            interface, &interface_geom,
            core, &core_geom,
            conditions.ambient_temp_k + 20.0, // Coolant slightly above ambient
            conditions.h_convection,
        )
    }

    /// Optimize pulse dynamics with thermal coupling
    fn optimize_pulse_thermal(
        &self,
        conditions: &OperatingConditions,
        effective_healing: f64,
        thermal_profile: &TemperatureProfile,
    ) -> PulseThermalResult {
        // Create pulse profile based on power level
        let pulse = if conditions.power_kw < 100.0 {
            PulseProfile::pulsed(conditions.power_kw * 1.5, 0.1, 1.0) // Consumer: 100ms pulse, 1s period
        } else {
            PulseProfile::continuous(conditions.power_kw) // Industrial: continuous operation
        };

        // Calculate thermal cycling
        let dt = thermal_profile.t_max - thermal_profile.t_shell_outer;

        // Apply swing factor for damping
        let thermal_tau: f64 = 100.0; // Thermal time constant (s)
        let swing_factor: f64 = (1.0_f64 - (-pulse.pulse_duration_s / thermal_tau).exp()).min(0.5);
        let effective_dt = dt * swing_factor;

        // Fatigue lifetime (Coffin-Manson)
        let fatigue_coeff = 1e10; // HEA fatigue coefficient
        let fatigue_exp = 2.5;
        let fatigue_cycles = fatigue_coeff / effective_dt.max(1.0).powf(fatigue_exp);

        let cycling = ThermalCycling {
            delta_t: effective_dt,
            time_constant: thermal_tau,
            cycles_to_failure: fatigue_cycles,
            fatigue_safety: 2.0,
        };

        // Calculate equilibrium DPA and lifetime
        // DPA rate depends on neutron flux at wall, which scales with power/area
        // Larger reactors have better geometric spreading
        let power_mw = conditions.power_kw / 1000.0;
        // Approximate first wall area (scales with power^0.67 for volume scaling)
        let wall_area_m2 = 4.0 * std::f64::consts::PI * (power_mw.powf(0.33) * 2.0).powi(2);
        // Neutron wall load (MW/m²) - typically 1-2 MW/m² for fusion
        let wall_load = power_mw / wall_area_m2.max(1.0);
        // DPA rate: ~10 DPA/year per MW/m² for steel-like materials
        let dpa_per_year = wall_load * 10.0;
        let dpa_rate = dpa_per_year / (365.25 * 24.0 * 3600.0); // Convert to DPA/s

        let equilibrium_dpa = dpa_rate / effective_healing.max(1e-15);

        // Critical DPA depends on material - MAX phase more resistant
        let critical_dpa = if conditions.power_kw > 10_000.0 {
            200.0 // MAX phase: more radiation resistant
        } else {
            100.0 // HEA
        };
        let lifetime_years = if equilibrium_dpa < critical_dpa {
            f64::INFINITY
        } else {
            critical_dpa / (dpa_rate * 3600.0 * 24.0 * 365.25)
        };

        // Calculate cycles per year (using period_s which includes both pulse and rest)
        let cycles_per_year = 365.25 * 24.0 * 3600.0 / pulse.period_s;
        let fatigue_lifetime_years = fatigue_cycles / cycles_per_year;

        let limiting_factor = if lifetime_years < fatigue_lifetime_years {
            "Radiation damage".to_string()
        } else {
            "Thermal fatigue".to_string()
        };

        PulseThermalResult {
            pulse,
            cycling,
            equilibrium_dpa,
            lifetime_years: lifetime_years.min(1e6),
            fatigue_lifetime_years: fatigue_lifetime_years.min(1e6),
            limiting_factor,
        }
    }

    /// Assess overall feasibility
    fn assess_feasibility(
        &self,
        conditions: &OperatingConditions,
        thermal_profile: &TemperatureProfile,
        geo_shield: &GeometryShieldingResult,
        pulse_thermal: &PulseThermalResult,
    ) -> (bool, Vec<String>, Vec<String>) {
        let mut limiting_factors = Vec::new();
        let mut recommendations = Vec::new();
        let mut feasible = true;

        // Check shielding (with 10% tolerance)
        let dose_limit = conditions.max_dose_rate * 1.1;
        if geo_shield.shielding.final_dose > dose_limit {
            feasible = false;
            limiting_factors.push(format!(
                "Dose rate {:.4} mSv/hr exceeds limit {:.4} mSv/hr",
                geo_shield.shielding.final_dose, conditions.max_dose_rate
            ));
            recommendations.push("Increase shielding thickness or use higher-Z material".to_string());
        }

        // Check temperature - material-dependent limits
        // Consumer/prototype: HEA shell (1200 K limit)
        // Industrial: MAX phase ceramics (1600 K limit)
        let (max_temp_limit, material_name) = if conditions.power_kw > 10_000.0 {
            (1600.0, "MAX phase")  // Ti3SiC2 for industrial
        } else {
            (1200.0, "HEA")  // TiVZrNbPd for consumer
        };

        if thermal_profile.t_max > max_temp_limit {
            feasible = false;
            limiting_factors.push(format!(
                "Max temperature {:.0} K exceeds {} limit {:.0} K",
                thermal_profile.t_max, material_name, max_temp_limit
            ));
            recommendations.push("Improve cooling or reduce power density".to_string());
        }

        // Check lifetime
        let min_lifetime = conditions.target_lifetime_years * 0.5;
        let actual_lifetime = pulse_thermal.lifetime_years.min(pulse_thermal.fatigue_lifetime_years);
        if actual_lifetime < min_lifetime {
            feasible = false;
            limiting_factors.push(format!(
                "Lifetime {:.1} years below target {:.1} years",
                actual_lifetime, conditions.target_lifetime_years
            ));
            recommendations.push("Reduce duty cycle or improve materials".to_string());
        }

        if feasible {
            recommendations.push("Design meets all feasibility criteria".to_string());
        }

        (feasible, limiting_factors, recommendations)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn setup() -> CoupledPhysicsEngine {
        let genesis = GenesisSeed::from_phrase("coupled test");
        CoupledPhysicsEngine::from_genesis(&genesis)
    }

    #[test]
    fn test_consumer_simulation() {
        let engine = setup();
        let conditions = OperatingConditions::consumer();
        let result = engine.simulate(&conditions);

        assert!(result.thermal_profile.t_max > result.thermal_profile.t_min);
        assert!(result.geometry_shielding.total_mass_kg > 0.0);
    }

    #[test]
    fn test_thermal_damage_coupling() {
        let coupling = ThermalDamageCoupling::hea_default();

        let profile = TemperatureProfile {
            radii: vec![0.0, 0.1],
            temperatures: vec![600.0, 500.0],
            t_max: 700.0,
            t_min: 400.0,
            t_shell_outer: 500.0,
            t_core_center: 600.0,
            heat_flux_outer: 50000.0,
        };

        let rate = coupling.effective_healing_rate(&profile);
        assert!(rate > 0.0);
    }

    #[test]
    fn test_industrial_simulation() {
        let engine = setup();
        let conditions = OperatingConditions::industrial();
        let result = engine.simulate(&conditions);

        // Industrial should have larger mass
        let consumer_result = engine.simulate(&OperatingConditions::consumer());
        assert!(result.geometry_shielding.total_mass_kg > consumer_result.geometry_shielding.total_mass_kg);
    }
}
