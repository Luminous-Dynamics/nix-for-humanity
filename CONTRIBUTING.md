# Contributing to Luminous Nix

Thank you for your interest in contributing to Luminous Nix!

## Development Setup

### Prerequisites
- Python 3.11+
- Poetry
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix.git
cd luminous-nix

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Verify setup
poetry run pytest tests/test_core_imports.py -v
poetry run ask-nix --version
```

## Pre-commit Hooks

We use pre-commit hooks to maintain code quality. Hooks run automatically before each commit.

### What the hooks do:
- **black**: Auto-format Python code
- **ruff**: Lint and auto-fix issues
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML files
- **check-toml**: Validate TOML files
- **pytest-quick**: Run core tests (on push only)

### Running hooks manually:

```bash
# Run all hooks on all files
poetry run pre-commit run --all-files

# Run specific hook
poetry run pre-commit run black --all-files

# Skip hooks for emergency commits (not recommended)
git commit --no-verify -m "Emergency fix"
```

## Code Quality Standards

### Formatting
- Use **black** for code formatting (line length: 88)
- All code must pass black checks

### Linting
- Use **ruff** for linting
- Fix all auto-fixable issues
- Document reasons for ignoring lint rules

### Testing
- Write tests for new features
- Maintain >80% test coverage
- All tests must pass before merging

### Type Hints
- Add type hints to function signatures
- Use mypy for type checking

## Development Workflow

### 1. Create a branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make changes
- Write code
- Write tests
- Update documentation

### 3. Run quality checks
```bash
# Format code
poetry run black src/ tests/

# Run linting
poetry run ruff check --fix src/ tests/

# Run tests
poetry run pytest tests/

# Run all pre-commit hooks
poetry run pre-commit run --all-files
```

### 4. Commit changes
```bash
git add .
git commit -m "feat: your feature description"
# Hooks will run automatically
```

### 5. Push and create PR
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

## Commit Message Convention

Use conventional commits format:

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting)
- **refactor**: Code refactoring
- **test**: Test changes
- **chore**: Build/tooling changes

Examples:
```
feat: add voice interface support
fix: resolve import error in maya_mode.py
docs: update installation instructions
```

## Testing

### Running Tests

```bash
# All tests
poetry run pytest tests/

# Specific test file
poetry run pytest tests/test_core_imports.py

# With coverage
poetry run pytest --cov=luminous_nix --cov-report=term-missing

# Verbose output
poetry run pytest -v tests/
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names

Example:
```python
def test_executor_imports():
    """Test that SafeExecutor imports successfully"""
    from luminous_nix.core.executor import SafeExecutor
    assert SafeExecutor is not None
```

## Documentation

### Code Documentation
- Add docstrings to public functions/classes
- Use Google-style docstrings
- Include examples where helpful

### Project Documentation
- Update README.md for user-facing changes
- Update CHANGELOG.md for releases
- Add technical details to docs/

## Pull Request Process

1. **Before submitting:**
   - All tests pass
   - Code is formatted (black)
   - No lint errors (ruff)
   - Documentation updated
   - Pre-commit hooks pass

2. **PR Description:**
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable
   - Testing instructions

3. **Review Process:**
   - Address review feedback
   - Keep commits clean
   - Update PR description as needed

## Getting Help

- **Documentation**: Check README.md and docs/
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions
- **Examples**: Check existing code for patterns

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

Feel free to open an issue or start a discussion!

---

**Happy contributing!** 🎉
