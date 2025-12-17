"""
Docker Operations Plugin

Adds Docker container management to Luminous Nix.
Allows natural language commands like "run nginx container" or "list docker containers".
"""

import subprocess
import json
from luminous_nix.plugins import OperationPlugin, PluginMetadata


class DockerOperationsPlugin(OperationPlugin):
    """
    Plugin to add Docker operations to Luminous Nix.

    Supports:
    - DOCKER_RUN: Run a container
    - DOCKER_STOP: Stop a container
    - DOCKER_PS: List running containers
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata"""
        return PluginMetadata(
            name="docker-operations",
            version="1.0.0",
            author="Luminous Dynamics",
            description="Adds Docker container operations",
            operation_types=["DOCKER_RUN", "DOCKER_STOP", "DOCKER_PS"]
        )

    def activate(self):
        """Check Docker is available"""
        super().activate()

        # Check Docker is installed
        if not self._docker_available():
            self.logger.warning("Docker not found! Plugin will be limited.")
        else:
            self.logger.info("Docker operations plugin activated")

    def can_handle(self, operation_type: str) -> bool:
        """Check if plugin can handle operation type"""
        return operation_type in [
            "DOCKER_RUN",
            "DOCKER_STOP",
            "DOCKER_PS"
        ]

    def execute(self, state):
        """
        Execute Docker operation.

        Args:
            state: Operation state with details

        Returns:
            Updated operation state with results
        """
        # Check permissions
        self.require_permission("operations:execute")

        operation_type = state.operation_type

        try:
            if operation_type == "DOCKER_RUN":
                return self._docker_run(state)
            elif operation_type == "DOCKER_STOP":
                return self._docker_stop(state)
            elif operation_type == "DOCKER_PS":
                return self._docker_ps(state)
            else:
                state.status = "failed"
                state.error = f"Unknown operation: {operation_type}"

        except Exception as e:
            state.status = "failed"
            state.error = str(e)
            self.logger.error(f"Docker operation failed: {e}")

        return state

    def validate(self, state):
        """Validate operation can be executed"""
        # Check Docker is available
        if not self._docker_available():
            self.logger.error("Docker is not available")
            return False

        # Check user query has required info
        if not state.user_query:
            return False

        return True

    # Private methods

    def _docker_available(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _docker_run(self, state):
        """
        Run a Docker container.

        Expected query format: "run <image> container"
        Example: "run nginx container"
        """
        # Parse image name from query
        query = state.user_query.lower()
        words = query.split()

        # Simple parsing - look for "run X container"
        if "run" in words and "container" in words:
            run_idx = words.index("run")
            container_idx = words.index("container")
            if container_idx > run_idx + 1:
                image = words[run_idx + 1]
            else:
                image = "nginx"  # default
        else:
            image = "nginx"  # default

        self.logger.info(f"Running container: {image}")

        try:
            # Run container in detached mode
            result = subprocess.run(
                ["docker", "run", "-d", image],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            container_id = result.stdout.strip()

            state.status = "completed"
            state.result = {
                "container_id": container_id,
                "image": image,
                "message": f"Container started successfully"
            }

        except subprocess.CalledProcessError as e:
            state.status = "failed"
            state.error = f"Docker error: {e.stderr}"

        except subprocess.TimeoutExpired:
            state.status = "failed"
            state.error = "Docker command timed out"

        return state

    def _docker_stop(self, state):
        """
        Stop a Docker container.

        Expected query format: "stop container <id>"
        """
        # Parse container ID from query
        query = state.user_query
        words = query.split()

        # Look for container ID (last word usually)
        container_id = words[-1] if words else None

        if not container_id:
            state.status = "failed"
            state.error = "No container ID specified"
            return state

        self.logger.info(f"Stopping container: {container_id}")

        try:
            result = subprocess.run(
                ["docker", "stop", container_id],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            state.status = "completed"
            state.result = {
                "container_id": container_id,
                "message": "Container stopped successfully"
            }

        except subprocess.CalledProcessError as e:
            state.status = "failed"
            state.error = f"Docker error: {e.stderr}"

        return state

    def _docker_ps(self, state):
        """
        List running Docker containers.

        Expected query format: "list docker containers" or "docker ps"
        """
        self.logger.info("Listing Docker containers")

        try:
            # Get containers as JSON for structured output
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )

            # Parse JSON output (each line is a JSON object)
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

            state.status = "completed"
            state.result = {
                "count": len(containers),
                "containers": containers,
                "message": f"Found {len(containers)} running container(s)"
            }

        except subprocess.CalledProcessError as e:
            state.status = "failed"
            state.error = f"Docker error: {e.stderr}"

        return state


# For testing independently
if __name__ == "__main__":
    # Create and test the plugin
    plugin = DockerOperationsPlugin()
    print(f"Plugin: {plugin.metadata.name}")
    print(f"Version: {plugin.metadata.version}")
    print(f"Type: {plugin.type}")
    print(f"Provides: {plugin.metadata.operation_types}")

    # Test activation
    plugin.activate()

    # Test can_handle
    print(f"\nCan handle DOCKER_RUN: {plugin.can_handle('DOCKER_RUN')}")
    print(f"Can handle INSTALL: {plugin.can_handle('INSTALL')}")

    # Test Docker availability
    if plugin._docker_available():
        print("\n✓ Docker is available")
    else:
        print("\n✗ Docker is not available (install Docker to use this plugin)")
