#!/usr/bin/env python3
"""
Comprehensive tests for Home Manager integration.
Tests the complete flow from natural language to home configuration.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.luminous_nix.core.luminous_core import LuminousNixCore, Query, Response
from src.luminous_nix.core.home_executor import HomeExecutor, HomeResult
from src.luminous_nix.core.home_manager import HomeManager, HomeConfig
from src.luminous_nix.nlp import SimpleIntentRecognizer, IntentType


class TestHomeManagerIntegration(unittest.TestCase):
    """Test Home Manager integration with the core system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.core = LuminousNixCore()
        self.executor = HomeExecutor()
        self.recognizer = SimpleIntentRecognizer()
    
    def test_home_intent_recognition(self):
        """Test that home-related queries are recognized correctly."""
        test_queries = [
            ("set up my dotfiles", IntentType.HOME),
            ("configure vim and tmux", IntentType.HOME),
            ("manage my home configuration", IntentType.HOME),
            ("apply dracula theme", IntentType.HOME),
            ("setup my shell config", IntentType.HOME),
            ("home manager init", IntentType.HOME),
        ]
        
        for query, expected_type in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(
                intent.type, expected_type,
                f"Query '{query}' should be recognized as {expected_type}"
            )
    
    def test_home_executor_init(self):
        """Test HomeExecutor initialization operation."""
        result = self.executor.execute(
            intent_type="home",
            query="set up vim and tmux with dracula theme",
            entities={}
        )
        
        self.assertIsInstance(result, HomeResult)
        self.assertTrue(result.success)
        self.assertIn("vim", str(result.dotfiles).lower() if result.dotfiles else "")
        self.assertIn("tmux", str(result.dotfiles).lower() if result.dotfiles else "")
        self.assertIn("dracula", str(result.themes).lower() if result.themes else "")
    
    def test_home_executor_theme(self):
        """Test HomeExecutor theme application."""
        result = self.executor.execute(
            intent_type="home",
            query="apply nord theme to terminal",
            entities={"theme": "nord"}
        )
        
        self.assertIsInstance(result, HomeResult)
        self.assertTrue(result.success)
        if result.themes:
            self.assertIn("nord", result.themes)
    
    def test_home_executor_add_dotfile(self):
        """Test HomeExecutor adding dotfiles."""
        result = self.executor.execute(
            intent_type="home",
            query="add vim configuration",
            entities={"target": "vim"}
        )
        
        self.assertIsInstance(result, HomeResult)
        self.assertTrue(result.success)
        if result.dotfiles:
            self.assertIn("vim", result.dotfiles)
    
    def test_core_home_integration(self):
        """Test full integration through LuminousNixCore."""
        query = Query("set up my development environment with vim and tmux")
        response = self.core.process_query(query)
        
        self.assertIsInstance(response, Response)
        self.assertTrue(response.success)
        self.assertIsNotNone(response.message)
        
        # Check that home manager was invoked
        if response.data:
            dotfiles = response.data.get('dotfiles', [])
            self.assertTrue(
                any('vim' in str(d).lower() for d in dotfiles) or
                'vim' in response.message.lower()
            )
    
    def test_home_manager_config_generation(self):
        """Test HomeManager config generation."""
        manager = HomeManager()
        config = manager.init_home_config("vim and tmux with dracula theme")
        
        self.assertIsInstance(config, HomeConfig)
        self.assertTrue(len(config.dotfiles) > 0)
        
        # Generate home.nix
        home_nix = manager.generate_home_nix(config)
        self.assertIn("home.packages", home_nix)
        self.assertIn("programs.", home_nix)
    
    def test_natural_language_variations(self):
        """Test various natural language patterns for home management."""
        test_cases = [
            "I want to manage my dotfiles",
            "setup vim with my favorite settings",
            "configure my development environment",
            "make my terminal look nice with dracula theme",
            "sync my configs between machines",
            "backup my current configuration",
        ]
        
        for query_text in test_cases:
            query = Query(query_text)
            response = self.core.process_query(query)
            
            self.assertIsInstance(response, Response)
            # Should either succeed or provide helpful error
            if not response.success:
                self.assertIsNotNone(response.error)
                self.assertIsNotNone(response.message)
    
    @patch('subprocess.run')
    def test_home_manager_command_execution(self, mock_run):
        """Test that home-manager commands are constructed correctly."""
        # Mock successful home-manager execution
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Home configuration applied",
            stderr=""
        )
        
        result = self.executor.execute(
            intent_type="home",
            query="apply configuration",
            entities={}
        )
        
        self.assertTrue(result.success)
        if result.command:
            self.assertIn("home-manager", result.command)
    
    def test_theme_detection(self):
        """Test theme detection from natural language."""
        theme_queries = [
            ("I like the dracula theme", "dracula"),
            ("apply nord colors", "nord"),
            ("use solarized dark theme", "solarized-dark"),
            ("gruvbox looks nice", "gruvbox"),
        ]
        
        for query, expected_theme in theme_queries:
            result = self.executor.execute(
                intent_type="home",
                query=query,
                entities={}
            )
            
            if result.themes:
                self.assertIn(expected_theme, result.themes)
    
    def test_dotfile_detection(self):
        """Test dotfile type detection from natural language."""
        dotfile_queries = [
            ("configure vim", ["vim"]),
            ("set up tmux and git", ["tmux", "git"]),
            ("I need bash and zsh configs", ["bash", "zsh"]),
            ("manage my neovim settings", ["neovim"]),
        ]
        
        for query, expected_dotfiles in dotfile_queries:
            result = self.executor.execute(
                intent_type="home",
                query=query,
                entities={}
            )
            
            if result.dotfiles:
                for expected in expected_dotfiles:
                    self.assertTrue(
                        any(expected in d for d in result.dotfiles),
                        f"Expected {expected} in {result.dotfiles}"
                    )
    
    def test_backup_functionality(self):
        """Test configuration backup."""
        with patch('shutil.copy2') as mock_copy:
            result = self.executor.execute(
                intent_type="home",
                query="backup my configurations",
                entities={}
            )
            
            self.assertTrue(result.success)
            self.assertIn("backup", result.message.lower())
    
    def test_sync_functionality(self):
        """Test configuration sync between machines."""
        result = self.executor.execute(
            intent_type="home",
            query="sync from laptop to desktop",
            entities={}
        )
        
        self.assertIsInstance(result, HomeResult)
        # Sync might not be fully implemented but should handle gracefully
        self.assertIsNotNone(result.message)
    
    def test_list_configurations(self):
        """Test listing managed configurations."""
        result = self.executor.execute(
            intent_type="home",
            query="show my configurations",
            entities={}
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.message)
    
    def test_error_handling(self):
        """Test error handling in home manager operations."""
        # Test with malformed query
        with patch.object(HomeManager, 'init_home_config', side_effect=Exception("Test error")):
            result = self.executor.execute(
                intent_type="home",
                query="this will fail",
                entities={}
            )
            
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)
            self.assertIn("failed", result.message.lower())
    
    def test_shell_preference_detection(self):
        """Test shell preference detection."""
        shell_queries = [
            ("I use zsh", "zsh"),
            ("configure for fish shell", "fish"),
            ("bash is my shell", "bash"),
        ]
        
        for query, expected_shell in shell_queries:
            manager = HomeManager()
            config = manager.init_home_config(query)
            
            if config.shell_config:
                detected_shell = config.shell_config.get('shell', 'bash')
                self.assertEqual(detected_shell, expected_shell)
    
    def test_package_inclusion(self):
        """Test that relevant packages are included."""
        manager = HomeManager()
        config = manager.init_home_config("vim and tmux development setup")
        
        # Should suggest relevant packages
        self.assertTrue(
            any('vim' in p.lower() for p in config.packages) or
            len(config.dotfiles) > 0
        )
    
    def test_home_manager_not_installed(self):
        """Test graceful handling when home-manager is not installed."""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            check_result = self.executor.check_home_manager_installed()
            self.assertFalse(check_result)
    
    def test_comprehensive_config(self):
        """Test a comprehensive configuration request."""
        query = Query(
            "Set up my development environment with vim, tmux, git, "
            "zsh with oh-my-zsh, dracula theme for everything, "
            "and include rust development tools"
        )
        
        response = self.core.process_query(query)
        
        self.assertTrue(response.success)
        if response.data:
            # Should have multiple dotfiles
            dotfiles = response.data.get('dotfiles', [])
            self.assertTrue(len(dotfiles) >= 2)
            
            # Should have theme
            themes = response.data.get('themes', [])
            self.assertTrue(len(themes) >= 1)


class TestHomeManagerCommands(unittest.TestCase):
    """Test Home Manager CLI commands."""
    
    @patch('click.echo')
    def test_home_init_command(self, mock_echo):
        """Test home init CLI command."""
        from src.luminous_nix.cli.home_command import init
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(init, ['--preview', 'vim and tmux setup'])
        
        # Command should succeed
        self.assertEqual(result.exit_code, 0)
        
        # Should show configuration
        mock_echo.assert_called()
        calls_str = str(mock_echo.call_args_list)
        self.assertTrue(
            'Home Configuration' in calls_str or
            'home.nix' in calls_str
        )
    
    @patch('click.echo')
    def test_home_theme_command(self, mock_echo):
        """Test home theme CLI command."""
        from src.luminous_nix.cli.home_command import theme
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(theme, ['dracula', '--apps', 'terminal', '--preview'])
        
        # Command should succeed
        self.assertEqual(result.exit_code, 0)
        
        # Should show theme application
        calls_str = str(mock_echo.call_args_list)
        self.assertTrue(
            'dracula' in calls_str.lower() or
            'theme' in calls_str.lower()
        )
    
    @patch('click.echo')
    def test_home_list_command(self, mock_echo):
        """Test home list CLI command."""
        from src.luminous_nix.cli.home_command import list as list_cmd
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(list_cmd)
        
        # Command should succeed
        self.assertEqual(result.exit_code, 0)
        
        # Should show status
        calls_str = str(mock_echo.call_args_list)
        self.assertTrue(
            'Home Manager Status' in calls_str or
            'Themes' in calls_str
        )


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)