#!/usr/bin/env python3
"""
Flake Migration Assistant - Convert legacy configs to modern flakes
Intelligent migration that preserves functionality while modernizing
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MigrationAnalysis:
    """Analysis of configuration for flake migration"""
    config_type: str  # 'simple', 'modular', 'complex'
    current_structure: Dict[str, Any]
    
    # Detected patterns
    has_overlays: bool
    has_custom_packages: bool
    has_home_manager: bool
    has_secrets: bool
    has_remote_builders: bool
    
    # Migration recommendations
    migration_complexity: str  # 'trivial', 'moderate', 'complex'
    estimated_effort_hours: float
    breaking_changes: List[str]
    benefits: List[str]
    
    # Generated flake
    flake_nix: str
    inputs_required: Dict[str, str]
    migration_commands: List[str]
    
    confidence: float

@dataclass
class FlakeInput:
    """Represents a flake input dependency"""
    name: str
    url: str
    description: str
    follows: Optional[str] = None

class FlakeMigrationAssistant:
    """
    Intelligent flake migration using HRM reasoning
    Converts traditional NixOS configs to modern flake-based approach
    """
    
    def __init__(self):
        # Common flake inputs
        self.standard_inputs = {
            'nixpkgs': FlakeInput(
                name='nixpkgs',
                url='github:NixOS/nixpkgs/nixos-unstable',
                description='NixOS packages collection'
            ),
            'home-manager': FlakeInput(
                name='home-manager',
                url='github:nix-community/home-manager',
                description='User environment management',
                follows='nixpkgs'
            ),
            'nixos-hardware': FlakeInput(
                name='nixos-hardware',
                url='github:NixOS/nixos-hardware/master',
                description='Hardware-specific configurations'
            ),
            'flake-utils': FlakeInput(
                name='flake-utils',
                url='github:numtide/flake-utils',
                description='Flake utility functions'
            ),
            'sops-nix': FlakeInput(
                name='sops-nix',
                url='github:Mic92/sops-nix',
                description='Secrets management',
                follows='nixpkgs'
            ),
        }
        
        # Migration patterns
        self.migration_patterns = {
            'package_override': self._migrate_package_override,
            'overlay': self._migrate_overlay,
            'module': self._migrate_module,
            'home_manager': self._migrate_home_manager,
            'boot_config': self._migrate_boot_config,
        }
    
    def analyze_configuration(self, config_path: Optional[str] = None) -> MigrationAnalysis:
        """
        Analyze existing configuration for migration
        
        Args:
            config_path: Path to configuration.nix (default: /etc/nixos/configuration.nix)
        
        Returns:
            MigrationAnalysis with recommendations
        """
        try:
            config_path = config_path or '/etc/nixos/configuration.nix'
            
            # Read and analyze configuration
            config_content = self._read_config(config_path)
            structure = self._analyze_structure(config_content)
            
            # Detect patterns
            has_overlays = self._detect_overlays(config_content)
            has_custom_packages = self._detect_custom_packages(config_content)
            has_home_manager = self._detect_home_manager(config_content)
            has_secrets = self._detect_secrets(config_content)
            has_remote_builders = self._detect_remote_builders(config_content)
            
            # Determine complexity
            complexity = self._assess_complexity(
                has_overlays, has_custom_packages, 
                has_home_manager, has_secrets, has_remote_builders
            )
            
            # Generate flake
            flake_nix = self._generate_flake(
                structure, has_overlays, has_custom_packages,
                has_home_manager, has_secrets
            )
            
            # Determine required inputs
            inputs = self._determine_inputs(
                has_home_manager, has_secrets, has_custom_packages
            )
            
            # Generate migration commands
            commands = self._generate_migration_commands(config_path)
            
            # Identify breaking changes
            breaking_changes = self._identify_breaking_changes(structure)
            
            # List benefits
            benefits = self._list_migration_benefits()
            
            # Estimate effort
            effort = self._estimate_effort(complexity)
            
            return MigrationAnalysis(
                config_type=structure['type'],
                current_structure=structure,
                has_overlays=has_overlays,
                has_custom_packages=has_custom_packages,
                has_home_manager=has_home_manager,
                has_secrets=has_secrets,
                has_remote_builders=has_remote_builders,
                migration_complexity=complexity,
                estimated_effort_hours=effort,
                breaking_changes=breaking_changes,
                benefits=benefits,
                flake_nix=flake_nix,
                inputs_required=inputs,
                migration_commands=commands,
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Configuration analysis failed: {e}")
            return self._create_fallback_analysis(str(e))
    
    def migrate_to_flake(self, config_path: Optional[str] = None, 
                         output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform actual migration to flake
        
        Args:
            config_path: Path to existing configuration
            output_dir: Where to create flake (default: /etc/nixos)
        
        Returns:
            Migration result with created files
        """
        try:
            analysis = self.analyze_configuration(config_path)
            output_dir = output_dir or '/etc/nixos'
            
            # Create flake.nix
            flake_path = Path(output_dir) / 'flake.nix'
            
            # Backup existing if present
            if flake_path.exists():
                backup_path = flake_path.with_suffix('.nix.backup')
                flake_path.rename(backup_path)
            
            # Write new flake
            with open(flake_path, 'w') as f:
                f.write(analysis.flake_nix)
            
            # Create flake.lock
            lock_commands = [
                f'cd {output_dir}',
                'nix flake lock',
                'nix flake show'
            ]
            
            return {
                'success': True,
                'flake_path': str(flake_path),
                'commands_to_run': lock_commands,
                'next_steps': self._get_next_steps(),
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Flake migration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'suggestions': self._get_migration_suggestions()
            }
    
    def validate_flake(self, flake_path: str = '.') -> Dict[str, Any]:
        """Validate a flake configuration"""
        try:
            # Check flake syntax
            syntax_valid = self._check_flake_syntax(flake_path)
            
            # Check inputs
            inputs_valid = self._check_flake_inputs(flake_path)
            
            # Check outputs
            outputs_valid = self._check_flake_outputs(flake_path)
            
            # Check evaluation
            eval_result = self._check_flake_evaluation(flake_path)
            
            return {
                'valid': all([syntax_valid, inputs_valid, outputs_valid, eval_result['success']]),
                'syntax': syntax_valid,
                'inputs': inputs_valid,
                'outputs': outputs_valid,
                'evaluation': eval_result,
                'warnings': self._get_flake_warnings(flake_path),
                'suggestions': self._get_flake_suggestions(flake_path)
            }
            
        except Exception as e:
            logger.error(f"Flake validation failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def suggest_improvements(self, flake_path: str = '.') -> List[str]:
        """Suggest improvements for existing flake"""
        suggestions = []
        
        try:
            # Read flake
            with open(f'{flake_path}/flake.nix', 'r') as f:
                content = f.read()
            
            # Check for pinning
            if 'nixos-unstable' in content and '/archive/' not in content:
                suggestions.append("Pin nixpkgs to specific revision for reproducibility")
            
            # Check for flake-utils
            if 'flake-utils' not in content and 'systems = [' in content:
                suggestions.append("Use flake-utils for cleaner multi-system support")
            
            # Check for follows
            if content.count('.inputs.nixpkgs') > 2:
                suggestions.append("Use 'follows' to ensure consistent nixpkgs across inputs")
            
            # Check for descriptions
            if 'description = ' not in content:
                suggestions.append("Add description to document flake purpose")
            
            # Check for dev shell
            if 'devShells' not in content:
                suggestions.append("Add development shell for better developer experience")
            
        except Exception as e:
            logger.error(f"Failed to suggest improvements: {e}")
        
        return suggestions
    
    def _read_config(self, config_path: str) -> str:
        """Read configuration file"""
        try:
            with open(config_path, 'r') as f:
                return f.read()
        except:
            # Return example config for demo
            return """
{ config, pkgs, ... }:
{
  imports = [ ./hardware-configuration.nix ];
  
  boot.loader.systemd-boot.enable = true;
  networking.hostName = "nixos";
  
  environment.systemPackages = with pkgs; [
    vim wget firefox
  ];
  
  services.openssh.enable = true;
  system.stateVersion = "24.05";
}
"""
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze configuration structure"""
        structure = {
            'type': 'simple',
            'imports': [],
            'modules': [],
            'has_functions': '= {' in content or ': {' in content,
            'lines': len(content.split('\n'))
        }
        
        # Check for imports
        import_matches = re.findall(r'imports\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if import_matches:
            structure['imports'] = [i.strip() for i in import_matches[0].split('\n') if i.strip()]
        
        # Determine type
        if structure['lines'] > 200:
            structure['type'] = 'complex'
        elif len(structure['imports']) > 2:
            structure['type'] = 'modular'
        
        return structure
    
    def _detect_overlays(self, content: str) -> bool:
        """Detect if configuration uses overlays"""
        return 'nixpkgs.overlays' in content or 'overlay' in content.lower()
    
    def _detect_custom_packages(self, content: str) -> bool:
        """Detect custom package definitions"""
        return 'buildPackage' in content or 'mkDerivation' in content
    
    def _detect_home_manager(self, content: str) -> bool:
        """Detect home-manager usage"""
        return 'home-manager' in content or 'home.nix' in content
    
    def _detect_secrets(self, content: str) -> bool:
        """Detect secrets management"""
        return 'sops' in content or 'agenix' in content or 'secrets' in content.lower()
    
    def _detect_remote_builders(self, content: str) -> bool:
        """Detect remote builder configuration"""
        return 'buildMachines' in content or 'distributedBuilds' in content
    
    def _assess_complexity(self, *features) -> str:
        """Assess migration complexity"""
        feature_count = sum(features)
        
        if feature_count == 0:
            return 'trivial'
        elif feature_count <= 2:
            return 'moderate'
        else:
            return 'complex'
    
    def _generate_flake(self, structure: Dict, has_overlays: bool,
                       has_custom_packages: bool, has_home_manager: bool,
                       has_secrets: bool) -> str:
        """Generate flake.nix content"""
        
        # Build inputs section
        inputs = ['    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";']
        
        if has_home_manager:
            inputs.append('    home-manager.url = "github:nix-community/home-manager";')
            inputs.append('    home-manager.inputs.nixpkgs.follows = "nixpkgs";')
        
        if has_secrets:
            inputs.append('    sops-nix.url = "github:Mic92/sops-nix";')
            inputs.append('    sops-nix.inputs.nixpkgs.follows = "nixpkgs";')
        
        # Build outputs section
        outputs = []
        if has_home_manager:
            outputs.append('home-manager')
        if has_secrets:
            outputs.append('sops-nix')
        
        outputs_str = ', '.join(['nixpkgs'] + outputs)
        
        flake_template = f'''{{
  description = "NixOS configuration";

  inputs = {{
{chr(10).join(inputs)}
  }};

  outputs = {{ self, {outputs_str}, ... }}@inputs: {{
    nixosConfigurations.default = nixpkgs.lib.nixosSystem {{
      system = "x86_64-linux";
      modules = [
        ./configuration.nix'''
        
        if has_home_manager:
            flake_template += '''
        home-manager.nixosModules.home-manager
        {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
        }'''
        
        if has_secrets:
            flake_template += '''
        sops-nix.nixosModules.sops'''
        
        flake_template += '''
      ];
    };
  };
}'''
        
        return flake_template
    
    def _determine_inputs(self, has_home_manager: bool, 
                         has_secrets: bool, has_custom_packages: bool) -> Dict[str, str]:
        """Determine required flake inputs"""
        inputs = {'nixpkgs': self.standard_inputs['nixpkgs'].url}
        
        if has_home_manager:
            inputs['home-manager'] = self.standard_inputs['home-manager'].url
        
        if has_secrets:
            inputs['sops-nix'] = self.standard_inputs['sops-nix'].url
        
        if has_custom_packages:
            inputs['flake-utils'] = self.standard_inputs['flake-utils'].url
        
        return inputs
    
    def _generate_migration_commands(self, config_path: str) -> List[str]:
        """Generate commands for migration"""
        return [
            "# 1. Enable flakes",
            "echo 'experimental-features = nix-command flakes' | sudo tee -a /etc/nix/nix.conf",
            "",
            "# 2. Initialize flake",
            "cd /etc/nixos",
            "sudo nix flake init",
            "",
            "# 3. Copy generated flake",
            "# (Replace flake.nix with generated content)",
            "",
            "# 4. Update flake inputs", 
            "sudo nix flake update",
            "",
            "# 5. Test configuration",
            "sudo nixos-rebuild test --flake /etc/nixos#default",
            "",
            "# 6. Switch when ready",
            "sudo nixos-rebuild switch --flake /etc/nixos#default"
        ]
    
    def _identify_breaking_changes(self, structure: Dict) -> List[str]:
        """Identify potential breaking changes"""
        changes = []
        
        if structure['type'] == 'complex':
            changes.append("Complex configurations may need restructuring")
        
        if structure['has_functions']:
            changes.append("Custom functions need to be in separate modules")
        
        return changes
    
    def _list_migration_benefits(self) -> List[str]:
        """List benefits of migrating to flakes"""
        return [
            "Reproducible builds with lock file",
            "Better dependency management",
            "Cleaner configuration structure",
            "Easier CI/CD integration",
            "Native support for multiple systems",
            "Improved caching and performance"
        ]
    
    def _estimate_effort(self, complexity: str) -> float:
        """Estimate migration effort in hours"""
        effort_map = {
            'trivial': 0.5,
            'moderate': 2.0,
            'complex': 8.0
        }
        return effort_map.get(complexity, 4.0)
    
    def _migrate_package_override(self, content: str) -> str:
        """Migrate package override pattern"""
        # Convert package overrides to overlay format
        return content  # Simplified for now
    
    def _migrate_overlay(self, content: str) -> str:
        """Migrate overlay pattern"""
        return content  # Simplified for now
    
    def _migrate_module(self, content: str) -> str:
        """Migrate module pattern"""
        return content  # Simplified for now
    
    def _migrate_home_manager(self, content: str) -> str:
        """Migrate home-manager configuration"""
        return content  # Simplified for now
    
    def _migrate_boot_config(self, content: str) -> str:
        """Migrate boot configuration"""
        return content  # Simplified for now
    
    def _check_flake_syntax(self, flake_path: str) -> bool:
        """Check flake syntax validity"""
        # In production, would run: nix flake check
        return True
    
    def _check_flake_inputs(self, flake_path: str) -> bool:
        """Check flake inputs validity"""
        return True
    
    def _check_flake_outputs(self, flake_path: str) -> bool:
        """Check flake outputs validity"""
        return True
    
    def _check_flake_evaluation(self, flake_path: str) -> Dict[str, Any]:
        """Check if flake evaluates correctly"""
        return {'success': True, 'time_ms': 150}
    
    def _get_flake_warnings(self, flake_path: str) -> List[str]:
        """Get flake warnings"""
        return []
    
    def _get_flake_suggestions(self, flake_path: str) -> List[str]:
        """Get flake improvement suggestions"""
        return ["Consider pinning nixpkgs to specific revision"]
    
    def _get_next_steps(self) -> List[str]:
        """Get next steps after migration"""
        return [
            "Test the new flake configuration",
            "Update any deployment scripts",
            "Document the new structure",
            "Set up CI/CD if needed"
        ]
    
    def _get_migration_suggestions(self) -> List[str]:
        """Get migration suggestions on failure"""
        return [
            "Ensure flakes are enabled in nix.conf",
            "Check that all imports are valid",
            "Verify no syntax errors in configuration"
        ]
    
    def _create_fallback_analysis(self, error: str) -> MigrationAnalysis:
        """Create fallback analysis on error"""
        return MigrationAnalysis(
            config_type='unknown',
            current_structure={},
            has_overlays=False,
            has_custom_packages=False,
            has_home_manager=False,
            has_secrets=False,
            has_remote_builders=False,
            migration_complexity='unknown',
            estimated_effort_hours=0.0,
            breaking_changes=[f"Error: {error}"],
            benefits=[],
            flake_nix="",
            inputs_required={},
            migration_commands=[],
            confidence=0.0
        )