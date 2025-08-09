# 🎬 Demo Materials Guide - Nix for Humanity

This guide explains how to create professional demo materials (videos, GIFs, screenshots) for showcasing the enhanced TUI.

## 📸 Quick Start

```bash
# Make scripts executable
chmod +x create-demo-materials.sh capture-tui-screenshots.py

# Option 1: Create animated GIF demo
./create-demo-materials.sh
# Select option 1 (VHS) or 2 (Built-in demo)

# Option 2: Generate screenshots
python capture-tui-screenshots.py

# Option 3: Run demo mode
./run-enhanced-tui.sh
# Press F5 to start automated demo
```

## 🎯 Demo Creation Methods

### 1. VHS (Recommended for GIFs) ⭐

**Install VHS:**
```bash
# macOS
brew install vhs

# NixOS
nix-env -iA nixpkgs.vhs

# Other Linux
wget https://github.com/charmbracelet/vhs/releases/latest/download/vhs_Linux_x86_64.tar.gz
```

**Use the provided tape:**
```bash
vhs demo-tui.tape
# Creates: enhanced-tui-demo.gif
```

**Customize the demo:**
Edit `demo-tui.tape` to change:
- Terminal size and theme
- Commands to showcase
- Timing between actions
- Output format (GIF, MP4, WebM)

### 2. Built-in Demo Mode 🤖

The TUI includes an automated demo mode that runs through all features:

```bash
# Start TUI with auto-demo
python -c "
import sys
sys.argv.append('--demo')
from nix_humanity.ui.enhanced_main_app_with_demo import EnhancedNixForHumanityTUIWithDemo
app = EnhancedNixForHumanityTUIWithDemo()
app.run()
"
```

**Features:**
- Automated command typing
- Perfect timing
- Narrative overlays
- Consistent every time

**Recording the demo:**
While demo mode runs, use any screen recorder:
- OBS Studio
- SimpleScreenRecorder
- QuickTime (macOS)
- Built-in screen recorder

### 3. Manual Demo Recording 🎥

**Best practices:**
1. Clean terminal first: `clear && printf '\e[3J'`
2. Set consistent size: `resize -s 40 120`
3. Use good font: Fira Code, JetBrains Mono
4. Dark theme recommended: Dracula, Nord, Solarized

**Demo script sequence:**
```bash
./run-enhanced-tui.sh

# Basic interaction
help
install firefox

# Voice visualization
voice on
# (Show waveforms)

# Learning mode  
learn about nix generations
# (Show progress bar growing)

# Build flow state (5+ commands)
search editor
update system
list packages
check network
clean cache
# (Sacred geometry appears)

# Zen mode
Ctrl+Z
# (Minimal UI)
Ctrl+Z
# (Back to normal)

# Exit
Ctrl+C
```

### 4. Screenshot Generation 📷

Generate static images of different states:

```bash
python capture-tui-screenshots.py
```

Creates screenshots in `./screenshots/`:
- `01-idle-state.svg` - Default view
- `02-listening.svg` - Listening state
- `03-thinking-particles.svg` - Processing with particles
- `04-voice-active.svg` - Voice visualization
- `05-learning-mode.svg` - Learning progress
- `06-flow-state.svg` - Flow with sacred geometry
- `07-error-state.svg` - Error handling

**Convert to PNG:**
```bash
# Using ImageMagick
for f in screenshots/*.svg; do
    convert -density 300 "$f" "${f%.svg}.png"
done

# Using Inkscape
for f in screenshots/*.svg; do
    inkscape "$f" --export-png="${f%.svg}.png" --export-dpi=300
done
```

## 🎨 Creating Professional Demos

### Terminal Setup

```bash
# Optimal terminal settings
Terminal: Alacritty, iTerm2, or Kitty
Font: Fira Code 14-16pt
Size: 120x40 characters (1200x800 pixels)
Theme: Dracula or Nord
Background: Slightly transparent (95% opacity)
```

### Recording Settings

**For GIFs:**
- FPS: 10-15 (smaller file size)
- Resolution: 1200x800 max
- Duration: 30-90 seconds
- Colors: 256 (optimized palette)

**For Videos:**
- FPS: 30-60 (smooth animations)
- Resolution: 1920x1080
- Codec: H.264 or H.265
- Bitrate: 5-10 Mbps

### Post-Processing

**Optimize GIF size:**
```bash
# Using gifsicle
gifsicle -O3 --colors 256 input.gif > output.gif

# Using ffmpeg (better quality)
ffmpeg -i input.mp4 -vf "fps=15,scale=1000:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i input.mp4 -i palette.png -filter_complex "fps=15,scale=1000:-1:flags=lanczos[x];[x][1:v]paletteuse" output.gif
```

**Add captions:**
```bash
# Using ffmpeg
ffmpeg -i demo.mp4 -vf "drawtext=text='Nix for Humanity':fontsize=30:fontcolor=white:x=10:y=10" output.mp4
```

## 📊 Demo Content Checklist

Essential features to showcase:

- [ ] **Consciousness Orb** - Breathing animation
- [ ] **Natural Language** - "install firefox" 
- [ ] **Voice Visualization** - Waveform display
- [ ] **Particle Systems** - Different types
- [ ] **Network Status** - Connection indicator
- [ ] **Learning Progress** - Growing bar
- [ ] **Flow State** - Sacred geometry at 80%+
- [ ] **Zen Mode** - Minimal UI toggle
- [ ] **Quick Actions** - Button interactions
- [ ] **Error Handling** - Graceful failures

## 🚀 Using Demo Materials

### In README
```markdown
![Nix for Humanity Demo](demo-materials/enhanced-tui-demo.gif)

### Features
![Idle State](screenshots/01-idle-state.png)
![Voice Active](screenshots/04-voice-active.png)
![Flow State](screenshots/06-flow-state.png)
```

### In Presentations
- Use MP4 videos for smooth playback
- Have GIFs as backup (no audio needed)
- Screenshots for static slides

### On Social Media
- Twitter: GIFs under 15MB
- GitHub: GIFs under 10MB in README
- YouTube: Full video demos with narration

## 🎭 Demo Mode API

For developers creating custom demos:

```python
from nix_humanity.ui.demo_mode import DemoScript, DemoStep

# Create custom demo
demo = DemoScript(app)
demo.script = [
    DemoStep("type", "install vim", 0.1, "Install a package"),
    DemoStep("key", "enter", 0.5),
    DemoStep("wait", "", 3.0, "Show result"),
    DemoStep("narrate", "✨ Natural language NixOS!", 3.0),
]

# Play demo
await demo.play()
```

## 📝 Tips for Great Demos

1. **Start Simple** - Show basic "help" first
2. **Build Complexity** - Progress to advanced features
3. **Show Failures** - Demonstrate error handling
4. **Highlight Unique** - Focus on consciousness-first features
5. **Keep It Short** - 60-90 seconds maximum
6. **Add Context** - Use narration or captions
7. **Test First** - Practice the flow before recording

## 🆘 Troubleshooting

**GIF too large?**
- Reduce FPS to 10
- Scale to 800px width
- Shorten duration
- Use fewer colors

**Animations not smooth?**
- Ensure 60fps TUI rendering
- Use video instead of GIF
- Check terminal performance

**Text not readable?**
- Increase font size
- Use high contrast theme
- Add padding around terminal
- Export at higher resolution

---

Create beautiful demos that showcase the revolutionary consciousness-first interface! 🌟