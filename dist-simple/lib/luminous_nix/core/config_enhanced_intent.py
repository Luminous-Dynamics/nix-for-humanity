"""Configuration for Enhanced Intent Recognition

This module manages the settings for hybrid pattern-LLM intent recognition.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class IntentRecognitionConfig:
    """Configuration for intent recognition system."""
    
    # Mode selection
    mode: str = "balanced"  # "fast", "balanced", "accurate"
    
    # LLM settings
    enable_llm: bool = True
    llm_timeout_ms: int = 2000
    llm_confidence_threshold: float = 0.7
    
    # Pattern settings  
    pattern_confidence_threshold: float = 0.85
    
    # Learning settings
    enable_learning: bool = True
    save_corrections: bool = True
    corrections_file: str = "~/.local/share/luminous-nix/intent_corrections.json"
    
    # Performance settings
    cache_enabled: bool = True
    cache_size: int = 1000
    
    # Debug settings
    explain_recognition: bool = False
    log_metrics: bool = False
    
    @classmethod
    def from_env(cls) -> "IntentRecognitionConfig":
        """Create config from environment variables."""
        config = cls()
        
        # Check environment variables
        if os.environ.get("LUMINOUS_INTENT_MODE"):
            config.mode = os.environ["LUMINOUS_INTENT_MODE"]
            
        if os.environ.get("LUMINOUS_NO_LLM", "").lower() == "true":
            config.enable_llm = False
            
        if os.environ.get("LUMINOUS_INTENT_EXPLAIN", "").lower() == "true":
            config.explain_recognition = True
            
        if os.environ.get("LUMINOUS_INTENT_FAST", "").lower() == "true":
            config.mode = "fast"
            config.enable_llm = False
            
        if os.environ.get("LUMINOUS_INTENT_ACCURATE", "").lower() == "true":
            config.mode = "accurate"
            config.enable_llm = True
            
        return config
        
    def to_pipeline_kwargs(self) -> dict:
        """Convert to kwargs for pipeline initialization."""
        return {
            'prefer_llm': self.mode == "accurate",
            'enable_learning': self.enable_learning,
            'explain': self.explain_recognition,
        }