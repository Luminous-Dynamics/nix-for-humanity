# Version 0.1 - Achievable MVP (4 Weeks)

*What we can actually build with $200/month in one month*

## Core Functionality

### Natural Language to Nix Commands
- Basic pattern matching for 10-15 common commands
- Simple web interface (already started)
- No AI, no consciousness, no learning
- Just working command translation

### Supported Commands
```
"install firefox" → nix-env -iA nixos.firefox
"update system" → sudo nixos-rebuild switch
"search python" → nix search nixpkgs python
"list installed" → nix-env -q
"remove package X" → nix-env -e X
```

### Technical Stack
- TypeScript for NLP patterns (existing)
- Express.js web server
- Basic HTML/CSS interface
- Local execution only

### Success Metrics
- 10 commands working reliably
- <2 second response time
- Basic error handling
- Runs on NixOS

### What We DON'T Include
- ❌ Voice input
- ❌ Learning/adaptation
- ❌ AI consciousness
- ❌ Desktop app (Tauri)
- ❌ Multi-user support
- ❌ Fancy UI animations

## Development Timeline

### Week 1: Core Pattern Engine
- Set up TypeScript NLP patterns
- Implement command builder
- Basic safety validation
- Unit tests

### Week 2: Web Interface
- Simple HTML interface
- Command input/output
- Error display
- Basic styling

### Week 3: NixOS Integration
- Secure command execution
- Permission handling
- Testing on real NixOS
- Bug fixes

### Week 4: Polish & Package
- Documentation
- Installation script
- Basic examples
- GitHub release

## Budget Allocation
- Claude Code Max: $200
- Developer time: 20 hrs/week
- No other costs

## Deliverables
1. Working web interface for natural language → Nix commands
2. Support for 10-15 most common operations
3. Basic documentation
4. Installation instructions
5. GitHub repository with clean code

## Reality Check
✅ This is achievable in 4 weeks
✅ Solves a real problem
✅ Foundation for future versions
✅ Honest about capabilities
✅ Actually helps users

---

*"Start small, ship something real, build trust through working code."*