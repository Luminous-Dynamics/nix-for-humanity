#!/usr/bin/env python3
"""
Create the clean Python-only package structure for Nix for Humanity.
This establishes the target architecture from ARCHITECTURE_IMPROVEMENT_PLAN.md.
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create the clean Python package structure."""
    root = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity')
    
    # Define the new structure
    structure = {
        'nix_humanity': {
            '__init__.py': '"""Nix for Humanity - Making NixOS accessible through natural conversation."""\n\n__version__ = "0.5.2"',
            'core': {
                '__init__.py': '"""Core business logic for intent recognition and command execution."""',
                'intents.py': '"""Unified intent recognition system."""',
                'executor.py': '"""Safe command execution with sandboxing."""',
                'knowledge.py': '"""Knowledge base for NixOS operations."""',
                'personality.py': '"""10-persona adaptive response system."""',
            },
            'learning': {
                '__init__.py': '"""AI/ML components for continuous improvement."""',
                'patterns.py': '"""Pattern learning from user interactions."""',
                'preferences.py': '"""User preference tracking and adaptation."""',
                'adaptation.py': '"""Adaptive behavior based on usage."""',
            },
            'interfaces': {
                '__init__.py': '"""User interfaces - CLI, TUI, Voice, API."""',
                'cli.py': '"""Command-line interface adapter."""',
                'tui.py': '"""Terminal UI with Textual."""',
                'voice.py': '"""Voice interface with pipecat."""',
                'api.py': '"""REST/GraphQL API server."""',
            },
            'security': {
                '__init__.py': '"""Security layer for input validation and sandboxing."""',
                'validator.py': '"""Input validation and sanitization."""',
            },
            'utils': {
                '__init__.py': '"""Shared utilities and helpers."""',
                'config.py': '"""Configuration management."""',
                'logging.py': '"""Logging configuration."""',
            },
        }
    }
    
    def create_structure(base_path: Path, structure: dict):
        """Recursively create directory structure with files."""
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # It's a directory
                path.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created directory: {path}")
                create_structure(path, content)
            else:
                # It's a file
                if not path.exists():
                    path.write_text(content)
                    print(f"📄 Created file: {path}")
    
    # Create the main package
    create_structure(root, {'nix_humanity': structure['nix_humanity']})
    
    # Create other necessary directories
    other_dirs = ['tests', 'docs', 'scripts']
    for dir_name in other_dirs:
        dir_path = root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"📁 Created directory: {dir_path}")
    
    # Create pyproject.toml
    pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "nix-humanity"
version = "0.5.2"
description = "Natural language interface for NixOS"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Tristan Stoltz", email = "tristan.stoltz@gmail.com"},
]
keywords = ["nixos", "ai", "natural-language", "cli", "tui"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: System :: Systems Administration",
]

dependencies = [
    "click>=8.0",
    "textual>=0.38",
    "sqlalchemy>=2.0",
    "pydantic>=2.0",
    "aiohttp>=3.8",
    "asyncio>=3.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1",
]
voice = [
    "speech_recognition>=3.10",
    "pyttsx3>=2.90",
]

[project.scripts]
nix-humanity = "nix_humanity.interfaces.cli:main"
nix-humanity-tui = "nix_humanity.interfaces.tui:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["nix_humanity*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "B", "C90", "D"]
ignore = ["D100", "D101", "D102", "D103", "D104"]
'''
    
    pyproject_path = root / 'pyproject.toml'
    if not pyproject_path.exists():
        pyproject_path.write_text(pyproject_content)
        print(f"📄 Created file: {pyproject_path}")
    
    print("\n✅ Python package structure created successfully!")

def migrate_existing_code():
    """Migrate existing Python code to new structure."""
    root = Path('/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity')
    
    migrations = [
        # Core migrations
        ('backend/core/intent.py', 'nix_humanity/core/intents.py'),
        ('backend/core/executor.py', 'nix_humanity/core/executor.py'),
        ('backend/core/knowledge.py', 'nix_humanity/core/knowledge.py'),
        ('backend/core/personality.py', 'nix_humanity/core/personality.py'),
        
        # Learning migrations
        ('backend/learning/pattern_learner.py', 'nix_humanity/learning/patterns.py'),
        ('backend/learning/preference_manager.py', 'nix_humanity/learning/preferences.py'),
        ('backend/ui/adaptive_complexity.py', 'nix_humanity/learning/adaptation.py'),
        
        # Interface migrations
        ('bin/ask-nix', 'nix_humanity/interfaces/cli.py'),
        ('bin/nix-tui', 'nix_humanity/interfaces/tui.py'),
        
        # Security migrations
        ('backend/security/input_validator.py', 'nix_humanity/security/validator.py'),
    ]
    
    print("\n📦 Migrating existing code...")
    for old_path, new_path in migrations:
        old_file = root / old_path
        new_file = root / new_path
        
        if old_file.exists() and not new_file.exists():
            # Read content
            content = old_file.read_text()
            
            # Update imports
            content = content.replace('from backend.', 'from nix_humanity.')
            content = content.replace('from ..', 'from nix_humanity')
            content = content.replace('import nix_humanity.core as backend.', 'import nix_humanity.')
            
            # Write to new location
            new_file.parent.mkdir(parents=True, exist_ok=True)
            new_file.write_text(content)
            print(f"✅ Migrated: {old_path} → {new_path}")

def main():
    """Main execution."""
    print("🏗️  Creating Python-Only Package Structure")
    print("=" * 50)
    
    create_directory_structure()
    # migrate_existing_code()  # Will implement after TypeScript removal
    
    print("\n🎉 Structure creation complete!")
    print("\nNext steps:")
    print("1. Run remove_typescript_javascript.py to clean up TS/JS files")
    print("2. Migrate existing Python code to new structure")
    print("3. Update all imports to use nix_humanity package")
    print("4. Run tests to ensure everything works")

if __name__ == '__main__':
    main()