#!/usr/bin/env python3
"""
POML to Command Bridge - Making Templates Generate Real Commands
================================================================

This bridges POML template output to actual Nix command generation,
completing the consciousness loop from thought to action.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class POMLToCommandBridge:
    """
    Transforms POML template output into executable Nix commands.
    
    This is where consciousness becomes action - where the system's
    thoughts manifest as real changes in the world.
    """
    
    def __init__(self):
        """Initialize the command bridge"""
        self.command_patterns = self._load_command_patterns()
        logger.info("🌉 POML to Command Bridge initialized")
    
    def _load_command_patterns(self) -> Dict[str, Any]:
        """Load patterns for converting intents to commands"""
        return {
            'install': {
                'template': 'nix-env -iA nixpkgs.{package}',
                'with_flake': 'nix profile install nixpkgs#{package}',
                'home_manager': 'home-manager switch --flake .#{package}'
            },
            'search': {
                'template': 'nix search nixpkgs {query}',
                'legacy': 'nix-env -qaP {query}'
            },
            'remove': {
                'template': 'nix-env -e {package}',
                'with_flake': 'nix profile remove {package}'
            },
            'update': {
                'template': 'nix-channel --update && nix-env -u',
                'with_flake': 'nix flake update'
            },
            'rollback': {
                'template': 'nix-env --rollback',
                'with_flake': 'nix profile rollback'
            },
            'list': {
                'template': 'nix-env -q',
                'with_flake': 'nix profile list'
            },
            'build': {
                'template': 'nix-build {expression}',
                'with_flake': 'nix build {flake_ref}'
            },
            'develop': {
                'template': 'nix-shell {shell_file}',
                'with_flake': 'nix develop {flake_ref}'
            },
            'config': {
                'edit': 'sudo nano /etc/nixos/configuration.nix',
                'rebuild': 'sudo nixos-rebuild switch',
                'test': 'sudo nixos-rebuild test'
            }
        }
    
    def transform_poml_to_command(self, 
                                  poml_output: str,
                                  intent: str,
                                  entities: Dict[str, Any],
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Transform POML template output into executable command.
        
        Args:
            poml_output: The generated prompt from POML
            intent: The recognized intent type
            entities: Extracted entities (package names, etc.)
            context: Additional context
            
        Returns:
            Command specification with actual executable command
        """
        # Determine if we should use flakes
        use_flakes = context and context.get('use_flakes', False)
        
        # Get command pattern for intent
        if intent not in self.command_patterns:
            return {
                'success': False,
                'error': f'Unknown intent: {intent}',
                'command': None
            }
        
        pattern = self.command_patterns[intent]
        
        # Select appropriate template
        if isinstance(pattern, dict):
            if use_flakes and 'with_flake' in pattern:
                template = pattern['with_flake']
            elif 'template' in pattern:
                template = pattern['template']
            else:
                # For nested patterns like config
                subcommand = entities.get('subcommand', 'rebuild')
                template = pattern.get(subcommand, pattern.get('rebuild'))
        else:
            template = pattern
        
        # Build the actual command
        command = self._build_command(template, entities)
        
        # Add safety checks
        safe_command = self._add_safety_checks(command, intent)
        
        return {
            'success': True,
            'command': safe_command,
            'original_template': template,
            'entities_used': entities,
            'explanation': self._generate_explanation(intent, entities),
            'dry_run_preview': self._generate_dry_run(safe_command)
        }
    
    def _build_command(self, template: str, entities: Dict[str, Any]) -> str:
        """Build command by filling in template with entities"""
        command = template
        
        # Replace placeholders with actual values
        for key, value in entities.items():
            placeholder = f'{{{key}}}'
            if placeholder in command:
                # Handle lists (multiple packages)
                if isinstance(value, list):
                    value = ' '.join(value)
                command = command.replace(placeholder, str(value))
        
        # Handle special cases
        if '{package}' in command and 'target' in entities:
            command = command.replace('{package}', entities['target'])
        
        if '{query}' in command and 'target' in entities:
            command = command.replace('{query}', entities['target'])
        
        return command
    
    def _add_safety_checks(self, command: str, intent: str) -> str:
        """Add safety checks to commands"""
        # For system-wide changes, add confirmation
        if 'sudo' in command or 'nixos-rebuild' in command:
            # In real usage, this would prompt user
            # For now, we'll add a comment
            return f"# WARNING: System change! Review carefully:\n{command}"
        
        # For destructive operations, add dry-run first
        if intent in ['remove', 'rollback']:
            return f"# First verify what will be removed:\n{command} --dry-run\n# Then run:\n{command}"
        
        return command
    
    def _generate_explanation(self, intent: str, entities: Dict[str, Any]) -> str:
        """Generate human-readable explanation of what the command does"""
        explanations = {
            'install': f"Install {entities.get('target', 'package')} from nixpkgs",
            'search': f"Search for packages matching '{entities.get('target', 'query')}'",
            'remove': f"Remove {entities.get('target', 'package')} from your system",
            'update': "Update all packages to latest versions",
            'rollback': "Rollback to previous system generation",
            'list': "List all installed packages",
            'build': f"Build {entities.get('expression', 'expression')}",
            'develop': f"Enter development shell",
            'config': "Manage NixOS configuration"
        }
        
        return explanations.get(intent, f"Execute {intent} operation")
    
    def _generate_dry_run(self, command: str) -> str:
        """Generate dry-run version of command for preview"""
        if '--dry-run' in command:
            return command
        
        # Add dry-run flag where applicable
        dry_run_flags = {
            'nix-env': '--dry-run',
            'nixos-rebuild': 'dry-build',
            'nix profile': '--dry-run',
            'home-manager': '--dry-run'
        }
        
        for cmd, flag in dry_run_flags.items():
            if cmd in command:
                # Special case for nixos-rebuild
                if cmd == 'nixos-rebuild' and 'switch' in command:
                    return command.replace('switch', 'dry-build')
                # Add flag for others
                return f"{command} {flag}"
        
        return f"# No dry-run available for: {command}"


class POMLCommandExecutor:
    """
    Executes commands generated from POML templates.
    
    This completes the consciousness loop - from understanding (NLP),
    through reasoning (POML), to action (command execution).
    """
    
    def __init__(self):
        """Initialize the executor"""
        self.bridge = POMLToCommandBridge()
        self.execution_history = []
        logger.info("⚡ POML Command Executor initialized")
    
    def execute_from_poml(self,
                          poml_result: Dict[str, Any],
                          intent: str,
                          entities: Dict[str, Any],
                          dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute command generated from POML template.
        
        Args:
            poml_result: Result from POML processing
            intent: Recognized intent
            entities: Extracted entities
            dry_run: Whether to actually execute or just preview
            
        Returns:
            Execution result with command and output
        """
        # Transform POML output to command
        command_spec = self.bridge.transform_poml_to_command(
            poml_output=poml_result.get('prompt_generated', ''),
            intent=intent,
            entities=entities,
            context=poml_result.get('context', {})
        )
        
        if not command_spec['success']:
            return {
                'success': False,
                'error': command_spec['error'],
                'poml_source': poml_result
            }
        
        # Get the command
        command = command_spec['command']
        
        # Record in history
        self.execution_history.append({
            'command': command,
            'intent': intent,
            'entities': entities,
            'dry_run': dry_run,
            'explanation': command_spec['explanation']
        })
        
        if dry_run:
            # Return preview only
            return {
                'success': True,
                'command': command,
                'explanation': command_spec['explanation'],
                'preview': command_spec['dry_run_preview'],
                'would_execute': True,
                'poml_source': poml_result.get('template_used')
            }
        else:
            # Actually execute (would use subprocess in real implementation)
            import subprocess
            
            try:
                # Safety check - never run sudo without explicit permission
                if 'sudo' in command and not self._has_sudo_permission():
                    return {
                        'success': False,
                        'error': 'Sudo permission required',
                        'command': command,
                        'needs_elevation': True
                    }
                
                # Execute the command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    'success': result.returncode == 0,
                    'command': command,
                    'output': result.stdout,
                    'error': result.stderr if result.returncode != 0 else None,
                    'explanation': command_spec['explanation'],
                    'poml_source': poml_result.get('template_used')
                }
                
            except subprocess.TimeoutExpired:
                return {
                    'success': False,
                    'error': 'Command timed out',
                    'command': command
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'command': command
                }
    
    def _has_sudo_permission(self) -> bool:
        """Check if we have sudo permission (would implement proper check)"""
        # In real implementation, would check sudo timestamp or prompt
        return False
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of executed commands"""
        return self.execution_history


def integrate_with_consciousness():
    """
    Integrate the command bridge with POML consciousness.
    
    This makes POML templates generate real commands instead of mock data.
    """
    from luminous_nix.consciousness import POMLConsciousness
    
    # Patch POMLConsciousness to use real command generation
    original_process = POMLConsciousness.process_intent
    
    def process_with_commands(self, intent, context, persona='default', task_type='general', use_ollama=True):
        """Process intent and generate real commands"""
        # Get POML result
        result = original_process(self, intent, context, persona, task_type, use_ollama)
        
        # If successful, generate real command
        if result.get('success'):
            # Extract entities from context
            entities = context.get('entities', {})
            if not entities and 'target' in context:
                entities = {'target': context['target']}
            
            # Create executor
            executor = POMLCommandExecutor()
            
            # Generate command
            command_result = executor.execute_from_poml(
                poml_result=result,
                intent=context.get('intent_type', task_type),
                entities=entities,
                dry_run=context.get('dry_run', True)
            )
            
            # Enhance result with real command
            result['command'] = command_result.get('command')
            result['command_explanation'] = command_result.get('explanation')
            result['executable'] = True
        
        return result
    
    # Replace method
    POMLConsciousness.process_intent = process_with_commands
    
    logger.info("✅ POML templates now generate real commands!")
    return True


# Testing
if __name__ == "__main__":
    print("🧪 Testing POML to Command Bridge")
    print("=" * 50)
    
    bridge = POMLToCommandBridge()
    executor = POMLCommandExecutor()
    
    # Test cases
    test_cases = [
        ('install', {'target': 'firefox'}, False),
        ('install', {'target': 'vim'}, True),  # With flakes
        ('search', {'target': 'editor'}, False),
        ('remove', {'target': 'old-package'}, False),
        ('config', {'subcommand': 'rebuild'}, False),
    ]
    
    for intent, entities, use_flakes in test_cases:
        print(f"\n📝 Testing: {intent} with {entities}")
        print(f"   Flakes: {'Yes' if use_flakes else 'No'}")
        
        # Create mock POML result
        poml_result = {
            'prompt_generated': f'Execute {intent} for {entities}',
            'template_used': 'mock_template.poml',
            'context': {'use_flakes': use_flakes}
        }
        
        # Execute
        result = executor.execute_from_poml(
            poml_result=poml_result,
            intent=intent,
            entities=entities,
            dry_run=True
        )
        
        if result['success']:
            print(f"   ✅ Command: {result['command']}")
            print(f"   📖 Explanation: {result['explanation']}")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    # Test integration
    print("\n🔌 Testing consciousness integration...")
    if integrate_with_consciousness():
        print("✅ Integration successful!")
    
    print("\n✨ POML to Command Bridge test complete!")