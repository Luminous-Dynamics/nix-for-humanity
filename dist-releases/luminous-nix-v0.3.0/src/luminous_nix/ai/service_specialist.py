#!/usr/bin/env python3
"""
ServiceSpecialist - Handles systemd service operations
Part of v0.3.1 critical fixes to differentiate service operations from package installation
"""

from typing import Dict, List, Optional
import re


class ServiceSpecialist:
    """Specialist for systemd service operations"""

    def __init__(self):
        # Common services that users often confuse with packages
        self.common_services = {
            "docker": "docker.service",
            "ssh": "sshd.service",
            "nginx": "nginx.service",
            "apache": "httpd.service",
            "mysql": "mysql.service",
            "postgres": "postgresql.service",
            "postgresql": "postgresql.service",
            "bluetooth": "bluetooth.service",
            "cups": "cups.service",
            "network": "NetworkManager.service",
            "firewall": "firewall.service",
            "ntp": "ntpd.service",
            "cron": "cron.service",
            "redis": "redis.service",
            "mongodb": "mongodb.service",
            "elasticsearch": "elasticsearch.service",
            "jenkins": "jenkins.service",
            "gitlab": "gitlab.service",
            "nextcloud": "nextcloud.service",
            "syncthing": "syncthing.service",
            "transmission": "transmission.service",
            "plex": "plex.service",
            "jellyfin": "jellyfin.service",
        }

        self.patterns = {
            "enable": [
                r"enable\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"start\s+(?:the\s+)?(\w+)\s+(?:service\s+)?(?:on|at)\s+boot",
                r"(?:auto[\s-]?start|autostart)\s+(\w+)",
                r"make\s+(\w+)\s+(?:start|run)\s+(?:on|at)\s+boot",
                r"systemctl\s+enable\s+(\w+)",
            ],
            "disable": [
                r"disable\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"stop\s+(?:the\s+)?(\w+)\s+(?:from\s+)?(?:starting|running)\s+(?:on|at)\s+boot",
                r"prevent\s+(\w+)\s+(?:from\s+)?(?:auto[\s-]?start|autostart)",
                r"systemctl\s+disable\s+(\w+)",
            ],
            "start": [
                r"start\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"run\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"launch\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"systemctl\s+start\s+(\w+)",
            ],
            "stop": [
                r"stop\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"kill\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"terminate\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"systemctl\s+stop\s+(\w+)",
            ],
            "restart": [
                r"restart\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"reload\s+(?:the\s+)?(\w+)(?:\s+service)?",
                r"systemctl\s+restart\s+(\w+)",
            ],
            "status": [
                r"(?:check\s+)?status\s+(?:of\s+)?(?:the\s+)?(\w+)(?:\s+service)?",
                r"is\s+(\w+)\s+running",
                r"show\s+(\w+)\s+(?:service\s+)?status",
                r"systemctl\s+status\s+(\w+)",
            ],
        }

    def can_handle(self, query: str) -> bool:
        """Check if this specialist can handle the query"""
        query_lower = query.lower()

        # Check for service-related keywords
        service_keywords = [
            "service",
            "systemctl",
            "systemd",
            "enable",
            "disable",
            "start",
            "stop",
            "restart",
            "daemon",
            "running",
            "status",
        ]

        # Check if query contains service keywords
        if any(kw in query_lower for kw in service_keywords):
            return True

        # Check if query mentions a known service with action verb
        action_verbs = ["enable", "disable", "start", "stop", "restart", "check"]
        for service in self.common_services:
            if service in query_lower and any(
                verb in query_lower for verb in action_verbs
            ):
                return True

        # Check patterns
        for patterns in self.patterns.values():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return True

        return False

    def handle_query(self, query: str) -> Dict:
        """Process a service-related query"""
        query_lower = query.lower()

        # Find the operation and service
        operation = None
        service_name = None
        confidence = 0.5

        for op, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    operation = op
                    service_name = match.group(1) if match.lastindex else None
                    confidence = 0.9
                    break
            if operation:
                break

        # If we found a service name, try to resolve it
        if service_name:
            # Check if it's a known service
            if service_name in self.common_services:
                service_name = self.common_services[service_name]
                confidence = 0.95
            else:
                # Add .service suffix if not present
                if not service_name.endswith(".service"):
                    service_name = f"{service_name}.service"
                confidence = 0.85

        # Generate command based on operation
        if operation and service_name:
            commands = {
                "enable": f"sudo systemctl enable {service_name}",
                "disable": f"sudo systemctl disable {service_name}",
                "start": f"sudo systemctl start {service_name}",
                "stop": f"sudo systemctl stop {service_name}",
                "restart": f"sudo systemctl restart {service_name}",
                "status": f"systemctl status {service_name}",
            }

            explanations = {
                "enable": f"Enable {service_name} to start at boot",
                "disable": f"Disable {service_name} from starting at boot",
                "start": f"Start {service_name} immediately",
                "stop": f"Stop {service_name} immediately",
                "restart": f"Restart {service_name}",
                "status": f"Check status of {service_name}",
            }

            return {
                "command": commands[operation],
                "explanation": explanations[operation],
                "category": "service",
                "confidence": confidence,
                "specialist": "ServiceSpecialist",
                "alternatives": self._get_alternatives(operation, service_name),
                "note": self._get_note(operation, service_name),
            }

        # Check if user is confusing service with package install
        if any(word in query_lower for word in ["install", "get", "add"]):
            for service, service_file in self.common_services.items():
                if service in query_lower:
                    return {
                        "command": f"nix-env -iA nixpkgs.{service}",
                        "explanation": f"Install {service} package (not enable service)",
                        "category": "package",
                        "confidence": 0.7,
                        "specialist": "ServiceSpecialist",
                        "alternatives": [
                            f"sudo systemctl enable {service_file}",
                            f"sudo systemctl start {service_file}",
                        ],
                        "note": f"To install the package use the command above. To enable the service after installation, use: sudo systemctl enable {service_file}",
                    }

        # Default fallback
        return {
            "command": "systemctl list-units --type=service",
            "explanation": "List all available services",
            "category": "service",
            "confidence": 0.5,
            "specialist": "ServiceSpecialist",
            "alternatives": [
                "systemctl list-unit-files --type=service",
                "systemctl --help",
            ],
        }

    def _get_alternatives(self, operation: str, service_name: str) -> List[str]:
        """Get alternative commands"""
        alternatives = []

        if operation == "enable":
            alternatives = [
                f"sudo systemctl enable --now {service_name}",  # Enable and start
                f"sudo systemctl start {service_name}",  # Just start
            ]
        elif operation == "disable":
            alternatives = [
                f"sudo systemctl disable --now {service_name}",  # Disable and stop
                f"sudo systemctl stop {service_name}",  # Just stop
            ]
        elif operation == "start":
            alternatives = [
                f"sudo systemctl enable --now {service_name}",  # Enable and start
                f"sudo systemctl restart {service_name}",  # Restart instead
            ]
        elif operation == "status":
            alternatives = [
                f"sudo systemctl is-active {service_name}",  # Simple active check
                f"sudo journalctl -u {service_name} -n 20",  # View logs
            ]

        return alternatives

    def _get_note(self, operation: str, service_name: str) -> Optional[str]:
        """Get helpful note for the operation"""
        notes = {
            "enable": "This will make the service start automatically at boot",
            "disable": "This will prevent the service from starting at boot",
            "start": "This starts the service immediately but does not enable it at boot",
            "stop": "This stops the service immediately but does not disable it at boot",
            "restart": "This will stop and start the service, useful after configuration changes",
            "status": "This shows if the service is running and recent log entries",
        }
        return notes.get(operation)

    def get_common_tasks(self) -> List[Dict]:
        """Return common service tasks"""
        return [
            {
                "task": "Enable Docker service",
                "command": "sudo systemctl enable docker.service",
                "frequency": "very_common",
            },
            {
                "task": "Start SSH service",
                "command": "sudo systemctl start sshd.service",
                "frequency": "common",
            },
            {
                "task": "Check nginx status",
                "command": "systemctl status nginx.service",
                "frequency": "common",
            },
            {
                "task": "Restart bluetooth",
                "command": "sudo systemctl restart bluetooth.service",
                "frequency": "common",
            },
            {
                "task": "List all services",
                "command": "systemctl list-units --type=service",
                "frequency": "occasional",
            },
        ]
