# 🎯 Strategic Test Coverage Plan - Maximum User Impact

*Focused testing strategy for TUI App and CLI Adapter - the user-facing foundation*

## Overview

**Goal**: Achieve maximum coverage impact by focusing on user-critical components  
**Strategy**: High-impact, targeted testing of the two most critical gaps  
**Timeline**: 2-4 weeks in Kairos time  
**Expected Coverage Jump**: 60% → 85%+ overall coverage

## 🚀 Phase 1: Critical User Interface Testing (Immediate Priority)

### Target 1: TUI App Testing (0% → 95%) - 192 Lines Impact

**File**: `src/nix_for_humanity/tui/app.py`  
**Current Coverage**: 0% (192 lines uncovered)  
**User Impact**: PRIMARY - This is the beautiful terminal interface users see

#### TUI App Test Suite Plan:

```python
# tests/tui/test_tui_app_comprehensive.py
"""
Comprehensive TUI App testing covering all user interactions
Priority: MAXIMUM - User-facing component with 0% coverage
"""

import pytest
from textual.testing import TUITestApp
from nix_for_humanity.tui.app import NixHumanityTUI

class TestTUIAppCore:
    """Core application functionality tests"""
    
    def test_app_initialization(self):
        """Test TUI app starts successfully with all panels"""
        app = NixHumanityTUI()
        with TUITestApp(app) as pilot:
            # Verify main panels exist
            assert pilot.app.query_one("#input-panel")
            assert pilot.app.query_one("#response-panel") 
            assert pilot.app.query_one("#xai-panel")
            assert pilot.app.query_one("#status-panel")
    
    def test_input_processing_flow(self):
        """Test complete input → processing → response flow"""
        app = NixHumanityTUI()
        with TUITestApp(app) as pilot:
            # Type query
            input_widget = pilot.app.query_one("#input-field")
            pilot.click("#input-field")
            pilot.type("install firefox")
            pilot.press("Enter")
            
            # Verify processing state
            assert "Processing..." in pilot.app.query_one("#status-panel").renderable
            
            # Wait for response (with timeout)
            pilot.wait_for_scheduled_animations()
            
            # Verify response appears
            response_panel = pilot.app.query_one("#response-panel")
            assert "firefox" in str(response_panel.renderable)

class TestTUIPersonaAdaptation:
    """Test persona-specific styling and behavior"""
    
    @pytest.mark.parametrize("persona", [
        "grandma_rose", "maya_adhd", "alex_blind", "dr_sarah", "carlos_learner"
    ])
    def test_persona_styling_adaptation(self, persona):
        """Test TUI adapts styling for each persona"""
        app = NixHumanityTUI(persona=persona)
        with TUITestApp(app) as pilot:
            # Get persona-specific expectations
            expected_style = self.get_persona_style_expectations(persona)
            
            # Verify styling matches persona
            app_styles = pilot.app.get_css_vars()
            
            if persona == "maya_adhd":
                # Maya needs minimal, high-contrast
                assert "high-contrast" in str(app_styles)
                assert pilot.app.query_one("#response-panel").styles.text_style == "minimal"
            elif persona == "grandma_rose":
                # Grandma Rose needs larger text, warm colors
                assert pilot.app.query_one("#response-panel").styles.text_size == "large"
            elif persona == "alex_blind":
                # Alex needs screen reader optimization
                assert pilot.app.query_one("#input-field").has_attribute("aria-label")
                assert pilot.app.query_one("#response-panel").has_attribute("aria-live")

class TestTUIXAIIntegration:
    """Test XAI explanation panel functionality"""
    
    def test_xai_explanation_display(self):
        """Test XAI explanations appear correctly"""
        app = NixHumanityTUI()
        with TUITestApp(app) as pilot:
            # Submit query that generates XAI explanation
            pilot.click("#input-field")
            pilot.type("install firefox")
            pilot.press("Enter")
            
            # Wait for processing
            pilot.wait_for_scheduled_animations()
            
            # Verify XAI panel populated
            xai_panel = pilot.app.query_one("#xai-panel")
            xai_content = str(xai_panel.renderable)
            
            assert "Why:" in xai_content
            assert "Confidence:" in xai_content
            assert "firefox" in xai_content.lower()
    
    def test_xai_explanation_levels(self):
        """Test XAI explanation depth levels (simple/detailed/expert)"""
        app = NixHumanityTUI()
        with TUITestApp(app) as pilot:
            # Start with simple explanation
            pilot.click("#input-field")
            pilot.type("install firefox")
            pilot.press("Enter")
            pilot.wait_for_scheduled_animations()
            
            # Switch to detailed explanation
            pilot.press("Ctrl+X")  # Toggle XAI detail level
            xai_content = str(pilot.app.query_one("#xai-panel").renderable)
            assert "reasoning_path" in xai_content or "detailed" in xai_content.lower()
            
            # Switch to expert explanation
            pilot.press("Ctrl+X")
            xai_content = str(pilot.app.query_one("#xai-panel").renderable)
            assert "decision_tree" in xai_content or "expert" in xai_content.lower()

class TestTUIErrorHandling:
    """Test error display and educational feedback"""
    
    def test_error_display_educational(self):
        """Test errors display with educational feedback"""
        app = NixHumanityTUI()
        with TUITestApp(app) as pilot:
            # Submit invalid query
            pilot.click("#input-field")
            pilot.type("install nonexistent-package-xyz")
            pilot.press("Enter")
            pilot.wait_for_scheduled_animations()
            
            # Verify educational error display
            response_panel = pilot.app.query_one("#response-panel")
            error_content = str(response_panel.renderable)
            
            assert "not found" in error_content.lower()
            assert "try" in error_content.lower()  # Suggestions provided
            assert "search" in error_content.lower()  # Alternative suggested
    
    def test_error_recovery_suggestions(self):
        """Test error recovery suggestions appear"""
        app = NixHumanityTUI()
        with TUITestApp(app) as pilot:
            # Submit typo query
            pilot.click("#input-field")
            pilot.type("install fierfix")  # Common typo
            pilot.press("Enter")
            pilot.wait_for_scheduled_animations()
            
            # Verify typo correction suggested
            response_content = str(pilot.app.query_one("#response-panel").renderable)
            assert "firefox" in response_content.lower()  # Correction suggested
            assert "did you mean" in response_content.lower() or "installing firefox" in response_content.lower()

class TestTUIAccessibility:
    """Test accessibility features for all personas"""
    
    def test_keyboard_navigation_complete(self):
        """Test 100% keyboard navigation (for Alex - blind developer)"""
        app = NixHumanityTUI(persona="alex_blind")
        with TUITestApp(app) as pilot:
            # Test tab navigation through all interactive elements
            pilot.press("Tab")  # Should focus input field
            focused = pilot.app.focused
            assert focused.id == "input-field"
            
            pilot.press("Tab")  # Should focus next interactive element
            # Continue testing tab order...
            
            # Test all keyboard shortcuts work
            pilot.press("Ctrl+H")  # Help
            pilot.press("Ctrl+X")  # XAI toggle
            pilot.press("Ctrl+E")  # Examples
            pilot.press("Ctrl+Q")  # Quit
    
    def test_screen_reader_attributes(self):
        """Test screen reader accessibility attributes"""
        app = NixHumanityTUI(persona="alex_blind")
        with TUITestApp(app) as pilot:
            # Verify ARIA attributes
            input_field = pilot.app.query_one("#input-field")
            assert input_field.has_attribute("aria-label")
            assert input_field.get_attribute("aria-label") == "Natural language command input"
            
            response_panel = pilot.app.query_one("#response-panel")
            assert response_panel.has_attribute("aria-live")
            assert response_panel.get_attribute("aria-live") == "polite"

class TestTUIPerformance:
    """Test TUI performance requirements"""
    
    def test_maya_adhd_speed_requirement(self):
        """Test <1 second response for Maya (ADHD persona)"""
        app = NixHumanityTUI(persona="maya_adhd")
        with TUITestApp(app) as pilot:
            import time
            
            # Submit simple query
            start_time = time.perf_counter()
            pilot.click("#input-field")
            pilot.type("install firefox")
            pilot.press("Enter")
            
            # Wait for response
            pilot.wait_for_scheduled_animations()
            
            # Verify response appears
            response_panel = pilot.app.query_one("#response-panel")
            assert len(str(response_panel.renderable)) > 0
            
            # Verify <1 second requirement
            duration = time.perf_counter() - start_time
            assert duration < 1.0, f"Maya needs <1s, took {duration:.3f}s"
    
    def test_memory_usage_stability(self):
        """Test TUI doesn't leak memory during extended use"""
        import psutil
        import os
        
        app = NixHumanityTUI()
        with TUITestApp(app) as pilot:
            # Baseline memory
            process = psutil.Process(os.getpid())
            baseline_memory = process.memory_info().rss
            
            # Simulate extended use
            for i in range(100):
                pilot.click("#input-field")
                pilot.type(f"help command {i}")
                pilot.press("Enter")
                pilot.wait_for_scheduled_animations()
                
                # Clear for next iteration
                pilot.press("Ctrl+L")  # Clear if available
            
            # Check memory didn't grow excessively
            final_memory = process.memory_info().rss
            memory_growth = final_memory - baseline_memory
            
            # Allow reasonable growth (< 50MB for 100 operations)
            assert memory_growth < 50 * 1024 * 1024, f"Memory grew by {memory_growth / 1024 / 1024:.1f}MB"

    def get_persona_style_expectations(self, persona):
        """Helper method to get persona-specific style expectations"""
        return {
            "maya_adhd": {"style": "minimal", "contrast": "high", "animations": "reduced"},
            "grandma_rose": {"text_size": "large", "colors": "warm", "complexity": "low"},
            "alex_blind": {"aria": "complete", "keyboard": "full", "audio": "optimized"},
            "dr_sarah": {"detail": "high", "technical": "available", "efficient": "true"},
            "carlos_learner": {"educational": "true", "encouraging": "true", "patient": "true"}
        }
```

### Target 2: CLI Adapter Testing (0% → 95%) - 92 Lines Impact

**File**: `src/nix_for_humanity/adapters/cli_adapter.py`  
**Current Coverage**: 0% (92 lines uncovered)  
**User Impact**: CRITICAL - Primary command-line interface

#### CLI Adapter Test Suite Plan:

```python
# tests/adapters/test_cli_adapter_comprehensive.py
"""
Comprehensive CLI Adapter testing covering all command-line interactions
Priority: CRITICAL - Primary interface with 0% coverage
"""

import pytest
from unittest.mock import Mock, patch
from nix_for_humanity.adapters.cli_adapter import CLIAdapter

class TestCLIAdapterCore:
    """Core CLI adapter functionality"""
    
    def test_adapter_initialization(self):
        """Test CLI adapter initializes with proper configuration"""
        adapter = CLIAdapter()
        
        assert adapter.backend is not None
        assert adapter.personality == "friendly"  # Default
        assert adapter.output_format == "rich"   # Default
        assert hasattr(adapter, 'process_query')
    
    def test_query_processing_flow(self):
        """Test complete query processing flow"""
        adapter = CLIAdapter()
        
        # Mock backend response
        mock_response = {
            "intent": "install_package",
            "response": {"text": "Installing Firefox..."},
            "xai_explanation": {"why": "Firefox is a popular browser"},
            "success": True
        }
        
        with patch.object(adapter.backend, 'process_query', return_value=mock_response):
            result = adapter.process_query("install firefox")
            
            assert result['success'] is True
            assert "firefox" in result['response']['text'].lower()
            assert result['xai_explanation']['why'] is not None

class TestCLIPersonalityAdaptation:
    """Test personality-specific CLI adaptations"""
    
    @pytest.mark.parametrize("personality,expected_style", [
        ("minimal", "brief"),
        ("friendly", "conversational"),
        ("technical", "precise"),
        ("encouraging", "supportive"),
        ("symbiotic", "learning-focused")
    ])
    def test_personality_response_styling(self, personality, expected_style):
        """Test CLI adapts responses for each personality"""
        adapter = CLIAdapter(personality=personality)
        
        mock_response = {
            "intent": "install_package",
            "response": {"text": "Installing Firefox..."},
            "success": True
        }
        
        with patch.object(adapter.backend, 'process_query', return_value=mock_response):
            result = adapter.process_query("install firefox")
            formatted_output = adapter.format_output(result)
            
            if personality == "minimal":
                # Minimal should be brief
                assert len(formatted_output.split('\n')) <= 3
                assert "Installing Firefox" in formatted_output
            elif personality == "friendly":
                # Friendly should be conversational
                assert any(word in formatted_output.lower() for word in ["great", "sure", "happy to"])
            elif personality == "technical":
                # Technical should include details
                assert "firefox" in formatted_output.lower()
                assert len(formatted_output) > 50  # More detailed
            elif personality == "encouraging":
                # Encouraging should be supportive
                assert any(word in formatted_output.lower() for word in ["excellent", "good", "well done"])

class TestCLIOutputFormatting:
    """Test CLI output formatting for different modes"""
    
    def test_rich_output_formatting(self):
        """Test rich text output formatting"""
        adapter = CLIAdapter(output_format="rich")
        
        response = {
            "intent": "install_package",
            "response": {"text": "Installing Firefox..."},
            "xai_explanation": {"why": "Firefox is popular", "confidence": 0.95},
            "success": True
        }
        
        formatted = adapter.format_output(response)
        
        # Rich format should include colors/styling markers
        assert "[green]" in formatted or "[bold]" in formatted
        assert "Installing Firefox" in formatted
        assert "95%" in formatted  # Confidence displayed
    
    def test_plain_output_formatting(self):
        """Test plain text output formatting"""
        adapter = CLIAdapter(output_format="plain")
        
        response = {
            "intent": "install_package", 
            "response": {"text": "Installing Firefox..."},
            "success": True
        }
        
        formatted = adapter.format_output(response)
        
        # Plain format should be clean text
        assert "[green]" not in formatted
        assert "[bold]" not in formatted
        assert "Installing Firefox" in formatted
    
    def test_json_output_formatting(self):
        """Test JSON output formatting"""
        adapter = CLIAdapter(output_format="json")
        
        response = {
            "intent": "install_package",
            "response": {"text": "Installing Firefox..."},
            "success": True
        }
        
        formatted = adapter.format_output(response)
        
        # Should be valid JSON
        import json
        parsed = json.loads(formatted)
        assert parsed["success"] is True
        assert parsed["intent"] == "install_package"

class TestCLIErrorHandling:
    """Test CLI error handling and educational feedback"""
    
    def test_error_formatting_educational(self):
        """Test errors are formatted with educational content"""
        adapter = CLIAdapter()
        
        error_response = {
            "success": False,
            "error": {
                "type": "package_not_found",
                "message": "Package 'fierfix' not found",
                "suggestions": ["Try 'firefox' instead", "Search with 'search browser'"],
                "educational": "Firefox is the correct spelling for the popular browser"
            }
        }
        
        formatted = adapter.format_output(error_response)
        
        assert "not found" in formatted.lower()
        assert "try 'firefox'" in formatted.lower()
        assert "search" in formatted.lower()
        assert "firefox is the correct spelling" in formatted.lower()
    
    def test_security_error_handling(self):
        """Test security errors are handled appropriately"""
        adapter = CLIAdapter()
        
        security_response = {
            "success": False,
            "error": {
                "type": "security_violation",
                "message": "Dangerous command detected",
                "educational": "Commands with ';' can be unsafe. Try rephrasing without special characters."
            }
        }
        
        formatted = adapter.format_output(security_response)
        
        assert "dangerous" in formatted.lower() or "unsafe" in formatted.lower()
        assert "try rephrasing" in formatted.lower()
        assert "special characters" in formatted.lower()

class TestCLIStreamingOutput:
    """Test streaming output for long operations"""
    
    def test_progress_streaming(self):
        """Test progress updates stream correctly"""
        adapter = CLIAdapter()
        
        # Mock streaming response
        progress_updates = [
            {"type": "progress", "message": "Downloading...", "percent": 25},
            {"type": "progress", "message": "Installing...", "percent": 75},
            {"type": "complete", "message": "Done!", "percent": 100}
        ]
        
        with patch.object(adapter.backend, 'process_query_stream') as mock_stream:
            mock_stream.return_value = iter(progress_updates)
            
            outputs = list(adapter.process_query_stream("install large-package"))
            
            assert len(outputs) == 3
            assert outputs[0]["message"] == "Downloading..."
            assert outputs[1]["percent"] == 75
            assert outputs[2]["type"] == "complete"

class TestCLIAccessibility:
    """Test CLI accessibility features"""
    
    def test_screen_reader_compatibility(self):
        """Test output is screen-reader friendly"""
        adapter = CLIAdapter(accessibility_mode=True)
        
        response = {
            "intent": "system_status",
            "response": {"text": "System is up to date"},
            "success": True
        }
        
        formatted = adapter.format_output(response)
        
        # Should avoid complex formatting for screen readers
        assert "[progress bar]" not in formatted  # Should be text description
        assert "System is up to date" in formatted
        # Should include verbal cues
        assert formatted.endswith(".")  # Proper sentence ending
    
    def test_high_contrast_mode(self):
        """Test high contrast output mode"""
        adapter = CLIAdapter(high_contrast=True)
        
        response = {
            "intent": "install_package",
            "response": {"text": "Installing Firefox..."},
            "success": True
        }
        
        formatted = adapter.format_output(response)
        
        # High contrast should use strong color choices
        assert "[bright_white]" in formatted or "[black on white]" in formatted

class TestCLIPerformance:
    """Test CLI performance requirements"""
    
    def test_response_time_under_budget(self):
        """Test CLI responses meet performance budgets"""
        adapter = CLIAdapter()
        
        import time
        
        # Mock fast backend response
        with patch.object(adapter.backend, 'process_query') as mock_process:
            mock_process.return_value = {
                "intent": "help",
                "response": {"text": "Available commands..."},
                "success": True
            }
            
            start_time = time.perf_counter()
            result = adapter.process_query("help")
            duration = time.perf_counter() - start_time
            
            # CLI adapter overhead should be minimal (<50ms)
            assert duration < 0.05, f"CLI adapter took {duration:.3f}s, should be <0.05s"
    
    def test_memory_efficiency(self):
        """Test CLI adapter is memory efficient"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss
        
        # Create multiple adapters
        adapters = [CLIAdapter() for _ in range(10)]
        
        # Process queries
        for i, adapter in enumerate(adapters):
            with patch.object(adapter.backend, 'process_query') as mock:
                mock.return_value = {"success": True, "response": {"text": f"Response {i}"}}
                adapter.process_query(f"query {i}")
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - baseline_memory
        
        # Should not grow excessively (< 10MB for 10 adapters)
        assert memory_growth < 10 * 1024 * 1024, f"Memory grew by {memory_growth / 1024 / 1024:.1f}MB"

class TestCLIIntegration:
    """Test CLI adapter integration with backend"""
    
    def test_backend_error_propagation(self):
        """Test backend errors are properly handled"""
        adapter = CLIAdapter()
        
        # Mock backend exception
        with patch.object(adapter.backend, 'process_query') as mock_process:
            mock_process.side_effect = Exception("Backend connection failed")
            
            result = adapter.process_query("install firefox")
            
            assert result['success'] is False
            assert "error" in result
            assert "connection" in result['error']['message'].lower()
    
    def test_backend_timeout_handling(self):
        """Test backend timeout scenarios"""
        adapter = CLIAdapter(timeout=1.0)  # 1 second timeout
        
        import time
        
        # Mock slow backend
        def slow_response(*args, **kwargs):
            time.sleep(2.0)  # Longer than timeout
            return {"success": True}
        
        with patch.object(adapter.backend, 'process_query', side_effect=slow_response):
            result = adapter.process_query("install firefox")
            
            assert result['success'] is False
            assert "timeout" in result['error']['message'].lower()
```

## 📊 Expected Impact

### Coverage Jump Projection:
- **TUI App**: 192 lines covered = ~15% overall coverage increase
- **CLI Adapter**: 92 lines covered = ~7% overall coverage increase
- **Total Impact**: 284 lines = ~22% coverage increase
- **Result**: 60% → 82% overall coverage (approaching 85% target)

### User Experience Benefits:
- **Primary interfaces** fully tested and reliable
- **All 10 personas** validated in both CLI and TUI
- **Error handling** comprehensive and educational
- **Accessibility** features thoroughly tested
- **Performance budgets** enforced for all personas

## 🚀 Implementation Timeline

### Week 1: TUI App Testing Blitz
- Implement comprehensive TUI test suite
- Focus on persona adaptation and XAI integration
- Validate accessibility features
- **Target**: TUI App 0% → 95%

### Week 2: CLI Adapter Excellence  
- Implement complete CLI adapter test suite
- Test all output formats and personalities
- Validate streaming and error handling
- **Target**: CLI Adapter 0% → 95%

### Week 3: Integration & Refinement
- Integration testing between TUI and CLI
- Performance optimization based on test findings
- Bug fixes and edge case handling
- **Target**: Overall coverage 60% → 85%

## Success Metrics

- **TUI App Coverage**: 0% → 95% ✅
- **CLI Adapter Coverage**: 0% → 95% ✅  
- **Overall Project Coverage**: 60% → 85% ✅
- **User Experience**: All 10 personas successfully tested ✅
- **Performance**: All response time budgets met ✅
- **Accessibility**: WCAG AAA compliance maintained ✅

This strategic approach ensures maximum user benefit while efficiently reaching our coverage targets. Ready to begin implementation?