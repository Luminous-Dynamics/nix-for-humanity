#!/usr/bin/env python3
import os
import tarfile
import hashlib
from pathlib import Path

version = "1.0.0"
project_root = Path(__file__).parent.parent.parent

# Files to include in release
include_patterns = [
    "bin/",
    "src/",
    "backend/",
    "frontends/",
    "docs/",
    "flake.nix",
    "flake.lock", 
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "VERSION",
    "CHANGELOG.md",
]

# Files to exclude
exclude_patterns = [
    "__pycache__",
    "*.pyc",
    ".git",
    ".pytest_cache",
    "*.egg-info",
    "dist/",
    "build/",
    ".env",
    "*.log",
]

def should_include(path):
    path_str = str(path)
    
    # Check excludes first
    for pattern in exclude_patterns:
        if pattern in path_str:
            return False
    
    # Check includes
    for pattern in include_patterns:
        if path_str.startswith(pattern) or pattern in path_str:
            return True
    
    return False

# Create tarball
output_file = f"nix-for-humanity-v{version}.tar.gz"
print(f"Creating {output_file}...")

with tarfile.open(output_file, "w:gz") as tar:
    for root, dirs, files in os.walk(project_root):
        # Filter directories
        dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_patterns)]
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)
            
            if should_include(relative_path):
                print(f"  Adding: {relative_path}")
                tar.add(file_path, arcname=f"nix-for-humanity-v{version}/{relative_path}")

# Generate checksum
print("\nGenerating checksum...")
with open(output_file, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()

with open(f"{output_file}.sha256", "w") as f:
    f.write(f"{sha256}  {output_file}\n")

print(f"\n✅ Release package created: {output_file}")
print(f"✅ Checksum: {sha256}")
