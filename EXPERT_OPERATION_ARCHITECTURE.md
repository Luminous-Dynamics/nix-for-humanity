# 🎯 Expert Operation Architecture - From "Install Firefox" to "Anything a NixOS Expert Can Do"

**Created**: December 2, 2025
**Context**: User insight - "a install is at the low end of what we need this system to handel - it needs to handel any thing a NixOS expert can do."

---

## The Profound Insight

### What "Install Firefox" Actually Requires (Full Chain)

```
User: "install firefox"
    ↓
[LAYER 1: SEMANTIC UNDERSTANDING] ✅ Working
├─ Gemma3+HRM Hybrid: Intent = "install", Entity = "firefox"
├─ Confidence: 0.92, Language: English
└─ Alternative interpretations: ["firefox-esr", "firefox-dev"]
    ↓
[LAYER 2: CONTEXT ANALYSIS] 🚧 Partial
├─ System State: Is firefox already installed? (✅ Working)
├─ User Preference: User environment vs system-wide? (❌ Missing)
├─ Dependency Impact: What else changes? (✅ Working)
├─ Conflict Detection: Will this break anything? (✅ Working)
└─ Permission Check: Can user do this? (❌ Missing)
    ↓
[LAYER 3: STRATEGY SELECTION] 🚧 Partial
├─ Installation Method:
│   ├─ nix-env (user environment)
│   ├─ configuration.nix (system-wide)
│   ├─ nix-shell (temporary)
│   └─ flake (modern approach)
├─ Version Selection: Latest? Stable? Specific? (❌ Missing)
└─ Optimization: Binary cache vs local build? (❌ Missing)
    ↓
[LAYER 4: EXECUTION PLANNING] 🚧 Partial
├─ Pre-flight Checks:
│   ├─ Disk space available?
│   ├─ Network connectivity?
│   └─ Lock files accessible?
├─ Execution Steps:
│   ├─ Update channels (if needed)
│   ├─ Fetch package
│   ├─ Build/install
│   └─ Verify installation
├─ Rollback Plan: How to undo if fails? (✅ Working)
└─ Time Estimate: 30s - 5min depending on cache
    ↓
[LAYER 5: EXECUTION WITH MONITORING] 🚧 Partial
├─ Progress Tracking: Real-time feedback (❌ Missing)
├─ Error Detection: Catch issues early (🚧 Partial)
├─ Adaptive Recovery: Retry with different strategy (❌ Missing)
└─ Learning: Record success/failure for next time (❌ Missing)
    ↓
[LAYER 6: POST-EXECUTION] 🚧 Partial
├─ Verification: Did it actually work? (🚧 Partial)
├─ Documentation: What was installed? Where? Why? (❌ Missing)
├─ Optimization Hints: "You could also..." (❌ Missing)
└─ Related Suggestions: "Users who installed X also..." (❌ Missing)
```

**Current Reality**: We handle layers 1-2 well, but 3-6 are incomplete.
**User's Insight**: If we can't handle all 6 layers for "install firefox", we definitely can't handle "configure secure web server" (which needs all 6 layers × 10 components).

---

## What a NixOS Expert Can Do (Complexity Pyramid)

### Tier 1: Foundational Operations ✅ 90%+ Working
```
- Install/remove packages
- Search packages
- Update system
- List installed packages
- Rollback to previous generation
```

### Tier 2: Configuration Management 🚧 60% Working
```
- Generate configuration.nix from requirements
- Edit system configuration
- Enable/configure services
- Manage user environments
- Create development shells
```

### Tier 3: Advanced System Operations 🚧 30% Working
```
- Optimize build performance
- Configure networking (firewall, VPN, etc.)
- Set up secure web servers
- Manage secrets and credentials
- Configure desktop environments
```

### Tier 4: Expert Operations 🚧 20% Working
```
- Migrate from channels to flakes
- Debug slow rebuilds
- Refactor configuration for modularity
- Create custom NixOS modules
- Set up distributed builds
```

### Tier 5: Master-Level Operations ❌ 5% Working
```
- Contribute upstream fixes
- Debug Nix language evaluation
- Optimize closure sizes
- Create reproducible deployments
- Implement custom builders
```

**Reality Check**: Most users need Tier 2-3. Power users need Tier 4. We're at ~50% capability across the pyramid.

---

## The Architecture Gap: What's Missing

### 1. Intent → Strategy Router ❌ MISSING

**Current**: Intent recognized → Simple executor called
**Needed**: Intent recognized → Analyze context → Select best strategy → Execute

```python
class StrategyRouter:
    """Determine the best execution strategy for an intent"""

    def route(self, intent: Intent, context: SystemContext) -> ExecutionStrategy:
        """
        Consider:
        - User's skill level (beginner → expert)
        - System state (flakes? channels? hybrid?)
        - Available resources (disk space, network, time)
        - Risk tolerance (safe → aggressive)
        - Optimization goals (speed vs reliability)
        """

        if intent.type == "install_package":
            if context.using_flakes:
                return FlakeInstallStrategy()
            elif context.user_skill == "beginner":
                return SafeNixEnvStrategy()
            elif context.optimize_for == "speed":
                return BinaryCacheStrategy()
            else:
                return SystemWideStrategy()
```

**Why This Matters**: "Install firefox" has 4+ valid execution paths. Expert needs the RIGHT one for their context.

### 2. Multi-Component Orchestration ❌ MISSING

**Current**: Single operations work. Multi-step templates are hardcoded.
**Needed**: Dynamic composition of operations with dependencies.

```python
class OperationComposer:
    """Compose complex operations from primitives"""

    def compose(self, goal: str) -> ExecutionDAG:
        """
        "setup secure web server" →

        DAG:
        ┌─────────────┐
        │ Install nginx│
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │Configure nginx│
        └──────┬───────┘
               │
        ┌──────▼───────┐    ┌─────────────┐
        │ Setup certbot├────►Install python│
        └──────┬───────┘    └─────────────┘
               │
        ┌──────▼───────┐
        │Configure SSL │
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │Enable service│
        └──────┬───────┘
               │
        ┌──────▼───────┐
        │  Test ports  │
        └──────────────┘
        """
```

**Why This Matters**: Expert operations are ALWAYS multi-component. Can't hardcode every possibility.

### 3. Adaptive Execution Engine ❌ MISSING

**Current**: Execute plan. If fails, stop.
**Needed**: Execute plan. If fails, try alternative. Learn from outcome.

```python
class AdaptiveExecutor:
    """Execute with learning and adaptation"""

    def execute(self, plan: ExecutionPlan) -> Result:
        """
        For each step:
        1. Check if already satisfied (optimization)
        2. Execute with monitoring
        3. If fails:
           a. Diagnose failure reason
           b. Try alternative approach
           c. If all alternatives fail, rollback
        4. Record outcome for learning
        """

        for step in plan.steps:
            if self.already_satisfied(step):
                continue  # Skip unnecessary work

            try:
                result = self.execute_with_monitoring(step)
                self.learn(step, result, success=True)
            except ExecutionError as e:
                alternative = self.find_alternative(step, e)
                if alternative:
                    result = self.execute_with_monitoring(alternative)
                else:
                    self.rollback_to_safe_state()
                    raise
                self.learn(step, result, success=False)
```

**Why This Matters**: Real-world operations fail. Network issues. Package unavailable. Disk full. Expert systems adapt.

### 4. Knowledge Accumulation System ❌ MISSING

**Current**: Every operation is independent. No learning.
**Needed**: System remembers what worked, what failed, what users prefer.

```python
class KnowledgeBase:
    """Accumulate operational knowledge"""

    def record_operation(self,
                        intent: Intent,
                        strategy: Strategy,
                        outcome: Outcome,
                        user_feedback: Optional[Feedback]):
        """
        Store:
        - What worked (success patterns)
        - What failed (failure patterns)
        - User corrections (preference learning)
        - System context (when things work)
        """

    def suggest_strategy(self, intent: Intent, context: Context) -> Strategy:
        """
        Based on historical data:
        - Which strategy succeeded most often for similar intent?
        - Which strategy did THIS user prefer?
        - What worked for similar system configurations?
        """
```

**Why This Matters**: Expert knowledge is accumulated, not static. System should improve with use.

### 5. Multi-Domain Reasoning ❌ MISSING

**Current**: Each operation type handled independently.
**Needed**: Cross-domain reasoning for complex scenarios.

```python
class MultiDomainReasoner:
    """Reason across multiple domains for expert operations"""

    def analyze(self, request: str) -> AnalysisResult:
        """
        "Make my system faster and more secure" requires:

        Performance Domain:
        - Boot optimization (systemd analysis)
        - Build optimization (cache, parallel)
        - Runtime optimization (memory, CPU)

        Security Domain:
        - Service hardening
        - Firewall configuration
        - Update management

        Interaction Analysis:
        - Does hardening slow boot? (trade-off)
        - Does cache optimization create security risk?
        - Can we optimize build AND security together?
        """
```

**Why This Matters**: Expert operations rarely fit one domain. "Optimize AND secure" needs both.

---

## Concrete Implementation Path: 80/20 Rule

### Phase 1: Wire What Exists (30% effort → 80% capability boost)

**Week 1-2**: Intent → Strategy Router
```python
# File: src/luminous_nix/core/strategy_router.py (NEW)

class StrategyRouter:
    def __init__(self, system_profiler, user_profiler):
        self.system = system_profiler
        self.user = user_profiler

    def select_strategy(self, intent: Intent) -> Strategy:
        # Check system capabilities
        has_flakes = self.system.check_flakes_enabled()
        has_cache = self.system.check_binary_cache()

        # Check user preferences (from conversation history)
        prefers_system_wide = self.user.prefers_system_packages()
        skill_level = self.user.get_skill_level()

        # Select best strategy
        if intent.type == "install":
            strategies = [
                SystemWideStrategy() if prefers_system_wide else None,
                FlakeStrategy() if has_flakes else None,
                UserEnvStrategy() if skill_level == "beginner" else None,
                BinaryCacheStrategy() if has_cache else None,
            ]
            return self.rank_strategies(strategies, intent)[0]
```

**Week 3**: Operation Composer
```python
# File: src/luminous_nix/core/operation_composer.py (NEW)

class OperationComposer:
    def compose(self, goal: str, context: Context) -> ExecutionDAG:
        # Break goal into sub-goals
        sub_goals = self.decompose(goal)

        # For each sub-goal, find operations
        operations = []
        for sub in sub_goals:
            ops = self.find_operations(sub)
            operations.extend(ops)

        # Build dependency graph
        dag = DependencyGraph()
        for op in operations:
            dag.add_node(op)
            for dep in op.dependencies:
                dag.add_edge(dep, op)

        return ExecutionDAG(dag)
```

**Week 4**: Adaptive Executor
```python
# File: src/luminous_nix/core/adaptive_executor.py (MODIFY existing executor.py)

class AdaptiveExecutor(SafeExecutor):
    def execute_with_adaptation(self, plan: ExecutionDAG) -> Result:
        for step in plan.topological_order():
            try:
                result = self.execute_step(step)
                self.knowledge_base.record_success(step, result)
            except Exception as e:
                # Try alternatives
                alternatives = self.get_alternatives(step)
                for alt in alternatives:
                    try:
                        result = self.execute_step(alt)
                        self.knowledge_base.record_success(alt, result)
                        break
                    except Exception:
                        continue
                else:
                    # All failed, rollback
                    self.rollback()
                    raise
```

### Phase 2: Implement Real Expert Operations (40% effort)

**Month 2 Week 1-2**: Performance Profiler (COMPLETE IT)
```python
# File: src/luminous_nix/advanced_features/performance.py (EXPAND)

class PerformanceProfiler:
    def profile_boot(self) -> BootAnalysis:
        # systemd-analyze critical-chain
        # Parse output, identify bottlenecks

    def profile_rebuild(self) -> RebuildAnalysis:
        # Time each phase: eval, build, activate
        # Identify slow derivations

    def suggest_optimizations(self) -> List[Optimization]:
        # Based on profile, suggest:
        # - Enable binary cache
        # - Parallel builds
        # - Reduce closure size
```

**Month 2 Week 3-4**: Security Auditor (COMPLETE IT)
```python
# File: src/luminous_nix/advanced_features/security.py (EXPAND)

class SecurityAuditor:
    def audit_system(self) -> SecurityReport:
        # Check: services exposed
        # Check: firewall configuration
        # Check: outdated packages
        # Check: known vulnerabilities

    def suggest_hardening(self) -> List[HardeningStep]:
        # Based on audit, suggest:
        # - Disable unnecessary services
        # - Enable firewall rules
        # - Update vulnerable packages
```

### Phase 3: Learning System (30% effort)

**Month 3**: Knowledge Accumulation + Federated Learning Prep

```python
# File: src/luminous_nix/learning/knowledge_base.py (NEW)

class OperationalKnowledge:
    """Learn from every operation"""

    def record(self, operation: Operation, outcome: Outcome):
        # Store in SQLite
        self.db.insert({
            'operation_type': operation.type,
            'strategy_used': operation.strategy,
            'success': outcome.success,
            'duration': outcome.duration,
            'system_context': operation.context,
            'user_id': hash(user)  # Anonymous
        })

    def query_best_strategy(self, operation_type: str) -> Strategy:
        # Query database for most successful strategy
        results = self.db.query("""
            SELECT strategy, COUNT(*) as success_count
            FROM operations
            WHERE type = ? AND success = true
            GROUP BY strategy
            ORDER BY success_count DESC
        """, operation_type)

        return results[0]['strategy']
```

---

## Success Metrics: How to Know It Works

### Tier 1 Success (Month 1 Complete)
```
✅ "install firefox" → System asks: "user env or system-wide?"
✅ "install firefox" → System detects flakes, offers flake-based install
✅ "setup python dev" → System composes: install python + poetry + create shell.nix
✅ Failed operations → System tries alternative strategy automatically
```

### Tier 2 Success (Month 2 Complete)
```
✅ "make my system faster" → Profiles boot, suggests 3 optimizations, implements
✅ "audit my security" → Scans system, reports 5 issues, suggests fixes
✅ "setup secure web server" → Orchestrates 8 steps, verifies each, tests final result
✅ "migrate to flakes" → Analyzes current setup, generates flake, tests, commits
```

### Tier 3 Success (Month 3 Complete)
```
✅ System remembers user prefers system-wide installs → auto-suggests
✅ Strategy fails → System tries alternative → learns which works for this context
✅ "Do what I did last time" → System recalls previous successful operation
✅ Ready for Mycelix federated learning integration
```

---

## The Real Architecture: 5-Layer Orchestration

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: SEMANTIC UNDERSTANDING (✅ WORKING)            │
│ - Gemma3+HRM hybrid: Intent + entities + confidence     │
│ - 98.5% accuracy, 100+ languages, typo tolerance        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: CONTEXT ANALYSIS (🚧 PARTIAL → ✅ COMPLETE)  │
│ - System profiler: What's installed? What's possible?   │
│ - User profiler: What does user prefer? Skill level?    │
│ - Risk analyzer: What could go wrong?                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: STRATEGY SELECTION (❌ MISSING → ✅ BUILD)   │
│ - Strategy router: Which approach for this context?     │
│ - Operation composer: Break into sub-operations         │
│ - Dependency resolver: What order?                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 4: ADAPTIVE EXECUTION (❌ MISSING → ✅ BUILD)   │
│ - Executor: Run with monitoring                         │
│ - Error handler: Try alternatives if fails              │
│ - Progress tracker: Real-time feedback                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 5: LEARNING (❌ MISSING → ✅ BUILD)              │
│ - Knowledge base: Record what worked                    │
│ - Strategy optimizer: Improve suggestions over time     │
│ - Federated learning: Share knowledge (Mycelix)         │
└─────────────────────────────────────────────────────────┘
```

---

## Bottom Line: The Path to Expert Capability

**Current State**: We have layers 1-2 at 80%+. Layers 3-5 at 10-20%.

**3-Month Path**:
- **Month 1**: Wire layers 3-4 (strategy selection + adaptive execution)
- **Month 2**: Implement real expert operations (performance, security, migration)
- **Month 3**: Add layer 5 (learning system + Mycelix prep)

**Outcome**: System that truly "handles anything a NixOS expert can do" - not by having every answer hardcoded, but by having the architecture to reason, compose, adapt, and learn.

**Key Insight**: "Install firefox" is simple. Making "install firefox" work RELIABLY across all contexts (flakes vs channels, user vs system, cached vs uncached, network issues, disk space, etc.) requires ALL 5 layers. That's what makes it expert-level.

---

*"The difference between a tool and an expert system is not what it can do, but how it decides what to do."*

**Status**: Architecture defined, implementation path clear
**Next**: Begin Phase 1 - Wire what exists
**Timeline**: 3 months to expert capability
**Effort**: 400-500 developer-hours
