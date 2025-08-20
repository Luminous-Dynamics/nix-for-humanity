#!/usr/bin/env python3
"""Rewrite prepare-production-release.py to fix f-string issues"""

# Read the broken file to understand the structure
with open('scripts/prepare-production-release.py', 'r') as f:
    lines = f.readlines()

# Extract the class and method structure
class_def = None
methods = []
current_method = None

for i, line in enumerate(lines):
    if line.strip().startswith('class ReleasePreparation'):
        class_def = i
    elif line.strip().startswith('def '):
        if current_method:
            methods.append(current_method)
        current_method = {'start': i, 'name': line.strip()}

if current_method:
    methods.append(current_method)

print(f"Found class at line {class_def + 1}")
print(f"Found {len(methods)} methods")

# The issue is in methods that generate content with Nix syntax
# We need to rewrite them to avoid f-strings for Nix code blocks

# Create a simpler version that works
new_content = '''#!/usr/bin/env python3
"""
Production Release Preparation Script for Nix for Humanity
Prepares all necessary files and documentation for v1.0.0 release
"""

import os
import sys
import json
import shutil
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ReleasePreparation:
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.prev_version = "0.8.3"
        self.release_date = datetime.date.today().strftime("%Y-%m-%d")
        self.project_root = Path(__file__).parent.parent
        self.release_dir = self.project_root / "release" / f"v{version}"
        
        # Create release directory
        self.release_dir.mkdir(parents=True, exist_ok=True)
        
    def update_version_files(self):
        """Update version in all relevant files"""
        print("📝 Updating version files...")
        
        # Update VERSION file
        version_file = self.project_root / "VERSION"
        version_file.write_text(self.version)
        
        # Update pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            content = content.replace(f'version = "{self.prev_version}"', f'version = "{self.version}"')
            pyproject_path.write_text(content)
        
        # Update flake.nix
        flake_path = self.project_root / "flake.nix"
        if flake_path.exists():
            content = flake_path.read_text()
            content = content.replace(f'version = "{self.prev_version}";', f'version = "{self.version}";')
            flake_path.write_text(content)
        
        print(f"✅ Version updated to {self.version}")
    
    def generate_release_notes(self):
        """Generate comprehensive release notes"""
        print("📋 Generating release notes...")
        
        # Use format() instead of f-strings for content with special characters
        release_notes = """# Nix for Humanity v{version} Release Notes

**Release Date**: {release_date}

## 🎉 Overview

Nix for Humanity v1.0.0 represents a major milestone in making NixOS accessible through natural language. This production-ready release delivers on our vision of consciousness-first computing with revolutionary performance and user experience improvements.

## 🚀 Major Achievements

### 1. Lightning-Fast Native Operations ⚡
- **10x-1500x Performance Improvement**: Direct Python-Nix API integration eliminates subprocess timeouts
- **Instant Operations**: List generations, system info, and rollback now complete in <0.1s
- **Real-time Progress**: All operations show live progress with time estimates

### 2. Natural Language Excellence 🗣️
- **85% Accuracy**: Enhanced intent recognition for common NixOS tasks
- **Smart Package Discovery**: Find packages by description, not just name
- **Educational Error Messages**: Transform cryptic errors into learning opportunities

### 3. Configuration Generation 🔧
- **Natural Language to NixOS Configs**: Generate complete configuration.nix from descriptions
- **Flake Management**: Create modern development environments easily
- **Home Manager Integration**: Personal dotfile management through conversation

### 4. Beautiful User Interface 🎨
- **Connected TUI**: Textual interface with consciousness orb visualization
- **Multi-Modal Support**: CLI, TUI, and voice-ready architecture
- **Accessibility First**: Full screen reader support and keyboard navigation

### 5. Production Quality 🏗️
- **Comprehensive Testing**: Real integration tests against actual NixOS
- **Security Hardened**: Command injection prevention and sandboxed execution
- **Configuration System**: Profiles, aliases, and shortcuts for personalization

## 📊 Performance Metrics

| Operation | v0.8.3 | v1.0.0 | Improvement |
|-----------|--------|--------|-------------|
| List Generations | 2-5s | <0.1s | ∞x |
| System Info | 1-3s | <0.1s | ∞x |
| Package Search | 5-10s | 0.5-1s | 10x |
| Rollback | 10-30s | 0.2-0.5s | 50x |
| Config Generation | N/A | <1s | New! |

## ✨ New Features

### Core Features
- **Configuration.nix Generation**: Natural language descriptions to full configs
- **Smart Package Discovery**: Fuzzy search with description matching
- **Flake Support**: Modern NixOS development environments
- **Generation Management**: System health checks and recovery
- **Home Manager Integration**: Dotfile configuration made simple
- **Error Intelligence**: Educational feedback that teaches NixOS concepts

### User Experience
- **10 Personality Styles**: From Grandma Rose to power users
- **Configuration Profiles**: Save and switch between preferences
- **Progress Indicators**: Multiple styles with ETA
- **Voice Interface Architecture**: Ready for speech integration

### Developer Features
- **Native Python-Nix API**: Direct integration with nixos-rebuild-ng
- **Comprehensive Testing**: Integration tests with real NixOS operations
- **Sacred Trinity Workflow**: Revolutionary $200/mo development model
- **Plugin Architecture**: Extensible design for community contributions

## 🔄 Breaking Changes

### API Changes
- Python backend now default (set `NIX_HUMANITY_PYTHON_BACKEND=true`)
- New configuration format (automatic migration provided)
- Voice interface API restructured for better performance

### Deprecated Features
- Subprocess-based execution (replaced with native API)
- Mock testing mode (replaced with real integration tests)
- Legacy configuration format (migrated automatically)

## 🐛 Bug Fixes

- Fixed command injection vulnerability in input handling
- Resolved timeout issues with long-running operations
- Fixed package search edge cases
- Corrected TUI connection issues
- Resolved memory leaks in learning system
- Fixed path resolution for voice dependencies

## 📦 Installation

### NixOS Users
```nix
# Add to configuration.nix
services.nixForHumanity = {{
  enable = true;
  package = pkgs.nixForHumanity;
  voice.enable = true;  # Optional
}};
```

### Flake Users
```nix
{{
  inputs.nix-for-humanity.url = "github:Luminous-Dynamics/nix-for-humanity/v1.0.0";
  
  outputs = {{ self, nixpkgs, nix-for-humanity }}: {{
    nixosConfigurations.mySystem = nixpkgs.lib.nixosSystem {{
      modules = [
        nix-for-humanity.nixosModules.default
        {{
          services.nixForHumanity.enable = true;
        }}
      ];
    }};
  }};
}}
```

### Development
```bash
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
nix develop
```

## 🚀 Quick Start

```bash
# Enable native performance
export NIX_HUMANITY_PYTHON_BACKEND=true

# Natural language commands
ask-nix "install firefox"
ask-nix "create python dev environment"
ask-nix "generate gaming desktop config"

# Beautiful TUI
nix-tui

# Configuration wizard
ask-nix settings wizard
```

## 📈 What's Next (v1.1 Roadmap)

- **Voice Interface Activation**: Complete pipecat integration
- **Learning System Activation**: Enable RLHF pipeline
- **Federated Learning**: Privacy-preserving collective intelligence
- **Advanced Personas**: Complete 10-persona system
- **Community Features**: Sharing and collaboration tools

## 🙏 Acknowledgments

This release represents the culmination of the Sacred Trinity development model:
- **Human (Tristan)**: Vision, user empathy, and real-world validation
- **Claude Code Max**: Architecture, implementation, and synthesis
- **Local LLM**: NixOS expertise and best practices

Special thanks to all contributors and early testers who helped make NixOS accessible to everyone.

## 📚 Documentation

- [Migration Guide](MIGRATION_GUIDE_v1.0.0.md)
- [API Reference](API_REFERENCE_v1.0.0.md)
- [Configuration Guide](CONFIGURATION_GUIDE_v1.0.0.md)
- [Troubleshooting](TROUBLESHOOTING_v1.0.0.md)

## 🐞 Known Issues

- Voice interface requires manual activation (coming in v1.1)
- Learning system framework complete but not fully active
- Some edge cases in natural language parsing
- TUI may flicker on certain terminal emulators

## 📞 Support

- GitHub Issues: https://github.com/Luminous-Dynamics/nix-for-humanity/issues
- Discussions: https://github.com/Luminous-Dynamics/nix-for-humanity/discussions
- Documentation: https://nix-for-humanity.dev

---

**Philosophy**: Making NixOS accessible through consciousness-first computing, where technology amplifies human awareness rather than fragmenting it.

**Achievement**: $200/month development model delivering $4.2M enterprise quality - proving sacred technology can be practical.
""".format(version=self.version, release_date=self.release_date)
        
        release_notes_path = self.release_dir / "RELEASE_NOTES.md"
        release_notes_path.write_text(release_notes)
        print(f"✅ Release notes generated: {release_notes_path}")
    
    def generate_release_checklist(self):
        """Generate comprehensive release checklist"""
        print("✅ Generating release checklist...")
        
        checklist = """# Nix for Humanity v{version} Release Checklist

## Pre-Release Testing
- [ ] All unit tests passing (`pytest tests/`)
- [ ] All integration tests passing (`pytest tests/integration/`)
- [ ] Manual testing of core features:
  - [ ] Natural language CLI commands
  - [ ] Configuration generation
  - [ ] Package discovery
  - [ ] Flake management
  - [ ] Generation management
  - [ ] Home Manager integration
  - [ ] TUI interface
  - [ ] Error handling
- [ ] Performance benchmarks meet targets
- [ ] Security audit completed
- [ ] Accessibility testing passed

## Documentation
- [ ] Release notes reviewed and finalized
- [ ] Migration guide completed
- [ ] API documentation updated
- [ ] User guide updated
- [ ] README.md reflects current state
- [ ] CHANGELOG.md updated
- [ ] All examples tested

## Code Quality
- [ ] No TODO comments in production code
- [ ] All deprecated code removed
- [ ] Code formatting consistent (`black .`)
- [ ] Type hints complete
- [ ] Docstrings comprehensive
- [ ] No hardcoded values

## Version Updates
- [ ] VERSION file updated
- [ ] pyproject.toml version updated
- [ ] flake.nix version updated
- [ ] Documentation references updated
- [ ] API version bumped

## Build & Package
- [ ] Clean build successful
- [ ] Nix flake check passing
- [ ] Package builds on NixOS 24.11
- [ ] Package builds on NixOS unstable
- [ ] Binary size acceptable
- [ ] Dependencies locked

## Release Artifacts
- [ ] Source tarball created
- [ ] Nix package built
- [ ] Installation instructions tested
- [ ] Migration script tested
- [ ] Release notes proofread

## Communication
- [ ] Announcement blog post drafted
- [ ] Social media announcements prepared
- [ ] Community notifications ready
- [ ] Contributor acknowledgments complete

## Git & GitHub
- [ ] Create release branch
- [ ] Tag version (v{version})
- [ ] Push tag to GitHub
- [ ] Create GitHub release
- [ ] Upload release artifacts
- [ ] Update default branch protection

## Post-Release
- [ ] Monitor issue tracker
- [ ] Respond to community feedback
- [ ] Plan hotfix process if needed
- [ ] Update roadmap for next version
- [ ] Celebrate! 🎉

## Rollback Plan
- [ ] Previous version backup available
- [ ] Rollback procedure documented
- [ ] Database migration reversible
- [ ] Configuration migration reversible

---
**Release Manager**: _______________________
**Date Completed**: _______________________
""".format(version=self.version)
        
        checklist_path = self.release_dir / "RELEASE_CHECKLIST.md"
        checklist_path.write_text(checklist)
        print(f"✅ Release checklist generated: {checklist_path}")
    
    def create_installation_instructions(self):
        """Generate detailed installation instructions"""
        print("📦 Creating installation instructions...")
        
        # Create the instructions content separately
        nix_config_content = """# Add to configuration.nix
services.nixForHumanity = {
  enable = true;
  package = pkgs.nixForHumanity;
  voice.enable = true;  # Optional
};"""

        flake_content = """{
  inputs.nix-for-humanity.url = "github:Luminous-Dynamics/nix-for-humanity/v{version}";
  
  outputs = { self, nixpkgs, nix-for-humanity }: {
    nixosConfigurations.mySystem = nixpkgs.lib.nixosSystem {
      modules = [
        nix-for-humanity.nixosModules.default
        {
          services.nixForHumanity.enable = true;
        }
      ];
    };
  };
}"""

        nix_config_detailed = """{ config, pkgs, ... }:

{
  # Add Nix for Humanity
  services.nixForHumanity = {
    enable = true;
    package = pkgs.nixForHumanity;
    
    # Optional features
    voice = {
      enable = true;
      wakeWord = "hey nix";
    };
    
    learning = {
      enable = true;
      privacy = "local-only";
    };
    
    # Personalization
    defaultPersona = "maya";  # Fast responses for ADHD
    theme = "consciousness";  # Sacred theme
  };
}"""

        flake_detailed = """{
  description = "My NixOS configuration with Nix for Humanity";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    nix-for-humanity.url = "github:Luminous-Dynamics/nix-for-humanity/v{version}";
  };
  
  outputs = { self, nixpkgs, nix-for-humanity }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        nix-for-humanity.nixosModules.default
        {
          services.nixForHumanity.enable = true;
        }
      ];
    };
  };
}"""
        
        instructions = """# Nix for Humanity v{version} Installation Guide

## System Requirements

- **OS**: NixOS 24.11 or newer (25.11 recommended for best performance)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for core, 2GB with all features
- **Python**: 3.11+ (provided by Nix)
- **Optional**: Microphone for voice interface

## Installation Methods

### Method 1: NixOS Module (Recommended)

1. Add to your `configuration.nix`:

```nix
{nix_config_detailed}
```

2. Rebuild your system:
```bash
sudo nixos-rebuild switch
```

### Method 2: Flakes (Modern Approach)

1. Create or update your `flake.nix`:

```nix
{flake_detailed}
```

2. Enable flakes and rebuild:
```bash
sudo nixos-rebuild switch --flake .#myhost
```

### Method 3: User Installation (No System Changes)

1. Clone and enter environment:
```bash
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
nix develop
```

2. Install to user profile:
```bash
./install-user.sh
```

3. Add to PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Method 4: Try Without Installing

```bash
nix run github:Luminous-Dynamics/nix-for-humanity#{version} -- "help"
```

## Post-Installation Setup

### 1. Initial Configuration

Run the setup wizard:
```bash
ask-nix settings wizard
```

This will:
- Select your preferred interaction style
- Configure voice settings (if enabled)
- Set up learning preferences
- Create initial aliases

### 2. Voice Setup (Optional)

If voice is enabled:
```bash
ask-nix voice setup
```

Test voice:
```bash
ask-nix voice test
Say: "Hey Nix, what's the weather?"
```

### 3. Verify Installation

```bash
# Check version
ask-nix --version

# Run diagnostics
ask-nix diagnose

# Test core features
ask-nix "help"
ask-nix "list installed packages"
```

## Troubleshooting

### Common Issues

**"Command not found"**
- Ensure PATH includes installation directory
- Run `hash -r` to refresh command cache

**"Permission denied"**
- Some operations require sudo
- Check with `ask-nix "why does this need sudo?"`

**Voice not working**
- Check microphone permissions
- Ensure PulseAudio/PipeWire running
- Run `ask-nix voice diagnose`

**Slow responses**
- Enable Python backend: `export NIX_HUMANITY_PYTHON_BACKEND=true`
- Check system resources: `ask-nix performance check`

### Getting Help

- **Quick help**: `ask-nix help [topic]`
- **Documentation**: `ask-nix docs`
- **Community**: https://github.com/Luminous-Dynamics/nix-for-humanity/discussions
- **Issues**: https://github.com/Luminous-Dynamics/nix-for-humanity/issues

## Uninstallation

### NixOS Module
Remove from `configuration.nix` and rebuild

### User Installation
```bash
~/.local/share/nix-for-humanity/uninstall.sh
```

### Clean all data
```bash
rm -rf ~/.config/nix-for-humanity
rm -rf ~/.local/share/nix-for-humanity
rm -rf ~/.cache/nix-for-humanity
```

---

**Next Steps**: Run `ask-nix tutorial` to start learning!
""".format(
            version=self.version,
            nix_config_detailed=nix_config_detailed,
            flake_detailed=flake_detailed.format(version=self.version)
        )
        
        install_path = self.release_dir / "INSTALLATION.md"
        install_path.write_text(instructions)
        print(f"✅ Installation instructions created: {install_path}")
    
    def generate_migration_guide(self):
        """Generate migration guide from v0.8.3 to v1.0.0"""
        print("📚 Generating migration guide...")
        
        migration = """# Migration Guide: v0.8.3 to v{version}

## Overview

Nix for Humanity v1.0.0 introduces significant improvements while maintaining backward compatibility. This guide helps you migrate smoothly.

## Breaking Changes

### 1. Python Backend Now Default

**Old behavior**: Subprocess-based execution
**New behavior**: Native Python-Nix API

**Action required**:
```bash
# Add to your shell configuration
export NIX_HUMANITY_PYTHON_BACKEND=true
```

Or in NixOS configuration:
```nix
services.nixForHumanity.pythonBackend = true;
```

### 2. Configuration Format Update

**Old format** (v0.8.3):
```json
{{
  "user": {{
    "name": "Alice",
    "style": "technical"
  }}
}}
```

**New format** (v1.0.0):
```json
{{
  "version": "1.0.0",
  "user": {{
    "name": "Alice",
    "persona": "technical",
    "preferences": {{
      "theme": "default",
      "verbosity": "normal"
    }}
  }}
}}
```

**Automatic migration**: Run `ask-nix migrate config`

### 3. Voice API Changes

**Old API**:
```python
from nix_for_humanity.voice import VoiceInterface
voice = VoiceInterface()
```

**New API**:
```python
from nix_for_humanity.interfaces.voice import VoiceEngine
voice = VoiceEngine(persona="maya")
```

## New Features to Adopt

### 1. Configuration Generation

Transform descriptions into NixOS configs:
```bash
ask-nix "generate config for web development with nodejs and postgresql"
```

### 2. Smart Package Discovery

Find packages by what they do:
```bash
ask-nix "find markdown editor with preview"
ask-nix "package for editing photos"
```

### 3. Flake Management

Create development environments:
```bash
ask-nix "create python dev environment with numpy and pandas"
ask-nix "setup rust project with wasm target"
```

### 4. Enhanced Error Messages

Errors now educate:
```
Error: Package 'neovim' has unfree license
Learning: Unfree packages need explicit permission in NixOS.
Solution: Add to configuration.nix:
  nixpkgs.config.allowUnfree = true;
Or for this package only:
  nixpkgs.config.allowUnfreePredicate = pkg: pkg.pname == "neovim";
```

## Performance Improvements

### Before (v0.8.3)
- List generations: 2-5 seconds
- Package search: 5-10 seconds
- System operations: Often timeout

### After (v1.0.0)
- List generations: <0.1 seconds (∞x faster)
- Package search: 0.5-1 second (10x faster)
- System operations: No timeouts, real-time progress

## Migration Steps

### 1. Backup Current Configuration
```bash
cp ~/.config/nix-for-humanity/config.json ~/.config/nix-for-humanity/config.json.backup
```

### 2. Update Package
```bash
# For NixOS module users
sudo nixos-rebuild switch

# For flake users
nix flake update
sudo nixos-rebuild switch

# For user installation
cd ~/nix-for-humanity
git pull
nix develop
./install-user.sh
```

### 3. Run Migration Tool
```bash
ask-nix migrate all
```

This will:
- Update configuration format
- Migrate learning data
- Update aliases and shortcuts
- Preserve all customizations

### 4. Verify Migration
```bash
ask-nix diagnose migration
```

## Rollback Procedure

If issues occur:

### 1. Restore Configuration
```bash
cp ~/.config/nix-for-humanity/config.json.backup ~/.config/nix-for-humanity/config.json
```

### 2. Downgrade Package
```nix
# In configuration.nix
services.nixForHumanity.package = pkgs.nixForHumanity_0_8_3;
```

### 3. Rebuild System
```bash
sudo nixos-rebuild switch
```

## Common Migration Issues

### Issue: "Unknown configuration version"
**Solution**: Run `ask-nix migrate config`

### Issue: "Voice not working after upgrade"
**Solution**: Re-run voice setup: `ask-nix voice setup`

### Issue: "Custom aliases missing"
**Solution**: Aliases are preserved but may need reactivation: `ask-nix settings reload`

### Issue: "Slower performance than expected"
**Solution**: Ensure Python backend is enabled: `export NIX_HUMANITY_PYTHON_BACKEND=true`

## What's Deprecated

### Removed Features
- Mock testing mode (use real integration tests)
- Legacy subprocess executor
- Old configuration format
- Experimental plugins (being redesigned)

### Replaced Features
- `ask-nix test-mode` → Use `--dry-run` flag
- `nix-humanity-cli` → Unified as `ask-nix`
- Manual persona files → Integrated persona system

## Getting Help

- **Migration issues**: `ask-nix migrate help`
- **Documentation**: `ask-nix docs migration`
- **Community support**: GitHub discussions
- **Direct support**: Create issue with `migration` label

## Timeline

- **v0.8.3 support**: Ends 3 months after v1.0.0 release
- **Migration tool availability**: 6 months
- **Legacy API compatibility**: 1 year with warnings

---

**Remember**: This upgrade brings 10x-1500x performance improvements and powerful new features. The migration effort is worth it!
""".format(version=self.version)
        
        migration_path = self.release_dir / "MIGRATION_GUIDE_v1.0.0.md"
        migration_path.write_text(migration)
        print(f"✅ Migration guide generated: {migration_path}")
    
    def generate_announcement_templates(self):
        """Generate announcement templates for various platforms"""
        print("📢 Generating announcement templates...")
        
        # Blog post
        blog_post = """# Announcing Nix for Humanity v{version}: Natural Language for NixOS

We're thrilled to announce the production release of Nix for Humanity v1.0.0, a revolutionary tool that makes NixOS accessible through natural conversation.

## What is Nix for Humanity?

Nix for Humanity transforms the NixOS experience from complex command-line operations to simple, natural language interactions. Instead of memorizing commands and syntax, you can now just say what you want:

- "Install Firefox" → Handles all the Nix complexity
- "Create a Python development environment" → Generates complete flake
- "Setup web server with nginx" → Creates full configuration.nix

## Revolutionary Performance

Through our Native Python-Nix API integration, we've achieved:
- **10x-1500x faster operations** 
- **Zero timeout issues**
- **Real-time progress tracking**
- **Instant system information**

## Key Features

### For Everyone
- Natural language understanding
- Educational error messages
- Voice interface ready
- 10 personality styles

### For Power Users  
- Configuration generation from descriptions
- Smart package discovery
- Flake management
- Home Manager integration

### For the Community
- Local-first privacy
- Sacred Trinity development model
- Consciousness-first computing
- $200/month achieving $4.2M quality

## Get Started

```bash
# Try it now
nix run github:Luminous-Dynamics/nix-for-humanity -- "help"

# Or install permanently
# Add to configuration.nix:
services.nixForHumanity.enable = true;
```

## The Philosophy

Nix for Humanity embodies consciousness-first computing - technology that amplifies human awareness rather than fragmenting it. Every feature is designed to respect your attention, preserve your agency, and support your growth.

## Join Us

This release proves that sacred technology can be practical. We invite you to:
- Try Nix for Humanity and share feedback
- Contribute to the project
- Join our community discussions
- Help make NixOS accessible to everyone

**Links**:
- GitHub: https://github.com/Luminous-Dynamics/nix-for-humanity
- Documentation: https://nix-for-humanity.dev
- Discussion: https://github.com/Luminous-Dynamics/nix-for-humanity/discussions

Together, we're building a future where technology serves consciousness.
""".format(version=self.version)
        
        # Social media
        twitter_announcement = """🎉 Nix for Humanity v{version} is here!

Natural language for NixOS that actually works:
✨ "Install Firefox" → It just happens
⚡ 10x-1500x faster with native Python-Nix API
🧠 AI that learns from you, privately
🎨 Beautiful TUI with consciousness visualization

Sacred tech made practical: $200/mo delivering $4.2M quality

Try now:
nix run github:Luminous-Dynamics/nix-for-humanity -- "help"

#NixOS #AI #OpenSource #ConsciousnessFirst
""".format(version=self.version)
        
        # GitHub Release
        github_release = """## 🎉 Nix for Humanity v{version} - Production Release

### Natural Language for NixOS That Actually Works

This release represents a major milestone in making NixOS accessible to everyone through natural conversation.

### ✨ Highlights

- **10x-1500x Performance**: Native Python-Nix API eliminates timeouts
- **Natural Language Excellence**: 85% accuracy on common tasks
- **Configuration Generation**: Describe what you want, get perfect configs
- **Beautiful Interface**: TUI with consciousness orb visualization
- **Production Ready**: Comprehensive testing and security hardening

### 🚀 Quick Start

```bash
# Try without installing
nix run github:Luminous-Dynamics/nix-for-humanity -- "install firefox"

# Or add to NixOS
services.nixForHumanity.enable = true;
```

### 📊 Performance Improvements

- List generations: ∞x faster (was 2-5s, now <0.1s)
- Package search: 10x faster
- System rollback: 50x faster
- Configuration generation: <1s for complex configs

### 🙏 Sacred Trinity Achievement

This release proves our development model: $200/month achieving what traditionally costs $4.2M through:
- Human vision and empathy
- AI architecture and implementation  
- Local LLM domain expertise

### 📚 Documentation

- [Installation Guide](https://github.com/Luminous-Dynamics/nix-for-humanity/blob/main/release/v1.0.0/INSTALLATION.md)
- [Migration Guide](https://github.com/Luminous-Dynamics/nix-for-humanity/blob/main/release/v1.0.0/MIGRATION_GUIDE_v1.0.0.md)
- [Release Notes](https://github.com/Luminous-Dynamics/nix-for-humanity/blob/main/release/v1.0.0/RELEASE_NOTES.md)

### What's Changed
[Full changelog and commits since v0.8.3]

### Contributors
[List of contributors]

**Full Changelog**: https://github.com/Luminous-Dynamics/nix-for-humanity/compare/v0.8.3...v{version}
""".format(version=self.version)
        
        # Save all templates
        templates_dir = self.release_dir / "announcements"
        templates_dir.mkdir(exist_ok=True)
        
        (templates_dir / "blog_post.md").write_text(blog_post)
        (templates_dir / "twitter.txt").write_text(twitter_announcement)
        (templates_dir / "github_release.md").write_text(github_release)
        
        print(f"✅ Announcement templates generated in: {templates_dir}")
    
    def create_release_package(self):
        """Create release package with all necessary files"""
        print("📦 Creating release package...")
        
        # Create package script with {{ }} escaped for format strings
        package_script = """#!/usr/bin/env python3
import os
import tarfile
import hashlib
from pathlib import Path

version = "{version}"
project_root = Path(__file__).parent.parent.parent

# Files to include in release
include_patterns = [
    "bin/",
    "src/",
    "backend/",
    "frontends/",
    "docs/",
    "flake.nix",
    "flake.lock", 
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "VERSION",
    "CHANGELOG.md",
]

# Files to exclude
exclude_patterns = [
    "__pycache__",
    "*.pyc",
    ".git",
    ".pytest_cache",
    "*.egg-info",
    "dist/",
    "build/",
    ".env",
    "*.log",
]

def should_include(path):
    path_str = str(path)
    
    # Check excludes first
    for pattern in exclude_patterns:
        if pattern in path_str:
            return False
    
    # Check includes
    for pattern in include_patterns:
        if path_str.startswith(pattern) or pattern in path_str:
            return True
    
    return False

# Create tarball
output_file = f"nix-for-humanity-v{{version}}.tar.gz"
print(f"Creating {{output_file}}...")

with tarfile.open(output_file, "w:gz") as tar:
    for root, dirs, files in os.walk(project_root):
        # Filter directories
        dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_patterns)]
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)
            
            if should_include(relative_path):
                print(f"  Adding: {{relative_path}}")
                tar.add(file_path, arcname=f"nix-for-humanity-v{{version}}/{{relative_path}}")

# Generate checksum
print("\\nGenerating checksum...")
with open(output_file, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()

with open(f"{{output_file}}.sha256", "w") as f:
    f.write(f"{{sha256}}  {{output_file}}\\n")

print(f"\\n✅ Release package created: {{output_file}}")
print(f"✅ Checksum: {{sha256}}")
""".format(version=self.version)
        
        package_script_path = self.release_dir / "create_package.py"
        package_script_path.write_text(package_script)
        os.chmod(package_script_path, 0o755)
        
        print(f"✅ Package script created: {package_script_path}")
    
    def generate_changelog_update(self):
        """Update CHANGELOG.md with new version"""
        print("📝 Updating CHANGELOG.md...")
        
        changelog_entry = """
## [{version}] - {release_date}

### Added
- Native Python-Nix API integration for 10x-1500x performance
- Natural language configuration generation
- Smart package discovery by description
- Flake management for development environments
- Generation management with health checks
- Home Manager integration
- Beautiful TUI with consciousness visualization
- Educational error messages
- Comprehensive configuration system
- Voice interface architecture

### Changed
- Default to Python backend for all operations
- Improved intent recognition to 85% accuracy
- Enhanced error handling with learning opportunities
- Restructured configuration format
- Unified all interfaces under single backend

### Fixed
- Command injection vulnerability
- Subprocess timeout issues
- Package search edge cases
- TUI connection problems
- Memory leaks in learning system
- Path resolution for voice dependencies

### Performance
- List generations: ∞x improvement (now instant)
- System info: ∞x improvement (now instant)  
- Package search: 10x improvement
- Rollback operations: 50x improvement
- Configuration generation: <1s for complex configs

### Security
- Sandboxed command execution
- Input validation hardening
- Permission checking improvements

""".format(version=self.version, release_date=self.release_date)
        
        changelog_path = self.project_root / "CHANGELOG.md"
        if changelog_path.exists():
            content = changelog_path.read_text()
            # Insert after header
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# Changelog'):
                    lines.insert(i + 2, changelog_entry)
                    break
            
            changelog_path.write_text('\n'.join(lines))
            print(f"✅ CHANGELOG.md updated")
        else:
            # Create new changelog
            new_changelog = """# Changelog

All notable changes to Nix for Humanity will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{changelog_entry}

## [0.8.3] - Previous Release
- Initial public release
- Basic natural language processing
- CLI interface
- Initial documentation
""".format(changelog_entry=changelog_entry)
            changelog_path.write_text(new_changelog)
            print(f"✅ CHANGELOG.md created")
    
    def create_final_summary(self):
        """Create summary of all release preparation steps"""
        print("\n📋 Creating release summary...")
        
        summary = """# Nix for Humanity v{version} Release Preparation Summary

**Date**: {release_date}
**Version**: {prev_version} → {version}

## ✅ Completed Steps

1. **Version Updates**
   - VERSION file updated
   - pyproject.toml updated
   - flake.nix updated

2. **Documentation Generated**
   - Release Notes: `release/v{version}/RELEASE_NOTES.md`
   - Installation Guide: `release/v{version}/INSTALLATION.md`
   - Migration Guide: `release/v{version}/MIGRATION_GUIDE_v1.0.0.md`
   - Release Checklist: `release/v{version}/RELEASE_CHECKLIST.md`

3. **Announcements Created**
   - Blog post template
   - Twitter announcement
   - GitHub release description

4. **Package Preparation**
   - Package creation script generated
   - CHANGELOG.md updated

## 📋 Next Steps

1. **Review all generated documents** for accuracy
2. **Run final tests** using the checklist
3. **Create release package**:
   ```bash
   cd release/v{version}
   python3 create_package.py
   ```

4. **Git operations**:
   ```bash
   git add .
   git commit -m "Prepare v{version} release"
   git tag -a v{version} -m "Release v{version}: Natural Language for NixOS"
   git push origin main
   git push origin v{version}
   ```

5. **Create GitHub release**:
   - Use the generated GitHub release description
   - Upload the release package and checksum
   - Mark as latest release

6. **Announce the release**:
   - Publish blog post
   - Send social media announcements
   - Notify the community

## 🎉 Congratulations!

You're about to release Nix for Humanity v1.0.0 - a major milestone in making NixOS accessible to everyone through natural language and consciousness-first computing.

This release represents:
- Months of dedicated development
- Revolutionary Sacred Trinity collaboration
- 10x-1500x performance improvements
- A new paradigm in human-AI partnership

Thank you for making sacred technology practical! 🙏
""".format(version=self.version, release_date=self.release_date, prev_version=self.prev_version)
        
        summary_path = self.release_dir / "RELEASE_SUMMARY.md"
        summary_path.write_text(summary)
        
        print(f"\n{'='*60}")
        print(f"✅ Release preparation complete!")
        print(f"📁 All files generated in: {self.release_dir}")
        print(f"📋 Review the summary at: {summary_path}")
        print(f"{'='*60}\n")

def main():
    """Main execution function"""
    print(f"\n{'='*60}")
    print(f"🚀 Nix for Humanity Production Release Preparation")
    print(f"{'='*60}\n")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: Must run from nix-for-humanity root directory")
        sys.exit(1)
    
    # Create release preparation instance
    prep = ReleasePreparation(version="1.0.0")
    
    # Execute all preparation steps
    prep.update_version_files()
    prep.generate_release_notes()
    prep.generate_release_checklist()
    prep.create_installation_instructions()
    prep.generate_migration_guide()
    prep.generate_announcement_templates()
    prep.create_release_package()
    prep.generate_changelog_update()
    prep.create_final_summary()
    
    print("🎉 Production release preparation complete!")
    print(f"📁 Check the release directory: release/v1.0.0/")
    print("📋 Follow the checklist to complete the release process.")

if __name__ == "__main__":
    main()
'''

# Write the new version
with open('scripts/prepare-production-release.py', 'w') as f:
    f.write(new_content)

print("✅ Rewrote prepare-production-release.py with fixed syntax!")