# Docker Operations Plugin

An example plugin that adds Docker container management to Luminous Nix.

## What It Does

This plugin adds three new operation types:

- **DOCKER_RUN**: Run a Docker container
- **DOCKER_STOP**: Stop a running container  
- **DOCKER_PS**: List running containers

## Prerequisites

Docker must be installed and running:

```bash
# Check Docker is available
docker --version
```

## Installation

```bash
# Copy to plugins directory
cp -r examples/plugins/docker-operations ~/.local/share/luminous-nix/plugins/

# Load the plugin
ask-nix plugin load docker-operations
```

## Usage

Once loaded, use natural language commands:

```bash
# Run a container
ask-nix "run nginx container"

# List running containers
ask-nix "list docker containers"

# Stop a container
ask-nix "stop container abc123"
```

## Testing

Test the plugin independently:

```bash
cd examples/plugins/docker-operations
python main.py
```

## Code Structure

- `plugin.toml` - Plugin manifest with Docker operation types
- `main.py` - Plugin implementation (~250 lines)
- `README.md` - This file

## Learning Points

This example demonstrates:

1. **Plugin Type**: OperationPlugin for custom operations
2. **Operation Types**: DOCKER_RUN, DOCKER_STOP, DOCKER_PS
3. **Validation**: Checking Docker is available
4. **Subprocess**: Running Docker commands
5. **Error Handling**: Catching and reporting errors
6. **Permissions**: Requiring operations:execute permission
7. **Result Formatting**: Structured JSON results

## Security

This plugin requires:
- `operations:execute` - To execute Docker commands
- `filesystem:read` - To access Docker socket

Note: In production, Docker operations should be further restricted.

## License

MIT
