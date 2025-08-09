# Mock Usage Report - Nix for Humanity

## Summary

This report identifies all locations where Mock objects are being used in the Nix for Humanity codebase, particularly in test files. These should be replaced with real Request/Response objects from the new contracts defined in `src/nix_for_humanity/core/types.py`.

## Core Types Available

The following real types are available and should be used instead of mocks:

```python
from nix_for_humanity.core.types import (
    Request,      # Main request object with query and context
    Response,     # Main response object with text, intent, plan, result
    Context,      # Request context with execute, dry_run, personality, etc.
    Intent,       # Recognized intent with type and entities
    IntentType,   # Enum of intent types (INSTALL, REMOVE, UPDATE, etc.)
    ExecutionResult,  # Result of command execution
    Plan,         # Execution plan with steps and commands
    Command,      # Single command to execute
    Package,      # Nix package information
    FeedbackItem  # User feedback
)
```

## Files Using Mocks

### 1. Unit Tests (22 files total)

#### Test Files with Mock Imports:
1. `/tests/unit/test_cli_adapter.py`
   - Uses: `Mock`, `MagicMock`, `patch`
   - Mocks: backend, args
   - Comments indicate some awareness: "Use real Response object instead of Mock"

2. `/tests/unit/test_headless_engine.py`
   - Uses: `MagicMock`, `patch`
   - Mocks: knowledge, feedback, plugin_manager, learning, cache

3. `/tests/unit/test_executor.py`
   - Uses: `Mock`, `MagicMock`, `patch`
   - Mocks: progress_callback

4. `/tests/unit/test_tui_app.py`
   - Uses mocks for TUI testing

5. `/tests/unit/test_nix_integration.py`
6. `/tests/unit/test_nix_integration_clean.py`
7. `/tests/unit/test_knowledge_comprehensive.py`
8. `/tests/unit/test_intent_comprehensive.py`
9. `/tests/unit/test_executor_comprehensive.py`
10. `/tests/unit/test_backend_comprehensive.py`
11. `/tests/unit/test_knowledge_base_enhanced.py`
12. `/tests/unit/test_engine_enhanced.py`
13. `/tests/unit/test_execution_engine_enhanced.py`
14. `/tests/unit/test_core_engine.py`
15. `/tests/unit/test_execution_engine.py`

### 2. Integration Tests (4 files)

1. `/tests/integration/test_cli_core_pipeline.py`
2. `/tests/integration/test_cli_core_pipeline_simple.py`
3. `/tests/integration/test_security_execution.py`

### 3. E2E Tests (1 file)

1. `/tests/e2e/test_persona_journeys.py`

### 4. Other Test Files

1. `/test_nix_integration_simple.py`
2. `/run_tests.py`
3. `/backend/python/test_resilient_voice.py`

## Recommended Actions

### 1. Replace Mock Request/Response Objects

Instead of:
```python
mock_response = Mock()
mock_response.text = "Installing firefox..."
mock_response.success = True
```

Use:
```python
from nix_for_humanity.core.types import Response, Intent, IntentType

response = Response(
    success=True,
    text="Installing firefox...",
    intent=Intent(
        type=IntentType.INSTALL,
        entities={"package": "firefox"}
    )
)
```

### 2. Replace Mock Context Objects

Instead of:
```python
mock_context = Mock()
mock_context.execute = False
mock_context.dry_run = True
```

Use:
```python
from nix_for_humanity.core.types import Context

context = Context(
    execute=False,
    dry_run=True,
    personality="friendly",
    frontend="cli"
)
```

### 3. Replace Mock Request Objects

Instead of:
```python
mock_request = Mock()
mock_request.query = "install firefox"
```

Use:
```python
from nix_for_humanity.core.types import Request, Context

request = Request(
    query="install firefox",
    context=Context(dry_run=True)
)
```

### 4. Keep Mocks for External Dependencies

It's still appropriate to use mocks for:
- External services (knowledge base, feedback collector)
- System calls (subprocess, file I/O)
- Plugin managers
- Progress callbacks

### 5. Benefits of Using Real Types

1. **Type Safety**: Real dataclasses provide type hints and validation
2. **Serialization**: Built-in `to_dict()` and `from_dict()` methods
3. **Documentation**: Self-documenting structure
4. **Consistency**: Same objects used in production and tests
5. **Refactoring**: Changes to types automatically update tests

## Priority Files to Update

1. `test_cli_adapter.py` - Already has comments about using real Response objects
2. `test_headless_engine.py` - Core engine tests should use real types
3. `test_executor.py` - Execution tests need real Intent and ExecutionResult
4. Integration tests - Should definitely use real types for end-to-end testing

## Migration Strategy

1. Start with unit tests that already have comments about using real objects
2. Update integration tests to use real Request/Response flow
3. Keep mocks for external dependencies only
4. Run tests after each file update to ensure nothing breaks
5. Update test documentation to show proper usage of real types