#!/usr/bin/env python3
"""
from typing import List
Process scraped NixOS documentation into training formats
Creates Q&A pairs, instruction data, and other formats for model fine-tuning
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from collections import defaultdict
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrainingDataProcessor:
    """Process raw documentation into training formats"""
    
    def __init__(self, input_dir: str = "training-data/nixos-docs", 
                 output_dir: str = "training-data/processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # NixOS-specific patterns
        self.nixos_patterns = {
            'package_install': re.compile(r'(install|add|include)\s+(\w+)\s+(package|program|software)', re.I),
            'configuration': re.compile(r'(configuration\.nix|config\.nix|nixos configuration)', re.I),
            'flake': re.compile(r'(flake|flakes|nix flake)', re.I),
            'module': re.compile(r'(nixos module|module system|custom module)', re.I),
            'overlay': re.compile(r'(overlay|overlays|package override)', re.I),
            'command': re.compile(r'(nixos-rebuild|nix-env|nix-shell|nix develop|nix build)', re.I),
        }
    
    def extract_qa_pairs(self, doc: Dict) -> List[Dict]:
        """Extract Q&A pairs from documentation sections"""
        qa_pairs = []
        
        # Process each section
        for section in doc.get('sections', []):
            heading = section['heading']
            content = section['content']
            
            # Skip very short sections
            if len(content) < 50:
                continue
            
            # Generate questions based on heading patterns
            questions = self._generate_questions_from_heading(heading)
            
            for question in questions:
                qa_pairs.append({
                    'question': question,
                    'answer': self._clean_answer(content),
                    'source': doc['source'],
                    'context': doc['title'],
                    'section': heading
                })
        
        # Extract Q&A from FAQ-style content
        faq_pairs = self._extract_faq_style_qa(doc['content'])
        qa_pairs.extend(faq_pairs)
        
        return qa_pairs
    
    def _generate_questions_from_heading(self, heading: str) -> List[str]:
        """Generate natural questions from section headings"""
        questions = []
        heading_lower = heading.lower()
        
        # Direct question if heading ends with ?
        if heading.endswith('?'):
            questions.append(heading)
            return questions
        
        # Common patterns
        if heading_lower.startswith('how to'):
            questions.append(heading.replace('How to', 'How do I') + '?')
            questions.append(heading + '?')
        
        elif heading_lower.startswith('installing'):
            package = heading.replace('Installing', '').strip()
            questions.append(f"How do I install {package}?")
            questions.append(f"What's the process for installing {package}?")
        
        elif 'configuration' in heading_lower:
            questions.append(f"How do I configure {heading}?")
            questions.append(f"What is {heading}?")
        
        elif any(word in heading_lower for word in ['setup', 'setting up']):
            questions.append(f"How do I {heading.lower()}?")
        
        else:
            # Generic questions
            questions.append(f"What is {heading}?")
            questions.append(f"Can you explain {heading}?")
        
        return questions
    
    def _extract_faq_style_qa(self, content: str) -> List[Dict]:
        """Extract Q&A pairs from FAQ-style content"""
        qa_pairs = []
        
        # Pattern for Q: ... A: ...
        qa_pattern = re.compile(r'Q:\s*(.+?)\s*A:\s*(.+?)(?=Q:|$)', re.DOTALL | re.I)
        matches = qa_pattern.findall(content)
        
        for question, answer in matches:
            qa_pairs.append({
                'question': question.strip(),
                'answer': self._clean_answer(answer.strip()),
                'source': 'FAQ section',
                'context': 'FAQ',
                'section': 'FAQ'
            })
        
        return qa_pairs
    
    def _clean_answer(self, answer: str) -> str:
        """Clean and format answer text"""
        # Remove excessive whitespace
        answer = re.sub(r'\s+', ' ', answer)
        
        # Remove references like [1], [2], etc.
        answer = re.sub(r'\[\d+\]', '', answer)
        
        # Ensure answer is complete sentences
        if answer and not answer[-1] in '.!?':
            answer += '.'
        
        return answer.strip()
    
    def create_instruction_data(self, doc: Dict) -> List[Dict]:
        """Create instruction-following format data"""
        instructions = []
        
        # Process code examples
        for example in doc.get('code_examples', []):
            code = example['code']
            lang = example.get('language', 'nix')
            
            # Skip if code is too short or not Nix
            if len(code) < 20 or lang not in ['nix', 'bash', 'sh']:
                continue
            
            # Find context for this code
            context = self._find_code_context(doc, code)
            
            # Generate instructions based on code patterns
            if 'environment.systemPackages' in code:
                instructions.append({
                    'instruction': "Show me how to install packages system-wide in NixOS",
                    'input': '',
                    'output': code,
                    'explanation': context,
                    'source': doc['source']
                })
            
            elif 'systemd.services' in code:
                instructions.append({
                    'instruction': "How do I create a systemd service in NixOS?",
                    'input': '',
                    'output': code,
                    'explanation': context,
                    'source': doc['source']
                })
            
            elif 'nixos-rebuild' in code:
                instructions.append({
                    'instruction': "How do I apply configuration changes in NixOS?",
                    'input': '',
                    'output': code,
                    'explanation': context,
                    'source': doc['source']
                })
            
            elif 'mkDerivation' in code:
                instructions.append({
                    'instruction': "Show me how to package software for NixOS",
                    'input': '',
                    'output': code,
                    'explanation': context,
                    'source': doc['source']
                })
            
            elif 'flake.nix' in code or 'inputs' in code and 'outputs' in code:
                instructions.append({
                    'instruction': "How do I create a Nix flake?",
                    'input': '',
                    'output': code,
                    'explanation': context,
                    'source': doc['source']
                })
        
        return instructions
    
    def _find_code_context(self, doc: Dict, code_snippet: str) -> str:
        """Find surrounding context for a code example"""
        content = doc['content']
        
        # Try to find the code snippet in content
        code_start = content.find(code_snippet[:50])  # First 50 chars
        if code_start == -1:
            return "This code example demonstrates NixOS configuration."
        
        # Get text before the code (up to 200 chars)
        context_start = max(0, code_start - 200)
        context = content[context_start:code_start].strip()
        
        # Clean up context
        sentences = context.split('.')
        if sentences:
            # Get last complete sentence
            context = sentences[-1].strip() + '.'
        
        return context if context else "This code example demonstrates NixOS configuration."
    
    def create_concept_explanations(self, doc: Dict) -> List[Dict]:
        """Create explanations for NixOS concepts"""
        concepts = []
        
        # Key NixOS concepts to look for
        concept_patterns = {
            'derivation': "A derivation in Nix is a build recipe that describes how to build a package",
            'flake': "A flake is a self-contained Nix package with explicit dependencies",
            'overlay': "An overlay is a way to customize or override packages in nixpkgs",
            'channel': "A Nix channel is a versioned collection of packages",
            'profile': "A Nix profile is a collection of installed packages for a user",
            'generation': "A generation is a snapshot of your system configuration",
            'garbage collection': "Garbage collection removes unused packages and old generations",
            'store': "The Nix store (/nix/store) contains all packages and their dependencies",
        }
        
        content_lower = doc['content'].lower()
        
        for concept, base_explanation in concept_patterns.items():
            if concept in content_lower:
                # Extract more detailed explanation from doc
                detailed = self._extract_concept_explanation(doc, concept)
                
                concepts.append({
                    'concept': concept,
                    'brief': base_explanation,
                    'detailed': detailed,
                    'source': doc['source'],
                    'examples': self._find_concept_examples(doc, concept)
                })
        
        return concepts
    
    def _extract_concept_explanation(self, doc: Dict, concept: str) -> str:
        """Extract detailed explanation of a concept from documentation"""
        content = doc['content']
        
        # Find sentences containing the concept
        sentences = content.split('.')
        relevant_sentences = []
        
        for i, sentence in enumerate(sentences):
            if concept.lower() in sentence.lower():
                # Include this sentence and surrounding context
                start = max(0, i - 1)
                end = min(len(sentences), i + 2)
                relevant_sentences.extend(sentences[start:end])
        
        # Join and clean
        explanation = '. '.join(set(relevant_sentences))
        return self._clean_answer(explanation)
    
    def _find_concept_examples(self, doc: Dict, concept: str) -> List[str]:
        """Find code examples related to a concept"""
        examples = []
        
        for code_example in doc.get('code_examples', []):
            code = code_example['code']
            if concept.lower() in code.lower():
                examples.append(code)
        
        return examples[:3]  # Limit to 3 examples
    
    def create_troubleshooting_pairs(self, doc: Dict) -> List[Dict]:
        """Extract troubleshooting Q&A pairs"""
        troubleshooting = []
        
        # Common error patterns in NixOS
        error_patterns = [
            (r'error:.*not found', 'package not found'),
            (r'error:.*infinite recursion', 'infinite recursion'),
            (r'error:.*collision', 'package collision'),
            (r'error:.*permission denied', 'permission issue'),
            (r'error:.*no such file', 'missing file'),
            (r'error:.*syntax error', 'syntax error'),
        ]
        
        content = doc['content']
        
        for pattern, error_type in error_patterns:
            matches = re.finditer(pattern, content, re.I)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                
                troubleshooting.append({
                    'error': match.group(),
                    'error_type': error_type,
                    'solution': self._extract_solution(context),
                    'source': doc['source']
                })
        
        return troubleshooting
    
    def _extract_solution(self, context: str) -> str:
        """Extract solution from error context"""
        # Look for solution indicators
        solution_patterns = [
            r'solution:(.+?)(?:\.|$)',
            r'fix:(.+?)(?:\.|$)',
            r'to resolve:(.+?)(?:\.|$)',
            r'you can:(.+?)(?:\.|$)',
            r'try:(.+?)(?:\.|$)',
        ]
        
        for pattern in solution_patterns:
            match = re.search(pattern, context, re.I | re.DOTALL)
            if match:
                return self._clean_answer(match.group(1))
        
        # If no explicit solution, return general advice
        return "Check your configuration for errors and ensure all referenced packages exist."
    
    def process_all_documents(self):
        """Process all scraped documents"""
        all_qa = []
        all_instructions = []
        all_concepts = []
        all_troubleshooting = []
        
        # Track statistics
        stats = defaultdict(int)
        
        # Process each document
        doc_files = list(self.input_dir.glob('*.json'))
        logger.info(f"Processing {len(doc_files)} documents...")
        
        for doc_path in doc_files:
            logger.info(f"Processing {doc_path.name}...")
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                
                # Extract different types of training data
                qa_pairs = self.extract_qa_pairs(doc)
                instructions = self.create_instruction_data(doc)
                concepts = self.create_concept_explanations(doc)
                troubleshooting = self.create_troubleshooting_pairs(doc)
                
                # Update collections
                all_qa.extend(qa_pairs)
                all_instructions.extend(instructions)
                all_concepts.extend(concepts)
                all_troubleshooting.extend(troubleshooting)
                
                # Update stats
                stats['documents'] += 1
                stats['qa_pairs'] += len(qa_pairs)
                stats['instructions'] += len(instructions)
                stats['concepts'] += len(concepts)
                stats['troubleshooting'] += len(troubleshooting)
                
            except Exception as e:
                logger.error(f"Error processing {doc_path}: {e}")
                continue
        
        # Remove duplicates
        all_qa = self._deduplicate(all_qa, 'question')
        all_instructions = self._deduplicate(all_instructions, 'instruction')
        
        # Save processed data
        self._save_json(all_qa, 'qa_pairs.json')
        self._save_json(all_instructions, 'instructions.json')
        self._save_json(all_concepts, 'concepts.json')
        self._save_json(all_troubleshooting, 'troubleshooting.json')
        
        # Save statistics
        self._save_json(dict(stats), 'statistics.json')
        
        # Print summary
        logger.info("\nProcessing complete!")
        logger.info(f"Documents processed: {stats['documents']}")
        logger.info(f"Q&A pairs created: {len(all_qa)}")
        logger.info(f"Instructions created: {len(all_instructions)}")
        logger.info(f"Concepts extracted: {len(all_concepts)}")
        logger.info(f"Troubleshooting items: {len(all_troubleshooting)}")
    
    def _deduplicate(self, items: List[Dict], key: str) -> List[Dict]:
        """Remove duplicate items based on a key"""
        seen = set()
        unique_items = []
        
        for item in items:
            # Create hash of the key field
            item_hash = hashlib.md5(item[key].encode()).hexdigest()
            if item_hash not in seen:
                seen.add(item_hash)
                unique_items.append(item)
        
        return unique_items
    
    def _save_json(self, data: List[Dict], filename: str):
        """Save data to JSON file"""
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(data)} items to {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Process NixOS docs for training')
    parser.add_argument('--input', default='training-data/nixos-docs',
                       help='Input directory with scraped docs')
    parser.add_argument('--output', default='training-data/processed',
                       help='Output directory for processed data')
    
    args = parser.parse_args()
    
    processor = TrainingDataProcessor(args.input, args.output)
    processor.process_all_documents()


if __name__ == '__main__':
    main()