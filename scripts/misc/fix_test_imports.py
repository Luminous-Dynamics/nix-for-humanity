#!/usr/bin/env python3
"""
Fix test imports to use backend/ instead of nix_for_humanity
"""

import os
import re
from pathlib import Path


def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
        
    original_content = content
    
    # Map of replacements
    replacements = [
        # Core modules
        (r'from nix_for_humanity\.core\.engine import', 'from luminous_nix.core.engine import'),
        (r'from nix_for_humanity\.core\.types import', 'from luminous_nix.core.intents import'),
        (r'from nix_for_humanity\.core\.intent_engine import', 'from luminous_nix.core.intents import'),
        (r'from nix_for_humanity\.core\.intent import', 'from luminous_nix.core.intents import'),
        (r'from nix_for_humanity\.core\.execution_engine import', 'from luminous_nix.core.executor import'),
        (r'from nix_for_humanity\.core\.executor import', 'from luminous_nix.core.executor import'),
        (r'from nix_for_humanity\.core\.knowledge_base import', 'from luminous_nix.core.knowledge import'),
        (r'from nix_for_humanity\.core\.knowledge import', 'from luminous_nix.core.knowledge import'),
        (r'from nix_for_humanity\.core\.backend import', 'from luminous_nix.core.engine import'),
        (r'from nix_for_humanity\.core\.personality_system import', 'from luminous_nix.core.personality import'),
        (r'from nix_for_humanity\.core\.interface import', 'from luminous_nix.core.interface import'),
        
        # NLP modules
        (r'from nix_for_humanity\.nlp\.intent_engine import', 'from luminous_nix.core.intents import'),
        (r'from nix_for_humanity\.nlp\.pattern_matcher import', 'from luminous_nix.core.intents import'),
        
        # Learning modules
        (r'from nix_for_humanity\.learning\.preferences import', 'from luminous_nix.learning.preferences import'),
        (r'from nix_for_humanity\.learning\.pattern_learner import', 'from luminous_nix.learning.pattern_learner import'),
        
        # XAI modules
        (r'from nix_for_humanity\.xai\.engine import', 'from luminous_nix.xai.engine import'),
        (r'from nix_for_humanity\.xai\.causal_engine import', 'from luminous_nix.xai.causal_engine import'),
        (r'from nix_for_humanity\.xai\.explanation_formatter import', 'from luminous_nix.xai.explanation_formatter import'),
        
        # TUI modules
        (r'from nix_for_humanity\.tui\.app import', 'from luminous_nix.tui.app import'),
        (r'from nix_for_humanity\.tui\.enhanced_app import', 'from luminous_nix.tui.enhanced_app import'),
        (r'from nix_for_humanity\.tui\.persona_styles import', 'from luminous_nix.tui.persona_styles import'),
        
        # Voice modules
        (r'from nix_for_humanity\.voice\.interface import', 'from luminous_nix.voice.interface import'),
        (r'from nix_for_humanity\.voice\.model_manager import', 'from luminous_nix.voice.model_manager import'),
        (r'from nix_for_humanity\.voice\.voice_config import', 'from luminous_nix.voice.voice_config import'),
        
        # Security modules
        (r'from nix_for_humanity\.security\.validator import', 'from luminous_nix.security.validator import'),
        (r'from nix_for_humanity\.security\.enhanced_validator import', 'from luminous_nix.security.enhanced_validator import'),
        
        # Accessibility modules
        (r'from nix_for_humanity\.accessibility\.screen_reader import', 'from luminous_nix.accessibility.screen_reader import'),
        (r'from nix_for_humanity\.accessibility\.persona_accessibility import', 'from luminous_nix.accessibility.persona_accessibility import'),
        
        # Monitoring modules
        (r'from nix_for_humanity\.monitoring\.performance_monitor import', 'from luminous_nix.monitoring.performance_monitor import'),
        
        # Adapters
        (r'from nix_for_humanity\.adapters\.cli_adapter import', 'from luminous_nix.adapters.cli_adapter import'),
        
        # Caching modules
        (r'from nix_for_humanity\.caching\.response_cache import', 'from luminous_nix.caching.response_cache import'),
        (r'from nix_for_humanity\.caching\.xai_cache import', 'from luminous_nix.caching.xai_cache import'),
        
        # Testing modules
        (r'from nix_for_humanity\.testing\.persona_testing_framework import', 'from luminous_nix.testing.persona_testing_framework import'),
        
        # General catch-all for any missed imports
        (r'from nix_for_humanity\.', 'from luminous_nix.'),
        (r'import nix_for_humanity\.', 'import luminous_nix.'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
        
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False


def main():
    """Fix imports in all test files"""
    test_dir = Path(__file__).parent / 'tests'
    
    fixed_count = 0
    total_count = 0
    
    # Find all Python test files
    for test_file in test_dir.rglob('*.py'):
        total_count += 1
        if fix_imports_in_file(test_file):
            fixed_count += 1
            print(f"Fixed imports in: {test_file.relative_to(test_dir.parent)}")
            
    print(f"\nFixed {fixed_count} out of {total_count} test files")
    

if __name__ == "__main__":
    main()