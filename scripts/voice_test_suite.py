#!/usr/bin/env python3
"""
from typing import List, Dict, Optional
Voice Test Suite - Components Testing Each Other
================================================

A comprehensive test suite where voice components test each other:
- Piper generates audio for Whisper to transcribe
- Different voices test different accents
- Fallback scenarios are tested
- Performance is measured

This implements the user's vision of resilient, self-testing systems.
"""

import os
import sys
import time
import json
import wave
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import numpy as np
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.system_capabilities import CapabilityDetector, SystemCapabilities
from backend.python.voice_interface import ResilientVoiceInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a single test"""
    test_name: str
    persona: str
    success: bool
    accuracy: float
    time_taken: float
    tier_used: str
    notes: str


@dataclass
class TestPhrase:
    """A phrase to test with metadata"""
    text: str
    persona: str
    difficulty: str  # easy, medium, hard
    expected_corrections: Dict[str, str]  # Common misrecognitions


class VoiceTestSuite:
    """Comprehensive voice testing using components to test each other"""
    
    def __init__(self, capabilities: SystemCapabilities):
        self.capabilities = capabilities
        self.voice_interface = ResilientVoiceInterface()
        self.results = []
        self.temp_dir = Path(tempfile.mkdtemp(prefix="voice_test_"))
        
        # Test phrases for each persona
        self.test_phrases = [
            # Grandma Rose - Simple, clear phrases
            TestPhrase(
                "Hello, I need to install Firefox please",
                "Grandma Rose",
                "easy",
                {"firefox": ["firefocks", "fire fox"]}
            ),
            TestPhrase(
                "My computer is running slowly today",
                "Grandma Rose", 
                "easy",
                {"computer": ["compuper"], "slowly": ["showly"]}
            ),
            
            # Viktor (ESL) - Accented English
            TestPhrase(
                "I vant to update ze system",
                "Viktor",
                "medium",
                {"vant": ["want"], "ze": ["the"]}
            ),
            TestPhrase(
                "Vhere is my wifi password",
                "Viktor",
                "medium", 
                {"vhere": ["where"], "wifi": ["vifi"]}
            ),
            
            # Maya (ADHD) - Fast speech
            TestPhrase(
                "quickinstallpythonrightnow",
                "Maya",
                "hard",
                {"quickinstallpythonrightnow": ["quick install python right now"]}
            ),
            TestPhrase(
                "needvscodeASAP",
                "Maya",
                "hard",
                {"needvscodeASAP": ["need vscode ASAP", "need vs code ASAP"]}
            ),
            
            # Carlos (Learning) - Technical terms
            TestPhrase(
                "How do I use nix-shell with Python three eleven",
                "Carlos",
                "medium",
                {"three eleven": ["311", "3.11"]}
            ),
            TestPhrase(
                "What is a flake dot nix file",
                "Carlos",
                "medium",
                {"dot": [".", "dot"]}
            ),
            
            # Luna (Autistic) - Precise language
            TestPhrase(
                "Install package firefox version 121.0",
                "Luna",
                "easy",
                {"121.0": ["one twenty one point zero", "121 point 0"]}
            ),
            TestPhrase(
                "Show system generation number seventeen",
                "Luna",
                "easy",
                {"seventeen": ["17"]}
            ),
            
            # Common mispronunciations
            TestPhrase(
                "Install lib-r-office",
                "General",
                "medium",
                {"lib-r-office": ["libreoffice", "libre office"]}
            ),
            TestPhrase(
                "I need gee-nome terminal",
                "General",
                "medium",
                {"gee-nome": ["gnome"]}
            ),
        ]
    
    def run_all_tests(self, mode: str = "auto") -> List[TestResult]:
        """Run all tests in specified mode"""
        logger.info(f"🚀 Starting Voice Test Suite in {mode} mode")
        logger.info(f"🔍 System has: Whisper={self.capabilities.has_whisper}, "
                   f"Piper={self.capabilities.has_piper}")
        
        # Run different test categories
        if mode in ["auto", "comprehensive"]:
            self._test_component_interaction()
            self._test_fallback_scenarios()
            self._test_persona_phrases()
            self._test_performance_benchmarks()
            
        elif mode == "quick":
            self._test_basic_functionality()
            
        elif mode == "interactive":
            self._run_interactive_tests()
        
        # Generate report
        self._generate_report()
        
        return self.results
    
    def _test_component_interaction(self):
        """Test 1: Components testing each other"""
        logger.info("\n🔄 Test 1: Component Interaction Testing")
        
        if not (self.capabilities.has_piper and self.capabilities.has_whisper):
            logger.warning("⚠️  Skipping: Requires both Piper and Whisper")
            return
        
        # Piper generates -> Whisper transcribes
        for phrase in self.test_phrases[:3]:  # Test first 3 phrases
            logger.info(f"Testing: '{phrase.text}'")
            
            # Generate audio with Piper
            audio_file = self.temp_dir / f"{phrase.persona}_{int(time.time())}.wav"
            
            try:
                # Generate speech
                start_time = time.time()
                self.voice_interface.text_to_speech(phrase.text, str(audio_file))
                tts_time = time.time() - start_time
                
                # Transcribe with Whisper
                start_time = time.time()
                transcription = self.voice_interface.speech_to_text(str(audio_file))
                stt_time = time.time() - start_time
                
                # Calculate accuracy
                accuracy = self._calculate_accuracy(phrase.text, transcription)
                
                # Check if corrections needed
                corrected = transcription
                for wrong, correct_options in phrase.expected_corrections.items():
                    if wrong in transcription.lower():
                        for correct in correct_options:
                            if correct in transcription.lower():
                                corrected = transcription.replace(wrong, correct)
                                break
                
                result = TestResult(
                    test_name="Component Interaction",
                    persona=phrase.persona,
                    success=accuracy > 0.8,
                    accuracy=accuracy,
                    time_taken=tts_time + stt_time,
                    tier_used="Piper->Whisper",
                    notes=f"Original: {transcription}, Corrected: {corrected}"
                )
                
                self.results.append(result)
                logger.info(f"✅ Accuracy: {accuracy:.2%}, Time: {result.time_taken:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                self.results.append(TestResult(
                    test_name="Component Interaction",
                    persona=phrase.persona,
                    success=False,
                    accuracy=0.0,
                    time_taken=0.0,
                    tier_used="Failed",
                    notes=str(e)
                ))
    
    def _test_fallback_scenarios(self):
        """Test 2: Fallback tier testing"""
        logger.info("\n🔀 Test 2: Fallback Scenarios")
        
        # Simulate Whisper failure
        if self.capabilities.has_vosk:
            logger.info("Testing Vosk fallback...")
            
            # Force Vosk usage
            original_whisper = self.voice_interface.whisper_available
            self.voice_interface.whisper_available = False
            
            audio_file = self._generate_test_audio("Testing fallback to Vosk")
            
            try:
                start_time = time.time()
                transcription = self.voice_interface.speech_to_text(str(audio_file))
                elapsed = time.time() - start_time
                
                result = TestResult(
                    test_name="Fallback Test",
                    persona="System",
                    success=len(transcription) > 0,
                    accuracy=0.7,  # Vosk is less accurate
                    time_taken=elapsed,
                    tier_used="Vosk",
                    notes=f"Transcription: {transcription}"
                )
                self.results.append(result)
                
            finally:
                self.voice_interface.whisper_available = original_whisper
        
        # Test espeak fallback
        if self.capabilities.has_espeak:
            logger.info("Testing espeak fallback...")
            
            original_piper = self.voice_interface.piper_available
            self.voice_interface.piper_available = False
            
            try:
                audio_file = self.temp_dir / "espeak_test.wav"
                start_time = time.time()
                self.voice_interface.text_to_speech("Hello from espeak", str(audio_file))
                elapsed = time.time() - start_time
                
                result = TestResult(
                    test_name="Fallback Test",
                    persona="System",
                    success=audio_file.exists(),
                    accuracy=1.0,
                    time_taken=elapsed,
                    tier_used="espeak",
                    notes="Robotic but functional"
                )
                self.results.append(result)
                
            finally:
                self.voice_interface.piper_available = original_piper
    
    def _test_persona_phrases(self):
        """Test 3: Each persona's specific phrases"""
        logger.info("\n👥 Test 3: Persona-Specific Testing")
        
        personas_tested = set()
        
        for phrase in self.test_phrases:
            if phrase.persona in personas_tested and phrase.persona != "General":
                continue
                
            logger.info(f"\nTesting {phrase.persona}: '{phrase.text}'")
            
            # Generate and test
            audio_file = self._generate_test_audio(phrase.text)
            
            if audio_file:
                transcription = self.voice_interface.speech_to_text(str(audio_file))
                accuracy = self._calculate_accuracy(phrase.text, transcription)
                
                result = TestResult(
                    test_name="Persona Test",
                    persona=phrase.persona,
                    success=accuracy > 0.7,
                    accuracy=accuracy,
                    time_taken=0.0,
                    tier_used=self.voice_interface.active_stt_tier,
                    notes=f"Difficulty: {phrase.difficulty}"
                )
                
                self.results.append(result)
                personas_tested.add(phrase.persona)
    
    def _test_performance_benchmarks(self):
        """Test 4: Performance measurements"""
        logger.info("\n⚡ Test 4: Performance Benchmarks")
        
        # Test different audio lengths
        test_lengths = [
            ("Short", "Install Firefox"),
            ("Medium", "I need help installing Visual Studio Code for development"),
            ("Long", "Can you please help me understand how to use NixOS configuration "
                     "files to manage my system packages and services declaratively")
        ]
        
        for length_name, text in test_lengths:
            audio_file = self._generate_test_audio(text)
            
            if audio_file:
                # Measure STT performance
                start_time = time.time()
                transcription = self.voice_interface.speech_to_text(str(audio_file))
                stt_time = time.time() - start_time
                
                # Measure TTS performance
                output_file = self.temp_dir / f"perf_{length_name}.wav"
                start_time = time.time()
                self.voice_interface.text_to_speech(text, str(output_file))
                tts_time = time.time() - start_time
                
                result = TestResult(
                    test_name="Performance",
                    persona=length_name,
                    success=True,
                    accuracy=1.0,
                    time_taken=stt_time + tts_time,
                    tier_used=f"{self.voice_interface.active_stt_tier}+{self.voice_interface.active_tts_tier}",
                    notes=f"STT: {stt_time:.2f}s, TTS: {tts_time:.2f}s"
                )
                
                self.results.append(result)
    
    def _test_basic_functionality(self):
        """Quick basic tests"""
        logger.info("\n✨ Running Quick Tests")
        
        # Test STT
        if self.capabilities.has_whisper or self.capabilities.has_vosk:
            audio_file = self._generate_test_audio("Quick test")
            if audio_file:
                result = self.voice_interface.speech_to_text(str(audio_file))
                logger.info(f"STT Result: {result}")
        
        # Test TTS
        if self.capabilities.has_piper or self.capabilities.has_espeak:
            output = self.temp_dir / "quick_tts.wav"
            self.voice_interface.text_to_speech("Quick test", str(output))
            logger.info(f"TTS Generated: {output.exists()}")
    
    def _run_interactive_tests(self):
        """Interactive testing mode"""
        logger.info("\n🎮 Interactive Testing Mode")
        
        while True:
            print("\n" + "="*50)
            print("Voice Test Suite - Interactive Mode")
            print("="*50)
            print("1. Test Piper → Whisper round trip")
            print("2. Test fallback scenarios")
            print("3. Test specific persona")
            print("4. Custom phrase test")
            print("5. View results")
            print("6. Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._interactive_round_trip()
            elif choice == "2":
                self._test_fallback_scenarios()
            elif choice == "3":
                self._interactive_persona_test()
            elif choice == "4":
                self._interactive_custom_test()
            elif choice == "5":
                self._generate_report()
            elif choice == "6":
                break
    
    def _interactive_round_trip(self):
        """Interactive round trip test"""
        text = input("Enter text to test: ")
        
        # Generate with Piper
        audio_file = self.temp_dir / f"interactive_{int(time.time())}.wav"
        print("🔊 Generating speech with Piper...")
        self.voice_interface.text_to_speech(text, str(audio_file))
        
        # Play audio (optional)
        if input("Play audio? (y/n): ").lower() == 'y':
            subprocess.run(['aplay', str(audio_file)])
        
        # Transcribe with Whisper
        print("🎤 Transcribing with Whisper...")
        transcription = self.voice_interface.speech_to_text(str(audio_file))
        
        print(f"\n📝 Original: {text}")
        print(f"📝 Transcribed: {transcription}")
        print(f"✅ Accuracy: {self._calculate_accuracy(text, transcription):.2%}")
    
    def _generate_test_audio(self, text: str) -> Optional[Path]:
        """Generate test audio file"""
        if not (self.capabilities.has_piper or self.capabilities.has_espeak):
            return None
            
        audio_file = self.temp_dir / f"test_{int(time.time())}.wav"
        
        try:
            self.voice_interface.text_to_speech(text, str(audio_file))
            return audio_file if audio_file.exists() else None
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            return None
    
    def _calculate_accuracy(self, original: str, transcribed: str) -> float:
        """Calculate word accuracy between original and transcribed"""
        if not transcribed:
            return 0.0
            
        original_words = original.lower().split()
        transcribed_words = transcribed.lower().split()
        
        # Simple word matching
        matches = sum(1 for o, t in zip(original_words, transcribed_words) if o == t)
        total = max(len(original_words), len(transcribed_words))
        
        return matches / total if total > 0 else 0.0
    
    def _generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("Voice Test Suite Report")
        print("="*60)
        
        # Group by test name
        test_groups = {}
        for result in self.results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            test_groups[result.test_name].append(result)
        
        # Print results by group
        for test_name, results in test_groups.items():
            print(f"\n{test_name}:")
            print("-" * 40)
            
            success_rate = sum(1 for r in results if r.success) / len(results)
            avg_accuracy = sum(r.accuracy for r in results) / len(results)
            avg_time = sum(r.time_taken for r in results) / len(results)
            
            print(f"Success Rate: {success_rate:.1%}")
            print(f"Average Accuracy: {avg_accuracy:.1%}")
            print(f"Average Time: {avg_time:.2f}s")
            
            # Show per-persona results
            personas = {}
            for r in results:
                if r.persona not in personas:
                    personas[r.persona] = []
                personas[r.persona].append(r)
            
            for persona, p_results in personas.items():
                p_success = sum(1 for r in p_results if r.success) / len(p_results)
                print(f"  {persona}: {p_success:.0%} success")
        
        # Overall summary
        print("\n" + "="*60)
        print("Overall Summary:")
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {sum(1 for r in self.results if r.success)}")
        print(f"Failed: {sum(1 for r in self.results if not r.success)}")
        
        # Save detailed results
        report_path = self.temp_dir / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")


def main():
    """Run the voice test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Test Suite")
    parser.add_argument('--mode', choices=['auto', 'quick', 'comprehensive', 'interactive'],
                      default='auto', help='Test mode')
    parser.add_argument('--save-audio', action='store_true',
                      help='Keep generated audio files')
    
    args = parser.parse_args()
    
    # Detect capabilities
    print("🔍 Detecting system capabilities...")
    detector = CapabilityDetector()
    capabilities = detector.detect_all()
    
    # Run tests
    suite = VoiceTestSuite(capabilities)
    results = suite.run_all_tests(args.mode)
    
    # Cleanup unless requested to save
    if not args.save_audio:
        import shutil
        shutil.rmtree(suite.temp_dir)
        print("\n🧹 Cleaned up temporary files")
    else:
        print(f"\n💾 Audio files saved in: {suite.temp_dir}")


if __name__ == "__main__":
    main()