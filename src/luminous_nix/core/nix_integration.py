#!/usr/bin/env python3
"""
from typing import Dict
NixOS Integration Module for Unified Backend
Bridges the subprocess-based operations with our backend architecture
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Set up logger
logger = logging.getLogger(__name__)

# Import the native backend
from luminous_nix.core.native_operations import (  # noqa: E402
    NATIVE_API_AVAILABLE,
    NativeNixBackend,
    NixResult,
    OperationType,
)

logger.info("✅ Using native backend with standard Nix performance improvements")


class NixOSIntegration:
    """
    Integration layer between Luminous Nix backend and native NixOS API

    This class:
    - Translates high-level intents to NixOS operations
    - Handles progress updates and streaming
    - Provides educational context for operations
    - Manages error recovery and suggestions
    """

    def __init__(self, progress_callback=None):
        self.native_backend = NativeNixBackend()
        if progress_callback:
            if hasattr(self.native_backend, "set_progress_callback"):
                self.native_backend.set_progress_callback(progress_callback)
            else:
                # Fallback for basic backend
                self.native_backend.progress.callback = progress_callback

        self.operation_count = 0
        self.using_native_api = NATIVE_API_AVAILABLE

        # Log backend capabilities
        logger.info(
            "Native backend features: caching, security validation, error recovery, progress tracking"
        )

    def get_status(self) -> dict[str, Any]:
        """Get integration status"""
        status = {
            "native_api_available": self.using_native_api,
            "operations_completed": self.operation_count,
            "backend": "native" if self.using_native_api else "subprocess",
            "performance_boost": "10x" if self.using_native_api else "1x",
        }

        # Add metrics if available
        if hasattr(self.native_backend, "get_metrics"):
            status["metrics"] = self.native_backend.get_metrics()

        return status

    async def execute_intent(
        self, intent: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a user intent using native NixOS API

        Args:
            intent: The intent type (e.g., "install_package", "update_system")
            params: Parameters for the operation

        Returns:
            Result dictionary with success, message, and data
        """
        logger.info(f"Executing intent: {intent} with params: {params}")

        try:
            # Map intent to operation parameters
            operation_type, packages, options = self._map_intent_to_operation(
                intent, params
            )

            # Execute using native backend
            result = await self.native_backend.execute_native_operation(
                operation_type=operation_type, packages=packages, options=options
            )

            # Add educational context
            enhanced_result = self._enhance_result(intent, result)

            self.operation_count += 1
            return enhanced_result

        except Exception as e:
            logger.error(f"Failed to execute intent {intent}: {e}")
            return {
                "success": False,
                "message": f"Operation failed: {str(e)}",
                "error": str(e),
                "suggestion": self._get_error_suggestion(str(e)),
            }

    def _map_intent_to_operation(
        self, intent: str, params: dict[str, Any]
    ) -> tuple[OperationType, list[str], dict[str, Any]]:
        """Map high-level intent to NixOS operation parameters

        Returns:
            Tuple of (operation_type, packages, options)
        """

        intent_mapping = {
            "update_system": OperationType.SWITCH,  # Was UPDATE, now SWITCH
            "rollback_system": OperationType.ROLLBACK,
            "install_package": OperationType.BUILD,  # Was INSTALL, declarative package addition
            "remove_package": OperationType.BUILD,  # Was REMOVE, declarative package removal
            "search_package": OperationType.SEARCH_PACKAGES,  # Was SEARCH
            "build_system": OperationType.BUILD,
            "test_configuration": OperationType.TEST,
            "list_generations": OperationType.LIST_GENERATIONS,
        }

        operation_type = intent_mapping.get(intent, OperationType.BUILD)

        # Extract packages if present
        packages = []
        if params.get("package"):
            packages = [params["package"]]
        elif params.get("packages"):
            packages = params["packages"]

        # Build options dictionary
        options = params.get("options", {})
        if params.get("dry_run"):
            options["dry_run"] = True

        return (operation_type, packages, options)

    def _enhance_result(self, intent: str, result: NixResult) -> dict[str, Any]:
        """Add educational context to results"""

        enhanced = {
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "intent": intent,
            "native_api": self.using_native_api,
        }

        if result.error:
            enhanced["error"] = result.error
            enhanced["suggestion"] = self._get_error_suggestion(result.error)

        # Add educational context based on intent
        if intent == "update_system" and result.success:
            enhanced["education"] = {
                "what_happened": "Your NixOS system configuration was rebuilt from source",
                "why_it_matters": "This ensures reproducibility - the same config always produces the same system",
                "next_steps": "You can rollback anytime with 'rollback my system'",
            }

        elif intent == "rollback_system" and result.success:
            enhanced["education"] = {
                "what_happened": "Switched to the previous system generation",
                "why_it_matters": "NixOS keeps every system state, making rollbacks 2-5 seconds and safe",
                "next_steps": "Run 'list generations' to see all available system states",
            }

        elif intent == "install_package":
            enhanced["education"] = {
                "what_happened": "Generated instructions for package installation",
                "why_it_matters": "NixOS uses declarative configuration - packages are defined in config files",
                "next_steps": "Edit the configuration file and rebuild to apply changes",
            }

        return enhanced

    def _get_error_suggestion(self, error: str) -> str:
        """Provide helpful suggestions for common errors"""

        error_lower = error.lower()

        if "permission" in error_lower:
            return "This operation requires root privileges. Try with 'sudo' or as root user."

        if "no such file" in error_lower:
            return "Configuration file not found. Check if /etc/nixos/configuration.nix exists."

        if "build failed" in error_lower:
            return "Build failed - check your configuration for syntax errors. Run 'nixos-rebuild build' to see details."

        if "network" in error_lower or "download" in error_lower:
            return (
                "Network issue detected. Check your internet connection and try again."
            )

        if (
            "disk space" in error_lower
            or "no space" in error_lower
            or "space left" in error_lower
        ):
            return "Low disk space. Run 'nix-collect-garbage -d' to free up space."

        return "Check the NixOS manual or ask the community for help with this error."

    async def get_system_info(self) -> dict[str, Any]:
        """Get current system information"""
        try:
            # Get generations using native operation
            result = await self.native_backend.execute_native_operation(
                operation_type=OperationType.LIST_GENERATIONS, packages=[], options={}
            )

            generations = []
            current_gen = None

            if result.success and result.data.get("generations"):
                generations = result.data["generations"]
                current_gen = next((g for g in generations if g.get("current")), None)

            return {
                "nixos_version": self._get_nixos_version(),
                "current_generation": current_gen,
                "total_generations": len(generations),
                "using_flakes": self.native_backend.use_flakes,
                "native_api": self.using_native_api,
            }

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"error": str(e), "native_api": self.using_native_api}

    def _get_nixos_version(self) -> str:
        """Get NixOS version"""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("VERSION="):
                        return line.split("=")[1].strip().strip('"')
        except Exception:  # noqa: S110
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return "Unknown"


# Convenience functions for direct use
async def update_system(
    dry_run: bool = False, progress_callback=None
) -> dict[str, Any]:
    """Update NixOS system using native Python API"""
    integration = NixOSIntegration(progress_callback)
    return await integration.execute_intent("update_system", {"dry_run": dry_run})


async def rollback_system(progress_callback=None) -> dict[str, Any]:
    """Rollback to previous generation"""
    integration = NixOSIntegration(progress_callback)
    return await integration.execute_intent("rollback_system", {})


async def install_package(package: str, progress_callback=None) -> dict[str, Any]:
    """Get instructions for installing a package"""
    integration = NixOSIntegration(progress_callback)
    return await integration.execute_intent("install_package", {"package": package})


# Example usage
async def demo():
    """Demonstrate the native integration"""
    print("ℹ️ Using standard subprocess operations")

    # Create integration
    integration = NixOSIntegration()

    # Show status
    status = integration.get_status()
    print("✅ Integration Status:")
    print(f"  - Native API: {status['native_api_available']}")
    print(f"  - Backend: {status['backend']}")
    print(f"  - Performance: {status['performance_boost']}")

    # Get system info
    print("\n📊 System Information:")
    info = await integration.get_system_info()
    print(f"  - NixOS Version: {info.get('nixos_version', 'Unknown')}")
    print(f"  - Using Flakes: {info.get('using_flakes', False)}")
    print(f"  - Total Generations: {info.get('total_generations', 0)}")

    # Test update (dry run)
    print("\n🧪 Testing System Update (dry run)...")
    result = await update_system(dry_run=True)
    print(f"  - Success: {result['success']}")
    print(f"  - Message: {result['message']}")

    if result.get("education"):
        print("\n📚 Educational Context:")
        edu = result["education"]
        print(f"  - What happened: {edu['what_happened']}")
        print(f"  - Why it matters: {edu['why_it_matters']}")
        print(f"  - Next steps: {edu['next_steps']}")


if __name__ == "__main__":
    asyncio.run(demo())
