# Archive Log - 2025-08-12

## Reason for Archive: The 955 Broken Tests Disaster

### What Happened
- We discovered 955 tests for features that don't exist
- Tests were written for aspirational features in documentation
- Created false "95% coverage" when reality was 8%
- Tests assumed 5 backends when only 1 exists (NixForHumanityBackend)

### What We're Archiving
- All tests that import non-existent modules
- Tests for advanced learning system (doesn't exist)
- Tests for multiple backends (only 1 exists)
- Tests for symbiotic intelligence features (not implemented)
- Tests for causal XAI engine (not built)

### Lessons Learned
1. **Test what IS, not what MIGHT BE**
2. **Build features WITH tests, not tests WITHOUT features**
3. **Documentation ≠ Implementation**
4. **Be honest about coverage**

### Files Archived
See list below - these are tests for phantom features.

---

## Archive Contents

### Unit Tests (Broken) - 36 files archived
- test_advanced_learning.py - Tests for non-existent learning system
- test_ai_nlp.py - Tests for complex AI that doesn't exist
- test_backend_comprehensive.py - Tests 5 backends, only 1 exists
- test_caching_layer.py - Tests advanced caching not implemented
- test_cli_adapter_comprehensive.py - Tests old CLIAdapter (renamed)
- test_execution_engine_enhanced.py - Tests features not built
- test_explainable_self_maintenance_orchestrator.py - Pure fantasy
- test_headless_engine.py - HeadlessBackend doesn't exist
- test_intent_comprehensive.py - Tests complex intent system not built
- test_learning_system_comprehensive.py - Learning system doesn't exist
- test_nix_integration_clean.py - Tests features not implemented
- test_performance_benchmark.py - Benchmarks non-existent features
- test_personality_system_enhanced.py - Advanced personality not built
- test_serve_demo_simple.py - Demo features not implemented
- test_headless_architecture.py - Tests non-existent architecture
- test_imports.py - Tests imports of non-existent modules
- test_unified_backend.py - UnifiedBackend doesn't exist
- test_symbiotic.py - Symbiotic intelligence not implemented
- test_headless_engine_simple.py - Imports from non-existent headless_engine
- test_jsonrpc_server.py - Imports from non-existent headless_engine
- test_performance_monitor.py - Imports from non-existent monitoring.performance_monitor
- test_engine_enhanced.py - Imports from non-existent learning.preferences
- test_executor.py - Imports Intent/IntentType from wrong module (core)
- test_executor_simple.py - Imports Intent/IntentType from wrong module (core)
- test_intent_engine_enhanced.py - Imports Intent from wrong module (core)
- test_backend_core.py - Imports Intent from wrong module (core)
- test_intent_engine.py - Imports Intent from wrong module (core)

### CLI Tests (Broken) - 5 files archived
- test_cli_adapter_comprehensive.py - Imports non-existent CLIAdapter
- test_cli_backend_integration.py - Imports non-existent CLIAdapter
- test_cli_interface.py - Imports non-existent CLIAdapter
- test_cli_basic.py - Imports non-existent CLIAdapter
- test_cli_simple.py - Imports non-existent CLIAdapter

### Integration Tests (Broken) - 9 files archived
- test_ai_nlp_integration.py - AI integration doesn't exist
- test_advanced_features.py - Features not implemented
- test_real_nixos_operations.py - All operations are mocked
- test_voice_interface.py - Voice not fully integrated
- test_full_integration.py - Tests non-existent features
- test_comprehensive.py - Tests comprehensive features not built
- test_research_components_simple.py - Tests research features that don't exist
- test_research_integration.py - Tests for non-existent research integration

### Root Tests (Broken) - 11 files archived
- test_unified_backend_features.py - Imports from non-existent scripts/backend
- test_component_integration.py - Tests non-existent research components (SKG, trust_engine)
- test_tui_structure.py - Checks wrong directory structure (src/tui instead of src/nix_for_humanity/tui)

### The Reality
- Only 11 tests actually work
- These test real, implemented features
- Real coverage is about 8%, not 95%
- **61 tests archived so far** (36 unit + 5 CLI + 9 integration + 11 root tests)

---

*"We learned that testing the dream instead of the reality creates a nightmare of maintenance."*