# 🔌 Plugin Examples

This directory contains example plugins demonstrating the Luminous Nix plugin system.

## Available Examples

### 1. Hello World (`hello-world/`)
**Type**: HookPlugin  
**Complexity**: ⭐ Beginner  
**Lines**: ~80

A simple plugin that prints greetings before and after operations.

**Demonstrates**:
- Basic plugin structure
- Hook system (pre/post operation)
- Plugin lifecycle
- No special permissions needed

**Usage**:
```bash
ask-nix plugin load hello-world
ask-nix "search vim"
```

---

### 2. Docker Operations (`docker-operations/`)
**Type**: OperationPlugin  
**Complexity**: ⭐⭐⭐ Intermediate  
**Lines**: ~250

Adds Docker container management operations.

**Demonstrates**:
- Custom operation types
- Subprocess execution
- Permission requirements
- Validation and error handling
- Structured result formatting

**Usage**:
```bash
ask-nix plugin load docker-operations
ask-nix "run nginx container"
ask-nix "list docker containers"
```

---

## Installation

### System-Wide (All Users)
```bash
sudo cp -r examples/plugins/* /usr/share/luminous-nix/plugins/
```

### User-Specific
```bash
cp -r examples/plugins/* ~/.local/share/luminous-nix/plugins/
```

### Project-Specific
```bash
cp -r examples/plugins/* .luminous-nix/plugins/
```

## Loading Plugins

```bash
# Load a specific plugin
ask-nix plugin load hello-world

# Load all available plugins
ask-nix plugin load-all

# List loaded plugins
ask-nix plugin list
```

## Creating Your Own Plugin

1. **Start with hello-world** - Copy and modify for your needs
2. **Read the Development Guide** - See `docs/PLUGIN_DEVELOPMENT_GUIDE.md`
3. **Study the examples** - Understand patterns and best practices
4. **Test thoroughly** - Use `python main.py` for quick testing

## Plugin Directory Structure

Each plugin should have:

```
my-plugin/
├── plugin.toml          # Manifest (REQUIRED)
├── main.py              # Implementation (REQUIRED)
├── README.md            # Documentation (recommended)
└── tests/               # Tests (recommended)
    └── test_plugin.py
```

## Testing Examples

Each plugin can be tested independently:

```bash
cd examples/plugins/hello-world
python main.py

cd examples/plugins/docker-operations  
python main.py
```

## Contributing Examples

Have a great example plugin? Submit a PR!

1. Create your plugin in `examples/plugins/`
2. Add README with clear documentation
3. Test thoroughly
4. Submit PR with description

## Need Help?

- **Documentation**: `docs/PLUGIN_DEVELOPMENT_GUIDE.md`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

*"The best way to learn is by example."*
