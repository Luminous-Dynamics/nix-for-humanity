#!/usr/bin/env python3
"""
Build a fast package cache for common searches
"""

import json
import subprocess
from pathlib import Path

# Common package prefixes to cache
COMMON_SEARCHES = [
    "vim", "emacs", "nano", "firefox", "chromium", "brave",
    "python", "nodejs", "rust", "gcc", "git", "docker",
    "vscode", "neovim", "terminal", "shell", "zsh", "bash",
    "wget", "curl", "tree", "htop", "btop", "tmux", "screen"
]

def build_cache():
    """Build a cache of common packages"""
    print("Building package cache...")
    
    all_packages = {}
    
    for term in COMMON_SEARCHES:
        print(f"  Caching packages for '{term}'...")
        try:
            # Use nix-env -qa with a short timeout
            result = subprocess.run(
                ["nix-env", "-qa", f"*{term}*"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[:20]:  # Limit per term
                    if line.strip():
                        all_packages[line.strip()] = {"name": line.strip(), "terms": [term]}
        except subprocess.TimeoutExpired:
            print(f"    Timeout for '{term}', skipping...")
        except Exception as e:
            print(f"    Error for '{term}': {e}")
    
    # Save cache
    cache = {
        "packages": list(all_packages.values()),
        "count": len(all_packages)
    }
    
    cache_file = Path("package_cache.json")
    cache_file.write_text(json.dumps(cache, indent=2))
    print(f"✅ Cached {len(all_packages)} packages to {cache_file}")

if __name__ == "__main__":
    build_cache()