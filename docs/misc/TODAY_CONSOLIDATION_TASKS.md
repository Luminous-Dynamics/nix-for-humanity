# TODAY: Starting the ask-nix Consolidation

## Morning Tasks (Core Integration)

### 1. Verify Current State
```bash
# What actually works?
./ask-nix "install firefox"  # Test basic functionality
./ask-nix --help            # Document current flags
```

### 2. Add Symbiotic Features to ask-nix ✅ COMPLETE!
- [x] Copy feedback_collector.py integration from our work
- [x] Add --symbiotic personality flag
- [x] Add --no-feedback flag
- [x] Add --summary flag for learning stats

### 3. Create Plugin Structure
```
scripts/
├── core/
│   ├── __init__.py
│   ├── nlp_engine.py      # Extract from ask-nix-modern
│   ├── knowledge_base.py   # Extract from nix-knowledge-engine.py
│   └── executor.py         # Command execution logic
└── plugins/
    ├── __init__.py
    ├── symbiotic.py        # Feedback collection
    ├── personality.py      # All personality modes
    └── cache.py            # Smart caching logic
```

## Afternoon Tasks (Cleanup)

### 4. Archive Old Commands
```bash
mkdir -p archive
# Move broken/duplicate commands
mv ask-nix-hybrid ask-nix-v3 ask-nix-adaptive archive/
mv ask-nix-ai-* ask-nix-learning ask-nix-python archive/

# Add deprecation script
cat > archive/deprecation-notice.sh << 'EOF'
#!/bin/bash
echo "⚠️  This command is deprecated!"
echo "Please use 'ask-nix' instead:"
echo ""
echo "  ask-nix $@"
echo ""
echo "See 'ask-nix --help' for all available options."
EOF

# Symlink old commands to deprecation notice
for cmd in archive/ask-nix-*; do
  ln -sf deprecation-notice.sh $(basename $cmd)
done
```

### 5. Test Everything
- [ ] Run ask-nix with each personality
- [ ] Test feedback collection
- [ ] Verify execution modes
- [ ] Check all flags work

### 6. Update Critical Docs
- [ ] Update WORKING_COMMANDS.md
- [ ] Add note to CLAUDE.md about consolidation
- [ ] Update bin/README.md

## Evening Tasks (If Time)

### 7. Start Plugin Extraction
- [ ] Create plugin base class
- [ ] Move personality logic to plugin
- [ ] Move feedback logic to plugin
- [ ] Test plugin loading

## Success Criteria for Today

✅ ask-nix has all features from our symbiotic work
✅ Old commands are archived with clear deprecation
✅ Basic plugin structure is created
✅ All tests pass
✅ Documentation is updated

## Tomorrow's Focus

- Complete plugin architecture
- Create comprehensive test suite
- Polish the user experience
- Prepare for next week's headless extraction

---

*"A journey of a thousand miles begins with a single step. Today, we take that step."*