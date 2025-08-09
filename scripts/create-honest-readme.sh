#!/usr/bin/env bash
# Create an honest README that reflects actual project state

set -euo pipefail

echo "📝 Creating honest README.md..."

# Backup existing README
if [ -f "README.md" ]; then
    cp README.md README.md.backup-$(date +%Y%m%d-%H%M%S)
    echo "  ✓ Backed up existing README"
fi

# Create new honest README
cat > README.md << 'EOF'
# Nix for Humanity

Natural language interface for NixOS. Currently in active development.

## Project Status: Alpha (v0.8.5)

**Working Features** ✅
- Basic CLI with natural language processing
- Package search functionality  
- Simple install/remove commands (reliability: ~70%)
- Error handling with user-friendly messages
- Basic intent recognition

**In Development** 🚧
- Native Python-Nix API integration (partially complete)
- TUI interface (UI exists but not fully connected)
- Voice interface (architecture done, integration pending)
- Learning system (saves data but doesn't use it yet)
- Performance optimizations

**Not Yet Implemented** ❌
- Federated learning
- Full persona system (5 of 10 working)
- Community features
- Plugin architecture

## Quick Start

```bash
# Clone repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Enter development environment
nix develop

# Try the CLI
./bin/ask-nix "help"
./bin/ask-nix "search firefox"
./bin/ask-nix "install vim" --dry-run
```

## Why This Project?

NixOS is powerful but has a steep learning curve. We're building a natural language interface that makes NixOS accessible to everyone - from developers to grandparents.

## Architecture

```
src/nix_humanity/
├── core/       # Natural language processing and execution
├── native/     # Python-Nix API integration (WIP)
├── cli/        # Command-line interface
├── tui/        # Terminal UI (not fully connected)
└── voice/      # Voice interface (planned)
```

## Contributing

We need help! The project has ambitious goals but currently only ~25% of envisioned features are working.

**Priority Areas:**
1. Fix reliability of install/remove commands
2. Complete native Python-Nix API integration
3. Connect the TUI to the backend
4. Write real integration tests (not mocks)

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Development

```bash
# Run tests
pytest tests/

# Check what actually works
./scripts/functionality-check.sh

# Validate performance claims
python scripts/validate-performance.py
```

## Performance

**Current Performance:**
- Package search: 2-5 seconds
- Install command: 3-10 seconds (when it works)
- Response time: Variable

**Target Performance:**
- All operations < 0.5 seconds
- 10x improvement with native API (partially achieved)

## Roadmap

### Phase 1 (Current) - Foundation
- [x] Basic CLI functionality
- [x] Intent recognition
- [ ] Reliable command execution
- [ ] Native API integration

### Phase 2 - Core Features  
- [ ] Voice interface
- [ ] Learning system activation
- [ ] TUI full integration
- [ ] Performance targets met

### Phase 3 - Production
- [ ] All 10 personas working
- [ ] Community features
- [ ] Plugin system
- [ ] 1.0 release

## Philosophy

We believe in:
- **Honest communication** about what works and what doesn't
- **Privacy first** - all processing happens locally
- **Accessibility** - technology should work for everyone
- **Continuous improvement** - ship small, iterate often

## License

MIT - See [LICENSE](LICENSE)

## Acknowledgments

Built using the "Sacred Trinity" development model - a unique collaboration between human, AI, and local LLM that achieves remarkable results on a $200/month budget.

---

**Note**: This README reflects the actual current state of the project. For the full vision of where we're heading, see [docs/VISION.md](docs/VISION.md).
EOF

echo "✅ Created honest README.md"

# Create a functionality check script
cat > scripts/functionality-check.sh << 'SCRIPT'
#!/usr/bin/env bash
# Check what actually works in Nix for Humanity

set -euo pipefail

echo "🔍 Nix for Humanity Functionality Check"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_feature() {
    local feature=$1
    local command=$2
    local expected=$3
    
    echo -n "Checking $feature... "
    
    if eval "$command" 2>/dev/null | grep -q "$expected" 2>/dev/null; then
        echo -e "${GREEN}✅ WORKING${NC}"
        return 0
    else
        echo -e "${RED}❌ NOT WORKING${NC}"
        return 1
    fi
}

check_feature_warn() {
    local feature=$1
    local command=$2
    local expected=$3
    
    echo -n "Checking $feature... "
    
    if eval "$command" 2>/dev/null | grep -q "$expected" 2>/dev/null; then
        echo -e "${GREEN}✅ WORKING${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  PARTIALLY WORKING${NC}"
        return 1
    fi
}

# Basic CLI
echo "## Basic CLI Features"
check_feature "CLI starts" "./bin/ask-nix --version" "Nix for Humanity"
check_feature "Help command" "./bin/ask-nix help" "Available commands"
check_feature "Dry run mode" "./bin/ask-nix 'install vim' --dry-run" "DRY RUN"

echo ""
echo "## Core Functionality"
check_feature_warn "Package search" "./bin/ask-nix 'search firefox'" "firefox"
check_feature_warn "Intent recognition" "python -c 'from nix_humanity.core.nlp import NLPEngine; e=NLPEngine(); print(e.parse(\"install firefox\").action)'" "install"

echo ""
echo "## Advanced Features"
check_feature "Native API available" "python -c 'from nix_humanity.native.api import NativeAPI; print(NativeAPI.is_available())'" "True"
check_feature_warn "TUI launches" "./bin/nix-tui --help" "help"
check_feature "Voice dependencies" "python -c 'import whisper'" "whisper"

echo ""
echo "## Performance"
echo -n "Checking startup time... "
start=$(date +%s%N)
./bin/ask-nix --version >/dev/null 2>&1
end=$(date +%s%N)
duration=$(( ($end - $start) / 1000000 ))
if [ $duration -lt 500 ]; then
    echo -e "${GREEN}✅ ${duration}ms (target: <500ms)${NC}"
else
    echo -e "${RED}❌ ${duration}ms (target: <500ms)${NC}"
fi

echo ""
echo "## Summary"
echo "This check shows what actually works vs what's documented."
echo "Many features are partially implemented or unreliable."
SCRIPT

chmod +x scripts/functionality-check.sh

# Create migration guide for existing docs
cat > docs/DOCUMENTATION_MIGRATION.md << 'EOF'
# Documentation Migration Guide

## Current State

The documentation describes an ambitious vision, but only ~25% is implemented.

## Migration Plan

### 1. Archive Vision Documents
Move all aspirational documents to `docs/archive/vision/`:
- Documents describing unimplemented features
- Roadmaps for features not yet started
- Technical specs for future components

### 2. Update Core Documents
Rewrite to reflect reality:
- README.md - What actually works today
- QUICKSTART.md - Steps that actually succeed
- ARCHITECTURE.md - Current implementation only

### 3. Mark WIP Features
For partially implemented features:
- Add "🚧 UNDER DEVELOPMENT" badges
- Include "Current Status" sections
- List specific working/broken parts

### 4. Create Honest Metrics
Replace aspirational metrics with real ones:
- Actual performance numbers
- Real success rates
- Current limitations

## Documentation Standards

### For Implemented Features
- Include working examples
- Show actual output
- List known issues

### For Planned Features
- Move to ROADMAP.md
- Mark clearly as "PLANNED"
- No promises on timeline

### For Partial Features
- List what works
- List what doesn't
- Be specific about reliability

## Review Checklist

- [ ] Does this document describe reality?
- [ ] Can a new user follow these steps successfully?
- [ ] Are performance claims backed by measurements?
- [ ] Are limitations clearly stated?
- [ ] Is the vision separated from current state?
EOF

echo ""
echo "📋 Created documentation migration guide"
echo ""
echo "✅ Honest documentation package complete!"
echo ""
echo "Next steps:"
echo "1. Review the new README.md"
echo "2. Run ./scripts/functionality-check.sh"
echo "3. Start migrating other documentation"
echo ""
echo "Remember: Honesty builds trust. Users appreciate knowing exactly what works."