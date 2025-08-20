#!/usr/bin/env python3
"""Add missing methods that TUI expects from backend."""

from pathlib import Path
import re

from typing import List, Dict, Optional
def add_tui_methods():
    """Add methods TUI needs to the backend."""
    
    print("🔧 Adding TUI-required methods to backend\n")
    
    engine_file = Path('src/luminous_nix/core/engine.py')
    
    # Methods to add
    new_methods = '''
    def get_current_context(self) -> Dict[str, Any]:
        """Get current context information for TUI display.
        
        Returns:
            Dict containing current state, settings, and context
        """
        return {
            "personality": self.get_current_personality(),
            "native_api_enabled": self._has_python_api,
            "current_directory": str(Path.cwd()),
            "nixos_version": self._get_nixos_version() if hasattr(self, '_get_nixos_version') else "Unknown",
            "generation": self._get_current_generation() if hasattr(self, '_get_current_generation') else "Unknown",
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings for TUI configuration panel.
        
        Returns:
            Dict of current settings
        """
        return {
            "personality": self.get_current_personality(),
            "execute_commands": False,  # Safety first
            "show_explanations": True,
            "native_api": self._has_python_api,
            "voice_enabled": False,  # For future
            "theme": "dark",  # TUI theme
        }
    
    def execute_command(self, command: str, dry_run: bool = True) -> Dict[str, Any]:
        """Execute a Nix command with safety checks.
        
        Args:
            command: The command to execute
            dry_run: If True, only show what would be done
            
        Returns:
            Dict with success, output, and error information
        """
        # Use the existing executor
        result = self.executor.execute(command, dry_run=dry_run)
        
        return {
            "success": result.success if hasattr(result, 'success') else False,
            "output": result.output if hasattr(result, 'output') else "",
            "error": result.error if hasattr(result, 'error') else None,
            "command": command,
            "dry_run": dry_run
        }
    
    def get_suggestions(self, partial: str, context: Optional[str] = None) -> List[str]:
        """Get autocomplete suggestions for partial input.
        
        Args:
            partial: Partial text to complete
            context: Optional context (like current command type)
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Package name suggestions
        if context == "package" or "install" in partial.lower():
            packages = self.search_packages(partial, limit=5)
            suggestions.extend([p.name for p in packages])
        
        # Command suggestions
        command_starters = [
            "install", "remove", "search", "update", "rollback",
            "list generations", "show installed", "help"
        ]
        for cmd in command_starters:
            if cmd.startswith(partial.lower()):
                suggestions.append(cmd)
        
        return suggestions[:10]  # Limit suggestions
    
    def get_current_personality(self) -> str:
        """Get the current personality setting."""
        # Default personality
        return "balanced"
    
    def _get_nixos_version(self) -> str:
        """Get NixOS version (if not already defined)."""
        if hasattr(super(), '_get_nixos_version'):
            return super()._get_nixos_version()
        
        try:
            import subprocess
            result = subprocess.run(['nixos-version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        return "Unknown"
    
    def _get_current_generation(self) -> str:
        """Get current system generation."""
        try:
            import subprocess
            result = subprocess.run(
                ['nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\\n')
                for line in lines:
                    if '(current)' in line:
                        return line.split()[0]
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        return "Unknown"
'''
    
    # Read current content
    with open(engine_file) as f:
        content = f.read()
    
    # Check which methods are missing
    missing_methods = []
    for method in ['get_current_context', 'get_settings', 'execute_command', 'get_suggestions']:
        if f'def {method}(' not in content:
            missing_methods.append(method)
    
    if not missing_methods:
        print("✅ All TUI methods already present!")
        return
    
    print(f"Adding {len(missing_methods)} missing methods: {', '.join(missing_methods)}")
    
    # Find where to insert (before the last method or at end of class)
    # Look for the search_packages method we just added
    insert_pos = content.find('def search_packages(')
    if insert_pos > 0:
        # Find the end of search_packages method
        method_end = content.find('\n\n    def ', insert_pos)
        if method_end == -1:
            # It's the last method, find the end
            method_end = content.find('\n\nclass', insert_pos)
            if method_end == -1:
                method_end = len(content) - 2
        
        # Insert the new methods
        content = content[:method_end] + '\n' + new_methods + content[method_end:]
    else:
        print("❌ Could not find insertion point")
        return
    
    # Write back
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ Added missing TUI methods to backend!")
    
    # Also need to fix the async issue
    print("\n🔧 Fixing async process_request issue...")
    
    # The process_request is async, so we need to make it sync or handle async in TUI
    # Let's check if it's really async
    if 'async def process_request' in content:
        print("  Note: process_request is async - TUI will need to handle this")
    else:
        print("  process_request appears to be sync")

if __name__ == '__main__':
    add_tui_methods()