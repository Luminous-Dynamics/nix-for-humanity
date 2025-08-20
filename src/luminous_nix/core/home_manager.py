#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Home Manager Integration for Nix for Humanity

Provides natural language management of personal configurations:
- Dotfiles (vim, tmux, git, shell)
- Desktop themes and appearance
- Application settings
- Cross-machine synchronization
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import subprocess


@dataclass
class DotfileConfig:
    """Configuration for a dotfile"""
    name: str
    source_path: Path
    target_path: Path
    description: str
    backup_path: Optional[Path] = None
    

@dataclass
class ThemeConfig:
    """Theme configuration"""
    name: str
    type: str  # terminal, desktop, application
    settings: Dict[str, Any]
    

@dataclass
class HomeConfig:
    """Complete home configuration"""
    username: str
    dotfiles: List[DotfileConfig]
    themes: List[ThemeConfig]
    shell_config: Dict[str, Any]
    packages: List[str]
    services: Dict[str, Any]


class HomeManager:
    """Manages home configurations with natural language understanding"""
    
    def __init__(self, home_dir: Optional[Path] = None):
        self.home_dir = home_dir or Path.home()
        self.config_dir = self.home_dir / ".config" / "nix-humanity"
        self.backup_dir = self.config_dir / "backups"
        self.templates_dir = Path(__file__).parent.parent / "templates" / "home"
        
        # Create directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Common dotfile mappings
        self.dotfile_mappings = {
            "vim": {
                "config": ".vimrc",
                "dir": ".vim",
                "description": "Vim editor configuration"
            },
            "neovim": {
                "config": ".config/nvim/init.vim",
                "lua_config": ".config/nvim/init.lua",
                "dir": ".config/nvim",
                "description": "Neovim editor configuration"
            },
            "tmux": {
                "config": ".tmux.conf",
                "description": "Terminal multiplexer configuration"
            },
            "git": {
                "config": ".gitconfig",
                "ignore": ".gitignore_global",
                "description": "Git version control configuration"
            },
            "bash": {
                "config": ".bashrc",
                "profile": ".bash_profile",
                "aliases": ".bash_aliases",
                "description": "Bash shell configuration"
            },
            "zsh": {
                "config": ".zshrc",
                "profile": ".zprofile",
                "description": "Zsh shell configuration"
            },
            "fish": {
                "config": ".config/fish/config.fish",
                "dir": ".config/fish",
                "description": "Fish shell configuration"
            },
            "alacritty": {
                "config": ".config/alacritty/alacritty.yml",
                "description": "Alacritty terminal emulator"
            },
            "kitty": {
                "config": ".config/kitty/kitty.conf",
                "description": "Kitty terminal emulator"
            }
        }
        
        # Common themes
        self.themes = {
            "dracula": {
                "type": "dark",
                "colors": {
                    "background": "#282a36",
                    "foreground": "#f8f8f2",
                    "black": "#000000",
                    "red": "#ff5555",
                    "green": "#50fa7b",
                    "yellow": "#f1fa8c",
                    "blue": "#6272a4",
                    "magenta": "#ff79c6",
                    "cyan": "#8be9fd",
                    "white": "#bfbfbf"
                }
            },
            "nord": {
                "type": "dark",
                "colors": {
                    "background": "#2e3440",
                    "foreground": "#d8dee9",
                    "black": "#3b4252",
                    "red": "#bf616a",
                    "green": "#a3be8c",
                    "yellow": "#ebcb8b",
                    "blue": "#81a1c1",
                    "magenta": "#b48ead",
                    "cyan": "#88c0d0",
                    "white": "#e5e9f0"
                }
            },
            "solarized-dark": {
                "type": "dark",
                "colors": {
                    "background": "#002b36",
                    "foreground": "#839496",
                    "black": "#073642",
                    "red": "#dc322f",
                    "green": "#859900",
                    "yellow": "#b58900",
                    "blue": "#268bd2",
                    "magenta": "#d33682",
                    "cyan": "#2aa198",
                    "white": "#eee8d5"
                }
            },
            "gruvbox": {
                "type": "dark",
                "colors": {
                    "background": "#282828",
                    "foreground": "#ebdbb2",
                    "black": "#282828",
                    "red": "#cc241d",
                    "green": "#98971a",
                    "yellow": "#d79921",
                    "blue": "#458588",
                    "magenta": "#b16286",
                    "cyan": "#689d6a",
                    "white": "#a89984"
                }
            }
        }
    
    def init_home_config(self, description: str = "") -> HomeConfig:
        """Initialize a new home configuration from natural language"""
        # Parse description for hints
        desc_lower = description.lower()
        
        # Detect requested tools
        dotfiles = []
        if any(word in desc_lower for word in ["vim", "neovim", "editor"]):
            dotfiles.append("vim")
        if "tmux" in desc_lower or "terminal multiplexer" in desc_lower:
            dotfiles.append("tmux")
        if "git" in desc_lower or "version control" in desc_lower:
            dotfiles.append("git")
            
        # Detect shell preference
        shell = "bash"  # default
        if "zsh" in desc_lower:
            shell = "zsh"
        elif "fish" in desc_lower:
            shell = "fish"
            
        # Detect theme preference
        theme = None
        for theme_name in self.themes:
            if theme_name in desc_lower:
                theme = theme_name
                break
        if not theme and "dark" in desc_lower:
            theme = "dracula"  # default dark theme
            
        # Create initial config
        config = HomeConfig(
            username=os.environ.get("USER", "user"),
            dotfiles=[],
            themes=[],
            shell_config={"shell": shell},
            packages=[],
            services={}
        )
        
        # Add requested dotfiles
        for dotfile in dotfiles:
            self._add_dotfile_to_config(config, dotfile)
            
        # Add theme if requested
        if theme:
            self._add_theme_to_config(config, theme, ["terminal"])
            
        return config
    
    def _add_dotfile_to_config(self, config: HomeConfig, dotfile_name: str):
        """Add a dotfile configuration"""
        if dotfile_name in self.dotfile_mappings:
            mapping = self.dotfile_mappings[dotfile_name]
            
            # Add main config file
            if "config" in mapping:
                config_path = Path(mapping["config"])
                dotfile = DotfileConfig(
                    name=f"{dotfile_name}_config",
                    source_path=self.home_dir / config_path,
                    target_path=config_path,
                    description=mapping["description"]
                )
                config.dotfiles.append(dotfile)
                
            # Add additional files
            for key in ["dir", "ignore", "profile", "aliases", "lua_config"]:
                if key in mapping:
                    path = Path(mapping[key])
                    dotfile = DotfileConfig(
                        name=f"{dotfile_name}_{key}",
                        source_path=self.home_dir / path,
                        target_path=path,
                        description=f"{mapping['description']} - {key}"
                    )
                    config.dotfiles.append(dotfile)
    
    def _add_theme_to_config(self, config: HomeConfig, theme_name: str, 
                            applications: List[str]):
        """Add a theme configuration"""
        if theme_name in self.themes:
            theme_data = self.themes[theme_name]
            
            for app in applications:
                theme = ThemeConfig(
                    name=f"{theme_name}_{app}",
                    type=app,
                    settings=theme_data
                )
                config.themes.append(theme)
    
    def backup_existing_configs(self, config: HomeConfig) -> List[Path]:
        """Backup existing configuration files"""
        backups = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / timestamp
        backup_subdir.mkdir(exist_ok=True)
        
        for dotfile in config.dotfiles:
            source = self.home_dir / dotfile.target_path
            if source.exists():
                backup_path = backup_subdir / dotfile.target_path.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                if source.is_file():
                    shutil.copy2(source, backup_path)
                else:
                    shutil.copytree(source, backup_path)
                    
                dotfile.backup_path = backup_path
                backups.append(backup_path)
                
        return backups
    
    def generate_home_nix(self, config: HomeConfig) -> str:
        """Generate home.nix configuration"""
        # Template for home.nix
        template = '''{{ config, pkgs, ... }}:

{{
  # Home Manager needs a bit of information about you and the
  # paths it should manage.
  home.username = "{username}";
  home.homeDirectory = "/home/{username}";

  # This value determines the Home Manager release that your
  # configuration is compatible with.
  home.stateVersion = "23.11";

  # Packages to install
  home.packages = with pkgs; [
{packages}
  ];

  # Program configurations
{programs}

  # File management
  home.file = {{
{files}
  }};

  # Session variables
  home.sessionVariables = {{
{session_vars}
  }};

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;
}}
'''
        
        # Build package list
        packages = []
        # Add packages based on dotfiles
        for dotfile in config.dotfiles:
            if "vim" in dotfile.name:
                packages.append("vim")
            elif "neovim" in dotfile.name:
                packages.append("neovim")
            elif "tmux" in dotfile.name:
                packages.append("tmux")
            elif "git" in dotfile.name:
                packages.append("git")
                
        # Add shell if not bash
        if config.shell_config.get("shell") == "zsh":
            packages.append("zsh")
        elif config.shell_config.get("shell") == "fish":
            packages.append("fish")
            
        # Add user packages
        packages.extend(config.packages)
        
        # Format packages
        package_lines = [f"    {pkg}" for pkg in packages]
        
        # Build program configurations
        programs = []
        
        # Git configuration
        if any("git" in d.name for d in config.dotfiles):
            programs.append('''  programs.git = {
    enable = true;
    userName = "Your Name";
    userEmail = "your.email@example.com";
  };''')
            
        # Shell configuration
        shell = config.shell_config.get("shell", "bash")
        if shell == "zsh":
            programs.append('''  programs.zsh = {
    enable = true;
    enableCompletion = true;
    enableAutosuggestions = true;
    syntaxHighlighting.enable = true;
  };''')
        elif shell == "fish":
            programs.append('''  programs.fish = {
    enable = true;
  };''')
        else:
            programs.append('''  programs.bash = {
    enable = true;
    enableCompletion = true;
  };''')
            
        # File declarations
        files = []
        for dotfile in config.dotfiles:
            if dotfile.source_path.exists():
                files.append(f'''    ".{dotfile.target_path}" = {{
      source = ./{dotfile.target_path.name};
    }};''')
                
        # Session variables
        session_vars = []
        if config.shell_config.get("shell") != "bash":
            session_vars.append(f'    SHELL = "${{pkgs.{shell}}}/bin/{shell}";')
            
        # Apply theme to terminal
        for theme in config.themes:
            if theme.type == "terminal" and "colors" in theme.settings:
                # This would be expanded to set terminal colors
                pass
                
        # Fill template
        return template.format(
            username=config.username,
            packages="\n".join(package_lines) if package_lines else "    # No packages",
            programs="\n\n".join(programs) if programs else "  # No program configs",
            files="\n\n".join(files) if files else "    # No files",
            session_vars="\n".join(session_vars) if session_vars else "    # No session vars"
        )
    
    def apply_config(self, config: HomeConfig, preview: bool = True) -> Dict[str, Any]:
        """Apply home configuration"""
        result = {
            "success": False,
            "preview": preview,
            "actions": [],
            "home_nix": "",
            "commands": []
        }
        
        # Generate home.nix
        home_nix = self.generate_home_nix(config)
        result["home_nix"] = home_nix
        
        if preview:
            # Just show what would be done
            result["actions"].append("Would create home.nix configuration")
            result["actions"].append(f"Would manage {len(config.dotfiles)} dotfiles")
            result["actions"].append(f"Would apply {len(config.themes)} themes")
            result["actions"].append(f"Would install {len(config.packages)} packages")
            
            # Show commands that would be run
            result["commands"] = [
                "home-manager init",
                "home-manager switch"
            ]
        else:
            # Actually apply the configuration
            # This would integrate with home-manager
            try:
                # Create home.nix file
                home_nix_path = self.config_dir / "home.nix"
                home_nix_path.write_text(home_nix)
                result["actions"].append(f"Created {home_nix_path}")
                
                # Copy dotfiles to config directory
                for dotfile in config.dotfiles:
                    if dotfile.source_path.exists():
                        dest = self.config_dir / dotfile.target_path.name
                        if dotfile.source_path.is_file():
                            shutil.copy2(dotfile.source_path, dest)
                        else:
                            shutil.copytree(dotfile.source_path, dest)
                        result["actions"].append(f"Copied {dotfile.name}")
                        
                result["success"] = True
                
            except Exception as e:
                result["error"] = str(e)
                
        return result
    
    def sync_configs(self, source_machine: str, target_machine: str) -> Dict[str, Any]:
        """Sync configurations between machines"""
        # This would implement config synchronization
        # For now, return a placeholder
        return {
            "success": True,
            "message": f"Would sync configs from {source_machine} to {target_machine}",
            "configs_to_sync": ["vim", "tmux", "git", "shell"]
        }
    
    def apply_theme(self, theme_name: str, applications: List[str]) -> Dict[str, Any]:
        """Apply a theme to specified applications"""
        result = {
            "success": False,
            "theme": theme_name,
            "applications": applications,
            "changes": []
        }
        
        if theme_name not in self.themes:
            result["error"] = f"Unknown theme: {theme_name}"
            result["available_themes"] = list(self.themes.keys())
            return result
            
        theme_data = self.themes[theme_name]
        
        for app in applications:
            if app == "terminal":
                # Generate terminal theme config
                if "alacritty" in str(self.home_dir / ".config/alacritty"):
                    # Generate alacritty theme
                    result["changes"].append({
                        "application": "alacritty",
                        "file": "~/.config/alacritty/alacritty.yml",
                        "theme_applied": theme_name
                    })
                elif "kitty" in str(self.home_dir / ".config/kitty"):
                    # Generate kitty theme
                    result["changes"].append({
                        "application": "kitty",
                        "file": "~/.config/kitty/kitty.conf",
                        "theme_applied": theme_name
                    })
                    
            elif app == "vim":
                # Generate vim colorscheme
                result["changes"].append({
                    "application": "vim",
                    "file": "~/.vimrc",
                    "theme_applied": theme_name
                })
                
        result["success"] = True
        return result
    
    def list_managed_configs(self) -> Dict[str, List[str]]:
        """List all managed configurations"""
        managed = {
            "dotfiles": [],
            "themes": [],
            "packages": [],
            "backups": []
        }
        
        # Check for existing dotfiles
        for name, mapping in self.dotfile_mappings.items():
            for key, path in mapping.items():
                if key in ["config", "dir", "lua_config"]:
                    full_path = self.home_dir / path
                    if full_path.exists():
                        managed["dotfiles"].append(f"{name} ({path})")
                        
        # List available themes
        managed["themes"] = list(self.themes.keys())
        
        # List backups
        if self.backup_dir.exists():
            backups = sorted(self.backup_dir.iterdir(), reverse=True)
            managed["backups"] = [b.name for b in backups[:10]]  # Last 10
            
        return managed


def demonstrate_home_manager():
    """Demo the home manager functionality"""
    manager = HomeManager()
    
    print("🏠 Home Manager Integration Demo")
    print("=" * 50)
    
    # Example 1: Initialize from description
    print("\n1. Natural Language Configuration:")
    config = manager.init_home_config(
        "Set up my dotfiles for vim and tmux with dracula theme"
    )
    print(f"   Created config for: {', '.join(d.name for d in config.dotfiles)}")
    print(f"   Theme: {config.themes[0].name if config.themes else 'none'}")
    
    # Example 2: Generate home.nix
    print("\n2. Generated home.nix:")
    home_nix = manager.generate_home_nix(config)
    print("   " + "\n   ".join(home_nix.split("\n")[:10]) + "\n   ...")
    
    # Example 3: List managed configs
    print("\n3. Currently Managed:")
    managed = manager.list_managed_configs()
    print(f"   Dotfiles: {len(managed['dotfiles'])}")
    print(f"   Available themes: {', '.join(managed['themes'])}")
    
    print("\n✨ Home Manager ready for natural language configuration!")


if __name__ == "__main__":
    demonstrate_home_manager()