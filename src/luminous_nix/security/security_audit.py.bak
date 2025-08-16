#!/usr/bin/env python3
"""
from typing import List, Dict, Optional, Tuple
Enhanced Security Audit System for Nix for Humanity

Provides comprehensive security auditing, validation, and protection
against various attack vectors including command injection, path traversal,
and privilege escalation.
"""

import hashlib
import hmac
import json
import os
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import toml
import yaml

from nix_for_humanity.utils.logging import get_logger

from .validator import InputValidator

logger = get_logger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditCategory(Enum):
    """Categories of security audits"""

    INPUT_VALIDATION = "input_validation"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXPOSURE = "data_exposure"
    RATE_LIMITING = "rate_limiting"
    CONFIG_SECURITY = "config_security"
    DEPENDENCY_SECURITY = "dependency_security"


@dataclass
class SecurityViolation:
    """Record of a security violation"""

    category: AuditCategory
    threat_level: ThreatLevel
    description: str
    location: str
    timestamp: datetime
    details: dict[str, Any]
    remediation: str


@dataclass
class AuditResult:
    """Result of a security audit"""

    passed: bool
    violations: list[SecurityViolation]
    warnings: list[str]
    score: float  # 0.0 to 1.0
    timestamp: datetime
    recommendations: list[str]


class RateLimiter:
    """Rate limiting for API calls and operations"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[datetime]] = {}

    def check_rate_limit(self, identifier: str) -> tuple[bool, int | None]:
        """Check if request is within rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                ts for ts in self.requests[identifier] if ts > window_start
            ]
        else:
            self.requests[identifier] = []

        # Check limit
        current_requests = len(self.requests[identifier])
        if current_requests >= self.max_requests:
            # Calculate seconds until oldest request expires
            oldest = min(self.requests[identifier])
            wait_seconds = int(
                (oldest + timedelta(seconds=self.window_seconds) - now).total_seconds()
            )
            return False, wait_seconds

        # Add request
        self.requests[identifier].append(now)
        return True, None

    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier"""
        if identifier in self.requests:
            del self.requests[identifier]


class SecurityAuditor:
    """
    Comprehensive security auditor for Nix for Humanity

    Features:
    - Input validation and sanitization
    - Command injection prevention
    - Path traversal protection
    - Privilege escalation detection
    - Configuration security
    - Rate limiting
    - Security logging
    """

    def __init__(self):
        self.input_validator = InputValidator()
        self.rate_limiter = RateLimiter()
        self.violation_history: list[SecurityViolation] = []
        self.trusted_commands = self._load_trusted_commands()
        self.dangerous_patterns = self._load_dangerous_patterns()

    def _load_trusted_commands(self) -> set[str]:
        """Load list of trusted commands"""
        return {
            "nix",
            "nix-env",
            "nix-channel",
            "nix-store",
            "nix-build",
            "nixos-rebuild",
            "nixos-version",
            "nix-shell",
            "nix-instantiate",
            "nix-collect-garbage",
            "nix-hash",
            "nix-prefetch-url",
            "home-manager",
            "systemctl",
            "journalctl",
            "ip",
            "ping",
            "df",
            "free",
            "ps",
            "which",
            "whereis",
            "ls",
            "cat",
            "echo",
            "true",
            "false",
            "date",
            "whoami",
            "hostname",
        }

    def _load_dangerous_patterns(self) -> list[tuple[re.Pattern, str]]:
        """Load dangerous command patterns"""
        patterns = [
            # Command injection
            (r"[;&|](?!&)", "Command chaining detected"),
            (r"`[^`]+`", "Command substitution detected"),
            (r"\$\([^)]+\)", "Command substitution detected"),
            (r"\${[^}]+}", "Variable expansion detected"),
            # Path traversal
            (r"\.\./", "Parent directory traversal detected"),
            (r"/\.\.", "Parent directory traversal detected"),
            (r"\.\.\\", "Windows-style traversal detected"),
            # Dangerous commands
            (r"\brm\s+-rf\s+/", "Dangerous recursive deletion detected"),
            (r"\bdd\s+if=/dev/(zero|random)", "Disk destruction command detected"),
            (r"\bmkfs\.", "Filesystem format command detected"),
            (r":\(\)\{\s*:\|:\&\s*\};:", "Fork bomb detected"),
            # Privilege escalation
            (r"\bsudo\s+-i", "Interactive sudo detected"),
            (r"\bsu\s+-", "Switch user detected"),
            (r"/etc/passwd|/etc/shadow", "Sensitive file access detected"),
            # Network operations
            (r"\bnc\s+-l", "Netcat listener detected"),
            (r"\bwget\s+.*\|.*sh", "Remote code execution detected"),
            (r"\bcurl\s+.*\|.*sh", "Remote code execution detected"),
        ]

        return [(re.compile(pattern, re.IGNORECASE), msg) for pattern, msg in patterns]

    def audit_input(self, user_input: str, context: str = "general") -> AuditResult:
        """Perform comprehensive input audit"""
        violations = []
        warnings = []

        # Check rate limiting
        user_id = self._get_user_identifier()
        allowed, wait_time = self.rate_limiter.check_rate_limit(user_id)
        if not allowed:
            violations.append(
                SecurityViolation(
                    category=AuditCategory.RATE_LIMITING,
                    threat_level=ThreatLevel.MEDIUM,
                    description="Rate limit exceeded",
                    location="input",
                    timestamp=datetime.now(),
                    details={"wait_seconds": wait_time},
                    remediation=f"Wait {wait_time} seconds before retry",
                )
            )

        # Validate input
        validation_result = self.input_validator.validate_input(user_input, context)
        if not validation_result["valid"]:
            violations.append(
                SecurityViolation(
                    category=AuditCategory.INPUT_VALIDATION,
                    threat_level=ThreatLevel.HIGH,
                    description=validation_result["reason"],
                    location="input",
                    timestamp=datetime.now(),
                    details={"input": user_input[:100]},
                    remediation="; ".join(validation_result.get("suggestions", [])),
                )
            )

        # Check for dangerous patterns
        for pattern, message in self.dangerous_patterns:
            if pattern.search(user_input):
                violations.append(
                    SecurityViolation(
                        category=AuditCategory.COMMAND_INJECTION,
                        threat_level=ThreatLevel.CRITICAL,
                        description=message,
                        location="input",
                        timestamp=datetime.now(),
                        details={"pattern": pattern.pattern},
                        remediation="Remove dangerous patterns from input",
                    )
                )

        # Check for suspicious behavior
        if self._detect_suspicious_behavior(user_input):
            warnings.append("Suspicious input pattern detected")

        # Calculate security score
        score = self._calculate_security_score(violations, warnings)

        # Generate recommendations
        recommendations = self._generate_recommendations(violations, warnings)

        return AuditResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            score=score,
            timestamp=datetime.now(),
            recommendations=recommendations,
        )

    def audit_command(self, command: list[str]) -> AuditResult:
        """Audit a command before execution"""
        violations = []
        warnings = []

        if not command:
            violations.append(
                SecurityViolation(
                    category=AuditCategory.INPUT_VALIDATION,
                    threat_level=ThreatLevel.LOW,
                    description="Empty command",
                    location="command",
                    timestamp=datetime.now(),
                    details={},
                    remediation="Provide a valid command",
                )
            )

        else:
            # Check base command
            base_cmd = os.path.basename(command[0])
            if base_cmd not in self.trusted_commands:
                violations.append(
                    SecurityViolation(
                        category=AuditCategory.PRIVILEGE_ESCALATION,
                        threat_level=ThreatLevel.HIGH,
                        description=f"Untrusted command: {base_cmd}",
                        location="command",
                        timestamp=datetime.now(),
                        details={"command": base_cmd},
                        remediation="Use only trusted commands",
                    )
                )

            # Check arguments
            dangerous_args = self._check_dangerous_args(command)
            for arg, reason in dangerous_args:
                violations.append(
                    SecurityViolation(
                        category=AuditCategory.COMMAND_INJECTION,
                        threat_level=ThreatLevel.HIGH,
                        description=f"Dangerous argument: {reason}",
                        location="command_args",
                        timestamp=datetime.now(),
                        details={"argument": arg},
                        remediation="Remove dangerous arguments",
                    )
                )

        score = self._calculate_security_score(violations, warnings)
        recommendations = self._generate_recommendations(violations, warnings)

        return AuditResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            score=score,
            timestamp=datetime.now(),
            recommendations=recommendations,
        )

    def audit_file_operation(self, path: str, operation: str) -> AuditResult:
        """Audit file operations for security"""
        violations = []
        warnings = []

        # Normalize path
        try:
            normalized_path = Path(path).resolve()
        except Exception:
            violations.append(
                SecurityViolation(
                    category=AuditCategory.PATH_TRAVERSAL,
                    threat_level=ThreatLevel.HIGH,
                    description="Invalid path",
                    location="file_operation",
                    timestamp=datetime.now(),
                    details={"path": path, "operation": operation},
                    remediation="Use valid absolute paths",
                )
            )
            normalized_path = None

        if normalized_path:
            # Check path traversal
            if ".." in str(path):
                violations.append(
                    SecurityViolation(
                        category=AuditCategory.PATH_TRAVERSAL,
                        threat_level=ThreatLevel.HIGH,
                        description="Path traversal attempt",
                        location="file_operation",
                        timestamp=datetime.now(),
                        details={"path": str(path)},
                        remediation="Use absolute paths without ..",
                    )
                )

            # Check sensitive paths
            sensitive_paths = [
                "/etc/passwd",
                "/etc/shadow",
                "/etc/sudoers",
                "/root",
                "/home/*/.ssh",
                "/var/log/auth.log",
            ]

            for sensitive in sensitive_paths:
                if self._path_matches(str(normalized_path), sensitive):
                    violations.append(
                        SecurityViolation(
                            category=AuditCategory.DATA_EXPOSURE,
                            threat_level=ThreatLevel.CRITICAL,
                            description=f"Access to sensitive path: {sensitive}",
                            location="file_operation",
                            timestamp=datetime.now(),
                            details={"path": str(normalized_path)},
                            remediation="Avoid accessing sensitive system files",
                        )
                    )

            # Check write operations to system directories
            if operation in ["write", "delete", "modify"]:
                system_dirs = ["/etc", "/usr", "/bin", "/sbin", "/lib", "/boot"]
                for sys_dir in system_dirs:
                    if str(normalized_path).startswith(sys_dir):
                        violations.append(
                            SecurityViolation(
                                category=AuditCategory.PRIVILEGE_ESCALATION,
                                threat_level=ThreatLevel.HIGH,
                                description=f"Write to system directory: {sys_dir}",
                                location="file_operation",
                                timestamp=datetime.now(),
                                details={"path": str(normalized_path)},
                                remediation="Use appropriate NixOS configuration methods",
                            )
                        )

        score = self._calculate_security_score(violations, warnings)
        recommendations = self._generate_recommendations(violations, warnings)

        return AuditResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            score=score,
            timestamp=datetime.now(),
            recommendations=recommendations,
        )

    def audit_configuration(
        self, config_data: dict[str, Any], format: str = "yaml"
    ) -> AuditResult:
        """Audit configuration for security issues"""
        violations = []
        warnings = []

        # Check for exposed secrets
        secret_patterns = [
            (r'(password|passwd|pwd)\s*[:=]\s*["\']?[^"\'\s]+', "Exposed password"),
            (r'(api_key|apikey|key)\s*[:=]\s*["\']?[^"\'\s]+', "Exposed API key"),
            (r'(token|secret)\s*[:=]\s*["\']?[^"\'\s]+', "Exposed token/secret"),
            (
                r'(private_key|privatekey)\s*[:=]\s*["\']?[^"\'\s]+',
                "Exposed private key",
            ),
        ]

        config_str = self._serialize_config(config_data, format)

        for pattern, message in secret_patterns:
            if re.search(pattern, config_str, re.IGNORECASE):
                violations.append(
                    SecurityViolation(
                        category=AuditCategory.DATA_EXPOSURE,
                        threat_level=ThreatLevel.CRITICAL,
                        description=message,
                        location="configuration",
                        timestamp=datetime.now(),
                        details={},
                        remediation="Use environment variables or secure vaults for secrets",
                    )
                )

        # Check permissions settings
        if "permissions" in config_data or "chmod" in config_str.lower():
            if re.search(r"0?777|0?666", config_str):
                violations.append(
                    SecurityViolation(
                        category=AuditCategory.CONFIG_SECURITY,
                        threat_level=ThreatLevel.HIGH,
                        description="Overly permissive file permissions",
                        location="configuration",
                        timestamp=datetime.now(),
                        details={},
                        remediation="Use restrictive permissions (e.g., 600, 644)",
                    )
                )

        # Check for unsafe settings
        unsafe_settings = {
            "debug_mode": True,
            "allow_root": True,
            "disable_auth": True,
            "skip_validation": True,
        }

        for setting, unsafe_value in unsafe_settings.items():
            if self._check_config_value(config_data, setting, unsafe_value):
                warnings.append(f"Unsafe setting detected: {setting}={unsafe_value}")

        score = self._calculate_security_score(violations, warnings)
        recommendations = self._generate_recommendations(violations, warnings)

        return AuditResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            score=score,
            timestamp=datetime.now(),
            recommendations=recommendations,
        )

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)

    def hash_sensitive_data(self, data: str, salt: str | None = None) -> str:
        """Hash sensitive data with salt"""
        if not salt:
            salt = secrets.token_hex(16)

        # Use PBKDF2 for secure hashing

        dk = hashlib.pbkdf2_hmac(
            "sha256", data.encode("utf-8"), salt.encode("utf-8"), 100000
        )  # iterations
        return f"{salt}${dk.hex()}"

    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verify hashed data"""
        try:
            salt, hash_hex = hash_value.split("$")
            new_hash = self.hash_sensitive_data(data, salt)
            return hmac.compare_digest(new_hash, hash_value)
        except Exception:
            return False

    def _get_user_identifier(self) -> str:
        """Get user identifier for rate limiting"""
        # In a real implementation, this would get the actual user ID
        # For now, use a combination of username and session
        return f"{os.getenv('USER', 'unknown')}_{os.getpid()}"

    def _detect_suspicious_behavior(self, input_str: str) -> bool:
        """Detect suspicious behavior patterns"""
        suspicious_indicators = [
            # Multiple failed attempts at dangerous operations
            re.compile(
                r"(rm|delete|remove).*\b(fail|error|denied)\b.*\1", re.IGNORECASE
            ),
            # Repeated privilege escalation attempts
            re.compile(r"(sudo|root|admin).*\1.*\1", re.IGNORECASE),
            # Obfuscation attempts
            re.compile(r"\\x[0-9a-f]{2}|\\[0-7]{3}", re.IGNORECASE),
            # Base64 encoded commands
            re.compile(r"echo\s+[A-Za-z0-9+/]{20,}.*\|\s*base64", re.IGNORECASE),
        ]

        return any(pattern.search(input_str) for pattern in suspicious_indicators)

    def _check_dangerous_args(self, command: list[str]) -> list[tuple[str, str]]:
        """Check for dangerous command arguments"""
        dangerous = []

        dangerous_flags = {
            "--no-sandbox": "Disables security sandbox",
            "--privileged": "Requests privileged access",
            "--disable-security": "Disables security features",
            "-rf /": "Recursive force deletion from root",
            "of=/": "Output to root filesystem",
        }

        for arg in command[1:]:
            for flag, reason in dangerous_flags.items():
                if flag in arg:
                    dangerous.append((arg, reason))

            # Check for shell metacharacters
            if any(char in arg for char in ";|&`$<>"):
                dangerous.append((arg, "Contains shell metacharacters"))

        return dangerous

    def _path_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches a pattern (with wildcards)"""
        import fnmatch

        return fnmatch.fnmatch(path, pattern)

    def _serialize_config(self, config: dict[str, Any], format: str) -> str:
        """Serialize configuration to string"""
        if format == "yaml":
            return yaml.dump(config)
        if format == "json":
            return json.dumps(config)
        if format == "toml":
            return toml.dumps(config)
        return str(config)

    def _check_config_value(self, config: dict[str, Any], key: str, value: Any) -> bool:
        """Recursively check for config value"""
        if key in config and config[key] == value:
            return True

        for k, v in config.items():
            if isinstance(v, dict):
                if self._check_config_value(v, key, value):
                    return True

        return False

    def _calculate_security_score(
        self, violations: list[SecurityViolation], warnings: list[str]
    ) -> float:
        """Calculate overall security score"""
        if not violations and not warnings:
            return 1.0

        # Weight violations by threat level
        threat_weights = {
            ThreatLevel.CRITICAL: 0.4,
            ThreatLevel.HIGH: 0.3,
            ThreatLevel.MEDIUM: 0.2,
            ThreatLevel.LOW: 0.1,
            ThreatLevel.SAFE: 0.0,
        }

        total_weight = sum(threat_weights[v.threat_level] for v in violations)
        warning_weight = len(warnings) * 0.05

        score = max(0.0, 1.0 - total_weight - warning_weight)
        return round(score, 2)

    def _generate_recommendations(
        self, violations: list[SecurityViolation], warnings: list[str]
    ) -> list[str]:
        """Generate security recommendations"""
        recommendations = []

        # Group violations by category
        categories = {}
        for violation in violations:
            if violation.category not in categories:
                categories[violation.category] = []
            categories[violation.category].append(violation)

        # Generate category-specific recommendations
        if AuditCategory.INPUT_VALIDATION in categories:
            recommendations.append(
                "Implement stricter input validation and sanitization"
            )

        if AuditCategory.COMMAND_INJECTION in categories:
            recommendations.append(
                "Avoid shell execution; use direct API calls instead"
            )

        if AuditCategory.PATH_TRAVERSAL in categories:
            recommendations.append(
                "Use absolute paths and validate all file operations"
            )

        if AuditCategory.PRIVILEGE_ESCALATION in categories:
            recommendations.append("Follow principle of least privilege")

        if AuditCategory.DATA_EXPOSURE in categories:
            recommendations.append("Use secure credential management systems")

        if AuditCategory.RATE_LIMITING in categories:
            recommendations.append("Implement proper rate limiting and backoff")

        # Add general recommendations
        if len(violations) > 5:
            recommendations.append("Consider a comprehensive security review")

        if warnings:
            recommendations.append(
                "Address security warnings to improve overall posture"
            )

        return recommendations

    def log_violation(self, violation: SecurityViolation) -> None:
        """Log security violation for analysis"""
        self.violation_history.append(violation)

        # Log to security log
        logger.warning(
            f"Security violation: {violation.category.value} - "
            f"{violation.threat_level.value} - {violation.description}",
            extra={
                "category": violation.category.value,
                "threat_level": violation.threat_level.value,
                "location": violation.location,
                "timestamp": violation.timestamp.isoformat(),
            },
        )

    def get_security_report(self, days: int = 7) -> dict[str, Any]:
        """Generate security report for the specified period"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_violations = [v for v in self.violation_history if v.timestamp > cutoff]

        # Group by category and threat level
        by_category = {}
        by_threat = {}

        for violation in recent_violations:
            # By category
            if violation.category not in by_category:
                by_category[violation.category] = 0
            by_category[violation.category] += 1

            # By threat level
            if violation.threat_level not in by_threat:
                by_threat[violation.threat_level] = 0
            by_threat[violation.threat_level] += 1

        return {
            "period_days": days,
            "total_violations": len(recent_violations),
            "by_category": {k.value: v for k, v in by_category.items()},
            "by_threat_level": {k.value: v for k, v in by_threat.items()},
            "most_recent": recent_violations[-5:] if recent_violations else [],
        }


# Global auditor instance
security_auditor = SecurityAuditor()


def audit_user_input(input_str: str, context: str = "general") -> AuditResult:
    """Convenience function to audit user input"""
    return security_auditor.audit_input(input_str, context)


def audit_command_execution(command: list[str]) -> AuditResult:
    """Convenience function to audit command execution"""
    return security_auditor.audit_command(command)


def generate_secure_config_token() -> str:
    """Generate secure configuration token"""
    return security_auditor.generate_secure_token()
