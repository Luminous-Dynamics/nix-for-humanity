# 🚨 CRITICAL: Nix Development Rules for Claude Code

## The Sacred Nix Commandments

### 1. NEVER USE PIP 🚫
**FORBIDDEN**:
```bash
pip install anything  # ❌ NEVER DO THIS
python -m pip install # ❌ ALSO FORBIDDEN
pip3 install         # ❌ ABSOLUTELY NOT
```

**CORRECT**:
```bash
nix develop          # ✅ Everything provided by Nix
nix-shell           # ✅ For specific environments
```

### 2. All Dependencies Through Nix
- Python packages: Defined in `flake.nix`
- System packages: Defined in `flake.nix`
- Voice dependencies: Already in flake.nix
- Research components: Already in flake.nix

### 3. If You See pip install Anywhere
1. It's a bug - fix it immediately
2. Update documentation to use Nix
3. Add the dependency to flake.nix instead

### 4. Voice Dependencies Are Already Included
In `flake.nix` development shell:
```nix
(python311.withPackages (ps: with ps; [
  openai-whisper
  sounddevice
  numpy
  pyaudio
  torch
  torchaudio
]))
piper-tts
portaudio
```

### 5. Proper Installation Flow
```bash
# For development
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
nix develop  # EVERYTHING is provided!

# For users (NixOS)
# Add to configuration.nix:
services.nixForHumanity.voice.enable = true;
```

### 6. Common Mistakes to Avoid
- ❌ Running `pip install -r requirements.txt`
- ❌ Creating virtual environments (venv, virtualenv)
- ❌ Using system Python instead of Nix Python
- ❌ Installing packages globally with pip
- ✅ Always use `nix develop` or `nix-shell`

### 7. If Dependencies Are Missing
1. Check if you're in nix develop: `echo $IN_NIX_SHELL`
2. Add missing deps to flake.nix, not pip
3. Exit and re-enter nix develop
4. Never resort to pip as a "quick fix"

## Remember
- Nix = Reproducible
- pip = Chaos
- Choose wisely!

## Files That Need pip References Removed
These files incorrectly mention pip and need updating:
- docs/VOICE_SETUP_GUIDE.md (partially fixed)
- docs/VOICE_TROUBLESHOOTING.md
- setup_voice.py
- Many test scripts
- Old documentation

## The Path Forward
All Python dependencies should be managed through:
1. `flake.nix` - Primary source of truth
2. `shell.nix` - For non-flake users
3. NixOS modules - For system-wide installation
4. NEVER through pip

---
*Last updated: 2025-08-08*
*Sacred Rule: In Nix we trust, pip we must not!*
