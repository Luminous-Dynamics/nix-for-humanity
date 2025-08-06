# 💻 Development Guide

*Building Nix for Humanity with consciousness and code*

## Overview

This section contains everything you need to contribute to Nix for Humanity. We follow a unique Sacred Trinity development model that combines human intuition, AI assistance, and local expertise.

## Development Documents

### Getting Started
1. **[Development Guide](./01-DEVELOPMENT-GUIDE.md)** - Complete setup and workflow
2. **[Sacred Trinity Workflow](./02-SACRED-TRINITY-WORKFLOW.md)** - Our unique collaboration model
3. **[Quick Start](./03-QUICK-START.md)** - Get coding in 5 minutes

### Standards & Practices
4. **[Code Standards](./04-CODE-STANDARDS.md)** - Style guide and best practices
5. **[Testing Strategy](./05-TESTING-STRATEGY.md)** - How we ensure quality
6. **[Documentation Standards](./06-DOCUMENTATION-STANDARDS.md)** - Writing clear docs

### Contributing
7. **[Contributing Guide](./07-CONTRIBUTING.md)** - How to submit changes
8. **[Development Philosophy](./08-DEVELOPMENT-PHILOSOPHY.md)** - The sacred pause and conscious coding

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Enable native performance
export NIX_HUMANITY_PYTHON_BACKEND=true

# Run tests
pytest tests/

# Start developing
python3 -m src.tui.app  # For TUI work
./bin/ask-nix --help    # For CLI work
```

## The Sacred Trinity Model

### Human (Tristan)
- Provides vision and user empathy
- Tests with real users
- Validates that solutions work
- Maintains philosophical alignment

### Claude Code Max
- Architects elegant solutions
- Implements with best practices
- Documents thoroughly
- Synthesizes research

### Local LLM (Mistral-7B)
- Provides NixOS expertise
- Suggests idiomatic patterns
- Validates technical accuracy
- Shares domain knowledge

### How It Works
```
Human Need → LLM Expertise → Claude Implementation → Human Validation
     ↑                                                      ↓
     ←──────────────── Continuous Iteration ───────────────←
```

## Development Principles

### 1. The Sacred Pause
Before writing any code:
- **PAUSE** - Take a breath, center awareness
- **REFLECT** - What serves users?
- **CONNECT** - How does this build trust?
- **FOCUS** - What's the ONE next step?

### 2. Consciousness-First Coding
- Every function is an act of compassion
- Code quality reflects care for others
- User experience honors attention
- Ship weekly to provide continuous value

### 3. Test-Driven Development
- Write tests first when possible
- Aim for >95% coverage
- Test all personas
- Integration tests for workflows

### 4. Documentation as Code
- Document while coding, not after
- Examples are better than explanations
- Keep docs next to code
- Update docs with code changes

## Project Structure

```
nix-for-humanity/
├── backend/               # Unified backend engine
│   ├── core/             # Core functionality
│   ├── python/           # Native integrations
│   ├── learning/         # ML components
│   └── api/              # API definitions
├── src/                   # Frontend implementations
│   ├── cli/              # Command-line interface
│   ├── tui/              # Terminal UI (Textual)
│   ├── voice/            # Voice interface
│   └── api/              # REST/GraphQL API
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                  # Documentation
├── scripts/               # Helper scripts
└── bin/                   # Executable commands
```

## Development Workflow

### 1. Pick an Issue
- Check GitHub issues
- Look for "good first issue" tags
- Coordinate in discussions

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Implement with TDD
```bash
# Write test first
vim tests/test_your_feature.py

# Run test (should fail)
pytest tests/test_your_feature.py

# Implement feature
vim src/your_feature.py

# Run test (should pass)
pytest tests/test_your_feature.py
```

### 4. Check Quality
```bash
# Run all tests
pytest

# Check code style
ruff check .
black --check .

# Type checking
mypy src/
```

### 5. Submit PR
- Clear description of changes
- Link to relevant issues
- Include test results
- Update documentation

## Key Technologies

### Core Stack
- Python 3.11+ (matches NixOS)
- AsyncIO for concurrency
- SQLite for data storage
- pytest for testing

### Key Libraries
- **CLI**: Click, Rich
- **TUI**: Textual
- **NLP**: NLTK, spaCy
- **ML**: scikit-learn, transformers
- **API**: FastAPI

### Development Tools
- **Ruff**: Fast Python linter
- **Black**: Code formatter
- **mypy**: Type checker
- **pytest**: Testing framework

## Common Tasks

### Adding a New Intent
1. Define in `backend/core/intent.py`
2. Add patterns to recognition
3. Implement handler in backend
4. Add tests
5. Update documentation

### Creating a Widget
1. Define in `src/tui/widgets.py`
2. Style in `src/tui/styles.css`
3. Use in main app
4. Add widget tests
5. Document usage

### Improving Performance
1. Profile with `cProfile`
2. Identify bottlenecks
3. Optimize critical paths
4. Measure improvements
5. Document changes

## Getting Help

### Resources
- GitHub Discussions
- Issue Tracker
- Code Comments
- This Documentation

### Community
- Be respectful and kind
- Help others learn
- Share your knowledge
- Celebrate successes

## The Joy of Contributing

Contributing to Nix for Humanity means:
- Making NixOS accessible to millions
- Proving sacred tech can be practical
- Learning from a unique dev model
- Building the future of human-AI partnership

Every contribution, no matter how small, makes a difference. Whether you fix a typo, add a test, or implement a feature, you're part of something transformative.

---

*"Code with consciousness, test with compassion, ship with confidence."*

🌊 We flow together in sacred development!