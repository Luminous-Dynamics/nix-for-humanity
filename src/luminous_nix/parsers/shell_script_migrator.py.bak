"""
Shell Script Migration Assistant
Converts shell scripts to Nix configurations and NixOS modules
"""

import re
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ShellCommand:
    """Represents a parsed shell command"""
    command: str
    args: List[str]
    flags: List[str]
    environment: Dict[str, str] = field(default_factory=dict)
    redirects: Dict[str, str] = field(default_factory=dict)
    pipe_to: Optional['ShellCommand'] = None
    background: bool = False
    sudo: bool = False


@dataclass
class ScriptAnalysis:
    """Analysis of a shell script"""
    shebang: Optional[str] = None
    commands: List[ShellCommand] = field(default_factory=list)
    functions: Dict[str, List[str]] = field(default_factory=dict)
    variables: Dict[str, str] = field(default_factory=dict)
    packages_needed: List[str] = field(default_factory=list)
    services_configured: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    directories_created: List[str] = field(default_factory=list)
    system_modifications: List[str] = field(default_factory=list)
    can_migrate: bool = True
    migration_warnings: List[str] = field(default_factory=list)
    nix_config: Optional[str] = None
    nix_derivation: Optional[str] = None


class ShellScriptParser:
    """Parse shell scripts and extract structure"""
    
    # Common package managers and their Nix equivalents
    PACKAGE_MANAGERS = {
        "apt": "apt-get",
        "apt-get": "apt-get",
        "yum": "yum",
        "dnf": "dnf",
        "pacman": "pacman",
        "brew": "brew",
        "snap": "snap",
        "pip": "pip",
        "pip3": "pip3",
        "npm": "npm",
        "yarn": "yarn",
        "gem": "gem",
        "cargo": "cargo",
    }
    
    # Map common commands to Nix packages
    COMMAND_TO_PACKAGE = {
        "git": "git",
        "curl": "curl",
        "wget": "wget",
        "make": "gnumake",
        "gcc": "gcc",
        "g++": "gcc",
        "python": "python3",
        "python3": "python3",
        "node": "nodejs",
        "npm": "nodejs",
        "docker": "docker",
        "vim": "vim",
        "emacs": "emacs",
        "nano": "nano",
        "htop": "htop",
        "tree": "tree",
        "jq": "jq",
        "tmux": "tmux",
        "screen": "screen",
        "nginx": "nginx",
        "apache2": "apacheHttpd",
        "mysql": "mysql",
        "postgres": "postgresql",
        "redis": "redis",
        "rustc": "rustc",
        "cargo": "cargo",
        "go": "go",
    }
    
    # Service management commands
    SERVICE_COMMANDS = {
        "systemctl": ["start", "stop", "restart", "enable", "disable"],
        "service": ["start", "stop", "restart"],
        "rc-service": ["start", "stop", "restart"],
    }
    
    def parse_script(self, script_path: str) -> ScriptAnalysis:
        """Parse a shell script"""
        path = Path(script_path)
        
        if not path.exists():
            raise ValueError(f"Script not found: {script_path}")
        
        content = path.read_text()
        lines = content.splitlines()
        
        analysis = ScriptAnalysis()
        
        # Parse shebang
        if lines and lines[0].startswith("#!"):
            analysis.shebang = lines[0]
        
        # Parse the script
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Parse variables
            if "=" in line and not " " in line.split("=")[0]:
                self._parse_variable(line, analysis)
            
            # Parse functions
            elif line.startswith("function ") or line.endswith("()"):
                self._parse_function(lines, line_num, analysis)
            
            # Parse commands
            else:
                commands = self._parse_command_line(line)
                for cmd in commands:
                    analysis.commands.append(cmd)
                    self._analyze_command(cmd, analysis)
        
        # Determine if we can migrate
        analysis.can_migrate = self._can_migrate(analysis)
        
        # Generate Nix configurations
        if analysis.can_migrate:
            analysis.nix_config = self._generate_nix_config(analysis)
            analysis.nix_derivation = self._generate_nix_derivation(analysis, path.name)
        
        return analysis
    
    def _parse_variable(self, line: str, analysis: ScriptAnalysis):
        """Parse variable assignment"""
        if "=" in line:
            parts = line.split("=", 1)
            var_name = parts[0].strip()
            var_value = parts[1].strip().strip('"').strip("'")
            
            # Handle export
            if var_name.startswith("export "):
                var_name = var_name[7:].strip()
            
            analysis.variables[var_name] = var_value
    
    def _parse_function(self, lines: List[str], start_line: int, analysis: ScriptAnalysis):
        """Parse function definition"""
        line = lines[start_line].strip()
        
        # Extract function name
        if line.startswith("function "):
            func_name = line[9:].split("(")[0].strip()
        else:
            func_name = line.split("(")[0].strip()
        
        # Find function body
        func_body = []
        brace_count = 0
        in_function = False
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            
            if "{" in line:
                brace_count += line.count("{")
                in_function = True
            if "}" in line:
                brace_count -= line.count("}")
            
            if in_function:
                func_body.append(line)
                
                if brace_count == 0:
                    break
        
        analysis.functions[func_name] = func_body
    
    def _parse_command_line(self, line: str) -> List[ShellCommand]:
        """Parse a command line into structured commands"""
        commands = []
        
        # Handle pipes
        if "|" in line:
            parts = line.split("|")
            prev_cmd = None
            
            for part in parts:
                cmd = self._parse_single_command(part.strip())
                if prev_cmd:
                    prev_cmd.pipe_to = cmd
                else:
                    commands.append(cmd)
                prev_cmd = cmd
        else:
            commands.append(self._parse_single_command(line))
        
        return commands
    
    def _parse_single_command(self, cmd_str: str) -> ShellCommand:
        """Parse a single command"""
        cmd = ShellCommand(command="", args=[], flags=[])
        
        # Check for sudo
        if cmd_str.startswith("sudo "):
            cmd.sudo = True
            cmd_str = cmd_str[5:].strip()
        
        # Check for background
        if cmd_str.endswith(" &"):
            cmd.background = True
            cmd_str = cmd_str[:-2].strip()
        
        # Parse redirections
        redirect_patterns = [
            (r'>\s*(\S+)', 'stdout'),
            (r'2>\s*(\S+)', 'stderr'),
            (r'<\s*(\S+)', 'stdin'),
            (r'>>\s*(\S+)', 'append'),
        ]
        
        for pattern, redirect_type in redirect_patterns:
            match = re.search(pattern, cmd_str)
            if match:
                cmd.redirects[redirect_type] = match.group(1)
                cmd_str = re.sub(pattern, '', cmd_str).strip()
        
        # Parse the command itself
        try:
            parts = shlex.split(cmd_str)
            if parts:
                cmd.command = parts[0]
                
                for part in parts[1:]:
                    if part.startswith("-"):
                        cmd.flags.append(part)
                    else:
                        cmd.args.append(part)
        except Exception as e:
            logger.warning(f"Error parsing command: {cmd_str} - {e}")
            cmd.command = cmd_str.split()[0] if cmd_str else ""
        
        return cmd
    
    def _analyze_command(self, cmd: ShellCommand, analysis: ScriptAnalysis):
        """Analyze a command for migration requirements"""
        
        # Package installation
        if cmd.command in self.PACKAGE_MANAGERS:
            self._analyze_package_install(cmd, analysis)
        
        # Service management
        elif cmd.command in self.SERVICE_COMMANDS:
            self._analyze_service_command(cmd, analysis)
        
        # File operations
        elif cmd.command in ["touch", "mkdir", "cp", "mv", "ln"]:
            self._analyze_file_operation(cmd, analysis)
        
        # Check if command needs a package
        elif cmd.command in self.COMMAND_TO_PACKAGE:
            pkg = self.COMMAND_TO_PACKAGE[cmd.command]
            if pkg not in analysis.packages_needed:
                analysis.packages_needed.append(pkg)
        
        # System modifications
        elif cmd.command in ["useradd", "groupadd", "usermod", "chmod", "chown"]:
            analysis.system_modifications.append(f"{cmd.command} {' '.join(cmd.args)}")
        
        # Warn about difficult migrations
        elif cmd.command in ["source", ".", "eval"]:
            analysis.migration_warnings.append(
                f"Dynamic command '{cmd.command}' may not migrate cleanly"
            )
    
    def _analyze_package_install(self, cmd: ShellCommand, analysis: ScriptAnalysis):
        """Analyze package installation commands"""
        if cmd.command in ["apt", "apt-get"] and "install" in cmd.args:
            # Extract package names
            installing = False
            for arg in cmd.args:
                if arg == "install":
                    installing = True
                elif installing and not arg.startswith("-"):
                    # Map apt package to Nix package
                    nix_pkg = self._map_package_name(arg, "apt")
                    if nix_pkg and nix_pkg not in analysis.packages_needed:
                        analysis.packages_needed.append(nix_pkg)
        
        elif cmd.command in ["pip", "pip3"] and "install" in cmd.args:
            for arg in cmd.args:
                if arg != "install" and not arg.startswith("-"):
                    pkg_name = f"python3Packages.{arg.replace('-', '_')}"
                    if pkg_name not in analysis.packages_needed:
                        analysis.packages_needed.append(pkg_name)
        
        elif cmd.command == "npm" and "install" in cmd.args:
            if "-g" in cmd.flags or "--global" in cmd.flags:
                for arg in cmd.args:
                    if arg != "install" and not arg.startswith("-"):
                        pkg_name = f"nodePackages.{arg}"
                        if pkg_name not in analysis.packages_needed:
                            analysis.packages_needed.append(pkg_name)
    
    def _analyze_service_command(self, cmd: ShellCommand, analysis: ScriptAnalysis):
        """Analyze service management commands"""
        if cmd.command == "systemctl":
            if len(cmd.args) >= 2:
                action = cmd.args[0]
                service = cmd.args[1].replace(".service", "")
                
                if action in ["enable", "start"]:
                    if service not in analysis.services_configured:
                        analysis.services_configured.append(service)
    
    def _analyze_file_operation(self, cmd: ShellCommand, analysis: ScriptAnalysis):
        """Analyze file operations"""
        if cmd.command == "mkdir":
            for arg in cmd.args:
                if not arg.startswith("-"):
                    analysis.directories_created.append(arg)
        
        elif cmd.command == "touch":
            for arg in cmd.args:
                if not arg.startswith("-"):
                    analysis.files_created.append(arg)
    
    def _map_package_name(self, apt_name: str, source: str = "apt") -> Optional[str]:
        """Map package names from other systems to Nix"""
        # Common mappings
        mappings = {
            "build-essential": "gcc",
            "python3-pip": "python3Packages.pip",
            "python3-dev": "python3",
            "libssl-dev": "openssl",
            "libffi-dev": "libffi",
            "nodejs": "nodejs",
            "npm": "nodePackages.npm",
            "docker.io": "docker",
            "docker-ce": "docker",
        }
        
        if apt_name in mappings:
            return mappings[apt_name]
        
        # Direct mapping for many packages
        if apt_name in self.COMMAND_TO_PACKAGE.values():
            return apt_name
        
        # Default: try the name as-is
        return apt_name
    
    def _can_migrate(self, analysis: ScriptAnalysis) -> bool:
        """Determine if script can be migrated to Nix"""
        # Can't migrate if there are too many warnings
        if len(analysis.migration_warnings) > 5:
            return False
        
        # Can't migrate complex dynamic scripts
        dangerous_patterns = ["eval", "source", "exec", "trap"]
        for cmd in analysis.commands:
            if cmd.command in dangerous_patterns:
                return False
        
        return True
    
    def _generate_nix_config(self, analysis: ScriptAnalysis) -> str:
        """Generate NixOS configuration from script analysis"""
        config_parts = []
        
        # Header
        config_parts.append("{ config, pkgs, ... }:\n\n{")
        
        # System packages
        if analysis.packages_needed:
            config_parts.append("  environment.systemPackages = with pkgs; [")
            for pkg in analysis.packages_needed:
                config_parts.append(f"    {pkg}")
            config_parts.append("  ];")
        
        # Services
        if analysis.services_configured:
            config_parts.append("\n  # Services")
            for service in analysis.services_configured:
                # Map service names
                nix_service = self._map_service_name(service)
                if nix_service:
                    config_parts.append(f"  services.{nix_service}.enable = true;")
        
        # System modifications
        if analysis.system_modifications:
            config_parts.append("\n  # System modifications")
            config_parts.append("  # Note: These require manual translation:")
            for mod in analysis.system_modifications:
                config_parts.append(f"  # - {mod}")
        
        config_parts.append("}")
        
        return "\n".join(config_parts)
    
    def _map_service_name(self, service: str) -> Optional[str]:
        """Map service names to NixOS services"""
        mappings = {
            "ssh": "openssh",
            "sshd": "openssh",
            "docker": "docker",
            "nginx": "nginx",
            "apache2": "httpd",
            "mysql": "mysql",
            "postgresql": "postgresql",
            "redis": "redis",
        }
        
        return mappings.get(service, service)
    
    def _generate_nix_derivation(self, analysis: ScriptAnalysis, script_name: str) -> str:
        """Generate a Nix derivation for the script"""
        derivation = f"""{{ pkgs ? import <nixpkgs> {{}} }}:

pkgs.writeScriptBin "{script_name.replace('.sh', '')}" ''
  #!${{pkgs.bash}}/bin/bash
  
  # Original script: {script_name}
  # Migrated to Nix derivation
  
  # Set PATH with required tools
  export PATH="${{pkgs.lib.makeBinPath (with pkgs; [
    coreutils
    gnugrep
    gnused
    gawk"""
        
        if analysis.packages_needed:
            for pkg in analysis.packages_needed[:5]:  # Limit to avoid too long
                derivation += f"\n    {pkg}"
        
        derivation += """
  ])}}"
  
  # Variables"""
        
        for var_name, var_value in analysis.variables.items():
            derivation += f"\n  {var_name}=\"{var_value}\""
        
        derivation += "\n\n  # Main script logic"
        derivation += "\n  # TODO: Migrate command logic here"
        
        derivation += "\n''"
        
        return derivation


class ShellToNixMigrator:
    """Main migrator that converts shell scripts to Nix"""
    
    def __init__(self):
        self.parser = ShellScriptParser()
    
    def migrate_script(self, script_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Migrate a shell script to Nix configuration"""
        analysis = self.parser.parse_script(script_path)
        
        result = {
            "success": analysis.can_migrate,
            "script": script_path,
            "analysis": {
                "packages_needed": analysis.packages_needed,
                "services_configured": analysis.services_configured,
                "variables": analysis.variables,
                "functions": list(analysis.functions.keys()),
                "warnings": analysis.migration_warnings,
            },
            "nix_config": analysis.nix_config,
            "nix_derivation": analysis.nix_derivation,
        }
        
        # Save to files if output directory provided
        if output_dir and analysis.can_migrate:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            script_name = Path(script_path).stem
            
            # Save NixOS configuration
            if analysis.nix_config:
                config_file = output_path / f"{script_name}-config.nix"
                config_file.write_text(analysis.nix_config)
                result["config_file"] = str(config_file)
            
            # Save derivation
            if analysis.nix_derivation:
                deriv_file = output_path / f"{script_name}-derivation.nix"
                deriv_file.write_text(analysis.nix_derivation)
                result["derivation_file"] = str(deriv_file)
        
        return result
    
    def suggest_improvements(self, analysis: ScriptAnalysis) -> List[str]:
        """Suggest improvements for migration"""
        suggestions = []
        
        if analysis.migration_warnings:
            suggestions.append("Simplify dynamic commands (source, eval) for better migration")
        
        if len(analysis.packages_needed) > 20:
            suggestions.append("Consider breaking script into smaller, focused modules")
        
        if analysis.system_modifications:
            suggestions.append("System modifications need manual review for NixOS compatibility")
        
        if not analysis.can_migrate:
            suggestions.append("Script is too complex for automatic migration - consider manual conversion")
        
        return suggestions


# Integration function
def migrate_shell_script(script_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Main entry point for shell script migration"""
    migrator = ShellToNixMigrator()
    return migrator.migrate_script(script_path, output_dir)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python shell_script_migrator.py <script_path> [output_dir]")
        sys.exit(1)
    
    script_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\n🔄 Migrating Shell Script: {script_path}")
    print("=" * 60)
    
    result = migrate_shell_script(script_path, output_dir)
    
    if result["success"]:
        print("✅ Migration successful!")
        
        analysis = result["analysis"]
        
        if analysis["packages_needed"]:
            print(f"\n📦 Packages needed ({len(analysis['packages_needed'])}):")
            for pkg in analysis["packages_needed"][:10]:
                print(f"  - {pkg}")
        
        if analysis["services_configured"]:
            print(f"\n🔧 Services configured:")
            for service in analysis["services_configured"]:
                print(f"  - {service}")
        
        if analysis["warnings"]:
            print(f"\n⚠️  Warnings:")
            for warning in analysis["warnings"]:
                print(f"  - {warning}")
        
        if result.get("config_file"):
            print(f"\n📝 NixOS config saved to: {result['config_file']}")
        
        if result.get("derivation_file"):
            print(f"📝 Nix derivation saved to: {result['derivation_file']}")
        
        print(f"\n📄 Generated NixOS Configuration:")
        print("-" * 40)
        print(result["nix_config"])
    else:
        print("❌ Migration failed - script too complex for automatic conversion")
        print(f"Warnings: {result['analysis']['warnings']}")