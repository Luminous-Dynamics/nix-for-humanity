#!/usr/bin/env python3
"""
Example: How the enhanced system handles Docker installation
Shows the intelligence of recognizing Docker as a service, not just a package
"""

import os
import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

from luminous_nix.core.responses import ResponseGenerator, SolutionPath, PathType, EducationalContent, ContextWarning

def docker_example():
    """Show how we intelligently handle Docker"""
    
    print("🐳 Enhanced Response for 'install docker'\n")
    print("=" * 80)
    
    # Create custom Docker response
    paths = [
        SolutionPath(
            path_type=PathType.DECLARATIVE,
            title="Enable Docker Service (Recommended)",
            description="Docker on NixOS requires service configuration, not just package installation",
            commands=[
                "# Edit your configuration",
                "sudo nano /etc/nixos/configuration.nix",
                "",
                "# Add Docker service configuration:",
                "virtualisation.docker.enable = true;",
                "",
                "# Allow your user to run Docker without sudo:",
                "users.users.YOUR_USERNAME.extraGroups = [ \"docker\" ];",
                "",
                "# Apply the configuration",
                "sudo nixos-rebuild switch"
            ],
            explanation="Enables Docker with proper daemon configuration",
            pros=[
                "Docker daemon runs automatically",
                "Proper systemd integration",
                "User permissions configured correctly",
                "Survives system updates"
            ],
            cons=[
                "Requires system rebuild",
                "Need to log out/in for group changes"
            ],
            requires_sudo=True,
            permanence="system",
            reproducible=True
        ),
        
        SolutionPath(
            path_type=PathType.IMPERATIVE,
            title="Quick Docker Test (Without Service)",
            description="Try Docker without enabling the service",
            commands=[
                "# Enter a shell with Docker",
                "nix-shell -p docker",
                "",
                "# Note: You'll need to start the daemon manually:",
                "sudo dockerd &",
                "",
                "# Then you can use Docker:",
                "docker run hello-world"
            ],
            explanation="Quick way to test Docker without system changes",
            pros=[
                "No system configuration needed",
                "Good for testing",
                "Leaves no permanent changes"
            ],
            cons=[
                "Daemon must be started manually",
                "No systemd integration",
                "Lost when shell exits"
            ],
            requires_sudo=True,
            permanence="temporary",
            reproducible=False
        ),
        
        SolutionPath(
            path_type=PathType.DECLARATIVE,
            title="Docker with Additional Options",
            description="Advanced Docker setup with common options",
            commands=[
                "# Configuration with storage driver and insecure registries:",
                "virtualisation.docker = {",
                "  enable = true;",
                "  storageDriver = \"overlay2\";",
                "  daemon.settings = {",
                "    insecure-registries = [ \"localhost:5000\" ];",
                "  };",
                "};"
            ],
            explanation="For users who need specific Docker configurations",
            pros=[
                "Full control over Docker daemon",
                "Optimized storage driver",
                "Support for local registries"
            ],
            cons=[
                "More complex configuration",
                "Requires understanding Docker internals"
            ],
            requires_sudo=True,
            permanence="system",
            reproducible=True
        )
    ]
    
    # Educational content about services vs packages
    education = EducationalContent(
        concept="Services vs Packages in NixOS",
        explanation=(
            "Docker isn't just a package - it's a system service that needs a daemon. "
            "In NixOS, services are configured declaratively through the configuration.nix "
            "file. This ensures the Docker daemon starts automatically and runs with the "
            "correct permissions and settings."
        ),
        why_it_matters=(
            "Simply installing the Docker package won't start the daemon. NixOS's "
            "declarative service management ensures your Docker setup is reproducible "
            "and properly integrated with the system."
        ),
        next_steps=[
            "Learn about other NixOS services: virtualisation.libvirtd, services.kubernetes",
            "Explore Docker-Compose integration: virtualisation.docker.enableOnBoot",
            "Consider Podman as a rootless alternative: virtualisation.podman.enable"
        ]
    )
    
    # Warning about common mistake
    warning = ContextWarning(
        warning_type="service_not_package",
        message="Docker requires service configuration, not just package installation",
        suggestion="Use the declarative service configuration for a proper Docker setup"
    )
    
    # Create response
    from luminous_nix.core.responses import Response, DryRunSuggestion
    
    response = Response(
        intent="install_docker",
        summary="I'll help you set up Docker on NixOS! Docker is a service that needs special configuration:",
        paths=paths,
        education=education,
        warnings=[warning],
        dry_run=DryRunSuggestion(
            command="ask-nix --dry-run enable docker service",
            description="Preview the configuration changes without applying them"
        ),
        related_topics=["docker-compose", "podman", "kubernetes", "container management"]
    )
    
    # Display the response
    print(response.format_for_cli())
    
    print("\n" + "=" * 80)
    print("\n✨ Notice how the system:")
    print("- Recognizes Docker as a service, not just a package")
    print("- Provides proper NixOS configuration guidance")
    print("- Explains WHY the service approach is needed")
    print("- Offers alternatives and related topics")
    print("- Includes warnings about common mistakes")

if __name__ == "__main__":
    docker_example()