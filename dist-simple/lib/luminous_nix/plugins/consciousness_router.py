"""
Consciousness Router - The Sacred Dispatcher

This module routes user intentions to the appropriate handler,
whether that's the core engine or a plugin. It is the central
nervous system of our consciousness-first architecture.
"""

import re
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from pathlib import Path
import asyncio
import json

try:
    from .plugin_loader import PluginLoader, DiscoveredPlugin
    from .sandbox import PluginSandbox, ConsentRequired
except ImportError:
    from plugin_loader import PluginLoader, DiscoveredPlugin
    from sandbox import PluginSandbox, ConsentRequired


@dataclass
class RouteMatch:
    """A match between an intent and a handler"""
    confidence: float
    handler_type: str  # 'core' or 'plugin'
    handler_id: Optional[str]  # plugin ID if plugin
    intent_pattern: str
    plugin_info: Optional[Any] = None  # Plugin info if plugin match
    
    @property
    def is_plugin(self) -> bool:
        return self.handler_type == 'plugin'


class ConsciousnessRouter:
    """
    The Sacred Dispatcher that routes intentions to their proper handlers.
    
    This router understands both the core capabilities and all plugin
    capabilities, intelligently routing based on pattern matching,
    consciousness principles, and user preferences.
    """
    
    # Core patterns that are always handled by the main engine
    CORE_PATTERNS = {
        # Package management
        r"install\s+(.+)": "install",
        r"remove\s+(.+)": "remove",
        r"uninstall\s+(.+)": "remove",
        r"search\s+(.+)": "search",
        r"find\s+(.+)": "search",
        
        # Configuration
        r"generate\s+(.+)\s+config": "generate_config",
        r"create\s+(.+)\s+configuration": "generate_config",
        r"show\s+config": "show_config",
        
        # System management
        r"rollback": "rollback",
        r"update\s+system": "update",
        r"check\s+health": "health_check",
        
        # Settings
        r"settings": "settings",
        r"preferences": "settings",
        r"configure": "settings",
    }
    
    def __init__(self, plugins_dir: Optional[Path] = None):
        """
        Initialize the Consciousness Router.
        
        Args:
            plugins_dir: Directory containing plugins
        """
        self.plugin_loader = PluginLoader(plugins_dir)
        self.plugin_sandboxes: Dict[str, PluginSandbox] = {}
        self.route_cache: Dict[str, RouteMatch] = {}
        
        # Discover plugins on initialization
        self.plugins = self.plugin_loader.discover_plugins()
        
        # Precompile regex patterns for efficiency
        self.compiled_core_patterns = {
            re.compile(pattern, re.IGNORECASE): intent
            for pattern, intent in self.CORE_PATTERNS.items()
        }
    
    def route(self, user_query: str) -> RouteMatch:
        """
        Route a user query to the appropriate handler.
        
        This is the main routing logic that determines whether
        a query should go to core or a plugin.
        """
        # Check cache first
        if user_query in self.route_cache:
            return self.route_cache[user_query]
        
        # Normalize query
        query = user_query.strip().lower()
        
        # Check core patterns first (they have priority)
        core_match = self._match_core_pattern(query)
        if core_match:
            return core_match
        
        # Check plugin patterns
        plugin_match = self._match_plugin_pattern(query)
        if plugin_match:
            return plugin_match
        
        # Default to core with low confidence
        # The core engine can handle unknown queries with its NLP
        return RouteMatch(
            confidence=0.3,
            handler_type='core',
            handler_id=None,
            intent_pattern='unknown'
        )
    
    def _match_core_pattern(self, query: str) -> Optional[RouteMatch]:
        """
        Match query against core patterns.
        """
        for pattern, intent in self.compiled_core_patterns.items():
            match = pattern.match(query)
            if match:
                return RouteMatch(
                    confidence=0.95,  # Core patterns are high confidence
                    handler_type='core',
                    handler_id=None,
                    intent_pattern=intent
                )
        return None
    
    def _match_plugin_pattern(self, query: str) -> Optional[RouteMatch]:
        """
        Match query against plugin patterns.
        """
        best_match = None
        best_confidence = 0.0
        
        for plugin in self.plugins:
            if not plugin.is_valid:
                continue
            
            # Get plugin intents
            intents = plugin.manifest_data.get('capabilities', {}).get('intents', [])
            
            for intent in intents:
                pattern = intent.get('pattern', '')
                if not pattern:
                    continue
                
                # Calculate match confidence
                confidence = self._calculate_pattern_confidence(query, pattern)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = RouteMatch(
                        confidence=confidence,
                        handler_type='plugin',
                        handler_id=plugin.id,
                        intent_pattern=pattern,
                        plugin_info=plugin
                    )
        
        # Return if confidence is meaningful (including medium confidence for whispers)
        if best_confidence > 0.4:
            return best_match
        
        return None
    
    def _calculate_pattern_confidence(self, query: str, pattern: str) -> float:
        """
        Calculate how well a query matches a pattern.
        
        This is a simple implementation - in production we'd use
        more sophisticated NLP matching.
        """
        # Exact match
        if query == pattern.lower():
            return 1.0
        
        # Pattern is contained in query
        if pattern.lower() in query:
            return 0.8
        
        # All pattern words are in query
        pattern_words = set(pattern.lower().split())
        query_words = set(query.split())
        
        if pattern_words.issubset(query_words):
            return 0.7
        
        # Check for related keywords for medium confidence
        focus_keywords = {'focus', 'concentrate', 'work', 'distraction', 'attention', 'productivity'}
        pattern_has_focus = bool(focus_keywords & pattern_words)
        query_has_focus = bool(focus_keywords & query_words)
        
        if pattern_has_focus and query_has_focus:
            # Related domain - medium confidence
            return 0.5
        
        # Some pattern words match
        overlap = len(pattern_words & query_words)
        if overlap > 0:
            return 0.4 + (0.2 * overlap / len(pattern_words))
        
        return 0.0
    
    def get_plugin_suggestions(self, user_query: str) -> List[Dict[str, Any]]:
        """
        Get plugin suggestions for a query.
        
        Returns a list of plugins that might be relevant to the query,
        especially for medium-confidence matches where we want to
        provide "whisper" suggestions.
        """
        suggestions = []
        query = user_query.strip().lower()
        
        for plugin in self.plugins:
            if not plugin.is_valid:
                continue
                
            # Calculate relevance to query
            relevance = 0.0
            intents = plugin.manifest_data.get('capabilities', {}).get('intents', [])
            
            for intent in intents:
                pattern = intent.get('pattern', '')
                if not pattern:
                    continue
                    
                confidence = self._calculate_pattern_confidence(query, pattern)
                relevance = max(relevance, confidence)
            
            # Include plugins with medium relevance (whisper zone)
            if 0.3 < relevance < 0.8:
                suggestions.append({
                    'plugin_id': plugin.id,
                    'plugin_name': plugin.name,
                    'description': plugin.manifest_data.get('consciousness', {}).get('sacred_promise', ''),
                    'relevance': relevance,
                    'governing_principle': plugin.governing_principle
                })
        
        # Sort by relevance
        suggestions.sort(key=lambda x: x['relevance'], reverse=True)
        return suggestions[:3]  # Return top 3 suggestions
    
    async def execute(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a user query by routing to the appropriate handler.
        
        This is the main entry point for processing user intentions.
        """
        # Route the query
        route = self.route(user_query)
        
        # Add to cache for efficiency
        self.route_cache[user_query] = route
        
        # Execute based on route
        if route.handler_type == 'core':
            return await self._execute_core(user_query, route, context)
        else:
            return await self._execute_plugin(user_query, route, context)
    
    async def _execute_core(self, query: str, route: RouteMatch, 
                           context: Optional[Dict]) -> Dict[str, Any]:
        """
        Execute a query through the core engine.
        """
        # In production, this would call the actual core engine
        # For now, return a structured response
        return {
            'source': 'core',
            'intent': route.intent_pattern,
            'confidence': route.confidence,
            'query': query,
            'message': f"Core would handle: {query}",
            'context': context
        }
    
    async def _execute_plugin(self, query: str, route: RouteMatch, 
                             context: Optional[Dict]) -> Dict[str, Any]:
        """
        Execute a query through a plugin.
        """
        plugin_id = route.handler_id
        
        # Get or create sandbox for this plugin
        if plugin_id not in self.plugin_sandboxes:
            sandbox = await self._create_sandbox(plugin_id)
            if not sandbox:
                return {
                    'source': 'router',
                    'error': f"Could not load plugin: {plugin_id}",
                    'query': query
                }
            self.plugin_sandboxes[plugin_id] = sandbox
        
        sandbox = self.plugin_sandboxes[plugin_id]
        
        try:
            # Execute in sandbox
            result = await sandbox.execute(
                route.intent_pattern,
                {'query': query, 'context': context}
            )
            
            # Add routing metadata
            result['route'] = {
                'plugin_id': plugin_id,
                'plugin_name': route.plugin_info.name if route.plugin_info else 'Unknown',
                'confidence': route.confidence,
                'pattern': route.intent_pattern
            }
            
            return result
            
        except ConsentRequired as e:
            # Handle consent requirement
            return {
                'source': 'plugin',
                'plugin_id': plugin_id,
                'consent_required': True,
                'consent_prompt': e.prompt,
                'query': query
            }
        
        except Exception as e:
            return {
                'source': 'plugin',
                'plugin_id': plugin_id,
                'error': str(e),
                'query': query
            }
    
    async def _create_sandbox(self, plugin_id: str) -> Optional[PluginSandbox]:
        """
        Create a sandbox for a plugin.
        """
        plugin = self.plugin_loader.discovered_plugins.get(plugin_id)
        if not plugin:
            return None
        
        # Load the plugin module
        try:
            # Add plugin directory to path
            import sys
            plugin_dir = str(plugin.path)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            
            # Import the plugin
            import importlib
            plugin_module = importlib.import_module('plugin')
            
            # Get the plugin class
            plugin_class = getattr(plugin_module, 'Plugin', None)
            if not plugin_class:
                plugin_class = getattr(plugin_module, 'FlowGuardian', None)
            
            if not plugin_class:
                print(f"No Plugin class found in {plugin_id}")
                return None
            
            # Create instance
            plugin_instance = plugin_class()
            
            # Create sandbox
            sandbox = PluginSandbox(plugin.manifest_data, plugin_instance)
            
            return sandbox
            
        except Exception as e:
            print(f"Error loading plugin {plugin_id}: {e}")
            return None
    
    def get_routing_report(self) -> str:
        """
        Generate a report of routing capabilities.
        """
        report = """
╔══════════════════════════════════════════════════════════╗
║           🧭 Consciousness Router Report                  ║
╚══════════════════════════════════════════════════════════╝

📊 Routing Statistics:
"""
        
        # Core patterns
        report += f"  • Core patterns: {len(self.CORE_PATTERNS)}\n"
        
        # Plugin patterns
        plugin_pattern_count = 0
        for plugin in self.plugins:
            if plugin.is_valid:
                intents = plugin.manifest_data.get('capabilities', {}).get('intents', [])
                plugin_pattern_count += len(intents)
        
        report += f"  • Plugin patterns: {plugin_pattern_count}\n"
        report += f"  • Valid plugins: {len([p for p in self.plugins if p.is_valid])}\n"
        report += f"  • Cached routes: {len(self.route_cache)}\n"
        
        # Core capabilities
        report += "\n🎯 Core Capabilities:\n"
        for pattern in list(self.CORE_PATTERNS.keys())[:5]:
            report += f"  • {pattern}\n"
        if len(self.CORE_PATTERNS) > 5:
            report += f"  ... and {len(self.CORE_PATTERNS) - 5} more\n"
        
        # Plugin capabilities
        report += "\n🔌 Plugin Capabilities:\n"
        for plugin in self.plugins[:3]:
            if not plugin.is_valid:
                continue
            report += f"\n  📦 {plugin.name}:\n"
            intents = plugin.manifest_data.get('capabilities', {}).get('intents', [])
            for intent in intents[:2]:
                report += f"    • \"{intent.get('pattern', 'unknown')}\"\n"
        
        # Routing examples
        report += "\n💡 Example Routes:\n"
        examples = [
            "install firefox",
            "start focus session",
            "check interruptions",
            "generate web server config"
        ]
        
        for example in examples:
            route = self.route(example)
            emoji = "🎯" if route.handler_type == 'core' else "🔌"
            report += f"  {emoji} \"{example}\" → {route.handler_type}"
            if route.handler_id:
                report += f" ({route.handler_id})"
            report += f" [confidence: {route.confidence:.0%}]\n"
        
        return report
    
    def get_plugin_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """
        Get plugin suggestions for a query that doesn't match well.
        
        This helps users discover relevant plugins.
        """
        suggestions = []
        
        # Extract key words from query
        query_words = set(query.lower().split())
        
        for plugin in self.plugins:
            if not plugin.is_valid:
                continue
            
            # Check if plugin might be relevant
            relevance_score = 0.0
            
            # Check plugin description
            description = plugin.manifest_data.get('plugin', {}).get('description', '')
            desc_words = set(description.lower().split())
            
            overlap = len(query_words & desc_words)
            if overlap > 0:
                relevance_score += overlap * 0.1
            
            # Check governing principle
            principle = plugin.governing_principle
            if any(word in principle for word in query_words):
                relevance_score += 0.3
            
            # Check patterns
            intents = plugin.manifest_data.get('capabilities', {}).get('intents', [])
            for intent in intents:
                pattern = intent.get('pattern', '').lower()
                if any(word in pattern for word in query_words):
                    relevance_score += 0.2
            
            if relevance_score > 0:
                suggestions.append({
                    'plugin_id': plugin.id,
                    'plugin_name': plugin.name,
                    'description': description,
                    'principle': principle,
                    'relevance': relevance_score
                })
        
        # Sort by relevance
        suggestions.sort(key=lambda x: x['relevance'], reverse=True)
        
        return suggestions[:3]  # Top 3 suggestions


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_router():
        # Create router
        router = ConsciousnessRouter()
        
        # Print routing report
        print(router.get_routing_report())
        
        # Test some queries
        test_queries = [
            "install firefox",
            "start focus session for 25 minutes",
            "check my interruptions",
            "generate nginx config",
            "help me focus",
            "block distractions"
        ]
        
        print("\n" + "=" * 60)
        print("Testing Query Routing")
        print("=" * 60)
        
        for query in test_queries:
            route = router.route(query)
            print(f"\n📝 Query: \"{query}\"")
            print(f"   Route: {route.handler_type}")
            if route.handler_id:
                print(f"   Plugin: {route.handler_id}")
            print(f"   Pattern: {route.intent_pattern}")
            print(f"   Confidence: {route.confidence:.0%}")
            
            # Get suggestions if low confidence
            if route.confidence < 0.6:
                suggestions = router.get_plugin_suggestions(query)
                if suggestions:
                    print("   💡 Suggestions:")
                    for s in suggestions:
                        print(f"      • {s['plugin_name']}: {s['description'][:50]}...")
        
        # Test execution
        print("\n" + "=" * 60)
        print("Testing Query Execution")
        print("=" * 60)
        
        result = await router.execute("start focus session", {'duration': 25})
        print("\nExecution result:")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_router())