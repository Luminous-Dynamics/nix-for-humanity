# Contributing to Nix for Humanity

Help us build two hero capabilities that actually work!

## 🎯 Current Focus: v1.0 in 6 Weeks

We're laser-focused on two features:
1. **Native Python-Nix API** - Lightning-fast operations
2. **Smart Learning Loop** - Genuine helpfulness

Everything else is deferred. See [FOCUSED_ROADMAP.md](FOCUSED_ROADMAP.md) for details.

## 🚀 Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/nix-for-humanity
cd nix-for-humanity

# Enter development environment
nix develop

# Run tests
pytest tests/integration/  # Real tests, not mocks!

# Test your changes
./bin/ask-nix "help"
```

## 🎯 What We Need Right Now

### Week 1 (Jan 13-19): Cleanup Help Needed
- [ ] Help remove unused code (see [CLEANUP_PLAN.md](CLEANUP_PLAN.md))
- [ ] Consolidate scattered Python files
- [ ] Simplify documentation
- [ ] Update tests to match reality

### Week 2-3: Native API Development
- [ ] Complete nixos-rebuild Python integration
- [ ] Add progress indicators
- [ ] Handle edge cases
- [ ] Write integration tests

### Week 4-5: Learning Loop Implementation
- [ ] Pattern tracking system
- [ ] Suggestion engine
- [ ] User preference learning
- [ ] Feedback integration

## 📝 Code Guidelines

### Simplicity Rules
```python
# ❌ DON'T: Over-engineer
class AbstractCommandExecutorFactoryProvider:
    def create_executor_instance_with_context(self, context_params):
        # 50 lines of abstraction

# ✅ DO: Keep it simple
def execute_nix_command(command, package):
    return nix_api.run(command, package)
```

### Testing Reality
```python
# ❌ DON'T: Mock everything
def test_install():
    mock_nix = MagicMock()
    mock_nix.install.return_value = "success"
    
# ✅ DO: Test real commands
def test_install_real():
    result = nix_api.install("hello")  # Real package
    assert result.success
    assert shutil.which("hello")  # Actually installed
```

### Document Truth
```markdown
❌ DON'T: Document aspirations
"The AI learns from your behavior and anticipates needs"

✅ DO: Document reality
"The system tracks successful commands and suggests similar ones"
```

## 🚫 What NOT to Submit

During the v1.0 sprint, we will **NOT** accept PRs for:
- Voice interfaces
- Complex AI features
- New personas beyond 3 styles
- Distributed systems
- Research implementations
- Feature additions beyond the two hero capabilities

Save these ideas for post-v1.0!

## ✅ PR Checklist

Before submitting:
- [ ] Advances one of two hero capabilities
- [ ] Includes real integration tests
- [ ] Simplifies rather than complicates
- [ ] Documentation reflects reality
- [ ] No new dependencies unless essential
- [ ] Works with actual Nix commands

## 🧪 Testing Requirements

### Integration Tests Required
```python
# Every PR must include tests like:
def test_native_api_performance():
    start = time.time()
    nix_api.search("firefox")
    assert time.time() - start < 0.5  # Performance requirement

def test_learning_improves():
    # Install similar packages
    execute_command("install python311")
    execute_command("install python311Packages.pip")
    
    # Check suggestions improve
    suggestions = get_suggestions("install python")
    assert "python311Packages" in suggestions[0]
```

## 🎨 Code Style

- Python 3.11+ with type hints
- Black formatting (run `black .`)
- Clear names: `install_package()` not `ip()`
- Comments explain why, not what
- Maximum function length: 20 lines

## 📋 How to Submit

1. **Check Focus**: Does this help our two hero capabilities?
2. **Write Tests**: Real integration tests, not mocks
3. **Keep Simple**: Can you make it simpler?
4. **Update Docs**: Only if functionality changed
5. **Open PR**: With clear description of impact

### PR Template
```markdown
## Impact on Hero Capabilities
- [ ] Improves Native API performance
- [ ] Enhances Learning Loop
- [ ] Fixes critical bug
- [ ] Improves test coverage

## What Changed
Brief description

## Performance Impact
Before: X seconds
After: Y seconds

## Test Coverage
- [ ] Integration tests added
- [ ] All tests pass
```

## 💬 Communication

### GitHub Issues
- Bug reports with reproduction steps
- Performance improvements
- Learning enhancements

### What We're NOT Discussing (Yet)
- Voice interfaces
- GUI designs  
- Advanced AI features
- Distributed architectures
- New feature requests

## 🏃 Development Workflow

```bash
# 1. Create feature branch
git checkout -b improve-native-api-performance

# 2. Make focused changes
# Edit only files related to hero capabilities

# 3. Test thoroughly
pytest tests/integration/test_performance.py -v

# 4. Ensure code quality
black .
mypy backend/core/

# 5. Submit PR
git push origin improve-native-api-performance
```

## 🎯 Success Metrics

Your contribution is successful when:
1. It makes one hero capability better
2. It includes real tests
3. It simplifies rather than complicates
4. It works reliably
5. It's merged and users benefit

## 🙏 Thank You!

Every contribution helps make NixOS accessible to more people. By focusing on two capabilities and doing them well, we're building a foundation for the future.

**Questions?** Open an issue or ask in discussions.

---

*Remember: We're saying no to 100 good ideas to say yes to 2 great ones. Help us make those 2 exceptional!*