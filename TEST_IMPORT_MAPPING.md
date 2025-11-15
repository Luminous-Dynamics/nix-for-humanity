# Test Import Mapping - Actual vs Expected
## November 15, 2025

Quick reference for fixing test imports.

## Engine/Backend Classes

### engine.py
**Expected:** `NixForHumanityBackend`
**Actual:** `LuminousNixBackend`

**Fix:**
```python
# Change from:
from luminous_nix.core.engine import NixForHumanityBackend

# To:
from luminous_nix.core.engine import LuminousNixBackend

# OR add alias in tests:
NixForHumanityBackend = LuminousNixBackend
```

**Affected Files (6):**
- tests/e2e/test_persona_journeys.py
- tests/integration/test_cli_core_pipeline.py
- tests/integration/test_real_nixos_operations.py
- tests/unit/test_backend_core.py
- tests/v1.0/test_v1_core_features.py

## Intents Classes

### intents.py
**Expected:** `Package`, `FeedbackItem`
**Actual:** Classes don't exist

**Available Classes:**
- `IntentType` (Enum)
- `Intent`
- `IntentRecognizer`

**Fix:** Skip test or remove import
```python
@pytest.mark.skip(reason="Package/FeedbackItem classes not implemented")
```

**Affected Files (1):**
- tests/unit/test_core_types.py

## Flake Manager Classes

### flake_manager.py
**Expected:** `DevShell`, `FlakeInput`
**Actual:** Classes don't exist

**Available Classes:**
- `FlakeTemplate`
- `FlakeManager`

**Fix:** Update test to use actual classes or skip
```python
@pytest.mark.skip(reason="DevShell/FlakeInput not implemented")
```

**Affected Files (1):**
- tests/unit/test_flake_manager.py

## Missing Modules

### Module: luminous_nix.core.backend
**Status:** Doesn't exist
**Fix:** Use `luminous_nix.core.engine` instead

**Affected Files (1):**
- tests/integration/test_error_intelligence_integration.py

### Module: luminous_nix.consciousness
**Status:** Doesn't exist
**Fix:** Skip tests or remove dependency

**Affected Files (1):**
- tests/unit/test_adaptive_voice.py

### Module: feedback_collector
**Status:** Not in expected location
**Fix:** Skip test or find actual module

**Affected Files (1):**
- tests/unit/test_feedback_collector.py

## Missing Script Files

### scripts/educational-error-handler.py
**Status:** File doesn't exist
**Fix:** Add skip decorator

**Affected Files (2):**
- tests/unit/test_educational_error_handler.py
- tests/unit/test_nix_integration_clean.py

## Summary

**Total Affected:** ~15 test files
**Quick Fixes:** 6 files (simple rename)
**Skip Required:** 6 files (missing classes/modules)
**Module Redirects:** 3 files (wrong module path)

**Estimated Time:** 45-60 minutes to fix all
