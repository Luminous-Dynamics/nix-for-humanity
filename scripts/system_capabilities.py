#!/usr/bin/env python3
"""
from typing import Optional
System Capabilities Detector
============================

Unified detection of system capabilities for resilient architecture.
Run once on startup to create an immutable snapshot of what's available.
"""

import os
import sys
import subprocess
import platform
import psutil
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SystemCapabilities:
    """A single, unified snapshot of what the system can do"""
    # System info
    os_type: str
    nixos_version: Optional[str]
    python_version: str
    
    # Hardware
    cpu_cores: int
    ram_gb: float
    has_gpu: bool
    gpu_info: Optional[str]
    
    # NixOS tools
    has_nixos_rebuild_ng: bool
    has_nix_profile: bool
    has_nix_env: bool
    
    # Voice engines
    has_whisper: bool
    whisper_model: Optional[str]
    has_vosk: bool
    vosk_model_path: Optional[str]
    has_piper: bool
    piper_voices: list
    has_espeak: bool
    espeak_version: Optional[str]
    
    # LLM
    has_mistral_7b: bool
    has_ollama: bool
    
    # Terminal
    terminal_supports_unicode: bool
    terminal_supports_color: bool
    terminal_supports_rich: bool
    
    # Network
    has_tor_service: bool
    internet_available: bool
    
    # Audio
    has_audio_input: bool
    has_audio_output: bool
    audio_system: Optional[str]


class CapabilityDetector:
    """Detect all system capabilities in one pass"""
    
    def __init__(self):
        self.capabilities = {}
        
    def detect_all(self) -> SystemCapabilities:
        """Run all detection methods and return capabilities"""
        logger.info("🔍 Starting system capability detection...")
        
        # System info
        self._detect_system_info()
        
        # Hardware
        self._detect_hardware()
        
        # NixOS tools
        self._detect_nixos_tools()
        
        # Voice engines
        self._detect_voice_engines()
        
        # LLM
        self._detect_llm()
        
        # Terminal
        self._detect_terminal()
        
        # Network
        self._detect_network()
        
        # Audio
        self._detect_audio()
        
        # Create immutable capabilities object
        caps = SystemCapabilities(**self.capabilities)
        
        logger.info("✅ Capability detection complete!")
        self._log_summary(caps)
        
        return caps
    
    def _detect_system_info(self):
        """Detect OS and system information"""
        self.capabilities['os_type'] = platform.system()
        self.capabilities['python_version'] = platform.python_version()
        
        # Check if NixOS
        if os.path.exists('/etc/nixos/configuration.nix'):
            try:
                result = subprocess.run(
                    ['nixos-version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.capabilities['nixos_version'] = result.stdout.strip()
                else:
                    self.capabilities['nixos_version'] = "Unknown"
            except Exception:
                self.capabilities['nixos_version'] = None
        else:
            self.capabilities['nixos_version'] = None
    
    def _detect_hardware(self):
        """Detect hardware capabilities"""
        self.capabilities['cpu_cores'] = os.cpu_count() or 1
        self.capabilities['ram_gb'] = round(psutil.virtual_memory().total / (1024**3), 1)
        
        # GPU detection
        try:
            result = subprocess.run(
                ['lspci'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                vga_lines = [line for line in result.stdout.split('\n') 
                           if 'VGA' in line or '3D' in line]
                if vga_lines:
                    self.capabilities['has_gpu'] = True
                    self.capabilities['gpu_info'] = vga_lines[0]
                else:
                    self.capabilities['has_gpu'] = False
                    self.capabilities['gpu_info'] = None
            else:
                self.capabilities['has_gpu'] = False
                self.capabilities['gpu_info'] = None
        except Exception:
            self.capabilities['has_gpu'] = False
            self.capabilities['gpu_info'] = None
    
    def _detect_nixos_tools(self):
        """Detect NixOS-specific tools"""
        # nixos-rebuild-ng (Python API)
        self.capabilities['has_nixos_rebuild_ng'] = self._check_command('nixos-rebuild') and \
            self._check_python_module('nixos_rebuild')
        
        # nix profile
        self.capabilities['has_nix_profile'] = self._check_command_with_args(
            'nix', ['profile', '--version']
        )
        
        # nix-env
        self.capabilities['has_nix_env'] = self._check_command('nix-env')
    
    def _detect_voice_engines(self):
        """Detect voice processing engines"""
        # Whisper
        try:
            import whisper
            self.capabilities['has_whisper'] = True
            # Check for model
            model_path = Path.home() / '.cache' / 'whisper'
            if model_path.exists():
                models = list(model_path.glob('*.pt'))
                if models:
                    self.capabilities['whisper_model'] = models[0].stem
                else:
                    self.capabilities['whisper_model'] = None
            else:
                self.capabilities['whisper_model'] = None
        except ImportError:
            self.capabilities['has_whisper'] = False
            self.capabilities['whisper_model'] = None
        
        # Vosk
        try:
            import vosk
            self.capabilities['has_vosk'] = True
            # Check for model
            model_path = Path.home() / '.cache' / 'vosk'
            if model_path.exists():
                models = list(model_path.glob('vosk-model-*'))
                if models:
                    self.capabilities['vosk_model_path'] = str(models[0])
                else:
                    self.capabilities['vosk_model_path'] = None
            else:
                self.capabilities['vosk_model_path'] = None
        except ImportError:
            self.capabilities['has_vosk'] = False
            self.capabilities['vosk_model_path'] = None
        
        # Piper
        if self._check_command('piper'):
            self.capabilities['has_piper'] = True
            # Try to list voices
            try:
                result = subprocess.run(
                    ['piper', '--list-voices'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    voices = [line.strip() for line in result.stdout.split('\n') if line]
                    self.capabilities['piper_voices'] = voices[:5]  # First 5 voices
                else:
                    self.capabilities['piper_voices'] = []
            except Exception:
                self.capabilities['piper_voices'] = []
        else:
            self.capabilities['has_piper'] = False
            self.capabilities['piper_voices'] = []
        
        # espeak
        if self._check_command('espeak-ng'):
            self.capabilities['has_espeak'] = True
            self.capabilities['espeak_version'] = 'espeak-ng'
        elif self._check_command('espeak'):
            self.capabilities['has_espeak'] = True
            self.capabilities['espeak_version'] = 'espeak'
        else:
            self.capabilities['has_espeak'] = False
            self.capabilities['espeak_version'] = None
    
    def _detect_llm(self):
        """Detect LLM capabilities"""
        # Check for Mistral model
        model_path = Path.home() / '.cache' / 'mistral-7b-instruct'
        self.capabilities['has_mistral_7b'] = model_path.exists()
        
        # Check for Ollama
        self.capabilities['has_ollama'] = self._check_command('ollama')
    
    def _detect_terminal(self):
        """Detect terminal capabilities"""
        # Unicode support
        try:
            print("✨", end='', flush=True)
            print("\r  ", end='', flush=True)
            self.capabilities['terminal_supports_unicode'] = True
        except Exception:
            self.capabilities['terminal_supports_unicode'] = False
        
        # Color support
        term = os.environ.get('TERM', '')
        self.capabilities['terminal_supports_color'] = term != 'dumb' and \
            ('color' in term or term in ['xterm', 'screen'])
        
        # Rich terminal (256 colors)
        self.capabilities['terminal_supports_rich'] = term in [
            'xterm-256color', 'screen-256color'
        ]
    
    def _detect_network(self):
        """Detect network capabilities"""
        # Tor service
        self.capabilities['has_tor_service'] = self._check_command('tor') or \
            os.path.exists('/var/run/tor')
        
        # Internet connectivity
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.capabilities['internet_available'] = True
        except Exception:
            self.capabilities['internet_available'] = False
    
    def _detect_audio(self):
        """Detect audio capabilities"""
        # Check for audio devices
        try:
            # Check ALSA
            result = subprocess.run(
                ['arecord', '-l'],
                capture_output=True,
                text=True
            )
            self.capabilities['has_audio_input'] = result.returncode == 0 and \
                'card' in result.stdout
            
            result = subprocess.run(
                ['aplay', '-l'],
                capture_output=True,
                text=True
            )
            self.capabilities['has_audio_output'] = result.returncode == 0 and \
                'card' in result.stdout
            
            # Detect audio system
            if self._check_command('pipewire'):
                self.capabilities['audio_system'] = 'PipeWire'
            elif self._check_command('pulseaudio'):
                self.capabilities['audio_system'] = 'PulseAudio'
            elif self.capabilities['has_audio_output']:
                self.capabilities['audio_system'] = 'ALSA'
            else:
                self.capabilities['audio_system'] = None
                
        except Exception:
            self.capabilities['has_audio_input'] = False
            self.capabilities['has_audio_output'] = False
            self.capabilities['audio_system'] = None
    
    def _check_command(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_command_with_args(self, command: str, args: list) -> bool:
        """Check if a command works with specific args"""
        try:
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_python_module(self, module: str) -> bool:
        """Check if a Python module can be imported"""
        try:
            # Try to find nixos-rebuild-ng in nix store
            result = subprocess.run(
                ['find', '/nix/store', '-name', module, '-type', 'd'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and module in result.stdout
        except Exception:
            return False
    
    def _log_summary(self, caps: SystemCapabilities):
        """Log a summary of detected capabilities"""
        logger.info("\n📊 System Capabilities Summary:")
        logger.info(f"  OS: {caps.os_type} {caps.nixos_version or ''}")
        logger.info(f"  Hardware: {caps.cpu_cores} cores, {caps.ram_gb}GB RAM")
        
        if caps.has_gpu:
            logger.info(f"  GPU: {caps.gpu_info}")
        
        # Voice capabilities
        voice_status = []
        if caps.has_whisper:
            voice_status.append(f"Whisper ({caps.whisper_model or 'no model'})")
        if caps.has_vosk:
            voice_status.append("Vosk")
        if caps.has_piper:
            voice_status.append(f"Piper ({len(caps.piper_voices)} voices)")
        if caps.has_espeak:
            voice_status.append(caps.espeak_version)
            
        if voice_status:
            logger.info(f"  Voice: {', '.join(voice_status)}")
        else:
            logger.info("  Voice: No engines available")
        
        # Terminal
        term_features = []
        if caps.terminal_supports_unicode:
            term_features.append("Unicode")
        if caps.terminal_supports_rich:
            term_features.append("Rich")
        elif caps.terminal_supports_color:
            term_features.append("Color")
            
        logger.info(f"  Terminal: {', '.join(term_features) or 'Basic'}")


def save_capabilities(caps: SystemCapabilities, path: Optional[str] = None):
    """Save capabilities to JSON file"""
    if path is None:
        path = Path.home() / '.config' / 'nix-for-humanity' / 'capabilities.json'
    
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(asdict(caps), f, indent=2)
    
    logger.info(f"💾 Saved capabilities to {path}")


def load_capabilities(path: Optional[str] = None) -> Optional[SystemCapabilities]:
    """Load capabilities from JSON file"""
    if path is None:
        path = Path.home() / '.config' / 'nix-for-humanity' / 'capabilities.json'
    
    path = Path(path)
    if not path.exists():
        return None
    
    try:
        with open(path) as f:
            data = json.load(f)
        return SystemCapabilities(**data)
    except Exception as e:
        logger.error(f"Failed to load capabilities: {e}")
        return None


def main():
    """Run capability detection"""
    detector = CapabilityDetector()
    caps = detector.detect_all()
    
    # Save for future use
    save_capabilities(caps)
    
    # Show overall system rating
    print("\n🌟 Overall System Rating:")
    
    rating = "Basic"
    if caps.has_mistral_7b and caps.has_whisper and caps.has_piper:
        rating = "Premium"
    elif caps.has_whisper or caps.has_piper:
        rating = "Standard"
    elif caps.has_vosk or caps.has_espeak:
        rating = "Basic"
    else:
        rating = "Minimal"
    
    print(f"  Your system capabilities: {rating}")
    print(f"  Ready for Nix for Humanity! 🚀")


if __name__ == "__main__":
    main()