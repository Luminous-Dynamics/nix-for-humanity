#!/usr/bin/env python3
"""
🎤 Voice Commands Registry for UI Generation
Comprehensive voice command system for NixOS interface generation
"""

import re
import json
from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from nixos_package_interface import NixOSPackageInterface
from nixos_config_editor import NixOSConfigEditor
from system_monitor_dashboard import SystemMonitorDashboard
from service_management_interface import ServiceManagementInterface
from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext


@dataclass
class VoiceCommandPattern:
    """Pattern for voice command matching"""
    
    pattern: str  # Regex pattern
    handler: Callable
    interface_type: str
    description: str
    examples: List[str]
    priority: int = 0  # Higher priority patterns matched first


class VoiceCommandRegistry:
    """Registry of all voice commands for UI generation"""
    
    def __init__(self):
        # Initialize all interface generators
        self.package_interface = NixOSPackageInterface()
        self.config_editor = NixOSConfigEditor()
        self.system_monitor = SystemMonitorDashboard()
        self.service_manager = ServiceManagementInterface()
        self.ui_builder = NLInterfaceBuilderV2(use_llm=False)
        
        # Command patterns registry
        self.command_patterns: List[VoiceCommandPattern] = []
        
        # Register all voice commands
        self._register_package_commands()
        self._register_config_commands()
        self._register_monitor_commands()
        self._register_service_commands()
        self._register_generic_commands()
        self._register_navigation_commands()
        self._register_help_commands()
        
        # Sort by priority
        self.command_patterns.sort(key=lambda x: x.priority, reverse=True)
    
    def _register_package_commands(self):
        """Register package management voice commands"""
        
        # Search packages
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(search|find|look for) (?:packages? )?(?:for |named )?([\w\s-]+)",
            handler=self._handle_package_search,
            interface_type="package_search",
            description="Search for NixOS packages",
            examples=[
                "search for firefox",
                "find packages named vim",
                "look for browser packages"
            ],
            priority=10
        ))
        
        # Install package
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(install|add|get) (?:package )?([\w\s-]+)",
            handler=self._handle_package_install,
            interface_type="package_install",
            description="Install a NixOS package",
            examples=[
                "install firefox",
                "add vim package",
                "get chromium"
            ],
            priority=10
        ))
        
        # Remove package
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(remove|uninstall|delete) (?:package )?([\w\s-]+)",
            handler=self._handle_package_remove,
            interface_type="package_remove",
            description="Remove a NixOS package",
            examples=[
                "remove firefox",
                "uninstall vim",
                "delete chromium package"
            ],
            priority=10
        ))
        
        # Show package manager
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:show|open|display) (?:the )?package manager",
            handler=self._handle_package_manager,
            interface_type="package_manager",
            description="Show package manager interface",
            examples=[
                "show package manager",
                "open the package manager",
                "display package manager"
            ],
            priority=9
        ))
    
    def _register_config_commands(self):
        """Register configuration editing commands"""
        
        # Open config editor
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:open|show|edit) (?:nixos )?(?:configuration|config|settings)",
            handler=self._handle_config_editor,
            interface_type="config_editor",
            description="Open NixOS configuration editor",
            examples=[
                "open configuration",
                "edit nixos config",
                "show settings"
            ],
            priority=9
        ))
        
        # Edit specific config section
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:edit|modify|change) (?:the )?(boot|network|services|packages|users) (?:configuration|config|settings)?",
            handler=self._handle_config_section,
            interface_type="config_section",
            description="Edit specific configuration section",
            examples=[
                "edit boot configuration",
                "modify network settings",
                "change services config"
            ],
            priority=10
        ))
    
    def _register_monitor_commands(self):
        """Register system monitoring commands"""
        
        # Show system monitor
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:show|open|display) (?:system )?(?:monitor|monitoring|metrics|stats)",
            handler=self._handle_system_monitor,
            interface_type="system_monitor",
            description="Show system monitoring dashboard",
            examples=[
                "show system monitor",
                "open monitoring",
                "display metrics"
            ],
            priority=9
        ))
        
        # Show specific metric
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:show|display|check) (?:the )?(cpu|memory|disk|network) (?:usage|status|metric)?",
            handler=self._handle_specific_metric,
            interface_type="specific_metric",
            description="Show specific system metric",
            examples=[
                "show cpu usage",
                "check memory status",
                "display disk usage"
            ],
            priority=10
        ))
    
    def _register_service_commands(self):
        """Register service management commands"""
        
        # Show services
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:show|list|display) (?:all )?(?:services|daemons|processes)",
            handler=self._handle_service_list,
            interface_type="service_list",
            description="Show all services",
            examples=[
                "show services",
                "list all services",
                "display daemons"
            ],
            priority=9
        ))
        
        # Service control
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(start|stop|restart|enable|disable) (?:the )?([\w\s-]+) (?:service|daemon)?",
            handler=self._handle_service_control,
            interface_type="service_control",
            description="Control a service",
            examples=[
                "start nginx service",
                "stop docker",
                "restart ssh daemon"
            ],
            priority=10
        ))
    
    def _register_generic_commands(self):
        """Register generic UI generation commands"""
        
        # Create dashboard
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:create|make|build|show) (?:a |an )?dashboard (?:with |for )?([\w\s-]*)",
            handler=self._handle_create_dashboard,
            interface_type="dashboard",
            description="Create a custom dashboard",
            examples=[
                "create a dashboard",
                "build dashboard with dark theme",
                "make a monitoring dashboard"
            ],
            priority=8
        ))
        
        # Create form
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:create|make|build) (?:a |an )?form (?:for |to )?([\w\s-]*)",
            handler=self._handle_create_form,
            interface_type="form",
            description="Create a form interface",
            examples=[
                "create a form",
                "make form for user input",
                "build registration form"
            ],
            priority=8
        ))
        
        # Create custom interface
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:create|make|build|generate) (?:an? )?(?:interface|ui|screen) (?:for |to |with )?(.*)",
            handler=self._handle_create_custom,
            interface_type="custom",
            description="Create custom interface",
            examples=[
                "create interface for file management",
                "build ui with charts",
                "generate screen for data entry"
            ],
            priority=7
        ))
    
    def _register_navigation_commands(self):
        """Register navigation commands"""
        
        # Go to/Navigate
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:go to|navigate to|open|switch to) ([\w\s-]+)",
            handler=self._handle_navigation,
            interface_type="navigation",
            description="Navigate to a screen",
            examples=[
                "go to home",
                "navigate to settings",
                "switch to dashboard"
            ],
            priority=6
        ))
        
        # Back/Forward
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(go )?(back|forward|home)",
            handler=self._handle_navigation_simple,
            interface_type="navigation_simple",
            description="Simple navigation",
            examples=[
                "go back",
                "forward",
                "home"
            ],
            priority=5
        ))
    
    def _register_help_commands(self):
        """Register help and information commands"""
        
        # Help
        self.command_patterns.append(VoiceCommandPattern(
            pattern=r"(?:help|what can you do|show commands|list capabilities)",
            handler=self._handle_help,
            interface_type="help",
            description="Show help and available commands",
            examples=[
                "help",
                "what can you do",
                "show commands"
            ],
            priority=15  # High priority to catch help requests
        ))
    
    # === Command Handlers ===
    
    def _handle_package_search(self, match, context: Dict) -> Dict:
        """Handle package search command"""
        query = match.group(2).strip()
        result = self.package_interface.generate_search_results_ui(query)
        
        return {
            "success": True,
            "interface": result.get("interface"),
            "message": f"Found {result['results_count']} packages for '{query}'",
            "type": "package_search",
            "data": {"query": query, "results": result['results_count']}
        }
    
    def _handle_package_install(self, match, context: Dict) -> Dict:
        """Handle package installation command"""
        package_name = match.group(2).strip()
        
        # Generate installation UI
        result = self.package_interface.generate_package_details_ui(package_name)
        
        # Also prepare the actual install command
        install_result = self.package_interface.install_package(package_name, dry_run=True)
        
        return {
            "success": True,
            "interface": result.get("interface"),
            "message": f"Ready to install {package_name}",
            "type": "package_install",
            "data": {
                "package": package_name,
                "command": install_result.get("command")
            }
        }
    
    def _handle_package_remove(self, match, context: Dict) -> Dict:
        """Handle package removal command"""
        package_name = match.group(2).strip()
        
        # Generate removal UI
        result = self.package_interface.generate_package_details_ui(package_name)
        
        # Prepare removal command
        remove_result = self.package_interface.remove_package(package_name, dry_run=True)
        
        return {
            "success": True,
            "interface": result.get("interface"),
            "message": f"Ready to remove {package_name}",
            "type": "package_remove",
            "data": {
                "package": package_name,
                "command": remove_result.get("command")
            }
        }
    
    def _handle_package_manager(self, match, context: Dict) -> Dict:
        """Handle package manager display"""
        result = self.package_interface.generate_package_manager_ui()
        
        return {
            "success": True,
            "interface": result["interface"],
            "message": f"Package manager with {result['packages']} packages",
            "type": "package_manager",
            "data": {
                "total": result['packages'],
                "installed": result['installed']
            }
        }
    
    def _handle_config_editor(self, match, context: Dict) -> Dict:
        """Handle configuration editor"""
        result = self.config_editor.generate_editor_ui()
        
        return {
            "success": True,
            "interface": result["interface"],
            "message": f"Configuration editor with {result['section_count']} sections",
            "type": "config_editor"
        }
    
    def _handle_config_section(self, match, context: Dict) -> Dict:
        """Handle specific config section"""
        section = match.group(1).strip()
        result = self.config_editor.generate_section_editor(section)
        
        return {
            "success": True,
            "interface": result["interface"],
            "message": f"Editing {section} configuration",
            "type": "config_section",
            "data": {"section": section}
        }
    
    def _handle_system_monitor(self, match, context: Dict) -> Dict:
        """Handle system monitor display"""
        result = self.system_monitor.generate_dashboard_ui()
        
        return {
            "success": True,
            "interface": result["interface"],
            "message": f"System monitor with {result['metrics_count']} metrics",
            "type": "system_monitor",
            "data": {"metrics": result['metrics_count']}
        }
    
    def _handle_specific_metric(self, match, context: Dict) -> Dict:
        """Handle specific metric display"""
        metric_type = match.group(1).strip()
        result = self.system_monitor.generate_metric_detail_ui(metric_type)
        
        return {
            "success": True,
            "interface": result["interface"],
            "message": f"Showing {metric_type} metrics",
            "type": "specific_metric",
            "data": {"metric": metric_type}
        }
    
    def _handle_service_list(self, match, context: Dict) -> Dict:
        """Handle service listing"""
        result = self.service_manager.generate_service_dashboard_ui()
        
        return {
            "success": True,
            "interface": result["interface"],
            "message": f"Services: {result['running']} running, {result['stopped']} stopped",
            "type": "service_list",
            "data": {
                "total": result['services_count'],
                "running": result['running'],
                "stopped": result['stopped']
            }
        }
    
    def _handle_service_control(self, match, context: Dict) -> Dict:
        """Handle service control command"""
        action = match.group(1).strip()
        service = match.group(2).strip()
        
        # Generate service detail UI
        result = self.service_manager.generate_service_detail_ui(service)
        
        # Execute action (dry run)
        action_result = self.service_manager.execute_service_action(
            service, action, dry_run=True
        )
        
        return {
            "success": True,
            "interface": result.get("interface"),
            "message": f"Ready to {action} {service}",
            "type": "service_control",
            "data": {
                "service": service,
                "action": action,
                "command": action_result.get("message")
            }
        }
    
    def _handle_create_dashboard(self, match, context: Dict) -> Dict:
        """Handle dashboard creation"""
        specs = match.group(1).strip() if match.group(1) else ""
        request = f"Create a dashboard {specs}".strip()
        
        user_context = UserContext(
            user_id=context.get("user_id", "voice_user"),
            preferences=context.get("preferences", {})
        )
        
        interface = self.ui_builder.build_interface(request, user_context)
        
        return {
            "success": True,
            "interface": interface,
            "message": "Created custom dashboard",
            "type": "dashboard"
        }
    
    def _handle_create_form(self, match, context: Dict) -> Dict:
        """Handle form creation"""
        purpose = match.group(1).strip() if match.group(1) else ""
        request = f"Create a form {purpose}".strip()
        
        user_context = UserContext(
            user_id=context.get("user_id", "voice_user"),
            preferences=context.get("preferences", {})
        )
        
        interface = self.ui_builder.build_interface(request, user_context)
        
        return {
            "success": True,
            "interface": interface,
            "message": "Created form interface",
            "type": "form"
        }
    
    def _handle_create_custom(self, match, context: Dict) -> Dict:
        """Handle custom interface creation"""
        specs = match.group(1).strip() if match.group(1) else ""
        request = f"Create an interface {specs}".strip()
        
        user_context = UserContext(
            user_id=context.get("user_id", "voice_user"),
            preferences=context.get("preferences", {})
        )
        
        interface = self.ui_builder.build_interface(request, user_context)
        
        return {
            "success": True,
            "interface": interface,
            "message": "Created custom interface",
            "type": "custom"
        }
    
    def _handle_navigation(self, match, context: Dict) -> Dict:
        """Handle navigation command"""
        destination = match.group(1).strip()
        
        return {
            "success": True,
            "interface": None,
            "message": f"Navigating to {destination}",
            "type": "navigation",
            "data": {"destination": destination}
        }
    
    def _handle_navigation_simple(self, match, context: Dict) -> Dict:
        """Handle simple navigation"""
        direction = match.group(2) if match.group(2) else match.group(1)
        
        return {
            "success": True,
            "interface": None,
            "message": f"Going {direction}",
            "type": "navigation_simple",
            "data": {"direction": direction}
        }
    
    def _handle_help(self, match, context: Dict) -> Dict:
        """Handle help request"""
        # Generate help interface showing all commands
        help_text = self.generate_help_text()
        
        request = f"Create a help interface showing these commands: {help_text}"
        user_context = UserContext(user_id=context.get("user_id", "voice_user"))
        
        interface = self.ui_builder.build_interface(request, user_context)
        
        return {
            "success": True,
            "interface": interface,
            "message": "Here are the available commands",
            "type": "help",
            "data": {"commands": len(self.command_patterns)}
        }
    
    def process_voice_command(self, text: str, context: Dict = None) -> Dict:
        """Process a voice command text"""
        
        if context is None:
            context = {}
        
        # Try to match against registered patterns
        for pattern_obj in self.command_patterns:
            match = re.search(pattern_obj.pattern, text, re.IGNORECASE)
            if match:
                try:
                    result = pattern_obj.handler(match, context)
                    result["matched_pattern"] = pattern_obj.pattern
                    return result
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "message": f"Error processing command: {e}",
                        "type": "error"
                    }
        
        # No pattern matched - try generic UI generation
        return self._handle_generic_request(text, context)
    
    def _handle_generic_request(self, text: str, context: Dict) -> Dict:
        """Handle requests that don't match specific patterns"""
        
        user_context = UserContext(
            user_id=context.get("user_id", "voice_user"),
            preferences=context.get("preferences", {})
        )
        
        try:
            interface = self.ui_builder.build_interface(text, user_context)
            
            return {
                "success": True,
                "interface": interface,
                "message": "Generated interface from request",
                "type": "generic"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Could not understand the command",
                "type": "unknown"
            }
    
    def generate_help_text(self) -> str:
        """Generate help text listing all commands"""
        
        categories = {}
        
        # Group commands by interface type
        for pattern in self.command_patterns:
            category = pattern.interface_type.split('_')[0]
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                "description": pattern.description,
                "examples": pattern.examples
            })
        
        help_text = "Available voice commands:\n"
        for category, commands in categories.items():
            help_text += f"\n{category.upper()}:\n"
            for cmd in commands:
                help_text += f"  • {cmd['description']}\n"
                if cmd['examples']:
                    help_text += f"    Examples: {', '.join(cmd['examples'][:2])}\n"
        
        return help_text
    
    def list_all_commands(self) -> List[Dict]:
        """List all registered commands"""
        
        commands = []
        for pattern in self.command_patterns:
            commands.append({
                "type": pattern.interface_type,
                "description": pattern.description,
                "examples": pattern.examples,
                "priority": pattern.priority
            })
        
        return commands


def demo_voice_commands():
    """Demonstrate voice command processing"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        🎤 VOICE COMMANDS REGISTRY DEMO                             ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    registry = VoiceCommandRegistry()
    
    # Test various voice commands
    test_commands = [
        "show package manager",
        "search for firefox",
        "install vim",
        "open configuration",
        "show system monitor",
        "check cpu usage",
        "list services",
        "start nginx service",
        "create a dashboard with dark theme",
        "navigate to settings",
        "help"
    ]
    
    print(f"📝 Registered {len(registry.command_patterns)} command patterns\n")
    
    for command_text in test_commands:
        print(f"\n🎙️ Command: '{command_text}'")
        result = registry.process_voice_command(command_text)
        
        print(f"   ✅ Success: {result.get('success')}")
        print(f"   📋 Type: {result.get('type')}")
        print(f"   💬 Message: {result.get('message')}")
        
        if result.get('data'):
            print(f"   📊 Data: {result['data']}")
    
    # Show command categories
    print("\n\n📚 Command Categories:")
    print("-" * 40)
    
    categories = {}
    for pattern in registry.command_patterns:
        category = pattern.interface_type.split('_')[0]
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    for category, count in sorted(categories.items()):
        print(f"   {category.capitalize()}: {count} commands")
    
    print("""
═══════════════════════════════════════════════════════════════════════
✨ Voice Commands Successfully Registered!

Features:
• Pattern-based command matching with priorities
• Context-aware command processing
• Real NixOS operation integration
• Fallback to generic UI generation
• Comprehensive help system

Total Commands: {}
Categories: {}
═══════════════════════════════════════════════════════════════════════
    """.format(len(registry.command_patterns), len(categories)))


if __name__ == "__main__":
    demo_voice_commands()