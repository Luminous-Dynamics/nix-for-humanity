#!/usr/bin/env python3
"""
Standalone test runner for NixOSIntegration tests
Avoids import issues by running tests directly
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
project_root = Path(__file__).parent.absolute()
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

# Now run the tests
if __name__ == "__main__":
    # Import and run the test file directly
    exec(open(project_root / "tests" / "unit" / "test_nix_integration.py").read())