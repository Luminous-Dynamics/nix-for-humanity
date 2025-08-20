#!/usr/bin/env python3
"""Tests for Home Manager integration - personal configuration management."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json
import os

from luminous_nix.core.home_manager import (
    DotfileConfig,
    ThemeConfig,
    HomeConfig
)


class TestHomeManagerDataclasses(unittest.TestCase):
    """Test Home Manager dataclasses."""
    
    def test_dotfile_config_creation(self):
        """Test DotfileConfig dataclass."""
        config = DotfileConfig(
            name="vimrc",
            source_path=Path("~/.vimrc"),
            target_path=Path("/etc/nixos/dotfiles/vimrc"),
            description="Vim configuration"
        )
        
        self.assertEqual(config.name, "vimrc")
        self.assertEqual(config.source_path, Path("~/.vimrc"))
        self.assertEqual(config.target_path, Path("/etc/nixos/dotfiles/vimrc"))
        self.assertEqual(config.description, "Vim configuration")
        self.assertIsNone(config.backup_path)
        
    def test_dotfile_config_with_backup(self):
        """Test DotfileConfig with backup path."""
        config = DotfileConfig(
            name="bashrc",
            source_path=Path("~/.bashrc"),
            target_path=Path("/etc/nixos/dotfiles/bashrc"),
            description="Bash configuration",
            backup_path=Path("~/.bashrc.backup")
        )
        
        self.assertIsNotNone(config.backup_path)
        self.assertEqual(config.backup_path, Path("~/.bashrc.backup"))
        
    def test_theme_config_creation(self):
        """Test ThemeConfig dataclass."""
        theme = ThemeConfig(
            name="dracula",
            type="terminal",
            settings={
                "background": "#282a36",
                "foreground": "#f8f8f2",
                "cursor": "#f8f8f2"
            }
        )
        
        self.assertEqual(theme.name, "dracula")
        self.assertEqual(theme.type, "terminal")
        self.assertIn("background", theme.settings)
        self.assertEqual(theme.settings["background"], "#282a36")
        
    def test_home_config_creation(self):
        """Test HomeConfig dataclass."""
        dotfiles = [
            DotfileConfig(
                name="gitconfig",
                source_path=Path("~/.gitconfig"),
                target_path=Path("/etc/nixos/dotfiles/gitconfig"),
                description="Git configuration"
            )
        ]
        
        themes = [
            ThemeConfig(
                name="solarized",
                type="desktop",
                settings={"variant": "dark"}
            )
        ]
        
        config = HomeConfig(
            username="testuser",
            dotfiles=dotfiles,
            themes=themes,
            shell_config={"shell": "zsh", "prompt": "starship"},
            packages=["vim", "git", "tmux"],
            services={"gpg-agent": {"enable": True}}
        )
        
        self.assertEqual(config.username, "testuser")
        self.assertEqual(len(config.dotfiles), 1)
        self.assertEqual(config.dotfiles[0].name, "gitconfig")
        self.assertEqual(len(config.themes), 1)
        self.assertEqual(config.themes[0].name, "solarized")
        self.assertIn("vim", config.packages)
        self.assertEqual(config.shell_config["shell"], "zsh")
        self.assertTrue(config.services["gpg-agent"]["enable"])
        
    def test_multiple_dotfiles(self):
        """Test HomeConfig with multiple dotfiles."""
        dotfiles = [
            DotfileConfig(
                name="vimrc",
                source_path=Path("~/.vimrc"),
                target_path=Path("/etc/nixos/dotfiles/vimrc"),
                description="Vim config"
            ),
            DotfileConfig(
                name="tmux",
                source_path=Path("~/.tmux.conf"),
                target_path=Path("/etc/nixos/dotfiles/tmux.conf"),
                description="Tmux config"
            ),
            DotfileConfig(
                name="zshrc",
                source_path=Path("~/.zshrc"),
                target_path=Path("/etc/nixos/dotfiles/zshrc"),
                description="Zsh config"
            )
        ]
        
        self.assertEqual(len(dotfiles), 3)
        self.assertEqual(dotfiles[1].name, "tmux")
        self.assertEqual(dotfiles[2].description, "Zsh config")
        
    def test_theme_types(self):
        """Test different theme types."""
        terminal_theme = ThemeConfig(
            name="nord",
            type="terminal",
            settings={"style": "dark"}
        )
        
        desktop_theme = ThemeConfig(
            name="arc",
            type="desktop",
            settings={"window_decorations": "minimal"}
        )
        
        app_theme = ThemeConfig(
            name="vscode-dark",
            type="application",
            settings={"editor.theme": "Dark+"}
        )
        
        self.assertEqual(terminal_theme.type, "terminal")
        self.assertEqual(desktop_theme.type, "desktop")
        self.assertEqual(app_theme.type, "application")
        
    def test_empty_home_config(self):
        """Test minimal HomeConfig."""
        config = HomeConfig(
            username="minimal",
            dotfiles=[],
            themes=[],
            shell_config={},
            packages=[],
            services={}
        )
        
        self.assertEqual(config.username, "minimal")
        self.assertEqual(len(config.dotfiles), 0)
        self.assertEqual(len(config.themes), 0)
        self.assertEqual(len(config.packages), 0)
        self.assertEqual(len(config.services), 0)
        
    def test_complex_shell_config(self):
        """Test complex shell configuration."""
        shell_config = {
            "shell": "fish",
            "prompt": "starship",
            "aliases": {
                "ll": "ls -la",
                "gs": "git status",
                "gc": "git commit"
            },
            "environment": {
                "EDITOR": "nvim",
                "BROWSER": "firefox"
            },
            "plugins": ["z", "fzf", "git"]
        }
        
        config = HomeConfig(
            username="power-user",
            dotfiles=[],
            themes=[],
            shell_config=shell_config,
            packages=[],
            services={}
        )
        
        self.assertEqual(config.shell_config["shell"], "fish")
        self.assertIn("aliases", config.shell_config)
        self.assertEqual(config.shell_config["aliases"]["ll"], "ls -la")
        self.assertEqual(config.shell_config["environment"]["EDITOR"], "nvim")
        self.assertIn("fzf", config.shell_config["plugins"])
        
    def test_services_configuration(self):
        """Test services configuration."""
        services = {
            "gpg-agent": {
                "enable": True,
                "defaultCacheTtl": 1800,
                "maxCacheTtl": 7200
            },
            "syncthing": {
                "enable": True,
                "dataDir": "/home/user/Sync"
            },
            "redshift": {
                "enable": True,
                "temperature": {
                    "day": 5500,
                    "night": 3500
                }
            }
        }
        
        config = HomeConfig(
            username="service-user",
            dotfiles=[],
            themes=[],
            shell_config={},
            packages=[],
            services=services
        )
        
        self.assertTrue(config.services["gpg-agent"]["enable"])
        self.assertEqual(config.services["syncthing"]["dataDir"], "/home/user/Sync")
        self.assertEqual(config.services["redshift"]["temperature"]["night"], 3500)
        
    def test_development_packages(self):
        """Test development-oriented package list."""
        packages = [
            "vim", "neovim", "emacs",
            "git", "gh", "tig",
            "tmux", "screen",
            "python3", "nodejs", "rustc",
            "docker", "podman",
            "ripgrep", "fd", "bat", "exa"
        ]
        
        config = HomeConfig(
            username="developer",
            dotfiles=[],
            themes=[],
            shell_config={},
            packages=packages,
            services={}
        )
        
        self.assertIn("neovim", config.packages)
        self.assertIn("rustc", config.packages)
        self.assertIn("ripgrep", config.packages)
        self.assertEqual(len(config.packages), 17)  # Count updated


if __name__ == "__main__":
    unittest.main()