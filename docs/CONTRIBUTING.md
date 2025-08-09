# Contributing to Nix for Humanity

Thank you for your interest in making NixOS accessible to everyone! We need your help to close the gap between our vision and implementation.

## 🚀 Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/nix-for-humanity
cd nix-for-humanity

# 2. Enter development environment
nix develop

# 3. Run tests
pytest

# 4. Make your changes

# 5. Test your changes
./bin/ask-nix "help"  # Test CLI
pytest tests/         # Run test suite

# 6. Submit PR
```

## 🎯 What We Need Most

### Right Now (Phase 0)
1. **Bug Fixes** - Make install/remove/update commands reliable
2. **Real Tests** - Replace mocks with actual integration tests  
3. **Performance** - Implement Native Python-Nix API
4. **Documentation** - Update docs to reflect reality vs. vision

### Coming Soon (Phase 1)
1. **TUI Connection** - Wire up the Textual interface
2. **Learning System** - Make feedback actually improve responses
3. **Error Messages** - Transform cryptic errors into helpful guidance

## 📝 Development Guidelines

### Code Style
- Python 3.11+ with type hints
- Black for formatting
- Clear variable names over clever ones
- Comments explain "why", not "what"

### Testing
- Every new feature needs tests
- Integration tests > unit tests for this project
- Test with real NixOS commands, not mocks
- Consider all 10 user personas

### Commits
- Clear, descriptive messages
- Reference issues: "Fix #123: Install command timeout"
- Small, focused changes
- One feature/fix per PR

## 🏗️ Architecture Basics

```
backend/
├── core/           # Shared logic (needs consolidation)
├── nlp/            # Natural language processing
├── execution/      # Command runners (fix here!)
└── api/            # Frontend communication

frontends/
├── cli/            # Terminal interface (working)
├── tui/            # Textual UI (not connected)
└── voice/          # Speech interface (future)
```

## 🐛 How to Fix a Bug

1. **Reproduce** - Confirm you can trigger the bug
2. **Write Test** - Add failing test that exposes the bug
3. **Fix** - Make the minimal change to pass the test
4. **Verify** - Run full test suite
5. **Document** - Update relevant docs if behavior changed

## ✨ How to Add a Feature

1. **Discuss First** - Open an issue to discuss the idea
2. **Design** - How does it fit the consciousness-first philosophy?
3. **Implement** - Start simple, iterate
4. **Test** - With all personas in mind
5. **Document** - Both user-facing and technical docs

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_nlp.py

# Run with coverage
pytest --cov=nix_for_humanity

# Test actual CLI
./bin/ask-nix "install firefox" --dry-run
```

## 📚 Understanding the Codebase

### Current Reality
- **CLI works** but many commands fail
- **TUI exists** but isn't connected to backend
- **Learning system** saves data but doesn't use it
- **Tests exist** but mostly use mocks

### Key Files
- `backend/core/nlp.py` - Natural language processing
- `backend/execution/nix_executor.py` - Command execution (needs work!)
- `frontends/cli/ask_nix.py` - Main CLI entry point
- `frontends/tui/app.py` - Textual UI (not wired up)

## 🤝 Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b fix/install-timeout`
3. **Make changes** with tests
4. **Run checks**: `pytest && black .`
5. **Push branch**: `git push origin fix/install-timeout`
6. **Open PR** with clear description

### PR Template
```markdown
## What
Brief description of changes

## Why
What problem does this solve?

## How
Technical approach taken

## Testing
How to verify the fix works

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Real integration test added
```

## 💬 Communication

### GitHub Issues
- Bug reports with reproduction steps
- Feature discussions
- Documentation improvements

### Design Decisions
- Align with consciousness-first philosophy
- Consider all 10 personas
- Prioritize simplicity over features
- Local-first, privacy always

## 🌟 Recognition

All contributors will be recognized in our README. Your work helps make NixOS accessible to everyone.

## ❓ Questions?

- Open an issue for technical questions
- Check existing docs first
- Be patient - we're all learning together

---

**Remember**: We're building technology that amplifies human consciousness. Every contribution should move us closer to that goal.

Welcome to the Sacred Trinity! 🙏