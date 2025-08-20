"""Command-line interface adapter."""

# === Merged from migration ===


"""
from typing import Optional
Nix for Humanity - THE Unified Command
Natural language interface for NixOS with symbiotic learning capabilities

This is the consolidated version that replaces all ask-nix-* variants.
Features integrated from ask-nix-modern, ask-nix-hybrid, and ask-nix-v3.
Now with plugin architecture for extensibility!
"""

import sys
import subprocess
import time
import threading
from pathlib import Path
import os
import json
import shutil
import tempfile
import importlib.util
import uuid
from typing import Dict, Optional, Tuple
from datetime import datetime

# Add scripts directory to path
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, script_dir)

# Add src directory to path for security module
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, src_dir)

# Import security module
try:
    from luminous_nix.security import InputValidator, SecurityLevel, ValidationError
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    if os.environ.get('NIX_HUMANITY_DEBUG', '').lower() == 'true':
        print("Debug: Security module not available. Running without enhanced security.")

# Import new v1.0 improvements
try:
    from luminous_nix.core.first_run_wizard import FirstRunWizard, run_if_needed
    from luminous_nix.core.graceful_degradation import degradation_handler, DegradationLevel
    from luminous_nix.security.security_audit import security_auditor, audit_user_input, audit_command_execution
    V1_IMPROVEMENTS_AVAILABLE = True
except ImportError:
    V1_IMPROVEMENTS_AVAILABLE = False
    if os.environ.get('NIX_HUMANITY_DEBUG', '').lower() == 'true':
        print("Debug: v1.0 improvements not available. Running without enhanced features.")

# Import our knowledge engines and systems
# Legacy imports commented out - using new backend instead
# from nix_knowledge_engine import NixOSKnowledgeEngine
# spec = importlib.util.spec_from_file_location("nix_knowledge_engine_modern", 
#     os.path.join(script_dir, "nix-knowledge-engine-modern.py"))
# nix_knowledge_engine_modern = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(nix_knowledge_engine_modern)
# ModernNixOSKnowledgeEngine = nix_knowledge_engine_modern.ModernNixOSKnowledgeEngine

# Import plugin system
try:
    # Add scripts directory to path for plugin imports
    import sys
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    
    from core.plugin_manager import get_plugin_manager
    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False
    # Plugin system is optional - only show warning in debug mode
    if os.environ.get('NIX_HUMANITY_DEBUG', '').lower() == 'true':
        print("Debug: Plugin system not available. Running without plugins.")

# Import learning and cache systems
try:
    # Use importlib to handle hyphenated filenames (already imported above)
    
    # Import command learning system
    spec = importlib.util.spec_from_file_location("command_learning_system", 
        os.path.join(script_dir, "command-learning-system.py"))
    command_learning_system = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(command_learning_system)
    CommandLearningSystem = command_learning_system.CommandLearningSystem
    
    # Import package cache manager
    spec = importlib.util.spec_from_file_location("package_cache_manager", 
        os.path.join(script_dir, "package-cache-manager.py"))
    package_cache_manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package_cache_manager)
    IntelligentPackageCache = package_cache_manager.IntelligentPackageCache
    
    # Import feedback collector for symbiotic learning
    from feedback_collector import FeedbackCollector
except Exception as e:
    # Fallback: Create dummy implementations if modules are missing
    # Advanced features are optional - only show warning in debug mode
    if os.environ.get('NIX_HUMANITY_DEBUG', '').lower() == 'true':
        print(f"Debug: Could not load advanced features: {e}")
    class CommandLearningSystem:
        def __init__(self):
            pass
        def learn_from_outcome(self, *args, **kwargs):
            pass
        def get_success_rate(self, *args, **kwargs):
            return 0.0
    
    class IntelligentPackageCache:
        def __init__(self):
            pass
        def get_cached_search(self, *args, **kwargs):
            return None
        def cache_search_results(self, *args, **kwargs):
            pass
        def search_with_fallback(self, *args, **kwargs):
            return [], False
        def get_cache_stats(self, *args, **kwargs):
            return {'total_packages': 0, 'cache_age': 'N/A'}
    
    class FeedbackCollector:
        def __init__(self):
            pass
        def collect_implicit_feedback(self, *args, **kwargs):
            return {}
        def collect_explicit_feedback(self, *args, **kwargs):
            return {}
        def get_feedback_stats(self, *args, **kwargs):
            return {'total_feedback': 0, 'helpful_percentage': 0, 'preference_pairs': 0}

# Try to import Rich for better visuals (graceful fallback)
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None
    rprint = print

class ProgressSpinner:
    """Simple progress spinner for long operations"""
    def __init__(self, message="Processing", estimated_time=None):
        self.message = message
        self.estimated_time = estimated_time
        self.running = False
        self.thread = None
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current = 0
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        
    def _spin(self):
        while self.running:
            time_info = f" (Est: {self.estimated_time})" if self.estimated_time else ""
            sys.stdout.write(f'\r{self.spinner_chars[self.current]} {self.message}{time_info}')
            sys.stdout.flush()
            self.current = (self.current + 1) % len(self.spinner_chars)
            time.sleep(0.1)
            
    def stop(self, final_message=None):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
        if final_message:
            print(final_message)
        sys.stdout.flush()

class UnifiedNixAssistant:
    def __init__(self):
        # Check and handle v1.0 improvements
        if V1_IMPROVEMENTS_AVAILABLE:
            # Check degradation level
            self.degradation_level = degradation_handler.determine_level()
            if self.degradation_level != DegradationLevel.FULL:
                strategy = degradation_handler.get_strategy()
                if strategy.fallback_message:
                    print(f"\n⚠️  {strategy.fallback_message}")
                    
        # Initialize both knowledge engines
        # self.basic_knowledge = NixOSKnowledgeEngine()  # Legacy - not needed with new backend
        # self.modern_knowledge = ModernNixOSKnowledgeEngine()  # Legacy - not needed with new backend
        
        # Initialize intelligent systems
        self.learning_system = CommandLearningSystem()
        self.cache_manager = IntelligentPackageCache()
        self.feedback_collector = FeedbackCollector()  # For symbiotic learning
        
        # Initialize plugin system if available
        self.plugin_manager = None
        if PLUGINS_AVAILABLE:
            try:
                self.plugin_manager = get_plugin_manager()
                self.plugin_manager.load_all_plugins()
            except Exception as e:
                print(f"Warning: Failed to initialize plugin system: {e}")
                self.plugin_manager = None
        
        # Assistant configuration
        self.personality = 'friendly'  # Can be: minimal, friendly, encouraging, technical, symbiotic
        self.show_progress = True
        self.dry_run = False  # Execute by default (Phase 1: Make It Real)
        self.show_intent = False
        self.retry_count = 3  # For reliability
        self.use_cache = True  # Use intelligent caching by default
        self.visual_mode = RICH_AVAILABLE  # Use rich visuals if available
        self.collect_feedback = True  # Enable feedback collection by default
        
        # Session tracking for feedback
        self.session_id = str(uuid.uuid4())[:8]
        self.interaction_start_time = None
        
        # Learning configuration
        self.learning_enabled = self.check_learning_enabled()
        self.current_command_id = None
        
    def check_learning_enabled(self):
        """Check if learning is enabled in config"""
        config_file = Path.home() / ".config" / "nix-humanity" / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('learning_enabled', False)
        return False
    
    def _simple_intent_recognition(self, query: str) -> dict:
        """Simple fallback intent recognition when backend not available"""
        query_lower = query.lower()
        
        # Simple pattern matching
        if any(word in query_lower for word in ['install', 'add', 'get']):
            # Extract package name after the keyword
            for word in ['install', 'add', 'get']:
                if word in query_lower:
                    parts = query_lower.split(word, 1)
                    if len(parts) > 1:
                        package = parts[1].strip().split()[0] if parts[1].strip() else ''
                        return {'action': 'install_package', 'package': package, 'entities': {'package': package}}
            return {'action': 'install_package', 'package': '', 'entities': {'package': ''}}
        
        elif any(word in query_lower for word in ['remove', 'uninstall', 'delete']):
            for word in ['remove', 'uninstall', 'delete']:
                if word in query_lower:
                    parts = query_lower.split(word, 1)
                    if len(parts) > 1:
                        package = parts[1].strip().split()[0] if parts[1].strip() else ''
                        return {'action': 'remove_package', 'package': package, 'entities': {'package': package}}
            return {'action': 'remove_package', 'package': '', 'entities': {'package': ''}}
        
        elif any(word in query_lower for word in ['search', 'find', 'look for']):
            query_text = query_lower.replace('search', '').replace('find', '').replace('look for', '').strip()
            return {'action': 'search_packages', 'query': query_text, 'entities': {'query': query_text}}
        
        elif 'update' in query_lower:
            return {'action': 'update_system', 'entities': {}}
        
        elif 'help' in query_lower or '?' in query_lower:
            return {'action': 'help', 'entities': {}}
        
        elif 'list' in query_lower or 'show' in query_lower:
            if 'generation' in query_lower:
                return {'action': 'list_generations', 'entities': {}}
            else:
                return {'action': 'list_packages', 'entities': {}}
        
        # Default to search
        return {'action': 'search_packages', 'query': query, 'entities': {'query': query}}
    
    def _get_progress_message(self, operation: str) -> dict:
        """Get progress message for an operation"""
        messages = {
            'install': {'message': '📦 Installing package...', 'estimated_time': 30},
            'remove': {'message': '🗑️ Removing package...', 'estimated_time': 20},
            'search': {'message': '🔍 Searching packages...', 'estimated_time': 5},
            'update': {'message': '🔄 Updating system...', 'estimated_time': 120},
            'command': {'message': '⚡ Executing command...', 'estimated_time': 10}
        }
        return messages.get(operation, {'message': '⏳ Processing...', 'estimated_time': 10})
    
    def _get_solution(self, intent: dict) -> dict:
        """Get solution for an intent"""
        action = intent.get('action', 'unknown')
        entities = intent.get('entities', {})
        
        solutions = {
            'install_package': {
                'command': f"nix-env -iA nixos.{entities.get('package', 'package')}",
                'description': f"Install {entities.get('package', 'the package')}"
            },
            'remove_package': {
                'command': f"nix-env -e {entities.get('package', 'package')}",
                'description': f"Remove {entities.get('package', 'the package')}"
            },
            'search_packages': {
                'command': f"nix search nixpkgs {entities.get('query', '')}",
                'description': f"Search for packages matching '{entities.get('query', 'your query')}'"
            },
            'update_system': {
                'command': "sudo nixos-rebuild switch",
                'description': "Update your NixOS system"
            },
            'list_packages': {
                'command': "nix-env -q",
                'description': "List installed packages"
            },
            'list_generations': {
                'command': "nix-env --list-generations",
                'description': "List system generations"
            },
            'help': {
                'command': None,
                'description': "Show help information"
            }
        }
        
        return solutions.get(action, {
            'command': None,
            'description': "I don't understand that command yet"
        })
    
    def _format_response(self, intent: dict, solution: dict) -> str:
        """Format response for user"""
        if solution.get('command'):
            return f"{solution['description']}\nCommand: {solution['command']}"
        else:
            return solution.get('description', "I don't understand that request")
    
    def try_general_python_backend(self, query: str) -> bool:
        """Try to use Python backend for any query"""
        # Check feature flag
        if not os.getenv('NIX_HUMANITY_PYTHON_BACKEND', '').lower() in ('true', '1', 'yes'):
            if os.getenv('DEBUG'):
                print("Backend disabled by feature flag")
            return False
        
        try:
            # Check if new backend is available
            backend_path = Path(__file__).parent.parent / "backend"
            if not backend_path.exists():
                return False
            
            # Add parent directory to Python path so we can import luminous_nix.core as backend
            parent_path = backend_path.parent
            if str(parent_path) not in sys.path:
                sys.path.insert(0, str(parent_path))
            
            # Import the unified backend
            from luminous_nix.core.engine import NixForHumanityBackend
            from luminous_nix.api.schema import Request, Context
            
            backend_instance = NixForHumanityBackend()
            
            # Build request
            context = Context(
                personality=self.personality,
                execute=not self.dry_run,
                dry_run=self.dry_run,
                frontend='cli',
                session_id=self.session_id,
                user_preferences={
                    'collect_feedback': self.collect_feedback,
                    'use_cache': True,
                    'learning_mode': False
                }
            )
            request = Request(query=query, context=context)
            
            # Execute via Python backend
            response = backend_instance.process(request)
            
            # Display result
            print(response.text)
            
            # Show commands if available
            if response.commands and not self.dry_run:
                print("\n📦 Commands executed:")
                for cmd in response.commands:
                    status = "✅" if cmd.get('success', True) else "❌"
                    print(f"  {status} {cmd['description']}")
                    if os.getenv('DEBUG') and 'command' in cmd:
                        print(f"     Command: {cmd['command']}")
            
            # Return success status
            return response.success
            
        except Exception as e:
            if os.getenv('DEBUG'):
                import traceback
                traceback.print_exc()
            # Fall back to traditional method
            return False
    
    def try_python_backend(self, action: str, package: str = None) -> bool:
        """Try to use Python backend for NixOS operations"""
        # Check feature flag
        if not os.getenv('NIX_HUMANITY_PYTHON_BACKEND', '').lower() in ('true', '1', 'yes'):
            return False
        try:
            # Check if new backend is available
            backend_path = Path(__file__).parent.parent / "backend"
            if not backend_path.exists():
                # Try old location for backward compatibility
                backend_path = Path(__file__).parent.parent / "scripts" / "backend"
                if not backend_path.exists():
                    return False
            
            # Add backend to Python path
            if str(backend_path) not in sys.path:
                sys.path.insert(0, str(backend_path))
            
            # Import the unified backend
            try:
                from luminous_nix.core import NixForHumanityBackend, Request
                backend = NixForHumanityBackend()
                if os.getenv('DEBUG'):
                    print("✨ Using native backend with 10x-1500x performance")
            except ImportError:
                # Fallback to old backend
                try:
                    from luminous_nix.core.engine import UnifiedNixBackend, IntentType
                    return self._use_old_backend(action, package)
                except ImportError as e:
                    if os.getenv('DEBUG'):
                        print(f"Failed to import luminous_nix.core as backend: {e}")
                    return False
            
            # Build query based on action
            if action == "install" and package:
                query = f"install {package}"
            elif action == "update":
                query = "update my system"
            elif action == "search" and package:
                query = f"search {package}"
            elif action == "remove" and package:
                query = f"remove {package}"
            else:
                return False
            
            # Build request
            request = Request(
                query=query,
                context={
                    'personality': self.personality,
                    'execute': not self.dry_run,
                    'dry_run': self.dry_run,
                    'frontend': 'cli',
                    'collect_feedback': self.collect_feedback,
                    'session_id': self.session_id,
                    'use_cache': True,
                    'learning_mode': False
                },
                frontend='cli'
            )
            
            # Execute via Python backend
            print("\n🐍 Using Python backend for improved performance...")
            response = backend.process(request)
            
            # Display result
            print(response.text)
            
            # Show commands if available
            if response.commands and not self.dry_run:
                print("\n📦 Commands executed:")
                for cmd in response.commands:
                    status = "✅" if cmd.get('success', True) else "❌"
                    print(f"  {status} {cmd['description']}")
                    if os.getenv('DEBUG') and 'command' in cmd:
                        print(f"     Command: {cmd['command']}")
            
            # Return success status
            return response.success
            
        except Exception as e:
            if os.getenv('DEBUG'):
                import traceback
                traceback.print_exc()
            # Fall back to traditional method
            return False
    
    def _use_old_backend(self, action: str, package: str = None) -> bool:
        """Use old backend for backward compatibility"""
        from luminous_nix.core.engine import UnifiedNixBackend, IntentType
        
        # Create backend instance with progress callback
        def progress_callback(message: str, progress: float = None):
            if progress is not None:
                print(f"\r{message} [{int(progress*100)}%]", end='', flush=True)
            else:
                print(f"\n{message}")
        
        backend = UnifiedNixBackend(progress_callback=progress_callback)
        
        # Build query based on action
        if action == "install" and package:
            query = f"install {package}"
        elif action == "update":
            query = "update my system"
        elif action == "search" and package:
            query = f"search {package}"
        elif action == "remove" and package:
            query = f"remove {package}"
        else:
            return False
        
        # Extract intent from query
        intent = backend.extract_intent(query)
        
        # Prepare context
        context = {
            'personality': self.personality,
            'dry_run': self.dry_run,
            'frontend': 'cli',
            'collect_feedback': self.collect_feedback,
            'session_id': self.session_id
        }
        
        # Execute via Python backend
        print("\n🐍 Using Python backend for improved performance...")
        response = backend.process_intent(intent, context)
        
        # Display result
        print(response.text)
        
        # Show commands if available
        if response.commands:
            print("\n📦 Commands executed:")
            for cmd in response.commands:
                print(f"  • {cmd['description']}: {cmd['command']}")
        
        # Return success status
        return response.success
        
    def enhance_response(self, response: str, query: str, personality: str) -> str:
        """Add personality to the factual response"""
        
        # Check if plugin manager can handle personality transformation
        if self.plugin_manager:
            context = {
                'query': query,
                'personality': personality,
                'session_id': self.session_id
            }
            transformed = self.plugin_manager.apply_personality(response, context)
            if transformed != response:  # Plugin handled it
                return transformed
        
        # Fallback to built-in personalities
        if personality == 'minimal':
            # Just return the facts
            return response
            
        elif personality == 'friendly':
            # Add warm greeting and closing
            enhanced = f"Hi there! {response}\n\nLet me know if you need any clarification! 😊"
            return enhanced
            
        elif personality == 'encouraging':
            # Add encouragement
            enhanced = f"Great question! {response}\n\nYou're doing awesome learning NixOS! Keep it up! 🌟"
            
            # Add extra tips for beginners
            if 'without sudo' in query.lower():
                enhanced += "\n\n💡 Pro tip: You're already thinking like a NixOS pro by avoiding sudo!"
            return enhanced
            
        elif personality == 'technical':
            # Add technical depth
            enhanced = f"{response}\n\nNote: This follows NixOS's declarative configuration paradigm."
            
            # Add technical details
            if 'nix profile' in response:
                enhanced += "\n\nTechnical note: nix profile uses the new Nix 2.0 CLI with improved UX."
            return enhanced
            
        elif personality == 'symbiotic':
            # New personality that admits uncertainty and invites partnership
            enhanced = f"{response}\n\n🤝 I'm still learning! Was this helpful? Your feedback helps me improve."
            return enhanced
            
        return response
    
    def execute_with_bridge(self, intent: Dict, operation: str = "command") -> tuple:
        """Execute command using the execution bridge for safer operation"""
        import json
        
        # Get progress info for this operation
        progress_info = self._get_progress_message(operation)
        
        # Prepare intent for bridge
        intent_json = json.dumps(intent)
        bridge_path = os.path.join(os.path.dirname(__file__), 'execution-bridge.js')
        
        # Start progress spinner
        spinner = ProgressSpinner(progress_info['message'], progress_info['estimated_time'])
        if self.show_progress:
            spinner.start()
        
        try:
            # Execute via bridge
            result = subprocess.run(
                ['node', bridge_path, intent_json],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if self.show_progress:
                spinner.stop()
            
            # Parse bridge response
            if result.stdout:
                try:
                    response = json.loads(result.stdout)
                    
                    # Check for educational error information
                    if not response.get('success', False) and response.get('suggestions'):
                        # Format educational error message
                        error_msg = f"\n❌ {response.get('error', 'Operation failed')}\n"
                        
                        if response.get('suggestions'):
                            error_msg += "\n💡 Suggestions:\n"
                            for suggestion in response['suggestions']:
                                error_msg += f"   • {suggestion}\n"
                        
                        if response.get('learnMore'):
                            error_msg += f"\n📚 Learn more: {response['learnMore']}\n"
                        
                        return False, response.get('output', ''), error_msg
                    
                    return response.get('success', False), response.get('output', ''), response.get('error', '')
                except json.JSONDecodeError:
                    return False, '', f"Invalid bridge response: {result.stdout}"
            else:
                return False, '', result.stderr or "Bridge execution failed"
                
        except subprocess.TimeoutExpired:
            if self.show_progress:
                spinner.stop()
            return False, '', "Command timed out. This might be normal for large operations."
        except Exception as e:
            if self.show_progress:
                spinner.stop()
            return False, '', str(e)
    
    def execute_with_progress(self, command: str, operation: str = "command") -> tuple:
        """Execute command with progress indicator and retry logic"""
        # Get progress info for this operation
        progress_info = self._get_progress_message(operation)
        
        # Start progress spinner
        spinner = ProgressSpinner(progress_info['message'], progress_info['estimated_time'])
        if self.show_progress:
            spinner.start()
        
        success = False
        output = ""
        error = ""
        
        for attempt in range(self.retry_count):
            try:
                # Convert string command to list for safety
                if isinstance(command, str):
                    import shlex
                    command_list = shlex.split(command)
                else:
                    command_list = command
                
                # Enhanced security audit if available
                if V1_IMPROVEMENTS_AVAILABLE:
                    audit_result = audit_command_execution(command_list)
                    if not audit_result.passed:
                        if self.show_progress:
                            spinner.stop()
                        error_msg = "🛡️ Security audit failed:\n"
                        for violation in audit_result.violations:
                            error_msg += f"  • {violation.description}\n"
                        return False, "", error_msg
                
                # Validate command before execution
                if SECURITY_AVAILABLE:
                    validator = InputValidator(SecurityLevel.BALANCED)
                    try:
                        # Validate each argument in the command list
                        validated_args = validator.validate_command_args(command_list)
                        # Reconstruct command list from validated args
                        command_list = [arg.sanitized for arg in validated_args]
                    except ValidationError as e:
                        if self.show_progress:
                            spinner.stop()
                        return False, "", f"Security validation failed: {e.message}"
                    
                # Execute command
                result = subprocess.run(
                    command_list,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    success = True
                    output = result.stdout
                    break
                else:
                    error = result.stderr
                    if attempt < self.retry_count - 1:
                        time.sleep(2)  # Wait before retry
                        
            except subprocess.TimeoutExpired:
                error = "Command timed out. This might be normal for large operations."
                if attempt < self.retry_count - 1:
                    spinner.message = f"{progress_info['message']} (Retry {attempt + 1})"
            except Exception as e:
                # Handle with graceful degradation if available
                if V1_IMPROVEMENTS_AVAILABLE:
                    from luminous_nix.core.graceful_degradation import handle_degraded_operation
                    try:
                        nix_error = degradation_handler.handle_resource_error(e, operation)
                        error = f"{nix_error.user_message}\n"
                        if nix_error.suggestions:
                            error += "\n💡 Suggestions:\n"
                            for suggestion in nix_error.suggestions:
                                error += f"  • {suggestion}\n"
                    except Exception:
                        error = str(e)
                else:
                    error = str(e)
                break
        
        # Stop spinner
        if self.show_progress:
            if success:
                spinner.stop(f"✅ {operation.capitalize()} completed successfully!")
            else:
                spinner.stop(f"❌ {operation.capitalize()} failed")
        
        return success, output, error
    
    def check_home_manager_installed(self) -> bool:
        """Check if Home Manager is installed"""
        try:
            result = subprocess.run(
                ["home-manager", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def execute_search(self, query: str, package: Optional[str] = None):
        """Execute package search with intelligent caching"""
        search_term = package or query.replace('search', '').strip()
        
        # Try Python backend first
        if self.try_python_backend("search", search_term):
            return
            
        if RICH_AVAILABLE and self.visual_mode:
            console.print(f"\n🔍 [bold blue]Searching for '{search_term}'...[/bold blue]")
        else:
            print(f"\n🔍 Searching for '{search_term}'...")
        
        # Try cache first if enabled
        if self.use_cache:
            cached_results = self.cache_manager.get_cached_search(search_term)
            if cached_results:
                if RICH_AVAILABLE and self.visual_mode:
                    console.print("[dim]Using cached results (instant!)[/dim]")
                else:
                    print("Using cached results (instant!)")
                
                # Format and display results
                self._display_search_results(cached_results, search_term)
                return
        
        # Show progress for actual search
        if self.show_progress:
            if RICH_AVAILABLE and self.visual_mode:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                    console=console
                ) as progress:
                    task = progress.add_task("Searching nixpkgs...", total=None)
                    
                    # Perform actual search
                    results = self._perform_search(search_term)
                    
                    progress.update(task, completed=True)
            else:
                spinner = ProgressSpinner("Searching nixpkgs", "10-30 seconds")
                spinner.start()
                results = self._perform_search(search_term)
                spinner.stop()
        else:
            results = self._perform_search(search_term)
        
        # Cache the results if caching is enabled
        if self.use_cache and results:
            self.cache_manager.cache_search_results(search_term, results)
        
        # Display results
        self._display_search_results(results, search_term)
    
    def _perform_search(self, search_term: str) -> Dict:
        """Perform actual package search"""
        # Validate and sanitize search term
        if SECURITY_AVAILABLE:
            validator = InputValidator(SecurityLevel.BALANCED)
            try:
                validated = validator.validate(search_term, context="search")
                safe_search_term = validated.sanitized
                
                # Warn user if input was modified
                if validated.modifications:
                    print(f"Note: Search term sanitized for security.")
                    if validated.warnings:
                        for warning in validated.warnings:
                            print(f"  ⚠️  {warning}")
            except ValidationError as e:
                print(f"❌ Security validation failed: {e.message}")
                if e.suggested_fix:
                    print(f"💡 Suggestion: {e.suggested_fix}")
                return {}
        else:
            # Basic fallback sanitization
            safe_search_term = search_term.replace(';', '').replace('|', '').replace('&', '')
        
        try:
            result = subprocess.run(
                ["nix", "search", "nixpkgs", safe_search_term, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            else:
                return {}
        except subprocess.TimeoutExpired:
            if RICH_AVAILABLE and self.visual_mode:
                console.print("[yellow]Search timed out. Try a more specific search term.[/yellow]")
            else:
                print("Search timed out. Try a more specific search term.")
            return {}
        except Exception as e:
            if RICH_AVAILABLE and self.visual_mode:
                console.print(f"[red]Search error: {str(e)}[/red]")
            else:
                print(f"Search error: {str(e)}")
            return {}
    
    def _display_search_results(self, results: Dict, search_term: str):
        """Display search results with rich formatting if available"""
        if not results:
            if RICH_AVAILABLE and self.visual_mode:
                console.print(f"\n[yellow]No packages found matching '{search_term}'[/yellow]")
                console.print("\n💡 [dim]Try a different search term or check spelling[/dim]")
            else:
                print(f"\nNo packages found matching '{search_term}'")
                print("\n💡 Try a different search term or check spelling")
            return
        
        # Sort results by relevance (exact matches first)
        sorted_results = sorted(
            results.items(),
            key=lambda x: (
                search_term.lower() not in x[0].split('.')[-1].lower(),
                x[0]
            )
        )[:10]  # Show top 10 results
        
        if RICH_AVAILABLE and self.visual_mode:
            # Create a nice table
            table = Table(title=f"Search Results for '{search_term}'")
            table.add_column("Package", style="cyan", no_wrap=True)
            table.add_column("Version", style="green")
            table.add_column("Description", style="white")
            
            for pkg_path, pkg_info in sorted_results:
                pkg_name = pkg_path.split('.')[-1]
                version = pkg_info.get('version', 'unknown')
                description = pkg_info.get('description', 'No description')[:60]
                if len(pkg_info.get('description', '')) > 60:
                    description += "..."
                
                table.add_row(pkg_name, version, description)
            
            console.print(table)
            console.print(f"\n[dim]Showing top {len(sorted_results)} results[/dim]")
            console.print("\n💡 To install: [bold]ask-nix 'install package-name'[/bold]")
        else:
            # Simple text output
            print(f"\nFound {len(results)} packages:")
            print("-" * 60)
            
            for pkg_path, pkg_info in sorted_results:
                pkg_name = pkg_path.split('.')[-1]
                version = pkg_info.get('version', 'unknown')
                description = pkg_info.get('description', 'No description')[:50]
                if len(pkg_info.get('description', '')) > 50:
                    description += "..."
                
                print(f"  {pkg_name} ({version})")
                print(f"    {description}")
                print()
            
            print(f"\nShowing top {len(sorted_results)} results")
            print("\n💡 To install: ask-nix 'install package-name'")
    
    def validate_package_name(self, package: str) -> tuple:
        """Validate if package exists in nixpkgs"""
        if not package:
            return False, "No package name provided"
            
        # Skip validation if using bridge - let nix handle it
        if hasattr(self, 'use_bridge') and self.use_bridge:
            return True, "Package validation deferred to nix"
            
        # Quick validation with nix search
        spinner = None
        if self.show_progress:
            spinner = ProgressSpinner("🔍 Validating package name", "2-5 seconds")
            spinner.start()
            
        try:
            # Search more broadly - just check if search returns any results
            result = subprocess.run(
                ["nix", "search", "nixpkgs", package, "--json"],
                capture_output=True,
                text=True,
                timeout=15  # Reduced timeout from 30 to 15 seconds
            )
            
            if spinner:
                spinner.stop()
                
            if result.returncode == 0 and result.stdout.strip() != "{}":
                # Parse JSON to find exact match or close match
                try:
                    import json
                    packages = json.loads(result.stdout)
                    # Look for exact match or package containing the search term
                    for pkg_path, pkg_info in packages.items():
                        pkg_name = pkg_path.split('.')[-1]
                        if pkg_name.lower() == package.lower():
                            return True, f"Package '{package}' found"
                        elif package.lower() in pkg_name.lower():
                            return True, f"Package '{package}' found (as '{pkg_name}')"
                    # If we found results but no exact match, still allow it
                    if packages:
                        return True, f"Package '{package}' may be available"
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
                    
                return True, "Package search returned results"
            else:
                # Try common aliases
                if package in self.basic_knowledge.package_aliases:
                    actual_package = self.basic_knowledge.package_aliases[package]
                    return True, f"Package '{package}' maps to '{actual_package}'"
                    
                # For common packages that might have different names, be lenient
                common_packages = ['tree', 'htop', 'git', 'vim', 'emacs', 'firefox', 'chrome']
                if package.lower() in common_packages:
                    return True, f"Package '{package}' is likely available"
                    
                return False, f"Package '{package}' not found in nixpkgs"
        except subprocess.TimeoutExpired:
            if spinner:
                spinner.stop()
            print("\n⚠️  Package validation timed out")
            # On timeout, be permissive rather than restrictive
            return True, f"Could not validate package '{package}' in time, proceeding anyway"
        except Exception as e:
            if spinner:
                spinner.stop()
            # On error, be permissive rather than restrictive
            return True, f"Could not validate package '{package}' ({str(e)}), proceeding anyway"
    
    def confirm_action(self, action: str, details: str) -> bool:
        """Ask for confirmation before destructive actions"""
        print(f"\n⚠️  Confirm {action}:")
        print(f"   {details}")
        print()
        
        # Check if we're in a non-interactive environment
        if not sys.stdin.isatty():
            print("Running in non-interactive mode, auto-confirming...")
            return True
            
        try:
            response = input("Proceed? [y/N]: ").strip().lower()
            return response in ['y', 'yes']
        except EOFError:
            # Handle EOF error in pipes/scripts
            print("\nNo input available, assuming 'no'")
            return False
        except KeyboardInterrupt:
            print("\nCancelled by user")
            return False
    
    def execute_list(self):
        """Execute list packages command with formatting"""
        print("📦 Listing installed packages...")
        
        command = "nix profile list"
        
        # Execute the command
        success, output, error = self.execute_with_progress(command, "list")
        
        if success:
            if output.strip():
                print("\n📋 Installed packages:")
                print("-" * 50)
                
                # Parse and format the output (new nix profile list format)
                lines = output.strip().split('\n')
                package_num = 1
                current_package = None
                
                for line in lines:
                    line = line.strip()
                    # Look for package names (bold in terminal output)
                    if line.startswith('Name:'):
                        # Extract package name (remove ANSI codes)
                        import re
                        package_name = re.sub(r'\x1b\[[0-9;]*m', '', line)
                        package_name = package_name.replace('Name:', '').strip()
                        if package_name and package_name != 'home-manager-path':
                            print(f"  {package_num}. {package_name}")
                            package_num += 1
                        
                print("\n💡 Tip: Use 'ask-nix \"remove package-name\"' to remove a package")
            else:
                print("\n📋 No packages installed in current profile")
                print("\n💡 Install packages with: ask-nix \"install package-name\"")
        else:
            print(f"\n❌ Failed to list packages: {error}")
    
    def execute_remove(self, package: str):
        """Execute package removal with confirmation"""
        # Try Python backend first
        if self.try_python_backend("remove", package):
            return
            
        # First list packages in JSON format to get indices
        result = subprocess.run(
            ["nix", "profile", "list", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to list packages: {result.stderr}")
            return
            
        # Parse JSON to find the package
        package_index = None
        package_name_found = None
        
        try:
            profiles = json.loads(result.stdout)
            # profiles is a dict where keys are indices
            for index, info in profiles.items():
                # Check various fields for the package name
                if 'storePaths' in info and info['storePaths']:
                    # Extract package name from store path
                    store_path = info['storePaths'][0]
                    # Format: /nix/store/hash-packagename-version
                    parts = store_path.split('-', 2)
                    if len(parts) >= 3:
                        pkg_name = parts[1]
                        if package.lower() in pkg_name.lower():
                            package_index = index
                            package_name_found = pkg_name
                            break
                
                # Also check flakeAttribute if available
                if 'flakeAttribute' in info:
                    attr = info['flakeAttribute']
                    if package.lower() in attr.lower():
                        package_index = index
                        package_name_found = attr.split('.')[-1]
                        break
        except json.JSONDecodeError:
            print("❌ Failed to parse package list")
            return
        
        if not package_index:
            print(f"\n⚠️  Package '{package}' not found in profile")
            print("\n💡 Use 'ask-nix \"list packages\"' to see installed packages")
            return
        
        # Confirm removal
        if not self.dry_run and not hasattr(self, 'skip_confirmation'):
            if not self.confirm_action("removal", f"Remove package '{package}' (index {package_index})"):
                print("\n❌ Removal cancelled.")
                return
        
        print(f"\n🗑️  Removing {package}...")
        
        command = f"nix profile remove {package_index}"
        if self.dry_run:
            command += " --dry-run"
            print(f"\n🔍 Dry run mode - showing what would happen:")
        
        # Execute the command
        success, output, error = self.execute_with_progress(command, "remove")
        
        # Record outcome for learning (if enabled)
        if self.learning_enabled and hasattr(self, 'current_command_id') and self.current_command_id:
            self.learning_system.record_outcome(self.current_command_id, success=success, error=error if not success else None)
        
        if success:
            if self.dry_run:
                print("\n✅ Dry run successful! To actually remove, run:")
                print(f"   {command.replace(' --dry-run', '')}")
            else:
                print(f"\n✅ Successfully removed {package}!")
                print("\n💡 The package has been removed from your profile.")
        else:
            # Check for learned solutions (if enabled)
            if self.learning_enabled and hasattr(self, 'learning_system') and error:
                if hasattr(self.learning_system, 'get_error_solution'):
                    solution = self.learning_system.get_error_solution(error)
                else:
                    solution = None
                if solution:
                    print(f"\n💡 Based on previous experience: {solution}")
            
            print(f"\n❌ Removal failed: {error}")
            print("\n💡 Troubleshooting tips:")
            print("   - Check if the package is installed")
            print("   - Use 'ask-nix \"list packages\"' to verify")
    
    def execute_update(self, prefer_no_sudo: bool = False):
        """Execute system update with appropriate method"""
        # Try Python backend first
        if self.try_python_backend("update"):
            return
            
        if prefer_no_sudo or not self._is_nixos():
            # Use Home Manager if available
            if self.check_home_manager_installed():
                print("🔄 Updating Home Manager packages...")
                command = "home-manager switch"
                operation = "Home Manager update"
            else:
                print("🔄 Updating nix profile packages...")
                command = "nix profile upgrade '.*'"
                operation = "profile update"
        else:
            # Full system update
            print("🔄 Updating NixOS system configuration...")
            
            # Confirm system update
            if not self.dry_run and not hasattr(self, 'skip_confirmation'):
                if not self.confirm_action("system update", "Update entire NixOS system (requires sudo)"):
                    print("\n❌ Update cancelled.")
                    return
            
            # Update channels first
            print("\n📡 Updating channels...")
            channel_success, _, channel_error = self.execute_with_progress(
                "sudo nix-channel --update", 
                "channel update"
            )
            
            if not channel_success:
                print(f"⚠️  Channel update failed: {channel_error}")
                print("Continuing with system rebuild anyway...")
            
            command = "sudo nixos-rebuild switch"
            operation = "system rebuild"
            
            if self.dry_run:
                command += " --dry-run"
                print(f"\n🔍 Dry run mode - showing what would happen:")
        
        # Execute the update
        success, output, error = self.execute_with_progress(command, operation)
        
        # Record outcome for learning (if enabled)
        if self.learning_enabled and hasattr(self, 'current_command_id') and self.current_command_id:
            self.learning_system.record_outcome(self.current_command_id, success=success, error=error if not success else None)
            if success:
                # Learn user preference for update method
                update_method = 'sudo' if 'sudo' in command else 'no-sudo'
                self.learning_system.learn_user_preference('update_method', update_method)
        
        if success:
            if self.dry_run:
                print("\n✅ Dry run successful! To actually update, run:")
                print(f"   {command.replace(' --dry-run', '')}")
            else:
                print(f"\n✅ Successfully updated!")
                if "nixos-rebuild" in command:
                    print("\n🎉 Your NixOS system is now up to date!")
                    print("💡 Tip: Some changes may require a reboot to take effect.")
                else:
                    print("\n🎉 Your packages are now up to date!")
        else:
            # Check for learned solutions (if enabled)
            if self.learning_enabled and hasattr(self, 'learning_system') and error:
                if hasattr(self.learning_system, 'get_error_solution'):
                    solution = self.learning_system.get_error_solution(error)
                else:
                    solution = None
                if solution:
                    print(f"\n💡 Based on previous experience: {solution}")
            
            print(f"\n❌ Update failed: {error}")
            print("\n💡 Troubleshooting tips:")
            print("   - Check your internet connection")
            print("   - Try running with --show-trace for more details")
            if "nixos-rebuild" in command:
                print("   - Check for syntax errors in /etc/nixos/configuration.nix")
    
    def _is_nixos(self) -> bool:
        """Check if running on NixOS"""
        try:
            return Path("/etc/nixos/configuration.nix").exists()
        except Exception:
            return False
    
    def execute_install(self, package: str, method: str = 'nix-profile'):
        """Execute package installation with proper error handling"""
        # Try Python backend first
        if self.try_python_backend("install", package):
            return
        
        # Validate package first
        valid, message = self.validate_package_name(package)
        if not valid:
            print(f"\n⚠️  {message}")
            print("\n💡 Try searching for the package:")
            print(f"   nix search nixpkgs {package}")
            return
        
        # Confirm installation unless --yes flag is used
        if not self.dry_run and not hasattr(self, 'skip_confirmation'):
            if not self.confirm_action("installation", f"Install package '{package}'"):
                print("\n❌ Installation cancelled.")
                return
        
        print(f"\n📦 Installing {package} using {method}...")
        
        if method == 'nix-profile':
            command = f"nix profile install nixpkgs#{package}"
            if self.dry_run:
                command += " --dry-run"
                print(f"\n🔍 Dry run mode - showing what would happen:")
                
        elif method == 'home-manager':
            if not self.check_home_manager_installed():
                print("\n⚠️  Home Manager is not installed.")
                print("\n💡 To install Home Manager, run:")
                print("   nix-channel --add https://github.com/nix-community/home-manager/archive/master.tar.gz home-manager")
                print("   nix-channel --update")
                print("   nix-shell '<home-manager>' -A install")
                return
                
            print("\n📝 To install with Home Manager:")
            print(f"1. Edit ~/.config/home-manager/home.nix")
            print(f"2. Add to home.packages: {package}")
            print(f"3. Run: home-manager switch")
            return
            
        # Execute the command - use bridge if available
        if hasattr(self, 'use_bridge') and self.use_bridge:
            intent = {
                'action': 'install_package',
                'package': package
            }
            success, output, error = self.execute_with_bridge(intent, "install")
        else:
            success, output, error = self.execute_with_progress(command, "install")
        
        # Record outcome for learning (if enabled)
        if self.learning_enabled and hasattr(self, 'current_command_id') and self.current_command_id:
            self.learning_system.record_outcome(self.current_command_id, success=success, error=error if not success else None)
            if success:
                # Learn user preference for install method
                self.learning_system.learn_user_preference('install_method', method)
        
        if success:
            if self.dry_run:
                print("\n✅ Dry run successful! To actually install, run:")
                print(f"   {command.replace(' --dry-run', '')}")
            else:
                print(f"\n✅ Successfully installed {package}!")
                print("\n💡 The package is now available in your PATH.")
        else:
            # Check for learned solutions (if enabled)
            if self.learning_enabled and hasattr(self, 'learning_system') and error:
                if hasattr(self.learning_system, 'get_error_solution'):
                    solution = self.learning_system.get_error_solution(error)
                else:
                    solution = None
                if solution:
                    print(f"\n💡 Based on previous experience: {solution}")
            
            # If error is already formatted (from bridge), just print it
            if hasattr(self, 'use_bridge') and self.use_bridge and '\n💡 Suggestions:' in error:
                print(error)
            else:
                print(f"\n❌ Installation failed: {error}")
                print("\n💡 Troubleshooting tips:")
                print("   - Check if the package name is correct")
                print("   - Try updating your channels: nix-channel --update")
                print("   - Check your internet connection")
    
    def answer(self, query: str):
        """Process query through modern knowledge engine"""
        
        # Security audit if available
        if V1_IMPROVEMENTS_AVAILABLE:
            audit_result = audit_user_input(query, context="nlp")
            if not audit_result.passed:
                print("\n🛡️ Security Notice:")
                for violation in audit_result.violations:
                    print(f"  ⚠️  {violation.description}")
                    if violation.remediation:
                        print(f"     💡 {violation.remediation}")
                if audit_result.score < 0.5:
                    print("\n❌ Query blocked for security reasons.")
                    return
                    
        # Try Python backend first for all queries
        if self.try_general_python_backend(query):
            return
        
        # Fallback: Simple pattern matching if backend not available
        # This ensures basic functionality always works
        intent = self._simple_intent_recognition(query)
        
        # Record command for learning (if enabled)
        if self.learning_enabled and hasattr(self, 'learning_system') and hasattr(self.learning_system, 'record_command'):
            self.current_command_id = self.learning_system.record_command(
                intent=intent['action'],
                query=query,
                command=f"ask-nix {query}",
                executed=not self.dry_run  # Only mark as executed if not dry-run
            )
        
        if self.show_intent:
            print(f"\n🎯 Intent detected: {intent['action']}")
            if intent.get('package'):
                print(f"📦 Package: {intent['package']}")
            if intent.get('prefer_no_sudo'):
                print(f"🔓 No sudo preference: Yes")
            print()
        
        # Check for learned suggestions (if enabled)
        if self.learning_enabled and hasattr(self, 'learning_system'):
            # Get success rate for this intent
            if hasattr(self.learning_system, 'get_success_rate'):
                success_rate = self.learning_system.get_success_rate(intent['action'])
            else:
                success_rate = 1.0  # Default to high success rate if method not available
            if success_rate < 0.5 and success_rate > 0:  # Low success rate
                print(f"⚠️  Note: This command has a {success_rate:.0%} success rate in your history")
                print("   Consider checking the command syntax or using --help\n")
        
        # Step 1.5: Check if a plugin can handle this intent
        if self.plugin_manager:
            plugin_context = {
                'query': query,
                'intent': intent,
                'session_id': self.session_id,
                'dry_run': self.dry_run,
                'personality': self.personality
            }
            
            plugin_result = self.plugin_manager.handle_intent(intent['action'], plugin_context)
            
            if plugin_result and plugin_result.get('success'):
                # Plugin handled the request
                final_response = plugin_result.get('response', '')
                
                # Apply personality to plugin response
                final_response = self.enhance_response(final_response, query, self.personality)
                
                # Add dry-run notice if applicable
                if self.dry_run and intent['action'] in ['install_package', 'remove_package', 'update_system', 'update_system_sudo']:
                    final_response += "\n\n🔍 Running in dry-run mode (use without --dry-run to execute)"
                
                print(final_response)
                
                # Collect feedback if enabled
                if self.collect_feedback and self.personality == 'symbiotic':
                    self._gather_feedback(query, final_response, intent)
                
                return
        
        # Step 2: Get accurate solution using modern engine (fallback if no plugin)
        solution = self._get_solution(intent)
        
        # Step 3: Format response
        response = self._format_response(intent, solution)
        
        # Step 4: Add personality
        final_response = self.enhance_response(response, query, self.personality)
        
        # Step 5: Add dry-run notice if applicable
        if self.dry_run and intent['action'] in ['install_package', 'remove_package', 'update_system', 'update_system_sudo']:
            final_response += "\n\n🔍 Running in dry-run mode (use without --dry-run to execute)"
        
        print(final_response)
        
        # Step 6: Collect feedback if enabled
        if self.collect_feedback and self.personality == 'symbiotic':
            self._gather_feedback(query, final_response, intent)
        
        # Step 7: Note about execution (removed since we now auto-execute)
    
    def _gather_feedback(self, query: str, response: str, intent: Dict):
        """Gather user feedback for continuous improvement"""
        try:
            # Quick implicit feedback
            print("\n" + "=" * 50)
            helpful = input("Was this helpful? (y/n/skip): ").lower().strip()
            
            if helpful == 'skip' or helpful == '':
                # User chose to skip feedback
                return
            
            if helpful == 'n':
                # Collect improvement
                print("\nI'd love to learn how to help better!")
                improved = input("What would have been a better response? (or press Enter to skip): ").strip()
                
                if improved:
                    self.feedback_collector.collect_explicit_feedback(
                        query=query,
                        response=response,
                        helpful=False,
                        better_response=improved,
                        session_id=self.session_id
                    )
                    print("Thank you! I'll use this to improve.")
                else:
                    # Just record that it wasn't helpful
                    self.feedback_collector.collect_explicit_feedback(
                        query=query,
                        response=response,
                        helpful=False,
                        session_id=self.session_id
                    )
            
            elif helpful == 'y':
                # Record positive feedback
                self.feedback_collector.collect_explicit_feedback(
                    query=query,
                    response=response,
                    helpful=True,
                    rating=5,  # Implicit high rating for helpful
                    session_id=self.session_id
                )
                print("Great! Thank you for the feedback.")
            
            # Track usage pattern
            if intent['action'] == 'install_package' and intent.get('package'):
                self.feedback_collector.track_usage_pattern(
                    action='install_package',
                    package=intent['package'],
                    success=True if helpful == 'y' else False,
                    session_id=self.session_id
                )
        
        except KeyboardInterrupt:
            # User interrupted feedback - that's OK
            pass
        except Exception as e:
            # Don't let feedback errors interrupt the main flow
            if os.getenv('DEBUG'):
                print(f"\nFeedback error: {e}")
        
    def set_personality(self, style: str):
        """Change response personality"""
        if style in ['minimal', 'friendly', 'encouraging', 'technical', 'symbiotic']:
            self.personality = style

def print_usage():
    """Print usage information"""
    # Get plugin information if available
    plugin_info = None
    plugin_flags = []
    try:
        # Create a temporary instance to get plugin info
        temp_assistant = UnifiedNixAssistant()
        if temp_assistant.plugin_manager:
            plugin_info = temp_assistant.plugin_manager.get_plugin_info()
            plugin_flags = temp_assistant.plugin_manager.get_all_flags()
    except Exception:
        # TODO: Add proper error handling
        pass  # Silent for now, should log error
    
    if RICH_AVAILABLE:
        console.print("[bold cyan]🗣️  Nix for Humanity - Unified Command[/bold cyan]")
        console.print("Natural language interface for NixOS\n")
        
        console.print("[bold]Usage:[/bold] ask-nix [OPTIONS] 'your question'")
        
        console.print("\n[bold]Examples:[/bold]")
        console.print("  ask-nix 'How do I install Firefox?'")
        console.print("  ask-nix 'Search for python packages'")
        console.print("  ask-nix 'Update my system'")
        console.print("  ask-nix 'List installed packages'")
        
        console.print("\n[bold]Personality Options:[/bold]")
        console.print("  --minimal         Just the facts")
        console.print("  --friendly        Warm and helpful (default)")
        console.print("  --encouraging     Supportive for beginners")
        console.print("  --technical       Detailed explanations")
        console.print("  --symbiotic       🧬 Co-evolutionary mode (admits uncertainty)")
        
        console.print("\n[bold]Execution Options:[/bold]")
        console.print("  --dry-run         Test without executing")
        console.print("  --yes             Skip confirmation prompts")
        console.print("  --execute         Use execution bridge (safer)")
        console.print("  --bridge          Alias for --execute")
        
        console.print("\n[bold]Visual Options:[/bold]")
        console.print("  --no-progress     Disable progress indicators")
        console.print("  --no-visual       Disable rich formatting")
        console.print("  --show-intent     Show intent detection")
        
        console.print("\n[bold]Cache Options:[/bold]")
        console.print("  --no-cache        Disable intelligent caching")
        console.print("  --clear-cache     Clear cache before running")
        
        console.print("\n[bold]Learning System:[/bold]")
        console.print("  --enable-learning     Turn on intelligent learning")
        console.print("  --disable-learning    Turn off learning")
        console.print("  --learning-status     Check if learning is enabled")
        console.print("  --show-insights       View your usage patterns")
        console.print("  --show-privacy        See what data is tracked")
        console.print("  --export-learning     Export your learning data")
        console.print("  --clear-learning      Clear learning data")
        
        console.print("\n[bold]Setup & Security:[/bold]")
        console.print("  --setup               Run first-time setup wizard")
        console.print("  --security-report     View security report")
        
        console.print("\n[bold]Feedback Options:[/bold]")
        console.print("  --no-feedback     Don't collect feedback")
        console.print("  --summary         Show feedback summary")
        
        console.print("\n[bold]Unified Features:[/bold]")
        console.print("  ✨ Intelligent search caching (100x faster!)")
        console.print("  🧠 Command learning system")
        console.print("  📊 Rich visual feedback (when available)")
        console.print("  🔄 Modern nix profile commands")
        console.print("  🏠 Home Manager integration")
        console.print("  🎓 Educational error messages")
        console.print("  🔁 Automatic retry on failures")
        console.print("  🎭 Multiple personality styles")
        console.print("  🔒 Privacy-first local learning")
        
        # Add plugin information
        if plugin_info and plugin_info['total_plugins'] > 0:
            console.print(f"\n[bold]Plugin System:[/bold]")
            console.print(f"  🔌 Total plugins loaded: {plugin_info['total_plugins']}")
            console.print(f"  🎭 Personality plugins: {plugin_info['personality_plugins']}")
            console.print(f"  ✨ Feature plugins: {plugin_info['feature_plugins']}")
            
            if plugin_flags:
                console.print("\n[bold]Plugin Options:[/bold]")
                for flag_info in plugin_flags:
                    flag_name = flag_info.get('name', '')
                    flag_desc = flag_info.get('description', 'No description')
                    if flag_name:
                        console.print(f"  {flag_name:<20} {flag_desc}")
    else:
        print("🗣️  Nix for Humanity - Unified Command")
        print("Natural language interface for NixOS\n")
        
        print("Usage: ask-nix [OPTIONS] 'your question'")
        
        print("\nExamples:")
        print("  ask-nix 'How do I install Firefox?'")
        print("  ask-nix 'Search for python packages'")
        print("  ask-nix 'Update my system'")
        print("  ask-nix 'List installed packages'")
        
        print("\nPersonality Options:")
        print("  --minimal         Just the facts")
        print("  --friendly        Warm and helpful (default)")
        print("  --encouraging     Supportive for beginners")
        print("  --technical       Detailed explanations")
        print("  --symbiotic       🧬 Co-evolutionary mode (admits uncertainty)")
        
        print("\nExecution Options:")
        print("  --dry-run         Test without executing")
        print("  --yes             Skip confirmation prompts")
        print("  --execute         Use execution bridge (safer)")
        print("  --bridge          Alias for --execute")
        
        print("\nVisual Options:")
        print("  --no-progress     Disable progress indicators")
        print("  --no-visual       Disable rich formatting")
        print("  --show-intent     Show intent detection")
        
        print("\nCache Options:")
        print("  --no-cache        Disable intelligent caching")
        print("  --clear-cache     Clear cache before running")
        
        print("\nFeedback Options:")
        print("  --no-feedback     Don't collect feedback")
        print("  --summary         Show feedback summary")
        
        print("\nUnified Features:")
        print("  ✨ Intelligent search caching (100x faster!)")
        print("  🧠 Command learning system")
        print("  📊 Rich visual feedback (when available)")
        print("  🔄 Modern nix profile commands")
        print("  🏠 Home Manager integration")
        print("  🎓 Educational error messages")
        print("  🔁 Automatic retry on failures")
        print("  🎭 Multiple personality styles")
        
        # Add plugin information
        if plugin_info and plugin_info['total_plugins'] > 0:
            print(f"\nPlugin System:")
            print(f"  🔌 Total plugins loaded: {plugin_info['total_plugins']}")
            print(f"  🎭 Personality plugins: {plugin_info['personality_plugins']}")
            print(f"  ✨ Feature plugins: {plugin_info['feature_plugins']}")
            
            if plugin_flags:
                print("\nPlugin Options:")
                for flag_info in plugin_flags:
                    flag_name = flag_info.get('name', '')
                    flag_desc = flag_info.get('description', 'No description')
                    if flag_name:
                        print(f"  {flag_name:<20} {flag_desc}")

def main():
    # Check for first-run wizard if available
    if V1_IMPROVEMENTS_AVAILABLE:
        try:
            from luminous_nix.config.config_manager import ConfigManager
            config_manager = ConfigManager()
            if not run_if_needed(config_manager):
                print("\n❌ Setup failed. Please try again or use default settings.")
                # Continue with defaults
        except Exception as e:
            if os.environ.get('NIX_HUMANITY_DEBUG', '').lower() == 'true':
                print(f"Debug: First-run wizard error: {e}")
    
    # Intelligent dispatcher logic
    is_interactive = sys.stdout.isatty()
    has_piped_input = not sys.stdin.isatty()
    has_cli_args = len(sys.argv) > 1
    
    # Check if we should launch the TUI
    if is_interactive and not has_piped_input and not has_cli_args:
        # No arguments, interactive terminal, no piped input = launch TUI!
        try:
            # Try to import and run the TUI
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
            from luminous_nix.tui import run as run_tui
            
            print("✨ Launching Nix for Humanity interactive interface...")
            print("💡 Tip: For CLI mode, use: ask-nix 'your question'")
            print()
            time.sleep(1)  # Brief pause for user to read
            
            # Run the TUI
            run_tui()
            return
        except ImportError as e:
            # TUI not available, fall back to showing usage
            print("⚠️  Interactive TUI not available. Using CLI mode.")
            print(f"   (Error: {e})")
            print()
            print_usage()
            sys.exit(1)
    
    # Otherwise, continue with CLI mode
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # Handle special commands
    if len(sys.argv) >= 2 and sys.argv[1].startswith('--'):
        # Handle setup wizard
        if sys.argv[1] == '--setup':
            if V1_IMPROVEMENTS_AVAILABLE:
                from luminous_nix.config.config_manager import ConfigManager
                wizard = FirstRunWizard(ConfigManager())
                if wizard.run():
                    print("\n✅ Setup completed successfully!")
                else:
                    print("\n❌ Setup failed or was cancelled.")
            else:
                print("Setup wizard not available in this version.")
            return
            
        # Handle security report
        if sys.argv[1] == '--security-report':
            if V1_IMPROVEMENTS_AVAILABLE:
                report = security_auditor.get_security_report()
                print("\n🛡️ Security Report (last 7 days):")
                print(f"Total violations: {report['total_violations']}")
                if report['by_category']:
                    print("\nBy Category:")
                    for cat, count in report['by_category'].items():
                        print(f"  • {cat}: {count}")
                if report['by_threat_level']:
                    print("\nBy Threat Level:")
                    for level, count in report['by_threat_level'].items():
                        print(f"  • {level}: {count}")
            else:
                print("Security auditing not available in this version.")
            return
        
        # Handle feedback summary
        if sys.argv[1] == '--summary':
            collector = FeedbackCollector()
            summary = collector.get_feedback_summary()
            print("\n📊 Feedback Summary:")
            print(f"Total feedback collected: {summary['total_feedback']}")
            print(f"Helpfulness rate: {summary['helpfulness_rate']:.1%}")
            print(f"Average rating: {summary['average_rating']:.1f}/5")
            print(f"Preferences collected: {summary['total_preferences']}")
            print(f"Usage patterns tracked: {summary['total_patterns']}")
            print(f"Success rate: {summary['success_rate']:.1%}")
            print(f"\nData location: {summary['data_path']}")
            return
        
        # Handle learning system commands
        learning_commands = {
            '--enable-learning': 'enable',
            '--disable-learning': 'disable',
            '--learning-status': 'status',
            '--show-insights': 'insights',
            '--show-privacy': 'privacy',
            '--export-learning': 'export',
            '--clear-learning': 'clear'
        }
        
        if sys.argv[1] in learning_commands:
            # Run the learning activation script
            import subprocess
            script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'activate-learning.py')
            cmd = [sys.executable, script_path, learning_commands[sys.argv[1]]]
            
            # Add additional args (like --purge or days for clear)
            if len(sys.argv) > 2:
                cmd.extend(sys.argv[2:])
                
            subprocess.run(cmd)
            return
    
    assistant = UnifiedNixAssistant()
    
    # Get plugin flags if available
    plugin_flags = {}
    if assistant.plugin_manager:
        for flag_info in assistant.plugin_manager.get_all_flags():
            flag_name = flag_info.get('name', '')
            if flag_name:
                plugin_flags[flag_name] = flag_info
    
    # Parse arguments
    args = sys.argv[1:]
    execute_mode = False
    
    while args and args[0].startswith('--'):
        flag = args.pop(0)
        
        if flag in ['--minimal', '--friendly', '--encouraging', '--technical', '--symbiotic']:
            assistant.set_personality(flag[2:])
        elif flag == '--dry-run':
            assistant.dry_run = True
        elif flag == '--yes':
            assistant.skip_confirmation = True
        elif flag == '--show-intent':
            assistant.show_intent = True
        elif flag == '--no-progress':
            assistant.show_progress = False
        elif flag in ['--execute', '--bridge']:
            assistant.use_bridge = True
        elif flag == '--no-visual':
            assistant.visual_mode = False
        elif flag == '--no-cache':
            assistant.use_cache = False
        elif flag == '--no-feedback':
            assistant.collect_feedback = False
        elif flag == '--clear-cache':
            if RICH_AVAILABLE and assistant.visual_mode:
                console.print("[yellow]Cache clearing not implemented yet[/yellow]")
            else:
                print("Cache clearing not implemented yet")
            # TODO: Implement cache clearing functionality
            # For now, just inform the user
        elif flag == '--help':
            print_usage()
            sys.exit(0)
        elif flag in plugin_flags:
            # Handle plugin flag
            flag_info = plugin_flags[flag]
            handler = flag_info.get('handler')
            if handler and callable(handler):
                # Call the plugin's flag handler
                if flag_info.get('takes_value', False) and args:
                    value = args.pop(0)
                    handler(value)
                else:
                    handler()
            else:
                print(f"Plugin flag {flag} has no handler")
        else:
            print(f"Unknown option: {flag}")
            print_usage()
            sys.exit(1)
    
    if not args:
        print("Error: No question provided")
        sys.exit(1)
        
    query = ' '.join(args)
    
    # Process the query
    assistant.answer(query)
    
    # Auto-execute install commands (unless in dry-run mode)
    intent = assistant._simple_intent_recognition(query)
    if intent['action'] == 'install_package' and intent.get('package'):
        print()
        if not assistant.dry_run:
            # Determine method based on sudo preference
            if intent.get('prefer_no_sudo'):
                if assistant.check_home_manager_installed():
                    method = 'home-manager'
                else:
                    method = 'nix-profile'
            else:
                method = 'nix-profile'
                
            assistant.execute_install(intent['package'], method)
    
    # Auto-execute list commands
    elif intent['action'] == 'list_packages':
        print()
        assistant.execute_list()
    
    # Auto-execute remove commands
    elif intent['action'] == 'remove_package' and intent.get('package'):
        print()
        if not assistant.dry_run:
            # Use bridge if available
            if hasattr(assistant, 'use_bridge') and assistant.use_bridge:
                intent_for_bridge = {
                    'action': 'remove_package',
                    'package': intent['package']
                }
                success, output, error = assistant.execute_with_bridge(intent_for_bridge, "remove")
                if success:
                    print(f"\n✅ Successfully removed {intent['package']}!")
                else:
                    # Error is already formatted with suggestions
                    print(error)
            else:
                assistant.execute_remove(intent['package'])
    
    # Auto-execute search commands
    elif intent['action'] == 'search_package':
        print()
        # Use the new unified search method with caching
        assistant.execute_search(query, intent.get('package'))
    
    # Auto-execute update commands
    elif intent['action'] in ['update_system', 'update_system_sudo']:
        print()
        if not assistant.dry_run:
            # Use bridge if available
            if hasattr(assistant, 'use_bridge') and assistant.use_bridge:
                intent_for_bridge = {
                    'action': 'update_system',
                    'query': query,
                    'systemUpdate': intent['action'] == 'update_system_sudo'
                }
                success, output, error = assistant.execute_with_bridge(intent_for_bridge, "update")
                if success:
                    print(f"\n✅ Update completed successfully!")
                else:
                    print(f"\n❌ Update failed: {error}")
            else:
                assistant.execute_update(intent.get('prefer_no_sudo', False))
    
    # Auto-execute config generation commands
    elif intent['action'] == 'generate_config':
        # Config generation is handled in the answer method, just need to print the command
        print()
        if not assistant.dry_run:
            print("💡 To use the generated configuration, run:")
            print("   ask-nix config generate \"" + query + "\"")

if __name__ == "__main__":
    main()

if __name__ == '__main__':
    main()