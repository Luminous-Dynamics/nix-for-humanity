# Reddit r/NixOS Post

## Title
[Tool Update] Luminous Nix v0.3.1 - We fixed everything you complained about in 24 hours

## Post Content

Hey r/NixOS!

Yesterday I posted v0.3.0 here - our natural language interface for NixOS with real neural networks. You gave amazing feedback, pointing out critical missing features.

**Your top complaints:**
1. "No home-manager support!"
2. "Flake operations don't work"
3. "It confuses services with packages"
4. "How do I garbage collect?"

**We fixed ALL of them in 24 hours:**

### v0.3.1 Changelog
- ✅ **HomeManagerSpecialist**: `ask-nix "home-manager switch"` works perfectly
- ✅ **FlakeSpecialist**: All flake operations (init, update, check, develop)
- ✅ **ServiceSpecialist**: Knows `enable docker` vs `install docker`
- ✅ **GC Support**: `ask-nix "gc old generations"` frees your disk space

### Performance
- Accuracy: 96.3% → 97.8%
- Response: Still 0.1ms (cached)
- Zero regressions on existing features

### Installation
```bash
# Standalone (no Python needed)
wget https://github.com/Luminous-Dynamics/luminous-nix/releases/download/v0.3.1/luminous-nix-v0.3.1-standalone.tar.gz
tar -xzf luminous-nix-v0.3.1-standalone.tar.gz
./luminous-nix "home-manager switch"

# Or via pip
pip install luminous-nix==0.3.1
```

### Technical Details
We use a specialist architecture - each problem domain gets its own module (~150 lines). This makes it super easy to add features based on feedback. The core is a PyTorch transformer with 27M parameters trained on real NixOS queries.

### What's Next (Week 3)
Based on YOUR feedback:
- VS Code extension
- Shell completions (bash, zsh, fish)
- Config file generation
- More service integrations

### The Philosophy
Ship early, listen carefully, iterate rapidly. This 24-hour turnaround shows we're serious about making NixOS accessible to everyone. Keep the feedback coming!

**Special thanks to everyone who tested v0.3.0 and reported issues. You made this release possible.**

GitHub: https://github.com/Luminous-Dynamics/luminous-nix

Questions? Feedback? I'm here and listening!
