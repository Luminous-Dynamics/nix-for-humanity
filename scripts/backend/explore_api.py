#!/usr/bin/env python3
"""Explore the nixos-rebuild API"""

import sys
sys.path.insert(0, "/nix/store/lwmjrs31xfgn2q1a0b9f81a61ka4ym6z-nixos-rebuild-ng-0.0.0/lib/python3.13/site-packages")

from nixos_rebuild import models
import inspect

print("🔍 Exploring nixos-rebuild API\n")

# Check Profile class
print("📋 Profile class:")
print(f"  Attributes: {[a for a in dir(models.Profile) if not a.startswith('_')]}")

# Check methods with signatures
for name in dir(models.Profile):
    if not name.startswith('_') and callable(getattr(models.Profile, name)):
        method = getattr(models.Profile, name)
        try:
            sig = inspect.signature(method)
            print(f"  {name}{sig}")
        except Exception:
            print(f"  {name}()")

# Check Profile creation
print("\n📋 Creating Profile:")
try:
    # Try different ways
    profile = models.Profile(system=True)
    print(f"✅ Profile(system=True): {profile}")
except Exception as e:
    print(f"❌ Profile(system=True): {e}")

try:
    profile = models.Profile.from_arg("system")
    print(f"✅ Profile.from_arg('system'): {profile}")
except Exception as e:
    print(f"❌ Profile.from_arg('system'): {e}")

# Check other useful classes
print("\n📋 Other useful items in models:")
for name in dir(models):
    if not name.startswith('_') and name not in ['Profile', 'Action']:
        item = getattr(models, name)
        if hasattr(item, '__name__'):
            print(f"  {name}: {type(item).__name__}")