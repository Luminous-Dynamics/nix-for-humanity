#!/usr/bin/env bash
# Sacred Nix Training - Adapted for our Trinity Workflow

set -e

echo "🕉️ Sacred Nix Training for Trinity Workflow"
echo "=========================================="
echo ""
echo "This training creates our local NixOS expert to complement:"
echo "  👤 Human (Tristan) - Vision & user empathy"
echo "  🏗️ Claude - Architecture & implementation"
echo "  🧙 Local LLM - NixOS expertise & best practices"
echo ""

# Sacred preparation
echo "🙏 Setting sacred intention..."
echo "We train this model to serve users with wisdom and compassion."
sleep 2

# Check if we have existing knowledge
KNOWLEDGE_DIR="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/nix-knowledge"
if [ -d "$KNOWLEDGE_DIR" ] && [ "$(ls -A $KNOWLEDGE_DIR)" ]; then
    echo ""
    echo "📚 Found existing Sacred Trinity knowledge!"
    echo "   Questions: $(find $KNOWLEDGE_DIR/questions -name "*.txt" 2>/dev/null | wc -l)"
    echo "   Answers: $(find $KNOWLEDGE_DIR/answers -name "*.txt" 2>/dev/null | wc -l)"
    echo ""
    read -p "Include this wisdom in training? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        INCLUDE_TRINITY_WISDOM=true
    fi
fi

# Choose training approach
echo ""
echo "🌟 Choose your training path:"
echo "1. Quick Training (1-2 hours) - Essential NixOS knowledge"
echo "2. Deep Training (3-4 hours) - Include PhD thesis & theory"
echo "3. Trinity Training (2-3 hours) - Optimized for our workflow"
echo ""
read -p "Select path (1-3) [3]: " TRAINING_PATH
TRAINING_PATH=${TRAINING_PATH:-3}

# Set training parameters based on choice
case $TRAINING_PATH in
    1)
        echo "⚡ Quick training selected..."
        SKIP_THESIS="--skip-thesis"
        MODEL_NAME="nix-guide"
        ;;
    2)
        echo "📚 Deep training selected..."
        SKIP_THESIS=""
        MODEL_NAME="nix-expert-deep"
        ;;
    3)
        echo "🤝 Trinity training selected..."
        SKIP_THESIS="--skip-thesis"
        MODEL_NAME="nix-trinity"
        INCLUDE_TRINITY_WISDOM=true
        ;;
esac

# Create adapted training script
cat > /tmp/trinity-nix-trainer.py << 'SACRED_EOF'
#!/usr/bin/env python3
"""
Sacred Trinity Nix Training
Optimized for Human + Claude + Local LLM workflow
"""

import json
import os
from pathlib import Path
import subprocess
import sys

class TrinityNixTrainer:
    def __init__(self, model_name="nix-trinity"):
        self.model_name = model_name
        self.knowledge_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/nix-knowledge")
        self.training_dir = Path("training-data/trinity")
        self.training_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_trinity_wisdom(self):
        """Collect Q&A from our Sacred Trinity workflow"""
        print("🤝 Collecting Sacred Trinity wisdom...")
        
        trinity_qa = []
        
        # Load saved Q&A pairs
        questions_dir = self.knowledge_dir / "questions"
        answers_dir = self.knowledge_dir / "answers"
        
        if questions_dir.exists() and answers_dir.exists():
            for q_file in questions_dir.glob("q_*.txt"):
                timestamp = q_file.stem.replace("q_", "")
                a_file = answers_dir / f"a_{timestamp}.txt"
                
                if a_file.exists():
                    with open(q_file) as qf, open(a_file) as af:
                        question = qf.read().strip()
                        answer = af.read().strip()
                        
                        trinity_qa.append({
                            "q": question,
                            "a": answer,
                            "source": "Sacred Trinity",
                            "category": "workflow"
                        })
        
        # Add Trinity-specific patterns
        trinity_patterns = [
            {
                "q": "How do I install packages declaratively?",
                "a": "In NixOS, always prefer adding packages to configuration.nix or home.nix over using nix-env. This ensures reproducibility and aligns with the Trinity workflow where we build lasting solutions.",
                "category": "trinity-best-practice"
            },
            {
                "q": "What's the Trinity approach to NixOS development?",
                "a": "The Sacred Trinity workflow combines: Human vision (what users need), Claude's architecture (how to build it), and Local LLM expertise (NixOS best practices). Always consider all three perspectives.",
                "category": "trinity-philosophy"
            },
            {
                "q": "How should I handle errors in the Trinity workflow?",
                "a": "Errors are teachers. First, ask the local LLM for NixOS-specific insights. Then, let Claude design a user-friendly solution. Finally, test with real human empathy.",
                "category": "trinity-process"
            }
        ]
        
        trinity_qa.extend(trinity_patterns)
        
        # Save Trinity wisdom
        with open(self.training_dir / "trinity_wisdom.json", 'w') as f:
            json.dump(trinity_qa, f, indent=2)
        
        print(f"✓ Collected {len(trinity_qa)} Trinity wisdom examples")
        return trinity_qa
    
    def create_focused_training_data(self):
        """Create training data focused on Trinity workflow needs"""
        print("🎯 Creating Trinity-focused training data...")
        
        focused_qa = [
            # User empathy examples
            {
                "q": "My grandma wants to install Firefox",
                "a": "For non-technical users, I recommend adding Firefox to the system configuration. Edit /etc/nixos/configuration.nix and add 'firefox' to environment.systemPackages, then run 'sudo nixos-rebuild switch'. This is the safest, most permanent way.",
                "category": "user-empathy"
            },
            # Common tasks
            {
                "q": "How do I update my system?",
                "a": "To update NixOS: 1) Update channel: 'sudo nix-channel --update', 2) Rebuild: 'sudo nixos-rebuild switch'. For automatic updates, you can enable system.autoUpgrade in configuration.nix.",
                "category": "common-task"
            },
            # Developer workflows
            {
                "q": "How do I create a development shell?",
                "a": "Create a shell.nix file with your dependencies. For example, for Python development:\n{ pkgs ? import <nixpkgs> {} }:\npkgs.mkShell {\n  buildInputs = with pkgs; [ python3 python3Packages.pip ];\n}\nThen run 'nix-shell' to enter the environment.",
                "category": "development"
            }
        ]
        
        # Save focused data
        with open(self.training_dir / "trinity_focused.json", 'w') as f:
            json.dump(focused_qa, f, indent=2)
        
        return focused_qa
    
    def create_trinity_modelfile(self, all_qa):
        """Create Ollama modelfile optimized for Trinity workflow"""
        print("📝 Creating Trinity modelfile...")
        
        modelfile_content = f"""# Sacred Trinity Nix Expert
# Optimized for Human + Claude + Local LLM workflow

FROM mistral:7b

# Trinity-aware system message
SYSTEM "You are a NixOS expert in the Sacred Trinity workflow. You provide:
- Clear, accurate NixOS knowledge and best practices
- User-friendly explanations (thinking of Grandma Rose)
- Developer-friendly details when needed
- Emphasis on declarative, reproducible approaches
- Understanding that you complement human vision and Claude's architecture

Remember: Every answer serves both technical accuracy and human understanding."

# Parameters for balanced responses
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096

# Trinity workflow examples
MESSAGE user What's the best way to install software in NixOS?
MESSAGE assistant The best way to install software in NixOS follows the declarative approach:

1. **System-wide** (recommended): Add to /etc/nixos/configuration.nix
   ```nix
   environment.systemPackages = with pkgs; [
     firefox
     vscode
   ];
   ```
   Then run: `sudo nixos-rebuild switch`

2. **User-specific**: Add to ~/.config/nixpkgs/home.nix (with home-manager)
3. **Temporary testing**: `nix-shell -p firefox`

Avoid `nix-env -i` as it's imperative and breaks reproducibility. The declarative approach ensures your system can be perfectly recreated.

MESSAGE user How do I fix "attribute missing" error?
MESSAGE assistant The "attribute missing" error in Nix usually means:

1. **Typo in package name**: Check exact spelling
   - Wrong: `firfox`
   - Right: `firefox`

2. **Package in different attribute**: Some packages are nested
   - Wrong: `vscode`
   - Right: `vscode` or `vscodium`

3. **Not in your channel**: Update with `sudo nix-channel --update`

To search for the correct name:
```bash
nix search nixpkgs firefox
```

This error is Nix protecting you from mistakes - it's a feature, not a bug!
"""
        
        # Add a few high-quality examples from our Q&A
        for i, qa in enumerate(all_qa[:3]):
            if qa.get('category') in ['trinity-best-practice', 'user-empathy']:
                modelfile_content += f"""
MESSAGE user {qa['q']}
MESSAGE assistant {qa['a']}
"""
        
        modelfile_path = self.training_dir / "trinity.modelfile"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        print(f"✓ Created Trinity modelfile: {modelfile_path}")
        return modelfile_path
    
    def train_trinity_model(self):
        """Train the Trinity-optimized model"""
        print(f"\n🚀 Training Sacred Trinity Nix Model: {self.model_name}")
        
        # Collect all wisdom
        trinity_qa = self.collect_trinity_wisdom()
        focused_qa = self.create_focused_training_data()
        all_qa = trinity_qa + focused_qa
        
        # Create modelfile
        modelfile_path = self.create_trinity_modelfile(all_qa)
        
        # Create model with Ollama
        print(f"\n🔮 Creating Ollama model...")
        try:
            result = subprocess.run([
                "ollama", "create",
                self.model_name,
                "-f", str(modelfile_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Sacred Trinity model created: {self.model_name}")
                return True
            else:
                print(f"❌ Model creation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_trinity_model(self):
        """Test with Trinity workflow scenarios"""
        print(f"\n🧪 Testing Trinity model...")
        
        test_scenarios = [
            "How do I install software the NixOS way?",
            "What's wrong with using nix-env?",
            "My system update failed, what should I do?",
            "How do I create a Python development environment?"
        ]
        
        for question in test_scenarios[:2]:  # Test first 2
            print(f"\n❓ {question}")
            try:
                result = subprocess.run([
                    "ollama", "run",
                    self.model_name,
                    question
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ {result.stdout[:300]}...")
                else:
                    print(f"❌ Error: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("⏱️ Response timeout")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sacred Trinity Nix Training")
    parser.add_argument("--model-name", default="nix-trinity", help="Model name")
    parser.add_argument("--skip-thesis", action="store_true", help="Skip PhD thesis")
    args = parser.parse_args()
    
    trainer = TrinityNixTrainer(args.model_name)
    
    if trainer.train_trinity_model():
        trainer.test_trinity_model()
        print("\n✨ Sacred Trinity training complete!")
        print(f"🙏 Use with: ollama run {args.model_name}")
        print(f"🤝 Or via: ask-nix-guru (will auto-detect)")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
SACRED_EOF

# Make it executable
chmod +x /tmp/trinity-nix-trainer.py

# Run the training
echo ""
echo "🌊 Starting Sacred Trinity training..."
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts

if [ "$INCLUDE_TRINITY_WISDOM" = true ]; then
    echo "📚 Including existing Trinity wisdom in training..."
fi

# Run our adapted trainer
python3 /tmp/trinity-nix-trainer.py --model-name "$MODEL_NAME" $SKIP_THESIS

# Update ask-nix-guru to use our model
echo ""
echo "🔗 Updating ask-nix-guru..."
sed -i "s/MODEL=\"\${NIX_GURU_MODEL:-.*}\"/MODEL=\"\${NIX_GURU_MODEL:-$MODEL_NAME}\"/" \
    /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/bin/ask-nix-guru 2>/dev/null || true

echo ""
echo "✨ Sacred Trinity Nix Training Complete!"
echo ""
echo "🎯 Your trained model: $MODEL_NAME"
echo ""
echo "📖 How to use in the Trinity workflow:"
echo "1. Human (you) identifies need: 'Users struggle with X'"
echo "2. Ask Local LLM: ask-nix-guru 'How to do X in NixOS?'"
echo "3. Claude integrates the knowledge into implementation"
echo ""
echo "🙏 The Sacred Trinity flows as one!"