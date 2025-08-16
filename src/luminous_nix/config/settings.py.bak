"""Configuration management for Nix for Humanity."""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Environment(Enum):
    """Application environment."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    
    url: str = "sqlite:///nixos_knowledge.db"
    echo: bool = False
    pool_size: int = 5
    pool_recycle: int = 3600
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create config from environment variables."""
        return cls(
            url=os.getenv("DATABASE_URL", cls.url),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
            pool_recycle=int(os.getenv("DATABASE_POOL_RECYCLE", "3600")),
        )


@dataclass
class RedisConfig:
    """Redis cache configuration."""
    
    url: str = "redis://localhost:6379/0"
    enabled: bool = True
    ttl_default: int = 3600
    ttl_packages: int = 86400
    ttl_commands: int = 3600
    max_connections: int = 50
    
    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Create config from environment variables."""
        return cls(
            url=os.getenv("REDIS_URL", cls.url),
            enabled=os.getenv("REDIS_ENABLED", "true").lower() == "true",
            ttl_default=int(os.getenv("REDIS_TTL_DEFAULT", "3600")),
            ttl_packages=int(os.getenv("REDIS_TTL_PACKAGES", "86400")),
            ttl_commands=int(os.getenv("REDIS_TTL_COMMANDS", "3600")),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
        )


@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    level: str = "INFO"
    format: str = "console"  # console or json
    file: Optional[Path] = None
    colorize: bool = True
    structured: bool = True
    
    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Create config from environment variables."""
        log_file = os.getenv("LOG_FILE")
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format=os.getenv("LOG_FORMAT", "console"),
            file=Path(log_file) if log_file else None,
            colorize=os.getenv("NO_COLOR") is None,
            structured=os.getenv("STRUCTURED_LOGS", "true").lower() == "true",
        )


@dataclass
class SecurityConfig:
    """Security configuration."""
    
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    allowed_hosts: List[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    
    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create config from environment variables."""
        return cls(
            secret_key=os.getenv("SECRET_KEY", cls.secret_key),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", cls.jwt_algorithm),
            jwt_expiry_hours=int(os.getenv("JWT_EXPIRY_HOURS", "24")),
            rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
            allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(","),
            cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        )


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    
    enabled: bool = True
    metrics_enabled: bool = True
    tracing_enabled: bool = False
    prometheus_port: int = 9090
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831
    service_name: str = "nix-for-humanity"
    
    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        """Create config from environment variables."""
        return cls(
            enabled=os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
            tracing_enabled=os.getenv("TRACING_ENABLED", "false").lower() == "true",
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", "9090")),
            jaeger_host=os.getenv("JAEGER_HOST", "localhost"),
            jaeger_port=int(os.getenv("JAEGER_PORT", "6831")),
            service_name=os.getenv("SERVICE_NAME", "nix-for-humanity"),
        )


@dataclass
class NixConfig:
    """NixOS-specific configuration."""
    
    python_backend: bool = True
    nixos_config_path: Path = Path("/etc/nixos/configuration.nix")
    nix_store_path: Path = Path("/nix/store")
    home_manager_enabled: bool = True
    flakes_enabled: bool = True
    max_generations: int = 10
    
    @classmethod
    def from_env(cls) -> "NixConfig":
        """Create config from environment variables."""
        return cls(
            python_backend=os.getenv("NIX_HUMANITY_PYTHON_BACKEND", "true").lower() == "true",
            nixos_config_path=Path(os.getenv("NIXOS_CONFIG_PATH", "/etc/nixos/configuration.nix")),
            nix_store_path=Path(os.getenv("NIX_STORE_PATH", "/nix/store")),
            home_manager_enabled=os.getenv("HOME_MANAGER_ENABLED", "true").lower() == "true",
            flakes_enabled=os.getenv("FLAKES_ENABLED", "true").lower() == "true",
            max_generations=int(os.getenv("MAX_GENERATIONS", "10")),
        )


@dataclass
class WebConfig:
    """Web server configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 4
    websocket_enabled: bool = True
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    @classmethod
    def from_env(cls) -> "WebConfig":
        """Create config from environment variables."""
        return cls(
            host=os.getenv("WEB_HOST", "0.0.0.0"),
            port=int(os.getenv("WEB_PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            workers=int(os.getenv("WEB_WORKERS", "4")),
            websocket_enabled=os.getenv("WEBSOCKET_ENABLED", "true").lower() == "true",
            websocket_ping_interval=int(os.getenv("WEBSOCKET_PING_INTERVAL", "30")),
            websocket_ping_timeout=int(os.getenv("WEBSOCKET_PING_TIMEOUT", "10")),
        )


@dataclass
class Config:
    """Main application configuration."""
    
    environment: Environment
    app_name: str = "Nix for Humanity"
    version: str = "1.2.0"
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig.from_env)
    redis: RedisConfig = field(default_factory=RedisConfig.from_env)
    logging: LoggingConfig = field(default_factory=LoggingConfig.from_env)
    security: SecurityConfig = field(default_factory=SecurityConfig.from_env)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig.from_env)
    nix: NixConfig = field(default_factory=NixConfig.from_env)
    web: WebConfig = field(default_factory=WebConfig.from_env)
    
    # Paths
    data_dir: Path = Path.home() / ".local" / "share" / "nix-humanity"
    cache_dir: Path = Path.home() / ".cache" / "nix-humanity"
    config_dir: Path = Path.home() / ".config" / "nix-humanity"
    
    def __post_init__(self) -> None:
        """Post-initialization setup."""
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        environment = Environment(env_str)
        
        return cls(
            environment=environment,
            app_name=os.getenv("APP_NAME", "Nix for Humanity"),
            version=os.getenv("APP_VERSION", "1.2.0"),
        )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.environment == Environment.TESTING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "environment": self.environment.value,
            "app_name": self.app_name,
            "version": self.version,
            "database": {
                "url": self.database.url,
                "pool_size": self.database.pool_size,
            },
            "redis": {
                "url": self.redis.url,
                "enabled": self.redis.enabled,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
            },
            "monitoring": {
                "enabled": self.monitoring.enabled,
                "service_name": self.monitoring.service_name,
            },
            "nix": {
                "python_backend": self.nix.python_backend,
                "flakes_enabled": self.nix.flakes_enabled,
            },
            "web": {
                "host": self.web.host,
                "port": self.web.port,
                "debug": self.web.debug,
            },
        }


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global config instance.
    
    Returns:
        Application configuration
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reset_config() -> None:
    """Reset the global config instance (useful for testing)."""
    global _config
    _config = None