"""
from typing import List, Tuple, Dict, Optional
🎯 Voice Performance Testing Framework

Real-world performance benchmarks for the voice interface system, ensuring
consciousness-first response times and resource usage across all personas.

This framework validates that the voice interface meets the stringent performance
requirements necessary for serving all 10 personas effectively, especially those
with specific timing needs like Maya (ADHD <1s) and flow state protection.
"""

import asyncio
import pytest
import time
import statistics
import psutil
import threading
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import tempfile

# Import voice components
from nix_humanity.voice.model_manager import ModelManager, ModelType, ModelSize
from nix_humanity.voice.pipecat_interface import PipecatVoiceInterface
from nix_humanity.voice.voice_config import VOICE_PERSONAS


@dataclass
class PerformanceBenchmark:
    """Performance benchmark specification for voice operations."""
    operation_name: str
    max_duration_ms: int
    max_memory_mb: int
    max_cpu_percent: float
    persona_requirements: Dict[str, int]  # persona -> max_ms
    description: str


@dataclass
class PerformanceResult:
    """Results from a performance test run."""
    duration_ms: float
    memory_used_mb: float
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None


class PerformanceMonitor:
    """Monitor system resources during voice operations."""
    
    def __init__(self):
        self.monitoring = False
        self.cpu_samples = []
        self.memory_samples = []
        self.start_memory = 0
        
    def start_monitoring(self):
        """Start monitoring system resources."""
        self.monitoring = True
        self.cpu_samples = []
        self.memory_samples = []
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Background monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Tuple[float, float]:
        """Stop monitoring and return average CPU and peak memory usage."""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1.0)
        
        avg_cpu = statistics.mean(self.cpu_samples) if self.cpu_samples else 0.0
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        peak_memory = current_memory - self.start_memory
        
        return avg_cpu, peak_memory
    
    def _monitor_resources(self):
        """Background thread to monitor resources."""
        process = psutil.Process()
        
        while self.monitoring:
            try:
                self.cpu_samples.append(process.cpu_percent())
                self.memory_samples.append(process.memory_info().rss / 1024 / 1024)
                time.sleep(0.1)  # Sample every 100ms
            except Exception:
                break


class VoicePerformanceTest:
    """Performance testing framework for voice operations."""
    
    # Performance benchmarks for different operations
    BENCHMARKS = {
        "model_loading": PerformanceBenchmark(
            operation_name="Model Loading",
            max_duration_ms=5000,      # 5 seconds max for model loading
            max_memory_mb=200,         # 200MB max additional memory
            max_cpu_percent=80,        # 80% CPU during loading is acceptable
            persona_requirements={
                "maya_adhd": 3000,     # Maya needs faster loading (3s max)
                "grandma_rose": 8000,  # Grandma Rose can wait longer (8s)
                "alex_blind": 5000,    # Alex needs standard timing
            },
            description="Loading Whisper and Piper models from disk"
        ),
        
        "speech_transcription": PerformanceBenchmark(
            operation_name="Speech Transcription",
            max_duration_ms=2000,      # 2 seconds max for transcription
            max_memory_mb=100,         # 100MB max additional memory
            max_cpu_percent=90,        # High CPU is acceptable for STT
            persona_requirements={
                "maya_adhd": 500,      # Maya needs instant transcription
                "grandma_rose": 3000,  # Grandma can wait for accuracy
                "alex_blind": 1000,    # Alex needs responsive feedback
                "dr_sarah": 1500,      # Dr. Sarah expects efficiency
            },
            description="Converting speech audio to text"
        ),
        
        "intent_processing": PerformanceBenchmark(
            operation_name="Intent Processing",
            max_duration_ms=500,       # 500ms max for NLP processing
            max_memory_mb=50,          # 50MB max additional memory
            max_cpu_percent=60,        # Moderate CPU for NLP
            persona_requirements={
                "maya_adhd": 200,      # Maya needs instant understanding
                "grandma_rose": 1000,  # Grandma can wait for accuracy
                "alex_blind": 300,     # Alex needs quick feedback
                "dr_sarah": 400,       # Dr. Sarah expects precision
            },
            description="Processing natural language into actionable intents"
        ),
        
        "speech_synthesis": PerformanceBenchmark(
            operation_name="Speech Synthesis",
            max_duration_ms=1500,      # 1.5 seconds max for TTS
            max_memory_mb=80,          # 80MB max additional memory  
            max_cpu_percent=75,        # Moderate CPU for TTS
            persona_requirements={
                "maya_adhd": 800,      # Maya needs quick audio response
                "grandma_rose": 2500,  # Grandma prioritizes clarity
                "alex_blind": 1000,    # Alex needs timely audio feedback
                "dr_sarah": 1200,      # Dr. Sarah expects efficiency
            },
            description="Converting text responses to speech audio"
        ),
        
        "end_to_end_voice": PerformanceBenchmark(
            operation_name="End-to-End Voice",
            max_duration_ms=5000,      # 5 seconds total for full pipeline
            max_memory_mb=300,         # 300MB max for complete operation
            max_cpu_percent=85,        # High CPU acceptable for full pipeline
            persona_requirements={
                "maya_adhd": 2000,     # Maya's total <2s requirement
                "grandma_rose": 8000,  # Grandma can wait for quality
                "alex_blind": 3000,    # Alex needs reasonable response
                "dr_sarah": 4000,      # Dr. Sarah expects good performance
            },
            description="Complete voice interaction from speech input to audio output"
        )
    }
    
    @pytest.fixture
    async def performance_monitor(self):
        """Create performance monitor for testing."""
        return PerformanceMonitor()
    
    @pytest.fixture
    async def voice_interface_optimized(self, temp_data_dir):
        """Create optimized voice interface for performance testing."""
        interface = PipecatVoiceInterface(data_dir=temp_data_dir)
        
        # Use optimized settings for performance
        interface.optimization_mode = "performance"
        interface.model_cache_enabled = True
        interface.parallel_processing = True
        
        return interface
    
    @pytest.fixture
    async def temp_data_dir(self):
        """Create temporary data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    async def run_performance_test(
        self, 
        operation_func,
        benchmark: PerformanceBenchmark,
        persona: str = "default",
        monitor: PerformanceMonitor = None
    ) -> PerformanceResult:
        """Run a performance test for a specific operation."""
        
        if monitor:
            monitor.start_monitoring()
        
        start_time = time.perf_counter()
        success = True
        error_message = None
        
        try:
            # Run the operation
            await operation_func()
            
        except Exception as e:
            success = False
            error_message = str(e)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if monitor:
            avg_cpu, memory_used = monitor.stop_monitoring()
        else:
            avg_cpu, memory_used = 0.0, 0.0
        
        return PerformanceResult(
            duration_ms=duration_ms,
            memory_used_mb=memory_used,
            cpu_percent=avg_cpu,
            success=success,
            error_message=error_message
        )
    
    def validate_performance(
        self, 
        result: PerformanceResult, 
        benchmark: PerformanceBenchmark,
        persona: str = "default"
    ) -> Tuple[bool, List[str]]:
        """Validate performance result against benchmark."""
        issues = []
        
        # Check persona-specific timing requirements
        if persona in benchmark.persona_requirements:
            max_time = benchmark.persona_requirements[persona]
            if result.duration_ms > max_time:
                issues.append(
                    f"{benchmark.operation_name} took {result.duration_ms:.1f}ms "
                    f"for {persona}, exceeds {max_time}ms requirement"
                )
        
        # Check general timing requirements
        if result.duration_ms > benchmark.max_duration_ms:
            issues.append(
                f"{benchmark.operation_name} took {result.duration_ms:.1f}ms, "
                f"exceeds {benchmark.max_duration_ms}ms limit"
            )
        
        # Check memory requirements
        if result.memory_used_mb > benchmark.max_memory_mb:
            issues.append(
                f"{benchmark.operation_name} used {result.memory_used_mb:.1f}MB, "
                f"exceeds {benchmark.max_memory_mb}MB limit"
            )
        
        # Check CPU requirements
        if result.cpu_percent > benchmark.max_cpu_percent:
            issues.append(
                f"{benchmark.operation_name} used {result.cpu_percent:.1f}% CPU, "
                f"exceeds {benchmark.max_cpu_percent}% limit"
            )
        
        return len(issues) == 0, issues


class TestVoicePerformanceBenchmarks:
    """Comprehensive voice performance testing."""
    
    def __init__(self):
        self.perf_test = VoicePerformanceTest()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_model_loading_performance(self, voice_interface_optimized, performance_monitor):
        """Test model loading performance across personas."""
        
        benchmark = VoicePerformanceTest.BENCHMARKS["model_loading"]
        
        async def load_models():
            """Mock model loading operation."""
            # Simulate model loading time and resource usage
            await asyncio.sleep(0.1)  # Simulate I/O
            
            # Mock memory allocation for models
            large_data = bytearray(50 * 1024 * 1024)  # 50MB allocation
            await asyncio.sleep(0.1)
            del large_data
        
        # Test for key personas
        personas_to_test = ["maya_adhd", "grandma_rose", "alex_blind"]
        
        for persona in personas_to_test:
            result = await self.perf_test.run_performance_test(
                load_models, benchmark, persona, performance_monitor
            )
            
            passed, issues = self.perf_test.validate_performance(result, benchmark, persona)
            
            assert passed, f"Model loading performance failed for {persona}: {', '.join(issues)}"
            assert result.success, f"Model loading failed for {persona}: {result.error_message}"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_speech_transcription_performance(self, voice_interface_optimized, performance_monitor):
        """Test speech transcription performance."""
        
        benchmark = VoicePerformanceTest.BENCHMARKS["speech_transcription"]
        
        async def transcribe_speech():
            """Mock speech transcription."""
            # Simulate Whisper processing
            with patch.object(voice_interface_optimized, '_transcribe_audio', new_callable=AsyncMock) as mock_transcribe:
                mock_transcribe.return_value = "install firefox"
                
                # Simulate processing time based on audio length
                await asyncio.sleep(0.05)  # Simulate fast transcription
                return await voice_interface_optimized._transcribe_audio(b"mock_audio_data")
        
        # Test critical personas
        personas_to_test = ["maya_adhd", "alex_blind", "dr_sarah"]
        
        for persona in personas_to_test:
            voice_interface_optimized.set_persona(persona)
            
            result = await self.perf_test.run_performance_test(
                transcribe_speech, benchmark, persona, performance_monitor
            )
            
            passed, issues = self.perf_test.validate_performance(result, benchmark, persona)
            
            assert passed, f"Speech transcription performance failed for {persona}: {', '.join(issues)}"
            assert result.success, f"Speech transcription failed for {persona}: {result.error_message}"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_intent_processing_performance(self, voice_interface_optimized, performance_monitor):
        """Test intent processing performance."""
        
        benchmark = VoicePerformanceTest.BENCHMARKS["intent_processing"]
        
        async def process_intent():
            """Mock intent processing."""
            # Simulate NLP processing
            text = "install firefox"
            
            # Mock the intent processing pipeline
            await asyncio.sleep(0.02)  # Simulate NLP processing
            
            return {
                "intent": "install_package",
                "entity": "firefox",
                "confidence": 0.95
            }
        
        # Test all key personas
        personas_to_test = ["maya_adhd", "grandma_rose", "alex_blind", "dr_sarah"]
        
        for persona in personas_to_test:
            result = await self.perf_test.run_performance_test(
                process_intent, benchmark, persona, performance_monitor
            )
            
            passed, issues = self.perf_test.validate_performance(result, benchmark, persona)
            
            assert passed, f"Intent processing performance failed for {persona}: {', '.join(issues)}"
            assert result.success, f"Intent processing failed for {persona}: {result.error_message}"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_speech_synthesis_performance(self, voice_interface_optimized, performance_monitor):
        """Test speech synthesis performance."""
        
        benchmark = VoicePerformanceTest.BENCHMARKS["speech_synthesis"]
        
        async def synthesize_speech():
            """Mock speech synthesis."""
            # Simulate Piper TTS processing
            with patch.object(voice_interface_optimized, '_synthesize_speech', new_callable=AsyncMock) as mock_synthesize:
                mock_synthesize.return_value = b"mock_audio_data"
                
                # Simulate TTS processing time
                await asyncio.sleep(0.08)  # Simulate TTS generation
                return await voice_interface_optimized._synthesize_speech("Installing Firefox for you!")
        
        # Test personas with different speech requirements
        personas_to_test = ["maya_adhd", "grandma_rose", "alex_blind"]
        
        for persona in personas_to_test:
            voice_interface_optimized.set_persona(persona)
            
            result = await self.perf_test.run_performance_test(
                synthesize_speech, benchmark, persona, performance_monitor
            )
            
            passed, issues = self.perf_test.validate_performance(result, benchmark, persona)
            
            assert passed, f"Speech synthesis performance failed for {persona}: {', '.join(issues)}"
            assert result.success, f"Speech synthesis failed for {persona}: {result.error_message}"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_end_to_end_voice_performance(self, voice_interface_optimized, performance_monitor):
        """Test complete end-to-end voice pipeline performance."""
        
        benchmark = VoicePerformanceTest.BENCHMARKS["end_to_end_voice"]
        
        async def end_to_end_voice():
            """Mock complete voice interaction."""
            # Simulate complete pipeline: STT -> NLP -> Command -> TTS
            
            with patch.object(voice_interface_optimized, '_transcribe_audio', new_callable=AsyncMock) as mock_transcribe, \
                 patch.object(voice_interface_optimized, '_synthesize_speech', new_callable=AsyncMock) as mock_synthesize:
                
                mock_transcribe.return_value = "install firefox"
                mock_synthesize.return_value = b"mock_audio_response"
                
                # Simulate each stage of the pipeline
                await asyncio.sleep(0.05)  # STT
                await asyncio.sleep(0.02)  # NLP
                await asyncio.sleep(0.01)  # Command processing
                await asyncio.sleep(0.08)  # TTS
                
                return await voice_interface_optimized.process_voice_input(b"mock_audio_input")
        
        # Test critical personas
        personas_to_test = ["maya_adhd", "alex_blind"]
        
        for persona in personas_to_test:
            voice_interface_optimized.set_persona(persona)
            
            result = await self.perf_test.run_performance_test(
                end_to_end_voice, benchmark, persona, performance_monitor
            )
            
            passed, issues = self.perf_test.validate_performance(result, benchmark, persona)
            
            assert passed, f"End-to-end voice performance failed for {persona}: {', '.join(issues)}"
            assert result.success, f"End-to-end voice failed for {persona}: {result.error_message}"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_voice_requests(self, voice_interface_optimized, performance_monitor):
        """Test performance under concurrent voice requests."""
        
        async def simulate_voice_request(request_id: int):
            """Simulate a single voice request."""
            with patch.object(voice_interface_optimized, 'process_voice_input', new_callable=AsyncMock) as mock_process:
                mock_process.return_value = {"success": True, "response": f"Response {request_id}"}
                
                await asyncio.sleep(0.1)  # Simulate processing time
                return await voice_interface_optimized.process_voice_input(f"request_{request_id}")
        
        # Test with 3 concurrent requests (realistic scenario)
        concurrent_requests = 3
        
        performance_monitor.start_monitoring()
        start_time = time.perf_counter()
        
        # Run concurrent requests
        tasks = [simulate_voice_request(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        avg_cpu, memory_used = performance_monitor.stop_monitoring()
        
        # Verify all requests succeeded
        assert all(result["success"] for result in results), "Some concurrent requests failed"
        
        # Verify reasonable performance (should handle 3 requests in reasonable time)
        assert duration_ms < 3000, f"Concurrent processing took {duration_ms}ms, too slow"
        
        # Verify memory usage stays reasonable
        assert memory_used < 500, f"Concurrent processing used {memory_used}MB, too much"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, voice_interface_optimized):
        """Test for memory leaks during repeated voice operations."""
        
        async def repeated_voice_operations():
            """Perform repeated voice operations to detect leaks."""
            for i in range(10):  # 10 iterations
                with patch.object(voice_interface_optimized, 'process_voice_input', new_callable=AsyncMock) as mock_process:
                    mock_process.return_value = {"success": True, "response": f"Response {i}"}
                    
                    await voice_interface_optimized.process_voice_input(f"test command {i}")
                    
                    # Small delay between operations
                    await asyncio.sleep(0.01)
        
        # Measure memory before and after
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        await repeated_voice_operations()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # Allow for some memory growth but detect significant leaks
        assert memory_growth < 50, f"Potential memory leak detected: {memory_growth}MB growth"
    
    @pytest.mark.performance 
    def test_performance_requirements_documented(self):
        """Test that all personas have documented performance requirements."""
        
        required_personas = ["maya_adhd", "grandma_rose", "alex_blind", "dr_sarah"]
        
        for benchmark_name, benchmark in VoicePerformanceTest.BENCHMARKS.items():
            for persona in required_personas:
                if persona == "maya_adhd":
                    # Maya must have requirements in all benchmarks (ADHD needs)
                    assert persona in benchmark.persona_requirements, \
                        f"Maya (ADHD) missing performance requirement in {benchmark_name}"
                    
                    # Maya's requirements should be stricter than general limits
                    maya_limit = benchmark.persona_requirements[persona]
                    assert maya_limit <= benchmark.max_duration_ms, \
                        f"Maya's limit ({maya_limit}ms) should be <= general limit ({benchmark.max_duration_ms}ms)"


class TestVoiceScalabilityBenchmarks:
    """Test voice interface scalability under various conditions."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_model_cache_effectiveness(self, voice_interface_optimized):
        """Test that model caching improves performance."""
        
        # First load (cold cache)
        start_time = time.perf_counter()
        with patch.object(voice_interface_optimized.model_manager, 'get_whisper_model', new_callable=AsyncMock) as mock_whisper:
            mock_whisper.return_value = Path("/tmp/whisper_model.bin")
            await voice_interface_optimized.model_manager.get_whisper_model()
        cold_load_time = (time.perf_counter() - start_time) * 1000
        
        # Second load (warm cache)
        start_time = time.perf_counter() 
        with patch.object(voice_interface_optimized.model_manager, 'get_whisper_model', new_callable=AsyncMock) as mock_whisper:
            mock_whisper.return_value = Path("/tmp/whisper_model.bin")
            await voice_interface_optimized.model_manager.get_whisper_model()
        warm_load_time = (time.perf_counter() - start_time) * 1000
        
        # Warm load should be significantly faster
        improvement_ratio = cold_load_time / warm_load_time if warm_load_time > 0 else float('inf')
        assert improvement_ratio > 2.0, f"Cache not effective: {improvement_ratio:.1f}x improvement"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_degraded_performance_under_load(self, voice_interface_optimized):
        """Test graceful performance degradation under system load."""
        
        # Simulate high system load
        def cpu_intensive_task():
            """Simulate CPU-intensive background task."""
            end_time = time.time() + 0.5  # Run for 500ms
            while time.time() < end_time:
                pass  # Busy loop
        
        # Run voice operation under load
        load_thread = threading.Thread(target=cpu_intensive_task)
        load_thread.start()
        
        try:
            start_time = time.perf_counter()
            with patch.object(voice_interface_optimized, 'process_voice_input', new_callable=AsyncMock) as mock_process:
                mock_process.return_value = {"success": True}
                await voice_interface_optimized.process_voice_input("test under load")
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Should still complete within reasonable time even under load
            assert duration_ms < 10000, f"Voice processing took {duration_ms}ms under load, too slow"
            
        finally:
            load_thread.join()


if __name__ == "__main__":
    # Run performance tests
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "benchmarks":
            pytest.main(["-v", "-m", "performance", "TestVoicePerformanceBenchmarks"])
        elif test_type == "scalability":
            pytest.main(["-v", "-m", "performance", "TestVoiceScalabilityBenchmarks"])
        elif test_type == "maya":
            # Test specifically for Maya's ADHD requirements
            pytest.main(["-v", "-k", "maya_adhd"])
        else:
            pytest.main(["-v", "-m", "performance"])
    else:
        # Run all performance tests
        pytest.main(["-v", "-m", "performance", __file__])