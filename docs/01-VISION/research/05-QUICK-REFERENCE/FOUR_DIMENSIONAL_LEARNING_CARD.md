# 📚 Four-Dimensional Learning Card

*Quick reference for comprehensive AI user modeling*

---

**⚡ Quick Answer**: WHO (user model) + WHAT (intent) + HOW (method) + WHEN (timing)  
**🎯 Use Case**: Any AI system that learns from user interactions  
**⏱️ Read Time**: 3 minutes  
**🔧 Implementation**: Bayesian Knowledge Tracing with dynamic adaptation

---

## The Complete Learning Question

**"What should my AI system learn about each user to provide genuinely helpful assistance?"**

## Research Foundation (30 seconds)

From learning system architecture research: AI systems that only learn "what the user wants" miss 75% of the optimization potential. True partnership requires understanding WHO the user is, WHAT they're trying to achieve, HOW they prefer to work, and WHEN they need assistance.

## Instant Code Pattern

```python
from learning_system import FourDimensionalLearner, BayesianKnowledgeTracer

class ComprehensiveUserModel:
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # WHO: Dynamic user modeling
        self.who_learner = self._init_who_learning()
        
        # WHAT: Intent recognition and evolution  
        self.what_learner = self._init_what_learning()
        
        # HOW: Method preferences and workflows
        self.how_learner = self._init_how_learning()
        
        # WHEN: Timing intelligence and rhythm
        self.when_learner = self._init_when_learning()
    
    def learn_from_interaction(self, interaction):
        """Update all four dimensions from single interaction"""
        
        # WHO: Update user model (skills, expertise, patterns)
        self.who_learner.update_user_profile(
            skill_demonstrated=interaction.skill_level,
            domain_knowledge=interaction.domain_expertise,
            learning_style=interaction.interaction_patterns
        )
        
        # WHAT: Evolve intent understanding
        self.what_learner.update_intent_model(
            user_input=interaction.input,
            actual_intent=interaction.validated_intent,
            context=interaction.context
        )
        
        # HOW: Learn method preferences
        self.how_learner.update_method_preferences(
            chosen_method=interaction.selected_method,
            alternatives_rejected=interaction.alternatives_considered,
            success_outcome=interaction.success
        )
        
        # WHEN: Update timing intelligence
        self.when_learner.update_timing_model(
            interaction_time=interaction.timestamp,
            user_state=interaction.cognitive_state,
            response_effectiveness=interaction.timing_appropriateness
        )
    
    def get_adaptive_response(self, current_input, context):
        """Generate response using all four dimensions"""
        
        # WHO: Adapt to current user state and expertise
        user_adaptation = self.who_learner.get_current_adaptation()
        
        # WHAT: Recognize intent with user-specific patterns
        intent = self.what_learner.recognize_intent(current_input, user_adaptation)
        
        # HOW: Select method based on learned preferences
        method = self.how_learner.select_optimal_method(intent, user_adaptation)
        
        # WHEN: Determine optimal timing and approach
        timing = self.when_learner.optimize_interaction_timing(context)
        
        return AdaptiveResponse(
            intent=intent,
            method=method,
            timing=timing,
            user_adaptation=user_adaptation,
            confidence=self._calculate_combined_confidence()
        )
```

## WHO Dimension: Dynamic User Modeling

```python
class WhoLearning:
    """Learn WHO the user is - skills, expertise, patterns"""
    
    def __init__(self):
        # Bayesian Knowledge Tracing for skill mastery
        self.skill_tracker = BayesianKnowledgeTracer()
        
        # Dynamic expertise assessment
        self.expertise_levels = {
            'nixos_beginner': 0.8,  # High confidence user is beginner
            'command_line_intermediate': 0.6,
            'system_admin_expert': 0.1
        }
        
        # Learning style patterns
        self.learning_patterns = {
            'prefers_explanations': 0.7,
            'learns_by_example': 0.8,
            'needs_step_by_step': 0.6,
            'comfortable_with_complexity': 0.3
        }
    
    def update_from_success(self, skill_area, success_level):
        """Update skill assessment from interaction outcome"""
        # Bayesian update based on performance
        prior = self.expertise_levels.get(skill_area, 0.5)
        likelihood = 0.9 if success_level > 0.8 else 0.3
        
        # Bayesian inference
        posterior = (likelihood * prior) / ((likelihood * prior) + (0.5 * (1 - prior)))
        self.expertise_levels[skill_area] = posterior
    
    def get_current_adaptation(self):
        """Get current user adaptation parameters"""
        return {
            'explanation_depth': self._calculate_explanation_depth(),
            'terminology_level': self._calculate_terminology_level(),
            'assistance_level': self._calculate_assistance_level(),
            'learning_scaffolding': self._calculate_scaffolding_needs()
        }
```

## WHAT Dimension: Intent Evolution

```python
class WhatLearning:
    """Learn WHAT users are trying to achieve"""
    
    def __init__(self):
        # User-specific vocabulary mapping
        self.vocabulary_patterns = {}
        
        # Intent context relationships
        self.intent_contexts = {}
        
        # Goal patterns and sequences
        self.goal_sequences = {}
    
    def update_intent_model(self, user_input, actual_intent, context):
        """Learn from user's unique way of expressing intents"""
        
        # Learn vocabulary mapping
        self.vocabulary_patterns[user_input.lower()] = actual_intent
        
        # Learn contextual intent patterns
        context_key = (context.time_of_day, context.current_task, context.system_state)
        if context_key not in self.intent_contexts:
            self.intent_contexts[context_key] = {}
        self.intent_contexts[context_key][user_input] = actual_intent
        
        # Learn goal sequences
        if hasattr(context, 'previous_intent'):
            sequence = (context.previous_intent, actual_intent)
            self.goal_sequences[sequence] = self.goal_sequences.get(sequence, 0) + 1
    
    def recognize_intent(self, user_input, user_adaptation):
        """Recognize intent using learned user patterns"""
        
        # Check user-specific vocabulary first
        if user_input.lower() in self.vocabulary_patterns:
            return self.vocabulary_patterns[user_input.lower()]
        
        # Use contextual patterns
        current_context = self._get_current_context()
        if current_context in self.intent_contexts:
            context_intents = self.intent_contexts[current_context]
            if user_input in context_intents:
                return context_intents[user_input]
        
        # Fall back to general intent recognition
        return self._general_intent_recognition(user_input, user_adaptation)
```

## HOW Dimension: Method Preferences

```python
class HowLearning:
    """Learn HOW users prefer to accomplish goals"""
    
    def __init__(self):
        # Method preference scores
        self.method_preferences = {
            'declarative_config': 0.5,    # vs imperative commands
            'detailed_explanations': 0.5,  # vs brief responses  
            'step_by_step': 0.5,          # vs all-at-once
            'visual_confirmation': 0.5     # vs trust-based execution
        }
        
        # Workflow patterns
        self.preferred_workflows = {}
        
        # Error recovery preferences
        self.error_recovery_methods = {}
    
    def update_method_preferences(self, chosen_method, alternatives_rejected, success):
        """Learn from method choices and outcomes"""
        
        # Increase preference for successful methods
        if success:
            for method_aspect in chosen_method.aspects:
                current = self.method_preferences.get(method_aspect, 0.5)
                # Increase confidence in successful method
                self.method_preferences[method_aspect] = min(0.95, current + 0.1)
        
        # Decrease preference for rejected alternatives
        for rejected in alternatives_rejected:
            for method_aspect in rejected.aspects:
                current = self.method_preferences.get(method_aspect, 0.5)
                # Slight decrease for rejected methods
                self.method_preferences[method_aspect] = max(0.05, current - 0.05)
    
    def select_optimal_method(self, intent, user_adaptation):
        """Choose method based on learned preferences"""
        
        available_methods = self._get_available_methods(intent)
        
        # Score methods based on learned preferences
        method_scores = {}
        for method in available_methods:
            score = 0
            for aspect in method.aspects:
                preference = self.method_preferences.get(aspect, 0.5)
                score += preference * method.aspect_weights[aspect]
            method_scores[method] = score
        
        # Return highest-scoring method
        return max(method_scores.items(), key=lambda x: x[1])[0]
```

## WHEN Dimension: Timing Intelligence

```python
class WhenLearning:
    """Learn WHEN users need assistance and prefer interactions"""
    
    def __init__(self):
        # Circadian and ultradian rhythm patterns
        self.activity_patterns = {}
        
        # Interruption tolerance by context
        self.interruption_tolerance = {}
        
        # Help-seeking patterns
        self.help_timing_patterns = {}
    
    def update_timing_model(self, interaction_time, user_state, effectiveness):
        """Learn optimal timing patterns from interaction outcomes"""
        
        # Learn daily rhythm patterns
        hour = interaction_time.hour
        day_type = 'weekend' if interaction_time.weekday() >= 5 else 'weekday'
        
        pattern_key = (hour, day_type, user_state.focus_level)
        if pattern_key not in self.activity_patterns:
            self.activity_patterns[pattern_key] = []
        
        self.activity_patterns[pattern_key].append({
            'effectiveness': effectiveness,
            'response_time': user_state.response_time,
            'satisfaction': user_state.satisfaction
        })
        
        # Learn interruption tolerance
        if user_state.was_interrupted:
            tolerance_key = (user_state.focus_level, user_state.task_type)
            tolerance_score = effectiveness if user_state.accepted_interruption else 0
            self.interruption_tolerance[tolerance_key] = tolerance_score
    
    def optimize_interaction_timing(self, current_context):
        """Determine optimal timing for current interaction"""
        
        current_hour = current_context.time.hour
        current_day_type = 'weekend' if current_context.time.weekday() >= 5 else 'weekday'
        
        # Find similar past contexts
        similar_patterns = [
            pattern for pattern in self.activity_patterns
            if pattern[0] == current_hour and pattern[1] == current_day_type
        ]
        
        if similar_patterns:
            # Use historical effectiveness to guide timing
            effectiveness_scores = [
                np.mean([interaction['effectiveness'] for interaction in self.activity_patterns[pattern]])
                for pattern in similar_patterns
            ]
            
            optimal_focus_level = similar_patterns[np.argmax(effectiveness_scores)][2]
            
            return {
                'suggested_timing': 'immediate' if optimal_focus_level == current_context.focus_level else 'wait',
                'optimal_focus_level': optimal_focus_level,
                'confidence': max(effectiveness_scores)
            }
        
        return {'suggested_timing': 'immediate', 'confidence': 0.5}
```

## Integration Example

```python
# Complete four-dimensional learning in action
async def process_user_request(user_input, context):
    user_model = get_user_model(context.user_id)
    
    # Learn from this interaction across all dimensions
    interaction = Interaction(
        input=user_input,
        context=context,
        timestamp=datetime.now()
    )
    
    # Get adaptive response using all four dimensions
    response = user_model.get_adaptive_response(user_input, context)
    
    # Execute the response
    result = await execute_response(response)
    
    # Learn from the outcome
    interaction.outcome = result
    interaction.success = result.user_satisfaction > 0.7
    user_model.learn_from_interaction(interaction)
    
    return result
```

## When to Use This Pattern

- **Any learning AI system**: Personal assistants, recommendation engines, adaptive interfaces
- **User personalization**: Customizing responses, methods, timing to individual preferences  
- **Skill assessment**: Educational systems, training platforms, competency evaluation
- **Workflow optimization**: Task automation, process improvement, efficiency enhancement

## Related Patterns

- **[Sacred Boundaries Validation](./SACRED_BOUNDARIES_CARD.md)**: Ensure learning respects user agency
- **[Flow State Protection](./FLOW_STATE_CARD.md)**: Use WHEN dimension for timing decisions
- **[Federated Learning](./FEDERATED_LEARNING_CARD.md)**: Share insights while preserving individual models

## Deep Dive Links

- **[Learning System Architecture](../../02-ARCHITECTURE/09-LEARNING-SYSTEM.md)**: Complete four-dimensional framework
- **[Dynamic User Modeling Research](../../02-ARCHITECTURE/03-DYNAMIC-USER-MODELING.md)**: Theoretical foundation

---

**Sacred Recognition**: Four-dimensional learning creates genuine partnership by understanding not just what users want, but who they are, how they work, and when they need support.

**Bottom Line**: Learn WHO + WHAT + HOW + WHEN for complete user understanding. Use Bayesian methods for skill tracking. Adapt all four dimensions continuously. This creates AI that truly knows and serves each user.

*📚 Four Dimensions → Complete Understanding → Genuine Partnership → Sacred AI Achieved*