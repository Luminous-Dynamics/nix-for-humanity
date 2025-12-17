"""
Hello World Plugin

A simple example plugin that demonstrates the hook system.
Prints a greeting before and after each operation.
"""

from luminous_nix.plugins import HookPlugin, PluginMetadata


class HelloWorldPlugin(HookPlugin):
    """
    A simple hello world plugin.

    This plugin demonstrates the basic hook system by printing
    messages before and after each operation.
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata"""
        return PluginMetadata(
            name="hello-world",
            version="1.0.0",
            author="Luminous Dynamics",
            description="Says hello before and after operations"
        )

    def activate(self):
        """Called when plugin is activated"""
        super().activate()
        print("👋 Hello World plugin activated!")
        self.logger.info("Hello World plugin activated")

    def pre_operation(self, state):
        """
        Called before each operation.

        Args:
            state: Operation state about to be executed
        """
        operation_type = state.operation_type.value
        operation_id = state.operation_id

        print(f"\n🚀 Starting operation: {operation_type}")
        print(f"   Operation ID: {operation_id}")
        print(f"   Query: {state.user_query}")

        self.logger.debug(f"Pre-operation: {operation_id}")

    def post_operation(self, state):
        """
        Called after each operation completes.

        Args:
            state: Operation state after execution
        """
        operation_type = state.operation_type.value
        operation_id = state.operation_id
        status = state.status.value

        print(f"\n✅ Completed operation: {operation_type}")
        print(f"   Operation ID: {operation_id}")
        print(f"   Status: {status}")

        if state.result:
            # Show first 100 chars of result
            result_preview = str(state.result)[:100]
            print(f"   Result: {result_preview}...")

        self.logger.debug(f"Post-operation: {operation_id}")

    def on_error(self, state, error):
        """
        Called when an operation fails.

        Args:
            state: Operation state when error occurred
            error: The exception that occurred
        """
        operation_type = state.operation_type.value
        operation_id = state.operation_id

        print(f"\n❌ Operation failed: {operation_type}")
        print(f"   Operation ID: {operation_id}")
        print(f"   Error: {error}")

        self.logger.error(f"Operation {operation_id} failed: {error}")

    def deactivate(self):
        """Called when plugin is deactivated"""
        print("👋 Goodbye from Hello World plugin!")
        self.logger.info("Hello World plugin deactivated")
        super().deactivate()


# For testing independently
if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/src")

    # Create and test the plugin
    plugin = HelloWorldPlugin()
    print(f"Plugin: {plugin.metadata.name}")
    print(f"Version: {plugin.metadata.version}")
    print(f"Type: {plugin.type}")

    # Simulate activation
    plugin.activate()

    # Create a mock operation state for testing
    from luminous_nix.core.types import OperationState, OperationType, OperationStatus

    state = OperationState(
        operation_id="test_001",
        operation_type=OperationType.SEARCH,
        user_query="test search vim",
        status=OperationStatus.CREATED
    )

    # Test hooks
    plugin.pre_operation(state)

    state.status = OperationStatus.COMPLETED
    state.result = "Search results: vim, neovim, ..."

    plugin.post_operation(state)

    # Test error hook
    try:
        raise Exception("Test error")
    except Exception as e:
        plugin.on_error(state, e)

    # Deactivate
    plugin.deactivate()
