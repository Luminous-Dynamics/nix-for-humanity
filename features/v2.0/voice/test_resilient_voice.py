#!/usr/bin/env python3
"""
Comprehensive Test Suite for Resilient Voice Interface
=====================================================

Tests the multi-tiered voice system with real binaries, fallback mechanisms,
and cross-component testing (Piper speaks, Whisper listens).
"""

import os
import sys
import time
import json
import tempfile
import subprocess
import asyncio
import wave
import struct
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_interface import ResilientVoiceInterface, VoiceEngineStatus

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestAudioGenerator:
    """Generate test audio for testing STT engines"""
    
    @staticmethod
    def create_silence(duration: float, sample_rate: int = 16000) -> bytes:
        """Create silent audio data"""
        num_samples = int(duration * sample_rate)
        return struct.pack('<' + 'h' * num_samples, *[0] * num_samples)
    
    @staticmethod
    def create_tone(frequency: float, duration: float, sample_rate: int = 16000) -> bytes:
        """Create a sine wave tone"""
        import math
        num_samples = int(duration * sample_rate)
        samples = []
        
        for i in range(num_samples):
            sample = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            samples.append(sample)
        
        return struct.pack('<' + 'h' * num_samples, *samples)
    
    @staticmethod
    def save_wav(audio_data: bytes, filename: str, sample_rate: int = 16000, channels: int = 1):
        """Save audio data to WAV file"""
        with wave.open(filename, 'wb') as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)
            wav.writeframes(audio_data)


class TestResilientVoice(unittest.TestCase):
    """Test cases for resilient voice interface"""
    
    def setUp(self):
        """Set up test environment"""
        self.interface = ResilientVoiceInterface()
        self.test_dir = tempfile.mkdtemp(prefix="voice_test_")
        self.audio_gen = TestAudioGenerator()
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temp directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_engine_detection(self):
        """Test that engine detection works correctly"""
        # At least one engine should be detected
        stt_available = any(e.available for e in self.interface.engines["stt"].values())
        tts_available = any(e.available for e in self.interface.engines["tts"].values())
        
        self.assertTrue(stt_available or tts_available, 
                       "No voice engines detected - install at least one")
        
        # Log detected engines
        logger.info("Detected STT engines:")
        for name, engine in self.interface.engines["stt"].items():
            logger.info(f"  {name}: {'✅' if engine.available else '❌'}")
        
        logger.info("Detected TTS engines:")
        for name, engine in self.interface.engines["tts"].items():
            logger.info(f"  {name}: {'✅' if engine.available else '❌'}")
    
    def test_fallback_mechanism(self):
        """Test fallback from primary to secondary engines"""
        # Save original states
        original_stt = dict(self.interface.engines["stt"])
        original_tts = dict(self.interface.engines["tts"])
        
        # Test STT fallback
        if self.interface.engines["stt"]["whisper"].available:
            # Simulate Whisper failure
            self.interface.engines["stt"]["whisper"].available = False
            self.interface._select_best_engines()
            
            # Should fall back to Vosk if available
            if original_stt["vosk"].available:
                self.assertEqual(self.interface.current_stt, "vosk")
                logger.info("✅ STT fallback: Whisper → Vosk")
            else:
                self.assertIsNone(self.interface.current_stt)
                logger.info("✅ STT fallback: Whisper → None (no fallback available)")
        
        # Test TTS fallback
        if self.interface.engines["tts"]["piper"].available:
            # Simulate Piper failure
            self.interface.engines["tts"]["piper"].available = False
            self.interface._select_best_engines()
            
            # Should fall back to espeak if available
            if original_tts["espeak"].available:
                self.assertEqual(self.interface.current_tts, "espeak")
                logger.info("✅ TTS fallback: Piper → espeak")
            else:
                self.assertIsNone(self.interface.current_tts)
                logger.info("✅ TTS fallback: Piper → None (no fallback available)")
        
        # Restore original states
        self.interface.engines = {"stt": original_stt, "tts": original_tts}
        self.interface._select_best_engines()
    
    async def test_tts_synthesis(self):
        """Test TTS synthesis with available engines"""
        test_phrases = [
            "Hello, I am testing the voice system.",
            "This is a test of fallback mechanisms.",
            "Can you hear me clearly?"
        ]
        
        results = {}
        
        for phrase in test_phrases:
            if self.interface.current_tts:
                start_time = time.time()
                audio, elapsed = await self.interface.synthesize_speech(phrase)
                
                if audio:
                    # Save audio for manual verification
                    filename = os.path.join(self.test_dir, 
                        f"tts_{self.interface.current_tts}_{phrase[:10]}.wav")
                    with open(filename, 'wb') as f:
                        f.write(audio)
                    
                    results[phrase] = {
                        "engine": self.interface.current_tts,
                        "success": True,
                        "elapsed": elapsed,
                        "audio_size": len(audio),
                        "file": filename
                    }
                    logger.info(f"✅ TTS '{phrase[:30]}...' - {elapsed:.2f}s, {len(audio)} bytes")
                else:
                    results[phrase] = {"success": False}
                    logger.error(f"❌ TTS failed for '{phrase[:30]}...'")
        
        return results
    
    async def test_cross_component(self):
        """Test using one component to test another (Piper → Whisper)"""
        if not (self.interface.current_tts and self.interface.current_stt):
            self.skipTest("Need both TTS and STT for cross-component testing")
        
        test_phrases = [
            "Testing cross component integration",
            "The quick brown fox jumps over the lazy dog",
            "Install Firefox please"
        ]
        
        results = []
        
        for original_phrase in test_phrases:
            # Step 1: Generate speech with TTS
            logger.info(f"🔊 Generating: '{original_phrase}'")
            audio, tts_time = await self.interface.synthesize_speech(original_phrase)
            
            if not audio:
                logger.error("TTS generation failed")
                continue
            
            # Save audio for debugging
            audio_file = os.path.join(self.test_dir, f"cross_test_{len(results)}.wav")
            with open(audio_file, 'wb') as f:
                f.write(audio)
            
            # Step 2: Transcribe with STT
            logger.info(f"🎤 Transcribing audio...")
            recognized_text, stt_time = await self.interface.transcribe_audio(audio)
            
            # Compare results
            if recognized_text:
                similarity = self._calculate_similarity(original_phrase.lower(), 
                                                       recognized_text.lower())
                results.append({
                    "original": original_phrase,
                    "recognized": recognized_text,
                    "similarity": similarity,
                    "tts_engine": self.interface.current_tts,
                    "stt_engine": self.interface.current_stt,
                    "tts_time": tts_time,
                    "stt_time": stt_time,
                    "audio_file": audio_file
                })
                
                logger.info(f"📝 Original:   '{original_phrase}'")
                logger.info(f"📝 Recognized: '{recognized_text}'")
                logger.info(f"📊 Similarity: {similarity:.1%}")
            else:
                logger.error("STT transcription failed")
        
        # Report results
        if results:
            successful = sum(1 for r in results if r["similarity"] > 0.7)
            logger.info(f"\n📊 Cross-component test: {successful}/{len(results)} successful")
            
            for r in results:
                status = "✅" if r["similarity"] > 0.7 else "⚠️"
                logger.info(f"{status} '{r['original'][:30]}...' → '{r['recognized'][:30]}...' "
                          f"({r['similarity']:.1%})")
        
        return results
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings (simple approach)"""
        # Simple word-based similarity
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def test_performance_tracking(self):
        """Test performance tracking and reporting"""
        if not self.interface.current_tts:
            self.skipTest("No TTS engine available")
        
        # Generate multiple requests to build performance history
        test_phrases = ["Test " + str(i) for i in range(5)]
        
        for phrase in test_phrases:
            await self.interface.synthesize_speech(phrase)
            await asyncio.sleep(0.1)  # Small delay between requests
        
        # Get performance report
        report = self.interface.get_performance_report()
        
        # Verify report structure
        self.assertIn("current_setup", report)
        self.assertIn("engines", report)
        self.assertIn("recommendations", report)
        
        # Check if performance metrics were recorded
        tts_engine = self.interface.current_tts
        if tts_engine:
            engine_stats = report["engines"]["tts"][tts_engine]
            self.assertGreater(engine_stats["usage_count"], 0)
            self.assertGreater(engine_stats["avg_response_time"], 0)
        
        logger.info(f"📊 Performance Report:\n{json.dumps(report, indent=2)}")
    
    async def test_resource_adaptation(self):
        """Test system adaptation to different resource availability"""
        # Simulate different resource scenarios
        scenarios = [
            {
                "name": "High Performance",
                "whisper": True, "vosk": True,
                "piper": True, "espeak": True
            },
            {
                "name": "Limited STT",
                "whisper": False, "vosk": True,
                "piper": True, "espeak": True
            },
            {
                "name": "Limited TTS",
                "whisper": True, "vosk": True,
                "piper": False, "espeak": True
            },
            {
                "name": "Minimal Resources",
                "whisper": False, "vosk": True,
                "piper": False, "espeak": True
            }
        ]
        
        original_engines = {
            "stt": dict(self.interface.engines["stt"]),
            "tts": dict(self.interface.engines["tts"])
        }
        
        for scenario in scenarios:
            logger.info(f"\n🔧 Testing scenario: {scenario['name']}")
            
            # Set engine availability
            self.interface.engines["stt"]["whisper"].available = scenario["whisper"]
            self.interface.engines["stt"]["vosk"].available = scenario["vosk"]
            self.interface.engines["tts"]["piper"].available = scenario["piper"]
            self.interface.engines["tts"]["espeak"].available = scenario["espeak"]
            
            # Re-select engines
            self.interface._select_best_engines()
            
            # Get status message
            status = self.interface.get_status_message()
            logger.info(f"📊 Status: {status}")
            logger.info(f"   STT: {self.interface.current_stt or 'None'}")
            logger.info(f"   TTS: {self.interface.current_tts or 'None'}")
            
            # Test basic functionality
            if self.interface.current_tts:
                test_phrase = f"Testing {scenario['name']} configuration"
                audio, elapsed = await self.interface.synthesize_speech(test_phrase)
                if audio:
                    logger.info(f"   ✅ TTS working ({elapsed:.2f}s)")
                else:
                    logger.info(f"   ❌ TTS failed")
        
        # Restore original configuration
        self.interface.engines = original_engines
        self.interface._select_best_engines()


class InteractiveVoiceDemo:
    """Interactive demonstration of voice system capabilities"""
    
    def __init__(self):
        self.interface = ResilientVoiceInterface()
        self.running = False
    
    async def run(self):
        """Run interactive demo"""
        print("""
🎙️  Interactive Voice System Demo
=================================

This demo shows the resilient voice system in action with real-time
fallback mechanisms and quality adaptation.
        """)
        
        # Show initial status
        print("\n📊 Initial System Status:")
        print(self.interface.get_status_message())
        print("\nAvailable engines:")
        for engine_type in ["stt", "tts"]:
            print(f"\n{engine_type.upper()}:")
            for name, engine in self.interface.engines[engine_type].items():
                status = "✅" if engine.available else "❌"
                print(f"  {status} {name} - Quality: {engine.quality}, Speed: {engine.performance}")
        
        # Menu
        while True:
            print("\n📋 Options:")
            print("1. Test TTS with all available engines")
            print("2. Test cross-component (TTS → STT)")
            print("3. Simulate engine failures")
            print("4. Show performance report")
            print("5. Test adaptation scenarios")
            print("6. Run stress test")
            print("0. Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                await self.test_all_tts()
            elif choice == "2":
                await self.test_cross_component()
            elif choice == "3":
                await self.simulate_failures()
            elif choice == "4":
                self.show_performance_report()
            elif choice == "5":
                await self.test_adaptation()
            elif choice == "6":
                await self.run_stress_test()
            else:
                print("Invalid option")
    
    async def test_all_tts(self):
        """Test all available TTS engines"""
        print("\n🔊 Testing all TTS engines...")
        
        test_phrase = input("Enter test phrase (or press Enter for default): ").strip()
        if not test_phrase:
            test_phrase = "Hello! This is a test of the text to speech system."
        
        # Save current engine
        original_tts = self.interface.current_tts
        
        # Test each available engine
        for engine_name, engine in self.interface.engines["tts"].items():
            if engine.available:
                print(f"\n🎵 Testing {engine_name}...")
                self.interface.current_tts = engine_name
                
                start_time = time.time()
                audio, elapsed = await self.interface.synthesize_speech(test_phrase)
                
                if audio:
                    # Save audio
                    filename = f"test_{engine_name}_{int(time.time())}.wav"
                    with open(filename, 'wb') as f:
                        f.write(audio)
                    print(f"✅ Success! Audio saved to {filename}")
                    print(f"   Time: {elapsed:.2f}s, Size: {len(audio)} bytes")
                    print(f"   Quality: {engine.quality}, Speed: {engine.performance}")
                    
                    # Play audio if possible
                    if sys.platform == "linux":
                        subprocess.run(["aplay", filename], capture_output=True)
                else:
                    print(f"❌ Failed to generate audio")
        
        # Restore original engine
        self.interface.current_tts = original_tts
    
    async def test_cross_component(self):
        """Test TTS speaking to STT"""
        if not (self.interface.current_tts and self.interface.current_stt):
            print("❌ Need both TTS and STT engines for this test")
            return
        
        print(f"\n🔄 Cross-component test: {self.interface.current_tts} → {self.interface.current_stt}")
        
        test_phrases = [
            "The quick brown fox jumps over the lazy dog",
            "Install Firefox on my computer",
            "Show me the system status",
            "Update all packages please"
        ]
        
        print("\nTest phrases:")
        for i, phrase in enumerate(test_phrases):
            print(f"{i+1}. {phrase}")
        
        choice = input("\nSelect phrase (1-4) or enter custom: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 4:
            test_phrase = test_phrases[int(choice) - 1]
        else:
            test_phrase = choice if choice else test_phrases[0]
        
        print(f"\n🔊 Speaking: '{test_phrase}'")
        audio, tts_time = await self.interface.synthesize_speech(test_phrase)
        
        if audio:
            print(f"✅ TTS generated ({tts_time:.2f}s)")
            
            # Save for debugging
            audio_file = f"cross_test_{int(time.time())}.wav"
            with open(audio_file, 'wb') as f:
                f.write(audio)
            
            print(f"🎤 Transcribing...")
            recognized, stt_time = await self.interface.transcribe_audio(audio)
            
            if recognized:
                print(f"✅ STT recognized ({stt_time:.2f}s)")
                print(f"\n📝 Original:   '{test_phrase}'")
                print(f"📝 Recognized: '{recognized}'")
                
                # Calculate accuracy
                original_words = set(test_phrase.lower().split())
                recognized_words = set(recognized.lower().split())
                accuracy = len(original_words.intersection(recognized_words)) / len(original_words)
                print(f"📊 Word accuracy: {accuracy:.1%}")
            else:
                print(f"❌ STT failed to recognize")
        else:
            print(f"❌ TTS failed to generate audio")
    
    async def simulate_failures(self):
        """Simulate engine failures and test fallbacks"""
        print("\n🔧 Simulating engine failures...")
        
        # Save original states
        original_engines = {
            "stt": {k: v.available for k, v in self.interface.engines["stt"].items()},
            "tts": {k: v.available for k, v in self.interface.engines["tts"].items()}
        }
        
        scenarios = [
            ("Whisper fails", {"stt": {"whisper": False}}),
            ("Piper fails", {"tts": {"piper": False}}),
            ("All primary engines fail", {"stt": {"whisper": False}, "tts": {"piper": False}}),
            ("Only fallbacks available", {"stt": {"whisper": False}, "tts": {"piper": False}})
        ]
        
        for scenario_name, failures in scenarios:
            print(f"\n📍 Scenario: {scenario_name}")
            
            # Apply failures
            for engine_type, engines in failures.items():
                for engine_name, available in engines.items():
                    self.interface.engines[engine_type][engine_name].available = available
            
            # Re-select engines
            self.interface._select_best_engines()
            
            # Show new status
            print(f"   STT: {self.interface.current_stt or 'None'}")
            print(f"   TTS: {self.interface.current_tts or 'None'}")
            print(f"   Status: {self.interface.get_status_message()}")
            
            # Test functionality
            if self.interface.current_tts:
                audio, _ = await self.interface.synthesize_speech("Testing fallback")
                print(f"   TTS test: {'✅ Working' if audio else '❌ Failed'}")
        
        # Restore original states
        for engine_type in ["stt", "tts"]:
            for engine_name, available in original_engines[engine_type].items():
                self.interface.engines[engine_type][engine_name].available = available
        
        self.interface._select_best_engines()
        print(f"\n✅ Restored original configuration")
    
    def show_performance_report(self):
        """Display detailed performance report"""
        report = self.interface.get_performance_report()
        print("\n📊 Performance Report")
        print("=" * 50)
        print(json.dumps(report, indent=2))
    
    async def test_adaptation(self):
        """Test system adaptation to resource changes"""
        print("\n🔄 Testing resource adaptation...")
        
        print("\nThis test will simulate different resource availability scenarios")
        print("and show how the system adapts.\n")
        
        # Define test phrase
        test_phrase = "Testing system adaptation"
        
        # Test different resource levels
        levels = [
            ("🏃 Fast mode", {"quality": "low", "speed": "fast"}),
            ("🎯 Balanced mode", {"quality": "medium", "speed": "normal"}),
            ("✨ Quality mode", {"quality": "high", "speed": "slow"})
        ]
        
        for mode_name, preferences in levels:
            print(f"\n{mode_name}:")
            
            # In a real system, this would adjust engine selection based on preferences
            # For now, just show what would happen
            print(f"  Preferences: Quality={preferences['quality']}, Speed={preferences['speed']}")
            
            if self.interface.current_tts:
                start = time.time()
                audio, _ = await self.interface.synthesize_speech(test_phrase)
                elapsed = time.time() - start
                
                if audio:
                    print(f"  ✅ Generated in {elapsed:.2f}s ({len(audio)} bytes)")
                    print(f"  Using: {self.interface.current_tts}")
    
    async def run_stress_test(self):
        """Run stress test to evaluate system under load"""
        print("\n🏃 Running stress test...")
        
        iterations = 10
        test_phrases = [
            "Short test",
            "This is a medium length test phrase for the system",
            "The quick brown fox jumps over the lazy dog, testing all letters"
        ]
        
        results = {
            "tts": {"success": 0, "failed": 0, "times": []},
            "cross": {"success": 0, "failed": 0, "accuracies": []}
        }
        
        print(f"\nRunning {iterations} iterations...")
        
        for i in range(iterations):
            phrase = test_phrases[i % len(test_phrases)]
            
            # Test TTS
            if self.interface.current_tts:
                start = time.time()
                audio, _ = await self.interface.synthesize_speech(phrase)
                elapsed = time.time() - start
                
                if audio:
                    results["tts"]["success"] += 1
                    results["tts"]["times"].append(elapsed)
                else:
                    results["tts"]["failed"] += 1
            
            # Test cross-component if both available
            if self.interface.current_tts and self.interface.current_stt:
                audio, _ = await self.interface.synthesize_speech(phrase)
                if audio:
                    recognized, _ = await self.interface.transcribe_audio(audio)
                    if recognized:
                        # Simple accuracy check
                        accuracy = len(set(phrase.lower().split()) & 
                                     set(recognized.lower().split())) / len(phrase.split())
                        results["cross"]["success"] += 1
                        results["cross"]["accuracies"].append(accuracy)
                    else:
                        results["cross"]["failed"] += 1
            
            # Progress indicator
            print(f"\r  Progress: {i+1}/{iterations}", end="", flush=True)
        
        print("\n\n📊 Stress Test Results:")
        print(f"TTS: {results['tts']['success']}/{iterations} successful")
        if results["tts"]["times"]:
            avg_time = sum(results["tts"]["times"]) / len(results["tts"]["times"])
            print(f"  Average time: {avg_time:.2f}s")
            print(f"  Min/Max: {min(results['tts']['times']):.2f}s / {max(results['tts']['times']):.2f}s")
        
        if results["cross"]["accuracies"]:
            print(f"\nCross-component: {results['cross']['success']} successful")
            avg_accuracy = sum(results["cross"]["accuracies"]) / len(results["cross"]["accuracies"])
            print(f"  Average accuracy: {avg_accuracy:.1%}")


async def run_automated_tests():
    """Run all automated tests"""
    print("""
🤖 Automated Test Suite for Resilient Voice Interface
====================================================
""")
    
    # Run unit tests
    print("Running unit tests...\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestResilientVoice)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run async tests manually
    print("\n\nRunning async tests...\n")
    
    test_instance = TestResilientVoice()
    test_instance.setUp()
    
    try:
        # Test TTS
        print("\n📝 Testing TTS synthesis...")
        await test_instance.test_tts_synthesis()
        
        # Test cross-component
        print("\n📝 Testing cross-component integration...")
        await test_instance.test_cross_component()
        
        # Test performance tracking
        print("\n📝 Testing performance tracking...")
        await test_instance.test_performance_tracking()
        
        # Test resource adaptation
        print("\n📝 Testing resource adaptation...")
        await test_instance.test_resource_adaptation()
        
    finally:
        test_instance.tearDown()
    
    print("\n✅ Automated tests complete!")
    
    return result.wasSuccessful()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test resilient voice interface")
    parser.add_argument("--automated", action="store_true", 
                       help="Run automated tests")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run interactive demo")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick smoke test")
    
    args = parser.parse_args()
    
    if args.automated:
        success = await run_automated_tests()
        sys.exit(0 if success else 1)
    
    elif args.interactive:
        demo = InteractiveVoiceDemo()
        await demo.run()
    
    elif args.quick:
        # Quick smoke test
        print("🚀 Running quick smoke test...\n")
        
        interface = ResilientVoiceInterface()
        print("Status:", interface.get_status_message())
        
        if interface.current_tts:
            print("\nTesting TTS...")
            audio, elapsed = await interface.synthesize_speech("Quick test of voice system")
            print(f"Result: {'✅ Success' if audio else '❌ Failed'} ({elapsed:.2f}s)")
        
        print("\nPerformance report:")
        print(json.dumps(interface.get_performance_report(), indent=2))
    
    else:
        # Default: show options
        print("""
Usage: python test_resilient_voice.py [options]

Options:
  --automated    Run full automated test suite
  --interactive  Run interactive demo
  --quick        Run quick smoke test

Example:
  python test_resilient_voice.py --automated
        """)


if __name__ == "__main__":
    asyncio.run(main())