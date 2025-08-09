#!/usr/bin/env python3
"""
from typing import Tuple, Optional
AI Environment Generator - Actually creates the flake.nix files
Handles file creation, validation, and user interaction
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

class AIEnvironmentGenerator:
    """Handles actual generation of AI/ML environment files"""
    
    def __init__(self):
        self.generated_environments = []
        
    def create_environment(self, response: Dict, target_dir: Optional[str] = None, 
                          force: bool = False) -> Tuple[bool, str]:
        """
        Actually create the environment files
        
        Args:
            response: Response dict from AIEnvironmentIntegration
            target_dir: Override target directory
            force: Overwrite existing files
            
        Returns:
            (success, message)
        """
        
        # Determine target directory
        if target_dir:
            output_dir = Path(target_dir)
        else:
            output_dir = Path(response.get('output_dir', './ai-ml-project'))
        
        # Check if directory exists
        if output_dir.exists() and not force:
            if any(output_dir.iterdir()):
                return False, f"Directory {output_dir} already exists and is not empty. Use --force to overwrite."
        
        # Create directory
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Failed to create directory: {e}"
        
        # Write files
        files_created = []
        try:
            for filename, content in response['files_to_create'].items():
                file_path = output_dir / filename
                
                # Backup existing file if force is used
                if file_path.exists() and force:
                    backup_path = file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                    shutil.copy2(file_path, backup_path)
                    files_created.append(f"Backed up: {backup_path}")
                
                # Write the file
                with open(file_path, 'w') as f:
                    f.write(content)
                files_created.append(f"Created: {file_path}")
                
                # Make scripts executable if needed
                if filename.endswith('.sh'):
                    os.chmod(file_path, 0o755)
            
            # Create .gitignore for Python projects
            if response['requirements'].get('experimental'):
                gitignore_path = output_dir / '.gitignore'
                with open(gitignore_path, 'w') as f:
                    f.write(self._generate_gitignore())
                files_created.append(f"Created: {gitignore_path}")
            
            # Create .envrc for direnv users
            envrc_path = output_dir / '.envrc'
            with open(envrc_path, 'w') as f:
                f.write("use flake\n")
            files_created.append(f"Created: {envrc_path}")
            
            # Track this environment
            self.generated_environments.append({
                'path': str(output_dir),
                'timestamp': datetime.now().isoformat(),
                'requirements': response['requirements']
            })
            
            # Success message
            success_msg = "\n".join([
                f"✅ Environment created successfully in {output_dir}",
                "",
                "Files created:",
                *[f"  {fc}" for fc in files_created],
                "",
                "Next steps:",
                f"  cd {output_dir}",
                "  nix develop",
                "",
                "💡 Tip: If you use direnv, run 'direnv allow' to auto-activate"
            ])
            
            return True, success_msg
            
        except Exception as e:
            # Cleanup on failure
            if output_dir.exists() and not any(output_dir.iterdir()):
                output_dir.rmdir()
            return False, f"Failed to create files: {e}"
    
    def validate_environment(self, env_dir: str) -> Tuple[bool, str]:
        """Validate that an environment is properly set up"""
        env_path = Path(env_dir)
        
        if not env_path.exists():
            return False, f"Directory {env_dir} does not exist"
        
        # Check for required files
        flake_path = env_path / "flake.nix"
        if not flake_path.exists():
            return False, "Missing flake.nix file"
        
        # Basic flake validation
        try:
            with open(flake_path, 'r') as f:
                content = f.read()
                
            # Check for basic flake structure
            required_elements = ['description', 'inputs', 'outputs', 'devShells']
            missing = [elem for elem in required_elements if elem not in content]
            
            if missing:
                return False, f"Flake.nix missing required elements: {', '.join(missing)}"
            
            # Check if it's a Nix for Humanity generated flake
            if "Generated by Nix for Humanity" in content:
                return True, "✅ Valid Nix for Humanity AI environment"
            else:
                return True, "✅ Valid flake.nix (not generated by Nix for Humanity)"
                
        except Exception as e:
            return False, f"Error reading flake.nix: {e}"
    
    def _generate_gitignore(self) -> str:
        """Generate appropriate .gitignore for AI/ML projects"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb_checkpoints

# ML/AI specific
models/
*.ckpt
*.h5
*.pkl
*.pth
*.onnx
*.tflite
checkpoints/
logs/
tensorboard/
wandb/

# Data
data/
datasets/
*.csv
*.parquet
*.json
*.jsonl

# Environment
.env
.envrc.local
.direnv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Nix
result
result-*
"""
    
    def create_example_notebook(self, env_dir: str, model_type: str) -> Tuple[bool, str]:
        """Create an example Jupyter notebook for the environment"""
        examples = {
            'transformers': '''# Transformers Example
from transformers import pipeline

# Load a pre-trained model
classifier = pipeline("sentiment-analysis")

# Test it out
texts = [
    "I love using Nix for ML development!",
    "This is frustrating and doesn't work.",
    "The weather is nice today."
]

for text in texts:
    result = classifier(text)
    print(f"Text: {text}")
    print(f"Result: {result[0]['label']} (confidence: {result[0]['score']:.2f})")
    print()
''',
            'sklearn': '''# Scikit-learn Example
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
''',
            'pytorch': '''# PyTorch Example
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Check CUDA availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Simple neural network
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(10, 50)
        self.fc2 = nn.Linear(50, 1)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Create model
model = SimpleNet().to(device)
print(f"Model: {model}")

# Generate some dummy data
X = torch.randn(100, 10).to(device)
y = torch.randn(100, 1).to(device)

# Training setup
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Quick training loop
for epoch in range(10):
    optimizer.zero_grad()
    outputs = model(X)
    loss = criterion(outputs, y)
    loss.backward()
    optimizer.step()
    
    if epoch % 2 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
'''
        }
        
        # Determine which example to use
        example_content = examples.get(model_type, examples['sklearn'])
        
        # Create notebook structure
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# {model_type.title()} Example Notebook\n",
                        "\n",
                        "This notebook was generated by Nix for Humanity to help you get started.\n",
                        "\n",
                        "## Setup\n",
                        "\n",
                        "Make sure you're in the Nix development environment:\n",
                        "```bash\n",
                        "nix develop\n",
                        "jupyter notebook\n",
                        "```"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": example_content.strip().split('\n')
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.11.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Write notebook
        try:
            notebook_path = Path(env_dir) / "example.ipynb"
            with open(notebook_path, 'w') as f:
                json.dump(notebook, f, indent=2)
            
            return True, f"Created example notebook: {notebook_path}"
        except Exception as e:
            return False, f"Failed to create notebook: {e}"


def main():
    """CLI for testing"""
    generator = AIEnvironmentGenerator()
    
    # Test validation
    test_dirs = [".", "./test-env", "/tmp/test-ml-env"]
    
    for dir_path in test_dirs:
        valid, msg = generator.validate_environment(dir_path)
        print(f"\nValidating {dir_path}: {msg}")


if __name__ == "__main__":
    main()