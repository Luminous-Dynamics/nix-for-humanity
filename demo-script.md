# 📹 Luminous Nix Demo Script (2 minutes)

## Setup Before Recording
1. Clear terminal
2. Have Luminous Nix ready in `/srv/luminous-dynamics/11-meta-consciousness/luminous-nix`
3. Make terminal font larger for visibility
4. Dark theme recommended

## Script

### Opening (10 seconds)
"Hi! I'm going to show you Luminous Nix - a tool that lets you control NixOS using plain English instead of complex commands."

### Demo 1: Installation (30 seconds)
```bash
# Show traditional way first
echo "# Traditional NixOS:"
echo "nix-env -iA nixos.firefox"
echo ""
echo "# With Luminous Nix:"

# Now show Luminous Nix
./bin/ask-nix "install firefox"
# (Let it show the preview)
# Type 'n' to cancel

echo "See? Just natural language!"
```

### Demo 2: Search (30 seconds)
```bash
# Search for something
./bin/ask-nix "search for markdown editors"

# Show it finds multiple options
echo "It searches by description, not just package names!"
```

### Demo 3: Natural Language (30 seconds)
```bash
# Show more natural queries
./bin/ask-nix "I need a video player"

# Show system management
./bin/ask-nix "update my system"
# (Cancel with 'n')
```

### Demo 4: Help & Intelligence (15 seconds)
```bash
# Show help system
./bin/ask-nix "help"

# Show it understands problems
./bin/ask-nix "something is wrong with my system"
```

### Closing (15 seconds)
"Luminous Nix is open source and in active development. We're looking for beta testers and contributors. Check the GitHub link in the description to try it yourself. Thanks for watching!"

## Tips for Recording
- **Use asciinema** for terminal recording: `asciinema rec demo.cast`
- **Or use phone** to record screen directly
- **Keep energy high** - this is exciting!
- **Don't worry about mistakes** - can re-record
- **Show the actual output** - people want to see it really works

## Alternative: Quick GIF Demo
If video is too much, create a GIF:
```bash
# Install asciinema and asciicast2gif
asciinema rec demo.cast
# Do the demo
# Ctrl+D to stop

# Convert to GIF
docker run --rm -v $PWD:/data asciinema/asciicast2gif -w 80 -h 24 demo.cast demo.gif
```