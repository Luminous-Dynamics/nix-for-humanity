"""
Plugin Context - Sacred Vessel for Plugin-Core Communication

This module provides a safe, controlled interface for plugins to interact
with the core system through the SystemOrchestrator.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, TYPE_CHECKING
from queue import Queue
from enum import Enum
from datetime import datetime

from ..learning.adaptation import ComplexityStage
from ..core.generation_manager import SystemHealth

# Import GraphInterface if available
if TYPE_CHECKING:
    from ..knowledge.graph_interface import GraphInterface


class PluginRequestType(Enum):
    """Types of requests plugins can make"""
    EXECUTE_COMMAND = "execute_command"
    SHOW_NOTIFICATION = "show_notification"
    UPDATE_STATUS = "update_status"
    REQUEST_INPUT = "request_input"
    LOG_MESSAGE = "log_message"
    QUERY_KNOWLEDGE = "query_knowledge"


@dataclass
class PluginRequest:
    """A request from a plugin to the core system"""
    request_type: PluginRequestType
    data: Dict[str, Any]
    callback: Optional[Callable] = None
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher = more urgent


@dataclass
class PluginCapabilities:
    """What a plugin is allowed to do"""
    can_execute_commands: bool = False
    can_show_notifications: bool = True
    can_access_settings: bool = True
    can_modify_settings: bool = False
    can_access_knowledge_graph: bool = False
    max_requests_per_minute: int = 60
    allowed_commands: List[str] = field(default_factory=list)


@dataclass
class PluginContext:
    """
    Sacred vessel for plugin-core communication.
    
    Provides safe, controlled access to system state and functionality.
    Plugins receive this context when executed by the SystemOrchestrator.
    """
    
    # Plugin identity
    plugin_id: str
    plugin_name: str
    plugin_version: str
    
    # User context (read-only)
    user_id: str
    user_mastery: ComplexityStage
    user_preferences: Dict[str, Any]
    
    # System state (read-only)
    system_health: SystemHealth
    system_mode: str  # 'native' or 'subprocess'
    nixos_version: str
    
    # Plugin capabilities
    capabilities: PluginCapabilities
    
    # Communication channel
    request_queue: Queue[PluginRequest] = field(default_factory=Queue)
    
    # Knowledge graph access (if permitted)
    knowledge_graph: Optional['GraphInterface'] = None  # Safe, read-only graph access
    
    # Execution metadata
    execution_id: str = field(default_factory=lambda: datetime.now().isoformat())
    start_time: datetime = field(default_factory=datetime.now)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting (read-only).
        
        Args:
            key: Setting key (e.g., 'ui.verbosity')
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        if not self.capabilities.can_access_settings:
            raise PermissionError(f"Plugin {self.plugin_name} cannot access settings")
        
        # Settings are in user_preferences
        parts = key.split('.')
        current = self.user_preferences
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def request_command_execution(self, command: str, description: str = "") -> bool:
        """
        Request execution of a system command.
        
        Args:
            command: Command to execute
            description: Human-readable description
            
        Returns:
            True if request was queued
        """
        if not self.capabilities.can_execute_commands:
            raise PermissionError(f"Plugin {self.plugin_name} cannot execute commands")
        
        if self.capabilities.allowed_commands:
            # Check if command is in allowed list
            cmd_base = command.split()[0]
            if cmd_base not in self.capabilities.allowed_commands:
                raise PermissionError(f"Command {cmd_base} not in allowed list")
        
        request = PluginRequest(
            request_type=PluginRequestType.EXECUTE_COMMAND,
            data={
                'command': command,
                'description': description,
                'plugin_id': self.plugin_id
            },
            priority=5
        )
        
        self.request_queue.put(request)
        return True
    
    def query_knowledge_graph(self, query_type: str, **params) -> Optional[Dict[str, Any]]:
        """
        Query the knowledge graph for configuration information.
        
        Args:
            query_type: Type of query (e.g., 'find_packages', 'get_dependencies')
            **params: Query parameters
            
        Returns:
            Query result or None if not available
            
        Raises:
            PermissionError: If plugin doesn't have graph access
        """
        if not self.capabilities.can_access_knowledge_graph:
            raise PermissionError(f"Plugin {self.plugin_name} cannot access knowledge graph")
        
        if not self.knowledge_graph:
            return None
        
        # Import QueryType dynamically to avoid circular imports
        from ..knowledge.graph_interface import QueryType
        
        try:
            # Convert string query_type to enum
            qt = QueryType[query_type.upper()]
            result = self.knowledge_graph.query(qt, **params)
            
            if result.success:
                return {
                    'success': True,
                    'data': result.data,
                    'query_time_ms': result.query_time_ms
                }
            else:
                return {
                    'success': False,
                    'error': result.error,
                    'query_time_ms': result.query_time_ms
                }
        except (KeyError, ValueError) as e:
            return {
                'success': False,
                'error': f"Invalid query type: {query_type}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def show_notification(self, message: str, level: str = "info") -> bool:
        """
        Request to show a notification to the user.
        
        Args:
            message: Notification message
            level: Notification level ('info', 'warning', 'error', 'success')
            
        Returns:
            True if request was queued
        """
        if not self.capabilities.can_show_notifications:
            raise PermissionError(f"Plugin {self.plugin_name} cannot show notifications")
        
        request = PluginRequest(
            request_type=PluginRequestType.SHOW_NOTIFICATION,
            data={
                'message': message,
                'level': level,
                'plugin_id': self.plugin_id
            },
            priority=3
        )
        
        self.request_queue.put(request)
        return True
    
    def update_status(self, status: str, progress: Optional[float] = None) -> bool:
        """
        Update plugin execution status.
        
        Args:
            status: Status message
            progress: Optional progress (0.0 to 1.0)
            
        Returns:
            True if request was queued
        """
        request = PluginRequest(
            request_type=PluginRequestType.UPDATE_STATUS,
            data={
                'status': status,
                'progress': progress,
                'plugin_id': self.plugin_id
            },
            priority=1
        )
        
        self.request_queue.put(request)
        return True
    
    def log(self, message: str, level: str = "info") -> bool:
        """
        Log a message to the system log.
        
        Args:
            message: Log message
            level: Log level ('debug', 'info', 'warning', 'error')
            
        Returns:
            True if request was queued
        """
        request = PluginRequest(
            request_type=PluginRequestType.LOG_MESSAGE,
            data={
                'message': message,
                'level': level,
                'plugin_id': self.plugin_id
            },
            priority=0
        )
        
        self.request_queue.put(request)
        return True
    
        
    def get_elapsed_time(self) -> float:
        """Get elapsed execution time in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def is_complexity_appropriate(self) -> bool:
        """
        Check if plugin complexity matches user's mastery level.
        
        Returns:
            True if plugin is appropriate for user's current stage
        """
        # Simple heuristic - can be enhanced
        if self.user_mastery == ComplexityStage.SANCTUARY:
            # Beginners should use simpler plugins
            return 'advanced' not in self.plugin_name.lower()
        elif self.user_mastery == ComplexityStage.OPEN_SKY:
            # Experts can use any plugin
            return True
        else:
            # Gymnasium users - middle ground
            return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            'plugin_id': self.plugin_id,
            'plugin_name': self.plugin_name,
            'plugin_version': self.plugin_version,
            'user_id': self.user_id,
            'user_mastery': self.user_mastery.value,
            'system_mode': self.system_mode,
            'execution_id': self.execution_id,
            'elapsed_time': self.get_elapsed_time()
        }


class PluginContextBuilder:
    """
    Builder for creating PluginContext objects.
    
    Used by SystemOrchestrator to construct appropriate contexts for plugins.
    """
    
    def __init__(self):
        self._reset()
    
    def _reset(self):
        """Reset builder state."""
        self._context = None
        
    def with_plugin_info(self, plugin_id: str, name: str, version: str):
        """Set plugin information."""
        self._plugin_id = plugin_id
        self._plugin_name = name
        self._plugin_version = version
        return self
    
    def with_user_context(self, user_id: str, mastery: ComplexityStage, preferences: Dict):
        """Set user context."""
        self._user_id = user_id
        self._mastery = mastery
        self._preferences = preferences
        return self
    
    def with_system_state(self, health: SystemHealth, mode: str, nixos_version: str):
        """Set system state."""
        self._health = health
        self._mode = mode
        self._nixos_version = nixos_version
        return self
    
    def with_capabilities(self, capabilities: PluginCapabilities):
        """Set plugin capabilities."""
        self._capabilities = capabilities
        return self
    
    def with_knowledge_graph(self, graph):
        """Set knowledge graph interface (future)."""
        self._graph = graph
        return self
    
    def build(self) -> PluginContext:
        """Build the PluginContext."""
        context = PluginContext(
            plugin_id=self._plugin_id,
            plugin_name=self._plugin_name,
            plugin_version=self._plugin_version,
            user_id=self._user_id,
            user_mastery=self._mastery,
            user_preferences=self._preferences,
            system_health=self._health,
            system_mode=self._mode,
            nixos_version=self._nixos_version,
            capabilities=self._capabilities,
            knowledge_graph=getattr(self, '_graph', None)
        )
        
        self._reset()
        return context