#!/usr/bin/env python3
"""
Unit tests for the ResponseGenerator component
"""

import unittest
from pathlib import Path

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from luminous_nix.core.responses import ResponseGenerator
from luminous_nix.core.personality import PersonalityStyle


class TestResponseGenerator(unittest.TestCase):
    """Test the ResponseGenerator component"""
    
    def setUp(self):
        """Create personality system for testing"""
        self.system = ResponseGenerator()
        
    def test_initialization(self):
        """Test personality system initialization"""
        self.assertEqual(self.system.current_style, PersonalityStyle.FRIENDLY)
        self.assertIsNotNone(self.system.user_preferences)
        
    def test_set_style(self):
        """Test setting personality style"""
        # Test valid styles
        for style in PersonalityStyle:
            self.system.set_style(style)
            self.assertEqual(self.system.current_style, style)
            
        # Test that set_style returns the style
        self.system.set_style(PersonalityStyle.MINIMAL)
        self.assertEqual(self.system.current_style, PersonalityStyle.MINIMAL)
        
    def test_minimal_personality(self):
        """Test minimal personality style"""
        self.system.set_style(PersonalityStyle.MINIMAL)
        
        response = "Here is the information you requested."
        adapted = self.system.adapt_response(response, "install firefox")
        
        # Minimal should return response as-is
        self.assertEqual(adapted, response)
        
    def test_friendly_personality(self):
        """Test friendly personality style"""
        self.system.set_style(PersonalityStyle.FRIENDLY)
        
        response = "Installing firefox..."
        adapted = self.system.adapt_response(response, "install firefox")
        
        # Friendly should add greeting and emoji
        self.assertIn("Hi there!", adapted)
        self.assertIn("😊", adapted)
        self.assertIn(response, adapted)
        
    def test_encouraging_personality(self):
        """Test encouraging personality style"""
        self.system.set_style(PersonalityStyle.ENCOURAGING)
        
        response = "Package installed."
        adapted = self.system.adapt_response(response, "install vim")
        
        # Encouraging should be supportive
        self.assertIn("Great", adapted)
        self.assertIn("awesome", adapted.lower())
        self.assertIn("🌟", adapted)
        
    def test_technical_personality(self):
        """Test technical personality style"""
        self.system.set_style(PersonalityStyle.TECHNICAL)
        
        response = "Updating system."
        adapted = self.system.adapt_response(response, "update_system")
        
        # Technical style just returns the response as-is based on the actual implementation
        self.assertEqual(adapted, response)
        
    def test_adaptive_personality(self):
        """Test adaptive personality style"""
        self.system.set_style(PersonalityStyle.ADAPTIVE)
        
        response = "Installing package."
        adapted = self.system.adapt_response(response, "install firefox")
        
        # Adaptive should match the actual implementation
        # Based on the code, adaptive returns the response as-is
        self.assertEqual(adapted, response)
        
    def test_symbiotic_personality(self):
        """Test symbiotic personality style"""
        self.system.set_style(PersonalityStyle.SYMBIOTIC)
        
        response = "Firefox installed."
        adapted = self.system.adapt_response(response, "install firefox")
        
        # Symbiotic should invite partnership
        self.assertIn("🤝", adapted)
        self.assertIn("learning", adapted.lower())
        
    def test_personality_for_errors(self):
        """Test personality adaptation for error messages"""
        error_response = "Error: Package not found"
        
        # Friendly should add emoji to errors
        self.system.set_style(PersonalityStyle.FRIENDLY)
        adapted = self.system.adapt_response(error_response, "install xyz")
        self.assertIn("Hi there!", adapted)
        
        # Technical should keep errors as-is
        self.system.set_style(PersonalityStyle.TECHNICAL)
        adapted = self.system.adapt_response(error_response, "install xyz")
        self.assertEqual(adapted, error_response)
        
    def test_personality_style_enum(self):
        """Test PersonalityStyle enum values"""
        # Check all expected styles exist
        expected_styles = [
            'minimal', 'friendly', 'encouraging', 
            'technical', 'symbiotic', 'adaptive'
        ]
        
        actual_styles = [style.value for style in PersonalityStyle]
        for expected in expected_styles:
            self.assertIn(expected, actual_styles)
            
    def test_adapt_response_preserves_content(self):
        """Test that adapt_response always includes original content"""
        original = "Important information about your system"
        
        for style in PersonalityStyle:
            self.system.set_style(style)
            adapted = self.system.adapt_response(original, "query")
            
            # Original content should always be preserved
            if style != PersonalityStyle.MINIMAL:
                self.assertIn(original, adapted, 
                    f"Style {style} did not preserve original content")
                    
    def test_empty_response_handling(self):
        """Test handling of empty responses"""
        self.system.set_style(PersonalityStyle.FRIENDLY)
        
        # Empty response should still get personality
        adapted = self.system.adapt_response("", "help")
        self.assertGreater(len(adapted), 0)
        self.assertIn("Hi there!", adapted)
        
    def test_long_response_handling(self):
        """Test handling of very long responses"""
        long_response = "Line 1\n" * 100  # 100 lines
        
        self.system.set_style(PersonalityStyle.FRIENDLY)
        adapted = self.system.adapt_response(long_response, "list packages")
        
        # Should preserve all content
        self.assertIn(long_response, adapted)
        
    def test_special_characters_in_response(self):
        """Test responses with special characters"""
        response = "Install with: nix-env -iA nixos.firefox-bin"
        
        self.system.set_style(PersonalityStyle.TECHNICAL)
        adapted = self.system.adapt_response(response, "install firefox")
        
        # Special characters should be preserved
        self.assertIn("nix-env -iA", adapted)
        self.assertIn("nixos.firefox-bin", adapted)


    def test_learn_preference(self):
        """Test user preference learning"""
        user_id = "test_user_123"
        
        # Learn a preference
        self.system.learn_preference(user_id, PersonalityStyle.TECHNICAL)
        
        # Verify it was stored
        self.assertEqual(self.system.get_user_style(user_id), PersonalityStyle.TECHNICAL)
        
        # Learn a different preference
        self.system.learn_preference(user_id, PersonalityStyle.MINIMAL)
        self.assertEqual(self.system.get_user_style(user_id), PersonalityStyle.MINIMAL)
        
    def test_get_user_style(self):
        """Test retrieving user style preferences"""
        # Non-existent user should return current style (not None)
        self.assertEqual(self.system.get_user_style("unknown_user"), self.system.current_style)
        
        # Learn preferences for multiple users
        self.system.learn_preference("user1", PersonalityStyle.FRIENDLY)
        self.system.learn_preference("user2", PersonalityStyle.SYMBIOTIC)
        
        # Verify each user's preference is maintained separately
        self.assertEqual(self.system.get_user_style("user1"), PersonalityStyle.FRIENDLY)
        self.assertEqual(self.system.get_user_style("user2"), PersonalityStyle.SYMBIOTIC)
        
    def test_get_style_description(self):
        """Test getting human-readable style descriptions"""
        # Test specific style descriptions
        minimal_desc = self.system.get_style_description(PersonalityStyle.MINIMAL)
        self.assertIn("facts", minimal_desc.lower())
        
        friendly_desc = self.system.get_style_description(PersonalityStyle.FRIENDLY)
        self.assertIn("warm", friendly_desc.lower())
        
        encouraging_desc = self.system.get_style_description(PersonalityStyle.ENCOURAGING)
        self.assertIn("support", encouraging_desc.lower())
        
        technical_desc = self.system.get_style_description(PersonalityStyle.TECHNICAL)
        self.assertIn("technical", technical_desc.lower())
        
        symbiotic_desc = self.system.get_style_description(PersonalityStyle.SYMBIOTIC)
        self.assertIn("learning", symbiotic_desc.lower())
        
        adaptive_desc = self.system.get_style_description(PersonalityStyle.ADAPTIVE)
        self.assertIn("adjust", adaptive_desc.lower())
        
    def test_adaptive_response_method(self):
        """Test the _adaptive_response private method behavior"""
        self.system.set_style(PersonalityStyle.ADAPTIVE)
        
        # Test with help query - should use encouraging style
        help_response = self.system.adapt_response("Here are the available commands.", "help")
        self.assertIn("Great question!", help_response)
        self.assertIn("You're doing awesome", help_response)
        
        # Test with technical query - should use technical style
        tech_response = self.system.adapt_response("Configuration updated.", "update config")
        # Technical style returns the response as-is (no modification)
        self.assertEqual(tech_response, "Configuration updated.")
        
        # Test with polite query - should use friendly style
        polite_response = self.system.adapt_response("Installation complete.", "please install firefox")
        self.assertIn("Hi there!", polite_response)
        self.assertIn("😊", polite_response)
        
        # Test with terse query - should use minimal style
        terse_response = self.system.adapt_response("Done.", "ls")
        self.assertEqual(terse_response, "Done.")
        
    def test_style_consistency_across_sessions(self):
        """Test that style preferences are maintained consistently"""
        # Set a style and adapt multiple responses
        self.system.set_style(PersonalityStyle.FRIENDLY)
        
        responses = []
        for i in range(5):
            response = self.system.adapt_response(f"Command {i} executed.", f"command{i}")
            responses.append(response)
            
        # All responses should have consistent friendly style
        for response in responses:
            self.assertIn("Hi there!", response)
            self.assertIn("😊", response)
            
    def test_edge_case_none_style(self):
        """Test handling when style is explicitly set to None"""
        # This should use the current style
        response = self.system.adapt_response("Test response", "test", style=None)
        
        # Should use the default FRIENDLY style
        self.assertIn("Hi there!", response)
        
    def test_concurrent_user_preferences(self):
        """Test that multiple users' preferences don't interfere"""
        users = ["alice", "bob", "charlie", "diana", "eve"]
        styles = list(PersonalityStyle)
        
        # Each user learns a different style
        for user, style in zip(users, styles):
            self.system.learn_preference(user, style)
            
        # Verify all preferences are maintained correctly
        for user, expected_style in zip(users, styles):
            actual_style = self.system.get_user_style(user)
            self.assertEqual(actual_style, expected_style)
            
    def test_response_adaptation_with_override(self):
        """Test that style parameter overrides current style"""
        self.system.set_style(PersonalityStyle.MINIMAL)
        
        # Override with different style
        response = self.system.adapt_response(
            "Installation complete.", 
            "install package",
            style=PersonalityStyle.ENCOURAGING
        )
        
        # Should use encouraging style, not minimal
        self.assertIn("Great", response)
        self.assertIn("🌟", response)
        
        # Verify current style wasn't changed
        self.assertEqual(self.system.current_style, PersonalityStyle.MINIMAL)
        
    def test_empty_query_handling(self):
        """Test adaptation with empty query string"""
        response = self.system.adapt_response("System ready", "")
        
        # Should still apply personality
        self.assertIn("Hi there!", response)
        
    def test_very_long_query_handling(self):
        """Test adaptation with very long query"""
        long_query = "install " + " ".join([f"package{i}" for i in range(100)])
        response = self.system.adapt_response("Processing request", long_query)
        
        # Should handle without issues
        self.assertIsNotNone(response)
        self.assertIn("Processing request", response)
        
    def test_special_characters_in_query(self):
        """Test queries with special characters"""
        queries = [
            "install $PACKAGE_NAME",
            "remove package@version",
            "update system && reboot",
            "search for \"exact phrase\"",
            "install package; echo done"
        ]
        
        for query in queries:
            response = self.system.adapt_response("Command processed", query)
            self.assertIn("Command processed", response)
            
    def test_personality_description_completeness(self):
        """Test that all personalities have descriptions"""
        for style in PersonalityStyle:
            description = self.system.get_style_description(style)
            self.assertIsNotNone(description)
            self.assertGreater(len(description), 10)  # Should be meaningful description
            
    def test_multiline_response_handling(self):
        """Test handling of multiline responses"""
        multiline_response = """Line 1: Starting process
Line 2: Processing...
Line 3: Complete"""
        
        self.system.set_style(PersonalityStyle.FRIENDLY)
        adapted = self.system.adapt_response(multiline_response, "complex task")
        
        # Should preserve all lines
        self.assertIn("Line 1", adapted)
        self.assertIn("Line 2", adapted)
        self.assertIn("Line 3", adapted)
        
        # Should add personality
        self.assertIn("Hi there!", adapted)


if __name__ == '__main__':
    unittest.main()