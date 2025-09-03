# 🔧 Luminous Nix API Reference

*Complete API documentation for developers*

## Core Module

### `luminous_nix.core.LuminousNixCore`

The main engine that processes natural language queries.

```python
from luminous_nix.core import LuminousNixCore

core = LuminousNixCore()
```

#### Methods

##### `process_query(query: Query) -> Response`

Process a natural language query and return a response.

```python
from luminous_nix.core import Query

query = Query(text="install firefox", dry_run=True)
response = core.process_query(query)
print(response.message)
```

**Parameters:**
- `query` (Query): Query object containing the user's request

**Returns:**
- `Response`: Response object with results and metadata

##### `search_packages(query: str) -> List[Package]`

Search for packages using natural language.

```python
packages = core.search_packages("text editor")
for pkg in packages:
    print(f"{pkg.name}: {pkg.description}")
```

##### `get_package_info(package_name: str) -> PackageInfo`

Get detailed information about a package.

```python
info = core.get_package_info("firefox")
print(f"Version: {info.version}")
print(f"Description: {info.description}")
```

## Configuration Generator

### `luminous_nix.core.config_generator.NixConfigGenerator`

Generate NixOS configurations from natural language.

```python
from luminous_nix.core.config_generator import NixConfigGenerator

generator = NixConfigGenerator()
```

#### Methods

##### `parse_intent(text: str) -> Dict[str, Any]`

Parse natural language into configuration intent.

```python
intent = generator.parse_intent("web server with nginx and postgresql")
print(intent["modules"])  # ['web.nginx', 'db.postgresql']
```

##### `generate_config(intent: Dict) -> str`

Generate NixOS configuration from parsed intent.

```python
config = generator.generate_config(intent)
print(config)  # Complete configuration.nix content
```

##### `validate_config(path: str) -> Tuple[bool, str]`

Validate a NixOS configuration file.

```python
valid, message = generator.validate_config("/etc/nixos/configuration.nix")
if valid:
    print("Configuration is valid!")
else:
    print(f"Error: {message}")
```

##### `save_config(config: str, path: str, backup: bool = True) -> Tuple[bool, str]`

Save configuration with optional backup.

```python
success, message = generator.save_config(
    config_content,
    "/etc/nixos/configuration.nix",
    backup=True
)
```

## Flake Manager

### `luminous_nix.core.flake_manager.FlakeManager`

Manage Nix flakes for development environments.

```python
from luminous_nix.core.flake_manager import FlakeManager

manager = FlakeManager()
```

#### Methods

##### `parse_intent(description: str) -> Dict[str, Any]`

Parse natural language into flake configuration.

```python
intent = manager.parse_intent("python web app with django and postgresql")
print(intent["language"])    # 'python'
print(intent["packages"])    # ['django', 'postgresql']
print(intent["frameworks"])  # ['django']
```

##### `create_flake(intent: Dict, project_path: Path) -> Tuple[bool, str]`

Create a flake.nix file from intent.

```python
from pathlib import Path

success, message = manager.create_flake(intent, Path("./my-project"))
if success:
    print("Flake created successfully!")
```

##### `validate_flake(project_path: Path) -> Tuple[bool, str]`

Validate an existing flake.

```python
valid, message = manager.validate_flake(Path("./my-project"))
```

##### `convert_to_flake(project_path: Path) -> Tuple[bool, str]`

Convert shell.nix to flake.nix.

```python
success, message = manager.convert_to_flake(Path("./legacy-project"))
```

## Smart Package Discovery

### `luminous_nix.core.smart_package_discovery.SmartPackageDiscovery`

Intelligent package search with typo correction and semantic understanding.

```python
from luminous_nix.core.smart_package_discovery import SmartPackageDiscovery

discovery = SmartPackageDiscovery()
```

#### Methods

##### `search(query: str, limit: int = 20) -> List[Package]`

Search packages with fuzzy matching and semantic understanding.

```python
results = discovery.search("text editer", limit=10)  # Handles typo
for pkg in results:
    print(f"{pkg.name} (score: {pkg.relevance_score})")
```

##### `suggest_correction(query: str) -> Optional[str]`

Suggest spelling corrections for package names.

```python
correction = discovery.suggest_correction("fierfix")
print(correction)  # 'firefox'
```

##### `find_by_category(category: str) -> List[Package]`

Find packages by category.

```python
editors = discovery.find_by_category("editors")
browsers = discovery.find_by_category("web-browsers")
```

## Data Types

### `Query`

Represents a user query.

```python
from luminous_nix.types import Query

query = Query(
    text="install firefox",
    dry_run=False,
    verbose=True,
    channel="unstable"
)
```

**Attributes:**
- `text` (str): The natural language query
- `dry_run` (bool): Preview without executing
- `verbose` (bool): Enable verbose output
- `channel` (str): Nix channel to use
- `json_output` (bool): Return JSON formatted output

### `Response`

Response from query processing.

```python
from luminous_nix.types import Response

response = Response(
    success=True,
    message="Firefox installed successfully",
    data={"package": "firefox", "version": "120.0"},
    changes=["Installed: firefox-120.0"]
)
```

**Attributes:**
- `success` (bool): Whether operation succeeded
- `message` (str): Human-readable message
- `data` (Dict): Structured response data
- `changes` (List[str]): List of changes made
- `suggestions` (List[str]): Alternative suggestions

### `Package`

Represents a Nix package.

```python
from luminous_nix.types import Package

package = Package(
    name="firefox",
    version="120.0",
    description="Mozilla Firefox web browser",
    homepage="https://www.mozilla.org/firefox/",
    platforms=["x86_64-linux", "aarch64-linux"]
)
```

### `Intent`

Parsed intent from natural language.

```python
from luminous_nix.types import Intent, IntentType

intent = Intent(
    type=IntentType.INSTALL_PACKAGE,
    packages=["firefox", "git"],
    options={"dry_run": True}
)
```

## CLI Integration

### Using the CLI programmatically

```python
import subprocess
import json

# Run command and get JSON output
result = subprocess.run(
    ["ask-nix", "search", "editor", "--json"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
```

### Creating custom commands

```python
from luminous_nix.cli import create_cli_app
import click

app = create_cli_app()

@app.command()
@click.argument('package')
def custom_install(package):
    """Custom installation command"""
    core = LuminousNixCore()
    query = Query(text=f"install {package}")
    response = core.process_query(query)
    print(response.message)
```

## Plugin System

### Creating a plugin

```python
from luminous_nix.plugins import Plugin, register_plugin

class MyPlugin(Plugin):
    """Custom plugin for Luminous Nix"""
    
    def __init__(self):
        super().__init__("my-plugin", "1.0.0")
    
    def process_query(self, query: Query) -> Optional[Response]:
        """Process queries that match this plugin"""
        if "my-feature" in query.text:
            return Response(
                success=True,
                message="Handled by my plugin"
            )
        return None
    
    def get_commands(self) -> List[click.Command]:
        """Add custom CLI commands"""
        @click.command()
        def my_command():
            """My custom command"""
            print("Hello from plugin!")
        
        return [my_command]

# Register the plugin
register_plugin(MyPlugin())
```

## Error Handling

### Custom exceptions

```python
from luminous_nix.exceptions import (
    LuminousNixError,
    PackageNotFoundError,
    InvalidConfigError,
    FlakeValidationError
)

try:
    core.install_package("nonexistent")
except PackageNotFoundError as e:
    print(f"Package not found: {e.package_name}")
    print(f"Suggestions: {e.suggestions}")
except LuminousNixError as e:
    print(f"Error: {e}")
```

## Configuration

### Loading configuration

```python
from luminous_nix.config import Config

config = Config.load()  # Load from default location
config = Config.load("/path/to/config.yaml")  # Custom path

print(config.defaults.dry_run)
print(config.search.fuzzy_threshold)
```

### Modifying configuration

```python
config.defaults.dry_run = True
config.search.max_results = 50
config.save()  # Save changes
```

## Testing

### Unit testing with mocks

```python
import pytest
from unittest.mock import Mock, patch
from luminous_nix.core import LuminousNixCore

def test_search_packages():
    core = LuminousNixCore()
    
    with patch('luminous_nix.core.NixBackend') as mock_backend:
        mock_backend.return_value.search.return_value = [
            Package(name="vim", description="Text editor")
        ]
        
        results = core.search_packages("editor")
        assert len(results) == 1
        assert results[0].name == "vim"
```

### Integration testing

```python
import tempfile
from pathlib import Path
from luminous_nix.core.flake_manager import FlakeManager

def test_flake_creation():
    manager = FlakeManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        intent = manager.parse_intent("python web app")
        success, message = manager.create_flake(intent, project_path)
        
        assert success
        assert (project_path / "flake.nix").exists()
```

## Async Support

### Async operations

```python
import asyncio
from luminous_nix.async_core import AsyncLuminousNixCore

async def main():
    core = AsyncLuminousNixCore()
    
    # Async search
    packages = await core.search_packages_async("editor")
    
    # Parallel operations
    tasks = [
        core.get_package_info_async("firefox"),
        core.get_package_info_async("vscode"),
        core.get_package_info_async("git")
    ]
    results = await asyncio.gather(*tasks)
    
    for info in results:
        print(f"{info.name}: {info.version}")

asyncio.run(main())
```

## Logging

### Configure logging

```python
import logging
from luminous_nix.logging import setup_logging

# Setup with default configuration
setup_logging()

# Custom configuration
setup_logging(
    level=logging.DEBUG,
    log_file="/var/log/luminous-nix.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get logger for module
logger = logging.getLogger("luminous_nix.core")
logger.debug("Processing query: %s", query.text)
```

## Environment Variables

### Available environment variables

```python
import os

# Enable debug mode
os.environ["LUMINOUS_DEBUG"] = "1"

# Set custom config path
os.environ["LUMINOUS_CONFIG"] = "/path/to/config.yaml"

# Disable color output
os.environ["NO_COLOR"] = "1"

# Set default channel
os.environ["NIX_CHANNEL"] = "unstable"

# Enable experimental features
os.environ["LUMINOUS_EXPERIMENTAL"] = "1"

# Set cache directory
os.environ["LUMINOUS_CACHE_DIR"] = "/tmp/luminous-cache"
```

## Performance Optimization

### Caching

```python
from luminous_nix.cache import PackageCache

cache = PackageCache()

# Cache package data
cache.set("firefox", package_data, ttl=3600)  # 1 hour TTL

# Retrieve from cache
data = cache.get("firefox")
if data is None:
    # Not in cache, fetch from backend
    data = fetch_package_data("firefox")
    cache.set("firefox", data)
```

### Batch operations

```python
# Batch package installation
packages = ["firefox", "git", "vim", "tmux"]
core.install_packages(packages)  # Single transaction

# Batch search
queries = ["editor", "browser", "terminal"]
results = core.batch_search(queries)  # Parallel processing
```

## Advanced Examples

### Custom intent processor

```python
from luminous_nix.core.intent_processor import IntentProcessor

class CustomIntentProcessor(IntentProcessor):
    def process(self, text: str) -> Intent:
        # Custom processing logic
        if "my special command" in text:
            return Intent(
                type=IntentType.CUSTOM,
                action="special_action",
                data={"custom": "data"}
            )
        return super().process(text)

# Use custom processor
core = LuminousNixCore(intent_processor=CustomIntentProcessor())
```

### Extending the configuration generator

```python
from luminous_nix.core.config_generator import NixConfigGenerator

class ExtendedConfigGenerator(NixConfigGenerator):
    def _load_modules_database(self):
        modules = super()._load_modules_database()
        
        # Add custom modules
        modules["custom.myservice"] = NixModule(
            name="services.myservice",
            config={"services.myservice.enable": True},
            description="My custom service"
        )
        
        return modules
```

---

*For more examples and advanced usage, see the [examples/](../examples/) directory.*