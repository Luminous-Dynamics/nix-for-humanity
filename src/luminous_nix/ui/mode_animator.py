#!/usr/bin/env python3
"""
Mode Animator - Beautiful transition animations for system mode changes

This module provides smooth, visual transitions when switching between
different system modes, making the transformation feel organic and intentional.
"""

import asyncio
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn


class AnimationType(Enum):
    """Types of transition animations"""

    FADE = "fade"
    SLIDE = "slide"
    MORPH = "morph"
    PARTICLE = "particle"
    WAVE = "wave"
    DISSOLVE = "dissolve"
    MATRIX = "matrix"
    SPIRAL = "spiral"


@dataclass
class TransitionFrame:
    """Single frame in an animation"""

    content: str
    duration: float  # seconds
    color: Optional[str] = None


class ModeAnimator:
    """
    Handles beautiful animations for mode transitions

    Each mode has its own personality:
    - Gaming: Fast, energetic, RGB-like
    - Privacy: Smooth, discrete, minimal
    - Developer: Technical, matrix-like
    - Creative: Colorful, flowing, artistic
    - Minimal: Clean, simple, zen-like
    - Server: Systematic, reliable, stable
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize the animator"""
        self.console = console or Console()

        # Mode personalities (colors and animations)
        self.mode_themes = {
            "gaming": {
                "colors": ["red", "green", "blue", "magenta", "cyan"],
                "animation": AnimationType.PARTICLE,
                "speed": 0.02,
            },
            "privacy": {
                "colors": ["dim", "grey", "white"],
                "animation": AnimationType.FADE,
                "speed": 0.05,
            },
            "developer": {
                "colors": ["green", "bright_green"],
                "animation": AnimationType.MATRIX,
                "speed": 0.01,
            },
            "creative": {
                "colors": ["magenta", "yellow", "cyan", "bright_magenta"],
                "animation": AnimationType.WAVE,
                "speed": 0.03,
            },
            "minimal": {
                "colors": ["white", "bright_white"],
                "animation": AnimationType.DISSOLVE,
                "speed": 0.04,
            },
            "server": {
                "colors": ["blue", "bright_blue"],
                "animation": AnimationType.SLIDE,
                "speed": 0.02,
            },
        }

    async def animate_transition(
        self,
        from_mode: str,
        to_mode: str,
        callback: Optional[Callable] = None,
        duration: float = 2.0,
    ):
        """Animate transition between modes"""

        # Get animation type
        animation_type = self.mode_themes.get(to_mode, {}).get(
            "animation", AnimationType.FADE
        )

        # Select animation
        if animation_type == AnimationType.FADE:
            await self._animate_fade(from_mode, to_mode, duration)
        elif animation_type == AnimationType.MATRIX:
            await self._animate_matrix(from_mode, to_mode, duration)
        elif animation_type == AnimationType.PARTICLE:
            await self._animate_particle(from_mode, to_mode, duration)
        elif animation_type == AnimationType.WAVE:
            await self._animate_wave(from_mode, to_mode, duration)
        elif animation_type == AnimationType.DISSOLVE:
            await self._animate_dissolve(from_mode, to_mode, duration)
        else:
            await self._animate_slide(from_mode, to_mode, duration)

        # Execute callback if provided
        if callback:
            callback()

    async def _animate_fade(self, from_mode: str, to_mode: str, duration: float):
        """Fade transition animation"""

        steps = 20
        step_duration = duration / steps

        with Live(console=self.console, refresh_per_second=30) as live:
            for i in range(steps + 1):
                opacity = i / steps

                # Create fading text
                if i < steps // 2:
                    # Fade out old mode
                    text = self._create_mode_display(from_mode, 1 - opacity * 2)
                else:
                    # Fade in new mode
                    text = self._create_mode_display(to_mode, (opacity - 0.5) * 2)

                live.update(text)
                await asyncio.sleep(step_duration)

    async def _animate_matrix(self, from_mode: str, to_mode: str, duration: float):
        """Matrix-style transition animation"""

        width = 60
        height = 20

        with Live(console=self.console, refresh_per_second=30) as live:
            start_time = time.time()

            while time.time() - start_time < duration:
                # Create matrix rain effect
                matrix = []
                for _ in range(height):
                    row = ""
                    for _ in range(width):
                        if random.random() > 0.7:
                            char = random.choice("01アイウエオカキクケコ")
                            color = random.choice(["green", "bright_green", "dim"])
                            row += f"[{color}]{char}[/{color}]"
                        else:
                            row += " "
                    matrix.append(row)

                # Add mode text in center
                progress = (time.time() - start_time) / duration
                if progress < 0.5:
                    mode_text = f"[bold white]{from_mode.upper()}[/bold white]"
                else:
                    mode_text = (
                        f"[bold bright_green]{to_mode.upper()}[/bold bright_green]"
                    )

                matrix[height // 2] = " " * ((width - len(to_mode)) // 2) + mode_text

                panel = Panel(
                    "\n".join(matrix),
                    border_style="green",
                    title="[bold]MODE TRANSFORMATION[/bold]",
                )

                live.update(panel)
                await asyncio.sleep(0.03)

    async def _animate_particle(self, from_mode: str, to_mode: str, duration: float):
        """Particle explosion animation"""

        class Particle:
            def __init__(self, x, y, vx, vy, char, color):
                self.x = x
                self.y = y
                self.vx = vx
                self.vy = vy
                self.char = char
                self.color = color

            def update(self, dt):
                self.x += self.vx * dt
                self.y += self.vy * dt
                self.vy += 9.8 * dt  # gravity

        # Initialize particles
        particles = []
        colors = self.mode_themes.get(to_mode, {}).get("colors", ["white"])

        for char in from_mode.upper():
            for _ in range(5):  # Multiple particles per character
                particles.append(
                    Particle(
                        x=30,
                        y=10,
                        vx=random.uniform(-20, 20),
                        vy=random.uniform(-15, 5),
                        char=char,
                        color=random.choice(colors),
                    )
                )

        with Live(console=self.console, refresh_per_second=30) as live:
            start_time = time.time()

            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                progress = elapsed / duration

                # Create display grid
                width, height = 80, 24
                grid = [[" " for _ in range(width)] for _ in range(height)]

                # Update and render particles
                for p in particles:
                    p.update(0.1)

                    # Convert to grid coordinates
                    gx = int(p.x)
                    gy = int(p.y)

                    if 0 <= gx < width and 0 <= gy < height:
                        grid[gy][gx] = f"[{p.color}]{p.char}[/{p.color}]"

                # Add new mode text (appearing gradually)
                if progress > 0.5:
                    mode_text = to_mode.upper()
                    start_x = (width - len(mode_text)) // 2
                    for i, char in enumerate(mode_text):
                        if random.random() < (progress - 0.5) * 2:
                            grid[height // 2][
                                start_x + i
                            ] = f"[bold {colors[0]}]{char}[/bold {colors[0]}]"

                # Convert grid to string
                display = "\n".join("".join(row) for row in grid)

                live.update(Panel(display, border_style=colors[0]))
                await asyncio.sleep(0.03)

    async def _animate_wave(self, from_mode: str, to_mode: str, duration: float):
        """Wave transition animation"""

        width = 60
        height = 20

        with Live(console=self.console, refresh_per_second=30) as live:
            start_time = time.time()

            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                progress = elapsed / duration

                lines = []
                for y in range(height):
                    line = ""
                    for x in range(width):
                        # Create wave pattern
                        wave = (x + elapsed * 20) / 10
                        intensity = abs(y - height / 2 - 5 * sin(wave))

                        if intensity < 2:
                            if progress < 0.5:
                                char = from_mode[int(x / 10) % len(from_mode)]
                            else:
                                char = to_mode[int(x / 10) % len(to_mode)]

                            colors = self.mode_themes.get(to_mode, {}).get(
                                "colors", ["white"]
                            )
                            color = colors[int(wave) % len(colors)]
                            line += f"[{color}]{char}[/{color}]"
                        else:
                            line += " "

                    lines.append(line)

                display = "\n".join(lines)

                title = f"[bold]Transitioning: {from_mode} → {to_mode}[/bold]"
                live.update(Panel(display, title=title))
                await asyncio.sleep(0.03)

    async def _animate_dissolve(self, from_mode: str, to_mode: str, duration: float):
        """Dissolve transition animation"""

        steps = 30
        step_duration = duration / steps

        from_text = self._create_ascii_art(from_mode)
        to_text = self._create_ascii_art(to_mode)

        with Live(console=self.console, refresh_per_second=30) as live:
            for step in range(steps + 1):
                progress = step / steps

                # Randomly dissolve pixels
                display_lines = []
                for i in range(max(len(from_text), len(to_text))):
                    line = ""

                    from_line = from_text[i] if i < len(from_text) else " " * 60
                    to_line = to_text[i] if i < len(to_text) else " " * 60

                    for j in range(max(len(from_line), len(to_line))):
                        if random.random() > progress:
                            # Show from_mode character
                            char = from_line[j] if j < len(from_line) else " "
                            line += f"[dim]{char}[/dim]"
                        else:
                            # Show to_mode character
                            char = to_line[j] if j < len(to_line) else " "
                            line += f"[bright_white]{char}[/bright_white]"

                    display_lines.append(line)

                display = "\n".join(display_lines)
                live.update(Panel(display, title="[bold]Mode Transition[/bold]"))
                await asyncio.sleep(step_duration)

    async def _animate_slide(self, from_mode: str, to_mode: str, duration: float):
        """Slide transition animation"""

        width = 60
        steps = 30
        step_duration = duration / steps

        from_panel = self._create_mode_panel(from_mode)
        to_panel = self._create_mode_panel(to_mode)

        with Live(console=self.console, refresh_per_second=30) as live:
            for step in range(steps + 1):
                progress = step / steps
                offset = int(progress * width)

                # Create sliding effect
                display_lines = []
                for i in range(10):
                    line = ""

                    # Old mode sliding out
                    if offset < width:
                        from_part = (
                            from_panel[i][offset:]
                            if i < len(from_panel)
                            else " " * (width - offset)
                        )
                        line += from_part[: width - offset]

                    # New mode sliding in
                    if offset > 0:
                        to_part = (
                            to_panel[i][:offset] if i < len(to_panel) else " " * offset
                        )
                        line += to_part

                    display_lines.append(line)

                display = "\n".join(display_lines)
                live.update(
                    Panel(
                        display, title=f"[bold]Activating {to_mode.upper()} Mode[/bold]"
                    )
                )
                await asyncio.sleep(step_duration)

    def _create_mode_display(self, mode: str, opacity: float) -> Panel:
        """Create a display panel for a mode with given opacity"""

        colors = self.mode_themes.get(mode, {}).get("colors", ["white"])

        if opacity < 0.3:
            style = "dim"
        elif opacity < 0.7:
            style = colors[0]
        else:
            style = f"bold {colors[0]}"

        content = f"""
        [{style}]
        ╔══════════════════════════════════════╗
        ║                                      ║
        ║      {mode.upper():^30}      ║
        ║                                      ║
        ╚══════════════════════════════════════╝
        [/{style}]
        """

        return Panel(Align.center(content, vertical="middle"), border_style=style)

    def _create_ascii_art(self, mode: str) -> list[str]:
        """Create ASCII art for a mode"""

        # Simple ASCII representations
        ascii_art = {
            "gaming": [
                "  ▄████  ▄▄▄       ███▄ ▄███▓ ██▓ ███▄    █   ▄████ ",
                " ██▒ ▀█▒▒████▄    ▓██▒▀█▀ ██▒▓██▒ ██ ▀█   █  ██▒ ▀█▒",
                "▒██░▄▄▄░▒██  ▀█▄  ▓██    ▓██░▒██▒▓██  ▀█ ██▒▒██░▄▄▄░",
                "░▓█  ██▓░██▄▄▄▄██ ▒██    ▒██ ░██░▓██▒  ▐▌██▒░▓█  ██▓",
                "░▒▓███▀▒ ▓█   ▓██▒▒██▒   ░██▒░██░▒██░   ▓██░░▒▓███▀▒",
            ],
            "privacy": [
                "╔═══════════════════╗",
                "║  🔒 PRIVACY MODE  ║",
                "║   Secure & Safe   ║",
                "╚═══════════════════╝",
            ],
            "developer": [
                "< DEVELOPER MODE >",
                " ─────────────────",
                "  ▶ Code",
                "  ▶ Build",
                "  ▶ Deploy",
            ],
            "creative": [
                "✨ CREATIVE MODE ✨",
                "   🎨 🎭 🎪 🎯",
                "  Unleash Ideas",
            ],
            "minimal": [
                "   minimal",
                "   ───────",
                "   simple",
                "   clean",
                "   focused",
            ],
            "server": [
                "┌─────────────┐",
                "│ SERVER MODE │",
                "├─────────────┤",
                "│ ▣ Services  │",
                "│ ▣ Uptime    │",
                "└─────────────┘",
            ],
        }

        return ascii_art.get(mode, [mode.upper()])

    def _create_mode_panel(self, mode: str) -> list[str]:
        """Create a panel representation for a mode"""

        colors = self.mode_themes.get(mode, {}).get("colors", ["white"])

        panel = []
        panel.append("═" * 60)
        panel.append(f"  Mode: {mode.upper()}")
        panel.append("─" * 60)

        # Mode-specific content
        if mode == "gaming":
            panel.extend(
                [
                    "  🎮 High Performance",
                    "  ⚡ GPU Acceleration",
                    "  🔊 Enhanced Audio",
                ]
            )
        elif mode == "privacy":
            panel.extend(
                [
                    "  🔒 VPN Active",
                    "  🛡️ Firewall Enabled",
                    "  👁️ Trackers Blocked",
                ]
            )
        elif mode == "developer":
            panel.extend(
                [
                    "  💻 Dev Tools Ready",
                    "  🔧 Build Systems",
                    "  📦 Package Managers",
                ]
            )
        elif mode == "creative":
            panel.extend(
                [
                    "  🎨 Creative Suite",
                    "  🎵 Audio Tools",
                    "  📸 Image Editors",
                ]
            )
        elif mode == "minimal":
            panel.extend(
                [
                    "  ⚪ Essentials Only",
                    "  🔇 Quiet Mode",
                    "  💤 Low Power",
                ]
            )
        elif mode == "server":
            panel.extend(
                [
                    "  🖥️ Server Services",
                    "  📊 Monitoring",
                    "  🔄 Auto-updates",
                ]
            )

        panel.append("═" * 60)

        # Pad to consistent height
        while len(panel) < 10:
            panel.append(" " * 60)

        return panel

    def create_progress_animation(
        self,
        from_mode: str,
        to_mode: str,
        steps: list[tuple[str, float]],  # (description, duration)
    ):
        """Create a progress-based transition animation"""

        colors = self.mode_themes.get(to_mode, {}).get("colors", ["white"])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        ) as progress:
            # Main transition task
            main_task = progress.add_task(
                f"[{colors[0]}]Transitioning to {to_mode.upper()} mode...[/{colors[0]}]",
                total=len(steps),
            )

            for description, duration in steps:
                # Sub-task for each step
                sub_task = progress.add_task(f"[dim]{description}[/dim]", total=100)

                # Animate progress
                for i in range(100):
                    time.sleep(duration / 100)
                    progress.update(sub_task, advance=1)

                progress.update(main_task, advance=1)
                progress.remove_task(sub_task)

            # Final message
            self.console.print(
                f"\n[bold {colors[0]}]✨ {to_mode.upper()} mode activated![/bold {colors[0]}]"
            )

    def get_transition_steps(
        self, from_mode: str, to_mode: str
    ) -> list[tuple[str, float]]:
        """Get the transition steps for a mode change"""

        # Mode-specific transition steps
        steps = {
            "gaming": [
                ("Maximizing GPU performance", 0.5),
                ("Disabling compositing", 0.3),
                ("Setting CPU governor to performance", 0.4),
                ("Configuring audio for low latency", 0.3),
                ("Starting game mode services", 0.5),
            ],
            "privacy": [
                ("Activating VPN connection", 1.0),
                ("Enabling firewall rules", 0.5),
                ("Blocking tracking domains", 0.4),
                ("Clearing browser data", 0.3),
                ("Starting Tor services", 0.8),
            ],
            "developer": [
                ("Starting language servers", 0.6),
                ("Loading development databases", 0.8),
                ("Mounting project directories", 0.3),
                ("Starting Docker daemon", 1.0),
                ("Initializing build caches", 0.5),
            ],
            "creative": [
                ("Loading creative applications", 0.7),
                ("Calibrating color profiles", 0.5),
                ("Initializing audio interfaces", 0.6),
                ("Mounting asset libraries", 0.4),
                ("Starting render engines", 0.8),
            ],
            "minimal": [
                ("Stopping unnecessary services", 0.6),
                ("Reducing CPU frequency", 0.3),
                ("Disabling animations", 0.2),
                ("Clearing memory caches", 0.4),
                ("Entering power save mode", 0.5),
            ],
            "server": [
                ("Starting web servers", 0.8),
                ("Initializing databases", 1.0),
                ("Setting up monitoring", 0.5),
                ("Configuring firewall", 0.4),
                ("Starting scheduled tasks", 0.6),
            ],
        }

        return steps.get(
            to_mode,
            [
                ("Preparing configuration", 0.5),
                ("Applying settings", 0.5),
                ("Restarting services", 1.0),
            ],
        )


# Helper function for sin
def sin(x):
    """Simple sine approximation"""
    import math

    return math.sin(x)


async def demo():
    """Demo the mode animator"""

    animator = ModeAnimator()

    # Test different animations
    modes = ["minimal", "gaming", "developer", "privacy", "creative", "server"]

    for i in range(len(modes) - 1):
        from_mode = modes[i]
        to_mode = modes[i + 1]

        print(f"\n\nTransitioning: {from_mode} → {to_mode}")
        await animator.animate_transition(from_mode, to_mode, duration=2.0)
        time.sleep(1)

    # Test progress animation
    print("\n\nProgress-based transition:")
    animator.create_progress_animation(
        "minimal", "gaming", animator.get_transition_steps("minimal", "gaming")
    )


if __name__ == "__main__":
    asyncio.run(demo())
