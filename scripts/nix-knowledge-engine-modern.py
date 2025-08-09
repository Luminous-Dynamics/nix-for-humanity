#!/usr/bin/env python3
"""
from typing import Optional
NixOS Knowledge Engine - Modern Commands Version
Uses current best practices: nix profile, Home Manager, etc.
"""

import json
import subprocess
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import sys
import os

# Import the intelligent cache manager
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from package_cache_manager import IntelligentPackageCache
except ImportError:
    IntelligentPackageCache = None

class ModernNixOSKnowledgeEngine:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.db_path = self.base_dir / "nixos_knowledge_modern.db"
        self.init_db()
        
        # Initialize intelligent cache
        self.cache_manager = IntelligentPackageCache() if IntelligentPackageCache else None
        
        # Common package mappings
        self.package_aliases = {
            'firefox': 'firefox',
            'chrome': 'google-chrome',
            'chromium': 'chromium',
            'vscode': 'vscode',
            'code': 'vscode',
            'vim': 'vim',
            'neovim': 'neovim',
            'emacs': 'emacs',
            'python': 'python3',
            'python3': 'python311',
            'nodejs': 'nodejs',
            'node': 'nodejs',
            'docker': 'docker',
            'git': 'git',
            'htop': 'htop',
            'tmux': 'tmux',
            'zsh': 'zsh',
            'fish': 'fish',
            'rust': 'rustc cargo',
            'go': 'go',
            'java': 'openjdk'
        }
        
        # Deprecated command mappings
        self.deprecated_commands = {
            'nix-env -i': 'Use: nix profile install',
            'nix-env -iA': 'Use: nix profile install',
            'nix-env': 'nix-env is deprecated. Use: nix profile',
            'nix-env -e': 'Use: nix profile remove',
            'nix-env -u': 'Use: nix profile upgrade',
            'nix-env --list-generations': 'Use: nix profile history',
            'nix-channel --update': 'Use: nix flake update (with flakes) or home-manager switch',
        }
        
        # Modern installation methods
        self.install_methods = {
            'declarative': {
                'name': 'System Configuration (Recommended)',
                'description': 'Add to configuration.nix for system-wide installation',
                'command': 'Edit /etc/nixos/configuration.nix',
                'example': 'environment.systemPackages = with pkgs; [ {package} ];',
                'requires_sudo': True
            },
            'home-manager': {
                'name': 'Home Manager (User-level, No Sudo)',
                'description': 'User-specific installation without root access',
                'command': 'Edit ~/.config/home-manager/home.nix',
                'example': 'home.packages = with pkgs; [ {package} ];',
                'requires_sudo': False
            },
            'nix-profile': {
                'name': 'Nix Profile (Modern Imperative)',
                'description': 'Quick installation with modern tooling',
                'command': 'nix profile install nixpkgs#{package}',
                'example': 'nix profile install nixpkgs#{package}',
                'requires_sudo': False
            },
            'shell': {
                'name': 'Temporary Shell',
                'description': 'Try without installing',
                'command': 'nix-shell -p {package}',
                'example': 'nix-shell -p {package}',
                'requires_sudo': False
            }
        }
        
    def init_db(self):
        """Initialize knowledge database with modern commands"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Solutions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY,
                intent TEXT NOT NULL,
                category TEXT NOT NULL,
                solution TEXT NOT NULL,
                example TEXT,
                explanation TEXT,
                related TEXT,
                requires_sudo BOOLEAN DEFAULT 0
            )
        ''')
        
        # Common problems table
        c.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY,
                symptom TEXT NOT NULL,
                cause TEXT NOT NULL,
                solution TEXT NOT NULL,
                prevention TEXT
            )
        ''')
        
        # Progress indicators table
        c.execute('''
            CREATE TABLE IF NOT EXISTS progress_messages (
                id INTEGER PRIMARY KEY,
                operation TEXT NOT NULL,
                message TEXT NOT NULL,
                estimated_time TEXT
            )
        ''')
        
        # Initialize with modern solutions
        self._populate_modern_knowledge(c)
        
        conn.commit()
        conn.close()
        
    def _populate_modern_knowledge(self, cursor):
        """Populate with modern NixOS best practices"""
        solutions = [
            # Modern package management
            ('install_package', 'package', 'Use declarative installation or modern nix profile', 
             'nix profile install nixpkgs#firefox', 
             'Modern nix profile replaces deprecated nix-env', 
             'search_package,remove_package', False),
            
            ('search_package', 'package', 'Search using nix search or online', 
             'nix search nixpkgs firefox', 
             'Use search.nixos.org for web interface', 
             'install_package', False),
            
            ('remove_package', 'package', 'Remove packages with nix profile', 
             'nix profile remove firefox', 
             'For declarative, remove from configuration.nix', 
             'install_package', False),
            
            ('list_packages', 'package', 'List installed packages in profile', 
             'nix profile list', 
             'Shows all packages installed in current profile', 
             'remove_package,install_package', False),
            
            # System management without sudo when possible
            ('update_system', 'system', 'Update system or user packages', 
             'home-manager switch', 
             'Use Home Manager for user packages without sudo', 
             'rollback_system', False),
            
            ('update_system_sudo', 'system', 'Update full system configuration', 
             'sudo nixos-rebuild switch', 
             'Only needed for system-wide changes', 
             'rollback_system', True),
            
            ('rollback_system', 'system', 'Rollback to previous generation', 
             'nix profile rollback', 
             'User packages rollback without sudo', 
             'update_system,list_generations', False),
            
            ('list_generations', 'system', 'Show profile history', 
             'nix profile history', 
             'Shows all generations of current profile', 
             'rollback_system', False),
            
            # Home Manager specific
            ('setup_home_manager', 'home-manager', 'Initial Home Manager setup', 
             'nix-channel --add https://github.com/nix-community/home-manager/archive/master.tar.gz home-manager', 
             'One-time setup for user-level package management', 
             'install_package', False),
            
            # Network
            ('fix_wifi', 'network', 'Enable NetworkManager or check hardware', 
             'networking.networkmanager.enable = true;', 
             'Most WiFi issues are solved by enabling NetworkManager', 
             'network_status', True),
            
            # Services
            ('enable_service', 'service', 'Add to configuration.nix services section', 
             'services.openssh.enable = true;', 
             'Services are managed declaratively in NixOS', 
             'disable_service,list_services', True),
        ]
        
        for solution in solutions:
            cursor.execute('''
                INSERT OR REPLACE INTO solutions 
                (intent, category, solution, example, explanation, related, requires_sudo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', solution)
            
        # Common problems
        problems = [
            ('command not found', 'Package not in PATH', 
             'Install package with nix profile install or use nix-shell', 
             'Use declarative installation when possible'),
             
            ('read-only file system', 'Trying to modify /etc directly', 
             'Edit configuration.nix instead', 
             'NixOS manages /etc through configuration'),
             
            ('infinite recursion', 'Circular dependency in config', 
             'Check for recursive definitions', 
             'Use mkForce or mkDefault for overrides'),
             
            ('nix-env deprecated warning', 'Using old nix-env commands', 
             'Switch to nix profile commands', 
             'nix profile is the modern replacement'),
        ]
        
        for problem in problems:
            cursor.execute('''
                INSERT OR REPLACE INTO problems
                (symptom, cause, solution, prevention)
                VALUES (?, ?, ?, ?)
            ''', problem)
            
        # Progress messages
        progress_messages = [
            ('search', '🔍 Searching NixOS packages...', '2-5 seconds'),
            ('install', '📦 Installing package...', '10-60 seconds'),
            ('rebuild', '🔄 Rebuilding system configuration...', '1-5 minutes'),
            ('update', '⬆️ Updating channels/flakes...', '30-90 seconds'),
            ('download', '⬇️ Downloading dependencies...', 'Varies by package size'),
            ('list', '📋 Loading profile information', '1-2 seconds'),
            ('remove', '🗑️ Removing package', '2-5 seconds'),
            ('channel update', '📡 Fetching channel updates', '30-60 seconds'),
            ('system rebuild', '🔧 Rebuilding system configuration', '2-10 minutes'),
            ('Home Manager update', '🏠 Updating user packages', '1-3 minutes'),
            ('profile update', '📦 Upgrading profile packages', '1-5 minutes'),
        ]
        
        for operation, message, time in progress_messages:
            cursor.execute('''
                INSERT OR REPLACE INTO progress_messages
                (operation, message, estimated_time)
                VALUES (?, ?, ?)
            ''', (operation, message, time))
    
    def check_deprecated_command(self, query: str) -> Optional[str]:
        """Check if query contains deprecated commands"""
        query_lower = query.lower()
        for old_cmd, suggestion in self.deprecated_commands.items():
            if old_cmd in query_lower:
                return f"⚠️ Note: '{old_cmd}' is deprecated. {suggestion}"
        return None
    
    def extract_intent(self, query: str) -> Dict:
        """Extract intent from natural language query"""
        query_lower = query.lower()
        
        # Check for "without sudo" preference
        prefer_no_sudo = 'without sudo' in query_lower or 'no sudo' in query_lower
        
        # List patterns (check before install to avoid confusion with "list" as package)
        if (any(word in query_lower for word in ['list', 'show', 'what']) and 
            any(word in query_lower for word in ['installed', 'packages', 'profile'])):
            return {
                'action': 'list_packages',
                'query': query
            }
        
        # Installation patterns
        elif any(word in query_lower for word in ['install', 'get', 'need', 'want', 'set up']):
            # Extract package name
            package = None
            for alias, pkg in self.package_aliases.items():
                if alias in query_lower:
                    package = pkg
                    break
            
            if not package:
                # Try to extract any word that might be a package
                words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9-]+\b', query)
                for word in words:
                    if word not in ['i', 'want', 'need', 'install', 'get', 'the', 'a', 'an', 'without', 'sudo', 'no']:
                        package = word.lower()
                        break
                        
            return {
                'action': 'install_package',
                'package': package,
                'query': query,
                'prefer_no_sudo': prefer_no_sudo
            }
            
        # Search patterns
        elif any(word in query_lower for word in ['search', 'find', 'look for', 'is there']):
            # Extract search term
            package = None
            for alias, pkg in self.package_aliases.items():
                if alias in query_lower:
                    package = pkg
                    break
            
            if not package:
                # Try to extract any word that might be a search term
                words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9-]+\b', query)
                for word in words:
                    if word not in ['i', 'want', 'search', 'find', 'look', 'for', 'is', 'there', 'the', 'a', 'an']:
                        package = word.lower()
                        break
            
            return {
                'action': 'search_package',
                'package': package,
                'query': query
            }
            
        # Update patterns
        elif any(word in query_lower for word in ['update', 'upgrade']):
            return {
                'action': 'update_system' if prefer_no_sudo else 'update_system_sudo',
                'query': query,
                'prefer_no_sudo': prefer_no_sudo
            }
            
        # Home Manager patterns
        elif 'home manager' in query_lower or 'home-manager' in query_lower:
            if 'setup' in query_lower or 'install' in query_lower:
                return {
                    'action': 'setup_home_manager',
                    'query': query
                }
            else:
                return {
                    'action': 'update_system',
                    'query': query,
                    'prefer_no_sudo': True
                }
            
        # WiFi/Network patterns
        elif any(word in query_lower for word in ['wifi', 'wi-fi', 'internet', 'network']):
            return {
                'action': 'fix_wifi',
                'query': query
            }
            
        # Remove patterns
        elif any(word in query_lower for word in ['remove', 'uninstall', 'delete']):
            # Extract package name
            package = None
            for alias, pkg in self.package_aliases.items():
                if alias in query_lower:
                    package = pkg
                    break
            
            if not package:
                # Try to extract any word that might be a package
                words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9-]+\b', query)
                for word in words:
                    if word not in ['i', 'want', 'remove', 'uninstall', 'delete', 'the', 'a', 'an']:
                        package = word.lower()
                        break
                        
            return {
                'action': 'remove_package',
                'package': package,
                'query': query
            }
        
        # Flake patterns
        elif 'flake' in query_lower:
            if any(word in query_lower for word in ['create', 'make', 'generate']):
                # Extract description
                description = query
                for word in ['create', 'make', 'generate', 'flake', 'a', 'for']:
                    description = description.replace(word, '').strip()
                return {
                    'action': 'create_flake',
                    'description': description or query,
                    'query': query
                }
            elif any(word in query_lower for word in ['validate', 'check', 'verify']):
                return {
                    'action': 'validate_flake',
                    'query': query
                }
            elif 'convert' in query_lower:
                return {
                    'action': 'convert_flake',
                    'query': query
                }
            elif any(word in query_lower for word in ['show', 'info', 'describe']):
                return {
                    'action': 'show_flake_info',
                    'query': query
                }
        
        # Configuration generation patterns
        elif any(word in query_lower for word in ['generate', 'create', 'make', 'build']) and \
             any(word in query_lower for word in ['config', 'configuration']):
            # Extract description more carefully using regex
            import re
            # Pattern to extract everything after config generation keywords
            pattern = r'(?:generate|create|make|build)\s+(?:me\s+)?(?:a\s+)?(?:config|configuration)\s+(?:for\s+)?(.+)'
            match = re.search(pattern, query_lower)
            if match:
                description = match.group(1).strip()
            # Also handle "make me a X configuration/config"
            elif re.search(r'(?:make|create|build)\s+(?:me\s+)?(?:a\s+)?(.+?)\s+(?:config|configuration)', query_lower):
                match = re.search(r'(?:make|create|build)\s+(?:me\s+)?(?:a\s+)?(.+?)\s+(?:config|configuration)', query_lower)
                description = match.group(1).strip()
            else:
                # Fallback: just remove the action words
                description = query_lower
                for word in ['generate', 'create', 'make', 'build']:
                    description = re.sub(r'\b' + word + r'\b', '', description)
                description = re.sub(r'\b(?:a|me)\s+(?:config|configuration)\b', '', description)
                description = re.sub(r'\s+', ' ', description).strip()
            
            return {
                'action': 'generate_config',
                'description': description or query,
                'query': query
            }
        
        # Generation patterns (system generations, not config generation)
        elif any(word in query_lower for word in ['generation', 'rollback', 'previous', 'undo', 'history']):
            if 'list' in query_lower or 'show' in query_lower or 'history' in query_lower:
                return {
                    'action': 'list_generations',
                    'query': query
                }
            else:
                return {
                    'action': 'rollback_system',
                    'query': query
                }
            
        # Service patterns
        elif any(word in query_lower for word in ['service', 'enable', 'start', 'systemd']):
            return {
                'action': 'enable_service',
                'query': query
            }
            
        # Default
        return {
            'action': 'unknown',
            'query': query
        }
    
    def get_solution(self, intent: Dict) -> Dict:
        """Get modern solution for intent from knowledge base"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        action = intent.get('action', 'unknown')
        prefer_no_sudo = intent.get('prefer_no_sudo', False)
        
        # Fetch solution
        if prefer_no_sudo and action == 'update_system_sudo':
            action = 'update_system'
            
        c.execute('''
            SELECT solution, example, explanation, related, requires_sudo
            FROM solutions
            WHERE intent = ?
        ''', (action,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            # Special handling for generate_config
            if action == 'generate_config':
                return {
                    'found': True,
                    'solution': 'Generate a NixOS configuration file',
                    'example': f'ask-nix config generate "{intent.get("description", "web server with nginx")}"',
                    'explanation': 'I can generate NixOS configurations from natural language descriptions',
                    'related': ['configuration.nix', 'nixos-rebuild'],
                    'requires_sudo': False
                }
            
            # Special handling for flake operations
            elif action == 'create_flake':
                return {
                    'found': True,
                    'solution': 'Create a Nix flake for development environment',
                    'example': f'ask-nix flake create "{intent.get("description", "python development environment")}"',
                    'explanation': 'I can create Nix flakes from natural language descriptions for development environments',
                    'related': ['flake.nix', 'nix develop', 'nix flake'],
                    'requires_sudo': False
                }
            elif action == 'validate_flake':
                return {
                    'found': True,
                    'solution': 'Validate a flake.nix file',
                    'example': 'ask-nix flake validate',
                    'explanation': 'Check if your flake.nix is syntactically correct and well-formed',
                    'related': ['flake.nix', 'nix flake check'],
                    'requires_sudo': False
                }
            elif action == 'convert_flake':
                return {
                    'found': True,
                    'solution': 'Convert shell.nix to flake.nix',
                    'example': 'ask-nix flake convert',
                    'explanation': 'Automatically convert traditional Nix files to the modern flake format',
                    'related': ['shell.nix', 'default.nix', 'flake.nix'],
                    'requires_sudo': False
                }
            elif action == 'show_flake_info':
                return {
                    'found': True,
                    'solution': 'Show information about a flake',
                    'example': 'ask-nix flake info',
                    'explanation': 'Display description, inputs, outputs, and available dev shells',
                    'related': ['flake.nix', 'nix flake metadata'],
                    'requires_sudo': False
                }
            
            return {
                'found': False,
                'suggestion': 'I don\'t understand that yet. Try asking about installing packages, updating the system, or fixing WiFi.'
            }
            
        solution, example, explanation, related, requires_sudo = result
        
        # Customize for specific package if applicable
        if action == 'install_package' and intent.get('package'):
            package = intent['package']
            
            # Filter methods based on sudo preference
            methods = []
            for key, method in self.install_methods.items():
                if prefer_no_sudo and method.get('requires_sudo'):
                    continue
                methods.append({
                    'type': key,
                    'name': method['name'],
                    'description': method['description'],
                    'command': method['command'].format(package=package),
                    'example': method['example'].format(package=package),
                    'requires_sudo': method.get('requires_sudo', False)
                })
            
            # Sort to prioritize no-sudo methods
            methods.sort(key=lambda x: x['requires_sudo'])
            
            return {
                'found': True,
                'solution': solution,
                'methods': methods,
                'explanation': explanation,
                'package': package,
                'related': related.split(',') if related else [],
                'prefer_no_sudo': prefer_no_sudo
            }
            
        return {
            'found': True,
            'solution': solution,
            'example': example,
            'explanation': explanation,
            'related': related.split(',') if related else [],
            'requires_sudo': bool(requires_sudo)
        }
    
    def get_progress_message(self, operation: str) -> Dict:
        """Get progress indicator for operation"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT message, estimated_time
            FROM progress_messages
            WHERE operation = ?
        ''', (operation,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'message': result[0],
                'estimated_time': result[1]
            }
        
        return {
            'message': '⏳ Processing...',
            'estimated_time': 'Unknown'
        }
    
    def format_response(self, intent: Dict, solution: Dict) -> str:
        """Format solution as natural response with modern commands"""
        # Check for deprecated commands first
        deprecated_warning = self.check_deprecated_command(intent['query'])
        
        if not solution['found']:
            return solution['suggestion']
            
        response = ""
        
        if deprecated_warning:
            response += f"{deprecated_warning}\n\n"
            
        # Handle search intent with intelligent cache
        if intent['action'] == 'search_package' and self.cache_manager:
            package = intent.get('package', '')
            if package:
                search_data = self.search_packages_with_cache(package)
                return self.format_search_results(search_data)
            else:
                return "Please specify what package you want to search for."
            
        if intent['action'] == 'install_package':
            package = solution.get('package', 'that package')
            
            if solution.get('prefer_no_sudo'):
                response += f"I'll help you install {package} without sudo! Here are your options:\n\n"
            else:
                response += f"I'll help you install {package}! Here are your options:\n\n"
            
            for i, method in enumerate(solution['methods'], 1):
                sudo_note = " (requires sudo)" if method['requires_sudo'] else " (no sudo needed)"
                response += f"{i}. **{method['name']}**{sudo_note}\n"
                response += f"   {method['description']}\n"
                response += f"   ```\n   {method['example']}\n   ```\n\n"
                
            response += f"\n💡 {solution['explanation']}"
            
            if solution.get('prefer_no_sudo'):
                response += "\n\n🎯 Tip: Home Manager and nix profile don't need sudo!"
                
            if solution.get('related'):
                response += f"\n\nRelated: {', '.join(solution['related'])}"
                
            return response
        
        elif intent['action'] == 'generate_config':
            description = intent.get('description', 'your system')
            response += f"I can help you generate a NixOS configuration for {description}!\n\n"
            response += "To generate the configuration, I'll analyze your requirements and create a complete configuration.nix file.\n\n"
            response += f"Run this command:\n```\n{solution['example']}\n```\n\n"
            response += "This will:\n"
            response += "• Parse your natural language description\n"
            response += "• Identify needed modules (desktop environments, services, etc.)\n"
            response += "• Add appropriate packages\n"
            response += "• Generate a complete configuration.nix\n"
            response += "• Save it to /tmp/generated-config.nix for review\n\n"
            response += "💡 You can then test it with: sudo nixos-rebuild test -I nixos-config=/tmp/generated-config.nix"
            return response
            
        elif intent['action'] == 'create_flake':
            description = intent.get('description', 'development environment')
            response += f"I can help you create a Nix flake for {description}!\n\n"
            response += "Flakes are the modern way to manage Nix projects with:\n"
            response += "• Reproducible builds across all machines\n"
            response += "• Locked dependencies with flake.lock\n"
            response += "• Clean, declarative project structure\n\n"
            response += f"Run this command:\n```\n{solution['example']}\n```\n\n"
            response += "This will:\n"
            response += "• Detect your project type (Python, Node.js, Rust, etc.)\n"
            response += "• Create a flake.nix with appropriate dev tools\n"
            response += "• Set up development shell with all dependencies\n"
            response += "• Configure language-specific tooling\n\n"
            response += "💡 Then use `nix develop` to enter the development environment!"
            return response
            
        elif intent['action'] in ['validate_flake', 'convert_flake', 'show_flake_info']:
            response += f"{solution['solution']}\n\n"
            response += f"Command:\n```\n{solution['example']}\n```\n\n"
            response += f"💡 {solution['explanation']}\n\n"
            if solution.get('related'):
                response += f"Related: {', '.join(solution['related'])}"
            return response
            
        else:
            response += f"{solution['solution']}\n\n"
            
            if solution.get('requires_sudo'):
                response += "⚠️ This operation requires sudo privileges.\n\n"
                
            if solution.get('example'):
                response += f"Example:\n```\n{solution['example']}\n```\n\n"
                
            if solution.get('explanation'):
                response += f"💡 {solution['explanation']}"
                
            return response
    
    def search_packages_with_cache(self, query: str) -> Dict:
        """Search packages using intelligent cache"""
        if not self.cache_manager:
            return {
                'found': False,
                'error': 'Cache not available',
                'suggestion': 'Use nix search nixpkgs ' + query
            }
            
        # Use intelligent cache with fallback
        results, from_cache = self.cache_manager.search_with_fallback(query, timeout=5)
        
        return {
            'found': True if results else False,
            'results': results,
            'from_cache': from_cache,
            'query': query
        }
    
    def format_search_results(self, search_data: Dict) -> str:
        """Format search results from cache"""
        if not search_data['found']:
            return f"No packages found for '{search_data['query']}'. Try a different search term."
            
        response = f"🔍 Search results for '{search_data['query']}'"
        if search_data['from_cache']:
            response += " (from intelligent cache - instant!):\n\n"
        else:
            response += " (fresh search):\n\n"
            
        results = search_data['results']
        if not results:
            return f"No packages found matching '{search_data['query']}'."
            
        # Show up to 10 results
        for i, pkg in enumerate(results[:10], 1):
            response += f"{i}. **{pkg['name']}**"
            if pkg.get('version'):
                response += f" ({pkg['version']})"
            if pkg.get('popularity', 0) > 0:
                response += f" ⭐ Popular"
            response += "\n"
            
            if pkg.get('description'):
                response += f"   {pkg['description'][:80]}"
                if len(pkg['description']) > 80:
                    response += "..."
                response += "\n"
                
            if pkg.get('attribute'):
                response += f"   Install: `nix profile install {pkg['attribute']}`\n"
            response += "\n"
            
        if len(results) > 10:
            response += f"... and {len(results) - 10} more results.\n"
            
        response += "\n💡 Tip: The cache learns from your searches and gets smarter over time!"
        
        return response


def main():
    """Test the modern knowledge engine"""
    engine = ModernNixOSKnowledgeEngine()
    
    test_queries = [
        "How do I install Firefox?",
        "I need VS Code without sudo",
        "Update my system",
        "Update without sudo",
        "My WiFi isn't working",
        "Show my generations",
        "How do I rollback?",
        "install docker with nix-env",  # Should warn about deprecation
        "Setup home manager",
    ]
    
    print("🧠 Modern NixOS Knowledge Engine Test\n")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        
        # Extract intent
        intent = engine.extract_intent(query)
        print(f"🎯 Intent: {intent['action']}")
        if intent.get('package'):
            print(f"📦 Package: {intent['package']}")
        if intent.get('prefer_no_sudo'):
            print(f"🔓 Prefers no sudo: Yes")
            
        # Get solution
        solution = engine.get_solution(intent)
        
        # Get progress message if applicable
        if intent['action'] in ['install_package', 'search_package', 'update_system']:
            progress = engine.get_progress_message(intent['action'].split('_')[0])
            print(f"\n{progress['message']} (Est: {progress['estimated_time']})")
        
        # Format response
        response = engine.format_response(intent, solution)
        print(f"\n💬 Response:\n{response}")
        print("=" * 50)


if __name__ == "__main__":
    main()