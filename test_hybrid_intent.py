#!/usr/bin/env python3
"""Test the hybrid intent recognition system."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.intent_factory import create_intent_recognizer, IntentRecognizerProxy
from luminous_nix.core.config_enhanced_intent import IntentRecognitionConfig
from luminous_nix.core.intents import IntentType


def test_basic_recognition():
    """Test basic pattern recognition."""
    print("🧪 Testing Basic Recognition")
    print("=" * 50)
    
    # Force pattern-only mode
    config = IntentRecognitionConfig(enable_llm=False)
    recognizer = IntentRecognizerProxy(config)
    
    test_cases = [
        ("install firefox", IntentType.INSTALL_PACKAGE),
        ("search vim", IntentType.SEARCH_PACKAGE),
        ("update system", IntentType.UPDATE_SYSTEM),
        ("disk usage", IntentType.DISK_USAGE),
        ("analyze disk space", IntentType.ANALYZE_DISK),  # This was failing before
        ("help", IntentType.HELP),
    ]
    
    for query, expected in test_cases:
        intent = recognizer.recognize(query)
        status = "✅" if intent.type == expected else "❌"
        print(f"{status} '{query}' -> {intent.type} (expected {expected})")
        if hasattr(intent, 'confidence'):
            print(f"   Confidence: {intent.confidence:.2f}")
    
    print()
    

def test_enhanced_recognition():
    """Test enhanced recognition with LLM (if available)."""
    print("🤖 Testing Enhanced Recognition")
    print("=" * 50)
    
    # Try enhanced mode
    config = IntentRecognitionConfig(enable_llm=True, mode="balanced")
    recognizer = IntentRecognizerProxy(config)
    
    # Check if enhanced is actually available
    insights = recognizer.get_insights()
    if insights['capabilities'].get('ai_available'):
        print("✅ LLM is available for enhanced recognition")
    else:
        print("⚠️  LLM not available, falling back to patterns")
    
    print()
    
    # Test some ambiguous queries
    ambiguous_queries = [
        "I need more space",  # Could be disk space or package space
        "check my network",   # Could be status or connectivity
        "clean up",          # Could be garbage collect or disk cleanup
        "make it work",      # Very ambiguous
    ]
    
    print("Testing ambiguous queries:")
    for query in ambiguous_queries:
        intent = recognizer.recognize(query)
        print(f"📝 '{query}' -> {intent.type}")
        if hasattr(intent, 'confidence'):
            print(f"   Confidence: {intent.confidence:.2f}")
        if hasattr(intent, 'explanation'):
            print(f"   Explanation: {intent.explanation}")
    
    print()


def test_learning():
    """Test the learning/correction feature."""
    print("🎓 Testing Learning System")
    print("=" * 50)
    
    config = IntentRecognitionConfig(enable_llm=True, enable_learning=True)
    recognizer = IntentRecognizerProxy(config)
    
    # Test phrase that might be misunderstood
    test_phrase = "wipe the disk"
    
    # First recognition
    intent1 = recognizer.recognize(test_phrase)
    print(f"Initial: '{test_phrase}' -> {intent1.type}")
    
    # Teach correct intent
    if recognizer.is_enhanced:
        response = recognizer.teach(test_phrase, IntentType.GARBAGE_COLLECT)
        print(f"Teaching: {response}")
        
        # Try again
        intent2 = recognizer.recognize(test_phrase)
        print(f"After learning: '{test_phrase}' -> {intent2.type}")
    else:
        print("⚠️  Learning not available in basic mode")
    
    print()


def test_performance():
    """Test performance difference between modes."""
    print("⚡ Testing Performance")
    print("=" * 50)
    
    import time
    
    queries = [
        "install firefox",
        "search for text editor",
        "update my system",
        "show disk usage",
    ]
    
    # Test pattern-only mode
    config_fast = IntentRecognitionConfig(enable_llm=False)
    recognizer_fast = IntentRecognizerProxy(config_fast)
    
    start = time.time()
    for query in queries * 10:  # Run 40 queries
        recognizer_fast.recognize(query)
    fast_time = time.time() - start
    
    print(f"Pattern-only mode: {fast_time:.3f}s for 40 queries")
    print(f"Average: {(fast_time/40)*1000:.1f}ms per query")
    
    # Test enhanced mode (if available)
    config_enhanced = IntentRecognitionConfig(enable_llm=True, mode="accurate")
    recognizer_enhanced = IntentRecognizerProxy(config_enhanced)
    
    if recognizer_enhanced.is_enhanced:
        start = time.time()
        for query in queries:  # Run only 4 queries (LLM is slower)
            recognizer_enhanced.recognize(query)
        enhanced_time = time.time() - start
        
        print(f"\nEnhanced mode: {enhanced_time:.3f}s for 4 queries")
        print(f"Average: {(enhanced_time/4)*1000:.1f}ms per query")
        
        # Get insights
        insights = recognizer_enhanced.get_insights()
        if 'performance' in insights:
            print(f"\nInsights:")
            print(f"  Pattern success rate: {insights['performance'].get('pattern_success_rate', 0):.1%}")
            print(f"  AI assistance rate: {insights['performance'].get('ai_assistance_rate', 0):.1%}")


if __name__ == "__main__":
    print("🌟 Hybrid Intent Recognition System Test")
    print("=" * 50)
    print()
    
    # Run all tests
    test_basic_recognition()
    test_enhanced_recognition()
    test_learning()
    test_performance()
    
    print("✨ Testing complete!")