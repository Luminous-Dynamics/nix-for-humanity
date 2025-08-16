# Tui

*Comprehensive test coverage for the Luminous Nix TUI application.*

## 📚 Contents


### 📁 Subdirectories

- [__pycache__/](__pycache__/) - 0 documents

---

## Original Documentation


Comprehensive test coverage for the Luminous Nix TUI application.

## Test Classes

### 1. TestTUIAppCore
Core functionality tests covering:
- App initialization and configuration
- Widget composition and layout
- Backend integration
- Message processing and query handling
- Progress updates and status management
- Response formatting
- Keyboard shortcuts

### 2. TestTUIPersonaAdaptation
Tests for all 10 personas:
- Grandma Rose (gentle, voice-friendly)
- Maya (ADHD - minimal, fast)
- David (tired parent - reassuring)
- Dr. Sarah (technical, precise)
- Alex (blind - screen reader optimized)
- Carlos (learner - educational)
- Priya (busy mom - efficient)
- Jamie (privacy advocate - transparent)
- Viktor (ESL - clear language)
- Luna (autistic - predictable)

Each persona tested for:
- Style selection
- Response time requirements
- Language adaptation
- Error message personalization

### 3. TestTUIXAIIntegration
XAI (Explainable AI) features:
- Explanation display
- Confidence indicators
- Reasoning path visualization
- Educational integration
- Keyboard shortcuts for XAI

### 4. TestTUIErrorHandling
Error scenarios:
- Backend connection errors
- Invalid command errors
- Permission denied errors
- Network timeout errors
- Error recovery suggestions

### 5. TestTUIAccessibility
Accessibility compliance:
- Complete keyboard navigation
- Screen reader metadata
- ARIA labels
- High contrast mode
- Focus indicators

### 6. TestTUIPerformance
Performance requirements:
- Startup time < 3 seconds
- Response time < 2 seconds
- Memory usage < 300MB
- Smooth scrolling with 1000+ messages
- Native API 10x performance boost

## Running Tests

```bash
# Run all TUI tests
pytest tests/tui/test_tui_app_comprehensive.py -v

# Run specific test class
pytest tests/tui/test_tui_app_comprehensive.py::TestTUIPersonaAdaptation -v

# Run with coverage
pytest tests/tui/test_tui_app_comprehensive.py --cov=src.tui.app --cov-report=html

# Run performance tests only
pytest tests/tui/test_tui_app_comprehensive.py -k "performance" -v
```

## Coverage Target

This test suite aims to achieve 95% coverage of the TUI App component (192 lines).

## Key Testing Strategies

1. **Mock Backend**: All backend interactions are mocked to test UI in isolation
2. **Async Testing**: Uses pytest-asyncio for testing async methods
3. **Textual Pilot**: Uses Textual's testing framework for UI interactions
4. **Persona-Driven**: Each feature tested across all 10 personas
5. **Performance Monitoring**: Actual timing measurements for performance tests
