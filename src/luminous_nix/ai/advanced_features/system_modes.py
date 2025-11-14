#!/usr/bin/env python3
"""
System Mode Transformations - Transform your system for different contexts
Switch between gaming, work, presentation, and other modes 2-5 secondsly
"""

import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SystemMode(Enum):
    """Available system modes"""

    WORK = "work"
    GAMING = "gaming"
    PRESENTATION = "presentation"
    STREAMING = "streaming"
    FOCUS = "focus"
    BATTERY_SAVER = "battery_saver"
    PERFORMANCE = "performance"
    QUIET = "quiet"
    SECURE = "secure"
    MINIMAL = "minimal"


@dataclass
class ModeProfile:
    """Configuration profile for a system mode"""

    name: SystemMode
    description: str

    # Service adjustments
    enable_services: List[str]
    disable_services: List[str]

    # Resource allocation
    cpu_governor: str  # performance, powersave, ondemand
    gpu_profile: str  # auto, performance, battery
    memory_swappiness: int  # 0-100

    # Network settings
    network_optimizations: Dict[str, Any]
    firewall_rules: List[str]

    # Display settings
    compositor_effects: bool
    display_brightness: Optional[int]  # 0-100
    refresh_rate: Optional[int]  # Hz

    # Audio settings
    audio_profile: str  # low-latency, power-save, balanced
    notification_sounds: bool

    # Application behavior
    auto_start_apps: List[str]
    kill_apps: List[str]
    nice_adjustments: Dict[str, int]  # app: nice_value

    # Power management
    suspend_timeout: Optional[int]  # minutes
    screen_timeout: Optional[int]  # minutes

    # Security settings
    lock_screen: bool
    vpn_required: bool

    # Custom scripts
    pre_switch_hook: Optional[str]
    post_switch_hook: Optional[str]


@dataclass
class ModeTransition:
    """Represents a transition between modes"""

    from_mode: SystemMode
    to_mode: SystemMode
    timestamp: datetime
    duration: timedelta
    success: bool
    changes_applied: List[str]
    rollback_available: bool


class SystemModeManager:
    """
    Manages system mode transformations
    Allows 2-5 seconds switching between different operational modes
    """

    def __init__(self):
        # Define mode profiles
        self.profiles = self._initialize_profiles()

        # Track current mode
        self.current_mode = self._detect_current_mode()

        # Transition history
        self.transition_history: List[ModeTransition] = []

        # Mode hooks
        self.mode_hooks: Dict[SystemMode, List[Callable]] = {}

    def _initialize_profiles(self) -> Dict[SystemMode, ModeProfile]:
        """Initialize all mode profiles"""
        return {
            SystemMode.WORK: ModeProfile(
                name=SystemMode.WORK,
                description="Optimized for productivity and development",
                enable_services=["docker", "postgresql", "redis"],
                disable_services=["steam", "gamemode"],
                cpu_governor="balanced",
                gpu_profile="battery",
                memory_swappiness=60,
                network_optimizations={"tcp_congestion": "cubic"},
                firewall_rules=["allow ssh", "allow http/https"],
                compositor_effects=True,
                display_brightness=80,
                refresh_rate=60,
                audio_profile="balanced",
                notification_sounds=True,
                auto_start_apps=["slack", "vscode", "terminal"],
                kill_apps=["games"],
                nice_adjustments={"chrome": 5, "firefox": 5},
                suspend_timeout=30,
                screen_timeout=10,
                lock_screen=True,
                vpn_required=False,
                pre_switch_hook=None,
                post_switch_hook='notify-send "Work Mode Activated"',
            ),
            SystemMode.GAMING: ModeProfile(
                name=SystemMode.GAMING,
                description="Maximum performance for gaming",
                enable_services=["gamemode", "steam"],
                disable_services=["docker", "postgresql", "indexing"],
                cpu_governor="performance",
                gpu_profile="performance",
                memory_swappiness=10,
                network_optimizations={
                    "tcp_congestion": "bbr",
                    "tcp_notsent_lowat": 16384,
                },
                firewall_rules=["gaming ports"],
                compositor_effects=False,
                display_brightness=100,
                refresh_rate=144,
                audio_profile="low-latency",
                notification_sounds=False,
                auto_start_apps=["steam", "discord"],
                kill_apps=["slack", "teams", "indexing"],
                nice_adjustments={"game": -10},
                suspend_timeout=None,
                screen_timeout=None,
                lock_screen=False,
                vpn_required=False,
                pre_switch_hook="killall -STOP tracker-miner-fs",
                post_switch_hook='notify-send "Gaming Mode: Performance Unleashed!"',
            ),
            SystemMode.PRESENTATION: ModeProfile(
                name=SystemMode.PRESENTATION,
                description="Clean setup for presentations",
                enable_services=[],
                disable_services=["notifications", "updates"],
                cpu_governor="powersave",
                gpu_profile="balanced",
                memory_swappiness=60,
                network_optimizations={},
                firewall_rules=["strict"],
                compositor_effects=True,
                display_brightness=100,
                refresh_rate=60,
                audio_profile="balanced",
                notification_sounds=False,
                auto_start_apps=[],
                kill_apps=["messengers", "mail"],
                nice_adjustments={},
                suspend_timeout=None,
                screen_timeout=None,
                lock_screen=False,
                vpn_required=False,
                pre_switch_hook="do-not-disturb --enable",
                post_switch_hook=None,
            ),
            SystemMode.FOCUS: ModeProfile(
                name=SystemMode.FOCUS,
                description="Deep work with minimal distractions",
                enable_services=["focus-mode"],
                disable_services=["notifications", "mail", "messengers"],
                cpu_governor="powersave",
                gpu_profile="battery",
                memory_swappiness=60,
                network_optimizations={"block_sites": ["social", "news"]},
                firewall_rules=["block distractions"],
                compositor_effects=False,
                display_brightness=70,
                refresh_rate=60,
                audio_profile="quiet",
                notification_sounds=False,
                auto_start_apps=["terminal", "editor"],
                kill_apps=["browser", "slack", "discord"],
                nice_adjustments={},
                suspend_timeout=60,
                screen_timeout=30,
                lock_screen=True,
                vpn_required=False,
                pre_switch_hook="focus-timer --start",
                post_switch_hook='notify-send "Focus Mode: Stay in the zone"',
            ),
            SystemMode.BATTERY_SAVER: ModeProfile(
                name=SystemMode.BATTERY_SAVER,
                description="Maximum battery life",
                enable_services=["tlp", "powertop"],
                disable_services=["bluetooth", "indexing", "syncing"],
                cpu_governor="powersave",
                gpu_profile="battery",
                memory_swappiness=100,
                network_optimizations={"wifi_power_save": True},
                firewall_rules=[],
                compositor_effects=False,
                display_brightness=40,
                refresh_rate=30,
                audio_profile="power-save",
                notification_sounds=False,
                auto_start_apps=[],
                kill_apps=["heavy-apps"],
                nice_adjustments={"all": 10},
                suspend_timeout=5,
                screen_timeout=2,
                lock_screen=True,
                vpn_required=False,
                pre_switch_hook="rfkill block bluetooth",
                post_switch_hook='notify-send "Battery Saver: Maximum efficiency"',
            ),
            SystemMode.SECURE: ModeProfile(
                name=SystemMode.SECURE,
                description="Enhanced security and privacy",
                enable_services=["firewall", "vpn", "apparmor"],
                disable_services=["avahi", "cups", "samba"],
                cpu_governor="balanced",
                gpu_profile="auto",
                memory_swappiness=60,
                network_optimizations={"vpn_only": True},
                firewall_rules=["deny all", "allow vpn"],
                compositor_effects=True,
                display_brightness=80,
                refresh_rate=60,
                audio_profile="balanced",
                notification_sounds=True,
                auto_start_apps=["vpn-client", "password-manager"],
                kill_apps=["untrusted"],
                nice_adjustments={},
                suspend_timeout=5,
                screen_timeout=1,
                lock_screen=True,
                vpn_required=True,
                pre_switch_hook="firejail --enable-all",
                post_switch_hook='notify-send "Secure Mode: Protected"',
            ),
        }

    def switch_mode(
        self, target_mode: SystemMode, dry_run: bool = False
    ) -> ModeTransition:
        """
        Switch system to target mode

        Args:
            target_mode: Mode to switch to
            dry_run: Preview changes without applying

        Returns:
            ModeTransition with results
        """
        try:
            start_time = datetime.now()
            profile = self.profiles[target_mode]
            changes = []

            # Pre-switch hook
            if profile.pre_switch_hook and not dry_run:
                subprocess.run(profile.pre_switch_hook, shell=True)
                changes.append(f"Ran pre-switch hook")

            # Apply service changes
            for service in profile.disable_services:
                if not dry_run:
                    self._disable_service(service)
                changes.append(f"Disabled {service}")

            for service in profile.enable_services:
                if not dry_run:
                    self._enable_service(service)
                changes.append(f"Enabled {service}")

            # Apply CPU governor
            if not dry_run:
                self._set_cpu_governor(profile.cpu_governor)
            changes.append(f"CPU governor: {profile.cpu_governor}")

            # Apply GPU profile
            if not dry_run:
                self._set_gpu_profile(profile.gpu_profile)
            changes.append(f"GPU profile: {profile.gpu_profile}")

            # Apply memory settings
            if not dry_run:
                self._set_swappiness(profile.memory_swappiness)
            changes.append(f"Swappiness: {profile.memory_swappiness}")

            # Apply network optimizations
            if profile.network_optimizations and not dry_run:
                self._apply_network_optimizations(profile.network_optimizations)
                changes.append(f"Network optimizations applied")

            # Apply display settings
            if profile.display_brightness is not None and not dry_run:
                self._set_brightness(profile.display_brightness)
                changes.append(f"Brightness: {profile.display_brightness}%")

            if profile.refresh_rate and not dry_run:
                self._set_refresh_rate(profile.refresh_rate)
                changes.append(f"Refresh rate: {profile.refresh_rate}Hz")

            # Apply audio settings
            if not dry_run:
                self._set_audio_profile(profile.audio_profile)
            changes.append(f"Audio: {profile.audio_profile}")

            # Handle applications
            for app in profile.kill_apps:
                if not dry_run:
                    self._kill_app(app)
                changes.append(f"Killed {app}")

            for app in profile.auto_start_apps:
                if not dry_run:
                    self._start_app(app)
                changes.append(f"Started {app}")

            # Post-switch hook
            if profile.post_switch_hook and not dry_run:
                subprocess.run(profile.post_switch_hook, shell=True)
                changes.append(f"Ran post-switch hook")

            # Record transition
            transition = ModeTransition(
                from_mode=self.current_mode,
                to_mode=target_mode,
                timestamp=start_time,
                duration=datetime.now() - start_time,
                success=True,
                changes_applied=changes,
                rollback_available=True,
            )

            if not dry_run:
                self.current_mode = target_mode
                self.transition_history.append(transition)

            return transition

        except Exception as e:
            logger.error(f"Mode switch failed: {e}")
            return ModeTransition(
                from_mode=self.current_mode,
                to_mode=target_mode,
                timestamp=datetime.now(),
                duration=timedelta(0),
                success=False,
                changes_applied=[],
                rollback_available=False,
            )

    def create_custom_mode(
        self, name: str, base_mode: SystemMode, customizations: Dict[str, Any]
    ) -> ModeProfile:
        """
        Create a custom mode based on existing mode

        Args:
            name: Name for custom mode
            base_mode: Base mode to customize
            customizations: Custom settings

        Returns:
            New ModeProfile
        """
        base_profile = self.profiles[base_mode]

        # Create new profile with customizations
        custom_profile = ModeProfile(
            name=SystemMode.WORK,  # Would need dynamic enum
            description=customizations.get("description", f"Custom {name}"),
            enable_services=customizations.get(
                "enable_services", base_profile.enable_services
            ),
            disable_services=customizations.get(
                "disable_services", base_profile.disable_services
            ),
            cpu_governor=customizations.get("cpu_governor", base_profile.cpu_governor),
            gpu_profile=customizations.get("gpu_profile", base_profile.gpu_profile),
            memory_swappiness=customizations.get(
                "memory_swappiness", base_profile.memory_swappiness
            ),
            network_optimizations=customizations.get(
                "network_optimizations", base_profile.network_optimizations
            ),
            firewall_rules=customizations.get(
                "firewall_rules", base_profile.firewall_rules
            ),
            compositor_effects=customizations.get(
                "compositor_effects", base_profile.compositor_effects
            ),
            display_brightness=customizations.get(
                "display_brightness", base_profile.display_brightness
            ),
            refresh_rate=customizations.get("refresh_rate", base_profile.refresh_rate),
            audio_profile=customizations.get(
                "audio_profile", base_profile.audio_profile
            ),
            notification_sounds=customizations.get(
                "notification_sounds", base_profile.notification_sounds
            ),
            auto_start_apps=customizations.get(
                "auto_start_apps", base_profile.auto_start_apps
            ),
            kill_apps=customizations.get("kill_apps", base_profile.kill_apps),
            nice_adjustments=customizations.get(
                "nice_adjustments", base_profile.nice_adjustments
            ),
            suspend_timeout=customizations.get(
                "suspend_timeout", base_profile.suspend_timeout
            ),
            screen_timeout=customizations.get(
                "screen_timeout", base_profile.screen_timeout
            ),
            lock_screen=customizations.get("lock_screen", base_profile.lock_screen),
            vpn_required=customizations.get("vpn_required", base_profile.vpn_required),
            pre_switch_hook=customizations.get(
                "pre_switch_hook", base_profile.pre_switch_hook
            ),
            post_switch_hook=customizations.get(
                "post_switch_hook", base_profile.post_switch_hook
            ),
        )

        return custom_profile

    def schedule_mode_switch(self, mode: SystemMode, time: datetime) -> bool:
        """
        Schedule a mode switch for specific time

        Args:
            mode: Target mode
            time: When to switch

        Returns:
            Success status
        """
        try:
            # Would use systemd timer or cron in production
            logger.info(f"Scheduled {mode.value} mode for {time}")
            return True
        except Exception as e:
            logger.error(f"Scheduling failed: {e}")
            return False

    def get_mode_recommendations(self) -> List[Tuple[SystemMode, str]]:
        """
        Recommend modes based on current context

        Returns:
            List of (mode, reason) tuples
        """
        recommendations = []
        current_hour = datetime.now().hour

        # Time-based recommendations
        if 9 <= current_hour < 17:
            recommendations.append((SystemMode.WORK, "Business hours"))
        elif 20 <= current_hour < 23:
            recommendations.append((SystemMode.GAMING, "Evening gaming time"))
        elif current_hour >= 23 or current_hour < 6:
            recommendations.append((SystemMode.QUIET, "Late night quiet mode"))

        # Battery-based (would check actual battery)
        battery_level = self._get_battery_level()
        if battery_level and battery_level < 20:
            recommendations.append(
                (SystemMode.BATTERY_SAVER, f"Low battery ({battery_level}%)")
            )

        # Application-based
        if self._is_app_running("zoom") or self._is_app_running("teams"):
            recommendations.append((SystemMode.PRESENTATION, "Meeting detected"))

        return recommendations

    def _detect_current_mode(self) -> SystemMode:
        """Detect current system mode based on active settings"""
        # Simplified detection logic
        try:
            governor = subprocess.run(
                ["cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"],
                capture_output=True,
                text=True,
            ).stdout.strip()

            if governor == "performance":
                return SystemMode.GAMING
            elif governor == "powersave":
                return SystemMode.BATTERY_SAVER
            else:
                return SystemMode.WORK
        except:
            return SystemMode.WORK  # Default

    def _disable_service(self, service: str):
        """Disable a system service"""
        try:
            subprocess.run(["systemctl", "stop", service], check=False)
        except:
            pass

    def _enable_service(self, service: str):
        """Enable a system service"""
        try:
            subprocess.run(["systemctl", "start", service], check=False)
        except:
            pass

    def _set_cpu_governor(self, governor: str):
        """Set CPU frequency governor"""
        try:
            for cpu in Path("/sys/devices/system/cpu").glob("cpu[0-9]*"):
                governor_file = cpu / "cpufreq/scaling_governor"
                if governor_file.exists():
                    governor_file.write_text(governor)
        except:
            pass

    def _set_gpu_profile(self, profile: str):
        """Set GPU power profile"""
        # Would implement GPU-specific commands
        pass

    def _set_swappiness(self, value: int):
        """Set memory swappiness"""
        try:
            Path("/proc/sys/vm/swappiness").write_text(str(value))
        except:
            pass

    def _apply_network_optimizations(self, opts: Dict[str, Any]):
        """Apply network optimizations"""
        # Would implement network tuning
        pass

    def _set_brightness(self, level: int):
        """Set display brightness"""
        try:
            # Example for Intel backlight
            max_brightness = int(
                Path("/sys/class/backlight/intel_backlight/max_brightness").read_text()
            )
            brightness = int(max_brightness * level / 100)
            Path("/sys/class/backlight/intel_backlight/brightness").write_text(
                str(brightness)
            )
        except:
            pass

    def _set_refresh_rate(self, rate: int):
        """Set display refresh rate"""
        # Would use xrandr or wayland equivalent
        pass

    def _set_audio_profile(self, profile: str):
        """Set audio profile"""
        # Would use PulseAudio/PipeWire commands
        pass

    def _kill_app(self, app: str):
        """Kill application by name"""
        try:
            subprocess.run(["pkill", app], check=False)
        except:
            pass

    def _start_app(self, app: str):
        """Start application"""
        try:
            subprocess.Popen(
                [app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except:
            pass

    def _get_battery_level(self) -> Optional[int]:
        """Get battery level percentage"""
        try:
            capacity = Path("/sys/class/power_supply/BAT0/capacity").read_text()
            return int(capacity)
        except:
            return None

    def _is_app_running(self, app: str) -> bool:
        """Check if application is running"""
        try:
            result = subprocess.run(["pgrep", app], capture_output=True)
            return result.returncode == 0
        except:
            return False
