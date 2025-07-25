# 🔧 Nix for Humanity - Technical Architecture

## Overview

Nix for Humanity uses a hybrid approach combining deterministic rules, statistical models, and optional neural networks to achieve high accuracy with minimal resources.

## Core Architecture

### Three-Layer NLP Stack

```
┌─────────────────────────────────────────┐
│         User Input (Voice/Text)          │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│   Layer 1: Deterministic Rules (40%)     │
│   - Common patterns                      │
│   - Direct mappings                      │
│   - Syntax templates                     │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│   Layer 2: Statistical Models (50%)      │
│   - Intent classification                │
│   - Entity extraction                    │
│   - Context awareness                    │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│   Layer 3: Neural Fallback (10%)         │
│   - Complex reasoning                    │
│   - Ambiguity resolution                 │
│   - Learning from corrections            │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│         NixOS Command Execution          │
└─────────────────────────────────────────┘
```

### Key Components

#### 1. Intent Recognition Engine
```rust
pub struct IntentEngine {
    rules: Vec<IntentRule>,
    classifier: StatisticalClassifier,
    context: ConversationContext,
}

impl IntentEngine {
    pub fn classify(&mut self, input: &str) -> Intent {
        // Try deterministic rules first (fastest)
        if let Some(intent) = self.match_rules(input) {
            return intent;
        }
        
        // Statistical classification with context
        if let Some(intent) = self.classifier.classify(input, &self.context) {
            return intent;
        }
        
        // Neural fallback for complex cases
        self.neural_classify(input)
    }
}
```

#### 2. Command Translation Layer
```rust
pub struct NixTranslator {
    command_templates: HashMap<Intent, CommandTemplate>,
    safety_checker: SafetyValidator,
}

impl NixTranslator {
    pub fn translate(&self, intent: Intent, entities: Entities) -> Result<NixCommand> {
        let template = self.command_templates.get(&intent)?;
        let command = template.fill(entities)?;
        
        // Always validate before execution
        self.safety_checker.validate(&command)?;
        
        Ok(command)
    }
}
```

#### 3. Context Management
```rust
pub struct ConversationContext {
    history: VecDeque<Interaction>,
    user_profile: UserProfile,
    system_state: SystemState,
    active_task: Option<Task>,
}

impl ConversationContext {
    pub fn update(&mut self, interaction: Interaction) {
        self.history.push_back(interaction);
        if self.history.len() > 10 {
            self.history.pop_front();
        }
        
        // Update user patterns
        self.user_profile.learn_from(&interaction);
        
        // Track multi-turn conversations
        self.update_active_task(&interaction);
    }
}
```

## Operational Intelligence Architecture

### Overview
The Operational Intelligence layer provides context-aware, personalized system operations by learning WHO the user is, WHAT they want, HOW they prefer to work, and WHEN to act.

### Core Components

#### 1. User Pattern Recognition (WHO)
```rust
pub struct UserProfileLearner {
    interaction_history: VecDeque<TimestampedInteraction>,
    preference_model: PreferenceModel,
    skill_estimator: SkillLevelEstimator,
    naming_patterns: HashMap<String, Vec<String>>,
}

impl UserProfileLearner {
    pub fn learn_from_interaction(&mut self, interaction: &Interaction) {
        // Track naming preferences
        if let Some(resolved_package) = interaction.resolved_package() {
            self.naming_patterns
                .entry(resolved_package)
                .or_default()
                .push(interaction.user_term());
        }
        
        // Estimate technical skill level
        self.skill_estimator.update(interaction);
        
        // Learn preferences
        self.preference_model.update(interaction);
    }
    
    pub fn suggest_based_on_history(&self, context: &str) -> Vec<Suggestion> {
        // Personalized suggestions based on past behavior
        self.preference_model.predict(context)
    }
}
```

#### 2. Intent Understanding Engine (WHAT)
```rust
pub struct IntentInferenceEngine {
    literal_interpreter: LiteralInterpreter,
    contextual_reasoner: ContextualReasoner,
    goal_predictor: GoalPredictor,
}

impl IntentInferenceEngine {
    pub fn infer_intent(&self, input: &str, context: &Context) -> InferredIntent {
        // Start with literal interpretation
        let literal = self.literal_interpreter.parse(input);
        
        // Apply contextual reasoning
        let contextual = self.contextual_reasoner.enhance(literal, context);
        
        // Predict higher-level goal
        let goal = self.goal_predictor.predict(&contextual, context);
        
        InferredIntent {
            literal,
            contextual,
            predicted_goal: goal,
            confidence: self.calculate_confidence(&contextual),
        }
    }
}

// Example transformations:
// "make it faster" -> Optimize performance based on user's typical bottlenecks
// "clean up" -> User's preferred cleanup routine (not generic)
// "fix internet" -> Diagnose network issues in user's typical order
```

#### 3. Method Preference Learning (HOW)
```rust
pub enum InstallationMethod {
    ConfigurationNix,    // System-wide declarative
    HomeManager,         // User-scoped declarative
    NixEnv,             // Imperative installation
    Flakes,             // Flake-based installation
}

pub struct MethodPreferenceTracker {
    method_history: HashMap<PackageCategory, Vec<(InstallationMethod, bool)>>,
    user_expertise: ExpertiseLevel,
    context_patterns: Vec<ContextPattern>,
}

impl MethodPreferenceTracker {
    pub fn suggest_method(&self, package: &Package, context: &Context) -> InstallationMethod {
        // Check historical success rates
        let category = package.category();
        let history = self.method_history.get(&category);
        
        // Consider user expertise
        match self.user_expertise {
            ExpertiseLevel::Beginner => self.suggest_simple_method(package),
            ExpertiseLevel::Intermediate => self.suggest_balanced_method(package, history),
            ExpertiseLevel::Advanced => self.suggest_preferred_method(history),
        }
    }
    
    pub fn adapt_response(&self, base_response: Response) -> Response {
        // Tailor language and options to user's preferred methods
        match self.user_expertise {
            ExpertiseLevel::Beginner => base_response.simplify(),
            ExpertiseLevel::Advanced => base_response.add_advanced_options(),
            _ => base_response,
        }
    }
}
```

#### 4. Workflow-Aware Scheduler (WHEN)
```rust
pub struct WorkflowIntelligence {
    activity_patterns: TimeSeriesModel,
    task_timing_preferences: HashMap<TaskType, TimingPreference>,
    system_load_predictor: LoadPredictor,
    focus_time_detector: FocusTimeDetector,
}

impl WorkflowIntelligence {
    pub fn optimal_execution_time(&self, task: &Task) -> ExecutionStrategy {
        let current_load = self.system_load_predictor.current();
        let predicted_load = self.system_load_predictor.forecast(Duration::hours(24));
        let user_schedule = self.activity_patterns.predict_availability();
        
        match task.priority() {
            Priority::Critical => ExecutionStrategy::Immediate,
            Priority::Normal => {
                if self.focus_time_detector.is_focus_time() {
                    ExecutionStrategy::Defer(self.next_break_time())
                } else {
                    ExecutionStrategy::Queue
                }
            },
            Priority::Low => {
                ExecutionStrategy::Schedule(self.find_idle_window(task, predicted_load))
            }
        }
    }
    
    pub fn learn_timing_preference(&mut self, task: &Task, execution: &Execution) {
        self.task_timing_preferences
            .entry(task.task_type())
            .or_default()
            .update(execution.timing, execution.success);
    }
}
```

#### 5. Relationship Intelligence
```rust
pub struct PackageRelationshipGraph {
    dependency_graph: Graph<Package, Relationship>,
    usage_patterns: HashMap<(Package, Package), f32>,
    conflict_history: HashMap<(Package, Package), Vec<Conflict>>,
    community_preferences: CommunityModel,
}

impl PackageRelationshipGraph {
    pub fn suggest_related(&self, package: &Package) -> Vec<PackageSuggestion> {
        let mut suggestions = Vec::new();
        
        // Direct dependencies
        for dep in self.dependency_graph.neighbors(package) {
            suggestions.push(PackageSuggestion::Required(dep));
        }
        
        // Commonly paired packages
        for (paired, strength) in self.usage_patterns.iter() {
            if paired.0 == *package && strength > &0.7 {
                suggestions.push(PackageSuggestion::Recommended(paired.1.clone()));
            }
        }
        
        // Community preferences
        suggestions.extend(self.community_preferences.suggestions_for(package));
        
        suggestions
    }
}
```

#### 6. Rollback Intelligence
```rust
pub struct RollbackPredictor {
    failure_patterns: Vec<FailurePattern>,
    recovery_strategies: HashMap<FailureType, RecoveryStrategy>,
    user_rollback_history: Vec<RollbackEvent>,
}

impl RollbackPredictor {
    pub fn assess_risk(&self, planned_changes: &[Change]) -> RiskAssessment {
        let mut risk_score = 0.0;
        let mut warnings = Vec::new();
        
        for change in planned_changes {
            // Check against known failure patterns
            for pattern in &self.failure_patterns {
                if pattern.matches(change) {
                    risk_score += pattern.risk_weight;
                    warnings.push(pattern.warning_message());
                }
            }
        }
        
        RiskAssessment {
            score: risk_score,
            warnings,
            suggested_precautions: self.suggest_precautions(risk_score),
        }
    }
    
    pub fn learn_from_rollback(&mut self, rollback: RollbackEvent) {
        // Extract pattern from failure
        if let Some(pattern) = FailurePattern::extract_from(&rollback) {
            self.failure_patterns.push(pattern);
        }
        
        // Update recovery strategies
        self.recovery_strategies
            .entry(rollback.failure_type())
            .or_default()
            .update(rollback.recovery_method());
    }
}
```

### Privacy-Preserving Learning

```rust
pub struct PrivateUserModel {
    encrypted_store: EncryptedStore,
    local_only: bool,
    export_format: ExportFormat,
}

impl PrivateUserModel {
    pub fn new() -> Self {
        Self {
            encrypted_store: EncryptedStore::new_local(),
            local_only: true,
            export_format: ExportFormat::Json,
        }
    }
    
    pub fn export_learnings(&self) -> Result<String> {
        // User owns their data
        self.encrypted_store.export(self.export_format)
    }
    
    pub fn reset(&mut self) {
        // Complete erasure on request
        self.encrypted_store.wipe();
    }
    
    pub fn explain_reasoning(&self, decision: &Decision) -> Explanation {
        // Transparency in AI decisions
        Explanation {
            factors: decision.contributing_factors(),
            weights: decision.factor_weights(),
            historical_basis: self.get_relevant_history(decision),
        }
    }
}
```

## Natural Language Processing

### Intent Categories

1. **Package Management**
   - Install/remove/update packages
   - Search for software
   - Check installed versions

2. **System Configuration**
   - Network settings
   - User management
   - Service control

3. **Troubleshooting**
   - Diagnose problems
   - Fix common issues
   - System health checks

4. **Information Queries**
   - System status
   - Configuration values
   - Help and documentation

### Entity Extraction

```rust
pub enum Entity {
    PackageName(String),
    ServiceName(String),
    ConfigOption(String),
    FilePath(PathBuf),
    TimeExpression(DateTime),
    Quantity(i32, Unit),
}

pub struct EntityExtractor {
    patterns: Vec<EntityPattern>,
    fuzzy_matcher: FuzzyMatcher,
}
```

### Fuzzy Matching for Packages

```rust
// User says: "install that photo editor everyone likes"
// System resolves: gimp

pub struct PackageResolver {
    package_db: PackageDatabase,
    aliases: HashMap<String, Vec<String>>,
    popularity: HashMap<String, f32>,
}

impl PackageResolver {
    pub fn resolve(&self, description: &str) -> Vec<PackageMatch> {
        let tokens = tokenize(description);
        
        // Check aliases first
        if let Some(packages) = self.resolve_aliases(&tokens) {
            return packages;
        }
        
        // Fuzzy search in descriptions
        self.fuzzy_search(description)
            .sorted_by(|a, b| {
                // Prefer popular packages
                self.popularity[&b.name]
                    .partial_cmp(&self.popularity[&a.name])
                    .unwrap()
            })
            .take(3)
            .collect()
    }
}
```

## Voice Interface

### Architecture
```rust
pub struct VoiceInterface {
    audio_capture: AudioCapture,
    vad: VoiceActivityDetector,
    stt: SpeechToText,
    tts: TextToSpeech,
    audio_output: AudioOutput,
}

// Using Whisper for STT (runs locally)
impl SpeechToText for WhisperSTT {
    async fn transcribe(&self, audio: AudioBuffer) -> Result<String> {
        // Efficient streaming transcription
        self.model.transcribe_streaming(audio).await
    }
}
```

### Wake Word Detection
- "Hey Nix" or "Nix, please"
- Low-power always-listening mode
- Privacy-preserving (no cloud)

## Error Recovery System

### Intelligent Error Messages

```rust
pub struct ErrorTranslator {
    error_patterns: Vec<ErrorPattern>,
    solution_db: SolutionDatabase,
}

impl ErrorTranslator {
    pub fn translate(&self, nix_error: &str) -> UserFriendlyError {
        // Pattern match common Nix errors
        let error_type = self.classify_error(nix_error);
        
        // Get solution suggestions
        let solutions = self.solution_db.get_solutions(error_type);
        
        UserFriendlyError {
            summary: self.simple_explanation(error_type),
            details: self.helpful_context(nix_error),
            suggestions: solutions,
            learn_more: self.get_help_url(error_type),
        }
    }
}
```

### Self-Healing Capabilities

```rust
pub struct SelfHealer {
    fixers: HashMap<ErrorType, Box<dyn Fixer>>,
}

impl SelfHealer {
    pub async fn attempt_fix(&self, error: &Error) -> Result<()> {
        if let Some(fixer) = self.fixers.get(&error.error_type) {
            // Ask user permission first
            if self.get_user_consent(&fixer.description()).await? {
                fixer.apply().await?;
            }
        }
        Ok(())
    }
}
```

## Performance Optimizations

### 1. Caching Strategy
```rust
pub struct CommandCache {
    recent_commands: LruCache<IntentHash, NixCommand>,
    user_patterns: UserPatternCache,
}
```

### 2. Progressive Enhancement
- Start with basic rules (150MB RAM)
- Load statistical models on demand (500MB)
- Neural models only when needed (2GB)

### 3. Background Learning
```rust
pub struct BackgroundLearner {
    interaction_log: InteractionLog,
    pattern_miner: PatternMiner,
}

impl BackgroundLearner {
    pub fn learn_user_patterns(&self) {
        // Run during idle time
        thread::spawn(|| {
            self.pattern_miner.extract_patterns(&self.interaction_log);
        });
    }
}
```

## Security Architecture

### Sandboxed Execution
```rust
pub struct SafeExecutor {
    sandbox: NixSandbox,
    permission_manager: PermissionManager,
}

impl SafeExecutor {
    pub async fn execute(&self, command: NixCommand) -> Result<Output> {
        // Check permissions
        self.permission_manager.verify(&command)?;
        
        // Execute in sandbox first
        let dry_run = self.sandbox.dry_run(&command).await?;
        
        // Show changes to user
        if self.get_user_confirmation(&dry_run).await? {
            self.sandbox.execute(command).await
        } else {
            Err(Error::UserCancelled)
        }
    }
}
```

### Privacy Preservation
- All processing happens locally
- No telemetry or usage tracking
- Voice data never leaves device
- Learn from user, but data stays private

## Integration Points

### 1. NixOS Integration
```rust
// Direct integration with Nix daemon
pub struct NixDaemon {
    socket: UnixSocket,
    protocol: NixProtocol,
}

// For evaluation and builds
pub struct NixEvaluator {
    evaluator: Evaluator,
    builder: Builder,
}
```

### 2. System Integration
- systemd service management
- NetworkManager for networking
- User session integration
- Desktop environment hooks

### 3. Extension System
```rust
pub trait NixForHumanityPlugin {
    fn name(&self) -> &str;
    fn register_intents(&self) -> Vec<Intent>;
    fn handle(&self, intent: Intent, ctx: Context) -> Result<Response>;
}
```

## Development Workflow with Claude Code Max

### 1. Iterative Development
```bash
# Claude writes initial implementation
# Human tests and provides feedback
# Claude refines based on real usage
```

### 2. Test-Driven Development
```rust
#[cfg(test)]
mod tests {
    #[test]
    fn test_install_firefox() {
        let input = "install firefox";
        let intent = engine.classify(input);
        assert_eq!(intent, Intent::InstallPackage("firefox"));
    }
}
```

### 3. Continuous Refinement
- Real user testing
- Pattern extraction
- Model improvement
- Documentation updates

---

Next: See [DEVELOPMENT.md](./DEVELOPMENT.md) for contributing →