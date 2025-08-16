"""
Multi-Language Code Understanding with Tree-sitter
Automatically generates Nix configurations based on project analysis
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProjectDependency:
    """Represents a project dependency"""
    name: str
    version: Optional[str] = None
    type: str = "runtime"  # runtime, dev, test
    source: str = ""  # Where we found it
    confidence: float = 1.0  # How confident we are


@dataclass
class ProjectAnalysis:
    """Complete project analysis results"""
    language: str
    framework: Optional[str] = None
    dependencies: List[ProjectDependency] = field(default_factory=list)
    dev_dependencies: List[ProjectDependency] = field(default_factory=list)
    build_system: Optional[str] = None
    entry_point: Optional[str] = None
    requires_database: bool = False
    requires_redis: bool = False
    environment_variables: Set[str] = field(default_factory=set)
    ports: Set[int] = field(default_factory=set)
    suggested_nix_packages: List[str] = field(default_factory=list)
    nix_shell_config: Optional[str] = None
    confidence_score: float = 0.0


class LanguageDetector:
    """Detect project language and framework"""
    
    LANGUAGE_FILES = {
        "python": ["*.py", "pyproject.toml", "requirements.txt", "setup.py"],
        "nodejs": ["*.js", "*.ts", "package.json", "yarn.lock"],
        "rust": ["*.rs", "Cargo.toml", "Cargo.lock"],
        "go": ["*.go", "go.mod", "go.sum"],
        "ruby": ["*.rb", "Gemfile", "Gemfile.lock"],
        "java": ["*.java", "pom.xml", "build.gradle"],
        "haskell": ["*.hs", "*.cabal", "stack.yaml"],
        "elixir": ["*.ex", "*.exs", "mix.exs"],
        "php": ["*.php", "composer.json", "composer.lock"],
        "csharp": ["*.cs", "*.csproj", "*.sln"],
    }
    
    FRAMEWORK_INDICATORS = {
        "python": {
            "django": ["manage.py", "settings.py", "urls.py"],
            "flask": ["app.py", "application.py", "__init__.py"],
            "fastapi": ["main.py", "routers/"],
            "poetry": ["pyproject.toml", "poetry.lock"],
        },
        "nodejs": {
            "express": ["app.js", "server.js", "routes/"],
            "react": ["App.js", "App.jsx", "index.js"],
            "vue": ["App.vue", "main.js"],
            "next": ["next.config.js", "pages/"],
        },
        "rust": {
            "actix": ["actix-web"],
            "rocket": ["rocket"],
            "tauri": ["tauri.conf.json"],
        }
    }
    
    def detect_language(self, project_path: Path) -> Optional[str]:
        """Detect the primary language of the project"""
        file_counts = {}
        
        for language, patterns in self.LANGUAGE_FILES.items():
            count = 0
            for pattern in patterns:
                if pattern.startswith("*."):
                    # Count files with this extension
                    count += len(list(project_path.rglob(pattern)))
                else:
                    # Check if specific file exists
                    if (project_path / pattern).exists():
                        count += 10  # Weight config files higher
            
            if count > 0:
                file_counts[language] = count
        
        if not file_counts:
            return None
        
        # Return language with most indicators
        return max(file_counts, key=file_counts.get)
    
    def detect_framework(self, project_path: Path, language: str) -> Optional[str]:
        """Detect the framework being used"""
        if language not in self.FRAMEWORK_INDICATORS:
            return None
        
        for framework, indicators in self.FRAMEWORK_INDICATORS[language].items():
            for indicator in indicators:
                if (project_path / indicator).exists():
                    return framework
                # Check if it's in dependencies
                if language == "python" and (project_path / "pyproject.toml").exists():
                    content = (project_path / "pyproject.toml").read_text()
                    if framework.lower() in content.lower():
                        return framework
                elif language == "nodejs" and (project_path / "package.json").exists():
                    content = (project_path / "package.json").read_text()
                    if framework.lower() in content.lower():
                        return framework
        
        return None


class PythonAnalyzer:
    """Analyze Python projects"""
    
    def analyze(self, project_path: Path) -> ProjectAnalysis:
        """Analyze a Python project"""
        analysis = ProjectAnalysis(language="python")
        
        # Check for pyproject.toml (Poetry/modern Python)
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            analysis = self._analyze_pyproject(pyproject_path, analysis)
            analysis.build_system = "poetry"
        
        # Check for requirements.txt
        requirements_path = project_path / "requirements.txt"
        if requirements_path.exists():
            analysis = self._analyze_requirements(requirements_path, analysis)
            if not analysis.build_system:
                analysis.build_system = "pip"
        
        # Check for setup.py
        setup_path = project_path / "setup.py"
        if setup_path.exists():
            analysis = self._analyze_setup_py(setup_path, analysis)
            if not analysis.build_system:
                analysis.build_system = "setuptools"
        
        # Detect framework
        detector = LanguageDetector()
        analysis.framework = detector.detect_framework(project_path, "python")
        
        # Find entry point
        analysis.entry_point = self._find_entry_point(project_path)
        
        # Check for database usage
        analysis = self._check_database_usage(project_path, analysis)
        
        # Find environment variables
        analysis = self._find_env_vars(project_path, analysis)
        
        # Generate Nix packages
        analysis.suggested_nix_packages = self._suggest_nix_packages(analysis)
        
        # Generate shell.nix
        analysis.nix_shell_config = self._generate_shell_nix(analysis)
        
        # Calculate confidence
        analysis.confidence_score = self._calculate_confidence(analysis)
        
        return analysis
    
    def _analyze_pyproject(self, path: Path, analysis: ProjectAnalysis) -> ProjectAnalysis:
        """Analyze pyproject.toml"""
        try:
            import tomli
            content = path.read_text()
            data = tomli.loads(content)
            
            # Get dependencies
            if "tool" in data and "poetry" in data["tool"]:
                poetry = data["tool"]["poetry"]
                if "dependencies" in poetry:
                    for dep, version in poetry["dependencies"].items():
                        if dep != "python":
                            analysis.dependencies.append(
                                ProjectDependency(name=dep, version=str(version), source="pyproject.toml")
                            )
                
                if "dev-dependencies" in poetry:
                    for dep, version in poetry["dev-dependencies"].items():
                        analysis.dev_dependencies.append(
                            ProjectDependency(name=dep, version=str(version), type="dev", source="pyproject.toml")
                        )
            
            # Get project metadata
            if "project" in data:
                project = data["project"]
                if "dependencies" in project:
                    for dep in project["dependencies"]:
                        # Parse PEP 508 dependency strings
                        dep_name = re.split(r'[<>=!]', dep)[0].strip()
                        analysis.dependencies.append(
                            ProjectDependency(name=dep_name, source="pyproject.toml")
                        )
        except Exception as e:
            logger.warning(f"Error parsing pyproject.toml: {e}")
        
        return analysis
    
    def _analyze_requirements(self, path: Path, analysis: ProjectAnalysis) -> ProjectAnalysis:
        """Analyze requirements.txt"""
        content = path.read_text()
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # Parse requirement
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    dep_name = match.group(1)
                    analysis.dependencies.append(
                        ProjectDependency(name=dep_name, source="requirements.txt")
                    )
        
        return analysis
    
    def _analyze_setup_py(self, path: Path, analysis: ProjectAnalysis) -> ProjectAnalysis:
        """Analyze setup.py"""
        content = path.read_text()
        
        # Find install_requires
        install_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if install_match:
            requires_text = install_match.group(1)
            for req in re.findall(r'["\']([^"\']+)["\']', requires_text):
                dep_name = re.split(r'[<>=!]', req)[0].strip()
                analysis.dependencies.append(
                    ProjectDependency(name=dep_name, source="setup.py")
                )
        
        return analysis
    
    def _find_entry_point(self, project_path: Path) -> Optional[str]:
        """Find the main entry point"""
        common_entry_points = ["main.py", "app.py", "run.py", "manage.py", "__main__.py"]
        
        for entry in common_entry_points:
            if (project_path / entry).exists():
                return entry
        
        # Check for package with __main__
        for item in project_path.iterdir():
            if item.is_dir() and (item / "__main__.py").exists():
                return f"{item.name}/__main__.py"
        
        return None
    
    def _check_database_usage(self, project_path: Path, analysis: ProjectAnalysis) -> ProjectAnalysis:
        """Check if project uses databases"""
        db_indicators = {
            "postgresql": ["psycopg2", "asyncpg", "postgresql"],
            "mysql": ["mysqlclient", "pymysql", "mysql-connector"],
            "sqlite": ["sqlite3"],
            "mongodb": ["pymongo", "motor"],
            "redis": ["redis", "aioredis"],
        }
        
        all_deps = [d.name for d in analysis.dependencies]
        
        for db_type, indicators in db_indicators.items():
            for indicator in indicators:
                if indicator in all_deps:
                    if db_type == "redis":
                        analysis.requires_redis = True
                    else:
                        analysis.requires_database = True
                    break
        
        return analysis
    
    def _find_env_vars(self, project_path: Path, analysis: ProjectAnalysis) -> ProjectAnalysis:
        """Find environment variables used"""
        env_patterns = [
            r'os\.environ\.get\(["\'](\w+)["\']',
            r'os\.environ\[["\'](\w+)["\']',
            r'getenv\(["\'](\w+)["\']',
        ]
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern in env_patterns:
                    matches = re.findall(pattern, content)
                    analysis.environment_variables.update(matches)
            except Exception:
                pass
        
        # Check for .env.example
        env_example = project_path / ".env.example"
        if env_example.exists():
            content = env_example.read_text()
            for line in content.splitlines():
                if "=" in line and not line.startswith("#"):
                    var_name = line.split("=")[0].strip()
                    analysis.environment_variables.add(var_name)
        
        return analysis
    
    def _suggest_nix_packages(self, analysis: ProjectAnalysis) -> List[str]:
        """Suggest Nix packages based on dependencies"""
        packages = ["python311", "poetry"]
        
        # Map Python packages to Nix packages
        package_map = {
            "django": "python311Packages.django_4",
            "flask": "python311Packages.flask",
            "fastapi": "python311Packages.fastapi",
            "numpy": "python311Packages.numpy",
            "pandas": "python311Packages.pandas",
            "pytest": "python311Packages.pytest",
            "black": "python311Packages.black",
            "mypy": "python311Packages.mypy",
            "psycopg2": "python311Packages.psycopg2",
            "redis": "python311Packages.redis",
        }
        
        for dep in analysis.dependencies:
            if dep.name.lower() in package_map:
                packages.append(package_map[dep.name.lower()])
        
        if analysis.requires_database:
            packages.append("postgresql")
        
        if analysis.requires_redis:
            packages.append("redis")
        
        return packages
    
    def _generate_shell_nix(self, analysis: ProjectAnalysis) -> str:
        """Generate a shell.nix configuration"""
        packages = " ".join(analysis.suggested_nix_packages)
        
        template = f"""{{ pkgs ? import <nixpkgs> {{}} }}:

pkgs.mkShell {{
  buildInputs = with pkgs; [
    {packages}
  ];

  shellHook = ''
    echo "🐍 Python Development Environment"
    echo "Language: {analysis.language}"
    echo "Framework: {analysis.framework or 'None detected'}"
    echo "Build System: {analysis.build_system or 'Unknown'}"
    
    # Set up Python environment
    export PYTHONPATH="$PWD:$PYTHONPATH"
    
    # Activate Poetry if available
    if command -v poetry &> /dev/null; then
      echo "Activating Poetry environment..."
      poetry install
    fi
  '';
}}"""
        
        return template
    
    def _calculate_confidence(self, analysis: ProjectAnalysis) -> float:
        """Calculate confidence score"""
        score = 0.0
        
        # Has build system
        if analysis.build_system:
            score += 0.2
        
        # Has dependencies
        if analysis.dependencies:
            score += 0.2
        
        # Has entry point
        if analysis.entry_point:
            score += 0.2
        
        # Has framework
        if analysis.framework:
            score += 0.2
        
        # Has suggested packages
        if analysis.suggested_nix_packages:
            score += 0.2
        
        return min(score, 1.0)


class NodeJSAnalyzer:
    """Analyze Node.js projects"""
    
    def analyze(self, project_path: Path) -> ProjectAnalysis:
        """Analyze a Node.js project"""
        analysis = ProjectAnalysis(language="nodejs")
        
        # Check for package.json
        package_json = project_path / "package.json"
        if package_json.exists():
            analysis = self._analyze_package_json(package_json, analysis)
        
        # Detect framework
        detector = LanguageDetector()
        analysis.framework = detector.detect_framework(project_path, "nodejs")
        
        # Find entry point
        analysis.entry_point = self._find_entry_point(project_path, analysis)
        
        # Check for database usage
        analysis = self._check_database_usage(analysis)
        
        # Generate Nix packages
        analysis.suggested_nix_packages = self._suggest_nix_packages(analysis)
        
        # Generate shell.nix
        analysis.nix_shell_config = self._generate_shell_nix(analysis)
        
        # Calculate confidence
        analysis.confidence_score = self._calculate_confidence(analysis)
        
        return analysis
    
    def _analyze_package_json(self, path: Path, analysis: ProjectAnalysis) -> ProjectAnalysis:
        """Analyze package.json"""
        try:
            data = json.loads(path.read_text())
            
            # Get dependencies
            if "dependencies" in data:
                for dep, version in data["dependencies"].items():
                    analysis.dependencies.append(
                        ProjectDependency(name=dep, version=version, source="package.json")
                    )
            
            if "devDependencies" in data:
                for dep, version in data["devDependencies"].items():
                    analysis.dev_dependencies.append(
                        ProjectDependency(name=dep, version=version, type="dev", source="package.json")
                    )
            
            # Get scripts
            if "scripts" in data:
                if "start" in data["scripts"]:
                    # Parse start script for entry point
                    start_script = data["scripts"]["start"]
                    match = re.search(r'node\s+(\S+)', start_script)
                    if match:
                        analysis.entry_point = match.group(1)
            
            # Detect build system
            if (path.parent / "yarn.lock").exists():
                analysis.build_system = "yarn"
            elif (path.parent / "pnpm-lock.yaml").exists():
                analysis.build_system = "pnpm"
            else:
                analysis.build_system = "npm"
                
        except Exception as e:
            logger.warning(f"Error parsing package.json: {e}")
        
        return analysis
    
    def _find_entry_point(self, project_path: Path, analysis: ProjectAnalysis) -> Optional[str]:
        """Find the main entry point"""
        if analysis.entry_point:
            return analysis.entry_point
        
        common_entry_points = ["index.js", "app.js", "server.js", "main.js"]
        
        for entry in common_entry_points:
            if (project_path / entry).exists():
                return entry
        
        return None
    
    def _check_database_usage(self, analysis: ProjectAnalysis) -> ProjectAnalysis:
        """Check if project uses databases"""
        db_indicators = {
            "postgresql": ["pg", "postgres", "sequelize"],
            "mysql": ["mysql", "mysql2"],
            "mongodb": ["mongodb", "mongoose"],
            "redis": ["redis", "ioredis"],
        }
        
        all_deps = [d.name for d in analysis.dependencies]
        
        for db_type, indicators in db_indicators.items():
            for indicator in indicators:
                if indicator in all_deps:
                    if db_type == "redis":
                        analysis.requires_redis = True
                    else:
                        analysis.requires_database = True
                    break
        
        return analysis
    
    def _suggest_nix_packages(self, analysis: ProjectAnalysis) -> List[str]:
        """Suggest Nix packages"""
        packages = ["nodejs", "nodePackages.npm"]
        
        if analysis.build_system == "yarn":
            packages.append("yarn")
        elif analysis.build_system == "pnpm":
            packages.append("nodePackages.pnpm")
        
        if analysis.requires_database:
            packages.append("postgresql")
        
        if analysis.requires_redis:
            packages.append("redis")
        
        return packages
    
    def _generate_shell_nix(self, analysis: ProjectAnalysis) -> str:
        """Generate shell.nix"""
        packages = " ".join(analysis.suggested_nix_packages)
        
        return f"""{{ pkgs ? import <nixpkgs> {{}} }}:

pkgs.mkShell {{
  buildInputs = with pkgs; [
    {packages}
  ];

  shellHook = ''
    echo "🟢 Node.js Development Environment"
    echo "Framework: {analysis.framework or 'None'}"
    echo "Build System: {analysis.build_system}"
    
    # Install dependencies
    {analysis.build_system} install
  '';
}}"""
    
    def _calculate_confidence(self, analysis: ProjectAnalysis) -> float:
        """Calculate confidence score"""
        score = 0.0
        
        if analysis.build_system:
            score += 0.25
        if analysis.dependencies:
            score += 0.25
        if analysis.entry_point:
            score += 0.25
        if analysis.framework:
            score += 0.25
        
        return min(score, 1.0)


class MultiLanguageAnalyzer:
    """Main analyzer that delegates to language-specific analyzers"""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.analyzers = {
            "python": PythonAnalyzer(),
            "nodejs": NodeJSAnalyzer(),
            # Add more analyzers as we implement them
        }
    
    def analyze_project(self, project_path: str) -> ProjectAnalysis:
        """Analyze a project and return comprehensive analysis"""
        path = Path(project_path)
        
        if not path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        # Detect language
        language = self.detector.detect_language(path)
        
        if not language:
            return ProjectAnalysis(
                language="unknown",
                confidence_score=0.0
            )
        
        # Use appropriate analyzer
        if language in self.analyzers:
            return self.analyzers[language].analyze(path)
        else:
            # Basic analysis for unsupported languages
            return ProjectAnalysis(
                language=language,
                confidence_score=0.1
            )
    
    def generate_nix_config(self, analysis: ProjectAnalysis) -> str:
        """Generate complete Nix configuration for project"""
        if analysis.nix_shell_config:
            return analysis.nix_shell_config
        
        # Fallback for unknown languages
        return f"""{{ pkgs ? import <nixpkgs> {{}} }}:

pkgs.mkShell {{
  buildInputs = with pkgs; [
    # Detected language: {analysis.language}
    # Add your packages here
  ];
}}"""
    
    def suggest_improvements(self, analysis: ProjectAnalysis) -> List[str]:
        """Suggest improvements for the project"""
        suggestions = []
        
        if not analysis.build_system:
            if analysis.language == "python":
                suggestions.append("Consider using Poetry for dependency management")
            elif analysis.language == "nodejs":
                suggestions.append("Consider using Yarn or pnpm for better performance")
        
        if not analysis.entry_point:
            suggestions.append("Define a clear entry point for your application")
        
        if analysis.requires_database and "docker" not in [d.name for d in analysis.dependencies]:
            suggestions.append("Consider using Docker for database development")
        
        if analysis.environment_variables and not (Path(analysis.language) / ".env.example").exists():
            suggestions.append("Create a .env.example file to document required environment variables")
        
        return suggestions


# Integration with main system
def analyze_and_generate(project_path: str) -> Dict[str, Any]:
    """Main entry point for project analysis"""
    analyzer = MultiLanguageAnalyzer()
    
    # Analyze the project
    analysis = analyzer.analyze_project(project_path)
    
    # Generate Nix configuration
    nix_config = analyzer.generate_nix_config(analysis)
    
    # Get suggestions
    suggestions = analyzer.suggest_improvements(analysis)
    
    return {
        "analysis": {
            "language": analysis.language,
            "framework": analysis.framework,
            "build_system": analysis.build_system,
            "entry_point": analysis.entry_point,
            "dependencies": [d.name for d in analysis.dependencies],
            "dev_dependencies": [d.name for d in analysis.dev_dependencies],
            "requires_database": analysis.requires_database,
            "requires_redis": analysis.requires_redis,
            "environment_variables": list(analysis.environment_variables),
            "confidence": analysis.confidence_score,
        },
        "nix_config": nix_config,
        "suggested_packages": analysis.suggested_nix_packages,
        "improvements": suggestions,
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        result = analyze_and_generate(project_path)
        
        print(f"\n🔍 Project Analysis: {project_path}")
        print("=" * 60)
        
        analysis = result["analysis"]
        print(f"Language: {analysis['language']}")
        print(f"Framework: {analysis['framework'] or 'None detected'}")
        print(f"Build System: {analysis['build_system'] or 'Unknown'}")
        print(f"Entry Point: {analysis['entry_point'] or 'Not found'}")
        print(f"Confidence: {analysis['confidence']:.0%}")
        
        if analysis['dependencies']:
            print(f"\nDependencies ({len(analysis['dependencies'])}):")
            for dep in analysis['dependencies'][:5]:
                print(f"  - {dep}")
            if len(analysis['dependencies']) > 5:
                print(f"  ... and {len(analysis['dependencies']) - 5} more")
        
        if result['suggested_packages']:
            print(f"\nSuggested Nix Packages:")
            for pkg in result['suggested_packages']:
                print(f"  - {pkg}")
        
        if result['improvements']:
            print(f"\nSuggested Improvements:")
            for suggestion in result['improvements']:
                print(f"  💡 {suggestion}")
        
        print(f"\n📝 Generated shell.nix:")
        print("-" * 40)
        print(result['nix_config'])
    else:
        print("Usage: python multi_language_parser.py <project_path>")