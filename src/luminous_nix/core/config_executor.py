#!/usr/bin/env python3
"""
Configuration File Executor
============================

This module integrates the configuration parser with the core system,
enabling intelligent analysis and suggestions for NixOS configurations.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

from ..core.config_parser import ConfigurationParser, ParsedConfiguration

logger = logging.getLogger(__name__)


@dataclass
class ConfigResult:
    """Result from configuration analysis"""
    success: bool
    message: str
    error: Optional[str] = None
    config: Optional[ParsedConfiguration] = None
    suggestions: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


class ConfigExecutor:
    """
    Executes configuration parsing and analysis requests.
    
    This executor:
    - Parses configuration.nix files
    - Validates configurations
    - Suggests improvements
    - Generates configuration snippets
    - Learns from configuration patterns
    """
    
    def __init__(self):
        """Initialize the configuration executor"""
        self.parser = ConfigurationParser()
        self.default_config_paths = [
            "/etc/nixos/configuration.nix",
            "~/.config/nixos/configuration.nix",
            "./configuration.nix"
        ]
        logger.info("📝 ConfigExecutor initialized - ready to analyze configurations")
    
    def execute(self, intent_type: str, query: str, entities: Dict[str, Any]) -> ConfigResult:
        """
        Execute a configuration-related request.
        
        Args:
            intent_type: Type of intent (should be CONFIG_PARSE)
            query: Original user query
            entities: Extracted entities from query
            
        Returns:
            ConfigResult with analysis results
        """
        logger.info(f"Executing config request: {query}")
        
        # Determine the configuration file to parse
        config_path = self._determine_config_path(entities.get('target'), query)
        
        if not config_path:
            return ConfigResult(
                success=False,
                message="Could not find configuration.nix file",
                error="No configuration file found at standard locations",
                suggestions=[
                    "Specify the path: 'parse config /path/to/configuration.nix'",
                    "Create a configuration: 'generate basic config'"
                ]
            )
        
        # Parse the configuration
        try:
            config = self.parser.parse_file(str(config_path))
            
            # Validate the configuration
            is_valid, validation_errors = self.parser.validate(config)
            
            # Get improvement suggestions
            improvements = self.parser.suggest_improvements(config)
            
            # Calculate statistics
            statistics = self._calculate_statistics(config)
            
            # Build result message
            message = self._build_result_message(config, is_valid, statistics)
            
            return ConfigResult(
                success=True,
                message=message,
                config=config,
                suggestions=config.suggestions,
                improvements=improvements,
                validation_errors=validation_errors,
                statistics=statistics
            )
            
        except Exception as e:
            logger.error(f"Failed to parse configuration: {e}")
            return ConfigResult(
                success=False,
                message=f"Failed to parse configuration: {str(e)}",
                error=str(e),
                suggestions=[
                    "Check that the file exists and is readable",
                    "Ensure the configuration has valid Nix syntax",
                    "Try: 'nixos-rebuild dry-build' to check for syntax errors"
                ]
            )
    
    def _determine_config_path(self, target: Optional[str], query: str) -> Optional[Path]:
        """
        Determine which configuration file to parse.
        
        Args:
            target: Extracted target from entities
            query: Original query
            
        Returns:
            Path to configuration file or None
        """
        # If a specific path is mentioned
        if target and ('/' in target or '.nix' in target):
            path = Path(target).expanduser()
            if path.exists():
                return path
        
        # Check for path in query
        for word in query.split():
            if '/' in word or word.endswith('.nix'):
                path = Path(word).expanduser()
                if path.exists():
                    return path
        
        # Try default locations
        for default_path in self.default_config_paths:
            path = Path(default_path).expanduser()
            if path.exists():
                logger.info(f"Found configuration at: {path}")
                return path
        
        return None
    
    def _calculate_statistics(self, config: ParsedConfiguration) -> Dict[str, Any]:
        """
        Calculate statistics about the configuration.
        
        Args:
            config: Parsed configuration
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_packages': len(config.packages),
            'total_services': len(config.services),
            'enabled_services': sum(1 for s in config.services.values() 
                                   if s.get('enabled', False)),
            'total_users': len(config.users),
            'total_imports': len(config.imports),
            'total_modules': len(config.modules),
            'has_boot_loader': bool(config.boot_config.get('loader')),
            'has_networking': bool(config.networking_config.get('hostname')),
            'firewall_enabled': config.networking_config.get('firewall_enabled', False),
            'parse_errors': len(config.parse_errors),
            'total_suggestions': len(config.suggestions)
        }
        
        # Categorize packages by type (heuristic)
        dev_packages = [p for p in config.packages if any(
            kw in p.lower() for kw in ['gcc', 'python', 'node', 'rust', 'git', 'vim', 'emacs']
        )]
        system_packages = [p for p in config.packages if any(
            kw in p.lower() for kw in ['htop', 'tree', 'wget', 'curl', 'tmux']
        )]
        
        stats['dev_packages'] = len(dev_packages)
        stats['system_packages'] = len(system_packages)
        
        return stats
    
    def _build_result_message(self, 
                              config: ParsedConfiguration,
                              is_valid: bool,
                              statistics: Dict[str, Any]) -> str:
        """
        Build a comprehensive result message.
        
        Args:
            config: Parsed configuration
            is_valid: Whether configuration is valid
            statistics: Calculated statistics
            
        Returns:
            Formatted result message
        """
        lines = []
        
        # Header
        lines.append("📋 NixOS Configuration Analysis")
        lines.append("=" * 40)
        
        # Validation status
        if is_valid:
            lines.append("✅ Configuration is valid")
        else:
            lines.append("⚠️ Configuration has issues")
        
        # Basic info
        lines.append(f"\n🖥️ System: {config.networking_config.get('hostname', 'unnamed')}")
        lines.append(f"📦 Packages: {statistics['total_packages']}")
        lines.append(f"🔧 Services: {statistics['enabled_services']}/{statistics['total_services']} enabled")
        lines.append(f"👤 Users: {statistics['total_users']}")
        
        # Boot and networking
        if config.boot_config.get('loader'):
            lines.append(f"🚀 Boot: {config.boot_config['loader']}")
        
        if statistics['firewall_enabled']:
            lines.append("🔥 Firewall: Enabled")
            if config.networking_config.get('allowed_tcp_ports'):
                ports = config.networking_config['allowed_tcp_ports']
                lines.append(f"   Open ports: {', '.join(map(str, ports))}")
        else:
            lines.append("⚠️ Firewall: Disabled")
        
        # Services detail
        if config.services:
            lines.append("\n📡 Active Services:")
            for service, details in config.services.items():
                if details.get('enabled'):
                    lines.append(f"  • {service}")
        
        # Users detail
        if config.users:
            lines.append("\n👥 Configured Users:")
            for username, user_config in config.users.items():
                user_type = "normal" if user_config.get('isNormalUser') else "system"
                shell = user_config.get('shell', 'default')
                lines.append(f"  • {username} ({user_type}, shell: {shell})")
        
        # Top packages
        if config.packages:
            lines.append("\n📦 Sample Packages (first 10):")
            for pkg in config.packages[:10]:
                lines.append(f"  • {pkg}")
            if len(config.packages) > 10:
                lines.append(f"  ... and {len(config.packages) - 10} more")
        
        # Statistics summary
        lines.append("\n📊 Statistics:")
        lines.append(f"  Development packages: {statistics.get('dev_packages', 0)}")
        lines.append(f"  System packages: {statistics.get('system_packages', 0)}")
        lines.append(f"  Total modules: {statistics['total_modules']}")
        
        # Issues and suggestions
        if config.parse_errors:
            lines.append("\n❌ Parse Errors:")
            for error in config.parse_errors[:3]:
                lines.append(f"  • {error}")
        
        if config.suggestions:
            lines.append("\n💡 Suggestions:")
            for suggestion in config.suggestions[:5]:
                lines.append(f"  {suggestion}")
        
        return "\n".join(lines)
    
    def generate_fix(self, issue: str) -> str:
        """
        Generate a fix for a specific configuration issue.
        
        Args:
            issue: Description of the issue
            
        Returns:
            Configuration snippet to fix the issue
        """
        # Map common issues to fixes
        fixes = {
            "firewall": self.parser.generate_snippet('networking.firewall.enable', True),
            "hostname": self.parser.generate_snippet('networking.hostName', 'nixos-system'),
            "boot": "boot.loader.systemd-boot.enable = true;\nboot.loader.efi.canTouchEfiVariables = true;",
            "password": "# Use mkpasswd -m sha-512 to generate\nusers.users.username.hashedPassword = \"$6$...\";",
            "ssh": self.parser.generate_snippet('services.openssh.enable', True)
        }
        
        # Find relevant fix
        issue_lower = issue.lower()
        for key, fix in fixes.items():
            if key in issue_lower:
                return fix
        
        # Default suggestion
        return "# No specific fix available - check NixOS manual"
    
    def learn_from_config(self, config: ParsedConfiguration) -> Dict[str, Any]:
        """
        Extract learning points from the configuration for SKG.
        
        Args:
            config: Parsed configuration
            
        Returns:
            Learning data for SKG integration
        """
        learning = {
            'patterns': [],
            'antipatterns': [],
            'user_preferences': {},
            'system_characteristics': {}
        }
        
        # Learn patterns
        if config.services.get('docker', {}).get('enabled'):
            learning['patterns'].append('containerization')
        
        if config.services.get('nginx', {}).get('enabled'):
            learning['patterns'].append('web_server')
        
        if len([s for s in config.services.values() if s.get('enabled')]) > 5:
            learning['patterns'].append('service_rich')
        
        # Learn antipatterns
        for user_config in config.users.values():
            if user_config.get('has_plaintext_password'):
                learning['antipatterns'].append('plaintext_passwords')
        
        if config.networking_config.get('firewall_disabled'):
            learning['antipatterns'].append('firewall_disabled')
        
        # Learn preferences
        if config.packages:
            # Detect editor preference
            for editor in ['vim', 'neovim', 'emacs', 'vscode', 'sublime']:
                if any(editor in pkg.lower() for pkg in config.packages):
                    learning['user_preferences']['editor'] = editor
                    break
            
            # Detect shell preference
            for shell in ['zsh', 'fish', 'bash']:
                if any(shell in pkg.lower() for pkg in config.packages):
                    learning['user_preferences']['shell'] = shell
                    break
        
        # System characteristics
        learning['system_characteristics'] = {
            'package_count': len(config.packages),
            'service_count': len([s for s in config.services.values() if s.get('enabled')]),
            'user_count': len(config.users),
            'uses_flakes': any('flake' in imp.path.lower() for imp in config.imports),
            'uses_home_manager': any('home-manager' in imp.path.lower() for imp in config.imports)
        }
        
        return learning


# Convenience function
def get_config_executor() -> ConfigExecutor:
    """Get or create the configuration executor"""
    return ConfigExecutor()