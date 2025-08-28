#!/usr/bin/env python3
"""
📝 NixOS Configuration Editor Interface Generator
Creates interactive UIs for editing NixOS configuration files
"""

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext


@dataclass
class ConfigSection:
    """Represents a section of NixOS configuration"""
    name: str
    path: str
    content: str
    line_start: int
    line_end: int
    category: str  # system, packages, services, networking, etc.
    editable: bool = True


@dataclass
class ConfigOption:
    """Represents a NixOS configuration option"""
    name: str
    value: Any
    type: str  # string, bool, list, attrset
    description: str
    example: str | None = None
    default: Any | None = None


class NixOSConfigEditor:
    """Generates configuration editor interfaces for NixOS"""

    def __init__(self):
        self.builder = NLInterfaceBuilderV2(use_llm=False)
        self.config_path = Path("/etc/nixos/configuration.nix")
        self.backup_path = Path("/tmp/configuration.nix.backup")
        self.sections = {}
        self.options = {}
        self._load_configuration()

    def _load_configuration(self):
        """Load and parse the NixOS configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self.config_content = f.read()
                self._parse_configuration()
            except PermissionError:
                print(f"⚠️ Cannot read {self.config_path} - need sudo")
                self.config_content = self._get_sample_config()
                self._parse_configuration()
        else:
            self.config_content = self._get_sample_config()
            self._parse_configuration()

    def _get_sample_config(self) -> str:
        """Return a sample NixOS configuration for demo"""
        return """{ config, pkgs, ... }:

{
  imports = [ 
    ./hardware-configuration.nix
  ];

  # Boot loader
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Networking
  networking.hostName = "nixos-demo";
  networking.networkmanager.enable = true;

  # Time zone
  time.timeZone = "America/Chicago";

  # Locale
  i18n.defaultLocale = "en_US.UTF-8";

  # Desktop Environment
  services.xserver.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;

  # Sound
  sound.enable = true;
  hardware.pulseaudio.enable = true;

  # Users
  users.users.demo = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" ];
  };

  # System packages
  environment.systemPackages = with pkgs; [
    vim
    wget
    firefox
    git
  ];

  # Enable SSH
  services.openssh.enable = true;

  # Firewall
  networking.firewall.enable = true;
  networking.firewall.allowedTCPPorts = [ 22 80 443 ];

  system.stateVersion = "23.11";
}"""

    def _parse_configuration(self):
        """Parse configuration into sections"""
        lines = self.config_content.split('\n')
        current_section = None
        section_start = 0

        # Simple section detection based on comments and keywords
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect section headers (comments)
            if stripped.startswith('# '):
                if current_section:
                    # Save previous section
                    self.sections[current_section] = ConfigSection(
                        name=current_section,
                        path=self.config_path.name,
                        content='\n'.join(lines[section_start:i]),
                        line_start=section_start,
                        line_end=i-1,
                        category=self._categorize_section(current_section)
                    )
                current_section = stripped[2:]
                section_start = i

            # Detect common options
            if '=' in line and not stripped.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    option_name = parts[0].strip()
                    option_value = parts[1].strip().rstrip(';')

                    self.options[option_name] = ConfigOption(
                        name=option_name,
                        value=option_value,
                        type=self._detect_type(option_value),
                        description=self._get_option_description(option_name)
                    )

        # Save last section
        if current_section:
            self.sections[current_section] = ConfigSection(
                name=current_section,
                path=self.config_path.name,
                content='\n'.join(lines[section_start:]),
                line_start=section_start,
                line_end=len(lines)-1,
                category=self._categorize_section(current_section)
            )

    def _categorize_section(self, section_name: str) -> str:
        """Categorize a configuration section"""
        section_lower = section_name.lower()

        if 'boot' in section_lower:
            return 'boot'
        if 'network' in section_lower:
            return 'networking'
        if 'package' in section_lower:
            return 'packages'
        if 'service' in section_lower:
            return 'services'
        if 'user' in section_lower:
            return 'users'
        if 'hardware' in section_lower:
            return 'hardware'
        return 'system'

    def _detect_type(self, value: str) -> str:
        """Detect the type of a configuration value"""
        if value in ['true', 'false']:
            return 'bool'
        if value.startswith('[') and value.endswith(']'):
            return 'list'
        if value.startswith('{') and value.endswith('}'):
            return 'attrset'
        if value.startswith('"') and value.endswith('"'):
            return 'string'
        return 'expression'

    def _get_option_description(self, option_name: str) -> str:
        """Get description for common NixOS options"""
        descriptions = {
            'boot.loader.systemd-boot.enable': 'Enable systemd-boot EFI boot loader',
            'networking.hostName': 'The hostname of the system',
            'networking.networkmanager.enable': 'Enable NetworkManager for network configuration',
            'time.timeZone': 'The system time zone',
            'services.xserver.enable': 'Enable the X11 windowing system',
            'environment.systemPackages': 'List of packages to install system-wide',
            'services.openssh.enable': 'Enable the OpenSSH daemon',
            'networking.firewall.enable': 'Enable the firewall'
        }
        return descriptions.get(option_name, 'NixOS configuration option')

    def generate_editor_ui(self) -> dict:
        """Generate main configuration editor interface"""

        request = """Create a configuration editor interface with:
        1. File tree panel on the left showing configuration files
        2. Main editor area in the center with syntax highlighting
        3. Options reference panel on the right
        4. Toolbar with Save, Validate, and Rebuild buttons
        5. Status bar showing current file and line number
        6. Search bar for finding options
        7. Dark theme with syntax highlighting colors
        8. Tab bar for multiple open files"""

        context = UserContext(
            user_id="nixos_admin",
            expertise_level="expert",
            device_type="desktop",
            preferences={"theme": "dark", "font": "monospace"}
        )

        interface = self.builder.build_interface(request, context)

        # Inject configuration data
        self._inject_config_data(interface)

        return {
            "interface": interface,
            "sections": len(self.sections),
            "options": len(self.options),
            "config_path": str(self.config_path)
        }

    def _inject_config_data(self, interface):
        """Inject real configuration data into interface"""

        for component in interface.components:
            # File tree component
            if 'tree' in component.dna.purpose.lower():
                component.data = {
                    "root": "/etc/nixos",
                    "files": [
                        {"name": "configuration.nix", "type": "file", "active": True},
                        {"name": "hardware-configuration.nix", "type": "file"},
                        {"name": "packages.nix", "type": "file"},
                        {"name": "services.nix", "type": "file"}
                    ]
                }

            # Editor component
            elif 'editor' in component.dna.purpose.lower():
                component.content = self.config_content
                component.language = "nix"
                component.theme = "monokai"

            # Options panel
            elif 'reference' in component.dna.purpose.lower():
                component.data = [
                    {
                        "name": opt.name,
                        "type": opt.type,
                        "description": opt.description
                    }
                    for opt in list(self.options.values())[:10]  # Show first 10
                ]

    def generate_section_editor_ui(self, section_name: str) -> dict:
        """Generate editor for specific configuration section"""

        section = self.sections.get(section_name)
        if not section:
            return {"error": f"Section '{section_name}' not found"}

        request = f"""Create a focused editor for the {section_name} section:
        - Section title: {section_name}
        - Editor with the section content
        - Common options for this section type
        - Quick actions based on section category
        - Validation indicator
        - Apply changes button"""

        context = UserContext(
            user_id="nixos_user",
            expertise_level="intermediate"
        )

        interface = self.builder.build_interface(request, context)

        # Add section-specific content
        for component in interface.components:
            if 'editor' in component.dna.purpose.lower():
                component.content = section.content
            elif 'title' in component.dna.purpose.lower():
                component.text = f"Editing: {section.name}"

        return {
            "interface": interface,
            "section": section.__dict__
        }

    def generate_option_search_ui(self) -> dict:
        """Generate option search and discovery interface"""

        request = """Create an option search interface:
        - Search bar with autocomplete
        - Filter by category (boot, network, services, packages)
        - Results list with option name, type, and description
        - Current value display
        - Edit button for each option
        - Example values section
        - Documentation link"""

        context = UserContext(
            user_id="nixos_user",
            expertise_level="intermediate"
        )

        interface = self.builder.build_interface(request, context)

        return {
            "interface": interface,
            "total_options": len(self.options)
        }

    def validate_configuration(self) -> dict:
        """Validate the current configuration"""

        # Save current config to temp file
        temp_file = Path("/tmp/test-configuration.nix")
        with open(temp_file, 'w') as f:
            f.write(self.config_content)

        # Run nixos-rebuild dry-build
        try:
            result = subprocess.run(
                ["nixos-rebuild", "dry-build", "-I", f"nixos-config={temp_file}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    "valid": True,
                    "message": "Configuration is valid",
                    "output": result.stdout
                }
            return {
                "valid": False,
                "message": "Configuration has errors",
                "errors": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "valid": False,
                "message": "Validation timed out"
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation failed: {e}"
            }

    def save_configuration(self, content: str, backup: bool = True) -> dict:
        """Save configuration with optional backup"""

        if backup and self.config_path.exists():
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(f"/tmp/configuration.nix.{timestamp}")

            try:
                with open(self.config_path) as src:
                    with open(backup_path, 'w') as dst:
                        dst.write(src.read())
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to create backup: {e}"
                }

        # Save new configuration
        try:
            # Would need sudo for real /etc/nixos/configuration.nix
            with open("/tmp/configuration.nix.new", 'w') as f:
                f.write(content)

            return {
                "success": True,
                "message": "Configuration saved (to temp file)",
                "path": "/tmp/configuration.nix.new",
                "backup": str(backup_path) if backup else None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to save: {e}"
            }

    def generate_diff_view_ui(self, original: str, modified: str) -> dict:
        """Generate diff view interface for changes"""

        request = """Create a diff view interface:
        - Split view with original on left, modified on right
        - Highlighted additions in green
        - Highlighted deletions in red
        - Line numbers on both sides
        - Accept/Reject buttons for each change
        - Apply all / Discard all buttons
        - Summary of changes at top"""

        context = UserContext(
            user_id="nixos_admin",
            expertise_level="expert"
        )

        interface = self.builder.build_interface(request, context)

        return {
            "interface": interface,
            "changes": self._calculate_diff(original, modified)
        }

    def _calculate_diff(self, original: str, modified: str) -> dict:
        """Calculate diff statistics"""
        orig_lines = original.split('\n')
        mod_lines = modified.split('\n')

        added = len([l for l in mod_lines if l not in orig_lines])
        removed = len([l for l in orig_lines if l not in mod_lines])

        return {
            "added_lines": added,
            "removed_lines": removed,
            "total_changes": added + removed
        }


def demo_config_editor():
    """Demonstrate configuration editor interface generation"""

    print("""
╔════════════════════════════════════════════════════════════════════╗
║         📝 NIXOS CONFIGURATION EDITOR INTERFACE DEMO               ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    editor = NixOSConfigEditor()

    # 1. Generate main editor
    print("\n1️⃣ Generating Main Configuration Editor...")
    result = editor.generate_editor_ui()
    print(f"   ✅ Created with {len(result['interface'].components)} components")
    print(f"   📁 Config: {result['config_path']}")
    print(f"   📑 Sections: {result['sections']}")
    print(f"   ⚙️ Options: {result['options']}")

    # 2. Generate section editor
    print("\n2️⃣ Generating Section Editor for 'Networking'...")
    result = editor.generate_section_editor_ui("Networking")
    if 'section' in result:
        section = result['section']
        print(f"   ✅ Section: {section['name']}")
        print(f"   📍 Lines: {section['line_start']}-{section['line_end']}")
        print(f"   🏷️ Category: {section['category']}")

    # 3. Generate option search
    print("\n3️⃣ Generating Option Search Interface...")
    result = editor.generate_option_search_ui()
    print("   ✅ Created search interface")
    print(f"   🔍 Searchable options: {result['total_options']}")

    # 4. Validate configuration
    print("\n4️⃣ Validating Configuration...")
    validation = editor.validate_configuration()
    if validation['valid']:
        print("   ✅ Configuration is valid")
    else:
        print(f"   ⚠️ {validation['message']}")

    # 5. Demo save operation
    print("\n5️⃣ Demonstrating Save Operation...")
    modified_config = editor.config_content + "\n# Modified by demo"
    result = editor.save_configuration(modified_config)
    if result['success']:
        print(f"   ✅ {result['message']}")
        print(f"   💾 Saved to: {result['path']}")
        if result.get('backup'):
            print(f"   🔒 Backup: {result['backup']}")

    # 6. Generate diff view
    print("\n6️⃣ Generating Diff View...")
    result = editor.generate_diff_view_ui(
        editor.config_content,
        modified_config
    )
    changes = result['changes']
    print("   ✅ Diff view created")
    print(f"   ➕ Added: {changes['added_lines']} lines")
    print(f"   ➖ Removed: {changes['removed_lines']} lines")

    print("""
═══════════════════════════════════════════════════════════════════════
✨ Configuration editor interfaces generated successfully!

Key Features Demonstrated:
• Full configuration file editing with syntax highlighting
• Section-based focused editing
• Option search and discovery
• Configuration validation
• Safe save with automatic backups
• Visual diff for reviewing changes

Next Steps:
1. Connect to real file operations (requires sudo)
2. Add real-time syntax checking
3. Implement option autocomplete
4. Add configuration templates
5. Create rebuild progress tracking
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_config_editor()
