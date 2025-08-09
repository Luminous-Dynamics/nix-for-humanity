#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Non-LLM AI Pipeline for Nix for Humanity
Demonstrates the power of specialized AI models without needing LLMs
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

# These would be imported in production:
# from sklearn.linear_model import LogisticRegression
# from sentence_transformers import SentenceTransformer
# import spacy
# import nltk
# import pandas as pd

class NonLLMPipeline:
    """
    Efficient AI pipeline using specialized models instead of LLMs
    """
    
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.db_path = self.base_dir / "nixos_knowledge.db"
        
        # Initialize models (mock for now - would load real models in production)
        self.sentence_model = None  # SentenceTransformer('all-MiniLM-L6-v2')
        self.spacy_nlp = None      # spacy.load('en_core_web_sm')
        self.prediction_model = None # LogisticRegression()
        
        # Pre-calculated embeddings for common intents
        self.intent_embeddings = {
            'install_package': "install a package software application program",
            'update_system': "update upgrade nixos system configuration",
            'search_package': "search find look for package software",
            'fix_error': "fix error problem issue broken failed",
            'enable_service': "enable start service daemon systemd",
            'rollback': "rollback undo revert previous generation"
        }
        
    def normalize_text(self, text: str) -> List[str]:
        """
        NLTK-style text normalization
        Clean and standardize user input
        """
        # Convert to lowercase
        text = text.lower()
        
        # Fix common typos
        typo_fixes = {
            'plz': 'please',
            'pls': 'please',
            'u': 'you',
            'ur': 'your',
            'thx': 'thanks',
            'fierfox': 'firefox',
            'fireofx': 'firefox',
            'pythn': 'python',
            'nodejs': 'node.js'
        }
        
        for typo, fix in typo_fixes.items():
            text = re.sub(r'\b' + typo + r'\b', fix, text)
        
        # Tokenize (simple version - real NLTK would be more sophisticated)
        tokens = text.split()
        
        # Remove stop words (simplified)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        tokens = [t for t in tokens if t not in stop_words]
        
        return tokens
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        spaCy-style Named Entity Recognition
        Extract package names, file paths, error codes
        """
        entities = {
            'PACKAGE': [],
            'FILE': [],
            'ERROR_CODE': [],
            'SERVICE': []
        }
        
        # Simple pattern-based NER (real spaCy would use trained models)
        
        # Package names (common software)
        package_patterns = [
            'firefox', 'chrome', 'chromium', 'vscode', 'vim', 'neovim',
            'python', 'nodejs', 'rust', 'go', 'java', 'docker', 'git'
        ]
        for pkg in package_patterns:
            if pkg in text.lower():
                entities['PACKAGE'].append(pkg)
        
        # File paths
        file_pattern = r'/[\w/.-]+\.nix'
        for match in re.finditer(file_pattern, text):
            entities['FILE'].append(match.group())
        
        # Error codes
        error_pattern = r'error:\s*([^\n]+)'
        for match in re.finditer(error_pattern, text, re.IGNORECASE):
            entities['ERROR_CODE'].append(match.group(1))
        
        # Services
        service_pattern = r'([\w-]+)\.service'
        for match in re.finditer(service_pattern, text):
            entities['SERVICE'].append(match.group(1))
        
        return entities
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        SentenceTransformers-style semantic similarity
        """
        # Simplified cosine similarity based on word overlap
        # Real implementation would use sentence embeddings
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
            
        return len(intersection) / len(union)
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Intent classification using semantic similarity
        """
        normalized = ' '.join(self.normalize_text(text))
        
        best_intent = 'unknown'
        best_score = 0.0
        
        for intent, intent_text in self.intent_embeddings.items():
            similarity = self.calculate_semantic_similarity(normalized, intent_text)
            if similarity > best_score:
                best_score = similarity
                best_intent = intent
        
        return best_intent, best_score
    
    def predict_next_command(self, command_history: List[str]) -> Tuple[str, float]:
        """
        Scikit-learn style command prediction
        """
        # Common command sequences
        command_sequences = {
            'install nodejs': ['install yarn', 'install npm', 'install typescript'],
            'install python': ['install pip', 'install poetry', 'install virtualenv'],
            'install rust': ['install cargo', 'install rustup'],
            'update system': ['rollback', 'reboot', 'check status'],
            'enable ssh': ['generate ssh key', 'configure firewall']
        }
        
        if not command_history:
            return 'help', 0.0
            
        last_command = command_history[-1].lower()
        
        # Find matching pattern
        for pattern, predictions in command_sequences.items():
            if pattern in last_command:
                # Return most likely next command
                return predictions[0], 0.85  # 85% confidence
        
        return 'search packages', 0.5  # Default suggestion
    
    def analyze_error(self, error_log: str) -> Dict[str, any]:
        """
        Intelligent error analysis using NER and pattern matching
        """
        entities = self.extract_entities(error_log)
        
        analysis = {
            'type': 'unknown',
            'packages': entities['PACKAGE'],
            'files': entities['FILE'],
            'suggestion': 'Check the error message for more details'
        }
        
        # Common error patterns
        if 'attribute' in error_log and 'missing' in error_log:
            analysis['type'] = 'missing_attribute'
            analysis['suggestion'] = f"Package or attribute not found. Try searching: nix search nixpkgs {entities['PACKAGE'][0] if entities['PACKAGE'] else 'package'}"
        
        elif 'collision' in error_log:
            analysis['type'] = 'package_collision'
            analysis['suggestion'] = "Multiple packages provide the same file. Use priority or remove one package."
        
        elif 'read-only file system' in error_log:
            analysis['type'] = 'readonly_fs'
            analysis['suggestion'] = "Cannot modify system files directly. Edit configuration.nix instead."
        
        elif 'out of memory' in error_log:
            analysis['type'] = 'oom'
            analysis['suggestion'] = "Build ran out of memory. Try: nix-build --cores 1 --max-jobs 1"
        
        return analysis
    
    def process_query(self, query: str, command_history: Optional[List[str]] = None) -> Dict:
        """
        Main processing pipeline combining all AI models
        """
        # Step 1: Normalize text (NLTK)
        normalized_tokens = self.normalize_text(query)
        
        # Step 2: Extract entities (spaCy)
        entities = self.extract_entities(query)
        
        # Step 3: Classify intent (SentenceTransformers)
        intent, confidence = self.classify_intent(query)
        
        # Step 4: Predict next action (Scikit-learn)
        next_command = None
        if command_history:
            next_cmd, next_conf = self.predict_next_command(command_history)
            if next_conf > 0.7:
                next_command = {
                    'command': next_cmd,
                    'confidence': next_conf
                }
        
        # Step 5: Error analysis if needed
        error_analysis = None
        if 'error' in query.lower() or 'failed' in query.lower():
            error_analysis = self.analyze_error(query)
        
        return {
            'original_query': query,
            'normalized': normalized_tokens,
            'intent': {
                'type': intent,
                'confidence': confidence
            },
            'entities': entities,
            'next_command': next_command,
            'error_analysis': error_analysis
        }


def demonstrate_pipeline():
    """
    Demonstrate the non-LLM AI pipeline
    """
    pipeline = NonLLMPipeline()
    
    # Test cases
    test_queries = [
        {
            'query': "Plz can u get me the fierfox browser",
            'history': []
        },
        {
            'query': "error: attribute 'firefox' missing at /etc/nixos/configuration.nix:42:15",
            'history': ['search firefox']
        },
        {
            'query': "I just installed nodejs, what should I do next?",
            'history': ['install nodejs']
        },
        {
            'query': "make my system safe and secure",
            'history': []
        }
    ]
    
    print("🧠 Non-LLM AI Pipeline Demonstration\n")
    print("=" * 60)
    
    for test in test_queries:
        print(f"\n📝 Query: {test['query']}")
        print("-" * 60)
        
        result = pipeline.process_query(test['query'], test['history'])
        
        print(f"🔤 Normalized: {' '.join(result['normalized'])}")
        print(f"🎯 Intent: {result['intent']['type']} (confidence: {result['intent']['confidence']:.2%})")
        
        if result['entities']['PACKAGE']:
            print(f"📦 Packages: {', '.join(result['entities']['PACKAGE'])}")
        
        if result['next_command']:
            print(f"🔮 Predicted next: {result['next_command']['command']} ({result['next_command']['confidence']:.0%} confidence)")
        
        if result['error_analysis']:
            print(f"🔍 Error type: {result['error_analysis']['type']}")
            print(f"💡 Suggestion: {result['error_analysis']['suggestion']}")
        
        print("=" * 60)


if __name__ == "__main__":
    demonstrate_pipeline()