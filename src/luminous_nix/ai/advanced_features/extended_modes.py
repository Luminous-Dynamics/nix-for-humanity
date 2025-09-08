#!/usr/bin/env python3
"""
Extended System Modes - Additional sophisticated modes for specialized use cases
Includes Developer, Creative, Server, Privacy, and more advanced modes
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .system_modes import SystemMode, ModeProfile, SystemModeManager


class ExtendedSystemMode(Enum):
    """Extended system modes for specialized contexts"""
    DEVELOPER = "developer"
    CREATIVE = "creative"
    SERVER = "server"
    PRIVACY = "privacy"
    LEARNING = "learning"
    MEDITATION = "meditation"
    RECORDING = "recording"
    COMPILATION = "compilation"
    BACKUP = "backup"
    EMERGENCY = "emergency"


def get_extended_profiles() -> Dict[SystemMode, ModeProfile]:
    """Get extended mode profiles for specialized use cases"""
    return {
        # Developer Mode - Optimized for coding
        "developer": ModeProfile(
            name=SystemMode.WORK,  # Base on work mode
            description="Ultimate development environment with all tools active",
            enable_services=[
                'docker', 'docker-compose', 'postgresql', 'mysql', 'redis',
                'mongodb', 'elasticsearch', 'rabbitmq', 'nginx', 'apache',
                'nodejs', 'python', 'ruby', 'java', 'golang', 'rust',
                'vscode-server', 'jupyter', 'gitlab-runner', 'jenkins'
            ],
            disable_services=[
                'gaming', 'streaming', 'bluetooth-audio'
            ],
            cpu_governor='performance',  # Need speed for compilation
            gpu_profile='balanced',  # GPU for ML/CUDA development
            memory_swappiness=10,  # Keep everything in RAM
            network_optimizations={
                'tcp_congestion': 'bbr',
                'tcp_keepalive': True,
                'port_forwarding': 'enabled',
                'localhost_optimize': True
            },
            firewall_rules=[
                'allow development ports 3000-9999',
                'allow database ports',
                'allow docker networks'
            ],
            compositor_effects=False,  # Maximum performance
            display_brightness=75,
            refresh_rate=60,
            audio_profile='balanced',
            notification_sounds=False,  # Deep focus
            auto_start_apps=[
                'terminal', 'vscode', 'browser', 'docker-desktop',
                'database-client', 'postman', 'git-kraken'
            ],
            kill_apps=['games', 'social-media'],
            nice_adjustments={
                'compiler': -5,
                'language-server': -3,
                'docker': -2
            },
            suspend_timeout=None,  # Never suspend during long builds
            screen_timeout=30,
            lock_screen=True,
            vpn_required=False,
            pre_switch_hook='git status --porcelain | head -5',
            post_switch_hook='notify-send "🚀 Developer Mode Active" "All development services ready"'
        ),
        
        # Creative Mode - For artists, designers, content creators
        "creative": ModeProfile(
            name=SystemMode.WORK,
            description="Optimized for creative work: design, video, music, art",
            enable_services=[
                'jack', 'pulseaudio-jack', 'midi', 'wacom',
                'color-management', 'font-server', 'adobe-cc',
                'blender-server', 'davinci-resolve'
            ],
            disable_services=[
                'development', 'databases', 'virtualization'
            ],
            cpu_governor='ondemand',
            gpu_profile='performance',  # Need GPU for rendering
            memory_swappiness=20,  # Balance for large media files
            network_optimizations={
                'streaming_optimize': True,
                'large_file_transfer': True
            },
            firewall_rules=['allow creative-cloud'],
            compositor_effects=True,  # Visual feedback important
            display_brightness=100,  # Color accuracy
            refresh_rate=60,  # 144Hz for animation work if available
            audio_profile='studio-quality',
            notification_sounds=False,
            auto_start_apps=[
                'creative-suite', 'color-picker', 'tablet-config',
                'spotify', 'inspiration-board'
            ],
            kill_apps=['email', 'slack'],
            nice_adjustments={
                'renderer': -10,
                'preview': -5
            },
            suspend_timeout=None,
            screen_timeout=None,
            lock_screen=False,
            vpn_required=False,
            pre_switch_hook='color-calibrate --quick',
            post_switch_hook='notify-send "🎨 Creative Mode" "Color profiles loaded"'
        ),
        
        # Server Mode - Turn desktop into server
        "server": ModeProfile(
            name=SystemMode.MINIMAL,
            description="Server mode: maximum resources for services, minimal UI",
            enable_services=[
                'sshd', 'nginx', 'apache', 'mysql', 'postgresql',
                'docker', 'kubernetes', 'monitoring', 'backup',
                'fail2ban', 'ufw', 'cron', 'systemd-timers'
            ],
            disable_services=[
                'desktop', 'display-manager', 'audio', 'bluetooth',
                'cups', 'avahi', 'gaming', 'multimedia'
            ],
            cpu_governor='powersave',  # Stable performance, lower heat
            gpu_profile='off',  # No GPU needed
            memory_swappiness=60,  # Standard server setting
            network_optimizations={
                'tcp_congestion': 'cubic',
                'tcp_fastopen': True,
                'net.core.somaxconn': 65535,
                'server_mode': True
            },
            firewall_rules=[
                'default deny all',
                'allow ssh',
                'allow http/https',
                'allow established'
            ],
            compositor_effects=False,
            display_brightness=10,  # Minimal if display attached
            refresh_rate=30,  # Save power
            audio_profile='disabled',
            notification_sounds=False,
            auto_start_apps=['htop', 'monitoring-dashboard'],
            kill_apps=['gui-apps'],
            nice_adjustments={
                'web-server': -5,
                'database': -5
            },
            suspend_timeout=None,  # Servers never sleep
            screen_timeout=5,
            lock_screen=True,
            vpn_required=False,
            pre_switch_hook='systemctl start server-stack',
            post_switch_hook='logger "Server mode activated"'
        ),
        
        # Privacy Mode - Maximum privacy and security
        "privacy": ModeProfile(
            name=SystemMode.SECURE,
            description="Maximum privacy: VPN, Tor, encrypted DNS, no tracking",
            enable_services=[
                'tor', 'vpn', 'dnscrypt', 'firewall', 'apparmor',
                'firejail', 'usbguard', 'rkhunter', 'clamav'
            ],
            disable_services=[
                'telemetry', 'crash-reporter', 'location',
                'bluetooth', 'avahi', 'cups', 'samba',
                'remote-desktop', 'ssh-server'
            ],
            cpu_governor='balanced',
            gpu_profile='balanced',
            memory_swappiness=0,  # No swap for sensitive data
            network_optimizations={
                'vpn_killswitch': True,
                'dns_over_https': True,
                'disable_ipv6': True,
                'tor_proxy': 'strict'
            },
            firewall_rules=[
                'deny all incoming',
                'deny all outgoing',
                'allow vpn only',
                'allow tor only'
            ],
            compositor_effects=False,
            display_brightness=60,
            refresh_rate=60,
            audio_profile='balanced',
            notification_sounds=False,
            auto_start_apps=[
                'tor-browser', 'vpn-client', 'password-manager',
                'encrypted-messenger', 'privacy-dashboard'
            ],
            kill_apps=[
                'chrome', 'social-media', 'cloud-sync',
                'telemetry', 'analytics'
            ],
            nice_adjustments={},
            suspend_timeout=1,  # Quick lock
            screen_timeout=1,
            lock_screen=True,
            vpn_required=True,
            pre_switch_hook='shred -vfz ~/.cache/* 2>/dev/null',
            post_switch_hook='notify-send "🔐 Privacy Mode" "All traffic encrypted"'
        ),
        
        # Learning Mode - Optimized for studying and research
        "learning": ModeProfile(
            name=SystemMode.FOCUS,
            description="Distraction-free learning environment with research tools",
            enable_services=[
                'reference-manager', 'note-taking', 'pdf-tools',
                'dictionary', 'translator', 'jupyter'
            ],
            disable_services=[
                'gaming', 'social-media', 'entertainment',
                'notifications', 'mail'
            ],
            cpu_governor='powersave',  # Quiet operation
            gpu_profile='battery',
            memory_swappiness=60,
            network_optimizations={
                'block_distractions': True,
                'academic_sites_priority': True,
                'youtube_education_only': True
            },
            firewall_rules=['block entertainment'],
            compositor_effects=False,
            display_brightness=70,  # Easy on eyes
            refresh_rate=60,
            audio_profile='quiet',  # For libraries
            notification_sounds=False,
            auto_start_apps=[
                'obsidian', 'anki', 'zotero', 'calibre',
                'focus-timer', 'white-noise'
            ],
            kill_apps=['discord', 'slack', 'games'],
            nice_adjustments={},
            suspend_timeout=30,
            screen_timeout=15,
            lock_screen=True,
            vpn_required=False,
            pre_switch_hook='focus-timer --start 25',
            post_switch_hook='notify-send "📚 Learning Mode" "25-minute focus timer started"'
        ),
        
        # Recording Mode - For streaming, screencasting, tutorials
        "recording": ModeProfile(
            name=SystemMode.STREAMING,
            description="Optimized for recording: stable performance, no interruptions",
            enable_services=[
                'obs-studio', 'audio-processing', 'virtual-camera',
                'streaming-tools', 'noise-suppression'
            ],
            disable_services=[
                'updates', 'indexing', 'backup', 'sync',
                'notifications', 'screen-saver'
            ],
            cpu_governor='performance',
            gpu_profile='performance',  # Hardware encoding
            memory_swappiness=10,  # No stutters
            network_optimizations={
                'streaming_priority': True,
                'low_latency': True,
                'upload_optimize': True
            },
            firewall_rules=['allow streaming'],
            compositor_effects=False,  # Clean recording
            display_brightness=100,
            refresh_rate=60,  # Consistent framerate
            audio_profile='broadcasting',
            notification_sounds=False,  # Silent
            auto_start_apps=[
                'obs', 'audio-mixer', 'script-prompter',
                'camera-app'
            ],
            kill_apps=['everything-else'],
            nice_adjustments={
                'obs': -10,
                'encoder': -10
            },
            suspend_timeout=None,
            screen_timeout=None,
            lock_screen=False,
            vpn_required=False,
            pre_switch_hook='do-not-disturb --force',
            post_switch_hook='notify-send "🎬 Recording Mode" "All interruptions disabled"'
        ),
        
        # Compilation Mode - For building large projects
        "compilation": ModeProfile(
            name=SystemMode.PERFORMANCE,
            description="Maximum CPU/RAM for compilation and builds",
            enable_services=['distcc', 'ccache'],
            disable_services=['everything-non-essential'],
            cpu_governor='performance',
            gpu_profile='off',  # Unless CUDA compilation
            memory_swappiness=0,  # Use all RAM
            network_optimizations={},
            firewall_rules=[],
            compositor_effects=False,
            display_brightness=50,
            refresh_rate=30,  # Save resources
            audio_profile='disabled',
            notification_sounds=False,
            auto_start_apps=['htop', 'build-monitor'],
            kill_apps=['browsers', 'editors'],  # Close IDE during build
            nice_adjustments={'make': -20},  # Maximum priority
            suspend_timeout=None,
            screen_timeout=60,
            lock_screen=False,
            vpn_required=False,
            pre_switch_hook='ccache -s',
            post_switch_hook='notify-send "⚙️ Compilation Mode" "All cores at maximum"'
        )
    }


class ExtendedModeManager(SystemModeManager):
    """Extended mode manager with additional sophisticated modes"""
    
    def __init__(self):
        super().__init__()
        # Add extended profiles
        extended = get_extended_profiles()
        self.profiles.update(extended)
        
        # Mode scheduling rules
        self.schedule_rules = {
            'weekday_morning': 'developer',
            'weekday_evening': 'learning',
            'weekend_morning': 'creative',
            'late_night': 'meditation'
        }
        
    def suggest_mode_by_context(self) -> Optional[str]:
        """Suggest mode based on current context"""
        import datetime
        import psutil
        
        now = datetime.datetime.now()
        hour = now.hour
        weekday = now.weekday() < 5
        
        # Time-based suggestions
        if weekday:
            if 6 <= hour < 9:
                return 'developer'
            elif 9 <= hour < 17:
                return 'work'
            elif 17 <= hour < 20:
                return 'learning'
            elif 20 <= hour < 23:
                return 'creative'
            else:
                return 'meditation'
        else:  # Weekend
            if 8 <= hour < 12:
                return 'creative'
            elif 12 <= hour < 18:
                return 'gaming'
            else:
                return 'privacy'
        
    def auto_switch_by_app(self, app_name: str) -> Optional[str]:
        """Auto-switch mode based on launched application"""
        app_mode_map = {
            'obs': 'recording',
            'blender': 'creative',
            'vscode': 'developer',
            'steam': 'gaming',
            'zoom': 'presentation',
            'tor-browser': 'privacy',
            'make': 'compilation'
        }
        
        for app, mode in app_mode_map.items():
            if app in app_name.lower():
                return mode
        return None
    
    def create_custom_blend(self, modes: List[str], weights: Optional[List[float]] = None) -> ModeProfile:
        """Blend multiple modes into a custom profile"""
        if weights is None:
            weights = [1.0 / len(modes)] * len(modes)
        
        # Start with base profile
        blended = self.profiles[modes[0]].__dict__.copy()
        
        # Blend services (union)
        all_enable = set()
        all_disable = set()
        for mode, weight in zip(modes, weights):
            profile = self.profiles.get(mode)
            if profile and weight > 0.3:  # Only include if significant weight
                all_enable.update(profile.enable_services)
                all_disable.update(profile.disable_services)
        
        blended['enable_services'] = list(all_enable - all_disable)
        blended['disable_services'] = list(all_disable)
        
        # Average numeric values
        for key in ['memory_swappiness', 'display_brightness', 'refresh_rate']:
            values = []
            for mode in modes:
                profile = self.profiles.get(mode)
                if profile:
                    val = getattr(profile, key)
                    if val is not None:
                        values.append(val)
            if values:
                blended[key] = sum(values) / len(values)
        
        return ModeProfile(**blended)