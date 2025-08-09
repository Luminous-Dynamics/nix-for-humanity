# 🚀 Oracle Research Implementation Plan

*Concrete steps to integrate Oracle research insights into Nix for Humanity*

---

💡 **Quick Context**: Actionable implementation plan based on Oracle research synthesis  
📍 **You are here**: Vision → Research → Oracle Implementation Plan  
🔗 **Related**: [Oracle Research Synthesis](./ORACLE_RESEARCH_SYNTHESIS.md) | [Implementation Priority Guide](../../IMPLEMENTATION_PRIORITY_GUIDE.md)  
⏱️ **Timeline**: This week → Next quarter  
📊 **Status**: Ready for implementation

---

## 📅 Immediate Tasks (This Week)

### 1. Install and Experiment with ActivityWatch

#### Installation Steps
```bash
# Option 1: Install via Nix
nix-env -iA nixpkgs.activitywatch

# Option 2: Add to configuration.nix
environment.systemPackages = with pkgs; [ activitywatch ];

# Option 3: Try in temporary shell
nix-shell -p activitywatch
```

#### Initial Experiments
```bash
# Start ActivityWatch
aw-qt  # GUI version
# or
aw-server  # Headless server only

# Access the web interface
firefox http://localhost:5600

# Test the API
curl http://localhost:5600/api/0/buckets
```

#### Key Areas to Explore
- Default watchers: window, afk, web
- Data export formats
- API authentication (if any)
- Resource usage and performance
- Privacy settings and data storage location

#### Documentation to Create
- `experiments/activitywatch/SETUP_NOTES.md`
- `experiments/activitywatch/API_EXPLORATION.md`
- `experiments/activitywatch/PRIVACY_ANALYSIS.md`

### 2. Design SKG Schema for SQLite

#### Schema Design Document
Create `/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/02-ARCHITECTURE/SKG_SCHEMA_DESIGN.md`:

```sql
-- Layer 1: Ontological (Domain Knowledge)
CREATE TABLE ontological_entities (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL, -- 'Package', 'Module', 'Option', 'Flake'
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, name)
);

CREATE TABLE ontological_relationships (
    id INTEGER PRIMARY KEY,
    from_entity_id INTEGER,
    to_entity_id INTEGER,
    relationship_type TEXT NOT NULL, -- 'depends_on', 'imports', 'has_type'
    metadata JSON,
    FOREIGN KEY (from_entity_id) REFERENCES ontological_entities(id),
    FOREIGN KEY (to_entity_id) REFERENCES ontological_entities(id)
);

-- Layer 2: Episodic (Interaction History)
CREATE TABLE episodic_interactions (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_input TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    command_executed TEXT,
    success BOOLEAN,
    error_message TEXT,
    context JSON -- Additional context data
);

CREATE TABLE episodic_patterns (
    id INTEGER PRIMARY KEY,
    pattern_type TEXT NOT NULL, -- 'command_sequence', 'error_recovery', 'learning_moment'
    pattern_data JSON,
    frequency INTEGER DEFAULT 1,
    last_seen TIMESTAMP
);

-- Layer 3: Phenomenological (User Experience)
CREATE TABLE phenomenological_states (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flow_probability REAL,
    anxiety_probability REAL,
    confusion_probability REAL,
    cognitive_load REAL,
    evidence JSON -- What led to this inference
);

CREATE TABLE phenomenological_triggers (
    id INTEGER PRIMARY KEY,
    trigger_type TEXT NOT NULL, -- 'frustration_pattern', 'flow_indicator'
    trigger_conditions JSON,
    observed_count INTEGER DEFAULT 0
);

-- Layer 4: Metacognitive (AI Self-Model)
CREATE TABLE metacognitive_capabilities (
    id INTEGER PRIMARY KEY,
    capability_name TEXT NOT NULL,
    confidence_level REAL,
    limitations TEXT,
    last_updated TIMESTAMP
);

CREATE TABLE metacognitive_reasoning (
    id INTEGER PRIMARY KEY,
    interaction_id INTEGER,
    reasoning_trace JSON,
    uncertainty_points JSON,
    decision_path TEXT,
    FOREIGN KEY (interaction_id) REFERENCES episodic_interactions(id)
);
```

#### Migration Strategy
- Start with existing SQLite database
- Add SKG tables incrementally
- Migrate existing data to appropriate layers
- Maintain backward compatibility

### 3. Create Phenomenological Modeling Prototype

#### Prototype Implementation
Create `/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src/phenomenology/qualia_computer.py`:

```python
import numpy as np
from typing import Dict, Any
from dataclasses import dataclass
from scipy.stats import entropy

@dataclass
class SystemState:
    """Raw computational state of the system"""
    react_loops: int = 0
    tokens_processed: int = 0
    planning_revisions: int = 0
    error_rate: float = 0.0
    intent_probabilities: Dict[str, float] = None
    predictive_accuracy: float = 0.0
    reward_signal_mean: float = 0.0
    reward_signal_variance: float = 0.0

@dataclass
class QualiaVector:
    """Computed subjective experience proxies"""
    effort: float = 0.0
    confusion: float = 0.0
    flow: float = 0.0
    learning_momentum: float = 0.0
    empathic_resonance: float = 0.0

class ComputationalPhenomenology:
    """Transform raw computational states into experiential qualia"""
    
    def __init__(self):
        # Weights for effort calculation
        self.w1 = 0.3  # react_loops weight
        self.w2 = 0.2  # tokens_processed weight
        self.w3 = 0.3  # planning_revisions weight
        self.w4 = 0.2  # error_rate weight
        
    def compute_qualia(self, state: SystemState) -> QualiaVector:
        """Compute subjective experience from system state"""
        
        # Effort - how hard the system is working
        effort = (
            self.w1 * min(state.react_loops / 10, 1.0) +
            self.w2 * min(state.tokens_processed / 1000, 1.0) +
            self.w3 * min(state.planning_revisions / 5, 1.0) +
            self.w4 * state.error_rate
        )
        
        # Confusion - uncertainty in decision making
        if state.intent_probabilities:
            probs = list(state.intent_probabilities.values())
            confusion = entropy(probs) / np.log(len(probs)) if len(probs) > 1 else 0
        else:
            confusion = 0.0
        
        # Flow - smooth, effective operation
        flow = self._calculate_flow(
            state.predictive_accuracy,
            state.reward_signal_mean,
            state.reward_signal_variance
        )
        
        # Learning momentum - rate of improvement
        learning_momentum = self._calculate_learning_rate(state)
        
        # Empathic resonance - alignment with user
        empathic_resonance = self._calculate_user_alignment(state)
        
        return QualiaVector(
            effort=effort,
            confusion=confusion,
            flow=flow,
            learning_momentum=learning_momentum,
            empathic_resonance=empathic_resonance
        )
    
    def _calculate_flow(self, accuracy: float, reward_mean: float, 
                       reward_variance: float) -> float:
        """Calculate flow state probability"""
        # High accuracy + consistent positive rewards = flow
        consistency = 1.0 - min(reward_variance, 1.0)
        return accuracy * reward_mean * consistency
    
    def _calculate_learning_rate(self, state: SystemState) -> float:
        """Calculate current learning momentum"""
        # Simplified: high accuracy with low effort indicates learning
        if state.tokens_processed > 0:
            efficiency = state.predictive_accuracy / (state.tokens_processed / 100)
            return min(efficiency, 1.0)
        return 0.0
    
    def _calculate_user_alignment(self, state: SystemState) -> float:
        """Calculate alignment with user's needs"""
        # High reward + low confusion = good alignment
        if state.intent_probabilities:
            max_prob = max(state.intent_probabilities.values())
            clarity = max_prob * state.reward_signal_mean
            return min(clarity, 1.0)
        return state.reward_signal_mean
    
    def explain_qualia(self, qualia: QualiaVector) -> str:
        """Generate natural language explanation of internal state"""
        
        explanations = []
        
        if qualia.confusion > 0.7:
            explanations.append(
                "I'm quite confused about what you're trying to do. "
                "I see multiple possible interpretations of your request."
            )
        
        if qualia.effort > 0.8 and qualia.flow < 0.3:
            explanations.append(
                "That was challenging for me - I had to try several approaches "
                "before finding a solution."
            )
        
        if qualia.flow > 0.8:
            explanations.append(
                "Everything clicked perfectly! I knew exactly what you needed."
            )
        
        if qualia.learning_momentum > 0.7:
            explanations.append(
                "I'm learning quickly from our interactions. "
                "Each conversation helps me understand you better."
            )
        
        if qualia.empathic_resonance < 0.3:
            explanations.append(
                "I'm not sure I fully understood what you need. "
                "Could you help me understand better?"
            )
        
        return " ".join(explanations) if explanations else "I'm processing normally."

# Example usage and tests
if __name__ == "__main__":
    phenomenology = ComputationalPhenomenology()
    
    # Test case 1: High confusion state
    confused_state = SystemState(
        react_loops=8,
        tokens_processed=500,
        planning_revisions=6,
        error_rate=0.3,
        intent_probabilities={"install": 0.3, "update": 0.3, "search": 0.4},
        predictive_accuracy=0.4,
        reward_signal_mean=0.2,
        reward_signal_variance=0.8
    )
    
    qualia = phenomenology.compute_qualia(confused_state)
    print("Confused state qualia:", qualia)
    print("Explanation:", phenomenology.explain_qualia(qualia))
    print()
    
    # Test case 2: Flow state
    flow_state = SystemState(
        react_loops=2,
        tokens_processed=200,
        planning_revisions=1,
        error_rate=0.0,
        intent_probabilities={"install": 0.95, "update": 0.05},
        predictive_accuracy=0.95,
        reward_signal_mean=0.9,
        reward_signal_variance=0.1
    )
    
    qualia = phenomenology.compute_qualia(flow_state)
    print("Flow state qualia:", qualia)
    print("Explanation:", phenomenology.explain_qualia(qualia))
```

## 📆 Short-term Tasks (This Month)

### 1. ActivityWatch Integration with Custom NixOS Watcher

#### Custom Watcher Development
Create `/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/src/watchers/nixos_watcher.py`:

```python
#!/usr/bin/env python3
"""
Custom ActivityWatch watcher for NixOS-specific activities
"""

import time
import json
import subprocess
from datetime import datetime, timezone
from aw_core import Event
from aw_client import ActivityWatchClient

class NixOSWatcher:
    def __init__(self):
        self.client = ActivityWatchClient("nixos-watcher")
        self.bucket_id = "aw-watcher-nixos"
        self.poll_interval = 1.0  # seconds
        
    def setup(self):
        """Create bucket for NixOS events"""
        self.client.create_bucket(
            self.bucket_id,
            event_type="nixos-command",
            queued=True
        )
    
    def watch_terminal_commands(self):
        """Monitor terminal for NixOS commands"""
        # This is a simplified example - real implementation would
        # monitor shell history or use terminal hooks
        
        last_command = None
        
        while True:
            try:
                # Get last command from history (example)
                # In practice, this would integrate with shell
                current_command = self._get_last_command()
                
                if current_command and current_command != last_command:
                    # Check if it's a NixOS-related command
                    if self._is_nixos_command(current_command):
                        event = Event(
                            timestamp=datetime.now(timezone.utc),
                            data={
                                "command": current_command,
                                "category": self._categorize_command(current_command)
                            }
                        )
                        self.client.insert_event(self.bucket_id, event)
                        last_command = current_command
                
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
    
    def _get_last_command(self):
        """Get the last executed command"""
        # Placeholder - would integrate with shell history
        return None
    
    def _is_nixos_command(self, command: str) -> bool:
        """Check if command is NixOS-related"""
        nixos_keywords = [
            'nix-env', 'nix-build', 'nix-shell', 'nix-store',
            'nixos-rebuild', 'nix', 'home-manager'
        ]
        return any(keyword in command for keyword in nixos_keywords)
    
    def _categorize_command(self, command: str) -> str:
        """Categorize the type of NixOS command"""
        if 'install' in command or 'nix-env -i' in command:
            return 'package_install'
        elif 'rebuild' in command:
            return 'system_rebuild'
        elif 'search' in command:
            return 'package_search'
        elif 'shell' in command:
            return 'development'
        else:
            return 'other'

if __name__ == "__main__":
    watcher = NixOSWatcher()
    watcher.setup()
    print("NixOS watcher started. Press Ctrl+C to stop.")
    watcher.watch_terminal_commands()
```

### 2. SKG Foundation Implementation

#### Phase 1: Core Infrastructure
- Implement SKG manager class
- Create layer-specific interfaces
- Build query engine for cross-layer reasoning
- Implement data migration from current SQLite

#### Phase 2: Layer Implementation
- **Week 1**: Ontological layer with NixOS package graph
- **Week 2**: Episodic layer with interaction history
- **Week 3**: Phenomenological layer with state inference
- **Week 4**: Metacognitive layer with self-model

### 3. Research Mamba Implementation Options

#### Available Libraries
```python
# Option 1: Mamba-minimal
# pip install mamba-minimal

# Option 2: Mamba-ssm (official)
# pip install mamba-ssm

# Option 3: Custom implementation based on papers
```

#### Evaluation Criteria
- Performance on long sequences (>10k tokens)
- Memory efficiency
- Integration complexity
- Training requirements
- License compatibility

#### Proof of Concept
Create comparison notebook:
- Load user interaction history
- Compare Transformer vs Mamba on:
  - Processing time
  - Memory usage
  - Context retention
  - Inference quality

## 🗓️ Medium-term Tasks (Next Quarter)

### 1. Complete Phenomenological Layer

#### Integration Points
- Connect to ActivityWatch data stream
- Real-time qualia computation
- Store in SKG phenomenological tables
- Surface in user interactions

#### Advanced Features
- Temporal qualia patterns
- Predictive state modeling
- Intervention recommendations
- User state dashboard

### 2. Begin Metacognitive Development

#### Self-Model Components
- Capability assessment
- Uncertainty quantification
- Reasoning trace visualization
- Limitation acknowledgment

#### Implementation Strategy
- Start with explicit self-assessment
- Add reasoning trace capture
- Build uncertainty calibration
- Create explanation generation

### 3. Prototype VLM Integration

#### Research Phase
- Evaluate SeeAct and AppAgent
- Test on NixOS GUI applications
- Assess safety boundaries
- Design integration architecture

#### Proof of Concept
- Simple GUI automation demo
- Safety sandbox implementation
- Performance benchmarks
- User study design

## 📊 Success Metrics

### This Week
- [ ] ActivityWatch installed and API tested
- [ ] SKG schema designed and reviewed
- [ ] Phenomenology prototype computing qualia

### This Month
- [ ] Custom NixOS watcher capturing commands
- [ ] SKG foundation with 2+ layers implemented
- [ ] Mamba evaluation complete with recommendation

### Next Quarter
- [ ] Full phenomenological layer in production
- [ ] Metacognitive self-assessment active
- [ ] VLM prototype demonstrating value

## 🔗 Resources

### Documentation
- [ActivityWatch Docs](https://docs.activitywatch.net/)
- [SQLite Schema Best Practices](https://www.sqlite.org/bestpractice.html)
- [Mamba Paper](https://arxiv.org/abs/2312.00752)

### Code References
- ActivityWatch API: `aw-client` Python library
- SKG Implementation: Graph databases in Python
- Phenomenology: Cognitive science libraries

### Research Papers
- Computational Phenomenology in AI
- Symbiotic Knowledge Graphs
- Long-sequence modeling with SSMs

---

*"From research to reality - implementing consciousness-first AI one step at a time."*

**Status**: Ready for implementation 🚀  
**Next Action**: Install ActivityWatch and begin exploration  
**Remember**: Each step brings us closer to true human-AI symbiosis 🌊