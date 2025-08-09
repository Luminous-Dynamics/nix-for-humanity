"""
Wrapper module to import from the hyphenated filename
This allows ask-nix-hybrid to import nix_knowledge_engine properly
"""

import importlib.util
import sys
from pathlib import Path

# Get the path to the hyphenated file
module_path = Path(__file__).parent / "nix-knowledge-engine.py"

# Load the module from the hyphenated filename
spec = importlib.util.spec_from_file_location("nix_knowledge_engine_impl", module_path)
module = importlib.util.module_from_spec(spec)
sys.modules["nix_knowledge_engine_impl"] = module
spec.loader.exec_module(module)

# Export everything from the original module
from nix_knowledge_engine_impl import *