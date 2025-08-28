"""
Unified System Architecture for Luminous Nix

This is the CORE that connects all modes and features into one coherent system.
All modes (Grandma, Maya, Standard) share common infrastructure.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

# Import all our modes
from .grandma_mode import GrandmaMode
from .maya_mode import MayaMode
from .luminous_core import LuminousNixCore
from .native_nix_api import NativeNixAPI
from .sacred_utils import ConsciousnessField, SacredTimer


class UserMode(Enum):
    """All available user modes"""
    GRANDMA = "grandma"      # Non-technical, safety-first
    MAYA = "maya"            # ADHD, lightning-fast
    STANDARD = "standard"    # Natural language
    DEVELOPER = "developer"  # Technical, verbose
    VOICE = "voice"          # Voice-first (future)
    CHILD = "child"          # Simplified, educational
    RESEARCH = "research"    # Dr. Sarah mode
    ACCESSIBILITY = "accessibility"  # Screen reader optimized


@dataclass
class SystemConfig:
    """Unified configuration for all modes"""
    # Core settings
    mode: UserMode = UserMode.STANDARD
    dry_run: bool = False
    use_native_api: bool = True
    
    # Performance settings
    enable_cache: bool = True
    cache_dir: Path = field(default_factory=lambda: Path.home() / '.cache' / 'luminous-nix')
    parallel_operations: bool = True
    timeout_seconds: int = 30
    
    # Consciousness settings
    enable_sacred_pauses: bool = True
    mindful_operations: bool = True
    flow_protection: bool = True
    
    # Accessibility settings
    high_contrast: bool = False
    large_text: bool = False
    screen_reader: bool = False
    voice_feedback: bool = False
    
    # Safety settings
    require_confirmation: bool = True
    auto_rollback: bool = True
    safe_mode: bool = False
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'SystemConfig':
        """Load config from JSON/YAML file"""
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def save_to_file(self, path: Path):
        """Save config to file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=str)


@dataclass
class SharedState:
    """Shared state between all modes"""
    # User session
    current_user: str = "default"
    current_mode: UserMode = UserMode.STANDARD
    session_start: float = field(default_factory=time.time)
    
    # Operation history
    history: List[Dict[str, Any]] = field(default_factory=list)
    last_operation: Optional[Dict[str, Any]] = None
    operation_count: int = 0
    
    # Package cache
    installed_packages: List[str] = field(default_factory=list)
    available_packages: Dict[str, Any] = field(default_factory=dict)
    package_cache_time: float = 0
    
    # Consciousness metrics
    flow_interruptions: int = 0
    errors_encountered: int = 0
    successful_operations: int = 0
    consciousness_level: float = 1.0
    
    # Learning data
    common_operations: Dict[str, int] = field(default_factory=dict)
    user_patterns: List[str] = field(default_factory=list)
    preferred_packages: List[str] = field(default_factory=list)


class PackageCache:
    """Unified package cache shared by all modes"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = {}
        self.cache_lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get from cache (memory first, then disk)"""
        # Check memory cache
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                # Refresh memory cache
                self.memory_cache[key] = data
                return data
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set in cache (both memory and disk)"""
        with self.cache_lock:
            # Memory cache
            self.memory_cache[key] = {
                'data': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
            
            # Disk cache
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, 'w') as f:
                json.dump(self.memory_cache[key], f)
    
    def is_fresh(self, key: str) -> bool:
        """Check if cache entry is still fresh"""
        entry = self.get(key)
        if not entry:
            return False
        
        elapsed = time.time() - entry.get('timestamp', 0)
        ttl = entry.get('ttl', 3600)
        return elapsed < ttl


class ModeRouter:
    """Routes operations to appropriate mode based on context"""
    
    def __init__(self, config: SystemConfig, state: SharedState):
        self.config = config
        self.state = state
        
        # Initialize all modes with shared components
        self.modes = {
            UserMode.GRANDMA: GrandmaMode(),
            UserMode.MAYA: MayaMode(),
            UserMode.STANDARD: LuminousNixCore(),
        }
        
    def detect_best_mode(self, input_text: str) -> UserMode:
        """Auto-detect best mode based on input pattern"""
        # Quick commands suggest Maya mode
        if len(input_text.split()) <= 2 and not ' ' in input_text.strip():
            return UserMode.MAYA
        
        # Questions suggest Grandma mode
        if any(word in input_text.lower() for word in ['what', 'how', 'help', 'please']):
            return UserMode.GRANDMA
        
        # Technical terms suggest developer mode
        if any(word in input_text.lower() for word in ['flake', 'derivation', 'overlay']):
            return UserMode.DEVELOPER
        
        # Default to configured mode
        return self.config.mode
    
    def route(self, operation: str, **kwargs) -> Any:
        """Route operation to appropriate mode"""
        mode = self.state.current_mode
        
        if mode not in self.modes:
            mode = UserMode.STANDARD
        
        handler = self.modes[mode]
        
        # Call appropriate method
        if hasattr(handler, operation):
            method = getattr(handler, operation)
            return method(**kwargs)
        else:
            # Fallback to standard mode
            return self.modes[UserMode.STANDARD].process_query(operation)


class UnifiedLuminousNix:
    """
    The MAIN system that unifies all Luminous Nix components.
    
    This is what gets instantiated and used by all interfaces (CLI, TUI, API).
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        # Load configuration
        if config_path is None:
            config_path = Path.home() / '.config' / 'luminous-nix' / 'config.json'
        self.config = SystemConfig.load_from_file(config_path)
        
        # Initialize shared state
        self.state = SharedState()
        
        # Initialize shared components
        self.cache = PackageCache(self.config.cache_dir)
        self.native_api = NativeNixAPI() if self.config.use_native_api else None
        self.consciousness = ConsciousnessField() if self.config.mindful_operations else None
        self.router = ModeRouter(self.config, self.state)
        
        # Background tasks
        self.task_queue = queue.Queue()
        self.start_background_tasks()
        
    def start_background_tasks(self):
        """Start background tasks for cache refresh, learning, etc."""
        def worker():
            while True:
                try:
                    task = self.task_queue.get(timeout=1)
                    task()
                except queue.Empty:
                    # Periodic tasks
                    self.refresh_cache_if_needed()
                    self.update_consciousness_field()
                
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def refresh_cache_if_needed(self):
        """Refresh package cache if stale"""
        if not self.cache.is_fresh('installed_packages'):
            # Refresh in background
            self.task_queue.put(self._refresh_installed_packages)
        
        if not self.cache.is_fresh('available_packages'):
            self.task_queue.put(self._refresh_available_packages)
    
    def _refresh_installed_packages(self):
        """Background task to refresh installed packages"""
        if self.native_api:
            packages = self.native_api.list_installed()
            self.cache.set('installed_packages', packages)
            self.state.installed_packages = packages
    
    def _refresh_available_packages(self):
        """Background task to refresh available packages"""
        # This would be expensive, so we do it rarely
        pass  # TODO: Implement smart caching
    
    def update_consciousness_field(self):
        """Update consciousness metrics"""
        if self.consciousness:
            self.consciousness.update({
                'operations': self.state.operation_count,
                'errors': self.state.errors_encountered,
                'flow': 1.0 - (self.state.flow_interruptions / max(1, self.state.operation_count)),
                'coherence': self.state.successful_operations / max(1, self.state.operation_count)
            })
            self.state.consciousness_level = self.consciousness.coherence
    
    def set_mode(self, mode: Union[UserMode, str]):
        """Switch to a different user mode"""
        if isinstance(mode, str):
            mode = UserMode(mode)
        
        self.state.current_mode = mode
        self.config.mode = mode
        
        # Adjust settings based on mode
        if mode == UserMode.GRANDMA:
            self.config.require_confirmation = True
            self.config.safe_mode = True
            self.config.large_text = True
        elif mode == UserMode.MAYA:
            self.config.require_confirmation = False
            self.config.parallel_operations = True
            self.config.enable_sacred_pauses = False
        elif mode == UserMode.ACCESSIBILITY:
            self.config.screen_reader = True
            self.config.high_contrast = True
            self.config.voice_feedback = True
    
    def process(self, input_text: str) -> Dict[str, Any]:
        """
        Main entry point for all operations.
        Routes to appropriate mode and returns unified response.
        """
        # Track operation
        self.state.operation_count += 1
        start_time = time.time()
        
        # Auto-detect mode if configured
        if self.config.mode == UserMode.STANDARD:
            detected_mode = self.router.detect_best_mode(input_text)
            if detected_mode != self.state.current_mode:
                self.set_mode(detected_mode)
        
        try:
            # Process through appropriate mode
            result = self.router.route('process', input=input_text)
            
            # Track success
            self.state.successful_operations += 1
            
            # Update history
            operation = {
                'input': input_text,
                'mode': self.state.current_mode.value,
                'result': result,
                'timestamp': time.time(),
                'duration': time.time() - start_time
            }
            self.state.history.append(operation)
            self.state.last_operation = operation
            
            # Learn from operation
            self.learn_from_operation(operation)
            
            return {
                'success': True,
                'result': result,
                'mode': self.state.current_mode.value,
                'duration': operation['duration']
            }
            
        except Exception as e:
            # Track error
            self.state.errors_encountered += 1
            
            return {
                'success': False,
                'error': str(e),
                'mode': self.state.current_mode.value,
                'suggestion': self.get_error_suggestion(str(e))
            }
    
    def learn_from_operation(self, operation: Dict[str, Any]):
        """Learn from user operations to improve over time"""
        # Track common operations
        input_text = operation['input']
        if input_text in self.state.common_operations:
            self.state.common_operations[input_text] += 1
        else:
            self.state.common_operations[input_text] = 1
        
        # Track patterns
        words = input_text.lower().split()
        if 'install' in words:
            for word in words:
                if word not in ['install', 'the', 'a', 'an']:
                    if word not in self.state.preferred_packages:
                        self.state.preferred_packages.append(word)
    
    def get_error_suggestion(self, error: str) -> str:
        """Get helpful suggestion based on error"""
        if "not found" in error.lower():
            return "Try searching first with 'search <name>'"
        elif "permission" in error.lower():
            return "This operation needs sudo. Try running with admin rights."
        elif "network" in error.lower():
            return "Check your internet connection"
        else:
            return "Try a simpler command or type 'help'"
    
    def get_suggestions(self) -> List[str]:
        """Get suggestions based on user history"""
        suggestions = []
        
        # Suggest common operations
        for op, count in sorted(self.state.common_operations.items(), 
                                key=lambda x: x[1], reverse=True)[:3]:
            suggestions.append(op)
        
        # Suggest preferred packages not installed
        for pkg in self.state.preferred_packages:
            if pkg not in self.state.installed_packages:
                suggestions.append(f"install {pkg}")
        
        return suggestions
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'mode': self.state.current_mode.value,
            'user': self.state.current_user,
            'session_duration': time.time() - self.state.session_start,
            'operations': self.state.operation_count,
            'success_rate': self.state.successful_operations / max(1, self.state.operation_count),
            'consciousness_level': self.state.consciousness_level,
            'cache_size': len(self.cache.memory_cache),
            'config': {
                'dry_run': self.config.dry_run,
                'native_api': self.config.use_native_api,
                'sacred_pauses': self.config.enable_sacred_pauses
            }
        }
    
    def shutdown(self):
        """Graceful shutdown"""
        # Save state
        state_file = self.config.cache_dir / 'state.json'
        with open(state_file, 'w') as f:
            json.dump({
                'history': self.state.history[-100:],  # Keep last 100
                'common_operations': dict(self.state.common_operations),
                'preferred_packages': self.state.preferred_packages
            }, f)
        
        # Save config
        self.config.save_to_file(
            Path.home() / '.config' / 'luminous-nix' / 'config.json'
        )


# Singleton instance for easy access
_instance: Optional[UnifiedLuminousNix] = None

def get_instance() -> UnifiedLuminousNix:
    """Get or create the singleton instance"""
    global _instance
    if _instance is None:
        _instance = UnifiedLuminousNix()
    return _instance


def main():
    """Example usage"""
    # Get the unified system
    nix = get_instance()
    
    # Process different types of input
    print("Standard mode:")
    print(nix.process("install firefox"))
    
    print("\nAuto-detected Maya mode (short command):")
    print(nix.process("i ff"))
    
    print("\nAuto-detected Grandma mode (question):")
    print(nix.process("what is installed?"))
    
    print("\nSystem status:")
    print(nix.get_status())
    
    print("\nSuggestions based on usage:")
    print(nix.get_suggestions())
    
    # Cleanup
    nix.shutdown()


if __name__ == "__main__":
    main()