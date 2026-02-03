# Symthaea Feature Matrix

**Version:** 0.5.0
**Last Updated:** February 2026
**Total Features:** 52

---

## Quick Start

```bash
# Minimal build (library only)
cargo build

# With shell TUI
cargo build --features shell

# With embeddings
cargo build --features embeddings

# Full build (all features)
cargo build --features full
```

---

## Feature Categories

### Binary Support Features

These features enable specific executables:

| Feature | Binary | Dependencies | Purpose |
|---------|--------|--------------|---------|
| `service` | `symthaea` | clap | Background service daemon |
| `shell` | `symthaea-shell` | crossterm, ratatui | Interactive TUI |
| `gui` | `symthaea-gui` | eframe, egui | Graphical interface |
| `demo` | `symthaea-mind`, `symthaea-repl`, `demo-sentinel` | clap, ctrlc | Demo binaries |
| `api_module` | `symthaea-api` | axum, tower-http | HTTP API server |
| `full` | All of above | All of above | Everything |

---

### Voice & Audio Features

| Feature | Dependencies | Purpose |
|---------|--------------|---------|
| `voice-tts` | ort, hound, hf-hub | Text-to-Speech (Kokoro ONNX, CPU) |
| `voice-tts-cuda` | voice-tts + ort/cuda | TTS with CUDA acceleration |
| `voice-tts-async` | voice-tts + futures | Async/streaming TTS |
| `voice-stt` | symthaea-stt, hound | Speech-to-Text (HDC+LTC+CfC) |
| `audio-sentinel` | symthaea-sentinel | Zero-shot audio pattern recognition |
| `audio` | voice-tts + rodio | Full audio I/O with playback |
| `audio-cuda` | voice-tts-cuda + rodio | Audio with GPU acceleration |

---

### AI/ML Features

| Feature | Dependencies | Purpose |
|---------|--------------|---------|
| `embeddings` | tokenizers, ort, hf-hub | Qwen3/BGE text embeddings (ONNX) |
| `vision` | ort, hf-hub | SigLIP image embeddings (ONNX) |
| `perception` | embeddings + vision | Full multimodal perception |
| `neural-bridge` | candle-*, tokenizers, hf-hub, safetensors, half | BGE-M3 via Candle (pure Rust) |
| `neural-bridge-cuda` | neural-bridge + candle-*/cuda | Candle with CUDA |
| `semantic-burn` | burn, burn-ndarray | Pure Rust semantic encoder |
| `pyphi` | pyo3 | PyPhi integration for exact IIT validation |

---

### Infrastructure Features

| Feature | Dependencies | Purpose |
|---------|--------------|---------|
| `swarm` | iroh | P2P tensor streaming (Iroh 0.96+) |
| `notifications` | zbus | D-Bus desktop notifications |
| `systemd` | libsystemd | Systemd socket activation |
| `desktop` | notifications + systemd | Full desktop integration |
| `mycelix` | sha3 | Mycelix governance (hashing only) |

---

### Database Features (Deferred)

These are compile guards only - dependencies not yet added:

| Feature | Purpose | Status |
|---------|---------|--------|
| `qdrant` | Vector database | Deferred |
| `datalog` | Datalog reasoning | Deferred |
| `lance` | LanceDB vector storage | Deferred |
| `duck` | DuckDB analytics | Deferred |
| `hdf5` | HDF5 file loading | Deferred |

---

### Module Compilation Gates

These enable specific modules and examples:

| Feature | Purpose |
|---------|---------|
| `integration_module` | Integration patterns |
| `observability_module` | Metrics and tracing |
| `full_consciousness` | Extended consciousness submodules |
| `full_perception` | Extended perception submodules |
| `full_language` | Advanced grammar/parsers |
| `benchmarks_module` | Benchmark examples |
| `consciousness_module` | Consciousness examples |
| `embeddings_module` | Embedding examples |
| `language_module` | Language examples |
| `brain_module` | Brain subsystem examples |
| `soul_module` | Soul/identity examples |
| `school_module` | Learning examples |
| `physiology_module` | Physiology integration |
| `magi_loop` | MAGI world-grounded prediction |
| `partnership_module` | Phi_dyad computation |
| `web_research_module` | Epistemic verification |

---

## Common Feature Combinations

### For Development

```bash
# Quick iteration
cargo build

# With TUI for testing
cargo build --features shell

# With embeddings for semantic tests
cargo build --features embeddings,embeddings_module
```

### For Research

```bash
# Consciousness experiments
cargo build --features consciousness_module,benchmarks_module

# With PyPhi validation
cargo build --features pyphi,consciousness_module

# Full perception stack
cargo build --features perception
```

### For Production

```bash
# Service daemon
cargo build --release --features service

# API server
cargo build --release --features api_module

# Full deployment
cargo build --release --features full
```

---

## Feature Dependency Graph

```
full
├── service (clap)
├── shell (crossterm, ratatui)
├── gui (eframe, egui)
└── demo (clap, ctrlc)

audio
└── voice-tts (ort, hound, hf-hub)
    └── voice-tts-cuda (ort/cuda)
        └── audio-cuda (rodio)

perception
├── embeddings (tokenizers, ort, hf-hub)
└── vision (ort, hf-hub)

neural-bridge
├── candle-core
├── candle-nn
├── candle-transformers
├── tokenizers
├── hf-hub
├── safetensors
└── half
    └── neural-bridge-cuda (candle-*/cuda)

desktop
├── notifications (zbus)
└── systemd (libsystemd)
```

---

## Examples by Required Features

| Features Required | Example Count | Examples |
|-------------------|---------------|----------|
| `benchmarks_module` | 9 | causal_tower_test, cognitive_loop_validation, etc. |
| `consciousness_module` | 10 | phi_crossvalidation, meta_consciousness_conversation, etc. |
| `language_module` | 7 | conscious_nixos_assistant, llm_integration_test, etc. |
| `embeddings_module` | 4 | semantic_consciousness, toddler_test, etc. |
| `brain_module` + `embeddings_module` | 3 | hippocampus_integration, prefrontal_integration, etc. |
| `magi_loop` | 4 | magi_simulation, dream_feedback_experiment, etc. |
| `perception` | 1 | multimodal_io_test |
| `neural-bridge` | 1 | modern_embeddings_demo |
| (none) | 2 | full_pipeline, meditation_phi_analysis |

---

## Test Coverage by Feature

| Category | Features | Tested | Coverage |
|----------|----------|--------|----------|
| Binary Support | 6 | 0 | 0% |
| Voice/Audio | 7 | 0 | 0% |
| AI/ML | 7 | 2 | 29% |
| Infrastructure | 5 | 0 | 0% |
| Module Gates | 20 | 8 | 40% |

**Priority for testing:** Binary features (0% coverage is critical gap)

---

## Notes

- **Default features:** None (`default = []`)
- **CUDA features:** Require CUDA toolkit installed
- **PyPhi feature:** Requires Python environment with pyphi
- **Deferred database features:** Empty compile guards, no dependencies yet

---

*For architecture details, see [ARCHITECTURE.md](architecture/ARCHITECTURE_DEEP_DIVE.md)*
*For current status, see [HONEST_STATUS.md](HONEST_STATUS.md)*
