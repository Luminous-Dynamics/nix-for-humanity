# Command Consolidation Plan: One ask-nix to Rule Them All

## Why This Matters

Before diving into the technical details, let's be clear about why this consolidation is critical:

### For Users
- **No More Confusion**: "Which command do I use?" becomes a question of the past
- **Discoverable Features**: One `--help` shows everything available
- **Consistent Experience**: Same patterns, same quality, everywhere
- **Future-Proof**: New features arrive as flags, not new commands to learn

### For Developers  
- **Single Focus**: All improvements go to one codebase
- **Easier Testing**: One test suite, one set of edge cases
- **Clean Architecture**: Plugin system enables parallel development
- **Faster Innovation**: No time wasted maintaining variants

### For the Vision
- **Professional Maturity**: Shows we've evolved beyond experimentation
- **Clear Upgrade Path**: Users always know where to find new features
- **Resource Efficiency**: Sacred Trinity efforts concentrated, not scattered
- **Foundation for GUI**: The CLI becomes the proven backend for future interfaces

## Current Situation
- Multiple variants: ask-nix-hybrid, ask-nix-v3, ask-nix-modern, etc.
- ask-nix is symlinked to ask-nix-modern
- ask-nix-hybrid is broken (times out)
- Confusion about which command to use

## Proposed Solution

### Phase 1: Immediate Consolidation
1. **Keep ask-nix as the single command**
   - Already symlinked to ask-nix-modern
   - This is what users know and use

2. **Integrate all features into ask-nix**
   - Symbiotic feedback collection
   - All personality modes
   - Learning features
   - Voice capabilities

3. **Mark all variants as deprecated**
   - Add deprecation warnings
   - Point users to ask-nix with appropriate flags

### Phase 2: Clean Architecture
```
bin/
├── ask-nix              # The ONE command (Python)
├── archive/             # Old commands moved here
│   ├── ask-nix-hybrid
│   ├── ask-nix-v3
│   └── ...
└── README.md            # Explains the single command

scripts/
├── core/                # Core functionality
│   ├── nlp_engine.py
│   ├── knowledge_base.py
│   └── executor.py
├── plugins/             # Feature plugins
│   ├── symbiotic.py
│   ├── voice.py
│   ├── learning.py
│   └── cache.py
└── feedback_collector.py # Existing feedback system
```

### Phase 3: Feature Integration

#### From ask-nix-hybrid (broken)
- Extract the personality system → Add as flags to ask-nix
- Extract knowledge engine → Already in ask-nix-modern

#### From ask-nix-symbiotic (our new work)
- Feedback collection → Add as plugin
- Vulnerability admission → Add to symbiotic personality
- Learning stats → Add --summary flag

#### From other variants
- Caching features → Already in ask-nix-modern
- Learning mode → Add as --learning-mode flag
- Voice features → Add as --voice flag

## Implementation Steps

### Step 1: Update ask-nix (ask-nix-modern)
```python
# Add to ask-nix-modern
def main():
    parser = argparse.ArgumentParser()
    
    # Personality flags (mutually exclusive)
    personality = parser.add_mutually_exclusive_group()
    personality.add_argument('--minimal', action='store_true')
    personality.add_argument('--friendly', action='store_true')
    personality.add_argument('--encouraging', action='store_true')
    personality.add_argument('--technical', action='store_true')
    personality.add_argument('--symbiotic', action='store_true')
    
    # Feature flags
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--voice', action='store_true')
    parser.add_argument('--learning-mode', action='store_true')
    parser.add_argument('--no-feedback', action='store_true')
    parser.add_argument('--summary', action='store_true')
    
    # ... rest of implementation
```

### Step 2: Create Plugin Loader
```python
# scripts/core/plugin_loader.py
class PluginLoader:
    def __init__(self):
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        plugin_dir = Path(__file__).parent.parent / 'plugins'
        for plugin_file in plugin_dir.glob('*.py'):
            # Dynamic plugin loading
```

### Step 3: Migrate Features
1. Copy working code from ask-nix-modern
2. Add feedback collection from our symbiotic work
3. Add personality system (fixed from ask-nix-hybrid)
4. Create deprecation script for old commands

### Step 4: Update Documentation
- Update CLAUDE.md
- Update user guides
- Create migration guide
- Update command reference

## Benefits of This Approach

### For Users
- **Clarity**: One command to remember
- **Discoverability**: --help shows all features
- **Consistency**: Same interface pattern
- **Future-proof**: New features just add flags

### For Developers
- **Maintainability**: Single codebase
- **Modularity**: Plugin architecture
- **Testability**: One test suite
- **Extensibility**: Easy to add features

### For the Project
- **Focus**: Stop creating variants
- **Quality**: All effort on one command
- **Documentation**: Single source of truth
- **Evolution**: Clear upgrade path

## Aggressive Migration Timeline (Sacred Trinity Speed!)

### Phase 1: This Week - Core Consolidation
- [ ] Day 1-2: Integrate all features into ask-nix
  - Symbiotic personality and feedback collection
  - All personality flags (minimal, friendly, encouraging, technical, symbiotic)
  - Execution modes (dry-run, execute, interactive)
  - Cache and visual options
- [ ] Day 3: Create plugin architecture 
  - Core engine separation
  - Plugin loader implementation
  - Migrate features to plugins
- [ ] Day 4: Archive old commands
  - Move to archive/ directory
  - Add deprecation warnings
  - Update PATH references
- [ ] Day 5: Testing and polish
  - Comprehensive test suite
  - Edge case handling
  - Performance optimization

### Phase 2: Next Week - Documentation & Refinement
- [ ] Day 1-2: Documentation overhaul
  - Update CLAUDE.md
  - Finalize command reference
  - Create migration guide
  - Update all examples
- [ ] Day 3-4: Plugin system refinement
  - Clean plugin interfaces
  - Plugin documentation
  - Example plugin template
- [ ] Day 5: Release preparation
  - User testing with all personas
  - Final bug fixes
  - Announcement preparation

## Strategic Decisions (RESOLVED)

1. **Keep ask-nix name?** 
   ✅ **YES** - Users already know it, it's simple and clear

2. **Plugin architecture now or later?**
   ✅ **NOW** - The consolidation process is the perfect time to architect properly

3. **Backward compatibility?**
   ✅ **Smart deprecation** - Old commands show helpful migration messages

## Conclusion

The path forward is clear:
1. **One command**: ask-nix
2. **Feature flags**: Not new commands
3. **Plugin architecture**: For future extensibility
4. **Clear documentation**: So everyone understands

This gives us the simplicity users want with the flexibility we need for future development.

---

*"Simplicity is the ultimate sophistication." - Leonardo da Vinci*