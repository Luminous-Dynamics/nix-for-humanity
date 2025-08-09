#!/usr/bin/env python3
"""
from typing import Optional
Discover and test nixos-rebuild-ng Python API
This is the first step in our Native Python-Nix Interface implementation
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

class NixOSRebuildAPIDiscovery:
    """Discover and explore the nixos-rebuild-ng Python API"""
    
    def __init__(self):
        self.nixos_rebuild_path = None
        self.module_path = None
        
    def find_nixos_rebuild_binary(self) -> Optional[Path]:
        """Find the nixos-rebuild binary location"""
        try:
            result = subprocess.run(
                ['which', 'nixos-rebuild'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                binary_path = Path(result.stdout.strip())
                # Follow symlinks to real location
                real_path = binary_path.resolve()
                print(f"✅ Found nixos-rebuild at: {real_path}")
                return real_path
        except Exception as e:
            print(f"❌ Error finding nixos-rebuild: {e}")
        return None
        
    def find_python_module(self, binary_path: Path) -> Optional[Path]:
        """Find the Python module path from the binary location"""
        # The binary is typically at /nix/store/hash-nixos-rebuild-ng-version/bin/nixos-rebuild
        # The Python module should be at /nix/store/hash-nixos-rebuild-ng-version/lib/pythonX.Y/site-packages
        store_path = binary_path.parent.parent  # Go up to the store package root
        
        # Look for Python site-packages
        for python_dir in store_path.glob("lib/python*/site-packages"):
            if (python_dir / "nixos_rebuild").exists():
                print(f"✅ Found Python module at: {python_dir}")
                return python_dir
                
        # Alternative locations
        alternative_paths = [
            store_path / "lib" / "python3.11" / "site-packages",
            store_path / "lib" / "python3.12" / "site-packages",
            store_path / "lib" / "python3.13" / "site-packages",
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists() and (alt_path / "nixos_rebuild").exists():
                print(f"✅ Found Python module at: {alt_path}")
                return alt_path
                
        return None
        
    def import_module(self, module_path: Path) -> bool:
        """Try to import the nixos_rebuild module"""
        try:
            # Add to Python path
            sys.path.insert(0, str(module_path))
            
            # Try importing
            import nixos_rebuild
            print(f"✅ Successfully imported nixos_rebuild module!")
            
            # Explore what's available
            print("\n📦 Available modules:")
            for item in dir(nixos_rebuild):
                if not item.startswith('_'):
                    print(f"  - {item}")
                    
            # Try to import submodules
            try:
                from nixos_rebuild import models, nix, services
                print("\n✅ Successfully imported submodules: models, nix, services")
                
                # Explore models
                print("\n📊 Available models:")
                for item in dir(models):
                    if not item.startswith('_'):
                        obj = getattr(models, item)
                        print(f"  - {item}: {type(obj).__name__}")
                        
                # Explore nix module
                print("\n🔧 Available nix functions:")
                for item in dir(nix):
                    if not item.startswith('_') and callable(getattr(nix, item)):
                        print(f"  - {item}()")
                        
                # Explore services
                print("\n🌐 Available services:")
                for item in dir(services):
                    if not item.startswith('_'):
                        print(f"  - {item}")
                        
            except ImportError as e:
                print(f"⚠️  Could not import submodules: {e}")
                
            return True
            
        except ImportError as e:
            print(f"❌ Failed to import nixos_rebuild: {e}")
            return False
            
    def explore_api_capabilities(self):
        """Explore what we can do with the API"""
        try:
            from nixos_rebuild import models
            
            print("\n🎯 Exploring API capabilities:")
            
            # Check available actions
            if hasattr(models, 'Action'):
                print("\n📋 Available actions:")
                for action in models.Action:
                    print(f"  - {action.name}: {action.value}")
                    
            # Check profile handling
            if hasattr(models, 'Profile'):
                print("\n👤 Profile capabilities:")
                print(f"  - Profile class available for system profile management")
                
            # Check build attributes
            if hasattr(models, 'BuildAttr'):
                print("\n🏗️  Build attribute handling available")
                
            # Check flake support
            if hasattr(models, 'Flake'):
                print("\n❄️  Flake support detected")
                
        except Exception as e:
            print(f"⚠️  Error exploring API: {e}")
            
    def create_example_integration(self):
        """Create an example of how we'll integrate this"""
        print("\n💡 Example integration code:")
        
        example_code = '''
# Example: Native Python-Nix Interface for Nix for Humanity

from nixos_rebuild import models, nix, services
from nixos_rebuild.models import Action, Profile

class NixForHumanityNativeBackend:
    """Direct Python API integration with nixos-rebuild-ng"""
    
    def __init__(self):
        self.profile = Profile.from_arg("system")
        
    async def update_system(self, dry_run: bool = False):
        """Update NixOS system using native API"""
        action = Action.BUILD if dry_run else Action.SWITCH
        
        # Build the system
        build_attr = models.BuildAttr(
            attr="config.system.build.toplevel",
            file=None
        )
        
        try:
            # Native API call - no subprocess!
            path = await nix.build(build_attr, self.profile)
            
            if not dry_run:
                # Apply the configuration
                await nix.switch_to_configuration(path, action, self.profile)
                
            return {"success": True, "path": path}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def rollback_system(self):
        """Rollback to previous generation"""
        try:
            await nix.rollback(self.profile)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
'''
        
        print(example_code)
        
    def run_discovery(self):
        """Run the complete discovery process"""
        print("🔍 Starting NixOS Rebuild API Discovery...\n")
        
        # Step 1: Find binary
        binary_path = self.find_nixos_rebuild_binary()
        if not binary_path:
            print("❌ Could not find nixos-rebuild binary")
            return False
            
        # Step 2: Find Python module
        module_path = self.find_python_module(binary_path)
        if not module_path:
            print("❌ Could not find Python module")
            return False
            
        self.module_path = module_path
        
        # Step 3: Import module
        if not self.import_module(module_path):
            return False
            
        # Step 4: Explore capabilities
        self.explore_api_capabilities()
        
        # Step 5: Show integration example
        self.create_example_integration()
        
        print(f"\n✨ Discovery complete!")
        print(f"📁 Module path for imports: {self.module_path}")
        return True
        

def main():
    """Main entry point"""
    discovery = NixOSRebuildAPIDiscovery()
    
    if discovery.run_discovery():
        print("\n🚀 Next steps:")
        print("1. Create NixForHumanityNativeBackend class")
        print("2. Replace subprocess calls with native API")
        print("3. Add progress streaming and error handling")
        print("4. Test with real NixOS operations")
    else:
        print("\n❌ Discovery failed. Falling back to subprocess approach.")
        

if __name__ == "__main__":
    main()