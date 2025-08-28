"""AI and NLP components for Nix for Humanity."""

# Try to import NLP components
try:
    from .nlp import (
        NLPPipeline,
        process,
        extract_package_name,
        record_interaction_feedback,
        get_explanation_for_user
    )
    # Alias for backward compatibility
    NLPEngine = NLPPipeline
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    NLPEngine = None
    NLPPipeline = None

# Import Ollama integration
try:
    from .ollama_client import OllamaClient, SocraticOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OllamaClient = None
    SocraticOllama = None

__all__ = [
    'OllamaClient',
    'SocraticOllama',
    'NLPEngine',
    'NLPPipeline',
    'process',
    'extract_package_name',
    'record_interaction_feedback',
    'get_explanation_for_user'
]
