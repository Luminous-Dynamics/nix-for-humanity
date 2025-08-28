#!/usr/bin/env python3
"""Comprehensive test suite for hybrid intent recognition system.

This test suite validates:
1. All intent types are recognizable
2. Edge cases and ambiguous queries
3. Learning system functionality
4. Performance characteristics
5. Confidence scoring accuracy
"""

import pytest
import time
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.core.intents import IntentType, IntentRecognizer, Intent
from luminous_nix.core.intent_factory import IntentRecognizerProxy
from luminous_nix.core.config_enhanced_intent import IntentRecognitionConfig
from luminous_nix.core.intent_pipeline_enhanced import AdaptiveIntentRecognizer


@dataclass
class TestCase:
    """Test case for intent recognition."""
    query: str
    expected_intent: IntentType
    min_confidence: float = 0.7
    description: str = ""
    is_ambiguous: bool = False


class TestIntentComprehensive:
    """Comprehensive test suite for intent recognition."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.pattern_recognizer = IntentRecognizer()
        cls.hybrid_recognizer = IntentRecognizerProxy(
            IntentRecognitionConfig(enable_llm=True, mode="balanced")
        )
        
    def test_all_intent_types_coverage(self):
        """Ensure every IntentType has at least one working pattern."""
        test_cases = [
            # Package management
            TestCase("install firefox", IntentType.INSTALL_PACKAGE, 0.9),
            TestCase("remove vim", IntentType.REMOVE_PACKAGE, 0.9),
            TestCase("search text editor", IntentType.SEARCH_PACKAGE, 0.8),
            TestCase("list installed packages", IntentType.LIST_INSTALLED, 0.9),
            
            # System management
            TestCase("update system", IntentType.UPDATE_SYSTEM, 0.85),
            TestCase("rollback", IntentType.ROLLBACK, 0.9),
            TestCase("garbage collect", IntentType.GARBAGE_COLLECT, 0.85),
            TestCase("list generations", IntentType.LIST_GENERATIONS, 0.9),
            TestCase("switch to generation 5", IntentType.SWITCH_GENERATION, 0.9),
            TestCase("rebuild", IntentType.REBUILD, 0.85),
            
            # Configuration
            TestCase("edit config", IntentType.EDIT_CONFIG, 0.9),
            TestCase("show config", IntentType.SHOW_CONFIG, 0.9),
            TestCase("validate config", IntentType.VALIDATE_CONFIG, 0.85),
            TestCase("generate config for web server", IntentType.GENERATE_CONFIG, 0.85),
            
            # Network management
            TestCase("show network", IntentType.SHOW_NETWORK, 0.9),
            TestCase("show ip", IntentType.SHOW_IP, 0.9),
            TestCase("connect wifi", IntentType.CONNECT_WIFI, 0.85),
            TestCase("list wifi networks", IntentType.LIST_WIFI, 0.85),
            TestCase("test connection", IntentType.TEST_CONNECTION, 0.85),
            
            # Service management
            TestCase("start nginx", IntentType.START_SERVICE, 0.85),
            TestCase("stop docker", IntentType.STOP_SERVICE, 0.85),
            TestCase("restart postgresql", IntentType.RESTART_SERVICE, 0.85),
            TestCase("nginx status", IntentType.SERVICE_STATUS, 0.85),
            TestCase("list services", IntentType.LIST_SERVICES, 0.9),
            TestCase("enable ssh", IntentType.ENABLE_SERVICE, 0.85),
            TestCase("disable bluetooth", IntentType.DISABLE_SERVICE, 0.85),
            TestCase("show nginx logs", IntentType.SERVICE_LOGS, 0.85),
            
            # User management
            TestCase("create user alice", IntentType.CREATE_USER, 0.85),
            TestCase("list users", IntentType.LIST_USERS, 0.9),
            TestCase("add alice to wheel", IntentType.ADD_USER_TO_GROUP, 0.8),
            TestCase("change password", IntentType.CHANGE_PASSWORD, 0.85),
            TestCase("grant sudo to bob", IntentType.GRANT_SUDO, 0.8),
            
            # Storage management
            TestCase("disk usage", IntentType.DISK_USAGE, 0.9),
            TestCase("analyze disk space", IntentType.ANALYZE_DISK, 0.9),
            TestCase("mount /dev/sdb1", IntentType.MOUNT_DEVICE, 0.85),
            TestCase("unmount /mnt/usb", IntentType.UNMOUNT_DEVICE, 0.85),
            TestCase("find large files", IntentType.FIND_LARGE_FILES, 0.9),
            
            # Flake management
            TestCase("create flake", IntentType.CREATE_FLAKE, 0.85),
            TestCase("validate flake", IntentType.VALIDATE_FLAKE, 0.85),
            TestCase("convert to flake", IntentType.CONVERT_FLAKE, 0.8),
            TestCase("show flake info", IntentType.SHOW_FLAKE_INFO, 0.85),
            
            # Package discovery
            TestCase("discover markdown editor", IntentType.DISCOVER_PACKAGE, 0.8),
            TestCase("what package has vim", IntentType.FIND_BY_COMMAND, 0.8),
            TestCase("browse categories", IntentType.BROWSE_CATEGORIES, 0.85),
            TestCase("show popular packages", IntentType.SHOW_POPULAR, 0.85),
            
            # Help and explain
            TestCase("help", IntentType.HELP, 0.95),
            TestCase("what is nixos", IntentType.EXPLAIN, 0.8),
            TestCase("configure ssh", IntentType.CONFIGURE, 0.85),
            TestCase("check status", IntentType.CHECK_STATUS, 0.85),
        ]
        
        failed_cases = []
        untested_intents = set(IntentType) - {IntentType.UNKNOWN}
        
        for test_case in test_cases:
            intent = self.pattern_recognizer.recognize(test_case.query)
            
            # Remove from untested set
            if test_case.expected_intent in untested_intents:
                untested_intents.remove(test_case.expected_intent)
            
            # Check if intent matches
            if intent.type != test_case.expected_intent:
                failed_cases.append((test_case, intent))
            else:
                # Check confidence
                assert intent.confidence >= test_case.min_confidence, \
                    f"Low confidence for '{test_case.query}': {intent.confidence}"
        
        # Report failures
        if failed_cases:
            failure_msg = "\n".join([
                f"  '{tc.query}' -> {intent.type} (expected {tc.expected_intent})"
                for tc, intent in failed_cases
            ])
            pytest.fail(f"Failed intent recognition:\n{failure_msg}")
        
        # Check coverage
        if untested_intents:
            pytest.fail(f"Untested intent types: {untested_intents}")
            
    def test_ambiguous_queries(self):
        """Test handling of ambiguous queries."""
        ambiguous_cases = [
            TestCase("clean", IntentType.GARBAGE_COLLECT, 0.5, 
                    "Could be garbage collect or clean something else", True),
            TestCase("space", IntentType.DISK_USAGE, 0.5,
                    "Could be disk space or package namespace", True),
            TestCase("update", IntentType.UPDATE_SYSTEM, 0.5,
                    "Could be system update or package update", True),
            TestCase("fix it", IntentType.UNKNOWN, 0.1,
                    "Too vague to determine intent", True),
            TestCase("make it work", IntentType.UNKNOWN, 0.1,
                    "No specific action identifiable", True),
        ]
        
        for test_case in ambiguous_cases:
            intent = self.pattern_recognizer.recognize(test_case.query)
            
            # For ambiguous queries, we just check they don't crash
            # and return something reasonable
            assert intent is not None
            assert 0.0 <= intent.confidence <= 1.0
            
            # If it's truly ambiguous, confidence should be lower
            if test_case.is_ambiguous and intent.type != IntentType.UNKNOWN:
                assert intent.confidence <= 0.8, \
                    f"Too confident for ambiguous query '{test_case.query}': {intent.confidence}"
                    
    def test_query_variations(self):
        """Test that variations of the same intent are recognized."""
        variation_groups = [
            # Different ways to install a package
            (IntentType.INSTALL_PACKAGE, [
                "install firefox",
                "add firefox",
                "get firefox",
                "I need firefox",
                "I want firefox",
                "can you install firefox",
                "please install firefox",
                "set up firefox",
            ]),
            
            # Different ways to search
            (IntentType.SEARCH_PACKAGE, [
                "search vim",
                "find vim",
                "look for vim",
                "is there vim",
                "what packages have vim",
                "available vim",
            ]),
            
            # Different ways to ask for help
            (IntentType.HELP, [
                "help",
                "help me",
                "what can you do",
                "what can I say",
                "show me commands",
                "list commands",
            ]),
        ]
        
        for expected_intent, queries in variation_groups:
            failed_variations = []
            
            for query in queries:
                intent = self.pattern_recognizer.recognize(query)
                if intent.type != expected_intent:
                    failed_variations.append((query, intent.type))
            
            if failed_variations:
                failure_msg = "\n".join([
                    f"  '{q}' -> {actual} (expected {expected_intent})"
                    for q, actual in failed_variations
                ])
                pytest.fail(f"Failed variations for {expected_intent}:\n{failure_msg}")
                
    def test_confidence_scoring(self):
        """Test that confidence scores make sense."""
        confidence_cases = [
            # High confidence - exact matches
            ("help", 0.9, 1.0),
            ("install firefox", 0.85, 1.0),
            ("list generations", 0.85, 1.0),
            
            # Medium confidence - partial matches
            ("maybe install something", 0.5, 0.8),
            ("I think I need vim", 0.6, 0.9),
            
            # Low confidence - vague queries
            ("something", 0.0, 0.5),
            ("do the thing", 0.0, 0.3),
        ]
        
        for query, min_conf, max_conf in confidence_cases:
            intent = self.pattern_recognizer.recognize(query)
            assert min_conf <= intent.confidence <= max_conf, \
                f"Confidence for '{query}' out of range: {intent.confidence} not in [{min_conf}, {max_conf}]"
                
    def test_entity_extraction(self):
        """Test that entities are correctly extracted from queries."""
        entity_cases = [
            ("install firefox", "package", "firefox"),
            ("remove vim", "package", "vim"),
            ("start nginx", "service", "nginx"),
            ("create user alice", "username", "alice"),
            ("switch to generation 5", "generation", 5),
            ("mount /dev/sdb1", "device", "/dev/sdb1"),
        ]
        
        for query, entity_key, expected_value in entity_cases:
            intent = self.pattern_recognizer.recognize(query)
            
            # Check entity exists
            assert entity_key in intent.entities, \
                f"Missing entity '{entity_key}' in query '{query}'"
            
            # Check entity value
            actual_value = intent.entities[entity_key]
            if isinstance(expected_value, int):
                assert actual_value == expected_value, \
                    f"Wrong entity value for '{query}': {actual_value} != {expected_value}"
            else:
                assert actual_value.lower() == expected_value.lower(), \
                    f"Wrong entity value for '{query}': {actual_value} != {expected_value}"
                    
    def test_performance_benchmarks(self):
        """Benchmark performance of different recognizer modes."""
        queries = [
            "install firefox",
            "search vim", 
            "update system",
            "disk usage",
            "help",
        ] * 20  # 100 queries total
        
        # Benchmark pattern recognizer
        start = time.time()
        for query in queries:
            self.pattern_recognizer.recognize(query)
        pattern_time = time.time() - start
        pattern_avg = (pattern_time / len(queries)) * 1000
        
        print(f"\nPerformance Benchmarks:")
        print(f"  Pattern recognizer: {pattern_avg:.2f}ms average")
        
        # Should be very fast
        assert pattern_avg < 5.0, f"Pattern recognition too slow: {pattern_avg}ms"
        
        # TODO: Benchmark hybrid recognizer when LLM is available
        
    def test_learning_system(self):
        """Test the learning and correction system."""
        if not self.hybrid_recognizer.is_enhanced:
            pytest.skip("Learning system requires enhanced recognizer")
            
        test_phrase = "nuke the system"
        
        # Initial recognition
        intent1 = self.hybrid_recognizer.recognize(test_phrase)
        initial_type = intent1.type
        
        # Teach correct intent
        self.hybrid_recognizer.teach(test_phrase, IntentType.GARBAGE_COLLECT)
        
        # Recognize again
        intent2 = self.hybrid_recognizer.recognize(test_phrase)
        
        # Should now recognize correctly
        assert intent2.type == IntentType.GARBAGE_COLLECT, \
            f"Learning failed: still recognizing as {intent2.type}"
        assert intent2.confidence == 1.0, \
            "Learned intent should have maximum confidence"
            
    def test_edge_cases(self):
        """Test edge cases and potential failure modes."""
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "a" * 1000,  # Very long string
            "!@#$%^&*()",  # Special characters only
            "インストール",  # Non-English characters
            "INSTALL FIREFOX",  # All caps
            "install  firefox",  # Multiple spaces
            "install\nfirefox",  # Newline in query
            None,  # None input (should handle gracefully)
        ]
        
        for query in edge_cases:
            if query is None:
                continue  # Skip None for now
                
            try:
                intent = self.pattern_recognizer.recognize(query)
                assert intent is not None
                assert isinstance(intent.type, IntentType)
                assert 0.0 <= intent.confidence <= 1.0
            except Exception as e:
                pytest.fail(f"Failed on edge case '{query}': {e}")


class TestIntentImprovement:
    """Tests focused on continuous improvement of the system."""
    
    def test_collect_failure_cases(self):
        """Collect cases where intent recognition fails."""
        recognizer = IntentRecognizer()
        
        # Real-world queries that might fail
        difficult_queries = [
            "how do I install stuff",
            "my disk is full",
            "wifi isn't working",
            "everything is broken",
            "undo what I just did",
            "make firefox my default browser",
            "why is my system slow",
            "how much RAM is chrome using",
            "kill all python processes",
            "what version of nixos am I running",
        ]
        
        failures = []
        for query in difficult_queries:
            intent = recognizer.recognize(query)
            if intent.type == IntentType.UNKNOWN or intent.confidence < 0.5:
                failures.append({
                    'query': query,
                    'recognized_as': intent.type.value,
                    'confidence': intent.confidence
                })
        
        # Save failures for analysis
        if failures:
            report = {
                'timestamp': time.time(),
                'failures': failures,
                'failure_rate': len(failures) / len(difficult_queries)
            }
            
            # Print for immediate feedback
            print("\nDifficult queries that need improvement:")
            for f in failures:
                print(f"  '{f['query']}' -> {f['recognized_as']} ({f['confidence']:.2f})")
                
            # Could save to file for tracking over time
            # Path("test_results/intent_failures.json").write_text(json.dumps(report, indent=2))
            
    def test_pattern_conflicts(self):
        """Identify patterns that conflict with each other."""
        recognizer = IntentRecognizer()
        
        # Queries that might match multiple patterns
        conflict_tests = [
            ("install and configure nginx", 
             [IntentType.INSTALL_PACKAGE, IntentType.CONFIGURE]),
            ("update and upgrade system", 
             [IntentType.UPDATE_SYSTEM]),
            ("search and install vim",
             [IntentType.SEARCH_PACKAGE, IntentType.INSTALL_PACKAGE]),
            ("stop and disable bluetooth",
             [IntentType.STOP_SERVICE, IntentType.DISABLE_SERVICE]),
        ]
        
        conflicts = []
        for query, possible_intents in conflict_tests:
            intent = recognizer.recognize(query)
            
            # Check if it picked a reasonable intent
            if intent.type not in possible_intents and intent.type != IntentType.UNKNOWN:
                conflicts.append({
                    'query': query,
                    'recognized': intent.type,
                    'expected_one_of': possible_intents
                })
        
        if conflicts:
            print("\nPattern conflicts found:")
            for c in conflicts:
                print(f"  '{c['query']}' -> {c['recognized']} (expected: {c['expected_one_of']})")
                
    def test_generate_training_data(self):
        """Generate training data for improving the system."""
        recognizer = IntentRecognizer()
        
        # Generate variations of successful patterns
        training_data = []
        
        base_queries = [
            ("install {}", IntentType.INSTALL_PACKAGE, ["firefox", "vim", "emacs", "docker"]),
            ("remove {}", IntentType.REMOVE_PACKAGE, ["chrome", "nodejs", "python"]),
            ("search {}", IntentType.SEARCH_PACKAGE, ["editor", "browser", "terminal"]),
            ("{} service", IntentType.SERVICE_STATUS, ["nginx", "docker", "ssh"]),
        ]
        
        for template, expected_intent, variations in base_queries:
            for variation in variations:
                query = template.format(variation)
                intent = recognizer.recognize(query)
                
                training_data.append({
                    'query': query,
                    'expected': expected_intent.value,
                    'recognized': intent.type.value,
                    'correct': intent.type == expected_intent,
                    'confidence': intent.confidence
                })
        
        # Calculate accuracy
        correct = sum(1 for d in training_data if d['correct'])
        accuracy = correct / len(training_data) if training_data else 0
        
        print(f"\nTraining data generation:")
        print(f"  Generated {len(training_data)} examples")
        print(f"  Accuracy: {accuracy:.1%}")
        
        # Could save for ML training
        # Path("test_results/training_data.json").write_text(json.dumps(training_data, indent=2))


if __name__ == "__main__":
    # Run specific test sections
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        pytest.main([__file__, f"::{test_name}", "-v"])
    else:
        # Run all tests
        pytest.main([__file__, "-v", "--tb=short"])