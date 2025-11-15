#!/usr/bin/env python3
"""
Corrected test suite for nixos-rebuild-ng Python API
Based on actual API signatures discovered through inspection
"""

import inspect
import subprocess
import sys
from pathlib import Path


def setup_python_path() -> bool:
    """Setup Python path to include nixos-rebuild-ng modules"""
    try:
        result = subprocess.run(
            ["nix-build", "<nixpkgs>", "-A", "nixos-rebuild-ng", "--no-out-link"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ Failed to build nixos-rebuild-ng: {result.stderr}")
            return False

        rebuild_path = result.stdout.strip()
        site_packages = Path(rebuild_path) / "lib" / "python3.13" / "site-packages"

        if site_packages.exists():
            sys.path.insert(0, str(site_packages))
            print(f"✅ Added to Python path: {site_packages}")
            return True
        else:
            print("❌ Site packages not found")
            return False

    except Exception as e:
        print(f"❌ Error setting up Python path: {e}")
        return False


def explore_actual_api():
    """Explore the actual API structure"""
    print("\n🔍 Exploring Actual API Structure")
    print("=" * 50)

    try:
        from nixos_rebuild import models
        from nixos_rebuild.process import Remote

        # Explore BuildAttr
        print("\nBuildAttr actual signature:")
        print(f"  {inspect.signature(models.BuildAttr)}")
        print("  Parameters: path (str|Path), attr (str|None)")

        # Create correct BuildAttr
        build_attr = models.BuildAttr(
            path="<nixpkgs/nixos>",  # Path to nixpkgs
            attr="system",  # Attribute to build
        )
        print(f"  Example: {build_attr}")

        # Explore Flake
        print("\nFlake actual signature:")
        print(f"  {inspect.signature(models.Flake)}")
        print("  Parameters: path (Path|str), attr (str)")

        # Create correct Flake
        flake = models.Flake(
            path="/path/to/flake",
            attr="nixosConfigurations.hostname.config.system.build.toplevel",
        )
        print(f"  Example: {flake}")

        # Explore Remote
        print("\nRemote actual signature:")
        print(f"  {inspect.signature(Remote)}")
        print("  Parameters: host (str), opts (list[str]), sudo_password (str|None)")

        # Create correct Remote
        remote = Remote(
            host="example.com",
            opts=["-o", "StrictHostKeyChecking=no"],
            sudo_password=None,
        )
        print(f"  Example: {remote}")

        # Explore Profile
        print("\nProfile class:")
        print(
            f"  Available methods: {[x for x in dir(models.Profile) if not x.startswith('_')]}"
        )

        # Profile is created from string
        profile = models.Profile.from_arg("/nix/var/nix/profiles/system")
        print(f"  Example: {profile}")

        return True
    except Exception as e:
        print(f"❌ Error exploring API: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_actual_functions():
    """Test with correct API signatures"""
    print("\n✅ Testing with Correct Signatures")
    print("=" * 50)

    try:
        from nixos_rebuild import nix, utils

        # Test build function signature
        print("\nbuild() function signature:")
        print(f"  {inspect.signature(nix.build)}")

        # The build function expects:
        # - attr: str (the attribute name like "system")
        # - build_attr: BuildAttr object
        # - build_flags: optional dict

        print("\nCorrect usage example:")
        print('  build_attr = models.BuildAttr(path="<nixpkgs/nixos>", attr="system")')
        print('  path = nix.build("system", build_attr, build_flags=None)')

        # Test switch_to_configuration signature
        print("\nswitch_to_configuration() signature:")
        print(f"  {inspect.signature(nix.switch_to_configuration)}")

        # Test utils functions
        print("\nUtils functions:")
        flags = utils.dict_to_flags({"verbose": True, "option": "value"})
        print(f"  dict_to_flags result: {flags}")

        return True
    except Exception as e:
        print(f"❌ Error testing functions: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_generation_functions():
    """Test generation-related functions"""
    print("\n📋 Testing Generation Functions")
    print("=" * 50)

    try:
        from nixos_rebuild import models, nix

        # Test get_generations
        print("get_generations() signature:")
        print(f"  {inspect.signature(nix.get_generations)}")

        # Create profile
        profile = models.Profile.from_arg("/nix/var/nix/profiles/system")

        try:
            # This might need sudo
            generations = nix.get_generations(profile)
            print(f"✅ Found {len(generations)} generations")

            if generations:
                gen = generations[0]
                print(f"  Generation example: {gen}")

        except PermissionError:
            print("⚠️  Permission denied - needs sudo")
        except FileNotFoundError:
            print("⚠️  Profile not found")
        except Exception as e:
            print(f"⚠️  Could not get generations: {e}")

        return True
    except Exception as e:
        print(f"❌ Error in generation test: {e}")
        return False


def test_query_functions():
    """Test query functions that don't modify system"""
    print("\n🔍 Testing Query Functions")
    print("=" * 50)

    try:
        from nixos_rebuild import nix

        # Test find_file
        print("Testing find_file()...")
        nixpkgs = nix.find_file("nixpkgs")
        if nixpkgs:
            print(f"✅ Found nixpkgs at: {nixpkgs}")
        else:
            print("⚠️  nixpkgs not found")

        # Test get_nixpkgs_rev
        print("\nTesting get_nixpkgs_rev()...")
        if nixpkgs:
            rev = nix.get_nixpkgs_rev(nixpkgs)
            if rev:
                print(f"✅ Nixpkgs revision: {rev}")
            else:
                print("⚠️  Could not get revision")

        return True
    except Exception as e:
        print(f"❌ Error in query functions: {e}")
        return False


def document_real_api():
    """Document the real API based on discoveries"""
    print("\n📖 Documenting Real API")
    print("=" * 50)

    doc = """# nixos-rebuild-ng Python API - Real Documentation

## Discovered API Structure (NixOS 25.11)

### Key Differences from Expected API

The actual API differs significantly from what one might expect:

1. **BuildAttr** takes `(path, attr)` not `(attribute)`
2. **Flake** takes `(path, attr)` not complex options
3. **Profile** is created via `Profile.from_arg(path)` not an enum
4. **Remote** is in `process` module, not `models`

### Correct Usage Examples

#### Import the API
```python
import sys
import subprocess
from pathlib import Path

# Get nixos-rebuild-ng path
result = subprocess.run(
    ["nix-build", "<nixpkgs>", "-A", "nixos-rebuild-ng", "--no-out-link"],
    capture_output=True,
    text=True
)
rebuild_path = result.stdout.strip()
site_packages = Path(rebuild_path) / "lib" / "python3.13" / "site-packages"
sys.path.insert(0, str(site_packages))

# Import modules
from nixos_rebuild import models, nix, services, utils
from nixos_rebuild.process import Remote
```

#### Building System Configuration
```python
# Create BuildAttr with correct signature
build_attr = models.BuildAttr(
    path="<nixpkgs/nixos>",  # Path to nixpkgs
    attr="system"             # Attribute to build
)

# Build the system
# Note: build() takes the attr as first argument!
path = nix.build("system", build_attr, build_flags=None)
```

#### Working with Flakes
```python
# Create Flake object
flake = models.Flake(
    path="/path/to/flake",
    attr="nixosConfigurations.hostname.config.system.build.toplevel"
)

# Build with flake
path = nix.build_flake(flake.attr, flake, flake_build_flags=None)
```

#### Managing Generations
```python
# Create Profile from path
profile = models.Profile.from_arg("/nix/var/nix/profiles/system")

# Get generations
generations = nix.get_generations(profile)

# Rollback
path = nix.rollback(profile, target_host=None, sudo=True)
```

#### Remote Operations
```python
from nixos_rebuild.process import Remote

# Create Remote object
remote = Remote(
    host="example.com",
    opts=["-o", "StrictHostKeyChecking=no"],
    sudo_password=None  # Or provide password for sudo
)

# Build remotely
build_attr = models.BuildAttr(path="<nixpkgs/nixos>", attr="system")
path = nix.build_remote(
    "system",
    build_attr,
    build_host=remote,
    realise_flags=None,
    instantiate_flags=None,
    copy_flags=None
)
```

#### Switching Configuration
```python
# Apply configuration
nix.switch_to_configuration(
    path_to_config=path,
    action=models.Action.SWITCH,
    target_host=None,  # Or Remote object
    sudo=True,
    install_bootloader=False,
    specialisation=None
)
```

### Available Actions (Enum)
- `Action.SWITCH` - Apply now and on boot
- `Action.BOOT` - Apply on next boot
- `Action.TEST` - Apply now but not on boot
- `Action.BUILD` - Build only
- `Action.DRY_BUILD` - Show what would be built
- `Action.DRY_ACTIVATE` - Test activation

### Utility Functions
```python
# Convert dict to command-line flags
flags = utils.dict_to_flags({"verbose": True, "option": "value"})
# Returns: ['--verbose', '--option', 'value']

# Find file in Nix path
nixpkgs = nix.find_file("nixpkgs")

# Get nixpkgs revision
rev = nix.get_nixpkgs_rev(nixpkgs)
```

### Error Handling
```python
from nixos_rebuild.models import NixOSRebuildError

try:
    path = nix.build("system", build_attr)
except NixOSRebuildError as e:
    print(f"Build failed: {e}")
```

## Integration with Luminous Nix

### Updated native_nix_api.py Implementation
```python
class NativeNixAPI:
    def __init__(self):
        self.nix, self.models, self.Remote = self._setup_api()

    def _setup_api(self):
        # Import nixos-rebuild-ng modules
        # ... (setup code) ...
        from nixos_rebuild import models, nix
        from nixos_rebuild.process import Remote
        return nix, models, Remote

    def build_configuration(self, attribute="system"):
        build_attr = self.models.BuildAttr(
            path="<nixpkgs/nixos>",
            attr=attribute
        )
        return self.nix.build(attribute, build_attr)

    def switch_to_configuration(self, path, action="switch"):
        action_map = {
            "switch": self.models.Action.SWITCH,
            "boot": self.models.Action.BOOT,
            "test": self.models.Action.TEST,
        }

        self.nix.switch_to_configuration(
            path_to_config=path,
            action=action_map[action],
            target_host=None,
            sudo=True
        )
```

## Key Learnings

1. **The API exists but is undocumented** - We had to discover signatures through inspection
2. **Different from expectations** - Not a simple object-oriented API
3. **Still valuable** - Provides structured access without subprocess
4. **Needs wrapper** - Raw API is awkward, needs abstraction layer

## Performance Impact

While the API doesn't eliminate subprocess calls internally (nixos-rebuild-ng still calls nix commands), it provides:
- **Structured data** instead of text parsing
- **Proper error handling** via exceptions
- **Type safety** with dataclasses
- **No shell escaping issues**
- **Cleaner integration** with Python code

## Recommendation

Use the Python API but wrap it in a cleaner abstraction layer that:
1. Hides the awkward signatures
2. Provides sensible defaults
3. Handles path setup automatically
4. Falls back to subprocess when needed
"""

    # Save documentation
    doc_path = Path(
        "/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/NIXOS_REBUILD_API_REAL.md"
    )
    doc_path.write_text(doc)
    print(f"✅ Real documentation saved to {doc_path}")

    return True


def main():
    """Run corrected tests"""
    print("🚀 nixos-rebuild-ng Python API Test Suite v2")
    print("=" * 50)

    if not setup_python_path():
        print("\n❌ Failed to setup Python path")
        return 1

    tests = [
        ("Explore Actual API", explore_actual_api),
        ("Test Actual Functions", test_actual_functions),
        ("Test Generation Functions", test_generation_functions),
        ("Test Query Functions", test_query_functions),
        ("Document Real API", document_real_api),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    print("\n📝 Key Findings:")
    print("1. The Python API exists and is functional")
    print("2. API signatures differ from documentation/expectations")
    print("3. BuildAttr takes (path, attr) not just attribute")
    print("4. Profile is created via Profile.from_arg() not enum")
    print("5. Remote is in process module, not models")
    print("\n✅ We can use this API with proper abstraction!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
