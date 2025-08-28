#!/usr/bin/env python3
"""
🔇 Logging Configuration for Invisible Consciousness
Keep the system quiet unless explicitly asked to speak
"""

import logging
import os


def configure_logging():
    """Configure logging to be quiet by default"""
    
    # Get debug flag
    debug = os.environ.get('NIX_HUMANITY_DEBUG', '').lower() == 'true'
    
    # Set base logging level
    if debug:
        level = logging.DEBUG
    else:
        level = logging.ERROR  # Only show errors in normal mode
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if debug else '%(message)s'
    )
    
    # Silence specific noisy loggers unless in debug
    if not debug:
        # Silence backend warnings about missing databases
        logging.getLogger('luminous_nix.nix.native_backend').setLevel(logging.ERROR)
        logging.getLogger('src.luminous_nix.persistence.trinity_store').setLevel(logging.ERROR)
        logging.getLogger('luminous_nix.nix.improved_cache').setLevel(logging.ERROR)
        logging.getLogger('luminous_nix.persistence.trinity_store').setLevel(logging.ERROR)
        
        # Silence Seven Spirals initialization
        logging.getLogger('sovereignty_auditor').setLevel(logging.ERROR)
        logging.getLogger('dialogue_facilitator').setLevel(logging.ERROR)
        logging.getLogger('intention_engine').setLevel(logging.ERROR)
        logging.getLogger('co_creator_console').setLevel(logging.ERROR)
        logging.getLogger('noospheric_weaver').setLevel(logging.ERROR)
        logging.getLogger('sangha_mirror').setLevel(logging.ERROR)


# Auto-configure when imported
configure_logging()