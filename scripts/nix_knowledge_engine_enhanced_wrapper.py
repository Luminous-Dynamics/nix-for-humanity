"""
Wrapper module to allow clean imports of nix-knowledge-engine-enhanced
"""

import importlib.util
import sys
from pathlib import Path

# First load the AI licensing advisor wrapper
import ai_licensing_advisor_wrapper

# Then load the enhanced engine
module_path = Path(__file__).parent / "nix-knowledge-engine-enhanced.py"
spec = importlib.util.spec_from_file_location("nix_knowledge_engine_enhanced", module_path)
nix_knowledge_engine_enhanced = importlib.util.module_from_spec(spec)
sys.modules["nix_knowledge_engine_enhanced"] = nix_knowledge_engine_enhanced
spec.loader.exec_module(nix_knowledge_engine_enhanced)

# Export the class
EnhancedNixOSKnowledgeEngine = nix_knowledge_engine_enhanced.EnhancedNixOSKnowledgeEngine