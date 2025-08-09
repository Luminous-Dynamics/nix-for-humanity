#!/usr/bin/env python3
"""
from typing import List
AI Environment Architect - Generates sophisticated flake.nix files for ML/AI environments
Part of Nix for Humanity's natural language interface
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import textwrap

class AIEnvironmentArchitect:
    """Generates optimized Nix flakes for AI/ML environments"""
    
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.templates_dir = self.base_dir / "templates" / "ai-environments"
        
        # Model requirements database
        self.model_requirements = {
            # Stable models with direct Nix support
            'stable': {
                'pytorch': {
                    'packages': ['python311Packages.torch', 'python311Packages.torchvision',
                                'python311Packages.torchaudio'],
                    'cuda': True,
                    'min_ram': '8GB',
                    'description': 'PyTorch deep learning framework'
                },
                'transformers': {
                    'packages': ['python311Packages.transformers', 'python311Packages.torch', 
                                'python311Packages.accelerate'],
                    'cuda': True,
                    'min_ram': '8GB',
                    'description': 'Hugging Face Transformers library'
                },
                'tensorflow': {
                    'packages': ['python311Packages.tensorflow'],
                    'cuda': True,
                    'min_ram': '8GB',
                    'description': 'TensorFlow deep learning framework'
                },
                'scikit-learn': {
                    'packages': ['python311Packages.scikit-learn', 'python311Packages.pandas',
                                'python311Packages.numpy', 'python311Packages.matplotlib'],
                    'cuda': False,
                    'min_ram': '4GB',
                    'description': 'Traditional ML with scikit-learn'
                },
                'jupyter': {
                    'packages': ['python311Packages.jupyter', 'python311Packages.ipython',
                                'python311Packages.notebook'],
                    'cuda': False,
                    'min_ram': '2GB',
                    'description': 'Jupyter notebook environment'
                }
            },
            # Bleeding edge requiring pip
            'experimental': {
                'llama-cpp': {
                    'nix_packages': ['python311', 'gcc', 'cmake'],
                    'pip_packages': ['llama-cpp-python'],
                    'cuda': True,
                    'min_ram': '16GB',
                    'description': 'Llama.cpp Python bindings for local LLMs',
                    'license_warning': 'Check model licenses before commercial use'
                },
                'langchain': {
                    'nix_packages': ['python311'],
                    'pip_packages': ['langchain', 'openai', 'chromadb'],
                    'cuda': False,
                    'min_ram': '8GB',
                    'description': 'LangChain for LLM application development'
                },
                'whisper': {
                    'nix_packages': ['python311', 'ffmpeg'],
                    'pip_packages': ['openai-whisper'],
                    'cuda': True,
                    'min_ram': '8GB',
                    'description': 'OpenAI Whisper for speech recognition'
                },
                'stable-diffusion': {
                    'nix_packages': ['python311'],
                    'pip_packages': ['diffusers', 'transformers', 'accelerate'],
                    'cuda': True,
                    'min_ram': '16GB',
                    'description': 'Stable Diffusion image generation',
                    'license_warning': 'Check model licenses and ethical usage guidelines'
                }
            }
        }
        
        # Common development tools
        self.dev_tools = {
            'essential': ['git', 'curl', 'wget', 'jq', 'ripgrep'],
            'monitoring': ['htop', 'nvtop', 'iotop'],
            'editors': ['neovim', 'vscode']
        }
        
    def analyze_requirements(self, user_request: str) -> Dict:
        """Analyze user requirements and determine needed components"""
        request_lower = user_request.lower()
        
        requirements = {
            'models': [],
            'cuda_needed': False,
            'experimental': False,
            'dev_tools': [],
            'custom_packages': [],
            'estimated_ram': '4GB'
        }
        
        # Check for stable models
        for model, info in self.model_requirements['stable'].items():
            if model in request_lower or any(keyword in request_lower 
                for keyword in self._get_model_keywords(model)):
                requirements['models'].append(('stable', model, info))
                if info.get('cuda'):
                    requirements['cuda_needed'] = True
                    
        # Check for experimental models
        for model, info in self.model_requirements['experimental'].items():
            if model in request_lower or any(keyword in request_lower 
                for keyword in self._get_model_keywords(model)):
                requirements['models'].append(('experimental', model, info))
                requirements['experimental'] = True
                if info.get('cuda'):
                    requirements['cuda_needed'] = True
                    
        # Auto-add dev tools based on context
        if any(word in request_lower for word in ['develop', 'code', 'build']):
            requirements['dev_tools'].extend(self.dev_tools['essential'])
        if 'edit' in request_lower or 'vim' in request_lower:
            requirements['dev_tools'].extend(self.dev_tools['editors'])
        if requirements['cuda_needed']:
            requirements['dev_tools'].extend(self.dev_tools['monitoring'])
            
        # Estimate RAM requirements
        max_ram = 4
        for _, _, info in requirements['models']:
            ram_str = info.get('min_ram', '4GB')
            ram_gb = int(ram_str.replace('GB', ''))
            max_ram = max(max_ram, ram_gb)
        requirements['estimated_ram'] = f"{max_ram}GB"
        
        return requirements
    
    def _get_model_keywords(self, model: str) -> List[str]:
        """Get keywords associated with a model"""
        keywords = {
            'pytorch': ['torch', 'neural', 'deep learning', 'cnn', 'rnn'],
            'transformers': ['hugging face', 'bert', 'gpt', 'nlp'],
            'tensorflow': ['tf', 'keras', 'deep learning'],
            'scikit-learn': ['sklearn', 'ml', 'machine learning'],
            'jupyter': ['notebook', 'ipynb'],
            'llama-cpp': ['llama', 'local llm', 'gguf'],
            'langchain': ['chain', 'rag', 'agent'],
            'whisper': ['speech', 'audio', 'transcription'],
            'stable-diffusion': ['image', 'diffusion', 'sdxl', 'art']
        }
        return keywords.get(model, [])
    
    def generate_flake(self, requirements: Dict, project_name: str = "ai-env") -> str:
        """Generate a complete flake.nix file"""
        flake = []
        
        # Header
        flake.append('''{
  description = "AI/ML Development Environment - Generated by Nix for Humanity";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        ''')
        
        # Python packages section
        if requirements['experimental']:
            flake.append('''
        # Python environment with pip for experimental packages
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          pip
          virtualenv
          setuptools
          wheel''')
            
            # Add stable Python packages
            for tier, model, info in requirements['models']:
                if tier == 'stable':
                    for pkg in info['packages']:
                        if pkg.startswith('python311Packages.'):
                            pkg_name = pkg.replace('python311Packages.', '')
                            flake.append(f'          {pkg_name}')
            flake.append('        ]);')
        else:
            # Pure Nix approach for stable packages
            python_packages = []
            for tier, model, info in requirements['models']:
                if tier == 'stable':
                    python_packages.extend(info['packages'])
            
            if python_packages:
                flake.append('        pythonPackages = with pkgs; [')
                for pkg in python_packages:
                    flake.append(f'          {pkg}')
                flake.append('        ];')
        
        # Main derivation
        flake.append('''
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [''')
        
        # Add system packages
        if requirements['experimental']:
            flake.append('            pythonEnv')
        elif 'pythonPackages' in '\n'.join(flake):
            flake.append('            python311')
        
        # Add CUDA support if needed
        if requirements['cuda_needed']:
            flake.append('''            
            # CUDA support
            cudaPackages.cudatoolkit
            cudaPackages.cudnn''')
        
        # Add development tools
        for tool in set(requirements['dev_tools']):
            flake.append(f'            {tool}')
        
        # Add additional packages for experimental models
        all_nix_packages = set()
        for tier, model, info in requirements['models']:
            if tier == 'experimental':
                all_nix_packages.update(info.get('nix_packages', []))
        
        for pkg in all_nix_packages:
            if pkg != 'python311':  # Already added
                flake.append(f'            {pkg}')
        
        flake.append('          ]')
        
        # Add Python packages if using pure Nix
        if not requirements['experimental'] and 'pythonPackages' in '\n'.join(flake):
            flake.append('            ++ pythonPackages;')
        else:
            flake.append(';')
        
        # Shell hook
        flake.append('''
          shellHook = \'\'
            echo "🤖 AI/ML Development Environment"
            echo "================================"''')
        
        # Add model information
        for tier, model, info in requirements['models']:
            desc = info.get('description', model)
            flake.append(f'            echo "✓ {desc}"')
        
        if requirements['cuda_needed']:
            flake.append('            echo "✓ CUDA support enabled"')
        
        flake.append(f'            echo "✓ Estimated RAM needed: {requirements["estimated_ram"]}"')
        
        # Add pip setup for experimental
        if requirements['experimental']:
            flake.append('''
            echo ""
            echo "📦 Setting up Python virtual environment..."
            
            # Create venv if it doesn't exist
            if [ ! -d ".venv" ]; then
              python -m venv .venv
            fi
            
            # Activate venv
            source .venv/bin/activate
            
            # Upgrade pip
            pip install --upgrade pip
            
            echo ""
            echo "📋 Installing experimental packages..."''')
            
            # Install pip packages
            pip_packages = []
            for tier, model, info in requirements['models']:
                if tier == 'experimental':
                    pip_packages.extend(info.get('pip_packages', []))
            
            if pip_packages:
                pip_cmd = 'pip install ' + ' '.join(pip_packages)
                flake.append(f'            echo "{pip_cmd}"')
                flake.append(f'            {pip_cmd}')
        
        # License warnings
        warnings = []
        for tier, model, info in requirements['models']:
            if 'license_warning' in info:
                warnings.append(f"{model}: {info['license_warning']}")
        
        if warnings:
            flake.append('''
            echo ""
            echo "⚠️  License Warnings:"''')
            for warning in warnings:
                flake.append(f'            echo "  - {warning}"')
        
        # Final message
        flake.append('''
            echo ""
            echo "🚀 Environment ready! Happy hacking!"
          \'\';''')
        
        # Environment variables
        if requirements['cuda_needed']:
            flake.append('''
          # CUDA environment variables
          LD_LIBRARY_PATH = "${pkgs.cudaPackages.cudatoolkit}/lib:${pkgs.cudaPackages.cudnn}/lib";
          CUDA_PATH = "${pkgs.cudaPackages.cudatoolkit}";''')
        
        # Close the flake
        flake.append('''        };
      }
    );
}''')
        
        return '\n'.join(flake)
    
    def generate_readme(self, requirements: Dict, flake_content: str) -> str:
        """Generate a README with usage instructions"""
        readme = ['''# AI/ML Development Environment

Generated by Nix for Humanity - Natural Language NixOS Interface

## Quick Start

1. Make sure you have Nix with flakes enabled:
   ```bash
   nix --version  # Should be 2.4 or higher
   ```

2. Enter the development environment:
   ```bash
   nix develop
   ```

3. Start coding!

## What's Included
''']
        
        # List included models
        for tier, model, info in requirements['models']:
            desc = info.get('description', model)
            readme.append(f"- **{desc}**")
            if tier == 'experimental':
                readme.append(f"  - Installed via pip: {', '.join(info.get('pip_packages', []))}")
            else:
                readme.append(f"  - Pure Nix packages")
        
        if requirements['cuda_needed']:
            readme.append("\n### GPU Support")
            readme.append("- CUDA toolkit and cuDNN are included")
            readme.append("- Make sure you have NVIDIA drivers installed on your host system")
        
        readme.append(f"\n### System Requirements")
        readme.append(f"- Minimum RAM: {requirements['estimated_ram']}")
        if requirements['cuda_needed']:
            readme.append("- NVIDIA GPU with CUDA support")
        
        if requirements['experimental']:
            readme.append('''
## Python Virtual Environment

This flake automatically creates and activates a Python virtual environment
with all experimental packages installed via pip.

To manually activate the venv:
```bash
source .venv/bin/activate
```

To install additional packages:
```bash
pip install <package-name>
```
''')
        
        # Add example code
        readme.append("\n## Example Usage\n")
        
        # Add model-specific examples
        for tier, model, info in requirements['models']:
            if model == 'transformers':
                readme.append('''### Transformers Example
```python
from transformers import pipeline
classifier = pipeline("sentiment-analysis")
result = classifier("I love using Nix for ML development!")
print(result)
```
''')
            elif model == 'llama-cpp':
                readme.append('''### Llama.cpp Example
```python
from llama_cpp import Llama
llm = Llama(model_path="./models/llama-2-7b.gguf")
output = llm("Q: What is Nix? A:", max_tokens=100)
print(output)
```
''')
            elif model == 'stable-diffusion':
                readme.append('''### Stable Diffusion Example
```python
from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

image = pipe("A beautiful landscape in the style of Claude Monet").images[0]
image.save("landscape.png")
```
''')
        
        readme.append('''
## Customization

To add more packages, edit `flake.nix` and add them to the `buildInputs` section.

## Troubleshooting

- **CUDA not found**: Make sure NVIDIA drivers are installed on your host
- **Out of memory**: Close other applications or use a model with lower requirements
- **Package conflicts**: Try using a fresh virtual environment

---
Generated with ❤️ by Nix for Humanity
''')
        
        return '\n'.join(readme)


def main():
    """CLI interface for testing"""
    architect = AIEnvironmentArchitect()
    
    # Test examples
    test_cases = [
        "I want to run Llama locally with CUDA",
        "Set up a Jupyter notebook for machine learning",
        "I need transformers and langchain for my NLP project",
        "Create a stable diffusion environment"
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Request: {test}")
        print(f"{'='*60}\n")
        
        requirements = architect.analyze_requirements(test)
        print("Requirements detected:")
        print(json.dumps(requirements, indent=2))
        
        flake = architect.generate_flake(requirements)
        print("\nGenerated flake.nix preview (first 20 lines):")
        print('\n'.join(flake.split('\n')[:20]))
        print("...")


if __name__ == "__main__":
    main()