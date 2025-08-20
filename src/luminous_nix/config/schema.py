"""
from typing import Dict, List, Optional
Configuration Schema Definitions

Defines the complete configuration schema for Nix for Humanity
with type safety and validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import os


class Personality(str, Enum):
    """Available personality styles"""
    MINIMAL = "minimal"
    FRIENDLY = "friendly"
    ENCOURAGING = "encouraging"
    TECHNICAL = "technical"
    ACCESSIBLE = "accessible"


class ResponseFormat(str, Enum):
    """Response formatting options"""
    PLAIN = "plain"
    STRUCTURED = "structured"
    JSON = "json"
    YAML = "yaml"


class NLPEngine(str, Enum):
    """NLP engine types"""
    RULE_BASED = "rule-based"
    STATISTICAL = "statistical"
    NEURAL = "neural"
    HYBRID = "hybrid"


class DataCollection(str, Enum):
    """Data collection levels"""
    NONE = "none"
    MINIMAL = "minimal"
    STANDARD = "standard"
    FULL = "full"


class PrivacyMode(str, Enum):
    """Privacy modes for learning"""
    STRICT = "strict"
    BALANCED = "balanced"
    OPEN = "open"


@dataclass
class CoreConfig:
    """Core system configuration"""
    version: str = "0.8.3"
    backend: str = "python"  # python, nodejs, hybrid
    data_directory: str = "~/.local/share/nix-for-humanity"
    cache_directory: str = "~/.cache/nix-for-humanity"
    log_level: str = "info"  # debug, info, warn, error
    
    def __post_init__(self):
        """Expand paths"""
        self.data_directory = os.path.expanduser(self.data_directory)
        self.cache_directory = os.path.expanduser(self.cache_directory)


@dataclass
class UIConfig:
    """User interface configuration"""
    default_personality: Personality = Personality.FRIENDLY
    response_format: ResponseFormat = ResponseFormat.STRUCTURED
    show_commands: bool = True
    confirm_actions: bool = True
    use_colors: bool = True
    progress_indicators: bool = True
    theme: str = "default"  # default, dark, light, high-contrast
    
    # Custom messages
    greeting: Optional[str] = None
    farewell: Optional[str] = None
    error_prefix: str = "Oops!"
    success_prefix: str = "Great!"


@dataclass
class NLPConfig:
    """Natural language processing configuration"""
    engine: NLPEngine = NLPEngine.HYBRID
    confidence_threshold: float = 0.7
    typo_correction: bool = True
    context_memory: int = 10
    learning_enabled: bool = True
    
    # Advanced NLP settings
    fuzzy_match_threshold: float = 0.8
    synonym_expansion: bool = True
    intent_patterns_file: Optional[str] = None
    custom_vocabulary: List[str] = field(default_factory=list)


@dataclass
class PerformanceConfig:
    """Performance tuning configuration"""
    fast_mode: bool = False
    cache_responses: bool = True
    parallel_processing: bool = True
    memory_limit: str = "512MB"
    timeout: int = 30
    
    # Advanced performance settings
    worker_threads: int = 4
    cache_size: int = 1000
    batch_size: int = 10
    prefetch_common: bool = True


@dataclass
class PrivacyConfig:
    """Privacy and security configuration"""
    data_collection: DataCollection = DataCollection.MINIMAL
    share_anonymous_stats: bool = False
    local_only: bool = True
    encrypt_data: bool = True
    auto_cleanup: bool = True
    
    # Data retention
    log_retention_days: int = 30
    cache_retention_days: int = 7
    learning_retention_days: int = 365
    
    # Security
    allowed_commands: List[str] = field(default_factory=lambda: [
        "nix-env", "nixos-rebuild", "nix-channel", "nix", "home-manager"
    ])
    forbidden_patterns: List[str] = field(default_factory=lambda: [
        "rm -rf /", "dd if=", "mkfs", "> /dev/"
    ])


@dataclass
class LearningConfig:
    """Learning system configuration"""
    enabled: bool = True
    personal_preferences: bool = True
    command_patterns: bool = True
    error_recovery: bool = True
    privacy_mode: PrivacyMode = PrivacyMode.STRICT
    retention_days: int = 365
    
    # Learning parameters
    min_confidence: float = 0.6
    feedback_weight: float = 0.3
    success_boost: float = 0.1
    failure_penalty: float = 0.05


@dataclass
class AccessibilityConfig:
    """Accessibility configuration"""
    screen_reader: bool = False
    high_contrast: bool = False
    large_text: bool = False
    reduce_motion: bool = False
    keyboard_only: bool = False
    simple_language: bool = False
    
    # Additional accessibility
    consistent_terminology: bool = True
    structured_output: bool = False
    extra_confirmations: bool = False
    patient_mode: bool = False


@dataclass
class VoiceConfig:
    """Voice interface configuration"""
    enabled: bool = False
    wake_word: str = "hey nix"
    language: str = "en-US"
    voice_feedback: bool = True
    noise_reduction: bool = True
    
    # Voice parameters
    silence_threshold: float = 0.1
    speech_timeout: int = 5
    voice_model: str = "whisper-small"
    tts_voice: str = "default"
    speed: float = 1.0


@dataclass
class DevelopmentConfig:
    """Development and debugging configuration"""
    debug_mode: bool = False
    test_mode: bool = False
    api_logging: bool = False
    performance_profiling: bool = False
    mock_execution: bool = False
    
    # Development features
    show_internal_errors: bool = False
    save_all_interactions: bool = False
    benchmark_mode: bool = False
    experimental_features: bool = False


@dataclass
class IntegrationConfig:
    """External integration configuration"""
    shell_integration: bool = True
    editor_integration: Dict[str, bool] = field(default_factory=lambda: {
        "vscode": False,
        "vim": False,
        "emacs": False,
    })
    
    # API settings
    api_enabled: bool = False
    api_port: int = 8765
    api_host: str = "localhost"
    api_key: Optional[str] = None


@dataclass
class CustomAliases:
    """Custom command aliases"""
    aliases: Dict[str, str] = field(default_factory=lambda: {
        "up": "update system",
        "i": "install",
        "s": "search",
        "r": "remove",
    })
    
    shortcuts: Dict[str, List[str]] = field(default_factory=lambda: {
        "dev-setup": ["install git vim tmux", "install docker", "install vscode"],
        "clean": ["collect garbage", "optimize store"],
    })


@dataclass
class ConfigSchema:
    """Complete configuration schema for Nix for Humanity"""
    
    # Core sections
    core: CoreConfig = field(default_factory=CoreConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    accessibility: AccessibilityConfig = field(default_factory=AccessibilityConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    development: DevelopmentConfig = field(default_factory=DevelopmentConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    aliases: CustomAliases = field(default_factory=CustomAliases)
    
    # Metadata
    profile_name: Optional[str] = None
    last_modified: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Validate core settings
        if self.core.log_level not in ["debug", "info", "warn", "error"]:
            errors.append(f"Invalid log_level: {self.core.log_level}")
            
        # Validate performance settings
        if self.performance.timeout < 1:
            errors.append(f"Timeout must be at least 1 second")
            
        if self.performance.worker_threads < 1:
            errors.append(f"Worker threads must be at least 1")
            
        # Validate NLP settings
        if not 0 <= self.nlp.confidence_threshold <= 1:
            errors.append("Confidence threshold must be between 0 and 1")
            
        # Validate privacy settings
        if self.privacy.log_retention_days < 0:
            errors.append("Log retention days must be non-negative")
            
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "core": {
                "version": self.core.version,
                "backend": self.core.backend,
                "data_directory": self.core.data_directory,
                "cache_directory": self.core.cache_directory,
                "log_level": self.core.log_level,
            },
            "ui": {
                "default_personality": self.ui.default_personality.value,
                "response_format": self.ui.response_format.value,
                "show_commands": self.ui.show_commands,
                "confirm_actions": self.ui.confirm_actions,
                "use_colors": self.ui.use_colors,
                "progress_indicators": self.ui.progress_indicators,
                "theme": self.ui.theme,
                "greeting": self.ui.greeting,
                "farewell": self.ui.farewell,
                "error_prefix": self.ui.error_prefix,
                "success_prefix": self.ui.success_prefix,
            },
            "nlp": {
                "engine": self.nlp.engine.value,
                "confidence_threshold": self.nlp.confidence_threshold,
                "typo_correction": self.nlp.typo_correction,
                "context_memory": self.nlp.context_memory,
                "learning_enabled": self.nlp.learning_enabled,
                "fuzzy_match_threshold": self.nlp.fuzzy_match_threshold,
                "synonym_expansion": self.nlp.synonym_expansion,
                "intent_patterns_file": self.nlp.intent_patterns_file,
                "custom_vocabulary": self.nlp.custom_vocabulary,
            },
            "performance": {
                "fast_mode": self.performance.fast_mode,
                "cache_responses": self.performance.cache_responses,
                "parallel_processing": self.performance.parallel_processing,
                "memory_limit": self.performance.memory_limit,
                "timeout": self.performance.timeout,
                "worker_threads": self.performance.worker_threads,
                "cache_size": self.performance.cache_size,
                "batch_size": self.performance.batch_size,
                "prefetch_common": self.performance.prefetch_common,
            },
            "privacy": {
                "data_collection": self.privacy.data_collection.value,
                "share_anonymous_stats": self.privacy.share_anonymous_stats,
                "local_only": self.privacy.local_only,
                "encrypt_data": self.privacy.encrypt_data,
                "auto_cleanup": self.privacy.auto_cleanup,
                "log_retention_days": self.privacy.log_retention_days,
                "cache_retention_days": self.privacy.cache_retention_days,
                "learning_retention_days": self.privacy.learning_retention_days,
                "allowed_commands": self.privacy.allowed_commands,
                "forbidden_patterns": self.privacy.forbidden_patterns,
            },
            "learning": {
                "enabled": self.learning.enabled,
                "personal_preferences": self.learning.personal_preferences,
                "command_patterns": self.learning.command_patterns,
                "error_recovery": self.learning.error_recovery,
                "privacy_mode": self.learning.privacy_mode.value,
                "retention_days": self.learning.retention_days,
                "min_confidence": self.learning.min_confidence,
                "feedback_weight": self.learning.feedback_weight,
                "success_boost": self.learning.success_boost,
                "failure_penalty": self.learning.failure_penalty,
            },
            "accessibility": {
                "screen_reader": self.accessibility.screen_reader,
                "high_contrast": self.accessibility.high_contrast,
                "large_text": self.accessibility.large_text,
                "reduce_motion": self.accessibility.reduce_motion,
                "keyboard_only": self.accessibility.keyboard_only,
                "simple_language": self.accessibility.simple_language,
                "consistent_terminology": self.accessibility.consistent_terminology,
                "structured_output": self.accessibility.structured_output,
                "extra_confirmations": self.accessibility.extra_confirmations,
                "patient_mode": self.accessibility.patient_mode,
            },
            "voice": {
                "enabled": self.voice.enabled,
                "wake_word": self.voice.wake_word,
                "language": self.voice.language,
                "voice_feedback": self.voice.voice_feedback,
                "noise_reduction": self.voice.noise_reduction,
                "silence_threshold": self.voice.silence_threshold,
                "speech_timeout": self.voice.speech_timeout,
                "voice_model": self.voice.voice_model,
                "tts_voice": self.voice.tts_voice,
                "speed": self.voice.speed,
            },
            "development": {
                "debug_mode": self.development.debug_mode,
                "test_mode": self.development.test_mode,
                "api_logging": self.development.api_logging,
                "performance_profiling": self.development.performance_profiling,
                "mock_execution": self.development.mock_execution,
                "show_internal_errors": self.development.show_internal_errors,
                "save_all_interactions": self.development.save_all_interactions,
                "benchmark_mode": self.development.benchmark_mode,
                "experimental_features": self.development.experimental_features,
            },
            "integration": {
                "shell_integration": self.integration.shell_integration,
                "editor_integration": self.integration.editor_integration,
                "api_enabled": self.integration.api_enabled,
                "api_port": self.integration.api_port,
                "api_host": self.integration.api_host,
                "api_key": self.integration.api_key,
            },
            "aliases": {
                "aliases": self.aliases.aliases,
                "shortcuts": self.aliases.shortcuts,
            },
            "profile_name": self.profile_name,
            "last_modified": self.last_modified,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigSchema":
        """Create configuration from dictionary"""
        config = cls()
        
        # Load core config
        if "core" in data:
            config.core = CoreConfig(**data["core"])
            
        # Load UI config
        if "ui" in data:
            ui_data = data["ui"].copy()
            if "default_personality" in ui_data:
                ui_data["default_personality"] = Personality(ui_data["default_personality"])
            if "response_format" in ui_data:
                ui_data["response_format"] = ResponseFormat(ui_data["response_format"])
            config.ui = UIConfig(**ui_data)
            
        # Load NLP config
        if "nlp" in data:
            nlp_data = data["nlp"].copy()
            if "engine" in nlp_data:
                nlp_data["engine"] = NLPEngine(nlp_data["engine"])
            config.nlp = NLPConfig(**nlp_data)
            
        # Load other configs similarly...
        if "performance" in data:
            config.performance = PerformanceConfig(**data["performance"])
            
        if "privacy" in data:
            privacy_data = data["privacy"].copy()
            if "data_collection" in privacy_data:
                privacy_data["data_collection"] = DataCollection(privacy_data["data_collection"])
            config.privacy = PrivacyConfig(**privacy_data)
            
        if "learning" in data:
            learning_data = data["learning"].copy()
            if "privacy_mode" in learning_data:
                learning_data["privacy_mode"] = PrivacyMode(learning_data["privacy_mode"])
            config.learning = LearningConfig(**learning_data)
            
        if "accessibility" in data:
            config.accessibility = AccessibilityConfig(**data["accessibility"])
            
        if "voice" in data:
            config.voice = VoiceConfig(**data["voice"])
            
        if "development" in data:
            config.development = DevelopmentConfig(**data["development"])
            
        if "integration" in data:
            config.integration = IntegrationConfig(**data["integration"])
            
        if "aliases" in data:
            config.aliases = CustomAliases(**data["aliases"])
            
        # Load metadata
        config.profile_name = data.get("profile_name")
        config.last_modified = data.get("last_modified")
        
        return config