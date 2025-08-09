# Consciousness-First Testing Guide

## Philosophy

Consciousness-first testing replaces traditional mocking with deterministic test implementations that behave like real components. This approach:

1. **Tests Real Behavior**: Verifies actual component interactions
2. **Supports All Personas**: Built-in testing for all 10 user personas
3. **Maintains Privacy**: All test data stays in memory
4. **Ensures Determinism**: Predictable results without timing issues
5. **Promotes Sacred Boundaries**: Respects user agency and system integrity

## Available Test Implementations

### Core Components (from `test_implementations.py`)

```python
from tests.test_utils.test_implementations import (
    TestNLPEngine,              # Natural language processing with deterministic intent recognition
    TestExecutionBackend,       # Command execution with predictable results
    TestDatabase,              # In-memory SQLite for testing
    TestLearningEngine,        # Learning system with test adaptations
    TestKnowledgeBase,         # NixOS knowledge with test data
    TestBackendAPI,            # Full backend API simulation
    TestContextManager,        # Conversation context tracking
    TestProgressCallback,      # Progress tracking
    PERSONA_TEST_DATA,         # Test data for all 10 personas
    create_successful_process, # Helper for successful command results
    create_failed_process,     # Helper for failed command results
    create_test_process       # Helper for custom process results
)
```

## Refactoring Pattern

### Step 1: Remove Mock Imports
```python
# Before
from unittest.mock import Mock, MagicMock, patch, AsyncMock

# After
from tests.test_utils.test_implementations import (
    TestNLPEngine, TestExecutionBackend, TestDatabase
)
```

### Step 2: Replace Mock Creation with Test Implementations
```python
# Before
mock_nlp = MagicMock()
mock_nlp.process.return_value = {"intent": "install", "package": "firefox"}

# After
test_nlp = TestNLPEngine()
# TestNLPEngine has deterministic behavior - it will recognize 
# "install firefox" and return appropriate intent
```

### Step 3: Use Dependency Injection
```python
# Before
class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.nlp = MagicMock()  # Mock injection

# After
class TestEngine:
    @pytest.fixture
    def test_nlp(self):
        return TestNLPEngine()
    
    @pytest.fixture
    def engine(self, test_nlp):
        engine = Engine()
        engine.nlp = test_nlp  # Test implementation injection
        return engine
```

### Step 4: Test Through Behavior, Not Mock Calls
```python
# Before
def test_install_command(self):
    self.mock_executor.execute.return_value = {"success": True}
    result = self.engine.install("firefox")
    self.mock_executor.execute.assert_called_once_with("nix-env", ["-iA", "nixos.firefox"])

# After  
def test_install_command(self, engine, test_executor):
    result = engine.install("firefox")
    
    # Verify through state and behavior
    assert result["success"] is True
    assert "firefox" in test_executor.installed_packages
    assert test_executor.commands_executed[-1] == ("nix-env", ["-iA", "nixos.firefox"])
```

## Persona-Aware Testing

Test implementations support all 10 personas with realistic behavior:

```python
def test_maya_adhd_fast_response(self, test_nlp):
    # Maya needs responses in <1 second
    result = test_nlp.process("firefox now", persona="maya_adhd")
    
    assert result['processing_time'] < 0.1  # Super fast for Maya
    assert result['response_style'] == 'minimal'
    assert result['intent'] == 'install'
    assert result['package'] == 'firefox'

def test_grandma_rose_friendly_help(self, test_nlp):
    # Grandma Rose needs friendly, simple language
    result = test_nlp.process("I need that Firefox thing", persona="grandma_rose")
    
    assert result['response_style'] == 'friendly'
    assert result['corrections'] is None  # Don't confuse with corrections
    assert result['intent'] == 'install'
    assert result['package'] == 'firefox'
```

## When to Keep Mocks

Some mocking is appropriate for system boundaries:

### Keep These Mocks:
- `patch('sys.argv')` - Command line arguments
- `patch('builtins.input')` - User input simulation
- `patch('sys.stdin.isatty')` - Terminal detection
- External UI frameworks (like Textual)
- Network calls (if any)
- File system operations (when not testing file handling)

### Replace These Mocks:
- Service/component mocks
- Business logic mocks
- Database mocks (use TestDatabase)
- Learning system mocks
- NLP/AI component mocks

## Example: Complete Test Refactoring

### Before (Mock-based)
```python
class TestBackend(unittest.TestCase):
    def setUp(self):
        self.nlp = MagicMock()
        self.executor = MagicMock()
        self.kb = MagicMock()
        
        self.backend = Backend()
        self.backend.nlp = self.nlp
        self.backend.executor = self.executor
        self.backend.knowledge = self.kb
        
    def test_install_firefox(self):
        self.nlp.process.return_value = {"intent": "install", "package": "firefox"}
        self.kb.has_package.return_value = True
        self.executor.execute.return_value = {"success": True}
        
        result = self.backend.process("install firefox")
        
        self.nlp.process.assert_called_once()
        self.executor.execute.assert_called_with("nix-env", ["-iA", "nixos.firefox"])
        self.assertTrue(result["success"])
```

### After (Consciousness-First)
```python
class TestBackend:
    @pytest.fixture
    def test_components(self):
        db = TestDatabase()
        return {
            'nlp': TestNLPEngine(),
            'executor': TestExecutionBackend(),
            'knowledge': TestKnowledgeBase(),
            'learning': TestLearningEngine(db)
        }
    
    @pytest.fixture
    def backend(self, test_components):
        backend = Backend()
        for name, component in test_components.items():
            setattr(backend, name, component)
        return backend
    
    def test_install_firefox(self, backend, test_components):
        # Process with real test implementations
        result = backend.process("install firefox")
        
        # Verify through actual behavior
        assert result["success"] is True
        assert "firefox" in test_components['executor'].installed_packages
        
        # Verify learning happened
        stats = test_components['learning'].db.get_learning_stats('default')
        assert stats['total_interactions'] == 1
        assert stats['successful_interactions'] == 1
        
    @pytest.mark.parametrize("persona,input_text", [
        ("grandma_rose", "I need that Firefox thing"),
        ("maya_adhd", "firefox now"),
        ("dr_sarah", "install firefox-esr for research"),
        ("alex_blind", "install firefox with screen reader support")
    ])
    def test_install_across_personas(self, backend, persona, input_text):
        # Test with different personas
        result = backend.process(input_text, context={'persona': persona})
        
        # All personas should succeed
        assert result["success"] is True
        
        # But with persona-appropriate responses
        persona_data = PERSONA_TEST_DATA[persona]
        assert result['response_time'] < persona_data['max_response_time']
```

## Benefits Achieved

1. **More Realistic**: Tests verify actual component behavior
2. **Better Coverage**: Testing real interactions catches more bugs  
3. **Persona Support**: Built-in testing for all user types
4. **Maintainable**: Less mock setup code
5. **Deterministic**: Predictable results every time
6. **Educational**: Tests document real behavior

## Next Steps

1. Continue refactoring remaining test files
2. Add more test implementations as needed
3. Create test utilities for common scenarios
4. Document new test patterns
5. Ensure CI/CD uses consciousness-first approach

Remember: The goal is not to eliminate all mocks, but to test real behavior wherever possible while maintaining fast, deterministic tests.