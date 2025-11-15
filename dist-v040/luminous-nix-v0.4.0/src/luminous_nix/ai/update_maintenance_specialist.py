"""
Update and Maintenance Specialist for Luminous Nix
Handles system update, upgrade, and maintenance queries with high accuracy
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class UpdateMaintenanceSpecialist:
    """Specialized handler for update and maintenance queries (fixing 50% accuracy)"""

    def __init__(self):
        # Comprehensive patterns for update/maintenance operations
        self.update_patterns = {
            # System updates
            r"(update|upgrade).*(system|nixos)": {
                "command": "sudo nixos-rebuild switch",
                "description": "Update NixOS system configuration",
                "confidence": 0.95,
                "note": "Updates system to latest configuration",
            },
            r"update\s+(all|everything)": {
                "command": "sudo nixos-rebuild switch --upgrade",
                "description": "Update system and all packages",
                "confidence": 0.95,
                "note": "Upgrades entire system including channel",
            },
            r"(nixos-rebuild|rebuild).*(switch|update)": {
                "command": "sudo nixos-rebuild switch",
                "description": "Rebuild and switch to new configuration",
                "confidence": 0.98,
                "note": "Standard NixOS update command",
            },
            # Channel updates
            r"update.*(channel|channels)": {
                "command": "sudo nix-channel --update",
                "description": "Update NixOS channels",
                "confidence": 0.95,
                "note": "Fetches latest package definitions",
            },
            r"upgrade.*(channel|nixpkgs)": {
                "command": "sudo nix-channel --update && sudo nixos-rebuild switch",
                "description": "Update channels and rebuild",
                "confidence": 0.93,
                "note": "Full system upgrade",
            },
            # Garbage collection (NEW for v0.3.1)
            r"(gc|garbage[\s-]?collect|clean).*old.*generations?": {
                "command": "nix-collect-garbage -d",
                "description": "Delete old generations and garbage collect",
                "confidence": 0.95,
                "note": "Frees disk space by removing old system generations",
            },
            r"(garbage[\s-]?collect|gc|clean[\s-]?up)": {
                "command": "nix-collect-garbage",
                "description": "Run garbage collection",
                "confidence": 0.90,
                "note": "Removes unreferenced store paths",
            },
            r"delete.*old.*generations?": {
                "command": "nix-collect-garbage -d",
                "description": "Delete old generations",
                "confidence": 0.93,
                "note": "Removes all non-current generations",
            },
            r"free.*disk.*space": {
                "command": "nix-collect-garbage -d",
                "description": "Free disk space by garbage collecting",
                "confidence": 0.88,
                "note": "Removes old generations and unused packages",
            },
            r"clean.*nix.*store": {
                "command": "nix-store --gc",
                "description": "Clean the Nix store",
                "confidence": 0.90,
                "note": "Garbage collect the Nix store",
            },
            r"optimize.*store": {
                "command": "nix-store --optimise",
                "description": "Optimize Nix store (deduplicate)",
                "confidence": 0.92,
                "note": "Saves space by hard-linking identical files",
            },
            # Generation management (NEW for v0.3.1)
            r"list.*generations?": {
                "command": "nix-env --list-generations",
                "description": "List all generations",
                "confidence": 0.95,
                "note": "Shows all system and user generations",
            },
            r"show.*generations?": {
                "command": "sudo nix-env --list-generations --profile /nix/var/nix/profiles/system",
                "description": "Show system generations",
                "confidence": 0.93,
                "note": "Lists all system generations",
            },
            r"switch.*generation\s+(\d+)": {
                "command": "sudo nix-env --switch-generation \\1 --profile /nix/var/nix/profiles/system",
                "description": "Switch to specific generation",
                "confidence": 0.90,
                "note": "Switches to a specific generation number",
            },
            r"delete.*generation\s+(\d+)": {
                "command": "sudo nix-env --delete-generations \\1 --profile /nix/var/nix/profiles/system",
                "description": "Delete specific generation",
                "confidence": 0.90,
                "note": "Removes a specific generation",
            },
            # Package updates
            r"update.*(package|packages|pkgs)": {
                "command": "nix-env -u",
                "description": "Update user packages",
                "confidence": 0.90,
                "note": "Updates packages in user profile",
            },
            r"upgrade.*(package|packages|all)": {
                "command": "nix-env -u '*'",
                "description": "Upgrade all user packages",
                "confidence": 0.90,
                "note": "Upgrades everything in user profile",
            },
            # Specific package updates
            r"update\s+(\w+)$": {
                "command": "nix-env -u {package}",
                "description": "Update specific package",
                "confidence": 0.85,
                "note": "Updates named package only",
            },
            # Garbage collection and cleanup
            r"(clean|cleanup|garbage).*(old|generations|system)": {
                "command": "sudo nix-collect-garbage -d",
                "description": "Clean old generations and garbage",
                "confidence": 0.95,
                "note": "Frees disk space",
            },
            r"(remove|delete).*(old|previous).*(generations|systems)": {
                "command": "sudo nix-env --delete-generations old",
                "description": "Delete old generations",
                "confidence": 0.93,
                "note": "Removes previous system versions",
            },
            r"free.*(space|disk)": {
                "command": "sudo nix-collect-garbage -d",
                "description": "Free disk space",
                "confidence": 0.90,
                "note": "Removes unreferenced packages",
            },
            # Rollback operations
            r"(rollback|revert|undo).*(update|upgrade|system)": {
                "command": "sudo nixos-rebuild switch --rollback",
                "description": "Rollback to previous generation",
                "confidence": 0.95,
                "note": "Reverts last system change",
            },
            r"(previous|last).*(generation|system|config)": {
                "command": "sudo nixos-rebuild switch --rollback",
                "description": "Switch to previous generation",
                "confidence": 0.90,
                "note": "Goes back one generation",
            },
            # Generation management
            r"list.*(generations|history|versions)": {
                "command": "sudo nix-env --list-generations",
                "description": "List system generations",
                "confidence": 0.95,
                "note": "Shows all system versions",
            },
            r"switch.*generation\s+(\d+)": {
                "command": "sudo nix-env --switch-generation {number}",
                "description": "Switch to specific generation",
                "confidence": 0.93,
                "note": "Activates specific version",
            },
            # Repair and maintenance
            r"(repair|fix).*(store|nix|system)": {
                "command": "sudo nix-store --verify --check-contents --repair",
                "description": "Repair Nix store",
                "confidence": 0.90,
                "note": "Fixes corrupted store paths",
            },
            r"(verify|check).*(store|system|integrity)": {
                "command": "sudo nix-store --verify --check-contents",
                "description": "Verify store integrity",
                "confidence": 0.90,
                "note": "Checks for corruption",
            },
            # Optimize operations
            r"(optimize|optimise).*(store|nix|system)": {
                "command": "sudo nix-store --optimise",
                "description": "Optimize Nix store",
                "confidence": 0.93,
                "note": "Deduplicates store files",
            },
            # Flake updates
            r"(update|upgrade).*flake": {
                "command": "nix flake update",
                "description": "Update flake inputs",
                "confidence": 0.95,
                "note": "Updates flake.lock",
            },
            r"flake.*(update|upgrade)": {
                "command": "nix flake update",
                "description": "Update flake dependencies",
                "confidence": 0.95,
                "note": "Refreshes all inputs",
            },
            # Home Manager updates
            r"(update|upgrade).*home.?manager": {
                "command": "home-manager switch",
                "description": "Update Home Manager configuration",
                "confidence": 0.90,
                "note": "Applies user config changes",
            },
            # Check for updates
            r"check.*(updates|upgrades|available)": {
                "command": "nix-channel --update --dry-run",
                "description": "Check for available updates",
                "confidence": 0.85,
                "note": "Shows what would be updated",
            },
        }

        # Common variations and aliases
        self.aliases = {
            "update": ["update", "upgrade", "refresh", "sync"],
            "system": ["system", "nixos", "os", "machine"],
            "clean": ["clean", "cleanup", "garbage", "gc", "purge"],
            "rollback": ["rollback", "revert", "undo", "restore"],
        }

        # Safety checks for dangerous operations
        self.requires_confirmation = [
            "nix-collect-garbage -d",
            "nix-env --delete-generations",
            "nixos-rebuild switch --upgrade",
        ]

    def handle_query(self, query: str) -> Optional[Dict]:
        """
        Handle update and maintenance queries
        Returns command, description, and confidence
        """
        query_lower = query.lower().strip()

        # First, try exact pattern matching
        for pattern, result in self.update_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                logger.info(f"Matched update pattern: {pattern}")

                # Handle parameterized commands
                command = result["command"]
                if "{package}" in command and match.groups():
                    command = command.format(package=match.group(1))
                elif "{number}" in command and match.groups():
                    command = command.format(number=match.group(1))

                return {
                    "command": command,
                    "description": result["description"],
                    "confidence": result["confidence"],
                    "note": result.get("note", ""),
                    "type": "maintenance_command",
                    "requires_confirmation": command in self.requires_confirmation,
                }

        # Second, try fuzzy matching with aliases
        fuzzy_result = self._fuzzy_match(query_lower)
        if fuzzy_result:
            return fuzzy_result

        # Third, check for general update intent
        if self._is_update_query(query_lower):
            return self._suggest_update_command(query_lower)

        return None

    def _fuzzy_match(self, query: str) -> Optional[Dict]:
        """Try fuzzy matching with common variations"""
        # Normalize query using aliases
        normalized = query
        for key, variations in self.aliases.items():
            for variant in variations:
                if variant in normalized:
                    normalized = normalized.replace(variant, key)

        # Try matching again with normalized query
        for pattern, result in self.update_patterns.items():
            if re.search(pattern, normalized):
                return {
                    "command": result["command"],
                    "description": result["description"],
                    "confidence": result["confidence"]
                    * 0.9,  # Slightly lower for fuzzy
                    "note": result.get("note", ""),
                    "type": "maintenance_command",
                }

        return None

    def _is_update_query(self, query: str) -> bool:
        """Check if query is about updates/maintenance"""
        update_keywords = [
            "update",
            "upgrade",
            "refresh",
            "sync",
            "clean",
            "garbage",
            "rollback",
            "revert",
            "generation",
            "maintain",
            "maintenance",
        ]
        return any(keyword in query for keyword in update_keywords)

    def _suggest_update_command(self, query: str) -> Dict:
        """Suggest most likely update command based on context"""
        if "package" in query:
            command = "nix-env -u"
            description = "Update user packages"
        elif "channel" in query:
            command = "sudo nix-channel --update"
            description = "Update NixOS channels"
        elif "clean" in query or "garbage" in query:
            command = "sudo nix-collect-garbage -d"
            description = "Clean old generations"
        elif "rollback" in query or "revert" in query:
            command = "sudo nixos-rebuild switch --rollback"
            description = "Rollback system"
        else:
            command = "sudo nixos-rebuild switch"
            description = "Update system configuration"

        return {
            "command": command,
            "description": description,
            "confidence": 0.70,  # Lower confidence for suggestions
            "note": "Suggested based on context",
            "type": "maintenance_command",
        }

    def get_training_examples(self) -> List[Tuple[str, str]]:
        """Generate training examples for the neural network"""
        examples = []

        # Generate variations for each update operation
        templates = [
            "update system",
            "upgrade nixos",
            "update all packages",
            "clean old generations",
            "rollback system",
            "check for updates",
            "update channels",
            "optimize nix store",
            "repair nix store",
            "list generations",
        ]

        # Add variations
        for template in templates:
            examples.append((template, self.handle_query(template)["command"]))
            examples.append(
                (f"please {template}", self.handle_query(template)["command"])
            )
            examples.append(
                (f"how to {template}", self.handle_query(template)["command"])
            )
            examples.append(
                (f"I want to {template}", self.handle_query(template)["command"])
            )

        return examples

    def validate_command(self, command: str) -> Dict:
        """Validate update command and provide safety information"""
        validation = {
            "safe": True,
            "requires_sudo": "sudo" in command,
            "destructive": False,
            "reversible": True,
            "warnings": [],
        }

        # Check for destructive operations
        if "collect-garbage -d" in command:
            validation["destructive"] = True
            validation["warnings"].append(
                "This will permanently delete old generations"
            )

        if "delete-generations" in command:
            validation["destructive"] = True
            validation["warnings"].append("This will remove system restore points")

        if "--upgrade" in command:
            validation["warnings"].append(
                "This will update all packages to latest versions"
            )

        # Check for operations that can't be easily reversed
        if "nix-store --optimise" in command:
            validation["reversible"] = False
            validation["warnings"].append("Store optimization cannot be undone")

        return validation
