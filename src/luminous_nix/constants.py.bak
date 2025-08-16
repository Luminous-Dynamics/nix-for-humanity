"""
Central Constants for Nix for Humanity.

Defines all magic numbers, thresholds, and configuration constants
used throughout the codebase. Centralizing these values improves
maintainability and makes the codebase more self-documenting.

Usage Example:
    >>> from nix_for_humanity.constants import MAX_WORKERS_DEFAULT
    >>> executor = AsyncCommandExecutor(max_workers=MAX_WORKERS_DEFAULT)

Since: v1.0.0
"""

# ============================================================================
# Concurrency and Threading
# ============================================================================

MAX_WORKERS_DEFAULT = 4
"""Default number of worker threads for async operations."""

MAX_CONCURRENT_OPERATIONS = 10
"""Maximum concurrent operations in parallel execution."""

THREAD_POOL_SIZE = 5
"""Default thread pool size for background tasks."""

# ============================================================================
# Timeouts (in seconds)
# ============================================================================

DEFAULT_TIMEOUT = 30.0
"""Default timeout for operations in seconds."""

COMMAND_TIMEOUT = 120
"""Timeout for long-running commands like nixos-rebuild."""

CACHE_OPERATION_TIMEOUT = 5.0
"""Timeout for cache operations."""

NETWORK_TIMEOUT = 60.0
"""Timeout for network operations."""

# ============================================================================
# Cache Configuration
# ============================================================================

CACHE_TTL_SECONDS = 300
"""Default cache time-to-live in seconds (5 minutes)."""

# ============================================================================
# Nix Store Paths
# ============================================================================

NIX_STORE_PATH = "/nix/store"
"""Path to the Nix store directory."""

NIX_DB_PATH = "/nix/var/nix/db/db.sqlite"
"""Path to the Nix database."""

NIX_PROFILES_PATH = "/nix/var/nix/profiles"
"""Path to Nix profiles directory."""

CACHE_MAX_SIZE = 1000
"""Maximum number of entries in memory cache."""

CACHE_MAX_AGE_DAYS = 7
"""Maximum age for persistent cache in days."""

CACHE_CLEANUP_INTERVAL = 3600
"""Cache cleanup interval in seconds (1 hour)."""

# ============================================================================
# Search and Discovery
# ============================================================================

SEARCH_RESULTS_DEFAULT = 20
"""Default number of search results to return."""

SEARCH_RESULTS_MAX = 100
"""Maximum number of search results allowed."""

FUZZY_MATCH_THRESHOLD = 0.8
"""Minimum similarity score for fuzzy matching (0-1)."""

# ============================================================================
# Learning and Patterns
# ============================================================================

MIN_PATTERN_OCCURRENCES = 3
"""Minimum occurrences before considering something a pattern."""

LEARNING_CONFIDENCE_THRESHOLD = 0.7
"""Minimum confidence for learning system decisions."""

HISTORY_MAX_ENTRIES = 1000
"""Maximum number of history entries to keep."""

PATTERN_DECAY_DAYS = 30
"""Days before patterns start losing weight."""

# ============================================================================
# UI and Display
# ============================================================================

PROGRESS_UPDATE_INTERVAL = 0.1
"""Progress bar update interval in seconds."""

TERMINAL_WIDTH_DEFAULT = 80
"""Default terminal width for formatting."""

MAX_ERROR_MESSAGE_LENGTH = 500
"""Maximum length of error messages to display."""

MAX_SUGGESTION_COUNT = 5
"""Maximum number of suggestions to show."""

# ============================================================================
# Performance and Optimization
# ============================================================================

BATCH_SIZE_DEFAULT = 10
"""Default batch size for bulk operations."""

BATCH_SIZE_MAX = 50
"""Maximum batch size for bulk operations."""

BENCHMARK_ITERATIONS_DEFAULT = 10
"""Default iterations for benchmarking."""

BENCHMARK_WARMUP_ITERATIONS = 2
"""Warmup iterations before benchmarking."""

# ============================================================================
# Retry and Error Handling
# ============================================================================

MAX_RETRY_ATTEMPTS = 3
"""Maximum number of retry attempts for failed operations."""

RETRY_DELAY_BASE = 1.0
"""Base delay between retries in seconds."""

RETRY_DELAY_MAX = 30.0
"""Maximum delay between retries in seconds."""

RETRY_BACKOFF_FACTOR = 2.0
"""Exponential backoff factor for retries."""

# ============================================================================
# File System
# ============================================================================

MAX_FILE_SIZE_MB = 100
"""Maximum file size to process in megabytes."""

MAX_LOG_FILE_SIZE_MB = 50
"""Maximum log file size before rotation in megabytes."""

LOG_BACKUP_COUNT = 5
"""Number of log file backups to keep."""

# ============================================================================
# Natural Language Processing
# ============================================================================

INTENT_CONFIDENCE_THRESHOLD = 0.6
"""Minimum confidence for intent recognition."""

ENTITY_CONFIDENCE_THRESHOLD = 0.5
"""Minimum confidence for entity extraction."""

MAX_QUERY_LENGTH = 500
"""Maximum length of natural language query."""

MIN_QUERY_LENGTH = 2
"""Minimum length of natural language query."""

# ============================================================================
# Security
# ============================================================================

MAX_COMMAND_LENGTH = 1000
"""Maximum length of command to execute."""

MAX_PATH_LENGTH = 4096
"""Maximum file path length."""

SESSION_TIMEOUT_MINUTES = 30
"""Session timeout in minutes."""

MAX_LOGIN_ATTEMPTS = 5
"""Maximum login attempts before lockout."""

# ============================================================================
# Version and Compatibility
# ============================================================================

MIN_PYTHON_VERSION = (3, 8)
"""Minimum Python version required."""

API_VERSION = "v1"
"""Current API version."""

SCHEMA_VERSION = 1
"""Current configuration schema version."""

# ============================================================================
# Defaults
# ============================================================================

DEFAULT_SHELL = "/bin/bash"
"""Default shell for command execution."""

DEFAULT_ENCODING = "utf-8"
"""Default text encoding."""

DEFAULT_LOG_LEVEL = "WARNING"
"""Default logging level."""

DEFAULT_DRY_RUN = True
"""Default dry-run mode for safety."""
