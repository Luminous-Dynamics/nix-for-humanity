#!/usr/bin/env python3
"""
from typing import Dict, Optional
Advanced Features Interface - User-Friendly Access to Power Features

This module provides easy-to-use interfaces for advanced NixOS features:
- Flake management
- Profile switching
- Interactive REPL
- Remote deployment
- Image building
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .native_operations_advanced import (
    AdvancedNativeOperations,
    FlakeOperationType,
    ImageOperationType,
    NativeOperationResult,
    ProfileOperationType,
    RemoteOperationType,
)


@dataclass
class FlakeManager:
    """Easy-to-use flake management"""

    def __init__(self):
        self.ops = AdvancedNativeOperations()

    async def init(self, path: Path | None = None) -> NativeOperationResult:
        """Initialize a new flake in the current directory"""
        return await self.ops.execute_flake_operation(
            FlakeOperationType.INIT_FLAKE, flake_path=path
        )

    async def update(self, path: Path | None = None) -> NativeOperationResult:
        """Update all flake inputs to latest versions"""
        return await self.ops.execute_flake_operation(
            FlakeOperationType.UPDATE_FLAKE, flake_path=path
        )

    async def show(self, path: Path | None = None) -> NativeOperationResult:
        """Show flake outputs and structure"""
        return await self.ops.execute_flake_operation(
            FlakeOperationType.SHOW_FLAKE, flake_path=path
        )

    async def check(self, path: Path | None = None) -> NativeOperationResult:
        """Validate flake configuration"""
        return await self.ops.execute_flake_operation(
            FlakeOperationType.CHECK_FLAKE, flake_path=path
        )

    async def build(self, path: Path | None = None) -> NativeOperationResult:
        """Build the flake configuration"""
        return await self.ops.execute_flake_operation(
            FlakeOperationType.BUILD_FLAKE, flake_path=path
        )

    async def edit(
        self, path: Path | None = None, editor: str | None = None
    ) -> NativeOperationResult:
        """Open flake.nix in editor"""
        return await self.ops.execute_flake_operation(
            FlakeOperationType.EDIT_FLAKE,
            flake_path=path,
            options={"editor": editor} if editor else {},
        )


@dataclass
class ProfileManager:
    """Easy profile management for different environments"""

    def __init__(self):
        self.ops = AdvancedNativeOperations()

    async def list(self) -> NativeOperationResult:
        """List all available profiles"""
        return await self.ops.execute_profile_operation(
            ProfileOperationType.LIST_PROFILES
        )

    async def switch(self, profile_name: str) -> NativeOperationResult:
        """Switch to a different profile (work/home/gaming/etc)"""
        return await self.ops.execute_profile_operation(
            ProfileOperationType.SWITCH_PROFILE, profile_name=profile_name
        )

    async def create(self, profile_name: str) -> NativeOperationResult:
        """Create a new profile"""
        return await self.ops.execute_profile_operation(
            ProfileOperationType.CREATE_PROFILE, profile_name=profile_name
        )

    async def backup(self, profile_name: str | None = None) -> NativeOperationResult:
        """Backup current or specified profile"""
        return await self.ops.execute_profile_operation(
            ProfileOperationType.BACKUP_PROFILE, profile_name=profile_name
        )

    async def diff(self, profile1: str, profile2: str) -> NativeOperationResult:
        """Compare two profiles"""
        return await self.ops.execute_profile_operation(
            ProfileOperationType.DIFF_PROFILES,
            profile_name=profile1,
            options={"compare_to": profile2},
        )


@dataclass
class RemoteBuilder:
    """Remote build and deployment made easy"""

    def __init__(self):
        self.ops = AdvancedNativeOperations()

    async def build(self, host: str, user: str | None = None) -> NativeOperationResult:
        """Build configuration on remote machine"""
        return await self.ops.execute_remote_operation(
            RemoteOperationType.BUILD_REMOTE,
            host=host,
            options={"user": user} if user else {},
        )

    async def deploy(self, host: str, user: str | None = None) -> NativeOperationResult:
        """Deploy configuration to remote machine"""
        return await self.ops.execute_remote_operation(
            RemoteOperationType.DEPLOY_REMOTE,
            host=host,
            options={"user": user} if user else {},
        )

    async def copy_system(
        self, host: str, system_path: str | None = None
    ) -> NativeOperationResult:
        """Copy system closure to remote machine"""
        return await self.ops.execute_remote_operation(
            RemoteOperationType.COPY_CLOSURE,
            host=host,
            options={"closure": system_path} if system_path else {},
        )

    async def check_builders(self) -> NativeOperationResult:
        """Check configured remote builders"""
        return await self.ops.execute_remote_operation(RemoteOperationType.CHECK_REMOTE)


@dataclass
class ImageBuilder:
    """Build various types of system images"""

    def __init__(self):
        self.ops = AdvancedNativeOperations()

    async def iso(self, minimal: bool = False) -> NativeOperationResult:
        """Build bootable ISO image"""
        options = {"minimal": minimal} if minimal else {}
        return await self.ops.execute_image_operation(
            ImageOperationType.BUILD_ISO, options=options
        )

    async def vm(self, with_display: bool = True) -> NativeOperationResult:
        """Build VM image for testing"""
        options = {"display": with_display}
        return await self.ops.execute_image_operation(
            ImageOperationType.BUILD_VM, options=options
        )

    async def container(self, container_type: str = "docker") -> NativeOperationResult:
        """Build container image (docker/podman)"""
        return await self.ops.execute_image_operation(
            ImageOperationType.BUILD_CONTAINER, options={"type": container_type}
        )

    async def sd_card(self, board: str | None = None) -> NativeOperationResult:
        """Build SD card image for embedded devices"""
        options = {"board": board} if board else {}
        return await self.ops.execute_image_operation(
            ImageOperationType.BUILD_SD_IMAGE, options=options
        )


class ReplLauncher:
    """Interactive REPL launcher"""

    def __init__(self):
        self.ops = AdvancedNativeOperations()

    async def launch(
        self, flake: bool = False, path: Path | None = None
    ) -> NativeOperationResult:
        """Launch interactive Nix REPL"""
        options = {"flake_path": path} if path else {}
        return await self.ops.launch_repl(flake=flake, options=options)

    async def launch_with_context(
        self, context: dict[str, Any]
    ) -> NativeOperationResult:
        """Launch REPL with pre-loaded context"""
        # This would create a temporary file with context
        return await self.ops.launch_repl(options={"context": context})


class AdvancedFeatures:
    """
    Main interface for all advanced features.

    Usage:
        features = AdvancedFeatures()

        # Flake management
        await features.flakes.init()
        await features.flakes.update()

        # Profile switching
        await features.profiles.switch("work")

        # Remote deployment
        await features.remote.deploy("myserver.com")

        # Build images
        await features.images.iso()

        # Launch REPL
        await features.repl.launch()
    """

    def __init__(self):
        self.flakes = FlakeManager()
        self.profiles = ProfileManager()
        self.remote = RemoteBuilder()
        self.images = ImageBuilder()
        self.repl = ReplLauncher()

    async def quick_demo(self):
        """Quick demonstration of advanced features"""
        print("🌟 Advanced Features Demo\n")

        # 1. Profile management
        print("📁 Profile Management:")
        result = await self.profiles.list()
        if result.success:
            print(f"  ✅ {result.message}")

        # 2. Flake features
        print("\n📦 Flake Support:")
        result = await self.flakes.show()
        print(f"  {'✅' if result.success else '❌'} {result.message}")

        # 3. REPL
        print("\n💬 Interactive REPL:")
        result = await self.repl.launch()
        print(f"  ✅ {result.message}")
        if result.suggestions:
            for suggestion in result.suggestions:
                print(f"     💡 {suggestion}")

        # 4. Image building
        print("\n💿 Image Building:")
        for image_type in ["ISO", "VM", "Container"]:
            print(f"  • {image_type} images can be built with native API")

        print("\n✨ All features available through simple, intuitive interfaces!")


# Convenience functions for common tasks


async def switch_to_work_profile():
    """Quick function to switch to work profile"""
    profiles = ProfileManager()
    return await profiles.switch("work")


async def update_system_flake():
    """Update system flake inputs"""
    flakes = FlakeManager()
    return await flakes.update(Path("/etc/nixos"))


async def deploy_to_server(hostname: str, username: str = "root"):
    """Deploy current configuration to a server"""
    remote = RemoteBuilder()
    return await remote.deploy(hostname, username)


async def build_test_vm():
    """Build a VM for testing current configuration"""
    images = ImageBuilder()
    return await images.vm(with_display=True)


# Demo script
async def main():
    """Demo all advanced features"""
    features = AdvancedFeatures()
    await features.quick_demo()

    print("\n\n🎯 Example Usage:")
    print("```python")
    print("# Initialize in your project")
    print("features = AdvancedFeatures()")
    print()
    print("# Switch to work profile")
    print("await features.profiles.switch('work')")
    print()
    print("# Update flake inputs")
    print("await features.flakes.update()")
    print()
    print("# Deploy to server")
    print("await features.remote.deploy('myserver.com')")
    print()
    print("# Build ISO image")
    print("await features.images.iso()")
    print("```")


if __name__ == "__main__":
    asyncio.run(main())
