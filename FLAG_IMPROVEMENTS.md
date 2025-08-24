# 🚩 Flag Improvements for Natural Language NixOS

## Current State
We have basic voice flags but missing essential UX flags for making the interface truly helpful.

## Proposed Improvements

### 1. 🎯 Core UX Flags (Immediate Priority)

```bash
# Socratic Mode - Ask clarifying questions
ask-nix --ask "install browser"
# Response: "What kind of browser would you prefer? Fast, private, or feature-rich?"

# Dry Run - Preview without executing
ask-nix --dry-run "update system"
ask-nix -n "install firefox"  # short form

# Yes Mode - Skip all confirmations
ask-nix --yes "install firefox"
ask-nix -y "remove package"

# Quiet Mode - Minimal output
ask-nix --quiet "search editor"
ask-nix -q "list installed"

# Verbose Mode - Detailed output
ask-nix --verbose "install package"
ask-nix -vv "debug issue"  # extra verbose

# Execute Mode - Actually run commands (explicit)
ask-nix --execute "install firefox"
ask-nix -e "update system"
```

### 2. 🤖 AI/Learning Flags

```bash
# Use local Ollama for AI responses
ask-nix --ai "why isn't wifi working?"
ask-nix --ollama "explain this error"

# Use specific persona
ask-nix --persona grandma "install browser"
ask-nix --persona developer "setup python"

# Learn from this interaction
ask-nix --learn "install firefox as brave"
# Remembers: user prefers Brave when asking for Firefox

# Don't learn from this session
ask-nix --no-learn "experiment with packages"
```

### 3. 🎨 Output Format Flags

```bash
# JSON output for scripting
ask-nix --json "list installed"

# Simple text output
ask-nix --plain "search editors"

# Markdown output
ask-nix --markdown "explain configuration"

# No emoji/colors
ask-nix --no-color "install package"
ask-nix --boring "list packages"
```

### 4. 🔍 Search & Discovery Flags

```bash
# Search with different strategies
ask-nix --fuzzy "search txt edtr"  # fuzzy matching
ask-nix --exact "search firefox"   # exact match only
ask-nix --description "search 'edit text files'"  # search descriptions

# Limit results
ask-nix --limit 5 "search editor"
ask-nix --top "search browser"  # top results only
```

### 5. 🛡️ Safety & Control Flags

```bash
# Safety levels
ask-nix --safe "remove packages"  # extra confirmations
ask-nix --unsafe "expert mode"    # fewer guardrails

# Rollback protection
ask-nix --snapshot "update system"  # create snapshot first
ask-nix --no-rollback "install test"  # skip rollback setup

# Timeout control
ask-nix --timeout 60 "search all packages"
ask-nix --patient "complex operation"  # no timeout
```

### 6. 📊 Debug & Diagnostic Flags

```bash
# Debug output
ask-nix --debug "failing command"
ask-nix --trace "complex issue"

# Show what would be executed
ask-nix --show-command "install firefox"
ask-nix --explain "update system"

# System diagnosis
ask-nix --diagnose "system health"
ask-nix --doctor "fix issues"
```

### 7. 🎭 Personality & Style Flags

```bash
# Response styles
ask-nix --friendly "help me"
ask-nix --professional "install software"
ask-nix --minimal "just work"
ask-nix --explain-everything "install package"

# Language preferences
ask-nix --simple "explain nix"
ask-nix --technical "detailed explanation"
ask-nix --eli5 "explain like I'm 5"
```

## Implementation Priority

### Phase 1: Essential (NOW)
- `--dry-run/-n` - Preview commands
- `--yes/-y` - Skip confirmations  
- `--execute/-e` - Explicit execution
- `--quiet/-q` - Minimal output
- `--verbose/-v` - Detailed output

### Phase 2: Socratic (Next Week)
- `--ask` - Ask clarifying questions
- `--persona` - Use specific personas
- `--explain` - Explain what will happen

### Phase 3: AI Integration (With Ollama)
- `--ai/--ollama` - Use AI for responses
- `--learn` - Learn from interactions
- `--no-learn` - Don't save preferences

### Phase 4: Advanced (Future)
- `--json/--plain/--markdown` - Output formats
- `--fuzzy/--exact` - Search modes
- `--diagnose/--doctor` - System health

## Usage Examples

### Beginner Friendly
```bash
# Simple, safe, asks questions
ask-nix --ask --safe "help me install a browser"
```

### Power User
```bash
# Fast, no confirmations, quiet
ask-nix -yqe "install firefox vim neovim"
```

### Debugging
```bash
# Verbose, debug, explain
ask-nix -vv --debug --explain "why is this failing"
```

### Scripting
```bash
# JSON output, no interaction, execute
ask-nix --json --yes --execute "list installed" | jq '.packages[]'
```

## The Socratic Principle

The flags should encourage discovery, not prescription:
- `--ask` doesn't tell, it asks what you want
- `--explain` helps you understand, not just execute
- `--learn` adapts to you, not forces you to adapt
- `--persona` meets you where you are

## Environment Variables (Alternative to Flags)

```bash
export LUMINOUS_DRY_RUN=true
export LUMINOUS_SKIP_CONFIRM=true
export LUMINOUS_PERSONA=grandma
export LUMINOUS_AI_ENABLED=true
export LUMINOUS_OUTPUT_FORMAT=json
```

This allows persistent preferences without repeating flags.