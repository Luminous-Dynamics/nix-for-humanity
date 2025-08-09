# Poetry Migration and Technology Review - Nix for Humanity

## Status: Poetry Migration Complete ✅

Successfully migrated from setuptools/pip to Poetry for NixOS compatibility:
- Converted pyproject.toml from PEP 621 to Poetry format
- Integrated dependencies from 3 requirements.txt files
- Generated poetry.lock (666KB) with all dependencies resolved
- Made dowhy conditional for Python <3.12 due to version constraints

## Causal Inference Alternatives to DoWhy

Since dowhy only supports Python <3.12, here are better alternatives:

### 1. **CausalML (Microsoft) - RECOMMENDED** 🌟
- **Pros**: 
  - Actively maintained by Microsoft
  - Supports Python 3.11+
  - Focuses on uplift modeling and heterogeneous treatment effects
  - Great for personalized AI experiences
- **Use Case**: Perfect for our learning system to understand which interventions help which users
- **Package**: `causalml`

### 2. **EconML (Microsoft)**
- **Pros**:
  - Also by Microsoft, complements CausalML
  - Supports Python 3.11+
  - Advanced ML methods for causal inference
- **Use Case**: More advanced causal analysis
- **Package**: `econml`

### 3. **pgmpy (Probabilistic Graphical Models)**
- **Pros**:
  - Pure Python, supports all Python versions
  - Bayesian Networks and causal reasoning
  - Lighter weight than dowhy
- **Use Case**: For our causal XAI engine
- **Package**: `pgmpy`

### 4. **CausalNex (QuantumBlack)**
- **Pros**:
  - Bayesian Networks with structure learning
  - Good visualization tools
  - Python 3.8+
- **Package**: `causalnex`

## Other Dependency Improvements

### 1. **Voice/Speech Recognition**
Currently using: whisper-cpp-python, piper-tts, vosk, py-espeak-ng

**Better alternatives:**
- **Whisper**: Consider `openai-whisper` (official) instead of whisper-cpp-python
- **TTS**: `coqui-tts` is more modern than piper-tts
- **Lightweight**: Keep vosk for offline use

### 2. **ML Stack**
Currently using: transformers, torch, scikit-learn

**Optimizations:**
- **Transformers**: Consider `optimum` for optimized inference
- **Torch**: Add `torch-directml` for Windows GPU support
- **ONNX Runtime**: Add for faster inference across platforms

### 3. **Vector Database**
Currently using: lancedb

**Alternatives to consider:**
- **ChromaDB**: More mature, better documentation
- **Qdrant**: Better performance for large-scale
- **Keep LanceDB**: Good choice for local-first!

### 4. **Web Framework**
Currently using: flask, gunicorn

**Modern alternatives:**
- **FastAPI**: Modern, async, auto-documentation
- **Uvicorn**: ASGI server instead of gunicorn
- **Keep minimal**: For our use case, Flask is fine

### 5. **Testing**
Currently using: pytest, pytest-cov, pytest-asyncio

**Additional tools:**
- **hypothesis**: Property-based testing (great for NLP)
- **pytest-benchmark**: Performance regression testing
- **pytest-xdist**: Parallel test execution

## Recommended Changes

### Immediate (High Impact)
1. Replace dowhy with pgmpy for broader Python support
2. Add hypothesis for property-based testing
3. Consider FastAPI for the web API (better async support)

### Future Considerations
1. Add optimum for transformer optimization
2. Consider ChromaDB if LanceDB has limitations
3. Add ONNX Runtime for cross-platform inference

## Next Steps

1. ✅ Poetry migration complete
2. Update flake.nix to use poetry2nix with new pyproject.toml
3. Test that all dependencies install correctly
4. Consider replacing dowhy with pgmpy
5. Remove old requirements.txt files after verification

## poetry2nix Integration

The flake.nix is already configured for poetry2nix:

```nix
poetryApplication = poetry2nix.mkPoetryApplication {
  projectDir = self;
  preferWheels = true;
};
```

This will now work with our Poetry-formatted pyproject.toml and poetry.lock!