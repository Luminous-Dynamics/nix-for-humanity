#!/usr/bin/env python3
"""
Verification Script - What ACTUALLY Works in Luminous Nix
Run this to get the TRUTH about the current state.
"""

import sys
import time
import subprocess
from pathlib import Path

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def test_import(module_path: str, class_name: str = None) -> tuple[bool, str]:
    """Test if a module/class can be imported."""
    try:
        module = __import__(module_path, fromlist=[class_name] if class_name else [])
        if class_name:
            getattr(module, class_name)
        return True, "✅ Imports successfully"
    except ImportError as e:
        return False, f"❌ Import error: {str(e)[:50]}"
    except AttributeError as e:
        return False, f"❌ Class not found: {str(e)[:50]}"
    except Exception as e:
        return False, f"❌ Error: {str(e)[:50]}"

def test_cli_command(command: str) -> tuple[bool, float, str]:
    """Test if a CLI command works and measure time."""
    try:
        start = time.time()
        result = subprocess.run(
            f"poetry run ask-nix {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        elapsed = (time.time() - start) * 1000
        
        if result.returncode == 0:
            return True, elapsed, "✅ Command executed"
        else:
            error = result.stderr[:50] if result.stderr else "No output"
            return False, elapsed, f"❌ Failed: {error}"
    except subprocess.TimeoutExpired:
        return False, 5000, "❌ Timeout (>5s)"
    except Exception as e:
        return False, 0, f"❌ Error: {str(e)[:50]}"

def main():
    print(f"\n{Colors.BOLD}LUMINOUS NIX - VERIFICATION OF ACTUAL STATUS{Colors.RESET}")
    print("=" * 60)
    
    results = {
        "imports": [],
        "commands": [],
        "performance": []
    }
    
    # Test Core Imports
    print(f"\n{Colors.BOLD}1. CORE MODULE IMPORTS{Colors.RESET}")
    modules_to_test = [
        ("luminous_nix.core.native_nix_api", "NativeNixAPI"),
        ("luminous_nix.core.json_optimized_nix", "JSONOptimizedNix"),
        ("luminous_nix.core.integrated_backend", "IntegratedBackend"),
        ("luminous_nix.core.executor", "SafeExecutor"),
        ("luminous_nix.services.cache", "CacheService"),
        ("luminous_nix.services.search", "SearchService"),
        ("luminous_nix.ai.hrm_reasoner_v2", "HRMv2NixOSReasoner"),  # Fixed class name
        ("luminous_nix.embeddings.gemma_encoder", "GemmaEncoder"),
    ]
    
    for module, cls in modules_to_test:
        success, msg = test_import(module, cls)
        results["imports"].append((f"{module}.{cls}", success))
        status = f"{Colors.GREEN}✅{Colors.RESET}" if success else f"{Colors.RED}❌{Colors.RESET}"
        print(f"  {status} {cls:30} {msg}")
    
    # Test CLI Commands
    print(f"\n{Colors.BOLD}2. CLI COMMAND FUNCTIONALITY{Colors.RESET}")
    commands = [
        "help",
        "list",
        "search vim",
        '"install firefox" --dry-run',
    ]
    
    for cmd in commands:
        success, elapsed, msg = test_cli_command(cmd)
        results["commands"].append((cmd, success, elapsed))
        status = f"{Colors.GREEN}✅{Colors.RESET}" if success else f"{Colors.RED}❌{Colors.RESET}"
        time_str = f"({elapsed:.0f}ms)" if elapsed > 0 else ""
        print(f"  {status} {cmd:30} {msg} {time_str}")
    
    # Performance Summary
    print(f"\n{Colors.BOLD}3. PERFORMANCE METRICS{Colors.RESET}")
    avg_time = sum(t for _, _, t in results["commands"] if t > 0) / len(results["commands"])
    
    if avg_time < 100:
        perf_status = f"{Colors.GREEN}✅ EXCELLENT{Colors.RESET}"
    elif avg_time < 500:
        perf_status = f"{Colors.GREEN}✅ GOOD{Colors.RESET}"
    elif avg_time < 2000:
        perf_status = f"{Colors.YELLOW}⚠️ ACCEPTABLE{Colors.RESET}"
    else:
        perf_status = f"{Colors.RED}❌ NEEDS WORK{Colors.RESET}"
    
    print(f"  Average response time: {avg_time:.0f}ms {perf_status}")
    
    # Overall Summary
    print(f"\n{Colors.BOLD}4. OVERALL SUMMARY{Colors.RESET}")
    imports_working = sum(1 for _, s in results["imports"] if s)
    imports_total = len(results["imports"])
    commands_working = sum(1 for _, s, _ in results["commands"] if s)
    commands_total = len(results["commands"])
    
    print(f"  Modules working:  {imports_working}/{imports_total} ({imports_working*100//imports_total}%)")
    print(f"  Commands working: {commands_working}/{commands_total} ({commands_working*100//commands_total}%)")
    print(f"  Performance:      {avg_time:.0f}ms average")
    
    # Honest Assessment
    print(f"\n{Colors.BOLD}5. HONEST ASSESSMENT{Colors.RESET}")
    
    if imports_working >= 6 and commands_working >= 3 and avg_time < 2000:
        print(f"  {Colors.GREEN}✅ Core functionality is working{Colors.RESET}")
        print(f"  Ready for: Alpha testing with known limitations")
    elif imports_working >= 4 and commands_working >= 2:
        print(f"  {Colors.YELLOW}⚠️ Partially functional{Colors.RESET}")
        print(f"  Ready for: Development testing only")
    else:
        print(f"  {Colors.RED}❌ Significant issues present{Colors.RESET}")
        print(f"  Ready for: Internal development only")
    
    # Write results to file for CLAUDE.md update
    with open("VERIFICATION_RESULTS.md", "w") as f:
        f.write(f"# Verification Results - {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Module Status\n")
        for name, success in results["imports"]:
            f.write(f"- {name}: {'✅ Working' if success else '❌ Not working'}\n")
        f.write(f"\n## Command Status\n")
        for cmd, success, elapsed in results["commands"]:
            f.write(f"- `{cmd}`: {'✅' if success else '❌'} ({elapsed:.0f}ms)\n")
        f.write(f"\n## Performance\n")
        f.write(f"- Average response: {avg_time:.0f}ms\n")
        f.write(f"- Target: <100ms\n")
        f.write(f"- Status: {'✅ Met' if avg_time < 100 else '❌ Not met'}\n")
    
    print(f"\n{Colors.BOLD}Results written to VERIFICATION_RESULTS.md{Colors.RESET}")
    
    return 0 if imports_working >= 6 else 1

if __name__ == "__main__":
    sys.path.insert(0, "/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/src")
    sys.exit(main())