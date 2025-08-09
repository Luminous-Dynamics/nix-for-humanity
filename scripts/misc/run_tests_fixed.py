#!/usr/bin/env python3
"""
Custom test runner for Nix for Humanity that fixes import errors.

This script:
1. Sets up comprehensive mocks for optional dependencies
2. Configures proper Python paths
3. Runs tests even when pytest and optional deps aren't installed
4. Provides detailed import error diagnostics
"""

import sys
import os
import traceback
import unittest
from pathlib import Path

def setup_environment():
    """Set up the testing environment with proper paths and mocks."""
    
    # Add paths
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    test_dir = project_root / "tests"
    
    sys.path.insert(0, str(src_dir))
    sys.path.insert(0, str(test_dir))
    
    # Import and apply mocks
    try:
        import conftest
        print("✅ Test environment configured with mocks")
        return True
    except Exception as e:
        print(f"⚠️  Could not configure test environment: {e}")
        return False

def discover_and_run_tests():
    """Discover and run tests using unittest."""
    
    print("🔍 Discovering test files...")
    
    # Find all test files
    test_dir = Path(__file__).parent / "tests"
    test_files = list(test_dir.rglob("test_*.py"))
    
    print(f"📁 Found {len(test_files)} test files:")
    for test_file in test_files:
        rel_path = test_file.relative_to(test_dir)
        print(f"   {rel_path}")
    
    if not test_files:
        print("❌ No test files found!")
        return False
    
    # Run tests using unittest
    print("\n🧪 Running tests...")
    
    # Collect test results
    successful_tests = []
    failed_tests = []
    skipped_tests = []
    
    for test_file in test_files:
        test_name = test_file.stem
        rel_path = test_file.relative_to(test_dir)
        
        print(f"\n📝 Testing {rel_path}...")
        
        try:
            # Add the test file's directory to path
            test_module_dir = test_file.parent
            if str(test_module_dir) not in sys.path:
                sys.path.insert(0, str(test_module_dir))
            
            # Try to import the test module
            spec = __import__(test_name)
            
            # Create a test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(spec)
            
            # Run the tests
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)
            
            if result.wasSuccessful():
                successful_tests.append(test_name)
                print(f"✅ {test_name}: {result.testsRun} tests passed")
            else:
                failed_tests.append((test_name, result))
                print(f"❌ {test_name}: {len(result.failures)} failures, {len(result.errors)} errors")
                
        except ImportError as e:
            failed_tests.append((test_name, f"Import error: {e}"))
            print(f"❌ {test_name}: Import failed - {e}")
            
        except Exception as e:
            failed_tests.append((test_name, f"Unexpected error: {e}"))
            print(f"❌ {test_name}: Unexpected error - {e}")
            
    # Summary
    print(f"\n📊 Test Results Summary:")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"⏭️  Skipped: {len(skipped_tests)}")
    
    if successful_tests:
        print(f"\n✅ Successful tests:")
        for test in successful_tests:
            print(f"   {test}")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test, error in failed_tests:
            print(f"   {test}: {error}")
            
    return len(failed_tests) == 0

def run_specific_test(test_pattern=None):
    """Run a specific test or pattern of tests."""
    
    if not test_pattern:
        return discover_and_run_tests()
    
    test_dir = Path(__file__).parent / "tests"
    
    # Find matching test files
    if test_pattern.endswith('.py'):
        test_files = [test_dir / test_pattern]
    else:
        test_files = list(test_dir.rglob(f"*{test_pattern}*.py"))
    
    if not test_files:
        print(f"❌ No test files found matching '{test_pattern}'")
        return False
    
    print(f"🎯 Running {len(test_files)} test file(s) matching '{test_pattern}':")
    
    success = True
    for test_file in test_files:
        if not test_file.exists():
            print(f"❌ {test_file} does not exist")
            success = False
            continue
            
        test_name = test_file.stem
        rel_path = test_file.relative_to(test_dir)
        
        print(f"\n📝 Running {rel_path}...")
        
        try:
            # Import and run the specific test
            test_module_dir = test_file.parent
            if str(test_module_dir) not in sys.path:
                sys.path.insert(0, str(test_module_dir))
            
            spec = __import__(test_name)
            
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(spec)
            
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            if not result.wasSuccessful():
                success = False
                print(f"❌ {test_name} failed")
            else:
                print(f"✅ {test_name} passed")
                
        except Exception as e:
            success = False
            print(f"❌ {test_name} failed with error: {e}")
            traceback.print_exc()
    
    return success

def main():
    """Main entry point."""
    
    print("🧪 Nix for Humanity Test Runner with Import Fixes")
    print("=" * 50)
    
    # Set up environment
    if not setup_environment():
        print("❌ Failed to set up test environment")
        return 1
    
    # Check command line arguments
    if len(sys.argv) > 1:
        test_pattern = sys.argv[1]
        success = run_specific_test(test_pattern)
    else:
        success = discover_and_run_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n💥 Some tests failed or had errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())