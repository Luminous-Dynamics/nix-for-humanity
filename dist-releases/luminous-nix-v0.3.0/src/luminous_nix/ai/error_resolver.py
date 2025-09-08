"""
Error Resolution System for NixOS
Transforms cryptic errors into helpful, actionable suggestions
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ErrorSolution:
    """Represents a solution to a NixOS error"""
    error_type: str
    explanation: str
    solutions: List[str]
    commands: List[str]
    confidence: float
    learn_more: Optional[str] = None

class NixOSErrorResolver:
    """
    Intelligent error resolution for NixOS
    Uses pattern matching and AI to provide helpful solutions
    """
    
    def __init__(self):
        # Common NixOS error patterns and their solutions
        self.error_patterns = {
            # Package not found errors
            r"attribute ['\"]?(\w+)['\"]? .*missing": {
                "type": "attribute_missing",
                "handler": self._handle_attribute_missing
            },
            r"error: undefined variable ['\"]?(\w+)['\"]?": {
                "type": "undefined_variable", 
                "handler": self._handle_undefined_variable
            },
            
            # Collision errors
            r"collision between .* and .*": {
                "type": "package_collision",
                "handler": self._handle_collision
            },
            r"error: packages have the same priority": {
                "type": "priority_conflict",
                "handler": self._handle_priority_conflict
            },
            
            # Permission errors
            r"error: opening .* Permission denied": {
                "type": "permission_denied",
                "handler": self._handle_permission_denied
            },
            r"error: cannot open .* for writing": {
                "type": "write_permission",
                "handler": self._handle_write_permission
            },
            
            # Build errors
            r"error: build of .* failed": {
                "type": "build_failed",
                "handler": self._handle_build_failed
            },
            r"out of memory": {
                "type": "out_of_memory",
                "handler": self._handle_out_of_memory
            },
            
            # Syntax errors
            r"error: syntax error, unexpected": {
                "type": "syntax_error",
                "handler": self._handle_syntax_error
            },
            r"error: infinite recursion encountered": {
                "type": "infinite_recursion",
                "handler": self._handle_infinite_recursion
            },
            
            # Network errors
            r"error: unable to download.*curl": {
                "type": "download_failed",
                "handler": self._handle_download_failed
            },
            r"error: .* HTTP/.*404": {
                "type": "not_found_404",
                "handler": self._handle_404_error
            },
            
            # Flake errors
            r"error: flake .* does not exist": {
                "type": "flake_not_found",
                "handler": self._handle_flake_not_found
            },
            r"error: .* is not a valid flake": {
                "type": "invalid_flake",
                "handler": self._handle_invalid_flake
            },
            
            # Channel errors
            r"error: .* no such channel": {
                "type": "channel_not_found",
                "handler": self._handle_channel_not_found
            },
            
            # Disk space
            r"No space left on device": {
                "type": "disk_full",
                "handler": self._handle_disk_full
            }
        }
        
        # Common package name corrections
        self.package_corrections = {
            "neovim": "neovim",
            "neo-vim": "neovim",
            "firefox-browser": "firefox",
            "chrome": "google-chrome",
            "vscode": "vscode",
            "vs-code": "vscode",
            "visual-studio-code": "vscode",
            "docker-compose": "docker-compose",
            "docker_compose": "docker-compose",
            "nodejs": "nodejs",
            "node-js": "nodejs",
            "python3": "python3",
            "python-3": "python3",
        }
        
    def resolve_error(self, error_text: str) -> ErrorSolution:
        """
        Main entry point - analyzes error and returns solution
        """
        # Try pattern matching first
        for pattern, info in self.error_patterns.items():
            match = re.search(pattern, error_text, re.IGNORECASE | re.MULTILINE)
            if match:
                handler = info["handler"]
                return handler(error_text, match)
        
        # If no pattern matches, try generic analysis
        return self._analyze_generic_error(error_text)
    
    def _handle_attribute_missing(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle attribute missing errors"""
        package_name = match.group(1)
        
        # Check if it's a common misspelling
        corrected = self.package_corrections.get(package_name.lower())
        
        solutions = []
        commands = []
        
        if corrected:
            solutions.append(f"The package name might be '{corrected}' instead of '{package_name}'")
            commands.append(f"nix-env -iA nixpkgs.{corrected}")
        else:
            solutions.extend([
                f"Search for the correct package name",
                f"Check if the package exists in nixpkgs",
                f"You may need to update your channels"
            ])
            commands.extend([
                f"nix search nixpkgs {package_name}",
                f"nix-env -qaP | grep -i {package_name}",
                "sudo nix-channel --update"
            ])
        
        return ErrorSolution(
            error_type="attribute_missing",
            explanation=f"NixOS cannot find a package called '{package_name}'. This usually means the package name is incorrect or not in your channels.",
            solutions=solutions,
            commands=commands,
            confidence=0.9 if corrected else 0.7,
            learn_more="https://nixos.org/manual/nix/stable/command-ref/nix-env.html"
        )
    
    def _handle_undefined_variable(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle undefined variable errors"""
        variable = match.group(1)
        
        return ErrorSolution(
            error_type="undefined_variable",
            explanation=f"The variable '{variable}' is not defined in your configuration.",
            solutions=[
                "Check your imports - the variable might be defined in another file",
                "Ensure you're using 'with pkgs;' if it's a package name",
                "Check for typos in the variable name"
            ],
            commands=[
                "# Add to your configuration:",
                f"# with pkgs; # if '{variable}' is a package",
                f"# let {variable} = ...; in # if defining a variable"
            ],
            confidence=0.8,
            learn_more="https://nixos.org/manual/nix/stable/language/values.html"
        )
    
    def _handle_collision(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle package collision errors"""
        return ErrorSolution(
            error_type="package_collision",
            explanation="Two packages are trying to install files to the same location.",
            solutions=[
                "Set different priorities for the conflicting packages",
                "Remove one of the conflicting packages",
                "Use nix-env --set-flag to set priority"
            ],
            commands=[
                "# Install with higher priority (lower number = higher priority):",
                "nix-env -iA nixpkgs.package --priority 5",
                "# Or remove the conflicting package:",
                "nix-env -e conflicting-package",
                "# Set priority on existing package:",
                "nix-env --set-flag priority 10 package-name"
            ],
            confidence=0.85,
            learn_more="https://nixos.org/manual/nix/stable/command-ref/nix-env.html#priorities"
        )
    
    def _handle_priority_conflict(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle priority conflict errors"""
        return ErrorSolution(
            error_type="priority_conflict",
            explanation="Multiple packages have the same priority and are conflicting.",
            solutions=[
                "Assign different priorities to resolve the conflict",
                "Lower number means higher priority"
            ],
            commands=[
                "nix-env --set-flag priority 5 package1",
                "nix-env --set-flag priority 10 package2",
                "# Or reinstall with priority:",
                "nix-env -iA nixpkgs.package --priority 3"
            ],
            confidence=0.9,
            learn_more="https://nixos.org/manual/nix/stable/command-ref/nix-env.html#priorities"
        )
    
    def _handle_permission_denied(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle permission denied errors"""
        return ErrorSolution(
            error_type="permission_denied",
            explanation="You don't have permission to access the required files.",
            solutions=[
                "Run the command with sudo if it's a system operation",
                "Check file ownership and permissions",
                "Ensure you're in the correct user context"
            ],
            commands=[
                "# If system operation:",
                "sudo nixos-rebuild switch",
                "# Check permissions:",
                "ls -la /path/to/file",
                "# Fix ownership:",
                "sudo chown $USER:$USER /path/to/file"
            ],
            confidence=0.8,
            learn_more="https://nixos.org/manual/nixos/stable/#sec-changing-config"
        )
    
    def _handle_write_permission(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle write permission errors"""
        return ErrorSolution(
            error_type="write_permission",
            explanation="Cannot write to the specified location.",
            solutions=[
                "Use sudo for system-level changes",
                "Check if the filesystem is read-only",
                "Verify disk space availability"
            ],
            commands=[
                "sudo nixos-rebuild switch",
                "df -h  # Check disk space",
                "mount | grep ' / '  # Check if filesystem is read-only"
            ],
            confidence=0.75,
            learn_more="https://nixos.org/manual/nixos/stable/"
        )
    
    def _handle_build_failed(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle build failure errors"""
        return ErrorSolution(
            error_type="build_failed",
            explanation="The package failed to build from source.",
            solutions=[
                "Check if there's a binary cache available",
                "Look for build logs for specific errors",
                "Try updating nixpkgs channel",
                "Check if there's enough disk space and RAM"
            ],
            commands=[
                "nix log /nix/store/...  # Check build logs",
                "sudo nix-channel --update",
                "nix-build '<nixpkgs>' -A package --option substituters 'https://cache.nixos.org'",
                "df -h  # Check disk space",
                "free -h  # Check memory"
            ],
            confidence=0.6,
            learn_more="https://nixos.org/manual/nix/stable/command-ref/nix-build.html"
        )
    
    def _handle_out_of_memory(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle out of memory errors"""
        return ErrorSolution(
            error_type="out_of_memory",
            explanation="The system ran out of memory during the operation.",
            solutions=[
                "Close other applications to free memory",
                "Increase swap space",
                "Use --max-jobs 1 to limit parallel builds",
                "Consider adding more RAM to your system"
            ],
            commands=[
                "free -h  # Check current memory usage",
                "sudo swapon --show  # Check swap status",
                "# Build with limited parallelism:",
                "nixos-rebuild switch --max-jobs 1",
                "# Create temporary swap file:",
                "sudo dd if=/dev/zero of=/swapfile bs=1G count=4",
                "sudo mkswap /swapfile && sudo swapon /swapfile"
            ],
            confidence=0.85,
            learn_more="https://nixos.wiki/wiki/Storage_optimization"
        )
    
    def _handle_syntax_error(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle syntax errors in Nix files"""
        # Try to extract line number if available
        line_match = re.search(r"at .*:(\d+):(\d+)", error)
        location = ""
        if line_match:
            location = f" at line {line_match.group(1)}, column {line_match.group(2)}"
        
        return ErrorSolution(
            error_type="syntax_error",
            explanation=f"There's a syntax error in your Nix configuration{location}.",
            solutions=[
                "Check for missing semicolons (;) at the end of statements",
                "Verify all brackets { } and parentheses ( ) are balanced",
                "Ensure strings are properly quoted",
                "Check for missing 'in' keyword in let expressions"
            ],
            commands=[
                "# Validate your configuration:",
                "nix-2-5 secondsiate --parse /etc/nixos/configuration.nix",
                "# Format your file (requires nixpkgs-fmt):",
                "nixpkgs-fmt /etc/nixos/configuration.nix"
            ],
            confidence=0.7,
            learn_more="https://nixos.org/manual/nix/stable/language/index.html"
        )
    
    def _handle_infinite_recursion(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle infinite recursion errors"""
        return ErrorSolution(
            error_type="infinite_recursion",
            explanation="Your configuration has a circular dependency causing infinite recursion.",
            solutions=[
                "Check for circular imports between files",
                "Look for self-referential definitions",
                "Use 'rec' keyword carefully with attribute sets",
                "Check overlay definitions for circular dependencies"
            ],
            commands=[
                "# Debug with --show-trace:",
                "nixos-rebuild switch --show-trace",
                "# Test specific attributes:",
                "nix-2-5 secondsiate --eval -E 'with import <nixpkgs> {}; your-attribute'"
            ],
            confidence=0.7,
            learn_more="https://nixos.org/manual/nix/stable/language/constructs.html#recursive-sets"
        )
    
    def _handle_download_failed(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle download failure errors"""
        return ErrorSolution(
            error_type="download_failed",
            explanation="Failed to download a required file or package.",
            solutions=[
                "Check your internet connection",
                "Try using a different binary cache",
                "The source might be temporarily unavailable",
                "Check proxy settings if behind a firewall"
            ],
            commands=[
                "# Test connectivity:",
                "curl -I https://cache.nixos.org",
                "# Try alternative cache:",
                "nix-build --option substituters 'https://cache.nixos.org https://nix-community.cachix.org'",
                "# Retry with increased timeout:",
                "nix-build --option connect-timeout 300"
            ],
            confidence=0.75,
            learn_more="https://nixos.org/manual/nix/stable/command-ref/conf-file.html#conf-substituters"
        )
    
    def _handle_404_error(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle 404 not found errors"""
        return ErrorSolution(
            error_type="not_found_404",
            explanation="The requested resource was not found (HTTP 404).",
            solutions=[
                "The package source might have moved or been deleted",
                "Update your channels to get the latest package definitions",
                "Check if the package is deprecated"
            ],
            commands=[
                "sudo nix-channel --update",
                "nix search nixpkgs package-name  # Search for alternatives",
                "# Check package status:",
                "nix eval nixpkgs#package-name.meta.broken"
            ],
            confidence=0.8,
            learn_more="https://search.nixos.org/packages"
        )
    
    def _handle_flake_not_found(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle flake not found errors"""
        return ErrorSolution(
            error_type="flake_not_found",
            explanation="The specified flake cannot be found.",
            solutions=[
                "Check the flake URL or path is correct",
                "Ensure the repository is accessible",
                "Initialize a flake if it doesn't exist"
            ],
            commands=[
                "# Initialize a new flake:",
                "nix flake init",
                "# Check flake info:",
                "nix flake info /path/to/flake",
                "# Update flake inputs:",
                "nix flake update"
            ],
            confidence=0.8,
            learn_more="https://nixos.wiki/wiki/Flakes"
        )
    
    def _handle_invalid_flake(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle invalid flake errors"""
        return ErrorSolution(
            error_type="invalid_flake",
            explanation="The flake.nix file is invalid or improperly formatted.",
            solutions=[
                "Check flake.nix syntax",
                "Ensure required attributes (description, inputs, outputs) are present",
                "Validate the flake structure"
            ],
            commands=[
                "# Check flake:",
                "nix flake check",
                "# Show flake contents:",
                "nix flake show",
                "# Validate syntax:",
                "nix-2-5 secondsiate --parse flake.nix"
            ],
            confidence=0.75,
            learn_more="https://nixos.wiki/wiki/Flakes"
        )
    
    def _handle_channel_not_found(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle channel not found errors"""
        return ErrorSolution(
            error_type="channel_not_found",
            explanation="The specified Nix channel doesn't exist.",
            solutions=[
                "List available channels",
                "Add the required channel",
                "Update existing channels"
            ],
            commands=[
                "# List channels:",
                "sudo nix-channel --list",
                "# Add nixos channel:",
                "sudo nix-channel --add https://nixos.org/channels/nixos-unstable nixos",
                "# Update channels:",
                "sudo nix-channel --update"
            ],
            confidence=0.85,
            learn_more="https://nixos.org/manual/nix/stable/command-ref/nix-channel.html"
        )
    
    def _handle_disk_full(self, error: str, match: re.Match) -> ErrorSolution:
        """Handle disk full errors"""
        return ErrorSolution(
            error_type="disk_full",
            explanation="Your disk is full and cannot store more data.",
            solutions=[
                "Free up disk space by removing old generations",
                "Clean the Nix store",
                "Remove unnecessary files",
                "Consider expanding your disk"
            ],
            commands=[
                "# Check disk usage:",
                "df -h",
                "# List generations:",
                "sudo nix-env --list-generations",
                "# Delete old generations (keep last 3):",
                "sudo nix-collect-garbage -d --delete-older-than 3d",
                "# Optimize store:",
                "nix-store --optimize",
                "# Find large files:",
                "du -sh /nix/store/* | sort -h | tail -20"
            ],
            confidence=0.95,
            learn_more="https://nixos.wiki/wiki/Storage_optimization"
        )
    
    def _analyze_generic_error(self, error: str) -> ErrorSolution:
        """Fallback for unrecognized errors"""
        # Try to extract useful information
        suggestions = ["Check the full error message for more details"]
        commands = ["nixos-rebuild switch --show-trace  # Get detailed error trace"]
        
        # Look for file paths
        if "/etc/nixos/" in error:
            suggestions.append("The error appears to be in your NixOS configuration")
            commands.append("sudo nano /etc/nixos/configuration.nix  # Edit configuration")
        
        # Look for package names
        if "nixpkgs" in error.lower():
            suggestions.append("This might be a package-related issue")
            commands.append("sudo nix-channel --update  # Update package channels")
        
        # Look for network issues
        if any(word in error.lower() for word in ["timeout", "connection", "network"]):
            suggestions.append("This appears to be a network-related issue")
            commands.append("ping cache.nixos.org  # Test connectivity")
        
        return ErrorSolution(
            error_type="unknown",
            explanation="This error doesn't match known patterns. Here are some general suggestions:",
            solutions=suggestions,
            commands=commands,
            confidence=0.3,
            learn_more="https://nixos.org/manual/nixos/stable/index.html#ch-troubleshooting"
        )
    
    def explain_error(self, error_solution: ErrorSolution) -> str:
        """Format the error solution for display to the user"""
        output = []
        output.append(f"🔍 **Error Type**: {error_solution.error_type.replace('_', ' ').title()}")
        output.append(f"📖 **Explanation**: {error_solution.explanation}")
        output.append(f"🔧 **Confidence**: {error_solution.confidence:.0%}")
        output.append("\n💡 **Solutions**:")
        for i, solution in enumerate(error_solution.solutions, 1):
            output.append(f"  {i}. {solution}")
        
        output.append("\n📝 **Commands to try**:")
        for cmd in error_solution.commands:
            if cmd.startswith("#"):
                output.append(f"  {cmd}")
            else:
                output.append(f"  $ {cmd}")
        
        if error_solution.learn_more:
            output.append(f"\n📚 **Learn more**: {error_solution.learn_more}")
        
        return "\n".join(output)


# Integration point for CLI
def resolve_nixos_error(error_text: str) -> str:
    """
    Main entry point for error resolution
    Returns formatted help text for the user
    """
    resolver = NixOSErrorResolver()
    solution = resolver.resolve_error(error_text)
    return resolver.explain_error(solution)