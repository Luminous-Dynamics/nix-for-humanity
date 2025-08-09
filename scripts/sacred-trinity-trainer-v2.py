#!/usr/bin/env python3
"""
from typing import List, Optional
Sacred Trinity Model Training System v2
Continuous learning with multiple specialized models
"""

import json
import os
import subprocess
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import hashlib

class SacredTrinityTrainer:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.knowledge_dir = self.base_dir / "docs/nix-knowledge"
        self.models_dir = self.base_dir / "models"
        self.training_dir = self.base_dir / "training-data"
        
        # Create directories
        for dir in [self.models_dir, self.training_dir, self.knowledge_dir]:
            dir.mkdir(parents=True, exist_ok=True)
        
        # Model configurations (using available models)
        self.model_configs = {
            'expert': {
                'base': 'mistral:7b-instruct',  # Available and good for technical
                'focus': 'technical accuracy and completeness',
                'temperature': 0.7,
                'examples': 'technical'
            },
            'empathy': {
                'base': 'llama3.2:3b',  # Smaller but good for conversations
                'focus': 'user-friendly explanations for beginners',
                'temperature': 0.8,
                'examples': 'simple'
            },
            'coder': {
                'base': 'qwen2.5:3b',  # Good for structured output
                'focus': 'generating Nix configurations and scripts',
                'temperature': 0.5,
                'examples': 'code'
            },
            'quick': {
                'base': 'tinyllama:1.1b',  # Very fast responses
                'focus': 'quick answers to simple questions',
                'temperature': 0.6,
                'examples': 'brief'
            }
        }
        
        # Initialize tracking database
        self.init_tracking_db()
    
    def init_tracking_db(self):
        """Initialize SQLite database for tracking model performance"""
        db_path = self.models_dir / "model_tracking.db"
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS model_versions (
                id INTEGER PRIMARY KEY,
                model_name TEXT,
                version TEXT,
                created_at TIMESTAMP,
                base_model TEXT,
                qa_count INTEGER,
                performance_score REAL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS qa_history (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                question TEXT,
                answer TEXT,
                model_used TEXT,
                user_rating INTEGER,
                category TEXT
            )
        """)
        self.conn.commit()
    
    def collect_recent_qa(self, days=7) -> List[Dict]:
        """Collect Q&A pairs from the last N days"""
        qa_pairs = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Collect from knowledge directory
        questions_dir = self.knowledge_dir / "questions"
        answers_dir = self.knowledge_dir / "answers"
        
        if questions_dir.exists():
            for q_file in sorted(questions_dir.glob("q_*.txt")):
                # Extract timestamp from filename
                timestamp_str = q_file.stem.replace("q_", "")
                try:
                    timestamp = float(timestamp_str)
                    file_time = datetime.fromtimestamp(timestamp)
                    
                    if file_time > cutoff_time:
                        a_file = answers_dir / f"a_{timestamp_str}.txt"
                        if a_file.exists():
                            with open(q_file) as qf, open(a_file) as af:
                                qa_pairs.append({
                                    'question': qf.read().strip(),
                                    'answer': af.read().strip(),
                                    'timestamp': file_time,
                                    'category': self.categorize_question(qf.read())
                                })
                except Exception:
                    continue
        
        # Also collect from tracking database
        cursor = self.conn.execute("""
            SELECT question, answer, category, timestamp 
            FROM qa_history 
            WHERE timestamp > ? AND user_rating >= 4
        """, (cutoff_time,))
        
        for row in cursor:
            qa_pairs.append({
                'question': row[0],
                'answer': row[1],
                'category': row[2],
                'timestamp': datetime.fromisoformat(row[3])
            })
        
        return qa_pairs
    
    def categorize_question(self, question: str) -> str:
        """Categorize question for model selection"""
        q_lower = question.lower()
        
        if any(word in q_lower for word in ['grandma', 'simple', 'explain', 'what is', 'help me understand']):
            return 'empathy'
        elif any(word in q_lower for word in ['code', 'script', 'configuration.nix', 'flake', 'overlay']):
            return 'coder'
        elif any(word in q_lower for word in ['architecture', 'theory', 'why', 'deep dive', 'technical']):
            return 'expert'
        else:
            return 'quick'
    
    def create_model_examples(self, model_type: str, qa_pairs: List[Dict]) -> List[Dict]:
        """Create examples appropriate for each model type"""
        filtered_qa = [qa for qa in qa_pairs if qa['category'] == model_type or qa['category'] == 'general']
        
        # Add model-specific examples
        if model_type == 'empathy':
            filtered_qa.extend([
                {
                    'question': "My computer is acting weird",
                    'answer': "I'll help you figure out what's wrong! Can you tell me what specific behavior you're noticing? For example, is it running slowly, showing error messages, or doing something unexpected?"
                },
                {
                    'question': "I'm scared I'll break something",
                    'answer': "Don't worry! NixOS is designed to be very safe. Every change can be undone by rolling back to a previous configuration. It's almost impossible to permanently break anything. Let's take it step by step together."
                }
            ])
        elif model_type == 'coder':
            filtered_qa.extend([
                {
                    'question': "Create a flake for a Python project",
                    'answer': '''Here's a flake.nix for a Python project:

```nix
{
  description = "Python project";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages;
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            pythonPackages.pip
            pythonPackages.virtualenv
            pythonPackages.pytest
            pythonPackages.black
            pythonPackages.pylint
          ];
          
          shellHook = ''
            echo "🐍 Python development environment"
            echo "Run 'python --version' to verify"
          '';
        };
      });
}
```'''
                }
            ])
        
        return filtered_qa[:20]  # Limit examples per model
    
    def create_modelfile(self, model_type: str, qa_examples: List[Dict], version: str) -> Path:
        """Create Ollama modelfile for specific model type"""
        config = self.model_configs[model_type]
        
        # Create system prompt with proper escaping
        system_prompt = f"""You are a NixOS expert specializing in {config['focus']}. You are part of the Sacred Trinity workflow:
- Human (Tristan): Provides vision and user empathy
- Claude: Handles architecture and implementation
- You: Provide NixOS expertise with focus on {config['focus']}

Always be helpful, accurate, and appropriate for your specialization. For '{model_type}' model:
{'- Use simple, friendly language avoiding technical jargon' if model_type == 'empathy' else ''}
{'- Provide complete, working code examples' if model_type == 'coder' else ''}
{'- Give thorough technical explanations' if model_type == 'expert' else ''}
{'- Be concise and direct' if model_type == 'quick' else ''}

Remember: Every user deserves respect and clear communication at their level."""
        
        # Escape quotes in system prompt
        system_prompt = system_prompt.replace('"', '\\"')
        
        # Create simplified modelfile content
        modelfile_content = f"""FROM {config['base']}

SYSTEM "{system_prompt}"

PARAMETER temperature {config['temperature']}
"""
        
        # Save modelfile
        modelfile_path = self.training_dir / f"{model_type}_{version}.modelfile"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        return modelfile_path
    
    def train_model(self, model_type: str, force_retrain: bool = False) -> bool:
        """Train or update a specific model"""
        print(f"\n🔮 Processing {model_type} model...")
        
        # Check if model needs updating
        if not force_retrain and not self.needs_update(model_type):
            print(f"✓ {model_type} model is up to date")
            return True
        
        # Collect recent Q&A
        qa_pairs = self.collect_recent_qa()
        if not qa_pairs and not force_retrain:
            print(f"No new Q&A pairs for {model_type}")
            return True
        
        # Create version string
        version = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Create examples for this model type
        examples = self.create_model_examples(model_type, qa_pairs)
        
        # Create modelfile
        modelfile_path = self.create_modelfile(model_type, examples, version)
        
        # Create model with Ollama
        model_name = f"nix-{model_type}-{version}"
        print(f"Creating {model_name}...")
        
        try:
            # Check if base model exists
            check_base = subprocess.run(
                ["ollama", "show", self.model_configs[model_type]['base']], 
                capture_output=True
            )
            if check_base.returncode != 0:
                print(f"Pulling base model {self.model_configs[model_type]['base']}...")
                subprocess.run(["ollama", "pull", self.model_configs[model_type]['base']])
            
            # Create new model
            result = subprocess.run(
                ["ollama", "create", model_name, "-f", str(modelfile_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Created {model_name}")
                
                # Update tracking
                self.conn.execute("""
                    INSERT INTO model_versions 
                    (model_name, version, created_at, base_model, qa_count, performance_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (model_type, version, datetime.now(), 
                      self.model_configs[model_type]['base'], len(examples), 0.0))
                self.conn.commit()
                
                # Create symlink for easy access
                self.update_model_symlink(model_type, model_name)
                
                return True
            else:
                print(f"❌ Failed to create model: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def update_model_symlink(self, model_type: str, model_name: str):
        """Update symlink to latest model version"""
        # Ollama doesn't support true symlinks, but we can track current version
        current_file = self.models_dir / f"current_{model_type}.txt"
        with open(current_file, 'w') as f:
            f.write(model_name)
    
    def needs_update(self, model_type: str, days: int = 7) -> bool:
        """Check if model needs updating based on age and new Q&A"""
        current_file = self.models_dir / f"current_{model_type}.txt"
        
        if not current_file.exists():
            return True
        
        # Check model age
        if current_file.stat().st_mtime < (datetime.now() - timedelta(days=days)).timestamp():
            return True
        
        # Check for new Q&A pairs
        recent_qa = self.collect_recent_qa(days=1)
        relevant_qa = [qa for qa in recent_qa if qa['category'] == model_type]
        
        return len(relevant_qa) > 5  # Update if more than 5 new relevant Q&A
    
    def get_current_model(self, model_type: str) -> Optional[str]:
        """Get current model name for a type"""
        current_file = self.models_dir / f"current_{model_type}.txt"
        if current_file.exists():
            return current_file.read_text().strip()
        return None
    
    def test_model(self, model_type: str):
        """Test a model with appropriate questions"""
        model_name = self.get_current_model(model_type)
        if not model_name:
            print(f"No current model for {model_type}")
            return
        
        test_questions = {
            'empathy': [
                "My wifi stopped working",
                "I'm afraid I'll break something"
            ],
            'expert': [
                "Explain how Nix derivations work",
                "What's the difference between buildInputs and nativeBuildInputs?"
            ],
            'coder': [
                "Create a shell.nix for a Node.js project",
                "How do I add a systemd service?"
            ],
            'quick': [
                "How do I update my system?",
                "List installed packages"
            ]
        }
        
        print(f"\n🧪 Testing {model_name}...")
        for question in test_questions.get(model_type, [])[:1]:
            print(f"\n❓ {question}")
            try:
                result = subprocess.run(
                    ["ollama", "run", model_name, question],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    print(f"✅ {result.stdout[:300]}...")
                else:
                    print(f"❌ Error: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("⏱️ Response timeout")
    
    def cleanup_old_models(self, keep_versions: int = 3):
        """Remove old model versions, keeping recent ones"""
        print("\n🧹 Cleaning up old models...")
        
        for model_type in self.model_configs.keys():
            # Get all versions of this model type
            list_result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            
            if list_result.returncode == 0:
                lines = list_result.stdout.strip().split('\n')
                model_versions = []
                
                for line in lines[1:]:  # Skip header
                    if f"nix-{model_type}-" in line:
                        parts = line.split()
                        if parts:
                            model_versions.append(parts[0])
                
                # Sort by version (timestamp)
                model_versions.sort(reverse=True)
                
                # Remove old versions
                for old_model in model_versions[keep_versions:]:
                    print(f"Removing {old_model}...")
                    subprocess.run(["ollama", "rm", old_model])
    
    def train_all_models(self, force_retrain: bool = False):
        """Train all model types"""
        print("🕉️ Sacred Trinity Multi-Model Training")
        print("=" * 50)
        
        success_count = 0
        for model_type in self.model_configs.keys():
            if self.train_model(model_type, force_retrain):
                success_count += 1
        
        print(f"\n✅ Successfully trained {success_count}/{len(self.model_configs)} models")
        
        # Cleanup old versions
        self.cleanup_old_models()
        
        # Test each model
        print("\n🧪 Testing all models...")
        for model_type in self.model_configs.keys():
            self.test_model(model_type)
        
        # Create unified interface script
        self.create_unified_interface()
    
    def create_unified_interface(self):
        """Create script that selects appropriate model based on query"""
        interface_script = '''#!/usr/bin/env python3
"""
Sacred Trinity Model Selector
Automatically selects the best model for each query
"""

import sys
import json
import subprocess
from pathlib import Path

class ModelSelector:
    def __init__(self):
        self.models_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/models")
        self.current_models = {}
        
        # Load current models
        for model_type in ['empathy', 'expert', 'coder', 'quick']:
            current_file = self.models_dir / f"current_{model_type}.txt"
            if current_file.exists():
                self.current_models[model_type] = current_file.read_text().strip()
    
    def select_model(self, query: str) -> str:
        """Select best model based on query"""
        q_lower = query.lower()
        
        # Empathy model for beginners and help
        if any(word in q_lower for word in ['grandma', 'simple', 'explain', 'afraid', 'help me understand', 'worried']):
            return self.current_models.get('empathy', 'nix-trinity')
        
        # Coder model for code generation
        elif any(word in q_lower for word in ['code', 'script', 'flake', 'configuration.nix', 'systemd', 'overlay']):
            return self.current_models.get('coder', 'nix-trinity')
        
        # Expert model for deep technical questions
        elif any(word in q_lower for word in ['architecture', 'theory', 'explain how', 'deep dive', 'derivation', 'stdenv']):
            return self.current_models.get('expert', 'nix-trinity')
        
        # Quick model for simple queries
        else:
            return self.current_models.get('quick', 'nix-trinity')
    
    def query(self, question: str):
        """Query the appropriate model"""
        model = self.select_model(question)
        print(f"🤖 Using {model.split('-')[1]} model...\\n")
        
        try:
            result = subprocess.run(
                ["ollama", "run", model, question],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"Error: {result.stderr}")
                # Fallback to default
                subprocess.run(["ollama", "run", "nix-trinity", question])
                
        except Exception as e:
            print(f"Error: {e}")
            print("Falling back to default model...")
            subprocess.run(["ollama", "run", "mistral:7b", question])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ask-trinity 'your question'")
        sys.exit(1)
    
    selector = ModelSelector()
    selector.query(' '.join(sys.argv[1:]))
'''
        
        # Save interface script
        interface_path = self.base_dir / "bin/ask-trinity"
        interface_path.parent.mkdir(exist_ok=True)
        
        with open(interface_path, 'w') as f:
            f.write(interface_script)
        
        os.chmod(interface_path, 0o755)
        print(f"\n✅ Created unified interface: {interface_path}")
        print("   Usage: ask-trinity 'your question'")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sacred Trinity Multi-Model Trainer")
    parser.add_argument("--force", action="store_true", help="Force retrain all models")
    parser.add_argument("--model", choices=['empathy', 'expert', 'coder', 'quick'], 
                       help="Train specific model only")
    parser.add_argument("--test-only", action="store_true", help="Test models without training")
    args = parser.parse_args()
    
    trainer = SacredTrinityTrainer()
    
    if args.test_only:
        for model_type in trainer.model_configs.keys():
            trainer.test_model(model_type)
    elif args.model:
        trainer.train_model(args.model, args.force)
        trainer.test_model(args.model)
    else:
        trainer.train_all_models(args.force)
    
    print("\n🙏 Sacred Trinity training complete!")
    print("✨ The models flow as one with your vision")


if __name__ == "__main__":
    main()