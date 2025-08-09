#!/usr/bin/env python3
"""
from typing import List
Example: Method-by-Method Migration Pattern
Shows how to migrate individual methods in ask-nix to use headless engine
"""

import os
import sys
from typing import Dict, Optional, List

# Feature flag
USE_HEADLESS = os.getenv('NIX_USE_HEADLESS', 'false').lower() == 'true'

class MigrationExample:
    """
    Example showing how to migrate methods one at a time
    while maintaining backward compatibility
    """
    
    def __init__(self):
        self.use_headless = USE_HEADLESS
        
        if self.use_headless:
            try:
                # Import headless components
                from core.headless_engine import HeadlessEngine, Context
                from adapters.cli_adapter import CLIAdapter
                
                self.adapter = CLIAdapter(use_server=False)
                self._headless_available = True
                print("✅ Headless engine initialized")
            except ImportError:
                self._headless_available = False
                self.use_headless = False
                print("⚠️  Headless not available, using legacy")
        
        if not self.use_headless:
            # Initialize legacy components
            from nix_knowledge_engine import NixOSKnowledgeEngine
            self.knowledge = NixOSKnowledgeEngine()
            self._headless_available = False
    
    # ========== EXAMPLE 1: Simple Method Migration ==========
    
    def extract_intent(self, query: str) -> Dict:
        """
        Example of migrating a simple method
        """
        if self.use_headless:
            # Headless implementation
            from core.headless_engine import Context
            context = Context()
            response = self.adapter.engine.process(query, context)
            return response.intent
        else:
            # Legacy implementation
            return self.knowledge.extract_intent(query)
    
    # ========== EXAMPLE 2: Method with Different Return Types ==========
    
    def get_solution(self, intent: Dict) -> Dict:
        """
        Example where return types might differ between implementations
        """
        if self.use_headless:
            # Headless returns different structure
            from core.headless_engine import Context
            context = Context()
            
            # Reconstruct query from intent for headless
            query = intent.get('query', '')
            response = self.adapter.engine.process(query, context)
            
            # Convert to legacy format
            return {
                'found': response.confidence > 0.5,
                'solution': response.solution.text if response.solution else '',
                'methods': response.solution.methods if response.solution else [],
                'explanation': response.solution.explanation if response.solution else ''
            }
        else:
            # Legacy implementation
            return self.knowledge.get_solution(intent)
    
    # ========== EXAMPLE 3: Complex Method with Side Effects ==========
    
    def process_with_feedback(self, query: str, collect_feedback: bool = True) -> Dict:
        """
        Example of migrating a method that has side effects (feedback collection)
        """
        if self.use_headless:
            # Headless handles feedback internally
            from core.headless_engine import Context
            
            context = Context(
                collect_feedback=collect_feedback,
                personality='friendly'
            )
            
            response = self.adapter.process_query(query, context)
            
            # Headless already collected feedback if enabled
            return {
                'response': response.get('text', ''),
                'feedback_collected': response.get('feedback_collected', False)
            }
        else:
            # Legacy implementation
            intent = self.knowledge.extract_intent(query)
            solution = self.knowledge.get_solution(intent)
            response_text = self.knowledge.format_response(intent, solution)
            
            # Manually handle feedback in legacy
            feedback_collected = False
            if collect_feedback and solution.get('found'):
                # Legacy feedback collection logic
                feedback_collected = self._legacy_collect_feedback(query, response_text)
            
            return {
                'response': response_text,
                'feedback_collected': feedback_collected
            }
    
    def _legacy_collect_feedback(self, query: str, response: str) -> bool:
        """Legacy feedback collection"""
        # Simplified for example
        print("📝 Legacy feedback collection")
        return True
    
    # ========== EXAMPLE 4: Gradual Feature Migration ==========
    
    def advanced_search(self, query: str, use_cache: bool = True) -> List[str]:
        """
        Example of gradually migrating features within a method
        """
        results = []
        
        # Step 1: Use headless for intent extraction if available
        if self.use_headless and self._should_use_headless_for('intent'):
            from core.headless_engine import Context
            context = Context()
            response = self.adapter.engine.process(query, context)
            intent = response.intent
        else:
            intent = self.knowledge.extract_intent(query)
        
        # Step 2: Use legacy for solution (not migrated yet)
        solution = self.knowledge.get_solution(intent)
        
        # Step 3: Use headless for caching if available
        if use_cache:
            if self.use_headless and self._should_use_headless_for('cache'):
                # Headless cache implementation
                cached = self.adapter.engine.cache_manager.get(query)
                if cached:
                    return cached
            else:
                # Legacy cache implementation
                # ... legacy cache logic ...
                pass
        
        # Process results
        if solution.get('found'):
            results = [method['name'] for method in solution.get('methods', [])]
        
        return results
    
    def _should_use_headless_for(self, feature: str) -> bool:
        """
        Granular control over which features use headless
        """
        # Can be controlled by environment variables
        feature_flags = {
            'intent': os.getenv(f'HEADLESS_{feature.upper()}', 'true') == 'true',
            'cache': os.getenv(f'HEADLESS_CACHE', 'false') == 'true',
            'feedback': os.getenv(f'HEADLESS_FEEDBACK', 'true') == 'true',
        }
        return self._headless_available and feature_flags.get(feature, False)
    
    # ========== EXAMPLE 5: Property-based Compatibility ==========
    
    @property
    def knowledge_engine(self):
        """
        Property that provides compatible interface regardless of engine
        """
        if self.use_headless:
            # Return a compatibility wrapper
            return self._get_headless_knowledge_wrapper()
        else:
            return self.knowledge
    
    def _get_headless_knowledge_wrapper(self):
        """
        Wrapper that makes headless engine look like legacy knowledge engine
        """
        class KnowledgeWrapper:
            def __init__(self, adapter):
                self.adapter = adapter
            
            def extract_intent(self, query):
                # Delegate to headless
                from core.headless_engine import Context
                response = self.adapter.engine.process(query, Context())
                return response.intent
            
            def get_solution(self, intent):
                # Convert and delegate
                query = intent.get('query', '')
                from core.headless_engine import Context
                response = self.adapter.engine.process(query, Context())
                # Convert response to legacy format
                return {
                    'found': response.confidence > 0.5,
                    'solution': response.solution.text if response.solution else ''
                }
        
        return KnowledgeWrapper(self.adapter)


def demonstrate_migration_patterns():
    """Show different migration patterns in action"""
    
    migrator = MigrationExample()
    
    print("🔄 Migration Pattern Examples")
    print("=" * 60)
    
    # Test query
    query = "install firefox"
    
    # Example 1: Simple method
    print("\n1️⃣ Simple Method Migration:")
    intent = migrator.extract_intent(query)
    print(f"Intent: {intent}")
    
    # Example 2: Return type conversion
    print("\n2️⃣ Return Type Conversion:")
    solution = migrator.get_solution(intent)
    print(f"Solution found: {solution.get('found')}")
    
    # Example 3: Side effects
    print("\n3️⃣ Method with Side Effects:")
    result = migrator.process_with_feedback(query)
    print(f"Response: {result['response'][:50]}...")
    print(f"Feedback collected: {result['feedback_collected']}")
    
    # Example 4: Gradual migration
    print("\n4️⃣ Gradual Feature Migration:")
    results = migrator.advanced_search(query)
    print(f"Search results: {results}")
    
    # Example 5: Property compatibility
    print("\n5️⃣ Property-based Compatibility:")
    engine = migrator.knowledge_engine
    print(f"Engine type: {type(engine).__name__}")
    

if __name__ == "__main__":
    demonstrate_migration_patterns()
    
    print("\n💡 Migration Tips:")
    print("- Start with simple methods")
    print("- Add conversion layers for different return types")
    print("- Use feature flags for granular control")
    print("- Test thoroughly with both engines")
    print("- Monitor performance and user feedback")