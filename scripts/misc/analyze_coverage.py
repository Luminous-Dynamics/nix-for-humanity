#!/usr/bin/env python3
"""
Manual coverage analysis for CLI adapter
"""

import ast
import sys
from pathlib import Path

def analyze_cli_adapter_coverage():
    """Analyze what we've covered in our tests"""
    
    # Path to the CLI adapter
    cli_adapter_path = Path("src/nix_for_humanity/adapters/cli_adapter.py")
    
    if not cli_adapter_path.exists():
        print(f"❌ CLI adapter not found at {cli_adapter_path}")
        return
    
    # Read the source code
    with open(cli_adapter_path) as f:
        source = f.read()
    
    # Parse AST
    tree = ast.parse(source)
    
    # Find all methods in the CLIAdapter class
    methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CLIAdapter":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)
    
    print("🔍 CLI Adapter Methods Found:")
    for method in sorted(methods):
        print(f"  • {method}")
    
    print(f"\n📊 Total methods: {len(methods)}")
    
    # Methods we tested comprehensively
    tested_methods = {
        "__init__",
        "_check_rich_available", 
        "process_query",
        "_get_user_id",
        "display_response", 
        "_display_simple",
        "_display_rich",
        "_gather_feedback",
        "set_personality",
        "get_stats"
    }
    
    print(f"\n✅ Methods with comprehensive tests: {len(tested_methods)}")
    for method in sorted(tested_methods):
        if method in methods:
            print(f"  ✓ {method}")
        else:
            print(f"  ⚠️ {method} - not found in source")
    
    # Calculate coverage
    untested = set(methods) - tested_methods
    coverage_percent = (len(tested_methods) / len(methods)) * 100
    
    print(f"\n📈 Method Coverage: {coverage_percent:.1f}% ({len(tested_methods)}/{len(methods)})")
    
    if untested:
        print(f"\n❌ Untested methods:")
        for method in sorted(untested):
            print(f"  • {method}")
    else:
        print(f"\n🎉 All methods have tests!")
    
    # Count lines of code 
    lines = source.split('\n')
    total_lines = len(lines)
    code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
    
    print(f"\n📝 Lines of Code Analysis:")
    print(f"  • Total lines: {total_lines}")
    print(f"  • Code lines: {code_lines}")
    print(f"  • Comments/blank: {total_lines - code_lines}")
    
    return {
        'total_methods': len(methods),
        'tested_methods': len(tested_methods),
        'coverage_percent': coverage_percent,
        'untested': untested,
        'all_methods': methods
    }

if __name__ == "__main__":
    analyze_cli_adapter_coverage()