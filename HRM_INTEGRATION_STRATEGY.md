# 🎯 HRM Integration Strategy for Luminous Nix

## Executive Summary
Strategic plan for integrating HRM into Luminous Nix while maintaining stability and backwards compatibility. We'll use a **hybrid approach**: HRM for NixOS-specific reasoning, Ollama for general knowledge.

## 🏗️ Architecture: Hybrid AI Orchestrator

```
User Query
    ↓
AI Orchestrator (New)
    ├─→ HRM (27M params) - For NixOS reasoning
    │   • Dependency resolution
    │   • Configuration generation
    │   • Error diagnosis
    │   • System optimization
    │
    └─→ Ollama (2-7B params) - For general knowledge
        • Explanations
        • Learning concepts
        • General Linux help
        • Conversational responses
```

## 📋 Integration Plan: 3-Phase Approach

### Phase 1: Parallel Implementation (Week 1)
**Goal**: Run HRM alongside existing Ollama without breaking anything

#### 1.1 Create AI Orchestrator
```python
# src/luminous_nix/ai/orchestrator.py
class AIOrchestrator:
    def __init__(self):
        self.hrm = HRMNixOSReasoner()
        self.ollama = OllamaInterface()
        self.router = IntentRouter()
    
    def process(self, query):
        intent = self.router.classify(query)
        
        if intent in ['dependency', 'config', 'error', 'optimize']:
            return self.hrm.reason(query)  # <1ms response
        else:
            return self.ollama.query(query)  # 300ms response
```

#### 1.2 Setup HRM with PyTorch
```bash
# Install minimal PyTorch for CPU
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install einops  # Required for HRM

# Download HRM checkpoint (100MB)
wget https://huggingface.co/sapientinc/HRM-checkpoint-nixos/model.pt
```

#### 1.3 Create Training Pipeline
```python
# Train HRM on NixOS dataset
python train_hrm_nixos.py \
    --dataset data/nixos-1000.json \
    --epochs 100 \
    --batch_size 32 \
    --output models/hrm-nixos-v1.pt
```

### Phase 2: Smart Routing (Week 2)
**Goal**: Intelligently route queries to the best model

#### 2.1 Enhanced Intent Classification
```python
class SmartRouter:
    def classify(self, query):
        # Fast keyword matching first
        if self.is_nixos_specific(query):
            return 'hrm'
        
        # Check for reasoning patterns
        if self.needs_reasoning(query):
            return 'hrm'
        
        # Default to Ollama for general
        return 'ollama'
    
    def is_nixos_specific(self, query):
        nixos_keywords = [
            'package', 'dependency', 'conflict',
            'configuration.nix', 'overlay', 'flake',
            'error:', 'attribute', 'collision',
            'nixos-rebuild', 'generation'
        ]
        return any(kw in query.lower() for kw in nixos_keywords)
```

#### 2.2 Confidence-Based Selection
```python
def process_with_confidence(self, query):
    # Try HRM first for speed
    hrm_result = self.hrm.reason(query)
    
    if hrm_result.confidence > 0.85:
        return hrm_result  # High confidence, use HRM
    
    # Low confidence, check with Ollama
    ollama_result = self.ollama.query(query)
    
    # Return best result
    return self.select_best(hrm_result, ollama_result)
```

#### 2.3 Fallback Mechanisms
```python
class RobustOrchestrator:
    def process_safe(self, query):
        try:
            # Try HRM first (fastest)
            return self.hrm.reason(query, timeout=0.1)
        except TimeoutError:
            # Fallback to Ollama
            return self.ollama.query(query)
        except Exception as e:
            # Ultimate fallback
            return self.pattern_match_response(query)
```

### Phase 3: Production Deployment (Week 3)
**Goal**: Seamless user experience with maximum performance

#### 3.1 User-Facing Integration
```bash
# Transparent to users
./bin/ask-nix "install firefox"
# Automatically uses HRM (<1ms)

./bin/ask-nix "explain what is NixOS"
# Automatically uses Ollama (300ms)
```

#### 3.2 Performance Optimization
```python
# Cache HRM model in memory
class CachedHRM:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = load_model()
        return cls._instance

# Batch processing for multiple queries
def batch_process(queries):
    nixos_queries = [q for q in queries if is_nixos(q)]
    general_queries = [q for q in queries if not is_nixos(q)]
    
    # Process in parallel
    hrm_results = hrm.batch_reason(nixos_queries)
    ollama_results = ollama.batch_query(general_queries)
    
    return merge_results(hrm_results, ollama_results)
```

#### 3.3 Monitoring & Analytics
```python
# Track which model handles what
class UsageAnalytics:
    def log_query(self, query, model_used, response_time):
        self.metrics.append({
            'query': query,
            'model': model_used,
            'time_ms': response_time,
            'timestamp': time.now()
        })
    
    def get_stats(self):
        return {
            'hrm_usage': sum(1 for m in self.metrics if m['model'] == 'hrm'),
            'ollama_usage': sum(1 for m in self.metrics if m['model'] == 'ollama'),
            'avg_hrm_time': avg([m['time_ms'] for m in self.metrics if m['model'] == 'hrm']),
            'avg_ollama_time': avg([m['time_ms'] for m in self.metrics if m['model'] == 'ollama'])
        }
```

## 🎯 Implementation Priority

### Immediate (This Week)
1. **Set up PyTorch environment**
   ```bash
   cd 11-meta-consciousness/luminous-nix
   poetry add torch --extras cpu
   poetry add einops
   ```

2. **Create orchestrator.py**
   - Basic routing logic
   - Both models callable
   - Simple confidence threshold

3. **Expand training dataset**
   - Mine NixOS manual
   - Scrape GitHub configs
   - Generate variations

### Next Sprint
1. **Train HRM model**
   - 1000 examples minimum
   - Validate on test set
   - Save checkpoint

2. **Integration tests**
   - Compare responses
   - Measure performance
   - Check accuracy

3. **CLI integration**
   - Update ask-nix
   - Add --model flag
   - Default to auto-select

### Future Enhancements
1. **Progressive Model Loading**
   - Load HRM immediately (100MB)
   - Load Ollama on-demand (2GB)
   - Unload unused models

2. **Edge Deployment**
   - Quantize HRM to 8-bit (50MB)
   - Run on Raspberry Pi
   - Mobile app potential

3. **Community Learning**
   - Collect anonymized queries
   - Retrain periodically
   - Distribute updates

## 📊 Success Metrics

### Performance Targets
| Metric | Current (Ollama) | Target (Hybrid) | Stretch Goal |
|--------|-----------------|-----------------|--------------|
| P50 Response Time | 300ms | 50ms | 10ms |
| P95 Response Time | 1200ms | 300ms | 100ms |
| NixOS Task Accuracy | 70% | 90% | 95% |
| Memory Usage | 2GB | 300MB | 150MB |
| Model Size | 2GB | 200MB | 100MB |

### User Experience Goals
- ✅ 2-5 seconds feel for common tasks
- ✅ No noticeable difference in accuracy
- ✅ Graceful degradation on errors
- ✅ Transparent model selection

## 🔧 Technical Details

### Directory Structure
```
src/luminous_nix/ai/
├── orchestrator.py       # Main AI orchestrator
├── hrm/
│   ├── __init__.py
│   ├── reasoner.py       # HRM reasoning engine
│   ├── trainer.py        # Training pipeline
│   └── models/           # Saved checkpoints
├── ollama/
│   ├── __init__.py
│   └── interface.py      # Existing Ollama code
├── routing/
│   ├── __init__.py
│   ├── classifier.py     # Intent classification
│   └── patterns.py       # NixOS patterns
└── data/
    ├── training/         # Training datasets
    └── validation/       # Test datasets
```

### Configuration
```yaml
# config/ai_models.yaml
models:
  hrm:
    enabled: true
    path: "models/hrm-nixos-v1.pt"
    max_response_time: 100  # ms
    confidence_threshold: 0.85
    
  ollama:
    enabled: true
    model: "gemma:2b"
    max_response_time: 2000  # ms
    fallback: true
    
routing:
  strategy: "confidence"  # or "speed", "accuracy"
  nixos_patterns_file: "patterns/nixos.json"
```

### API Design
```python
# Clean, simple API
from luminous_nix.ai import ask

# Auto-selects best model
response = ask("install firefox")

# Force specific model
response = ask("install firefox", model="hrm")

# Get detailed info
response = ask("install firefox", verbose=True)
# Returns: {
#   "answer": "...",
#   "model_used": "hrm",
#   "confidence": 0.95,
#   "response_time_ms": 0.8,
#   "reasoning_steps": [...]
# }
```

## 🚀 Migration Path

### For Users
**No change required!** The system automatically uses the best model:
- NixOS tasks → HRM (2-5 seconds)
- General questions → Ollama (standard)

### For Developers
```python
# Old way (still works)
from luminous_nix.ai import query_ollama
result = query_ollama(prompt)

# New way (recommended)
from luminous_nix.ai import orchestrator
result = orchestrator.process(query)
```

### Backwards Compatibility
- ✅ All existing commands work
- ✅ Same output format
- ✅ Optional model selection
- ✅ Graceful fallbacks

## 📈 Expected Outcomes

### Week 1
- Orchestrator working
- Both models callable
- Basic routing implemented

### Week 2
- Smart routing refined
- Training complete
- Performance validated

### Week 3
- Production ready
- Monitoring in place
- Documentation complete

### Month 1
- 95% of NixOS queries handled by HRM
- Average response time <50ms
- User satisfaction increased
- Resource usage decreased 90%

## 🎯 Decision Points

### Go/No-Go Criteria
**Proceed to production if:**
- HRM accuracy >85% on test set
- Response time <100ms for 95% of queries
- Fallback mechanisms tested
- No regression in user experience

**Reconsider if:**
- Training takes >1 week
- Model size >200MB
- Accuracy <80%
- Integration too complex

## 💡 Risk Mitigation

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| HRM training fails | Low | High | Use pre-trained checkpoint |
| PyTorch too heavy | Medium | Medium | Use ONNX runtime instead |
| Routing errors | Low | Low | Fallback to Ollama always |
| Memory issues | Low | Medium | Lazy load models |

### User Experience Risks
- **Risk**: Inconsistent responses between models
- **Mitigation**: Unified output formatting

- **Risk**: Slower responses for general queries  
- **Mitigation**: Parallel processing when possible

## 🏁 Conclusion & Recommendation

**Strong Recommendation: Proceed with Hybrid Approach**

The hybrid orchestrator gives us:
1. **Best of both worlds** - HRM speed for NixOS, Ollama knowledge for general
2. **Risk mitigation** - Fallbacks ensure reliability
3. **Progressive enhancement** - Start simple, improve over time
4. **User transparent** - No learning curve

**Next Step**: Create `orchestrator.py` with basic routing and test both models working together.

---

*"The best integration is invisible. Users get 2-5 seconds NixOS help without knowing two AIs are collaborating behind the scenes."*