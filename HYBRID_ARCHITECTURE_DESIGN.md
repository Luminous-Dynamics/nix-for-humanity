# Hybrid Architecture Design for Luminous Nix

## Vision

A three-layer architecture that combines Python's AI capabilities with Rust's performance and safety, while leveraging NixOS 25.11's improvements for optimal system integration.

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    USER LAYER                        │
├───────────────┬──────────────┬───────────────────────┤
│      CLI      │     TUI      │    Voice (Future)     │
│   (Python)    │  (Textual)   │  (Whisper/Piper)     │
└───────────────┴──────────────┴───────────────────────┘
                        │
┌──────────────────────────────────────────────────────┐
│                 INTELLIGENCE LAYER                    │
├───────────────────────────────────────────────────────┤
│  • HRM Neural Network (PyTorch)                      │
│  • Specialist Modules (Python)                       │
│  • Learning System (RL/Active)                       │
│  • Ollama Integration (Fallback)                     │
└──────────────────────────────────────────────────────┘
                        │
┌──────────────────────────────────────────────────────┐
│               OPTIMIZATION LAYER                      │
├─────────────────────┬─────────────────────────────────┤
│   Python (Fast)     │     Rust (Blazing)            │
├─────────────────────┼─────────────────────────────────┤
│ • JSON Processing   │ • Package Search (mmap)        │
│ • SQLite Cache      │ • Expression Validator         │
│ • Async Operations  │ • Dependency Resolver          │
│ • Batch Commands    │ • Secure Secrets               │
└─────────────────────┴─────────────────────────────────┘
                        │
┌──────────────────────────────────────────────────────┐
│                  SYSTEM LAYER                        │
├───────────────────────────────────────────────────────┤
│  • nixos-rebuild-ng (when available)                 │
│  • Nix commands with --json                          │
│  • Direct file operations                            │
└──────────────────────────────────────────────────────┘
```

## Component Distribution

### Python Components (60%)
```python
luminous_nix/
├── cli/                 # User interfaces
│   ├── main.py          # Click-based CLI
│   └── completions.py   # Shell completions
├── ui/                  # TUI components
│   ├── app.py           # Textual application
│   └── widgets.py       # Custom widgets
├── ai/                  # Intelligence
│   ├── hrm_model.py     # PyTorch neural network
│   ├── specialists/     # Domain experts
│   ├── learning.py      # RL/Active learning
│   └── ollama.py        # LLM fallback
├── core/                # Business logic
│   ├── orchestrator.py  # Request routing
│   ├── cache.py         # SQLite/memory cache
│   └── config.py        # Configuration
└── adapters/            # External interfaces
    ├── nix.py           # Subprocess wrapper
    └── rust_native.py   # Rust bindings
```

### Rust Components (20%)
```rust
nix_native/src/
├── lib.rs               # PyO3 module definition
├── search/              # Fast package search
│   ├── index.rs         # Memory-mapped index
│   └── trie.rs          # Prefix tree search
├── security/            # Security-critical
│   ├── validator.rs     # Expression validation
│   ├── secrets.rs       # Secure string handling
│   └── sandbox.rs       # Sandboxed execution
├── performance/         # Speed-critical
│   ├── cache.rs         # Lock-free cache
│   ├── resolver.rs      # Dependency graphs
│   └── parallel.rs      # Concurrent operations
└── system/              # System operations
    ├── profile.rs       # Atomic switching
    └── store.rs         # Nix store access
```

### System Integration (20%)
```bash
# Leveraging NixOS 25.11 features
- nixos-rebuild-ng (when available)
- JSON output everywhere
- Parallel nix operations
- Direct store access (read-only)
```

## Implementation Phases

### Phase 1: JSON Optimization (Week 3, Current)
**Goal**: 10x performance improvement without new dependencies

```python
# Before: Parse text output (slow, fragile)
result = subprocess.run(["nix", "search", query], text=True)
# Complex regex parsing...

# After: Structured data (fast, reliable)
result = subprocess.run(["nix", "search", query, "--json"], text=True)
packages = json.loads(result.stdout)  # Direct access!
```

**Tasks**:
1. Convert all Nix commands to use `--json`
2. Implement proper SQLite caching
3. Add batch operations for multiple queries
4. Profile and measure improvements

### Phase 2: Rust Foundation (Week 4)
**Goal**: Build Rust module infrastructure

```bash
# Create Rust module
cd luminous-nix
cargo init --lib nix_native
maturin init

# Basic structure
nix_native/
├── Cargo.toml
├── pyproject.toml
└── src/
    └── lib.rs
```

**Tasks**:
1. Setup PyO3 bindings
2. Create Python fallback pattern
3. Build CI/CD for Rust
4. Test cross-platform builds

### Phase 3: Security Components (Week 5)
**Goal**: Eliminate security vulnerabilities

```rust
// Priority: Prevent injection attacks
#[pyfunction]
fn validate_nix_expr(expr: &str) -> PyResult<ValidationResult> {
    // Check for dangerous patterns
    // Validate syntax without eval
    // Return safe AST representation
}

// Priority: Secure secrets
#[pyclass]
struct SecureString {
    // Pinned memory that's zeroed on drop
}
```

**Tasks**:
1. Expression validator
2. Secure string implementation
3. Path traversal prevention
4. Security test suite

### Phase 4: Performance Components (Week 6)
**Goal**: 1000x search performance

```rust
// Memory-mapped package index
#[pyclass]
struct PackageIndex {
    mmap: Mmap,
    trie: PackageTrie,
}

#[pymethods]
impl PackageIndex {
    fn search(&self, query: &str) -> Vec<Package> {
        // Sub-millisecond search
    }
}
```

**Tasks**:
1. Package search engine
2. Dependency resolver
3. Lock-free cache
4. Performance benchmarks

## Integration Patterns

### Python → Rust Fallback Pattern
```python
class NixSearchService:
    def __init__(self):
        self.rust_available = self._try_import_rust()
    
    def _try_import_rust(self):
        try:
            import nix_native
            self.rust = nix_native
            return True
        except ImportError:
            return False
    
    def search(self, query: str) -> List[Package]:
        if self.rust_available:
            # Fast path: Rust
            return self.rust.fast_search(query)
        else:
            # Fallback: Subprocess
            return self._subprocess_search(query)
```

### Rust → Python Callback Pattern
```rust
// Allow Python callbacks in Rust
#[pyfunction]
fn process_with_callback(data: Vec<String>, callback: PyObject) -> PyResult<()> {
    Python::with_gil(|py| {
        for item in data {
            callback.call1(py, (item,))?;
        }
        Ok(())
    })
}
```

### Async Integration Pattern
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class HybridExecutor:
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
    
    async def fast_operation(self, query):
        # Run Rust in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_pool,
            nix_native.fast_search,
            query
        )
```

## Performance Targets

### Current Baseline (v0.3.1)
| Operation | Time | Method |
|-----------|------|--------|
| Search | 2-3s | Subprocess |
| Install | 5-30s | Subprocess |
| Cache Hit | 0.1ms | Memory |
| Neural Network | 3.7ms | PyTorch |

### Phase 1 Target (JSON + Cache)
| Operation | Time | Improvement |
|-----------|------|-------------|
| Search | 200-500ms | 10x |
| Install | 5-30s | Same |
| Cache Hit | 0.01ms | 10x |
| Neural Network | 3.7ms | Same |

### Phase 4 Target (Full Hybrid)
| Operation | Time | Improvement |
|-----------|------|-------------|
| Search | 2-10ms | 1000x |
| Install | 5-30s | Same |
| Cache Hit | 1μs | 100x |
| Neural Network | 3.7ms | Same |
| Validation | 0.5ms | New |

## Distribution Strategy

### 1. Pure Python (PyPI)
```bash
pip install luminous-nix
# Works everywhere, Rust extensions optional
```

### 2. With Rust (Wheels)
```bash
pip install luminous-nix[native]
# Pre-built wheels with Rust extensions
```

### 3. NixOS Package
```nix
{ pkgs }:
pkgs.python3Packages.buildPythonApplication {
  pname = "luminous-nix";
  # Includes Rust components
  nativeBuildInputs = [ pkgs.rustc pkgs.cargo ];
}
```

### 4. Standalone Binary
```bash
# PyOxidizer bundle with everything
./luminous-nix-standalone
```

## Migration Path

### From Current (v0.3.1) to Hybrid

1. **No Breaking Changes**: All current features continue working
2. **Progressive Enhancement**: Rust components activate when available
3. **Graceful Degradation**: Falls back to Python when Rust unavailable
4. **Opt-in Performance**: Users choose when to install native extensions

### Code Migration Example
```python
# Current (v0.3.1)
def search_packages(query):
    result = subprocess.run(["nix", "search", query])
    return parse_text_output(result.stdout)

# Hybrid (v0.4.0)
def search_packages(query):
    # Try fast path
    if RUST_AVAILABLE:
        return nix_native.fast_search(query)
    
    # Try JSON (10x faster)
    result = subprocess.run(["nix", "search", query, "--json"])
    if result.returncode == 0:
        return json.loads(result.stdout)
    
    # Final fallback
    return parse_text_output(result.stdout)
```

## Risk Mitigation

### Technical Risks
1. **Rust compilation complexity**: Pre-build wheels for common platforms
2. **Cross-platform issues**: Extensive CI/CD testing
3. **API stability**: Version lock Rust/Python interfaces
4. **Performance regression**: Comprehensive benchmarks

### Mitigation Strategies
1. **Feature flags**: Enable/disable Rust per component
2. **Gradual rollout**: Start with search, expand slowly
3. **Fallback always**: Never require Rust
4. **Clear documentation**: Performance expectations

## Success Metrics

### Phase 1 (Week 3)
- [ ] All commands use `--json`: 10x faster
- [ ] SQLite cache working: 90% hit rate
- [ ] No new dependencies required
- [ ] All tests passing

### Phase 2 (Week 4)
- [ ] Rust module compiles
- [ ] PyO3 bindings work
- [ ] Fallback pattern tested
- [ ] CI/CD building wheels

### Phase 3 (Week 5)
- [ ] Expression validator complete
- [ ] Security tests passing
- [ ] No injection vulnerabilities
- [ ] Secrets properly handled

### Phase 4 (Week 6)
- [ ] Search <10ms
- [ ] Cache <1μs
- [ ] 1000x improvement verified
- [ ] v0.4.0 released

## Conclusion

This hybrid architecture gives us:
1. **Best of Both Worlds**: Python's AI + Rust's performance
2. **Security First**: Rust eliminates entire vulnerability classes
3. **Progressive Enhancement**: Works everywhere, fast where possible
4. **Future Proof**: Ready for NixOS 25.11 and beyond

The key insight: We don't need to rewrite everything. Strategic use of Rust where it matters most (security and performance hotspots) while keeping Python's incredible AI ecosystem gives us a 1000x improvement where users feel it most, without sacrificing any functionality.

---

*"The best architecture is invisible to the user. They just experience magic."*