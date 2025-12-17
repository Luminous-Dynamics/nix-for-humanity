"""
Sophia-NixOS: NixOS Package & Configuration Specialist

A specialized Sophia agent with deep expertise in:
- NixOS packages and the Nixpkgs repository
- Configuration generation and best practices
- Flakes and reproducible development environments
- System administration and troubleshooting
"""

from typing import Dict, List, Any, Union
from ..sophia.unified_consciousness import UnifiedSophiaEngine
from ..context import ensure_context, Context


class SophiaNixOS(UnifiedSophiaEngine):
    """
    NixOS Specialist Agent

    Extends the unified 9-layer consciousness with domain-specific
    knowledge about NixOS, packages, and configuration.
    """

    def __init__(self):
        """Initialize Sophia-NixOS specialist"""
        super().__init__()

        # Domain-specific knowledge
        self.specialization = "NixOS"
        self.expertise_domains = [
            "nixos",
            "packages",
            "configuration",
            "flakes",
            "derivations",
            "system-administration"
        ]

        # NixOS-specific knowledge base
        self.package_patterns = {
            # Common package categories
            "editors": ["vim", "emacs", "vscode", "nano", "kate"],
            "browsers": ["firefox", "chromium", "brave", "qutebrowser"],
            "terminals": ["alacritty", "kitty", "wezterm", "gnome-terminal"],
            "shells": ["bash", "zsh", "fish", "nushell"],
            "development": ["git", "gcc", "python3", "nodejs", "rust"],
        }

        self.common_configs = {
            "boot_loader": {
                "systemd-boot": "boot.loader.systemd-boot.enable = true;",
                "grub": "boot.loader.grub.enable = true;",
            },
            "network": {
                "networkmanager": "networking.networkmanager.enable = true;",
                "systemd-networkd": "systemd.network.enable = true;",
            },
            "desktop": {
                "gnome": "services.xserver.desktopManager.gnome.enable = true;",
                "plasma": "services.xserver.desktopManager.plasma5.enable = true;",
                "xfce": "services.xserver.desktopManager.xfce.enable = true;",
            }
        }

    def respond_to_query(self, query: str, context: Union[Dict[str, Any], Context]) -> Dict[str, Any]:
        """
        Respond to NixOS-specific queries with deep domain expertise

        Args:
            query: User query about NixOS
            context: Query context (dict or Context object)

        Returns:
            Enhanced response with NixOS-specific insights
        """
        # Ensure we have a proper Context object
        context = ensure_context(context)

        # Get base response from unified consciousness
        sophia_response = super().respond_to_query(query, context)

        # Convert SophiaResponse to dict for enhancement
        base_response = {
            "message": sophia_response.message,
            "insights": sophia_response.insights.copy(),
            "suggestions": sophia_response.suggestions.copy(),
            "actions": [],
            "confidence": 0.8,  # Default confidence
        }

        # Enhance with NixOS-specific knowledge
        query_lower = query.lower()

        # Package recommendations
        if any(word in query_lower for word in ["install", "package", "add"]):
            base_response = self._enhance_package_query(query_lower, base_response)

        # Configuration guidance
        elif any(word in query_lower for word in ["configure", "config", "setup", "enable"]):
            base_response = self._enhance_config_query(query_lower, base_response)

        # Flake recommendations
        elif "flake" in query_lower:
            base_response = self._enhance_flake_query(query_lower, base_response)

        # Add NixOS-specific confidence boost
        if base_response.get("confidence", 0) < 0.9:
            # NixOS specialist has high confidence in NixOS queries
            base_response["confidence"] = min(0.95, base_response.get("confidence", 0.8) + 0.1)

        return base_response

    def _enhance_package_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance package-related queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        # Identify package category
        for category, packages in self.package_patterns.items():
            if any(pkg in query for pkg in packages):
                insights.append(
                    f"💡 NixOS Expert: This is a {category} package. "
                    f"Consider these alternatives: {', '.join(packages[:3])}"
                )
                break

        # Add NixOS best practices
        suggestions.extend([
            "Use 'nix-env -iA nixpkgs.<package>' for user installation",
            "Consider adding to configuration.nix for system-wide installation",
            "Check 'nix-env -qaP <package>' to verify package name",
        ])

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def _enhance_config_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance configuration-related queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        # Identify configuration type
        for config_type, configs in self.common_configs.items():
            for name, config_line in configs.items():
                if name in query:
                    insights.append(
                        f"📝 NixOS Config: Add to /etc/nixos/configuration.nix:\n"
                        f"   {config_line}"
                    )
                    suggestions.append(
                        f"After editing, run: sudo nixos-rebuild switch"
                    )
                    break

        # Add general configuration advice
        if not any("NixOS Config" in i for i in insights):
            insights.append(
                "📝 NixOS Configuration: Edit /etc/nixos/configuration.nix "
                "for system-wide changes"
            )

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def _enhance_flake_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance flake-related queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "🚀 Flakes: Modern Nix feature for reproducible configurations"
        )

        suggestions.extend([
            "Initialize flake: 'nix flake init'",
            "Update inputs: 'nix flake update'",
            "Enter dev shell: 'nix develop'",
            "Build: 'nix build'",
        ])

        # Add flake template suggestion
        actions = response.get("actions", [])
        actions.append("show_flake_template")

        response["insights"] = insights
        response["suggestions"] = suggestions
        response["actions"] = actions
        return response

    def get_package_recommendations(self, category: str) -> List[str]:
        """Get package recommendations for a category"""
        return self.package_patterns.get(category, [])

    def get_config_template(self, config_type: str) -> str:
        """Get configuration template"""
        configs = self.common_configs.get(config_type, {})
        if configs:
            return "\n".join(configs.values())
        return ""

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get summary of NixOS expertise"""
        return {
            "specialization": self.specialization,
            "expertise_domains": self.expertise_domains,
            "package_categories": list(self.package_patterns.keys()),
            "config_types": list(self.common_configs.keys()),
            "confidence_in_domain": 0.95,
        }
