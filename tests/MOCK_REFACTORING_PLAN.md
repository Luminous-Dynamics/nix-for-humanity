# Mock Refactoring Plan - Consciousness-First Testing

## Overview
Transform all test files from mock-based testing to consciousness-first testing using real test implementations with deterministic behavior.

## Files to Refactor (Priority Order)

### High Priority (Heavy Mock Usage)
1. **test_backend_comprehensive.py** - Extensive MagicMock usage
   - Status: Started refactoring
   - Mocks: MagicMock for all dependencies, AsyncMock, patch decorators

2. **test_executor_comprehensive.py** - Mock nixos_rebuild modules
   - Mocks: sys.modules mocking, Mock() for nix API

3. **test_engine_enhanced.py** - Mock all engine components
   - Mocks: Mock() for intent, knowledge, execution, personality, learning

4. **test_headless_engine.py** - Mock all backend services
   - Mocks: MagicMock for knowledge, feedback, plugins, learning, cache

### Medium Priority (Moderate Mock Usage)
5. **test_cli_adapter_comprehensive.py** - Patch multiple imports
   - Mocks: patch() for core imports, Mock classes

6. **test_native_nix_backend.py** - Mock native API modules
   - Mocks: patch() for API availability, mock nix modules

7. **test_execution_engine.py** - Mock subprocess.run
   - Mocks: @patch('subprocess.run') throughout

8. **test_tui_app.py** - Mock textual framework
   - Mocks: MagicMock for entire textual library

### Low Priority (Minimal Mock Usage)
9. **test_caching_layer.py** - Only 2 Mock() instances
   - Status: ✅ COMPLETED

10. **test_cli_adapter.py** - Only patch() for sys.argv/input
    - Mocks: Minimal, only for system interaction

11. **test_learning_system_edge_cases.py** - Single patch for Path.home
    - Mocks: Very minimal

## Refactoring Pattern

### Before (Mock-based):
```python
from unittest.mock import Mock, MagicMock, patch

def test_something(self):
    mock_service = MagicMock()
    mock_service.method.return_value = "result"

    component = Component(mock_service)
    result = component.do_something()

    mock_service.method.assert_called_once()
```

### After (Consciousness-First):
```python
from tests.test_utils.test_implementations import TestService

def test_something(self):
    # Use real test implementation with deterministic behavior
    test_service = TestService()
    test_service.add_test_data("expected", "result")

    component = Component(test_service)
    result = component.do_something()

    # Verify through state, not mock calls
    assert result == "result"
    assert test_service.was_called_with("expected")
```

## Test Implementation Components Available

From `test_implementations.py`:
- `TestNLPEngine` - NLP with deterministic intent recognition
- `TestExecutionBackend` - Command execution with predictable results
- `TestDatabase` - In-memory SQLite for testing
- `TestLearningEngine` - Learning system with test adaptations
- `TestKnowledgeBase` - NixOS knowledge with test data
- `TestBackendAPI` - Full backend API simulation
- `TestContextManager` - Conversation context tracking
- `TestProgressCallback` - Progress tracking

## Benefits of Consciousness-First Testing

1. **Real Behavior**: Tests verify actual component interactions
2. **Deterministic**: Predictable results without flakiness
3. **Persona-Aware**: Built-in support for testing all 10 personas
4. **Privacy-Preserving**: Test data stays in memory
5. **Performance**: No mock overhead, real timing data

## Implementation Steps

1. Start with high-priority files that have extensive mocking
2. For each file:
   - Remove mock imports
   - Replace mocks with test implementations
   - Add persona-specific test cases where applicable
   - Ensure deterministic behavior
   - Use dependency injection pattern

3. Update imports to use test_implementations
4. Convert assertions from mock call verification to state verification
5. Add consciousness-first principles (sacred boundaries, user agency)

## Progress Tracking

- [x] test_caching_layer.py - COMPLETE
- [ ] test_backend_comprehensive.py - IN PROGRESS
- [ ] test_executor_comprehensive.py
- [ ] test_engine_enhanced.py
- [ ] test_headless_engine.py
- [ ] test_cli_adapter_comprehensive.py
- [ ] test_native_nix_backend.py
- [ ] test_execution_engine.py
- [ ] test_tui_app.py
- [ ] test_cli_adapter.py
- [ ] test_learning_system_edge_cases.py

## Notes

- Some system-level patches (like sys.argv) may need to remain
- Focus on removing business logic mocks, keep system interaction mocks minimal
- Each refactored test should demonstrate consciousness-first principles
