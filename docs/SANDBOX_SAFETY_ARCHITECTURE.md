# 🛡️ Sandbox & Safety Architecture for AI Self-Evolution

## 🎯 Goal
Enable the AI to safely modify and improve its own code without risking system integrity or introducing breaking changes.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Production System                      │
│  (Real CLI, TUI, GUI running in production)              │
└────────────────────┬───────────────────────────────────┘
                     │ Copy for modification
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Sandbox Layer                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │            1. Code Isolation                     │    │
│  │  • Docker container or VM                        │    │
│  │  • Nix shell with restricted permissions         │    │
│  │  • Temporary filesystem overlay                  │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │            2. Modification Engine                │    │
│  │  • AST-based code modifications                  │    │
│  │  • Git branch for changes                        │    │
│  │  • Rollback capability                          │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │            3. Validation System                  │    │
│  │  • Automated test suite                          │    │
│  │  • Performance benchmarks                        │    │
│  │  • Security scanning                             │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │            4. Human Review Interface             │    │
│  │  • Diff visualization                            │    │
│  │  • Impact analysis                               │    │
│  │  • Approval workflow                             │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                     │ After validation & approval
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Deployment                             │
│  • Gradual rollout                                       │
│  • Monitoring & rollback triggers                        │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Implementation Strategy

### Option 1: Docker-Based Sandbox (Recommended for Strong Isolation)

**Pros:**
- Complete filesystem isolation
- Resource limits (CPU, memory)
- Network isolation
- Easy cleanup
- Reproducible environment

**Cons:**
- Requires Docker
- Some overhead
- GUI testing more complex

**Implementation:**
```dockerfile
# Dockerfile.sandbox
FROM python:3.11-slim

# Install Nix for NixOS operations
RUN apt-get update && apt-get install -y curl xz-utils
RUN curl -L https://nixos.org/nix/install | sh

# Copy source code
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install poetry
RUN poetry install

# Restricted user
RUN useradd -m sandbox
USER sandbox

# Entry point for modifications
CMD ["python", "sandbox_runner.py"]
```

### Option 2: Nix Shell Sandbox (Native to NixOS)

**Pros:**
- Native to our NixOS environment
- Declarative and reproducible
- Good filesystem isolation with overlays
- Lightweight

**Cons:**
- Less isolation than Docker
- NixOS-specific

**Implementation:**
```nix
# sandbox-shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "ai-sandbox";
  
  buildInputs = with pkgs; [
    python311
    poetry
    git
    # Testing tools
    pytest
    black
    ruff
    bandit
  ];
  
  # Restrict network access
  __noChroot = false;
  
  # Use temporary directory
  shellHook = ''
    export SANDBOX_DIR=$(mktemp -d)
    cp -r . $SANDBOX_DIR/
    cd $SANDBOX_DIR
    echo "🛡️ Sandbox environment ready at $SANDBOX_DIR"
  '';
}
```

### Option 3: Python Virtual Environment + Git (Lightweight)

**Pros:**
- Simplest to implement
- Fast iteration
- Git provides versioning
- Works everywhere

**Cons:**
- Least isolation
- Relies on Git for safety

**Implementation:**
```python
# sandbox_manager.py
import tempfile
import shutil
import subprocess
from pathlib import Path

class SandboxManager:
    def __init__(self):
        self.sandbox_dir = None
        self.original_branch = None
    
    def create_sandbox(self):
        """Create isolated environment"""
        # Create temp directory
        self.sandbox_dir = tempfile.mkdtemp(prefix="ai_sandbox_")
        
        # Copy source code
        shutil.copytree(".", self.sandbox_dir, dirs_exist_ok=True)
        
        # Create git branch for changes
        subprocess.run(["git", "checkout", "-b", f"ai-modification-{timestamp}"], 
                      cwd=self.sandbox_dir)
        
        # Create virtual environment
        subprocess.run(["python", "-m", "venv", "venv"], 
                      cwd=self.sandbox_dir)
        
        # Install dependencies
        subprocess.run(["venv/bin/pip", "install", "-e", "."], 
                      cwd=self.sandbox_dir)
        
        return self.sandbox_dir
```

## 🛡️ Safe Modification System

### 1. Modification Request Format

```python
class ModificationRequest:
    """Standard format for AI modification requests"""
    
    def __init__(self):
        self.id = generate_uuid()
        self.timestamp = datetime.now()
        self.description = ""  # What change and why
        self.target_files = []  # Files to modify
        self.modifications = []  # AST transformations
        self.tests = []  # Tests that must pass
        self.rollback_plan = None  # How to undo
        self.risk_level = "low"  # low/medium/high
        self.requires_human_review = True
```

### 2. Validation Pipeline

```python
class ValidationPipeline:
    """Multi-stage validation for modifications"""
    
    async def validate(self, modification: ModificationRequest, sandbox_dir: Path):
        results = []
        
        # Stage 1: Syntax validation
        results.append(await self.validate_syntax(sandbox_dir))
        
        # Stage 2: Type checking
        results.append(await self.validate_types(sandbox_dir))
        
        # Stage 3: Unit tests
        results.append(await self.run_unit_tests(sandbox_dir))
        
        # Stage 4: Integration tests
        results.append(await self.run_integration_tests(sandbox_dir))
        
        # Stage 5: Performance benchmarks
        results.append(await self.run_benchmarks(sandbox_dir))
        
        # Stage 6: Security scan
        results.append(await self.security_scan(sandbox_dir))
        
        # Stage 7: Behavioral regression tests
        results.append(await self.behavioral_tests(sandbox_dir))
        
        return all(r.passed for r in results), results
```

### 3. Modification Constraints

```python
class SafetyConstraints:
    """Rules that modifications must follow"""
    
    # Files that CANNOT be modified
    IMMUTABLE_FILES = [
        "sandbox_manager.py",  # The sandbox itself
        "validation_pipeline.py",  # Validation system
        "safety_constraints.py",  # These rules
        ".git/*",  # Git history
        "*.key", "*.pem",  # Security files
    ]
    
    # Patterns that trigger automatic rejection
    FORBIDDEN_PATTERNS = [
        r"exec\(",  # No arbitrary code execution
        r"eval\(",  # No eval
        r"__import__",  # No dynamic imports
        r"subprocess.*shell=True",  # No shell injection
        r"os\.system",  # No system calls
        r"open\(.*(w|a)",  # Restricted file writing
    ]
    
    # Maximum changes per modification
    MAX_FILES_PER_CHANGE = 10
    MAX_LINES_PER_FILE = 500
    
    # Required test coverage
    MIN_TEST_COVERAGE = 0.8  # 80%
    
    # Performance constraints
    MAX_PERFORMANCE_DEGRADATION = 0.1  # 10% slower is ok
```

### 4. Human Review Interface

```python
class ReviewInterface:
    """Present modifications for human approval"""
    
    def generate_review_report(self, modification, validation_results):
        return {
            "summary": modification.description,
            "risk_assessment": self.assess_risk(modification),
            "changes": self.format_diff(modification),
            "test_results": validation_results,
            "performance_impact": self.measure_impact(validation_results),
            "recommendation": self.ai_recommendation(modification, validation_results),
            "approve_command": f"ai-mod approve {modification.id}",
            "reject_command": f"ai-mod reject {modification.id}",
        }
```

## 🚀 Complete Implementation

### Recommended Approach: Hybrid System

1. **Use Git branches** for versioning (lightweight, universal)
2. **Use Nix shell** for isolation (native to NixOS)
3. **Use Python AST** for safe modifications
4. **Use comprehensive testing** for validation

### Implementation Steps:

1. **Create the sandbox infrastructure**
2. **Build the modification engine**
3. **Implement validation pipeline**
4. **Create human review interface**
5. **Add monitoring and rollback**

## 🔬 Example: AI Self-Improvement Workflow

```python
async def ai_self_improve():
    """Complete workflow for AI self-modification"""
    
    # 1. AI identifies improvement
    improvement = ai.analyze_performance()
    # Example: "Search is slow, add caching"
    
    # 2. Create modification request
    mod_request = ModificationRequest()
    mod_request.description = "Add caching to search function"
    mod_request.target_files = ["src/luminous_nix/core/luminous_core.py"]
    mod_request.modifications = [
        AddCacheDecorator("search_packages"),
        AddImport("from functools import lru_cache"),
    ]
    
    # 3. Create sandbox
    sandbox = SandboxManager()
    sandbox_dir = sandbox.create_sandbox()
    
    # 4. Apply modifications in sandbox
    modifier = ModificationEngine()
    modifier.apply(mod_request, sandbox_dir)
    
    # 5. Validate changes
    validator = ValidationPipeline()
    passed, results = await validator.validate(mod_request, sandbox_dir)
    
    # 6. Human review (if required)
    if mod_request.requires_human_review:
        review = ReviewInterface()
        report = review.generate_review_report(mod_request, results)
        approved = await human_approval(report)
        
        if not approved:
            sandbox.cleanup()
            return False
    
    # 7. Deploy if validated
    if passed:
        deployer = SafeDeployer()
        deployer.deploy(sandbox_dir, monitoring=True)
        
        # 8. Monitor for issues
        monitor = PerformanceMonitor()
        if monitor.detect_regression():
            deployer.rollback()
    
    # 9. Cleanup
    sandbox.cleanup()
    return True
```

## 🎯 Safety Guarantees

1. **No production changes without validation**
2. **All changes are reversible**
3. **Human approval for risky changes**
4. **Automatic rollback on regression**
5. **Complete audit trail**
6. **Resource limits enforced**
7. **Security scanning mandatory**

## 📊 Risk Matrix

| Change Type | Risk | Human Review | Examples |
|------------|------|--------------|----------|
| Add comment | Low | No | Documentation |
| Add logging | Low | No | Debug output |
| Refactor function | Medium | Optional | Code cleanup |
| Add new feature | Medium | Yes | New command |
| Modify core logic | High | Required | Algorithm change |
| Change security | Critical | Required + 2FA | Auth, crypto |

## 🌟 Benefits of This Approach

1. **Safe** - Multiple layers of protection
2. **Transparent** - All changes tracked and reviewable
3. **Reversible** - Easy rollback at any point
4. **Gradual** - Can start simple, add layers
5. **Educational** - AI learns from rejections
6. **Auditable** - Complete history maintained

## 🚦 Getting Started

The simplest path to start:

1. Implement Git-based sandbox (Option 3)
2. Add basic validation (syntax + tests)
3. Require human approval for all changes
4. Gradually reduce human involvement as confidence grows
5. Add more sophisticated isolation as needed

This provides immediate value with low complexity, and can evolve to stronger guarantees over time.