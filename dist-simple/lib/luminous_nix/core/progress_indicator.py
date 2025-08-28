#!/usr/bin/env python3
"""
from typing import List, Optional
Progress Indicator System

Provides real-time feedback for long-running operations with:
- Multiple progress styles (spinner, bar, steps)
- Time estimates
- Friendly messages
- Cancelation support
"""

import asyncio
import time
from typing import Optional, Callable, List, Any
from dataclasses import dataclass
from enum import Enum
import threading
from datetime import datetime, timedelta


class ProgressStyle(Enum):
    """Different visual styles for progress"""
    SPINNER = "spinner"
    BAR = "bar"
    STEPS = "steps"
    DOTS = "dots"
    PULSE = "pulse"


@dataclass
class ProgressStep:
    """A single step in a multi-step operation"""
    name: str
    description: str
    weight: float = 1.0  # Relative time weight
    completed: bool = False
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class ProgressIndicator:
    """Smart progress indication with time estimates"""
    
    # Spinner frames for different moods
    SPINNERS = {
        "default": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "dots": ["⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈"],
        "pulse": ["·", "•", "●", "●", "•", "·", " ", " "],
        "nixos": ["❄️ ", "❄️.", "❄️..", "❄️...", "❄️..", "❄️.", "❄️ ", " "],
        "flow": ["🌊", "🌊.", "🌊..", "🌊...", "🌊..", "🌊.", "🌊", " "],
    }
    
    # Friendly messages for different operations
    MESSAGES = {
        "package_search": [
            "Searching the Nix universe...",
            "Looking through packages...",
            "Finding what you need...",
            "Almost there..."
        ],
        "package_install": [
            "Preparing installation...",
            "Downloading packages...",
            "Building dependencies...",
            "Setting up environment...",
            "Finalizing installation..."
        ],
        "system_update": [
            "Checking for updates...",
            "Downloading new packages...",
            "Building system configuration...",
            "Preparing switch...",
            "Updating your system..."
        ],
        "garbage_collect": [
            "Analyzing store...",
            "Finding unused packages...",
            "Calculating space to free...",
            "Removing old generations...",
            "Cleaning up..."
        ],
        "default": [
            "Working on it...",
            "Processing...",
            "Almost done...",
            "Just a moment..."
        ]
    }
    
    def __init__(
        self,
        style: ProgressStyle = ProgressStyle.SPINNER,
        callback: Optional[Callable[[str], None]] = None
    ):
        self.style = style
        self.callback = callback or print
        self.is_running = False
        self.current_step = 0
        self.total_steps = 0
        self.start_time = None
        self.steps: List[ProgressStep] = []
        self.current_message = ""
        self.spinner_frame = 0
        self._thread = None
        self._stop_event = threading.Event()
    
    def start(
        self,
        operation_type: str = "default",
        total_steps: Optional[int] = None,
        message: Optional[str] = None
    ):
        """Start showing progress"""
        self.is_running = True
        self.start_time = time.time()
        self.operation_type = operation_type
        self.total_steps = total_steps or len(self.steps)
        self.current_message = message or self._get_message(0)
        self._stop_event.clear()
        
        # Start animation thread
        self._thread = threading.Thread(target=self._animate)
        self._thread.daemon = True
        self._thread.start()
    
    def update(
        self,
        current: Optional[int] = None,
        message: Optional[str] = None,
        step_name: Optional[str] = None
    ):
        """Update progress state"""
        if current is not None:
            self.current_step = current
            
        if message:
            self.current_message = message
        elif step_name:
            # Find and update step
            for i, step in enumerate(self.steps):
                if step.name == step_name:
                    step.completed = True
                    step.end_time = time.time()
                    self.current_step = i + 1
                    self.current_message = step.description
                    break
        else:
            # Auto-update message based on progress
            self.current_message = self._get_message(self.current_step)
    
    def add_step(self, name: str, description: str, weight: float = 1.0):
        """Add a step for multi-step operations"""
        self.steps.append(ProgressStep(name, description, weight))
        self.total_steps = len(self.steps)
    
    def complete(self, message: Optional[str] = None):
        """Mark operation as complete"""
        self.is_running = False
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=0.5)
        
        # Show completion message
        elapsed = self._format_duration(time.time() - self.start_time)
        complete_msg = message or "✅ Complete!"
        self.callback(f"\r{complete_msg} (took {elapsed})")
        self.callback("")  # New line
    
    def error(self, message: str):
        """Mark operation as failed"""
        self.is_running = False
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=0.5)
        
        self.callback(f"\r❌ {message}")
        self.callback("")  # New line
    
    def _animate(self):
        """Animation thread for progress display"""
        while not self._stop_event.is_set():
            if self.style == ProgressStyle.SPINNER:
                self._show_spinner()
            elif self.style == ProgressStyle.BAR:
                self._show_bar()
            elif self.style == ProgressStyle.STEPS:
                self._show_steps()
            elif self.style == ProgressStyle.DOTS:
                self._show_dots()
            elif self.style == ProgressStyle.PULSE:
                self._show_pulse()
            
            time.sleep(0.1)
    
    def _show_spinner(self):
        """Show spinner animation"""
        spinner_type = "nixos" if "nix" in self.operation_type.lower() else "default"
        frames = self.SPINNERS[spinner_type]
        frame = frames[self.spinner_frame % len(frames)]
        self.spinner_frame += 1
        
        # Build progress line
        if self.total_steps > 0:
            progress = f" [{self.current_step}/{self.total_steps}]"
        else:
            progress = ""
        
        # Time estimate
        time_info = self._get_time_estimate()
        
        line = f"\r{frame} {self.current_message}{progress} {time_info}"
        self.callback(line.ljust(80), end="")
    
    def _show_bar(self):
        """Show progress bar"""
        if self.total_steps == 0:
            self._show_spinner()  # Fall back to spinner
            return
        
        # Calculate percentage
        percent = (self.current_step / self.total_steps) * 100
        bar_width = 30
        filled = int(bar_width * self.current_step / self.total_steps)
        
        # Build bar
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Time estimate
        time_info = self._get_time_estimate()
        
        line = f"\r[{bar}] {percent:.0f}% - {self.current_message} {time_info}"
        self.callback(line.ljust(80), end="")
    
    def _show_steps(self):
        """Show step-by-step progress"""
        if not self.steps:
            self._show_spinner()
            return
        
        # Clear and show all steps
        lines = ["\r" + " " * 80]  # Clear line
        for i, step in enumerate(self.steps):
            if step.completed:
                icon = "✅"
            elif i == self.current_step:
                icon = "🔄"
            else:
                icon = "⏳"
            
            lines.append(f"{icon} {step.description}")
        
        # Add time estimate
        time_info = self._get_time_estimate()
        lines.append(f"\n{time_info}")
        
        # Move cursor up to overwrite
        up_moves = "\033[A" * len(lines)
        self.callback(up_moves + "\n".join(lines))
    
    def _show_dots(self):
        """Show dots animation"""
        dots = "." * ((self.spinner_frame % 4) + 1)
        line = f"\r{self.current_message}{dots}".ljust(80)
        self.callback(line, end="")
        self.spinner_frame += 1
    
    def _show_pulse(self):
        """Show pulse animation"""
        frames = self.SPINNERS["pulse"]
        frame = frames[self.spinner_frame % len(frames)]
        self.spinner_frame += 1
        
        line = f"\r{frame} {self.current_message} {frame}".ljust(80)
        self.callback(line, end="")
    
    def _get_message(self, step: int) -> str:
        """Get appropriate message for current step"""
        messages = self.MESSAGES.get(self.operation_type, self.MESSAGES["default"])
        if step < len(messages):
            return messages[step]
        return messages[-1]
    
    def _get_time_estimate(self) -> str:
        """Get time elapsed and estimate"""
        if not self.start_time:
            return ""
        
        elapsed = time.time() - self.start_time
        
        # If we have steps, estimate remaining time
        if self.total_steps > 0 and self.current_step > 0:
            avg_time_per_step = elapsed / self.current_step
            remaining_steps = self.total_steps - self.current_step
            estimated_remaining = avg_time_per_step * remaining_steps
            
            if estimated_remaining > 1:
                return f"({self._format_duration(elapsed)} / ~{self._format_duration(estimated_remaining)} left)"
        
        return f"({self._format_duration(elapsed)})"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


class AsyncProgressIndicator(ProgressIndicator):
    """Async version of progress indicator"""
    
    async def start_async(
        self,
        operation_type: str = "default",
        total_steps: Optional[int] = None,
        message: Optional[str] = None
    ):
        """Start progress indicator asynchronously"""
        self.start(operation_type, total_steps, message)
        await asyncio.sleep(0.1)  # Let animation start
    
    async def update_async(
        self,
        current: Optional[int] = None,
        message: Optional[str] = None,
        step_name: Optional[str] = None
    ):
        """Update progress asynchronously"""
        self.update(current, message, step_name)
        await asyncio.sleep(0.05)  # Small delay for smooth animation
    
    async def complete_async(self, message: Optional[str] = None):
        """Complete progress asynchronously"""
        self.complete(message)
        await asyncio.sleep(0.1)


# Context manager for automatic cleanup
class progress_context:
    """Context manager for progress indication"""
    
    def __init__(
        self,
        operation_type: str = "default",
        style: ProgressStyle = ProgressStyle.SPINNER,
        message: Optional[str] = None
    ):
        self.operation_type = operation_type
        self.style = style
        self.message = message
        self.indicator = None
    
    def __enter__(self) -> ProgressIndicator:
        self.indicator = ProgressIndicator(style=self.style)
        self.indicator.start(self.operation_type, message=self.message)
        return self.indicator
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.indicator:
            if exc_type:
                self.indicator.error(f"Operation failed: {exc_val}")
            else:
                self.indicator.complete()


# Demo
if __name__ == "__main__":
    import random
    
    # Demo 1: Simple spinner
    print("Demo 1: Simple spinner")
    with progress_context("package_search") as progress:
        time.sleep(2)
    
    # Demo 2: Progress bar
    print("\nDemo 2: Progress bar")
    progress = ProgressIndicator(style=ProgressStyle.BAR)
    progress.start("package_install", total_steps=5)
    
    for i in range(5):
        time.sleep(1)
        progress.update(i + 1)
    
    progress.complete("Installation complete!")
    
    # Demo 3: Multi-step operation
    print("\nDemo 3: Multi-step operation")
    progress = ProgressIndicator(style=ProgressStyle.STEPS)
    progress.add_step("download", "Downloading packages")
    progress.add_step("extract", "Extracting files")
    progress.add_step("build", "Building from source")
    progress.add_step("install", "Installing to system")
    
    progress.start("package_install")
    
    for step in ["download", "extract", "build", "install"]:
        time.sleep(1.5)
        progress.update(step_name=step)
    
    progress.complete("Package installed successfully!")