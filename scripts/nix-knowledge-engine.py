#!/usr/bin/env python3
"""
from typing import List
NixOS Knowledge Engine - A better solution
Combines LLM intent recognition with deterministic knowledge
"""

import json
import subprocess
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class NixOSKnowledgeEngine:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.db_path = self.base_dir / "nixos_knowledge.db"
        self.init_db()
        
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
        
        # Installation methods
        self.install_methods = {
            'declarative': {
                'name': 'Declarative (Recommended)',
                'description': 'Add to your system configuration for permanent installation',
                'command': 'Edit /etc/nixos/configuration.nix and add to environment.systemPackages',
                'example': 'environment.systemPackages = with pkgs; [ {package} ];'
            },
            'home-manager': {
                'name': 'Home Manager',
                'description': 'User-specific declarative installation',
                'command': 'Edit ~/.config/home-manager/home.nix',
                'example': 'home.packages = with pkgs; [ {package} ];'
            },
            'imperative': {
                'name': 'Imperative',
                'description': 'Quick installation for current user',
                'command': 'nix-env -iA nixos.{package}',
                'example': 'nix-env -iA nixos.{package}'
            },
            'shell': {
                'name': 'Temporary Shell',
                'description': 'Try without installing',
                'command': 'nix-shell -p {package}',
                'example': 'nix-shell -p {package}'
            }
        }
        
    def init_db(self):
        """Initialize knowledge database"""
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
                related TEXT
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
        
        # Initialize with common solutions
        self._populate_initial_knowledge(c)
        
        conn.commit()
        conn.close()
        
    def _populate_initial_knowledge(self, cursor):
        """Populate with essential NixOS knowledge"""
        solutions = [
            # Package management
            ('install_package', 'package', 'Use declarative or imperative installation', 
             'nix-env -iA nixos.firefox', 'Declarative is preferred for reproducibility', 'search_package,remove_package'),
            
            ('search_package', 'package', 'Search using nix search or online', 
             'nix search nixpkgs firefox', 'Use search.nixos.org for web interface', 'install_package'),
            
            ('remove_package', 'package', 'Remove imperatively installed packages', 
             'nix-env -e firefox', 'For declarative, remove from configuration.nix', 'install_package'),
            
            # System management
            ('update_system', 'system', 'Update channels and rebuild', 
             'sudo nix-channel --update && sudo nixos-rebuild switch', 
             'Updates all packages and system configuration', 'rollback_system'),
            
            ('rollback_system', 'system', 'Boot previous generation', 
             'sudo nixos-rebuild switch --rollback', 
             'Every rebuild creates a new generation you can rollback to', 'update_system,list_generations'),
            
            ('list_generations', 'system', 'Show system generations', 
             'sudo nix-env --list-generations --profile /nix/var/nix/profiles/system', 
             'Each generation is a complete system snapshot', 'rollback_system'),
            
            # Network
            ('fix_wifi', 'network', 'Enable NetworkManager or check hardware', 
             'networking.networkmanager.enable = true;', 
             'Most WiFi issues are solved by enabling NetworkManager', 'network_status'),
            
            # Services
            ('enable_service', 'service', 'Add to configuration.nix services section', 
             'services.openssh.enable = true;', 
             'Services are managed declaratively in NixOS', 'disable_service,list_services'),
        ]
        
        for solution in solutions:
            cursor.execute('''
                INSERT OR IGNORE INTO solutions 
                (intent, category, solution, example, explanation, related)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', solution)
            
        # Common problems
        problems = [
            ('command not found', 'Package not in PATH', 
             'Install package or use nix-shell', 
             'Use declarative installation when possible'),
             
            ('read-only file system', 'Trying to modify /etc directly', 
             'Edit configuration.nix instead', 
             'NixOS manages /etc through configuration'),
             
            ('infinite recursion', 'Circular dependency in config', 
             'Check for recursive definitions', 
             'Use mkForce or mkDefault for overrides'),
        ]
        
        for problem in problems:
            cursor.execute('''
                INSERT OR IGNORE INTO problems
                (symptom, cause, solution, prevention)
                VALUES (?, ?, ?, ?)
            ''', problem)
    
    def extract_intent(self, query: str) -> Dict:
        """Extract intent from natural language query"""
        query_lower = query.lower()
        
        # Installation patterns
        if any(word in query_lower for word in ['install', 'get', 'need', 'want', 'set up']):
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
                    if word not in ['i', 'want', 'need', 'install', 'get', 'the', 'a', 'an']:
                        package = word.lower()
                        break
                        
            return {
                'action': 'install_package',
                'package': package,
                'query': query
            }
            
        # Search patterns
        elif any(word in query_lower for word in ['search', 'find', 'look for', 'is there']):
            return {
                'action': 'search_package',
                'query': query
            }
            
        # Update patterns
        elif any(word in query_lower for word in ['update', 'upgrade']):
            return {
                'action': 'update_system',
                'query': query
            }
            
        # WiFi/Network patterns
        elif any(word in query_lower for word in ['wifi', 'wi-fi', 'internet', 'network']):
            return {
                'action': 'fix_wifi',
                'query': query
            }
            
        # Generation patterns
        elif any(word in query_lower for word in ['generation', 'rollback', 'previous', 'undo']):
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
        """Get solution for intent from knowledge base"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        action = intent.get('action', 'unknown')
        
        # Fetch solution
        c.execute('''
            SELECT solution, example, explanation, related
            FROM solutions
            WHERE intent = ?
        ''', (action,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return {
                'found': False,
                'suggestion': 'I don\'t understand that yet. Try asking about installing packages, updating the system, or fixing WiFi.'
            }
            
        solution, example, explanation, related = result
        
        # Customize for specific package if applicable
        if action == 'install_package' and intent.get('package'):
            package = intent['package']
            return {
                'found': True,
                'solution': solution,
                'methods': self._get_install_methods(package),
                'explanation': explanation,
                'package': package,
                'related': related.split(',') if related else []
            }
            
        return {
            'found': True,
            'solution': solution,
            'example': example,
            'explanation': explanation,
            'related': related.split(',') if related else []
        }
    
    def _get_install_methods(self, package: str) -> List[Dict]:
        """Get installation methods for a package"""
        methods = []
        for key, method in self.install_methods.items():
            methods.append({
                'type': key,
                'name': method['name'],
                'description': method['description'],
                'command': method['command'].format(package=package),
                'example': method['example'].format(package=package)
            })
        return methods
    
    def format_response(self, intent: Dict, solution: Dict) -> str:
        """Format solution as natural response"""
        if not solution['found']:
            return solution['suggestion']
            
        if intent['action'] == 'install_package':
            package = solution.get('package', 'that package')
            response = f"I'll help you install {package}! Here are your options:\n\n"
            
            for i, method in enumerate(solution['methods'], 1):
                response += f"{i}. **{method['name']}** - {method['description']}\n"
                response += f"   ```\n   {method['example']}\n   ```\n\n"
                
            response += f"\n💡 {solution['explanation']}"
            
            if solution.get('related'):
                response += f"\n\nRelated: {', '.join(solution['related'])}"
                
            return response
            
        else:
            response = f"{solution['solution']}\n\n"
            if solution.get('example'):
                response += f"Example:\n```\n{solution['example']}\n```\n\n"
            if solution.get('explanation'):
                response += f"💡 {solution['explanation']}"
            return response


def main():
    """Test the knowledge engine"""
    engine = NixOSKnowledgeEngine()
    
    test_queries = [
        "How do I install Firefox?",
        "I need VS Code",
        "Update my system",
        "My WiFi isn't working",
        "What's a generation?",
        "How do I rollback?"
    ]
    
    print("🧠 NixOS Knowledge Engine Test\n")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        
        # Extract intent
        intent = engine.extract_intent(query)
        print(f"🎯 Intent: {intent['action']}")
        if intent.get('package'):
            print(f"📦 Package: {intent['package']}")
            
        # Get solution
        solution = engine.get_solution(intent)
        
        # Format response
        response = engine.format_response(intent, solution)
        print(f"\n💬 Response:\n{response}")
        print("=" * 50)


if __name__ == "__main__":
    main()