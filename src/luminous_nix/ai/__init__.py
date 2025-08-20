"""AI and NLP components for Nix for Humanity."""

from .nlp import (
    NLPPipeline,
    process,
    extract_package_name,
    record_interaction_feedback,
    get_explanation_for_user
)

# Alias for backward compatibility
NLPEngine = NLPPipeline

__all__ = [
    'NLPEngine',
    'NLPPipeline',
    'process',
    'extract_package_name',
    'record_interaction_feedback',
    'get_explanation_for_user'
]
