#!/usr/bin/env python3
"""Entry point for standalone executable."""
import sys
import os

# Ensure we can find our modules
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_dir = sys._MEIPASS
else:
    # Running as script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Import and run CLI
from luminous_nix.cli import main

if __name__ == '__main__':
    main()
