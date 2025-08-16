#!/usr/bin/env python3
"""
Unit tests for the ResponseGenerator component.
Tests the actual implementation that generates educational two-path responses.
"""

import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from luminous_nix.core.responses import ResponseGenerator, Response, SolutionPath, PathType

class TestResponseGenerator(unittest.TestCase):
    """Test the ResponseGenerator class"""

    def setUp(self):
        """Set up test instance"""
        self.generator = ResponseGenerator()

    def test_initialization(self):
        """Test ResponseGenerator initialization"""
        self.assertIsNotNone(self.generator)
        self.assertIsNotNone(self.generator.templates)
        self.assertIn("install_package", self.generator.templates)
        self.assertIn("update_system", self.generator.templates)
        self.assertIn("remove_package", self.generator.templates)
        self.assertIn("enable_service", self.generator.templates)

    def test_generate_install_package_response(self):
        """Test generating an install package response"""
        response = self.generator.generate(
            intent="install_package",
            context={"package": "firefox"}
        )
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent, "install_package")
        self.assertIn("firefox", response.summary.lower())
        self.assertIsNotNone(response.paths)
        self.assertGreater(len(response.paths), 0)
        
        # Check that we have different path types
        path_types = [path.path_type for path in response.paths]
        self.assertIn(PathType.IMPERATIVE, path_types)
        self.assertIn(PathType.DECLARATIVE, path_types)

    def test_generate_update_system_response(self):
        """Test generating an update system response"""
        response = self.generator.generate(
            intent="update_system",
            context={}
        )
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent, "update_system")
        self.assertIn("update", response.summary.lower())
        self.assertIsNotNone(response.paths)
        self.assertGreater(len(response.paths), 0)

    def test_generate_remove_package_response(self):
        """Test generating a remove package response"""
        response = self.generator.generate(
            intent="remove_package",
            context={"package": "vim"}
        )
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent, "remove_package")
        self.assertIn("remove", response.summary.lower())
        self.assertIsNotNone(response.paths)
        self.assertGreater(len(response.paths), 0)

    def test_generate_enable_service_response(self):
        """Test generating an enable service response"""
        response = self.generator.generate(
            intent="enable_service",
            context={"service": "nginx"}
        )
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.intent, "enable_service")
        self.assertIn("nginx", response.summary.lower())
        self.assertIsNotNone(response.paths)
        self.assertGreater(len(response.paths), 0)

    def test_unknown_intent_uses_default(self):
        """Test that unknown intents use the default template"""
        response = self.generator.generate(
            intent="unknown_intent",
            context={"query": "something"}
        )
        
        self.assertIsInstance(response, Response)
        # Default template sets intent to "unknown"
        self.assertEqual(response.intent, "unknown")
        # Default template should still provide a response
        self.assertIsNotNone(response.summary)

    def test_install_package_paths_structure(self):
        """Test the structure of install package solution paths"""
        response = self.generator.generate(
            intent="install_package",
            context={"package": "git"}
        )
        
        # Should have multiple paths
        self.assertGreaterEqual(len(response.paths), 2)
        
        # Check imperative path
        imperative_paths = [p for p in response.paths if p.path_type == PathType.IMPERATIVE]
        self.assertGreater(len(imperative_paths), 0)
        imperative = imperative_paths[0]
        
        self.assertIn("git", str(imperative.commands))
        self.assertFalse(imperative.requires_sudo)
        self.assertEqual(imperative.permanence, "user")
        self.assertFalse(imperative.reproducible)
        
        # Check declarative path
        declarative_paths = [p for p in response.paths if p.path_type == PathType.DECLARATIVE]
        self.assertGreater(len(declarative_paths), 0)
        declarative = declarative_paths[0]
        
        self.assertTrue(declarative.requires_sudo)
        self.assertEqual(declarative.permanence, "system")
        self.assertTrue(declarative.reproducible)

    def test_response_education_content(self):
        """Test that responses include educational content"""
        response = self.generator.generate(
            intent="install_package",
            context={"package": "neovim"}
        )
        
        # Should have educational content
        self.assertIsNotNone(response.education)
        self.assertIsNotNone(response.education.concept)
        self.assertIsNotNone(response.education.explanation)
        self.assertIsNotNone(response.education.why_it_matters)
        
        # Educational content should be relevant
        self.assertIn("declarative", response.education.explanation.lower())

    def test_response_dry_run_suggestion(self):
        """Test that responses include dry-run suggestions"""
        response = self.generator.generate(
            intent="install_package",
            context={"package": "htop"}
        )
        
        # Should have dry-run suggestion
        self.assertIsNotNone(response.dry_run)
        self.assertIn("htop", response.dry_run.command)
        self.assertIsNotNone(response.dry_run.description)

    def test_response_related_topics(self):
        """Test that responses include related topics"""
        response = self.generator.generate(
            intent="install_package",
            context={"package": "emacs"}
        )
        
        # Should have related topics
        self.assertIsNotNone(response.related_topics)
        self.assertIsInstance(response.related_topics, list)
        self.assertGreater(len(response.related_topics), 0)

    def test_empty_context_handling(self):
        """Test handling of empty context"""
        response = self.generator.generate(
            intent="install_package",
            context={}
        )
        
        # Should still generate a valid response with generic package
        self.assertIsInstance(response, Response)
        self.assertIn("package", response.summary.lower())

    def test_update_system_paths(self):
        """Test update system response paths"""
        response = self.generator.generate(
            intent="update_system",
            context={}
        )
        
        # Should have multiple update paths
        self.assertGreaterEqual(len(response.paths), 2)
        
        # Check for different update approaches
        titles = [path.title.lower() for path in response.paths]
        # Just verify we have different paths
        self.assertGreater(len(set(titles)), 1)  # More than one unique title

    def test_remove_package_with_specific_package(self):
        """Test remove package with specific package name"""
        response = self.generator.generate(
            intent="remove_package",
            context={"package": "firefox"}
        )
        
        # Package name should appear in commands
        all_commands = []
        for path in response.paths:
            all_commands.extend(path.commands)
        
        commands_str = " ".join(all_commands).lower()
        self.assertIn("firefox", commands_str)

    def test_service_enable_with_restart_option(self):
        """Test service enable includes restart information"""
        response = self.generator.generate(
            intent="enable_service",
            context={"service": "sshd"}
        )
        
        # Should mention both enable and start/restart
        all_commands = []
        for path in response.paths:
            all_commands.extend(path.commands)
        
        commands_str = " ".join(all_commands).lower()
        self.assertIn("enable", commands_str)
        self.assertTrue("start" in commands_str or "restart" in commands_str)

    def test_pros_and_cons_present(self):
        """Test that solution paths include pros and cons"""
        response = self.generator.generate(
            intent="install_package",
            context={"package": "zsh"}
        )
        
        for path in response.paths:
            self.assertIsNotNone(path.pros)
            self.assertIsNotNone(path.cons)
            self.assertIsInstance(path.pros, list)
            self.assertIsInstance(path.cons, list)
            self.assertGreater(len(path.pros), 0)
            self.assertGreater(len(path.cons), 0)

    def test_learn_more_links(self):
        """Test that some paths include learn_more links"""
        response = self.generator.generate(
            intent="install_package",
            context={"package": "docker"}
        )
        
        # At least one path should have a learn_more link
        has_learn_more = any(path.learn_more is not None for path in response.paths)
        self.assertTrue(has_learn_more)

    def test_warnings_field_exists(self):
        """Test that response has warnings field"""
        response = self.generator.generate(
            intent="update_system",
            context={}
        )
        
        self.assertIsNotNone(response.warnings)
        self.assertIsInstance(response.warnings, list)

if __name__ == "__main__":
    unittest.main()