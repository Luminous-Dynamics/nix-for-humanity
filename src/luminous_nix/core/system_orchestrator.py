"""
Unified System Orchestrator for Luminous Nix

This module provides a clean, unified interface to all the integrated systems:
- Error Intelligence
- Configuration Management  
- Adaptive Complexity Manager
- Generation Manager
- Learning System
- Native API Integration
- Plugin Ecosystem

The orchestrator coordinates all subsystems to provide a cohesive experience.
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from queue import Empty

# Import all our integrated systems
from .error_intelligence import ErrorIntelligence

# Import AST-enhanced components if available
try:
    from .error_intelligence_ast import ASTErrorIntelligence
    from .config_generator_ast import ASTConfigGenerator
    AST_COMPONENTS_AVAILABLE = True
except ImportError:
    AST_COMPONENTS_AVAILABLE = False
from ..config.config_manager import ConfigManager
from ..learning.adaptation import AdaptiveComplexityManager, ComplexityStage
from .generation_manager import GenerationManager, SystemHealth
from .native_nix_api import NativeNixAPI, get_native_api

logger = logging.getLogger(__name__)

# Import plugin system
try:
    from ..plugins.consciousness_router import ConsciousnessRouter
    from ..plugins.harmonic_resolver import HarmonicResolver
    from ..plugins.plugin_context import (
        PluginContext, PluginContextBuilder, PluginCapabilities,
        PluginRequest, PluginRequestType
    )
    from ..plugins.sandbox import PluginSandbox
    PLUGIN_SYSTEM_AVAILABLE = True
except ImportError as e:
    PLUGIN_SYSTEM_AVAILABLE = False
    logger.warning(f"Plugin system not fully available: {e}")


class SystemCapability(Enum):
    """Available system capabilities"""
    ERROR_INTELLIGENCE = "error_intelligence"
    CONFIG_MANAGEMENT = "config_management"
    ADAPTIVE_COMPLEXITY = "adaptive_complexity"
    GENERATION_SAFETY = "generation_safety"
    NATIVE_API = "native_api"
    LEARNING_SYSTEM = "learning_system"
    PLUGIN_ECOSYSTEM = "plugin_ecosystem"


@dataclass
class SystemStatus:
    """Overall system status"""
    capabilities: Dict[SystemCapability, bool]
    health: SystemHealth
    complexity_stage: ComplexityStage
    active_user: str
    configuration: Dict[str, Any]
    performance_mode: str  # 'native' or 'subprocess'


class SystemOrchestrator:
    """
    Unified orchestrator for all integrated systems.
    
    This class provides a single interface to coordinate all subsystems,
    ensuring they work together harmoniously.
    """
    
    def __init__(self):
        """Initialize all subsystems and establish coordination."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize all managers
        self._init_subsystems()
        
        # Establish inter-system connections
        self._connect_systems()
        
        # Load initial state
        self._load_state()
        
        self.logger.info("✨ System Orchestrator initialized with all subsystems")
    
    def _init_subsystems(self):
        """Initialize all subsystem managers."""
        # Core intelligence systems
        # Use AST-enhanced ErrorIntelligence if available
        if AST_COMPONENTS_AVAILABLE:
            try:
                self.error_intelligence = ASTErrorIntelligence()
                self.logger.info("🧠 Using AST-enhanced ErrorIntelligence")
            except Exception as e:
                self.logger.warning(f"Could not initialize AST ErrorIntelligence: {e}")
                self.error_intelligence = ErrorIntelligence()
        else:
            self.error_intelligence = ErrorIntelligence()
        self.config_manager = ConfigManager()
        self.complexity_manager = AdaptiveComplexityManager()
        self.generation_manager = GenerationManager()
        
        # Add AST-enhanced ConfigGenerator if available
        self.config_generator = None
        if AST_COMPONENTS_AVAILABLE:
            try:
                self.config_generator = ASTConfigGenerator()
                self.logger.info("✨ Using AST-enhanced ConfigGenerator")
            except Exception as e:
                self.logger.warning(f"Could not initialize AST ConfigGenerator: {e}")
        
        # Knowledge graph system
        self.knowledge_graph = None
        self.graph_interface = None
        self._init_knowledge_graph()
        
        # Performance systems
        self.native_api = None
        self._init_native_api()
        
        # Plugin ecosystem
        self.consciousness_router = None
        self.harmonic_resolver = None
        self.plugin_sandboxes = {}
        self._init_plugin_system()
        
        # Track available capabilities
        self.capabilities = {
            SystemCapability.ERROR_INTELLIGENCE: True,
            SystemCapability.CONFIG_MANAGEMENT: True,
            SystemCapability.ADAPTIVE_COMPLEXITY: True,
            SystemCapability.GENERATION_SAFETY: True,
            SystemCapability.NATIVE_API: self.native_api is not None,
            SystemCapability.LEARNING_SYSTEM: True,
            SystemCapability.PLUGIN_ECOSYSTEM: self.consciousness_router is not None
        }
    
    def _init_knowledge_graph(self):
        """Initialize Knowledge Graph and GraphInterface if available."""
        try:
            from ..knowledge.nix_knowledge_graph import NixKnowledgeGraph
            from ..knowledge.graph_interface import GraphInterface
            from ..core.nix_ast_parser import get_parser
            
            # Check if tree-sitter is available
            parser = get_parser()
            if parser:
                self.knowledge_graph = NixKnowledgeGraph(parser)
                self.graph_interface = GraphInterface(self.knowledge_graph)
                self.logger.info("🌐 Knowledge Graph initialized with GraphInterface")
            else:
                self.logger.warning("Tree-sitter not available - Knowledge Graph disabled")
        except ImportError as e:
            self.logger.warning(f"Knowledge Graph components not available: {e}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Knowledge Graph: {e}")
    
    def _init_native_api(self):
        """Initialize Native Python-Nix API if available."""
        try:
            if os.getenv('NIX_HUMANITY_PYTHON_BACKEND', 'true').lower() in ('true', '1', 'yes'):
                self.native_api = get_native_api()
                if self.native_api.has_native_api():
                    self.logger.info("🚀 Native Python-Nix API loaded (10x-1500x performance)")
                else:
                    self.native_api = None
                    self.logger.warning("Native API not available, using subprocess mode")
        except Exception as e:
            self.native_api = None
            self.logger.warning(f"Could not initialize Native API: {e}")
    
    def _init_plugin_system(self):
        """Initialize the plugin ecosystem."""
        if not PLUGIN_SYSTEM_AVAILABLE:
            self.logger.warning("Plugin system components not available")
            return
        
        try:
            # Check if plugins are enabled
            if os.getenv('LUMINOUS_NIX_PLUGINS', 'true').lower() not in ('true', '1', 'yes'):
                self.logger.info("Plugin system disabled by environment variable")
                return
            
            # Initialize consciousness router
            self.consciousness_router = ConsciousnessRouter()
            
            # Initialize harmonic resolver
            self.harmonic_resolver = HarmonicResolver()
            
            # Discover and register plugins
            plugins = self.consciousness_router.plugin_loader.discover_plugins()
            
            if plugins:
                self.logger.info(f"🔌 Discovered {len(plugins)} plugin(s)")
                for plugin in plugins:
                    if plugin.is_valid:
                        self.logger.info(f"  ✅ {plugin.name} ({plugin.governing_principle})")
            
            self.logger.info("✨ Plugin ecosystem initialized")
            
        except Exception as e:
            self.consciousness_router = None
            self.harmonic_resolver = None
            self.logger.warning(f"Could not initialize plugin system: {e}")
    
    def _connect_systems(self):
        """Establish connections between subsystems for coordination."""
        # Error Intelligence can use Config for user preferences
        if hasattr(self.error_intelligence, 'set_config'):
            self.error_intelligence.set_config(self.config_manager)
        
        # Complexity Manager can influence Error Intelligence verbosity
        if hasattr(self.complexity_manager, 'register_observer'):
            self.complexity_manager.register_observer(self._on_complexity_change)
    
    def _load_state(self):
        """Load initial state from configuration."""
        # Load user preferences
        config = self.config_manager.config
        
        # Set default user
        self.current_user = 'default'
        
        # Apply preferences to subsystems
        if hasattr(config, 'ui_preferences') and config.ui_preferences:
            self._apply_ui_preferences(config.ui_preferences)
        elif hasattr(config, 'ui'):
            self._apply_ui_preferences(config.ui)
        
        if hasattr(config, 'performance') and config.performance:
            self._apply_performance_settings(config.performance)
    
    def _apply_ui_preferences(self, preferences):
        """Apply UI preferences across all subsystems."""
        # Verbosity affects error messages
        if hasattr(preferences, 'verbosity'):
            verbosity = preferences.verbosity
            # Adjust error intelligence based on verbosity (if method exists)
            if hasattr(self.error_intelligence, 'set_verbosity'):
                if verbosity == 'minimal':
                    self.error_intelligence.set_verbosity('brief')
                elif verbosity == 'verbose':
                    self.error_intelligence.set_verbosity('detailed')
    
    def _apply_performance_settings(self, settings):
        """Apply performance settings across all subsystems."""
        # Cache settings
        if hasattr(settings, 'enable_cache'):
            self.cache_enabled = settings.enable_cache
        
        # Parallel operations
        if hasattr(settings, 'parallel_downloads'):
            self.parallel_downloads = settings.parallel_downloads
    
    def _on_complexity_change(self, user_id: str, new_stage: ComplexityStage):
        """Handle complexity stage changes."""
        self.logger.info(f"User {user_id} progressed to {new_stage.value} stage")
        
        # Adjust subsystems based on new complexity
        if hasattr(self.error_intelligence, 'set_verbosity'):
            if new_stage == ComplexityStage.SANCTUARY:
                # Beginner mode - maximum assistance
                self.error_intelligence.set_verbosity('educational')
                self.config_manager.set('ui.guidance_level', 'high')
            elif new_stage == ComplexityStage.GYMNASIUM:
                # Learning mode - balanced assistance
                self.error_intelligence.set_verbosity('balanced')
                self.config_manager.set('ui.guidance_level', 'medium')
            elif new_stage == ComplexityStage.OPEN_SKY:
                # Expert mode - minimal intrusion
                self.error_intelligence.set_verbosity('minimal')
                self.config_manager.set('ui.guidance_level', 'low')
    
    # === Public Interface Methods ===
    
    def has_capability(self, capability: str) -> bool:
        """Check if a specific capability is available."""
        # Check AST capabilities
        if capability == 'ast_config_generation':
            return self.config_generator is not None
        elif capability == 'ast_error_intelligence':
            return isinstance(self.error_intelligence, ASTErrorIntelligence) if AST_COMPONENTS_AVAILABLE else False
        elif capability == 'graph_interface':
            return hasattr(self, 'graph_interface') and self.graph_interface is not None
        # Check standard capabilities
        elif capability in [cap.value for cap in SystemCapability]:
            return self.capabilities.get(SystemCapability(capability), False)
        return False
    
    def generate_config_ast(self, natural_language: str) -> str:
        """Generate configuration using AST-based generator."""
        if not self.has_capability('ast_config_generation'):
            raise RuntimeError("AST configuration generation not available")
        
        # Use AST config generator
        self.last_intent = self.config_generator.parse_intent(natural_language)
        config_content = self.config_generator.generate_configuration(self.last_intent)
        return config_content
    
    def get_last_intent(self) -> dict:
        """Get the last parsed intent."""
        return getattr(self, 'last_intent', {})
    
    def analyze_error_ast(self, error_message: str, file_path: Optional[str] = None) -> dict:
        """Analyze error using AST-enhanced error intelligence."""
        if not self.has_capability('ast_error_intelligence'):
            # Fallback to regular error intelligence
            return self.error_intelligence.analyze_error(error_message)
        
        # Use AST error intelligence (which is the same object in our case)
        return self.error_intelligence.analyze_error(error_message, file_path)
    
    def get_status(self) -> SystemStatus:
        """Get overall system status."""
        health = self.generation_manager.check_system_health()
        mastery = self.complexity_manager.get_user_mastery(self.current_user)
        
        # Get configuration as dict
        config_dict = {
            'ui': {
                'personality': self.config_manager.get('ui.personality', 'friendly'),
                'verbosity': self.config_manager.get('ui.verbosity', 'normal')
            },
            'performance': {
                'cache': self.config_manager.get('performance.enable_cache', True),
                'native_api': self.native_api is not None
            }
        }
        
        return SystemStatus(
            capabilities=self.capabilities.copy(),
            health=health,
            complexity_stage=mastery.stage,
            active_user=self.current_user,
            configuration=config_dict,
            performance_mode='native' if self.native_api else 'subprocess'
        )
    
    def analyze_error(self, error_message: str) -> Dict[str, Any]:
        """
        Analyze an error with full intelligence.
        
        Combines Error Intelligence with user's complexity level
        to provide appropriate guidance.
        """
        # Get base analysis
        analysis = self.error_intelligence.analyze_error(error_message)
        
        # Adjust based on user complexity
        mastery = self.complexity_manager.get_user_mastery(self.current_user)
        
        if mastery.stage == ComplexityStage.SANCTUARY:
            # Beginner - provide maximum detail
            formatted = self.error_intelligence.format_analysis(analysis)
            return {
                'message': formatted,
                'solutions': analysis.solutions[:2],  # Limit options
                'education': True,
                'auto_fixable': analysis.auto_fixable,
                'fix_command': analysis.fix_command
            }
        elif mastery.stage == ComplexityStage.GYMNASIUM:
            # Learning - provide balanced detail
            return {
                'message': analysis.explanation,
                'solutions': analysis.solutions,
                'education': False,
                'auto_fixable': analysis.auto_fixable,
                'fix_command': analysis.fix_command
            }
        else:  # OPEN_SKY
            # Expert - minimal intrusion
            return {
                'message': analysis.solutions[0] if analysis.solutions else error_message,
                'auto_fixable': analysis.auto_fixable,
                'fix_command': analysis.fix_command
            }
    
    def update_setting(self, key: str, value: Any) -> bool:
        """
        Update a setting across all relevant subsystems.
        
        This ensures all systems stay synchronized.
        """
        # Update in config manager using its set method
        success = self.config_manager.set(key, value)
        
        if success:
            # Parse key to determine what to propagate
            parts = key.split('.')
            if len(parts) == 2:
                section, setting = parts
                
                if section == 'ui':
                    # Propagate UI settings
                    if setting == 'verbosity':
                        self._apply_verbosity(value)
                    elif setting == 'personality':
                        self._apply_personality(value)
                        
                elif section == 'performance':
                    # Propagate performance settings
                    if setting == 'use_native_api':
                        self._toggle_native_api(value)
            
            # Save configuration
            if hasattr(self.config_manager, 'save'):
                self.config_manager.save()
            
            self.logger.info(f"Updated setting {key} = {value}")
        
        return success
    
    def _apply_verbosity(self, level: str):
        """Apply verbosity setting across systems."""
        if hasattr(self.error_intelligence, 'set_verbosity'):
            if level == 'minimal':
                self.error_intelligence.set_verbosity('brief')
            elif level == 'verbose':
                self.error_intelligence.set_verbosity('detailed')
            else:
                self.error_intelligence.set_verbosity('balanced')
    
    def _apply_personality(self, personality: str):
        """Apply personality setting across systems."""
        # This could affect response generation
        self.config_manager.set('ui.personality', personality)
    
    def _toggle_native_api(self, enabled: bool):
        """Toggle Native API on/off."""
        if enabled and not self.native_api:
            self._init_native_api()
        elif not enabled and self.native_api:
            self.native_api = None
            self.capabilities[SystemCapability.NATIVE_API] = False
    
    def track_interaction(self, success: bool, command_type: str = None):
        """
        Track a user interaction for learning.
        
        Updates complexity tracking and adjusts systems accordingly.
        """
        # Update mastery tracking
        self.complexity_manager.update_mastery(
            user_id=self.current_user,
            command_success=success,
            complexity_handled=command_type
        )
        
        # Check for stage progression
        mastery = self.complexity_manager.get_user_mastery(self.current_user)
        
        # Log significant milestones
        if mastery.successful_commands % 10 == 0:
            self.logger.info(
                f"Milestone: User {self.current_user} completed "
                f"{mastery.successful_commands} successful commands"
            )
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        health = self.generation_manager.check_system_health()
        
        return {
            'overall_health': health.is_healthy,
            'disk_usage': health.disk_usage_percent,
            'memory_usage': health.memory_usage_percent,
            'failed_services': health.failed_services,
            'config_errors': health.config_errors,
            'warnings': health.warnings,
            'subsystems': {
                'error_intelligence': self.capabilities[SystemCapability.ERROR_INTELLIGENCE],
                'config_management': self.capabilities[SystemCapability.CONFIG_MANAGEMENT],
                'adaptive_complexity': self.capabilities[SystemCapability.ADAPTIVE_COMPLEXITY],
                'generation_safety': self.capabilities[SystemCapability.GENERATION_SAFETY],
                'native_api': self.capabilities[SystemCapability.NATIVE_API],
                'learning_system': self.capabilities[SystemCapability.LEARNING_SYSTEM]
            }
        }
    
    def get_user_context(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get complete context for a user.
        
        Combines mastery, preferences, and system state.
        """
        if user_id is None:
            user_id = self.current_user
        
        mastery = self.complexity_manager.get_user_mastery(user_id)
        
        # Get user preferences using config manager's get method
        preferences = {
            'personality': self.config_manager.get('ui.personality', 'friendly'),
            'verbosity': self.config_manager.get('ui.verbosity', 'normal'),
            'guidance_level': self.config_manager.get('ui.guidance_level', 'medium')
        }
        
        return {
            'user_id': user_id,
            'complexity_stage': mastery.stage.value,
            'confidence': mastery.confidence_score,
            'successful_commands': mastery.successful_commands,
            'error_rate': mastery.error_rate,
            'preferences': preferences,
            'system_mode': 'native' if self.native_api else 'subprocess'
        }
    
    def suggest_next_action(self, context: str = None) -> List[str]:
        """
        Suggest next actions based on user's stage and context.
        
        Provides intelligent suggestions that match user's skill level.
        """
        mastery = self.complexity_manager.get_user_mastery(self.current_user)
        suggestions = []
        
        if mastery.stage == ComplexityStage.SANCTUARY:
            # Beginner suggestions
            suggestions = [
                "Try: install firefox - to learn package installation",
                "Try: search text editor - to explore available packages",
                "Try: help - to see all available commands"
            ]
        elif mastery.stage == ComplexityStage.GYMNASIUM:
            # Intermediate suggestions
            suggestions = [
                "Explore: list generations - to see system history",
                "Learn: show config - to understand your system",
                "Practice: create dev environment - for development"
            ]
        else:  # OPEN_SKY
            # Advanced suggestions
            suggestions = [
                "Optimize: garbage collect - to clean old packages",
                "Configure: edit configuration.nix - for permanent changes",
                "Advanced: create custom flake - for reproducible configs"
            ]
        
        # Add context-specific suggestions
        if context:
            if 'error' in context.lower():
                suggestions.insert(0, "Debug: Check system health")
            elif 'slow' in context.lower():
                suggestions.insert(0, "Performance: Enable native API")
        
        return suggestions[:3]
    
    def perform_safety_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive safety check.
        
        Ensures all systems are functioning correctly.
        """
        issues = []
        warnings = []
        
        # Check system health
        health = self.generation_manager.check_system_health()
        if not health.is_healthy:
            issues.append("System health check failed")
            issues.extend(health.config_errors)
        
        # Check disk space
        if health.disk_usage_percent > 90:
            issues.append(f"Critical: Disk usage at {health.disk_usage_percent}%")
        elif health.disk_usage_percent > 80:
            warnings.append(f"Warning: Disk usage at {health.disk_usage_percent}%")
        
        # Check failed services
        if health.failed_services:
            issues.append(f"Failed services: {', '.join(health.failed_services)}")
        
        # Check configuration
        if hasattr(self.config_manager, 'validate_config'):
            if not self.config_manager.validate_config():
                warnings.append("Configuration validation failed")
        
        # Check Native API
        if not self.native_api and os.getenv('NIX_HUMANITY_PYTHON_BACKEND', 'true').lower() == 'true':
            warnings.append("Native API not available - performance degraded")
        
        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'recommendations': self._get_safety_recommendations(issues, warnings)
        }
    
    def _get_safety_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate safety recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            if 'disk usage' in issue.lower():
                recommendations.append("Run: garbage collect - to free disk space")
            elif 'failed services' in issue.lower():
                recommendations.append("Check: service status - to diagnose failures")
            elif 'health check' in issue.lower():
                recommendations.append("Consider: rollback generation - to restore stability")
        
        for warning in warnings:
            if 'native api' in warning.lower():
                recommendations.append("Enable: Native API - for better performance")
            elif 'configuration' in warning.lower():
                recommendations.append("Review: configuration settings")
        
        return recommendations
    
    def generate_config_with_ast(self, intent: str, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate configuration using AST-based understanding.
        
        Uses the consciousness-aware ConfigGenerator to create grammatically perfect configs.
        """
        if not self.config_generator:
            return {
                'success': False,
                'error': 'AST ConfigGenerator not available',
                'fallback': 'Use standard configuration generation'
            }
        
        try:
            # Load existing configuration if path provided
            if config_path:
                self.config_generator.load_configuration(config_path)
            
            # Analyze the intent with semantic understanding
            parsed_intent = self.config_generator.analyze_intent(intent)
            
            # Generate configuration changes
            changes = self.config_generator.generate_changes(parsed_intent)
            
            # Apply changes to create new configuration
            new_config = self.config_generator.apply_changes(changes)
            
            return {
                'success': True,
                'intent': parsed_intent.__dict__,
                'changes': [change.__dict__ for change in changes],
                'config': new_config,
                'consciousness_note': '✨ Generated with grammatical understanding and semantic awareness'
            }
            
        except Exception as e:
            self.logger.error(f"AST config generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback': 'Use standard configuration generation'
            }
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get complete system diagnostics.
        
        Useful for debugging and support.
        """
        diagnostics = {
            'status': self.get_status().__dict__,
            'health': self.get_system_health(),
            'user_context': self.get_user_context(),
            'safety_check': self.perform_safety_check(),
            'capabilities': {
                cap.value: enabled 
                for cap, enabled in self.capabilities.items()
            },
            'performance': {
                'native_api': self.native_api is not None,
                'cache_enabled': getattr(self, 'cache_enabled', False),
                'parallel_downloads': getattr(self, 'parallel_downloads', 4)
            }
        }
        
        # Add plugin system diagnostics if available
        if self.consciousness_router:
            diagnostics['plugins'] = {
                'enabled': True,
                'discovered': len(self.consciousness_router.plugins),
                'active_sandboxes': len(self.plugin_sandboxes)
            }
        
        return diagnostics
    
    # === Plugin System Methods ===
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Process a user query, routing to core or plugins as appropriate.
        
        Args:
            query: User's natural language query
            context: Optional context information
            
        Returns:
            Tuple of (response_text, metadata)
        """
        if not self.consciousness_router:
            # No plugin system, process normally
            return self._process_core_query(query, context)
        
        # Route the query
        route = self.consciousness_router.route(query)
        
        # Check if a plugin should handle this
        if route.handler_type == 'plugin' and route.confidence > 0.65:
            return self._process_plugin_query(query, route, context)
        else:
            return self._process_core_query(query, context)
    
    def _process_plugin_query(self, query: str, route: Any, context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Process a query through a plugin.
        
        Args:
            query: User query
            route: Routing decision from ConsciousnessRouter
            context: Optional context
            
        Returns:
            Tuple of (response, metadata)
        """
        plugin_info = route.plugin_info
        
        # Check for harmony/conflicts
        harmony_path = self.harmonic_resolver.resolve_dissonance(
            plugin_info.name,
            query,
            self.get_system_health()
        )
        
        if harmony_path.path_type.value == 'consent':
            # Need user consent
            return (
                f"🔐 Plugin '{plugin_info.name}' needs permission: {harmony_path.description}",
                {'needs_consent': True, 'plugin_id': route.handler_id}
            )
        elif harmony_path.path_type.value == 'blocked':
            # Plugin blocked due to conflict
            return (
                f"⚠️ Cannot use plugin: {harmony_path.description}",
                {'blocked': True, 'reason': harmony_path.description}
            )
        
        # Create plugin context
        plugin_context = self._create_plugin_context(plugin_info)
        
        # Create or get sandbox
        if route.handler_id not in self.plugin_sandboxes:
            self.plugin_sandboxes[route.handler_id] = PluginSandbox(
                plugin_info.path,
                max_memory_mb=512,
                max_cpu_percent=50,
                timeout_seconds=30
            )
        
        sandbox = self.plugin_sandboxes[route.handler_id]
        
        try:
            # Execute plugin (use intent_pattern as handler name)
            handler_name = getattr(route, 'handler_function', route.intent_pattern)
            result = sandbox.execute(
                handler_name=handler_name,
                query=query,
                context=plugin_context
            )
            
            # Process plugin requests
            self._process_plugin_requests(plugin_context)
            
            # Track interaction
            self.track_interaction(
                success=result.get('success', False),
                command_type=f"plugin:{plugin_info.name}"
            )
            
            return (
                result.get('response', 'Plugin executed successfully'),
                {
                    'plugin_id': route.handler_id,
                    'plugin_name': plugin_info.name,
                    'execution_time': plugin_context.get_elapsed_time()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Plugin execution failed: {e}")
            return (
                f"Plugin error: {str(e)}",
                {'error': str(e), 'plugin_id': route.handler_id}
            )
    
    def _process_core_query(self, query: str, context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Process a query through core system (fallback).
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Tuple of (response, metadata)
        """
        # This would normally call the core engine
        # For now, return a placeholder
        return (
            f"Processing through core: {query}",
            {'handler': 'core', 'context': context}
        )
    
    def _create_plugin_context(self, plugin_info) -> Any:  # PluginContext when available
        """
        Create a PluginContext for a plugin execution.
        
        Args:
            plugin_info: Plugin information
            
        Returns:
            Configured PluginContext
        """
        if not PLUGIN_SYSTEM_AVAILABLE:
            return None
            
        builder = PluginContextBuilder()
        
        # Get current state
        mastery = self.complexity_manager.get_user_mastery(self.current_user)
        health = self.generation_manager.check_system_health()
        
        # Build context
        context = (
            builder
            .with_plugin_info(
                plugin_info.id,
                plugin_info.name,
                plugin_info.version
            )
            .with_user_context(
                self.current_user,
                mastery.stage,
                self._get_user_preferences()
            )
            .with_system_state(
                health,
                'native' if self.native_api else 'subprocess',
                self._get_nixos_version()
            )
            .with_capabilities(
                self._get_plugin_capabilities(plugin_info)
            )
            .with_knowledge_graph(
                self.graph_interface if self.graph_interface else None
            )
            .build()
        )
        
        return context
    
    def _get_user_preferences(self) -> Dict[str, Any]:
        """Get current user preferences."""
        return {
            'personality': self.config_manager.get('ui.personality', 'friendly'),
            'verbosity': self.config_manager.get('ui.verbosity', 'normal'),
            'guidance_level': self.config_manager.get('ui.guidance_level', 'medium')
        }
    
    def _get_nixos_version(self) -> str:
        """Get NixOS version."""
        try:
            import subprocess
            result = subprocess.run(['nixos-version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "Unknown"
    
    def _get_plugin_capabilities(self, plugin_info) -> Any:  # PluginCapabilities when available
        """
        Determine plugin capabilities based on manifest and user consent.
        
        Args:
            plugin_info: Plugin information
            
        Returns:
            PluginCapabilities object
        """
        # Start with default safe capabilities
        if not PLUGIN_SYSTEM_AVAILABLE:
            return None
        
        caps = PluginCapabilities(
            can_execute_commands=False,
            can_show_notifications=True,
            can_access_settings=True,
            can_modify_settings=False,
            can_access_knowledge_graph=False
        )
        
        # Enhance based on plugin manifest permissions
        if hasattr(plugin_info, 'manifest_data'):
            perms = plugin_info.manifest_data.get('permissions', {})
            caps.can_execute_commands = perms.get('execute_commands', False)
            caps.can_modify_settings = perms.get('modify_settings', False)
            caps.can_access_knowledge_graph = perms.get('access_knowledge', False)
            
            # Set allowed commands if specified
            if perms.get('allowed_commands'):
                caps.allowed_commands = perms['allowed_commands']
        
        return caps
    
    def _process_plugin_requests(self, context: Any):  # PluginContext when available
        """
        Process requests from a plugin's request queue.
        
        Args:
            context: Plugin context with request queue
        """
        while not context.request_queue.empty():
            try:
                request = context.request_queue.get_nowait()
                self._handle_plugin_request(request, context)
            except Empty:
                break
    
    def _handle_plugin_request(self, request: Any, context: Any):  # PluginRequest, PluginContext when available
        """
        Handle a single plugin request.
        
        Args:
            request: The plugin request
            context: Plugin context
        """
        if not PLUGIN_SYSTEM_AVAILABLE:
            return
            
        if request.request_type == PluginRequestType.SHOW_NOTIFICATION:
            # Log the notification
            self.logger.info(
                f"Plugin {context.plugin_name} notification: {request.data['message']}"
            )
            
        elif request.request_type == PluginRequestType.LOG_MESSAGE:
            # Log the message
            level = request.data.get('level', 'info')
            message = f"[{context.plugin_name}] {request.data['message']}"
            getattr(self.logger, level, self.logger.info)(message)
            
        elif request.request_type == PluginRequestType.UPDATE_STATUS:
            # Update status (could be displayed in UI)
            self.logger.debug(
                f"Plugin {context.plugin_name} status: {request.data['status']}"
            )
            
        elif request.request_type == PluginRequestType.EXECUTE_COMMAND:
            # Would need proper sandboxed execution
            self.logger.warning(
                f"Plugin {context.plugin_name} wants to execute: {request.data['command']}"
            )
            # TODO: Implement safe command execution
            
        # Call callback if provided
        if request.callback:
            request.callback(request)


# Singleton instance
_orchestrator = None


def get_orchestrator() -> SystemOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator


def reset_orchestrator():
    """Reset the orchestrator (mainly for testing)."""
    global _orchestrator
    _orchestrator = None