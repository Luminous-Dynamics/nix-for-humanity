# Contributing to Luminous Nix

Thank you for your interest in contributing to Luminous Nix! This project aims to make NixOS accessible to everyone through natural language interfaces.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:
- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:
1. Check if the issue already exists in [GitHub Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
2. If not, create a new issue with:
   - Clear description of the problem or suggestion
   - Steps to reproduce (for bugs)
   - Your environment (NixOS version, Python version, etc.)
   - Any relevant error messages or logs

### Suggesting Features

We welcome feature suggestions! Please:
1. Open a [GitHub Discussion](https://github.com/Luminous-Dynamics/luminous-nix/discussions) first
2. Describe the use case and problem it solves
3. Consider how it fits with the project's philosophy
4. Be open to feedback and alternative approaches

### Contributing Code

#### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/luminous-nix.git
cd luminous-nix

# Enter Nix shell for dependencies
nix-shell

# Install Python dependencies
poetry install

# Run tests to verify setup
poetry run pytest tests/
```

#### Development Workflow

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style:
   - Use meaningful variable and function names
   - Add docstrings to all functions and classes
   - Keep functions focused and single-purpose
   - Write tests for new functionality

3. **Test your changes**:
   ```bash
   # Run all tests
   poetry run pytest tests/
   
   # Run specific test file
   poetry run pytest tests/test_specific.py
   
   # Check code style
   poetry run black --check src/
   poetry run ruff check src/
   ```

4. **Commit your changes** with clear messages:
   ```bash
   git add .
   git commit -m "feat: add natural language support for X"
   ```
   
   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions or changes
   - `refactor:` Code refactoring
   - `style:` Code style changes

5. **Push and create a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a PR on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots/examples if applicable

### Contributing Documentation

Documentation is crucial for accessibility! You can help by:
- Improving existing documentation for clarity
- Adding examples and tutorials
- Translating documentation
- Creating video tutorials or demos

### Testing

We especially need help with:
- Testing on different NixOS configurations
- Testing with different hardware setups
- Accessibility testing (screen readers, keyboard navigation)
- Performance testing on various systems

## Project Structure

```
luminous-nix/
├── src/luminous_nix/     # Main source code
│   ├── core/             # Core engine
│   ├── nlp/              # Natural language processing
│   ├── cli/              # Command-line interface
│   └── ui/               # User interfaces
├── tests/                # Test suite
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## Code Style Guidelines

- **Python**: Follow PEP 8, use Black for formatting
- **Docstrings**: Use Google style docstrings
- **Type hints**: Add type hints to function signatures
- **Comments**: Explain why, not what
- **Naming**: Use descriptive names that explain purpose

Example:
```python
def parse_user_intent(query: str) -> IntentResult:
    """Parse natural language query to determine user intent.
    
    Args:
        query: Natural language query from user
        
    Returns:
        IntentResult containing parsed intent and confidence
        
    Examples:
        >>> parse_user_intent("install firefox")
        IntentResult(action="install", target="firefox", confidence=0.95)
    """
    # Implementation here
```

## Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and error conditions

## Areas We Need Help

### High Priority
- **NixOS Command Coverage**: Expand support for more Nix commands
- **Error Messages**: Improve educational error explanations
- **Performance**: Optimize response times
- **Testing**: Increase test coverage (currently ~8%)

### Medium Priority
- **Documentation**: Tutorials, guides, examples
- **Internationalization**: Multi-language support
- **Accessibility**: Screen reader improvements
- **UI/UX**: Terminal UI enhancements

### Future Features
- **Voice Interface**: Complete integration
- **Plugin System**: Architecture for extensions
- **Community Features**: Pattern sharing
- **Learning System**: Improve with usage

## Questions?

- Open a [GitHub Discussion](https://github.com/Luminous-Dynamics/luminous-nix/discussions)
- Check the [documentation](docs/README.md)
- Review existing [issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)

## Recognition

All contributors will be recognized in our README and release notes. We value every contribution, no matter how small!

## Development Philosophy

This project follows a "consciousness-first" approach:
- **User agency**: Users should always be in control
- **Transparency**: Clear about what will happen
- **Education**: Help users learn while using
- **Accessibility**: Design for all users
- **Privacy**: Everything runs locally

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make NixOS more accessible to everyone! 🌟