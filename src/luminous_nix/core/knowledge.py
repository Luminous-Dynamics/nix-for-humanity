"""
from typing import List, Dict, Optional
Knowledge base for NixOS information

This module provides accurate NixOS knowledge without hallucination.
It acts as the source of truth for NixOS facts, commands, and best practices.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class KnowledgeBase:
    """NixOS knowledge base with accurate information"""
    
    def __init__(self):
        """Initialize the knowledge base"""
        self.base_dir = Path.home() / ".local" / "share" / "luminous-nix"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_dir / "nixos_knowledge.db"
        self._ensure_database()
        
    def _ensure_database(self):
        """Ensure the database exists and is initialized"""
        if not self.db_path.exists():
            self._init_database()
            
    def _init_database(self):
        """Initialize the knowledge database"""
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
        
        # Best practices table
        c.execute('''
            CREATE TABLE IF NOT EXISTS best_practices (
                id INTEGER PRIMARY KEY,
                topic TEXT NOT NULL,
                practice TEXT NOT NULL,
                reason TEXT,
                example TEXT
            )
        ''')
        
        # Initialize with common knowledge
        self._populate_initial_knowledge(c)
        
        conn.commit()
        conn.close()
        
    def _populate_initial_knowledge(self, cursor):
        """Populate with essential NixOS knowledge"""
        
        # Solutions
        solutions = [
            # Package management
            ('install_package', 'package', 'Use declarative or imperative installation', 
             'nix profile install nixpkgs#firefox', 
             'Declarative is preferred for reproducibility', 
             'search_package,remove_package'),
            
            ('search_package', 'package', 'Search using nix search or online', 
             'nix search nixpkgs firefox', 
             'Use search.nixos.org for web interface', 
             'install_package'),
            
            ('remove_package', 'package', 'Remove imperatively installed packages', 
             'nix profile remove firefox', 
             'For declarative, remove from configuration.nix', 
             'install_package'),
            
            # System management
            ('update_system', 'system', 'Update channels and rebuild', 
             'sudo nix-channel --update && sudo nixos-rebuild switch', 
             'Updates all packages and system configuration', 
             'rollback_system'),
            
            ('rollback_system', 'system', 'Boot previous generation', 
             'sudo nixos-rebuild switch --rollback', 
             'Every rebuild creates a new generation you can rollback to', 
             'update_system,list_generations'),
            
            ('list_generations', 'system', 'Show system generations', 
             'sudo nix-env --list-generations --profile /nix/var/nix/profiles/system', 
             'Each generation is a complete system snapshot', 
             'rollback_system'),
            
            # New system management commands
            ('garbage_collect', 'system', 'Free up disk space by removing old packages', 
             'sudo nix-collect-garbage -d', 
             'Removes old generations and unused store paths. Use --delete-older-than 30d to keep recent ones', 
             'list_generations,check_status'),
            
            ('switch_generation', 'system', 'Switch to a specific generation', 
             'sudo nixos-rebuild switch --rollback', 
             'You can also use: sudo nix-env --switch-generation <number> -p /nix/var/nix/profiles/system', 
             'list_generations,rollback'),
            
            ('rebuild', 'system', 'Rebuild NixOS configuration', 
             'sudo nixos-rebuild switch', 
             'Use "test" to try without making it default, "boot" to apply on next boot', 
             'update_system,rollback'),
            
            ('check_status', 'system', 'Check system health and information', 
             'nixos-version && df -h && free -h', 
             'Shows NixOS version, disk usage, and memory usage', 
             'list_installed,list_generations'),
            
            ('list_installed', 'package', 'List all installed packages', 
             'nix profile list', 
             'For system packages: nix-store -q --requisites /run/current-system | cut -d- -f2- | sort | uniq', 
             'install_package,remove_package'),
            
            # Configuration
            ('configure_service', 'service', 'Add to configuration.nix services section', 
             'services.openssh.enable = true;', 
             'Services are managed declaratively in NixOS', 
             'disable_service,list_services'),
            
            ('edit_config', 'configuration', 'Edit NixOS configuration', 
             'sudo nano /etc/nixos/configuration.nix', 
             'Main system configuration file. Consider using version control', 
             'show_config,rebuild'),
            
            ('show_config', 'configuration', 'Display current configuration', 
             'cat /etc/nixos/configuration.nix', 
             'Shows your system configuration. Hardware config is in hardware-configuration.nix', 
             'edit_config,rebuild'),
            
            # Network
            ('fix_wifi', 'network', 'Enable NetworkManager or check hardware', 
             'networking.networkmanager.enable = true;', 
             'Most WiFi issues are solved by enabling NetworkManager', 
             'network_status'),
            
            # Network management commands
            ('show_network', 'network', 'Display network configuration and status', 
             'ip addr show && ip route show', 
             'Shows network interfaces and routing information', 
             'show_ip,test_connection'),
            
            ('show_ip', 'network', 'Display IP addresses', 
             'ip addr show', 
             'Shows all network interfaces with their IP addresses', 
             'show_network,test_connection'),
            
            ('connect_wifi', 'network', 'Connect to a WiFi network', 
             'nmcli device wifi connect SSID', 
             'Requires NetworkManager. Will prompt for password if needed', 
             'list_wifi,show_network'),
            
            ('list_wifi', 'network', 'Scan for WiFi networks', 
             'nmcli device wifi list', 
             'Shows available WiFi networks with signal strength', 
             'connect_wifi,show_network'),
            
            ('test_connection', 'network', 'Test internet connectivity', 
             'ping -c 3 google.com', 
             'Tests DNS resolution and internet connectivity', 
             'show_network,show_ip'),
            
            # Service management commands
            ('start_service', 'service', 'Start a system service', 
             'sudo systemctl start nginx', 
             'Starts the service immediately. Use enable to start at boot', 
             'stop_service,enable_service'),
            
            ('stop_service', 'service', 'Stop a system service', 
             'sudo systemctl stop nginx', 
             'Stops the service immediately', 
             'start_service,disable_service'),
            
            ('restart_service', 'service', 'Restart a system service', 
             'sudo systemctl restart nginx', 
             'Stops and starts the service', 
             'start_service,service_status'),
            
            ('service_status', 'service', 'Check service status', 
             'systemctl status nginx', 
             'Shows if service is running and recent logs', 
             'start_service,service_logs'),
            
            ('list_services', 'service', 'List all services', 
             'systemctl list-units --type=service', 
             'Shows all systemd services and their status', 
             'service_status,enable_service'),
            
            ('enable_service', 'service', 'Enable service at boot', 
             'sudo systemctl enable nginx', 
             'Service will start automatically on boot', 
             'disable_service,start_service'),
            
            ('disable_service', 'service', 'Disable service at boot', 
             'sudo systemctl disable nginx', 
             'Service will not start automatically on boot', 
             'enable_service,stop_service'),
            
            ('service_logs', 'service', 'View service logs', 
             'journalctl -u nginx -n 50', 
             'Shows recent log entries for the service', 
             'service_status,list_services'),
            
            # User management commands
            ('create_user', 'user', 'Create a new user account', 
             'sudo useradd -m username', 
             'Creates user with home directory. Set password with passwd', 
             'list_users,grant_sudo'),
            
            ('list_users', 'user', 'List all users', 
             'getent passwd | grep -E ":[0-9]{4}:" | cut -d: -f1', 
             'Shows human users (UID >= 1000)', 
             'create_user,add_user_to_group'),
            
            ('add_user_to_group', 'user', 'Add user to group', 
             'sudo usermod -a -G groupname username', 
             'User may need to log out and back in', 
             'list_users,grant_sudo'),
            
            ('change_password', 'user', 'Change user password', 
             'sudo passwd username', 
             'Interactive password change', 
             'create_user,grant_sudo'),
            
            ('grant_sudo', 'user', 'Grant sudo privileges', 
             'sudo usermod -a -G wheel username', 
             'Adds user to wheel group for sudo access', 
             'create_user,add_user_to_group'),
            
            # Storage management commands
            ('disk_usage', 'storage', 'Show disk usage', 
             'df -h', 
             'Shows filesystem disk space usage', 
             'analyze_disk,find_large_files'),
            
            ('analyze_disk', 'storage', 'Analyze disk usage', 
             'du -h --max-depth=1 / | sort -hr | head -20', 
             'Shows largest directories', 
             'disk_usage,find_large_files'),
            
            ('mount_device', 'storage', 'Mount a device', 
             'sudo mount /dev/sdb1 /mnt', 
             'Mounts device to specified directory', 
             'unmount_device,disk_usage'),
            
            ('unmount_device', 'storage', 'Unmount a device', 
             'sudo umount /dev/sdb1', 
             'Safely unmounts the device', 
             'mount_device,disk_usage'),
            
            ('find_large_files', 'storage', 'Find large files', 
             'find / -type f -size +100M -exec ls -lh {} \\; | sort -k5 -hr | head -20', 
             'Finds files larger than 100MB', 
             'analyze_disk,disk_usage'),
        ]
        
        for solution in solutions:
            cursor.execute('''
                INSERT OR IGNORE INTO solutions 
                (intent, category, solution, example, explanation, related)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', solution)
            
        # Common problems
        problems = [
            ('command not found', 
             'Package not in PATH', 
             'Install package or use nix-shell', 
             'Use declarative installation when possible'),
             
            ('read-only file system', 
             'Trying to modify /etc directly', 
             'Edit configuration.nix instead', 
             'NixOS manages /etc through configuration'),
             
            ('infinite recursion', 
             'Circular dependency in config', 
             'Check for recursive definitions', 
             'Use mkForce or mkDefault for overrides'),
             
            ('error: attribute missing',
             'Package or option name incorrect',
             'Check correct attribute name',
             'Use nix search to find exact names'),
        ]
        
        for problem in problems:
            cursor.execute('''
                INSERT OR IGNORE INTO problems
                (symptom, cause, solution, prevention)
                VALUES (?, ?, ?, ?)
            ''', problem)
            
        # Best practices
        practices = [
            ('package_installation',
             'Always prefer declarative installation',
             'Ensures reproducibility and easy rollback',
             'Add to environment.systemPackages in configuration.nix'),
             
            ('system_updates',
             'Test configuration before switching',
             'Prevents breaking your system',
             'Use nixos-rebuild test before nixos-rebuild switch'),
             
            ('configuration_management',
             'Keep configuration modular',
             'Easier to maintain and share',
             'Split configuration into multiple .nix files'),
        ]
        
        for practice in practices:
            cursor.execute('''
                INSERT OR IGNORE INTO best_practices
                (topic, practice, reason, example)
                VALUES (?, ?, ?, ?)
            ''', practice)
            
    def get_solution(self, intent: str, query: str = "") -> Optional[Dict[str, Any]]:
        """Get solution for a specific intent
        
        Args:
            intent: The intent type (e.g., 'install_package')
            query: The original user query for context
            
        Returns:
            Dictionary with solution information or None
        """
        # Special handling for help intent
        if intent == 'help':
            return self._get_help_response()
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT solution, example, explanation, related
            FROM solutions
            WHERE intent = ?
        ''', (intent,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None
            
        solution, example, explanation, related = result
        
        # For install_package intent, extract package name from query
        if intent == 'install_package':
            # Try to extract package name from query
            import re
            package = None
            
            # Common package aliases
            package_aliases = {
                'firefox': 'firefox',
                'chrome': 'google-chrome',
                'vscode': 'vscode',
                'code': 'vscode',
                'vim': 'vim',
                'neovim': 'neovim',
                'python': 'python3',
                'nodejs': 'nodejs',
                'node': 'nodejs',
                'docker': 'docker',
                'git': 'git',
            }
            
            # Extract package name
            words = query.lower().split()
            for word in words:
                if word in package_aliases:
                    package = package_aliases[word]
                    break
                elif word not in ['install', 'get', 'add', 'need', 'want', 'i', 'the', 'a', 'an', 'to', 'for', 'me', 'please']:
                    package = word
                    break
            
            if package:
                # Get installation methods
                methods = self.get_installation_methods(package)
                
                return {
                    'found': True,
                    'solution': solution,
                    'methods': methods,
                    'explanation': explanation,
                    'package': package,
                    'related': related.split(',') if related else [],
                    'commands': [
                        {
                            'command': method['command'],
                            'description': method['description']
                        } for method in methods[:3]  # Top 3 methods
                    ]
                }
        
        return {
            'found': True,
            'solution': solution,
            'example': example,
            'explanation': explanation,
            'related': related.split(',') if related else [],
            'response': f"{solution}\n\nExample:\n```\n{example}\n```\n\n💡 {explanation}"
        }
        
    def get_problem_solution(self, symptom: str) -> Optional[Dict[str, Any]]:
        """Get solution for a common problem"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Use LIKE for fuzzy matching
        c.execute('''
            SELECT cause, solution, prevention
            FROM problems
            WHERE symptom LIKE ?
        ''', (f'%{symptom}%',))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None
            
        cause, solution, prevention = result
        
        return {
            'cause': cause,
            'solution': solution,
            'prevention': prevention
        }
        
    def get_best_practice(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get best practice for a topic"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT practice, reason, example
            FROM best_practices
            WHERE topic = ?
        ''', (topic,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None
            
        practice, reason, example = result
        
        return {
            'practice': practice,
            'reason': reason,
            'example': example
        }
        
    def get_installation_methods(self, package: str) -> List[Dict[str, Any]]:
        """Get all installation methods for a package"""
        methods = [
            {
                'type': 'declarative',
                'name': 'Declarative (Recommended)',
                'description': 'Add to your system configuration for permanent installation',
                'command': f'Edit /etc/nixos/configuration.nix and add to environment.systemPackages',
                'example': f'environment.systemPackages = with pkgs; [ {package} ];'
            },
            {
                'type': 'home-manager',
                'name': 'Home Manager',
                'description': 'User-specific declarative installation',
                'command': f'Edit ~/.config/home-manager/home.nix',
                'example': f'home.packages = with pkgs; [ {package} ];'
            },
            {
                'type': 'imperative',
                'name': 'Imperative (Quick)',
                'description': 'Quick installation using nix profile',
                'command': f'nix profile install nixpkgs#{package}',
                'example': f'nix profile install nixpkgs#{package}'
            },
            {
                'type': 'shell',
                'name': 'Temporary Shell',
                'description': 'Try without installing',
                'command': f'nix-shell -p {package}',
                'example': f'nix-shell -p {package}'
            },
            {
                'type': 'develop',
                'name': 'Development Shell',
                'description': 'For development environments',
                'command': f'nix develop',
                'example': f'Create shell.nix with buildInputs = [ {package} ];'
            }
        ]
        
        return methods
        
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search across all knowledge"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        results = []
        
        # Search solutions
        c.execute('''
            SELECT 'solution' as type, intent, solution, explanation
            FROM solutions
            WHERE solution LIKE ? OR explanation LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        
        for row in c.fetchall():
            results.append({
                'type': row[0],
                'intent': row[1],
                'content': row[2],
                'explanation': row[3]
            })
            
        # Search problems
        c.execute('''
            SELECT 'problem' as type, symptom, solution, cause
            FROM problems
            WHERE symptom LIKE ? OR solution LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        
        for row in c.fetchall():
            results.append({
                'type': row[0],
                'symptom': row[1],
                'solution': row[2],
                'cause': row[3]
            })
            
        conn.close()
        return results
    
    def _get_help_response(self, plugin_info: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate help response with all available commands"""
        help_text = """I can help you with a wide range of NixOS tasks:

**📦 Package Management**
• `install [package]` - Install software (e.g., "install firefox")
• `remove [package]` - Uninstall software (e.g., "remove vim")
• `search [query]` - Find packages (e.g., "search text editor")
• `list installed` - Show all installed packages

**🔧 System Maintenance**
• `update system` - Update all packages and system
• `garbage collect` - Free disk space by cleaning old packages
• `list generations` - Show system snapshots
• `switch generation [num]` - Restore previous system state
• `rollback` - Go back to previous generation

**⚙️ Configuration**
• `edit config` - Open configuration.nix for editing
• `show config` - Display current configuration
• `rebuild` - Apply configuration changes
• `configure [service]` - Help with service configuration

**🌐 Network Management**
• `show network` - Display network configuration
• `show ip` - Show IP addresses
• `connect wifi [network]` - Connect to WiFi
• `list wifi` - Scan for WiFi networks
• `test connection` - Check internet connectivity

**🔄 Service Management**
• `start [service]` - Start a service (e.g., "start nginx")
• `stop [service]` - Stop a service
• `restart [service]` - Restart a service
• `service status [name]` - Check if service is running
• `list services` - Show all services
• `enable [service]` - Enable service at boot
• `disable [service]` - Disable service at boot
• `service logs [name]` - View service logs

**👤 User Management**
• `create user [name]` - Add a new user account
• `list users` - Show all users
• `add [user] to [group]` - Add user to group
• `change password [user]` - Reset user password
• `grant [user] sudo` - Give admin privileges

**💾 Storage Management**
• `disk usage` - Show disk space usage
• `analyze disk` - Find what's using space
• `mount [device]` - Mount a USB/drive
• `unmount [device]` - Safely remove device
• `find large files` - Locate space hogs

**ℹ️ Information**
• `check status` - System health and resource usage
• `explain [topic]` - Learn about NixOS concepts
• `help` - Show this help message

Just ask naturally! Examples:
- "I need a web browser"
- "my system is running out of space"
- "how do I enable ssh?"
- "what version of NixOS am I running?"
- "create a user for my friend"
- "connect to my home wifi"
- "start the docker service"
"""
        
        # Add plugin commands if available
        if plugin_info:
            help_text += "\n\n**🔌 Available Plugins**\n"
            for plugin in plugin_info:
                help_text += f"• **{plugin['name']}** - {plugin['description']}\n"
                if plugin.get('commands'):
                    for cmd in plugin['commands'][:3]:  # Show top 3 commands
                        help_text += f"  - `{cmd}` \n"
        
        return {
            'found': True,
            'solution': 'Available commands and features',
            'response': help_text,
            'commands': [
                {'command': 'install firefox', 'description': 'Example: Install a package'},
                {'command': 'garbage collect', 'description': 'Example: Free disk space'},
                {'command': 'list generations', 'description': 'Example: View system history'}
            ],
            'explanation': 'I understand natural language, so feel free to ask in your own words!'
        }