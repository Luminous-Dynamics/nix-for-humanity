#!/usr/bin/env python3
"""Fix configuration validation support."""

import sqlite3
from pathlib import Path

def add_validation_support():
    """Add configuration validation support to knowledge base."""
    
    print("🔧 Adding Configuration Validation Support\n")
    
    # Connect to knowledge base
    db_path = Path("nixos_knowledge.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if validation entries already exist
    c.execute("SELECT COUNT(*) FROM solutions WHERE intent = 'validate_config'")
    count = c.fetchone()[0]
    
    if count > 0:
        print("✅ Validation support already exists")
        conn.close()
        return
    
    # Add validation solution
    validation_solution = {
        'intent': 'validate_config',
        'category': 'configuration',
        'solution': 'Validate NixOS configuration',
        'example': 'sudo nixos-rebuild test',
        'explanation': 'The `nixos-rebuild test` command validates your configuration and applies it temporarily without making it permanent. Use `nixos-rebuild dry-build` to check syntax without building.',
        'related': 'edit_config,show_config,rebuild_system'
    }
    
    c.execute('''
        INSERT INTO solutions (intent, category, solution, example, explanation, related)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        validation_solution['intent'],
        validation_solution['category'],
        validation_solution['solution'],
        validation_solution['example'],
        validation_solution['explanation'],
        validation_solution['related']
    ))
    
    conn.commit()
    print("✅ Added validation solution to knowledge base")
    
    # Now update the intent patterns
    print("\n🔧 Updating intent patterns...")
    
    intents_file = Path('src/nix_humanity/core/intents.py')
    
    with open(intents_file, 'r') as f:
        content = f.read()
    
    # Find where to add the new intent type
    if 'VALIDATE_CONFIG' not in content:
        # Add to IntentType enum
        enum_insert = content.find('class IntentType(Enum):')
        if enum_insert > 0:
            # Find a good place to insert (after EDIT_CONFIG if it exists)
            edit_config_pos = content.find('EDIT_CONFIG = "edit_config"')
            if edit_config_pos > 0:
                # Find the end of this line
                line_end = content.find('\n', edit_config_pos)
                # Insert new intent type
                new_intent = '\n    VALIDATE_CONFIG = "validate_config"'
                content = content[:line_end] + new_intent + content[line_end:]
                print("  ✅ Added VALIDATE_CONFIG to IntentType enum")
    
    # Add patterns for validation
    patterns_to_add = '''
            # Configuration validation
            (r'validate.*config', IntentType.VALIDATE_CONFIG),
            (r'check.*config', IntentType.VALIDATE_CONFIG),
            (r'test.*config', IntentType.VALIDATE_CONFIG),
            (r'verify.*config', IntentType.VALIDATE_CONFIG),
            (r'config.*valid', IntentType.VALIDATE_CONFIG),
'''
    
    # Find where to insert patterns
    patterns_pos = content.find('self.patterns = [')
    if patterns_pos > 0:
        # Find a good insertion point (after configuration patterns)
        config_pattern_pos = content.find("(r'.*configuration.*', IntentType.SHOW_CONFIG)")
        if config_pattern_pos > 0:
            # Find the end of this line
            line_end = content.find('\n', config_pattern_pos)
            # Insert new patterns
            content = content[:line_end] + ',' + patterns_to_add + content[line_end+1:]
            print("  ✅ Added validation patterns")
    
    # Write back the updated file
    with open(intents_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Configuration validation support added!")
    print("\nTest it with:")
    print("  ask-nix 'validate my config'")
    print("  ask-nix 'check configuration'")
    print("  ask-nix 'test config'")
    
    conn.close()

if __name__ == '__main__':
    add_validation_support()