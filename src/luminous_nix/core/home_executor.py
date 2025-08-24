#!/usr/bin/env python3
"""
Home Manager Executor - Integrates Home Manager with the core system

This module provides the execution layer for Home Manager operations,
connecting the HomeManager with the core intent processing system.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .home_manager import HomeManager, HomeConfig


@dataclass
class HomeResult:
    """Result for home manager operations"""
    success: bool
    message: str
    error: Optional[str] = None
    command: Optional[str] = None
    explanation: Optional[str] = None
    config_path: Optional[Path] = None
    dotfiles: List[str] = None
    themes: List[str] = None
    actions: List[str] = None


class HomeExecutor:
    """Execute Home Manager related operations with full integration"""
    
    def __init__(self):
        self.manager = HomeManager()
    
    def execute(self, intent_type: str, query: str, entities: Dict[str, Any]) -> HomeResult:
        """
        Execute a Home Manager operation based on intent
        
        Args:
            intent_type: Type of home operation
            query: Original user query
            entities: Extracted entities from intent recognition
            
        Returns:
            HomeResult with operation outcome
        """
        try:
            query_lower = query.lower()
            
            # Determine specific operation
            if "init" in query_lower or "setup" in query_lower or "configure" in query_lower:
                return self._init_home_config(query, entities)
            elif "theme" in query_lower or "color" in query_lower:
                return self._apply_theme(query, entities)
            elif "add" in query_lower or "manage" in query_lower:
                return self._add_dotfile(query, entities)
            elif "sync" in query_lower:
                return self._sync_configs(query, entities)
            elif "backup" in query_lower:
                return self._backup_configs(query, entities)
            elif "list" in query_lower or "show" in query_lower:
                return self._list_configs()
            else:
                # Default to init with the query as description
                return self._init_home_config(query, entities)
                
        except Exception as e:
            return HomeResult(
                success=False,
                message=f"Home Manager operation failed: {str(e)}",
                error=str(e)
            )
    
    def _init_home_config(self, query: str, entities: Dict[str, Any]) -> HomeResult:
        """Initialize home configuration from natural language"""
        # Use the query as the description for natural language parsing
        config = self.manager.init_home_config(query)
        
        # Generate home.nix
        home_nix = self.manager.generate_home_nix(config)
        
        # Apply the configuration (preview by default)
        result = self.manager.apply_config(config, preview=True)
        
        return HomeResult(
            success=True,
            message=f"Home configuration initialized for {config.username}",
            config_path=Path.home() / ".config" / "nixpkgs" / "home.nix",
            dotfiles=[d.name for d in config.dotfiles],
            themes=[t.name for t in config.themes],
            actions=result.get("actions", []),
            command="home-manager switch",
            explanation=self._generate_explanation(config)
        )
    
    def _apply_theme(self, query: str, entities: Dict[str, Any]) -> HomeResult:
        """Apply a theme to applications"""
        # Extract theme name from query
        theme_name = None
        for theme in ["dracula", "nord", "solarized-dark", "gruvbox"]:
            if theme in query.lower():
                theme_name = theme
                break
        
        if not theme_name:
            # Try to get from entities
            theme_name = entities.get('theme', 'dracula')
        
        # Extract applications
        applications = []
        if "terminal" in query.lower():
            applications.append("terminal")
        if "vim" in query.lower() or "neovim" in query.lower():
            applications.append("vim")
        if "desktop" in query.lower():
            applications.append("desktop")
        
        if not applications:
            applications = ["terminal"]  # Default
        
        result = self.manager.apply_theme(theme_name, applications)
        
        if result["success"]:
            return HomeResult(
                success=True,
                message=f"Applied {theme_name} theme to {', '.join(applications)}",
                themes=[theme_name],
                actions=result.get("changes", []),
                command="home-manager switch"
            )
        else:
            return HomeResult(
                success=False,
                message=result.get("error", "Failed to apply theme"),
                error=result.get("error")
            )
    
    def _add_dotfile(self, query: str, entities: Dict[str, Any]) -> HomeResult:
        """Add a dotfile to managed configuration"""
        # Extract dotfile type from query
        dotfile_types = ["vim", "neovim", "tmux", "git", "bash", "zsh", "fish", "alacritty", "kitty"]
        dotfiles_to_add = []
        
        for dtype in dotfile_types:
            if dtype in query.lower():
                dotfiles_to_add.append(dtype)
        
        if not dotfiles_to_add:
            # Try entities
            target = entities.get('target', '')
            for dtype in dotfile_types:
                if dtype in target:
                    dotfiles_to_add.append(dtype)
        
        if not dotfiles_to_add:
            return HomeResult(
                success=False,
                message="Could not determine which dotfile to add",
                error="Please specify: vim, tmux, git, bash, zsh, fish, alacritty, or kitty"
            )
        
        # Create config and add dotfiles
        config = HomeConfig(
            username=Path.home().name,
            dotfiles=[],
            themes=[],
            shell_config={},
            packages=[],
            services={}
        )
        
        for dotfile in dotfiles_to_add:
            self.manager._add_dotfile_to_config(config, dotfile)
        
        # Backup existing
        backups = self.manager.backup_existing_configs(config)
        
        return HomeResult(
            success=True,
            message=f"Added {', '.join(dotfiles_to_add)} to managed configuration",
            dotfiles=dotfiles_to_add,
            actions=[f"Backed up to {b}" for b in backups],
            command="home-manager switch",
            explanation=f"Run 'home-manager switch' to apply the new configuration"
        )
    
    def _sync_configs(self, query: str, entities: Dict[str, Any]) -> HomeResult:
        """Sync configurations between machines"""
        # Extract machine names
        words = query.lower().split()
        source = None
        target = None
        
        # Look for patterns like "from X to Y"
        if "from" in words:
            idx = words.index("from")
            if idx + 1 < len(words):
                source = words[idx + 1]
        
        if "to" in words:
            idx = words.index("to")
            if idx + 1 < len(words):
                target = words[idx + 1]
        
        if not source or not target:
            # Try common patterns
            if "laptop" in query.lower() and "desktop" in query.lower():
                source = "laptop"
                target = "desktop"
            else:
                return HomeResult(
                    success=False,
                    message="Could not determine source and target machines",
                    error="Please specify: sync from [source] to [target]"
                )
        
        result = self.manager.sync_configs(source, target)
        
        return HomeResult(
            success=result["success"],
            message=result["message"],
            explanation="Configuration sync initiated between machines"
        )
    
    def _backup_configs(self, query: str, entities: Dict[str, Any]) -> HomeResult:
        """Backup current configurations"""
        # Create a config with all current dotfiles
        config = self.manager.init_home_config("all current configurations")
        
        # Perform backup
        backups = self.manager.backup_existing_configs(config)
        
        if backups:
            return HomeResult(
                success=True,
                message=f"Created {len(backups)} backups",
                actions=[str(b) for b in backups],
                explanation="Your configurations have been safely backed up"
            )
        else:
            return HomeResult(
                success=True,
                message="No configurations found to backup",
                explanation="No existing dotfiles were found that needed backing up"
            )
    
    def _list_configs(self) -> HomeResult:
        """List managed configurations"""
        managed = self.manager.list_managed_configs()
        
        return HomeResult(
            success=True,
            message="Current Home Manager status",
            dotfiles=managed.get("dotfiles", []),
            themes=managed.get("themes", []),
            actions=managed.get("backups", [])[:5],  # Last 5 backups
            explanation="Use 'ask-nix home init' to set up new configurations"
        )
    
    def _generate_explanation(self, config: HomeConfig) -> str:
        """Generate a human-friendly explanation of what was configured"""
        parts = []
        
        if config.dotfiles:
            dotfile_names = [d.name for d in config.dotfiles]
            parts.append(f"Managing dotfiles for: {', '.join(dotfile_names)}")
        
        if config.themes:
            theme_names = [t.name for t in config.themes]
            parts.append(f"Applied themes: {', '.join(theme_names)}")
        
        if config.shell_config.get("shell") != "bash":
            parts.append(f"Using {config.shell_config['shell']} shell")
        
        if config.packages:
            parts.append(f"Including {len(config.packages)} packages")
        
        return ' | '.join(parts) if parts else "Basic home configuration created"
    
    def check_home_manager_installed(self) -> bool:
        """Check if Home Manager is installed"""
        try:
            import subprocess
            result = subprocess.run(
                ["home-manager", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False