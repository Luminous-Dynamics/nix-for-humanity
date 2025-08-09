#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Format processed NixOS documentation for different training approaches
Supports multiple formats: Alpaca, ShareGPT, completion, and Ollama modelfile
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrainingFormatter:
    """Format training data for different fine-tuning approaches"""
    
    def __init__(self, input_dir: str = "training-data/processed",
                 output_dir: str = "training-data/formatted"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # NixOS-specific system prompts
        self.system_prompts = {
            'expert': """You are a NixOS expert assistant. You provide accurate, idiomatic NixOS advice following current best practices. You prefer declarative configuration, flakes, and reproducible approaches. Always suggest the most appropriate method for the user's needs.""",
            
            'beginner_friendly': """You are a friendly NixOS helper. You explain NixOS concepts in simple terms, provide clear examples, and guide users step-by-step. You emphasize safety and best practices while being encouraging and patient.""",
            
            'troubleshooter': """You are a NixOS troubleshooting specialist. You help users diagnose and fix NixOS issues, explain error messages clearly, and provide practical solutions. You consider common pitfalls and edge cases."""
        }
    
    def format_alpaca(self, data: Dict, include_context: bool = True) -> Dict:
        """Format for Alpaca-style fine-tuning"""
        formatted = {
            'instruction': data.get('question', data.get('instruction', '')),
            'input': '',
            'output': data.get('answer', data.get('output', ''))
        }
        
        # Add context as part of instruction if available
        if include_context and 'context' in data:
            formatted['instruction'] = f"Context: {data['context']}\n\n{formatted['instruction']}"
        
        return formatted
    
    def format_sharegpt(self, data: Dict, system_prompt: Optional[str] = None) -> Dict:
        """Format for ShareGPT/conversation style"""
        conversations = []
        
        # Add system prompt if provided
        if system_prompt:
            conversations.append({
                'from': 'system',
                'value': system_prompt
            })
        
        # Add user question
        conversations.append({
            'from': 'human',
            'value': data.get('question', data.get('instruction', ''))
        })
        
        # Add assistant response
        answer = data.get('answer', data.get('output', ''))
        
        # Include code explanation if available
        if 'explanation' in data and data['explanation']:
            answer = f"{data['explanation']}\n\n{answer}"
        
        conversations.append({
            'from': 'assistant',
            'value': answer
        })
        
        return {'conversations': conversations}
    
    def format_completion(self, data: Dict, use_special_tokens: bool = True) -> str:
        """Format for completion-style training"""
        question = data.get('question', data.get('instruction', ''))
        answer = data.get('answer', data.get('output', ''))
        
        if use_special_tokens:
            # Format with special tokens for better training
            return f"<|user|>\n{question}\n<|assistant|>\n{answer}\n<|end|>"
        else:
            # Simple Q&A format
            return f"Q: {question}\n\nA: {answer}"
    
    def format_ollama_examples(self, data_list: List[Dict], model_base: str = "mistral") -> str:
        """Create Ollama modelfile with examples"""
        modelfile = f"""# NixOS Expert Model based on {model_base}
FROM {model_base}

# Set optimal parameters for technical Q&A
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER stop "<|user|>"
PARAMETER stop "<|end|>"

# System message for NixOS expertise
SYSTEM {json.dumps(self.system_prompts['expert'])}

# Training examples
"""
        
        # Add examples as messages
        for i, data in enumerate(data_list[:50]):  # Limit to 50 examples in modelfile
            question = data.get('question', data.get('instruction', ''))
            answer = data.get('answer', data.get('output', ''))
            
            modelfile += f"""
# Example {i+1}
MESSAGE user {json.dumps(question)}
MESSAGE assistant {json.dumps(answer)}
"""
        
        return modelfile
    
    def format_jsonl(self, data: Dict, format_type: str = 'alpaca') -> str:
        """Format as JSONL (one JSON object per line)"""
        if format_type == 'alpaca':
            formatted = self.format_alpaca(data)
        elif format_type == 'sharegpt':
            formatted = self.format_sharegpt(data, self.system_prompts['expert'])
        else:
            raise ValueError(f"Unknown format type: {format_type}")
        
        return json.dumps(formatted, ensure_ascii=False)
    
    def create_training_splits(self, data: List[Dict], 
                            train_ratio: float = 0.9,
                            val_ratio: float = 0.05,
                            test_ratio: float = 0.05) -> Dict[str, List[Dict]]:
        """Split data into train/validation/test sets"""
        # Shuffle data
        data_copy = data.copy()
        random.shuffle(data_copy)
        
        total = len(data_copy)
        train_size = int(total * train_ratio)
        val_size = int(total * val_ratio)
        
        splits = {
            'train': data_copy[:train_size],
            'validation': data_copy[train_size:train_size + val_size],
            'test': data_copy[train_size + val_size:]
        }
        
        return splits
    
    def process_qa_pairs(self):
        """Process Q&A pairs into multiple formats"""
        qa_path = self.input_dir / 'qa_pairs.json'
        if not qa_path.exists():
            logger.warning(f"Q&A pairs file not found: {qa_path}")
            return
        
        with open(qa_path, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        
        logger.info(f"Processing {len(qa_data)} Q&A pairs...")
        
        # Create train/val/test splits
        splits = self.create_training_splits(qa_data)
        
        # Format for different training approaches
        for split_name, split_data in splits.items():
            # Alpaca format
            alpaca_file = self.output_dir / f'qa_alpaca_{split_name}.jsonl'
            with open(alpaca_file, 'w', encoding='utf-8') as f:
                for item in split_data:
                    f.write(self.format_jsonl(item, 'alpaca') + '\n')
            logger.info(f"Saved {len(split_data)} items to {alpaca_file}")
            
            # ShareGPT format
            sharegpt_file = self.output_dir / f'qa_sharegpt_{split_name}.jsonl'
            with open(sharegpt_file, 'w', encoding='utf-8') as f:
                for item in split_data:
                    f.write(self.format_jsonl(item, 'sharegpt') + '\n')
            logger.info(f"Saved {len(split_data)} items to {sharegpt_file}")
            
            # Completion format
            completion_file = self.output_dir / f'qa_completion_{split_name}.txt'
            with open(completion_file, 'w', encoding='utf-8') as f:
                for item in split_data:
                    f.write(self.format_completion(item) + '\n\n')
            logger.info(f"Saved {len(split_data)} items to {completion_file}")
        
        # Create Ollama modelfile with examples
        modelfile_path = self.output_dir / 'nixos_expert.modelfile'
        with open(modelfile_path, 'w', encoding='utf-8') as f:
            f.write(self.format_ollama_examples(splits['train'][:100]))
        logger.info(f"Created Ollama modelfile: {modelfile_path}")
    
    def process_instructions(self):
        """Process instruction data"""
        inst_path = self.input_dir / 'instructions.json'
        if not inst_path.exists():
            logger.warning(f"Instructions file not found: {inst_path}")
            return
        
        with open(inst_path, 'r', encoding='utf-8') as f:
            inst_data = json.load(f)
        
        logger.info(f"Processing {len(inst_data)} instructions...")
        
        # Create splits
        splits = self.create_training_splits(inst_data)
        
        # Format for training
        for split_name, split_data in splits.items():
            # Alpaca format (most common for instruction tuning)
            alpaca_file = self.output_dir / f'instructions_alpaca_{split_name}.jsonl'
            with open(alpaca_file, 'w', encoding='utf-8') as f:
                for item in split_data:
                    f.write(self.format_jsonl(item, 'alpaca') + '\n')
            logger.info(f"Saved {len(split_data)} instructions to {alpaca_file}")
    
    def create_combined_dataset(self):
        """Combine different data types into a single training dataset"""
        combined_data = []
        
        # Load all data types
        data_files = {
            'qa_pairs.json': 'qa',
            'instructions.json': 'instruction',
            'concepts.json': 'concept',
            'troubleshooting.json': 'troubleshooting'
        }
        
        for filename, data_type in data_files.items():
            filepath = self.input_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Tag each item with its type
                for item in data:
                    item['data_type'] = data_type
                    combined_data.extend([item] if isinstance(item, dict) else data)
                    
                logger.info(f"Loaded {len(data)} items from {filename}")
        
        # Shuffle combined data
        random.shuffle(combined_data)
        logger.info(f"Total combined items: {len(combined_data)}")
        
        # Create splits
        splits = self.create_training_splits(combined_data)
        
        # Save combined dataset
        for split_name, split_data in splits.items():
            combined_file = self.output_dir / f'combined_{split_name}.jsonl'
            with open(combined_file, 'w', encoding='utf-8') as f:
                for item in split_data:
                    # Format based on data type
                    if item['data_type'] == 'troubleshooting':
                        # Special format for troubleshooting
                        formatted = {
                            'instruction': f"I'm getting this error: {item.get('error', 'unknown error')}. How do I fix it?",
                            'input': '',
                            'output': item.get('solution', 'Check your configuration for errors.')
                        }
                    else:
                        # Standard format
                        formatted = self.format_alpaca(item)
                    
                    f.write(json.dumps(formatted, ensure_ascii=False) + '\n')
            
            logger.info(f"Saved {len(split_data)} combined items to {combined_file}")
    
    def create_chat_format(self):
        """Create chat-formatted dataset for conversational fine-tuning"""
        qa_path = self.input_dir / 'qa_pairs.json'
        if not qa_path.exists():
            return
        
        with open(qa_path, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        
        # Create multi-turn conversations
        conversations = []
        
        # Group related Q&As by topic
        topic_groups = {}
        for qa in qa_data:
            topic = qa.get('section', 'General')
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(qa)
        
        # Create conversations from topic groups
        for topic, qas in topic_groups.items():
            if len(qas) >= 2:
                # Create a multi-turn conversation
                conversation = {
                    'messages': [
                        {'role': 'system', 'content': self.system_prompts['beginner_friendly']}
                    ]
                }
                
                # Add up to 3 turns
                for qa in qas[:3]:
                    conversation['messages'].append({
                        'role': 'user',
                        'content': qa['question']
                    })
                    conversation['messages'].append({
                        'role': 'assistant',
                        'content': qa['answer']
                    })
                
                conversations.append(conversation)
        
        # Save chat format
        chat_file = self.output_dir / 'nixos_chat_format.jsonl'
        with open(chat_file, 'w', encoding='utf-8') as f:
            for conv in conversations:
                f.write(json.dumps(conv, ensure_ascii=False) + '\n')
        
        logger.info(f"Created {len(conversations)} chat conversations")


def main():
    parser = argparse.ArgumentParser(description='Format NixOS training data')
    parser.add_argument('--input', default='training-data/processed',
                       help='Input directory with processed data')
    parser.add_argument('--output', default='training-data/formatted',
                       help='Output directory for formatted data')
    parser.add_argument('--formats', nargs='+', 
                       default=['qa', 'instructions', 'combined', 'chat'],
                       choices=['qa', 'instructions', 'combined', 'chat'],
                       help='Which formats to generate')
    
    args = parser.parse_args()
    
    formatter = TrainingFormatter(args.input, args.output)
    
    if 'qa' in args.formats:
        formatter.process_qa_pairs()
    
    if 'instructions' in args.formats:
        formatter.process_instructions()
    
    if 'combined' in args.formats:
        formatter.create_combined_dataset()
    
    if 'chat' in args.formats:
        formatter.create_chat_format()
    
    logger.info("Formatting complete!")


if __name__ == '__main__':
    main()