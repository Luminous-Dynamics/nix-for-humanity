# Nix for Humanity - Detailed Refactoring Guide

*Practical code transformations for production excellence*

## Overview

This guide provides specific, actionable refactoring examples to improve code quality, maintainability, and performance. Each example shows the current state and the improved version with explanations.

## 1. Intent Processing Refactoring

### Current State (Monolithic)
```python
# backend/core/nlp.py - 500+ lines of mixed concerns
def process_user_input(text):
    # Normalization
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    
    # Intent detection (100+ lines of if/elif)
    if "install" in text or "add" in text:
        package = extract_package_name(text)
        if not package:
            return {"error": "No package specified"}
        if not validate_package(package):
            return {"error": "Invalid package"}
        cmd = f"nix-env -iA nixos.{package}"
        result = subprocess.run(cmd, shell=True)
        # ... more logic
    elif "remove" in text or "uninstall" in text:
        # ... another 50 lines
    elif "search" in text:
        # ... another 80 lines
    # ... continues for 300+ lines
```

### Refactored (Separation of Concerns)
```python
# backend/core/text_normalizer.py
class TextNormalizer:
    """Single responsibility: text normalization"""
    def __init__(self):
        self.substitutions = [
            (r'\s+', ' '),
            (r'[^\w\s-]', ''),
            (r'^\s+|\s+$', '')
        ]
    
    def normalize(self, text: str) -> str:
        text = text.lower()
        for pattern, replacement in self.substitutions:
            text = re.sub(pattern, replacement, text)
        return text

# backend/core/intent_recognizer.py
class IntentRecognizer:
    """Single responsibility: intent recognition"""
    def __init__(self):
        self.patterns = {
            IntentType.INSTALL: [
                r'install\s+(\S+)',
                r'add\s+(\S+)',
                r'get\s+(\S+)\s+package'
            ],
            IntentType.REMOVE: [
                r'remove\s+(\S+)',
                r'uninstall\s+(\S+)',
                r'delete\s+(\S+)'
            ],
            IntentType.SEARCH: [
                r'search\s+(?:for\s+)?(.+)',
                r'find\s+(?:me\s+)?(.+)',
                r'look\s+for\s+(.+)'
            ]
        }
    
    def recognize(self, normalized_text: str) -> Intent:
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.match(pattern, normalized_text)
                if match:
                    return Intent(
                        type=intent_type,
                        entity=match.group(1) if match.groups() else None,
                        confidence=self._calculate_confidence(match)
                    )
        
        return Intent(type=IntentType.UNKNOWN, confidence=0.0)

# backend/core/intent_processor.py
class IntentProcessor:
    """Orchestrates the intent processing pipeline"""
    def __init__(self):
        self.normalizer = TextNormalizer()
        self.recognizer = IntentRecognizer()
        self.validator = IntentValidator()
        self.enhancer = IntentEnhancer()
    
    def process(self, raw_text: str) -> ProcessedIntent:
        # Clear pipeline with single responsibility components
        normalized = self.normalizer.normalize(raw_text)
        intent = self.recognizer.recognize(normalized)
        validated = self.validator.validate(intent)
        enhanced = self.enhancer.enhance(validated)
        
        return ProcessedIntent(
            original_text=raw_text,
            normalized_text=normalized,
            intent=enhanced,
            metadata=self._gather_metadata()
        )
```

## 2. Command Execution Refactoring

### Current State (Subprocess Spaghetti)
```python
# backend/execution/nix_executor.py
def execute_nix_command(cmd_type, package):
    try:
        if cmd_type == "install":
            # Direct subprocess call - prone to timeouts
            result = subprocess.run(
                f"sudo nix-env -iA nixos.{package}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # Often times out!
            )
            if result.returncode != 0:
                return {"error": result.stderr}
            return {"success": True, "output": result.stdout}
        elif cmd_type == "search":
            # Another subprocess variation
            result = subprocess.run(
                f"nix search nixpkgs {package}",
                shell=True,
                capture_output=True
            )
            # Manual parsing of output...
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out"}
    except Exception as e:
        return {"error": str(e)}
```

### Refactored (Native API with Fallback)
```python
# backend/execution/nix_api_adapter.py
from abc import ABC, abstractmethod
from typing import Optional
import asyncio

class NixAPIAdapter(ABC):
    """Abstract base for Nix API implementations"""
    @abstractmethod
    async def install(self, package: str) -> Result:
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[Package]:
        pass

# backend/execution/native_nix_api.py
class NativeNixAPI(NixAPIAdapter):
    """Uses NixOS 25.11+ Python API for blazing performance"""
    def __init__(self):
        # Import native API if available
        try:
            from nixos_rebuild import nix, models
            self.nix = nix
            self.models = models
            self.available = True
        except ImportError:
            self.available = False
    
    async def install(self, package: str) -> Result:
        if not self.available:
            raise NotImplementedError("Native API not available")
        
        # Direct Python API call - no subprocess!
        config = self.models.Configuration(
            packages=[package],
            action=self.models.Action.SWITCH
        )
        
        # Progress tracking built-in
        async for progress in self.nix.build_async(config):
            yield Progress(
                phase=progress.phase,
                percent=progress.percent,
                message=progress.message
            )
        
        return Result(success=True, package=package)

# backend/execution/subprocess_nix_api.py  
class SubprocessNixAPI(NixAPIAdapter):
    """Fallback using subprocess with better handling"""
    def __init__(self):
        self.process_pool = ProcessPoolExecutor(max_workers=4)
    
    async def install(self, package: str) -> Result:
        # Use process pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        # Break into smaller steps to avoid timeout
        steps = [
            ("eval", f"nix eval nixpkgs#{package} --json"),
            ("build", f"nix build nixpkgs#{package}"),
            ("install", f"nix profile install nixpkgs#{package}")
        ]
        
        for step_name, command in steps:
            result = await loop.run_in_executor(
                self.process_pool,
                self._run_command,
                command
            )
            
            if not result.success:
                return Result(
                    success=False,
                    error=f"Failed at {step_name}: {result.error}"
                )
            
            yield Progress(
                phase=step_name,
                percent=(steps.index((step_name, command)) + 1) / len(steps) * 100
            )
        
        return Result(success=True, package=package)

# backend/execution/smart_nix_executor.py
class SmartNixExecutor:
    """Intelligently chooses best execution strategy"""
    def __init__(self):
        self.native_api = NativeNixAPI()
        self.subprocess_api = SubprocessNixAPI()
        self.cache = ResultCache()
    
    async def execute(self, intent: ProcessedIntent) -> Result:
        # Try cache first
        cached = self.cache.get(intent)
        if cached and not intent.force_refresh:
            return cached
        
        # Choose best API
        api = self.native_api if self.native_api.available else self.subprocess_api
        
        # Execute with progress tracking
        result = None
        async for update in api.execute(intent):
            if isinstance(update, Progress):
                yield update
            else:
                result = update
        
        # Cache successful results
        if result and result.success:
            self.cache.set(intent, result)
        
        return result
```

## 3. Learning System Refactoring

### Current State (Data Collection Only)
```python
# backend/learning/learning_system.py
class LearningSystem:
    def __init__(self):
        self.db = sqlite3.connect("learning.db")
    
    def record_interaction(self, text, result):
        # Just saves to database, doesn't actually learn
        self.db.execute(
            "INSERT INTO interactions VALUES (?, ?, ?)",
            (datetime.now(), text, result)
        )
        self.db.commit()
    
    def get_suggestions(self, text):
        # Returns empty list - not implemented
        return []
```

### Refactored (Active Learning)
```python
# backend/learning/pattern_extractor.py
class PatternExtractor:
    """Extracts reusable patterns from successful interactions"""
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.clustering = DBSCAN(eps=0.3, min_samples=2)
    
    def extract_patterns(self, interactions: List[Interaction]) -> List[Pattern]:
        # Filter successful interactions
        successful = [i for i in interactions if i.success_score > 0.8]
        
        if len(successful) < 10:
            return []
        
        # Vectorize text
        texts = [i.normalized_text for i in successful]
        vectors = self.vectorizer.fit_transform(texts)
        
        # Cluster similar interactions
        clusters = self.clustering.fit_predict(vectors)
        
        # Extract patterns from each cluster
        patterns = []
        for cluster_id in set(clusters):
            if cluster_id == -1:  # Noise
                continue
            
            cluster_texts = [
                texts[i] for i, c in enumerate(clusters) if c == cluster_id
            ]
            
            pattern = self._extract_common_pattern(cluster_texts)
            if pattern:
                patterns.append(Pattern(
                    regex=pattern,
                    confidence=len(cluster_texts) / len(successful),
                    examples=cluster_texts[:5]
                ))
        
        return patterns

# backend/learning/intent_improver.py
class IntentImprover:
    """Improves intent recognition using learned patterns"""
    def __init__(self, base_recognizer: IntentRecognizer):
        self.base_recognizer = base_recognizer
        self.learned_patterns = []
        self.performance_tracker = PerformanceTracker()
    
    def update_patterns(self, new_patterns: List[Pattern]):
        """Safely integrate new patterns"""
        for pattern in new_patterns:
            # Test pattern performance on validation set
            improvement = self._test_pattern(pattern)
            
            if improvement > 0.02:  # 2% improvement threshold
                self.learned_patterns.append(pattern)
                logger.info(f"Added pattern: {pattern.regex} (+{improvement:.1%})")
    
    def recognize(self, text: str) -> Intent:
        # Try learned patterns first (they're more specific)
        for pattern in sorted(self.learned_patterns, key=lambda p: p.confidence, reverse=True):
            match = re.match(pattern.regex, text)
            if match:
                return Intent(
                    type=pattern.intent_type,
                    entity=match.group(1) if match.groups() else None,
                    confidence=pattern.confidence,
                    source="learned"
                )
        
        # Fall back to base recognizer
        return self.base_recognizer.recognize(text)

# backend/learning/active_learner.py
class ActiveLearner:
    """Orchestrates the learning pipeline"""
    def __init__(self):
        self.storage = InteractionStorage()
        self.extractor = PatternExtractor()
        self.improver = IntentImprover(base_recognizer)
        self.scheduler = LearningScheduler()
    
    async def learn_cycle(self):
        """Run learning cycle (scheduled every hour)"""
        # Get recent interactions
        recent = self.storage.get_recent(hours=24)
        
        if len(recent) < 50:  # Need enough data
            return
        
        # Extract patterns
        patterns = self.extractor.extract_patterns(recent)
        
        # Test and apply improvements
        self.improver.update_patterns(patterns)
        
        # Update metrics
        metrics = self.improver.performance_tracker.get_metrics()
        logger.info(f"Learning cycle complete. Accuracy: {metrics.accuracy:.1%}")
    
    def start(self):
        """Start background learning"""
        self.scheduler.schedule_recurring(
            self.learn_cycle,
            interval=timedelta(hours=1)
        )
```

## 4. Error Handling Refactoring

### Current State (Generic Errors)
```python
# Throughout the codebase
try:
    result = some_operation()
except Exception as e:
    return {"error": str(e)}  # Unhelpful to users!
```

### Refactored (Educational Error System)
```python
# backend/core/error_handler.py
class EducationalError(Exception):
    """Base class for user-friendly errors"""
    def __init__(self, message: str, suggestion: str, learn_more: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        self.learn_more = learn_more
        super().__init__(message)

class PackageNotFoundError(EducationalError):
    def __init__(self, package: str, similar: List[str]):
        message = f"Package '{package}' not found in nixpkgs"
        
        suggestion = "Try searching for the package first:\n"
        suggestion += f"  ask-nix 'search {package}'\n"
        
        if similar:
            suggestion += f"\nDid you mean one of these?\n"
            for sim in similar[:3]:
                suggestion += f"  - {sim}\n"
        
        learn_more = "https://search.nixos.org/packages"
        
        super().__init__(message, suggestion, learn_more)

# backend/core/error_translator.py
class ErrorTranslator:
    """Translates technical errors into educational messages"""
    def __init__(self):
        self.translations = {
            r"attribute '(.+)' missing": self._handle_missing_attribute,
            r"cannot coerce": self._handle_type_error,
            r"infinite recursion": self._handle_recursion,
            r"permission denied": self._handle_permission
        }
    
    def translate(self, technical_error: str) -> EducationalError:
        for pattern, handler in self.translations.items():
            match = re.search(pattern, technical_error, re.IGNORECASE)
            if match:
                return handler(match, technical_error)
        
        # Generic fallback
        return EducationalError(
            message="An unexpected error occurred",
            suggestion="Try breaking down your request into smaller steps",
            learn_more="ask-nix 'help troubleshooting'"
        )
    
    def _handle_missing_attribute(self, match, full_error):
        attribute = match.group(1)
        
        # Try to understand what they were looking for
        context = self._extract_context(full_error)
        
        if "package" in context:
            similar = self._find_similar_packages(attribute)
            return PackageNotFoundError(attribute, similar)
        else:
            return EducationalError(
                message=f"Configuration option '{attribute}' doesn't exist",
                suggestion=f"Search for available options:\n  ask-nix 'search options {attribute}'",
                learn_more="https://search.nixos.org/options"
            )

# backend/core/error_presenter.py
class ErrorPresenter:
    """Presents errors appropriately for each interface"""
    def __init__(self, persona_manager: PersonaManager):
        self.persona_manager = persona_manager
    
    def present(self, error: EducationalError, interface: str, persona: str) -> str:
        # Adapt to persona
        adapted_error = self.persona_manager.adapt_error(error, persona)
        
        if interface == "cli":
            return self._format_cli_error(adapted_error)
        elif interface == "voice":
            return self._format_voice_error(adapted_error)
        elif interface == "tui":
            return self._format_tui_error(adapted_error)
    
    def _format_cli_error(self, error: EducationalError) -> str:
        output = f"\n❌ {error.message}\n\n"
        output += f"💡 Suggestion:\n{error.suggestion}\n"
        
        if error.learn_more:
            output += f"\n📚 Learn more: {error.learn_more}\n"
        
        return output
```

## 5. Performance Optimization Refactoring

### Current State (Synchronous Blocking)
```python
# backend/api/server.py
@app.post("/process")
def process_request(request: Request):
    # Everything blocks the main thread
    text = request.text
    intent = nlp.process(text)  # Can take 1-2 seconds
    result = executor.execute(intent)  # Can take 5-30 seconds!
    return {"result": result}
```

### Refactored (Async with Progress)
```python
# backend/api/async_server.py
from fastapi import FastAPI, WebSocket
from asyncio import create_task, Queue
import uuid

app = FastAPI()

class RequestManager:
    def __init__(self):
        self.active_requests = {}
        self.progress_queues = {}
    
    async def process_async(self, request_id: str, text: str):
        """Process request asynchronously with progress tracking"""
        queue = Queue()
        self.progress_queues[request_id] = queue
        
        try:
            # Intent processing (fast)
            intent = await self.nlp.process_async(text)
            await queue.put(Progress(phase="intent", percent=10))
            
            # Validation (fast)
            validated = await self.validator.validate_async(intent)
            await queue.put(Progress(phase="validation", percent=20))
            
            # Execution (slow, but with progress)
            result = None
            async for update in self.executor.execute_async(validated):
                if isinstance(update, Progress):
                    # Map execution progress to 20-90%
                    update.percent = 20 + (update.percent * 0.7)
                    await queue.put(update)
                else:
                    result = update
            
            await queue.put(Progress(phase="complete", percent=100))
            self.active_requests[request_id] = result
            
        except Exception as e:
            await queue.put(Error(str(e)))
        finally:
            await queue.put(None)  # Signal completion

request_manager = RequestManager()

@app.post("/process")
async def process_request(request: Request):
    """Initiate async processing"""
    request_id = str(uuid.uuid4())
    
    # Start processing in background
    create_task(request_manager.process_async(request_id, request.text))
    
    # Return immediately
    return {
        "request_id": request_id,
        "status": "processing",
        "progress_url": f"/progress/{request_id}"
    }

@app.websocket("/progress/{request_id}")
async def progress_websocket(websocket: WebSocket, request_id: str):
    """Stream progress updates via WebSocket"""
    await websocket.accept()
    
    if request_id not in request_manager.progress_queues:
        await websocket.send_json({"error": "Invalid request ID"})
        await websocket.close()
        return
    
    queue = request_manager.progress_queues[request_id]
    
    while True:
        update = await queue.get()
        
        if update is None:  # Processing complete
            if request_id in request_manager.active_requests:
                result = request_manager.active_requests[request_id]
                await websocket.send_json({"type": "result", "data": result.dict()})
            break
        elif isinstance(update, Progress):
            await websocket.send_json({"type": "progress", "data": update.dict()})
        elif isinstance(update, Error):
            await websocket.send_json({"type": "error", "data": str(update)})
            break
    
    await websocket.close()
    
    # Cleanup
    del request_manager.progress_queues[request_id]
    if request_id in request_manager.active_requests:
        del request_manager.active_requests[request_id]
```

## Implementation Checklist

### Week 1: Foundation Refactoring
- [ ] Separate intent processing components
- [ ] Implement native API adapter pattern
- [ ] Create educational error system
- [ ] Set up async request handling

### Week 2: Testing & Integration
- [ ] Add integration tests for each component
- [ ] Performance benchmarks for native vs subprocess
- [ ] Error translation coverage tests
- [ ] Load testing for async endpoints

### Week 3: Learning System
- [ ] Implement pattern extraction
- [ ] Create intent improvement pipeline
- [ ] Set up A/B testing framework
- [ ] Deploy learning scheduler

### Week 4: Polish
- [ ] Complete persona adaptations
- [ ] Optimize caching strategies
- [ ] Fine-tune error messages
- [ ] Performance profiling

## Best Practices Applied

1. **Single Responsibility**: Each class has one clear purpose
2. **Dependency Injection**: Components receive dependencies, don't create them
3. **Async by Default**: Non-blocking operations throughout
4. **Progressive Enhancement**: Features gracefully degrade
5. **Fail Informatively**: Errors educate users
6. **Measure Everything**: Metrics guide decisions

## Conclusion

These refactoring patterns transform Nix for Humanity from a promising prototype into a production-ready system. The key themes are:

- **Separation of Concerns**: Breaking monoliths into focused components
- **Async Operations**: Never block on long-running tasks
- **Educational Errors**: Turn failures into learning opportunities
- **Active Learning**: Actually use collected data for improvement
- **Performance First**: Native API and smart caching

By following this guide, the codebase becomes more maintainable, testable, and performant while staying true to the consciousness-first philosophy.

---
*Remember: Refactor for clarity, not cleverness. The best code is code that others (including future you) can understand and modify with confidence.*