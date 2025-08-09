#!/usr/bin/env python3
"""
from typing import Dict, List
Process Nix theoretical documents (thesis, papers) into training data
Extracts key concepts, principles, and best practices
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2
from bs4 import BeautifulSoup
import nltk
from collections import defaultdict

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class NixTheoryProcessor:
    def __init__(self, docs_dir: str = "training-data/nix-docs-comprehensive"):
        self.docs_dir = Path(docs_dir)
        self.output_dir = Path("training-data/nix-theory-processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Key concepts to extract
        self.key_concepts = {
            "core_principles": [
                "purely functional", "reproducibility", "declarative",
                "immutability", "isolation", "atomic", "rollback"
            ],
            "technical_terms": [
                "derivation", "store path", "closure", "profile",
                "generation", "channel", "flake", "overlay",
                "fixed-output", "sandbox", "substitute"
            ],
            "best_practices": [
                "pin", "reproducible", "declarative", "avoid imperative",
                "use flakes", "overlay pattern", "module system"
            ]
        }
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF files like the thesis"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        return text
    
    def extract_key_passages(self, text: str) -> List[Dict[str, str]]:
        """Extract important passages that explain key concepts"""
        passages = []
        sentences = nltk.sent_tokenize(text)
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            
            # Check if sentence contains key concepts
            relevance_score = 0
            matched_concepts = []
            
            for category, terms in self.key_concepts.items():
                for term in terms:
                    if term in sentence_lower:
                        relevance_score += 1
                        matched_concepts.append(term)
            
            if relevance_score > 0:
                # Get context (previous and next sentence)
                context = ""
                if i > 0:
                    context = sentences[i-1] + " "
                context += sentence
                if i < len(sentences) - 1:
                    context += " " + sentences[i+1]
                
                passages.append({
                    "text": context.strip(),
                    "concepts": matched_concepts,
                    "relevance": relevance_score
                })
        
        # Sort by relevance and return top passages
        passages.sort(key=lambda x: x["relevance"], reverse=True)
        return passages[:500]  # Top 500 most relevant passages
    
    def process_thesis(self):
        """Process Eelco Dolstra's PhD thesis"""
        print("📚 Processing PhD Thesis...")
        
        thesis_path = self.docs_dir / "thesis" / "eelco-dolstra-phd-thesis.pdf"
        if not thesis_path.exists():
            print("⚠️  Thesis not found. Run download script first.")
            return
        
        # Extract text
        text = self.extract_pdf_text(thesis_path)
        
        # Extract key passages
        passages = self.extract_key_passages(text)
        
        # Create Q&A pairs from thesis content
        qa_pairs = []
        
        # Core concepts from thesis
        thesis_concepts = [
            {
                "q": "What is the purely functional software deployment model?",
                "a": "The purely functional deployment model treats packages as values produced by functions that depend only on their inputs, ensuring reproducibility and allowing multiple versions to coexist without conflicts."
            },
            {
                "q": "How does Nix ensure reproducibility?",
                "a": "Nix ensures reproducibility by using cryptographic hashes of all inputs to derive unique store paths, making builds deterministic and independent of system state."
            },
            {
                "q": "What is a derivation in Nix?",
                "a": "A derivation is a recipe that describes how to build a package, including all dependencies, build commands, and environment variables. It's the fundamental building block of Nix."
            },
            {
                "q": "Why can multiple versions coexist in Nix?",
                "a": "Multiple versions can coexist because each package is installed in an isolated directory named by a cryptographic hash of all its inputs, preventing conflicts."
            },
            {
                "q": "What is the Nix store?",
                "a": "The Nix store (typically /nix/store) is where all packages are stored in isolation, with paths like /nix/store/hash-name-version containing immutable package contents."
            }
        ]
        
        # Add concept explanations from extracted passages
        for passage in passages[:50]:  # Top 50 passages
            if passage["relevance"] >= 2:  # High relevance
                # Generate Q&A from passage
                concepts = ", ".join(passage["concepts"])
                qa_pairs.append({
                    "q": f"Explain the relationship between {concepts} in Nix",
                    "a": passage["text"],
                    "source": "PhD Thesis",
                    "concepts": passage["concepts"]
                })
        
        qa_pairs.extend(thesis_concepts)
        
        # Save processed thesis data
        with open(self.output_dir / "thesis_qa_pairs.json", 'w') as f:
            json.dump(qa_pairs, f, indent=2)
        
        print(f"✓ Extracted {len(qa_pairs)} Q&A pairs from thesis")
    
    def process_best_practices(self):
        """Process best practices into training data"""
        print("🌟 Processing Best Practices...")
        
        practices_file = self.docs_dir / "best-practices" / "collected_best_practices.json"
        if not practices_file.exists():
            print("⚠️  Best practices file not found")
            return
        
        with open(practices_file) as f:
            practices = json.load(f)
        
        qa_pairs = []
        instructions = []
        
        # Anti-patterns
        for anti in practices.get("anti_patterns", []):
            qa_pairs.append({
                "q": "Is this a good practice in Nix: " + anti.replace("Avoid ", "").replace("Don't ", ""),
                "a": f"No, this is an anti-pattern. {anti} Instead, use declarative configuration and Nix's proper abstractions.",
                "category": "anti-pattern"
            })
            
            instructions.append({
                "instruction": "What should I avoid doing in Nix?",
                "input": anti.replace("Avoid ", "").replace("Don't ", ""),
                "output": f"You should avoid this because {anti.lower()}. This goes against Nix principles of reproducibility and declarative configuration."
            })
        
        # Good patterns
        for pattern in practices.get("patterns", []):
            qa_pairs.append({
                "q": f"How should I {pattern.lower().replace('use ', '')}?",
                "a": pattern + " This follows Nix best practices for maintainable and reproducible configurations.",
                "category": "best-practice"
            })
            
            instructions.append({
                "instruction": "What's the best practice for this in Nix?",
                "input": pattern.split()[1],  # Extract key term
                "output": pattern
            })
        
        # Security practices
        for security in practices.get("security", []):
            qa_pairs.append({
                "q": f"What security consideration applies to: {security.split()[1]}",
                "a": security + " This is important for maintaining a secure Nix environment.",
                "category": "security"
            })
        
        # Save processed best practices
        with open(self.output_dir / "best_practices_qa.json", 'w') as f:
            json.dump(qa_pairs, f, indent=2)
        
        with open(self.output_dir / "best_practices_instructions.json", 'w') as f:
            json.dump(instructions, f, indent=2)
        
        print(f"✓ Created {len(qa_pairs)} Q&A pairs and {len(instructions)} instructions")
    
    def process_cookbook(self):
        """Process cookbook examples into training data"""
        print("🍳 Processing Cookbook Examples...")
        
        cookbook_file = self.docs_dir / "cookbook" / "nix_cookbook.json"
        if not cookbook_file.exists():
            print("⚠️  Cookbook file not found")
            return
        
        with open(cookbook_file) as f:
            cookbook = json.load(f)
        
        qa_pairs = []
        
        # Common tasks
        for task_name, task_info in cookbook.get("common_tasks", {}).items():
            readable_task = task_name.replace("_", " ")
            
            qa_pairs.append({
                "q": f"How do I {readable_task} in NixOS?",
                "a": f"To {readable_task}, you can use: {task_info.get('command', task_info.get('declarative', task_info.get('flake')))}. {task_info.get('explanation', '')}",
                "category": "how-to"
            })
            
            # Compare different approaches
            if "imperative" in task_info and "declarative" in task_info:
                qa_pairs.append({
                    "q": f"What's the difference between imperative and declarative approach for {readable_task}?",
                    "a": f"Imperative: {task_info['imperative']} (temporary, not reproducible). Declarative: {task_info['declarative']} (permanent, reproducible). Always prefer declarative.",
                    "category": "comparison"
                })
        
        # Development shells
        for lang, shell_code in cookbook.get("development_shells", {}).items():
            qa_pairs.append({
                "q": f"How do I create a {lang} development environment in Nix?",
                "a": f"Create a shell.nix file with:\n```nix\n{shell_code}\n```\nThen run 'nix-shell' to enter the environment.",
                "category": "development"
            })
        
        # Save cookbook Q&A
        with open(self.output_dir / "cookbook_qa.json", 'w') as f:
            json.dump(qa_pairs, f, indent=2)
        
        print(f"✓ Created {len(qa_pairs)} cookbook Q&A pairs")
    
    def create_conceptual_training(self):
        """Create training data for understanding Nix concepts"""
        print("🧠 Creating Conceptual Training Data...")
        
        concepts = {
            "derivation": {
                "definition": "A derivation is a description of how to build a package, including all inputs, dependencies, and build instructions.",
                "analogy": "Think of a derivation like a recipe that precisely describes all ingredients and steps to make a dish, ensuring anyone can reproduce it exactly.",
                "importance": "Derivations are the core abstraction that enables reproducibility in Nix."
            },
            "closure": {
                "definition": "A closure is the complete set of dependencies required by a package, transitively including all dependencies of dependencies.",
                "analogy": "Like packing for a trip and including everything you'll need, including batteries for devices that need them.",
                "importance": "Closures ensure packages are self-contained and portable."
            },
            "profile": {
                "definition": "A profile is a user-specific set of installed packages, implemented as generations that can be switched between.",
                "analogy": "Like having different outfits saved in your closet that you can switch between instantly.",
                "importance": "Profiles allow users to manage their packages without affecting the system or other users."
            },
            "generation": {
                "definition": "A generation is a snapshot of your system or profile configuration at a point in time.",
                "analogy": "Like save points in a video game - you can always go back to a previous save if something goes wrong.",
                "importance": "Generations enable safe experimentation and instant rollbacks."
            },
            "flake": {
                "definition": "A flake is a self-contained Nix project with explicit dependencies and a standardized structure.",
                "analogy": "Like a shipping container that includes everything needed and can be moved anywhere intact.",
                "importance": "Flakes solve reproducibility issues with channels and provide better composition."
            }
        }
        
        concept_qa = []
        
        for concept, info in concepts.items():
            # Definition question
            concept_qa.append({
                "q": f"What is a {concept} in Nix?",
                "a": info["definition"],
                "category": "concept"
            })
            
            # Analogy question
            concept_qa.append({
                "q": f"Can you explain {concept} with a simple analogy?",
                "a": info["analogy"],
                "category": "analogy"
            })
            
            # Importance question
            concept_qa.append({
                "q": f"Why is {concept} important in Nix?",
                "a": info["importance"],
                "category": "importance"
            })
        
        # Relationships between concepts
        relationships = [
            {
                "q": "How do derivations and the Nix store relate?",
                "a": "Derivations describe how to build packages, and their outputs are stored in the Nix store at paths determined by hashing all inputs to the derivation."
            },
            {
                "q": "What's the relationship between profiles and generations?",
                "a": "A profile is a sequence of generations. Each time you modify a profile (install/remove packages), a new generation is created, allowing rollback to any previous state."
            },
            {
                "q": "How do flakes improve upon channels?",
                "a": "Flakes pin exact versions of dependencies with lock files, while channels are mutable references that can change. Flakes ensure true reproducibility across time and machines."
            }
        ]
        
        concept_qa.extend(relationships)
        
        # Save conceptual training data
        with open(self.output_dir / "conceptual_qa.json", 'w') as f:
            json.dump(concept_qa, f, indent=2)
        
        print(f"✓ Created {len(concept_qa)} conceptual Q&A pairs")
    
    def create_philosophy_training(self):
        """Create training data about Nix philosophy and principles"""
        print("💭 Creating Philosophy Training Data...")
        
        philosophy_qa = [
            {
                "q": "What is the core philosophy of Nix?",
                "a": "Nix's core philosophy is treating package management as a purely functional programming problem, where packages are immutable values produced by deterministic functions. This ensures reproducibility, reliability, and composability.",
                "category": "philosophy"
            },
            {
                "q": "Why does Nix emphasize reproducibility so strongly?",
                "a": "Reproducibility eliminates 'works on my machine' problems, enables reliable deployments, allows time-travel debugging, and makes systems predictable. It's the foundation for trustworthy software deployment.",
                "category": "philosophy"
            },
            {
                "q": "What does 'purely functional' mean in the context of Nix?",
                "a": "In Nix, 'purely functional' means build outputs depend only on declared inputs - no hidden dependencies on system state, time, or network. Like pure functions in programming, same inputs always produce same outputs.",
                "category": "philosophy"
            },
            {
                "q": "How does Nix's approach differ from traditional package managers?",
                "a": "Traditional package managers mutate global state and can break existing packages. Nix installs each package in isolation, allows multiple versions, enables atomic upgrades/rollbacks, and guarantees no interference between packages.",
                "category": "comparison"
            },
            {
                "q": "What are the trade-offs of Nix's approach?",
                "a": "Benefits: perfect reproducibility, rollbacks, multiple versions, no dependency hell. Trade-offs: higher disk usage, steeper learning curve, different mental model, and some software needs adaptation for purity.",
                "category": "trade-offs"
            }
        ]
        
        # Save philosophy training data
        with open(self.output_dir / "philosophy_qa.json", 'w') as f:
            json.dump(philosophy_qa, f, indent=2)
        
        print(f"✓ Created {len(philosophy_qa)} philosophy Q&A pairs")
    
    def create_master_training_set(self):
        """Combine all processed data into master training sets"""
        print("\n🎯 Creating Master Training Set...")
        
        all_qa = []
        all_instructions = []
        
        # Load all generated Q&A files
        qa_files = [
            "thesis_qa_pairs.json",
            "best_practices_qa.json",
            "cookbook_qa.json",
            "conceptual_qa.json",
            "philosophy_qa.json"
        ]
        
        for qa_file in qa_files:
            file_path = self.output_dir / qa_file
            if file_path.exists():
                with open(file_path) as f:
                    all_qa.extend(json.load(f))
        
        # Load instruction files
        inst_files = ["best_practices_instructions.json"]
        
        for inst_file in inst_files:
            file_path = self.output_dir / inst_file
            if file_path.exists():
                with open(file_path) as f:
                    all_instructions.extend(json.load(f))
        
        # Create category statistics
        categories = defaultdict(int)
        for qa in all_qa:
            categories[qa.get("category", "general")] += 1
        
        # Save master files
        with open(self.output_dir / "nix_master_qa.json", 'w') as f:
            json.dump(all_qa, f, indent=2)
        
        with open(self.output_dir / "nix_master_instructions.json", 'w') as f:
            json.dump(all_instructions, f, indent=2)
        
        # Save statistics
        stats = {
            "total_qa_pairs": len(all_qa),
            "total_instructions": len(all_instructions),
            "categories": dict(categories),
            "sources": ["PhD Thesis", "Best Practices", "Cookbook", "Concepts", "Philosophy"]
        }
        
        with open(self.output_dir / "processing_stats.json", 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n📊 Master Training Set Statistics:")
        print(f"  Total Q&A Pairs: {len(all_qa)}")
        print(f"  Total Instructions: {len(all_instructions)}")
        print(f"  Categories: {dict(categories)}")
    
    def process_all(self):
        """Process all documentation types"""
        self.process_thesis()
        self.process_best_practices()
        self.process_cookbook()
        self.create_conceptual_training()
        self.create_philosophy_training()
        self.create_master_training_set()
        
        print("\n✅ Theory processing complete!")
        print(f"📁 Processed data saved to: {self.output_dir}")


def main():
    processor = NixTheoryProcessor()
    processor.process_all()


if __name__ == "__main__":
    main()