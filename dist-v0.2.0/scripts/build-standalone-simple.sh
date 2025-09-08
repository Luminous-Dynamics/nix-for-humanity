#!/usr/bin/env bash
# 🚀 Simple Standalone Build for Luminous Nix
# Creates a self-contained script that bundles Python code

set -e

echo "🚀 Building Luminous Nix Standalone Package"
echo "==========================================="

# Ensure we're in project root
cd "$(dirname "$0")/.."

# Create distribution directory
mkdir -p dist-simple

# Create standalone launcher script
echo "📝 Creating standalone launcher..."
cat > dist-simple/luminous-nix << 'EOF'
#!/usr/bin/env python3
"""
Luminous Nix - Natural Language NixOS Interface
Standalone launcher that checks dependencies and runs the CLI
"""

import sys
import os
import subprocess

def check_dependency(module_name, package_name=None):
    """Check if a Python module is available"""
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
        return True
    except ImportError:
        print(f"⚠️  Missing dependency: {package_name}")
        print(f"   Install with: pip install {package_name}")
        return False

def main():
    # Check critical dependencies
    required = [
        ("click", "click"),
        ("rich", "rich"),
        ("psutil", "psutil"),
        ("typer", "typer"),
        ("pydantic", "pydantic"),
    ]
    
    missing = []
    for module, package in required:
        if not check_dependency(module, package):
            missing.append(package)
    
    if missing:
        print("\n❌ Missing dependencies. Install with:")
        print(f"   pip install {' '.join(missing)}")
        print("\nOr install all at once:")
        print("   pip install click rich psutil typer pydantic textual questionary")
        sys.exit(1)
    
    # Add bundled code to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(script_dir, 'luminous_nix_code'))
    
    # Set environment
    os.environ['LUMINOUS_STANDALONE'] = 'true'
    os.environ['LUMINOUS_SKIP_ONBOARDING'] = 'true'
    
    # Import and run
    try:
        from luminous_nix.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"❌ Error loading Luminous Nix: {e}")
        print("Make sure the luminous_nix_code directory is present")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✨ Goodbye!")
        sys.exit(0)

if __name__ == '__main__':
    main()
EOF

# Make launcher executable
chmod +x dist-simple/luminous-nix

# Copy source code
echo "📦 Copying source code..."
cp -r src dist-simple/luminous_nix_code

# Create requirements file
echo "📝 Creating requirements file..."
cat > dist-simple/requirements.txt << 'EOF'
click>=8.0.0
rich>=13.0.0
psutil>=5.9.0
typer>=0.9.0
pydantic>=2.0.0
textual>=0.40.0
questionary>=2.0.0
prompt-toolkit>=3.0.0
requests>=2.28.0
pyyaml>=6.0
EOF

# Create README
echo "📝 Creating README..."
cat > dist-simple/README.md << 'EOF'
# Luminous Nix - Standalone Distribution

Natural language interface for NixOS - no Poetry required!

## Quick Start

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run Luminous Nix:
```bash
./luminous-nix help
./luminous-nix search firefox
./luminous-nix install vim --dry-run
```

## Features

- Natural language NixOS commands
- Package search and discovery
- Configuration generation
- Safe dry-run mode by default

## Version

v0.6.1 - Phase B Production Release

## Requirements

- Python 3.8+
- NixOS or Nix package manager
- Dependencies from requirements.txt

## Support

Visit: https://github.com/Luminous-Dynamics/luminous-nix
EOF

# Create archive
echo "📦 Creating distribution archive..."
cd dist-simple
tar -czf luminous-nix-standalone.tar.gz \
    luminous-nix \
    luminous_nix_code \
    requirements.txt \
    README.md

cd ..

echo ""
echo "✅ Standalone package created!"
echo "================================"
echo "📦 Files in dist-simple/:"
echo "  - luminous-nix (launcher script)"
echo "  - luminous_nix_code/ (Python source)"
echo "  - requirements.txt (dependencies)"
echo "  - README.md (instructions)"
echo "  - luminous-nix-standalone.tar.gz (archive)"
echo ""
echo "📤 Distribution size: $(du -h dist-simple/luminous-nix-standalone.tar.gz | cut -f1)"
echo ""
echo "🚀 To test locally:"
echo "  cd dist-simple"
echo "  ./luminous-nix --help"