"""
Plugin Architecture for Extending Luminous Nix

Allows third-party extensions to add new commands, intents, and behaviors
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import sys

@dataclass
class PluginMetadata:
    """Metadata about a plugin"""
    name: str
    version: str
    author: str
    description: str
    commands: List[str] = field(default_factory=list)
    intents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class PluginCommand:
    """A command provided by a plugin"""
    name: str
    handler: Callable
    description: str
    usage: str
    aliases: List[str] = field(default_factory=list)
    requires_sudo: bool = False
    category: str = "custom"

class Plugin(ABC):
    """
    Base class for all plugins
    
    Plugins must inherit from this class and implement required methods
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize plugin with optional configuration"""
        self.config = config or {}
        self.commands: Dict[str, PluginCommand] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    def register_command(self, command: PluginCommand):
        """Register a command provided by this plugin"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command
    
    def register_hook(self, event: str, handler: Callable):
        """Register a hook for an event"""
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(handler)
    
    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """Execute a command provided by this plugin"""
        if command_name in self.commands:
            return self.commands[command_name].handler(*args, **kwargs)
        raise ValueError(f"Command '{command_name}' not found in plugin")
    
    def cleanup(self):
        """Cleanup when plugin is unloaded"""
        pass

class PluginManager:
    """
    Manages loading, initialization, and execution of plugins
    
    Features:
    - Dynamic plugin loading
    - Dependency resolution
    - Hook system for events
    - Command registration
    - Configuration management
    """
    
    def __init__(self, plugin_dir: Optional[Path] = None):
        """Initialize plugin manager"""
        self.plugin_dir = plugin_dir or (Path.home() / ".config/luminous-nix/plugins")
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
        self.plugins: Dict[str, Plugin] = {}
        self.commands: Dict[str, Tuple[str, PluginCommand]] = {}  # command -> (plugin_name, command)
        self.hooks: Dict[str, List[Tuple[str, Callable]]] = {}  # event -> [(plugin_name, handler)]
        self.metadata: Dict[str, PluginMetadata] = {}
        
        # Core events that plugins can hook into
        self.core_events = [
            'pre_command',      # Before any command execution
            'post_command',     # After command execution
            'pre_install',      # Before package installation
            'post_install',     # After package installation
            'pre_search',       # Before search
            'post_search',      # After search
            'error_occurred',   # When an error occurs
            'startup',          # When the system starts
            'shutdown',         # When the system shuts down
            'intent_recognized', # When intent is recognized
            'entity_extracted', # When entities are extracted
        ]
        
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugin directory
        
        Returns:
            List of plugin names discovered
        """
        discovered = []
        
        # Look for Python files in plugin directory
        for file_path in self.plugin_dir.glob("*.py"):
            if file_path.stem != "__init__":
                discovered.append(file_path.stem)
        
        # Look for plugin packages (directories with __init__.py)
        for dir_path in self.plugin_dir.iterdir():
            if dir_path.is_dir():
                init_file = dir_path / "__init__.py"
                if init_file.exists():
                    discovered.append(dir_path.name)
        
        # Look for .nix-plugin files (JSON manifests)
        for manifest_path in self.plugin_dir.glob("*.nix-plugin"):
            with open(manifest_path) as f:
                manifest = json.load(f)
                if 'name' in manifest:
                    discovered.append(manifest['name'])
        
        return discovered
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Load a plugin by name
        
        Args:
            plugin_name: Name of the plugin to load
            config: Optional configuration for the plugin
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if plugin_name in self.plugins:
            print(f"Plugin '{plugin_name}' already loaded")
            return True
        
        try:
            # Try to import the plugin module
            plugin_module = self._import_plugin(plugin_name)
            
            if not plugin_module:
                return False
            
            # Find the Plugin class in the module
            plugin_class = self._find_plugin_class(plugin_module)
            
            if not plugin_class:
                print(f"No Plugin class found in '{plugin_name}'")
                return False
            
            # Instantiate the plugin
            plugin_instance = plugin_class(config)
            
            # Get metadata
            metadata = plugin_instance.get_metadata()
            
            # Check dependencies
            if not self._check_dependencies(metadata.dependencies):
                print(f"Dependencies not met for plugin '{plugin_name}'")
                return False
            
            # Initialize the plugin
            if not plugin_instance.initialize():
                print(f"Failed to initialize plugin '{plugin_name}'")
                return False
            
            # Register the plugin
            self.plugins[plugin_name] = plugin_instance
            self.metadata[plugin_name] = metadata
            
            # Register commands
            for command_name, command in plugin_instance.commands.items():
                self.commands[command_name] = (plugin_name, command)
            
            # Register hooks
            for event, handlers in plugin_instance.hooks.items():
                if event not in self.hooks:
                    self.hooks[event] = []
                for handler in handlers:
                    self.hooks[event].append((plugin_name, handler))
            
            # Trigger startup hook
            self.trigger_hook('startup', plugin_name=plugin_name)
            
            print(f"✅ Plugin '{plugin_name}' loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load plugin '{plugin_name}': {e}")
            return False
    
    def _import_plugin(self, plugin_name: str):
        """Import a plugin module"""
        # Try as a file
        plugin_file = self.plugin_dir / f"{plugin_name}.py"
        if plugin_file.exists():
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)
                return module
        
        # Try as a package
        plugin_package = self.plugin_dir / plugin_name
        if plugin_package.is_dir():
            init_file = plugin_package / "__init__.py"
            if init_file.exists():
                spec = importlib.util.spec_from_file_location(plugin_name, init_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = module
                    spec.loader.exec_module(module)
                    return module
        
        # Try to import from Python path
        try:
            return importlib.import_module(plugin_name)
        except ImportError:
            pass
        
        return None
    
    def _find_plugin_class(self, module) -> Optional[Type[Plugin]]:
        """Find the Plugin class in a module"""
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Plugin) and obj != Plugin:
                return obj
        return None
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if all dependencies are satisfied"""
        for dep in dependencies:
            # Check if it's a loaded plugin
            if dep.startswith("plugin:"):
                plugin_dep = dep[7:]
                if plugin_dep not in self.plugins:
                    return False
            # Check if it's a Python package
            elif dep.startswith("python:"):
                package = dep[7:]
                try:
                    importlib.import_module(package)
                except ImportError:
                    return False
            # Check if it's a system command
            elif dep.startswith("command:"):
                command = dep[8:]
                import shutil
                if not shutil.which(command):
                    return False
        return True
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            print(f"Plugin '{plugin_name}' not loaded")
            return False
        
        try:
            # Trigger shutdown hook
            self.trigger_hook('shutdown', plugin_name=plugin_name)
            
            # Cleanup the plugin
            self.plugins[plugin_name].cleanup()
            
            # Remove commands
            commands_to_remove = [cmd for cmd, (pname, _) in self.commands.items() if pname == plugin_name]
            for cmd in commands_to_remove:
                del self.commands[cmd]
            
            # Remove hooks
            for event in self.hooks:
                self.hooks[event] = [(pname, handler) for pname, handler in self.hooks[event] if pname != plugin_name]
            
            # Remove from registry
            del self.plugins[plugin_name]
            del self.metadata[plugin_name]
            
            print(f"✅ Plugin '{plugin_name}' unloaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to unload plugin '{plugin_name}': {e}")
            return False
    
    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """
        Execute a command from a plugin
        
        Args:
            command_name: Name of the command to execute
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command
            
        Returns:
            Result of the command execution
        """
        if command_name not in self.commands:
            raise ValueError(f"Command '{command_name}' not found")
        
        plugin_name, command = self.commands[command_name]
        plugin = self.plugins[plugin_name]
        
        # Trigger pre-command hook
        self.trigger_hook('pre_command', command=command_name, args=args, kwargs=kwargs)
        
        try:
            # Execute the command
            result = plugin.execute_command(command.name, *args, **kwargs)
            
            # Trigger post-command hook
            self.trigger_hook('post_command', command=command_name, result=result)
            
            return result
            
        except Exception as e:
            # Trigger error hook
            self.trigger_hook('error_occurred', command=command_name, error=e)
            raise
    
    def trigger_hook(self, event: str, **kwargs):
        """
        Trigger a hook event
        
        Args:
            event: Name of the event
            **kwargs: Data to pass to hook handlers
        """
        if event in self.hooks:
            for plugin_name, handler in self.hooks[event]:
                try:
                    handler(**kwargs)
                except Exception as e:
                    print(f"Error in hook '{event}' from plugin '{plugin_name}': {e}")
    
    def get_all_commands(self) -> Dict[str, PluginCommand]:
        """Get all commands from all loaded plugins"""
        return {name: cmd for name, (_, cmd) in self.commands.items()}
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get information about a plugin"""
        return self.metadata.get(plugin_name)
    
    def list_plugins(self) -> List[PluginMetadata]:
        """List all loaded plugins"""
        return list(self.metadata.values())
    
    def save_config(self):
        """Save plugin configuration to disk"""
        config_file = self.plugin_dir / "config.json"
        config = {
            'enabled_plugins': list(self.plugins.keys()),
            'plugin_configs': {
                name: plugin.config 
                for name, plugin in self.plugins.items()
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        """Load plugin configuration from disk"""
        config_file = self.plugin_dir / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                
            # Load enabled plugins
            for plugin_name in config.get('enabled_plugins', []):
                plugin_config = config.get('plugin_configs', {}).get(plugin_name, {})
                self.load_plugin(plugin_name, plugin_config)


# Example plugin implementation
class ExamplePlugin(Plugin):
    """Example plugin showing how to create a plugin"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example",
            version="1.0.0",
            author="Luminous Nix",
            description="Example plugin demonstrating the plugin system",
            commands=["hello", "example-command"],
            intents=["greet"],
            dependencies=[]
        )
    
    def initialize(self) -> bool:
        """Initialize the example plugin"""
        # Register commands
        self.register_command(PluginCommand(
            name="hello",
            handler=self._hello_command,
            description="Say hello",
            usage="hello [name]",
            aliases=["hi", "greet"]
        ))
        
        self.register_command(PluginCommand(
            name="example-command",
            handler=self._example_command,
            description="Example command",
            usage="example-command <arg>"
        ))
        
        # Register hooks
        self.register_hook('pre_install', self._pre_install_hook)
        self.register_hook('post_command', self._post_command_hook)
        
        return True
    
    def _hello_command(self, name: str = "World") -> str:
        """Handler for hello command"""
        return f"Hello, {name}! This is from the example plugin."
    
    def _example_command(self, arg: str) -> str:
        """Handler for example command"""
        return f"Example command executed with argument: {arg}"
    
    def _pre_install_hook(self, package: str, **kwargs):
        """Hook that runs before package installation"""
        print(f"[Example Plugin] About to install: {package}")
    
    def _post_command_hook(self, command: str, result: Any, **kwargs):
        """Hook that runs after any command"""
        print(f"[Example Plugin] Command '{command}' completed")