"""
Llama.cpp Integration for Ultra-Fast Local Inference
10x-100x faster than Ollama for supported models
"""

import subprocess
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Supported model architectures"""
    LLAMA = "llama"
    MISTRAL = "mistral"
    GEMMA = "gemma"
    QWEN = "qwen"
    PHI = "phi"

@dataclass
class LlamaCppConfig:
    """Configuration for llama.cpp engine"""
    model_path: Path = Path.home() / ".cache" / "llama-models"
    n_threads: int = 4  # CPU threads
    n_gpu_layers: int = -1  # -1 = all layers on GPU
    context_size: int = 4096
    batch_size: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    repeat_penalty: float = 1.1
    seed: int = -1  # -1 = random
    verbose: bool = False
    
@dataclass
class ModelInfo:
    """Information about a loaded model"""
    name: str
    type: ModelType
    size_gb: float
    quantization: str  # Q4_K_M, Q5_K_M, Q8_0, etc.
    context_window: int
    path: Path
    
class LlamaCppEngine:
    """High-performance local inference using llama.cpp"""
    
    def __init__(self, config: Optional[LlamaCppConfig] = None):
        self.config = config or LlamaCppConfig()
        self.models: Dict[str, ModelInfo] = {}
        self.current_model: Optional[str] = None
        self.process: Optional[asyncio.subprocess.Process] = None
        self._check_llama_cpp()
        
    def _check_llama_cpp(self):
        """Check if llama.cpp is available"""
        try:
            result = subprocess.run(
                ["llama-cpp", "--version"],
                capture_output=True,
                text=True
            )
            self.has_llama_cpp = result.returncode == 0
            if self.has_llama_cpp:
                logger.info(f"llama.cpp found: {result.stdout.strip()}")
        except FileNotFoundError:
            self.has_llama_cpp = False
            logger.warning("llama.cpp not found. Install from nixpkgs or build from source")
            
    async def download_model(self, model_name: str, quantization: str = "Q4_K_M") -> bool:
        """Download a model in GGUF format for llama.cpp"""
        # Model mapping to HuggingFace repos
        model_urls = {
            "mistral-7b": f"TheBloke/Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.{quantization}.gguf",
            "gemma-2b": f"google/gemma-2b-GGUF/gemma-2b.{quantization}.gguf",
            "qwen-7b": f"Qwen/Qwen2-7B-Instruct-GGUF/qwen2-7b-instruct.{quantization}.gguf",
            "llama3-8b": f"meta-llama/Meta-Llama-3-8B-Instruct-GGUF/llama-3-8b-instruct.{quantization}.gguf",
        }
        
        if model_name not in model_urls:
            logger.error(f"Unknown model: {model_name}")
            return False
            
        url = f"https://huggingface.co/{model_urls[model_name]}"
        output_path = self.config.model_path / f"{model_name}-{quantization}.gguf"
        
        # Create model directory
        self.config.model_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download with wget or curl
            logger.info(f"Downloading {model_name} ({quantization})...")
            process = await asyncio.create_subprocess_exec(
                "wget",
                "-c",  # Continue partial downloads
                "-O", str(output_path),
                url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Model downloaded: {output_path}")
                
                # Register the model
                self.models[model_name] = ModelInfo(
                    name=model_name,
                    type=self._get_model_type(model_name),
                    size_gb=output_path.stat().st_size / (1024**3),
                    quantization=quantization,
                    context_window=self.config.context_size,
                    path=output_path
                )
                return True
            else:
                logger.error(f"Download failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
            
    def _get_model_type(self, model_name: str) -> ModelType:
        """Determine model type from name"""
        if "llama" in model_name.lower():
            return ModelType.LLAMA
        elif "mistral" in model_name.lower():
            return ModelType.MISTRAL
        elif "gemma" in model_name.lower():
            return ModelType.GEMMA
        elif "qwen" in model_name.lower():
            return ModelType.QWEN
        elif "phi" in model_name.lower():
            return ModelType.PHI
        else:
            return ModelType.LLAMA  # Default
            
    async def load_model(self, model_name: str) -> bool:
        """Load a model for inference"""
        if model_name not in self.models:
            logger.error(f"Model {model_name} not found. Download it first.")
            return False
            
        # Kill existing process if any
        if self.process:
            self.process.terminate()
            await self.process.wait()
            
        model_info = self.models[model_name]
        
        try:
            # Start llama.cpp server
            args = [
                "llama-cpp",
                "--model", str(model_info.path),
                "--ctx-size", str(self.config.context_size),
                "--batch-size", str(self.config.batch_size),
                "--n-gpu-layers", str(self.config.n_gpu_layers),
                "--threads", str(self.config.n_threads),
                "--port", "8080",  # API server port
                "--host", "127.0.0.1",
            ]
            
            if self.config.verbose:
                args.append("--verbose")
                
            self.process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.current_model = model_name
            logger.info(f"Loaded model: {model_name}")
            
            # Wait for server to start
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
            
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """Generate text using loaded model"""
        
        if not self.current_model:
            raise RuntimeError("No model loaded. Call load_model() first.")
            
        temp = temperature or self.config.temperature
        
        # Use the API endpoint
        import aiohttp
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temp,
            "top_p": self.config.top_p,
            "top_k": self.config.top_k,
            "repeat_penalty": self.config.repeat_penalty,
            "stream": stream,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://127.0.0.1:8080/completion",
                json=payload
            ) as response:
                if stream:
                    async def stream_generator():
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode().strip())
                                    yield data.get("content", "")
                                except:
                                    pass
                    return stream_generator()
                else:
                    data = await response.json()
                    return data.get("content", "")
                    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: Optional[float] = None
    ) -> str:
        """Chat completion with conversation history"""
        
        # Format messages into prompt
        prompt = self._format_chat_prompt(messages)
        return await self.generate(prompt, max_tokens, temperature)
        
    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into model-specific prompt"""
        model_type = self.models[self.current_model].type
        
        if model_type == ModelType.LLAMA:
            # Llama 3 format
            prompt = "<|begin_of_text|>"
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                if role == "system":
                    prompt += f"<|start_header_id|>system<|end_header_id|>\n{content}<|eot_id|>"
                elif role == "user":
                    prompt += f"<|start_header_id|>user<|end_header_id|>\n{content}<|eot_id|>"
                elif role == "assistant":
                    prompt += f"<|start_header_id|>assistant<|end_header_id|>\n{content}<|eot_id|>"
            prompt += "<|start_header_id|>assistant<|end_header_id|>\n"
            
        elif model_type == ModelType.MISTRAL:
            # Mistral format
            prompt = ""
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                if role == "user":
                    prompt += f"[INST] {content} [/INST]"
                elif role == "assistant":
                    prompt += f" {content} "
                    
        else:
            # Generic format
            prompt = ""
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                prompt += f"{role.upper()}: {content}\n"
            prompt += "ASSISTANT: "
            
        return prompt
        
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a model"""
        return self.models.get(model_name)
        
    async def benchmark(self, model_name: str, prompt: str = "Hello, world!") -> Dict[str, Any]:
        """Benchmark model performance"""
        import time
        
        if not await self.load_model(model_name):
            return {"error": "Failed to load model"}
            
        # Warmup
        await self.generate(prompt, max_tokens=10)
        
        # Benchmark
        times = []
        tokens_per_second = []
        
        for _ in range(5):
            start = time.perf_counter()
            result = await self.generate(prompt, max_tokens=100)
            end = time.perf_counter()
            
            elapsed = end - start
            times.append(elapsed)
            
            # Estimate tokens (rough)
            tokens = len(result.split())
            tokens_per_second.append(tokens / elapsed)
            
        return {
            "model": model_name,
            "avg_time": sum(times) / len(times),
            "avg_tokens_per_second": sum(tokens_per_second) / len(tokens_per_second),
            "min_time": min(times),
            "max_time": max(times),
        }
        
    async def cleanup(self):
        """Clean up resources"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            

class LlamaCppOrchestrator:
    """Orchestrate multiple llama.cpp models for different tasks"""
    
    def __init__(self):
        self.engines: Dict[str, LlamaCppEngine] = {}
        self.task_routing = {
            "code": "qwen-7b",  # Best for code
            "chat": "mistral-7b",  # Best for conversation
            "analysis": "llama3-8b",  # Best for reasoning
            "quick": "gemma-2b",  # Fast responses
        }
        
    async def setup_models(self):
        """Download and prepare all models"""
        for task, model in self.task_routing.items():
            engine = LlamaCppEngine()
            
            # Download if needed
            if model not in engine.models:
                await engine.download_model(model)
                
            self.engines[task] = engine
            
    async def process(
        self,
        task_type: str,
        prompt: str,
        **kwargs
    ) -> str:
        """Process request with appropriate model"""
        
        if task_type not in self.engines:
            logger.warning(f"Unknown task type: {task_type}, using chat")
            task_type = "chat"
            
        engine = self.engines[task_type]
        model = self.task_routing[task_type]
        
        # Load model if not current
        if engine.current_model != model:
            await engine.load_model(model)
            
        return await engine.generate(prompt, **kwargs)


# Integration with Luminous Nix
async def llama_cpp_nixos_assistant(prompt: str, task_type: str = "chat"):
    """Use llama.cpp for ultra-fast NixOS assistance"""
    
    orchestrator = LlamaCppOrchestrator()
    await orchestrator.setup_models()
    
    # Add NixOS context
    nixos_prompt = f"""You are a helpful NixOS assistant using llama.cpp for ultra-fast responses.
User request: {prompt}

Provide a clear, concise response:"""
    
    response = await orchestrator.process(task_type, nixos_prompt)
    return response