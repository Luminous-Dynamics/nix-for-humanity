"""
Maya Mode - Lightning-fast NixOS for ADHD users

Designed for Maya (16, ADHD):
- INSTANT responses (no delays)
- MINIMAL text (just essentials)
- NO animations or pauses
- KEYBOARD shortcuts for everything  
- BATCH operations to reduce context switches
- VISUAL markers for quick scanning
"""

import subprocess
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import concurrent.futures
from threading import Thread
import queue


@dataclass
class MayaResponse:
    """Ultra-minimal response for ADHD users"""
    success: bool
    result: str  # ONE LINE result only
    cmd: Optional[str] = None  # Show the actual command for transparency
    time_ms: int = 0  # How fast we were


class MayaMode:
    """
    Lightning-fast NixOS interface for ADHD users.
    
    Philosophy:
    - SPEED is everything
    - NO waiting, NO fluff
    - Show command = trust
    - Parallel everything
    - Visual markers (✓ ✗ ⚡)
    """
    
    def __init__(self):
        # Pre-cache common operations for INSTANT response
        self.cache = {}
        self._precache_common()
        
        # Shortcuts for ultra-fast access
        self.shortcuts = {
            'ff': 'firefox',
            'tb': 'thunderbird', 
            'vs': 'vscode',
            'dc': 'discord',
            'sp': 'spotify',
            'ch': 'chromium',
            'gi': 'git',
            'py': 'python3',
            'nv': 'neovim'
        }
        
    def _precache_common(self):
        """Pre-cache common queries for instant response"""
        # Run in background to not block init
        Thread(target=self._cache_worker, daemon=True).start()
        
    def _cache_worker(self):
        """Background worker to keep cache fresh"""
        common_packages = ['firefox', 'vscode', 'discord', 'spotify']
        for pkg in common_packages:
            try:
                # Check if installed
                result = subprocess.run(
                    f"nix-env -q | grep -i {pkg}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                self.cache[f"installed_{pkg}"] = result.returncode == 0
            except:
                pass
    
    def quick_install(self, programs: List[str]) -> MayaResponse:
        """
        BATCH install multiple programs at once.
        Faster than one-by-one.
        """
        start = time.time()
        
        # Expand shortcuts
        expanded = []
        for p in programs:
            expanded.append(self.shortcuts.get(p.lower(), p))
        
        # Build single command for ALL packages
        packages = " ".join([f"nixpkgs#{p}" for p in expanded])
        cmd = f"nix profile install {packages}"
        
        # Execute FAST
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60  # Give it a minute max
            )
            
            elapsed = int((time.time() - start) * 1000)
            
            if result.returncode == 0:
                return MayaResponse(
                    success=True,
                    result=f"✓ {len(expanded)} installed",
                    cmd=cmd,
                    time_ms=elapsed
                )
            else:
                # Fast error - just show package that failed
                failed = result.stderr.split("'")[1] if "'" in result.stderr else "unknown"
                return MayaResponse(
                    success=False,
                    result=f"✗ {failed} failed",
                    cmd=cmd,
                    time_ms=elapsed
                )
                
        except subprocess.TimeoutExpired:
            return MayaResponse(
                success=False,
                result="✗ timeout",
                time_ms=60000
            )
    
    def quick_remove(self, programs: List[str]) -> MayaResponse:
        """BATCH remove - faster than individual"""
        start = time.time()
        
        # Expand shortcuts
        expanded = []
        for p in programs:
            expanded.append(self.shortcuts.get(p.lower(), p))
        
        # Single command
        packages = " ".join(expanded)
        cmd = f"nix-env -e {packages}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            elapsed = int((time.time() - start) * 1000)
            
            if result.returncode == 0:
                return MayaResponse(
                    success=True,
                    result=f"✓ {len(expanded)} removed",
                    cmd=cmd,
                    time_ms=elapsed
                )
            else:
                return MayaResponse(
                    success=False,
                    result="✗ not installed",
                    cmd=cmd,
                    time_ms=elapsed
                )
                
        except subprocess.TimeoutExpired:
            return MayaResponse(
                success=False,
                result="✗ timeout",
                time_ms=30000
            )
    
    def instant_search(self, term: str, max_results: int = 3) -> MayaResponse:
        """
        INSTANT search - no fancy formatting.
        Just package names.
        """
        start = time.time()
        
        # Check cache first for INSTANT response
        cache_key = f"search_{term}"
        if cache_key in self.cache:
            return MayaResponse(
                success=True,
                result=self.cache[cache_key],
                time_ms=0  # Instant!
            )
        
        cmd = f"nix search nixpkgs {term} --json 2>/dev/null | head -1000"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=2  # 2 seconds MAX
            )
            
            elapsed = int((time.time() - start) * 1000)
            
            if result.returncode == 0 and result.stdout:
                import json
                packages = json.loads(result.stdout)
                
                # Just package names, no descriptions
                names = []
                for name in list(packages.keys())[:max_results]:
                    pkg_name = name.split('.')[-1]
                    names.append(pkg_name)
                
                result_str = " ".join(names) if names else "✗ none"
                
                # Cache it
                self.cache[cache_key] = result_str
                
                return MayaResponse(
                    success=bool(names),
                    result=result_str,
                    time_ms=elapsed
                )
            else:
                return MayaResponse(
                    success=False,
                    result="✗ none",
                    time_ms=elapsed
                )
                
        except subprocess.TimeoutExpired:
            return MayaResponse(
                success=False,
                result="✗ slow",
                time_ms=2000
            )
        except:
            return MayaResponse(
                success=False,
                result="✗ error",
                time_ms=0
            )
    
    def list_installed(self, pattern: Optional[str] = None) -> MayaResponse:
        """
        Super fast list - just names, no versions.
        Optional grep pattern.
        """
        start = time.time()
        
        if pattern:
            cmd = f"nix-env -q | grep -i {pattern} | cut -d'-' -f1 | uniq"
        else:
            cmd = "nix-env -q | cut -d'-' -f1 | uniq | head -20"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=1  # 1 second max
            )
            
            elapsed = int((time.time() - start) * 1000)
            
            if result.returncode == 0 and result.stdout:
                # One line, space separated
                packages = result.stdout.strip().replace('\n', ' ')
                return MayaResponse(
                    success=True,
                    result=packages[:100],  # Limit length
                    time_ms=elapsed
                )
            else:
                return MayaResponse(
                    success=False,
                    result="✗ none",
                    time_ms=elapsed
                )
                
        except subprocess.TimeoutExpired:
            return MayaResponse(
                success=False,
                result="✗ slow",
                time_ms=1000
            )
    
    def quick_update(self) -> MayaResponse:
        """
        Start system update in background.
        Don't wait for it.
        """
        start = time.time()
        
        # Start update in background
        cmd = "nohup sudo nixos-rebuild switch > /tmp/maya-update.log 2>&1 &"
        
        try:
            subprocess.run(cmd, shell=True, timeout=0.1)
            
            elapsed = int((time.time() - start) * 1000)
            
            return MayaResponse(
                success=True,
                result="⚡ updating → /tmp/maya-update.log",
                cmd=cmd,
                time_ms=elapsed
            )
        except:
            return MayaResponse(
                success=False,
                result="✗ failed",
                time_ms=100
            )
    
    def multi_op(self, operations: List[Tuple[str, List[str]]]) -> List[MayaResponse]:
        """
        Execute multiple operations in PARALLEL.
        Maximum speed for ADHD workflow.
        
        Example:
            multi_op([
                ('install', ['firefox', 'vscode']),
                ('remove', ['chromium']),
                ('search', ['python'])
            ])
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for op, args in operations:
                if op == 'install':
                    future = executor.submit(self.quick_install, args)
                elif op == 'remove':
                    future = executor.submit(self.quick_remove, args)
                elif op == 'search':
                    future = executor.submit(self.instant_search, args[0] if args else '')
                elif op == 'list':
                    future = executor.submit(self.list_installed, args[0] if args else None)
                else:
                    continue
                    
                futures.append(future)
            
            # Collect results AS THEY COMPLETE (not in order)
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=5)
                    results.append(result)
                except:
                    results.append(MayaResponse(
                        success=False,
                        result="✗ timeout",
                        time_ms=5000
                    ))
        
        return results
    
    def show_shortcuts(self) -> MayaResponse:
        """Show keyboard shortcuts"""
        shortcuts_str = " ".join([f"{k}={v}" for k, v in self.shortcuts.items()])
        return MayaResponse(
            success=True,
            result=f"⚡ {shortcuts_str}",
            time_ms=0
        )
    
    def focus_mode(self, duration_minutes: int = 25) -> MayaResponse:
        """
        Pomodoro timer for ADHD focus.
        Runs in background.
        """
        cmd = f"(sleep {duration_minutes * 60} && notify-send '⏰ Break time!') &"
        
        try:
            subprocess.run(cmd, shell=True, timeout=0.1)
            return MayaResponse(
                success=True,
                result=f"⏱️ {duration_minutes}min",
                cmd=cmd,
                time_ms=0
            )
        except:
            return MayaResponse(
                success=False,
                result="✗ timer failed",
                time_ms=0
            )


class MayaCLI:
    """
    Ultra-minimal CLI for Maya Mode.
    Single letter commands for speed.
    """
    
    def __init__(self):
        self.maya = MayaMode()
        self.last_time = 0
        
    def run(self, args: List[str]):
        """Process ultra-short commands"""
        
        if not args:
            self.help()
            return
            
        cmd = args[0].lower()
        params = args[1:] if len(args) > 1 else []
        
        # Single letter commands for SPEED
        if cmd in ['i', 'install']:
            response = self.maya.quick_install(params)
        elif cmd in ['r', 'remove']:
            response = self.maya.quick_remove(params)
        elif cmd in ['s', 'search']:
            term = ' '.join(params)
            response = self.maya.instant_search(term)
        elif cmd in ['l', 'list']:
            pattern = params[0] if params else None
            response = self.maya.list_installed(pattern)
        elif cmd in ['u', 'update']:
            response = self.maya.quick_update()
        elif cmd in ['k', 'keys']:
            response = self.maya.show_shortcuts()
        elif cmd in ['f', 'focus']:
            mins = int(params[0]) if params else 25
            response = self.maya.focus_mode(mins)
        elif cmd in ['m', 'multi']:
            # Parse multi operations
            # Format: m i:ff,vs r:ch s:python
            ops = []
            for param in params:
                if ':' in param:
                    op, items = param.split(':')
                    items_list = items.split(',')
                    if op == 'i':
                        ops.append(('install', items_list))
                    elif op == 'r':
                        ops.append(('remove', items_list))
                    elif op == 's':
                        ops.append(('search', [items]))
            
            if ops:
                responses = self.maya.multi_op(ops)
                for r in responses:
                    self.show_response(r)
                return
            else:
                response = MayaResponse(False, "✗ format: m i:ff,vs r:ch")
        else:
            response = MayaResponse(False, f"✗ unknown: {cmd}")
        
        self.show_response(response)
    
    def show_response(self, response: MayaResponse):
        """Ultra-minimal output"""
        # Show result
        print(response.result, end='')
        
        # Show time if it was slow
        if response.time_ms > 1000:
            print(f" [{response.time_ms}ms]", end='')
        
        # Show command if requested (transparency)
        if response.cmd and '--show-cmd' in sys.argv:
            print(f" $ {response.cmd}", end='')
        
        print()  # Newline
        
        self.last_time = response.time_ms
    
    def help(self):
        """Ultra-compact help"""
        print("""
⚡ MAYA MODE - Lightning NixOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
i|install ff vs    Install (shortcuts work!)
r|remove ch        Remove packages
s|search term      Search (<2sec)
l|list [pattern]   List installed
u|update          Background update
k|keys            Show shortcuts
f|focus [min]     Pomodoro timer
m|multi          Parallel ops

SHORTCUTS: ff=firefox vs=vscode dc=discord sp=spotify
MULTI: m i:ff,vs r:ch s:python (parallel!)

NO WAITING. NO FLUFF. JUST SPEED.
""")


def main():
    """Maya Mode entry point"""
    import sys
    
    cli = MayaCLI()
    
    if len(sys.argv) > 1:
        # One-shot mode
        cli.run(sys.argv[1:])
    else:
        # Interactive mode (but still FAST)
        print("⚡ MAYA MODE - Type 'h' for help, 'q' to quit")
        
        while True:
            try:
                # Minimal prompt
                cmd = input("> ").strip()
                
                if cmd.lower() in ['q', 'quit', 'exit']:
                    print("⚡ bye")
                    break
                elif cmd.lower() in ['h', 'help']:
                    cli.help()
                else:
                    cli.run(cmd.split())
                    
            except KeyboardInterrupt:
                print("\n⚡ bye")
                break
            except EOFError:
                break


if __name__ == "__main__":
    main()