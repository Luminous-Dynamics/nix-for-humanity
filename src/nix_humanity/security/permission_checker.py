#!/usr/bin/env python3
"""
from typing import List, Dict
Permission Checker for Nix for Humanity
Ensures operations are performed with appropriate permissions
"""

import os
import pwd
import grp
import stat
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
import subprocess

logger = logging.getLogger(__name__)


class PermissionChecker:
    """
    Check and validate permissions for NixOS operations
    
    Features:
    - User permission validation
    - Sudo requirement detection
    - File access checks
    - Capability-based permissions
    - Educational permission explanations
    """
    
    # Operations that require elevated privileges
    PRIVILEGED_OPERATIONS = {
        'nixos-rebuild': {
            'subcommands': ['switch', 'boot', 'test'],
            'reason': 'System configuration changes require root'
        },
        'nix-channel': {
            'subcommands': ['--add', '--remove', '--update'],
            'reason': 'Channel modifications affect system-wide packages'
        },
        'systemctl': {
            'subcommands': ['start', 'stop', 'restart', 'enable', 'disable'],
            'reason': 'Service management requires root privileges'
        }
    }
    
    # Paths that require special permissions
    PROTECTED_PATHS = {
        '/etc/nixos': {
            'write': 'root',
            'reason': 'System configuration directory'
        },
        '/nix/store': {
            'write': 'root',
            'reason': 'Nix store is immutable'
        },
        '/boot': {
            'write': 'root',
            'reason': 'Boot configuration requires root'
        }
    }
    
    @classmethod
    def check_operation_permission(cls, operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if current user has permission for operation
        
        Args:
            operation: The operation to perform (e.g., 'install-package')
            context: Additional context (command, user, etc.)
            
        Returns:
            Dict with:
                - allowed: bool
                - requires_elevation: bool
                - reason: str
                - suggestions: List[str]
        """
        current_user = cls._get_current_user_info()
        command = context.get('command', [])
        
        # Check if operation requires privileges
        if command and command[0] in cls.PRIVILEGED_OPERATIONS:
            return cls._check_privileged_command(command, current_user)
            
        # Check file access permissions
        if 'file_path' in context:
            return cls._check_file_permission(context['file_path'], context.get('mode', 'read'), current_user)
            
        # Check capability-based permissions
        if operation == 'install-package':
            return cls._check_package_installation_permission(current_user)
        elif operation == 'modify-configuration':
            return cls._check_configuration_permission(current_user)
        elif operation == 'manage-service':
            return cls._check_service_permission(current_user)
            
        # Default to allowed for unknown operations
        return {
            'allowed': True,
            'requires_elevation': False,
            'reason': 'Operation permitted for current user'
        }
        
    @classmethod
    def _get_current_user_info(cls) -> Dict[str, Any]:
        """
        Get information about current user
        """
        uid = os.getuid()
        gid = os.getgid()
        
        try:
            pw_entry = pwd.getpwuid(uid)
            username = pw_entry.pw_name
            home_dir = pw_entry.pw_dir
        except KeyError:
            username = 'unknown'
            home_dir = os.path.expanduser('~')
            
        # Get group memberships
        groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
        
        # Check if user can use sudo
        can_sudo = cls._check_sudo_access()
        
        return {
            'uid': uid,
            'gid': gid,
            'username': username,
            'home_dir': home_dir,
            'groups': groups,
            'is_root': uid == 0,
            'can_sudo': can_sudo
        }
        
    @classmethod
    def _check_sudo_access(cls) -> bool:
        """
        Check if current user can use sudo
        """
        try:
            # Try sudo -n (non-interactive) to check access
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
            
    @classmethod
    def _check_privileged_command(cls, command: List[str], user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check permission for privileged commands
        """
        base_command = command[0]
        cmd_info = cls.PRIVILEGED_OPERATIONS.get(base_command, {})
        
        # Root can do anything
        if user_info['is_root']:
            return {
                'allowed': True,
                'requires_elevation': False,
                'reason': 'Running as root'
            }
            
        # Check if subcommand requires privileges
        requires_priv = False
        if 'subcommands' in cmd_info:
            for sub in cmd_info['subcommands']:
                if any(sub in arg for arg in command[1:]):
                    requires_priv = True
                    break
        else:
            # All subcommands require privileges
            requires_priv = True
            
        if requires_priv:
            if user_info['can_sudo']:
                return {
                    'allowed': True,
                    'requires_elevation': True,
                    'reason': cmd_info.get('reason', 'Operation requires elevated privileges'),
                    'suggestions': [f"This will run with sudo: sudo {' '.join(command)}"]
                }
            else:
                return {
                    'allowed': False,
                    'requires_elevation': True,
                    'reason': 'No sudo access available',
                    'suggestions': [
                        'Ask your system administrator for help',
                        'Or run this command as root',
                        f"Reason: {cmd_info.get('reason', 'Elevated privileges required')}"
                    ]
                }
                
        return {
            'allowed': True,
            'requires_elevation': False,
            'reason': 'Operation permitted for current user'
        }
        
    @classmethod
    def _check_file_permission(cls, file_path: str, mode: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check file access permissions
        """
        path = Path(file_path).resolve()
        
        # Check protected paths
        for protected_path, rules in cls.PROTECTED_PATHS.items():
            if str(path).startswith(protected_path):
                if mode == 'write' and rules.get('write') == 'root' and not user_info['is_root']:
                    return {
                        'allowed': user_info['can_sudo'],
                        'requires_elevation': True,
                        'reason': rules.get('reason', 'Protected directory'),
                        'suggestions': [
                            f"Writing to {protected_path} requires root privileges",
                            "The operation will use sudo if you proceed"
                        ] if user_info['can_sudo'] else [
                            f"Cannot write to {protected_path} without root privileges",
                            "Contact your system administrator"
                        ]
                    }
                    
        # Check actual file permissions
        try:
            if path.exists():
                file_stat = path.stat()
                file_uid = file_stat.st_uid
                file_gid = file_stat.st_gid
                file_mode = file_stat.st_mode
                
                # Check owner
                if file_uid == user_info['uid']:
                    # User owns the file
                    if mode == 'read' and file_mode & stat.S_IRUSR:
                        return {'allowed': True, 'requires_elevation': False, 'reason': 'You own this file'}
                    elif mode == 'write' and file_mode & stat.S_IWUSR:
                        return {'allowed': True, 'requires_elevation': False, 'reason': 'You own this file'}
                        
                # Check group
                if file_gid in [grp.getgrnam(g).gr_gid for g in user_info['groups']]:
                    if mode == 'read' and file_mode & stat.S_IRGRP:
                        return {'allowed': True, 'requires_elevation': False, 'reason': 'Group permission allows access'}
                    elif mode == 'write' and file_mode & stat.S_IWGRP:
                        return {'allowed': True, 'requires_elevation': False, 'reason': 'Group permission allows access'}
                        
                # Check others
                if mode == 'read' and file_mode & stat.S_IROTH:
                    return {'allowed': True, 'requires_elevation': False, 'reason': 'File is readable by all'}
                elif mode == 'write' and file_mode & stat.S_IWOTH:
                    return {'allowed': True, 'requires_elevation': False, 'reason': 'File is writable by all'}
                    
                # No permission
                return {
                    'allowed': False,
                    'requires_elevation': True,
                    'reason': f"No {mode} permission for {file_path}",
                    'suggestions': [
                        f"File is owned by {pwd.getpwuid(file_uid).pw_name}",
                        "You may need sudo to access this file"
                    ]
                }
            else:
                # File doesn't exist, check parent directory for write
                if mode == 'write':
                    parent = path.parent
                    if parent.exists():
                        return cls._check_file_permission(str(parent), 'write', user_info)
                        
                return {
                    'allowed': True,
                    'requires_elevation': False,
                    'reason': 'File does not exist yet'
                }
                
        except Exception as e:
            logger.error(f"Error checking file permissions: {e}")
            return {
                'allowed': False,
                'requires_elevation': False,
                'reason': f"Cannot check permissions: {str(e)}"
            }
            
    @classmethod
    def _check_package_installation_permission(cls, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if user can install packages
        """
        # Check if using user profile or system profile
        if 'nixos' in user_info['groups'] or user_info['is_root']:
            return {
                'allowed': True,
                'requires_elevation': False,
                'reason': 'Member of nixos group can install packages'
            }
        elif user_info['can_sudo']:
            return {
                'allowed': True,
                'requires_elevation': True,
                'reason': 'Package installation will use sudo',
                'suggestions': [
                    'Installing to user profile instead of system profile',
                    'Use: nix-env -i package-name'
                ]
            }
        else:
            # User can still install to their profile
            return {
                'allowed': True,
                'requires_elevation': False,
                'reason': 'Installing to user profile',
                'suggestions': [
                    'Packages will be installed for your user only',
                    'System-wide installation requires sudo'
                ]
            }
            
    @classmethod
    def _check_configuration_permission(cls, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if user can modify NixOS configuration
        """
        config_path = '/etc/nixos/configuration.nix'
        return cls._check_file_permission(config_path, 'write', user_info)
        
    @classmethod
    def _check_service_permission(cls, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if user can manage services
        """
        if user_info['is_root']:
            return {
                'allowed': True,
                'requires_elevation': False,
                'reason': 'Root can manage all services'
            }
        elif user_info['can_sudo']:
            return {
                'allowed': True,
                'requires_elevation': True,
                'reason': 'Service management requires sudo'
            }
        else:
            # Check if user services are available
            return {
                'allowed': True,
                'requires_elevation': False,
                'reason': 'Can manage user services only',
                'suggestions': [
                    'Use: systemctl --user for user services',
                    'System services require sudo access'
                ]
            }
            
    @classmethod
    def explain_permission_requirement(cls, operation: str, permission_result: Dict[str, Any]) -> str:
        """
        Provide educational explanation about permission requirements
        
        Args:
            operation: The operation being attempted
            permission_result: Result from permission check
            
        Returns:
            Human-friendly explanation
        """
        if permission_result['allowed'] and not permission_result.get('requires_elevation'):
            return f"✅ You have permission to {operation}"
            
        explanations = {
            'install-package': (
                "📦 **Package Installation**\n"
                "NixOS has two types of package installations:\n"
                "1. User packages (no sudo needed) - installed just for you\n"
                "2. System packages (sudo required) - available for all users\n\n"
                "You're installing to: {}"
            ),
            'modify-configuration': (
                "⚙️  **System Configuration**\n"
                "The /etc/nixos directory contains system-wide settings.\n"
                "Modifying these files affects all users and requires admin rights.\n\n"
                "Current status: {}"
            ),
            'manage-service': (
                "🔧 **Service Management**\n"
                "Services can be system-wide or user-specific:\n"
                "- System services: Require sudo (e.g., nginx, postgresql)\n"
                "- User services: No sudo needed (e.g., your personal apps)\n\n"
                "This operation: {}"
            )
        }
        
        base_explanation = explanations.get(operation, f"Operation '{operation}' permission check")
        
        if permission_result['allowed']:
            if permission_result.get('requires_elevation'):
                status = "⚠️  Sudo will be used"
            else:
                status = "✅ No elevation needed"
        else:
            status = "❌ Permission denied"
            
        explanation = base_explanation.format(status)
        
        # Add suggestions if available
        if 'suggestions' in permission_result:
            explanation += "\n**Suggestions:**\n"
            for suggestion in permission_result['suggestions']:
                explanation += f"  • {suggestion}\n"
                
        return explanation


# Demo and testing
def demo():
    """Demonstrate permission checking"""
    print("🔒 Permission Checker Demo\n")
    
    # Get current user info
    user_info = PermissionChecker._get_current_user_info()
    print(f"Current user: {user_info['username']} (uid={user_info['uid']})")
    print(f"Groups: {', '.join(user_info['groups'])}")
    print(f"Can sudo: {'Yes' if user_info['can_sudo'] else 'No'}")
    print(f"Is root: {'Yes' if user_info['is_root'] else 'No'}")
    print()
    
    # Test operations
    test_operations = [
        {
            'operation': 'install-package',
            'context': {'command': ['nix-env', '-iA', 'nixpkgs.firefox']}
        },
        {
            'operation': 'modify-configuration',
            'context': {'file_path': '/etc/nixos/configuration.nix', 'mode': 'write'}
        },
        {
            'operation': 'manage-service',
            'context': {'command': ['systemctl', 'restart', 'nginx']}
        },
        {
            'operation': 'read-file',
            'context': {'file_path': '/etc/passwd', 'mode': 'read'}
        },
    ]
    
    for test in test_operations:
        print(f"\n{'='*50}")
        print(f"Operation: {test['operation']}")
        print(f"Context: {test['context']}")
        
        result = PermissionChecker.check_operation_permission(
            test['operation'],
            test['context']
        )
        
        print(f"\nResult:")
        print(f"  Allowed: {'✅' if result['allowed'] else '❌'}")
        print(f"  Requires elevation: {'Yes' if result.get('requires_elevation') else 'No'}")
        print(f"  Reason: {result.get('reason', 'N/A')}")
        
        # Show educational explanation
        print(f"\n{PermissionChecker.explain_permission_requirement(test['operation'], result)}")


if __name__ == "__main__":
    demo()