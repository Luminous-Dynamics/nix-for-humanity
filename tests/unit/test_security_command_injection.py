#!/usr/bin/env python3
"""
Security tests to verify command injection vulnerabilities are fixed.
"""

import unittest
import subprocess
import sys
import os
from unittest.mock import patch, MagicMock

# Add the bin directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../bin'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

class TestCommandInjectionPrevention(unittest.TestCase):
    """Test that command injection vulnerabilities are prevented."""
    
    @patch('subprocess.run')
    def test_search_command_injection_prevented(self, mock_run):
        """Test that search functionality prevents command injection."""
        # Import the module
        from importlib import import_module
        import importlib.util
        
        # Load ask-nix module
        spec = importlib.util.spec_from_file_location(
            "ask_nix", 
            os.path.join(os.path.dirname(__file__), '../../bin/ask-nix')
        )
        ask_nix = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ask_nix)
        
        # Create assistant instance
        assistant = ask_nix.UnifiedNixAssistant()
        
        # Test dangerous search terms that would be exploited with shell=True
        dangerous_inputs = [
            "firefox; rm -rf /tmp/test",
            "vim && echo 'hacked'",
            "python | cat /etc/passwd",
            "nodejs`echo vulnerable`",
            "package$(malicious command)",
            "test'; DROP TABLE users; --",
            "package\n\nrm -rf /"
        ]
        
        for dangerous_input in dangerous_inputs:
            mock_run.reset_mock()
            
            # Perform search with dangerous input
            assistant._perform_search(dangerous_input)
            
            # Verify subprocess.run was called with list, not string
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            
            # Should be a list, not a string
            self.assertIsInstance(args, list, 
                f"Command should be list, not string for input: {dangerous_input}")
            
            # The dangerous input should be a single argument, not parsed by shell
            self.assertIn(dangerous_input, args,
                f"Dangerous input should be passed as single argument: {dangerous_input}")
            
            # Should NOT contain shell metacharacters as separate arguments
            for arg in args:
                if arg != dangerous_input:  # Skip the search term itself
                    self.assertNotIn(';', arg, "Shell command separator found in args")
                    self.assertNotIn('&&', arg, "Shell AND operator found in args")
                    self.assertNotIn('||', arg, "Shell OR operator found in args")
                    self.assertNotIn('|', arg, "Shell pipe found in args")
                    self.assertNotIn('`', arg, "Shell backtick found in args")
                    self.assertNotIn('$(', arg, "Shell command substitution found in args")
    
    @patch('subprocess.run')
    def test_execute_with_progress_prevents_injection(self, mock_run):
        """Test that execute_with_progress prevents command injection."""
        from importlib import import_module
        import importlib.util
        
        # Load ask-nix module
        spec = importlib.util.spec_from_file_location(
            "ask_nix", 
            os.path.join(os.path.dirname(__file__), '../../bin/ask-nix')
        )
        ask_nix = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ask_nix)
        
        # Create assistant instance
        assistant = ask_nix.UnifiedNixAssistant()
        assistant.show_progress = False  # Disable progress for testing
        
        # Test commands with injection attempts
        test_commands = [
            "nix profile install firefox; rm -rf /tmp/test",
            "nix search python && echo 'hacked'",
            "home-manager switch | cat /etc/passwd"
        ]
        
        for cmd in test_commands:
            mock_run.reset_mock()
            
            # Execute command
            assistant.execute_with_progress(cmd)
            
            # Verify subprocess.run was called with list
            mock_run.assert_called()
            args = mock_run.call_args[0][0]
            
            # Should be a list after shlex.split
            self.assertIsInstance(args, list,
                f"Command should be split into list: {cmd}")
            
            # Verify dangerous parts are not executed as separate commands
            # For example, "rm -rf /tmp/test" should not be a separate command
            self.assertNotIn(['rm', '-rf', '/tmp/test'], 
                [args[i:i+3] for i in range(len(args)-2)],
                "Dangerous command should not be parsed as separate")
    
    @patch('subprocess.run')
    def test_home_manager_check_safe(self, mock_run):
        """Test that home-manager version check is safe."""
        from importlib import import_module
        import importlib.util
        
        # Load ask-nix module
        spec = importlib.util.spec_from_file_location(
            "ask_nix", 
            os.path.join(os.path.dirname(__file__), '../../bin/ask-nix')
        )
        ask_nix = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ask_nix)
        
        # Create assistant instance
        assistant = ask_nix.UnifiedNixAssistant()
        
        # Check home manager
        assistant.check_home_manager_installed()
        
        # Verify it was called with a list
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        
        self.assertIsInstance(args, list, "Command should be a list")
        self.assertEqual(args, ["home-manager", "--version"], 
                        "Should be exact command list")
    
    def test_demo_script_safe(self):
        """Test that demo script is safe from injection."""
        # Import the demo module
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "demo_learning_mode",
            os.path.join(os.path.dirname(__file__), 
                        '../../scripts/demo/demo-learning-mode.py')
        )
        demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo)
        
        # Test the run_command function with mock
        with patch('subprocess.run') as mock_run:
            # Test with injection attempt
            demo.run_command("echo 'test'; rm -rf /tmp/test")
            
            # Verify it was called with a list
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            
            self.assertIsInstance(args, list, "Command should be a list")
            # After shlex.split, the semicolon should be part of the string
            self.assertTrue(
                any(";" in arg for arg in args),
                "Semicolon should be preserved in arguments, not parsed as separator"
            )
    
    def test_monitor_coverage_safe(self):
        """Test that monitor-coverage.py is safe from injection."""
        # Import the module
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "monitor_coverage",
            os.path.join(os.path.dirname(__file__), 
                        '../../scripts/monitor-coverage.py')
        )
        monitor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(monitor)
        
        # Test the run_command function
        with patch('subprocess.run') as mock_run:
            # Test with injection attempt
            monitor.run_command("pytest; echo 'hacked' > /tmp/pwned")
            
            # Verify safe execution
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            
            self.assertIsInstance(args, list, "Command should be a list")
            # After shlex.split, the entire command should be one argument with semicolon
            # This is safe because it won't be interpreted by shell
            joined_args = ' '.join(args)
            self.assertIn(";", joined_args, "Semicolon should be preserved, not interpreted as separator")
    
    def test_no_shell_true_in_codebase(self):
        """Verify no shell=True remains in critical files."""
        critical_files = [
            "bin/ask-nix",
            "scripts/demo/demo-learning-mode.py",
            "scripts/monitor-coverage.py",
            "intent_fix_summary.py"
        ]
        
        project_root = os.path.join(os.path.dirname(__file__), '../..')
        
        for file_path in critical_files:
            full_path = os.path.join(project_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                    self.assertNotIn('shell=True', content,
                        f"shell=True found in {file_path} - security vulnerability!")


if __name__ == '__main__':
    unittest.main()