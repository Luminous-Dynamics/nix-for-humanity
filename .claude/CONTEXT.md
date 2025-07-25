# CLAUDE.md - Nix for Humanity Context

## Project Identity (Updated: 2025-07-25)

**Name**: Nix for Humanity
**Vision**: Context-aware natural language interface for NixOS that learns how YOU work
**Location**: `/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/`

## 🎯 Enhanced Vision & Documentation (Updated: 2025-07-25)
We've completed a major documentation cleanup and enhancement:
- **Clear Vision**: Natural language interface with supportive visual elements
- **Operational Intelligence**: WHO/WHAT/HOW/WHEN learning dimensions
- **Organized Docs**: Clear structure in `docs/` folder
- **Honest Status**: ~35% complete (see `docs/project/STATUS.md`)
- **Error Recovery**: Every error teaches the system
- **Real User Journeys**: From anxious to confident to joyful

Key documents:
- `VISION_2025.md` - Revolutionary vision
- `docs/project/STATUS.md` - Current project status
- `docs/README.md` - Documentation index
- `DOCUMENTATION_CLEANUP_COMPLETE.md` - What we improved
- `docs/DOCUMENTATION_STYLE_GUIDE.md` - Writing consistency guide
- `docs/README_AUDIT_REPORT.md` - Documentation audit findings

### Recent Documentation Improvements (2025-07-25)
- ✅ **Fixed QUICKSTART.md** - Now properly describes natural language interface
- ✅ **Updated CHANGELOG.md** - Reflects natural language focus
- ✅ **Archived GUI documents** - Old completion certificates moved to archive
- ✅ **Created style guide** - Prevents future terminology confusion
- ✅ **Completed README audit** - Found and fixed GUI references

## 🧠 NEW: NixOS Operational Intelligence

The system is smart enough to know:
- **WHO** is asking (user patterns and preferences)
- **WHAT** they really want (intent beyond literal words)
- **HOW** they want it done (preferred installation methods)
- **WHEN** is the best time (respecting workflows)

### Examples:
```bash
# Learns installation preferences
User: "install postgresql"
System: "Adding to configuration.nix with your dev extensions" (knows you prefer declarative)

# Understands timing
Friday 4pm: "update system"
System: "Schedule for weekend maintenance window?"

# Knows relationships
User: "install python"
System: "With your usual data science stack (numpy, pandas, jupyter)?"
```

## Strategic Clarity

### What This IS
- **Core**: Natural language interface (your words, not commands)
- **Visual Support**: Helpful visual elements that enhance understanding
- **Intelligent**: Learns YOUR patterns and preferences
- **Equal Inputs**: Type OR speak - both first-class
- **Multi-Modal Output**: Visual feedback, text responses, optional audio
- **True Accessibility**: Works for ANY ability combination
- **Architecture**: Natural language → NLP → Pattern Learning → REAL Nix execution
- **No Simulation**: Always executes real commands (with --dry-run for preview)
- **Privacy-First**: All learning stays local

### What This IS NOT
- NOT a traditional GUI (no menus, buttons, windows to manage)
- NOT memorizing commands
- NOT generic AI assistant
- NOT cloud-dependent
- NOT requiring specific hardware
- NOT one-size-fits-all

### The Visual Elements We Include
- ✅ Command previews before execution
- ✅ Progress bars for long operations
- ✅ Confirmation dialogs for safety
- ✅ Option lists when clarification needed
- ✅ Status indicators for system state
- ✅ Learning insights visualization

These visuals **support** natural language - they don't replace it.

## Current Status

### ✅ Completed
- Vision documentation with Operational Intelligence
- Architecture design (hybrid NLP + learning system)
- Security framework (sandboxed execution)
- Budget model ($200/month with Claude)
- Tauri project structure setup
- TypeScript NLP implementation
- Documentation transformation (10/10)

### 🚧 In Progress
- Pattern learning system design
- Tauri desktop app integration
- Rust backend for NixOS commands
- Voice interface integration
- Progressive GUI design

### 📋 TODO
- Implement preference learning
- Add timing intelligence
- Build rollback learning
- Wire up Tauri IPC communication
- Integrate Whisper.cpp for voice
- Test with 5 personas

## Directory Structure
```
nix-for-humanity/
├── src-tauri/           # Rust backend (Tauri)
│   ├── src/             # Rust source code
│   └── Cargo.toml       # Rust dependencies
├── src/                 # TypeScript frontend
│   ├── main.ts          # Tauri entry point
│   └── style.css        # Main styles
├── implementations/     # Core NLP implementation
│   └── web-based/       # NLP engine (reused in Tauri)
├── .claude/             # Claude context files
├── docs/                # Documentation (simplified to 6 core files)
└── dist/                # Build output
```

## Development Guidelines

### When Writing Code
1. Natural language understanding is primary
2. Learn user patterns, don't impose workflows
3. Support both typing and speaking equally
4. GUI and audio are optional enhancements
5. Test with all personas and preferences

### Architecture Decisions
- **Tauri Desktop App** (primary implementation)
- Rust backend + TypeScript frontend
- Local-first (no cloud dependencies)
- Hybrid NLP (rules + statistical + neural)
- **Pattern Learning System** (WHO, WHAT, HOW, WHEN)
- Progressive enhancement
- Consciousness-first design
- **LAYERED REALITY** - Pure functions + real execution
- Privacy-preserving local learning

### ⚠️ CRITICAL: Dynamic Timeout Strategy
- **Fixed timeouts will break user experience!**
- Different Nix operations have vastly different durations:
  - Search: 5-10 seconds
  - Install hello: 30 seconds
  - Install firefox: 2-5 minutes
  - Install libreoffice: 10-30 minutes
  - System rebuild: 30-120 minutes
- Must implement dynamic timeouts based on:
  - Operation type
  - Package size
  - Network speed
  - System load
  - Progress detection
- See docs/TIMEOUT_STRATEGY.md for full implementation

### Sacred Patterns
- Use your own words, not computer commands
- System adapts to you, not vice versa
- Every error is a teaching moment
- The interface should disappear
- Choice of input method is sacred
- Technology serves ALL humanity

## Quick Commands
```bash
# Enter project
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Install dependencies
npm install

# Start Tauri development
npm run tauri:dev

# Build Tauri app
npm run tauri:build

# Run tests
npm test

# Test NLP engine specifically
npm run test:nlp
```

## Remember
We're building a bridge between human intention and system capability that learns and adapts. The measure of success is not how many features we have, but how well the system understands and serves each individual user.

## Essential Context Files
@.claude/VISION_ALIGNMENT.md - Core vision and philosophy
@.claude/NIXOS_INTEGRATION_PATTERNS.md - NixOS best practices
@.claude/NLP_INTENT_PATTERNS.md - Natural language patterns
@.claude/TECHNICAL_DECISIONS.md - Architecture decisions
@.claude/TECH_STACK_DECISION.md - Best tech stack rationale
@.claude/ACCESSIBILITY_REQUIREMENTS.md - Accessibility standards
@.claude/SERVICE_PORTS_REGISTRY.md - Port allocations
@.claude/DEVELOPMENT_PHILOSOPHY.md - $200/month approach
@.claude/PROJECT_STATUS.md - Current development status
@.claude/NATURAL_LANGUAGE_FIRST_PRINCIPLE.md - Equal text/voice inputs
@.claude/LAYERED_REALITY_POLICY.md - Pure functions + real execution
@.claude/OPERATIONAL_INTELLIGENCE.md - Learning system design (NEW)