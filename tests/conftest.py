"""Pytest configuration and fixtures"""
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


# ============= Backend & Engine Mocks =============


@pytest.fixture
def mock_backend():
    """Mock LuminousNixBackend for testing"""
    backend = Mock()
    backend.execute.return_value = Mock(
        success=True,
        stdout="Command executed successfully",
        stderr="",
        exit_code=0,
        duration=0.5,
    )
    backend.search.return_value = [
        {"name": "firefox", "version": "120.0"},
        {"name": "vim", "version": "9.0"},
    ]
    backend.list_packages.return_value = [
        {"name": "firefox", "version": "120.0"},
        {"name": "vim", "version": "9.0"},
        {"name": "git", "version": "2.42.0"},
    ]
    return backend


@pytest.fixture
def mock_executor():
    """Mock SafeExecutor for testing"""
    executor = Mock()
    executor.execute.return_value = Mock(
        success=True, output="Success", error=None, exit_code=0
    )
    executor.validate_command.return_value = True
    return executor


# ============= Intent & NLP Mocks =============


@pytest.fixture
def sample_intent():
    """Sample intent for testing"""
    return Mock(
        type="INSTALL",
        entities={"package": "firefox"},
        confidence=0.95,
        raw_text="install firefox",
    )


@pytest.fixture
def mock_intent_recognizer():
    """Mock IntentRecognizer"""
    recognizer = Mock()
    recognizer.recognize.return_value = Mock(
        type="INSTALL", entities={"package": "firefox"}, confidence=0.95
    )
    return recognizer


# ============= Execution Results =============


@pytest.fixture
def success_result():
    """Successful execution result"""
    return Mock(
        success=True, output="Command completed successfully", error=None, exit_code=0
    )


@pytest.fixture
def failure_result():
    """Failed execution result"""
    return Mock(
        success=False, output="", error="Command failed: Package not found", exit_code=1
    )


# ============= NixOS Specific =============


@pytest.fixture
def mock_nix_env():
    """Mock Nix environment variables"""
    return {
        "NIX_PATH": "/nix/var/nix/profiles/per-user/root/channels",
        "NIX_PROFILES": "/nix/var/nix/profiles/default",
        "NIX_STORE": "/nix/store",
    }


@pytest.fixture
def sample_packages():
    """Sample package list"""
    return [
        {"name": "firefox", "version": "120.0", "description": "Web browser"},
        {"name": "vim", "version": "9.0", "description": "Text editor"},
        {"name": "git", "version": "2.42.0", "description": "Version control"},
    ]


@pytest.fixture
def sample_config():
    """Sample configuration"""
    return {
        "packages": ["firefox", "vim", "git"],
        "services": {"nginx": {"enable": True}, "ssh": {"enable": True}},
        "environment": {"systemPackages": ["firefox", "vim"]},
    }


# ============= Cache & Database =============


@pytest.fixture
def mock_cache():
    """Mock cache service"""
    cache = Mock()
    cache.get.return_value = None
    cache.set.return_value = True
    cache.clear.return_value = True
    return cache


@pytest.fixture
def mock_database(tmp_path):
    """Mock database connection"""
    db_file = tmp_path / "test.db"
    db = Mock()
    db.path = str(db_file)
    db.execute.return_value = Mock(rowcount=1)
    db.fetchall.return_value = []
    return db


# ============= Temp Directories & Files =============


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for tests"""
    test_dir = tmp_path / "test_luminous"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def temp_config_file(temp_dir):
    """Temporary config file"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("# Test config\npackages: [firefox, vim]")
    return config_file


@pytest.fixture
def temp_nix_config(temp_dir):
    """Temporary Nix configuration"""
    nix_config = temp_dir / "configuration.nix"
    nix_config.write_text(
        """
    { config, pkgs, ... }:
    {
      environment.systemPackages = with pkgs; [
        firefox
        vim
      ];
    }
    """
    )
    return nix_config


# ============= AI & Learning Mocks =============


@pytest.fixture
def mock_hrm_reasoner():
    """Mock HRM reasoner"""
    reasoner = Mock()
    reasoner.reason.return_value = Mock(
        intent="INSTALL", confidence=0.95, solution="nix-env -iA nixos.firefox"
    )
    return reasoner


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client"""
    client = Mock()
    client.generate.return_value = Mock(
        response="Here's how to install Firefox...", model="llama2"
    )
    return client
