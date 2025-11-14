#!/usr/bin/env python3
"""
NixOS Documentation Corpus Builder

This module creates a comprehensive training corpus from:
- NixOS manual and documentation
- Nixpkgs repository documentation
- NixOS Wiki content
- Common configuration patterns
- Real-world examples
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel


@dataclass
class DocumentChunk:
    """A chunk of documentation for training"""

    id: str
    source: str  # manual, wiki, nixpkgs, examples
    category: str  # packages, services, configuration, troubleshooting
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    def to_training_format(self) -> Dict[str, Any]:
        """Convert to format suitable for training"""
        return {
            "text": self.content,
            "metadata": {
                "source": self.source,
                "category": self.category,
                "title": self.title,
                "keywords": self.keywords,
            },
            "examples": self.examples,
        }


@dataclass
class QAPair:
    """Question-Answer pair for training"""

    question: str
    answer: str
    context: str
    category: str
    confidence: float = 1.0

    def to_training_format(self) -> Dict[str, Any]:
        """Convert to training format"""
        return {
            "instruction": self.question,
            "input": self.context,
            "output": self.answer,
            "metadata": {"category": self.category, "confidence": self.confidence},
        }


class NixOSCorpusBuilder:
    """
    Builds comprehensive NixOS training corpus

    Features:
    - Extracts from multiple sources
    - Creates Q&A pairs
    - Generates examples
    - Validates accuracy
    """

    def __init__(self, output_dir: str = "corpus"):
        """Initialize the corpus builder"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.console = Console()
        self.documents: List[DocumentChunk] = []
        self.qa_pairs: List[QAPair] = []

        # Statistics
        self.stats = {"documents": 0, "qa_pairs": 0, "examples": 0, "total_tokens": 0}

    def build_corpus(self) -> Dict[str, Any]:
        """Build the complete corpus"""
        self.console.print("[bold cyan]🏗️ Building NixOS Training Corpus[/bold cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console,
        ) as progress:
            # Extract from different sources
            task1 = progress.add_task("Extracting NixOS options...", total=100)
            self._extract_nixos_options(progress, task1)

            task2 = progress.add_task("Extracting package info...", total=100)
            self._extract_package_info(progress, task2)

            task3 = progress.add_task("Extracting service configs...", total=100)
            self._extract_service_configs(progress, task3)

            task4 = progress.add_task("Generating Q&A pairs...", total=100)
            self._generate_qa_pairs(progress, task4)

            task5 = progress.add_task("Creating examples...", total=100)
            self._create_examples(progress, task5)

        # Save corpus
        self._save_corpus()

        # Display statistics
        self._display_stats()

        return {
            "documents": len(self.documents),
            "qa_pairs": len(self.qa_pairs),
            "output_dir": str(self.output_dir),
        }

    def _extract_nixos_options(self, progress, task):
        """Extract NixOS configuration options"""
        try:
            # Get all NixOS options
            result = subprocess.run(
                [
                    "nix-2-5 secondsiate",
                    "--eval",
                    "--json",
                    "-E",
                    "with import <nixpkgs/nixos> {}; builtins.attrNames options",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                option_names = json.loads(result.stdout)

                # Sample common options for training
                common_options = [
                    "boot.loader",
                    "networking.firewall",
                    "services.nginx",
                    "users.users",
                    "environment.systemPackages",
                    "services.openssh",
                    "system.stateVersion",
                    "time.timeZone",
                    "i18n.defaultLocale",
                ]

                for i, option in enumerate(common_options):
                    if option in option_names:
                        doc = self._get_option_documentation(option)
                        if doc:
                            self.documents.append(doc)

                    progress.update(task, completed=(i + 1) * 100 / len(common_options))

        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Could not extract options: {e}[/yellow]"
            )

        progress.update(task, completed=100)

    def _get_option_documentation(self, option: str) -> Optional[DocumentChunk]:
        """Get documentation for a specific option"""
        try:
            # Build documentation chunk
            doc = DocumentChunk(
                id=hashlib.md5(option.encode()).hexdigest()[:8],
                source="nixos-options",
                category="configuration",
                title=f"NixOS Option: {option}",
                content=f"The {option} option configures system settings in NixOS.",
                keywords=option.split("."),
            )

            # Add common patterns
            if "services" in option:
                doc.examples.append(f"{option}.enable = true;")
                doc.content += f"\n\nTo enable this service, add '{option}.enable = true;' to your configuration.nix"

            elif "environment.systemPackages" in option:
                doc.examples.append(
                    "environment.systemPackages = with pkgs; [ firefox vim git ];"
                )
                doc.content += (
                    "\n\nThis option specifies packages to be installed system-wide."
                )

            elif "boot.loader" in option:
                doc.examples.append("boot.loader.systemd-boot.enable = true;")
                doc.content += (
                    "\n\nThis option configures the boot loader for your system."
                )

            return doc

        except Exception:
            return None

    def _extract_package_info(self, progress, task):
        """Extract package information"""

        # Common packages with their descriptions
        packages = [
            ("firefox", "Web browser", ["browser", "internet", "web"]),
            ("vim", "Text editor", ["editor", "terminal", "text"]),
            ("git", "Version control", ["vcs", "development", "source"]),
            ("python3", "Python programming language", ["programming", "scripting"]),
            ("nodejs", "JavaScript runtime", ["javascript", "node", "npm"]),
            ("docker", "Container platform", ["containers", "virtualization"]),
            ("postgresql", "Database server", ["database", "sql", "server"]),
            ("nginx", "Web server", ["webserver", "reverse-proxy", "http"]),
            ("vscode", "Code editor", ["ide", "editor", "development"]),
            ("steam", "Gaming platform", ["games", "gaming", "entertainment"]),
        ]

        for i, (pkg_name, description, keywords) in enumerate(packages):
            doc = DocumentChunk(
                id=hashlib.md5(pkg_name.encode()).hexdigest()[:8],
                source="nixpkgs",
                category="packages",
                title=f"Package: {pkg_name}",
                content=f"{pkg_name} - {description}\n\nInstall with: nix-env -iA nixos.{pkg_name} or add to environment.systemPackages",
                keywords=keywords + [pkg_name],
                examples=[
                    f"nix-env -iA nixos.{pkg_name}",
                    f"environment.systemPackages = with pkgs; [ {pkg_name} ];",
                    f"nix-shell -p {pkg_name}",
                ],
            )

            self.documents.append(doc)
            progress.update(task, completed=(i + 1) * 100 / len(packages))

        progress.update(task, completed=100)

    def _extract_service_configs(self, progress, task):
        """Extract service configuration patterns"""

        services = [
            {
                "name": "openssh",
                "description": "SSH server for remote access",
                "config": """
services.openssh = {
  enable = true;
  settings = {
    PermitRootLogin = "no";
    PasswordAuthentication = false;
  };
};""",
            },
            {
                "name": "nginx",
                "description": "Web server and reverse proxy",
                "config": """
services.nginx = {
  enable = true;
  virtualHosts."example.com" = {
    enableACME = true;
    forceSSL = true;
    root = "/var/www/example";
  };
};""",
            },
            {
                "name": "postgresql",
                "description": "PostgreSQL database server",
                "config": """
services.postgresql = {
  enable = true;
  package = pkgs.postgresql_14;
  enableTCPIP = true;
  authentication = pkgs.lib.mkOverride 10 ''
    local all all trust
    host all all 127.0.0.1/32 trust
  '';
};""",
            },
        ]

        for i, service in enumerate(services):
            doc = DocumentChunk(
                id=hashlib.md5(service["name"].encode()).hexdigest()[:8],
                source="services",
                category="services",
                title=f"Service: {service['name']}",
                content=f"{service['description']}\n\nConfiguration:\n{service['config']}",
                keywords=[service["name"], "service", "systemd"],
                examples=[service["config"]],
            )

            self.documents.append(doc)
            progress.update(task, completed=(i + 1) * 100 / len(services))

        progress.update(task, completed=100)

    def _generate_qa_pairs(self, progress, task):
        """Generate question-answer pairs for training"""

        qa_templates = [
            # Installation questions
            (
                "How do I install {package}?",
                "To install {package}, you can either:\n1. Run: nix-env -iA nixos.{package}\n2. Add to configuration.nix: environment.systemPackages = with pkgs; [ {package} ];\n3. Try temporarily: nix-shell -p {package}",
                "packages",
            ),
            # Service questions
            (
                "How do I enable {service}?",
                "To enable {service}, add to your configuration.nix:\nservices.{service}.enable = true;\n\nThen rebuild with: sudo nixos-rebuild switch",
                "services",
            ),
            # Configuration questions
            (
                "How do I change my hostname?",
                'Set your hostname in configuration.nix:\nnetworking.hostName = "your-hostname";\n\nThen rebuild your system.',
                "configuration",
            ),
            (
                "How do I add a user?",
                'Add a user in configuration.nix:\nusers.users.username = {\n  isNormalUser = true;\n  extraGroups = [ "wheel" ];\n  packages = with pkgs; [ firefox ];\n};',
                "configuration",
            ),
            # Troubleshooting
            (
                "Why is my build failing?",
                "Common causes:\n1. Syntax error in configuration.nix - check with: nixos-rebuild test\n2. Network issues - check internet connection\n3. Conflicting packages - review your package list\n4. Out of disk space - check with: df -h",
                "troubleshooting",
            ),
            # Development environments
            (
                "How do I create a Python development environment?",
                "Create a shell.nix:\n{ pkgs ? import <nixpkgs> {} }:\npkgs.mkShell {\n  buildInputs = with pkgs; [\n    python3\n    python3Packages.pip\n    python3Packages.virtualenv\n  ];\n}\n\nThen run: nix-shell",
                "development",
            ),
        ]

        # Generate variations
        packages = ["firefox", "vim", "git", "python3", "nodejs"]
        services = ["nginx", "openssh", "docker", "postgresql"]

        for i, (q_template, a_template, category) in enumerate(qa_templates):
            if "{package}" in q_template:
                for pkg in packages:
                    self.qa_pairs.append(
                        QAPair(
                            question=q_template.format(package=pkg),
                            answer=a_template.format(package=pkg),
                            context=f"Installing {pkg} on NixOS",
                            category=category,
                        )
                    )
            elif "{service}" in q_template:
                for svc in services:
                    self.qa_pairs.append(
                        QAPair(
                            question=q_template.format(service=svc),
                            answer=a_template.format(service=svc),
                            context=f"Configuring {svc} service",
                            category=category,
                        )
                    )
            else:
                self.qa_pairs.append(
                    QAPair(
                        question=q_template,
                        answer=a_template,
                        context="NixOS configuration",
                        category=category,
                    )
                )

            progress.update(task, completed=(i + 1) * 100 / len(qa_templates))

        progress.update(task, completed=100)

    def _create_examples(self, progress, task):
        """Create practical examples"""

        examples = [
            {
                "title": "Basic Desktop Configuration",
                "description": "A minimal desktop setup with essential packages",
                "config": """
{ config, pkgs, ... }:
{
  # Boot loader
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Networking
  networking.hostName = "nixos-desktop";
  networking.networkmanager.enable = true;

  # Desktop Environment
  services.xserver.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;

  # Sound
  sound.enable = true;
  hardware.pulseaudio.enable = true;

  # User
  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" ];
    packages = with pkgs; [
      firefox
      thunderbird
      libreoffice
    ];
  };

  # System packages
  environment.systemPackages = with pkgs; [
    vim
    git
    wget
    htop
  ];

  system.stateVersion = "24.11";
}""",
            },
            {
                "title": "Web Server Configuration",
                "description": "Nginx web server with SSL",
                "config": """
{ config, pkgs, ... }:
{
  # Nginx web server
  services.nginx = {
    enable = true;
    recommendedGzipSettings = true;
    recommendedOptimisation = true;
    recommendedProxySettings = true;
    recommendedTlsSettings = true;

    virtualHosts."example.com" = {
      enableACME = true;
      forceSSL = true;
      root = "/var/www/example";
      
      locations."/" = {
        index = "index.html";
      };
    };
  };

  # Firewall
  networking.firewall.allowedTCPPorts = [ 80 443 ];
  
  # SSL certificates
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@example.com";
  };
}""",
            },
        ]

        for i, example in enumerate(examples):
            doc = DocumentChunk(
                id=hashlib.md5(example["title"].encode()).hexdigest()[:8],
                source="examples",
                category="configuration",
                title=example["title"],
                content=f"{example['description']}\n\n{example['config']}",
                keywords=["example", "configuration", "template"],
                examples=[example["config"]],
            )

            self.documents.append(doc)
            progress.update(task, completed=(i + 1) * 100 / len(examples))

        progress.update(task, completed=100)

    def _save_corpus(self):
        """Save the corpus to disk"""

        # Save documents
        docs_file = self.output_dir / "documents.jsonl"
        with open(docs_file, "w") as f:
            for doc in self.documents:
                json.dump(doc.to_training_format(), f)
                f.write("\n")

        # Save Q&A pairs
        qa_file = self.output_dir / "qa_pairs.jsonl"
        with open(qa_file, "w") as f:
            for qa in self.qa_pairs:
                json.dump(qa.to_training_format(), f)
                f.write("\n")

        # Save metadata
        metadata = {
            "created": datetime.now().isoformat(),
            "statistics": {
                "documents": len(self.documents),
                "qa_pairs": len(self.qa_pairs),
                "categories": list(set(d.category for d in self.documents)),
            },
        }

        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _display_stats(self):
        """Display corpus statistics"""

        stats_text = f"""
[bold]Corpus Statistics:[/bold]
• Documents: {len(self.documents)}
• Q&A Pairs: {len(self.qa_pairs)}
• Categories: {len(set(d.category for d in self.documents))}
• Total Examples: {sum(len(d.examples) for d in self.documents)}

[bold]Categories:[/bold]
"""

        # Count by category
        category_counts = {}
        for doc in self.documents:
            category_counts[doc.category] = category_counts.get(doc.category, 0) + 1

        for category, count in sorted(category_counts.items()):
            stats_text += f"• {category}: {count} documents\n"

        self.console.print(
            Panel(stats_text, title="[cyan]NixOS Training Corpus[/cyan]")
        )


def main():
    """Build the NixOS training corpus"""
    builder = NixOSCorpusBuilder()
    result = builder.build_corpus()

    print(f"\n✅ Corpus built successfully!")
    print(f"   Output directory: {result['output_dir']}")
    print(f"   Documents: {result['documents']}")
    print(f"   Q&A Pairs: {result['qa_pairs']}")


if __name__ == "__main__":
    main()
