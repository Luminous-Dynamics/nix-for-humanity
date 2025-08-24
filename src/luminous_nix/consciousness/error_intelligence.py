#!/usr/bin/env python3
"""
🧠 Error Intelligence - Learning from mistakes
Wrapper/alias for error_dojo for backward compatibility
"""

# Import everything from error_dojo
from .error_dojo import *

# Create alias for main class if needed
try:
    from .error_dojo import ErrorDojo
    ErrorIntelligence = ErrorDojo
except ImportError:
    pass

# Global instance
_ERROR_INTELLIGENCE = None

def get_error_intelligence():
    """Get or create error intelligence instance"""
    global _ERROR_INTELLIGENCE
    if _ERROR_INTELLIGENCE is None:
        try:
            from .error_dojo import get_error_dojo
            _ERROR_INTELLIGENCE = get_error_dojo()
        except ImportError:
            # Fallback to creating a simple instance
            _ERROR_INTELLIGENCE = ErrorIntelligence() if 'ErrorIntelligence' in globals() else None
    return _ERROR_INTELLIGENCE