"""
Self-Healing Intelligence Module

Revolutionary capability: Automatically detect and fix system issues
so users never see errors - just solutions that work.

This is the foundation of truly intelligent AI assistance.
"""

import subprocess
import time
import os
from typing import Optional, Tuple
from enum import Enum
from rich.console import Console

console = Console()


class ServiceStatus(Enum):
    """Service status states"""
    RUNNING = "running"
    STOPPED = "stopped"
    NOT_INSTALLED = "not_installed"
    UNKNOWN = "unknown"


class SelfHealingAgent:
    """
    Automatically detects and fixes common system issues.

    Philosophy: Users shouldn't see errors - the system should
    just fix problems invisibly and keep working.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize self-healing agent.

        Args:
            verbose: Show healing actions to user (default: invisible)
        """
        self.verbose = verbose
        self.healing_history = []

    def ensure_ollama_running(self) -> Tuple[bool, Optional[str]]:
        """
        Ensure Ollama is running, starting it automatically if needed.

        This is the core of self-healing: detect issue, fix invisibly.

        Returns:
            (success: bool, message: Optional[str])
            - (True, None) if running or successfully started
            - (False, error_msg) if couldn't fix
        """
        # Check current status
        status = self._check_ollama_status()

        if status == ServiceStatus.RUNNING:
            return (True, None)  # Already running, all good!

        if status == ServiceStatus.NOT_INSTALLED:
            return (False, "Ollama is not installed. Would you like me to help install it?")

        # Status is STOPPED - try to start it
        if self.verbose:
            console.print("[dim]🔧 Starting Ollama for you...[/dim]")

        success = self._start_ollama()

        if success:
            self.healing_history.append({
                'issue': 'ollama_not_running',
                'action': 'started_ollama',
                'success': True
            })

            if self.verbose:
                console.print("[dim]✅ Ollama started successfully[/dim]")

            return (True, None)
        else:
            return (False, "Could not start Ollama automatically. Please start it manually: systemctl start ollama")

    def _check_ollama_status(self) -> ServiceStatus:
        """
        Check if Ollama is running.

        Returns:
            ServiceStatus indicating current state
        """
        try:
            # Method 1: Check if ollama responds to HTTP
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/tags'],
                capture_output=True,
                timeout=2
            )

            if result.returncode == 0:
                return ServiceStatus.RUNNING

            # Method 2: Check systemd service status
            result = subprocess.run(
                ['systemctl', 'is-active', 'ollama'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if 'active' in result.stdout:
                return ServiceStatus.RUNNING
            elif 'inactive' in result.stdout:
                return ServiceStatus.STOPPED

            # Method 3: Check if ollama command exists
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True,
                timeout=1
            )

            if result.returncode == 0:
                return ServiceStatus.STOPPED  # Installed but not running
            else:
                return ServiceStatus.NOT_INSTALLED

        except subprocess.TimeoutExpired:
            return ServiceStatus.UNKNOWN
        except Exception:
            return ServiceStatus.UNKNOWN

    def _start_ollama(self) -> bool:
        """
        Attempt to start Ollama service.

        Tries multiple methods in order:
        1. systemctl start (NixOS/systemd)
        2. ollama serve in background
        3. User systemd service

        Returns:
            True if successfully started, False otherwise
        """
        # Method 1: Try systemctl (most reliable on NixOS)
        try:
            result = subprocess.run(
                ['systemctl', 'start', 'ollama'],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                # Wait a moment for service to start
                time.sleep(2)

                # Verify it's running
                if self._check_ollama_status() == ServiceStatus.RUNNING:
                    return True

        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

        # Method 2: Try starting as background process
        try:
            # Start ollama serve in background
            subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Wait for it to start
            time.sleep(3)

            # Verify it's running
            if self._check_ollama_status() == ServiceStatus.RUNNING:
                return True

        except Exception:
            pass

        # Method 3: Try user systemd service
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'start', 'ollama'],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                time.sleep(2)

                if self._check_ollama_status() == ServiceStatus.RUNNING:
                    return True

        except Exception:
            pass

        # All methods failed
        return False

    def auto_heal_before_query(self, query: str, needs_ollama: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Automatically heal system issues before processing a query.

        This is the main entry point for self-healing.
        Call this BEFORE attempting to process any query that needs AI.

        Args:
            query: User's query (for context)
            needs_ollama: Whether this query needs Ollama

        Returns:
            (ready: bool, error_msg: Optional[str])
        """
        if not needs_ollama:
            return (True, None)

        # Ensure Ollama is running
        success, error = self.ensure_ollama_running()

        return (success, error)

    def get_healing_stats(self) -> dict:
        """
        Get statistics about self-healing actions.

        Returns:
            Dictionary with healing stats
        """
        total_heals = len(self.healing_history)
        successful_heals = sum(1 for h in self.healing_history if h['success'])

        return {
            'total_healing_actions': total_heals,
            'successful_heals': successful_heals,
            'success_rate': successful_heals / total_heals if total_heals > 0 else 0,
            'issues_fixed': [h['issue'] for h in self.healing_history if h['success']]
        }


def get_self_healing_agent(verbose: bool = False) -> SelfHealingAgent:
    """
    Get singleton instance of self-healing agent.

    Args:
        verbose: Show healing actions to user

    Returns:
        SelfHealingAgent instance
    """
    global _self_healing_agent

    if _self_healing_agent is None:
        _self_healing_agent = SelfHealingAgent(verbose=verbose)

    return _self_healing_agent


# Singleton instance
_self_healing_agent: Optional[SelfHealingAgent] = None
