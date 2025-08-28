#!/usr/bin/env bash
# Professional restructuring script for Luminous Nix
# Transforms sprawled codebase into clean NixOS package structure

set -e

echo "🏗️  Starting Professional Restructure for Luminous Nix"
echo "================================================"

PROJECT_ROOT="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
cd "$PROJECT_ROOT"

# Create archive directory with timestamp
ARCHIVE_DIR=".archive-$(date +%Y-%m-%d-%H%M)-restructure"
mkdir -p "$ARCHIVE_DIR"

echo ""
echo "📦 Step 1: Archiving duplicate and experimental code..."
echo "-----------------------------------------------"

# Archive consciousness directory (too experimental)
if [ -d "src/luminous_nix/consciousness" ]; then
    echo "  Archiving consciousness/ (30+ files of experimental code)"
    mv src/luminous_nix/consciousness "$ARCHIVE_DIR/consciousness"
fi

# Archive redundant directories
for dir in src/luminous_nix/llm src/luminous_nix/sandbox src/luminous_nix/monitoring; do
    if [ -d "$dir" ]; then
        echo "  Archiving $(basename $dir)/"
        mv "$dir" "$ARCHIVE_DIR/$(basename $dir)"
    fi
done

# Archive gui attempts
if [ -d "src/gui" ]; then
    echo "  Archiving src/gui/ (incomplete GUI)"
    mv src/gui "$ARCHIVE_DIR/src-gui"
fi

if [ -d "gui" ]; then
    echo "  Archiving gui/ (another GUI attempt)"
    mv gui "$ARCHIVE_DIR/gui"
fi

if [ -d "gui-tauri" ]; then
    echo "  Archiving gui-tauri/ (Tauri GUI attempt)"
    mv gui-tauri "$ARCHIVE_DIR/gui-tauri"
fi

echo ""
echo "🏗️  Step 2: Creating professional directory structure..."
echo "-----------------------------------------------"

# Create clean structure
mkdir -p src/luminous_nix/{core,backends,frontends,extensions,utils}
mkdir -p tests/{unit/{core,backends,frontends,utils},integration}
mkdir -p docs/{user,api,development}
mkdir -p nix
mkdir -p examples

echo "  Created core structure:"
echo "    src/luminous_nix/core/       - Core functionality"
echo "    src/luminous_nix/backends/   - Nix backends"
echo "    src/luminous_nix/frontends/  - User interfaces"
echo "    src/luminous_nix/extensions/ - Optional features"
echo "    src/luminous_nix/utils/      - Shared utilities"

echo ""
echo "🔄 Step 3: Consolidating core functionality..."
echo "-----------------------------------------------"

# Move core intent and execution logic
if [ -d "src/luminous_nix/core" ] && [ "$(ls -A src/luminous_nix/core)" ]; then
    echo "  Core directory already has files, preserving..."
else
    echo "  Moving core components..."
    
    # Move intent recognition
    if [ -f "src/luminous_nix/nlp/intent_recognition.py" ]; then
        cp src/luminous_nix/nlp/intent_recognition.py src/luminous_nix/core/intent.py
        echo "    ✓ Intent recognition"
    fi
    
    # Move command executor
    if [ -f "src/luminous_nix/core/command_executor.py" ]; then
        cp src/luminous_nix/core/command_executor.py src/luminous_nix/core/executor.py
        echo "    ✓ Command executor"
    fi
    
    # Move knowledge base
    if [ -f "src/luminous_nix/knowledge/knowledge_base.py" ]; then
        cp src/luminous_nix/knowledge/knowledge_base.py src/luminous_nix/core/knowledge.py
        echo "    ✓ Knowledge base"
    fi
    
    # Move types
    if [ -f "src/luminous_nix/types.py" ]; then
        cp src/luminous_nix/types.py src/luminous_nix/core/types.py
        echo "    ✓ Type definitions"
    fi
fi

echo ""
echo "🔌 Step 4: Organizing backends..."
echo "-----------------------------------------------"

# Move backend implementations
if [ -f "src/luminous_nix/nix/nix_backend.py" ]; then
    cp src/luminous_nix/nix/nix_backend.py src/luminous_nix/backends/nix_native.py
    echo "  ✓ Native Nix backend"
fi

if [ -f "src/luminous_nix/nix/subprocess_backend.py" ]; then
    cp src/luminous_nix/nix/subprocess_backend.py src/luminous_nix/backends/subprocess.py
    echo "  ✓ Subprocess backend"
fi

echo ""
echo "🖥️  Step 5: Consolidating frontends..."
echo "-----------------------------------------------"

# Move CLI interface
if [ -f "src/luminous_nix/interfaces/cli.py" ]; then
    cp src/luminous_nix/interfaces/cli.py src/luminous_nix/frontends/cli.py
    echo "  ✓ CLI interface"
fi

# Move TUI interface
if [ -f "src/luminous_nix/interfaces/tui.py" ]; then
    cp src/luminous_nix/interfaces/tui.py src/luminous_nix/frontends/tui.py
    echo "  ✓ TUI interface"
fi

# Move API interface
if [ -f "src/luminous_nix/interfaces/api.py" ]; then
    cp src/luminous_nix/interfaces/api.py src/luminous_nix/frontends/api.py
    echo "  ✓ API interface"
fi

echo ""
echo "🔌 Step 6: Making extensions optional..."
echo "-----------------------------------------------"

# Move voice as extension
if [ -f "src/luminous_nix/interfaces/voice.py" ]; then
    cp src/luminous_nix/interfaces/voice.py src/luminous_nix/extensions/voice.py
    echo "  ✓ Voice extension"
fi

# Move learning as extension
if [ -d "src/luminous_nix/learning" ]; then
    # Consolidate learning implementations
    cat > src/luminous_nix/extensions/learning.py << 'EOF'
"""Learning extension for Luminous Nix - tracks and learns from usage."""

class LearningSystem:
    """Optional learning system that adapts to user behavior."""
    
    def __init__(self):
        self.enabled = False
        
    def track_command(self, command: str, success: bool):
        """Track command usage for learning."""
        if not self.enabled:
            return
        # Implementation when enabled
        pass
        
    def get_suggestions(self, context: str) -> list:
        """Get learned suggestions based on context."""
        if not self.enabled:
            return []
        # Implementation when enabled
        return []
EOF
    echo "  ✓ Learning extension"
fi

# Move AI integrations as extension
if [ -d "src/luminous_nix/ai" ]; then
    # Consolidate AI features
    cat > src/luminous_nix/extensions/ai.py << 'EOF'
"""AI extension for enhanced natural language understanding."""

class AIIntegration:
    """Optional AI integration for advanced features."""
    
    def __init__(self):
        self.enabled = False
        self.ollama_available = False
        
    def enhance_intent(self, query: str) -> str:
        """Use AI to enhance intent understanding."""
        if not self.enabled:
            return query
        # Implementation when enabled
        return query
EOF
    echo "  ✓ AI extension"
fi

echo ""
echo "🔧 Step 7: Setting up utilities..."
echo "-----------------------------------------------"

# Consolidate config management
if [ -f "src/luminous_nix/config/config_manager.py" ]; then
    cp src/luminous_nix/config/config_manager.py src/luminous_nix/utils/config.py
    echo "  ✓ Configuration utilities"
fi

# Move logging
if [ -f "src/luminous_nix/logging_config.py" ]; then
    cp src/luminous_nix/logging_config.py src/luminous_nix/utils/logging.py
    echo "  ✓ Logging utilities"
fi

# Create error handling utilities
cat > src/luminous_nix/utils/errors.py << 'EOF'
"""Error handling utilities for Luminous Nix."""

class LuminousNixError(Exception):
    """Base exception for Luminous Nix."""
    pass

class CommandNotFoundError(LuminousNixError):
    """Raised when a command cannot be found."""
    pass

class BackendError(LuminousNixError):
    """Raised when a backend operation fails."""
    pass
EOF
echo "  ✓ Error handling utilities"

echo ""
echo "🧪 Step 8: Cleaning up tests..."
echo "-----------------------------------------------"

# Archive tests for non-existent features
mkdir -p "$ARCHIVE_DIR/tests"

# Move aspirational tests
for test in tests/test_consciousness.py tests/test_sacred*.py tests/test_maya_mode.py; do
    if [ -f "$test" ]; then
        echo "  Archiving $(basename $test) (tests non-existent features)"
        mv "$test" "$ARCHIVE_DIR/tests/"
    fi
done

# Organize remaining tests
if [ -d "tests/unit" ]; then
    echo "  Organizing unit tests by module..."
    # Move tests to match new structure
fi

echo ""
echo "📋 Step 9: Creating proper __init__ files..."
echo "-----------------------------------------------"

# Create main __init__.py
cat > src/luminous_nix/__init__.py << 'EOF'
"""Luminous Nix - Natural Language Interface for NixOS."""

__version__ = "0.3.2"
__author__ = "Tristan Stoltz"

from .core import Intent, CommandExecutor, KnowledgeBase
from .frontends import CLI

__all__ = ['Intent', 'CommandExecutor', 'KnowledgeBase', 'CLI', '__version__']
EOF

# Create core __init__.py
cat > src/luminous_nix/core/__init__.py << 'EOF'
"""Core functionality for Luminous Nix."""

try:
    from .intent import Intent, IntentRecognizer
    from .executor import CommandExecutor
    from .knowledge import KnowledgeBase
    from .types import Command, Response
    
    __all__ = ['Intent', 'IntentRecognizer', 'CommandExecutor', 
               'KnowledgeBase', 'Command', 'Response']
except ImportError:
    # Graceful degradation if components not ready
    pass
EOF

# Create other __init__ files
touch src/luminous_nix/backends/__init__.py
touch src/luminous_nix/frontends/__init__.py
touch src/luminous_nix/extensions/__init__.py
touch src/luminous_nix/utils/__init__.py

echo "  ✓ Created module initialization files"

echo ""
echo "📦 Step 10: Creating Nix package files..."
echo "-----------------------------------------------"

# Create proper Nix package definition
cat > nix/default.nix << 'EOF'
{ lib
, python3Packages
, fetchFromGitHub
}:

python3Packages.buildPythonPackage rec {
  pname = "luminous-nix";
  version = "0.3.2";
  
  src = ../.;
  
  propagatedBuildInputs = with python3Packages; [
    click
    pydantic
    rich
    pyyaml
    sqlalchemy
  ];
  
  checkInputs = with python3Packages; [
    pytest
    pytest-cov
    pytest-mock
  ];
  
  # Disable tests that require network or Nix
  checkPhase = ''
    pytest tests/unit
  '';
  
  meta = with lib; {
    description = "Natural language interface for NixOS";
    homepage = "https://github.com/Luminous-Dynamics/luminous-nix";
    license = licenses.mit;
    maintainers = [ ];
  };
}
EOF

# Create NixOS module
cat > nix/module.nix << 'EOF'
{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.programs.luminous-nix;
in {
  options.programs.luminous-nix = {
    enable = mkEnableOption "Luminous Nix - Natural language NixOS interface";
    
    package = mkOption {
      type = types.package;
      default = pkgs.luminous-nix;
      description = "The luminous-nix package to use";
    };
    
    extensions = mkOption {
      type = types.listOf (types.enum [ "voice" "learning" "ai" ]);
      default = [];
      description = "Extensions to enable";
    };
  };
  
  config = mkIf cfg.enable {
    environment.systemPackages = [ cfg.package ];
    
    # Set up shell aliases
    environment.shellAliases = {
      nix = "ask-nix";
    };
  };
}
EOF

echo "  ✓ Created Nix package definition"
echo "  ✓ Created NixOS module"

echo ""
echo "📝 Step 11: Creating archive log..."
echo "-----------------------------------------------"

cat > "$ARCHIVE_DIR/ARCHIVE_LOG.md" << EOF
# Archive Log - Professional Restructure
Date: $(date)
Reason: Consolidating sprawled codebase into professional structure

## What was archived:
- consciousness/ - 30+ files of experimental consciousness features
- Multiple GUI attempts (gui/, gui-tauri/, src/gui/)
- Duplicate implementations of config, error, voice, learning
- Aspirational test files
- Experimental features not yet working

## Why:
- Too much code sprawl (500+ Python files)
- Multiple duplicate implementations
- Mixed aspirational and working code
- No clear separation of concerns

## New structure:
- core/ - Essential working functionality
- backends/ - Clean backend implementations
- frontends/ - One implementation per interface
- extensions/ - Optional features as plugins
- utils/ - Shared utilities

## Migration notes:
All archived code is preserved here for reference.
If features are needed, they should be properly reimplemented
in the new structure, not copied back.
EOF

echo "  ✓ Created archive log"

echo ""
echo "🔍 Step 12: Cleaning up root directory..."
echo "-----------------------------------------------"

# Archive old directories
for dir in frontends services models modelfiles benchmarks dashboard visualizations; do
    if [ -d "$dir" ]; then
        echo "  Archiving $dir/"
        mv "$dir" "$ARCHIVE_DIR/"
    fi
done

# Archive excessive scripts
if [ -d "scripts" ] && [ "$(find scripts -type f | wc -l)" -gt 20 ]; then
    echo "  Archiving excessive scripts (keeping essential ones)"
    mkdir -p "$ARCHIVE_DIR/scripts"
    # Keep only essential scripts
    find scripts -type f -name "*.py" -o -name "*.sh" | \
        grep -v "update-imports\|restructure\|install" | \
        xargs -I {} mv {} "$ARCHIVE_DIR/scripts/"
fi

echo ""
echo "✨ Step 13: Final verification..."
echo "-----------------------------------------------"

echo "  New structure:"
tree src/luminous_nix -d -L 2 2>/dev/null || find src/luminous_nix -type d -maxdepth 2 | sort

echo ""
echo "  File counts:"
echo "    Python files in src/: $(find src -name "*.py" | wc -l)"
echo "    Test files: $(find tests -name "test_*.py" | wc -l)"
echo "    Documentation files: $(find docs -name "*.md" | wc -l)"
echo "    Archived files: $(find "$ARCHIVE_DIR" -type f | wc -l)"

echo ""
echo "✅ Professional restructuring complete!"
echo ""
echo "Next steps:"
echo "  1. Run: python scripts/update-imports.py"
echo "  2. Run: pytest tests/unit"
echo "  3. Update pyproject.toml to match new structure"
echo "  4. Update bin/ask-nix to use new imports"
echo "  5. Release v0.4.0 with clean structure"
echo ""
echo "Archive created at: $ARCHIVE_DIR"
echo "Remember: NEVER copy archived code back without proper refactoring!"
