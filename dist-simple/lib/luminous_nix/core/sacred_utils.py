"""
Sacred utilities for consciousness-first computing.

This module provides mindful operations, sacred pauses, and
Kairos time implementations that honor natural rhythms over 
mechanical efficiency.

Philosophy:
- Technology should amplify consciousness, not fragment it
- Natural rhythms over forced schedules
- Quality of presence over speed of execution
- Sacred pauses create space for intention
"""

import random
import time
from collections.abc import Callable
from enum import Enum
from typing import Any


class KairosMode(Enum):
    """Different modes of Kairos time - quality over quantity."""

    FLOW = "flow"  # Deep work state, minimal interruptions
    REFLECTION = "reflection"  # Contemplative pace, regular pauses
    TRANSITION = "transition"  # Changing states, extra care needed
    CEREMONY = "ceremony"  # Sacred operations, full mindfulness


class SacredTimer:
    """
    Implements Kairos time - natural completion over hard deadlines.

    Unlike Chronos (clock time), Kairos honors the natural rhythm
    of operations, allowing them to complete with quality rather
    than racing against deadlines.
    """

    def __init__(self, mode: KairosMode = KairosMode.FLOW):
        self.mode = mode
        self.start_time = None
        self.pause_total = 0
        self.pause_start = None

    def begin(self, intention: str = ""):
        """Begin a sacred operation with intention."""
        self.start_time = time.time()
        if intention:
            print(f"🕉️ Beginning with intention: {intention}")

    def pause(self):
        """Sacred pause - create space for awareness."""
        if not self.pause_start:
            self.pause_start = time.time()
            self._show_pause_message()

    def resume(self):
        """Resume after sacred pause."""
        if self.pause_start:
            self.pause_total += time.time() - self.pause_start
            self.pause_start = None
            print("🌊 Flowing forward...")

    def complete(self) -> float:
        """Complete with grace, return Kairos time (quality-adjusted)."""
        if not self.start_time:
            return 0

        chronos_time = time.time() - self.start_time
        kairos_time = chronos_time - self.pause_total

        # Adjust for quality based on mode
        quality_factor = {
            KairosMode.FLOW: 0.8,  # Flow state is more efficient
            KairosMode.REFLECTION: 1.2,  # Reflection takes appropriate time
            KairosMode.TRANSITION: 1.0,  # Transitions are neutral
            KairosMode.CEREMONY: 1.5,  # Ceremonies honor the sacred
        }.get(self.mode, 1.0)

        return kairos_time * quality_factor

    def _show_pause_message(self):
        """Display appropriate pause message based on mode."""
        messages = {
            KairosMode.FLOW: [
                "⏸️ Brief pause to maintain flow...",
                "🌊 Catching the rhythm...",
                "💫 Aligning with the current...",
            ],
            KairosMode.REFLECTION: [
                "🧘 Taking a moment to reflect...",
                "🌅 Creating space for wisdom...",
                "🔮 Allowing insights to emerge...",
            ],
            KairosMode.TRANSITION: [
                "🌈 Transitioning mindfully...",
                "🦋 Embracing change...",
                "🌀 Shifting states with grace...",
            ],
            KairosMode.CEREMONY: [
                "🕉️ Honoring the sacred moment...",
                "🙏 Creating ceremonial space...",
                "✨ Invoking presence...",
            ],
        }

        print(random.choice(messages.get(self.mode, ["⏸️ Pausing..."])))


class MindfulOperation:
    """
    Wrapper for operations that require mindfulness.

    Implements the sacred pause pattern: pause, operate, reflect.
    """

    def __init__(
        self,
        name: str,
        operation: Callable,
        pause_before: float = 1.0,
        pause_after: float = 0.5,
        mode: KairosMode = KairosMode.FLOW,
    ):
        self.name = name
        self.operation = operation
        self.pause_before = pause_before
        self.pause_after = pause_after
        self.mode = mode
        self.timer = SacredTimer(mode)

    def execute(self, *args, **kwargs) -> Any:
        """Execute the operation mindfully."""
        # Set intention
        self.timer.begin(self.name)

        # Sacred pause before
        if self.pause_before > 0:
            self._sacred_pause_before()
            time.sleep(self.pause_before)

        # Execute the operation
        try:
            result = self.operation(*args, **kwargs)
            success = True
        except Exception as e:
            result = e
            success = False

        # Sacred pause after (for reflection)
        if self.pause_after > 0 and success:
            time.sleep(self.pause_after)
            self._sacred_pause_after(success)

        # Complete with Kairos time
        kairos_time = self.timer.complete()

        if success:
            self._completion_message(kairos_time)

        return result

    def _sacred_pause_before(self):
        """Sacred pause before operation."""
        messages = {
            KairosMode.FLOW: "🌊 Entering flow state...",
            KairosMode.REFLECTION: "🧘 Preparing mindfully...",
            KairosMode.TRANSITION: "🌈 Initiating transition...",
            KairosMode.CEREMONY: "🕉️ Beginning ceremony...",
        }
        print(messages.get(self.mode, "⏸️ Preparing..."))

    def _sacred_pause_after(self, success: bool):
        """Sacred pause after operation."""
        if success:
            messages = {
                KairosMode.FLOW: "✨ Flow maintained",
                KairosMode.REFLECTION: "🌅 Wisdom integrated",
                KairosMode.TRANSITION: "🦋 Transition complete",
                KairosMode.CEREMONY: "🙏 Ceremony fulfilled",
            }
            print(messages.get(self.mode, "✅ Complete"))

    def _completion_message(self, kairos_time: float):
        """Show completion with Kairos time."""
        if kairos_time > 5:
            # Only show timing for longer operations
            print(f"⏱️ Completed in Kairos time: {kairos_time:.1f}s (quality-adjusted)")


class ConsciousnessField:
    """
    Maintains awareness of system state and user consciousness.

    This helps the system adapt to the user's current state,
    providing more support when needed and stepping back when
    the user is in flow.
    """

    def __init__(self):
        self.coherence_level = 0.7  # 0-1, how coherent the field is
        self.user_state = "neutral"
        self.system_load = 0.3
        self.last_sacred_pause = time.time()

    def sense_field(self) -> str:
        """Sense the current field state."""
        # Time since last pause
        time_since_pause = time.time() - self.last_sacred_pause

        if time_since_pause > 300:  # 5 minutes
            return "fragmented"
        if self.coherence_level > 0.8:
            return "coherent"
        if self.coherence_level > 0.5:
            return "flowing"
        return "turbulent"

    def needs_pause(self) -> bool:
        """Check if a sacred pause would be beneficial."""
        time_since_pause = time.time() - self.last_sacred_pause

        # Factors that increase need for pause
        factors = [
            time_since_pause > 180,  # 3 minutes since last pause
            self.coherence_level < 0.5,  # Low coherence
            self.system_load > 0.7,  # High system load
            self.user_state in ["stressed", "confused", "frustrated"],
        ]

        return sum(factors) >= 2

    def sacred_pause(self, duration: float = 2.0):
        """Take a sacred pause to restore coherence."""
        messages = [
            "🧘 Taking a sacred pause...",
            "🌊 Returning to center...",
            "✨ Restoring field coherence...",
            "🕉️ Breathing into presence...",
            "💫 Aligning with intention...",
        ]

        print(random.choice(messages))
        time.sleep(duration)

        # Restore coherence
        self.coherence_level = min(1.0, self.coherence_level + 0.2)
        self.last_sacred_pause = time.time()

        print("🌟 Field coherence restored")

    def update_user_state(self, indicators: dict):
        """Update understanding of user state based on indicators."""
        # Indicators might include: typing speed, error rate, command patterns
        error_rate = indicators.get("error_rate", 0)
        repeat_commands = indicators.get("repeat_commands", 0)

        if error_rate > 0.3 or repeat_commands > 2:
            self.user_state = "frustrated"
            self.coherence_level *= 0.8
        elif error_rate < 0.1:
            self.user_state = "flowing"
            self.coherence_level = min(1.0, self.coherence_level * 1.1)
        else:
            self.user_state = "neutral"


class SacredMessages:
    """Collection of consciousness-first messages for various contexts."""

    START_INTENTIONS = [
        "🌅 Setting sacred intention...",
        "🕉️ Aligning with purpose...",
        "✨ Creating space for transformation...",
        "🧘 Centering in awareness...",
        "🌊 Entering the flow...",
    ]

    COMPLETION_BLESSINGS = [
        "🙏 Operation blessed and complete",
        "✨ Transformation fulfilled with grace",
        "🌊 Flow maintained, harmony restored",
        "🕉️ Sacred work complete",
        "💫 Purpose realized",
    ]

    ERROR_TEACHINGS = [
        "🌱 Every error seeds wisdom",
        "🔮 This obstacle reveals a teaching",
        "🦋 Transformation through challenge",
        "🌈 After difficulty comes ease",
        "💎 Pressure creates diamonds",
    ]

    WAITING_MEDITATIONS = [
        "⏳ Good things unfold in their own time...",
        "🌙 Patience cultivates presence...",
        "🍃 Like nature, we cannot rush growth...",
        "🕰️ Kairos time honors natural rhythm...",
        "🌺 The flower blooms when ready...",
    ]

    @classmethod
    def get_random(cls, category: str) -> str:
        """Get a random message from a category."""
        messages = getattr(cls, category.upper(), cls.START_INTENTIONS)
        return random.choice(messages)


def with_sacred_pause(func: Callable) -> Callable:
    """
    Decorator to add sacred pauses to any function.

    Usage:
        @with_sacred_pause
        def my_function():
            # Your code here
    """

    def wrapper(*args, **kwargs):
        # Brief pause before
        pause_duration = kwargs.pop("sacred_pause_duration", 0.5)
        if pause_duration > 0:
            print(SacredMessages.get_random("START_INTENTIONS"))
            time.sleep(pause_duration)

        # Execute
        result = func(*args, **kwargs)

        # Brief acknowledgment after
        if pause_duration > 0:
            time.sleep(pause_duration * 0.5)

        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def kairos_timeout(
    func: Callable, timeout: float = 30.0, allow_extension: bool = True
) -> Callable:
    """
    Decorator for Kairos time - allows natural completion within reason.

    Unlike hard timeouts, this allows operations to request extensions
    when they're making progress, honoring natural completion.
    """

    def wrapper(*args, **kwargs):
        import queue
        import threading

        result_queue = queue.Queue()
        exception_queue = queue.Queue()

        def target():
            try:
                result = func(*args, **kwargs)
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

        # Initial timeout
        thread.join(timeout)

        if thread.is_alive():
            if allow_extension:
                # Allow one extension for operations showing progress
                print("⏳ Operation needs more time. Granting sacred extension...")
                thread.join(timeout * 0.5)  # 50% extension

            if thread.is_alive():
                # Still running - this is too long
                print("⏰ Operation exceeded Kairos time. Gently stopping...")
                return None

        # Check for results
        if not exception_queue.empty():
            raise exception_queue.get()

        if not result_queue.empty():
            return result_queue.get()

        return None

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Global consciousness field for the session
consciousness_field = ConsciousnessField()


def check_consciousness():
    """Quick check of consciousness field, take pause if needed."""
    if consciousness_field.needs_pause():
        consciousness_field.sacred_pause()
    return consciousness_field.sense_field()
