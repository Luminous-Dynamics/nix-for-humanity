# Contributing to Nix for Humanity v1.0

*Focused contribution guide for building the Foundation of Trust*

## 🎯 v1.0 Mission

Make these 5 things work perfectly:
1. `ask-nix "install [package]"`
2. `ask-nix "remove [package]"`  
3. `ask-nix "search [package]"`
4. `ask-nix "update system"`
5. `ask-nix "help [topic]"`

That's it. No new features until these are rock-solid.

## 🚨 What We Need Most

### 1. Fix Command Reliability (Critical)
```bash
# This should work 95%+ of the time
ask-nix "install firefox"

# Currently fails ~40% with timeout or parse errors
# See: src/executor/nix_executor.py
```

### 2. Improve Error Messages (High)
```bash
# Current: "Error: Command failed with exit code 1"
# Goal: "Firefox is already installed. Did you mean to update it?"
```

### 3. Speed Up Response Time (High)
```bash
# Current: 2-5 seconds
# Goal: <2 seconds consistently
# Focus: src/nlp/basic_nlp.py optimization
```

### 4. Write Real Tests (Critical)
```bash
# We need integration tests that actually run nix commands
# Not mocks that pretend everything works
# See: tests/v1.0/integration/
```

## 🛠️ Development Setup

```bash
# 1. Clone and enter environment
git clone https://github.com/YOU/nix-for-humanity
cd nix-for-humanity
nix develop

# 2. Focus on v1.0 code only
cd src/  # This is where v1.0 lives

# 3. Run v1.0 tests
pytest tests/v1.0/ -v

# 4. Test your changes
./bin/ask-nix "install firefox" --dry-run
```

## 📁 v1.0 Code Structure

```
src/                    # v1.0 code ONLY
├── cli/               # Command-line interface
│   └── ask_nix.py    # Main entry point
├── nlp/               # Natural language processing
│   └── basic_nlp.py  # Simple, reliable NLP
├── executor/          # Command execution
│   └── nix_executor.py # Needs reliability fixes!
├── feedback/          # User feedback collection
│   └── collector.py  # Simple feedback system
└── utils/            # Shared utilities
    └── errors.py     # Error message improvements needed
```

**DO NOT TOUCH**: `future/` directory - that's for v1.1+

## ✅ v1.0 Pull Request Checklist

Before submitting a PR:

- [ ] Fixes a v1.0 issue (reliability, speed, errors)
- [ ] Includes integration tests (not mocks)
- [ ] No new features added
- [ ] Error messages are helpful
- [ ] Response time <2 seconds
- [ ] Works with all 3 personas (Beginner, Intermediate, Expert)

## 🧪 Testing for v1.0

### Integration Tests (Most Important)
```python
# tests/v1.0/integration/test_real_commands.py
def test_install_actually_works():
    """Test that install REALLY installs packages"""
    result = run_ask_nix("install hello", dry_run=True)
    assert result.success
    assert "would install hello" in result.output
```

### Performance Tests
```python
# tests/v1.0/performance/test_response_time.py
def test_response_under_2_seconds():
    """Ensure quick responses"""
    start = time.time()
    run_ask_nix("search python")
    assert time.time() - start < 2.0
```

### Error Message Tests
```python
# tests/v1.0/ux/test_error_messages.py
def test_helpful_error_messages():
    """Errors should guide users"""
    result = run_ask_nix("install nonexistent-package")
    assert "did you mean" in result.error.lower()
    assert "try searching" in result.error.lower()
```

## 🎯 v1.0 Success Metrics

Your PR helps v1.0 if it improves these numbers:

| Metric | Current | Target | How to Test |
|--------|---------|---------|-------------|
| Install Success | ~60% | 95% | `pytest tests/v1.0/integration/test_install.py` |
| Search Success | ~80% | 95% | `pytest tests/v1.0/integration/test_search.py` |
| Response Time | 2-5s | <2s | `pytest tests/v1.0/performance/` |
| Error Clarity | 3/10 | 8/10 | `pytest tests/v1.0/ux/test_errors.py` |
| Crash Rate | ~5% | 0% | `pytest tests/v1.0/stability/` |

## 🐛 v1.0 Bug Priorities

### P0 - Critical (Fix Immediately)
- Install command timeouts
- Remove command not implemented
- Crashes on special characters

### P1 - High (Fix This Week)
- Slow response times
- Cryptic error messages
- Search returning wrong results

### P2 - Medium (Fix This Month)
- Feedback not being saved properly
- Help command incomplete
- Persona switching issues

## 💡 v1.0 Code Standards

### Simplicity First
```python
# ❌ Clever but fragile
result = functools.reduce(operator.or_, 
    map(lambda x: x.process(), 
        filter(None, intents)))

# ✅ Simple and reliable
for intent in intents:
    if intent:
        result = intent.process()
        if result:
            break
```

### Helpful Errors
```python
# ❌ Developer-focused
raise ValueError("Invalid package specification")

# ✅ User-focused
raise UserError(
    "I couldn't understand that package name. "
    "Try something like 'firefox' or 'python3'."
)
```

### Fast Responses
```python
# ❌ Load everything upfront
def __init__(self):
    self.load_all_packages()  # 10 seconds!

# ✅ Lazy loading
def __init__(self):
    self._packages = None
    
@property
def packages(self):
    if self._packages is None:
        self._packages = self.load_packages()
    return self._packages
```

## 🚫 What NOT to Work On

These are preserved for future versions:

- ❌ Voice interface (v1.2)
- ❌ TUI with Textual (v1.1)
- ❌ AI learning features (v1.2)
- ❌ Advanced personas (v1.1)
- ❌ Native Python-Nix API (v1.1)

If you're excited about these, document your ideas in `future/` but don't implement yet.

## 📣 Communication

### For v1.0 Issues
Label: `v1.0-reliability`
```markdown
**What's broken**: Install fails with timeout
**How to reproduce**: `ask-nix "install firefox"`
**Expected**: Package installs
**Actual**: Timeout after 30 seconds
**Impact**: Users can't install packages
```

### For Future Ideas
Label: `future-feature`
```markdown
**Version**: v1.2
**Feature**: Voice interface
**Rationale**: Accessibility for vision-impaired users
**Preserved in**: `future/v1.2/voice/PROPOSAL.md`
```

## 🎉 Recognition

Contributors focusing on v1.0 reliability will be recognized as:
- **Foundation Builders** - Made v1.0 rock-solid
- **Trust Engineers** - Fixed critical reliability
- **Error Whisperers** - Transformed cryptic messages

Your name in the v1.0 release notes matters more than feature quantity.

## 🙏 The v1.0 Spirit

We're not building the most feature-rich NixOS tool. We're building the most reliable one. Every user who tries v1.0 should think:

> "It doesn't do everything, but what it does, it does perfectly."

That trust becomes the foundation for all future innovations.

---

**Focus**: Reliability over features  
**Goal**: 95% success rate on core commands  
**Timeline**: Now until Q1 2025  
**Motto**: "Foundation of Trust"

*Thank you for helping build something solid, reliable, and trustworthy.* 🙏