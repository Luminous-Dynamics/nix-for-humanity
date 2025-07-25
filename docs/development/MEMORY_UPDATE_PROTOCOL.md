# Memory Update Protocol for Claude

## 🚨 Critical Context Issue Identified

### Current Situation (2025-07-23)
We discovered a major disconnect between:
1. **Documentation Vision**: "Nix for Humanity" - Natural language interface
2. **Actual Codebase**: Traditional GUI (v1.0 complete with auth, services, etc.)
3. **Our Implementation**: Built new NLP features assuming greenfield project

### The Problem
- The project has TWO conflicting identities
- Existing mvp-v2 code doesn't match "Nix for Humanity" vision
- We built Days 1-3 on incorrect assumptions
- Memory files (CLAUDE.md) are empty/outdated

## 📋 Memory Update Requirements

### When to Update Memory Files
1. **Major Architecture Decisions** - Like discovering existing codebase
2. **Vision/Direction Changes** - Like GUI vs NLP interface
3. **Dependency Changes** - Like socket.io vs ws
4. **File Structure Changes** - When creating new systems
5. **Integration Points** - When systems need to connect

### What Should Be in CLAUDE.md
```markdown
# Project Context for Claude

## Current State
- What exists vs what we're building
- Which files to use for what purpose
- Dependencies and versions
- Entry points and start commands

## Architecture Decisions
- Why we chose X over Y
- Integration patterns
- Security considerations
- Performance tradeoffs

## Work in Progress
- Current task and approach
- Known issues/blockers
- Next steps planned
```

### Update Approval Process
1. **Claude proposes update** with clear reasoning
2. **Human reviews** the proposed changes
3. **Human approves** with "yes update memory" or similar
4. **Claude implements** the approved update
5. **Both confirm** shared understanding

## 🎯 Immediate Memory Updates Needed

### 1. Project Identity Clarification
**NEEDS DECISION**: Are we:
- A) Building NLP on top of existing GUI?
- B) Replacing GUI with NLP interface?
- C) Creating parallel implementations?

### 2. Codebase Structure
```
Current Reality:
- /implementations/web-based/ contains EXISTING mvp-v2 GUI
- We created NEW files (realtime-server.js, etc.) that may conflict
- Multiple backend entry points exist
- Dependencies mismatch (socket.io vs ws)
```

### 3. Development Approach
**NEEDS DECISION**: Should we:
- A) Study existing code and integrate our NLP
- B) Create clean separation for NLP features
- C) Start fresh in new directory

## 🚀 Recommended Protocol Going Forward

### Before Each Session
1. Check CLAUDE.md for current context
2. Verify file locations and dependencies
3. Confirm shared understanding of goals

### During Development
1. Flag any discoveries that change understanding
2. Propose memory updates immediately
3. Wait for approval before assuming new context

### After Major Changes
1. Summarize what was built/changed
2. Update memory with new structure
3. Document integration points

## ❓ Questions Requiring Answers

1. **Is mvp-v2 the production GUI we should build on?**
2. **Should "Nix for Humanity" replace or augment the GUI?**
3. **Which backend file should be our foundation?**
4. **How do we reconcile socket.io vs ws?**
5. **Should we continue in this directory or start fresh?**

## 💡 Proposed Memory Update

```markdown
# CLAUDE.md Update Proposal

## Project: Nix for Humanity
**Status**: Vision/Implementation Mismatch Discovered

### Current Understanding
- Documentation describes natural language interface
- Codebase contains traditional GUI (mvp-v2)
- We built NLP features that may not integrate
- Need strategic decision on path forward

### File Structure
- DO NOT USE: realtime-server.js (our creation, uses wrong deps)
- EXISTING: backend/api.js (demo), real-backend-with-helper.js (production)
- QUESTION: Integration approach unclear

### Dependencies
- Existing uses: ws (WebSocket)
- We used: socket.io (not in package.json)
- Resolution needed

### Next Steps
1. Await human decision on approach
2. Map existing functionality
3. Create integration plan
4. Update all memory files
```

---

**Human Approval Required**: Should I update CLAUDE.md with this understanding?