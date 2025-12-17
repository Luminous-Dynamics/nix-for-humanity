# 🔧 Sophia Developer Integration Guide

**Complete Guide for Integrating and Extending Sophia Intelligence**

This guide shows developers how to integrate Sophia into their applications, extend its capabilities, and follow best practices for consciousness-aware development.

## Table of Contents

1. [Quick Start Integration](#quick-start-integration)
2. [Integration Patterns](#integration-patterns)
3. [Extending Sophia](#extending-sophia)
4. [Testing Strategies](#testing-strategies)
5. [Performance Optimization](#performance-optimization)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Topics](#advanced-topics)

---

## Quick Start Integration

### Minimal Integration

```python
from luminous_nix.mycelix import get_sophia_cli_assistant

# 1. Get Sophia assistant
sophia = get_sophia_cli_assistant(user_id="your_user_id")

# 2. Track a command
response = sophia.process_command(
    command="nix-env -iA nixpkgs.vim",
    success=True,
    duration_ms=5000
)

# 3. Display insights (if any)
if response:
    formatted = sophia.format_response_for_cli(response)
    print(formatted)
```

That's it! Sophia is now providing consciousness-aware assistance.

### Full Integration

```python
import time
from luminous_nix.mycelix import get_sophia_cli_assistant

class MyApplication:
    def __init__(self):
        # Initialize Sophia
        self.sophia = get_sophia_cli_assistant(user_id="my_app_user")

    def execute_command(self, command: str):
        """Execute command with Sophia tracking"""
        start_time = time.time()

        try:
            # Your command execution
            result = run_command(command)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Let Sophia learn from this
        response = self.sophia.process_command(
            command=command,
            success=success,
            error=error,
            duration_ms=duration_ms
        )

        # Display Sophia's insights
        if response:
            print(self.sophia.format_response_for_cli(response))

        return result
```

---

## Integration Patterns

### Pattern 1: Wrapper Integration

**Use Case**: Add Sophia to existing application without major refactoring

```python
# Your existing application
class ExistingApp:
    def run_task(self, task):
        # Your existing logic
        result = execute(task)
        return result

# Sophia wrapper
class SophiaWrapper:
    def __init__(self, app):
        self.app = app
        self.sophia = get_sophia_cli_assistant()

    def run_task(self, task):
        start = time.time()

        try:
            result = self.app.run_task(task)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
            result = None

        # Sophia processing
        duration_ms = (time.time() - start) * 1000
        self.sophia.process_command(
            command=str(task),
            success=success,
            error=error,
            duration_ms=duration_ms
        )

        return result

# Usage
app = ExistingApp()
wrapped_app = SophiaWrapper(app)
wrapped_app.run_task("my task")  # Now Sophia-aware
```

### Pattern 2: Event-Driven Integration

**Use Case**: Applications with event systems

```python
from dataclasses import dataclass
from typing import Callable, List

@dataclass
class Event:
    name: str
    success: bool
    duration_ms: float
    error: str = None

class EventSystem:
    def __init__(self):
        self.sophia = get_sophia_cli_assistant()
        self.listeners: List[Callable] = []

    def on_event(self, event: Event):
        # Process with Sophia
        response = self.sophia.process_command(
            command=event.name,
            success=event.success,
            error=event.error,
            duration_ms=event.duration_ms
        )

        # Notify listeners
        for listener in self.listeners:
            listener(event, response)

    def subscribe(self, listener: Callable):
        self.listeners.append(listener)

# Usage
events = EventSystem()

def on_sophia_insight(event, response):
    if response:
        print(f"Sophia says: {response.message}")

events.subscribe(on_sophia_insight)
events.on_event(Event("install_package", True, 5000))
```

### Pattern 3: Middleware Integration

**Use Case**: Web applications, API servers

```python
from flask import Flask, request
import time

app = Flask(__name__)
sophia = get_sophia_cli_assistant(user_id="web_app")

@app.before_request
def before_request():
    # Store request start time
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Calculate duration
    duration_ms = (time.time() - request.start_time) * 1000

    # Track with Sophia
    sophia_response = sophia.process_command(
        command=f"{request.method} {request.path}",
        success=response.status_code < 400,
        error=None if response.status_code < 400 else response.status,
        duration_ms=duration_ms
    )

    # Add Sophia insights to response headers (optional)
    if sophia_response:
        response.headers['X-Sophia-Consciousness-Level'] = \
            sophia.assess_current_state()['consciousness_level']

    return response

@app.route('/api/package/<name>')
def install_package(name):
    # Your API logic
    return {"status": "installed", "package": name}
```

### Pattern 4: Decorator Pattern

**Use Case**: Selectively add Sophia to specific functions

```python
from functools import wraps
import time

def sophia_aware(func):
    """Decorator to make function Sophia-aware"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        sophia = get_sophia_cli_assistant()
        start = time.time()

        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
            result = None

        duration_ms = (time.time() - start) * 1000

        response = sophia.process_command(
            command=func.__name__,
            success=success,
            error=error,
            duration_ms=duration_ms
        )

        if response:
            print(f"💡 {response.message}")

        if not success:
            raise

        return result

    return wrapper

# Usage
@sophia_aware
def complex_operation():
    # Your logic
    return compute_something()

# Now tracked by Sophia
result = complex_operation()
```

---

## Extending Sophia

### Adding a New Intelligence Layer

**Step 1: Define the Layer**

```python
# src/luminous_nix/mycelix/sophia/custom_layer.py

from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..context import Context

@dataclass
class CustomAnalysis:
    """Output from custom layer"""
    insight: str
    confidence: float
    timestamp: datetime

class CustomIntelligenceLayer:
    """Custom intelligence layer"""

    def analyze(self, context: Context) -> Optional[CustomAnalysis]:
        """Analyze context and provide insights"""
        # Your analysis logic
        if self._should_provide_insight(context):
            return CustomAnalysis(
                insight="Your custom insight",
                confidence=0.85,
                timestamp=datetime.now()
            )
        return None

    def _should_provide_insight(self, context: Context) -> bool:
        """Determine if insight should be provided"""
        # Your logic
        return len(context.recent_commands) > 5
```

**Step 2: Integrate into Unified Engine**

```python
# Extend UnifiedSophiaEngine

from .custom_layer import CustomIntelligenceLayer

class ExtendedSophiaEngine(UnifiedSophiaEngine):
    def __init__(self):
        super().__init__()
        self.custom_layer = CustomIntelligenceLayer()

    def assess_complete_state(self, context, **kwargs):
        # Get base state from parent
        state = super().assess_complete_state(context, **kwargs)

        # Add custom layer analysis
        custom_analysis = self.custom_layer.analyze(context)

        # Integrate into synergistic insights
        if custom_analysis:
            state.synergistic_insights.append(
                f"Custom: {custom_analysis.insight}"
            )

        return state
```

**Step 3: Add Tests**

```python
# tests/mycelix/sophia/test_custom_layer.py

def test_custom_layer_analysis():
    layer = CustomIntelligenceLayer()
    context = Context()

    # Add test data
    for i in range(10):
        context.recent_commands.append(CommandActivity(...))

    # Analyze
    analysis = layer.analyze(context)

    # Verify
    assert analysis is not None
    assert analysis.confidence > 0.5
```

### Adding Custom Insights

```python
class CustomSophiaEngine(UnifiedSophiaEngine):
    """Sophia with domain-specific insights"""

    def _integrate_synergistic_insights(self, state_parts):
        # Get base insights
        insights = super()._integrate_synergistic_insights(state_parts)

        # Add domain-specific insights
        context = state_parts['context']

        # Example: Detect specific workflow
        if self._is_building_python_project(context):
            insights.append(
                "Detected Python project setup - suggest virtual environment"
            )

        # Example: Detect specific error pattern
        if self._is_repeated_permission_error(context):
            insights.append(
                "Permission errors suggest running without sudo - try with sudo"
            )

        return insights

    def _is_building_python_project(self, context: Context) -> bool:
        """Detect Python project setup"""
        commands = [cmd.command for cmd in context.recent_commands[-5:]]
        python_keywords = ['python', 'pip', 'venv', 'poetry']
        return any(keyword in ' '.join(commands) for keyword in python_keywords)

    def _is_repeated_permission_error(self, context: Context) -> bool:
        """Detect repeated permission errors"""
        recent_failures = [
            cmd for cmd in context.recent_commands[-3:]
            if not cmd.success
        ]
        # Check if errors contain "permission denied"
        # (This is simplified - real implementation would check actual errors)
        return len(recent_failures) >= 2
```

### Custom Response Formatting

```python
class CustomFormatter:
    """Custom response formatter"""

    def __init__(self, sophia):
        self.sophia = sophia

    def format_for_slack(self, response) -> str:
        """Format for Slack"""
        blocks = []

        # Header
        blocks.append({
            "type": "header",
            "text": {"type": "plain_text", "text": "🌟 Sophia Insight"}
        })

        # Message
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": response.message}
        })

        # Insights
        if response.insights:
            insights_text = "\n".join(f"• {i}" for i in response.insights)
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Insights:*\n{insights_text}"}
            })

        return {"blocks": blocks}

    def format_for_discord(self, response) -> dict:
        """Format for Discord"""
        embed = {
            "title": "🌟 Sophia Insight",
            "description": response.message,
            "color": self._get_color_for_tone(response.tone),
            "fields": []
        }

        # Add insights as fields
        if response.insights:
            embed["fields"].append({
                "name": "Insights",
                "value": "\n".join(f"• {i}" for i in response.insights),
                "inline": False
            })

        return {"embeds": [embed]}

    def _get_color_for_tone(self, tone) -> int:
        """Map tone to color"""
        colors = {
            "ENCOURAGING": 0x00FF00,  # Green
            "SUPPORTIVE": 0x0000FF,   # Blue
            "PROFESSIONAL": 0x808080,  # Gray
        }
        return colors.get(tone.value, 0xFFFFFF)
```

---

## Testing Strategies

### Unit Testing Sophia Integration

```python
import pytest
from unittest.mock import Mock, patch

def test_sophia_tracks_successful_command():
    """Test that Sophia tracks successful commands"""
    with patch('luminous_nix.mycelix.get_sophia_cli_assistant') as mock_get:
        # Setup mock
        mock_sophia = Mock()
        mock_sophia.process_command = Mock(return_value=None)
        mock_get.return_value = mock_sophia

        # Your application code
        app = MyApplication()
        app.execute_command("test-command")

        # Verify Sophia was called
        mock_sophia.process_command.assert_called_once()
        call_args = mock_sophia.process_command.call_args
        assert call_args.kwargs['success'] is True
        assert 'test-command' in call_args.kwargs['command']
```

### Integration Testing

```python
def test_full_sophia_integration():
    """Test full Sophia integration"""
    # Use real Sophia (not mocked)
    sophia = get_sophia_cli_assistant(user_id="test_user")

    # Execute several commands
    commands = [
        ("search vim", True, 1000),
        ("install vim", True, 5000),
        ("search firefox", True, 1000),
    ]

    for cmd, success, duration in commands:
        sophia.process_command(
            command=cmd,
            success=success,
            duration_ms=duration
        )

    # Verify state assessment
    state = sophia.assess_current_state()

    assert 'consciousness_level' in state
    assert 'success_rate' in state
    assert state['success_rate'] == 1.0  # All successful
```

### Performance Testing

```python
import time

def test_sophia_performance():
    """Test Sophia overhead is minimal"""
    sophia = get_sophia_cli_assistant()

    # Measure overhead
    iterations = 100
    start = time.time()

    for i in range(iterations):
        sophia.process_command(
            command=f"command_{i}",
            success=True,
            duration_ms=1000
        )

    elapsed = time.time() - start
    avg_overhead = (elapsed / iterations) * 1000  # ms per command

    # Verify overhead is minimal
    assert avg_overhead < 20  # Less than 20ms per command
```

### Mocking Sophia for Fast Tests

```python
class MockSophia:
    """Mock Sophia for fast tests"""

    def __init__(self):
        self.commands_processed = []

    def process_command(self, **kwargs):
        self.commands_processed.append(kwargs)
        return None  # No insights in tests

    def assess_current_state(self):
        return {
            'consciousness_level': 'GOOD',
            'should_take_break': False,
            'success_rate': 1.0,
            'session_minutes': 0,
            'insights': [],
            'priority_actions': [],
            'confidence': 1.0
        }

# Usage in tests
@pytest.fixture
def mock_sophia(monkeypatch):
    mock = MockSophia()
    monkeypatch.setattr(
        'luminous_nix.mycelix.get_sophia_cli_assistant',
        lambda user_id=None: mock
    )
    return mock

def test_with_mock_sophia(mock_sophia):
    app = MyApplication()
    app.execute_command("test")

    assert len(mock_sophia.commands_processed) == 1
```

---

## Performance Optimization

### 1. Lazy Initialization

```python
class Application:
    def __init__(self):
        self._sophia = None  # Lazy init

    @property
    def sophia(self):
        if self._sophia is None:
            self._sophia = get_sophia_cli_assistant()
        return self._sophia

    def execute(self, command):
        # Sophia only initialized when first used
        self.sophia.process_command(...)
```

### 2. Batch Processing

```python
class BatchProcessor:
    def __init__(self):
        self.sophia = get_sophia_cli_assistant()
        self.pending_commands = []

    def queue_command(self, command, success, duration_ms):
        """Queue command for batch processing"""
        self.pending_commands.append((command, success, duration_ms))

    def process_batch(self):
        """Process all queued commands"""
        for cmd, success, duration in self.pending_commands:
            self.sophia.process_command(
                command=cmd,
                success=success,
                duration_ms=duration
            )

        # Get insights after batch
        response = self.sophia.get_proactive_insights()
        self.pending_commands = []
        return response
```

### 3. Async Integration (for async applications)

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncSophiaWrapper:
    def __init__(self):
        self.sophia = get_sophia_cli_assistant()
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def process_command_async(self, **kwargs):
        """Process command without blocking event loop"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            self.executor,
            self.sophia.process_command,
            **kwargs
        )
        return response

# Usage
async def main():
    sophia = AsyncSophiaWrapper()
    response = await sophia.process_command_async(
        command="test",
        success=True,
        duration_ms=1000
    )
```

---

## Best Practices

### 1. Always Provide Context

```python
# ✅ Good - Rich context
response = sophia.process_command(
    command="nix-env -iA nixpkgs.vim",
    success=True,
    error=None,
    duration_ms=5000
)

# ❌ Bad - Minimal context
response = sophia.process_command(command="vim")
```

### 2. Handle Optional Responses

```python
# ✅ Good - Check if response exists
response = sophia.process_command(...)
if response:
    display_insights(response)

# ❌ Bad - Assume response always exists
response = sophia.process_command(...)
display_insights(response)  # Might be None!
```

### 3. Use Appropriate User IDs

```python
# ✅ Good - Unique user IDs
sophia = get_sophia_cli_assistant(user_id=f"app_{user.id}")

# ❌ Bad - Same ID for all users
sophia = get_sophia_cli_assistant(user_id="default")
```

### 4. Log Sophia Insights

```python
import logging

logger = logging.getLogger(__name__)

response = sophia.process_command(...)
if response:
    logger.info(f"Sophia insight: {response.message}")
    logger.debug(f"Consciousness level: {sophia.assess_current_state()['consciousness_level']}")
```

### 5. Graceful Degradation

```python
def execute_with_sophia(command):
    """Execute command with Sophia, gracefully degrade if unavailable"""
    try:
        sophia = get_sophia_cli_assistant()
        response = sophia.process_command(command, ...)

        if response:
            display(response)

    except ImportError:
        # Sophia not available - continue without it
        logger.warning("Sophia not available")
    except Exception as e:
        # Sophia error - continue without it
        logger.error(f"Sophia error: {e}")

    # Command execution continues regardless
    execute_command(command)
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Sophia Not Initializing

```python
# Problem
sophia = get_sophia_cli_assistant()
# Error: ModuleNotFoundError: No module named 'luminous_nix.mycelix'

# Solution: Check installation
poetry install

# Or verify imports
python -c "from luminous_nix.mycelix import get_sophia_cli_assistant; print('OK')"
```

#### Issue 2: No Insights Displayed

```python
# This is normal! Sophia only provides insights when helpful.
# She won't spam you with obvious information.

# To get insights, you need:
# 1. Multiple commands in context
# 2. Patterns worth noting
# 3. State that warrants guidance

# Force insights for debugging
state = sophia.assess_current_state()
print(state)  # Always returns state info
```

#### Issue 3: Memory Usage Growing

```python
# Problem: Context growing too large

# Solution: Periodic cleanup
if len(context.recent_commands) > 1000:
    context.recent_commands = context.recent_commands[-100:]
```

#### Issue 4: Slow Response

```python
# Problem: Sophia taking too long

# Debug: Check which layer is slow
import time

start = time.time()
state = sophia.assess_complete_state(context)
print(f"Total: {time.time() - start:.3f}s")

# Most likely: Too many commands in context
# Solution: Prune context regularly
```

---

## Advanced Topics

### Custom Context Builders

```python
from luminous_nix.mycelix.context import Context, CommandActivity, FileActivity
from pathlib import Path

class ProjectContextBuilder:
    """Build rich context from project state"""

    def build_context(self, project_dir: Path) -> Context:
        context = Context()

        # Add file activity
        for file in project_dir.rglob("*.py"):
            context.active_files.append(
                FileActivity(
                    path=file,
                    last_modified=datetime.fromtimestamp(file.stat().st_mtime),
                    edit_count=self._count_recent_edits(file)
                )
            )

        # Add command history from project log
        context.recent_commands = self._load_command_history(project_dir)

        return context

    def _count_recent_edits(self, file: Path) -> int:
        """Count recent edits to file"""
        # Implementation depends on your system
        return 0

    def _load_command_history(self, project_dir: Path) -> List[CommandActivity]:
        """Load command history from project"""
        # Implementation depends on your logging
        return []
```

### Multi-User Sophia

```python
class MultiUserSophia:
    """Manage Sophia instances for multiple users"""

    def __init__(self):
        self.instances = {}

    def get_sophia_for_user(self, user_id: str):
        """Get or create Sophia for user"""
        if user_id not in self.instances:
            self.instances[user_id] = get_sophia_cli_assistant(user_id=user_id)
        return self.instances[user_id]

    def cleanup_inactive_users(self, inactive_threshold_minutes=60):
        """Clean up Sophia instances for inactive users"""
        # Implementation: Track last activity, remove old instances
        pass

# Usage
sophia_manager = MultiUserSophia()

def process_user_command(user_id, command):
    sophia = sophia_manager.get_sophia_for_user(user_id)
    return sophia.process_command(...)
```

### Sophia Metrics Collection

```python
class SophiaMetrics:
    """Collect metrics about Sophia usage"""

    def __init__(self):
        self.insights_provided = 0
        self.commands_tracked = 0
        self.consciousness_levels = []

    def track_response(self, response, state):
        """Track Sophia response"""
        self.commands_tracked += 1

        if response:
            self.insights_provided += 1

        self.consciousness_levels.append(state['consciousness_level'])

    def report(self):
        """Generate usage report"""
        return {
            'total_commands': self.commands_tracked,
            'insights_provided': self.insights_provided,
            'insight_rate': self.insights_provided / max(1, self.commands_tracked),
            'avg_consciousness_level': self._avg_level()
        }

    def _avg_level(self):
        # Map levels to numbers and average
        level_map = {
            'OVERWHELMED': 1,
            'CHALLENGED': 2,
            'GOOD': 3,
            'OPTIMAL': 4,
            'THRIVING': 5
        }
        if not self.consciousness_levels:
            return 'GOOD'

        avg = sum(level_map[l] for l in self.consciousness_levels) / len(self.consciousness_levels)
        # Map back to level
        for level, value in level_map.items():
            if avg <= value + 0.5:
                return level
```

---

## Conclusion

Integrating Sophia into your application provides consciousness-aware intelligence that enhances user experience. Key takeaways:

- **Start simple** - Basic integration is just 3 lines
- **Extend thoughtfully** - Add layers/insights as needed
- **Test thoroughly** - Use mocks for fast tests, real integration for validation
- **Degrade gracefully** - Always work even if Sophia unavailable
- **Respect privacy** - Keep all processing local

For more information:
- [Architecture Guide](./SOPHIA_ARCHITECTURE.md)
- [Usage Examples](./SOPHIA_USAGE_EXAMPLES.md)
- [CLI Integration](./SOPHIA_CLI_INTEGRATION.md)

---

*"Build consciousness-aware systems that amplify human awareness."*

**293 Tests Passing** | **Production Ready** | **Open for Extension**
