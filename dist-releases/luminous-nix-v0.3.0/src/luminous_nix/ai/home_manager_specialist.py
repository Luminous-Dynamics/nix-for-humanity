#!/usr/bin/env python3
"""
HomeManagerSpecialist - Handles home-manager specific operations
Part of v0.3.1 critical fixes based on user feedback
"""

from typing import Dict, List, Optional
import re

class HomeManagerSpecialist:
    """Specialist for home-manager operations"""
    
    def __init__(self):
        self.patterns = {
            'switch': [
                r'home[\s-]?manager\s+switch',
                r'apply\s+home[\s-]?configuration',
                r'update\s+home[\s-]?config',
                r'reload\s+home[\s-]?manager',
            ],
            'rollback': [
                r'home[\s-]?manager\s+rollback',
                r'rollback\s+home[\s-]?configuration',
                r'undo\s+home[\s-]?manager',
                r'revert\s+home[\s-]?config',
            ],
            'generations': [
                r'home[\s-]?manager\s+generations',
                r'list\s+home[\s-]?generations',
                r'show\s+home[\s-]?manager\s+history',
                r'home[\s-]?config\s+history',
            ],
            'edit': [
                r'edit\s+home[\s-]?configuration',
                r'modify\s+home[\s-]?config',
                r'configure\s+home[\s-]?manager',
                r'home[\s-]?manager\s+config',
            ],
            'news': [
                r'home[\s-]?manager\s+news',
                r'home[\s-]?manager\s+changes',
                r'what\'?s?\s+new\s+home[\s-]?manager',
            ],
            'packages': [
                r'home[\s-]?manager\s+packages',
                r'list\s+home[\s-]?packages',
                r'installed\s+home[\s-]?programs',
            ],
            'expire': [
                r'expire\s+home[\s-]?generations',
                r'clean\s+home[\s-]?generations',
                r'remove\s+old\s+home[\s-]?configs',
            ],
        }
        
        self.commands = {
            'switch': 'home-manager switch',
            'rollback': 'home-manager switch --rollback',
            'generations': 'home-manager generations',
            'edit': 'nano ~/.config/home-manager/home.nix',
            'news': 'home-manager news',
            'packages': 'home-manager packages',
            'expire': 'home-manager expire-generations "-30 days"',
        }
        
        self.explanations = {
            'switch': 'Apply the current home-manager configuration',
            'rollback': 'Rollback to the previous home-manager generation',
            'generations': 'List all home-manager generations',
            'edit': 'Edit the home-manager configuration file',
            'news': 'Show news about home-manager updates',
            'packages': 'List packages managed by home-manager',
            'expire': 'Remove home-manager generations older than 30 days',
        }
    
    def can_handle(self, query: str) -> bool:
        """Check if this specialist can handle the query"""
        query_lower = query.lower()
        
        # Check for home-manager keywords
        if any(kw in query_lower for kw in ['home-manager', 'home manager', 'home config']):
            return True
        
        # Check specific patterns
        for patterns in self.patterns.values():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return True
        
        return False
    
    def handle_query(self, query: str) -> Dict:
        """Process a home-manager query"""
        query_lower = query.lower()
        
        # Find the best matching operation
        best_match = None
        best_score = 0
        
        for operation, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Calculate match score based on pattern specificity
                    score = len(pattern)
                    if score > best_score:
                        best_score = score
                        best_match = operation
        
        if best_match:
            return {
                'command': self.commands[best_match],
                'explanation': self.explanations[best_match],
                'category': 'home-manager',
                'confidence': min(0.95, 0.7 + (best_score / 100)),
                'specialist': 'HomeManagerSpecialist',
                'alternatives': self._get_alternatives(best_match),
            }
        
        # Default fallback for unrecognized home-manager queries
        return {
            'command': 'home-manager --help',
            'explanation': 'Show home-manager help to find the right command',
            'category': 'home-manager',
            'confidence': 0.5,
            'specialist': 'HomeManagerSpecialist',
            'alternatives': [
                'home-manager switch',
                'home-manager generations',
                'home-manager news',
            ],
        }
    
    def _get_alternatives(self, operation: str) -> List[str]:
        """Get alternative commands for an operation"""
        alternatives = []
        
        if operation == 'switch':
            alternatives = [
                'home-manager switch -b backup',  # Create backup
                'home-manager build',  # Build without switching
                'home-manager switch --show-trace',  # Debug mode
            ]
        elif operation == 'rollback':
            alternatives = [
                'home-manager generations',  # List to choose from
                'home-manager switch -g <generation>',  # Switch to specific
            ]
        elif operation == 'expire':
            alternatives = [
                'home-manager expire-generations "-7 days"',
                'home-manager expire-generations "-14 days"',
                'nix-collect-garbage -d',  # System-wide cleanup
            ]
        
        return alternatives
    
    def get_common_tasks(self) -> List[Dict]:
        """Return common home-manager tasks for help/suggestions"""
        return [
            {
                'task': 'Apply configuration changes',
                'command': 'home-manager switch',
                'frequency': 'very_common',
            },
            {
                'task': 'Rollback to previous config',
                'command': 'home-manager switch --rollback',
                'frequency': 'common',
            },
            {
                'task': 'Edit configuration',
                'command': 'nano ~/.config/home-manager/home.nix',
                'frequency': 'common',
            },
            {
                'task': 'List generations',
                'command': 'home-manager generations',
                'frequency': 'common',
            },
            {
                'task': 'Clean old generations',
                'command': 'home-manager expire-generations "-30 days"',
                'frequency': 'occasional',
            },
            {
                'task': 'View recent changes',
                'command': 'home-manager news',
                'frequency': 'occasional',
            },
        ]