"""
Logging utilities for Luminous Nix.
"""

import logging
import sys
from typing import Optional

# Configure default logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (defaults to 'luminous_nix')
    
    Returns:
        Logger instance
    """
    if name is None:
        name = 'luminous_nix'
    return logging.getLogger(name)

# Default logger instance
logger = get_logger()