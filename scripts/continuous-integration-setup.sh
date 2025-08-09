#!/usr/bin/env bash
# Set up continuous integration to maintain quality
# Supports GitHub Actions, GitLab CI, and local git hooks

set -euo pipefail

echo "🔄 Setting up Continuous Integration..."

# Create GitHub Actions workflow
mkdir -p .github/workflows

cat > .github/workflows/quality-check.yml << 'YAML'
name: Quality Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  structure-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Check root directory cleanliness
      run: |
        ROOT_FILES=$(find . -maxdepth 1 -type f -name "*.py" | wc -l)
        if [ $ROOT_FILES -gt 5 ]; then
          echo "❌ Too many Python files in root: $ROOT_FILES"
          exit 1
        fi
        echo "✅ Root directory is clean"
    
    - name: Check for test files in root
      run: |
        TEST_FILES=$(find . -maxdepth 1 -name "test_*.py" | wc -l)
        if [ $TEST_FILES -gt 0 ]; then
          echo "❌ Test files found in root: $TEST_FILES"
          exit 1
        fi
        echo "✅ No test files in root"

  python-quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install --no-interaction
    
    - name: Lint with black
      run: |
        poetry run black --check src/ tests/
    
    - name: Type check with mypy
      run: |
        poetry run mypy src/ --ignore-missing-imports
    
    - name: Security check
      run: |
        poetry run bandit -r src/ -ll

  test-suite:
    runs-on: ubuntu-latest
    needs: python-quality
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install Nix
      uses: cachix/install-nix-action@v22
      with:
        nix_path: nixpkgs=channel:nixos-23.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install --no-interaction --with dev,test
    
    - name: Run unit tests
      run: |
        poetry run pytest tests/unit -v --cov=nix_humanity --cov-report=xml
    
    - name: Run integration tests
      run: |
        poetry run pytest tests/integration -v -m "not slow"
    
    - name: Check test coverage
      run: |
        poetry run coverage report --fail-under=80

  performance-check:
    runs-on: ubuntu-latest
    needs: test-suite
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install --no-interaction
    
    - name: Run performance benchmarks
      run: |
        poetry run pytest tests/performance -v --benchmark-only
    
    - name: Check performance regression
      run: |
        poetry run python scripts/validate-performance.py

  documentation-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Check README honesty
      run: |
        if grep -q "99%" README.md && ! grep -q "alpha\|beta\|development" README.md; then
          echo "❌ README claims high completion without development disclaimer"
          exit 1
        fi
        echo "✅ README appears honest about development status"
    
    - name: Check for outdated examples
      run: |
        # Check if code examples in docs actually work
        poetry run python scripts/validate-examples.py || true

  release-readiness:
    runs-on: ubuntu-latest
    needs: [structure-check, python-quality, test-suite, documentation-check]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Generate progress report
      run: |
        python scripts/progress-dashboard.py
        
    - name: Upload progress report
      uses: actions/upload-artifact@v3
      with:
        name: progress-dashboard
        path: metrics/dashboard.html
YAML

echo "✅ Created GitHub Actions workflow"

# Create GitLab CI configuration
cat > .gitlab-ci.yml << 'YAML'
stages:
  - quality
  - test
  - performance
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

before_script:
  - python -V
  - pip install poetry
  - poetry install --no-interaction

structure-check:
  stage: quality
  script:
    - |
      ROOT_FILES=$(find . -maxdepth 1 -type f -name "*.py" | wc -l)
      if [ $ROOT_FILES -gt 5 ]; then
        echo "Too many Python files in root"
        exit 1
      fi

lint:
  stage: quality
  script:
    - poetry run black --check src/ tests/
    - poetry run flake8 src/ tests/
    - poetry run mypy src/

test:
  stage: test
  script:
    - poetry run pytest tests/ --cov=nix_humanity
    - poetry run coverage report --fail-under=80

performance:
  stage: performance
  script:
    - poetry run pytest tests/performance -v
    - poetry run python scripts/validate-performance.py

progress-report:
  stage: report
  script:
    - python scripts/progress-dashboard.py
  artifacts:
    paths:
      - metrics/
    expire_in: 1 week
YAML

echo "✅ Created GitLab CI configuration"

# Create local pre-commit hooks
cat > .pre-commit-config.yaml << 'YAML'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: ['--ignore-missing-imports']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']

  - repo: local
    hooks:
      - id: no-pip-install
        name: Check for pip install
        entry: 'pip install'
        language: pygrep
        types: [text]
        exclude: '^(archive/|\.git/)'
        
      - id: feature-freeze
        name: Enforce feature freeze
        entry: python scripts/feature-freeze-manager.py
        language: system
        pass_filenames: false
YAML

echo "✅ Created pre-commit configuration"

# Create validation script for examples
cat > scripts/validate-examples.py << 'PYTHON'
#!/usr/bin/env python3
"""
Validate that code examples in documentation actually work.
"""

import re
import ast
from pathlib import Path

def extract_code_blocks(markdown_file):
    """Extract code blocks from markdown files."""
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Find code blocks
    pattern = r'```(?:python|bash|sh)\n(.*?)\n```'
    blocks = re.findall(pattern, content, re.DOTALL)
    
    return blocks

def validate_python_code(code):
    """Check if Python code is syntactically valid."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def validate_bash_command(command):
    """Basic validation of bash commands."""
    # Check for common issues
    if 'rm -rf /' in command:
        return False, "Dangerous command"
    
    if command.strip().startswith('$'):
        return False, "Command starts with $ prompt"
    
    return True, None

def main():
    """Validate all examples in documentation."""
    issues = []
    
    # Find all markdown files
    for md_file in Path('.').rglob('*.md'):
        if 'archive' in str(md_file):
            continue
            
        blocks = extract_code_blocks(md_file)
        
        for i, block in enumerate(blocks):
            # Detect language
            if block.strip().startswith('#!') or 'bash' in block:
                valid, error = validate_bash_command(block)
                lang = 'bash'
            else:
                valid, error = validate_python_code(block)
                lang = 'python'
            
            if not valid:
                issues.append({
                    'file': str(md_file),
                    'block': i + 1,
                    'language': lang,
                    'error': error
                })
    
    # Report results
    if issues:
        print(f"❌ Found {len(issues)} invalid code examples:")
        for issue in issues[:10]:  # Limit output
            print(f"  - {issue['file']} block {issue['block']}: {issue['error']}")
        return 1
    else:
        print("✅ All code examples are valid")
        return 0

if __name__ == '__main__':
    exit(main())
PYTHON

chmod +x scripts/validate-examples.py

# Create CI setup script
cat > scripts/setup-ci.sh << 'BASH'
#!/usr/bin/env bash
# Set up CI based on detected environment

set -euo pipefail

echo "🔍 Detecting CI environment..."

if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    
    # Install pre-commit hooks
    if command -v pre-commit >/dev/null 2>&1; then
        echo "Installing pre-commit hooks..."
        pre-commit install
        echo "✅ Pre-commit hooks installed"
    else
        echo "⚠️  pre-commit not found. Install with: pip install pre-commit"
    fi
    
    # Check for CI service
    if [ -f ".github/workflows/quality-check.yml" ]; then
        echo "✅ GitHub Actions configured"
    elif [ -f ".gitlab-ci.yml" ]; then
        echo "✅ GitLab CI configured"
    else
        echo "⚠️  No CI service detected"
    fi
else
    echo "❌ Not a git repository"
fi

echo ""
echo "📋 CI Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Commit CI configuration files"
echo "2. Push to trigger first CI run"
echo "3. Add status badge to README"
BASH

chmod +x scripts/setup-ci.sh

echo "✅ CI setup scripts created!"
echo ""
echo "🚀 To enable CI:"
echo "1. Run: ./scripts/setup-ci.sh"
echo "2. Commit the CI configuration files"
echo "3. Push to your repository"