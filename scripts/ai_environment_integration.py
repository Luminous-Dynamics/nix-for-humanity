#!/usr/bin/env python3
"""
from typing import List, Optional
Integration module for AI Environment Architect with ask-nix
Handles natural language requests for AI/ML environment generation
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List

# Import the AI Environment Architect
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from ai_environment_architect import AIEnvironmentArchitect

class AIEnvironmentIntegration:
    """Integrates AI environment generation with NixOS assistant"""
    
    def __init__(self):
        self.architect = AIEnvironmentArchitect()
        
        # Intent patterns for environment generation
        self.environment_patterns = [
            # Direct requests
            r"create.*(?:ai|ml|machine learning).*environment",
            r"set.*up.*(?:tensorflow|pytorch|transformers)",
            r"generate.*flake.*(?:for|with).*(?:ai|ml)",
            r"i.*(?:want|need).*(?:jupyter|notebook).*environment",
            
            # Model-specific
            r"(?:run|use).*llama.*(?:locally|cuda)",
            r"(?:stable|diffusion).*environment",
            r"langchain.*(?:setup|environment)",
            r"whisper.*(?:setup|environment)",
            
            # General ML/AI
            r"machine learning.*(?:dev|development).*environment",
            r"ai.*(?:project|development).*(?:setup|environment)",
            r"deep learning.*(?:setup|environment)",
            r"neural network.*environment"
        ]
        
    def is_environment_request(self, query: str) -> bool:
        """Check if query is asking for AI/ML environment setup"""
        query_lower = query.lower()
        
        # Check explicit patterns
        import re
        for pattern in self.environment_patterns:
            if re.search(pattern, query_lower):
                return True
                
        # Check for keywords combination
        env_keywords = ['environment', 'setup', 'flake', 'develop', 'create']
        ai_keywords = ['ai', 'ml', 'machine learning', 'tensorflow', 'pytorch', 
                      'transformers', 'jupyter', 'llama', 'langchain', 'whisper',
                      'stable diffusion', 'neural', 'deep learning']
        
        has_env = any(kw in query_lower for kw in env_keywords)
        has_ai = any(kw in query_lower for kw in ai_keywords)
        
        return has_env and has_ai
    
    def handle_environment_request(self, query: str, output_dir: Optional[str] = None) -> Dict:
        """Process environment generation request"""
        
        # Analyze requirements
        requirements = self.architect.analyze_requirements(query)
        
        # Generate flake content
        flake_content = self.architect.generate_flake(requirements)
        readme_content = self.architect.generate_readme(requirements, flake_content)
        
        # Determine output directory
        if not output_dir:
            # Extract project name from query if possible
            project_name = self._extract_project_name(query)
            output_dir = f"./{project_name}"
        
        output_path = Path(output_dir)
        
        # Prepare response
        response = {
            'success': True,
            'action': 'generate_environment',
            'requirements': requirements,
            'output_dir': str(output_path),
            'files_to_create': {
                'flake.nix': flake_content,
                'README.md': readme_content
            },
            'preview': self._generate_preview(requirements, output_path),
            'next_steps': self._generate_next_steps(requirements, output_path)
        }
        
        return response
    
    def _extract_project_name(self, query: str) -> str:
        """Try to extract project name from query"""
        import re
        
        # Look for explicit project names
        patterns = [
            r"(?:project|called|named)\s+([a-zA-Z0-9-_]+)",
            r"for\s+(?:my\s+)?([a-zA-Z0-9-_]+)\s+project",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default based on detected models
        requirements = self.architect.analyze_requirements(query)
        if requirements['models']:
            _, model, _ = requirements['models'][0]
            return f"{model}-project"
        
        return "ai-ml-project"
    
    def _generate_preview(self, requirements: Dict, output_path: Path) -> str:
        """Generate a preview of what will be created"""
        preview_lines = []
        
        preview_lines.append("🎯 AI/ML Environment Summary:")
        preview_lines.append(f"📁 Location: {output_path}/")
        preview_lines.append("")
        
        preview_lines.append("📦 Components:")
        for tier, model, info in requirements['models']:
            icon = "🔬" if tier == 'experimental' else "✅"
            preview_lines.append(f"  {icon} {info['description']}")
        
        if requirements['cuda_needed']:
            preview_lines.append("  🎮 CUDA/GPU support")
        
        if requirements['dev_tools']:
            preview_lines.append(f"  🛠️  Dev tools: {', '.join(requirements['dev_tools'][:3])}...")
        
        preview_lines.append("")
        preview_lines.append(f"💾 Minimum RAM: {requirements['estimated_ram']}")
        
        if requirements['experimental']:
            preview_lines.append("")
            preview_lines.append("⚡ Hybrid approach: Nix + pip packages")
        
        return '\n'.join(preview_lines)
    
    def _generate_next_steps(self, requirements: Dict, output_path: Path) -> List[str]:
        """Generate next steps for the user"""
        steps = []
        
        steps.append(f"mkdir -p {output_path}")
        steps.append(f"cd {output_path}")
        steps.append("# Save the generated flake.nix and README.md")
        steps.append("nix develop")
        
        if requirements['experimental']:
            steps.append("# Virtual environment will be created automatically")
        
        # Add model-specific steps
        for tier, model, _ in requirements['models']:
            if model == 'llama-cpp':
                steps.append("# Download a GGUF model to ./models/")
            elif model == 'stable-diffusion':
                steps.append("# First run will download model weights (~5GB)")
        
        return steps
    
    def format_response(self, response: Dict, personality: str = 'friendly') -> str:
        """Format response for display"""
        lines = []
        
        if personality == 'friendly':
            lines.append("🎉 Great! I'll create an AI/ML environment for you.")
            lines.append("")
        
        lines.append(response['preview'])
        lines.append("")
        
        if personality in ['friendly', 'encouraging']:
            lines.append("📝 Next steps:")
        else:
            lines.append("Next steps:")
        
        for i, step in enumerate(response['next_steps'], 1):
            if step.startswith('#'):
                lines.append(f"   {step}")
            else:
                lines.append(f"{i}. {step}")
        
        if personality == 'encouraging':
            lines.append("")
            lines.append("🌟 You're all set to start your AI/ML journey! The environment will handle all the complex setup for you.")
        
        # Add warnings if needed
        warnings = []
        for _, model, info in response['requirements']['models']:
            if 'license_warning' in info:
                warnings.append(f"⚠️  {model}: {info['license_warning']}")
        
        if warnings:
            lines.append("")
            lines.append("Legal notices:")
            lines.extend(warnings)
        
        return '\n'.join(lines)


def test_integration():
    """Test the integration module"""
    integration = AIEnvironmentIntegration()
    
    test_queries = [
        "Create an AI environment with transformers and CUDA support",
        "I want to run Llama locally for my chatbot project",
        "Set up a Jupyter notebook environment for machine learning",
        "Generate a flake for stable diffusion art generation"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}\n")
        
        if integration.is_environment_request(query):
            response = integration.handle_environment_request(query)
            formatted = integration.format_response(response)
            print(formatted)
            
            print("\n--- Generated flake.nix (first 30 lines) ---")
            flake_lines = response['files_to_create']['flake.nix'].split('\n')
            print('\n'.join(flake_lines[:30]))
            print("...")
        else:
            print("Not detected as environment request")


if __name__ == "__main__":
    test_integration()