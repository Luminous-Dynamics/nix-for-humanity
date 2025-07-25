# 💻 System Requirements - Nix for Humanity

## Minimum Requirements

### Hardware
- **CPU**: 2 cores (x86_64 or ARM64)
- **RAM**: 2GB (4GB recommended)
- **Storage**: 1GB free space
- **Network**: Optional (for package downloads)
- **Audio**: Microphone (for voice input)

### Software
- **OS**: NixOS 23.11 or later
- **Browser**: Firefox 100+ or Chromium-based
- **Node.js**: 18+ (provided by Nix)
- **Audio**: PulseAudio or PipeWire

### Accessibility Hardware
- **Screen Reader**: Any NVDA/JAWS/Orca compatible
- **Alternative Input**: Switch control, eye tracking supported
- **Display**: Minimum 1024x768 (responsive to any size)

## Recommended Requirements

### Hardware
- **CPU**: 4 cores (better voice processing)
- **RAM**: 4GB (smooth neural model performance)
- **Storage**: 2GB (for models and cache)
- **Audio**: Good quality microphone
- **GPU**: Optional (speeds up neural processing)

### Network
- **Bandwidth**: 10 Mbps (for package downloads)
- **Latency**: Not critical (all processing local)
- **Offline**: Fully functional without internet

## Performance Targets

### Response Times
| Operation | Target | Maximum |
|-----------|--------|---------|
| Voice recognition | <500ms | 2s |
| Intent parsing | <100ms | 300ms |
| Command execution | <200ms | 500ms |
| Total response | <1s | 3s |

### Resource Usage
| Component | Idle | Active | Peak |
|-----------|------|--------|------|
| CPU | <5% | 15-25% | 40% |
| RAM | 150MB | 400MB | 600MB |
| Disk I/O | Minimal | 10MB/s | 50MB/s |

## Progressive Enhancement

### Minimal Mode (2GB RAM)
- Text input only
- Basic intent recognition
- Rule-based processing
- No voice support

### Standard Mode (4GB RAM)
- Voice input enabled
- Statistical NLP
- Learning GUI
- Full feature set

### Enhanced Mode (8GB+ RAM)
- Neural understanding
- Multi-language support
- Advanced context
- Predictive features

## Browser Requirements

### Supported Browsers
- **Firefox**: 100+ (recommended)
- **Chrome/Chromium**: 90+
- **Safari**: 15+ (limited voice support)
- **Edge**: 90+

### Required APIs
- Web Speech API (for voice)
- WebSocket (for real-time)
- Service Workers (for offline)
- IndexedDB (for local storage)

## NixOS Configuration

### Required Modules
```nix
{
  # Audio support
  hardware.pulseaudio.enable = true;
  # OR
  services.pipewire.enable = true;
  
  # Firewall (if using network features)
  networking.firewall.allowedTCPPorts = [ 3456 3457 ];
  
  # Recommended packages
  environment.systemPackages = with pkgs; [
    firefox
    nodejs_18
    git
  ];
}
```

### Desktop Environment
Works with any desktop environment:
- **GNOME**: Full support
- **KDE Plasma**: Full support
- **XFCE**: Full support
- **i3/Sway**: Full support
- **None (TTY)**: Text mode supported

## Accessibility Requirements

### Screen Readers
- **NVDA**: Version 2020.1+
- **JAWS**: Version 2019+
- **Orca**: Version 3.36+
- **VoiceOver**: macOS 10.15+

### Browser Extensions
Compatible with:
- Ad blockers
- Password managers
- Accessibility tools
- Dark mode extensions

## Development Requirements

### For Contributors
- **Node.js**: 18+ 
- **Rust**: 1.70+ (for core components)
- **Git**: 2.25+
- **Nix**: 2.3+ (for reproducible builds)

### Build Requirements
- **RAM**: 8GB (for building from source)
- **Storage**: 5GB (including build artifacts)
- **Time**: ~10 minutes full build

## Docker/Container Support

### Docker Minimum
```yaml
resources:
  limits:
    memory: 1GB
    cpus: '2.0'
  requests:
    memory: 512MB
    cpus: '1.0'
```

### Kubernetes
```yaml
resources:
  limits:
    memory: 2Gi
    cpu: 2000m
  requests:
    memory: 1Gi
    cpu: 1000m
```

## Virtual Machine Support

### QEMU/KVM
```bash
# Minimum VM configuration
qemu-system-x86_64 \
  -m 2048 \
  -smp 2 \
  -enable-kvm \
  -soundhw hda
```

### VirtualBox
- **RAM**: 2048MB minimum
- **CPU**: 2 cores
- **Audio**: Enable audio controller
- **Network**: NAT or Bridged

## Performance Optimization

### For Low-End Systems
```javascript
// Disable animations
settings.animations = false;

// Use lightweight theme
settings.theme = 'minimal';

// Disable neural models
settings.nlp.mode = 'rules-only';

// Reduce voice quality
settings.voice.quality = 'low';
```

### For High-End Systems
```javascript
// Enable all features
settings.animations = true;
settings.theme = 'full';
settings.nlp.mode = 'neural';
settings.voice.quality = 'high';
settings.predictions = true;
```

## Monitoring Requirements

### Health Checks
- CPU usage < 80%
- RAM usage < 90%
- Disk space > 100MB
- Response time < 3s

### Logs Location
```
~/.local/share/nix-for-humanity/logs/
├── nlp.log
├── voice.log
├── errors.log
└── audit.log
```

## Known Limitations

### Hardware
- ARM32 not supported (64-bit required)
- Requires audio hardware for voice
- No GPU acceleration yet

### Software  
- Wayland support experimental
- Some browsers have limited Web Speech API
- Offline package search limited to cache

### Network
- First run requires internet (model download)
- Package installation requires internet
- Voice models are English-only initially

---

*These requirements ensure Nix for Humanity runs smoothly while remaining accessible to users with older hardware.*