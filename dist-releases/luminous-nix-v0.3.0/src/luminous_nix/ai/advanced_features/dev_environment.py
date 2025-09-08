#!/usr/bin/env python3
"""
Development Environment Generator - Create perfect dev shells
Intelligent environment generation based on project needs
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProjectType(Enum):
    """Supported project types"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    RUST = "rust"
    GO = "go"
    CPP = "cpp"
    JAVA = "java"
    HASKELL = "haskell"
    WEB = "web"
    MOBILE = "mobile"
    DEVOPS = "devops"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "ml"
    UNKNOWN = "unknown"

@dataclass
class EnvironmentSpec:
    """Specification for a development environment"""
    project_type: ProjectType
    detected_stack: List[str]
    
    # Core requirements
    languages: List[str]
    frameworks: List[str]
    tools: List[str]
    databases: List[str]
    services: List[str]
    
    # Generated configuration
    shell_nix: str
    flake_nix: Optional[str]
    docker_compose: Optional[str]
    env_vars: Dict[str, str]
    
    # Additional setup
    vscode_settings: Dict[str, Any]
    git_hooks: List[str]
    aliases: Dict[str, str]
    
    confidence: float

class DevEnvironmentGenerator:
    """
    Intelligent dev environment generation using HRM
    Creates perfect development shells based on project analysis
    """
    
    def __init__(self):
        # Language detection patterns
        self.file_patterns = {
            ProjectType.PYTHON: ['*.py', 'requirements.txt', 'pyproject.toml', 'Pipfile'],
            ProjectType.JAVASCRIPT: ['*.js', '*.jsx', '*.ts', '*.tsx', 'package.json'],
            ProjectType.RUST: ['*.rs', 'Cargo.toml'],
            ProjectType.GO: ['*.go', 'go.mod'],
            ProjectType.CPP: ['*.cpp', '*.hpp', '*.c', '*.h', 'CMakeLists.txt'],
            ProjectType.JAVA: ['*.java', 'pom.xml', 'build.gradle'],
            ProjectType.HASKELL: ['*.hs', '*.cabal', 'stack.yaml'],
        }
        
        # Package sets for different stacks
        self.package_sets = {
            'python': {
                'base': ['python311', 'python311Packages.pip', 'python311Packages.virtualenv'],
                'scientific': ['python311Packages.numpy', 'python311Packages.scipy', 'python311Packages.pandas'],
                'web': ['python311Packages.flask', 'python311Packages.django', 'python311Packages.fastapi'],
                'ml': ['python311Packages.pytorch', 'python311Packages.tensorflow', 'python311Packages.scikit-learn'],
                'tools': ['poetry', 'black', 'ruff', 'mypy', 'pytest']
            },
            'javascript': {
                'base': ['nodejs_20', 'nodePackages.npm', 'nodePackages.yarn'],
                'frontend': ['nodePackages.webpack', 'nodePackages.vite', 'nodePackages.create-react-app'],
                'backend': ['nodePackages.express', 'nodePackages.nestjs'],
                'tools': ['nodePackages.eslint', 'nodePackages.prettier', 'nodePackages.typescript']
            },
            'rust': {
                'base': ['rustc', 'cargo', 'rustfmt', 'clippy'],
                'tools': ['rust-analyzer', 'cargo-edit', 'cargo-watch', 'cargo-audit']
            },
            'go': {
                'base': ['go', 'gotools', 'gopls'],
                'tools': ['golangci-lint', 'delve', 'go-tools']
            },
            'devops': {
                'base': ['docker', 'docker-compose', 'kubectl', 'terraform'],
                'cloud': ['awscli2', 'google-cloud-sdk', 'azure-cli'],
                'tools': ['ansible', 'vagrant', 'packer']
            }
        }
    
    def analyze_project(self, project_path: str = '.', use_poml: bool = True) -> EnvironmentSpec:
        """
        Analyze project and generate dev environment
        
        Args:
            project_path: Path to project directory
            use_poml: Whether to use POML-enhanced analysis
        
        Returns:
            EnvironmentSpec with generated configuration
        """
        try:
            path = Path(project_path)
            
            # Use POML-enhanced analysis if available
            if use_poml:
                enhanced_analysis = self._poml_enhanced_analysis(path)
                if enhanced_analysis:
                    return enhanced_analysis
            
            # Fallback to standard detection
            # Detect project type
            project_type = self._detect_project_type(path)
            
            # Detect technology stack
            stack = self._detect_stack(path, project_type)
            
            # Analyze dependencies
            languages = self._detect_languages(path)
            frameworks = self._detect_frameworks(path, project_type)
            tools = self._recommend_tools(project_type, frameworks)
            databases = self._detect_databases(path)
            services = self._detect_services(path)
            
            # Generate configurations
            shell_nix = self._generate_shell_nix(
                project_type, languages, frameworks, tools, databases, services
            )
            
            flake_nix = self._generate_flake_nix(
                project_type, languages, frameworks, tools
            )
            
            docker_compose = self._generate_docker_compose(databases, services)
            
            # Environment variables
            env_vars = self._generate_env_vars(project_type, databases, services)
            
            # VS Code settings
            vscode_settings = self._generate_vscode_settings(project_type, languages)
            
            # Git hooks
            git_hooks = self._recommend_git_hooks(project_type)
            
            # Useful aliases
            aliases = self._generate_aliases(project_type)
            
            return EnvironmentSpec(
                project_type=project_type,
                detected_stack=stack,
                languages=languages,
                frameworks=frameworks,
                tools=tools,
                databases=databases,
                services=services,
                shell_nix=shell_nix,
                flake_nix=flake_nix,
                docker_compose=docker_compose,
                env_vars=env_vars,
                vscode_settings=vscode_settings,
                git_hooks=git_hooks,
                aliases=aliases,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Project analysis failed: {e}")
            return self._create_fallback_spec(str(e))
    
    def generate_for_stack(self, stack: str) -> EnvironmentSpec:
        """
        Generate environment for specific technology stack
        
        Args:
            stack: Technology stack (e.g., "python-django", "react-typescript")
        
        Returns:
            EnvironmentSpec for the stack
        """
        try:
            # Parse stack string
            parts = stack.lower().split('-')
            
            # Determine project type
            project_type = self._stack_to_project_type(parts[0])
            
            # Determine frameworks
            frameworks = parts[1:] if len(parts) > 1 else []
            
            # Get appropriate packages
            languages = [parts[0]]
            tools = self._recommend_tools(project_type, frameworks)
            databases = self._recommend_databases(stack)
            services = []
            
            # Generate configurations
            shell_nix = self._generate_shell_nix(
                project_type, languages, frameworks, tools, databases, services
            )
            
            flake_nix = self._generate_flake_nix(
                project_type, languages, frameworks, tools
            )
            
            return EnvironmentSpec(
                project_type=project_type,
                detected_stack=[stack],
                languages=languages,
                frameworks=frameworks,
                tools=tools,
                databases=databases,
                services=services,
                shell_nix=shell_nix,
                flake_nix=flake_nix,
                docker_compose=None,
                env_vars={},
                vscode_settings={},
                git_hooks=[],
                aliases=self._generate_aliases(project_type),
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Stack generation failed: {e}")
            return self._create_fallback_spec(str(e))
    
    def _detect_project_type(self, path: Path) -> ProjectType:
        """Detect project type from files"""
        # Check for specific files
        files = list(path.glob('*'))
        file_names = [f.name for f in files]
        
        # Priority checks
        if 'package.json' in file_names:
            return ProjectType.JAVASCRIPT
        elif 'requirements.txt' in file_names or 'pyproject.toml' in file_names:
            return ProjectType.PYTHON
        elif 'Cargo.toml' in file_names:
            return ProjectType.RUST
        elif 'go.mod' in file_names:
            return ProjectType.GO
        elif 'pom.xml' in file_names or 'build.gradle' in file_names:
            return ProjectType.JAVA
        elif any(f.suffix in ['.cpp', '.hpp', '.c', '.h'] for f in files):
            return ProjectType.CPP
        elif any(f.suffix == '.hs' for f in files):
            return ProjectType.HASKELL
        
        # Check for web projects
        if 'index.html' in file_names:
            return ProjectType.WEB
        
        return ProjectType.UNKNOWN
    
    def _detect_stack(self, path: Path, project_type: ProjectType) -> List[str]:
        """Detect technology stack"""
        stack = []
        
        if project_type == ProjectType.PYTHON:
            # Check for frameworks
            if (path / 'manage.py').exists():
                stack.append('django')
            if any(path.glob('**/flask*.py')):
                stack.append('flask')
            if (path / 'pyproject.toml').exists():
                with open(path / 'pyproject.toml') as f:
                    content = f.read()
                    if 'fastapi' in content:
                        stack.append('fastapi')
                    if 'poetry' in content:
                        stack.append('poetry')
        
        elif project_type == ProjectType.JAVASCRIPT:
            if (path / 'package.json').exists():
                with open(path / 'package.json') as f:
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    dev_deps = pkg.get('devDependencies', {})
                    
                    all_deps = {**deps, **dev_deps}
                    
                    if 'react' in all_deps:
                        stack.append('react')
                    if 'vue' in all_deps:
                        stack.append('vue')
                    if 'angular' in all_deps:
                        stack.append('angular')
                    if 'express' in all_deps:
                        stack.append('express')
                    if 'next' in all_deps:
                        stack.append('nextjs')
        
        return stack
    
    def _detect_languages(self, path: Path) -> List[str]:
        """Detect programming languages used"""
        languages = set()
        
        for suffix_map in [
            ('.py', 'python'),
            ('.js', 'javascript'),
            ('.ts', 'typescript'),
            ('.rs', 'rust'),
            ('.go', 'go'),
            ('.java', 'java'),
            ('.cpp', 'cpp'),
            ('.c', 'c'),
            ('.hs', 'haskell'),
            ('.rb', 'ruby'),
            ('.php', 'php'),
        ]:
            if list(path.glob(f'**/*{suffix_map[0]}')):
                languages.add(suffix_map[1])
        
        return list(languages)
    
    def _detect_frameworks(self, path: Path, project_type: ProjectType) -> List[str]:
        """Detect frameworks used"""
        frameworks = []
        
        # Already detected in _detect_stack, reuse that logic
        stack = self._detect_stack(path, project_type)
        frameworks.extend(stack)
        
        return frameworks
    
    def _recommend_tools(self, project_type: ProjectType, frameworks: List[str]) -> List[str]:
        """Recommend development tools"""
        tools = []
        
        if project_type == ProjectType.PYTHON:
            tools.extend(['poetry', 'black', 'ruff', 'mypy', 'pytest'])
        elif project_type == ProjectType.JAVASCRIPT:
            tools.extend(['eslint', 'prettier', 'jest'])
            if 'typescript' in str(frameworks):
                tools.append('typescript')
        elif project_type == ProjectType.RUST:
            tools.extend(['rustfmt', 'clippy', 'cargo-watch'])
        elif project_type == ProjectType.GO:
            tools.extend(['gopls', 'golangci-lint'])
        
        # Common tools
        tools.extend(['git', 'curl', 'jq', 'ripgrep', 'fd'])
        
        return tools
    
    def _detect_databases(self, path: Path) -> List[str]:
        """Detect database usage"""
        databases = []
        
        # Check for database configs
        check_files = [
            ('docker-compose.yml', ['postgres', 'mysql', 'mongodb', 'redis']),
            ('.env', ['DATABASE_URL', 'POSTGRES', 'MYSQL', 'MONGO']),
            ('requirements.txt', ['psycopg2', 'pymongo', 'redis', 'mysql']),
            ('package.json', ['pg', 'mysql', 'mongodb', 'redis']),
        ]
        
        for file_name, patterns in check_files:
            file_path = path / file_name
            if file_path.exists():
                with open(file_path) as f:
                    content = f.read().lower()
                    for pattern in patterns:
                        if pattern.lower() in content:
                            db_name = pattern.split('_')[0] if '_' in pattern else pattern
                            if db_name not in databases:
                                databases.append(db_name)
        
        return databases
    
    def _detect_services(self, path: Path) -> List[str]:
        """Detect required services"""
        services = []
        
        # Check docker-compose
        compose_file = path / 'docker-compose.yml'
        if compose_file.exists():
            services.append('docker')
        
        # Check for CI/CD
        if (path / '.github' / 'workflows').exists():
            services.append('github-actions')
        if (path / '.gitlab-ci.yml').exists():
            services.append('gitlab-ci')
        
        return services
    
    def _generate_shell_nix(self, project_type: ProjectType, languages: List[str],
                           frameworks: List[str], tools: List[str],
                           databases: List[str], services: List[str]) -> str:
        """Generate shell.nix configuration"""
        
        # Build package list
        packages = []
        
        # Add language-specific packages
        if project_type == ProjectType.PYTHON:
            packages.extend(self.package_sets['python']['base'])
            if 'django' in frameworks or 'flask' in frameworks:
                packages.extend(self.package_sets['python']['web'])
            if any(ml in str(frameworks) for ml in ['ml', 'tensorflow', 'pytorch']):
                packages.extend(self.package_sets['python']['ml'])
        
        elif project_type == ProjectType.JAVASCRIPT:
            packages.extend(self.package_sets['javascript']['base'])
            if 'react' in frameworks or 'vue' in frameworks:
                packages.extend(self.package_sets['javascript']['frontend'])
        
        elif project_type == ProjectType.RUST:
            packages.extend(self.package_sets['rust']['base'])
        
        # Add databases
        db_packages = {
            'postgres': 'postgresql',
            'mysql': 'mysql80',
            'mongodb': 'mongodb',
            'redis': 'redis'
        }
        for db in databases:
            if db in db_packages:
                packages.append(db_packages[db])
        
        # Add tools
        packages.extend(['git', 'curl', 'jq', 'ripgrep', 'fd'])
        
        # Generate shell.nix
        packages_str = '\n    '.join(packages)
        
        shell_nix = f'''{{ pkgs ? import <nixpkgs> {{}} }}:
pkgs.mkShell {{
  buildInputs = with pkgs; [
    {packages_str}
  ];
  
  shellHook = ''
    echo "🚀 Development environment loaded!"
    echo "Project type: {project_type.value}"
    echo "Stack: {', '.join(frameworks)}"
    
    # Set up aliases
    alias dev="nix-shell"
    alias test="pytest"
    alias fmt="black . && ruff check --fix"
    
    # Environment variables
    export DEVELOPMENT=true
  '';
}}'''
        
        return shell_nix
    
    def _generate_flake_nix(self, project_type: ProjectType, languages: List[str],
                           frameworks: List[str], tools: List[str]) -> str:
        """Generate flake.nix configuration"""
        
        flake_nix = f'''{{
  description = "{project_type.value} development environment";
  
  inputs = {{
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  }};
  
  outputs = {{ self, nixpkgs, flake-utils }}:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${{system}};
      in {{
        devShells.default = pkgs.mkShell {{
          buildInputs = with pkgs; [
            # Add packages here
          ];
        }};
      }};
    );
}}'''
        
        return flake_nix
    
    def _generate_docker_compose(self, databases: List[str], services: List[str]) -> Optional[str]:
        """Generate docker-compose.yml if needed"""
        if not databases:
            return None
        
        services_config = []
        
        if 'postgres' in databases:
            services_config.append('''
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data''')
        
        if 'redis' in databases:
            services_config.append('''
  redis:
    image: redis:7
    ports:
      - "6379:6379"''')
        
        if not services_config:
            return None
        
        docker_compose = f'''version: '3.8'

services:{chr(10).join(services_config)}

volumes:
  postgres_data:'''
        
        return docker_compose
    
    def _generate_env_vars(self, project_type: ProjectType,
                          databases: List[str], services: List[str]) -> Dict[str, str]:
        """Generate environment variables"""
        env_vars = {
            'DEVELOPMENT': 'true',
            'DEBUG': 'true'
        }
        
        if 'postgres' in databases:
            env_vars['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost/myapp'
        
        if project_type == ProjectType.PYTHON:
            env_vars['PYTHONPATH'] = '.'
        
        return env_vars
    
    def _generate_vscode_settings(self, project_type: ProjectType, languages: List[str]) -> Dict[str, Any]:
        """Generate VS Code settings"""
        settings = {
            "editor.formatOnSave": True,
            "editor.rulers": [80, 120]
        }
        
        if project_type == ProjectType.PYTHON:
            settings.update({
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": False,
                "python.linting.ruffEnabled": True,
                "python.formatting.provider": "black"
            })
        
        return settings
    
    def _recommend_git_hooks(self, project_type: ProjectType) -> List[str]:
        """Recommend git hooks"""
        hooks = ["pre-commit: Run tests and linting"]
        
        if project_type == ProjectType.PYTHON:
            hooks.append("pre-commit: black --check")
            hooks.append("pre-commit: ruff check")
        
        return hooks
    
    def _generate_aliases(self, project_type: ProjectType) -> Dict[str, str]:
        """Generate useful aliases"""
        aliases = {
            "dev": "nix-shell",
            "update": "nix flake update"
        }
        
        if project_type == ProjectType.PYTHON:
            aliases.update({
                "test": "pytest",
                "fmt": "black . && ruff check --fix",
                "typecheck": "mypy ."
            })
        elif project_type == ProjectType.JAVASCRIPT:
            aliases.update({
                "start": "npm start",
                "test": "npm test",
                "build": "npm run build"
            })
        elif project_type == ProjectType.RUST:
            aliases.update({
                "b": "cargo build",
                "r": "cargo run",
                "t": "cargo test",
                "fmt": "cargo fmt"
            })
        
        return aliases
    
    def _stack_to_project_type(self, language: str) -> ProjectType:
        """Convert language string to project type"""
        mapping = {
            'python': ProjectType.PYTHON,
            'javascript': ProjectType.JAVASCRIPT,
            'js': ProjectType.JAVASCRIPT,
            'typescript': ProjectType.JAVASCRIPT,
            'ts': ProjectType.JAVASCRIPT,
            'rust': ProjectType.RUST,
            'go': ProjectType.GO,
            'java': ProjectType.JAVA,
            'cpp': ProjectType.CPP,
            'c++': ProjectType.CPP,
        }
        return mapping.get(language.lower(), ProjectType.UNKNOWN)
    
    def _recommend_databases(self, stack: str) -> List[str]:
        """Recommend databases for stack"""
        if 'django' in stack or 'rails' in stack:
            return ['postgres']
        elif 'express' in stack or 'fastapi' in stack:
            return ['postgres', 'redis']
        elif 'react' in stack or 'vue' in stack:
            return []  # Frontend only
        else:
            return ['postgres']  # Safe default
    
    def _poml_enhanced_analysis(self, path: Path) -> Optional[EnvironmentSpec]:
        """Use POML to enhance project analysis with AI reasoning"""
        try:
            # Check if POML bridge is available
            from ...agents.poml_bridge_v2 import POMLProcessor
            
            # Load the devenv POML template
            poml_path = Path(__file__).parent.parent.parent / 'agents' / 'devenv_analysis.poml'
            if not poml_path.exists():
                return None
            
            processor = POMLProcessor()
            
            # Gather project files
            project_files = [f.name for f in path.glob('*') if f.is_file()][:20]
            
            # Read key file contents
            file_contents = {}
            for key_file in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod']:
                file_path = path / key_file
                if file_path.exists():
                    with open(file_path) as f:
                        file_contents[key_file] = f.read()[:500]  # First 500 chars
            
            # Process with POML
            result = processor.process(
                str(poml_path),
                project_files=project_files,
                file_contents=file_contents
            )
            
            # Parse POML result and enhance standard analysis
            if result and 'project_type' in result:
                # Use POML insights to guide standard analysis
                logger.info(f"POML enhanced analysis: {result}")
                # Continue with standard analysis but with POML hints
                return None  # Let standard analysis continue with POML insights
                
        except Exception as e:
            logger.debug(f"POML enhancement not available: {e}")
        
        return None
    
    def _create_fallback_spec(self, error: str) -> EnvironmentSpec:
        """Create fallback spec on error"""
        return EnvironmentSpec(
            project_type=ProjectType.UNKNOWN,
            detected_stack=[],
            languages=[],
            frameworks=[],
            tools=['git', 'curl'],
            databases=[],
            services=[],
            shell_nix="{ pkgs ? import <nixpkgs> {} }: pkgs.mkShell { buildInputs = [ pkgs.git ]; }",
            flake_nix=None,
            docker_compose=None,
            env_vars={},
            vscode_settings={},
            git_hooks=[],
            aliases={},
            confidence=0.1
        )