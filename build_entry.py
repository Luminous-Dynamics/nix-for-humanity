#!/usr/bin/env python3
"""Entry point for standalone executable"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run main CLI
from luminous_nix.cli import main

if __name__ == "__main__":
    sys.exit(main())
