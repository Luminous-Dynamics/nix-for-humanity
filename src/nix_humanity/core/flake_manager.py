#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Flakes & Development Environment Management

This module handles Nix flakes creation, management, and development
environment setup, making modern Nix development accessible.
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import re

@dataclass
class FlakeInput:
    """Represents a flake input dependency"""
    name: str
    url: str
    follows: Optional[str] = None
    type: str = "github"  # github, git, path, tarball
    
@dataclass
class DevShell:
    """Represents a development shell configuration"""
    name: str = "default"
    packages: List[str] = field(default_factory=list)
    build_inputs: List[str] = field(default_factory=list)
    shell_hook: str = ""
    env_vars: Dict[str, str] = field(default_factory=dict)

@dataclass
class FlakeOutput:
    """Represents a flake output"""
    type: str  # package, devShell, nixosModule, etc.
    name: str
    content: str

class FlakeManager:
    """Manage Nix flakes and development environments"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.language_configs = self._load_language_configs()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load flake templates"""
        return {
            "basic": '''{{
  description = "{description}";

  inputs = {{
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
{inputs}  }};

  outputs = {{ self, nixpkgs, flake-utils{input_args} }}:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${{system}};
      in
      {{
{outputs}      }}
    );
}}
''',
            
            "devShell": '''        devShells.{name} = pkgs.mkShell {{
          buildInputs = with pkgs; [
{packages}          ];
          
{shell_hook}        }};
''',
            
            "package": '''        packages.{name} = pkgs.stdenv.mkDerivation {{
          pname = "{pname}";
          version = "{version}";
          src = ./.;
          
          buildInputs = with pkgs; [
{build_inputs}          ];
          
          installPhase = ''
{install_phase}          '';
        }};
''',
            
            "shell_hook": '''          shellHook = ''
{content}          '';
''',
            
            "python_dev": '''        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            python{python_version}
            python{python_version}Packages.pip
            python{python_version}Packages.virtualenv
{packages}          ];
          
          shellHook = ''
            echo "🐍 Python {python_version} development environment"
            echo "Creating virtual environment..."
            virtualenv .venv
            source .venv/bin/activate
            echo "Virtual environment activated!"
{extra_hook}          '';
        }};
''',
            
            "node_dev": '''        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            nodejs_{node_version}
            nodePackages.npm
            nodePackages.yarn
{packages}          ];
          
          shellHook = ''
            echo "📦 Node.js {node_version} development environment"
            echo "npm $(npm --version), yarn $(yarn --version)"
{extra_hook}          '';
        }};
''',
            
            "rust_dev": '''        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            rustc
            cargo
            rustfmt
            rust-analyzer
            clippy
{packages}          ];
          
          shellHook = ''
            echo "🦀 Rust development environment"
            echo "rustc $(rustc --version)"
            echo "cargo $(cargo --version)"
{extra_hook}          '';
        }};
''',
        }
    
    def _load_language_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load language-specific configurations"""
        return {
            "python": {
                "detector_files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
                "default_packages": ["python3", "pip", "virtualenv"],
                "common_packages": ["black", "flake8", "pytest", "mypy"],
                "versions": ["3", "38", "39", "310", "311", "312"]
            },
            "javascript": {
                "detector_files": ["package.json", "yarn.lock", "package-lock.json"],
                "default_packages": ["nodejs", "npm"],
                "common_packages": ["yarn", "typescript", "eslint", "prettier"],
                "versions": ["14", "16", "18", "20"]
            },
            "rust": {
                "detector_files": ["Cargo.toml", "Cargo.lock"],
                "default_packages": ["rustc", "cargo", "rustfmt"],
                "common_packages": ["rust-analyzer", "clippy"],
                "versions": ["stable", "nightly"]
            },
            "go": {
                "detector_files": ["go.mod", "go.sum"],
                "default_packages": ["go"],
                "common_packages": ["gopls", "golangci-lint"],
                "versions": ["1.19", "1.20", "1.21"]
            },
            "java": {
                "detector_files": ["pom.xml", "build.gradle", "build.gradle.kts"],
                "default_packages": ["jdk"],
                "common_packages": ["maven", "gradle"],
                "versions": ["8", "11", "17", "21"]
            },
            "c++": {
                "detector_files": ["CMakeLists.txt", "Makefile", "configure.ac"],
                "default_packages": ["gcc", "gnumake", "cmake"],
                "common_packages": ["clang", "gdb", "valgrind", "clang-tools"],
                "versions": []
            }
        }
    
    def detect_project_type(self, path: Path) -> Optional[str]:
        """Detect project type based on files present"""
        for lang, config in self.language_configs.items():
            for detector_file in config["detector_files"]:
                if (path / detector_file).exists():
                    return lang
        return None
    
    def parse_intent(self, natural_language: str) -> Dict[str, Any]:
        """Parse natural language into flake intent"""
        intent = {
            "action": "create",  # create, update, convert, check
            "type": "devShell",  # devShell, package, nixosModule
            "language": None,
            "packages": [],
            "description": "",
            "features": []
        }
        
        text = natural_language.lower()
        
        # Detect action
        if any(word in text for word in ["update", "modify", "change"]):
            intent["action"] = "update"
        elif any(word in text for word in ["convert", "migrate"]):
            intent["action"] = "convert"
        elif any(word in text for word in ["check", "validate"]):
            intent["action"] = "check"
        
        # Detect language
        for lang in self.language_configs.keys():
            if lang in text:
                intent["language"] = lang
                break
        
        # Common language aliases
        if "node" in text or "npm" in text:
            intent["language"] = "javascript"
        elif "cpp" in text or "c++" in text:
            intent["language"] = "c++"
        
        # Detect specific packages
        package_keywords = {
            "docker": "docker",
            "postgres": "postgresql",
            "mysql": "mysql",
            "redis": "redis",
            "nginx": "nginx",
            "vim": "vim",
            "emacs": "emacs",
            "vscode": "vscode",
            "git": "git",
            "tmux": "tmux",
            "htop": "htop",
            "ripgrep": "ripgrep",
            "fd": "fd",
            "bat": "bat",
            "exa": "exa"
        }
        
        for keyword, package in package_keywords.items():
            if keyword in text:
                intent["packages"].append(package)
        
        # Detect features
        if "test" in text or "testing" in text:
            intent["features"].append("testing")
        if "lint" in text or "linting" in text:
            intent["features"].append("linting")
        if "format" in text or "formatting" in text:
            intent["features"].append("formatting")
        if "debug" in text:
            intent["features"].append("debugging")
        
        # Extract description
        intent["description"] = self._extract_description(natural_language)
        
        return intent
    
    def _extract_description(self, text: str) -> str:
        """Extract a clean description from natural language"""
        # Remove common action words
        desc = text
        for word in ["create", "make", "build", "generate", "flake", "dev", "environment", "shell"]:
            desc = re.sub(r'\b' + word + r'\b', '', desc, flags=re.IGNORECASE)
        
        # Clean up and capitalize
        desc = re.sub(r'\s+', ' ', desc).strip()
        return desc.capitalize() if desc else "Development environment"
    
    def create_flake(self, intent: Dict[str, Any], path: Path = Path(".")) -> Tuple[bool, str]:
        """Create a flake.nix file based on intent"""
        # Check if flake already exists
        flake_path = path / "flake.nix"
        if flake_path.exists() and intent["action"] == "create":
            return False, "flake.nix already exists! Use 'update' to modify it."
        
        # Auto-detect language if not specified
        if not intent["language"] and intent["action"] == "create":
            detected = self.detect_project_type(path)
            if detected:
                intent["language"] = detected
        
        # Build flake content
        inputs = []
        outputs = []
        input_args = ""
        
        # Add language-specific inputs if needed
        if intent["language"] == "rust":
            inputs.append('    rust-overlay.url = "github:oxalica/rust-overlay";')
            input_args += ", rust-overlay"
        
        # Format inputs
        inputs_str = "\n".join(inputs) + "\n" if inputs else ""
        
        # Create dev shell based on language
        if intent["language"]:
            dev_shell = self._create_language_devshell(intent)
            outputs.append(dev_shell)
        else:
            # Generic dev shell
            packages = intent["packages"] or ["git", "vim", "tmux"]
            package_list = "\n".join([f"            {pkg}" for pkg in packages])
            
            shell_hook = ""
            if intent["features"]:
                hooks = []
                if "testing" in intent["features"]:
                    hooks.append('echo "✅ Testing tools available"')
                if "linting" in intent["features"]:
                    hooks.append('echo "🔍 Linting tools ready"')
                if hooks:
                    shell_hook = self.templates["shell_hook"].format(
                        content="\n".join(hooks)
                    )
            
            dev_shell = self.templates["devShell"].format(
                name="default",
                packages=package_list,
                shell_hook=shell_hook
            )
            outputs.append(dev_shell)
        
        # Format outputs
        outputs_str = "\n".join(outputs)
        
        # Generate final flake
        flake_content = self.templates["basic"].format(
            description=intent["description"],
            inputs=inputs_str,
            input_args=input_args,
            outputs=outputs_str
        )
        
        # Write flake
        try:
            with open(flake_path, 'w') as f:
                f.write(flake_content)
            return True, f"Created flake.nix at {flake_path}"
        except Exception as e:
            return False, f"Error creating flake: {str(e)}"
    
    def _create_language_devshell(self, intent: Dict[str, Any]) -> str:
        """Create language-specific development shell"""
        lang = intent["language"]
        lang_config = self.language_configs.get(lang, {})
        
        # Get base packages for the language
        packages = lang_config.get("default_packages", [])
        
        # Add requested packages
        packages.extend(intent["packages"])
        
        # Add feature-specific packages
        if "testing" in intent["features"] and lang == "python":
            packages.append("python3Packages.pytest")
        elif "testing" in intent["features"] and lang == "javascript":
            packages.append("nodePackages.jest")
        
        if "linting" in intent["features"] and lang == "python":
            packages.append("python3Packages.flake8")
        elif "linting" in intent["features"] and lang == "javascript":
            packages.append("nodePackages.eslint")
        
        # Use language-specific template
        if lang == "python":
            package_list = "\n".join([f"            {pkg}" for pkg in packages if pkg not in ["python3", "pip", "virtualenv"]])
            return self.templates["python_dev"].format(
                python_version="3",
                packages=package_list,
                extra_hook='echo "Run pip install -r requirements.txt to install dependencies"' if (Path(".") / "requirements.txt").exists() else ""
            )
        elif lang == "javascript":
            package_list = "\n".join([f"            {pkg}" for pkg in packages if pkg not in ["nodejs", "npm"]])
            return self.templates["node_dev"].format(
                node_version="18",
                packages=package_list,
                extra_hook='echo "Run npm install to install dependencies"' if (Path(".") / "package.json").exists() else ""
            )
        elif lang == "rust":
            package_list = "\n".join([f"            {pkg}" for pkg in packages if pkg not in ["rustc", "cargo", "rustfmt"]])
            return self.templates["rust_dev"].format(
                packages=package_list,
                extra_hook='echo "Run cargo build to compile the project"'
            )
        else:
            # Generic language shell
            package_list = "\n".join([f"            {pkg}" for pkg in packages])
            return self.templates["devShell"].format(
                name="default",
                packages=package_list,
                shell_hook=f'          shellHook = \'\'echo "💻 {lang.capitalize()} development environment ready!"\'\';'
            )
    
    def validate_flake(self, path: Path = Path(".")) -> Tuple[bool, str]:
        """Validate a flake.nix file"""
        flake_path = path / "flake.nix"
        
        if not flake_path.exists():
            return False, "No flake.nix found in current directory"
        
        try:
            # Check syntax with nix
            result = subprocess.run(
                ["nix", "flake", "check", "--no-build"],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, "Flake validation successful!"
            else:
                return False, f"Flake validation failed:\n{result.stderr}"
        except FileNotFoundError:
            return False, "nix command not found. Is Nix installed?"
        except Exception as e:
            return False, f"Error validating flake: {str(e)}"
    
    def show_flake_info(self, path: Path = Path(".")) -> str:
        """Show information about a flake"""
        flake_path = path / "flake.nix"
        
        if not flake_path.exists():
            return "No flake.nix found in current directory"
        
        try:
            # Get flake metadata
            result = subprocess.run(
                ["nix", "flake", "metadata"],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Flake information:\n{result.stdout}"
            else:
                # Fallback to showing file content
                with open(flake_path, 'r') as f:
                    content = f.read()
                
                # Extract key information
                info = ["Flake.nix contents:"]
                
                # Find description
                desc_match = re.search(r'description\s*=\s*"([^"]+)"', content)
                if desc_match:
                    info.append(f"Description: {desc_match.group(1)}")
                
                # Count inputs
                inputs = re.findall(r'(\w+)\.url\s*=', content)
                if inputs:
                    info.append(f"Inputs: {', '.join(set(inputs))}")
                
                # Find dev shells
                shells = re.findall(r'devShells\.(\w+)', content)
                if shells:
                    info.append(f"Dev shells: {', '.join(set(shells))}")
                
                return "\n".join(info)
        except Exception as e:
            return f"Error getting flake info: {str(e)}"
    
    def convert_to_flake(self, path: Path = Path(".")) -> Tuple[bool, str]:
        """Convert a traditional Nix project to flakes"""
        # Check for existing nix files
        shell_nix = path / "shell.nix"
        default_nix = path / "default.nix"
        
        if not shell_nix.exists() and not default_nix.exists():
            return False, "No shell.nix or default.nix found to convert"
        
        # Detect project type
        project_type = self.detect_project_type(path)
        
        # Read existing configuration
        packages = []
        if shell_nix.exists():
            with open(shell_nix, 'r') as f:
                content = f.read()
                # Extract packages (simple regex, not perfect)
                pkg_matches = re.findall(r'buildInputs\s*=\s*(?:with\s+pkgs;\s*)?\[(.*?)\]', content, re.DOTALL)
                if pkg_matches:
                    # Extract individual packages
                    pkg_text = pkg_matches[0]
                    packages = re.findall(r'(\w+)', pkg_text)
        
        # Create flake intent
        intent = {
            "action": "create",
            "language": project_type,
            "packages": packages,
            "description": f"Converted from {'shell.nix' if shell_nix.exists() else 'default.nix'}",
            "features": []
        }
        
        # Create the flake
        success, message = self.create_flake(intent, path)
        
        if success:
            return True, f"Successfully converted to flake!\n{message}\nOriginal files preserved."
        else:
            return False, message


# Example usage functions
def create_dev_environment(description: str, path: str = ".") -> str:
    """Create a development environment from natural language"""
    manager = FlakeManager()
    intent = manager.parse_intent(description)
    
    success, message = manager.create_flake(intent, Path(path))
    return message


if __name__ == "__main__":
    # Test examples
    examples = [
        "Create a Python development environment with testing tools",
        "Make a Node.js dev shell with TypeScript and ESLint",
        "Set up Rust development with debugging tools",
        "Create a flake for Go project with linting"
    ]
    
    for example in examples:
        print(f"\n{'='*60}")
        print(f"Input: {example}")
        print(f"{'='*60}")
        
        manager = FlakeManager()
        intent = manager.parse_intent(example)
        print(f"Parsed intent: {intent}")
        
        # Simulate flake creation
        print(f"\nWould create flake with:")
        print(f"- Language: {intent['language']}")
        print(f"- Packages: {intent['packages']}")
        print(f"- Features: {intent['features']}")
        print(f"- Description: {intent['description']}")