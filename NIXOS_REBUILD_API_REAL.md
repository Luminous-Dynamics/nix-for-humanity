# nixos-rebuild-ng Python API - Real Documentation

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
