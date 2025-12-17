"""
Sophia-Security: Security & Hardening Guardian

A specialized Sophia agent with deep expertise in:
- Security auditing and vulnerability detection
- Firewall configuration and network security
- SSL/TLS setup and certificate management
- Permission management and access control
- Security best practices and hardening
"""

from typing import Dict, List, Any, Union
from ..sophia.unified_consciousness import UnifiedSophiaEngine
from ..context import ensure_context, Context


class SophiaSecurity(UnifiedSophiaEngine):
    """
    Security Specialist Agent

    Extends the unified 9-layer consciousness with domain-specific
    knowledge about security, hardening, and best practices.
    """

    def __init__(self):
        """Initialize Sophia-Security specialist"""
        super().__init__()

        # Domain-specific knowledge
        self.specialization = "Security"
        self.expertise_domains = [
            "security",
            "firewall",
            "ssl",
            "permissions",
            "audit",
            "hardening"
        ]

        # Security best practices
        self.security_practices = {
            "firewall": {
                "nixos": "networking.firewall.enable = true;",
                "allow_ports": "networking.firewall.allowedTCPPorts = [ 80 443 ];",
                "block_ping": "networking.firewall.allowPing = false;",
            },
            "ssl": {
                "letsencrypt": "security.acme.acceptTerms = true;",
                "cert_email": "security.acme.defaults.email = \"admin@example.com\";",
                "nginx_ssl": "services.nginx.virtualHosts.\"example.com\".enableACME = true;",
            },
            "users": {
                "disable_root": "users.users.root.hashedPassword = \"!\";",
                "sudo_group": "security.sudo.enable = true;",
                "no_password_sudo": "security.sudo.wheelNeedsPassword = false;",
            },
            "ssh": {
                "disable_password": "services.openssh.settings.PasswordAuthentication = false;",
                "key_only": "services.openssh.settings.PubkeyAuthentication = true;",
                "disable_root_login": "services.openssh.settings.PermitRootLogin = \"no\";",
            }
        }

        # Common vulnerabilities
        self.vulnerability_checks = {
            "weak_permissions": [
                "Check file permissions: ls -la",
                "Fix permissions: chmod 644 file",
                "Secure directories: chmod 755 dir",
            ],
            "open_ports": [
                "Check open ports: ss -tulpn",
                "Close unnecessary ports in firewall",
                "Review running services: systemctl list-units",
            ],
            "weak_passwords": [
                "Enforce strong passwords",
                "Use key-based authentication",
                "Enable two-factor authentication",
            ],
            "outdated_software": [
                "Keep system updated: nixos-rebuild switch --upgrade",
                "Review security advisories",
                "Enable automatic security updates",
            ],
        }

        # Security scanning recommendations
        self.security_tools = {
            "audit": ["lynis", "aide", "rkhunter"],
            "firewall": ["ufw", "iptables", "nftables"],
            "ssl": ["certbot", "acme-client"],
            "monitoring": ["fail2ban", "ossec", "auditd"],
        }

    def respond_to_query(self, query: str, context: Union[Dict[str, Any], Context]) -> Dict[str, Any]:
        """
        Respond to security-related queries with deep domain expertise

        Args:
            query: User query about security
            context: Query context (dict or Context object)

        Returns:
            Enhanced response with security-specific insights
        """
        # Ensure we have a proper Context object
        context = ensure_context(context)

        # Get base response from unified consciousness
        sophia_response = super().respond_to_query(query, context)

        # Convert SophiaResponse to dict for enhancement
        base_response = {
            "message": sophia_response.message,
            "insights": sophia_response.insights.copy(),
            "suggestions": sophia_response.suggestions.copy(),
            "actions": [],
            "confidence": 0.8,  # Default confidence
            "warnings": [],  # Security-specific warnings
        }

        # Enhance with security-specific knowledge
        query_lower = query.lower()

        # Firewall configuration
        if any(word in query_lower for word in ["firewall", "port", "block", "allow"]):
            base_response = self._enhance_firewall_query(query_lower, base_response)

        # SSL/TLS setup
        elif any(word in query_lower for word in ["ssl", "tls", "certificate", "https"]):
            base_response = self._enhance_ssl_query(query_lower, base_response)

        # Permission management
        elif any(word in query_lower for word in ["permission", "chmod", "access", "user"]):
            base_response = self._enhance_permission_query(query_lower, base_response)

        # Security audit
        elif any(word in query_lower for word in ["secure", "audit", "harden", "vulnerability"]):
            base_response = self._enhance_audit_query(query_lower, base_response)

        # Add security-specific confidence boost
        if base_response.get("confidence", 0) < 0.9:
            base_response["confidence"] = min(0.95, base_response.get("confidence", 0.8) + 0.1)

        # Add security warning if needed
        if any(word in query_lower for word in ["disable", "open", "allow all"]):
            warnings = base_response.get("warnings", [])
            warnings.append(
                "⚠️ Security Warning: Ensure you understand the security implications"
            )
            base_response["warnings"] = warnings

        return base_response

    def _enhance_firewall_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance firewall-related queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "🛡️ Security Expert: Firewall Configuration"
        )

        # Add firewall best practices
        for config_line in self.security_practices["firewall"].values():
            suggestions.append(f"Add to configuration.nix: {config_line}")

        # Add security recommendations
        suggestions.extend([
            "Only open necessary ports",
            "Use fail2ban for intrusion prevention",
            "Regularly review firewall rules",
            "Monitor firewall logs",
        ])

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def _enhance_ssl_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance SSL/TLS queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "🔒 SSL/TLS Security:"
        )

        # Add SSL configuration
        suggestions.extend([
            "Use Let's Encrypt for free certificates",
            "Enable ACME for automatic renewal",
            "Configure HTTPS redirects",
            "Use strong cipher suites",
            "Enable HSTS for security",
        ])

        # Add configuration examples
        for config_line in self.security_practices["ssl"].values():
            suggestions.append(f"Config: {config_line}")

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def _enhance_permission_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance permission management queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "🔐 Permission Management:"
        )

        suggestions.extend([
            "Files: 644 (rw-r--r--) for regular files",
            "Executables: 755 (rwxr-xr-x) for scripts",
            "Sensitive files: 600 (rw-------) for private data",
            "Directories: 755 (rwxr-xr-x) for directories",
            "Use sudo for administrative tasks",
        ])

        # Add user management config
        for config_line in self.security_practices["users"].values():
            suggestions.append(f"Config: {config_line}")

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def _enhance_audit_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance security audit queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "🔍 Security Audit Checklist:"
        )

        # Add vulnerability checks
        for vuln_type, checks in self.vulnerability_checks.items():
            insights.append(f"• {vuln_type.replace('_', ' ').title()}")
            suggestions.extend(checks[:2])  # Add first 2 suggestions

        # Add security tool recommendations
        suggestions.append("\n🛠️ Recommended Security Tools:")
        for category, tools in self.security_tools.items():
            suggestions.append(f"{category.title()}: {', '.join(tools[:2])}")

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def get_security_checklist(self) -> List[str]:
        """Get comprehensive security checklist"""
        checklist = []
        checklist.append("✅ Firewall Configuration")
        checklist.extend([f"  • {k}" for k in self.security_practices["firewall"].keys()])

        checklist.append("✅ SSL/TLS Setup")
        checklist.extend([f"  • {k}" for k in self.security_practices["ssl"].keys()])

        checklist.append("✅ User Management")
        checklist.extend([f"  • {k}" for k in self.security_practices["users"].keys()])

        checklist.append("✅ SSH Hardening")
        checklist.extend([f"  • {k}" for k in self.security_practices["ssh"].keys()])

        return checklist

    def assess_security_risk(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Assess security risk level"""
        risks = []

        # Check for common misconfigurations
        if not config.get("firewall_enabled"):
            risks.append(("HIGH", "Firewall not enabled"))

        if config.get("password_auth_enabled"):
            risks.append(("MEDIUM", "Password authentication enabled for SSH"))

        if config.get("root_login_enabled"):
            risks.append(("HIGH", "Root login enabled"))

        # Calculate overall risk
        high_risks = sum(1 for level, _ in risks if level == "HIGH")
        medium_risks = sum(1 for level, _ in risks if level == "MEDIUM")

        if high_risks > 0:
            overall_risk = "HIGH"
        elif medium_risks > 1:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"

        return {
            "overall_risk": overall_risk,
            "high_risks": high_risks,
            "medium_risks": medium_risks,
            "total_risks": len(risks),
            "risks": risks,
        }

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get summary of security expertise"""
        return {
            "specialization": self.specialization,
            "expertise_domains": self.expertise_domains,
            "security_areas": list(self.security_practices.keys()),
            "vulnerability_types": list(self.vulnerability_checks.keys()),
            "security_tools": list(self.security_tools.keys()),
            "confidence_in_domain": 0.98,  # Highest confidence
        }
