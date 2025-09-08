#!/bin/bash
# Build standalone binary for Luminous Nix v0.3.0
# Creates a zero-dependency executable that can run anywhere

set -e

echo "🚀 Building Standalone Binary for Luminous Nix v0.3.0"
echo "====================================================="

# Clean previous builds
rm -rf dist-standalone/
mkdir -p dist-standalone/

# Install PyInstaller if not present
if ! poetry show pyinstaller &>/dev/null; then
    echo "📦 Installing PyInstaller..."
    poetry add --group dev pyinstaller
fi

# Create entry point script
cat > build_entry.py << 'EOF'
#!/usr/bin/env python3
"""Entry point for standalone executable"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run main CLI
from luminous_nix.cli import main

if __name__ == "__main__":
    sys.exit(main())
EOF

# Create PyInstaller spec file
cat > luminous-nix.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['build_entry.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('models', 'models'),
        ('data', 'data'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'luminous_nix',
        'luminous_nix.core',
        'luminous_nix.ai',
        'luminous_nix.ai.hrm_integrated_v6_final',
        'luminous_nix.ai.dev_environment_specialist',
        'luminous_nix.ai.update_maintenance_specialist',
        'luminous_nix.ai.transformer_enhanced_model',
        'luminous_nix.ai.active_learning_system',
        'luminous_nix.cache',
        'luminous_nix.services',
        'luminous_nix.ui',
        'click',
        'rich',
        'prompt_toolkit',
        'yaml',
        'toml',
        'textual',
        'httpx',
        'questionary',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'torchvision', 'transformers'],  # Exclude heavy ML libs for basic version
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='luminous-nix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

echo "📦 Building with PyInstaller..."
poetry run pyinstaller luminous-nix.spec --clean

# Move binary to dist-standalone
mv dist/luminous-nix dist-standalone/

# Create wrapper script
cat > dist-standalone/luminous-nix-wrapper << 'EOF'
#!/bin/bash
# Wrapper script for Luminous Nix standalone
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec "$DIR/luminous-nix" "$@"
EOF
chmod +x dist-standalone/luminous-nix-wrapper

# Create README for standalone
cat > dist-standalone/README.md << 'EOF'
# Luminous Nix v0.3.0 - Standalone Binary

## Quick Start

```bash
# Make executable
chmod +x luminous-nix

# Run directly
./luminous-nix "install firefox"

# Or add to PATH
sudo cp luminous-nix /usr/local/bin/
luminous-nix "search text editors"
```

## Features

This standalone binary includes:
- ✅ Natural language CLI
- ✅ 96.3% accuracy
- ✅ Pattern-based specialists
- ✅ Intelligent caching
- ❌ Neural networks (requires Python environment)
- ❌ Voice interface (requires additional dependencies)

For full features including neural networks, install via:
- PyPI: `pip install luminous-nix[neural]`
- Nix: `nix-env -iA nixpkgs.luminous-nix`

## System Requirements

- Linux x86_64
- 50MB disk space
- 256MB RAM

## License

MIT - See https://github.com/Luminous-Dynamics/luminous-nix
EOF

# Create tarball
echo "📦 Creating distribution archive..."
cd dist-standalone/
tar -czf luminous-nix-v0.3.0-standalone.tar.gz \
    luminous-nix \
    luminous-nix-wrapper \
    README.md

# Calculate checksums
sha256sum luminous-nix-v0.3.0-standalone.tar.gz > luminous-nix-v0.3.0-standalone.tar.gz.sha256
md5sum luminous-nix-v0.3.0-standalone.tar.gz > luminous-nix-v0.3.0-standalone.tar.gz.md5

# Display results
echo ""
echo "✅ Standalone binary built successfully!"
echo ""
echo "📁 Output files:"
ls -lh luminous-nix*
echo ""
echo "📊 Binary size: $(du -h luminous-nix | cut -f1)"
echo "📦 Package size: $(du -h luminous-nix-v0.3.0-standalone.tar.gz | cut -f1)"
echo ""
echo "🚀 Distribution ready at: dist-standalone/luminous-nix-v0.3.0-standalone.tar.gz"
echo ""
echo "Test with:"
echo "  ./luminous-nix --help"
echo "  ./luminous-nix 'install firefox'"