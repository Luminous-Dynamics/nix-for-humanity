#!/usr/bin/env python3
"""
📦 NixOS Package Management Interface Generator
Creates interactive UIs for real NixOS package operations
"""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext


@dataclass
class NixPackage:
    """Represents a NixOS package"""

    name: str
    version: str
    description: str
    installed: bool
    channel: str = "nixpkgs"
    size: int | None = None


class NixOSPackageInterface:
    """Generates package management interfaces connected to real NixOS"""

    def __init__(self):
        self.builder = NLInterfaceBuilderV2(use_llm=False)  # Fast NLP mode
        self.packages_cache = {}
        self._refresh_package_list()

    def _run_nix_command(self, command: list[str]) -> str | None:
        """Run a nix command and return output"""
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout
            print(f"Error running {command}: {result.stderr}")
            return None
        except subprocess.TimeoutExpired:
            print(f"Command timed out: {command}")
            return None
        except Exception as e:
            print(f"Failed to run command: {e}")
            return None

    def _refresh_package_list(self):
        """Get list of available packages"""
        # For demo, use a subset of common packages
        # In production, would query nix-env -qa
        self.packages_cache = {
            "firefox": NixPackage(
                name="firefox",
                version="122.0",
                description="Mozilla Firefox web browser",
                installed=self._is_installed("firefox"),
            ),
            "chromium": NixPackage(
                name="chromium",
                version="121.0",
                description="Open source web browser from Google",
                installed=self._is_installed("chromium"),
            ),
            "vim": NixPackage(
                name="vim",
                version="9.1",
                description="Highly configurable text editor",
                installed=self._is_installed("vim"),
            ),
            "emacs": NixPackage(
                name="emacs",
                version="29.2",
                description="Extensible, customizable text editor",
                installed=self._is_installed("emacs"),
            ),
            "git": NixPackage(
                name="git",
                version="2.43",
                description="Distributed version control system",
                installed=self._is_installed("git"),
            ),
            "htop": NixPackage(
                name="htop",
                version="3.3.0",
                description="Interactive process viewer",
                installed=self._is_installed("htop"),
            ),
            "neofetch": NixPackage(
                name="neofetch",
                version="7.1.0",
                description="System information tool",
                installed=self._is_installed("neofetch"),
            ),
            "tree": NixPackage(
                name="tree",
                version="2.1.1",
                description="Display directories as trees",
                installed=self._is_installed("tree"),
            ),
        }

    def _is_installed(self, package_name: str) -> bool:
        """Check if a package is installed"""
        output = self._run_nix_command(["nix-env", "-q", package_name])
        return output is not None and package_name in output

    def search_packages(self, query: str) -> list[NixPackage]:
        """Search for packages matching query"""
        results = []
        query_lower = query.lower()

        for name, package in self.packages_cache.items():
            if (
                query_lower in name.lower()
                or query_lower in package.description.lower()
            ):
                results.append(package)

        return results

    def install_package(self, package_name: str, dry_run: bool = True) -> dict:
        """Install a NixOS package"""
        if dry_run:
            return {
                "success": True,
                "message": f"Would install {package_name}",
                "command": f"nix-env -i {package_name}",
            }

        output = self._run_nix_command(["nix-env", "-i", package_name])

        if output:
            # Update cache
            if package_name in self.packages_cache:
                self.packages_cache[package_name].installed = True

            return {
                "success": True,
                "message": f"Installed {package_name}",
                "output": output,
            }
        return {"success": False, "message": f"Failed to install {package_name}"}

    def remove_package(self, package_name: str, dry_run: bool = True) -> dict:
        """Remove a NixOS package"""
        if dry_run:
            return {
                "success": True,
                "message": f"Would remove {package_name}",
                "command": f"nix-env -e {package_name}",
            }

        output = self._run_nix_command(["nix-env", "-e", package_name])

        if output:
            # Update cache
            if package_name in self.packages_cache:
                self.packages_cache[package_name].installed = False

            return {
                "success": True,
                "message": f"Removed {package_name}",
                "output": output,
            }
        return {"success": False, "message": f"Failed to remove {package_name}"}

    def generate_package_manager_ui(self) -> dict:
        """Generate a complete package manager interface"""

        request = """Create a package manager interface with these components:
        1. Search bar at the top with placeholder "Search NixOS packages..."
        2. Filter buttons: All, Installed, Available
        3. Package list table with columns: Name, Version, Description, Status, Actions
        4. Install/Remove buttons for each package
        5. Bulk selection checkboxes
        6. Status bar showing "X packages installed, Y available"
        7. Dark theme with NixOS blue accents
        8. Refresh button to update package list"""

        # Build the interface
        context = UserContext(
            user_id="nixos_admin",
            expertise_level="intermediate",
            device_type="desktop",
            preferences={"theme": "dark"},
        )

        interface = self.builder.build_interface(request, context)

        # Enhance with real package data
        self._inject_package_data(interface)

        return {
            "interface": interface,
            "packages": len(self.packages_cache),
            "installed": sum(1 for p in self.packages_cache.values() if p.installed),
        }

    def _inject_package_data(self, interface):
        """Inject real NixOS package data into interface"""

        # Find the table component
        for component in interface.components:
            if "table" in component.dna.purpose.lower():
                # Add real package data
                component.data = []
                for package in self.packages_cache.values():
                    component.data.append(
                        {
                            "name": package.name,
                            "version": package.version,
                            "description": package.description[:50] + "...",
                            "status": "✅ Installed"
                            if package.installed
                            else "📦 Available",
                            "action": "Remove" if package.installed else "Install",
                        }
                    )

    def generate_search_results_ui(self, query: str) -> dict:
        """Generate UI for search results"""

        results = self.search_packages(query)

        request = f"""Create a search results interface showing {len(results)} packages:
        - Title: "Search Results for '{query}'"
        - List of packages with install/remove buttons
        - Each package shows name, version, description
        - Highlight installed packages
        - Back to search button"""

        context = UserContext(user_id="nixos_user", expertise_level="intermediate")

        interface = self.builder.build_interface(request, context)

        # Add actual search results
        for component in interface.components:
            if "list" in component.dna.purpose.lower():
                component.data = [
                    {
                        "name": p.name,
                        "version": p.version,
                        "description": p.description,
                        "installed": p.installed,
                    }
                    for p in results
                ]

        return {"interface": interface, "results_count": len(results), "query": query}

    def generate_package_details_ui(self, package_name: str) -> dict:
        """Generate detailed view for a specific package"""

        package = self.packages_cache.get(package_name)
        if not package:
            return {"error": f"Package {package_name} not found"}

        request = f"""Create a package details interface for {package_name}:
        - Large title with package name and version
        - Full description text
        - Installation status indicator
        - Install/Remove button (based on status)
        - Dependencies list (if any)
        - File size information
        - Back button to package list"""

        context = UserContext(user_id="nixos_user", expertise_level="intermediate")

        interface = self.builder.build_interface(request, context)

        # Inject package details
        for component in interface.components:
            if "title" in component.dna.purpose.lower():
                component.text = f"{package.name} v{package.version}"
            elif "description" in component.dna.purpose.lower():
                component.text = package.description
            elif "status" in component.dna.purpose.lower():
                component.text = (
                    "✅ Installed" if package.installed else "📦 Not Installed"
                )
            elif "button" in component.dna.purpose.lower():
                component.label = "Remove" if package.installed else "Install"
                component.action = (
                    f"nix-env -{'e' if package.installed else 'i'} {package_name}"
                )

        return {"interface": interface, "package": package.__dict__}


def demo_package_interfaces():
    """Demonstrate package management interface generation"""

    print(
        """
╔════════════════════════════════════════════════════════════════════╗
║        📦 NIXOS PACKAGE MANAGEMENT INTERFACE DEMO                  ║
╚════════════════════════════════════════════════════════════════════╝
    """
    )

    manager = NixOSPackageInterface()

    # 1. Generate main package manager
    print("\n1️⃣ Generating Package Manager UI...")
    result = manager.generate_package_manager_ui()
    print(f"   ✅ Created with {len(result['interface'].components)} components")
    print(f"   📦 {result['packages']} packages ({result['installed']} installed)")

    # 2. Generate search results
    print("\n2️⃣ Generating Search Results for 'browser'...")
    result = manager.generate_search_results_ui("browser")
    print(f"   ✅ Found {result['results_count']} packages")
    print(f"   🔍 Query: {result['query']}")

    # 3. Generate package details
    print("\n3️⃣ Generating Package Details for 'firefox'...")
    result = manager.generate_package_details_ui("firefox")
    if "package" in result:
        pkg = result["package"]
        print(f"   ✅ Package: {pkg['name']} v{pkg['version']}")
        print(f"   📝 Status: {'Installed' if pkg['installed'] else 'Available'}")

    # 4. Demonstrate package operations
    print("\n4️⃣ Demonstrating Package Operations...")

    # Install a package (dry run)
    print("\n   Installing 'htop' (dry run)...")
    result = manager.install_package("htop", dry_run=True)
    print(f"   → {result['message']}")
    print(f"   → Command: {result.get('command', 'N/A')}")

    # Remove a package (dry run)
    print("\n   Removing 'firefox' (dry run)...")
    result = manager.remove_package("firefox", dry_run=True)
    print(f"   → {result['message']}")
    print(f"   → Command: {result.get('command', 'N/A')}")

    print(
        """
═══════════════════════════════════════════════════════════════════════
✨ Package management interfaces generated and connected to NixOS!
   
Next steps:
1. Connect UI events to actual package operations
2. Add real-time package installation progress
3. Implement dependency resolution UI
4. Add package configuration interfaces
═══════════════════════════════════════════════════════════════════════
    """
    )


if __name__ == "__main__":
    demo_package_interfaces()
