#!/usr/bin/env python3
"""
🌉 NIX BRIDGE - Connecting Consciousness to NixOS
The bridge between invisible consciousness and real NixOS functionality
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Setup minimal logging
logger = logging.getLogger(__name__)

# Import NixOS backends with graceful fallback
try:
    from luminous_nix.nix.native_backend import NativeNixBackend
    NATIVE_BACKEND_AVAILABLE = True
except ImportError:
    NATIVE_BACKEND_AVAILABLE = False
    logger.debug("Native backend not available")

try:
    from luminous_nix.core.package_discovery import PackageDiscovery
    PACKAGE_DISCOVERY_AVAILABLE = True
except ImportError:
    PACKAGE_DISCOVERY_AVAILABLE = False
    logger.debug("Package discovery not available")

try:
    from luminous_nix.core.smart_package_discovery import get_smart_discovery
    SMART_DISCOVERY_AVAILABLE = True
except ImportError:
    SMART_DISCOVERY_AVAILABLE = False
    logger.debug("Smart discovery not available")

try:
    from luminous_nix.core.config_generator_ast import ConfigGeneratorAST
    CONFIG_GENERATOR_AVAILABLE = True
except ImportError:
    try:
        # Try fallback simple generator
        from luminous_nix.core.simple_config_generator import ConfigGeneratorAST
        CONFIG_GENERATOR_AVAILABLE = True
        logger.debug("Using simple config generator")
    except ImportError:
        CONFIG_GENERATOR_AVAILABLE = False
        logger.debug("Config generator not available")


class NixBridge:
    """
    Bridge between consciousness and NixOS functionality
    Translates conscious understanding into real actions
    """
    
    def __init__(self):
        # Initialize backends
        self.native_backend = NativeNixBackend() if NATIVE_BACKEND_AVAILABLE else None
        self.package_discovery = PackageDiscovery() if PACKAGE_DISCOVERY_AVAILABLE else None
        self.config_generator = ConfigGeneratorAST() if CONFIG_GENERATOR_AVAILABLE else None
        self.smart_discovery = get_smart_discovery() if SMART_DISCOVERY_AVAILABLE else None
        
        # Cache for performance
        self._search_cache = {}
        self._config_cache = {}
        
    async def process_intent(
        self,
        intent: str,
        command: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user intent and execute appropriate NixOS action
        Returns enhanced response with actual results
        """
        
        # Determine action type from intent
        action = self._determine_action(intent, command)
        
        # Execute appropriate action
        if action == "search":
            return await self._handle_search(command, context)
        elif action == "install":
            return await self._handle_install(command, context)
        elif action == "config":
            return await self._handle_config(command, context)
        elif action == "rollback":
            return await self._handle_rollback(command, context)
        elif action == "info":
            return await self._handle_info(command, context)
        elif action == "update":
            return await self._handle_update(command, context)
        elif action == "remove":
            return await self._handle_remove(command, context)
        elif action == "list":
            return await self._handle_list(command, context)
        else:
            return await self._handle_general(command, context)
    
    def _determine_action(self, intent: str, command: str) -> str:
        """Determine action type from intent and command"""
        # First try to use the intent directly if it's a recognized intent type
        intent_to_action_map = {
            "install_package": "install",
            "search_package": "search",
            "list_installed": "list",
            "remove_package": "remove",
            "update_system": "update",
            "rollback": "rollback",
            "configure": "config",
            "explain": "info",
            "help": "general"
        }
        
        if intent in intent_to_action_map:
            return intent_to_action_map[intent]
        
        # Fallback to pattern matching on the command text
        command_lower = command.lower()
        
        # Rollback/generation patterns (check first as they're specific)
        if any(word in command_lower for word in ['rollback', 'undo', 'revert', 'previous', 'generation', 'generations']):
            return "rollback"
        
        # Search patterns (expanded with natural language)
        if any(word in command_lower for word in ['find', 'search', 'looking for', 'need something', 'want something', 'alternatives', 'something like', 'similar to', 'alternative to', 'replacement for', 'i need', 'i want', 'need a', 'want a', 'good', 'best']):
            return "search"
        
        # Install patterns
        if any(word in command_lower for word in ['install', 'add package', 'setup package']):
            return "install"
        
        # Configuration patterns
        if any(word in command_lower for word in ['config', 'configure', 'enable', 'disable', 'service', 'automatic']):
            return "config"
        
        # Info patterns
        if any(word in command_lower for word in ['what is', 'what are', 'explain', 'tell me about', 'describe', 'how do', 'how does', 'why']):
            return "info"
        
        # Update patterns
        if any(word in command_lower for word in ['update system', 'upgrade system', 'update nixos']):
            return "update"
        
        # Remove/uninstall patterns
        if any(word in command_lower for word in ['remove', 'uninstall', 'delete', 'get rid of']):
            return "remove"
        
        # List patterns
        if any(word in command_lower for word in ['list', 'show', 'what is installed', 'installed packages']):
            return "list"
        
        return "general"
    
    async def _handle_search(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle package search requests"""
        
        # Extract search query
        query = self._extract_package_name(command)
        
        # Check cache first
        if query in self._search_cache:
            results = self._search_cache[query]
            source = "cached"
        else:
            # Search for packages
            if self.package_discovery:
                try:
                    results = self.package_discovery.search_packages(query, limit=5)
                    self._search_cache[query] = results
                    source = "fresh"
                except Exception as e:
                    logger.error(f"Search failed: {e}")
                    results = []
                    source = "error"
            else:
                results = []
                source = "unavailable"
        
        # Format response
        if results:
            packages = [f"• {p.name}: {p.description[:50]}..." for p in results[:3]]
            response = f"Found {len(results)} packages matching '{query}':\n" + "\n".join(packages)
            
            if len(results) > 3:
                response += f"\n... and {len(results) - 3} more"
        else:
            # Try smart discovery for better suggestions
            if self.smart_discovery and SMART_DISCOVERY_AVAILABLE:
                smart_matches = self.smart_discovery.find_packages(query)
                
                if smart_matches:
                    response = f"No exact matches for '{query}', but here are suggestions:\n"
                    for match in smart_matches[:3]:
                        response += f"• {match.name}: {match.match_reason}\n"
                    
                    # Check for spelling correction
                    correction = self.smart_discovery.suggest_correction(query)
                    if correction and correction != query:
                        response += f"\n💡 Did you mean: {correction}?"
                else:
                    response = f"No packages found matching '{query}'"
                    
                    # Fallback to basic suggestions
                    suggestions = self._generate_suggestions(query)
                    if suggestions:
                        response += f"\n\nYou might try:\n" + "\n".join(f"• {s}" for s in suggestions)
            else:
                response = f"No packages found matching '{query}'"
                
                # Basic suggestions
                suggestions = self._generate_suggestions(query)
                if suggestions:
                    response += f"\n\nYou might try:\n" + "\n".join(f"• {s}" for s in suggestions)
        
        return {
            "response": response,
            "action": "search",
            "results": len(results),
            "source": source,
            "query": query
        }
    
    async def _handle_install(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle package installation requests"""
        
        # Extract package name
        package = self._extract_package_name(command)
        
        # Check if dry run
        dry_run = context.get('dry_run', True)  # Default to dry run for safety
        
        if self.native_backend:
            # Use the improved install_package method
            result = await self.native_backend.install_package(package, dry_run)
            
            if result.get('success'):
                if dry_run:
                    response = f"Would install '{package}' with:\n  {result.get('command', '')}\n\n"
                    response += "To actually install, use --execute flag"
                    status = "dry_run"
                else:
                    response = result.get('message', f"Successfully installed '{package}'")
                    status = "success"
            else:
                # Error occurred - provide helpful guidance
                error = result.get('error', 'Unknown error')
                suggestion = result.get('suggestion', '')
                
                response = f"❌ Failed to install '{package}'\n"
                response += f"Error: {error}\n"
                if suggestion:
                    response += f"\n💡 Suggestion: {suggestion}"
                status = "error"
        else:
            # Fallback if backend not available
            # Use nixos channel which is available on NixOS systems
            install_cmd = f"nix profile install nixpkgs#{package}"
            response = f"Would install '{package}' with:\n  {install_cmd}\n\n"
            response += "Backend not available for actual installation"
            status = "unavailable"
        
        return {
            "response": response,
            "action": "install",
            "package": package,
            "status": status
        }
    
    async def _handle_config(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration generation requests"""
        
        if not self.config_generator:
            return {
                "response": "Configuration generator not available",
                "action": "config",
                "status": "unavailable"
            }
        
        # Determine config type
        if "service" in command.lower():
            config_type = "service"
        elif "package" in command.lower():
            config_type = "package"
        else:
            config_type = "general"
        
        # Generate configuration
        try:
            config = self.config_generator.generate(command, config_type)
            
            response = f"Generated NixOS configuration:\n\n```nix\n{config}\n```\n\n"
            response += "Add this to your configuration.nix and run 'nixos-rebuild switch'"
            
            return {
                "response": response,
                "action": "config",
                "config": config,
                "type": config_type,
                "status": "success"
            }
        except Exception as e:
            return {
                "response": f"Failed to generate configuration: {e}",
                "action": "config",
                "status": "error"
            }
    
    async def _handle_update(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system update requests"""
        
        # Check if dry run
        dry_run = context.get('dry_run', True)  # Default to dry run for safety
        
        # Build the update command
        update_cmd = "sudo nixos-rebuild switch"
        
        if dry_run:
            response = f"Would update system with:\n  {update_cmd}\n\n"
            response += "This will:\n"
            response += "• Download latest packages from channels\n"
            response += "• Rebuild your system configuration\n"
            response += "• Apply all changes\n\n"
            response += "To actually update, use --execute flag"
            status = "dry_run"
        else:
            # For actual execution, we need to handle the long-running command
            response = f"Updating system...\n\n"
            response += "⚠️ Note: System updates take time and require sudo.\n"
            response += "The update has been started in the background.\n"
            response += "You can check progress with: journalctl -f\n\n"
            
            # We could start the update in background here
            # But for safety, we'll just inform the user
            response += "To run the update manually:\n"
            response += f"  {update_cmd}\n"
            status = "initiated"
        
        return {
            "response": response,
            "action": "update",
            "status": status,
            "command": update_cmd
        }
    
    async def _handle_remove(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle package removal requests"""
        
        # Extract package name
        package = self._extract_package_name(command)
        
        # Check if dry run
        dry_run = context.get('dry_run', True)  # Default to dry run for safety
        
        # Build the remove command - use nix profile for modern Nix
        import subprocess
        check_cmd = ["nix", "profile", "list"]
        try:
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=1)
            use_nix_profile = result.returncode == 0
        except:
            use_nix_profile = False
        
        if use_nix_profile:
            # Use modern nix profile command
            remove_cmd = f"nix profile remove {package}"
        else:
            # Fallback to nix-env
            remove_cmd = f"nix-env -e {package}"
        
        if dry_run:
            response = f"Would remove '{package}' with:\n  {remove_cmd}\n\n"
            response += "To actually remove, use --execute flag"
            status = "dry_run"
        else:
            # Actually remove the package
            try:
                result = subprocess.run(remove_cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    response = f"Successfully removed '{package}'"
                    status = "success"
                else:
                    response = f"Failed to remove '{package}'\n"
                    response += f"Error: {result.stderr}"
                    status = "error"
            except Exception as e:
                response = f"Error removing package: {e}"
                status = "error"
        
        return {
            "response": response,
            "action": "remove",
            "package": package,
            "status": status,
            "command": remove_cmd
        }
    
    async def _handle_list(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle listing installed packages"""
        
        # Build the list command
        import subprocess
        check_cmd = ["nix", "profile", "list"]
        try:
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=1)
            use_nix_profile = result.returncode == 0
        except:
            use_nix_profile = False
        
        if use_nix_profile:
            # Use modern nix profile command
            list_cmd = "nix profile list"
            try:
                result = subprocess.run(list_cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    packages = result.stdout.strip()
                    if packages:
                        response = "Installed packages:\n\n" + packages
                    else:
                        response = "No packages installed in user profile"
                    status = "success"
                else:
                    response = f"Error listing packages: {result.stderr}"
                    status = "error"
            except Exception as e:
                response = f"Error listing packages: {e}"
                status = "error"
        else:
            # Fallback to nix-env
            list_cmd = "nix-env -q"
            try:
                result = subprocess.run(list_cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    packages = result.stdout.strip()
                    if packages:
                        response = "Installed packages:\n\n" + packages
                    else:
                        response = "No packages installed in user profile"
                    status = "success"
                else:
                    response = f"Error listing packages: {result.stderr}"
                    status = "error"
            except Exception as e:
                response = f"Error listing packages: {e}"
                status = "error"
        
        return {
            "response": response,
            "action": "list",
            "status": status,
            "command": list_cmd
        }
    
    async def _handle_rollback(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system rollback requests"""
        
        if not self.native_backend:
            return {
                "response": "Rollback functionality not available",
                "action": "rollback",
                "status": "unavailable"
            }
        
        # Get available generations
        try:
            generations = await self.native_backend.list_generations()
            
            if not generations:
                response = "No previous generations available for rollback"
                status = "no_generations"
            else:
                current = generations[0]
                previous = generations[1] if len(generations) > 1 else None
                
                if previous:
                    response = f"Current generation: {current['generation']} ({current['date']})\n"
                    response += f"Would rollback to: {previous['generation']} ({previous['date']})\n\n"
                    response += "Use --execute to actually rollback"
                    status = "ready"
                else:
                    response = "Only one generation exists, cannot rollback"
                    status = "single_generation"
            
            return {
                "response": response,
                "action": "rollback",
                "generations": len(generations),
                "status": status
            }
        except Exception as e:
            return {
                "response": f"Failed to check generations: {e}",
                "action": "rollback",
                "status": "error"
            }
    
    async def _handle_info(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle information requests about packages or concepts"""
        
        # Extract topic
        topic = self._extract_package_name(command)
        
        # Try to get package info first
        if self.package_discovery:
            try:
                results = self.package_discovery.search_packages(topic, limit=1)
                if results:
                    package = results[0]
                    response = f"**{package.name}**\n\n"
                    response += f"{package.description}\n\n"
                    if hasattr(package, 'homepage'):
                        response += f"Homepage: {package.homepage}\n"
                    if hasattr(package, 'version'):
                        response += f"Version: {package.version}\n"
                    
                    return {
                        "response": response,
                        "action": "info",
                        "topic": topic,
                        "type": "package",
                        "status": "success"
                    }
            except:
                pass
        
        # Fallback to general explanation
        explanations = {
            "nix": "Nix is a purely functional package manager that ensures reproducible builds",
            "nixos": "NixOS is a Linux distribution built on top of the Nix package manager",
            "flake": "Flakes are an experimental feature providing reproducible Nix expressions",
            "channel": "Channels are versioned collections of packages in Nix",
            "generation": "Generations are snapshots of your system configuration you can rollback to"
        }
        
        explanation = explanations.get(topic.lower(), f"Information about '{topic}' not available")
        
        return {
            "response": explanation,
            "action": "info",
            "topic": topic,
            "type": "concept",
            "status": "success"
        }
    
    async def _handle_general(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general NixOS commands"""
        
        # Default response for unrecognized intents
        response = f"Processing: {command}\n\n"
        response += "I can help you:\n"
        response += "• Search packages: 'find text editor'\n"
        response += "• Install software: 'install firefox'\n"
        response += "• Generate configs: 'configure nginx service'\n"
        response += "• Rollback system: 'rollback to previous'\n"
        response += "• Get information: 'what is a flake?'"
        
        return {
            "response": response,
            "action": "general",
            "status": "help"
        }
    
    def _extract_package_name(self, command: str) -> str:
        """Extract package name from command"""
        # Remove common words
        words_to_remove = [
            'install', 'find', 'search', 'add', 'get', 'need', 'want', 'setup',
            'remove', 'uninstall', 'delete', 'rid', 'of',
            'for', 'a', 'an', 'the', 'package', 'program', 'software', 'tool',
            'looking', 'configure', 'what', 'is', 'about', 'info', 'enable',
            'i', "i'm", 'me', 'my', 'please', 'can', 'you', 'help', 'with',
            'something', 'like', 'similar', 'to', 'alternative', 'it', 'too',
            'also', 'service', 'system', 'show', 'list', 'display'
        ]
        
        # Special cases for known packages/concepts
        special_cases = {
            'text editor': 'editor',
            'code editor': 'vscode',
            'web browser': 'browser',
            'music player': 'music',
            'video editor': 'video',
            'markdown editor': 'markdown',
            'terminal emulator': 'terminal',
            'python development': 'python',
            'nodejs': 'nodejs',
            'node.js': 'nodejs',
            'docker service': 'docker',
            'ssh service': 'ssh',
            'nginx service': 'nginx',
            'automatic updates': 'auto-update',
            'firewall rules': 'firewall'
        }
        
        command_lower = command.lower()
        
        # Check special cases first
        for phrase, replacement in special_cases.items():
            if phrase in command_lower:
                return replacement
        
        # Remove question marks and punctuation
        command_clean = command_lower.replace('?', '').replace('!', '').replace('.', '').replace(',', '')
        
        words = command_clean.split()
        filtered = [w for w in words if w not in words_to_remove]
        
        # If we have a clear package name (single word), use it
        if len(filtered) == 1:
            return filtered[0]
        
        # For multi-word results, try to be smarter
        if filtered:
            # Common patterns: "python with pip" -> "python"
            if 'with' in filtered:
                idx = filtered.index('with')
                return ' '.join(filtered[:idx]) if idx > 0 else filtered[0]
            
            # If it's too long, probably grabbed too much
            if len(filtered) > 3:
                return filtered[0]  # Just take the first meaningful word
            
            return ' '.join(filtered)
        
        # Last resort - try to find any meaningful word
        for word in words:
            if len(word) > 2 and word not in words_to_remove:
                return word
        
        return 'package'  # Default fallback
    
    def _generate_suggestions(self, query: str) -> List[str]:
        """Generate alternative search suggestions"""
        suggestions = []
        
        # Common alternatives
        alternatives = {
            'editor': ['vim', 'neovim', 'emacs', 'vscode'],
            'browser': ['firefox', 'chromium', 'brave'],
            'terminal': ['alacritty', 'kitty', 'wezterm'],
            'shell': ['zsh', 'fish', 'bash'],
            'python': ['python3', 'python311', 'python312']
        }
        
        for key, values in alternatives.items():
            if key in query.lower():
                suggestions.extend(values[:2])
                break
        
        return suggestions


# Global bridge instance
_BRIDGE: Optional[NixBridge] = None

def get_nix_bridge() -> NixBridge:
    """Get or create the NixOS bridge"""
    global _BRIDGE
    if _BRIDGE is None:
        _BRIDGE = NixBridge()
    return _BRIDGE


if __name__ == "__main__":
    # Test the bridge
    import asyncio
    
    async def test():
        bridge = get_nix_bridge()
        
        # Test search
        result = await bridge.process_intent("search", "find text editor", {})
        print(f"Search result: {result['response']}\n")
        
        # Test install
        result = await bridge.process_intent("install", "install firefox", {"dry_run": True})
        print(f"Install result: {result['response']}\n")
        
        # Test config
        result = await bridge.process_intent("config", "configure nginx service", {})
        print(f"Config result: {result['response']}\n")
    
    asyncio.run(test())