#!/usr/bin/env python3
"""Fix executor tests specifically."""

import re

def fix_executor_test():
    """Fix the executor test file."""
    
    with open('tests/unit/test_executor.py', 'r') as f:
        content = f.read()
    
    # Replace all backend.core.executor patches with the right module
    content = re.sub(r"@patch\('backend\.core\.executor\.", "@patch('nix_for_humanity.core.execution_engine.", content)
    content = re.sub(r'with patch\(\'backend\.core\.executor\.', "with patch('nix_for_humanity.core.execution_engine.", content)
    
    # Replace Result(...) with dict
    content = re.sub(r'Result\(\s*success=([^,]+),\s*output=([^,]+),\s*error=([^)]+)\)', 
                     r"{'success': \1, 'output': \2, 'error': \3}", content)
    
    # Fix the class definition
    content = content.replace('self.executor = ExecutionEngine(progress_callback=self.progress_callback)',
                             'self.engine = ExecutionEngine()\n        self.engine.progress_callback = self.progress_callback')
    
    content = content.replace('self.executor', 'self.engine')
    
    # Fix asyncio imports
    content = re.sub(r"import asyncio", "import asyncio", content)
    
    # Add asyncio import if not present
    if "import asyncio" not in content:
        content = content.replace("import unittest", "import unittest\nimport asyncio")
    
    with open('tests/unit/test_executor.py', 'w') as f:
        f.write(content)
    
    print("Fixed test_executor.py")

def fix_executor_comprehensive_test():
    """Fix the comprehensive executor test file."""
    
    try:
        with open('tests/unit/test_executor_comprehensive.py', 'r') as f:
            content = f.read()
        
        # Similar fixes
        content = re.sub(r"from backend\.core\.executor import", "from nix_for_humanity.core.execution_engine import", content)
        content = content.replace('SafeExecutor', 'ExecutionEngine')
        content = content.replace('TestSafeExecutor', 'TestExecutionEngine')
        
        # Fix Result usage
        content = re.sub(r'Result\(\s*success=([^,]+),\s*output=([^,]+),\s*error=([^)]+)\)', 
                         r"{'success': \1, 'output': \2, 'error': \3}", content)
        
        with open('tests/unit/test_executor_comprehensive.py', 'w') as f:
            f.write(content)
        
        print("Fixed test_executor_comprehensive.py")
    except FileNotFoundError:
        print("test_executor_comprehensive.py not found")

if __name__ == '__main__':
    fix_executor_test()
    fix_executor_comprehensive_test()