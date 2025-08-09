# 🤖 Nix for Humanity Setup in Claude Code

## 🚀 Quick Start (NEW!)

We've created a simple setup script to handle Claude Code's timeout issues:

```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
./quick-nix-setup.sh
```

This gives you options:
1. **Minimal shell** - Quick 50MB download for testing
2. **Check cache** - See if deps are already downloaded
3. **Mock mode** - No downloads needed
4. **Full setup** - Instructions for outside Claude Code
5. **Help** - Understand the options

## The Download Challenge

Claude Code has a 2-minute execution timeout, but `nix develop` needs to download ~2.8GB of dependencies (573MB compressed). This WILL timeout on first run.

### Solutions (In Order of Preference)

#### 1. Use the Minimal Shell (Recommended for Claude Code)
```bash
nix-shell shell-voice-minimal.nix
```
- Downloads only ~50MB
- Includes Python, audio libraries, basic tools
- Can use Python venv for additional packages if needed

#### 2. Mock Mode (No Downloads)
```bash
export NIX_VOICE_MOCK=true
export NIX_HUMANITY_PYTHON_BACKEND=true
./bin/nix-voice
```

#### 3. Pre-download Outside Claude Code
Run this in a regular terminal (not Claude Code):
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
nix develop  # Let it download everything
# or
./scripts/prefetch-dependencies.sh
```

Once cached, Claude Code can use `nix develop` instantly!

#### 4. Use Binary Caches
Configure in `~/.config/nix/nix.conf`:
```
substituters = https://cache.nixos.org https://nix-community.cachix.org
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs=
```

## Dependency Sizes (FYI)

Major downloads when using `nix develop`:
- PyTorch + CUDA: ~1.5GB
- Whisper models: ~300MB
- Node.js ecosystem: ~200MB
- Rust toolchain: ~400MB
- Various Python packages: ~400MB

Total: ~2.8GB downloaded, ~6GB unpacked

## Quick Commands Once Environment is Ready

```bash
# CLI with natural language
./bin/ask-nix "install firefox"

# Beautiful TUI
./bin/nix-tui

# Voice interface
./bin/nix-voice

# Run tests
pytest tests/
```

## Important Files

- `flake.nix` - Main development environment (poetry2nix + all deps)
- `pyproject.toml` - Python dependencies (managed by poetry2nix)
- `shell-voice-minimal.nix` - Lightweight shell for Claude Code
- `.claude/NIX_DEVELOPMENT_RULES.md` - Sacred commandments (NO PIP!)

## Sacred Rules

1. **NEVER use pip** - Everything through Nix/poetry2nix
2. **Use minimal shell** in Claude Code to avoid timeouts
3. **Pre-download deps** outside Claude Code when possible
4. **Mock mode** for quick testing without deps

## Troubleshooting

### "nix develop" times out
- Expected in Claude Code! Use `./quick-nix-setup.sh` instead

### "command not found: whisper"
- You're not in the nix environment. Run option 1 or 3 from quick-nix-setup.sh

### "No module named 'textual'"
- The minimal shell doesn't include everything. Either:
  - Use mock mode for testing
  - Pre-download full environment outside Claude Code

---

*Note: Claude Code's 2-minute timeout is the main challenge. On a regular system, everything works smoothly!*