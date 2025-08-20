#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
🎯 Unified Nix Backend - The Brain That Powers All Frontends
Single source of truth for all Nix operations
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Add parent directories to path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import our components
from backend.nix_python_backend import NixPythonBackend, OperationType, OperationResult
from nix_knowledge_engine import NixOSKnowledgeEngine
from plugin_manager import PluginManager, get_plugin_manager
from feedback_collector import FeedbackCollector
from command_learning_system import CommandLearningSystem
from package_cache_manager import PackageCacheManager

# Import config generator
try:
    # Add parent directories to find the module
    import sys
    luminous_nix_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(luminous_nix_dir))
    from luminous_nix.core.config_generator import NixConfigGenerator
    CONFIG_GENERATOR_AVAILABLE = True
except ImportError:
    CONFIG_GENERATOR_AVAILABLE = False
    print("Config generator not available")

# Import home manager
try:
    from luminous_nix.core.home_manager import HomeManager
    HOME_MANAGER_AVAILABLE = True
except ImportError:
    HOME_MANAGER_AVAILABLE = False
    print("Home manager not available")

# Import package discovery
try:
    from luminous_nix.core.package_discovery import PackageDiscovery
    PACKAGE_DISCOVERY_AVAILABLE = True
except ImportError:
    PACKAGE_DISCOVERY_AVAILABLE = False
    print("Package discovery not available")


class IntentType(Enum):
    """Types of user intents"""
    # System operations (use Python backend)
    REBUILD_SYSTEM = "rebuild_system"
    UPDATE_SYSTEM = "update_system"
    ROLLBACK_SYSTEM = "rollback_system"
    LIST_GENERATIONS = "list_generations"
    
    # Package operations
    INSTALL_PACKAGE = "install_package"
    SEARCH_PACKAGE = "search_package"
    REMOVE_PACKAGE = "remove_package"
    
    # Information queries (use knowledge engine)
    EXPLAIN_CONCEPT = "explain_concept"
    SHOW_EXAMPLE = "show_example"
    GET_HELP = "get_help"
    
    # Configuration management
    GENERATE_CONFIG = "generate_config"
    
    # Flake management
    CREATE_FLAKE = "create_flake"
    VALIDATE_FLAKE = "validate_flake"
    CONVERT_FLAKE = "convert_flake"
    SHOW_FLAKE_INFO = "show_flake_info"
    
    # Generation management (advanced)
    ROLLBACK_GENERATION = "rollback_generation"
    DELETE_GENERATIONS = "delete_generations"
    CHECK_HEALTH = "check_health"
    CREATE_SNAPSHOT = "create_snapshot"
    COMPARE_GENERATIONS = "compare_generations"
    
    # Error handling
    EXPLAIN_ERROR = "explain_error"
    ANALYZE_LOG = "analyze_log"
    
    # Home Manager operations
    HOME_INIT = "home_init"
    CONFIGURE_DOTFILES = "configure_dotfiles"
    APPLY_THEME = "apply_theme"
    SYNC_CONFIGS = "sync_configs"
    LIST_HOME_CONFIGS = "list_home_configs"
    
    # Package discovery
    DISCOVER_PACKAGE = "discover_package"
    FIND_BY_COMMAND = "find_by_command"
    BROWSE_CATEGORIES = "browse_categories"
    SHOW_POPULAR = "show_popular"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Structured intent from user input"""
    type: IntentType
    query: str
    entities: Dict[str, Any]
    confidence: float
    raw_text: str = ""  # Original user input


@dataclass
class BackendResponse:
    """Unified response format for all operations"""
    success: bool
    text: str
    intent: Intent
    commands: List[Dict[str, str]] = None
    operation_result: Optional[OperationResult] = None
    suggestions: List[str] = None
    metadata: Dict[str, Any] = None


class UnifiedNixBackend:
    """
    The single backend that powers all frontends
    This is the brain - all intelligence lives here
    """
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        # Core components
        self.python_backend = NixPythonBackend(progress_callback)
        self.knowledge = NixOSKnowledgeEngine()
        self.plugin_manager = get_plugin_manager()
        
        # Supporting systems
        self.feedback = FeedbackCollector()
        self.learner = CommandLearningSystem()
        self.cache = PackageCacheManager()
        
        # Configuration
        self.collect_feedback = True
        self.use_cache = True
        
    def process_intent(self, 
                      intent: Intent, 
                      context: Dict[str, Any]) -> BackendResponse:
        """
        Main entry point - process any intent from any frontend
        
        This is where the magic happens!
        """
        
        # Check plugins first
        plugin_response = self._check_plugins(intent, context)
        if plugin_response:
            return plugin_response
        
        # Route to appropriate handler
        if intent.type in [IntentType.REBUILD_SYSTEM, IntentType.UPDATE_SYSTEM]:
            return self._handle_system_operation(intent, context)
        
        elif intent.type == IntentType.ROLLBACK_SYSTEM:
            return self._handle_rollback(intent, context)
        
        elif intent.type == IntentType.LIST_GENERATIONS:
            return self._handle_list_generations(intent, context)
        
        elif intent.type == IntentType.ROLLBACK_GENERATION:
            return self._handle_rollback_generation(intent, context)
        
        elif intent.type == IntentType.DELETE_GENERATIONS:
            return self._handle_delete_generations(intent, context)
        
        elif intent.type == IntentType.CHECK_HEALTH:
            return self._handle_check_health(intent, context)
        
        elif intent.type == IntentType.CREATE_SNAPSHOT:
            return self._handle_create_snapshot(intent, context)
        
        elif intent.type == IntentType.COMPARE_GENERATIONS:
            return self._handle_compare_generations(intent, context)
        
        elif intent.type == IntentType.INSTALL_PACKAGE:
            return self._handle_install_package(intent, context)
        
        elif intent.type == IntentType.SEARCH_PACKAGE:
            return self._handle_search_package(intent, context)
        
        elif intent.type == IntentType.GENERATE_CONFIG:
            return self._handle_generate_config(intent, context)
        
        elif intent.type == IntentType.CREATE_FLAKE:
            return self._handle_create_flake(intent, context)
        
        elif intent.type == IntentType.VALIDATE_FLAKE:
            return self._handle_validate_flake(intent, context)
        
        elif intent.type == IntentType.CONVERT_FLAKE:
            return self._handle_convert_flake(intent, context)
        
        elif intent.type == IntentType.SHOW_FLAKE_INFO:
            return self._handle_show_flake_info(intent, context)
        
        elif intent.type == IntentType.EXPLAIN_ERROR:
            return self._handle_explain_error(intent, context)
        
        elif intent.type == IntentType.ANALYZE_LOG:
            return self._handle_analyze_log(intent, context)
        
        # Home Manager operations
        elif intent.type == IntentType.HOME_INIT:
            return self._handle_home_init(intent, context)
        
        elif intent.type == IntentType.APPLY_THEME:
            return self._handle_apply_theme(intent, context)
        
        elif intent.type == IntentType.SYNC_CONFIGS:
            return self._handle_sync_configs(intent, context)
        
        elif intent.type == IntentType.LIST_HOME_CONFIGS:
            return self._handle_list_home_configs(intent, context)
        
        # Package discovery operations
        elif intent.type == IntentType.DISCOVER_PACKAGE:
            return self._handle_discover_package(intent, context)
        
        elif intent.type == IntentType.FIND_BY_COMMAND:
            return self._handle_find_by_command(intent, context)
        
        elif intent.type == IntentType.BROWSE_CATEGORIES:
            return self._handle_browse_categories(intent, context)
        
        elif intent.type == IntentType.SHOW_POPULAR:
            return self._handle_show_popular(intent, context)
        
        elif intent.type in [IntentType.EXPLAIN_CONCEPT, IntentType.SHOW_EXAMPLE, 
                            IntentType.GET_HELP]:
            return self._handle_knowledge_query(intent, context)
        
        else:
            return self._handle_unknown(intent, context)
    
    def extract_intent(self, query: str) -> Intent:
        """Extract structured intent from natural language"""
        query_lower = query.lower()
        
        # System operations
        if any(word in query_lower for word in ['rebuild', 'update', 'upgrade']):
            if 'system' in query_lower or 'nixos' in query_lower:
                return Intent(
                    type=IntentType.UPDATE_SYSTEM,
                    query=query,
                    entities={},
                    confidence=0.9,
                    raw_text=query
                )
        
        elif any(word in query_lower for word in ['rollback', 'previous', 'undo']):
            return Intent(
                type=IntentType.ROLLBACK_SYSTEM,
                query=query,
                entities={},
                confidence=0.8,
                raw_text=query
            )
        
        elif 'generation' in query_lower and any(word in query_lower for word in ['list', 'show']):
            return Intent(
                type=IntentType.LIST_GENERATIONS,
                query=query,
                entities={},
                confidence=0.9,
                raw_text=query
            )
        
        # Package operations
        elif any(word in query_lower for word in ['install', 'get', 'add']):
            # Try to extract package name
            package = self._extract_package_name(query)
            return Intent(
                type=IntentType.INSTALL_PACKAGE,
                query=query,
                entities={'package': package},
                confidence=0.85 if package else 0.5,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['search', 'find', 'look for']):
            search_term = self._extract_search_term(query)
            return Intent(
                type=IntentType.SEARCH_PACKAGE,
                query=query,
                entities={'search_term': search_term},
                confidence=0.8,
                raw_text=query
            )
        
        # Configuration generation
        elif any(word in query_lower for word in ['generate', 'create', 'make', 'build']) and \
             any(word in query_lower for word in ['config', 'configuration']):
            # Extract description
            description = query
            for word in ['generate', 'create', 'make', 'build', 'config', 'configuration', 'a', 'me']:
                description = description.replace(word, '').strip()
            
            return Intent(
                type=IntentType.GENERATE_CONFIG,
                entities={'description': description or query},
                confidence=0.8,
                raw_text=query
            )
        
        # Flake operations
        elif any(word in query_lower for word in ['create', 'make', 'generate']) and \
             'flake' in query_lower:
            # Extract description
            description = query
            for word in ['create', 'make', 'generate', 'flake', 'a', 'for']:
                description = description.replace(word, '').strip()
            
            return Intent(
                type=IntentType.CREATE_FLAKE,
                entities={'description': description or query},
                confidence=0.85,
                raw_text=query
            )
        
        elif 'convert' in query_lower and 'flake' in query_lower:
            return Intent(
                type=IntentType.CONVERT_FLAKE,
                entities={},
                confidence=0.9,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['validate', 'check', 'verify']) and \
             'flake' in query_lower:
            return Intent(
                type=IntentType.VALIDATE_FLAKE,
                entities={},
                confidence=0.9,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['show', 'info', 'describe']) and \
             'flake' in query_lower:
            return Intent(
                type=IntentType.SHOW_FLAKE_INFO,
                entities={},
                confidence=0.9,
                raw_text=query
            )
        
        # Generation management
        elif 'generation' in query_lower and any(word in query_lower for word in ['rollback', 'switch', 'revert']):
            # Extract generation number if specified
            import re
            gen_match = re.search(r'\b(\d+)\b', query)
            generation = gen_match.group(1) if gen_match else None
            
            return Intent(
                type=IntentType.ROLLBACK_GENERATION,
                query=query,
                entities={'generation': generation},
                confidence=0.9,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['delete', 'clean', 'remove']) and 'generation' in query_lower:
            # Extract keep count if specified
            import re
            keep_match = re.search(r'keep\s*(\d+)', query_lower)
            keep = int(keep_match.group(1)) if keep_match else 5
            
            return Intent(
                type=IntentType.DELETE_GENERATIONS,
                query=query,
                entities={'keep': keep},
                confidence=0.85,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['health', 'check', 'status']) and \
             any(word in query_lower for word in ['system', 'health', 'recovery']):
            return Intent(
                type=IntentType.CHECK_HEALTH,
                query=query,
                entities={},
                confidence=0.9,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['snapshot', 'backup']) and \
             any(word in query_lower for word in ['create', 'make', 'take']):
            # Extract description
            description = query
            for word in ['create', 'make', 'take', 'snapshot', 'backup', 'a']:
                description = description.replace(word, '').strip()
            
            return Intent(
                type=IntentType.CREATE_SNAPSHOT,
                query=query,
                entities={'description': description or 'Manual snapshot'},
                confidence=0.85,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['compare', 'diff', 'difference']) and 'generation' in query_lower:
            # Extract generation numbers
            import re
            numbers = re.findall(r'\b(\d+)\b', query)
            gen1 = numbers[0] if numbers else None
            gen2 = numbers[1] if len(numbers) > 1 else None
            
            return Intent(
                type=IntentType.COMPARE_GENERATIONS,
                query=query,
                entities={'generation1': gen1, 'generation2': gen2},
                confidence=0.8 if gen1 else 0.5,
                raw_text=query
            )
        
        # Error translation
        elif any(word in query_lower for word in ['error', 'failed', 'problem']) and \
             any(word in query_lower for word in ['explain', 'what', 'help', 'fix']):
            # Extract error text
            error_text = query
            for word in ['explain', 'what', 'help', 'fix', 'this', 'error', 'the']:
                error_text = error_text.replace(word, '').strip()
            
            return Intent(
                type=IntentType.EXPLAIN_ERROR,
                query=query,
                entities={'error_text': error_text or query},
                confidence=0.9,
                raw_text=query
            )
        
        # Home Manager operations
        elif any(word in query_lower for word in ['home', 'dotfile', 'dotfiles']) and \
             any(word in query_lower for word in ['init', 'setup', 'configure', 'manage']):
            # Extract description
            description = query
            for word in ['home', 'manager', 'init', 'setup', 'configure', 'manage', 'my']:
                description = description.replace(word, '').strip()
            
            return Intent(
                type=IntentType.HOME_INIT,
                query=query,
                entities={'description': description or query},
                confidence=0.85,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['theme', 'color', 'colorscheme']) and \
             any(word in query_lower for word in ['apply', 'set', 'use', 'change']):
            # Extract theme name
            theme = None
            for theme_name in ['dracula', 'nord', 'solarized', 'gruvbox']:
                if theme_name in query_lower:
                    theme = theme_name
                    break
            
            return Intent(
                type=IntentType.APPLY_THEME,
                query=query,
                entities={'theme': theme},
                confidence=0.9 if theme else 0.7,
                raw_text=query
            )
        
        elif 'sync' in query_lower and any(word in query_lower for word in ['config', 'dotfile', 'setting']):
            return Intent(
                type=IntentType.SYNC_CONFIGS,
                query=query,
                entities={},
                confidence=0.8,
                raw_text=query
            )
        
        # Package discovery operations
        elif any(phrase in query_lower for phrase in ['discover', 'find', 'i need', 'looking for', 'want']) and \
             any(word in query_lower for word in ['package', 'program', 'app', 'software', 'tool', 'editor', 'browser']):
            # Extract what they're looking for
            search_query = query
            for word in ['discover', 'find', 'i need', 'looking for', 'want', 'package', 'program', 'for']:
                search_query = search_query.replace(word, '').strip()
            
            return Intent(
                type=IntentType.DISCOVER_PACKAGE,
                query=query,
                entities={'search_query': search_query},
                confidence=0.85,
                raw_text=query
            )
        
        elif any(phrase in query_lower for phrase in ['command not found', 'which package provides', 'what package has']) or \
             ('command' in query_lower and any(word in query_lower for word in ['find', 'which', 'what'])):
            # Extract command name
            import re
            cmd_match = re.search(r'(?:command|provides?|has)\s+["\']?(\w+)["\']?', query_lower)
            command = cmd_match.group(1) if cmd_match else None
            
            return Intent(
                type=IntentType.FIND_BY_COMMAND,
                query=query,
                entities={'command': command},
                confidence=0.9 if command else 0.7,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['browse', 'show', 'list']) and \
             any(word in query_lower for word in ['categories', 'category', 'types']):
            # Check for specific category
            category = None
            categories = ['development', 'multimedia', 'graphics', 'networking', 'games', 'science']
            for cat in categories:
                if cat in query_lower:
                    category = cat
                    break
            
            return Intent(
                type=IntentType.BROWSE_CATEGORIES,
                query=query,
                entities={'category': category},
                confidence=0.9,
                raw_text=query
            )
        
        elif any(word in query_lower for word in ['popular', 'top', 'common', 'recommended']) and \
             any(word in query_lower for word in ['packages', 'programs', 'apps', 'software']):
            # Check for category filter
            category = None
            categories = ['development', 'multimedia', 'graphics', 'networking', 'games', 'science']
            for cat in categories:
                if cat in query_lower:
                    category = cat
                    break
            
            return Intent(
                type=IntentType.SHOW_POPULAR,
                query=query,
                entities={'category': category},
                confidence=0.9,
                raw_text=query
            )
        
        # Knowledge queries
        elif any(word in query_lower for word in ['what', 'how', 'why', 'explain']):
            return Intent(
                type=IntentType.EXPLAIN_CONCEPT,
                query=query,
                entities={},
                confidence=0.7,
                raw_text=query
            )
        
        # Fallback to knowledge engine's intent extraction
        legacy_intent = self.knowledge.extract_intent(query)
        return self._convert_legacy_intent(legacy_intent, query)
    
    def _handle_system_operation(self, 
                               intent: Intent, 
                               context: Dict[str, Any]) -> BackendResponse:
        """Handle system rebuild/update operations"""
        
        # Determine operation type
        operation = OperationType.SWITCH
        if context.get('dry_run'):
            operation = OperationType.DRY_BUILD
        elif context.get('test_only'):
            operation = OperationType.TEST
        
        # Use Python backend for speed!
        result = self.python_backend.rebuild_system(operation)
        
        if result.success:
            text = self._format_success_message(result, context)
            commands = [{
                'description': f'Rebuild system ({operation.value})',
                'command': f'nixos-rebuild {operation.value}',
                'executed': True
            }]
        else:
            text = self._format_error_message(result, context)
            commands = []
        
        # Learn from this
        if self.learner:
            self.learner.record_command(
                intent=intent.type.value,
                query=intent.query,
                command=f'nixos-rebuild {operation.value}'
            )
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            commands=commands,
            operation_result=result,
            suggestions=self._get_suggestions(result)
        )
    
    def _handle_rollback(self, 
                        intent: Intent, 
                        context: Dict[str, Any]) -> BackendResponse:
        """Handle system rollback"""
        
        generation = intent.entities.get('generation')
        result = self.python_backend.rollback(generation)
        
        if result.success:
            text = f"✅ {result.message}"
            if generation:
                text += f"\n\nYour system is now at generation {generation}."
            else:
                text += "\n\nYour system has been rolled back to the previous generation."
        else:
            text = f"❌ {result.message}"
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            operation_result=result
        )
    
    def _handle_list_generations(self, 
                                intent: Intent, 
                                context: Dict[str, Any]) -> BackendResponse:
        """List system generations"""
        
        result = self.python_backend.list_generations()
        
        if result.success:
            generations = result.details['generations']
            text = "📋 System Generations:\n\n"
            
            for gen in generations[-10:]:  # Show last 10
                marker = " ← current" if gen['current'] else ""
                text += f"  {gen['number']:3d} - {gen['date']}{marker}\n"
            
            if len(generations) > 10:
                text += f"\n(Showing last 10 of {len(generations)} generations)"
        else:
            text = f"❌ {result.message}"
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            operation_result=result
        )
    
    def _handle_install_package(self, 
                              intent: Intent, 
                              context: Dict[str, Any]) -> BackendResponse:
        """Handle package installation"""
        
        package = intent.entities.get('package')
        if not package:
            return BackendResponse(
                success=False,
                text="❓ I couldn't identify which package you want to install. Please specify the package name.",
                intent=intent
            )
        
        # Check cache first
        if self.use_cache:
            cached = self.cache.get_cached_search(package)
            if cached and cached['exact_match']:
                package = cached['packages'][0]['attribute']
        
        # Use Python backend to install
        result = self.python_backend.install_package(package)
        
        if result.success:
            text = f"✅ {result.message}\n\nThe package is now available in your user profile."
            commands = [{
                'description': f'Install {package}',
                'command': f'nix profile install nixpkgs#{package}',
                'executed': True
            }]
        else:
            # Provide helpful alternatives
            text = self._format_package_error(package, result, context)
            commands = []
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            commands=commands,
            operation_result=result
        )
    
    def _handle_search_package(self, 
                             intent: Intent, 
                             context: Dict[str, Any]) -> BackendResponse:
        """Handle package search"""
        
        search_term = intent.entities.get('search_term', intent.query)
        
        # Use cache for speed
        if self.use_cache:
            cached = self.cache.get_cached_search(search_term)
            if cached:
                packages = cached['packages'][:5]
            else:
                packages = self.python_backend.search_packages(search_term)
                if packages:
                    self.cache.cache_search_results(search_term, packages, False)
        else:
            packages = self.python_backend.search_packages(search_term)
        
        if packages:
            text = f"🔍 Found {len(packages)} packages matching '{search_term}':\n\n"
            for pkg in packages[:5]:
                text += f"• **{pkg['name']}** ({pkg['version']})\n"
                text += f"  {pkg['description'][:60]}...\n\n"
        else:
            text = f"❌ No packages found matching '{search_term}'"
        
        return BackendResponse(
            success=bool(packages),
            text=text,
            intent=intent,
            metadata={'packages': packages}
        )
    
    def _handle_knowledge_query(self, 
                              intent: Intent, 
                              context: Dict[str, Any]) -> BackendResponse:
        """Handle knowledge/help queries using knowledge engine"""
        
        # Convert to legacy format for knowledge engine
        legacy_intent = {
            'action': intent.type.value,
            'query': intent.query
        }
        
        solution = self.knowledge.get_solution(legacy_intent)
        
        if solution.get('found'):
            text = self.knowledge.format_response(legacy_intent, solution)
            
            # Extract commands if present
            commands = []
            if solution.get('methods'):
                for method in solution['methods']:
                    commands.append({
                        'description': method['name'],
                        'command': method['command'],
                        'example': method.get('example', '')
                    })
        else:
            text = solution.get('suggestion', "I don't have information about that yet.")
        
        return BackendResponse(
            success=solution.get('found', False),
            text=text,
            intent=intent,
            commands=commands
        )
    
    def _handle_generate_config(self, 
                              intent: Intent, 
                              context: Dict[str, Any]) -> BackendResponse:
        """Handle configuration generation requests"""
        
        if not CONFIG_GENERATOR_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Configuration generation feature is not available. Please check your installation.",
                intent=intent
            )
        
        description = intent.entities.get('description', intent.query)
        
        try:
            # Create config generator instance
            generator = NixConfigGenerator()
            
            # Parse the natural language description
            config_intent = generator.parse_intent(description)
            
            # Check for conflicts
            conflicts = generator.check_conflicts(config_intent["modules"])
            if conflicts:
                conflict_text = "⚠️  Configuration conflicts detected:\n"
                for m1, m2 in conflicts:
                    conflict_text += f"  • {m1} conflicts with {m2}\n"
                conflict_text += "\nPlease specify which module you prefer."
                
                return BackendResponse(
                    success=False,
                    text=conflict_text,
                    intent=intent,
                    metadata={'conflicts': conflicts}
                )
            
            # Generate the configuration
            config_content = generator.generate_config(config_intent)
            
            # Format response
            text = f"✅ Generated NixOS configuration for: {description}\n\n"
            text += "📋 Configuration includes:\n"
            if config_intent["modules"]:
                text += f"  • Modules: {', '.join(config_intent['modules'])}\n"
            if config_intent["packages"]:
                text += f"  • Packages: {', '.join(config_intent['packages'])}\n"
            if config_intent["users"]:
                text += f"  • Users: {', '.join([u['name'] for u in config_intent['users']])}\n"
            
            text += f"\n💾 Configuration saved to: /tmp/generated-config.nix\n"
            text += f"\n📝 To apply this configuration:\n"
            text += f"  1. Review: cat /tmp/generated-config.nix\n"
            text += f"  2. Test: sudo nixos-rebuild test -I nixos-config=/tmp/generated-config.nix\n"
            text += f"  3. Apply: sudo cp /tmp/generated-config.nix /etc/nixos/configuration.nix && sudo nixos-rebuild switch\n"
            
            # Save the configuration
            success, save_msg = generator.save_config(config_content, "/tmp/generated-config.nix", backup=False)
            
            if not success:
                text = f"❌ Failed to save configuration: {save_msg}"
                return BackendResponse(
                    success=False,
                    text=text,
                    intent=intent
                )
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                metadata={
                    'config_path': '/tmp/generated-config.nix',
                    'config_intent': config_intent,
                    'config_content': config_content
                },
                commands=[{
                    'description': 'Review generated configuration',
                    'command': 'cat /tmp/generated-config.nix'
                }, {
                    'description': 'Test configuration',
                    'command': 'sudo nixos-rebuild test -I nixos-config=/tmp/generated-config.nix'
                }]
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error generating configuration: {str(e)}",
                intent=intent
            )
    
    def _handle_create_flake(self, 
                           intent: Intent, 
                           context: Dict[str, Any]) -> BackendResponse:
        """Handle flake creation requests"""
        
        try:
            # Import flake manager
            from luminous_nix.core.flake_manager import FlakeManager
            manager = FlakeManager()
            
            description = intent.entities.get('description', intent.query)
            path = context.get('path', Path("."))
            
            # Parse the intent
            flake_intent = manager.parse_intent(description)
            
            # Create the flake
            success, message = manager.create_flake(flake_intent, path)
            
            if success:
                text = f"✅ {message}\n\n"
                text += "📦 Created development environment:\n"
                if flake_intent['language']:
                    text += f"   Language: {flake_intent['language'].capitalize()}\n"
                if flake_intent['packages']:
                    text += f"   Packages: {', '.join(flake_intent['packages'])}\n"
                if flake_intent['features']:
                    text += f"   Features: {', '.join(flake_intent['features'])}\n"
                
                text += "\n🚀 To use this environment:\n"
                text += "   nix develop        # Enter the dev shell\n"
                text += "   nix flake check    # Validate the flake\n"
                text += "   nix flake show     # Show available outputs"
                
                commands = [{
                    'description': 'Enter development shell',
                    'command': 'nix develop'
                }, {
                    'description': 'Validate flake',
                    'command': 'nix flake check'
                }]
            else:
                text = f"❌ {message}"
                commands = []
            
            return BackendResponse(
                success=success,
                text=text,
                intent=intent,
                commands=commands,
                metadata={'flake_intent': flake_intent}
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Flake management feature is not available. Please check your installation.",
                intent=intent
            )
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error creating flake: {str(e)}",
                intent=intent
            )
    
    def _handle_validate_flake(self, 
                              intent: Intent, 
                              context: Dict[str, Any]) -> BackendResponse:
        """Handle flake validation requests"""
        
        try:
            from luminous_nix.core.flake_manager import FlakeManager
            manager = FlakeManager()
            
            path = context.get('path', Path("."))
            success, message = manager.validate_flake(path)
            
            if success:
                text = f"✅ {message}"
            else:
                text = f"❌ {message}"
            
            return BackendResponse(
                success=success,
                text=text,
                intent=intent
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Flake management feature is not available.",
                intent=intent
            )
    
    def _handle_convert_flake(self, 
                            intent: Intent, 
                            context: Dict[str, Any]) -> BackendResponse:
        """Handle flake conversion requests"""
        
        try:
            from luminous_nix.core.flake_manager import FlakeManager
            manager = FlakeManager()
            
            path = context.get('path', Path("."))
            success, message = manager.convert_to_flake(path)
            
            if success:
                text = f"✅ {message}\n\n"
                text += "🎉 Your project now uses Nix flakes!\n"
                text += "Run 'nix develop' to enter the dev environment"
                
                commands = [{
                    'description': 'Enter the new flake environment',
                    'command': 'nix develop'
                }]
            else:
                text = f"❌ {message}"
                commands = []
            
            return BackendResponse(
                success=success,
                text=text,
                intent=intent,
                commands=commands
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Flake management feature is not available.",
                intent=intent
            )
    
    def _handle_show_flake_info(self, 
                               intent: Intent, 
                               context: Dict[str, Any]) -> BackendResponse:
        """Handle flake info display requests"""
        
        try:
            from luminous_nix.core.flake_manager import FlakeManager
            manager = FlakeManager()
            
            path = context.get('path', Path("."))
            info_text = manager.show_flake_info(path)
            
            return BackendResponse(
                success=True,
                text=info_text,
                intent=intent
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Flake management feature is not available.",
                intent=intent
            )
    
    def _handle_rollback_generation(self, 
                                   intent: Intent, 
                                   context: Dict[str, Any]) -> BackendResponse:
        """Handle generation rollback requests"""
        
        try:
            from luminous_nix.core.generation_manager import GenerationManager
            manager = GenerationManager()
            
            generation = intent.entities.get('generation')
            
            if generation:
                # Validate generation number
                try:
                    gen_num = int(generation)
                except ValueError:
                    return BackendResponse(
                        success=False,
                        text=f"❌ Invalid generation number: {generation}",
                        intent=intent
                    )
            else:
                gen_num = None
            
            # Perform rollback
            success, message = manager.rollback(gen_num)
            
            if success:
                if gen_num:
                    text = f"✅ {message}\n\n"
                    text += f"Your system has been rolled back to generation {gen_num}.\n"
                else:
                    text = f"✅ {message}\n\n"
                    text += "Your system has been rolled back to the previous generation.\n"
                text += "\n⚠️  Please reboot for all changes to take effect."
                
                commands = [{
                    'description': 'Reboot system to apply changes',
                    'command': 'sudo reboot'
                }]
            else:
                text = f"❌ {message}"
                commands = []
            
            return BackendResponse(
                success=success,
                text=text,
                intent=intent,
                commands=commands
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Generation management feature is not available. Please check your installation.",
                intent=intent
            )
    
    def _handle_delete_generations(self, 
                                  intent: Intent, 
                                  context: Dict[str, Any]) -> BackendResponse:
        """Handle generation deletion requests"""
        
        try:
            from luminous_nix.core.generation_manager import GenerationManager
            manager = GenerationManager()
            
            keep_last = intent.entities.get('keep', 5)
            
            # Get current generations for info
            generations = manager.list_generations()
            if len(generations) <= keep_last:
                return BackendResponse(
                    success=True,
                    text=f"✅ Only {len(generations)} generations exist, nothing to delete.\nYou're already at the minimum recommended generations.",
                    intent=intent
                )
            
            # Delete old generations
            success, message = manager.delete_generations(keep_last)
            
            if success:
                text = f"✅ {message}\n\n"
                text += "🧹 To reclaim disk space, run:\n"
                text += "   nix-collect-garbage\n\n"
                text += "💡 This will remove the actual files from the Nix store."
                
                commands = [{
                    'description': 'Reclaim disk space',
                    'command': 'nix-collect-garbage'
                }]
            else:
                text = f"❌ {message}"
                commands = []
            
            return BackendResponse(
                success=success,
                text=text,
                intent=intent,
                commands=commands
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Generation management feature is not available.",
                intent=intent
            )
    
    def _handle_check_health(self, 
                           intent: Intent, 
                           context: Dict[str, Any]) -> BackendResponse:
        """Handle system health check requests"""
        
        try:
            from luminous_nix.core.generation_manager import GenerationManager
            manager = GenerationManager()
            
            health = manager.check_system_health()
            
            # Format health report
            text = "🏥 System Health Check:\n\n"
            
            # Disk usage
            disk_emoji = "✅" if health.disk_usage_percent < 80 else "⚠️" if health.disk_usage_percent < 90 else "❌"
            text += f"{disk_emoji} Disk Usage: {health.disk_usage_percent:.1f}%\n"
            
            # Memory usage
            mem_emoji = "✅" if health.memory_usage_percent < 80 else "⚠️" if health.memory_usage_percent < 90 else "❌"
            text += f"{mem_emoji} Memory Usage: {health.memory_usage_percent:.1f}%\n"
            
            # Failed services
            svc_emoji = "✅" if len(health.failed_services) == 0 else "❌"
            text += f"{svc_emoji} Failed Services: {len(health.failed_services)}\n"
            if health.failed_services:
                for svc in health.failed_services[:3]:
                    text += f"   - {svc}\n"
                if len(health.failed_services) > 3:
                    text += f"   ... and {len(health.failed_services) - 3} more\n"
            
            # Config errors
            cfg_emoji = "✅" if len(health.config_errors) == 0 else "❌"
            text += f"{cfg_emoji} Config Errors: {len(health.config_errors)}\n"
            if health.config_errors:
                for err in health.config_errors[:2]:
                    text += f"   - {err[:60]}...\n"
            
            # Last boot
            if health.last_successful_boot:
                text += f"\n📅 Last Boot: {health.last_successful_boot.strftime('%Y-%m-%d %H:%M')}\n"
            
            # Overall status
            status_emoji = "✅" if health.is_healthy else "⚠️"
            status_text = "Healthy" if health.is_healthy else "Issues Detected"
            text += f"\n{status_emoji} Overall Status: {status_text}\n"
            
            # Warnings
            if health.warnings:
                text += "\n⚠️  Warnings:\n"
                for warning in health.warnings:
                    text += f"   • {warning}\n"
            
            # Suggestions
            suggestions = manager.suggest_recovery_actions(health)
            if suggestions:
                text += "\n💡 Recommended Actions:\n"
                for i, suggestion in enumerate(suggestions, 1):
                    text += f"   {i}. {suggestion}\n"
            
            # Add commands for common fixes
            commands = []
            if health.disk_usage_percent > 80:
                commands.append({
                    'description': 'Free up disk space',
                    'command': 'nix-collect-garbage -d'
                })
            if health.failed_services:
                commands.append({
                    'description': 'View service logs',
                    'command': f'journalctl -u {health.failed_services[0]} --no-pager'
                })
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                commands=commands,
                metadata={'health': health.__dict__}
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Generation management feature is not available.",
                intent=intent
            )
    
    def _handle_create_snapshot(self, 
                              intent: Intent, 
                              context: Dict[str, Any]) -> BackendResponse:
        """Handle recovery snapshot creation"""
        
        try:
            from luminous_nix.core.generation_manager import GenerationManager
            manager = GenerationManager()
            
            description = intent.entities.get('description', 'Manual recovery snapshot')
            
            # Create snapshot
            success, message = manager.create_recovery_snapshot(description)
            
            if success:
                text = f"✅ {message}\n\n"
                text += f"📸 Snapshot created with description:\n"
                text += f"   \"{description}\"\n\n"
                text += "💡 You can rollback to this snapshot if anything goes wrong.\n"
                text += "Use 'ask-nix generation list' to see all snapshots."
                
                commands = [{
                    'description': 'List all generations',
                    'command': 'ask-nix generation list'
                }]
            else:
                text = f"❌ {message}\n\n"
                if "configuration has errors" in message:
                    text += "💡 Fix configuration errors before creating a snapshot:\n"
                    text += "   nixos-rebuild test"
                    commands = [{
                        'description': 'Test configuration',
                        'command': 'nixos-rebuild test'
                    }]
                else:
                    commands = []
            
            return BackendResponse(
                success=success,
                text=text,
                intent=intent,
                commands=commands
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Generation management feature is not available.",
                intent=intent
            )
    
    def _handle_compare_generations(self, 
                                   intent: Intent, 
                                   context: Dict[str, Any]) -> BackendResponse:
        """Handle generation comparison requests"""
        
        try:
            from luminous_nix.core.generation_manager import GenerationManager
            manager = GenerationManager()
            
            gen1 = intent.entities.get('generation1')
            gen2 = intent.entities.get('generation2')
            
            # Validate generation numbers
            if not gen1:
                return BackendResponse(
                    success=False,
                    text="❌ Please specify which generations to compare.",
                    intent=intent
                )
            
            try:
                gen1_num = int(gen1)
                gen2_num = int(gen2) if gen2 else manager._get_current_generation()
            except ValueError:
                return BackendResponse(
                    success=False,
                    text="❌ Invalid generation number(s).",
                    intent=intent
                )
            
            # Get diff
            diff = manager.get_generation_diff(gen1_num, gen2_num)
            
            # Format comparison
            text = f"🔍 Comparing generation {gen1_num} with {gen2_num}:\n\n"
            
            if diff['kernel_changed']:
                text += "⚠️  Kernel version changed\n"
            
            if diff['nixos_version_changed']:
                text += "⚠️  NixOS version changed\n"
            
            if diff['packages_added']:
                text += f"\n✅ Added {len(diff['packages_added'])} packages:\n"
                for pkg in diff['packages_added'][:5]:
                    text += f"   + {pkg}\n"
                if len(diff['packages_added']) > 5:
                    text += f"   ... and {len(diff['packages_added']) - 5} more\n"
            
            if diff['packages_removed']:
                text += f"\n❌ Removed {len(diff['packages_removed'])} packages:\n"
                for pkg in diff['packages_removed'][:5]:
                    text += f"   - {pkg}\n"
                if len(diff['packages_removed']) > 5:
                    text += f"   ... and {len(diff['packages_removed']) - 5} more\n"
            
            if diff['config_changes']:
                text += f"\n🔧 {len(diff['config_changes'])} configuration changes\n"
            
            if not any([diff['kernel_changed'], diff['nixos_version_changed'], 
                       diff['packages_added'], diff['packages_removed']]):
                text += "✅ No significant differences found\n"
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                metadata={'diff': diff}
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Generation management feature is not available.",
                intent=intent
            )
    
    def _handle_explain_error(self, 
                            intent: Intent, 
                            context: Dict[str, Any]) -> BackendResponse:
        """Handle error explanation requests"""
        
        try:
            from luminous_nix.core.error_translator import ErrorTranslator
            translator = ErrorTranslator()
            
            error_text = intent.entities.get('error_text', intent.query)
            
            # Translate the error
            translated = translator.translate_error(error_text)
            
            # Get persona from context
            persona = context.get('personality', 'friendly')
            
            # Format response
            text = translated.format_for_persona(persona)
            
            # Add learn more section
            if translated.learn_more_topics:
                text += "\n\n💡 Learn more about:"
                for topic in translated.learn_more_topics:
                    text += f"\n  • ask-nix help {topic}"
            
            # Add related commands
            commands = []
            if translated.suggested_fixes:
                for fix in translated.suggested_fixes[:3]:
                    # Try to extract command from fix
                    if "ask-nix" in fix:
                        import re
                        cmd_match = re.search(r"ask-nix ['\"]([^'\"]+)['\"]", fix)
                        if cmd_match:
                            commands.append({
                                'description': 'Suggested fix',
                                'command': f'ask-nix {cmd_match.group(1)}'
                            })
                    elif "nix" in fix or "sudo" in fix:
                        # Extract command-like strings
                        cmd_match = re.search(r'`([^`]+)`|: ([^\n]+)$', fix)
                        if cmd_match:
                            cmd = cmd_match.group(1) or cmd_match.group(2)
                            commands.append({
                                'description': 'Suggested command',
                                'command': cmd.strip()
                            })
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                commands=commands,
                metadata={
                    'confidence': translated.confidence,
                    'error_type': translated._detect_error_type()
                }
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Error translation feature is not available. Please check your installation.",
                intent=intent
            )
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error analyzing the error: {str(e)}",
                intent=intent
            )
    
    def _handle_analyze_log(self, 
                          intent: Intent, 
                          context: Dict[str, Any]) -> BackendResponse:
        """Handle log analysis requests"""
        
        try:
            from luminous_nix.core.error_translator import ErrorTranslator
            translator = ErrorTranslator()
            
            log_path = intent.entities.get('log_path')
            if not log_path:
                return BackendResponse(
                    success=False,
                    text="❌ Please specify a log file to analyze.",
                    intent=intent
                )
            
            # Read log file
            try:
                with open(log_path, 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                return BackendResponse(
                    success=False,
                    text=f"❌ Log file not found: {log_path}",
                    intent=intent
                )
            except Exception as e:
                return BackendResponse(
                    success=False,
                    text=f"❌ Error reading log file: {str(e)}",
                    intent=intent
                )
            
            # Find errors in log
            import re
            error_pattern = re.compile(r'error:.*?(?=\n(?:error:|warning:|$))', re.DOTALL | re.MULTILINE)
            errors_found = error_pattern.findall(content)
            
            if not errors_found:
                return BackendResponse(
                    success=True,
                    text="✅ No errors found in the log file! Everything looks good.",
                    intent=intent
                )
            
            # Analyze first few errors
            text = f"🔍 Found {len(errors_found)} error(s) in the log:\n\n"
            
            for i, error_text in enumerate(errors_found[:3], 1):
                translated = translator.translate_error(error_text)
                text += f"**Error {i}**: {translated.simple_explanation}\n"
                if translated.suggested_fixes:
                    text += f"   Fix: {translated.suggested_fixes[0]}\n"
                text += "\n"
            
            if len(errors_found) > 3:
                text += f"... and {len(errors_found) - 3} more errors.\n\n"
            
            text += "💡 Use 'ask-nix error explain' on specific errors for detailed help."
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                metadata={'error_count': len(errors_found)}
            )
            
        except ImportError:
            return BackendResponse(
                success=False,
                text="❌ Error translation feature is not available.",
                intent=intent
            )
    
    def _handle_home_init(self, 
                         intent: Intent, 
                         context: Dict[str, Any]) -> BackendResponse:
        """Handle home configuration initialization"""
        
        if not HOME_MANAGER_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Home Manager feature is not available. Please check your installation.",
                intent=intent
            )
        
        try:
            manager = HomeManager()
            description = intent.entities.get('description', '')
            
            # Initialize configuration from description
            config = manager.init_home_config(description)
            
            # Generate home.nix
            result = manager.apply_config(config, preview=True)
            
            text = "🏠 Home Configuration Initialized\n\n"
            
            if config.dotfiles:
                text += "**Dotfiles:**\n"
                for dotfile in config.dotfiles:
                    text += f"  • {dotfile.description}\n"
                text += "\n"
            
            if config.themes:
                text += "**Themes:**\n"
                for theme in config.themes:
                    text += f"  • {theme.name}\n"
                text += "\n"
            
            if config.shell_config.get("shell") != "bash":
                text += f"**Shell:** {config.shell_config['shell']}\n\n"
            
            text += "**Generated home.nix:** (preview)\n"
            text += "```nix\n"
            text += result["home_nix"][:500] + "...\n" if len(result["home_nix"]) > 500 else result["home_nix"]
            text += "```\n\n"
            
            text += "✨ To apply this configuration, run: `ask-nix home apply`"
            
            commands = [{
                'description': 'Apply home configuration',
                'command': 'ask-nix home apply'
            }]
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                commands=commands
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error initializing home configuration: {str(e)}",
                intent=intent
            )
    
    def _handle_apply_theme(self, 
                           intent: Intent, 
                           context: Dict[str, Any]) -> BackendResponse:
        """Handle theme application requests"""
        
        if not HOME_MANAGER_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Home Manager feature is not available.",
                intent=intent
            )
        
        try:
            manager = HomeManager()
            theme_name = intent.entities.get('theme')
            
            if not theme_name:
                # List available themes
                text = "🎨 Available themes:\n\n"
                for theme in manager.themes:
                    text += f"  • {theme}\n"
                text += "\n💡 Use: `ask-nix apply dracula theme`"
                
                return BackendResponse(
                    success=True,
                    text=text,
                    intent=intent
                )
            
            # Apply theme
            result = manager.apply_theme(theme_name, ["terminal"])
            
            if result["success"]:
                text = f"🎨 Applying {theme_name} theme\n\n"
                for change in result["changes"]:
                    text += f"  • {change['application']}: {change['file']}\n"
                text += "\n✅ Theme applied! Restart your terminal to see changes."
            else:
                text = f"❌ {result.get('error', 'Failed to apply theme')}"
                if "available_themes" in result:
                    text += "\n\nAvailable themes: " + ", ".join(result["available_themes"])
            
            return BackendResponse(
                success=result["success"],
                text=text,
                intent=intent
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error applying theme: {str(e)}",
                intent=intent
            )
    
    def _handle_sync_configs(self, 
                            intent: Intent, 
                            context: Dict[str, Any]) -> BackendResponse:
        """Handle configuration sync requests"""
        
        if not HOME_MANAGER_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Home Manager feature is not available.",
                intent=intent
            )
        
        try:
            manager = HomeManager()
            
            # For now, return a helpful message about sync
            text = "🔄 Configuration Sync\n\n"
            text += "To sync your configurations between machines:\n\n"
            text += "1. **Push configs to git:**\n"
            text += "   ```\n"
            text += "   cd ~/.config/nix-humanity\n"
            text += "   git init\n"
            text += "   git add home.nix\n"
            text += "   git commit -m 'My home configuration'\n"
            text += "   git push\n"
            text += "   ```\n\n"
            text += "2. **Pull on other machine:**\n"
            text += "   ```\n"
            text += "   git clone <your-repo> ~/.config/nix-humanity\n"
            text += "   ask-nix home apply\n"
            text += "   ```\n\n"
            text += "💡 Full sync support coming soon!"
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error with sync: {str(e)}",
                intent=intent
            )
    
    def _handle_list_home_configs(self, 
                                 intent: Intent, 
                                 context: Dict[str, Any]) -> BackendResponse:
        """Handle listing managed configurations"""
        
        if not HOME_MANAGER_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Home Manager feature is not available.",
                intent=intent
            )
        
        try:
            manager = HomeManager()
            managed = manager.list_managed_configs()
            
            text = "📋 Home Manager Status\n\n"
            
            # Dotfiles
            if managed["dotfiles"]:
                text += "**Managed Dotfiles:**\n"
                for dotfile in managed["dotfiles"]:
                    text += f"  • {dotfile}\n"
            else:
                text += "**No dotfiles currently managed**\n"
            
            text += "\n"
            
            # Themes
            text += "**Available Themes:**\n"
            for theme in managed["themes"]:
                text += f"  • {theme}\n"
            
            # Backups
            if managed["backups"]:
                text += "\n**Recent Backups:**\n"
                for backup in managed["backups"][:5]:
                    text += f"  • {backup}\n"
            
            text += "\n💡 Tips:\n"
            text += "  • Use `ask-nix home init` to set up your configuration\n"
            text += "  • Use `ask-nix home add vim` to add specific dotfiles\n"
            text += "  • Use `ask-nix apply dracula theme` to apply themes"
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error listing configurations: {str(e)}",
                intent=intent
            )
    
    def _handle_discover_package(self, 
                                intent: Intent, 
                                context: Dict[str, Any]) -> BackendResponse:
        """Handle smart package discovery requests"""
        
        if not PACKAGE_DISCOVERY_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Package discovery feature is not available. Please check your installation.",
                intent=intent
            )
        
        try:
            discovery = PackageDiscovery()
            search_query = intent.entities.get('search_query', intent.query)
            
            # Search for packages using natural language
            matches = discovery.search_packages(search_query, limit=10)
            
            if not matches:
                text = f"❌ No packages found matching '{search_query}'\n\n"
                text += "💡 Try:\n"
                text += "  • Using different keywords\n"
                text += "  • Browsing categories with 'show package categories'\n"
                text += "  • Searching by command with 'which package provides <command>'"
                
                return BackendResponse(
                    success=False,
                    text=text,
                    intent=intent
                )
            
            text = f"🔍 Found {len(matches)} packages matching '{search_query}':\n\n"
            
            for match in matches[:5]:
                text += f"**{match.name}**\n"
                text += f"  {match.description}\n"
                text += f"  Match score: {'⭐' * int(match.score * 5)}\n"
                text += f"  Reason: {match.reason}\n\n"
            
            if len(matches) > 5:
                text += f"... and {len(matches) - 5} more matches\n\n"
            
            # Show installation command for top match
            text += f"📦 To install the top match:\n"
            text += f"   `ask-nix install {matches[0].name}`\n\n"
            
            # Show alternatives
            alternatives = discovery.find_alternatives(matches[0].name)
            if alternatives:
                text += f"🔄 Similar to {matches[0].name}: {', '.join(alternatives[:3])}"
            
            commands = [{
                'description': f'Install {matches[0].name}',
                'command': f'ask-nix install {matches[0].name}'
            }]
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                commands=commands,
                metadata={'matches': [m.__dict__ for m in matches]}
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error discovering packages: {str(e)}",
                intent=intent
            )
    
    def _handle_find_by_command(self, 
                               intent: Intent, 
                               context: Dict[str, Any]) -> BackendResponse:
        """Handle finding packages by command"""
        
        if not PACKAGE_DISCOVERY_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Package discovery feature is not available.",
                intent=intent
            )
        
        try:
            discovery = PackageDiscovery()
            command = intent.entities.get('command')
            
            if not command:
                return BackendResponse(
                    success=False,
                    text="❌ Please specify which command you're looking for.",
                    intent=intent
                )
            
            suggestions = discovery.suggest_by_command(command)
            
            if not suggestions:
                text = f"❌ No packages found that provide '{command}'\n\n"
                text += "The command might be:\n"
                text += "  • Part of a different package\n"
                text += "  • Available under a different name\n"
                text += "  • Not yet packaged for NixOS"
                
                return BackendResponse(
                    success=False,
                    text=text,
                    intent=intent
                )
            
            text = f"🔧 Command '{command}' not found\n\n"
            text += "📦 These packages provide this command:\n\n"
            
            commands = []
            for i, match in enumerate(suggestions[:3], 1):
                text += f"{i}. **{match.name}**\n"
                text += f"   {match.description}\n"
                text += f"   Install: `nix-env -iA nixpkgs.{match.name}`\n\n"
                
                if i == 1:
                    commands.append({
                        'description': f'Install {match.name}',
                        'command': f'ask-nix install {match.name}'
                    })
            
            text += f"💡 Quick install the most likely match:\n"
            text += f"   `ask-nix install {suggestions[0].name}`"
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                commands=commands,
                metadata={'suggestions': [s.__dict__ for s in suggestions]}
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error finding command: {str(e)}",
                intent=intent
            )
    
    def _handle_browse_categories(self, 
                                 intent: Intent, 
                                 context: Dict[str, Any]) -> BackendResponse:
        """Handle browsing package categories"""
        
        if not PACKAGE_DISCOVERY_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Package discovery feature is not available.",
                intent=intent
            )
        
        try:
            discovery = PackageDiscovery()
            category = intent.entities.get('category')
            categories = discovery.browse_categories()
            
            if category:
                # Show specific category
                if category not in categories:
                    text = f"❌ Category '{category}' not found\n\n"
                    text += f"Available categories: {', '.join(categories.keys())}"
                    
                    return BackendResponse(
                        success=False,
                        text=text,
                        intent=intent
                    )
                
                cat_info = categories[category]
                text = f"📁 **{category.title()} Packages**\n\n"
                text += f"**Keywords:** {', '.join(cat_info['keywords'])}\n"
                text += f"**Description:** {cat_info['description']}\n\n"
                text += "**Top Packages:**\n"
                
                commands = []
                for pkg in cat_info['top_packages'][:5]:
                    text += f"  • **{pkg}** - `ask-nix install {pkg}`\n"
                    if not commands:
                        commands.append({
                            'description': f'Install {pkg}',
                            'command': f'ask-nix install {pkg}'
                        })
                
            else:
                # Show all categories
                text = "📚 **Package Categories**\n\n"
                
                for cat_name, cat_info in list(categories.items())[:6]:
                    text += f"**{cat_name.title()}**\n"
                    text += f"  Keywords: {', '.join(cat_info['keywords'][:3])}...\n"
                    text += f"  Top packages: {', '.join(cat_info['top_packages'][:3])}\n\n"
                
                text += "💡 To browse a specific category:\n"
                text += "   `ask-nix browse development packages`"
                
                commands = [{
                    'description': 'Browse development packages',
                    'command': 'ask-nix browse development packages'
                }]
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                commands=commands
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error browsing categories: {str(e)}",
                intent=intent
            )
    
    def _handle_show_popular(self, 
                            intent: Intent, 
                            context: Dict[str, Any]) -> BackendResponse:
        """Handle showing popular packages"""
        
        if not PACKAGE_DISCOVERY_AVAILABLE:
            return BackendResponse(
                success=False,
                text="❌ Package discovery feature is not available.",
                intent=intent
            )
        
        try:
            discovery = PackageDiscovery()
            category = intent.entities.get('category')
            
            title = f"Popular {category.title()} Packages" if category else "Popular Packages"
            popular = discovery.get_popular_packages(category)
            
            if not popular:
                text = f"❌ No popular packages found{' in ' + category if category else ''}"
                return BackendResponse(
                    success=False,
                    text=text,
                    intent=intent
                )
            
            text = f"⭐ **{title}**\n\n"
            
            commands = []
            for pkg_name, pkg_desc in popular[:10]:
                text += f"**{pkg_name}**\n"
                text += f"  {pkg_desc}\n"
                text += f"  Install: `ask-nix install {pkg_name}`\n\n"
                
                if not commands:
                    commands.append({
                        'description': f'Install {pkg_name}',
                        'command': f'ask-nix install {pkg_name}'
                    })
            
            text += "💡 These are commonly used packages based on community usage"
            
            return BackendResponse(
                success=True,
                text=text,
                intent=intent,
                commands=commands,
                metadata={'popular': popular}
            )
            
        except Exception as e:
            return BackendResponse(
                success=False,
                text=f"❌ Error showing popular packages: {str(e)}",
                intent=intent
            )
    
    def _handle_unknown(self, 
                       intent: Intent, 
                       context: Dict[str, Any]) -> BackendResponse:
        """Handle unknown intents"""
        
        suggestions = [
            "install <package> - Install a package",
            "update system - Update NixOS",
            "rollback - Go to previous generation",
            "list generations - Show system history",
            "check health - System health status",
            "explain error <error> - Translate NixOS errors",
            "search <term> - Search for packages",
            "discover packages for <purpose> - Find packages using natural language",
            "which package provides <command> - Find package by command",
            "browse package categories - Explore packages by category",
            "show popular packages - See commonly used packages",
            "generate config for <description> - Create NixOS configuration",
            "create flake for <project> - Create a development environment",
            "setup home manager - Configure dotfiles and themes",
            "apply <theme> theme - Apply color theme",
            "list home configs - Show managed configurations",
            "help - Get general help"
        ]
        
        text = (f"I'm not sure what you want to do. Here are some things I can help with:\n\n"
                + "\n".join(f"• {s}" for s in suggestions))
        
        return BackendResponse(
            success=False,
            text=text,
            intent=intent,
            suggestions=suggestions
        )
    
    def _check_plugins(self, 
                      intent: Intent, 
                      context: Dict[str, Any]) -> Optional[BackendResponse]:
        """Check if any plugin can handle this intent"""
        
        for plugin in self.plugin_manager.get_active_plugins():
            if plugin.can_handle(intent.query):
                try:
                    result = plugin.handle(intent.query, context)
                    return BackendResponse(
                        success=True,
                        text=result.get('response', ''),
                        intent=intent,
                        commands=result.get('commands', []),
                        metadata={'plugin': plugin.name}
                    )
                except Exception as e:
                    print(f"Plugin {plugin.name} error: {e}")
        
        return None
    
    def _extract_package_name(self, query: str) -> Optional[str]:
        """Extract package name from query"""
        query_lower = query.lower()
        
        # Remove common words
        stopwords = ['install', 'get', 'add', 'please', 'can', 'you', 'i', 
                    'want', 'need', 'the', 'a', 'an', 'package', 'program']
        
        words = query_lower.split()
        for word in words:
            if word not in stopwords and len(word) > 2:
                return word
        
        return None
    
    def _extract_search_term(self, query: str) -> str:
        """Extract search term from query"""
        query_lower = query.lower()
        
        # Try to find what comes after search/find/look for
        for phrase in ['search for', 'find', 'look for']:
            if phrase in query_lower:
                parts = query_lower.split(phrase)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # Fallback to removing common words
        stopwords = ['search', 'find', 'look', 'for', 'please', 'can', 'you']
        words = query_lower.split()
        terms = [w for w in words if w not in stopwords]
        
        return ' '.join(terms) if terms else query
    
    def _convert_legacy_intent(self, legacy_intent: Dict, query: str) -> Intent:
        """Convert legacy knowledge engine intent to new format"""
        
        action_map = {
            'install_package': IntentType.INSTALL_PACKAGE,
            'search_package': IntentType.SEARCH_PACKAGE,
            'update_system': IntentType.UPDATE_SYSTEM,
            'rollback_system': IntentType.ROLLBACK_SYSTEM,
            'unknown': IntentType.UNKNOWN
        }
        
        intent_type = action_map.get(legacy_intent.get('action'), IntentType.UNKNOWN)
        
        return Intent(
            type=intent_type,
            query=query,
            entities={
                'package': legacy_intent.get('package'),
                'original_action': legacy_intent.get('action')
            },
            confidence=0.6,  # Lower confidence for legacy conversion
            raw_text=query
        )
    
    def _format_success_message(self, 
                              result: OperationResult, 
                              context: Dict[str, Any]) -> str:
        """Format success message based on personality"""
        
        personality = context.get('personality', 'friendly')
        
        if personality == 'minimal':
            return f"✓ {result.message}"
        
        elif personality == 'friendly':
            return (f"✅ {result.message}\n\n"
                   f"Completed in {result.duration:.1f} seconds. "
                   "Your system has been successfully updated!")
        
        elif personality == 'encouraging':
            return (f"🎉 {result.message}\n\n"
                   f"Great job keeping your system updated! "
                   f"Completed in just {result.duration:.1f} seconds.")
        
        elif personality == 'technical':
            details = result.details or {}
            return (f"✅ {result.message}\n\n"
                   f"Duration: {result.duration:.3f}s\n"
                   f"API Used: {details.get('api_used', False)}\n"
                   f"Profile: {details.get('profile', 'system')}")
        
        else:
            return f"✅ {result.message}"
    
    def _format_error_message(self, 
                            result: OperationResult, 
                            context: Dict[str, Any]) -> str:
        """Format error message helpfully"""
        
        base_msg = f"❌ {result.message}"
        
        # Add helpful suggestions based on error
        if result.error:
            if 'permission' in result.error.lower():
                base_msg += "\n\n💡 Try running with sudo"
            elif 'network' in result.error.lower():
                base_msg += "\n\n💡 Check your internet connection"
            elif 'disk space' in result.error.lower():
                base_msg += "\n\n💡 Free up some disk space with: nix-collect-garbage -d"
        
        return base_msg
    
    def _format_package_error(self, 
                            package: str, 
                            result: OperationResult, 
                            context: Dict[str, Any]) -> str:
        """Format package installation error with alternatives"""
        
        text = f"❌ {result.message}\n\n"
        
        # Try to search for similar packages
        similar = self.python_backend.search_packages(package)
        if similar:
            text += "💡 Did you mean one of these?\n\n"
            for pkg in similar[:3]:
                text += f"• {pkg['name']} - {pkg['description'][:50]}...\n"
        
        # Add installation methods
        text += f"\n📚 For system-wide installation, add to /etc/nixos/configuration.nix:\n"
        text += f"```\nenvironment.systemPackages = with pkgs; [ {package} ];\n```"
        
        return text
    
    def _get_suggestions(self, result: OperationResult) -> List[str]:
        """Get relevant suggestions based on operation result"""
        
        suggestions = []
        
        if result.success and result.operation == OperationType.SWITCH:
            suggestions.extend([
                "list generations - See all system generations",
                "rollback - Go back if something broke"
            ])
        elif not result.success:
            suggestions.extend([
                "Check the logs for more details",
                "Try with --dry-run first",
                "Ask for help with the specific error"
            ])
        
        return suggestions


def test_unified_backend():
    """Test the unified backend"""
    print("🎯 Unified Nix Backend Test")
    print("=" * 60)
    
    backend = UnifiedNixBackend()
    
    # Test queries
    test_queries = [
        "install firefox",
        "update my system",
        "what's a generation?",
        "search for text editors",
        "rollback to previous",
        "list generations"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        
        # Extract intent
        intent = backend.extract_intent(query)
        print(f"🎯 Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
        
        # Process with context
        context = {
            'personality': 'friendly',
            'frontend': 'cli',
            'collect_feedback': False
        }
        
        response = backend.process_intent(intent, context)
        print(f"✅ Success: {response.success}")
        print(f"💬 Response: {response.text[:150]}...")
        
        if response.commands:
            print(f"📦 Commands: {len(response.commands)}")


if __name__ == "__main__":
    test_unified_backend()