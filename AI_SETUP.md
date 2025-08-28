# 🤖 AI Integration Setup Guide

## Overview

Luminous Nix includes optional AI integration for advanced natural language understanding and intelligent assistance. This enables the system to handle complex queries, provide contextual help, and learn from usage patterns.

## Quick Setup

### 1. Install Ollama (5 minutes)

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### 2. Download AI Model (10-15 minutes)

```bash
# Start Ollama service
ollama serve &

# Download recommended model (Mistral 7B - 4.1GB)
ollama pull mistral:7b

# Alternative: Smaller, faster model (2.8GB)
ollama pull gemma:2b

# Alternative: Larger, smarter model (7.7GB)
ollama pull llama2:13b
```

### 3. Test AI Integration

```bash
# Test Ollama is working
ollama run mistral:7b "What is NixOS?"

# Test with Luminous Nix
LUMINOUS_AI_ENABLED=true ask-nix "explain how NixOS works"
```

## Detailed Setup

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: 5-10GB for models
- **CPU**: Any modern processor (GPU optional but faster)

### Installation Options

#### Option 1: System-wide Installation (Recommended)
```bash
# Install via official script
curl -fsSL https://ollama.com/install.sh | sh

# Start as system service
sudo systemctl enable ollama
sudo systemctl start ollama
```

#### Option 2: User Installation
```bash
# Download binary
wget https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64
chmod +x ollama-linux-amd64
mv ollama-linux-amd64 ~/.local/bin/ollama

# Add to PATH
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

#### Option 3: NixOS Installation
```nix
# Add to configuration.nix
environment.systemPackages = with pkgs; [
  ollama
];

# Or use nix-shell
nix-shell -p ollama
```

### Model Selection Guide

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| gemma:2b | 2.8GB | Fast | Good | Quick responses, low RAM |
| mistral:7b | 4.1GB | Medium | Better | Balanced performance (RECOMMENDED) |
| llama2:13b | 7.7GB | Slow | Best | Complex queries, best understanding |
| codellama:7b | 3.8GB | Medium | Good | Code-specific tasks |

### Configuration

#### Environment Variables
```bash
# Enable AI for all commands
export LUMINOUS_AI_ENABLED=true

# Set default model
export OLLAMA_MODEL=mistral:7b

# Set Ollama host (if not localhost)
export OLLAMA_HOST=http://localhost:11434
```

#### Permanent Configuration
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export LUMINOUS_AI_ENABLED=true' >> ~/.bashrc
echo 'export OLLAMA_MODEL=mistral:7b' >> ~/.bashrc
source ~/.bashrc
```

## Usage Examples

### Basic AI Queries
```bash
# Ask complex questions
LUMINOUS_AI_ENABLED=true ask-nix "what's the difference between nix-env and nix profile?"

# Get explanations
LUMINOUS_AI_ENABLED=true ask-nix "explain NixOS generations"

# Troubleshooting help
LUMINOUS_AI_ENABLED=true ask-nix "my system won't boot after update"
```

### Advanced Features

#### Socratic Mode (Ask clarifying questions)
```bash
ask-nix --ask "I need an editor"
# AI asks: "What kind of editing? Code, text, or markdown?"
```

#### Persona-based Responses
```bash
# Technical explanations
ask-nix --persona developer "explain flakes"

# Simple explanations
ask-nix --persona grandma "what is NixOS?"
```

#### Context-Aware Help
```bash
# AI remembers conversation context
ask-nix "install python"
ask-nix "now add numpy"  # Understands "add" means install numpy
```

## Troubleshooting

### "AI not available" Error
1. Check Ollama is running: `ollama list`
2. Start Ollama: `ollama serve &`
3. Verify model is downloaded: `ollama list`

### Slow Responses
1. Use smaller model: `ollama pull gemma:2b`
2. Check system resources: `htop`
3. Close other applications

### Connection Errors
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve &
```

### Memory Issues
```bash
# Use smaller model
export OLLAMA_MODEL=gemma:2b

# Limit memory usage
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
```

## Privacy & Security

### Local Processing
- All AI processing happens locally
- No data sent to cloud services
- Models stored in `~/.ollama/models/`

### Resource Control
```bash
# Limit CPU usage
export OLLAMA_NUM_THREAD=4

# Disable GPU
export CUDA_VISIBLE_DEVICES=-1
```

### Model Management
```bash
# List installed models
ollama list

# Remove unused models
ollama rm model-name

# Update models
ollama pull mistral:7b
```

## Performance Optimization

### GPU Acceleration (Optional)
```bash
# Check CUDA support
nvidia-smi

# Ollama automatically uses GPU if available
# No configuration needed
```

### CPU Optimization
```bash
# Use all CPU cores
export OLLAMA_NUM_THREAD=$(nproc)

# Reduce response time
export OLLAMA_KEEP_ALIVE=5m
```

## Integration with Luminous Nix

### How It Works
1. Query received by Luminous Nix
2. If pattern matching fails, query sent to AI
3. AI interprets intent and entities
4. Response converted to NixOS commands
5. Commands executed or explained

### Benefits
- Handles ambiguous queries
- Provides explanations
- Suggests alternatives
- Learns from usage

### Limitations
- Requires additional resources
- Slower than pattern matching
- May occasionally misunderstand

## Future Enhancements

### Planned Features
- Fine-tuning on NixOS documentation
- Custom models for better accuracy
- Voice integration with AI
- Learning from user corrections

### Community Models
Future support for community-trained models specific to NixOS and package management.

## Summary

AI integration transforms Luminous Nix from a smart command translator into an intelligent assistant that truly understands your needs. While optional, it significantly enhances the natural language experience and makes NixOS accessible to everyone.

### Quick Start Commands
```bash
# One-line setup
curl -fsSL https://ollama.com/install.sh | sh && ollama pull mistral:7b

# Test it works
LUMINOUS_AI_ENABLED=true ask-nix "help me set up a web server"
```

For any issues, refer to the [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) or open an issue on GitHub.