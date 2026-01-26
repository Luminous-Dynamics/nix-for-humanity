"""
NixOS Pattern Catalog for WisdomEngine

This is the "seed crystal" - the initial knowledge that bootstraps
Luminous Nix's understanding of NixOS best practices.

Based on the NixOS Codex test suite in mycelix-core-types/wisdom_engine/tests.rs

Pattern Categories:
1. Package Management: channels, flakes, nix-env
2. Development Environments: mkShell, devShell
3. Hardware Configuration: NVIDIA, AMD drivers
4. Secret Management: plaintext, agenix, sops-nix
5. System Configuration: monolithic, modular, flake-based

Each pattern includes:
- Description of what it does
- When to use it
- Known successors (if deprecated)
- Initial trust level
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING
from enum import Enum

# Handle both relative and absolute imports
try:
    from .wisdom_bridge import WisdomBridge, TrustLevel, PatternOutcome
except ImportError:
    from wisdom_bridge import WisdomBridge, TrustLevel, PatternOutcome


# ============ Domain Constants ============

class NIXOS_DOMAINS:
    """NixOS pattern domains (hierarchical)"""

    # Root domain
    NIXOS = "nixos"

    # Level 1 domains
    SYSTEM_MANAGEMENT = "system_management"
    PACKAGE_MANAGEMENT = "package_management"
    DEVELOPMENT = "development_environments"
    HARDWARE = "hardware"
    SECRETS = "secrets_management"
    REPRODUCIBILITY = "reproducibility"

    # Level 2 domains
    HARDWARE_NVIDIA = "hardware_nvidia"
    HARDWARE_AMD = "hardware_amd"
    FLAKES = "flakes"


@dataclass
class NixOSPattern:
    """A NixOS pattern definition"""
    id: str
    name: str
    description: str
    domain: str
    tags: List[str]
    trust_level: TrustLevel = TrustLevel.AUDITED
    deprecated: bool = False
    successor: Optional[str] = None
    nixos_wiki_url: Optional[str] = None


# ============ Pattern Catalog ============

NIXOS_PATTERN_CATALOG: Dict[str, NixOSPattern] = {
    # ===== Package Management (Legacy) =====
    "nix_channel": NixOSPattern(
        id="nix_channel",
        name="Nix Channels",
        description="Traditional package source management via nix-channel. "
                    "Mutable state, non-reproducible across machines.",
        domain=NIXOS_DOMAINS.PACKAGE_MANAGEMENT,
        tags=["legacy", "channels", "package-source"],
        trust_level=TrustLevel.AUDITED,
        deprecated=True,
        successor="flakes",
        nixos_wiki_url="https://nixos.wiki/wiki/Nix_channels",
    ),

    "monolithic_config": NixOSPattern(
        id="monolithic_config",
        name="Monolithic configuration.nix",
        description="Single-file NixOS configuration. Simple but hard to maintain "
                    "as system grows. No module reuse across machines.",
        domain=NIXOS_DOMAINS.SYSTEM_MANAGEMENT,
        tags=["legacy", "configuration", "simple"],
        trust_level=TrustLevel.TESTIMONIAL,
        deprecated=True,
        successor="modular_config",
    ),

    "nix_env_install": NixOSPattern(
        id="nix_env_install",
        name="nix-env -i",
        description="Imperative package installation. Creates mutable state that "
                    "differs from declarative configuration. Avoid in production.",
        domain=NIXOS_DOMAINS.PACKAGE_MANAGEMENT,
        tags=["legacy", "imperative", "anti-pattern"],
        trust_level=TrustLevel.TESTIMONIAL,
        deprecated=True,
        successor="declarative_packages",
    ),

    # ===== Package Management (Modern) =====
    "flakes": NixOSPattern(
        id="flakes",
        name="Nix Flakes",
        description="Modern, reproducible Nix with flake.nix. Provides lock files, "
                    "hermetic evaluation, and composable inputs. The future of Nix.",
        domain=NIXOS_DOMAINS.FLAKES,
        tags=["modern", "flakes", "reproducible", "recommended"],
        trust_level=TrustLevel.CRYPTOGRAPHIC,  # Lock files are cryptographic verification
    ),

    "flake_lock": NixOSPattern(
        id="flake_lock",
        name="Flake Lock Files",
        description="Cryptographic pinning of all inputs via flake.lock. "
                    "Ensures exact reproducibility across time and machines.",
        domain=NIXOS_DOMAINS.FLAKES,
        tags=["flakes", "lock", "reproducible", "security"],
        trust_level=TrustLevel.CRYPTOGRAPHIC,
    ),

    "declarative_packages": NixOSPattern(
        id="declarative_packages",
        name="Declarative Package Management",
        description="Define packages in configuration.nix or home.nix. "
                    "Reproducible, version-controlled, rollback-friendly.",
        domain=NIXOS_DOMAINS.PACKAGE_MANAGEMENT,
        tags=["declarative", "packages", "recommended"],
        trust_level=TrustLevel.AUDITED,
    ),

    # ===== Development Environments =====
    "mk_shell": NixOSPattern(
        id="mk_shell",
        name="mkShell (Legacy)",
        description="Traditional development shell using mkShell. Works but "
                    "lacks flake integration and modern features.",
        domain=NIXOS_DOMAINS.DEVELOPMENT,
        tags=["legacy", "shell", "development"],
        trust_level=TrustLevel.AUDITED,
        deprecated=True,
        successor="dev_shell",
    ),

    "dev_shell": NixOSPattern(
        id="dev_shell",
        name="devShells (Flakes)",
        description="Modern development environments via flake devShells. "
                    "Reproducible, composable, nix develop integration.",
        domain=NIXOS_DOMAINS.DEVELOPMENT,
        tags=["flakes", "shell", "development", "recommended"],
        trust_level=TrustLevel.CRYPTOGRAPHIC,
    ),

    "direnv_flake": NixOSPattern(
        id="direnv_flake",
        name="Direnv + Flakes",
        description="Automatic environment activation with direnv and flakes. "
                    "Seamless developer experience with use flake in .envrc.",
        domain=NIXOS_DOMAINS.DEVELOPMENT,
        tags=["direnv", "flakes", "automation", "recommended"],
        trust_level=TrustLevel.AUDITED,
    ),

    # ===== Hardware: NVIDIA =====
    "nvidia_driver": NixOSPattern(
        id="nvidia_driver",
        name="NVIDIA Proprietary Drivers",
        description="hardware.nvidia.enable for proprietary drivers. "
                    "Required for CUDA and optimal gaming performance.",
        domain=NIXOS_DOMAINS.HARDWARE_NVIDIA,
        tags=["nvidia", "driver", "proprietary", "gaming", "cuda"],
        trust_level=TrustLevel.AUDITED,
    ),

    "nvidia_offload": NixOSPattern(
        id="nvidia_offload",
        name="NVIDIA PRIME Offload",
        description="Optimus laptop support with PRIME render offload. "
                    "Allows switching between integrated and discrete GPU.",
        domain=NIXOS_DOMAINS.HARDWARE_NVIDIA,
        tags=["nvidia", "laptop", "optimus", "prime"],
        trust_level=TrustLevel.AUDITED,
    ),

    "nvidia_opengl": NixOSPattern(
        id="nvidia_opengl",
        name="NVIDIA OpenGL/Vulkan",
        description="OpenGL and Vulkan support for NVIDIA. "
                    "hardware.opengl with nvidia-related packages.",
        domain=NIXOS_DOMAINS.HARDWARE_NVIDIA,
        tags=["nvidia", "opengl", "vulkan", "graphics"],
        trust_level=TrustLevel.AUDITED,
    ),

    # ===== Hardware: AMD =====
    "amd_driver": NixOSPattern(
        id="amd_driver",
        name="AMD GPU Drivers (amdgpu)",
        description="Open-source amdgpu kernel driver. "
                    "Superior Linux support, recommended for AMD GPUs.",
        domain=NIXOS_DOMAINS.HARDWARE_AMD,
        tags=["amd", "driver", "open-source", "recommended"],
        trust_level=TrustLevel.AUDITED,
    ),

    "amd_vulkan": NixOSPattern(
        id="amd_vulkan",
        name="AMD Vulkan (RADV)",
        description="Mesa RADV Vulkan implementation. "
                    "Excellent performance, part of standard Mesa.",
        domain=NIXOS_DOMAINS.HARDWARE_AMD,
        tags=["amd", "vulkan", "radv", "gaming"],
        trust_level=TrustLevel.AUDITED,
    ),

    "amd_rocm": NixOSPattern(
        id="amd_rocm",
        name="AMD ROCm (GPU Compute)",
        description="AMD's GPU compute platform. "
                    "CUDA alternative for ML/HPC workloads.",
        domain=NIXOS_DOMAINS.HARDWARE_AMD,
        tags=["amd", "rocm", "compute", "ml", "cuda-alternative"],
        trust_level=TrustLevel.AUDITED,
    ),

    # ===== Secret Management =====
    "plaintext_secrets": NixOSPattern(
        id="plaintext_secrets",
        name="Plaintext Secrets (Anti-Pattern)",
        description="Storing secrets in configuration.nix or git. "
                    "SECURITY RISK: Never commit secrets to version control!",
        domain=NIXOS_DOMAINS.SECRETS,
        tags=["anti-pattern", "security-risk", "legacy"],
        trust_level=TrustLevel.TESTIMONIAL,
        deprecated=True,
        successor="agenix",
    ),

    "agenix": NixOSPattern(
        id="agenix",
        name="Agenix (Age Encryption)",
        description="Secret management using age encryption. "
                    "Secrets encrypted in git, decrypted at activation.",
        domain=NIXOS_DOMAINS.SECRETS,
        tags=["secrets", "encryption", "age", "recommended"],
        trust_level=TrustLevel.CRYPTOGRAPHIC,
    ),

    "sops_nix": NixOSPattern(
        id="sops_nix",
        name="sops-nix (SOPS)",
        description="Mozilla SOPS for NixOS secrets. "
                    "Supports age, GPG, cloud KMS. Popular in enterprise.",
        domain=NIXOS_DOMAINS.SECRETS,
        tags=["secrets", "sops", "encryption", "enterprise"],
        trust_level=TrustLevel.CRYPTOGRAPHIC,
    ),

    # ===== System Configuration =====
    "modular_config": NixOSPattern(
        id="modular_config",
        name="Modular NixOS Configuration",
        description="Split configuration across multiple files. "
                    "hardware.nix, networking.nix, users.nix, etc.",
        domain=NIXOS_DOMAINS.SYSTEM_MANAGEMENT,
        tags=["modular", "configuration", "maintainable"],
        trust_level=TrustLevel.AUDITED,
    ),

    "flake_config": NixOSPattern(
        id="flake_config",
        name="Flake-based NixOS Configuration",
        description="Full system configuration as a flake. "
                    "Reproducible, composable, multi-machine support.",
        domain=NIXOS_DOMAINS.SYSTEM_MANAGEMENT,
        tags=["flakes", "configuration", "recommended", "reproducible"],
        trust_level=TrustLevel.CRYPTOGRAPHIC,
    ),

    "home_manager": NixOSPattern(
        id="home_manager",
        name="Home Manager",
        description="User-level configuration management. "
                    "Dotfiles, user packages, and services declaratively.",
        domain=NIXOS_DOMAINS.SYSTEM_MANAGEMENT,
        tags=["home-manager", "user", "dotfiles", "recommended"],
        trust_level=TrustLevel.AUDITED,
    ),
}


class NixOSPatterns:
    """
    Utility class for working with NixOS patterns.

    Provides methods to initialize the WisdomEngine with the
    NixOS pattern catalog and record outcomes.
    """

    @staticmethod
    def initialize_engine(engine: WisdomBridge) -> int:
        """
        Initialize WisdomEngine with NixOS domains and patterns.

        Returns the number of patterns registered.
        """

        # Register domain hierarchy
        engine.register_domain(
            NIXOS_DOMAINS.NIXOS,
            "NixOS",
            description="Root domain for all NixOS patterns"
        )

        engine.register_domain(
            NIXOS_DOMAINS.SYSTEM_MANAGEMENT,
            "System Management",
            parent=NIXOS_DOMAINS.NIXOS,
            description="NixOS system configuration patterns"
        )

        engine.register_domain(
            NIXOS_DOMAINS.PACKAGE_MANAGEMENT,
            "Package Management",
            parent=NIXOS_DOMAINS.NIXOS,
            description="Package installation and management"
        )

        engine.register_domain(
            NIXOS_DOMAINS.DEVELOPMENT,
            "Development Environments",
            parent=NIXOS_DOMAINS.NIXOS,
            description="Development shell and tooling patterns"
        )

        engine.register_domain(
            NIXOS_DOMAINS.HARDWARE,
            "Hardware",
            parent=NIXOS_DOMAINS.NIXOS,
            description="Hardware configuration patterns"
        )

        engine.register_domain(
            NIXOS_DOMAINS.HARDWARE_NVIDIA,
            "NVIDIA Hardware",
            parent=NIXOS_DOMAINS.HARDWARE,
            description="NVIDIA GPU configuration"
        )

        engine.register_domain(
            NIXOS_DOMAINS.HARDWARE_AMD,
            "AMD Hardware",
            parent=NIXOS_DOMAINS.HARDWARE,
            description="AMD GPU configuration"
        )

        engine.register_domain(
            NIXOS_DOMAINS.SECRETS,
            "Secrets Management",
            parent=NIXOS_DOMAINS.NIXOS,
            description="Secret and credential management"
        )

        engine.register_domain(
            NIXOS_DOMAINS.FLAKES,
            "Flakes",
            parent=NIXOS_DOMAINS.NIXOS,
            description="Nix Flakes ecosystem"
        )

        engine.register_domain(
            NIXOS_DOMAINS.REPRODUCIBILITY,
            "Reproducibility",
            parent=NIXOS_DOMAINS.NIXOS,
            description="Reproducible build patterns"
        )

        # Register all patterns
        count = 0
        for pattern in NIXOS_PATTERN_CATALOG.values():
            engine.register_pattern(
                name=pattern.name,
                description=pattern.description,
                domain=pattern.domain,
                tags=pattern.tags,
                trust_level=pattern.trust_level,
                pattern_id=pattern.id,
            )

            # Mark deprecated patterns
            if pattern.deprecated:
                engine.deprecate_pattern(
                    pattern.id,
                    successor_id=pattern.successor,
                    reason="superseded by modern approach"
                )

            count += 1

        return count

    @staticmethod
    def seed_with_community_wisdom(engine: WisdomBridge):
        """
        Seed the engine with simulated community usage data.

        This represents the collective wisdom of the NixOS community
        accumulated over years of usage.

        Based on NixOS Codex test scenarios.
        """

        # Flakes: High success rate, widely adopted since 2021
        for _ in range(100):
            engine.record_success("flakes", context="general")
        for _ in range(5):
            engine.record_failure("flakes", context="learning_curve")

        # Channels: Decreasing usage, some failures with reproducibility
        for _ in range(50):
            engine.record_success("nix_channel", context="legacy_system")
        for _ in range(20):
            engine.record_failure("nix_channel", context="reproducibility_issue")

        # DevShell: Modern, high success
        for _ in range(80):
            engine.record_success("dev_shell", context="development")
        for _ in range(3):
            engine.record_failure("dev_shell", context="complex_dependencies")

        # Agenix: Strong success for secrets
        for _ in range(60):
            engine.record_success("agenix", context="secrets")
        for _ in range(2):
            engine.record_failure("agenix", context="key_management")

        # SOPS-nix: Also strong
        for _ in range(40):
            engine.record_success("sops_nix", context="secrets")
        for _ in range(3):
            engine.record_failure("sops_nix", context="cloud_kms_setup")

        # Plaintext secrets: All failures (security incidents)
        for _ in range(5):
            engine.record_failure("plaintext_secrets", context="security_incident")

        # Hardware drivers: Domain-specific success
        for _ in range(30):
            engine.record_success("nvidia_driver", context="nvidia_gpu")
        for _ in range(30):
            engine.record_success("amd_driver", context="amd_gpu")

        # Home Manager: High success
        for _ in range(70):
            engine.record_success("home_manager", context="user_config")


def get_nixos_pattern_catalog() -> Dict[str, NixOSPattern]:
    """Get the full NixOS pattern catalog"""
    return NIXOS_PATTERN_CATALOG
