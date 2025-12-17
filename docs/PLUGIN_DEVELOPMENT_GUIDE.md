# 🔌 Plugin Development Guide

**Version**: 1.0.0
**Audience**: Plugin Developers
**Prerequisites**: Basic Python knowledge, understanding of Luminous Nix

---

## 🎯 Quick Start

Create your first plugin in 5 minutes!

### Step 1: Create Plugin Directory

```bash
mkdir -p ~/.local/share/luminous-nix/plugins/hello-world
cd ~/.local/share/luminous-nix/plugins/hello-world
```

### Step 2: Create `plugin.toml`

```toml
[plugin]
name = "hello-world"
version = "1.0.0"
api_version = "1.0"

[plugin.metadata]
author = "Your Name"
email = "you@example.com"
description = "A simple hello world plugin"
license = "MIT"

[plugin.entry_points]
module = "main"
class = "HelloWorldPlugin"

[plugin.provides]
hooks = ["pre_operation", "post_operation"]
```

### Step 3: Create `main.py`

```python
from luminous_nix.plugins import HookPlugin, PluginMetadata

class HelloWorldPlugin(HookPlugin):
    """A simple hello world plugin"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hello-world",
            version="1.0.0",
            author="Your Name",
            description="Says hello before and after operations"
        )

    def pre_operation(self, state):
        """Called before each operation"""
        print(f"👋 Hello! About to run: {state.operation_type.value}")

    def post_operation(self, state):
        """Called after each operation"""
        print(f"✅ Done! Operation completed: {state.operation_type.value}")
```

### Step 4: Test Your Plugin

```bash
# Load the plugin
ask-nix plugin load hello-world

# Run an operation to see it in action
ask-nix "search vim"
```

You'll see:
```
👋 Hello! About to run: SEARCH
[search results]
✅ Done! Operation completed: SEARCH
```

---

## 📚 Plugin Types

Luminous Nix supports four types of plugins:

### 1. Operation Plugins

Add custom operation types (e.g., Docker, cloud operations).

```python
from luminous_nix.plugins import OperationPlugin, PluginMetadata
from luminous_nix.core.types import OperationState, OperationStatus

class CustomOperationPlugin(OperationPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom-operations",
            version="1.0.0",
            author="You",
            description="Custom operations",
            operation_types=["CUSTOM_OP"]
        )

    def can_handle(self, operation_type: str) -> bool:
        """Check if we can handle this operation"""
        return operation_type == "CUSTOM_OP"

    def execute(self, state: OperationState) -> OperationState:
        """Execute the operation"""
        # Your logic here
        state.status = OperationStatus.COMPLETED
        state.result = "Operation completed successfully!"
        return state

    def validate(self, state: OperationState) -> bool:
        """Validate before execution"""
        # Check if operation is valid
        return True
```

### 2. Hook Plugins

Hook into system events for logging, monitoring, etc.

```python
from luminous_nix.plugins import HookPlugin, PluginMetadata

class MonitoringPlugin(HookPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="monitoring",
            version="1.0.0",
            author="You",
            description="Monitors all operations"
        )

    def pre_operation(self, state):
        """Before operation"""
        print(f"Starting: {state.operation_id}")

    def post_operation(self, state):
        """After operation"""
        print(f"Completed: {state.operation_id}")

    def on_error(self, state, error):
        """On error"""
        print(f"Error in {state.operation_id}: {error}")
```

### 3. Security Plugins

Extend security with custom encryption, HSM integration, etc.

```python
from luminous_nix.plugins import SecurityPlugin, PluginMetadata

class CustomSecurityPlugin(SecurityPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom-security",
            version="1.0.0",
            author="You",
            description="Custom security features",
            requires_permissions=["security:encrypt", "security:decrypt"]
        )

    def encrypt(self, data: bytes, **kwargs) -> bytes:
        """Custom encryption"""
        # Your encryption logic
        return encrypted_data

    def decrypt(self, data: bytes, **kwargs) -> bytes:
        """Custom decryption"""
        # Your decryption logic
        return decrypted_data
```

### 4. AI Plugins

Extend AI capabilities with custom models or preprocessing.

```python
from luminous_nix.plugins import AIPlugin, PluginMetadata

class CustomAIPlugin(AIPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom-ai",
            version="1.0.0",
            author="You",
            description="Custom AI model"
        )

    def process_query(self, query: str, **kwargs) -> dict:
        """Process user query"""
        # Your AI logic
        return {
            "intent": "recognized_intent",
            "confidence": 0.95,
            "entities": {}
        }

    def can_handle(self, query: str) -> bool:
        """Check if we can handle this query"""
        return "custom_keyword" in query.lower()
```

---

## 🔐 Permissions

Declare required permissions in `plugin.toml`:

```toml
[plugin.permissions]
required = [
    "operations:execute",      # Execute operations
    "filesystem:read",         # Read files
    "network:http",            # Make HTTP requests
]
```

### Available Permissions

**Operations**:
- `operations:read` - Read operation state
- `operations:execute` - Execute operations
- `operations:modify` - Modify operation state

**Security**:
- `security:encrypt` - Use encryption
- `security:decrypt` - Use decryption
- `security:sign` - Create signatures
- `security:verify` - Verify signatures

**Filesystem**:
- `filesystem:read` - Read files
- `filesystem:write` - Write files
- `filesystem:execute` - Execute files

**Network**:
- `network:http` - HTTP/HTTPS requests
- `network:dns` - DNS lookups
- `network:socket` - Raw socket access

**Hardware**:
- `hardware:usb` - USB device access
- `hardware:hsm` - Hardware security module

---

## 🎨 Accessing Core Systems

Plugins can access Luminous Nix core systems through context:

```python
class MyPlugin(OperationPlugin):
    def execute(self, state):
        # Access StateManager
        state_manager = self.context.state_manager
        prev_state = state_manager.load_state("prev_op")

        # Access Security system
        security = self.context.security
        encrypted = security.pqc.encrypt(data)

        # Access AI system
        ai = self.context.ai
        result = ai.process_query(query)

        # Access Executor
        executor = self.context.executor
        result = executor.execute(command)

        return state
```

---

## ✅ Best Practices

### 1. Error Handling

Always catch and handle errors:

```python
def execute(self, state):
    try:
        # Your logic
        state.result = "Success"
    except Exception as e:
        state.status = OperationStatus.FAILED
        state.error = str(e)
        self.logger.error(f"Operation failed: {e}")
    return state
```

### 2. Logging

Use the built-in logger:

```python
class MyPlugin(OperationPlugin):
    def execute(self, state):
        self.logger.info("Starting operation")
        self.logger.debug(f"Details: {state}")
        self.logger.error("Something went wrong")
        return state
```

### 3. Validation

Validate input before processing:

```python
def validate(self, state):
    # Check required fields
    if not state.user_query:
        return False

    # Check dependencies exist
    if not self._check_dependencies():
        return False

    return True

def execute(self, state):
    if not self.validate(state):
        state.status = OperationStatus.FAILED
        state.error = "Validation failed"
        return state
    # ... proceed with execution
```

### 4. Permission Checks

Check permissions before sensitive operations:

```python
def execute(self, state):
    # Check permission
    if not self.check_permission("operations:execute"):
        state.status = OperationStatus.FAILED
        state.error = "Permission denied"
        return state

    # Or require permission (raises error if not granted)
    self.require_permission("security:encrypt")

    # ... proceed
```

### 5. Resource Cleanup

Clean up resources in deactivate:

```python
def activate(self):
    """Called when plugin is activated"""
    super().activate()
    self.connection = connect_to_service()

def deactivate(self):
    """Called when plugin is deactivated"""
    if self.connection:
        self.connection.close()
    super().deactivate()
```

---

## 🧪 Testing Plugins

### Basic Test Structure

```python
# tests/test_my_plugin.py
import pytest
from my_plugin.main import MyPlugin
from luminous_nix.core.types import OperationState, OperationType

def test_plugin_metadata():
    plugin = MyPlugin()
    assert plugin.metadata.name == "my-plugin"
    assert plugin.metadata.version == "1.0.0"

def test_can_handle():
    plugin = MyPlugin()
    assert plugin.can_handle("MY_OP") == True
    assert plugin.can_handle("OTHER_OP") == False

def test_execute():
    plugin = MyPlugin()
    state = OperationState(
        operation_id="test_001",
        operation_type=OperationType.INSTALL,
        user_query="test query"
    )
    result = plugin.execute(state)
    assert result.status == OperationStatus.COMPLETED
    assert result.result is not None
```

### Run Tests

```bash
cd ~/.local/share/luminous-nix/plugins/my-plugin
pytest tests/
```

---

## 📦 Plugin Structure

Recommended plugin directory structure:

```
my-plugin/
├── plugin.toml          # Plugin manifest (REQUIRED)
├── main.py              # Main plugin code (REQUIRED)
├── README.md            # Documentation (recommended)
├── LICENSE              # License file (recommended)
├── requirements.txt     # Python dependencies (optional)
├── tests/               # Tests (recommended)
│   └── test_plugin.py
└── examples/            # Usage examples (optional)
    └── example.py
```

---

## 🔄 Plugin Lifecycle

Plugins go through these states:

1. **DISCOVERED** - Found by discovery system
2. **VALIDATED** - Security validation passed
3. **LOADED** - Code loaded into memory
4. **INITIALIZED** - `__init__` called
5. **ACTIVE** - Available for use
6. **DISABLED** - Temporarily disabled
7. **FAILED** - Loading/execution failed

### Lifecycle Hooks

```python
class MyPlugin(OperationPlugin):
    def activate(self):
        """Called when plugin is activated"""
        super().activate()
        # Initialize resources
        self.logger.info("Plugin activated")

    def deactivate(self):
        """Called when plugin is deactivated"""
        # Release resources
        super().deactivate()
        self.logger.info("Plugin deactivated")

    def cleanup(self):
        """Called when plugin is unloaded"""
        # Final cleanup
        self.logger.info("Plugin cleanup")
```

---

## 🚀 Publishing Plugins

### 1. Add README

```markdown
# My Plugin

Description of what your plugin does.

## Installation

```bash
cd ~/.local/share/luminous-nix/plugins
git clone https://github.com/you/my-plugin
```

## Usage

```bash
ask-nix plugin load my-plugin
ask-nix "your command"
```

## License

MIT
```

### 2. Add LICENSE

Choose a license (MIT, Apache 2.0, etc.)

### 3. Test Thoroughly

- Test all operation types
- Test error cases
- Test with minimal permissions
- Test on different systems

### 4. Share

- Publish to GitHub
- Add to Luminous Nix plugin directory
- Share with community

---

## 🐛 Debugging

### Enable Debug Logging

```python
import logging

class MyPlugin(OperationPlugin):
    def __init__(self):
        super().__init__()
        self.logger.setLevel(logging.DEBUG)

    def execute(self, state):
        self.logger.debug(f"Processing: {state}")
        # ... your code
```

### Common Issues

**Plugin Not Found**:
- Check plugin directory location
- Verify `plugin.toml` exists and is valid
- Check plugin name matches directory name

**Import Errors**:
- Ensure all dependencies are installed
- Check Python version compatibility
- Verify entry point module exists

**Permission Denied**:
- Check required permissions in `plugin.toml`
- User must approve permissions on first load

**Plugin Failed to Load**:
- Check logs: `~/.local/share/luminous-nix/logs/plugins.log`
- Run plugin validation: `ask-nix plugin validate my-plugin`
- Test plugin independently: `python -m my_plugin.main`

---

## 📚 Complete Example

See the `examples` directory for complete, working plugins:

- **hello-world** - Simple hook plugin
- **docker-operations** - Operation plugin with Docker
- **prometheus-monitor** - Monitoring hook plugin
- **custom-ai-model** - AI plugin example

---

## 🤝 Contributing

Found a bug? Have a feature idea?

1. Open an issue on GitHub
2. Submit a pull request
3. Join the community discussions

---

## 📖 Further Reading

- **[Plugin System Design](./PLUGIN_SYSTEM_DESIGN.md)** - Complete architecture
- **[Security Guide](./DEVELOPER_SECURITY_GUIDE.md)** - Security best practices
- **[API Reference](./API_REFERENCE.md)** - Complete API documentation

---

*"The best plugins are simple, focused, and solve real problems."*

**Happy Plugin Development!** 🎉
