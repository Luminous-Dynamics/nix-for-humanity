# Test Cleanup Strategy - Phase 6

## Current Situation
- **120+ test files** scattered throughout codebase
- **905 test files originally** in git history
- Many duplicates, mocks, and aspirational tests
- Tests for features that don't exist

## Test Categories to Clean Up

### 1. Root Directory Tests (24 files) - TO BE REMOVED
These are scattered tests that should be consolidated:
- `test_*.py` files in root (testing during development)
- Duplicate functionality with tests/ directory
- Many are old experiments

### 2. Tests Directory Structure

#### Keep (Real Tests):
- `tests/integration/test_real_nixos.py` - Actually tests Nix operations
- `tests/integration/test_native_operations_real.py` - Tests native API
- `tests/performance/test_native_api_performance.py` - Performance benchmarks
- `tests/security/test_enhanced_validator.py` - Security validation
- `tests/unit/test_native_nix_backend.py` - Native backend tests

#### Remove (Mocks/Duplicates):
- `tests/test_*.py` - Old duplicates in tests root
- `tests/unit/test_*_engine.py` - Multiple engine test duplicates
- `tests/unit/test_cli_adapter*.py` - Redundant CLI tests
- `tests/test_graphrag_*.py` - GraphRAG not implemented
- `tests/test_model_*.py` - Model tests for non-existent models

### 3. Embedded Tests in src/
- `src/luminous_nix/ai/test_hrm_use_cases.py` - Move to tests/
- `src/luminous_nix/voice/test_voice_comprehensive.py` - Move to tests/

## Consolidation Plan

### Final Test Structure:
```
tests/
├── unit/           # Real unit tests
│   ├── test_native_api.py
│   ├── test_command_executor.py
│   ├── test_intent_recognition.py
│   └── test_config_generator.py
├── integration/    # Real integration tests
│   ├── test_real_nixos_operations.py
│   ├── test_cli_flow.py
│   └── test_tui_integration.py
├── performance/    # Performance tests
│   └── test_native_api_performance.py
├── security/       # Security tests
│   └── test_input_validation.py
└── conftest.py    # Shared fixtures
```

## Action Items

1. **Delete root test files** (24 files)
2. **Consolidate unit tests** (reduce 50+ to ~10)
3. **Remove mock tests** (tests that only test mocks)
4. **Remove aspirational tests** (tests for non-existent features)
5. **Move embedded tests** to proper location
6. **Update test imports** to use native API

## Expected Outcome
- From 120+ test files to ~15-20 focused test files
- All tests actually test real functionality
- Tests use native API for standard speed execution
- Clear separation of unit/integration/performance tests