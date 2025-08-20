#!/usr/bin/env python3
"""
from typing import List
Sacred Trinity RAG-Enhanced Trainer
Uses Retrieval Augmented Generation to give models actual NixOS knowledge
"""

import os
import sys
import json
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime
import time
from typing import List, Dict, Tuple
import re

class SacredTrinityRAG:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.knowledge_dir = self.base_dir / "docs" / "nix-knowledge"
        self.models_dir = self.base_dir / "models"
        self.db_path = self.base_dir / "trinity_rag.db"
        
        # Initialize knowledge database
        self.init_db()
        
        # Model configurations with RAG-enhanced prompts
        self.model_configs = {
            'expert': {
                'base': 'mistral:7b-instruct',
                'focus': 'technical accuracy and completeness',
                'temperature': 0.3,  # Lower for factual accuracy
                'retrieval_count': 3  # Number of examples to retrieve
            },
            'empathy': {
                'base': 'llama3.2:3b',
                'focus': 'user-friendly explanations for beginners',
                'temperature': 0.7,
                'retrieval_count': 2
            },
            'coder': {
                'base': 'qwen2.5:3b',
                'focus': 'generating Nix configurations and scripts',
                'temperature': 0.2,  # Very low for code accuracy
                'retrieval_count': 3
            },
            'quick': {
                'base': 'tinyllama:1.1b',
                'focus': 'quick answers to simple questions',
                'temperature': 0.5,
                'retrieval_count': 1
            }
        }
        
    def init_db(self):
        """Initialize SQLite database for Q&A storage and retrieval"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create knowledge table with embeddings
        c.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT,
                keywords TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Create index for fast searching
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_keywords ON knowledge(keywords)
        ''')
        
        conn.commit()
        conn.close()
        
    def load_qa_pairs(self) -> List[Dict]:
        """Load Q&A pairs from files and database"""
        qa_pairs = []
        
        # Load from files
        questions_dir = self.knowledge_dir / "questions"
        answers_dir = self.knowledge_dir / "answers"
        
        if questions_dir.exists() and answers_dir.exists():
            for q_file in questions_dir.glob("q_*.txt"):
                a_file = answers_dir / q_file.name.replace("q_", "a_")
                if a_file.exists():
                    question = q_file.read_text().strip()
                    answer = a_file.read_text().strip()
                    qa_pairs.append({
                        'question': question,
                        'answer': answer,
                        'source': 'file'
                    })
        
        # Load from database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT question, answer FROM knowledge')
        for row in c.fetchall():
            qa_pairs.append({
                'question': row[0],
                'answer': row[1],
                'source': 'db'
            })
        conn.close()
        
        return qa_pairs
        
    def import_qa_to_db(self, qa_pairs: List[Dict]):
        """Import Q&A pairs into database for retrieval"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for qa in qa_pairs:
            # Extract keywords from question
            keywords = self.extract_keywords(qa['question'])
            
            # Check if already exists
            c.execute('SELECT id FROM knowledge WHERE question = ?', (qa['question'],))
            if not c.fetchone():
                c.execute('''
                    INSERT INTO knowledge (question, answer, keywords)
                    VALUES (?, ?, ?)
                ''', (qa['question'], qa['answer'], keywords))
                
        conn.commit()
        conn.close()
        print(f"✅ Imported {len(qa_pairs)} Q&A pairs into knowledge database")
        
    def extract_keywords(self, text: str) -> str:
        """Extract keywords from text for search"""
        # Common NixOS terms
        important_terms = [
            'install', 'firefox', 'chrome', 'vscode', 'wifi', 'update',
            'generation', 'rollback', 'configuration.nix', 'home.nix',
            'flake', 'package', 'service', 'systemd', 'nixpkgs'
        ]
        
        text_lower = text.lower()
        keywords = []
        
        # Extract important terms
        for term in important_terms:
            if term in text_lower:
                keywords.append(term)
                
        # Extract any word that looks like a package name
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9-]+\b', text)
        for word in words:
            if len(word) > 3 and word.lower() not in ['what', 'how', 'when', 'where', 'why']:
                keywords.append(word.lower())
                
        return ' '.join(set(keywords))
        
    def retrieve_relevant_qa(self, query: str, count: int = 3) -> List[Dict]:
        """Retrieve relevant Q&A pairs for a query"""
        keywords = self.extract_keywords(query)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Search by keywords
        keyword_list = keywords.split()
        relevant_qa = []
        
        # First try exact keyword matches
        for keyword in keyword_list:
            c.execute('''
                SELECT question, answer, usage_count
                FROM knowledge
                WHERE keywords LIKE ?
                ORDER BY usage_count DESC
                LIMIT ?
            ''', (f'%{keyword}%', count))
            
            for row in c.fetchall():
                relevant_qa.append({
                    'question': row[0],
                    'answer': row[1],
                    'score': row[2]
                })
                
        # Deduplicate and get top results
        seen = set()
        unique_qa = []
        for qa in sorted(relevant_qa, key=lambda x: x['score'], reverse=True):
            if qa['question'] not in seen:
                seen.add(qa['question'])
                unique_qa.append(qa)
                if len(unique_qa) >= count:
                    break
                    
        # Update usage count
        for qa in unique_qa:
            c.execute('''
                UPDATE knowledge
                SET usage_count = usage_count + 1
                WHERE question = ?
            ''', (qa['question'],))
            
        conn.commit()
        conn.close()
        
        return unique_qa
        
    def create_rag_prompt(self, query: str, model_type: str, examples: List[Dict]) -> str:
        """Create a RAG-enhanced prompt with retrieved examples"""
        config = self.model_configs[model_type]
        
        # Base system prompt
        system_prompt = f"""You are a NixOS expert specializing in {config['focus']}.

IMPORTANT: Use the following examples to inform your responses about NixOS:

"""
        
        # Add retrieved examples
        for i, example in enumerate(examples, 1):
            system_prompt += f"""Example {i}:
Q: {example['question']}
A: {example['answer']}

"""
            
        # Add instructions based on model type
        if model_type == 'expert':
            system_prompt += """
Provide detailed, technically accurate answers. Include command examples and explain the reasoning.
"""
        elif model_type == 'empathy':
            system_prompt += """
Explain in simple, friendly terms. Avoid jargon. Be encouraging and patient.
"""
        elif model_type == 'coder':
            system_prompt += """
Focus on providing working Nix code examples. Include configuration snippets.
"""
        elif model_type == 'quick':
            system_prompt += """
Give brief, direct answers. One or two sentences maximum.
"""
            
        return system_prompt
        
    def query_with_rag(self, model_name: str, model_type: str, query: str) -> str:
        """Query model with RAG-enhanced context"""
        config = self.model_configs[model_type]
        
        # Retrieve relevant examples
        examples = self.retrieve_relevant_qa(query, config['retrieval_count'])
        
        if not examples:
            print(f"⚠️  No relevant examples found for: {query}")
            # Fall back to basic prompt
            return self.query_basic(model_name, query)
            
        # Create RAG-enhanced prompt by including examples in the query
        enhanced_query = "Based on these NixOS examples:\n\n"
        
        for i, example in enumerate(examples, 1):
            enhanced_query += f"Example {i}:\n"
            enhanced_query += f"Q: {example['question']}\n"
            enhanced_query += f"A: {example['answer']}\n\n"
            
        enhanced_query += f"Now answer this question: {query}"
        
        # Query with enhanced context
        cmd = ['ollama', 'run', model_name, enhanced_query]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Query timed out"
            
    def query_basic(self, model_name: str, query: str) -> str:
        """Basic query without RAG enhancement"""
        cmd = ['ollama', 'run', model_name, query]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Query timed out"
            
    def test_all_models(self):
        """Test all models with RAG enhancement"""
        test_queries = [
            "How do I install Firefox on NixOS?",
            "What's a NixOS generation?",
            "My WiFi isn't working",
            "How do I update my system?"
        ]
        
        print("\n🧪 Testing all models with RAG enhancement...\n")
        
        for model_type in self.model_configs:
            current_file = self.models_dir / f"current_{model_type}.txt"
            if current_file.exists():
                model_name = current_file.read_text().strip()
                print(f"\n📊 Testing {model_type} model ({model_name})...")
                
                for query in test_queries[:2]:  # Test first 2 queries
                    print(f"\n❓ {query}")
                    answer = self.query_with_rag(model_name, model_type, query)
                    print(f"💬 {answer[:200]}..." if len(answer) > 200 else f"💬 {answer}")
                    time.sleep(1)  # Be nice to Ollama
                    
    def import_nixos_qa_file(self, filepath: Path):
        """Import Q&A pairs from a file"""
        qa_pairs = []
        
        with open(filepath, 'r') as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|', 1)
                    if len(parts) == 2:
                        qa_pairs.append({
                            'question': parts[0].strip(),
                            'answer': parts[1].strip()
                        })
                        
        if qa_pairs:
            self.import_qa_to_db(qa_pairs)
            print(f"✅ Imported {len(qa_pairs)} Q&A pairs from {filepath}")
            

if __name__ == "__main__":
    rag = SacredTrinityRAG()
    
    # Import existing Q&A pairs
    print("📚 Loading knowledge base...")
    qa_pairs = rag.load_qa_pairs()
    if qa_pairs:
        rag.import_qa_to_db(qa_pairs)
        
    # Import core NixOS Q&A if it exists
    nixos_qa = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts/nixos-core-qa.txt")
    if nixos_qa.exists():
        rag.import_nixos_qa_file(nixos_qa)
        
    # Test all models
    rag.test_all_models()