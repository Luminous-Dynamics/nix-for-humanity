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
        (r'from nix_for_humanity\.core\.engine import', 'from nix_humanity.core.engine import'),
        (r'from nix_for_humanity\.core\.types import', 'from nix_humanity.core.intents import'),
        (r'from nix_for_humanity\.core\.intent_engine import', 'from nix_humanity.core.intents import'),
        (r'from nix_for_humanity\.core\.intent import', 'from nix_humanity.core.intents import'),
        (r'from nix_for_humanity\.core\.execution_engine import', 'from nix_humanity.core.executor import'),
        (r'from nix_for_humanity\.core\.executor import', 'from nix_humanity.core.executor import'),
        (r'from nix_for_humanity\.core\.knowledge_base import', 'from nix_humanity.core.knowledge import'),
        (r'from nix_for_humanity\.core\.knowledge import', 'from nix_humanity.core.knowledge import'),
        (r'from nix_for_humanity\.core\.backend import', 'from nix_humanity.core.engine import'),
        (r'from nix_for_humanity\.core\.personality_system import', 'from nix_humanity.core.personality import'),
        (r'from nix_for_humanity\.core\.interface import', 'from nix_humanity.core.interface import'),
        
        # NLP modules
        (r'from nix_for_humanity\.nlp\.intent_engine import', 'from nix_humanity.core.intents import'),
        (r'from nix_for_humanity\.nlp\.pattern_matcher import', 'from nix_humanity.core.intents import'),
        
        # Learning modules
        (r'from nix_for_humanity\.learning\.preferences import', 'from nix_humanity.learning.preferences import'),
        (r'from nix_for_humanity\.learning\.pattern_learner import', 'from nix_humanity.learning.pattern_learner import'),
        
        # XAI modules
        (r'from nix_for_humanity\.xai\.engine import', 'from nix_humanity.xai.engine import'),
        (r'from nix_for_humanity\.xai\.causal_engine import', 'from nix_humanity.xai.causal_engine import'),
        (r'from nix_for_humanity\.xai\.explanation_formatter import', 'from nix_humanity.xai.explanation_formatter import'),
        
        # TUI modules
        (r'from nix_for_humanity\.tui\.app import', 'from nix_humanity.tui.app import'),
        (r'from nix_for_humanity\.tui\.enhanced_app import', 'from nix_humanity.tui.enhanced_app import'),
        (r'from nix_for_humanity\.tui\.persona_styles import', 'from nix_humanity.tui.persona_styles import'),
        
        # Voice modules
        (r'from nix_for_humanity\.voice\.interface import', 'from nix_humanity.voice.interface import'),
        (r'from nix_for_humanity\.voice\.model_manager import', 'from nix_humanity.voice.model_manager import'),
        (r'from nix_for_humanity\.voice\.voice_config import', 'from nix_humanity.voice.voice_config import'),
        
        # Security modules
        (r'from nix_for_humanity\.security\.validator import', 'from nix_humanity.security.validator import'),
        (r'from nix_for_humanity\.security\.enhanced_validator import', 'from nix_humanity.security.enhanced_validator import'),
        
        # Accessibility modules
        (r'from nix_for_humanity\.accessibility\.screen_reader import', 'from nix_humanity.accessibility.screen_reader import'),
        (r'from nix_for_humanity\.accessibility\.persona_accessibility import', 'from nix_humanity.accessibility.persona_accessibility import'),
        
        # Monitoring modules
        (r'from nix_for_humanity\.monitoring\.performance_monitor import', 'from nix_humanity.monitoring.performance_monitor import'),
        
        # Adapters
        (r'from nix_for_humanity\.adapters\.cli_adapter import', 'from nix_humanity.adapters.cli_adapter import'),
        
        # Caching modules
        (r'from nix_for_humanity\.caching\.response_cache import', 'from nix_humanity.caching.response_cache import'),
        (r'from nix_for_humanity\.caching\.xai_cache import', 'from nix_humanity.caching.xai_cache import'),
        
        # Testing modules
        (r'from nix_for_humanity\.testing\.persona_testing_framework import', 'from nix_humanity.testing.persona_testing_framework import'),
        
        # General catch-all for any missed imports
        (r'from nix_for_humanity\.', 'from nix_humanity.'),
        (r'import nix_for_humanity\.', 'import nix_humanity.'),
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