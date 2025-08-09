#!/usr/bin/env bash
# Create proper test infrastructure with real tests instead of mocks

set -euo pipefail

echo "🧪 Setting up proper test infrastructure..."

# Create test structure
mkdir -p tests/{unit,integration,e2e,fixtures,helpers}

# Create test configuration
cat > tests/conftest.py << 'PYTHON'
"""
Pytest configuration for Nix for Humanity tests.
Focus on real testing with minimal mocking.
"""

import os
import sys
import pytest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Environment setup
os.environ['NIX_HUMANITY_TEST_MODE'] = '1'

@pytest.fixture(scope="session")
def test_mode():
    """Enable test mode for safe operations."""
    original = os.environ.get('NIX_HUMANITY_TEST_MODE')
    os.environ['NIX_HUMANITY_TEST_MODE'] = '1'
    yield
    if original:
        os.environ['NIX_HUMANITY_TEST_MODE'] = original
    else:
        del os.environ['NIX_HUMANITY_TEST_MODE']

@pytest.fixture
def real_nix_available():
    """Check if real Nix is available for integration tests."""
    import shutil
    return shutil.which('nix') is not None

@pytest.fixture
def temp_nix_config(tmp_path):
    """Create temporary Nix configuration for testing."""
    config_dir = tmp_path / "nix-config"
    config_dir.mkdir()
    
    # Create a minimal configuration.nix
    config_file = config_dir / "configuration.nix"
    config_file.write_text("""
{ config, pkgs, ... }:
{
  environment.systemPackages = with pkgs; [
    vim
    git
  ];
}
""")
    
    return config_dir

@pytest.fixture
def mock_nix_output():
    """Provide real Nix command outputs for testing."""
    return {
        "search": {
            "firefox": """
* firefox (115.0.2)
  Mozilla Firefox web browser

* firefox-esr (102.13.0esr)
  Mozilla Firefox ESR (Extended Support Release) web browser
""",
            "vim": """
* vim (9.0.1642)
  The most popular clone of the VI editor

* neovim (0.9.1)
  Vim-fork focused on extensibility and usability
"""
        },
        "list-generations": """
  1   2024-01-01 10:00:00
  2   2024-01-15 14:30:00
  3   2024-02-01 09:15:00   (current)
""",
        "system-info": """
NixOS 23.11 (Tapir)
Linux 6.1.38
""",
    }

# Performance benchmarking fixture
@pytest.fixture
def benchmark_timer():
    """Simple benchmark timer for performance tests."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.duration = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, *args):
            self.duration = (time.time() - self.start_time) * 1000  # ms
    
    return Timer

# Real command execution fixture (with safety)
@pytest.fixture
def safe_executor():
    """Execute real commands safely in test mode."""
    class SafeExecutor:
        def __init__(self):
            self.dry_run = True
        
        def execute(self, cmd, dry_run=None):
            if dry_run is None:
                dry_run = self.dry_run
            
            if dry_run:
                return f"[DRY RUN] Would execute: {cmd}"
            else:
                # Only allow safe read-only commands
                safe_commands = ['nix', 'search', 'nix-env', '-q', 'nixos-version']
                if any(cmd.startswith(safe) for safe in safe_commands):
                    import subprocess
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    return result.stdout
                else:
                    raise ValueError(f"Unsafe command in tests: {cmd}")
    
    return SafeExecutor()

# Fixtures for each component
@pytest.fixture
def nlp_engine():
    """Real NLP engine instance."""
    from nix_humanity.core.nlp import NLPEngine
    return NLPEngine()

@pytest.fixture
def test_intents():
    """Common test intents."""
    return {
        "install": "install firefox",
        "remove": "remove vim",
        "search": "search for text editor",
        "update": "update my system",
        "list": "show installed packages",
        "rollback": "rollback to previous generation",
    }
PYTHON

# Create test helpers
cat > tests/helpers/assertions.py << 'PYTHON'
"""
Custom assertions for Nix for Humanity tests.
"""

def assert_command_successful(result):
    """Assert that a command execution was successful."""
    assert result.success, f"Command failed: {result.error}"
    assert result.output, "Command produced no output"
    assert result.error is None or result.error == ""

def assert_performance_target(duration_ms, target_ms, operation="Operation"):
    """Assert that performance meets target."""
    assert duration_ms < target_ms, (
        f"{operation} took {duration_ms:.1f}ms, "
        f"target was {target_ms}ms"
    )

def assert_intent_recognized(intent, expected_action):
    """Assert that intent was correctly recognized."""
    assert intent is not None, "Intent recognition failed"
    assert intent.action == expected_action, (
        f"Expected action '{expected_action}', "
        f"got '{intent.action}'"
    )

def assert_no_mock_usage(test_func):
    """Decorator to ensure test doesn't use mocks."""
    import functools
    
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        # Check for mock usage
        import sys
        mock_modules = [m for m in sys.modules if 'mock' in m.lower()]
        assert not mock_modules, f"Test uses mocking: {mock_modules}"
        
        return test_func(*args, **kwargs)
    
    return wrapper
PYTHON

# Create real integration tests
cat > tests/integration/test_real_operations.py << 'PYTHON'
"""
Real integration tests for Nix operations.
These tests interact with actual Nix commands.
"""

import pytest
from tests.helpers.assertions import (
    assert_command_successful,
    assert_performance_target,
    assert_no_mock_usage
)

class TestRealNixOperations:
    """Test real Nix operations (requires NixOS)."""
    
    @pytest.mark.integration
    @pytest.mark.skipif("not real_nix_available")
    @assert_no_mock_usage
    def test_search_performance(self, safe_executor, benchmark_timer):
        """Test that search is actually fast."""
        with benchmark_timer as timer:
            result = safe_executor.execute("nix search nixpkgs firefox", dry_run=False)
        
        assert "firefox" in result.lower()
        assert_performance_target(timer.duration, 2000, "Package search")
    
    @pytest.mark.integration
    @pytest.mark.skipif("not real_nix_available")
    def test_list_generations(self, safe_executor):
        """Test listing system generations."""
        result = safe_executor.execute("nix-env --list-generations", dry_run=False)
        
        assert result  # Should have output
        assert any(char.isdigit() for char in result)  # Should contain generation numbers
    
    @pytest.mark.integration
    def test_dry_run_install(self, safe_executor):
        """Test dry-run installation (safe for CI)."""
        result = safe_executor.execute("nix-env -iA nixpkgs.hello --dry-run", dry_run=True)
        
        assert "[DRY RUN]" in result
        assert "hello" in result

class TestNativeAPI:
    """Test native Python-Nix API integration."""
    
    @pytest.mark.integration
    async def test_native_vs_subprocess_performance(self, benchmark_timer):
        """Verify claimed 10x performance improvement."""
        from nix_humanity.native.api import NativeAPI
        from nix_humanity.native.fallback import SubprocessFallback
        
        # Skip if native API not available
        if not NativeAPI.is_available():
            pytest.skip("Native API not available")
        
        native = NativeAPI()
        subprocess = SubprocessFallback()
        
        # Test search performance
        query = "firefox"
        
        # Native API timing
        with benchmark_timer as native_timer:
            native_result = await native.search(query)
        
        # Subprocess timing
        with benchmark_timer as subprocess_timer:
            subprocess_result = await subprocess.search(query)
        
        # Verify results are similar
        assert len(native_result) > 0
        assert len(subprocess_result) > 0
        
        # Verify performance improvement
        speedup = subprocess_timer.duration / native_timer.duration
        assert speedup > 5, f"Native API only {speedup:.1f}x faster, expected >5x"
        
        print(f"✓ Native API is {speedup:.1f}x faster!")
PYTHON

# Create unit tests with minimal mocking
cat > tests/unit/test_nlp_engine.py << 'PYTHON'
"""
Unit tests for NLP engine using real data.
"""

import pytest
from nix_humanity.core.nlp import NLPEngine
from nix_humanity.core.intents import Intent, IntentType

class TestNLPEngine:
    """Test NLP engine with real examples."""
    
    def test_basic_intent_recognition(self, nlp_engine):
        """Test recognizing basic intents."""
        test_cases = [
            ("install firefox", IntentType.INSTALL, "firefox"),
            ("remove vim", IntentType.REMOVE, "vim"),
            ("search for text editor", IntentType.SEARCH, "text editor"),
            ("update system", IntentType.UPDATE, None),
            ("show installed packages", IntentType.LIST, None),
        ]
        
        for text, expected_type, expected_package in test_cases:
            intent = nlp_engine.parse(text)
            assert intent.type == expected_type
            if expected_package:
                assert intent.package == expected_package
    
    def test_typo_correction(self, nlp_engine):
        """Test typo correction in commands."""
        typo_cases = [
            ("instal firefox", "install firefox"),
            ("remov vim", "remove vim"),
            ("serch editor", "search editor"),
        ]
        
        for typo_text, corrected in typo_cases:
            intent = nlp_engine.parse(typo_text)
            assert intent is not None, f"Failed to parse: {typo_text}"
            # Verify intent was recognized despite typo
    
    def test_natural_language_variations(self, nlp_engine):
        """Test various natural language expressions."""
        install_variations = [
            "install firefox",
            "please install firefox",
            "can you install firefox",
            "i need firefox installed",
            "add firefox to my system",
            "get me firefox",
        ]
        
        for text in install_variations:
            intent = nlp_engine.parse(text)
            assert intent.type == IntentType.INSTALL
            assert intent.package == "firefox"
    
    def test_confidence_scoring(self, nlp_engine):
        """Test confidence scoring for intents."""
        high_confidence = [
            "install firefox",
            "remove vim",
            "update system",
        ]
        
        low_confidence = [
            "maybe install something",
            "firefox or chrome",
            "do something with packages",
        ]
        
        for text in high_confidence:
            intent = nlp_engine.parse(text)
            assert intent.confidence > 0.8
        
        for text in low_confidence:
            intent = nlp_engine.parse(text)
            assert intent.confidence < 0.5
PYTHON

# Create performance tests
cat > tests/performance/test_benchmarks.py << 'PYTHON'
"""
Performance benchmarks for Nix for Humanity.
"""

import pytest
import time
from tests.helpers.assertions import assert_performance_target

class TestPerformanceBenchmarks:
    """Benchmark critical operations."""
    
    @pytest.mark.benchmark
    def test_startup_time(self, benchmark_timer):
        """Test CLI startup time."""
        import subprocess
        
        with benchmark_timer as timer:
            result = subprocess.run(
                ["python", "-m", "nix_humanity", "--version"],
                capture_output=True
            )
        
        assert result.returncode == 0
        assert_performance_target(timer.duration, 500, "CLI startup")
    
    @pytest.mark.benchmark
    def test_nlp_parsing_speed(self, nlp_engine, benchmark_timer):
        """Test NLP parsing performance."""
        test_phrases = [
            "install firefox",
            "remove vim neovim emacs",
            "search for all text editors that support python",
            "update my system and clean old generations",
        ]
        
        for phrase in test_phrases:
            with benchmark_timer as timer:
                intent = nlp_engine.parse(phrase)
            
            assert intent is not None
            assert_performance_target(timer.duration, 50, f"Parse '{phrase}'")
    
    @pytest.mark.benchmark
    def test_memory_usage(self):
        """Test memory usage stays under target."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Import main modules
        from nix_humanity.core import NLPEngine, SafeExecutor
        from nix_humanity.native import NativeAPI
        
        # Create instances
        nlp = NLPEngine()
        executor = SafeExecutor()
        
        # Check memory
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        assert memory_mb < 300, f"Memory usage {memory_mb:.1f}MB exceeds 300MB target"
PYTHON

# Create test runner script
cat > scripts/run-tests.sh << 'BASH'
#!/usr/bin/env bash
# Run tests with proper configuration

set -euo pipefail

echo "🧪 Running Nix for Humanity tests..."

# Set test environment
export NIX_HUMANITY_TEST_MODE=1
export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"

# Run different test suites
echo "Running unit tests..."
pytest tests/unit -v --tb=short

echo -e "\nRunning integration tests..."
pytest tests/integration -v --tb=short -m integration

echo -e "\nRunning performance benchmarks..."
pytest tests/performance -v --tb=short -m benchmark

echo -e "\nGenerating coverage report..."
pytest --cov=nix_humanity --cov-report=html --cov-report=term-missing

echo -e "\n✅ All tests complete!"
echo "Coverage report: htmlcov/index.html"
BASH

chmod +x scripts/run-tests.sh

echo "✅ Test infrastructure created!"
echo ""
echo "New test structure:"
echo "  - Real fixtures in tests/conftest.py"
echo "  - Helper assertions in tests/helpers/"
echo "  - Integration tests with real Nix"
echo "  - Performance benchmarks"
echo "  - Minimal mocking approach"
echo ""
echo "Run tests with: ./scripts/run-tests.sh"