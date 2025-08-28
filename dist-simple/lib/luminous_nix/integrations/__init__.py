"""
Enhanced Integrations for Luminous Nix
Bringing together voice, LLMs, memory, and developer tools
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Try importing each integration
try:
    from ..voice.unified_voice import UnifiedVoiceSystem, VoiceConfig
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False
    logger.debug("Voice integration not available")

try:
    from .llama_cpp_engine import LlamaCppEngine, LlamaCppConfig, LlamaCppOrchestrator
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False
    logger.debug("Llama.cpp integration not available")

try:
    from .faiss_memory import FAISSMemoryStore, SemanticLearningSystem, NixOSKnowledgeBase
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logger.debug("FAISS memory not available")

try:
    from .dev_tools import AsciinemaRecorder, GumInterface, CharmFreeze, VHSRecorder, DemoOrchestrator
    HAS_DEV_TOOLS = True
except ImportError:
    HAS_DEV_TOOLS = False
    logger.debug("Developer tools not available")

try:
    from .code_quality import CodeQualityOrchestrator, RuffLinter, MyPyChecker, BanditScanner
    HAS_CODE_QUALITY = True
except ImportError:
    HAS_CODE_QUALITY = False
    logger.debug("Code quality tools not available")


class EnhancedIntegrationHub:
    """Central hub for all enhanced integrations"""
    
    def __init__(self):
        self.voice: Optional[UnifiedVoiceSystem] = None
        self.llama: Optional[LlamaCppEngine] = None
        self.memory: Optional[FAISSMemoryStore] = None
        self.knowledge: Optional[NixOSKnowledgeBase] = None
        self.demo: Optional[DemoOrchestrator] = None
        self.quality: Optional[CodeQualityOrchestrator] = None
        
        self._initialize_integrations()
        
    def _initialize_integrations(self):
        """Initialize available integrations"""
        
        if HAS_VOICE:
            self.voice = UnifiedVoiceSystem()
            logger.info("✅ Voice integration initialized")
            
        if HAS_LLAMA_CPP:
            self.llama = LlamaCppEngine()
            logger.info("✅ Llama.cpp integration initialized")
            
        if HAS_FAISS:
            self.memory = FAISSMemoryStore()
            self.knowledge = NixOSKnowledgeBase()
            logger.info("✅ FAISS memory initialized")
            
        if HAS_DEV_TOOLS:
            self.demo = DemoOrchestrator()
            logger.info("✅ Developer tools initialized")
            
        if HAS_CODE_QUALITY:
            self.quality = CodeQualityOrchestrator()
            logger.info("✅ Code quality tools initialized")
            
    def get_status(self) -> Dict[str, bool]:
        """Get status of all integrations"""
        return {
            "voice": self.voice is not None,
            "llama_cpp": self.llama is not None,
            "semantic_memory": self.memory is not None,
            "knowledge_base": self.knowledge is not None,
            "demo_tools": self.demo is not None,
            "code_quality": self.quality is not None,
        }
        
    async def process_with_enhancements(
        self,
        query: str,
        use_voice: bool = False,
        use_fast_llm: bool = False,
        use_memory: bool = True
    ) -> Dict[str, Any]:
        """Process query using enhanced features"""
        
        result = {
            "query": query,
            "response": "",
            "enhancements_used": []
        }
        
        # Voice input processing
        if use_voice and self.voice:
            # In real use, would capture from microphone
            result["enhancements_used"].append("voice")
            
        # Check memory for similar queries
        if use_memory and self.knowledge:
            answer = self.knowledge.find_answer(query)
            if answer:
                result["response"] = answer
                result["enhancements_used"].append("memory")
                return result
                
        # Use fast LLM if requested
        if use_fast_llm and self.llama:
            # Would need model loaded
            result["enhancements_used"].append("llama_cpp")
            # response = await self.llama.generate(query)
            # result["response"] = response
            
        # Voice output if enabled
        if use_voice and self.voice and result["response"]:
            await self.voice.speak(result["response"])
            result["enhancements_used"].append("voice_output")
            
        return result


# Singleton instance
_hub: Optional[EnhancedIntegrationHub] = None

def get_integration_hub() -> EnhancedIntegrationHub:
    """Get or create the integration hub"""
    global _hub
    if _hub is None:
        _hub = EnhancedIntegrationHub()
    return _hub


# Export main classes
__all__ = [
    # Hub
    "EnhancedIntegrationHub",
    "get_integration_hub",
    
    # Voice
    "UnifiedVoiceSystem",
    "VoiceConfig",
    "VoicePersonaAdapter",
    
    # LLM
    "LlamaCppEngine",
    "LlamaCppConfig",
    "LlamaCppOrchestrator",
    
    # Memory
    "FAISSMemoryStore",
    "SemanticLearningSystem",
    "NixOSKnowledgeBase",
    
    # Dev Tools
    "AsciinemaRecorder",
    "GumInterface",
    "CharmFreeze",
    "VHSRecorder",
    "DemoOrchestrator",
    
    # Code Quality
    "CodeQualityOrchestrator",
    "RuffLinter",
    "MyPyChecker",
    "BanditScanner",
    
    # Status flags
    "HAS_VOICE",
    "HAS_LLAMA_CPP",
    "HAS_FAISS",
    "HAS_DEV_TOOLS",
    "HAS_CODE_QUALITY",
]