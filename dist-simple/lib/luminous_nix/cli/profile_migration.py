#!/usr/bin/env python3
"""
🔄 Automatic Profile Migration for NixOS 25.11+

Handles the transition from nix-env to nix profile automatically.
"""

import subprocess
import os
from pathlib import Path
from typing import List, Tuple, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ProfileMigrator:
    """Automatic profile migration handler"""
    
    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.home = Path.home()
        self.old_profile = self.home / ".nix-profile"
        self.backup_file = self.home / ".nix-profile-backup.json"
        
    def needs_migration(self) -> bool:
        """Check if profile needs migration"""
        try:
            result = subprocess.run(
                ["nix", "profile", "list"],
                capture_output=True,
                text=True
            )
            
            # Check for the specific incompatibility error
            if result.returncode != 0:
                return "incompatible with 'nix-env'" in result.stderr
                
            return False
            
        except Exception as e:
            logger.debug(f"Could not check profile status: {e}")
            return False
            
    def get_installed_packages(self) -> List[str]:
        """Get list of packages installed with nix-env"""
        try:
            result = subprocess.run(
                ["nix-env", "-q", "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse JSON output
                packages_data = json.loads(result.stdout)
                # Extract package names
                packages = []
                for pkg_name in packages_data.keys():
                    # Extract base package name (before version)
                    base_name = pkg_name.rsplit('-', 1)[0] if '-' in pkg_name else pkg_name
                    packages.append(base_name)
                return packages
                
            # Fallback to simple text parsing
            result = subprocess.run(
                ["nix-env", "-q"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                packages = []
                for line in lines:
                    if line:
                        # Extract package name (before version number)
                        parts = line.split('-')
                        # Handle cases like python3-3.11.0
                        if len(parts) > 1 and parts[-1][0].isdigit():
                            package = '-'.join(parts[:-1])
                        else:
                            package = parts[0]
                        packages.append(package)
                return packages
                
        except Exception as e:
            logger.error(f"Failed to get installed packages: {e}")
            
        return []
        
    def backup_profile(self, packages: List[str]) -> bool:
        """Backup current profile information"""
        try:
            backup_data = {
                'packages': packages,
                'timestamp': subprocess.run(
                    ["date", "+%Y-%m-%d %H:%M:%S"],
                    capture_output=True,
                    text=True
                ).stdout.strip(),
                'profile_path': str(self.old_profile)
            }
            
            with open(self.backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
                
            print(f"✅ Profile backed up to {self.backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup profile: {e}")
            return False
            
    def remove_old_profile(self) -> bool:
        """Remove old nix-env profile"""
        try:
            if self.old_profile.exists():
                # Use rm -rf for complete removal
                result = subprocess.run(
                    ["rm", "-rf", str(self.old_profile)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("✅ Old profile removed")
                    return True
                else:
                    print(f"⚠️  Could not remove old profile: {result.stderr}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove old profile: {e}")
            return False
            
    def install_packages(self, packages: List[str]) -> Tuple[List[str], List[str]]:
        """Install packages with new nix profile command"""
        successful = []
        failed = []
        
        for package in packages:
            try:
                print(f"📦 Installing {package}...")
                result = subprocess.run(
                    ["nix", "profile", "install", f"nixpkgs#{package}"],
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout per package
                )
                
                if result.returncode == 0:
                    successful.append(package)
                    print(f"  ✅ {package} installed")
                else:
                    # Check if already installed
                    if "already installed" in result.stderr:
                        successful.append(package)
                        print(f"  ℹ️  {package} already installed")
                    else:
                        failed.append(package)
                        print(f"  ❌ {package} failed: {result.stderr[:100]}")
                        
            except subprocess.TimeoutExpired:
                failed.append(package)
                print(f"  ⏱️  {package} timed out")
            except Exception as e:
                failed.append(package)
                print(f"  ❌ {package} error: {e}")
                
        return successful, failed
        
    def migrate_automatically(self) -> bool:
        """Perform automatic migration"""
        print("\n🔄 Starting Automatic Profile Migration")
        print("=" * 50)
        
        # Step 1: Get installed packages
        print("\n1️⃣ Detecting installed packages...")
        packages = self.get_installed_packages()
        
        if not packages:
            print("  ℹ️  No packages found in old profile")
            # Still need to remove old profile
            if self.remove_old_profile():
                print("\n✅ Migration complete! (no packages to migrate)")
                return True
            else:
                print("\n❌ Migration failed: could not remove old profile")
                return False
                
        print(f"  Found {len(packages)} packages: {', '.join(packages[:5])}")
        if len(packages) > 5:
            print(f"  ... and {len(packages)-5} more")
            
        # Step 2: Backup profile
        print("\n2️⃣ Backing up profile information...")
        if not self.backup_profile(packages):
            print("  ⚠️  Backup failed, but continuing...")
            
        # Step 3: Remove old profile
        print("\n3️⃣ Removing old nix-env profile...")
        if not self.remove_old_profile():
            print("  ❌ Could not remove old profile")
            print("  Try manually: rm -rf ~/.nix-profile")
            return False
            
        # Step 4: Install packages with new system
        print(f"\n4️⃣ Reinstalling {len(packages)} packages with nix profile...")
        successful, failed = self.install_packages(packages)
        
        # Step 5: Report results
        print("\n" + "=" * 50)
        print("📊 Migration Results:")
        print(f"  ✅ Successfully migrated: {len(successful)} packages")
        if failed:
            print(f"  ❌ Failed to migrate: {len(failed)} packages")
            print(f"     Failed packages: {', '.join(failed)}")
            print(f"\n  You can manually install failed packages with:")
            for pkg in failed[:3]:
                print(f"    nix profile install nixpkgs#{pkg}")
        else:
            print("  🎉 All packages migrated successfully!")
            
        print("\n✅ Profile migration complete!")
        
        if self.backup_file.exists():
            print(f"\n💾 Backup saved at: {self.backup_file}")
            print("  You can review it for reference")
            
        return len(failed) == 0
        
    def migrate_interactively(self) -> bool:
        """Interactive migration with user prompts"""
        print("\n⚠️  Profile Migration Required")
        print("Your Nix profile needs migration from nix-env to nix profile")
        print("This is a one-time migration for NixOS 25.11+")
        
        packages = self.get_installed_packages()
        
        if packages:
            print(f"\nFound {len(packages)} installed packages")
            print("First 10 packages:")
            for pkg in packages[:10]:
                print(f"  • {pkg}")
            if len(packages) > 10:
                print(f"  ... and {len(packages)-10} more")
                
        print("\nOptions:")
        print("1. Automatic migration (recommended)")
        print("2. Manual migration instructions")
        print("3. Cancel")
        
        choice = input("\nYour choice (1/2/3): ").strip()
        
        if choice == "1":
            return self.migrate_automatically()
        elif choice == "2":
            print("\nManual Migration Steps:")
            print("1. List current packages: nix-env -q > packages.txt")
            print("2. Remove old profile: rm -rf ~/.nix-profile")
            print("3. Install packages with: nix profile install nixpkgs#<package>")
            print("\nExample for your packages:")
            for pkg in packages[:3]:
                print(f"  nix profile install nixpkgs#{pkg}")
            return False
        else:
            print("Migration cancelled")
            return False
            
    def migrate(self) -> bool:
        """Main migration entry point"""
        if not self.needs_migration():
            return True  # No migration needed
            
        if self.interactive:
            return self.migrate_interactively()
        else:
            return self.migrate_automatically()


def auto_migrate_profile(interactive: bool = False) -> bool:
    """
    Convenience function for automatic profile migration
    
    Args:
        interactive: Whether to prompt user for choices
        
    Returns:
        True if migration successful or not needed
    """
    migrator = ProfileMigrator(interactive=interactive)
    return migrator.migrate()


if __name__ == "__main__":
    # Test the migrator
    import sys
    
    interactive = "--interactive" in sys.argv or "-i" in sys.argv
    
    migrator = ProfileMigrator(interactive=interactive)
    
    if migrator.needs_migration():
        print("Profile migration needed!")
        success = migrator.migrate()
        sys.exit(0 if success else 1)
    else:
        print("✅ Profile is already compatible with nix profile")
        sys.exit(0)