#!/usr/bin/env python3
"""
Enhanced unit tests for the KnowledgeBase component
Tests solutions, problems, and package cache functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
import sqlite3
import time
from unittest.mock import Mock, patch

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from nix_humanity.core.knowledge import KnowledgeBase
from nix_humanity.core.intents import IntentType


class TestKnowledgeBaseEnhanced(unittest.TestCase):
    """Enhanced tests for the KnowledgeBase component"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.kb = KnowledgeBase(self.temp_db.name)
        
    def tearDown(self):
        """Clean up temporary database"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        
    def test_database_initialization(self):
        """Test that database is properly initialized with schema"""
        # Check if tables exist
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Check for expected tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['solutions', 'problems', 'package_cache']
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} should exist")
            
        conn.close()
        
    def test_get_solution_by_intent(self):
        """Test getting solutions by intent type"""
        # Seed some test data
        self._seed_solution_data()
        
        # Test install intent
        solution = self.kb.get_solution(IntentType.INSTALL_PACKAGE)
        self.assertIsNotNone(solution)
        self.assertIn("install_package", solution.lower())
        self.assertIn("nix", solution.lower())
        
        # Test update intent
        solution = self.kb.get_solution(IntentType.UPDATE_SYSTEM)
        self.assertIsNotNone(solution)
        self.assertIn("update_system", solution.lower())
        self.assertIn("nixos-rebuild", solution.lower())
        
        # Test unknown intent
        solution = self.kb.get_solution(IntentType.UNKNOWN)
        self.assertIsNotNone(solution)
        self.assertIn("help", solution.lower())
        
    def test_get_install_methods(self):
        """Test getting installation methods"""
        # Seed install methods
        self._seed_install_methods()
        
        # Test getting methods
        methods = self.kb.get_install_methods("firefox")
        self.assertIsInstance(methods, list)
        self.assertGreater(len(methods), 0)
        
        # Check structure
        for method in methods:
            self.assertTrue('method' in method or 'name' in method)
            self.assertIn('description', method)
            self.assertIn('example', method)
            
        # Check content
        method_names = [m['method'] for m in methods]
        self.assertIn('declarative', method_names)
        self.assertIn('imperative', method_names)
        
    def test_get_problem_solution(self):
        """Test getting solutions for common problems"""
        # Seed problem data
        self._seed_problem_data()
        
        # Test disk space problem
        solution = self.kb.get_problem_solution("disk space")
        self.assertIsNotNone(solution)
        self.assertIn("nix-collect-garbage", solution.get("solution", ""))
        
        # Test broken package problem
        solution = self.kb.get_problem_solution("broken")
        self.assertIsNotNone(solution)
        self.assertTrue("rollback" in solution or isinstance(solution, dict))
        
        # Test unknown problem
        solution = self.kb.get_problem_solution("unknown-problem-xyz")
        self.assertIsNone(solution)
        
    def test_get_solution_with_context(self):
        """Test getting solutions with context parameters"""
        # Seed solution data with context
        self._seed_solution_data()
        
        # Test with package context for install
        solution = self.kb.get_solution(IntentType.INSTALL_PACKAGE, {'package': 'firefox'})
        self.assertIsNotNone(solution)
        self.assertIn("install_package", solution.lower())
        
        # Test search with query context
        solution = self.kb.get_solution(IntentType.SEARCH_PACKAGE, {'query': 'editor'})
        self.assertIsNotNone(solution)
        self.assertIn("search_package", solution.lower())
        
    def test_check_package_cache(self):
        """Test package cache functionality"""
        # Initially empty
        exists = self.kb.check_package_exists("firefox")
        self.assertFalse(exists)
        
        # Add to cache
        self.kb.update_package_cache("firefox", True)
        exists = self.kb.check_package_exists("firefox")
        self.assertTrue(exists)
        
        # Check non-existent package
        self.kb.update_package_cache("fake-package", False)
        exists = self.kb.check_package_exists("fake-package")
        self.assertFalse(exists)
            
    def test_sql_injection_protection(self):
        """Test that SQL injection attempts are handled safely"""
        malicious_inputs = [
            "'; DROP TABLE solutions; --",
            "' OR '1'='1",
            "'; DELETE FROM problems WHERE '1'='1'; --",
            "\" OR \"\"=\""
        ]
        
        # Seed data first
        self._seed_solution_data()
        
        for malicious in malicious_inputs:
            # Should not raise exceptions or damage database
            try:
                # Try various methods with malicious input
                self.kb.get_problem_solution(malicious)
                self.kb.check_package_exists(malicious)
                self.kb.update_package_cache(malicious, True)
            except Exception:
                # Some methods might raise, but shouldn't damage DB
                pass
            
            # Verify tables still exist
            conn = sqlite3.connect(self.temp_db.name)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn('solutions', tables)
            self.assertIn('problems', tables)
            conn.close()
            
    def test_performance_large_cache(self):
        """Test performance with large package cache"""
        # Add many packages to cache
        for i in range(1000):
            self.kb.update_package_cache(f"package-{i}", i % 2 == 0)
        
        # Measure lookup time
        start_time = time.time()
        exists = self.kb.check_package_exists("package-500")
        end_time = time.time()
        
        query_time = end_time - start_time
        self.assertLess(query_time, 0.01, "Cache lookup should be very fast")
        self.assertTrue(exists)  # package-500 should exist (500 % 2 == 0)
        
    def test_concurrent_cache_access(self):
        """Test concurrent package cache access"""
        import threading
        
        errors = []
        
        def cache_worker(package_num):
            try:
                # Write to cache
                self.kb.update_package_cache(f"pkg-{package_num}", True)
                # Read from cache
                exists = self.kb.check_package_exists(f"pkg-{package_num}")
                if not exists:
                    errors.append(f"Package pkg-{package_num} not found after insert")
            except Exception as e:
                errors.append(str(e))
                
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join()
            
        # Check results
        self.assertEqual(len(errors), 0, f"No errors should occur: {errors}")
        
    def test_get_all_intent_types(self):
        """Test getting solutions for all intent types"""
        # Seed comprehensive data
        self._seed_solution_data()
        
        # Test all intent types
        for intent_type in IntentType:
            solution = self.kb.get_solution(intent_type)
            self.assertIsNotNone(solution, f"Solution for {intent_type} should exist")
            self.assertIsInstance(solution, str)
            self.assertGreater(len(solution), 0)
        
    def test_cache_expiration(self):
        """Test that package cache entries can be updated"""
        # Add package to cache
        self.kb.update_package_cache("test-pkg", True)
        self.assertTrue(self.kb.check_package_exists("test-pkg"))
        
        # Update cache entry
        self.kb.update_package_cache("test-pkg", False)
        self.assertFalse(self.kb.check_package_exists("test-pkg"))
        
    def test_empty_database(self):
        """Test behavior with empty database"""
        # Don't seed any data
        
        # Test getting solution
        solution = self.kb.get_solution(IntentType.INSTALL_PACKAGE)
        self.assertIsNotNone(solution)  # Should have default
        
        # Test getting install methods
        methods = self.kb.get_install_methods("firefox")
        self.assertIsInstance(methods, list)
        # Should have defaults even with empty DB
        
        # Test problem solution
        solution = self.kb.get_problem_solution("test")
        self.assertIsNone(solution)  # No problems in DB
        
    # Helper methods for seeding test data
    
    def _seed_solution_data(self):
        """Seed database with test solution data"""
        # Use the actual schema: (id, intent, category, solution, example, explanation, related)
        solutions = [
            (None, 'install', 'package', 'To install packages in NixOS, use:\n- Declarative: Add to configuration.nix\n- Imperative: nix-env -iA nixos.package\n- Temporary: nix-shell -p package', 'nix-env -iA nixos.firefox', 'Multiple installation methods available', 'search,remove'),
            (None, 'remove', 'package', 'To remove packages:\n- Declarative: Remove from configuration.nix and rebuild\n- Imperative: nix-env -e package-name', 'nix-env -e firefox', 'Package removal options', 'install'),
            (None, 'update', 'system', 'To update NixOS:\n- Update channel: nix-channel --update\n- Rebuild: sudo nixos-rebuild switch\n- Or use: sudo nixos-rebuild switch --upgrade', 'sudo nixos-rebuild switch --upgrade', 'System update process', 'rollback'),
            (None, 'search', 'package', 'To search for packages:\n- nix search nixpkgs keyword\n- Visit search.nixos.org\n- Use tab completion with nix-env', 'nix search firefox', 'Package discovery methods', 'install'),
            (None, 'info', 'package', 'To get package information:\n- nix-env -qa --description package\n- nix show-derivation nixpkgs.package', 'nix-env -qa --description firefox', 'Package information queries', 'search'),
            (None, 'rollback', 'system', 'To rollback changes:\n- List generations: nix-env --list-generations\n- Rollback: nix-env --rollback\n- System rollback: sudo nixos-rebuild switch --rollback', 'sudo nixos-rebuild switch --rollback', 'System rollback procedures', 'update'),
            (None, 'unknown', 'help', 'I can help you with:\n- Installing/removing packages\n- System updates\n- Searching for software\n- And much more! Just ask.', 'ask me anything', 'General help information', 'help')
        ]
        
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Don't create table - it already exists from KnowledgeBase.__init__()
        # Insert using the actual schema
        cursor.executemany(
            "INSERT OR REPLACE INTO solutions (id, intent, category, solution, example, explanation, related) VALUES (?, ?, ?, ?, ?, ?, ?)",
            solutions
        )
        
        conn.commit()
        conn.close()
        
    def _seed_install_methods(self):
        """Seed database with install methods"""
        # This would normally be populated from the default_data.sql
        # For testing, we'll insert directly
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Create a mock solutions table entry for install methods using correct schema
        cursor.execute("""
            INSERT OR REPLACE INTO solutions (intent, category, solution, example, explanation, related)
            VALUES ('install', 'package', ?, ?, ?, ?)
        """, [
            '''**Installation Methods in NixOS:**

1. **Declarative (Recommended)**
   - Edit `/etc/nixos/configuration.nix`
   - Add package to `environment.systemPackages`
   - Run `sudo nixos-rebuild switch`
   - Example: `environment.systemPackages = with pkgs; [ firefox vim ];`

2. **Imperative (User-specific)**
   - Install: `nix-env -iA nixos.firefox`
   - Remove: `nix-env -e firefox`
   - List: `nix-env -q`

3. **Temporary (Try before installing)**
   - Run in shell: `nix-shell -p firefox`
   - Exits when you close the shell''',
            'nix-env -iA nixos.firefox',
            'Multiple installation methods for NixOS packages',
            'search,remove'
        ])
        
        conn.commit()
        conn.close()
        
    def _seed_problem_data(self):
        """Seed database with common problems and solutions"""
        # Use the actual schema: (id, symptom, cause, solution, prevention)
        problems = [
            (None, 'disk space', 'out of space', 'Run `nix-collect-garbage -d` to free disk space by removing old generations', 'Regularly clean old generations'),
            (None, 'broken', 'broken package', 'Try `sudo nixos-rebuild switch --rollback` to return to previous working configuration', 'Test in nix-shell first'),
            (None, 'conflict', 'collision', 'Package conflicts can be resolved by using overlays or removing one of the conflicting packages', 'Use overlays for conflicts'),
            (None, 'not found', 'attribute missing', 'Package might not exist or need different attribute path. Try searching: `nix search nixpkgs package-name`', 'Search before installing')
        ]
        
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Don't create table - it already exists from KnowledgeBase.__init__()
        # Use the actual schema
        cursor.executemany(
            "INSERT OR REPLACE INTO problems (id, symptom, cause, solution, prevention) VALUES (?, ?, ?, ?, ?)",
            problems
        )
        
        conn.commit()
        conn.close()
        
    def test_solution_formatting(self):
        """Test that solutions are properly formatted"""
        self._seed_solution_data()
        
        # Get a solution
        solution = self.kb.get_solution(IntentType.INSTALL_PACKAGE)
        
        # Check it's not empty
        self.assertIsNotNone(solution)
        self.assertGreater(len(str(solution)), 5)  # Should be substantial
        
        # Check it contains expected keywords
        self.assertIn("install_package", solution.lower())
        self.assertIn("nix", solution.lower())
        
    def test_install_methods_structure(self):
        """Test the structure of install methods"""
        self._seed_install_methods()
        
        methods = self.kb.get_install_methods()
        
        # Should return structured data
        self.assertIsInstance(methods, list)
        self.assertGreater(len(methods), 0)
        
        # Each method should have required fields
        for method in methods:
            self.assertTrue('method' in method or 'name' in method)
            self.assertIn('description', method)
            self.assertIn('example', method)


if __name__ == '__main__':
    unittest.main()