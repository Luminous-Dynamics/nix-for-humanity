#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Educational Error Handler for Nix for Humanity
Transforms errors into learning opportunities for all personas
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from enum import Enum
import subprocess

class ErrorCategory(Enum):
    """Error categories based on user impact"""
    USER_INPUT = "user_input"
    SYSTEM = "system"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    SAFETY = "safety"
    NETWORK = "network"
    DISK_SPACE = "disk_space"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"

class CommandError(Exception):
    """Educational error with helpful suggestions"""
    def __init__(self, 
                 user_message: str,
                 suggestions: List[str],
                 technical: Optional[str] = None,
                 learnable: bool = True,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 recovery_commands: Optional[List[Dict[str, str]]] = None):
        self.user_message = user_message
        self.suggestions = suggestions
        self.technical = technical
        self.learnable = learnable
        self.category = category
        self.recovery_commands = recovery_commands or []
        super().__init__(user_message)

class EducationalErrorHandler:
    """Transforms technical errors into educational opportunities"""
    
    def __init__(self):
        self.error_patterns = self._initialize_error_patterns()
        self.persona_adaptations = self._initialize_persona_adaptations()
        
    def _initialize_error_patterns(self) -> List[Dict]:
        """Initialize common error patterns with educational responses"""
        return [
            # Package not found errors
            {
                'pattern': r'attribute.*[\'"](\w+)[\'"].*missing|no such package',
                'category': ErrorCategory.NOT_FOUND,
                'extract': lambda m: m.group(1) if m.groups() else 'the package',
                'handler': self._handle_package_not_found
            },
            {
                'pattern': r'Package.*[\'"](\w+)[\'"].*not found',
                'category': ErrorCategory.NOT_FOUND,
                'extract': lambda m: m.group(1),
                'handler': self._handle_package_not_found
            },
            
            # Permission errors
            {
                'pattern': r'permission denied|operation not permitted|access denied',
                'category': ErrorCategory.PERMISSION,
                'handler': self._handle_permission_error
            },
            {
                'pattern': r'sudo.*required|requires root|must be root',
                'category': ErrorCategory.PERMISSION,
                'handler': self._handle_sudo_required
            },
            
            # Network errors
            {
                'pattern': r'network.*error|connection.*refused|timeout|cannot reach',
                'category': ErrorCategory.NETWORK,
                'handler': self._handle_network_error
            },
            {
                'pattern': r'SSL.*error|certificate.*error',
                'category': ErrorCategory.NETWORK,
                'handler': self._handle_ssl_error
            },
            
            # Disk space errors
            {
                'pattern': r'no space left|disk.*full|insufficient.*space',
                'category': ErrorCategory.DISK_SPACE,
                'handler': self._handle_disk_space_error
            },
            
            # Configuration errors
            {
                'pattern': r'syntax error|parse error|invalid.*configuration',
                'category': ErrorCategory.CONFIGURATION,
                'handler': self._handle_configuration_error
            },
            {
                'pattern': r'infinite recursion|evaluation.*aborted',
                'category': ErrorCategory.CONFIGURATION,
                'handler': self._handle_infinite_recursion
            },
            
            # Dependency conflicts
            {
                'pattern': r'collision|conflict|incompatible|cannot coexist',
                'category': ErrorCategory.DEPENDENCY,
                'handler': self._handle_dependency_conflict
            },
            
            # Channel/update errors
            {
                'pattern': r'channel.*update.*failed|cannot update',
                'category': ErrorCategory.SYSTEM,
                'handler': self._handle_channel_error
            },
        ]
    
    def _initialize_persona_adaptations(self) -> Dict[str, Dict]:
        """Initialize persona-specific message adaptations"""
        return {
            'grandma_rose': {
                'style': 'very_simple',
                'technical_level': 0,
                'examples': True,
                'voice_friendly': True
            },
            'maya': {
                'style': 'concise',
                'technical_level': 1,
                'examples': False,
                'voice_friendly': False
            },
            'david': {
                'style': 'clear',
                'technical_level': 1,
                'examples': True,
                'voice_friendly': False
            },
            'dr_sarah': {
                'style': 'technical',
                'technical_level': 3,
                'examples': False,
                'voice_friendly': False
            },
            'alex': {
                'style': 'screen_reader',
                'technical_level': 2,
                'examples': True,
                'voice_friendly': False
            },
            'carlos': {
                'style': 'educational',
                'technical_level': 1,
                'examples': True,
                'voice_friendly': False
            },
            'viktor': {
                'style': 'simple_english',
                'technical_level': 1,
                'examples': True,
                'voice_friendly': False
            },
            'luna': {
                'style': 'predictable',
                'technical_level': 1,
                'examples': True,
                'voice_friendly': False
            }
        }
    
    def analyze_error(self, error_message: str, context: Optional[Dict] = None) -> CommandError:
        """Analyze error and return educational CommandError"""
        context = context or {}
        
        # Try to match known patterns
        for pattern_info in self.error_patterns:
            match = re.search(pattern_info['pattern'], error_message, re.IGNORECASE)
            if match:
                # Extract relevant information
                extracted = None
                if 'extract' in pattern_info and match.groups():
                    extracted = pattern_info['extract'](match)
                
                # Call specific handler
                return pattern_info['handler'](error_message, extracted, context)
        
        # No pattern matched - generic handling
        return self._handle_unknown_error(error_message, context)
    
    def _handle_package_not_found(self, error: str, package: Optional[str], context: Dict) -> CommandError:
        """Handle package not found errors educationally"""
        package = package or "the package you're looking for"
        
        # Search for similar packages
        similar = self._find_similar_packages(package)
        
        user_message = f"I couldn't find {package} in the NixOS package collection."
        
        suggestions = [
            f"Try searching for it: nix search nixpkgs {package}",
            "The package might have a different name in NixOS"
        ]
        
        recovery_commands = [
            {
                'description': f'Search for packages containing "{package}"',
                'command': f'nix search nixpkgs {package}'
            }
        ]
        
        if similar:
            suggestions.append(f"Did you mean one of these: {', '.join(similar[:3])}")
            for pkg in similar[:3]:
                recovery_commands.append({
                    'description': f'Install {pkg} instead',
                    'command': f'nix profile install nixpkgs#{pkg}'
                })
        
        suggestions.extend([
            "Check the NixOS package search website: search.nixos.org",
            "Some packages are in different channels (unstable, stable)"
        ])
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical=f"Package attribute '{package}' not found in nixpkgs",
            learnable=True,
            category=ErrorCategory.NOT_FOUND,
            recovery_commands=recovery_commands
        )
    
    def _handle_permission_error(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle permission errors educationally"""
        user_message = "This action needs special permissions that you don't currently have."
        
        suggestions = [
            "Some operations need administrator (sudo) access",
            "I'll always ask before using sudo",
            "You can also try installing in your user profile instead"
        ]
        
        recovery_commands = []
        
        # Check if we can suggest sudo
        if context.get('command') and not context['command'].startswith('sudo'):
            recovery_commands.append({
                'description': 'Try with administrator privileges',
                'command': f"sudo {context['command']}"
            })
        
        recovery_commands.extend([
            {
                'description': 'Check your user groups',
                'command': 'groups'
            },
            {
                'description': 'Install in user profile instead',
                'command': context.get('command', '').replace('sudo ', '') if context.get('command') else ''
            }
        ])
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="Permission denied - insufficient privileges",
            learnable=True,
            category=ErrorCategory.PERMISSION,
            recovery_commands=recovery_commands
        )
    
    def _handle_sudo_required(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle sudo required errors"""
        user_message = "This system operation requires administrator access."
        
        suggestions = [
            "System-wide changes need sudo privileges",
            "I can help you run this safely with sudo",
            "Alternatively, try a user-level operation"
        ]
        
        recovery_commands = []
        
        if context.get('command'):
            recovery_commands.append({
                'description': 'Run with sudo (requires password)',
                'command': f"sudo {context['command']}"
            })
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="Operation requires root privileges",
            learnable=True,
            category=ErrorCategory.PERMISSION,
            recovery_commands=recovery_commands
        )
    
    def _handle_network_error(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle network errors educationally"""
        user_message = "I'm having trouble connecting to the internet to complete this task."
        
        suggestions = [
            "Check if you're connected to the internet",
            "Sometimes the package servers are temporarily down",
            "Your firewall might be blocking the connection"
        ]
        
        recovery_commands = [
            {
                'description': 'Test internet connection',
                'command': 'ping -c 3 1.1.1.1'
            },
            {
                'description': 'Check DNS resolution',
                'command': 'nslookup nixos.org'
            },
            {
                'description': 'Update channels and retry',
                'command': 'nix-channel --update'
            }
        ]
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="Network connection error",
            learnable=False,
            category=ErrorCategory.NETWORK,
            recovery_commands=recovery_commands
        )
    
    def _handle_ssl_error(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle SSL/certificate errors"""
        user_message = "There's a security certificate issue preventing the connection."
        
        suggestions = [
            "This might be due to incorrect system time",
            "Corporate networks sometimes have certificate issues",
            "The certificate might need to be updated"
        ]
        
        recovery_commands = [
            {
                'description': 'Check system time',
                'command': 'date'
            },
            {
                'description': 'Update certificate bundle',
                'command': 'sudo nix-channel --update'
            }
        ]
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="SSL certificate verification failed",
            learnable=False,
            category=ErrorCategory.NETWORK,
            recovery_commands=recovery_commands
        )
    
    def _handle_disk_space_error(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle disk space errors educationally"""
        user_message = "Your computer is running out of storage space."
        
        suggestions = [
            "NixOS keeps old versions for safety, but they use space",
            "We can clean up old, unused versions",
            "This won't affect your current programs"
        ]
        
        recovery_commands = [
            {
                'description': 'Check available space',
                'command': 'df -h /'
            },
            {
                'description': 'Clean up old versions (safe)',
                'command': 'nix-collect-garbage'
            },
            {
                'description': 'Deep clean (removes all old versions)',
                'command': 'sudo nix-collect-garbage -d'
            }
        ]
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="Insufficient disk space in /nix/store",
            learnable=False,
            category=ErrorCategory.DISK_SPACE,
            recovery_commands=recovery_commands
        )
    
    def _handle_configuration_error(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle configuration syntax errors"""
        user_message = "There's a problem with a configuration file."
        
        # Try to extract line number
        line_match = re.search(r'line (\d+)', error)
        line_num = line_match.group(1) if line_match else None
        
        if line_num:
            user_message += f" The issue is around line {line_num}."
        
        suggestions = [
            "Configuration files need exact formatting",
            "Common issues: missing semicolons, brackets, or quotes",
            "I can help you fix the syntax"
        ]
        
        recovery_commands = [
            {
                'description': 'Check configuration syntax',
                'command': 'sudo nixos-rebuild test'
            }
        ]
        
        if '/etc/nixos/configuration.nix' in error:
            recovery_commands.append({
                'description': 'Edit main configuration',
                'command': 'sudo nano /etc/nixos/configuration.nix'
            })
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical=f"Syntax error in Nix expression{f' at line {line_num}' if line_num else ''}",
            learnable=True,
            category=ErrorCategory.CONFIGURATION,
            recovery_commands=recovery_commands
        )
    
    def _handle_infinite_recursion(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle infinite recursion errors"""
        user_message = "The configuration has a circular reference - something is defined in terms of itself."
        
        suggestions = [
            "This happens when A depends on B, and B depends on A",
            "Check recent changes to your configuration",
            "Look for recursive variable definitions"
        ]
        
        recovery_commands = [
            {
                'description': 'Test configuration',
                'command': 'sudo nixos-rebuild test --show-trace'
            },
            {
                'description': 'Revert to previous generation',
                'command': 'sudo nixos-rebuild switch --rollback'
            }
        ]
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="Infinite recursion encountered in Nix evaluation",
            learnable=True,
            category=ErrorCategory.CONFIGURATION,
            recovery_commands=recovery_commands
        )
    
    def _handle_dependency_conflict(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle dependency conflict errors"""
        user_message = "Two packages you have installed need different versions of the same thing."
        
        suggestions = [
            "NixOS prevents conflicts to keep your system stable",
            "You can install conflicting packages in separate environments",
            "Using nix-shell is often the best solution"
        ]
        
        recovery_commands = [
            {
                'description': 'Use temporary shell instead',
                'command': f"nix-shell -p {context.get('package', 'PACKAGE')}"
            },
            {
                'description': 'Install in user profile',
                'command': f"nix-env -iA nixpkgs.{context.get('package', 'PACKAGE')}"
            }
        ]
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="Package collision detected",
            learnable=True,
            category=ErrorCategory.DEPENDENCY,
            recovery_commands=recovery_commands
        )
    
    def _handle_channel_error(self, error: str, extracted: Optional[str], context: Dict) -> CommandError:
        """Handle channel update errors"""
        user_message = "I couldn't update the package channels."
        
        suggestions = [
            "Channels are like app stores for NixOS",
            "This might be a temporary server issue",
            "Your network connection might be blocking it"
        ]
        
        recovery_commands = [
            {
                'description': 'List current channels',
                'command': 'nix-channel --list'
            },
            {
                'description': 'Try updating again',
                'command': 'sudo nix-channel --update'
            },
            {
                'description': 'Check channel URLs',
                'command': 'cat ~/.nix-channels'
            }
        ]
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical="Channel update failed",
            learnable=False,
            category=ErrorCategory.SYSTEM,
            recovery_commands=recovery_commands
        )
    
    def _handle_unknown_error(self, error: str, context: Dict) -> CommandError:
        """Handle unknown errors with generic but helpful advice"""
        user_message = "Something unexpected happened. Let me help you figure out what went wrong."
        
        suggestions = [
            "Try running the command again - sometimes issues are temporary",
            "Check if all the words are spelled correctly",
            "Make sure you have internet connection"
        ]
        
        # Try to extract any useful information
        if 'command not found' in error.lower():
            suggestions.insert(0, "The program might not be installed yet")
        elif 'broken pipe' in error.lower():
            suggestions.insert(0, "The operation was interrupted - try again")
        
        recovery_commands = [
            {
                'description': 'Check system status',
                'command': 'systemctl status'
            },
            {
                'description': 'View recent system logs',
                'command': 'journalctl -xe | tail -20'
            }
        ]
        
        return CommandError(
            user_message=user_message,
            suggestions=suggestions,
            technical=error[:200] + "..." if len(error) > 200 else error,
            learnable=True,
            category=ErrorCategory.UNKNOWN,
            recovery_commands=recovery_commands
        )
    
    def _find_similar_packages(self, package: str) -> List[str]:
        """Find packages with similar names"""
        # Common package name mappings
        common_mappings = {
            'chrome': ['google-chrome', 'chromium'],
            'firefox': ['firefox', 'firefox-esr'],
            'code': ['vscode', 'vscodium'],
            'python': ['python3', 'python311', 'python312'],
            'node': ['nodejs', 'nodejs-18_x', 'nodejs-20_x'],
            'docker': ['docker', 'podman'],
            'vim': ['vim', 'neovim'],
            'emacs': ['emacs', 'emacs-gtk'],
        }
        
        # Check if we have a known mapping
        package_lower = package.lower()
        for key, values in common_mappings.items():
            if key in package_lower or package_lower in key:
                return values
        
        # Try to search for similar packages (would need actual implementation)
        # For now, return empty list
        return []
    
    def format_for_persona(self, error: CommandError, persona: str = 'default') -> Dict[str, any]:
        """Format error message for specific persona"""
        persona_config = self.persona_adaptations.get(persona, {})
        
        result = {
            'message': error.user_message,
            'suggestions': error.suggestions,
            'category': error.category.value,
            'recovery_commands': error.recovery_commands
        }
        
        # Adapt based on persona
        if persona == 'grandma_rose':
            # Simplify language even more
            result['message'] = self._simplify_language(result['message'])
            result['suggestions'] = [self._simplify_language(s) for s in result['suggestions'][:2]]
            # Only show the simplest recovery command
            if result['recovery_commands']:
                result['recovery_commands'] = [result['recovery_commands'][0]]
        
        elif persona == 'maya':
            # Very concise
            result['suggestions'] = result['suggestions'][:1]
            
        elif persona == 'dr_sarah':
            # Add technical details
            if error.technical:
                result['technical_details'] = error.technical
        
        elif persona == 'alex':
            # Format for screen readers
            result['screen_reader_text'] = self._format_for_screen_reader(error)
        
        elif persona == 'viktor':
            # Use simpler English
            result['message'] = self._simplify_language(result['message'])
            result['suggestions'] = [self._simplify_language(s) for s in result['suggestions']]
        
        return result
    
    def _simplify_language(self, text: str) -> str:
        """Simplify language for less technical users"""
        replacements = {
            'administrator': 'special permission',
            'privileges': 'permissions',
            'configuration': 'settings',
            'repository': 'package source',
            'dependency': 'required program',
            'conflict': 'problem',
            'syntax': 'formatting',
            'attribute': 'name',
            'recursive': 'circular',
            'evaluation': 'processing'
        }
        
        result = text
        for complex_word, simple_word in replacements.items():
            result = re.sub(complex_word, simple_word, result, flags=re.IGNORECASE)
        
        return result
    
    def _format_for_screen_reader(self, error: CommandError) -> str:
        """Format error for screen reader users"""
        parts = [
            f"Error: {error.user_message}",
            f"Category: {error.category.value.replace('_', ' ')}",
            f"Suggestions: {'; '.join(error.suggestions)}"
        ]
        
        if error.recovery_commands:
            parts.append(f"Recovery options: {len(error.recovery_commands)} available")
        
        return ". ".join(parts)


def main():
    """Test the educational error handler"""
    handler = EducationalErrorHandler()
    
    # Test various errors
    test_errors = [
        ("error: attribute 'firefox' missing", {'command': 'nix profile install nixpkgs#firefox'}),
        ("error: permission denied", {'command': 'nixos-rebuild switch'}),
        ("error: no space left on device", {}),
        ("error: infinite recursion encountered", {}),
        ("error: SSL certificate problem", {}),
        ("error: network timeout", {})
    ]
    
    print("🎓 Educational Error Handler Test\n")
    
    for error_msg, context in test_errors:
        print(f"Original error: {error_msg}")
        print("-" * 50)
        
        cmd_error = handler.analyze_error(error_msg, context)
        
        print(f"User message: {cmd_error.user_message}")
        print(f"Category: {cmd_error.category.value}")
        print("\nSuggestions:")
        for i, suggestion in enumerate(cmd_error.suggestions, 1):
            print(f"  {i}. {suggestion}")
        
        if cmd_error.recovery_commands:
            print("\nRecovery commands:")
            for cmd in cmd_error.recovery_commands:
                print(f"  • {cmd['description']}")
                print(f"    $ {cmd['command']}")
        
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()