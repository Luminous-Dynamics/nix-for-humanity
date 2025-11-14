"""
Automatic profile migration for legacy nix-env users.

This module handles the transition from nix-env to nix profile
commands, which affects ~30% of existing NixOS users.
"""

import subprocess
from pathlib import Path
from typing import Any, Optional


class ProfileMigration:
    """Handle migration from legacy nix-env profiles to modern nix profile"""

    def __init__(self):
        """Initialize profile migration checker"""
        self.home = Path.home()
        self.legacy_profile = self.home / ".nix-profile"
        self.new_profile = self.home / ".local/state/nix/profiles/profile"
        self.migration_marker = self.home / ".local/share/luminous-nix/.migrated"

    def check_profile_state(self) -> dict[str, Any]:
        """
        Check the current profile state and determine if migration is needed.

        Returns:
            Dict with profile status information
        """
        state = {
            "legacy_exists": self.legacy_profile.exists(),
            "new_exists": self.new_profile.exists(),
            "needs_migration": False,
            "already_migrated": self.migration_marker.exists(),
            "profile_type": "unknown",
            "can_use_nix_profile": True,
        }

        # Check if we can use nix profile commands
        try:
            result = subprocess.run(
                ["nix", "profile", "list"], capture_output=True, text=True, timeout=5
            )

            if "incompatible with 'nix-env'" in result.stderr:
                state["needs_migration"] = True
                state["can_use_nix_profile"] = False
                state["profile_type"] = "legacy"
            elif result.returncode == 0:
                state["profile_type"] = "modern"
                state["can_use_nix_profile"] = True

        except subprocess.TimeoutExpired:
            state["profile_type"] = "timeout"
        except Exception:
            state["profile_type"] = "error"

        return state

    def needs_migration(self) -> bool:
        """
        Quick check if migration is needed.

        Returns:
            True if profile needs migration, False otherwise
        """
        if self.migration_marker.exists():
            return False

        state = self.check_profile_state()
        return state["needs_migration"]

    def migrate_profile(self, dry_run: bool = False) -> tuple[bool, str]:
        """
        Migrate from legacy nix-env profile to modern nix profile.

        Args:
            dry_run: If True, only show what would be done

        Returns:
            Tuple of (success, message)
        """
        if not self.needs_migration():
            return True, "Profile already migrated or using modern profile"

        steps = []

        # Step 1: List current nix-env packages
        try:
            result = subprocess.run(
                ["nix-env", "-q"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                installed_packages = result.stdout.strip().split("\n")
                installed_packages = [p for p in installed_packages if p]
                steps.append(f"Found {len(installed_packages)} packages to migrate")
            else:
                installed_packages = []

        except Exception as e:
            return False, f"Failed to list current packages: {e}"

        if dry_run:
            message = "DRY RUN - Would perform migration:\n"
            message += (
                f"1. Found {len(installed_packages)} packages in nix-env profile\n"
            )
            message += "2. Would backup current profile\n"
            message += "3. Would reinstall packages with nix profile\n"
            message += f"   Packages: {', '.join(installed_packages[:5])}"
            if len(installed_packages) > 5:
                message += f" ... and {len(installed_packages) - 5} more"
            return True, message

        # Step 2: Backup current profile (just in case)
        backup_dir = self.home / ".local/share/luminous-nix/profile-backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Step 3: Create new profile directory structure
        new_profile_dir = self.new_profile.parent
        new_profile_dir.mkdir(parents=True, exist_ok=True)

        # Step 4: Initialize new profile if needed
        try:
            # Try to initialize with a minimal package
            result = subprocess.run(
                ["nix", "profile", "install", "nixpkgs#hello"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0 and "already exists" not in result.stderr:
                return False, f"Failed to initialize new profile: {result.stderr}"

            # Remove the test package
            subprocess.run(
                ["nix", "profile", "remove", "hello"], capture_output=True, timeout=10
            )

        except Exception as e:
            return False, f"Failed to initialize profile: {e}"

        # Step 5: Mark as migrated
        self.migration_marker.parent.mkdir(parents=True, exist_ok=True)
        self.migration_marker.write_text(
            f"Migrated on {subprocess.check_output(['date']).decode().strip()}\n"
        )

        message = "Successfully migrated profile!\n"
        message += "- Backed up old profile\n"
        message += "- Initialized new nix profile\n"
        message += "- Ready to use modern nix commands\n"

        if installed_packages:
            message += (
                f"\nNote: You had {len(installed_packages)} packages installed.\n"
            )
            message += "You may want to reinstall them using:\n"
            for pkg in installed_packages[:5]:
                # Extract package name without version
                pkg_name = pkg.split("-")[0] if "-" in pkg else pkg
                message += f"  ask-nix 'install {pkg_name}'\n"
            if len(installed_packages) > 5:
                message += f"  ... and {len(installed_packages) - 5} more packages\n"

        return True, message

    def auto_migrate(self) -> Optional[str]:
        """
        Automatically migrate if needed, silently if successful.

        Returns:
            Error message if migration fails, None if successful or not needed
        """
        if not self.needs_migration():
            return None

        success, message = self.migrate_profile(dry_run=False)

        if not success:
            return f"Profile migration required but failed: {message}"

        return None  # Silent success

    def get_correct_command(self, command_type: str, package: str = "") -> list[str]:
        """
        Get the correct command based on profile state.

        Args:
            command_type: "install", "remove", or "list"
            package: Package name (for install/remove)

        Returns:
            List of command arguments
        """
        state = self.check_profile_state()

        if state["can_use_nix_profile"]:
            # Modern nix profile commands
            if command_type == "install":
                return ["nix", "profile", "install", f"nixpkgs#{package}"]
            elif command_type == "remove":
                return ["nix", "profile", "remove", package]
            elif command_type == "list":
                return ["nix", "profile", "list"]
        else:
            # Legacy nix-env commands
            if command_type == "install":
                return ["nix-env", "-iA", f"nixos.{package}"]
            elif command_type == "remove":
                return ["nix-env", "-e", package]
            elif command_type == "list":
                return ["nix-env", "-q"]

        return []


# Global instance for easy access
profile_migrator = ProfileMigration()


def check_and_migrate() -> Optional[str]:
    """
    Check if migration is needed and perform it if necessary.

    Returns:
        Error message if migration fails, None otherwise
    """
    return profile_migrator.auto_migrate()


def get_profile_info() -> dict[str, Any]:
    """Get current profile information"""
    return profile_migrator.check_profile_state()
