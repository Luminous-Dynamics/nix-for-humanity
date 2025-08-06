# 🔨 Implementation Guide: From Research to Reality

*Step-by-step guide to implementing the research recommendations*

## Overview

This guide translates our research findings into concrete implementation steps. Each section includes code examples, file structures, and specific tasks.

## Phase 1: Unified Backend Foundation (Week 1-2)

### Step 1.1: Restructure Project Layout

```bash
nix-for-humanity/
├── backend/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── backend.py          # Main NixForHumanityBackend
│   │   ├── intent.py           # Intent recognition
│   │   ├── executor.py         # Safe command execution
│   │   └── knowledge.py        # Knowledge base
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── models.py           # Model management
│   │   ├── nlp.py              # NLP pipeline
│   │   └── speech.py           # STT/TTS
│   ├── learning/
│   │   ├── __init__.py
│   │   ├── preferences.py      # User preferences
│   │   └── feedback.py         # Feedback loop
│   └── api/
│       ├── __init__.py
│       └── schema.py           # Request/Response types
├── frontends/
│   ├── cli/                    # CLI adapter
│   ├── tui/                    # Textual UI
│   ├── voice/                  # Voice interface
│   └── api/                    # REST API
├── tests/
└── docs/
```

### Step 1.2: Implement Core Backend

```python
# backend/core/backend.py
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..api.schema import Request, Response
from .intent import IntentRecognizer
from .executor import SafeExecutor
from .knowledge import KnowledgeBase

class NixForHumanityBackend:
    """Unified backend for all Nix for Humanity operations"""
    
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        self.executor = SafeExecutor()
        self.knowledge = KnowledgeBase()
        self._init_nixos_api()
    
    def _init_nixos_api(self):
        """Initialize direct nixos-rebuild-ng API"""
        try:
            import sys
            # Find nixos-rebuild-ng path dynamically
            nixos_rebuild_path = self._find_nixos_rebuild_path()
            sys.path.insert(0, nixos_rebuild_path)
            
            from nixos_rebuild import nix, models
            self.nix_api = nix
            self.nix_models = models
            self._has_python_api = True
        except ImportError:
            self._has_python_api = False
            
    async def process_request(
        self, 
        request: Request
    ) -> Response:
        """Main entry point for all requests"""
        
        # 1. Recognize intent
        intent = await self.intent_recognizer.recognize(
            request.text, 
            request.context
        )
        
        # 2. Validate and plan
        plan = await self._plan_actions(intent, request)
        
        # 3. Execute if requested
        result = None
        if request.context.get('execute', False):
            result = await self.executor.execute(plan)
        
        # 4. Generate response
        response = Response(
            intent=intent,
            plan=plan,
            result=result,
            explanation=self._explain(intent, plan),
            suggestions=self._get_suggestions(intent, result)
        )
        
        # 5. Learn from interaction
        await self._learn(request, response)
        
        return response
```

### Step 1.3: Implement Intent Recognition

```python
# backend/core/intent.py
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional
import re

class IntentType(Enum):
    INSTALL_PACKAGE = "install_package"
    UPDATE_SYSTEM = "update_system"
    SEARCH_PACKAGE = "search_package"
    ROLLBACK = "rollback"
    CONFIGURE = "configure"
    EXPLAIN = "explain"
    UNKNOWN = "unknown"

@dataclass
class Intent:
    type: IntentType
    entities: Dict[str, Any]
    confidence: float
    raw_text: str

class IntentRecognizer:
    """Fast, local intent recognition"""
    
    def __init__(self):
        self._load_patterns()
        self._load_embeddings()
    
    async def recognize(
        self, 
        text: str, 
        context: Dict[str, Any]
    ) -> Intent:
        """Recognize intent from natural language"""
        
        # 1. Normalize text
        normalized = self._normalize(text)
        
        # 2. Try pattern matching first (fast)
        if intent := self._match_patterns(normalized):
            return intent
            
        # 3. Use embeddings for semantic matching
        if intent := await self._semantic_match(normalized):
            return intent
            
        # 4. Unknown intent
        return Intent(
            type=IntentType.UNKNOWN,
            entities={},
            confidence=0.0,
            raw_text=text
        )
    
    def _match_patterns(self, text: str) -> Optional[Intent]:
        """Fast regex-based pattern matching"""
        
        # Install patterns
        install_pattern = r'(install|add|get)\s+(\S+)'
        if match := re.search(install_pattern, text):
            return Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={'package': match.group(2)},
                confidence=0.9,
                raw_text=text
            )
        
        # Update patterns
        if any(word in text for word in ['update', 'upgrade']):
            return Intent(
                type=IntentType.UPDATE_SYSTEM,
                entities={},
                confidence=0.85,
                raw_text=text
            )
        
        return None
```

## Phase 2: AI Model Integration (Week 3-4)

### Step 2.1: Set Up Model Management

```python
# backend/ai/models.py
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

class ModelManager:
    """Lazy-loading model manager"""
    
    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._model_paths = self._find_model_paths()
    
    def _find_model_paths(self) -> Dict[str, Path]:
        """Find models in NixOS store"""
        # Models are provided by NixOS packages
        return {
            'whisper': Path('/run/current-system/sw/share/whisper/models/'),
            'piper': Path('/run/current-system/sw/share/piper/'),
            'spacy': Path('/run/current-system/sw/lib/python3.11/site-packages/spacy/'),
        }
    
    @property
    def whisper(self):
        """Get Whisper model (lazy load)"""
        if 'whisper' not in self._models:
            import whisper_cpp
            self._models['whisper'] = whisper_cpp.Whisper(
                model_path=self._model_paths['whisper'] / 'base.en'
            )
        return self._models['whisper']
    
    @property
    def embeddings(self):
        """Get sentence transformer (lazy load)"""
        if 'embeddings' not in self._models:
            from sentence_transformers import SentenceTransformer
            self._models['embeddings'] = SentenceTransformer(
                'all-MiniLM-L6-v2',
                cache_folder='/tmp/nix-humanity-models'
            )
        return self._models['embeddings']
```

### Step 2.2: Implement NLP Pipeline

```python
# backend/ai/nlp.py
import spacy
from typing import List, Dict, Any
import nltk

class NLPPipeline:
    """Multi-stage NLP processing"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self._init_nltk()
    
    def _init_nltk(self):
        """Initialize NLTK data"""
        nltk_data = Path.home() / 'nltk_data'
        if not nltk_data.exists():
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
    
    def process(self, text: str) -> Dict[str, Any]:
        """Full NLP pipeline"""
        
        # 1. Preprocess with NLTK
        tokens = nltk.word_tokenize(text.lower())
        tokens = [t for t in tokens if t not in nltk.corpus.stopwords.words('english')]
        
        # 2. NER with spaCy
        doc = self.nlp(text)
        entities = {
            'packages': [ent.text for ent in doc.ents if ent.label_ == "PRODUCT"],
            'paths': [ent.text for ent in doc.ents if '/' in ent.text],
            'numbers': [ent.text for ent in doc.ents if ent.label_ == "CARDINAL"]
        }
        
        # 3. Dependency parsing for commands
        root_verb = None
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                root_verb = token.lemma_
                break
        
        return {
            'tokens': tokens,
            'entities': entities,
            'root_verb': root_verb,
            'doc': doc
        }
```

### Step 2.3: Implement Voice Pipeline

```python
# backend/ai/speech.py
import asyncio
import numpy as np
from typing import AsyncIterator, Optional
import pyaudio
import webrtcvad

class VoicePipeline:
    """Low-latency voice processing"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.vad = webrtcvad.Vad(3)  # Aggressive filtering
        self.audio = pyaudio.PyAudio()
        
    async def listen(self) -> AsyncIterator[str]:
        """Stream transcribed text as it's spoken"""
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=480  # 30ms chunks
        )
        
        try:
            buffer = []
            speaking = False
            
            while True:
                frame = stream.read(480, exception_on_overflow=False)
                is_speech = self.vad.is_speech(frame, 16000)
                
                if is_speech:
                    if not speaking:
                        speaking = True
                    buffer.append(frame)
                elif speaking:
                    # End of utterance
                    audio_data = b''.join(buffer)
                    text = await self._transcribe(audio_data)
                    if text:
                        yield text
                    buffer = []
                    speaking = False
                    
                await asyncio.sleep(0.01)  # Prevent blocking
                
        finally:
            stream.close()
    
    async def _transcribe(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio to text"""
        # Convert to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Run Whisper
        result = await asyncio.to_thread(
            self.model_manager.whisper.transcribe,
            audio_np
        )
        
        return result.get('text', '').strip()
    
    async def speak(self, text: str):
        """Convert text to speech"""
        # Use Piper TTS
        audio = await asyncio.to_thread(
            self.model_manager.piper.synthesize,
            text
        )
        
        # Play audio
        stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=22050,
            output=True
        )
        stream.write(audio.tobytes())
        stream.close()
```

## Phase 3: Frontend Development (Week 5-6)

### Step 3.1: CLI Adapter

```python
# frontends/cli/adapter.py
import asyncio
import argparse
from backend.api.schema import Request, Response
from backend.core.backend import NixForHumanityBackend

class CLIAdapter:
    """Thin CLI adapter for the backend"""
    
    def __init__(self):
        self.backend = NixForHumanityBackend()
        
    async def run(self, args: List[str]):
        """Process CLI arguments"""
        
        parser = argparse.ArgumentParser()
        parser.add_argument('query', nargs='+', help='Natural language query')
        parser.add_argument('--execute', action='store_true', help='Execute commands')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
        
        parsed = parser.parse_args(args)
        query = ' '.join(parsed.query)
        
        # Create request
        request = Request(
            text=query,
            context={
                'execute': parsed.execute and not parsed.dry_run,
                'dry_run': parsed.dry_run,
            },
            frontend='cli',
            session_id=self._get_session_id()
        )
        
        # Process
        response = await self.backend.process_request(request)
        
        # Display
        self._display_response(response)
    
    def _display_response(self, response: Response):
        """Format response for terminal"""
        
        print(f"\n🎯 Intent: {response.intent.type.value}")
        print(f"📊 Confidence: {response.intent.confidence:.0%}")
        
        if response.explanation:
            print(f"\n💡 {response.explanation}")
        
        if response.plan:
            print("\n📋 Plan:")
            for i, action in enumerate(response.plan, 1):
                print(f"  {i}. {action}")
        
        if response.result:
            print(f"\n✅ Result: {response.result}")
        
        if response.suggestions:
            print("\n💭 Suggestions:")
            for suggestion in response.suggestions:
                print(f"  • {suggestion}")
```

### Step 3.2: Textual TUI

```python
# frontends/tui/app.py
from textual.app import App, ComposeResult
from textual.widgets import Input, Static, ListView, ListItem
from textual.containers import Container, Horizontal, Vertical
from backend.core.backend import NixForHumanityBackend

class NixTUI(App):
    """Rich terminal UI for Nix for Humanity"""
    
    CSS = """
    Input {
        dock: bottom;
        height: 3;
    }
    
    #output {
        overflow-y: scroll;
        height: 100%;
    }
    
    .intent {
        color: $success;
        text-style: bold;
    }
    
    .command {
        color: $warning;
        margin: 1;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.backend = NixForHumanityBackend()
        
    def compose(self) -> ComposeResult:
        yield Container(
            ListView(id="output"),
            Input(placeholder="Ask me anything about NixOS..."),
            id="main"
        )
    
    async def on_input_submitted(self, event):
        """Process user input"""
        query = event.value
        input_widget = self.query_one(Input)
        input_widget.value = ""
        
        # Add to output
        output = self.query_one("#output")
        output.append(ListItem(Static(f"You: {query}")))
        
        # Process
        request = Request(
            text=query,
            context={'execute': False},
            frontend='tui',
            session_id=self.session_id
        )
        
        response = await self.backend.process_request(request)
        
        # Display response
        output.append(ListItem(
            Static(
                f"[bold cyan]Intent:[/] {response.intent.type.value}\n"
                f"[bold green]Response:[/] {response.explanation}",
                markup=True
            )
        ))
```

## Phase 4: Integration & Testing (Week 7-8)

### Step 4.1: Integration Tests

```python
# tests/test_integration.py
import pytest
import asyncio
from backend.core.backend import NixForHumanityBackend
from backend.api.schema import Request

@pytest.mark.asyncio
async def test_install_firefox():
    """Test package installation flow"""
    backend = NixForHumanityBackend()
    
    request = Request(
        text="install firefox",
        context={'execute': False},
        frontend='test',
        session_id='test-123'
    )
    
    response = await backend.process_request(request)
    
    assert response.intent.type.value == 'install_package'
    assert response.intent.entities['package'] == 'firefox'
    assert response.confidence > 0.8
    assert 'nix profile install' in str(response.plan)

@pytest.mark.asyncio
async def test_voice_pipeline():
    """Test voice processing"""
    from backend.ai.speech import VoicePipeline
    from backend.ai.models import ModelManager
    
    models = ModelManager()
    voice = VoicePipeline(models)
    
    # Test TTS
    await voice.speak("Hello, I am Nix for Humanity")
    
    # Test STT would require audio input
    # This is better tested with fixture audio files
```

### Step 4.2: Performance Benchmarks

```python
# tests/benchmark.py
import time
import asyncio
from backend.core.backend import NixForHumanityBackend

async def benchmark_intent_recognition():
    """Benchmark intent recognition speed"""
    backend = NixForHumanityBackend()
    
    queries = [
        "install firefox",
        "update my system",
        "search for python packages",
        "rollback to previous generation",
        "explain what a flake is"
    ]
    
    times = []
    for query in queries * 100:  # 500 total
        start = time.perf_counter()
        
        request = Request(
            text=query,
            context={},
            frontend='benchmark',
            session_id='bench'
        )
        response = await backend.process_request(request)
        
        times.append(time.perf_counter() - start)
    
    print(f"Average: {sum(times)/len(times)*1000:.1f}ms")
    print(f"P95: {sorted(times)[int(len(times)*0.95)]*1000:.1f}ms")
    print(f"Max: {max(times)*1000:.1f}ms")
```

## Migration Checklist

- [ ] Create new directory structure
- [ ] Move existing code to appropriate modules
- [ ] Implement unified backend
- [ ] Add intent recognition
- [ ] Integrate nixos-rebuild-ng API
- [ ] Add AI models
- [ ] Create CLI adapter
- [ ] Create TUI with Textual
- [ ] Add voice pipeline
- [ ] Write integration tests
- [ ] Run performance benchmarks
- [ ] Update documentation

## Next Steps

1. **Start with backend core** - Get the foundation right
2. **Add one frontend at a time** - CLI first, then TUI
3. **Integrate AI incrementally** - Start with embeddings
4. **Test continuously** - Every component should have tests
5. **Measure performance** - Track improvements

---

*"The best code is the code that's easy to understand, test, and change."*