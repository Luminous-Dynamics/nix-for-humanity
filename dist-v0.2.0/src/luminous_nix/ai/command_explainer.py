"""
Command Explanation System for NixOS
Explains what commands do, their options, and potential impacts
"""

import re
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CommandExplanation:
    """Represents an explanation of a command"""
    command: str
    description: str
    components: List[Dict[str, str]]  # Breaking down each part
    effects: List[str]  # What will happen
    warnings: List[str]  # Potential risks
    alternatives: List[str]  # Other ways to achieve the same
    examples: List[str]  # Example usages
    learn_more: Optional[str] = None

class NixCommandExplainer:
    """
    Explains NixOS and general Linux commands
    Breaks down complex commands into understandable parts
    """
    
    def __init__(self):
        # Common Nix commands and their explanations
        self.nix_commands = {
            "nix-env": {
                "description": "Manage packages in user environment",
                "common_options": {
                    "-i": "Install packages",
                    "-iA": "Install by attribute path (faster)",
                    "-e": "Erase/uninstall packages", 
                    "-u": "Upgrade packages",
                    "-q": "Query available/installed packages",
                    "-qa": "Query all available packages",
                    "-qas": "Query with status indicators",
                    "--list-generations": "Show system generations",
                    "--rollback": "Rollback to previous generation",
                    "--switch-generation": "Switch to specific generation",
                }
            },
            "nixos-rebuild": {
                "description": "Rebuild and switch NixOS configuration",
                "common_options": {
                    "switch": "Build, activate, and set as boot default",
                    "boot": "Build and set as boot default (activate on reboot)",
                    "test": "Build and activate but don't set as boot default",
                    "build": "Build only, don't activate",
                    "dry-build": "Show what would be built",
                    "dry-activate": "Show what would be activated",
                    "--upgrade": "Update channels before building",
                    "--rollback": "Rollback to previous generation",
                    "--show-trace": "Show detailed error traces",
                    "--fast": "Skip some checks for faster builds",
                }
            },
            "nix-shell": {
                "description": "Start an interactive shell with specified packages",
                "common_options": {
                    "-p": "Specify packages to include",
                    "-I": "Add to Nix search path",
                    "--pure": "Clear environment except specified",
                    "--run": "Run command in shell environment",
                    "--command": "Run interactive command",
                }
            },
            "nix-store": {
                "description": "Manipulate or query the Nix store",
                "common_options": {
                    "--gc": "Garbage collect",
                    "--optimize": "Optimize store by hardlinking",
                    "--verify": "Verify store integrity",
                    "--repair": "Repair corrupted paths",
                    "-q": "Query store",
                    "-qR": "Query runtime dependencies",
                    "--query --roots": "Show GC roots",
                }
            },
            "nix-channel": {
                "description": "Manage Nix channels (package sources)",
                "common_options": {
                    "--add": "Add a channel",
                    "--remove": "Remove a channel",
                    "--list": "List channels",
                    "--update": "Update all channels",
                }
            },
            "nix": {
                "description": "New unified Nix command (experimental)",
                "subcommands": {
                    "search": "Search for packages",
                    "build": "Build a derivation",
                    "develop": "Start development shell",
                    "run": "Run a program from a package",
                    "flake": "Manage Nix flakes",
                    "profile": "Manage Nix profiles",
                    "repl": "Start Nix REPL",
                }
            },
            "nix-collect-garbage": {
                "description": "Delete unreachable store paths",
                "common_options": {
                    "-d": "Delete old generations before collecting",
                    "--delete-old": "Delete all old generations",
                    "--delete-older-than": "Delete generations older than specified",
                }
            },
            "home-manager": {
                "description": "Manage user-specific configuration",
                "subcommands": {
                    "switch": "Build and activate configuration",
                    "build": "Build configuration without activating",
                    "generations": "List all generations",
                    "packages": "List installed packages",
                    "rollback": "Rollback to previous generation",
                }
            }
        }
        
        # Common patterns and their meanings
        self.patterns = {
            r"nixpkgs\.(\w+)": "Package from nixpkgs: {}",
            r"nixos\.(\w+)": "NixOS module: {}",
            r"pkgs\.(\w+)": "Package from pkgs set: {}",
            r"config\.(\w+)": "Configuration option: {}",
            r"lib\.(\w+)": "Nix library function: {}",
            r"builtins\.(\w+)": "Built-in Nix function: {}",
        }
        
        # Risk levels for different operations
        self.risk_levels = {
            "high": ["rm -rf", "nixos-rebuild switch", "nix-collect-garbage -d", "format", "dd"],
            "medium": ["nix-env -e", "systemctl stop", "kill", "nixos-rebuild test"],
            "low": ["nix-env -qa", "nix search", "nix-shell", "ls", "cat"],
        }
    
    def explain(self, command: str) -> CommandExplanation:
        """
        Main entry point - explains a command
        """
        # Parse the command into components
        components = self._parse_command(command)
        
        # Determine the base command
        base_cmd = components[0]["value"] if components else ""
        
        # Generate explanation based on command type
        if base_cmd in self.nix_commands:
            return self._explain_nix_command(command, components)
        elif base_cmd.startswith("nix"):
            return self._explain_generic_nix_command(command, components)
        else:
            return self._explain_general_command(command, components)
    
    def _parse_command(self, command: str) -> List[Dict[str, str]]:
        """Parse command into components"""
        components = []
        
        # Simple tokenization (could be improved with proper shell parsing)
        parts = command.split()
        
        if not parts:
            return components
        
        # First part is the command
        components.append({
            "type": "command",
            "value": parts[0],
            "description": self._get_command_description(parts[0])
        })
        
        # Parse the rest as options or arguments
        i = 1
        while i < len(parts):
            part = parts[i]
            
            if part.startswith("--"):
                # Long option
                if "=" in part:
                    opt, val = part.split("=", 1)
                    components.append({
                        "type": "option",
                        "value": opt,
                        "description": self._get_option_description(parts[0], opt)
                    })
                    components.append({
                        "type": "value",
                        "value": val,
                        "description": f"Value for {opt}"
                    })
                else:
                    components.append({
                        "type": "option",
                        "value": part,
                        "description": self._get_option_description(parts[0], part)
                    })
            elif part.startswith("-"):
                # Short option(s)
                components.append({
                    "type": "option",
                    "value": part,
                    "description": self._get_option_description(parts[0], part)
                })
            else:
                # Argument
                arg_type = self._determine_argument_type(part)
                components.append({
                    "type": arg_type,
                    "value": part,
                    "description": self._get_argument_description(parts[0], part, i)
                })
            
            i += 1
        
        return components
    
    def _get_command_description(self, cmd: str) -> str:
        """Get description for a command"""
        if cmd in self.nix_commands:
            return self.nix_commands[cmd]["description"]
        
        # Try to get from system
        try:
            result = subprocess.run(
                ["whatis", cmd],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                # Parse whatis output
                lines = result.stdout.strip().split("\n")
                if lines:
                    # Format: "command (section) - description"
                    parts = lines[0].split(" - ", 1)
                    if len(parts) > 1:
                        return parts[1]
        except:
            pass
        
        # Common commands
        descriptions = {
            "sudo": "Execute command with superuser privileges",
            "ls": "List directory contents",
            "cd": "Change directory",
            "cat": "Display file contents",
            "grep": "Search text patterns",
            "find": "Find files and directories",
            "curl": "Transfer data from/to servers",
            "wget": "Download files from the web",
            "systemctl": "Control systemd services",
            "journalctl": "View systemd logs",
        }
        
        return descriptions.get(cmd, f"Command: {cmd}")
    
    def _get_option_description(self, cmd: str, option: str) -> str:
        """Get description for a command option"""
        if cmd in self.nix_commands:
            cmd_data = self.nix_commands[cmd]
            
            # Check common options
            if "common_options" in cmd_data:
                # Remove leading dashes for lookup
                opt_key = option.lstrip("-")
                if opt_key in cmd_data["common_options"]:
                    return cmd_data["common_options"][opt_key]
                # Check without value part
                if "=" in opt_key:
                    opt_key = opt_key.split("=")[0]
                    if opt_key in cmd_data["common_options"]:
                        return cmd_data["common_options"][opt_key]
        
        # Generic option descriptions
        generic_options = {
            "-v": "Verbose output",
            "--verbose": "Verbose output",
            "-q": "Quiet mode",
            "--quiet": "Quiet mode",
            "-f": "Force operation",
            "--force": "Force operation",
            "-r": "Recursive",
            "-R": "Recursive",
            "--recursive": "Recursive operation",
            "-h": "Show help",
            "--help": "Show help",
            "-n": "Dry run (don't execute)",
            "--dry-run": "Dry run (don't execute)",
        }
        
        return generic_options.get(option, f"Option: {option}")
    
    def _determine_argument_type(self, arg: str) -> str:
        """Determine what type of argument this is"""
        if arg.startswith("/") or arg.startswith("./") or arg.startswith("~"):
            return "path"
        elif arg.startswith("http://") or arg.startswith("https://"):
            return "url"
        elif "nixpkgs#" in arg or "nixos#" in arg:
            return "flake"
        elif re.match(r"^[0-9]+$", arg):
            return "number"
        elif "." in arg and not "/" in arg:
            return "package"
        else:
            return "argument"
    
    def _get_argument_description(self, cmd: str, arg: str, position: int) -> str:
        """Get description for an argument"""
        arg_type = self._determine_argument_type(arg)
        
        if arg_type == "path":
            if arg.startswith("/nix/store"):
                return "Nix store path"
            elif arg.startswith("/etc/nixos"):
                return "NixOS configuration path"
            else:
                return f"File/directory path"
        elif arg_type == "url":
            return "Remote URL"
        elif arg_type == "flake":
            return f"Flake reference: {arg}"
        elif arg_type == "package":
            return f"Package name: {arg}"
        elif arg_type == "number":
            if cmd == "nixos-rebuild" and position == 2:
                return f"Generation number: {arg}"
            else:
                return f"Numeric value: {arg}"
        else:
            # Command-specific argument descriptions
            if cmd == "nixos-rebuild" and arg in ["switch", "boot", "test", "build"]:
                return self.nix_commands["nixos-rebuild"]["common_options"][arg]
            elif cmd == "nix" and arg in self.nix_commands["nix"]["subcommands"]:
                return self.nix_commands["nix"]["subcommands"][arg]
            else:
                return f"Argument: {arg}"
    
    def _explain_nix_command(self, command: str, components: List[Dict]) -> CommandExplanation:
        """Explain a Nix-specific command"""
        base_cmd = components[0]["value"]
        cmd_data = self.nix_commands[base_cmd]
        
        # Determine what the command will do
        effects = []
        warnings = []
        alternatives = []
        examples = []
        
        # Analyze based on command and options
        if base_cmd == "nix-env":
            if any(c["value"] in ["-i", "-iA"] for c in components if c["type"] == "option"):
                packages = [c["value"] for c in components if c["type"] in ["package", "argument"]]
                effects.append(f"Install packages: {', '.join(packages) if packages else 'specified packages'}")
                effects.append("Packages will be added to your user profile")
                effects.append("Creates new generation that can be rolled back")
                alternatives.append(f"nix profile install nixpkgs#{packages[0] if packages else 'package'}")
                examples.append(f"nix-env -iA nixpkgs.firefox")
            elif any(c["value"] == "-e" for c in components if c["type"] == "option"):
                effects.append("Remove packages from user profile")
                warnings.append("Removed packages can be recovered via rollback")
            elif any(c["value"] in ["-q", "-qa"] for c in components if c["type"] == "option"):
                effects.append("Query/search for packages")
                effects.append("No system changes will be made")
        
        elif base_cmd == "nixos-rebuild":
            action = next((c["value"] for c in components if c["value"] in ["switch", "boot", "test", "build"]), None)
            if action == "switch":
                effects.append("Build new system configuration")
                effects.append("Activate configuration immediately")
                effects.append("Set as default boot configuration")
                warnings.append("System-wide changes will take effect immediately")
                warnings.append("May affect running services")
            elif action == "boot":
                effects.append("Build new system configuration")
                effects.append("Set as default boot configuration")
                effects.append("Changes take effect on next reboot")
            elif action == "test":
                effects.append("Build and activate configuration")
                effects.append("NOT set as boot default")
                effects.append("Good for testing changes")
        
        elif base_cmd == "nix-collect-garbage":
            if any(c["value"] == "-d" for c in components if c["type"] == "option"):
                effects.append("Delete old system generations")
                effects.append("Remove unreachable store paths")
                effects.append("Free disk space")
                warnings.append("Cannot rollback to deleted generations")
                warnings.append("This is irreversible")
        
        # Assess risk level
        risk = self._assess_risk(command)
        if risk == "high":
            warnings.append("⚠️ HIGH RISK: This command makes significant system changes")
        elif risk == "medium":
            warnings.append("⚡ MEDIUM RISK: This command modifies system state")
        
        return CommandExplanation(
            command=command,
            description=cmd_data["description"],
            components=components,
            effects=effects if effects else ["Execute the specified Nix operation"],
            warnings=warnings if warnings else [],
            alternatives=alternatives,
            examples=examples if examples else [f"{base_cmd} --help"],
            learn_more=f"https://nixos.org/manual/nix/stable/command-ref/{base_cmd}.html"
        )
    
    def _explain_generic_nix_command(self, command: str, components: List[Dict]) -> CommandExplanation:
        """Explain a generic Nix-related command"""
        effects = ["Execute Nix-related operation"]
        warnings = []
        
        # Check for risky patterns
        if "sudo" in command:
            warnings.append("Running with superuser privileges")
        if "--force" in command or "-f" in command:
            warnings.append("Forcing operation, safety checks may be bypassed")
        
        return CommandExplanation(
            command=command,
            description="Nix-related command",
            components=components,
            effects=effects,
            warnings=warnings,
            alternatives=[],
            examples=[],
            learn_more="https://nixos.org/manual/"
        )
    
    def _explain_general_command(self, command: str, components: List[Dict]) -> CommandExplanation:
        """Explain a general Linux command"""
        base_cmd = components[0]["value"] if components else ""
        
        effects = []
        warnings = []
        
        # Analyze common commands
        if base_cmd == "sudo":
            warnings.append("Running with superuser privileges")
            if len(components) > 1:
                actual_cmd = components[1]["value"]
                effects.append(f"Execute '{actual_cmd}' as root user")
        elif base_cmd == "rm":
            if any(c["value"] in ["-r", "-rf"] for c in components if c["type"] == "option"):
                warnings.append("⚠️ DANGER: Recursive deletion")
                warnings.append("Files cannot be recovered after deletion")
            effects.append("Delete files or directories")
        elif base_cmd == "systemctl":
            if len(components) > 1:
                action = components[1]["value"]
                if action == "stop":
                    effects.append("Stop systemd service")
                    warnings.append("Service will be terminated")
                elif action == "start":
                    effects.append("Start systemd service")
                elif action == "restart":
                    effects.append("Restart systemd service")
                    warnings.append("Service will be temporarily unavailable")
        
        return CommandExplanation(
            command=command,
            description=self._get_command_description(base_cmd),
            components=components,
            effects=effects if effects else ["Execute system command"],
            warnings=warnings,
            alternatives=[],
            examples=[],
            learn_more=None
        )
    
    def _assess_risk(self, command: str) -> str:
        """Assess risk level of a command"""
        command_lower = command.lower()
        
        for pattern in self.risk_levels["high"]:
            if pattern in command_lower:
                return "high"
        
        for pattern in self.risk_levels["medium"]:
            if pattern in command_lower:
                return "medium"
        
        return "low"
    
    def format_explanation(self, explanation: CommandExplanation) -> str:
        """Format explanation for display"""
        output = []
        
        output.append(f"📖 **Command Explanation**")
        output.append(f"```bash\n{explanation.command}\n```")
        output.append(f"**Purpose**: {explanation.description}")
        
        if explanation.components:
            output.append("\n🔧 **Breaking it down**:")
            for comp in explanation.components:
                icon = {"command": "📌", "option": "⚙️", "argument": "📝", 
                        "path": "📁", "package": "📦", "url": "🌐"}.get(comp["type"], "▪️")
                output.append(f"  {icon} `{comp['value']}` → {comp['description']}")
        
        if explanation.effects:
            output.append("\n✨ **What will happen**:")
            for effect in explanation.effects:
                output.append(f"  • {effect}")
        
        if explanation.warnings:
            output.append("\n⚠️ **Warnings**:")
            for warning in explanation.warnings:
                output.append(f"  • {warning}")
        
        if explanation.alternatives:
            output.append("\n🔄 **Alternative commands**:")
            for alt in explanation.alternatives:
                output.append(f"  • `{alt}`")
        
        if explanation.examples:
            output.append("\n💡 **Examples**:")
            for ex in explanation.examples:
                output.append(f"  • `{ex}`")
        
        if explanation.learn_more:
            output.append(f"\n📚 **Learn more**: {explanation.learn_more}")
        
        return "\n".join(output)


# Integration point for CLI
def explain_command(command: str) -> str:
    """
    Main entry point for command explanation
    Returns formatted explanation for the user
    """
    explainer = NixCommandExplainer()
    explanation = explainer.explain(command)
    return explainer.format_explanation(explanation)