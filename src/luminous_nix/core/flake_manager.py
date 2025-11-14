#!/usr/bin/env python3
"""
Nix Flake Management System

Handles creation, validation, and conversion of Nix flakes from natural language.
Provides seamless development environment management.
"""

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class FlakeTemplate:
    """Template for generating flake.nix files"""

    name: str
    description: str
    inputs: dict[str, str]
    outputs: str
    dev_shell: str
    packages: list[str]
    build_inputs: list[str]


class FlakeManager:
    """Manage Nix flakes for development environments"""

    def __init__(self):
        self.templates = self._load_templates()
        self.language_detectors = self._setup_language_detection()

    def _load_templates(self) -> dict[str, FlakeTemplate]:
        """Load flake templates for different languages and frameworks"""
        return {
            "python": FlakeTemplate(
                name="Python Development",
                description="Python development environment with common tools",
                inputs={
                    "nixpkgs": "github:NixOS/nixpkgs/nixos-unstable",
                    "flake-utils": "github:numtide/flake-utils",
                },
                outputs="""
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${{system}};
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          {python_packages}
        ]);
      in {{
        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            pythonEnv
            {build_inputs}
          ];

          shellHook = ''
            echo "🐍 Python development environment loaded"
            echo "Python: $(python --version)"
            {shell_hook}
          '';
        }};
      }})""",
                dev_shell="",
                packages=["pip", "setuptools", "wheel"],
                build_inputs=["black", "ruff", "mypy"],
            ),
            "rust": FlakeTemplate(
                name="Rust Development",
                description="Rust development environment",
                inputs={
                    "nixpkgs": "github:NixOS/nixpkgs/nixos-unstable",
                    "rust-overlay": "github:oxalica/rust-overlay",
                    "flake-utils": "github:numtide/flake-utils",
                },
                outputs="""
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {{ inherit system overlays; }};
        rustToolchain = pkgs.rust-bin.stable.latest.default.override {{
          extensions = [ "rust-src" "rust-analyzer" ];
        }};
      in {{
        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            rustToolchain
            {build_inputs}
          ];

          shellHook = ''
            echo "🦀 Rust development environment loaded"
            echo "Rust: $(rustc --version)"
            {shell_hook}
          '';
        }};
      }})""",
                dev_shell="",
                packages=[],
                build_inputs=["cargo-watch", "cargo-edit", "cargo-audit"],
            ),
            "nodejs": FlakeTemplate(
                name="Node.js Development",
                description="Node.js/JavaScript development environment",
                inputs={
                    "nixpkgs": "github:NixOS/nixpkgs/nixos-unstable",
                    "flake-utils": "github:numtide/flake-utils",
                },
                outputs="""
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${{system}};
      in {{
        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            nodejs_{node_version}
            {build_inputs}
          ];

          shellHook = ''
            echo "📦 Node.js development environment loaded"
            echo "Node: $(node --version)"
            echo "npm: $(npm --version)"
            {shell_hook}
          '';
        }};
      }})""",
                dev_shell="",
                packages=[],
                build_inputs=["nodePackages.npm", "nodePackages.yarn"],
            ),
            "go": FlakeTemplate(
                name="Go Development",
                description="Go development environment",
                inputs={
                    "nixpkgs": "github:NixOS/nixpkgs/nixos-unstable",
                    "flake-utils": "github:numtide/flake-utils",
                },
                outputs="""
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${{system}};
      in {{
        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            go_{go_version}
            {build_inputs}
          ];

          shellHook = ''
            echo "🐹 Go development environment loaded"
            echo "Go: $(go version)"
            {shell_hook}
          '';
        }};
      }})""",
                dev_shell="",
                packages=[],
                build_inputs=["gopls", "golangci-lint", "delve"],
            ),
        }

    def _setup_language_detection(self) -> dict[str, list[str]]:
        """Setup patterns for detecting programming languages"""
        return {
            "python": [
                "python",
                "py",
                "django",
                "flask",
                "fastapi",
                "pytest",
                "jupyter",
                "pandas",
                "numpy",
            ],
            "rust": ["rust", "cargo", "actix", "rocket", "tokio", "serde"],
            "nodejs": [
                "node",
                "nodejs",
                "javascript",
                "js",
                "typescript",
                "ts",
                "react",
                "vue",
                "angular",
                "express",
            ],
            "go": ["go", "golang", "gin", "fiber", "echo", "gorilla"],
            "cpp": ["c++", "cpp", "cmake", "make", "gcc", "clang"],
            "java": ["java", "spring", "maven", "gradle"],
        }

    def parse_intent(self, description: str) -> dict[str, Any]:
        """Parse natural language description into flake configuration intent"""
        intent = {
            "language": None,
            "packages": [],
            "features": [],
            "tools": [],
            "frameworks": [],
        }

        # Normalize input
        text = description.lower()

        # Detect primary language
        for lang, keywords in self.language_detectors.items():
            if any(keyword in text for keyword in keywords):
                intent["language"] = lang
                break

        # Extract packages (words after "with")
        # Look for patterns like "with X and Y" or "with X, Y, Z"
        with_patterns = [
            r"with\s+([\w\s,and]+?)(?:\s+(?:for|to|in|using)|$)",
            r"using\s+([\w\s,and]+?)(?:\s+(?:for|to|in)|$)",
        ]

        packages = []
        for pattern in with_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Split by commas and "and"
                parts = re.split(r"[,\s]+and\s+|,\s*|\s+and\s+", match)
                for part in parts:
                    # Clean up each part
                    clean_part = part.strip()
                    if clean_part and clean_part.lower() not in ["and", "with"]:
                        packages.append(clean_part)

        if packages:
            intent["packages"] = packages

        # Detect common development features
        features_map = {
            "testing": ["test", "testing", "pytest", "jest", "mocha"],
            "linting": ["lint", "linting", "eslint", "flake8", "clippy"],
            "formatting": ["format", "formatter", "prettier", "black", "rustfmt"],
            "debugging": ["debug", "debugger", "gdb", "lldb", "delve"],
            "database": ["database", "db", "postgres", "mysql", "mongodb", "redis"],
            "docker": ["docker", "container", "containerization"],
            "ci": ["ci", "continuous integration", "github actions", "gitlab"],
        }

        for feature, keywords in features_map.items():
            if any(keyword in text for keyword in keywords):
                intent["features"].append(feature)

        # Detect specific tools
        tools_map = {
            "vscode": ["vscode", "vs code", "visual studio code"],
            "vim": ["vim", "neovim", "nvim"],
            "git": ["git", "version control"],
            "tmux": ["tmux", "terminal multiplexer"],
            "direnv": ["direnv", "environment"],
        }

        for tool, keywords in tools_map.items():
            if any(keyword in text for keyword in keywords):
                intent["tools"].append(tool)

        # Detect frameworks
        frameworks = {
            "python": ["django", "flask", "fastapi", "pyramid"],
            "nodejs": ["express", "next", "nuxt", "nest", "koa"],
            "rust": ["actix", "rocket", "warp", "axum"],
            "go": ["gin", "fiber", "echo", "beego"],
        }

        if intent["language"] in frameworks:
            for framework in frameworks[intent["language"]]:
                if framework in text:
                    intent["frameworks"].append(framework)

        return intent

    def create_flake(
        self, intent: dict[str, Any], project_path: Path
    ) -> tuple[bool, str]:
        """Create a flake.nix file from parsed intent"""
        try:
            # Check if flake already exists
            flake_path = project_path / "flake.nix"
            if flake_path.exists():
                return (
                    False,
                    f"flake.nix already exists at {flake_path}. Use --force to overwrite.",
                )

            # Detect language from project files if not specified
            if not intent.get("language"):
                intent["language"] = self._detect_project_type(project_path)

            # Generate flake content
            flake_content = self._generate_flake(intent)

            # Write flake.nix
            with open(flake_path, "w") as f:
                f.write(flake_content)

            # Initialize git if needed (flakes require git)
            if not (project_path / ".git").exists():
                subprocess.run(["git", "init"], cwd=project_path, capture_output=True)
                subprocess.run(
                    ["git", "add", "flake.nix"], cwd=project_path, capture_output=True
                )

            return True, f"Created flake.nix at {flake_path}"

        except Exception as e:
            return False, f"Error creating flake: {str(e)}"

    def _detect_project_type(self, project_path: Path) -> Optional[str]:
        """Detect project type from existing files"""
        detectors = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "nodejs": ["package.json", "yarn.lock", "package-lock.json"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "go": ["go.mod", "go.sum"],
            "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "cpp": ["CMakeLists.txt", "Makefile", "meson.build"],
        }

        for lang, files in detectors.items():
            if any((project_path / f).exists() for f in files):
                return lang

        return "python"  # Default fallback

    def _generate_flake(self, intent: dict[str, Any]) -> str:
        """Generate flake.nix content from intent"""
        language = intent.get("language", "python")

        # Get base template
        if language not in self.templates:
            language = "python"  # Fallback to Python

        template = self.templates[language]

        # Build package lists based on intent
        packages = []
        build_inputs = []

        # Add language-specific packages
        if language == "python":
            # Python packages
            package_map = {
                "django": "django",
                "flask": "flask",
                "fastapi": "fastapi uvicorn",
                "pytest": "pytest pytest-cov",
                "jupyter": "jupyter notebook ipython",
                "pandas": "pandas",
                "numpy": "numpy",
                "scipy": "scipy",
                "matplotlib": "matplotlib",
                "requests": "requests",
                "beautifulsoup4": "beautifulsoup4",
                "scikit-learn": "scikit-learn",
                "tensorflow": "tensorflow",
                "torch": "pytorch",
            }

            for pkg in intent.get("packages", []):
                if pkg in package_map:
                    packages.extend(package_map[pkg].split())
                else:
                    packages.append(pkg)

            # Add testing tools
            if "testing" in intent.get("features", []):
                packages.extend(["pytest", "pytest-cov", "pytest-mock"])

            # Format Python packages
            python_packages = (
                "\n          ".join(packages)
                if packages
                else "# No additional packages"
            )

        elif language == "nodejs":
            # Node.js version
            node_version = "18"  # Default
            if any(
                v in str(intent.get("packages", [])) for v in ["20", "19", "18", "16"]
            ):
                for v in ["20", "19", "18", "16"]:
                    if v in str(intent.get("packages", [])):
                        node_version = v
                        break

        elif language == "go":
            # Go version
            go_version = "1_21"  # Default
            if any(
                v in str(intent.get("packages", [])) for v in ["1.21", "1.20", "1.19"]
            ):
                go_version = "1_21"  # Simplify version detection

        # Add development tools
        dev_tools = []

        if "git" in intent.get("tools", []) or "git" in intent.get("packages", []):
            dev_tools.append("git")

        if "vscode" in intent.get("tools", []):
            dev_tools.append("vscode")

        if "vim" in intent.get("tools", []):
            dev_tools.append("vim")

        if "docker" in intent.get("features", []):
            dev_tools.append("docker")

        if "database" in intent.get("features", []):
            if "postgres" in str(intent):
                dev_tools.append("postgresql")
            if "mysql" in str(intent):
                dev_tools.append("mysql")
            if "redis" in str(intent):
                dev_tools.append("redis")

        # Build flake content
        flake = f"""{{
  description = "{self._generate_description(intent)}";

  inputs = {{
    {self._format_inputs(template.inputs)}
  }};

  outputs = {{ self, {', '.join(template.inputs.keys())} }}:"""

        # Add outputs based on template
        if language == "python":
            outputs = template.outputs.format(
                python_packages=python_packages
                if packages
                else "# No additional packages",
                build_inputs=" ".join(template.build_inputs + dev_tools),
                shell_hook="",
            )
        elif language == "nodejs":
            outputs = template.outputs.format(
                node_version=node_version,
                build_inputs=" ".join(template.build_inputs + dev_tools),
                shell_hook="",
            )
        elif language == "rust":
            outputs = template.outputs.format(
                build_inputs=" ".join(template.build_inputs + dev_tools), shell_hook=""
            )
        elif language == "go":
            outputs = template.outputs.format(
                go_version=go_version,
                build_inputs=" ".join(template.build_inputs + dev_tools),
                shell_hook="",
            )
        else:
            outputs = template.outputs

        flake += outputs + ";\n}"

        return flake

    def _generate_description(self, intent: dict[str, Any]) -> str:
        """Generate a description for the flake"""
        lang = intent.get("language", "development")

        if intent.get("frameworks"):
            return f"{lang.capitalize()} project with {', '.join(intent['frameworks'])}"
        elif intent.get("packages"):
            return f"{lang.capitalize()} development environment with {', '.join(intent['packages'][:3])}"
        else:
            return f"{lang.capitalize()} development environment"

    def _format_inputs(self, inputs: dict[str, str]) -> str:
        """Format flake inputs"""
        lines = []
        for name, url in inputs.items():
            lines.append(f'{name}.url = "{url}"')
        return ";\n    ".join(lines)

    def validate_flake(self, project_path: Path) -> tuple[bool, str]:
        """Validate a flake.nix file"""
        try:
            flake_path = project_path / "flake.nix"

            if not flake_path.exists():
                return False, f"No flake.nix found at {project_path}"

            # Check syntax with nix
            result = subprocess.run(
                ["nix", "flake", "check", str(project_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return True, "Flake is valid and all checks pass!"
            else:
                return False, f"Flake validation failed:\n{result.stderr}"

        except subprocess.TimeoutExpired:
            return False, "Validation timed out (>30 seconds)"
        except Exception as e:
            return False, f"Error validating flake: {str(e)}"

    def show_flake_info(self, project_path: Path) -> str:
        """Show information about a flake"""
        try:
            flake_path = project_path / "flake.nix"

            if not flake_path.exists():
                return f"❌ No flake.nix found at {project_path}"

            # Read flake content
            with open(flake_path) as f:
                content = f.read()

            info = ["📦 Flake Information\n"]
            info.append(f"📍 Location: {flake_path}")

            # Extract description
            desc_match = re.search(r'description\s*=\s*"([^"]+)"', content)
            if desc_match:
                info.append(f"📝 Description: {desc_match.group(1)}")

            # Extract inputs
            inputs_match = re.findall(r'(\w+)\.url\s*=\s*"([^"]+)"', content)
            if inputs_match:
                info.append("\n📥 Inputs:")
                for name, url in inputs_match:
                    info.append(f"   • {name}: {url}")

            # Check for dev shell
            if "devShells.default" in content or "devShell" in content:
                info.append("\n🔧 Development Shell: ✅ Available")
                info.append("   Run 'nix develop' to enter")

            # Detect language/framework
            if "python" in content.lower():
                info.append("\n🐍 Language: Python")
            elif "rust" in content.lower():
                info.append("\n🦀 Language: Rust")
            elif "node" in content.lower():
                info.append("\n📦 Language: Node.js")
            elif "go" in content.lower():
                info.append("\n🐹 Language: Go")

            # Check for common tools
            tools = []
            tool_patterns = {
                "Docker": ["docker"],
                "PostgreSQL": ["postgresql"],
                "Redis": ["redis"],
                "VSCode": ["vscode"],
            }

            for tool, patterns in tool_patterns.items():
                if any(p in content.lower() for p in patterns):
                    tools.append(tool)

            if tools:
                info.append(f"\n🛠️ Tools: {', '.join(tools)}")

            return "\n".join(info)

        except Exception as e:
            return f"❌ Error reading flake information: {str(e)}"

    def convert_to_flake(self, project_path: Path) -> tuple[bool, str]:
        """Convert shell.nix or default.nix to flake.nix"""
        try:
            # Check for existing nix files
            shell_nix = project_path / "shell.nix"
            default_nix = project_path / "default.nix"

            if not shell_nix.exists() and not default_nix.exists():
                return False, "No shell.nix or default.nix found to convert"

            # Read existing configuration
            source_file = shell_nix if shell_nix.exists() else default_nix
            with open(source_file) as f:
                old_content = f.read()

            # Parse packages from old file
            packages = []
            package_matches = re.findall(
                r"with\s+pkgs;\s*\[(.*?)\]", old_content, re.DOTALL
            )
            if package_matches:
                # Extract package names
                pkg_text = package_matches[0]
                packages = re.findall(r"\b(\w+)\b", pkg_text)

            # Detect language
            language = self._detect_language_from_packages(packages)

            # Create intent from old configuration
            intent = {
                "language": language,
                "packages": packages,
                "features": [],
                "tools": [],
                "frameworks": [],
            }

            # Generate new flake
            flake_content = self._generate_flake(intent)

            # Write flake.nix
            flake_path = project_path / "flake.nix"
            with open(flake_path, "w") as f:
                f.write(flake_content)

            return True, f"Successfully converted {source_file.name} to flake.nix"

        except Exception as e:
            return False, f"Error converting to flake: {str(e)}"

    def _detect_language_from_packages(self, packages: list[str]) -> str:
        """Detect programming language from package list"""
        language_indicators = {
            "python": ["python", "pip", "setuptools", "pytest"],
            "nodejs": ["nodejs", "npm", "yarn", "typescript"],
            "rust": ["cargo", "rustc", "clippy"],
            "go": ["go", "gopls", "golangci-lint"],
        }

        for lang, indicators in language_indicators.items():
            if any(ind in str(packages).lower() for ind in indicators):
                return lang

        return "python"  # Default fallback


# Example usage
if __name__ == "__main__":
    manager = FlakeManager()

    # Test parsing
    examples = [
        "python web app with django and postgresql",
        "rust cli tool with clap and serde",
        "nodejs api with express and typescript",
        "go microservice with gin and docker",
    ]

    for example in examples:
        print(f"\nParsing: {example}")
        intent = manager.parse_intent(example)
        print(f"Result: {json.dumps(intent, indent=2)}")
