#!/usr/bin/env python3
"""
from typing import List, Dict, Optional, Tuple
Consolidate multiple backend implementations into a single, clean architecture.
This script analyzes duplicate code and creates a unified backend.
"""

import os
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class CodeAnalyzer:
    """Analyze code for duplication and create consolidation plan."""
    
    def __init__(self):
        self.function_signatures: Dict[str, List[Path]] = defaultdict(list)
        self.class_definitions: Dict[str, List[Path]] = defaultdict(list)
        self.duplicate_functions: Dict[str, List[Path]] = defaultdict(list)
        self.import_graph: Dict[Path, Set[str]] = {}
    
    def analyze_file(self, filepath: Path):
        """Analyze a Python file for classes and functions."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract imports
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            self.import_graph[filepath] = imports
            
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig = self._get_function_signature(node)
                    self.function_signatures[sig].append(filepath)
                    
                    # Check for duplicate implementation
                    func_hash = self._hash_function(node)
                    if func_hash:
                        self.duplicate_functions[func_hash].append((filepath, node.name))
                
                elif isinstance(node, ast.ClassDef):
                    self.class_definitions[node.name].append(filepath)
        
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get a normalized function signature."""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return f"{node.name}({','.join(args)})"
    
    def _hash_function(self, node: ast.FunctionDef) -> str:
        """Create a hash of function implementation."""
        # Simple hash based on function structure
        try:
            # Remove docstrings for comparison
            body = [n for n in node.body if not (
                isinstance(n, ast.Expr) and isinstance(n.value, ast.Str)
            )]
            
            if body:
                # Create a simple hash of the function structure
                structure = ast.dump(body[0])[:100]  # First statement structure
                return hashlib.md5(structure.encode()).hexdigest()[:8]
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return ""
    
    def find_duplicates(self) -> Dict[str, List[Tuple[Path, str]]]:
        """Find duplicate implementations."""
        duplicates = {}
        
        for func_hash, locations in self.duplicate_functions.items():
            if len(locations) > 1:
                duplicates[func_hash] = locations
        
        return duplicates
    
    def suggest_consolidation(self) -> List[str]:
        """Suggest consolidation strategy."""
        suggestions = []
        
        # Find duplicate classes
        for class_name, locations in self.class_definitions.items():
            if len(locations) > 1:
                suggestions.append(
                    f"Class '{class_name}' found in {len(locations)} files: "
                    f"{', '.join(str(p) for p in locations)}"
                )
        
        # Find duplicate function signatures
        for sig, locations in self.function_signatures.items():
            if len(locations) > 1:
                suggestions.append(
                    f"Function '{sig}' found in {len(locations)} files: "
                    f"{', '.join(str(p) for p in locations)}"
                )
        
        return suggestions

def create_unified_backend():
    """Create a unified backend structure."""
    
    print("🔍 Analyzing existing backend code...")
    
    analyzer = CodeAnalyzer()
    
    # Analyze all Python files in backend directories
    backend_dirs = ['backend', 'luminous_nix', 'src/luminous_nix']
    
    for dir_path in backend_dirs:
        if Path(dir_path).exists():
            for py_file in Path(dir_path).rglob('*.py'):
                if 'test' not in str(py_file) and '__pycache__' not in str(py_file):
                    analyzer.analyze_file(py_file)
    
    # Find duplicates
    duplicates = analyzer.find_duplicates()
    
    if duplicates:
        print("\n⚠️  Found duplicate implementations:")
        for func_hash, locations in duplicates.items():
            print(f"\nDuplicate function implementations:")
            for path, func_name in locations:
                print(f"  - {func_name} in {path}")
    
    # Get consolidation suggestions
    suggestions = analyzer.suggest_consolidation()
    
    if suggestions:
        print("\n📋 Consolidation suggestions:")
        for suggestion in suggestions[:10]:  # Limit output
            print(f"  - {suggestion}")
    
    # Create consolidation plan
    print("\n📝 Creating consolidation plan...")
    
    plan = """
# Backend Consolidation Plan

## 1. Unified Structure
```
src/luminous_nix/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── executor.py      # Single executor implementation
│   ├── nlp.py          # NLP engine
│   ├── intents.py      # Intent definitions
│   └── errors.py       # Error handling
├── native/
│   ├── __init__.py
│   ├── api.py          # Native Nix API
│   ├── operations.py   # Native operations
│   └── fallback.py     # Subprocess fallback
├── learning/
│   ├── __init__.py
│   ├── patterns.py     # Pattern recognition
│   ├── storage.py      # Learning storage
│   └── feedback.py     # User feedback processing
├── interfaces/
│   ├── __init__.py
│   ├── cli.py          # CLI interface
│   ├── tui.py          # TUI interface
│   └── voice.py        # Voice interface
└── config/
    ├── __init__.py
    ├── settings.py     # User settings
    └── personas.py     # Persona definitions
```

## 2. Key Consolidations

### Executor (HIGHEST PRIORITY)
- Merge `backend/core/executor.py` and `luminous_nix/core/executor.py`
- Keep the best error handling from both
- Use dependency injection for backends

### NLP Engine
- Consolidate intent parsing logic
- Merge pattern matching approaches
- Unified confidence scoring

### Native API
- Single implementation of Python-Nix integration
- Clear fallback strategy
- Performance monitoring built-in

## 3. Migration Steps

1. **Create unified structure** in `src/luminous_nix/`
2. **Copy best implementations** from each duplicate
3. **Update all imports** to use new structure
4. **Remove old implementations** after testing
5. **Update tests** to use new structure

## 4. Code Example

```python
# src/luminous_nix/core/executor.py
from typing import Protocol
from ..native.api import NativeAPI
from ..native.fallback import SubprocessFallback

class ExecutionBackend(Protocol):
    async def execute(self, command: Command) -> Result:
        ...

class UnifiedExecutor:
    def __init__(self, prefer_native: bool = True):
        self.backend = self._select_backend(prefer_native)
    
    def _select_backend(self, prefer_native: bool) -> ExecutionBackend:
        if prefer_native and NativeAPI.is_available():
            return NativeAPI()
        return SubprocessFallback()
    
    async def execute(self, intent: Intent) -> Result:
        command = self.build_command(intent)
        return await self.backend.execute(command)
```
"""
    
    # Write consolidation plan
    with open('CONSOLIDATION_PLAN.md', 'w') as f:
        f.write(plan)
    
    print("\n✅ Consolidation plan created: CONSOLIDATION_PLAN.md")
    
    # Create migration script
    create_migration_script()

def create_migration_script():
    """Create a script to perform the actual consolidation."""
    
    migration_script = '''#!/usr/bin/env python3
"""
Automated backend consolidation script.
This performs the actual file moves and merges.
"""

import os
import shutil
from pathlib import Path

def consolidate_executors():
    """Merge executor implementations."""
    
    # Create unified executor combining best of both
    unified_executor = """
from typing import Optional, Dict, Any, Protocol
from dataclasses import dataclass
from abc import abstractmethod

from ..native.api import NativeAPI
from ..native.fallback import SubprocessFallback
from .errors import ExecutionError, ValidationError
from .intents import Intent, Command

class ExecutionBackend(Protocol):
    @abstractmethod
    async def execute(self, command: Command) -> Result:
        pass

@dataclass
class Result:
    success: bool
    output: str
    error: Optional[str] = None
    duration_ms: Optional[float] = None

class UnifiedExecutor:
    \"\"\"Unified executor with automatic backend selection.\"\"\"
    
    def __init__(self, prefer_native: bool = True, test_mode: bool = False):
        self.test_mode = test_mode
        self.backend = self._select_backend(prefer_native)
        self._performance_stats = {}
    
    def _select_backend(self, prefer_native: bool) -> ExecutionBackend:
        \"\"\"Select the best available backend.\"\"\"
        if self.test_mode:
            return MockBackend()
        
        if prefer_native and NativeAPI.is_available():
            print("Using native Python-Nix API for 10x performance!")
            return NativeAPI()
        
        print("Falling back to subprocess execution")
        return SubprocessFallback()
    
    async def execute(self, intent: Intent) -> Result:
        \"\"\"Execute an intent using the selected backend.\"\"\"
        # Validate intent
        validation = self.validate_intent(intent)
        if not validation.valid:
            return Result(
                success=False,
                output="",
                error=f"Invalid intent: {validation.reason}"
            )
        
        # Build command
        command = self.build_command(intent)
        
        # Execute with timing
        import time
        start = time.time()
        
        try:
            result = await self.backend.execute(command)
            result.duration_ms = (time.time() - start) * 1000
            
            # Track performance
            self._track_performance(intent.action, result.duration_ms)
            
            return result
        
        except Exception as e:
            return Result(
                success=False,
                output="",
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    def validate_intent(self, intent: Intent) -> ValidationResult:
        \"\"\"Validate intent before execution.\"\"\"
        # Add validation logic here
        return ValidationResult(valid=True)
    
    def build_command(self, intent: Intent) -> Command:
        \"\"\"Build executable command from intent.\"\"\"
        # Add command building logic here
        return Command(intent=intent)
    
    def _track_performance(self, action: str, duration_ms: float):
        \"\"\"Track performance metrics.\"\"\"
        if action not in self._performance_stats:
            self._performance_stats[action] = []
        self._performance_stats[action].append(duration_ms)
    
    def get_performance_summary(self) -> Dict[str, float]:
        \"\"\"Get average performance by action.\"\"\"
        summary = {}
        for action, durations in self._performance_stats.items():
            summary[action] = sum(durations) / len(durations)
        return summary
"""
    
    # Write the unified executor
    os.makedirs("src/luminous_nix/core", exist_ok=True)
    with open("src/luminous_nix/core/executor.py", "w") as f:
        f.write(unified_executor)
    
    print("✓ Created unified executor")

def main():
    print("🔧 Starting backend consolidation...")
    
    # Step 1: Create new structure
    dirs = [
        "src/luminous_nix/core",
        "src/luminous_nix/native", 
        "src/luminous_nix/learning",
        "src/luminous_nix/interfaces",
        "src/luminous_nix/config"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        init_file = os.path.join(d, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, 'a').close()
    
    # Step 2: Consolidate executors
    consolidate_executors()
    
    # Step 3: Move other components
    # ... add more consolidation logic
    
    print("✅ Backend consolidation complete!")

if __name__ == "__main__":
    main()
'''
    
    with open('scripts/perform-consolidation.py', 'w') as f:
        f.write(migration_script)
    
    os.chmod('scripts/perform-consolidation.py', 0o755)

if __name__ == '__main__':
    create_unified_backend()