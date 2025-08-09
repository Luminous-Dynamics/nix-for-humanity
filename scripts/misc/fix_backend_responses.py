#!/usr/bin/env python3
"""
Fix Response schema issues in backend.py

This script updates the backend to use the simple Response format
consistently throughout the codebase.
"""

import re

def fix_backend_responses():
    # Read the backend file
    with open('backend/core/backend.py', 'r') as f:
        content = f.read()
    
    # Track changes
    changes = 0
    original = content
    
    # Fix the main response creation pattern
    # Pattern 1: Response with many fields including intent, plan, result
    pattern1 = re.compile(
        r'response = Response\(\s*'
        r'intent=intent,\s*'
        r'plan=plan,\s*'
        r'result=result,\s*'
        r'explanation=self\._explain\(intent, plan, result\),\s*'
        r'suggestions=self\._get_suggestions\(intent, result\),\s*'
        r'success=result\.success if result else True,\s*'
        r'commands=self\._extract_commands\(plan\)\s*\)',
        re.MULTILINE | re.DOTALL
    )
    
    replacement1 = '''response = create_simple_response(
                    intent=intent,
                    success=result.success if result else True,
                    text=self._explain(intent, plan, result),
                    commands=self._extract_commands(plan),
                    data={
                        'plan': plan,
                        'result': result.__dict__ if result else None,
                        'suggestions': self._get_suggestions(intent, result)
                    }
                )'''
    
    content = pattern1.sub(replacement1, content)
    changes += len(pattern1.findall(original))
    
    # Fix response attribute access
    # Replace response.explanation with response.text
    content = re.sub(r'response\.explanation', 'response.text', content)
    
    # Replace response.data with response.data if it doesn't exist
    content = re.sub(
        r'response\.data\[',
        'response.data[',
        content
    )
    
    # Write the fixed content
    with open('backend/core/backend.py', 'w') as f:
        f.write(content)
    
    print(f"Fixed {changes} Response creations")
    print("Updated response attribute access")
    print("Backend should now use consistent Response schema")


if __name__ == '__main__':
    fix_backend_responses()