#!/usr/bin/env python3
"""
Test suite for the NixOS model training pipeline
Validates each step of the training process
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_nixos_docs import NixOSDocScraper
from scripts.process_training_data import TrainingDataProcessor
from scripts.format_for_training import TrainingFormatter


class TestNixOSDocScraper(unittest.TestCase):
    """Test the documentation scraper"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = NixOSDocScraper(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_can_fetch(self):
        """Test robots.txt checking"""
        # Test with a known allowed URL
        can_fetch = self.scraper.can_fetch("https://nixos.org/manual/")
        self.assertIsInstance(can_fetch, bool)
    
    def test_parse_manual_page(self):
        """Test HTML parsing"""
        sample_html = """
        <html>
        <head><title>NixOS Manual</title></head>
        <body>
            <div class="chapter">
                <h1>Getting Started</h1>
                <h2>Installation</h2>
                <p>Install NixOS by downloading the ISO.</p>
                <pre>sudo dd if=nixos.iso of=/dev/sda</pre>
            </div>
        </body>
        </html>
        """
        
        result = self.scraper.parse_manual_page(sample_html, "https://nixos.org/test")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'NixOS Manual')
        self.assertIn('Install NixOS', result['content'])
        self.assertEqual(len(result['code_examples']), 1)
        self.assertEqual(result['code_examples'][0]['code'], 'sudo dd if=nixos.iso of=/dev/sda')
    
    def test_save_training_data(self):
        """Test saving scraped data"""
        test_data = {
            'source': 'https://nixos.org/test',
            'title': 'Test Page',
            'content': 'Test content',
            'sections': [],
            'code_examples': []
        }
        
        self.scraper.save_training_data(test_data, 'test-doc')
        
        saved_file = Path(self.temp_dir) / 'test-doc.json'
        self.assertTrue(saved_file.exists())
        
        with open(saved_file) as f:
            loaded = json.load(f)
            self.assertEqual(loaded['title'], 'Test Page')
            self.assertIn('_metadata', loaded)


class TestTrainingDataProcessor(unittest.TestCase):
    """Test the training data processor"""
    
    def setUp(self):
        self.temp_input = tempfile.mkdtemp()
        self.temp_output = tempfile.mkdtemp()
        self.processor = TrainingDataProcessor(self.temp_input, self.temp_output)
        
        # Create sample input data
        self.sample_doc = {
            'source': 'https://nixos.org/manual/test',
            'title': 'Test Documentation',
            'content': 'How to install Firefox? You can install Firefox by adding it to your configuration.nix file.',
            'sections': [
                {
                    'heading': 'Installing Software',
                    'content': 'To install software in NixOS, add packages to environment.systemPackages.',
                    'level': 2
                }
            ],
            'code_examples': [
                {
                    'code': 'environment.systemPackages = with pkgs; [ firefox ];',
                    'language': 'nix'
                }
            ]
        }
        
        with open(Path(self.temp_input) / 'test-doc.json', 'w') as f:
            json.dump(self.sample_doc, f)
    
    def tearDown(self):
        shutil.rmtree(self.temp_input)
        shutil.rmtree(self.temp_output)
    
    def test_extract_qa_pairs(self):
        """Test Q&A extraction"""
        qa_pairs = self.processor.extract_qa_pairs(self.sample_doc)
        
        self.assertGreater(len(qa_pairs), 0)
        
        # Check if questions were generated
        first_qa = qa_pairs[0]
        self.assertIn('question', first_qa)
        self.assertIn('answer', first_qa)
        self.assertIn('How', first_qa['question'])  # Should be a question
    
    def test_create_instruction_data(self):
        """Test instruction format creation"""
        instructions = self.processor.create_instruction_data(self.sample_doc)
        
        self.assertGreater(len(instructions), 0)
        
        # Check instruction format
        first_inst = instructions[0]
        self.assertIn('instruction', first_inst)
        self.assertIn('output', first_inst)
        self.assertIn('environment.systemPackages', first_inst['output'])
    
    def test_process_all_documents(self):
        """Test full processing pipeline"""
        self.processor.process_all_documents()
        
        # Check output files exist
        qa_file = Path(self.temp_output) / 'qa_pairs.json'
        inst_file = Path(self.temp_output) / 'instructions.json'
        stats_file = Path(self.temp_output) / 'statistics.json'
        
        self.assertTrue(qa_file.exists())
        self.assertTrue(inst_file.exists())
        self.assertTrue(stats_file.exists())
        
        # Verify content
        with open(qa_file) as f:
            qa_data = json.load(f)
            self.assertIsInstance(qa_data, list)
            self.assertGreater(len(qa_data), 0)


class TestTrainingFormatter(unittest.TestCase):
    """Test the training data formatter"""
    
    def setUp(self):
        self.temp_input = tempfile.mkdtemp()
        self.temp_output = tempfile.mkdtemp()
        self.formatter = TrainingFormatter(self.temp_input, self.temp_output)
        
        # Create sample processed data
        self.sample_qa = [
            {
                'question': 'How do I install Firefox?',
                'answer': 'Add firefox to environment.systemPackages in configuration.nix',
                'source': 'manual',
                'context': 'Package Management'
            },
            {
                'question': 'What is a flake?',
                'answer': 'A flake is a self-contained Nix package with explicit dependencies.',
                'source': 'manual',
                'context': 'Flakes'
            }
        ]
        
        with open(Path(self.temp_input) / 'qa_pairs.json', 'w') as f:
            json.dump(self.sample_qa, f)
    
    def tearDown(self):
        shutil.rmtree(self.temp_input)
        shutil.rmtree(self.temp_output)
    
    def test_format_alpaca(self):
        """Test Alpaca format generation"""
        formatted = self.formatter.format_alpaca(self.sample_qa[0])
        
        self.assertIn('instruction', formatted)
        self.assertIn('input', formatted)
        self.assertIn('output', formatted)
        self.assertEqual(formatted['instruction'], 'How do I install Firefox?')
    
    def test_format_sharegpt(self):
        """Test ShareGPT format generation"""
        formatted = self.formatter.format_sharegpt(
            self.sample_qa[0], 
            self.formatter.system_prompts['expert']
        )
        
        self.assertIn('conversations', formatted)
        self.assertEqual(len(formatted['conversations']), 3)  # system, human, assistant
        self.assertEqual(formatted['conversations'][1]['from'], 'human')
    
    def test_format_completion(self):
        """Test completion format generation"""
        formatted = self.formatter.format_completion(self.sample_qa[0])
        
        self.assertIn('Q:', formatted)
        self.assertIn('A:', formatted)
        self.assertIn('<|user|>', formatted)
        self.assertIn('<|assistant|>', formatted)
    
    def test_create_training_splits(self):
        """Test data splitting"""
        splits = self.formatter.create_training_splits(self.sample_qa)
        
        self.assertIn('train', splits)
        self.assertIn('validation', splits)
        self.assertIn('test', splits)
        
        # Check proportions (with small dataset, might not be exact)
        total = len(self.sample_qa)
        self.assertGreaterEqual(len(splits['train']), 1)
    
    def test_process_qa_pairs(self):
        """Test Q&A processing into multiple formats"""
        self.formatter.process_qa_pairs()
        
        # Check output files
        output_files = list(Path(self.temp_output).glob('*.jsonl'))
        self.assertGreater(len(output_files), 0)
        
        # Check modelfile creation
        modelfile = Path(self.temp_output) / 'nixos_expert.modelfile'
        self.assertTrue(modelfile.exists())
        
        with open(modelfile) as f:
            content = f.read()
            self.assertIn('FROM mistral', content)
            self.assertIn('SYSTEM', content)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full pipeline"""
    
    def setUp(self):
        self.temp_base = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_base) / 'training-data'
        self.data_dir.mkdir()
        
        # Create subdirectories
        (self.data_dir / 'nixos-docs').mkdir()
        (self.data_dir / 'processed').mkdir()
        (self.data_dir / 'formatted').mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.temp_base)
    
    def test_pipeline_flow(self):
        """Test data flow through the pipeline"""
        # Step 1: Create mock scraped data
        scraper_output = self.data_dir / 'nixos-docs' / 'test-page.json'
        scraped_data = {
            'source': 'https://nixos.org/manual/test',
            'title': 'NixOS Test Page',
            'content': '''
                How do I install packages in NixOS?
                
                You can install packages by adding them to your configuration.nix file.
                
                Q: How do I update NixOS?
                A: Run sudo nixos-rebuild switch to update your system.
            ''',
            'sections': [
                {
                    'heading': 'Package Management',
                    'content': 'NixOS uses a declarative package management system.',
                    'level': 2
                }
            ],
            'code_examples': [
                {
                    'code': 'environment.systemPackages = with pkgs; [ vim firefox ];',
                    'language': 'nix'
                }
            ]
        }
        
        with open(scraper_output, 'w') as f:
            json.dump(scraped_data, f)
        
        # Step 2: Process the data
        processor = TrainingDataProcessor(
            str(self.data_dir / 'nixos-docs'),
            str(self.data_dir / 'processed')
        )
        processor.process_all_documents()
        
        # Verify processing
        qa_file = self.data_dir / 'processed' / 'qa_pairs.json'
        self.assertTrue(qa_file.exists())
        
        with open(qa_file) as f:
            qa_data = json.load(f)
            self.assertGreater(len(qa_data), 0)
        
        # Step 3: Format the data
        formatter = TrainingFormatter(
            str(self.data_dir / 'processed'),
            str(self.data_dir / 'formatted')
        )
        formatter.process_qa_pairs()
        
        # Verify formatting
        formatted_files = list((self.data_dir / 'formatted').glob('*.jsonl'))
        self.assertGreater(len(formatted_files), 0)
        
        # Check content of formatted file
        alpaca_file = self.data_dir / 'formatted' / 'qa_alpaca_train.jsonl'
        if alpaca_file.exists():
            with open(alpaca_file) as f:
                line = f.readline()
                data = json.loads(line)
                self.assertIn('instruction', data)
                self.assertIn('output', data)


class TestValidation(unittest.TestCase):
    """Validate output quality"""
    
    def test_nixos_specific_patterns(self):
        """Test that NixOS-specific content is preserved"""
        processor = TrainingDataProcessor()
        
        # Test NixOS-specific term preservation
        test_content = "Use nixos-rebuild switch to apply changes"
        cleaned = processor._clean_answer(test_content)
        
        self.assertIn('nixos-rebuild', cleaned)
        self.assertIn('switch', cleaned)
    
    def test_code_preservation(self):
        """Test that code examples are preserved correctly"""
        formatter = TrainingFormatter()
        
        test_data = {
            'question': 'How to add a package?',
            'answer': 'Add to configuration.nix',
            'code': 'environment.systemPackages = with pkgs; [ firefox ];'
        }
        
        formatted = formatter.format_alpaca(test_data)
        # Code should be in output if included
        self.assertIn('configuration.nix', formatted['output'])


def run_tests():
    """Run all tests with proper reporting"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNixOSDocScraper))
    suite.addTests(loader.loadTestsFromTestCase(TestTrainingDataProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestTrainingFormatter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)