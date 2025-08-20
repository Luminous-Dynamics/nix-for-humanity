# Symbiotic Refactoring Pattern

**Inspired by**: LuminousOS vision documents  
**Adapted for**: Luminous Nix practical development

## The Pattern

When fixing technical debt, use it as an opportunity to specify better architecture:

### Example: Fixing Test Coverage

**Traditional Approach**: Write tests that validate existing broken behavior  
**Symbiotic Approach**: Write tests that specify CORRECT behavior, then fix code to match

```python
# BAD: Test that reinforces current bugs
def test_vague_package_high_confidence():
    """Test that 'get me something' has high confidence (current bug)"""
    intent = recognizer.recognize("get me something")
    assert intent.confidence > 0.8  # This is wrong!

# GOOD: Test that specifies correct behavior
def test_vague_requests_low_confidence():
    """Vague requests should have low confidence - this guides users to be specific"""
    intent = recognizer.recognize("get me something") 
    assert intent.confidence < 0.7  # Teaching moment!
    # Now fix the code to match this specification
```

## Benefits

1. **Every bug fix improves architecture** - Not just patching symptoms
2. **Tests become specifications** - Documentation of intended behavior
3. **Technical debt becomes wisdom** - Each fix teaches us something

## Implementation Steps

1. **Identify the bug/debt**
2. **Ask: "What SHOULD happen?"** (consult the vision)
3. **Write test for correct behavior** (specification)
4. **Fix code to pass test** (implementation)
5. **Document the learning** (wisdom capture)

This way, our 35% → 70% test coverage journey becomes an architectural improvement journey!