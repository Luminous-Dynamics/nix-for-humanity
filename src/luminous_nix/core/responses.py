"""
from typing import Dict, List, Optional
Enhanced Response System for Nix for Humanity
Implements two-path philosophy and educational responses
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import textwrap

class PathType(Enum):
    """Types of solution paths"""
    IMPERATIVE = "imperative"
    DECLARATIVE = "declarative"
    HOME_MANAGER = "home_manager"
    FLAKE = "flake"
    TEMPORARY = "temporary"

@dataclass
class SolutionPath:
    """Represents one way to solve a problem"""
    path_type: PathType
    title: str
    description: str
    commands: List[str]
    explanation: str
    pros: List[str]
    cons: List[str]
    requires_sudo: bool = False
    permanence: str = "temporary"  # temporary, user, system
    reproducible: bool = False
    learn_more: Optional[str] = None

@dataclass
class EducationalContent:
    """Educational content related to the operation"""
    concept: str
    explanation: str
    why_it_matters: str
    next_steps: Optional[List[str]] = None

@dataclass
class ContextWarning:
    """Warnings about the current context"""
    warning_type: str
    message: str
    suggestion: str

@dataclass
class DryRunSuggestion:
    """Suggestion to try dry-run first"""
    command: str
    description: str

@dataclass
class Response:
    """Enhanced response with multiple paths and education"""
    intent: str
    summary: str
    paths: List[SolutionPath]
    education: Optional[EducationalContent] = None
    warnings: List[ContextWarning] = field(default_factory=list)
    dry_run: Optional[DryRunSuggestion] = None
    related_topics: List[str] = field(default_factory=list)
    
    def format_for_cli(self) -> str:
        """Format response for CLI output"""
        output = []
        
        # Summary
        output.append(f"🎯 {self.summary}")
        output.append("")
        
        # Warnings first
        if self.warnings:
            for warning in self.warnings:
                output.append(f"⚠️  {warning.message}")
                output.append(f"   💡 {warning.suggestion}")
            output.append("")
        
        # Paths
        for i, path in enumerate(self.paths, 1):
            output.append(f"**Option {i}: {path.title}**")
            output.append(f"{path.description}")
            output.append("")
            
            # Commands
            output.append("Commands:")
            for cmd in path.commands:
                if cmd.startswith("#"):
                    output.append(f"  {cmd}")
                else:
                    output.append(f"  ```bash")
                    output.append(f"  {cmd}")
                    output.append(f"  ```")
            output.append("")
            
            # Properties
            props = []
            if path.requires_sudo:
                props.append("🔐 Requires sudo")
            if path.reproducible:
                props.append("♻️  Reproducible")
            props.append(f"⏱️  {path.permanence.title()}")
            
            output.append(" • ".join(props))
            output.append("")
            
            # Pros/Cons
            if path.pros:
                output.append("✅ Pros:")
                for pro in path.pros:
                    output.append(f"  - {pro}")
            
            if path.cons:
                output.append("❌ Cons:")
                for con in path.cons:
                    output.append(f"  - {con}")
            
            output.append("")
            output.append("-" * 40)
            output.append("")
        
        # Dry run suggestion
        if self.dry_run:
            output.append("🧪 **Want to preview first?**")
            output.append(self.dry_run.description)
            output.append(f"```bash")
            output.append(self.dry_run.command)
            output.append("```")
            output.append("")
        
        # Educational content
        if self.education:
            output.append("📚 **Understanding NixOS:**")
            output.append(f"**{self.education.concept}**")
            output.append(textwrap.fill(self.education.explanation, 70))
            output.append("")
            output.append(f"**Why this matters:** {self.education.why_it_matters}")
            
            if self.education.next_steps:
                output.append("")
                output.append("**Learn more:**")
                for step in self.education.next_steps:
                    output.append(f"  - {step}")
            output.append("")
        
        # Related topics
        if self.related_topics:
            output.append("🔗 **Related topics:** " + ", ".join(self.related_topics))
        
        return "\n".join(output)


class ResponseGenerator:
    """Generates educational two-path responses"""
    
    def __init__(self):
        self.templates = self._init_templates()
    
    def _init_templates(self) -> Dict[str, Any]:
        """Initialize response templates for different operations"""
        return {
            'install_package': self._install_package_template,
            'update_system': self._update_system_template,
            'remove_package': self._remove_package_template,
            'enable_service': self._enable_service_template,
        }
    
    def generate(self, intent: str, context: Dict[str, Any]) -> Response:
        """Generate appropriate response for intent"""
        
        template_fn = self.templates.get(intent, self._default_template)
        return template_fn(context)
    
    def _install_package_template(self, context: Dict[str, Any]) -> Response:
        """Generate install package response"""
        package = context.get('package', 'package')
        
        paths = [
            # Quick install
            SolutionPath(
                path_type=PathType.IMPERATIVE,
                title="Quick Install (For Right Now)",
                description="Install immediately for current user",
                commands=[
                    f"nix profile install nixpkgs#{package}"
                ],
                explanation="Installs the package immediately for your user",
                pros=[
                    "Immediate access",
                    "No configuration files needed",
                    "No sudo required"
                ],
                cons=[
                    "Not reproducible",
                    "Only for current user",
                    "Lost on system reinstall"
                ],
                requires_sudo=False,
                permanence="user",
                reproducible=False
            ),
            
            # System configuration
            SolutionPath(
                path_type=PathType.DECLARATIVE,
                title="System Configuration (The NixOS Way)",
                description="Add to your system configuration for permanent installation",
                commands=[
                    "# Edit your configuration",
                    "sudo nano /etc/nixos/configuration.nix",
                    "",
                    "# Add package to systemPackages:",
                    f"environment.systemPackages = with pkgs; [",
                    f"  {package}",
                    f"];",
                    "",
                    "# Apply the configuration",
                    "sudo nixos-rebuild switch"
                ],
                explanation="Makes the package part of your system definition",
                pros=[
                    "Reproducible system state",
                    "Survives reinstalls",
                    "Available to all users",
                    "Version controlled with your config"
                ],
                cons=[
                    "Requires sudo access",
                    "Takes longer (rebuilds system)",
                    "Need to edit configuration"
                ],
                requires_sudo=True,
                permanence="system",
                reproducible=True,
                learn_more="https://nixos.org/manual/nixos/stable/#sec-declarative-package-mgmt"
            ),
            
            # Try without installing
            SolutionPath(
                path_type=PathType.TEMPORARY,
                title="Just Try It (Temporary Shell)",
                description="Try the package without installing",
                commands=[
                    f"nix-shell -p {package}"
                ],
                explanation="Opens a shell with the package available temporarily",
                pros=[
                    "No installation needed",
                    "Perfect for testing",
                    "Leaves no trace"
                ],
                cons=[
                    "Only available in that shell",
                    "Lost when you exit"
                ],
                requires_sudo=False,
                permanence="temporary",
                reproducible=True
            )
        ]
        
        # Add Home Manager path if available
        if context.get('has_home_manager', False):
            paths.insert(1, SolutionPath(
                path_type=PathType.HOME_MANAGER,
                title="Home Manager (User-Level Declarative)",
                description="Declarative user package management",
                commands=[
                    "# Edit Home Manager config",
                    "nano ~/.config/home-manager/home.nix",
                    "",
                    "# Add package:",
                    f"home.packages = with pkgs; [",
                    f"  {package}",
                    f"];",
                    "",
                    "# Apply changes",
                    "home-manager switch"
                ],
                explanation="Declarative configuration for user packages",
                pros=[
                    "Reproducible like system config",
                    "No sudo needed",
                    "User-specific customization"
                ],
                cons=[
                    "Requires Home Manager setup",
                    "Another tool to learn"
                ],
                requires_sudo=False,
                permanence="user",
                reproducible=True
            ))
        
        # Educational content
        education = EducationalContent(
            concept="Declarative vs Imperative",
            explanation=(
                "NixOS has two philosophies for managing packages. Imperative "
                "commands (like 'nix profile install') make immediate changes, "
                "similar to traditional package managers. Declarative configuration "
                "describes your desired system state in configuration files, which "
                "NixOS then builds to match exactly."
            ),
            why_it_matters=(
                "Declarative configuration is reproducible - you can recreate "
                "your exact system on another machine just by copying your "
                "configuration files."
            ),
            next_steps=[
                "Learn about configuration.nix structure",
                "Explore Home Manager for user packages",
                "Try version-controlling your configuration"
            ]
        )
        
        # Check for warnings
        warnings = []
        if package in ['docker', 'virtualbox', 'libvirt']:
            warnings.append(ContextWarning(
                warning_type="service_package",
                message=f"{package} is a service that needs configuration beyond just installation",
                suggestion=f"After installing, you'll need to enable the service. Try: ask-nix 'enable {package} service'"
            ))
        
        # Dry run suggestion
        dry_run = DryRunSuggestion(
            command=f"ask-nix --dry-run install {package}",
            description="See what would be installed without making changes"
        )
        
        return Response(
            intent="install_package",
            summary=f"I'll help you install {package}! Here are three ways to do it:",
            paths=paths,
            education=education,
            warnings=warnings,
            dry_run=dry_run,
            related_topics=["package search", "removing packages", "updating packages"]
        )
    
    def _update_system_template(self, context: Dict[str, Any]) -> Response:
        """Generate system update response"""
        
        paths = [
            SolutionPath(
                path_type=PathType.DECLARATIVE,
                title="Full System Update",
                description="Update channels and rebuild system",
                commands=[
                    "# Update channel information",
                    "sudo nix-channel --update",
                    "",
                    "# Rebuild with updates",
                    "sudo nixos-rebuild switch",
                    "",
                    "# Or do both in one command:",
                    "sudo nixos-rebuild switch --upgrade"
                ],
                explanation="Updates all system packages to latest channel versions",
                pros=[
                    "Updates everything",
                    "Creates new generation for rollback",
                    "Applies configuration changes too"
                ],
                cons=[
                    "Can take significant time",
                    "Requires restart for some updates",
                    "May introduce breaking changes"
                ],
                requires_sudo=True,
                permanence="system",
                reproducible=True
            ),
            
            SolutionPath(
                path_type=PathType.IMPERATIVE,
                title="Update User Packages Only",
                description="Update just your profile packages",
                commands=[
                    "nix profile upgrade"
                ],
                explanation="Updates packages installed with 'nix profile install'",
                pros=[
                    "Faster than system update",
                    "No sudo required",
                    "Won't affect system services"
                ],
                cons=[
                    "Only updates user packages",
                    "System packages remain outdated",
                    "Inconsistent system state"
                ],
                requires_sudo=False,
                permanence="user",
                reproducible=False
            )
        ]
        
        education = EducationalContent(
            concept="Generations and Rollbacks",
            explanation=(
                "Every time you rebuild NixOS, it creates a new 'generation' - "
                "a complete snapshot of your system. If an update breaks something, "
                "you can instantly rollback to any previous generation. This makes "
                "updates safe to try!"
            ),
            why_it_matters=(
                "Unlike traditional distros, you can fearlessly update NixOS "
                "knowing you can always go back to a working state."
            ),
            next_steps=[
                "View generations: sudo nix-env --list-generations --profile /nix/var/nix/profiles/system",
                "Rollback if needed: sudo nixos-rebuild switch --rollback",
                "Clean old generations: sudo nix-collect-garbage -d"
            ]
        )
        
        warnings = []
        if context.get('days_since_update', 30) > 60:
            warnings.append(ContextWarning(
                warning_type="old_system",
                message="Your system hasn't been updated in over 60 days",
                suggestion="Consider updating soon for security patches"
            ))
        
        return Response(
            intent="update_system",
            summary="I'll help you update your NixOS system!",
            paths=paths,
            education=education,
            warnings=warnings,
            related_topics=["rollback", "generations", "garbage collection"]
        )
    
    def _enable_service_template(self, context: Dict[str, Any]) -> Response:
        """Generate enable service response"""
        service = context.get('service', 'service')
        
        # Service name mapping
        service_map = {
            'ssh': 'openssh',
            'web': 'nginx',
            'httpd': 'apache',
            'mysql': 'mysql',
            'postgres': 'postgresql',
            'docker': 'docker'
        }
        
        nix_service = service_map.get(service, service)
        
        paths = [
            SolutionPath(
                path_type=PathType.DECLARATIVE,
                title="Enable in Configuration (Recommended)",
                description="Add service to your system configuration",
                commands=[
                    "# Edit configuration",
                    "sudo nano /etc/nixos/configuration.nix",
                    "",
                    "# Add service configuration:",
                    f"services.{nix_service}.enable = true;",
                    "",
                    "# Common options (optional):",
                    f"services.{nix_service}.settings = {{",
                    "  # Service-specific settings",
                    "};",
                    "",
                    "# Apply configuration",
                    "sudo nixos-rebuild switch"
                ],
                explanation="Permanently enables the service in your system",
                pros=[
                    "Service starts on boot",
                    "Configuration is reproducible",
                    "Can add service-specific settings"
                ],
                cons=[
                    "Requires system rebuild",
                    "Need sudo access"
                ],
                requires_sudo=True,
                permanence="system",
                reproducible=True
            ),
            
            SolutionPath(
                path_type=PathType.IMPERATIVE,
                title="Quick Test (Temporary)",
                description="Start service just for current session",
                commands=[
                    f"# Start service immediately",
                    f"sudo systemctl start {nix_service}",
                    "",
                    f"# Check status",
                    f"sudo systemctl status {nix_service}"
                ],
                explanation="Starts service temporarily without configuration",
                pros=[
                    "Immediate effect",
                    "Good for testing"
                ],
                cons=[
                    "Not persistent across reboots",
                    "No configuration integration",
                    "Service may not be installed"
                ],
                requires_sudo=True,
                permanence="temporary",
                reproducible=False
            )
        ]
        
        education = EducationalContent(
            concept="NixOS Services",
            explanation=(
                "In NixOS, services are configured declaratively through your "
                "configuration.nix file. This ensures services are configured "
                "correctly and consistently every time your system boots."
            ),
            why_it_matters=(
                "Declarative service configuration prevents 'configuration drift' "
                "and makes it easy to replicate your setup on other machines."
            ),
            next_steps=[
                f"View service options: man configuration.nix | grep -A 20 {nix_service}",
                f"See example configs: https://search.nixos.org/options?query={nix_service}",
                "Check all enabled services: systemctl list-unit-files --state=enabled"
            ]
        )
        
        return Response(
            intent="enable_service",
            summary=f"I'll help you enable the {service} service on NixOS!",
            paths=paths,
            education=education,
            related_topics=["disable service", "service status", "service logs"]
        )
    
    def _remove_package_template(self, context: Dict[str, Any]) -> Response:
        """Generate remove package response"""
        package = context.get('package', 'package')
        
        paths = [
            SolutionPath(
                path_type=PathType.IMPERATIVE,
                title="Remove User Package",
                description="Remove package installed with nix profile",
                commands=[
                    "# List installed packages",
                    "nix profile list",
                    "",
                    "# Remove by package name",
                    f"nix profile remove {package}",
                    "",
                    "# Or remove by number from list",
                    "# nix profile remove 3"
                ],
                explanation="Removes package from user profile",
                pros=[
                    "Immediate removal",
                    "No sudo required"
                ],
                cons=[
                    "Only removes user packages",
                    "Won't remove system packages"
                ],
                requires_sudo=False,
                permanence="user",
                reproducible=False
            ),
            
            SolutionPath(
                path_type=PathType.DECLARATIVE,
                title="Remove from System Configuration",
                description="Remove package from configuration.nix",
                commands=[
                    "# Edit configuration",
                    "sudo nano /etc/nixos/configuration.nix",
                    "",
                    f"# Remove {package} from systemPackages",
                    "# Delete or comment out the line with the package",
                    "",
                    "# Apply changes",
                    "sudo nixos-rebuild switch",
                    "",
                    "# Clean up old packages",
                    "sudo nix-collect-garbage"
                ],
                explanation="Removes package from system definition",
                pros=[
                    "Cleanly removes from system",
                    "Maintains reproducibility",
                    "Frees disk space with garbage collection"
                ],
                cons=[
                    "Requires editing configuration",
                    "Need sudo access",
                    "Requires rebuild"
                ],
                requires_sudo=True,
                permanence="system",
                reproducible=True
            )
        ]
        
        education = EducationalContent(
            concept="Garbage Collection",
            explanation=(
                "NixOS keeps old package versions until you run garbage collection. "
                "This allows rollbacks but uses disk space. Running 'nix-collect-garbage' "
                "removes unreferenced packages."
            ),
            why_it_matters=(
                "Understanding garbage collection helps you manage disk space while "
                "maintaining the ability to rollback when needed."
            ),
            next_steps=[
                "Free space: sudo nix-collect-garbage -d",
                "Keep some generations: sudo nix-collect-garbage --delete-older-than 30d",
                "Check disk usage: nix-store --gc --print-dead"
            ]
        )
        
        return Response(
            intent="remove_package",
            summary=f"I'll help you remove {package} from your system!",
            paths=paths,
            education=education,
            related_topics=["garbage collection", "disk usage", "list packages"]
        )
    
    def _default_template(self, context: Dict[str, Any]) -> Response:
        """Default response template"""
        return Response(
            intent=context.get('intent', 'unknown'),
            summary="I'll help you with that!",
            paths=[],
            education=None,
            warnings=[],
            related_topics=[]
        )


# Example usage
if __name__ == "__main__":
    generator = ResponseGenerator()
    
    # Test install response
    response = generator.generate('install_package', {'package': 'firefox'})
    print(response.format_for_cli())
    
    print("\n" + "="*80 + "\n")
    
    # Test service enable response
    response = generator.generate('enable_service', {'service': 'ssh'})
    print(response.format_for_cli())