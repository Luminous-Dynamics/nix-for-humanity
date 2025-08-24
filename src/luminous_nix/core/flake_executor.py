#!/usr/bin/env python3
"""
Flake Executor - Integrates flake management with the core system

This module provides the execution layer for flake operations,
connecting the FlakeManager with the core intent processing system.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from .flake_manager import FlakeManager


@dataclass
class FlakeResult:
    """Result for flake operations"""
    success: bool
    message: str
    error: Optional[str] = None
    command: Optional[str] = None
    explanation: Optional[str] = None
    flake_path: Optional[Path] = None
    dev_shells: List[str] = None
    packages: List[str] = None
    inputs: List[str] = None


class FlakeExecutor:
    """Execute flake-related operations with full integration"""
    
    def __init__(self):
        self.manager = FlakeManager()
        self.cache_dir = Path.home() / ".cache" / "luminous-nix" / "flakes"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, intent_type: str, query: str, entities: Dict[str, Any]) -> FlakeResult:
        """
        Execute a flake operation based on intent
        
        Args:
            intent_type: Type of flake operation
            query: Original user query
            entities: Extracted entities from intent recognition
            
        Returns:
            FlakeResult with operation outcome
        """
        try:
            # Map intent types to operations
            if intent_type == "flake" or "create flake" in query.lower():
                return self._create_flake(query, entities)
            elif intent_type == "develop" or "dev environment" in query.lower():
                return self._create_dev_environment(query, entities)
            elif "validate" in query.lower():
                return self._validate_flake(entities.get('path', '.'))
            elif "convert" in query.lower():
                return self._convert_to_flake(entities.get('path', '.'))
            else:
                return self._show_flake_info(entities.get('path', '.'))
                
        except Exception as e:
            return FlakeResult(
                success=False,
                message=f"Flake operation failed: {str(e)}",
                error=str(e)
            )
    
    def _create_flake(self, query: str, entities: Dict[str, Any]) -> FlakeResult:
        """Create a new flake.nix file"""
        # Parse the intent from the query
        intent = self.manager.parse_intent(query)
        
        # Add any specific entities
        if 'language' in entities:
            intent['language'] = entities['language']
        if 'packages' in entities:
            intent['packages'].extend(entities.get('packages', []))
        
        # Get the target path
        path = Path(entities.get('path', '.'))
        
        # Create the flake
        success, message = self.manager.create_flake(intent, path)
        
        if success:
            # Load flake info for the result
            flake_info = self._get_flake_details(path)
            
            return FlakeResult(
                success=True,
                message=message,
                flake_path=path / "flake.nix",
                dev_shells=flake_info.get('dev_shells', []),
                packages=flake_info.get('packages', []),
                inputs=flake_info.get('inputs', []),
                command=f"cd {path} && nix develop",
                explanation=self._generate_explanation(intent)
            )
        else:
            return FlakeResult(
                success=False,
                message=message,
                error=message
            )
    
    def _create_dev_environment(self, query: str, entities: Dict[str, Any]) -> FlakeResult:
        """Create a development environment (similar to flake but focused on dev shell)"""
        # Parse intent with dev environment focus
        intent = self.manager.parse_intent(query)
        intent['focus'] = 'devShell'  # Prioritize dev shell output
        
        return self._create_flake(query, entities)
    
    def _validate_flake(self, path: str) -> FlakeResult:
        """Validate an existing flake"""
        success, message = self.manager.validate_flake(Path(path))
        
        return FlakeResult(
            success=success,
            message=message,
            flake_path=Path(path) / "flake.nix" if success else None,
            command=f"nix flake check {path}" if success else None
        )
    
    def _convert_to_flake(self, path: str) -> FlakeResult:
        """Convert shell.nix or default.nix to flake"""
        success, message = self.manager.convert_to_flake(Path(path))
        
        return FlakeResult(
            success=success,
            message=message,
            flake_path=Path(path) / "flake.nix" if success else None,
            command=f"nix develop {path}" if success else None
        )
    
    def _show_flake_info(self, path: str) -> FlakeResult:
        """Show information about a flake"""
        info_text = self.manager.show_flake_info(Path(path))
        flake_info = self._get_flake_details(Path(path))
        
        return FlakeResult(
            success=True,
            message=info_text,
            flake_path=Path(path) / "flake.nix",
            dev_shells=flake_info.get('dev_shells', []),
            packages=flake_info.get('packages', []),
            inputs=flake_info.get('inputs', [])
        )
    
    def _get_flake_details(self, path: Path) -> Dict[str, Any]:
        """Extract details from a flake for the result"""
        flake_path = path / "flake.nix"
        if not flake_path.exists():
            return {}
        
        # For now, return basic info
        # Full implementation would parse the flake properly
        return {
            'dev_shells': ['default'],
            'packages': [],
            'inputs': ['nixpkgs', 'flake-utils']
        }
    
    def _generate_explanation(self, intent: Dict[str, Any]) -> str:
        """Generate a human-friendly explanation of what was created"""
        parts = []
        
        if intent.get('language'):
            parts.append(f"Created {intent['language']} development environment")
        else:
            parts.append("Created development environment")
        
        if intent.get('packages'):
            parts.append(f"with {', '.join(intent['packages'])}")
        
        if intent.get('features'):
            parts.append(f"including {', '.join(intent['features'])} support")
        
        return ' '.join(parts)
    
    def check_flake_support(self) -> bool:
        """Check if the system supports flakes"""
        try:
            import subprocess
            result = subprocess.run(
                ["nix", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Check if experimental features are enabled
            config_result = subprocess.run(
                ["nix", "show-config"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return "experimental-features" in config_result.stdout and "flakes" in config_result.stdout
            
        except Exception:
            return False