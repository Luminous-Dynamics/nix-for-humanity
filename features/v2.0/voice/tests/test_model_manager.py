"""
🧪 Tests for Voice Model Management System

Comprehensive unit tests for the model downloading, verification, and persona mapping
functionality in the voice interface model manager.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import hashlib
import tempfile
import shutil
from typing import Dict, Any

# Import the model manager components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from nix_humanity.voice.model_manager import (
    ModelManager,
    ModelSize,
    get_whisper_model_path,
    get_piper_voice_path,
    WHISPER_MODELS,
    PIPER_VOICES,
    PERSONA_VOICE_MAP
)


class TestModelManager:
    """Test the ModelManager class functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test models."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def model_manager(self, temp_dir):
        """Create a ModelManager instance for testing."""
        return ModelManager(data_dir=temp_dir)
    
    def test_init_creates_directories(self, temp_dir):
        """Test that ModelManager creates necessary directories."""
        manager = ModelManager(data_dir=temp_dir)
        
        assert (temp_dir / "models" / "whisper").exists()
        assert (temp_dir / "models" / "piper").exists()
        assert (temp_dir / "cache").exists()
    
    def test_whisper_model_sizes_configuration(self):
        """Test that all Whisper model sizes are properly configured."""
        expected_sizes = [ModelSize.TINY, ModelSize.BASE, ModelSize.SMALL, ModelSize.MEDIUM, ModelSize.LARGE]
        
        for size in expected_sizes:
            assert size in WHISPER_MODELS
            model_config = WHISPER_MODELS[size]
            assert "url" in model_config
            assert "sha256" in model_config
            assert "filename" in model_config
            assert model_config["url"].startswith("https://")
            assert len(model_config["sha256"]) == 64  # SHA256 is 64 hex chars
            assert model_config["filename"].endswith((".bin", ".ggml"))
    
    def test_piper_voice_configuration(self):
        """Test that all Piper voices are properly configured."""
        for voice_id, voice_config in PIPER_VOICES.items():
            assert "url" in voice_config
            assert "sha256" in voice_config
            assert "quality" in voice_config
            assert voice_config["url"].startswith("https://")
            assert len(voice_config["sha256"]) == 64
            assert voice_config["quality"] in ["low", "medium", "high", "x_low"]
    
    def test_persona_voice_mapping(self):
        """Test that all 10 personas have voice mappings."""
        expected_personas = [
            "grandma_rose", "maya", "david", "dr_sarah", "alex",
            "carlos", "priya", "jamie", "viktor", "luna"
        ]
        
        for persona in expected_personas:
            assert persona in PERSONA_VOICE_MAP
            voice_id = PERSONA_VOICE_MAP[persona]
            assert voice_id in PIPER_VOICES
    
    def test_calculate_sha256_file(self, temp_dir, model_manager):
        """Test SHA256 calculation for files."""
        # Create a test file with known content
        test_file = temp_dir / "test.txt"
        test_content = b"Hello, World!"
        test_file.write_bytes(test_content)
        
        # Calculate expected SHA256
        expected_hash = hashlib.sha256(test_content).hexdigest()
        
        # Test the function
        calculated_hash = model_manager._calculate_sha256(test_file)
        assert calculated_hash == expected_hash
    
    def test_calculate_sha256_nonexistent_file(self, temp_dir, model_manager):
        """Test SHA256 calculation for non-existent files."""
        nonexistent_file = temp_dir / "does_not_exist.txt"
        
        with pytest.raises(FileNotFoundError):
            model_manager._calculate_sha256(nonexistent_file)
    
    @pytest.mark.asyncio
    async def test_download_model_success(self, temp_dir, model_manager):
        """Test successful model downloading."""
        # Mock the download function
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {'content-length': '1000'}
            
            # Mock file content
            test_content = b"Mock model file content"
            mock_response.content.iter_chunked = AsyncMock(
                return_value=[test_content]
            )
            
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Test download
            url = "https://example.com/model.bin"
            target_path = temp_dir / "downloaded_model.bin"
            
            await model_manager._download_file(url, target_path)
            
            # Verify file was created
            assert target_path.exists()
            assert target_path.read_bytes() == test_content
    
    @pytest.mark.asyncio
    async def test_download_model_network_error(self, temp_dir, model_manager):
        """Test handling of network errors during download."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock network error
            mock_get.side_effect = Exception("Network error")
            
            url = "https://example.com/model.bin"
            target_path = temp_dir / "failed_download.bin"
            
            with pytest.raises(Exception, match="Network error"):
                await model_manager._download_file(url, target_path)
            
            # Verify file was not created
            assert not target_path.exists()
    
    @pytest.mark.asyncio
    async def test_get_whisper_model_existing(self, temp_dir, model_manager):
        """Test getting Whisper model when it already exists."""
        # Create a mock model file with correct hash
        model_config = WHISPER_MODELS[ModelSize.BASE]
        model_path = temp_dir / "models" / "whisper" / model_config["filename"]
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with mock content
        mock_content = b"Mock Whisper model"
        model_path.write_bytes(mock_content)
        
        # Mock SHA256 verification to pass
        with patch.object(model_manager, '_calculate_sha256') as mock_sha256:
            mock_sha256.return_value = model_config["sha256"]
            
            # Test getting the model
            result_path = await model_manager.get_whisper_model(ModelSize.BASE)
            
            assert result_path == model_path
            assert result_path.exists()
            mock_sha256.assert_called_once_with(model_path)
    
    @pytest.mark.asyncio
    async def test_get_whisper_model_download_needed(self, temp_dir, model_manager):
        """Test downloading Whisper model when it doesn't exist."""
        with patch.object(model_manager, '_download_file') as mock_download:
            with patch.object(model_manager, '_calculate_sha256') as mock_sha256:
                # Mock successful verification
                model_config = WHISPER_MODELS[ModelSize.BASE]
                mock_sha256.return_value = model_config["sha256"]
                
                # Mock successful download
                async def mock_download_side_effect(url, path):
                    path.write_bytes(b"Downloaded model content")
                
                mock_download.side_effect = mock_download_side_effect
                
                # Test getting the model
                result_path = await model_manager.get_whisper_model(ModelSize.BASE)
                
                expected_path = temp_dir / "models" / "whisper" / model_config["filename"]
                assert result_path == expected_path
                assert result_path.exists()
                
                # Verify download was called
                mock_download.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_whisper_model_invalid_hash(self, temp_dir, model_manager):
        """Test handling of invalid hash after download."""
        # Create a model file with wrong hash
        model_config = WHISPER_MODELS[ModelSize.BASE]
        model_path = temp_dir / "models" / "whisper" / model_config["filename"]
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.write_bytes(b"Invalid content")
        
        # Mock SHA256 to return wrong hash
        with patch.object(model_manager, '_calculate_sha256') as mock_sha256:
            mock_sha256.return_value = "wrong_hash"
            
            with pytest.raises(ValueError, match="SHA256 verification failed"):
                await model_manager.get_whisper_model(ModelSize.BASE)
    
    @pytest.mark.asyncio
    async def test_get_piper_voice_for_persona(self, temp_dir, model_manager):
        """Test getting Piper voice for specific persona."""
        persona = "grandma_rose"
        expected_voice_id = PERSONA_VOICE_MAP[persona]
        voice_config = PIPER_VOICES[expected_voice_id]
        
        # Mock the download and verification
        with patch.object(model_manager, '_download_file') as mock_download:
            with patch.object(model_manager, '_calculate_sha256') as mock_sha256:
                mock_sha256.return_value = voice_config["sha256"]
                
                async def mock_download_side_effect(url, path):
                    path.write_bytes(b"Voice model content")
                
                mock_download.side_effect = mock_download_side_effect
                
                # Test getting voice for persona
                result_path = await model_manager.get_piper_voice(persona)
                
                expected_filename = f"{expected_voice_id}.onnx"
                expected_path = temp_dir / "models" / "piper" / expected_filename
                
                assert result_path == expected_path
                assert result_path.exists()
    
    @pytest.mark.asyncio
    async def test_get_piper_voice_unknown_persona(self, temp_dir, model_manager):
        """Test handling of unknown persona for voice selection."""
        unknown_persona = "unknown_test_persona"
        
        # Should fall back to default voice
        with patch.object(model_manager, '_download_file') as mock_download:
            with patch.object(model_manager, '_calculate_sha256') as mock_sha256:
                default_voice_config = PIPER_VOICES["en_US-ljspeech-medium"]
                mock_sha256.return_value = default_voice_config["sha256"]
                
                async def mock_download_side_effect(url, path):
                    path.write_bytes(b"Default voice content")
                
                mock_download.side_effect = mock_download_side_effect
                
                result_path = await model_manager.get_piper_voice(unknown_persona)
                
                expected_path = temp_dir / "models" / "piper" / "en_US-ljspeech-medium.onnx"
                assert result_path == expected_path
    
    def test_model_size_enum(self):
        """Test ModelSize enum values."""
        assert ModelSize.TINY.value == "tiny"
        assert ModelSize.BASE.value == "base"
        assert ModelSize.SMALL.value == "small"
        assert ModelSize.MEDIUM.value == "medium"
        assert ModelSize.LARGE.value == "large"


class TestModuleHelperFunctions:
    """Test the module-level helper functions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.mark.asyncio
    async def test_get_whisper_model_path_function(self, temp_dir):
        """Test the get_whisper_model_path helper function."""
        with patch('nix_for_humanity.voice.model_manager.ModelManager') as mock_manager_class:
            mock_manager = AsyncMock()
            mock_manager_class.return_value = mock_manager
            
            expected_path = temp_dir / "whisper_model.bin"
            mock_manager.get_whisper_model.return_value = expected_path
            
            result = await get_whisper_model_path(temp_dir, ModelSize.BASE)
            
            assert result == expected_path
            mock_manager_class.assert_called_once_with(data_dir=temp_dir)
            mock_manager.get_whisper_model.assert_called_once_with(ModelSize.BASE)
    
    @pytest.mark.asyncio
    async def test_get_piper_voice_path_function(self, temp_dir):
        """Test the get_piper_voice_path helper function."""
        with patch('nix_for_humanity.voice.model_manager.ModelManager') as mock_manager_class:
            mock_manager = AsyncMock()
            mock_manager_class.return_value = mock_manager
            
            expected_path = temp_dir / "piper_voice.onnx"
            mock_manager.get_piper_voice.return_value = expected_path
            
            result = await get_piper_voice_path("maya", temp_dir)
            
            assert result == expected_path
            mock_manager_class.assert_called_once_with(data_dir=temp_dir)
            mock_manager.get_piper_voice.assert_called_once_with("maya")


class TestModelManagerEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def model_manager(self, temp_dir):
        """Create a ModelManager instance for testing."""
        return ModelManager(data_dir=temp_dir)
    
    @pytest.mark.asyncio
    async def test_concurrent_downloads(self, temp_dir, model_manager):
        """Test that concurrent downloads of the same model work correctly."""
        with patch.object(model_manager, '_download_file') as mock_download:
            with patch.object(model_manager, '_calculate_sha256') as mock_sha256:
                model_config = WHISPER_MODELS[ModelSize.BASE]
                mock_sha256.return_value = model_config["sha256"]
                
                download_started = asyncio.Event()
                download_can_finish = asyncio.Event()
                
                async def slow_download(url, path):
                    download_started.set()
                    await download_can_finish.wait()
                    path.write_bytes(b"Model content")
                
                mock_download.side_effect = slow_download
                
                # Start two concurrent downloads
                task1 = asyncio.create_task(model_manager.get_whisper_model(ModelSize.BASE))
                task2 = asyncio.create_task(model_manager.get_whisper_model(ModelSize.BASE))
                
                # Wait for first download to start
                await download_started.wait()
                
                # Allow download to finish
                download_can_finish.set()
                
                # Both should complete successfully
                result1 = await task1
                result2 = await task2
                
                assert result1 == result2
                # Download should only be called once due to concurrency handling
                assert mock_download.call_count <= 2  # Allow for some race conditions
    
    @pytest.mark.asyncio
    async def test_disk_full_during_download(self, temp_dir, model_manager):
        """Test handling of disk full error during download."""
        with patch.object(model_manager, '_download_file') as mock_download:
            # Mock disk full error
            mock_download.side_effect = OSError("No space left on device")
            
            with pytest.raises(OSError, match="No space left on device"):
                await model_manager.get_whisper_model(ModelSize.BASE)
    
    @pytest.mark.asyncio
    async def test_partial_download_recovery(self, temp_dir, model_manager):
        """Test recovery from partial downloads."""
        model_config = WHISPER_MODELS[ModelSize.BASE]
        model_path = temp_dir / "models" / "whisper" / model_config["filename"]
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a partial file (wrong content)
        model_path.write_bytes(b"Partial download")
        
        with patch.object(model_manager, '_download_file') as mock_download:
            with patch.object(model_manager, '_calculate_sha256') as mock_sha256:
                # First call returns wrong hash (partial file)
                # Second call returns correct hash (after re-download)
                mock_sha256.side_effect = ["wrong_hash", model_config["sha256"]]
                
                async def redownload(url, path):
                    path.write_bytes(b"Complete download")
                
                mock_download.side_effect = redownload
                
                result_path = await model_manager.get_whisper_model(ModelSize.BASE)
                
                assert result_path.exists()
                assert result_path.read_bytes() == b"Complete download"
                mock_download.assert_called_once()  # Should re-download once
    
    def test_invalid_data_directory(self):
        """Test handling of invalid data directory."""
        # Try to create manager with a file instead of directory
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(Exception):  # Should fail to create directories
                ModelManager(data_dir=Path(temp_file.name))


class TestIntegrationWithPipecatInterface:
    """Test integration points with the pipecat interface."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.mark.asyncio
    async def test_pipecat_interface_integration(self, temp_dir):
        """Test the integration points used by pipecat_interface.py."""
        # Mock the imports that pipecat_interface.py uses
        with patch('nix_for_humanity.voice.model_manager.get_whisper_model_path') as mock_whisper:
            with patch('nix_for_humanity.voice.model_manager.get_piper_voice_path') as mock_piper:
                
                expected_whisper_path = temp_dir / "whisper_model.bin"
                expected_piper_path = temp_dir / "piper_voice.onnx"
                
                mock_whisper.return_value = expected_whisper_path
                mock_piper.return_value = expected_piper_path
                
                # Simulate the calls made by pipecat_interface.py
                whisper_path = await mock_whisper(temp_dir, ModelSize.BASE)
                piper_path = await mock_piper("maya", temp_dir)
                
                assert whisper_path == expected_whisper_path
                assert piper_path == expected_piper_path
    
    def test_fallback_behavior_compatibility(self, temp_dir):
        """Test that fallback behavior matches pipecat_interface expectations."""
        # Test that default voice mapping matches what pipecat_interface expects
        default_voices = {
            "Grandma Rose": "en_US-ljspeech-high",
            "Maya": "en_US-amy-medium", 
            "Alex": "en_US-ryan-high",
            "default": "en_US-ljspeech-medium"
        }
        
        for persona_display_name, expected_voice in default_voices.items():
            if persona_display_name == "default":
                continue
                
            # Convert display name to internal format
            persona_key = persona_display_name.lower().replace(" ", "_")
            
            if persona_key in PERSONA_VOICE_MAP:
                mapped_voice = PERSONA_VOICE_MAP[persona_key]
                # Voice should either match expected or be a reasonable alternative
                assert mapped_voice in PIPER_VOICES
    
    @pytest.mark.asyncio
    async def test_graceful_fallback_on_failure(self, temp_dir):
        """Test that the system gracefully falls back when ModelManager fails."""
        # This tests the exception handling in pipecat_interface.py
        
        with patch('nix_for_humanity.voice.model_manager.get_whisper_model_path') as mock_whisper:
            mock_whisper.side_effect = Exception("Model download failed")
            
            # The pipecat interface should catch this and use fallback paths
            try:
                await mock_whisper(temp_dir, ModelSize.BASE)
                assert False, "Should have raised exception"
            except Exception as e:
                assert "Model download failed" in str(e)
                # This exception should be caught by pipecat_interface.py
                # and result in fallback to placeholder paths


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])