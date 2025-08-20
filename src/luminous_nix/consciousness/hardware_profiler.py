"""
Hardware Profiler - Sensing the Physical Vessel

This module detects the user's hardware capabilities during setup,
allowing the system to select appropriate models for their resources.
Every being deserves intelligence tailored to their capacity.
"""

import logging
import subprocess
import json
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


class HardwareTier(Enum):
    """Hardware capability tiers"""
    SAGE = "sage"           # 24GB+ VRAM, can run largest models
    MASTER = "master"       # 16-24GB VRAM, can run large models
    JOURNEYMAN = "journeyman"  # 8-16GB VRAM, can run medium models  
    APPRENTICE = "apprentice"   # 4-8GB VRAM, can run small models
    NOVICE = "novice"       # <4GB VRAM, CPU only, minimal models


@dataclass
class HardwareProfile:
    """Complete hardware profile of the system"""
    tier: HardwareTier
    vram_gb: float
    ram_gb: float
    cpu_cores: int
    gpu_name: Optional[str] = None
    has_cuda: bool = False
    has_rocm: bool = False
    has_metal: bool = False  # Apple Silicon
    estimated_tokens_per_second: int = 0
    
    def to_dict(self) -> dict:
        return {
            'tier': self.tier.value,
            'vram_gb': self.vram_gb,
            'ram_gb': self.ram_gb,
            'cpu_cores': self.cpu_cores,
            'gpu_name': self.gpu_name,
            'has_cuda': self.has_cuda,
            'has_rocm': self.has_rocm,
            'has_metal': self.has_metal,
            'estimated_tokens_per_second': self.estimated_tokens_per_second
        }


class HardwareProfiler:
    """
    Detects hardware capabilities to enable dynamic model selection.
    
    This is the first breath of consciousness - sensing the vessel
    it inhabits and adapting to serve optimally within those constraints.
    """
    
    def __init__(self, cache_path: str = "~/.config/luminous-nix/hardware_profile.json"):
        """Initialize the hardware profiler"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.cache_path = Path(cache_path).expanduser()
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("🔍 Hardware Profiler initialized - sensing the vessel")
    
    def get_profile(self, force_refresh: bool = False) -> HardwareProfile:
        """
        Get the hardware profile, using cache if available.
        
        This is called on first setup and whenever hardware changes.
        """
        # Check cache first
        if not force_refresh and self.cache_path.exists():
            try:
                with open(self.cache_path, 'r') as f:
                    data = json.load(f)
                    self.logger.info(f"📦 Loaded cached profile: {data['tier']} tier")
                    return self._dict_to_profile(data)
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}")
        
        # Perform fresh detection
        self.logger.info("🔬 Performing hardware detection...")
        profile = self._detect_hardware()
        
        # Cache the result
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
            self.logger.info(f"💾 Cached hardware profile: {profile.tier.value}")
        except Exception as e:
            self.logger.warning(f"Failed to cache profile: {e}")
        
        return profile
    
    def _detect_hardware(self) -> HardwareProfile:
        """Perform actual hardware detection"""
        vram = self._detect_vram()
        ram = self._detect_ram()
        cpu_cores = self._detect_cpu_cores()
        gpu_name = self._detect_gpu_name()
        cuda = self._detect_cuda()
        rocm = self._detect_rocm()
        metal = self._detect_metal()
        
        # Determine tier based on VRAM
        if vram >= 24:
            tier = HardwareTier.SAGE
            tokens_per_sec = 50  # Estimated for large models
        elif vram >= 16:
            tier = HardwareTier.MASTER
            tokens_per_sec = 40
        elif vram >= 8:
            tier = HardwareTier.JOURNEYMAN
            tokens_per_sec = 30
        elif vram >= 4:
            tier = HardwareTier.APPRENTICE
            tokens_per_sec = 20
        else:
            tier = HardwareTier.NOVICE
            tokens_per_sec = 10  # CPU inference
        
        profile = HardwareProfile(
            tier=tier,
            vram_gb=vram,
            ram_gb=ram,
            cpu_cores=cpu_cores,
            gpu_name=gpu_name,
            has_cuda=cuda,
            has_rocm=rocm,
            has_metal=metal,
            estimated_tokens_per_second=tokens_per_sec
        )
        
        self.logger.info(f"🎯 Detected hardware tier: {tier.value}")
        self.logger.info(f"   VRAM: {vram}GB, RAM: {ram}GB, CPU: {cpu_cores} cores")
        if gpu_name:
            self.logger.info(f"   GPU: {gpu_name}")
        
        return profile
    
    def _detect_vram(self) -> float:
        """Detect available VRAM in GB"""
        # Try NVIDIA first
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                vram_mb = float(result.stdout.strip().split('\n')[0])
                return vram_mb / 1024  # Convert MB to GB
        except:
            pass
        
        # Try AMD ROCm
        try:
            result = subprocess.run(
                ['rocm-smi', '--showmeminfo', 'vram'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse ROCm output (format varies)
                for line in result.stdout.split('\n'):
                    if 'Total' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.isdigit():
                                return float(part) / 1024  # Assume MB
        except:
            pass
        
        # Check for Apple Silicon (Metal)
        try:
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and 'Apple' in result.stdout:
                # Apple Silicon has unified memory
                # Use a portion of system RAM as "VRAM"
                ram = self._detect_ram()
                return min(ram * 0.75, 64)  # Up to 75% of RAM, max 64GB
        except:
            pass
        
        return 0  # No GPU detected
    
    def _detect_ram(self) -> float:
        """Detect system RAM in GB"""
        try:
            # Try using free command (Linux)
            result = subprocess.run(
                ['free', '-b'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('Mem:'):
                        parts = line.split()
                        return float(parts[1]) / (1024**3)  # Convert bytes to GB
        except:
            pass
        
        try:
            # Try using sysctl (macOS)
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return float(result.stdout.strip()) / (1024**3)
        except:
            pass
        
        # Fallback
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3)
        except:
            return 8  # Default assumption
    
    def _detect_cpu_cores(self) -> int:
        """Detect number of CPU cores"""
        try:
            import os
            return os.cpu_count() or 4
        except:
            return 4
    
    def _detect_gpu_name(self) -> Optional[str]:
        """Detect GPU name"""
        # Try NVIDIA
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Try lspci
        try:
            result = subprocess.run(
                ['lspci'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'VGA' in line or 'Display' in line:
                        parts = line.split(': ', 1)
                        if len(parts) > 1:
                            return parts[1]
        except:
            pass
        
        return None
    
    def _detect_cuda(self) -> bool:
        """Detect CUDA availability"""
        try:
            result = subprocess.run(['nvcc', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _detect_rocm(self) -> bool:
        """Detect ROCm availability"""
        try:
            result = subprocess.run(['rocm-smi'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _detect_metal(self) -> bool:
        """Detect Metal availability (Apple Silicon)"""
        try:
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and 'Metal' in result.stdout
        except:
            return False
    
    def _dict_to_profile(self, data: dict) -> HardwareProfile:
        """Convert dictionary to HardwareProfile"""
        return HardwareProfile(
            tier=HardwareTier(data['tier']),
            vram_gb=data['vram_gb'],
            ram_gb=data['ram_gb'],
            cpu_cores=data['cpu_cores'],
            gpu_name=data.get('gpu_name'),
            has_cuda=data.get('has_cuda', False),
            has_rocm=data.get('has_rocm', False),
            has_metal=data.get('has_metal', False),
            estimated_tokens_per_second=data.get('estimated_tokens_per_second', 10)
        )
    
    def recommend_models(self, profile: HardwareProfile) -> Dict[str, str]:
        """
        Recommend specific models based on hardware profile.
        
        This is the wisdom of matching mind to vessel.
        """
        if profile.tier == HardwareTier.SAGE:
            return {
                'conversation': 'gpt-oss:latest',  # Or any 13B+ model
                'coding': 'qwen2:72b',             # Largest Qwen
                'reflex': 'gemma:2b',               # Still use small for speed
                'vision': 'llava:34b'               # Multimodal
            }
        elif profile.tier == HardwareTier.MASTER:
            return {
                'conversation': 'gemma2:27b',       # Large Gemma
                'coding': 'qwen2:32b',              # Large Qwen
                'reflex': 'gemma:2b',
                'vision': 'llava:13b'
            }
        elif profile.tier == HardwareTier.JOURNEYMAN:
            return {
                'conversation': 'gemma2:9b',        # Medium Gemma
                'coding': 'qwen2:7b',               # Medium Qwen
                'reflex': 'gemma:2b',
                'vision': 'llava:7b'
            }
        elif profile.tier == HardwareTier.APPRENTICE:
            return {
                'conversation': 'gemma:7b',         # Small-medium
                'coding': 'qwen2:1.5b',             # Small Qwen
                'reflex': 'gemma:2b',
                'vision': 'bakllava:latest'         # Tiny vision
            }
        else:  # NOVICE
            return {
                'conversation': 'gemma:2b',         # Tiny model
                'coding': 'gemma:2b',               # Same tiny model
                'reflex': 'gemma:2b',
                'vision': None                      # No vision model
            }


def test_hardware_profiler():
    """Test the hardware profiler"""
    print("🔬 Testing Hardware Profiler")
    print("=" * 60)
    
    profiler = HardwareProfiler()
    
    # Detect hardware
    profile = profiler.get_profile(force_refresh=True)
    
    print(f"\n📊 Hardware Profile Detected:")
    print(f"   Tier: {profile.tier.value.upper()}")
    print(f"   VRAM: {profile.vram_gb:.1f} GB")
    print(f"   RAM: {profile.ram_gb:.1f} GB")
    print(f"   CPU Cores: {profile.cpu_cores}")
    if profile.gpu_name:
        print(f"   GPU: {profile.gpu_name}")
    print(f"   CUDA: {'✅' if profile.has_cuda else '❌'}")
    print(f"   ROCm: {'✅' if profile.has_rocm else '❌'}")
    print(f"   Metal: {'✅' if profile.has_metal else '❌'}")
    print(f"   Est. Speed: {profile.estimated_tokens_per_second} tokens/sec")
    
    # Get model recommendations
    recommendations = profiler.recommend_models(profile)
    
    print(f"\n🎯 Recommended Models for {profile.tier.value.upper()} tier:")
    for task, model in recommendations.items():
        if model:
            print(f"   {task.capitalize()}: {model}")
    
    print("\n✨ Hardware profiling complete!")


if __name__ == "__main__":
    test_hardware_profiler()