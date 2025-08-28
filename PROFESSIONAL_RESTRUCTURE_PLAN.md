# 🏗️ Professional NixOS Project Restructure Plan

## Executive Summary

**Problem**: Luminous Nix has significant code sprawl with:
- 30+ duplicate config/error/voice/learning implementations
- Mixed project files (Sacred Spaceports accidentally merged)
- No clear separation between core and extensions
- Multiple redundant archive directories
- Aspirational code mixed with working code

**Solution**: Restructure to professional NixOS package layout following best practices.

---

## 📊 Current Issues

### 1. Duplicate Implementations Found
```
src/luminous_nix/
├── config/           # Config system 1
├── consciousness/    # Has config, error, voice, learning
├── learning/         # Learning system 2
├── memory/           # Has learning components
├── ai/               # Has learning components
├── nlp/              # Has intent recognition
├── interfaces/       # Has voice interface
├── voice/            # Voice system 2
└── ui/               # Has error handling
```

### 2. Sprawl Statistics
- **Python files**: 500+ across multiple hierarchies
- **Duplicate features**: 30+ implementations of same concepts
- **Test files**: 150+ with many testing non-existent features
- **Documentation**: 200+ files, many outdated or aspirational

---

## 🎯 Target Professional Structure

```
luminous-nix/
├── src/
│   └── luminous_nix/           # Single source tree
│       ├── __init__.py
│       ├── core/                # Core functionality only
│       │   ├── __init__.py
│       │   ├── intent.py       # Intent recognition
│       │   ├── executor.py     # Command execution
│       │   ├── knowledge.py    # NixOS knowledge base
│       │   └── types.py        # Type definitions
│       ├── backends/            # Backend implementations
│       │   ├── __init__.py
│       │   ├── nix_native.py   # Native Python-Nix API
│       │   ├── subprocess.py   # Fallback subprocess
│       │   └── mock.py         # Testing backend
│       ├── frontends/           # User interfaces
│       │   ├── __init__.py
│       │   ├── cli.py          # CLI interface
│       │   ├── tui.py          # TUI interface
│       │   └── api.py          # REST API
│       ├── extensions/          # Optional features
│       │   ├── __init__.py
│       │   ├── voice.py        # Voice interface
│       │   ├── learning.py     # Learning system
│       │   └── ai.py           # AI integrations
│       └── utils/               # Shared utilities
│           ├── __init__.py
│           ├── config.py       # Configuration
│           ├── logging.py      # Logging
│           └── errors.py       # Error handling
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py            # Test configuration
├── bin/                         # Entry points
│   ├── ask-nix                 # Main CLI
│   └── nix-tui                 # TUI launcher
├── docs/                        # Documentation
│   ├── user/                   # User guides
│   ├── api/                    # API documentation
│   └── development/            # Developer guides
├── examples/                    # Example usage
├── nix/                         # Nix expressions
│   ├── default.nix             # Package definition
│   ├── module.nix              # NixOS module
│   └── overlay.nix             # Nixpkgs overlay
├── pyproject.toml              # Python project config
├── flake.nix                   # Nix flake
├── README.md                   # Project readme
└── LICENSE                     # License file
```

---

## 🔄 Migration Strategy

### Phase 1: Consolidate Core (Day 1)
1. **Identify working code**
   - Package management (install/remove/search)
   - Natural language processing
   - Error handling
   - CLI interface

2. **Create core module**
   ```python
   # src/luminous_nix/core/__init__.py
   from .intent import Intent, IntentRecognizer
   from .executor import CommandExecutor
   from .knowledge import KnowledgeBase
   from .types import Command, Response
   ```

3. **Remove duplicates**
   - Keep best implementation
   - Archive others with notes

### Phase 2: Organize Backends (Day 2)
1. **Extract backend interfaces**
   ```python
   # src/luminous_nix/backends/base.py
   class NixBackend(ABC):
       @abstractmethod
       def install_package(self, package: str) -> Response:
           pass
   ```

2. **Implement backends**
   - Native Python-Nix API (primary)
   - Subprocess fallback
   - Mock for testing

### Phase 3: Clean Frontends (Day 3)
1. **Consolidate interfaces**
   - One CLI implementation
   - One TUI implementation
   - One API implementation

2. **Remove experimental UIs**
   - Archive GUI attempts
   - Archive incomplete frontends

### Phase 4: Extensions as Plugins (Day 4)
1. **Make optional features truly optional**
   ```python
   # src/luminous_nix/extensions/__init__.py
   AVAILABLE_EXTENSIONS = {
       'voice': 'luminous_nix.extensions.voice',
       'learning': 'luminous_nix.extensions.learning',
       'ai': 'luminous_nix.extensions.ai',
   }
   ```

2. **Lazy loading**
   - Only load when requested
   - Clear dependencies

### Phase 5: Test Cleanup (Day 5)
1. **Remove aspirational tests**
   - Tests for non-existent features
   - Tests that always skip

2. **Organize by structure**
   ```
   tests/
   ├── unit/
   │   ├── test_core/
   │   ├── test_backends/
   │   └── test_utils/
   └── integration/
       ├── test_cli/
       └── test_real_nix/
   ```

---

## 📦 NixOS Best Practices Integration

### 1. Proper Nix Package
```nix
# nix/default.nix
{ lib, python3Packages, ... }:

python3Packages.buildPythonPackage rec {
  pname = "luminous-nix";
  version = "0.3.2";
  
  src = ../.; 
  
  propagatedBuildInputs = with python3Packages; [
    click
    pydantic
    rich
    # Only required dependencies
  ];
  
  checkInputs = with python3Packages; [
    pytest
    pytest-cov
  ];
  
  meta = with lib; {
    description = "Natural language interface for NixOS";
    homepage = "https://github.com/Luminous-Dynamics/luminous-nix";
    license = licenses.mit;
    maintainers = [ maintainers.tstoltz ];
  };
}
```

### 2. NixOS Module
```nix
# nix/module.nix
{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.luminous-nix;
in {
  options.services.luminous-nix = {
    enable = mkEnableOption "Luminous Nix natural language interface";
    
    extensions = mkOption {
      type = types.listOf types.str;
      default = [];
      description = "Extensions to enable (voice, learning, ai)";
    };
  };
  
  config = mkIf cfg.enable {
    environment.systemPackages = [ pkgs.luminous-nix ];
  };
}
```

### 3. Flake Structure
```nix
# flake.nix
{
  description = "Natural language interface for NixOS";
  
  outputs = { self, nixpkgs }: {
    packages = forAllSystems (system: {
      default = nixpkgs.legacyPackages.${system}.callPackage ./nix {};
    });
    
    nixosModules.default = ./nix/module.nix;
    
    overlays.default = final: prev: {
      luminous-nix = self.packages.${final.system}.default;
    };
  };
}
```

---

## 🚀 Implementation Steps

### Immediate Actions (Today)
1. **Create migration script**
   ```bash
   ./scripts/restructure.sh
   ```

2. **Archive sprawl**
   ```bash
   mkdir -p .archive-2025-08-25-restructure
   mv [duplicate-files] .archive-2025-08-25-restructure/
   ```

3. **Start with core**
   - Create new structure
   - Move working code
   - Update imports

### Success Metrics
- **Before**: 500+ Python files across 50+ directories
- **After**: ~50 Python files in clear structure
- **Test coverage**: Real 70%+ (not aspirational)
- **Documentation**: Matches actual functionality

---

## ⚠️ Critical Rules

1. **NO MOCKS IN PRODUCTION**
   - Test mocks stay in tests/
   - Never ship workarounds

2. **ARCHIVE, DON'T DELETE**
   - Everything goes to .archive-YYYY-MM-DD/
   - Include ARCHIVE_LOG.md

3. **ONE IMPLEMENTATION PER FEATURE**
   - No duplicate voice systems
   - No multiple config managers
   - No redundant learning engines

4. **FOLLOW NIX CONVENTIONS**
   - Use buildPythonPackage
   - Provide NixOS module
   - Include overlay

---

## 📝 Migration Script

```bash
#!/usr/bin/env bash
# restructure.sh - Professional restructuring for Luminous Nix

set -e

ARCHIVE_DIR=".archive-$(date +%Y-%m-%d)-restructure"
mkdir -p "$ARCHIVE_DIR"

# Step 1: Archive duplicates
echo "📦 Archiving duplicate implementations..."
find src -name "*config*" -o -name "*error*" | while read file; do
    # Logic to identify and archive duplicates
done

# Step 2: Create new structure
echo "🏗️ Creating professional structure..."
mkdir -p src/luminous_nix/{core,backends,frontends,extensions,utils}
mkdir -p tests/{unit,integration}
mkdir -p docs/{user,api,development}
mkdir -p nix

# Step 3: Move core functionality
echo "🎯 Moving core functionality..."
# Move intent recognition, executor, knowledge base

# Step 4: Update imports
echo "🔄 Updating imports..."
python scripts/update-imports.py

# Step 5: Run tests
echo "✅ Verifying functionality..."
pytest tests/

echo "✨ Restructuring complete!"
```

---

## 🎯 Expected Outcomes

### Code Quality
- Clear separation of concerns
- No duplicate implementations
- Testable architecture
- Plugin-based extensions

### Developer Experience
- Easy to understand structure
- Clear contribution path
- Standard Python patterns
- NixOS best practices

### User Experience
- Faster performance (less code)
- More reliable (tested code only)
- Clear feature set
- Professional feel

---

## 📅 Timeline

- **Day 1**: Core consolidation
- **Day 2**: Backend organization
- **Day 3**: Frontend cleanup
- **Day 4**: Extension system
- **Day 5**: Test suite cleanup
- **Week 2**: Documentation update
- **Week 3**: Release v0.4.0

---

*This plan transforms Luminous Nix from experimental sprawl to professional tool.*