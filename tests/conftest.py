"""
import subprocess
Global test configuration and fixtures.
"""
import sys
from unittest.mock import MagicMock
from pathlib import Path

# Add source directory to path
test_dir = Path(__file__).parent
project_root = test_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Mock optional dependencies that might not be installed
def mock_optional_dependencies():
    """Mock optional dependencies for testing."""
    
    # Mock textual if not available
    try:
        import textual
    except ImportError:
        # Create comprehensive mock textual module
        mock_textual = MagicMock()
        
        # Create mock submodules
        mock_app = MagicMock()
        mock_widget = MagicMock()
        mock_widgets = MagicMock()
        mock_containers = MagicMock()
        mock_screen = MagicMock()
        mock_reactive = MagicMock()
        mock_events = MagicMock()
        mock_message = MagicMock()
        mock_binding = MagicMock()
        
        # Mock the main classes with proper attributes
        mock_app.App = MagicMock()
        mock_app.ComposeResult = list
        mock_widget.Widget = MagicMock()
        mock_widgets.Header = MagicMock()
        mock_widgets.Footer = MagicMock()
        mock_widgets.Input = MagicMock()
        mock_widgets.Static = MagicMock()
        mock_widgets.RichLog = MagicMock()
        mock_widgets.Button = MagicMock()
        mock_widgets.LoadingIndicator = MagicMock()
        mock_widgets.Label = MagicMock()
        mock_widgets.Rule = MagicMock()
        mock_containers.Container = MagicMock()
        mock_containers.Horizontal = MagicMock()
        mock_containers.Vertical = MagicMock()
        mock_containers.ScrollableContainer = MagicMock()
        mock_screen.Screen = MagicMock()
        mock_reactive.reactive = lambda x: x  # Simple decorator mock
        mock_message.Message = MagicMock()
        mock_binding.Binding = MagicMock()
        
        # Set up the main module structure
        mock_textual.app = mock_app
        mock_textual.widget = mock_widget
        mock_textual.widgets = mock_widgets
        mock_textual.containers = mock_containers
        mock_textual.screen = mock_screen
        mock_textual.reactive = mock_reactive
        mock_textual.events = mock_events
        mock_textual.message = mock_message
        mock_textual.binding = mock_binding
        
        # Add direct exports
        mock_textual.App = mock_app.App
        mock_textual.Widget = mock_widget.Widget
        
        # Install all the mocks
        sys.modules['textual'] = mock_textual
        sys.modules['textual.app'] = mock_app
        sys.modules['textual.widget'] = mock_widget
        sys.modules['textual.widgets'] = mock_widgets
        sys.modules['textual.containers'] = mock_containers
        sys.modules['textual.screen'] = mock_screen
        sys.modules['textual.reactive'] = mock_reactive
        sys.modules['textual.events'] = mock_events
        sys.modules['textual.message'] = mock_message
        sys.modules['textual.binding'] = mock_binding
        
    # Mock rich if not available (textual depends on it)
    try:
        import rich
    except ImportError:
        mock_rich = MagicMock()
        mock_markdown = MagicMock()
        mock_panel = MagicMock()
        mock_syntax = MagicMock()
        mock_table = MagicMock()
        
        mock_markdown.Markdown = MagicMock()
        mock_panel.Panel = MagicMock()
        mock_syntax.Syntax = MagicMock()
        mock_table.Table = MagicMock()
        
        mock_rich.markdown = mock_markdown
        mock_rich.panel = mock_panel
        mock_rich.syntax = mock_syntax
        mock_rich.table = mock_table
        
        sys.modules['rich'] = mock_rich
        sys.modules['rich.markdown'] = mock_markdown
        sys.modules['rich.panel'] = mock_panel
        sys.modules['rich.syntax'] = mock_syntax
        sys.modules['rich.table'] = mock_table
        
    # Mock other optional dependencies that might cause issues
    optional_modules = [
        'requests',
        'click', 
        'colorama',
        'blessed',
        'pyperclip',
        'whisper_cpp_python',
        'piper_tts',
        'vosk',
        'py_espeak_ng',
        'flask',
        'gunicorn',
        'PyJWT',
        'pyOpenSSL',
        'websockets',
        'flask_socketio',
        'python_socketio',
        'cryptography',
        'pandas',
        'numpy',
        'nltk',
        'spacy',
        'transformers',
        'torch',
        'sklearn',
        'sentence_transformers',
        'beautifulsoup4',
        'lxml',
        'accelerate',
        'datasets',
        'peft',
        'trl',
        'lancedb',
        'networkx',
        'dowhy',
        'shap',
        'opentelemetry',
    ]
    
    for module_name in optional_modules:
        if module_name not in sys.modules:
            # Don't try to import - just mock missing modules
            sys.modules[module_name] = MagicMock()

# Apply mocking before any imports
mock_optional_dependencies()

# Import pytest after mocking (if available)
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create a mock pytest for basic functionality
    class MockPytest:
        class MonkeyPatch:
            class context:
                def __enter__(self):
                    return MockMonkeyPatch()
                def __exit__(self, *args):
                    pass
        
        @staticmethod
        def fixture(func):
            return func
    
    class MockMonkeyPatch:
        def setattr(self, name, value):
            pass
    
    pytest = MockPytest()


@pytest.fixture
def mock_backend():
    """Mock backend for testing frontends."""
    backend = MagicMock()
    backend.process_request.return_value = MagicMock(
        success=True,
        message="Test response",
        data={}
    )
    return backend


@pytest.fixture
def mock_nix_system():
    """Mock NixOS system calls for testing."""
    with pytest.MonkeyPatch.context() as m:
        # Mock subprocess calls
        mock_run = MagicMock()
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "success"
        mock_run.return_value.stderr = ""
        m.setattr("subprocess.run", mock_run)
        
        # Mock file system operations
        mock_path = MagicMock()
        mock_path.return_value.exists.return_value = True
        m.setattr("pathlib.Path", mock_path)
        
        yield m


@pytest.fixture
def sample_user_input():
    """Sample user inputs for testing."""
    return [
        "install firefox",
        "update my system", 
        "search for text editor",
        "rollback to previous generation",
        "configure ssh",
        "explain nixos",
        "help",
        "what can you do?"
    ]


@pytest.fixture
def mock_learning_data():
    """Mock learning data for testing."""
    return {
        "preferences": {
            "personality": "friendly", 
            "verbosity": "medium"
        },
        "patterns": {
            "firefox": "web browser",
            "code": "text editor"
        },
        "corrections": {
            "fierfix": "firefox",
            "updaet": "update"
        }
    }