#!/usr/bin/env python3
"""
import subprocess
Security-focused integration tests for command execution.
Ensures all user inputs are properly sanitized and validated.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from luminous_nix.core.executor import CommandExecutor as ExecutionEngine
from luminous_nix.core.engine import NixForHumanityBackend as IntentEngine

class TestSecurityExecution(unittest.TestCase):
    """Test security measures in command execution."""
    
    def setUp(self):
        """Set up test environment."""
        self.execution_engine = ExecutionEngine()
        self.intent_engine = IntentEngine()
    
    def test_command_injection_prevention(self):
        """Test prevention of command injection attacks."""
        # Dangerous inputs that should be blocked
        dangerous_inputs = [
            # Shell command chaining
            "firefox; rm -rf /",
            "firefox && malicious-command",
            "firefox || dangerous-fallback",
            "firefox | grep password",
            
            # Command substitution
            "firefox $(evil command)",
            "firefox `backdoor`",
            
            # Variable expansion
            "firefox ${SENSITIVE_VAR}",
            "firefox $HOME/../../../etc/passwd",
            
            # Path traversal
            "../../bin/evil",
            "/etc/passwd",
            "~/../../../root/.ssh/id_rsa",
            
            # Special characters
            "firefox\n\nrm -rf /",
            "firefox\r\nmalicious",
            "firefox;reboot",
            
            # Unicode tricks
            "firefox\u0000rm -rf /",
            "firefox\x00malicious"
        ]
        
        for dangerous_input in dangerous_inputs:
            # Process through intent engine
            intent = self.intent_engine.parse(f"install {dangerous_input}")
            
            # Validate through execution engine
            result = self.execution_engine.validate_safety(intent)
            
            # Should be rejected
            self.assertFalse(
                result['safe'],
                f"Dangerous input not blocked: {dangerous_input}"
            )
            self.assertIn('security', result.get('reason', '').lower())
    
    @patch('subprocess.run')
    def test_safe_command_construction(self, mock_run):
        """Test that commands are constructed safely."""
        # Safe package names
        safe_packages = [
            "firefox",
            "vim",
            "emacs",
            "python3",
            "nodejs-16_x",
            "rust-analyzer"
        ]
        
        for package in safe_packages:
            intent = self.intent_engine.parse(f"install {package}")
            command = self.execution_engine.build_command(intent)
            
            # Should use list form (not shell string)
            self.assertIsInstance(command['args'], list)
            
            # Should not contain shell metacharacters
            for arg in command['args']:
                self.assertNotIn(';', arg)
                self.assertNotIn('&', arg)
                self.assertNotIn('|', arg)
                self.assertNotIn('`', arg)
                self.assertNotIn('$', arg)
                self.assertNotIn('>', arg)
                self.assertNotIn('<', arg)
            
            # Execute safely
            result = self.execution_engine.execute(command, dry_run=False)
            
            # Verify subprocess.run was called safely
            if mock_run.called:
                # Should NOT use shell=True
                _, kwargs = mock_run.call_args
                self.assertFalse(kwargs.get('shell', False))
                
                # Should use list arguments
                args = mock_run.call_args[0][0]
                self.assertIsInstance(args, list)
    
    def test_path_validation(self):
        """Test path validation and sanitization."""
        # Dangerous paths
        dangerous_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/root/.ssh/id_rsa",
            "~/.ssh/id_rsa",
            "../../../etc/passwd",
            "../../../../root",
            "/sys/kernel/security",
            "/proc/self/environ"
        ]
        
        for path in dangerous_paths:
            result = self.execution_engine.validate_path(path)
            self.assertFalse(
                result['valid'],
                f"Dangerous path not blocked: {path}"
            )
    
    def test_environment_sanitization(self):
        """Test environment variable sanitization."""
        # Create a command that might use environment
        intent = self.intent_engine.parse("install firefox")
        command = self.execution_engine.build_command(intent)
        
        # Verify clean environment
        self.assertIn('env', command)
        clean_env = command['env']
        
        # Should have minimal environment
        self.assertIn('PATH', clean_env)
        self.assertIn('HOME', clean_env)
        
        # Should NOT have sensitive variables
        sensitive_vars = [
            'AWS_SECRET_ACCESS_KEY',
            'GITHUB_TOKEN',
            'SSH_AUTH_SOCK',
            'GPG_AGENT_INFO',
            'HISTFILE'
        ]
        
        for var in sensitive_vars:
            self.assertNotIn(var, clean_env)
    
    def test_timeout_enforcement(self):
        """Test command timeout enforcement."""
        # Long-running command
        intent = self.intent_engine.parse("update system")
        command = self.execution_engine.build_command(intent)
        
        # Should have timeout
        self.assertIn('timeout', command)
        self.assertLessEqual(command['timeout'], 300)  # 5 minutes max
    
    @patch('subprocess.run')
    def test_output_sanitization(self, mock_run):
        """Test that command output is sanitized."""
        # Mock output with sensitive data
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success! Password: secret123\nAPI_KEY=abcd1234",
            stderr="Warning: /home/user/.ssh/id_rsa"
        )
        
        intent = self.intent_engine.parse("check system")
        command = self.execution_engine.build_command(intent)
        result = self.execution_engine.execute(command)
        
        # Output should be sanitized
        output = result.get('output', '')
        
        # Should not contain obvious secrets
        self.assertNotIn('secret123', output)
        self.assertNotIn('abcd1234', output)
        self.assertNotIn('id_rsa', output)
        
        # Should mask sensitive patterns
        self.assertNotIn('Password:', output)
        self.assertNotIn('API_KEY=', output)
    
    def test_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation."""
        # Commands that try to escalate privileges
        escalation_attempts = [
            "sudo rm -rf /",
            "su root",
            "pkexec malicious",
            "doas dangerous",
            "setuid-wrapper evil"
        ]
        
        for attempt in escalation_attempts:
            intent = self.intent_engine.parse(attempt)
            result = self.execution_engine.validate_safety(intent)
            
            self.assertFalse(
                result['safe'],
                f"Privilege escalation not blocked: {attempt}"
            )
    
    def test_resource_limits(self):
        """Test resource limit enforcement."""
        intent = self.intent_engine.parse("install large-package")
        command = self.execution_engine.build_command(intent)
        
        # Should have resource limits
        self.assertIn('limits', command)
        limits = command['limits']
        
        # Memory limit
        self.assertIn('memory', limits)
        self.assertLessEqual(limits['memory'], 2 * 1024 * 1024 * 1024)  # 2GB max
        
        # CPU limit
        self.assertIn('cpu', limits)
        self.assertLessEqual(limits['cpu'], 50)  # 50% max
        
        # Disk I/O limit
        self.assertIn('io', limits)
    
    def test_audit_logging(self):
        """Test that all executions are logged for audit."""
        with patch('src.execution_engine.audit_logger') as mock_logger:
            intent = self.intent_engine.parse("install firefox")
            command = self.execution_engine.build_command(intent)
            self.execution_engine.execute(command)
            
            # Should log the execution
            mock_logger.info.assert_called()
            
            # Log should contain key information
            log_call = mock_logger.info.call_args[0][1]
            self.assertIn('command', log_call)
            self.assertIn('user', log_call)
            self.assertIn('timestamp', log_call)
            self.assertIn('result', log_call)
    
    def test_sandboxed_execution(self):
        """Test that commands run in sandboxed environment."""
        intent = self.intent_engine.parse("run custom-script")
        command = self.execution_engine.build_command(intent)
        
        # Should use sandbox
        self.assertIn('sandbox', command)
        sandbox_config = command['sandbox']
        
        # Network isolation
        self.assertFalse(sandbox_config.get('network', True))
        
        # Filesystem restrictions
        self.assertIn('read_only_paths', sandbox_config)
        self.assertIn('/nix/store', sandbox_config['read_only_paths'])
        
        # No access to sensitive directories
        self.assertIn('blocked_paths', sandbox_config)
        blocked = sandbox_config['blocked_paths']
        self.assertIn('/etc', blocked)
        self.assertIn('/root', blocked)
        self.assertIn('/home', blocked)

if __name__ == '__main__':
    unittest.main()