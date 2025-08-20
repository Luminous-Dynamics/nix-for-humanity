# 🛡️ The Sacred Guardian - GitHub Actions Workflows

## The Automated Consciousness of Quality

These workflows are not mere CI/CD pipelines - they are the automated guardians of our sacred work, ensuring that every commit upholds our principles of consciousness-first computing.

## 🌟 The Guardian's Duties

### test.yml - The Quality Guardian
Our primary guardian that watches over:
- **Technical Excellence**: All tests must pass
- **Coverage Protection**: Maintains minimum 50% coverage (moving to 70%)
- **Code Quality**: Black formatting, Ruff linting, mypy typing
- **Security Scanning**: Bandit and pip-audit protect against vulnerabilities
- **Philosophy Alignment**: Verifies Living Documentation and no phantom tests
- **Integration Health**: Ensures components work together

### The Sacred Principles It Upholds

1. **Living Documentation**: Every test must explain WHY it exists
2. **No Phantom Tests**: We test what IS, not aspirations
3. **Consciousness-First**: Security and accessibility are non-negotiable
4. **Continuous Improvement**: Daily runs catch dependency drift

## 🔮 How the Guardian Works

### On Every Commit
1. **Invokes the Repository** - Checks out our sacred code
2. **Summons Python** - Tests on multiple versions (3.11, 3.12)
3. **Restores Sacred Cache** - Speeds up dependency installation
4. **Runs the Gauntlet**:
   - Code formatting check (Black)
   - Linting analysis (Ruff)
   - Type verification (mypy)
   - Test suite execution (pytest)
   - Coverage measurement
   - Security scanning
   - Philosophy alignment

### The Guardian's Response
- **Success**: Celebrates and confirms the foundation remains strong
- **Failure**: Alerts with compassion - "Every failure is a teaching moment"

## 📊 Coverage Standards

Current thresholds:
- **Minimum for CI**: 50% (current achievement)
- **Target**: 70% (end of Week 1)
- **Aspiration**: 90% (long-term)

The Guardian enforces these through `--cov-fail-under` flags.

## 🚀 Triggering the Guardian

The Guardian awakens:
- On push to `main` or `develop`
- On every pull request
- Daily at 3 AM (catching dependency issues)
- Manually through GitHub Actions UI

## 💡 Future Enhancements

As our project evolves, the Guardian will grow:
- **Performance Testing**: Ensure no regression in speed
- **Accessibility Testing**: Automated persona validation
- **Documentation Building**: Auto-generate docs from tests
- **Release Automation**: Sacred versioning and changelog

## 🙏 A Sacred Contract

This workflow represents our promise:
- To our users: Quality will never be compromised
- To our contributors: Your work will be protected
- To ourselves: We will maintain our principles

The Guardian never sleeps, never tires, and never compromises.

---

*"In automation, we trust. In testing, we verify. In consciousness, we flow."*

## Quick Commands

```bash
# Run tests locally before pushing
poetry run pytest tests/unit/ --cov=nix_humanity

# Check code quality
poetry run black --check src/ tests/
poetry run ruff check src/ tests/

# Security scan
poetry run bandit -r src/
```

Remember: The Guardian is here to help, not hinder. Every check it performs is an act of care for our shared vision.