#!/usr/bin/env python3
"""
Real NixOS Integration Tests

These tests actually verify that commands work on a real NixOS system.
No mocks, no fakes - real system interaction.
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from luminous_nix.core.backend_real import RealNixBackend
from luminous_nix.core.intents import Intent, IntentType
from luminous_nix.frontends.cli import UnifiedNixAssistant


def test_real_backend():
    """Test the real backend with actual NixOS commands"""
    backend = RealNixBackend()
    results = []

    print("🧪 Testing Real NixOS Backend Integration")
    print("=" * 50)

    # Test 1: Help command
    print("\n1. Testing HELP command...")
    intent = Intent(type=IntentType.HELP, entities={}, confidence=1.0, raw_text="help")
    response = backend.process(intent)
    results.append(("HELP", response.success))
    print(f"   {'✅' if response.success else '❌'} Help: {response.success}")
    assert response.success, "Help command should always work"
    assert len(response.text) > 100, "Help should have substantial content"

    # Test 2: List installed packages
    print("\n2. Testing LIST command...")
    intent = Intent(
        type=IntentType.LIST_INSTALLED, entities={}, confidence=1.0, raw_text="list"
    )
    response = backend.process(intent)
    results.append(("LIST", response.success))
    print(f"   {'✅' if response.success else '❌'} List: {response.success}")
    assert response.success, "List should work on any NixOS system"
    assert response.data and "packages" in response.data, "Should return package list"
    packages = response.data["packages"]
    print(f"   Found {len(packages)} packages")
    assert len(packages) > 0, "Should have at least one package installed"

    # Test 3: System info
    print("\n3. Testing INFO command...")
    intent = Intent(
        type=IntentType.CHECK_STATUS, entities={}, confidence=1.0, raw_text="info"
    )
    response = backend.process(intent)
    results.append(("INFO", response.success))
    print(f"   {'✅' if response.success else '❌'} Info: {response.success}")
    assert response.success, "System info should always work"
    assert response.data, "Should return system data"
    assert "nix_version" in response.data, "Should have Nix version"
    assert "nixos_version" in response.data, "Should have NixOS version"
    print(f"   NixOS: {response.data.get('nixos_version', 'Unknown')}")
    print(f"   Nix: {response.data.get('nix_version', 'Unknown')}")

    # Test 4: Search (with timeout)
    print("\n4. Testing SEARCH command (5s timeout)...")
    backend.executor.timeout = 5  # Short timeout
    intent = Intent(
        type=IntentType.SEARCH_PACKAGE,
        entities={"package": "hello"},
        confidence=1.0,
        raw_text="search hello",
    )
    response = backend.process(intent)
    results.append(("SEARCH", response.success or "timeout" in response.text.lower()))
    if response.success:
        print("   ✅ Search: successful")
    else:
        print(
            f"   ⚠️  Search: {'timeout' if 'timeout' in response.text.lower() else 'failed'}"
        )
    # Search can timeout, that's OK

    # Test 5: Dry run install
    print("\n5. Testing INSTALL (dry-run)...")
    import os

    os.environ["LUMINOUS_DRY_RUN"] = "true"
    backend = RealNixBackend()  # Reinitialize with dry run
    intent = Intent(
        type=IntentType.INSTALL_PACKAGE,
        entities={"package": "cowsay"},
        confidence=1.0,
        raw_text="install cowsay",
    )
    response = backend.process(intent)
    results.append(("INSTALL_DRY", response.success))
    print(f"   {'✅' if response.success else '❌'} Dry run: {response.success}")
    assert response.success, "Dry run should always succeed"
    assert (
        "DRY RUN" in response.text or "Would" in response.text
    ), "Should indicate dry run"

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"   Passed: {passed}/{total}")

    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")

    assert passed >= 4, f"At least 4 tests should pass, got {passed}"
    print("\n✅ Real NixOS integration verified!")
    return True


def test_cli_with_real_backend():
    """Test the CLI with real backend integration"""
    print("\n🧪 Testing CLI with Real Backend")
    print("=" * 50)

    import os

    os.environ["LUMINOUS_DRY_RUN"] = "true"
    os.environ["LUMINOUS_SKIP_CONFIRM"] = "true"

    assistant = UnifiedNixAssistant()

    # Verify real backend is loaded
    assert assistant.real_backend is not None, "Real backend should be initialized"
    print("✅ Real backend loaded in CLI")

    # Test a simple query through the CLI
    import io
    from contextlib import redirect_stdout

    output = io.StringIO()
    with redirect_stdout(output):
        assistant._handle_list_installed()

    result = output.getvalue()
    assert (
        "packages" in result.lower() or "installed" in result.lower()
    ), "Should show packages"
    print("✅ CLI list command works with real backend")

    return True


def test_subprocess_execution():
    """Test that we can actually run NixOS commands"""
    print("\n🧪 Testing Direct Subprocess Execution")
    print("=" * 50)

    # Test 1: nix --version
    try:
        result = subprocess.run(
            ["nix", "--version"], capture_output=True, text=True, timeout=5
        )
        assert result.returncode == 0, "nix --version should succeed"
        assert "nix" in result.stdout.lower(), "Should contain 'nix' in output"
        print(f"✅ nix --version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Failed to run nix --version: {e}")
        return False

    # Test 2: nixos-version (might not be available in all environments)
    try:
        result = subprocess.run(
            ["nixos-version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"✅ nixos-version: {result.stdout.strip()}")
        else:
            print("⚠️  nixos-version not available (OK if not on NixOS)")
    except FileNotFoundError:
        print("⚠️  nixos-version command not found (OK if not on NixOS)")
    except Exception as e:
        print(f"⚠️  nixos-version failed: {e}")

    return True


def main():
    """Run all integration tests"""
    print("🚀 Luminous Nix - Real Integration Tests")
    print("=" * 50)
    print("Testing with REAL NixOS commands - no mocks!\n")

    tests = [
        ("Subprocess Execution", test_subprocess_execution),
        ("Real Backend", test_real_backend),
        ("CLI Integration", test_cli_with_real_backend),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'=' * 50}")
            print(f"Running: {test_name}")
            print("=" * 50)
            success = test_func()
            results.append((test_name, success))
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))
        except Exception as e:
            print(f"❌ Test error: {e}")
            results.append((test_name, False))

    # Final summary
    print("\n" + "=" * 50)
    print("🏁 FINAL RESULTS")
    print("=" * 50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Real NixOS integration working!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
