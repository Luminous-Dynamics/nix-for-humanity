# Luminous Nix: Developer's Quick-Start for Complexity Implementation

**Purpose**: Guide for developers implementing advanced multi-step operations  
**Target Complexity**: Levels 4-5 (complex multi-step with branching and expert operations)

---

## Quick Assessment: Where We Are

```
CURRENT STATE (As of Dec 2, 2025)
├── Level 1: Simple Operations ✅ WORKING
│   └── install, search, list (1-3 seconds, 95%+ success)
│
├── Level 2: Multi-Step Templates ✅ WORKING
│   └── 3+ hardcoded plans (python dev env, web server, gaming)
│
├── Level 3: Config Generation 🚧 PARTIAL
│   └── 50+ modules, conflicts detected, limited scope
│
├── Level 4: Complex Workflows 🚧 EXPERIMENTAL
│   ├── POML orchestration defined (not integrated)
│   ├── Flake migration analysis (not execution)
│   └── No dynamic workflow generation
│
└── Level 5: Expert Operations ❌ MOSTLY STUBS
    ├── Performance profiler (no real profiling)
    ├── Security auditor (no real auditing)
    ├── Config optimizer (no implementation)
    ├── Rollback intelligence ✅ (only thing that works)
    └── 12 other features (various stub states)
```

---

## Implementation Roadmap: 3-Month Path to Expert Capability

### MONTH 1: Foundation Wiring
**Goal**: Connect architecture pieces that exist but don't talk to each other

#### Week 1-2: Complete Intent-to-Feature Router
**Files to modify**: `ai_orchestrator.py`, `intent_pipeline.py`

```python
# Current: Intent recognized → executor called
# Goal: Intent recognized → route to advanced features OR executor

def route_intent_to_handler(intent: Intent) -> ExecutionPlan:
    """Route intent to appropriate handler"""
    
    # Multi-intent operations
    if intent.tags.contains(CONFIGURE_SYSTEM) and intent.tags.contains(OPTIMIZE):
        return ExecutionPlan([
            ConfigGenerator().generate(intent.description),
            PerformanceProfiler().analyze(),
            SecurityAuditor().audit(),
            RollbackIntelligence().analyze(),
        ])
    
    # Single-intent operations
    if intent.type == MANAGE_FLAKE:
        return ExecutionPlan([
            FlakeMigrationAssistant().analyze(),
            FlakeMigrationAssistant().execute(),
        ])
    
    # Default: simple executor
    return ExecutionPlan([SafeExecutor().execute(intent)])
```

**Testing**: Create 5 test cases with multiple intents
- "Setup Python dev environment with security hardening"
- "Optimize boot and reduce disk usage"
- "Migrate to flakes and audit security"

#### Week 2-3: Implement ExecutionPlan Class
**New file**: `core/execution_plan.py`

```python
class ExecutionStep:
    handler: Callable  # Function to execute
    parameters: Dict
    dependencies: List[str]  # Which steps must run first
    parallelizable: bool
    estimated_time: float
    
class ExecutionPlan:
    steps: List[ExecutionStep]
    
    def execute(self):
        # Topological sort by dependencies
        # Execute sequentially or parallel groups
        # Handle errors with recovery
        # Track state throughout
```

**Key insight**: Dependency graph is already in place (`dependency_resolver.py`), reuse it.

#### Week 3-4: State Tracking During Execution
**Files to modify**: `conversation_state.py`, create `execution_state.py`

```python
class ExecutionState:
    plan_id: str
    current_step: int
    completed_steps: List[StepResult]
    failed_steps: List[StepFailure]
    context: Dict[str, Any]  # Shared between steps
    
    def step_completed(self, step_name, result):
        # Save result
        # Update context for next steps
        # Check for breakpoints
        
    def rollback(self):
        # Use RollbackIntelligence to find safe point
        # Execute rollback commands
```

---

### MONTH 2: Expert Feature Implementation
**Goal**: Transform stubs into functional expert operations

#### Week 1: Performance Profiler → Real Implementation
**Current**: `performance_profiler.py` has methods that don't work  
**Goal**: Actually measure and optimize

```python
class PerformanceProfiler:
    def profile_rebuild(self) -> PerformanceAnalysis:
        # Step 1: Get current performance
        start = time.time()
        result = subprocess.run(['nixos-rebuild', 'build', '--show-trace'], 
                               capture_output=True)
        elapsed = time.time() - start
        
        # Step 2: Parse build logs
        # (nixos-rebuild supports --log-format internal-json)
        phases = self._parse_build_log(result.stderr)
        # Returns: {setup: 0.5s, patch: 1.2s, build: 45.3s, ...}
        
        # Step 3: Identify bottleneck
        slowest = max(phases.items(), key=lambda x: x[1])
        
        # Step 4: Generate suggestions
        suggestions = self._suggest_optimizations(slowest)
        # "Build step is slow: use ccache", "parallel builds: -j8", etc
        
        return PerformanceAnalysis(phases, suggestions, slowest)
```

**Integration with ExecutionPlan**:
```python
ExecutionPlan([
    ConfigGenerator().generate("web server"),
    PerformanceProfiler().profile_rebuild(),  # Measure new config
    PerformanceProfiler().suggest_optimizations(),  # Get improvements
    ConfigGenerator().apply_optimizations(),  # Apply suggestions
    PerformanceProfiler().profile_rebuild(),  # Verify improvement
])
```

#### Week 2: Security Auditor → Real Implementation
**Current**: Stubs for SSL, firewall, permissions  
**Goal**: Actually run security checks

```python
class SecurityAuditor:
    def audit_system(self) -> SecurityAuditResult:
        findings = []
        
        # Check 1: Firewall rules
        firewall = subprocess.run(
            ['nix-shell', '-p', 'iptables', '--run', 'iptables -L'],
            capture_output=True, text=True
        )
        if 'INPUT DROP' not in firewall.stdout:
            findings.append(Finding(
                category='firewall',
                severity='medium',
                message='Default INPUT policy should be DROP'
            ))
        
        # Check 2: SSH hardening
        config = Path('/etc/nixos/configuration.nix').read_text()
        if 'PermitRootLogin' not in config:
            findings.append(Finding(
                category='ssh',
                severity='high',
                message='PermitRootLogin should be explicitly disabled'
            ))
        
        # Check 3: SSL/TLS (if web services present)
        if self._has_web_server(config):
            # Check SSL configuration
            # Suggest: minimum TLS 1.2, strong ciphers
            pass
        
        # Check 4: Package permissions
        packages = self._parse_installed_packages(config)
        suspicious = self._check_suspicious_packages(packages)
        findings.extend(suspicious)
        
        return SecurityAuditResult(
            total_findings=len(findings),
            by_severity={'critical': 2, 'high': 5, 'medium': 12},
            findings=findings,
            recommendations=self._prioritize_recommendations(findings)
        )
```

#### Week 3: Config Optimizer → Implementation
**Current**: No implementation  
**Goal**: Suggest and apply modularization

```python
class ConfigOptimizer:
    def suggest_refactoring(self) -> RefactoringPlan:
        config = Path('/etc/nixos/configuration.nix').read_text()
        
        # Identify semantic sections
        sections = self._identify_sections(config)
        # Returns: {boot: 30 lines, services: 150 lines, users: 20 lines}
        
        # Suggest modularization
        suggestions = []
        for section, lines in sections.items():
            if lines > 50:
                suggestions.append(
                    f"Module '{section}' ({lines} lines) could be split to modules/{section}.nix"
                )
        
        # Generate module files
        modules = self._generate_modules(config, sections)
        # Returns: {boot.nix: content, services.nix: content, ...}
        
        return RefactoringPlan(
            suggestions=suggestions,
            modules=modules,
            # New configuration.nix that imports all modules
            new_config=self._generate_imports(modules.keys())
        )
```

#### Week 4: Integration Testing
**New file**: `tests/test_complex_operations.py`

```python
def test_full_web_server_pipeline():
    """Test: Configure web server with security + performance optimization"""
    
    plan = ExecutionPlan([
        ConfigGenerator().generate("web server with high performance"),
        PerformanceProfiler().profile_rebuild(),
        SecurityAuditor().audit_system(),
        ConfigOptimizer().suggest_refactoring(),
    ])
    
    result = plan.execute()
    
    assert result.all_steps_completed
    assert result.security_findings < 5  # Should fix major issues
    assert result.performance_improved > 1.1  # At least 10% faster
```

---

### MONTH 3: Learning & Adaptation
**Goal**: System improves over time

#### Week 1-2: Correction Learning System
**New file**: `core/learning_system.py`

```python
class LearningSystem:
    def capture_correction(self, 
                          original_query: str,
                          original_response: str,
                          user_correction: str):
        """Learn from user corrections"""
        
        # Store correction
        self.corrections_db.save({
            'query': original_query,
            'original_response': original_response,
            'correction': user_correction,
            'timestamp': datetime.now(),
            'extracted_patterns': self._extract_patterns(user_correction)
        })
        
        # Immediate: update intent patterns
        if 'package not found' in user_correction:
            self._update_package_search_patterns()
        
        if 'config syntax error' in user_correction:
            self._update_config_generation_patterns()
    
    def batch_retraining(self):
        """Monthly: retrain models on accumulated corrections"""
        corrections = self.corrections_db.get_all()
        
        # For HRM: retrain on corrected examples
        training_data = [(c['query'], c['correction']) 
                        for c in corrections]
        self.hrm.retrain(training_data)
        
        # For patterns: update intent recognition
        self._update_intent_patterns(corrections)
```

#### Week 2-3: Adaptive Step Generation
**Files to modify**: `advanced_features.py` (MultiStepPlanner)

```python
class AdaptiveMultiStepPlanner:
    def create_adaptive_plan(goal: str) -> ExecutionPlan:
        """Generate plan, adapting based on execution feedback"""
        
        # Start with base plan
        plan = self._create_base_plan(goal)
        
        # Execute step by step, adapting
        for step in plan.steps:
            result = step.execute()
            
            if result.success:
                # Continue normally
                continue
            elif result.recoverable:
                # Add recovery step
                recovery = self._generate_recovery(step, result.error)
                plan.insert_step(recovery)
            else:
                # Stop and ask user
                correction = self._ask_user(result.error)
                self.learning_system.capture_correction(
                    step.description, 
                    result.error,
                    correction
                )
                break
```

#### Week 3-4: Constraint Satisfaction
**New file**: `core/constraint_solver.py`

```python
class ConstraintSolver:
    def solve(goal: str, constraints: Dict[str, Any]) -> OptimalPlan:
        """Solve multi-step planning with constraints"""
        
        # Variables: all possible steps
        steps = self._identify_candidate_steps(goal)
        
        # Domains: which steps are valid
        domains = self._compute_domains(steps, constraints)
        
        # Constraints
        constraints_list = [
            # Dependency constraints
            Constraint(step1, '<', step2),  # step1 must run before step2
            
            # Resource constraints
            Constraint(total_time, '<=', 300),  # Max 5 minutes
            Constraint(disk_space, '<=', 50 * GB),
            
            # Quality constraints
            Constraint(security_findings, '<=', 5),
            Constraint(performance_improvement, '>=', 1.1),
        ]
        
        # Solve using backtracking or SMT solver
        solution = self._solve_csp(steps, domains, constraints_list)
        
        return OptimalPlan(solution.assignments)
```

---

## Quick Reference: Files to Create/Modify

### New Files to Create
```
core/
├── execution_plan.py         # ExecutionPlan + ExecutionStep classes
├── execution_state.py        # Track execution progress
├── learning_system.py        # Learn from corrections
├── constraint_solver.py      # CSP solver for multi-step planning

tests/
├── test_complex_operations.py  # Integration tests for full pipelines

agents/
├── performance_agent.py      # Activatable performance optimization
├── security_agent.py         # Activatable security hardening
├── refactoring_agent.py      # Activatable config refactoring
```

### Files to Significantly Modify
```
ai_orchestrator.py           # Route to advanced features
intent_pipeline.py           # Extract tags for multi-intent detection
advanced_features.py         # Add adaptive planning
conversation_state.py        # Track execution context
```

### Files Mostly Working (Just Need Wiring)
```
performance_profiler.py      # → Implement real profiling
security_auditor.py          # → Implement real auditing
flake_migration.py           # → Implement migration execution
dev_environment.py           # → Complete environment generation
```

---

## Testing Strategy: Each Level

### Level 1: Already Tested ✅

### Level 2: Simple Multi-Step
```python
def test_python_dev_environment():
    plan = MultiStepPlanner().create_plan("python dev environment")
    assert len(plan.steps) >= 5
    assert plan.risk_level in ['low', 'medium']
    # Execute would fail without actual system, so:
    assert plan.estimated_time > 60  # Should take time
```

### Level 3: Config Generation
```python
def test_web_server_config():
    config = ConfigGenerator().generate("web server")
    assert 'nginx' in config
    assert 'ssl' in config or 'tls' in config
    # Validate Nix syntax
    assert self._is_valid_nix(config)
```

### Level 4: Complex Workflows
```python
def test_flake_migration():
    analysis = FlakeMigrationAssistant().analyze_migration()
    assert analysis.complexity in ['trivial', 'moderate', 'complex']
    assert analysis.confidence > 0.5
    # Validate generated flake
    assert 'inputs' in analysis.flake_nix
    assert 'outputs' in analysis.flake_nix
```

### Level 5: Expert Operations
```python
def test_performance_optimization():
    profile = PerformanceProfiler().profile_rebuild()
    assert profile.phases is not None
    assert profile.slowest_phase is not None
    assert len(profile.suggestions) > 0
    
def test_security_audit():
    audit = SecurityAuditor().audit_system()
    # Should always find something (never perfect)
    assert len(audit.findings) > 0
```

---

## Deployment Checklist

Before releasing a level, verify:

```
[ ] Unit tests pass (pytest tests/)
[ ] Integration tests pass
[ ] No regressions in earlier levels
[ ] Error handling covers edge cases
[ ] Documentation updated
[ ] Examples added to tutorial
[ ] Performance acceptable (< 5min for complex ops)
[ ] Rollback always possible
[ ] User feedback mechanism in place
```

---

## Common Pitfalls to Avoid

1. **Don't hardcode paths** - Use `Path()` and check existence
2. **Don't assume success** - Always wrap subprocess calls in try/except
3. **Don't skip rollback** - Every operation should be reversible
4. **Don't ignore user context** - Use `ConversationState` to track preferences
5. **Don't create monolithic steps** - Keep steps atomic and reusable
6. **Don't block on slow operations** - Use async for long-running tasks
7. **Don't ignore learning** - Capture corrections for model improvement

---

## Questions? Check These Files First

- Architecture overview → `COMPLEXITY_HANDLING_ANALYSIS.md`
- Intent types → `core/intent_pipeline.py` (Intent enum)
- Advanced features → `ai/advanced_features/` (16 modules)
- Execution examples → `tests/` (once created)
- POML orchestration → `poml/orchestrations/multi_step_diagnostic.poml`

---

**Expected Timeline**: 3 months to full expert-level capability  
**Estimated Effort**: 400-600 developer-hours  
**Parallel Work**: Can implement features in any order; wire them together last

Good luck! The architecture is there—it's just waiting for implementation.
