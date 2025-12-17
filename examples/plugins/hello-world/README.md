# Hello World Plugin

A simple example plugin that demonstrates the Luminous Nix plugin system.

## What It Does

This plugin prints friendly messages before and after each NixOS operation:

- 🚀 Before operation: Shows what's about to run
- ✅ After operation: Shows completion status
- ❌ On error: Shows error details

## Installation

```bash
# Copy to plugins directory
cp -r examples/plugins/hello-world ~/.local/share/luminous-nix/plugins/

# Load the plugin
ask-nix plugin load hello-world
```

## Usage

Once loaded, the plugin automatically hooks into all operations:

```bash
ask-nix "search vim"
# Output:
# 🚀 Starting operation: SEARCH
#    Operation ID: op_12345
#    Query: search vim
#
# [search results]
#
# ✅ Completed operation: SEARCH
#    Operation ID: op_12345
#    Status: completed
```

## Testing

Test the plugin independently:

```bash
cd examples/plugins/hello-world
python main.py
```

## Code Structure

- `plugin.toml` - Plugin manifest with metadata
- `main.py` - Plugin implementation (80 lines)
- `README.md` - This file

## Learning Points

This example demonstrates:

1. **Plugin Type**: HookPlugin for event hooks
2. **Lifecycle**: activate(), pre_operation(), post_operation(), deactivate()
3. **Logging**: Using self.logger for debug messages
4. **Error Handling**: on_error() hook for failures
5. **No Permissions**: Simple plugins don't need special permissions

## License

MIT
