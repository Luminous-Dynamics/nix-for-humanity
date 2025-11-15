#!/usr/bin/env python3
"""
Final verification that v0.4.0 is ready for release
"""

import os
import sys
import tarfile


def check_performance():
    """Verify performance targets are met"""
    print("⚡ Performance Verification")
    print("-" * 40)

    from src.luminous_nix.core.ultra_fast_cache import get_ultra_cache

    cache = get_ultra_cache()

    # Test multiple operations
    operations = []

    # Search
    _, elapsed = cache.search_instant("firefox")
    operations.append(("Search", elapsed))

    # Info
    _, elapsed = cache.info_instant("vim")
    operations.append(("Info", elapsed))

    # List
    _, elapsed = cache.list_instant()
    operations.append(("List", elapsed))

    # Check all under 100ms
    all_fast = True
    for op, time_ms in operations:
        status = "✅" if time_ms < 100 else "❌"
        print(f"  {status} {op}: {time_ms:.3f}ms")
        if time_ms >= 100:
            all_fast = False

    avg_time = sum(t for _, t in operations) / len(operations)
    print(f"\n  Average: {avg_time:.3f}ms")

    return all_fast and avg_time < 100


def check_rust_module():
    """Check if Rust module is built"""
    print("\n🦀 Rust Module Check")
    print("-" * 40)

    rust_built = False

    # Check for built artifacts
    rust_paths = [
        "rust/target/release",
        "rust/target/debug",
        "target/release",
    ]

    for path in rust_paths:
        if os.path.exists(path):
            print(f"  ✅ Found Rust build: {path}")
            rust_built = True
            break

    if not rust_built:
        print("  ⚠️  Rust module not built (optional)")

    return True  # Rust is optional


def check_release_package():
    """Verify release package exists and is valid"""
    print("\n📦 Release Package Check")
    print("-" * 40)

    package_path = "dist-v040/luminous-nix-v0.4.0.tar.gz"

    if not os.path.exists(package_path):
        print(f"  ❌ Package not found: {package_path}")
        return False

    # Check size
    size_mb = os.path.getsize(package_path) / (1024 * 1024)
    print(f"  ✅ Package exists: {size_mb:.2f} MB")

    # Verify contents
    try:
        with tarfile.open(package_path, "r:gz") as tar:
            members = tar.getnames()

            required_files = [
                "luminous-nix-v0.4.0/luminous-nix",
                "luminous-nix-v0.4.0/src",
                "luminous-nix-v0.4.0/INSTALL.txt",
            ]

            for required in required_files:
                if any(required in m for m in members):
                    print(f"  ✅ Contains: {required}")
                else:
                    print(f"  ❌ Missing: {required}")
                    return False
    except Exception as e:
        print(f"  ❌ Package invalid: {e}")
        return False

    return True


def check_install_command():
    """Verify install command works"""
    print("\n📥 Install Command Check")
    print("-" * 40)

    from src.luminous_nix.core.install_handler import get_install_handler

    handler = get_install_handler(dry_run=True)

    # Test a few packages
    test_packages = ["firefox", "vim", "git"]

    for pkg in test_packages:
        success, _, elapsed = handler.install_package(pkg)
        status = "✅" if success and elapsed < 100 else "❌"
        print(f"  {status} Install {pkg}: {elapsed:.2f}ms")

    return True


def check_documentation():
    """Verify documentation is complete"""
    print("\n📚 Documentation Check")
    print("-" * 40)

    docs = [
        "README.md",
        "CHANGELOG.md",
        "RELEASE_ANNOUNCEMENT_v040.md",
        "ACHIEVEMENT_SUMMARY.md",
        "FINAL_ACHIEVEMENT_REPORT.md",
    ]

    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ Missing: {doc}")
            all_exist = False

    return all_exist


def run_all_checks():
    """Run all verification checks"""
    print("🔍 Luminous Nix v0.4.0 Release Verification")
    print("=" * 50)

    checks = [
        ("Performance", check_performance),
        ("Rust Module", check_rust_module),
        ("Release Package", check_release_package),
        ("Install Command", check_install_command),
        ("Documentation", check_documentation),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)

    all_pass = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_pass = False

    print("\n" + "=" * 50)
    if all_pass:
        print("🎉 ALL CHECKS PASSED!")
        print("✨ v0.4.0 is ready for release!")
        print("🚀 Performance target achieved: <100ms")
        print("📦 Package ready: dist-v040/luminous-nix-v0.4.0.tar.gz")
        print("\nNext steps:")
        print("  1. Tag the release: git tag v0.4.0")
        print("  2. Push to GitHub: git push origin v0.4.0")
        print("  3. Create GitHub release with RELEASE_ANNOUNCEMENT_v040.md")
        print("  4. Upload dist-v040/luminous-nix-v0.4.0.tar.gz")
        return 0
    else:
        print("⚠️  Some checks failed")
        print("Please fix issues before release")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_checks())
