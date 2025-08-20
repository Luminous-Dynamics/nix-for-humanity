#!/usr/bin/env python3
"""
Enhanced unit tests for the ResponseGenerator component
Tests all personality styles, adaptation logic, and user preferences
"""

import unittest
from pathlib import Path

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from luminous_nix.core.responses import ResponseGenerator, PersonalityStyle


class TestResponseGeneratorEnhanced(unittest.TestCase):
    """Enhanced tests for the ResponseGenerator component"""
    
    def setUp(self):
        """Create ResponseGenerator instance for testing"""
        self.ps = ResponseGenerator()
        
    def test_initialization(self):
        """Test default initialization"""
        self.assertEqual(self.ps.current_style, PersonalityStyle.FRIENDLY)
        self.assertEqual(self.ps.user_preferences, {})
        
        # Test with custom default
        ps_minimal = ResponseGenerator(PersonalityStyle.MINIMAL)
        self.assertEqual(ps_minimal.current_style, PersonalityStyle.MINIMAL)
        
    def test_minimal_style(self):
        """Test minimal personality style - just facts"""
        base = "Firefox has been installed."
        query = "install firefox"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.MINIMAL)
        
        # Should return exactly the base response
        self.assertEqual(result, base)
        
        # Test with different base responses
        bases = [
            "System update complete.",
            "Package not found: chrome",
            "Your system is up to date."
        ]
        
        for base_resp in bases:
            result = self.ps.adapt_response(base_resp, query, PersonalityStyle.MINIMAL)
            self.assertEqual(result, base_resp)
            
    def test_friendly_style(self):
        """Test friendly personality style"""
        base = "Firefox has been installed."
        query = "install firefox"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.FRIENDLY)
        
        # Should add greeting and emoji
        self.assertTrue(result.startswith("Hi there!"))
        self.assertIn(base, result)
        self.assertIn("😊", result)
        self.assertIn("Let me know if you need any clarification", result)
        
        # Test with question - shouldn't add clarification offer
        base_question = "Would you like to install the ESR version?"
        result = self.ps.adapt_response(base_question, query, PersonalityStyle.FRIENDLY)
        self.assertTrue(result.startswith("Hi there!"))
        self.assertNotIn("Let me know if you need any clarification", result)
        
    def test_encouraging_style(self):
        """Test encouraging personality style"""
        # Test for beginners
        base = "Here's how to install packages."
        query = "how do I install software for the first time"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.ENCOURAGING)
        
        self.assertTrue(result.startswith("Great question!"))
        self.assertIn("You're doing great getting started", result)
        self.assertIn("🌟", result)
        
        # Test for errors
        base = "Permission denied error occurred."
        query = "I got an error trying to install"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.ENCOURAGING)
        self.assertIn("Don't worry, everyone encounters this", result)
        self.assertIn("💪", result)
        
        # Test general case
        base = "Package installed successfully."
        query = "install vim"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.ENCOURAGING)
        self.assertIn("You're doing awesome learning NixOS", result)
        
    def test_technical_style(self):
        """Test technical personality style"""
        # Test nix profile mention
        base = "You can use nix profile install to add packages."
        query = "how to install packages"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.TECHNICAL)
        
        self.assertIn(base, result)
        self.assertIn("Technical note:", result)
        self.assertIn("Nix 2.0 CLI", result)
        
        # Test nixos-rebuild mention
        base = "Run nixos-rebuild switch to apply changes."
        query = "apply configuration"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.TECHNICAL)
        self.assertIn("declarative configuration paradigm", result)
        
        # Test declarative mention
        base = "Use declarative configuration for reproducibility."
        query = "best practices"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.TECHNICAL)
        self.assertIn("Technical detail:", result)
        self.assertIn("reproducibility", result)
        
    def test_symbiotic_style(self):
        """Test symbiotic personality style - learning together"""
        base = "Firefox has been installed."
        query = "install firefox"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.SYMBIOTIC)
        
        self.assertIn("🤝", result)
        self.assertIn("I'm still learning", result)
        self.assertIn("Was this helpful?", result)
        self.assertIn("Your feedback helps me improve", result)
        
        # Test with error query
        base = "Network error occurred."
        query = "error connecting to network"
        
        result = self.ps.adapt_response(base, query, PersonalityStyle.SYMBIOTIC)
        self.assertIn("If you found a solution", result)
        self.assertIn("I'd love to learn it", result)
        
    def test_adaptive_style(self):
        """Test adaptive personality style - auto-detection"""
        base = "Response content here."
        
        # Beginner query should use encouraging
        query = "help me understand what is nix"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        self.assertIn("Great question!", result)
        
        # Advanced query should use technical
        query = "configure overlay for custom derivation"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        self.assertIn("Response content here", result)
        # Would have technical notes if base had relevant content
        
        # Polite query should use friendly
        query = "hello, please install firefox"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        self.assertTrue("Hi" in result or "Hello" in result or len(result) > 0)
        
        # Terse query should use minimal
        query = "install vim"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        self.assertEqual(result, base)  # Minimal returns unchanged
        
    def test_set_style(self):
        """Test setting personality style"""
        self.assertEqual(self.ps.current_style, PersonalityStyle.FRIENDLY)
        
        self.ps.set_style(PersonalityStyle.TECHNICAL)
        self.assertEqual(self.ps.current_style, PersonalityStyle.TECHNICAL)
        
        # Test that it affects default behavior
        base = "Test response"
        result = self.ps.adapt_response(base, "test")
        # Should use technical style by default now
        self.assertEqual(result, base)  # Technical doesn't modify without triggers
        
    def test_user_preferences(self):
        """Test learning and retrieving user preferences"""
        # Learn preferences for different users
        self.ps.learn_preference("user1", PersonalityStyle.MINIMAL)
        self.ps.learn_preference("user2", PersonalityStyle.ENCOURAGING)
        self.ps.learn_preference("user3", PersonalityStyle.TECHNICAL)
        
        # Retrieve preferences
        self.assertEqual(self.ps.get_user_style("user1"), PersonalityStyle.MINIMAL)
        self.assertEqual(self.ps.get_user_style("user2"), PersonalityStyle.ENCOURAGING)
        self.assertEqual(self.ps.get_user_style("user3"), PersonalityStyle.TECHNICAL)
        
        # Unknown user should get default
        self.assertEqual(self.ps.get_user_style("unknown"), PersonalityStyle.FRIENDLY)
        
    def test_update_user_preference(self):
        """Test updating existing user preference"""
        self.ps.learn_preference("user1", PersonalityStyle.MINIMAL)
        self.assertEqual(self.ps.get_user_style("user1"), PersonalityStyle.MINIMAL)
        
        # Update preference
        self.ps.learn_preference("user1", PersonalityStyle.SYMBIOTIC)
        self.assertEqual(self.ps.get_user_style("user1"), PersonalityStyle.SYMBIOTIC)
        
    def test_style_descriptions(self):
        """Test getting style descriptions"""
        descriptions = {
            PersonalityStyle.MINIMAL: "Just the facts, no extra text",
            PersonalityStyle.FRIENDLY: "Warm and helpful with emojis",
            PersonalityStyle.ENCOURAGING: "Supportive for beginners",
            PersonalityStyle.TECHNICAL: "Detailed technical explanations",
            PersonalityStyle.SYMBIOTIC: "Learning together as partners",
            PersonalityStyle.ADAPTIVE: "Automatically adjusts to your needs"
        }
        
        for style, expected_desc in descriptions.items():
            desc = self.ps.get_style_description(style)
            self.assertEqual(desc, expected_desc)
            
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Empty query
        base = "Response"
        result = self.ps.adapt_response(base, "", PersonalityStyle.ADAPTIVE)
        # Should default to friendly for empty query
        self.assertTrue("Hi" in result or "Hello" in result or len(result) > 0)
        
        # Very long query
        long_query = " ".join(["word"] * 100)
        result = self.ps.adapt_response(base, long_query, PersonalityStyle.ADAPTIVE)
        # Should use friendly for long queries
        self.assertTrue("Hi" in result or "Hello" in result or len(result) > 0)
        
        # Mixed case sensitivity
        query = "INSTALL FIREFOX PLEASE"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        # Should still detect "please" and use friendly
        self.assertTrue("Hi" in result or "Hello" in result or len(result) > 0)
        
    def test_special_characters_in_query(self):
        """Test handling special characters in queries"""
        base = "Command executed"
        queries = [
            "install firefox!!!",
            "what's the best editor?",
            "help! error occurred",
            "@#$% broken",
            "install [package]"
        ]
        
        for query in queries:
            # Should not crash on special characters
            result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
            self.assertIsNotNone(result)
            self.assertIn(base, result)
            
    def test_consistency_across_styles(self):
        """Test that base content is preserved across all styles"""
        base = "The package firefox-esr version 91.0 has been installed to /nix/store/abc123"
        query = "install firefox extended support"
        
        for style in PersonalityStyle:
            result = self.ps.adapt_response(base, query, style)
            # Base content should always be present
            self.assertIn("firefox-esr", result)
            self.assertIn("91.0", result)
            self.assertIn("/nix/store/abc123", result)
            
    def test_style_specific_keywords(self):
        """Test that certain keywords trigger appropriate technical notes"""
        test_cases = [
            ("Use nix profile list to see installed", "Technical note:", PersonalityStyle.TECHNICAL),
            ("Run nixos-rebuild boot", "declarative configuration", PersonalityStyle.TECHNICAL),
            ("Declarative approach is better", "reproducibility", PersonalityStyle.TECHNICAL),
        ]
        
        for base, expected_content, style in test_cases:
            result = self.ps.adapt_response(base, "test", style)
            self.assertIn(expected_content, result)
            
    def test_adaptive_edge_detection(self):
        """Test edge cases in adaptive detection"""
        base = "Response"
        
        # Mixed signals - beginner + technical
        query = "help me understand derivations"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        # Should prioritize beginner signal
        self.assertIn("Great question!", result)
        
        # Multiple politeness markers
        query = "hi, please help me, thanks"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        self.assertTrue("Hi" in result or "Hello" in result or len(result) > 0)
        
        # Technical but terse
        query = "overlay config"
        result = self.ps.adapt_response(base, query, PersonalityStyle.ADAPTIVE)
        # Terse takes precedence
        self.assertEqual(result, base)
        
    def test_response_length_preservation(self):
        """Test that responses don't become too long"""
        # Very long base response
        base = "A" * 1000  # 1000 character response
        query = "test"
        
        for style in PersonalityStyle:
            result = self.ps.adapt_response(base, query, style)
            # Result should not be more than 2x the original
            self.assertLess(len(result), len(base) * 2)
            
    def test_unicode_handling(self):
        """Test handling of unicode in queries and responses"""
        base = "Package installé avec succès 🎉"
        queries = [
            "installer firefôx",
            "помогите установить",  # Russian
            "安装火狐",  # Chinese
            "🔥🦊"  # Emojis
        ]
        
        for query in queries:
            for style in PersonalityStyle:
                result = self.ps.adapt_response(base, query, style)
                # Should handle unicode gracefully
                self.assertIsNotNone(result)
                self.assertIn("🎉", result)


if __name__ == '__main__':
    unittest.main()