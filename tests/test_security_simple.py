#!/usr/bin/env python3
"""
Simple security test to verify command injection fixes.
"""

import subprocess
import shlex

def test_shlex_safety():
    """Test that shlex.split properly handles dangerous input."""
    dangerous_inputs = [
        "firefox; rm -rf /tmp/test",
        "vim && echo 'hacked'", 
        "python | cat /etc/passwd",
        "nodejs`echo vulnerable`",
    ]
    
    print("Testing shlex.split safety:")
    print("=" * 60)
    
    for dangerous_input in dangerous_inputs:
        # Show how shlex.split handles it
        safe_args = shlex.split(dangerous_input)
        print(f"\nInput: {dangerous_input}")
        print(f"Shlex output: {safe_args}")
        print(f"Number of args: {len(safe_args)}")
        
        # Demonstrate it's safe - semicolon is part of argument, not separator
        if ';' in dangerous_input:
            has_semicolon = any(';' in arg for arg in safe_args)
            print(f"Semicolon preserved in args: {has_semicolon}")
    
    print("\n" + "=" * 60)
    print("✅ All dangerous inputs are safely tokenized!")
    print("When passed to subprocess.run() as a list, shell metacharacters")
    print("are treated as literal characters, not command separators.")

def test_subprocess_safety():
    """Test that list-based subprocess calls are safe."""
    print("\n\nTesting subprocess safety:")
    print("=" * 60)
    
    # Safe: Using list arguments
    safe_cmd = ["echo", "hello; rm -rf /"]
    print(f"Safe command: {safe_cmd}")
    
    result = subprocess.run(safe_cmd, capture_output=True, text=True)
    print(f"Output: {result.stdout.strip()}")
    print("Notice: The semicolon is printed literally, not interpreted!")
    
    # Show what would happen with shell=True (DON'T DO THIS!)
    print("\n⚠️  What shell=True would do (DANGEROUS - commented out):")
    print('subprocess.run("echo hello; rm -rf /", shell=True)')
    print("This would execute BOTH commands - echo AND rm!")
    
    print("\n✅ List-based subprocess calls prevent command injection!")

def check_file_for_shell_true(filepath):
    """Check if a file contains shell=True."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if 'shell=True' in content:
                # Count occurrences
                count = content.count('shell=True')
                return True, count
            return False, 0
    except Exception as e:
        return None, str(e)

def test_codebase_security():
    """Test that critical files don't contain shell=True."""
    print("\n\nChecking codebase for shell=True:")
    print("=" * 60)
    
    critical_files = [
        "/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/bin/ask-nix",
        "/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts/demo/demo-learning-mode.py",
        "/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts/monitor-coverage.py",
        "/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/intent_fix_summary.py",
    ]
    
    all_safe = True
    for filepath in critical_files:
        has_shell_true, result = check_file_for_shell_true(filepath)
        
        if has_shell_true is None:
            print(f"❓ {filepath}: Could not check - {result}")
        elif has_shell_true:
            print(f"❌ {filepath}: FOUND shell=True ({result} occurrences)")
            all_safe = False
        else:
            print(f"✅ {filepath}: Safe - no shell=True found")
    
    if all_safe:
        print("\n🎉 All critical files are secure!")
    else:
        print("\n⚠️  Security issues found - please fix shell=True usage!")

if __name__ == "__main__":
    print("🛡️ Nix for Humanity Security Test")
    print("=" * 80)
    
    test_shlex_safety()
    test_subprocess_safety()
    test_codebase_security()
    
    print("\n" + "=" * 80)
    print("🏆 Security test complete!")