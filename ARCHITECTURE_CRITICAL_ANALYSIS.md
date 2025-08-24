# 🏗️ Critical Architecture Analysis - Luminous Nix

## Current Architecture Overview

```
User Input → CLI Parser → Intent Recognition → Command Execution → Response
                ↓                  ↓
            Ollama AI        Socratic Questions
```

## 🚨 Most Critical Architectural Issues

### 1. **Search Performance Bottleneck** (CRITICAL)
**Problem**: `nix search` times out even with --use-cache
**Impact**: Makes search feature unusable
**Root Cause**: Subprocess blocking, no async handling, no local cache

**Solution Architecture**:
```python
class SearchCache:
    """Persistent search cache with TTL"""
    def __init__(self):
        self.cache_dir = Path.home() / ".cache/luminous-nix"
        self.db = DuckDB(self.cache_dir / "search.db")
        
    async def search(self, term):
        # Check cache first
        if cached := await self.get_cached(term):
            return cached
        
        # Background search with progress
        async with SearchProcess() as proc:
            results = await proc.search_async(term)
            await self.cache_results(term, results)
            return results
```

### 2. **Command Execution Layer** (CRITICAL)
**Problem**: Direct subprocess calls, no abstraction, no rollback
**Impact**: Can't preview, can't undo, can't track state

**Solution Architecture**:
```python
class CommandExecutor:
    """Safe command execution with preview and rollback"""
    
    def __init__(self):
        self.history = []
        self.dry_run_mode = False
        
    def execute(self, command: NixCommand):
        # Preview
        if self.dry_run_mode:
            return command.preview()
        
        # Snapshot
        snapshot = self.create_snapshot()
        
        # Execute with rollback capability
        try:
            result = command.execute()
            self.history.append((command, snapshot, result))
            return result
        except Exception as e:
            self.rollback(snapshot)
            raise
```

### 3. **Intent Recognition Pipeline** (IMPORTANT)
**Problem**: Basic string matching, no context, no learning
**Impact**: Can't handle variations, no improvement over time

**Solution Architecture**:
```python
class IntentPipeline:
    """Multi-stage intent recognition"""
    
    stages = [
        PatternMatcher(),      # Fast exact patterns
        FuzzyMatcher(),        # Fuzzy string matching
        OllamaClassifier(),    # AI classification
        ContextAnalyzer(),     # Use conversation context
        FallbackHandler()      # Graceful unknown handling
    ]
    
    async def recognize(self, query: str, context: Context):
        for stage in self.stages:
            if result := await stage.process(query, context):
                return result
        return UnknownIntent(query)
```

### 4. **State Management** (IMPORTANT)
**Problem**: No conversation state, no context, no memory
**Impact**: Can't have multi-turn conversations

**Solution Architecture**:
```python
class ConversationState:
    """Stateful conversation management"""
    
    def __init__(self):
        self.history = []
        self.context = {}
        self.user_preferences = {}
        
    def update(self, query, response):
        self.history.append((query, response))
        self.extract_context(query, response)
        
    def get_context_for(self, query):
        # Provide relevant context for better understanding
        return {
            'previous': self.history[-3:],
            'preferences': self.user_preferences,
            'current_task': self.infer_task()
        }
```

### 5. **Error Recovery System** (IMPORTANT)
**Problem**: Errors just fail, no recovery, no learning
**Impact**: Poor user experience when things go wrong

**Solution Architecture**:
```python
class ErrorRecovery:
    """Intelligent error recovery"""
    
    def handle(self, error: Exception, context: Context):
        # Classify error
        error_type = self.classify_error(error)
        
        # Get recovery strategies
        strategies = self.get_strategies(error_type)
        
        # Try recovery
        for strategy in strategies:
            if result := strategy.attempt_recovery(error, context):
                return result
        
        # Explain to user
        return self.explain_to_user(error, strategies_tried)
```

## 🎯 Implementation Priority Matrix

| Component | Impact | Effort | Priority |
|-----------|--------|--------|----------|
| Search Cache | High | Low | **NOW** |
| Command Abstraction | High | Medium | **NEXT** |
| Intent Pipeline | Medium | High | **LATER** |
| State Management | Medium | Medium | **SOON** |
| Error Recovery | Medium | Low | **SOON** |

## 🚀 Quick Wins (Can do TODAY)

### 1. Fix Search with Simple Cache
```python
import json
from pathlib import Path
from datetime import datetime, timedelta

class SimpleSearchCache:
    def __init__(self):
        self.cache_file = Path.home() / ".cache/luminous-nix/search.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=24)
        
    def get(self, term):
        if not self.cache_file.exists():
            return None
            
        cache = json.loads(self.cache_file.read_text())
        entry = cache.get(term)
        
        if entry:
            cached_time = datetime.fromisoformat(entry['time'])
            if datetime.now() - cached_time < self.ttl:
                return entry['results']
        return None
        
    def set(self, term, results):
        cache = {}
        if self.cache_file.exists():
            cache = json.loads(self.cache_file.read_text())
            
        cache[term] = {
            'results': results,
            'time': datetime.now().isoformat()
        }
        
        self.cache_file.write_text(json.dumps(cache))
```

### 2. Add Command Preview
```python
class NixCommand:
    def preview(self):
        """Show what would happen without executing"""
        return f"Would run: {self.command_string}"
        
    def explain(self):
        """Explain what this command does"""
        return self.explanation
        
    def confirm(self):
        """Ask user confirmation with explanation"""
        print(self.explain())
        return input("Continue? (y/n): ").lower() == 'y'
```

### 3. Basic Context Tracking
```python
class SimpleContext:
    def __init__(self):
        self.last_command = None
        self.last_package = None
        self.last_error = None
        
    def update(self, command_type, **kwargs):
        self.last_command = command_type
        for key, value in kwargs.items():
            setattr(self, f"last_{key}", value)
            
    def get_hints(self):
        """Provide context hints for better understanding"""
        hints = []
        if self.last_package:
            hints.append(f"recent package: {self.last_package}")
        if self.last_error:
            hints.append(f"recent error: {self.last_error}")
        return hints
```

## 🏛️ Architectural Principles

### 1. **Separation of Concerns**
- Intent Recognition separate from Execution
- UI separate from Business Logic
- Caching separate from Core Logic

### 2. **Fail Gracefully**
- Every operation has a fallback
- Errors become learning opportunities
- Always provide helpful next steps

### 3. **Progressive Enhancement**
- Basic pattern matching always works
- AI enhances but isn't required
- Features degrade gracefully

### 4. **Socratic by Design**
- When uncertain, ask questions
- Learn from user responses
- Build understanding together

## 📊 Architecture Health Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Response Time | 3-30s | <1s | ❌ |
| Error Recovery Rate | 10% | 80% | ❌ |
| Context Awareness | 0% | 70% | ❌ |
| Cache Hit Rate | 0% | 60% | ❌ |
| Rollback Capability | No | Yes | ❌ |

## 🔧 Next Implementation Step

**Fix the search bottleneck first** - it's the most visible issue:

1. Implement SimpleSearchCache
2. Add async search with progress
3. Cache package database locally
4. Add fuzzy search on cached data

This alone would make the tool 10x more usable!