#!/usr/bin/env python3
"""
Enhanced test script for Python backend integration in ask-nix
Tests both dry-run and actual execution modes
"""

import subprocess
import sys
from pathlib import Path

def test_command(command: str, description: str, dry_run: bool = True):
    """Test a single ask-nix command"""
    print(f"\n{'='*60}")
    print(f"📋 Testing: {description}")
    print(f"💬 Command: ask-nix '{command}'")
    print(f"🔍 Mode: {'Dry-run' if dry_run else 'Execute'}")
    print(f"{'='*60}")
    
    # Build command
    ask_nix_path = Path(__file__).parent / "bin" / "ask-nix"
    cmd_args = [str(ask_nix_path), "--show-intent"]
    
    if dry_run:
        cmd_args.append("--dry-run")
    else:
        cmd_args.append("--execute")
    
    cmd_args.append(command)
    
    result = subprocess.run(
        cmd_args,
        capture_output=True,
        text=True
    )
    
    print("\n📤 Output:")
    print(result.stdout)
    
    if result.stderr:
        print("\n⚠️  Stderr:")
        print(result.stderr)
    
    # Check if Python backend was used
    if "🐍 Using Python backend" in result.stdout:
        print("\n✅ Python backend was used!")
        return True
    else:
        print("\n⚠️  Python backend was NOT used (fallback to traditional method)")
        return False

def main():
    print("🧪 Testing Python Backend Integration for ask-nix (Enhanced)")
    print("==" * 30)
    
    # Check if we're on NixOS
    is_nixos = Path("/etc/nixos").exists()
    print(f"💻 System: {'NixOS' if is_nixos else 'Non-NixOS'}")
    
    # Check if Python backend exists
    backend_path = Path(__file__).parent / "backend" / "python" / "migrate_to_python_backend.py"
    print(f"🐍 Python backend exists: {backend_path.exists()}")
    
    # Test cases - first with dry-run, then with execute
    tests = [
        # Dry-run tests
        ("install firefox", "Package installation (dry-run)", True),
        ("update my system", "System update (dry-run)", True),
        ("remove htop", "Package removal (dry-run)", True),
        ("search python", "Package search (dry-run)", True),
        
        # Execute tests (these should use Python backend)
        ("search rust", "Package search (execute)", False),
        ("install --dry-run neofetch", "Package installation test (execute mode)", False),
    ]
    
    results = []
    for command, description, dry_run in tests:
        success = test_command(command, description, dry_run)
        results.append((description, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary:")
    print("="*60)
    
    python_backend_used = 0
    dry_run_count = 0
    execute_count = 0
    
    for description, success in results:
        status = "✅ Python backend" if success else "⚠️  Traditional method"
        print(f"{description}: {status}")
        if success:
            python_backend_used += 1
        if "(dry-run)" in description:
            dry_run_count += 1
        else:
            execute_count += 1
    
    print(f"\n🎯 Python backend usage: {python_backend_used}/{len(tests)} tests")
    print(f"   Dry-run tests: {sum(1 for d, s in results if '(dry-run)' in d and s)}/{dry_run_count}")
    print(f"   Execute tests: {sum(1 for d, s in results if '(execute)' in d and s)}/{execute_count}")
    
    # Analysis
    print("\n📊 Analysis:")
    if python_backend_used == 0:
        print("❌ Python backend is not being used at all!")
        print("Possible reasons:")
        print("- Backend files don't exist in expected location")
        print("- Import errors in the backend")
        print("- nixos-rebuild-ng module not found")
    else:
        print("✅ Python backend is working for some commands")
        print("\nObservations:")
        print("- Python backend may be disabled in dry-run mode for safety")
        print("- Search commands seem to work differently")
        print("- Execute mode may be required for full Python backend usage")
        
    # Additional info
    print("\n💡 Note:")
    print("The Python backend is designed to work with actual execution,")
    print("not dry-run mode, for safety reasons. This is expected behavior.")

if __name__ == "__main__":
    main()