"""
Real-time Package Updates System
Monitors NixOS channels for package updates and notifies users
"""

import hashlib
import json
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class PackageUpdate:
    """Represents a package update"""

    package_name: str
    old_version: str
    new_version: str
    channel: str
    timestamp: float
    changelog: Optional[str] = None
    severity: str = "normal"  # security, important, normal, minor

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ChannelInfo:
    """Information about a NixOS channel"""

    name: str
    url: str
    last_checked: float
    last_revision: Optional[str] = None
    update_frequency: int = 3600  # Check every hour by default


class UpdateMonitor:
    """
    Monitors NixOS channels for package updates
    """

    def __init__(self, check_interval: int = 300):
        """Initialize update monitor"""
        # Update tracking
        self.check_interval = check_interval  # 5 minutes default
        self.channels: dict[str, ChannelInfo] = {}
        self.package_versions: dict[
            str, dict[str, str]
        ] = {}  # channel -> package -> version
        self.pending_updates: deque = deque(maxlen=1000)
        self.update_history: deque = deque(maxlen=10000)

        # Subscriptions
        self.update_callbacks: list[Callable] = []
        self.watched_packages: set[str] = set()

        # Threading
        self.monitor_thread = None
        self.stop_monitoring = threading.Event()
        self.update_lock = threading.RLock()

        # Persistence
        self.state_path = (
            Path.home() / ".cache" / "luminous-nix" / "update_monitor.json"
        )
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

        # Load saved state
        self._load_state()

        # Initialize default channels
        self._init_default_channels()

        # Start monitoring
        self._start_monitoring()

    def _init_default_channels(self):
        """Initialize default NixOS channels"""
        default_channels = [
            ChannelInfo(
                name="nixpkgs-unstable",
                url="https://nixos.org/channels/nixpkgs-unstable",
                last_checked=0,
            ),
            ChannelInfo(
                name="nixos-24.11",
                url="https://nixos.org/channels/nixos-24.11",
                last_checked=0,
            ),
            ChannelInfo(
                name="nixos-unstable",
                url="https://nixos.org/channels/nixos-unstable",
                last_checked=0,
            ),
        ]

        for channel in default_channels:
            if channel.name not in self.channels:
                self.channels[channel.name] = channel

    def _load_state(self):
        """Load saved state from disk"""
        if self.state_path.exists():
            try:
                with open(self.state_path) as f:
                    state = json.load(f)

                # Load channels
                for ch_data in state.get("channels", []):
                    channel = ChannelInfo(**ch_data)
                    self.channels[channel.name] = channel

                # Load package versions
                self.package_versions = state.get("package_versions", {})

                # Load watched packages
                self.watched_packages = set(state.get("watched_packages", []))

                # Load update history
                for update_data in state.get("update_history", []):
                    self.update_history.append(PackageUpdate(**update_data))

            except Exception as e:
                print(f"Error loading state: {e}")

    def _save_state(self):
        """Save current state to disk"""
        try:
            state = {
                "channels": [asdict(ch) for ch in self.channels.values()],
                "package_versions": self.package_versions,
                "watched_packages": list(self.watched_packages),
                "update_history": [asdict(u) for u in list(self.update_history)[-100:]],
            }

            with open(self.state_path, "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            print(f"Error saving state: {e}")

    def _start_monitoring(self):
        """Start the monitoring thread"""

        def monitor_worker():
            while not self.stop_monitoring.is_set():
                try:
                    # Check each channel
                    for channel_name, channel in list(self.channels.items()):
                        # Check if it's time to check this channel
                        if (
                            time.time() - channel.last_checked
                            > channel.update_frequency
                        ):
                            self._check_channel_updates(channel)

                    # Save state periodically
                    self._save_state()

                    # Wait for next check
                    self.stop_monitoring.wait(self.check_interval)

                except Exception as e:
                    print(f"Monitor error: {e}")

        self.monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitor_thread.start()

    def _check_channel_updates(self, channel: ChannelInfo):
        """Check a channel for updates"""
        try:
            # Get channel revision (simulated for now)
            current_revision = self._get_channel_revision(channel)

            if current_revision and current_revision != channel.last_revision:
                # Channel has been updated
                if channel.last_revision:
                    # Check for package updates
                    updates = self._find_package_updates(channel, current_revision)

                    for update in updates:
                        self._process_update(update)

                # Update channel info
                channel.last_revision = current_revision

            channel.last_checked = time.time()

        except Exception as e:
            print(f"Error checking channel {channel.name}: {e}")

    def _get_channel_revision(self, channel: ChannelInfo) -> Optional[str]:
        """Get current revision of a channel"""
        # In production, this would fetch actual channel info
        # For now, simulate with timestamp-based revision

        # Simulate periodic updates (every 6 hours)
        hours_passed = int((time.time() - channel.last_checked) / 21600)
        if hours_passed > 0:
            return hashlib.md5(f"{channel.name}{hours_passed}".encode()).hexdigest()[
                :12
            ]

        return channel.last_revision

    def _find_package_updates(
        self, channel: ChannelInfo, new_revision: str
    ) -> list[PackageUpdate]:
        """Find package updates in a channel"""
        updates = []

        # Get current package versions for this channel
        if channel.name not in self.package_versions:
            self.package_versions[channel.name] = {}

        current_packages = self.package_versions[channel.name]

        # Simulate package updates (in production, would diff actual packages)
        simulated_updates = self._simulate_package_updates(channel.name)

        for pkg_name, new_version in simulated_updates.items():
            old_version = current_packages.get(pkg_name)

            if old_version != new_version:
                # Check if this is a watched package or security update
                if pkg_name in self.watched_packages or self._is_security_update(
                    pkg_name, new_version
                ):
                    update = PackageUpdate(
                        package_name=pkg_name,
                        old_version=old_version or "unknown",
                        new_version=new_version,
                        channel=channel.name,
                        timestamp=time.time(),
                        severity=self._determine_severity(
                            pkg_name, old_version, new_version
                        ),
                    )

                    updates.append(update)

                # Update version tracking
                current_packages[pkg_name] = new_version

        return updates

    def _simulate_package_updates(self, channel: str) -> dict[str, str]:
        """Simulate package updates for testing"""
        # In production, would use actual nix commands

        # Simulate some package updates based on time
        hour = datetime.now().hour
        day = datetime.now().day

        packages = {}

        # Different updates at different times
        if hour % 6 == 0:  # Every 6 hours
            packages["firefox"] = f"120.{day}.0"
            packages["chromium"] = f"119.{day}.0"

        if hour % 12 == 0:  # Every 12 hours
            packages["python3"] = f"3.11.{day}"
            packages["nodejs"] = f"20.{day}.0"

        if day % 2 == 0:  # Every other day
            packages["git"] = f"2.43.{day}"
            packages["vim"] = f"9.0.{day * 10}"

        if day % 7 == 0:  # Weekly
            packages["kernel"] = f"6.6.{day}"
            packages["systemd"] = f"254.{day}"

        return packages

    def _is_security_update(self, package: str, version: str) -> bool:
        """Check if this is a security update"""
        # Simple heuristic: kernel, systemd, openssl, etc.
        security_packages = [
            "kernel",
            "linux",
            "systemd",
            "openssl",
            "openssh",
            "firefox",
            "chromium",
            "thunderbird",
        ]

        return any(sec_pkg in package.lower() for sec_pkg in security_packages)

    def _determine_severity(
        self, package: str, old_version: Optional[str], new_version: str
    ) -> str:
        """Determine update severity"""
        if self._is_security_update(package, new_version):
            return "security"

        if package in ["kernel", "systemd", "glibc"]:
            return "important"

        # Check version jump
        if old_version and old_version != "unknown":
            old_parts = old_version.split(".")
            new_parts = new_version.split(".")

            if len(old_parts) > 0 and len(new_parts) > 0:
                try:
                    # Major version change
                    if int(new_parts[0]) > int(old_parts[0]):
                        return "important"
                except:
                    pass

        return "normal"

    def _process_update(self, update: PackageUpdate):
        """Process a detected update"""
        with self.update_lock:
            # Add to pending updates
            self.pending_updates.append(update)

            # Add to history
            self.update_history.append(update)

            # Notify callbacks
            for callback in self.update_callbacks:
                try:
                    callback(update)
                except Exception as e:
                    print(f"Callback error: {e}")

    # === Public API ===

    def add_channel(self, name: str, url: str, check_frequency: int = 3600):
        """Add a channel to monitor"""
        channel = ChannelInfo(
            name=name, url=url, last_checked=0, update_frequency=check_frequency
        )

        self.channels[name] = channel
        self._save_state()

    def remove_channel(self, name: str):
        """Remove a channel from monitoring"""
        if name in self.channels:
            del self.channels[name]
            if name in self.package_versions:
                del self.package_versions[name]
            self._save_state()

    def watch_package(self, package_name: str):
        """Add a package to watch list"""
        self.watched_packages.add(package_name)
        self._save_state()

    def unwatch_package(self, package_name: str):
        """Remove a package from watch list"""
        self.watched_packages.discard(package_name)
        self._save_state()

    def subscribe_to_updates(self, callback: Callable):
        """Subscribe to update notifications"""
        self.update_callbacks.append(callback)

    def get_pending_updates(self) -> list[PackageUpdate]:
        """Get list of pending updates"""
        with self.update_lock:
            return list(self.pending_updates)

    def get_update_history(
        self, package: Optional[str] = None, limit: int = 100
    ) -> list[PackageUpdate]:
        """Get update history"""
        with self.update_lock:
            history = list(self.update_history)

            if package:
                history = [u for u in history if u.package_name == package]

            return history[-limit:]

    def check_for_updates(self, force: bool = False):
        """Manually check for updates"""
        for channel in self.channels.values():
            if force:
                channel.last_checked = 0
            self._check_channel_updates(channel)

    def get_statistics(self) -> dict:
        """Get update statistics"""
        with self.update_lock:
            total_updates = len(self.update_history)

            # Count by severity
            severity_counts = defaultdict(int)
            for update in self.update_history:
                severity_counts[update.severity] += 1

            # Count by channel
            channel_counts = defaultdict(int)
            for update in self.update_history:
                channel_counts[update.channel] += 1

            # Recent activity
            now = time.time()
            recent_24h = sum(
                1 for u in self.update_history if now - u.timestamp < 86400
            )

            return {
                "total_updates": total_updates,
                "pending_updates": len(self.pending_updates),
                "watched_packages": len(self.watched_packages),
                "channels_monitored": len(self.channels),
                "severity_breakdown": dict(severity_counts),
                "channel_breakdown": dict(channel_counts),
                "updates_24h": recent_24h,
            }

    def shutdown(self):
        """Clean shutdown"""
        self.stop_monitoring.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self._save_state()


class SmartUpdateNotifier:
    """
    Smart notification system for package updates
    """

    def __init__(self, monitor: UpdateMonitor):
        """Initialize smart notifier"""
        self.monitor = monitor

        # Notification preferences
        self.notify_security = True
        self.notify_watched = True
        self.notify_important = True
        self.batch_notifications = True
        self.batch_interval = 300  # 5 minutes

        # Notification queue
        self.notification_queue = deque()
        self.last_notification = 0

        # Subscribe to updates
        self.monitor.subscribe_to_updates(self._on_update)

        # Start notification thread
        self.notification_thread = None
        self.stop_notifying = threading.Event()
        self._start_notifier()

    def _on_update(self, update: PackageUpdate):
        """Handle incoming update"""
        should_notify = False

        if update.severity == "security" and self.notify_security:
            should_notify = True
        elif (
            update.package_name in self.monitor.watched_packages and self.notify_watched
        ):
            should_notify = True
        elif update.severity == "important" and self.notify_important:
            should_notify = True

        if should_notify:
            self.notification_queue.append(update)

    def _start_notifier(self):
        """Start notification thread"""

        def notifier_worker():
            while not self.stop_notifying.is_set():
                try:
                    # Check if we should send notifications
                    if self.notification_queue:
                        if self.batch_notifications:
                            # Wait for batch interval or urgent update
                            urgent = any(
                                u.severity == "security"
                                for u in self.notification_queue
                            )

                            if (
                                urgent
                                or time.time() - self.last_notification
                                > self.batch_interval
                            ):
                                self._send_notifications()
                        else:
                            # Send immediately
                            self._send_notifications()

                    self.stop_notifying.wait(10)

                except Exception as e:
                    print(f"Notifier error: {e}")

        self.notification_thread = threading.Thread(target=notifier_worker, daemon=True)
        self.notification_thread.start()

    def _send_notifications(self):
        """Send batched notifications"""
        if not self.notification_queue:
            return

        # Group updates by severity
        updates_by_severity = defaultdict(list)

        while self.notification_queue:
            update = self.notification_queue.popleft()
            updates_by_severity[update.severity].append(update)

        # Create notification message
        messages = []

        if "security" in updates_by_severity:
            security_updates = updates_by_severity["security"]
            messages.append(f"🔒 {len(security_updates)} SECURITY updates available")
            for update in security_updates[:3]:
                messages.append(
                    f"  • {update.package_name}: {update.old_version} → {update.new_version}"
                )

        if "important" in updates_by_severity:
            important_updates = updates_by_severity["important"]
            messages.append(f"⚠️ {len(important_updates)} important updates available")

        if "normal" in updates_by_severity:
            normal_updates = updates_by_severity["normal"]
            messages.append(f"📦 {len(normal_updates)} package updates available")

        # Send notification (in production, would use system notifications)
        print("\n" + "=" * 60)
        print("📬 PACKAGE UPDATE NOTIFICATION")
        print("=" * 60)
        for msg in messages:
            print(msg)
        print("=" * 60 + "\n")

        self.last_notification = time.time()

    def configure(
        self,
        notify_security: bool = True,
        notify_watched: bool = True,
        notify_important: bool = True,
        batch_notifications: bool = True,
        batch_interval: int = 300,
    ):
        """Configure notification preferences"""
        self.notify_security = notify_security
        self.notify_watched = notify_watched
        self.notify_important = notify_important
        self.batch_notifications = batch_notifications
        self.batch_interval = batch_interval

    def shutdown(self):
        """Clean shutdown"""
        self.stop_notifying.set()
        if self.notification_thread:
            self.notification_thread.join(timeout=2)


class UpdateIntegration:
    """
    Integration with Luminous Nix cache and search
    """

    def __init__(self, monitor: UpdateMonitor, cache=None):
        """Initialize update integration"""
        self.monitor = monitor
        self.cache = cache

        # Subscribe to updates
        self.monitor.subscribe_to_updates(self._invalidate_cache)

    def _invalidate_cache(self, update: PackageUpdate):
        """Invalidate cache entries for updated packages"""
        if self.cache:
            # Remove old version from cache
            cache_key = f"info:{update.package_name}"
            if hasattr(self.cache, "invalidate"):
                self.cache.invalidate(cache_key)

            # Update cache with new version info
            new_info = {
                "name": update.package_name,
                "version": update.new_version,
                "channel": update.channel,
                "updated": update.timestamp,
            }

            if hasattr(self.cache, "set"):
                self.cache.set(cache_key, new_info)

    def search_with_updates(self, query: str) -> tuple[list[dict], list[PackageUpdate]]:
        """Search packages and include update information"""
        # Perform normal search
        if self.cache:
            results, _, _ = self.cache.search_hybrid(query)
        else:
            results = []

        # Check for updates for these packages
        updates = []
        for result in results:
            pkg_name = result.get("name")
            if pkg_name:
                # Check update history
                pkg_updates = self.monitor.get_update_history(package=pkg_name, limit=1)
                if pkg_updates:
                    updates.append(pkg_updates[0])

        return results, updates

    def get_package_timeline(self, package: str) -> list[dict]:
        """Get version timeline for a package"""
        history = self.monitor.get_update_history(package=package)

        timeline = []
        for update in history:
            timeline.append(
                {
                    "version": update.new_version,
                    "timestamp": update.timestamp,
                    "channel": update.channel,
                    "severity": update.severity,
                }
            )

        return timeline
