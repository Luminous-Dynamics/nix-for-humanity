"""
Unified Intent System - Single source of truth for all intent processing.

This consolidates functionality from:
- intent_pipeline.py
- intent_pipeline_enhanced.py  
- intent_factory.py
- intent_improvement.py
- intent_secure_wrapper.py
- intent_security.py
- secure_intent_integration.py
- llm_intent_recognizer.py

Philosophy: Simple intent recognition with built-in security and optional LLM enhancement.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ==================== Intent Types ====================

class IntentType(Enum):
    """All supported intent types."""
    # Package management
    SEARCH_PACKAGE = "search_package"
    INSTALL_PACKAGE = "install_package"
    REMOVE_PACKAGE = "remove_package"
    UPDATE_PACKAGE = "update_package"
    LIST_INSTALLED = "list_installed"
    CHECK_STATUS = "check_status"
    
    # System management
    UPDATE_SYSTEM = "update_system"
    REBUILD_SYSTEM = "rebuild_system"
    ROLLBACK_SYSTEM = "rollback_system"
    
    # Configuration
    GENERATE_CONFIG = "generate_config"
    EDIT_CONFIG = "edit_config"
    VALIDATE_CONFIG = "validate_config"
    
    # Advanced features
    MANAGE_FLAKE = "manage_flake"
    MANAGE_GENERATION = "manage_generation"
    HOME_MANAGER = "home_manager"
    
    # Discovery
    DISCOVER_PACKAGES = "discover_packages"
    DISCOVER_OPTIONS = "discover_options"
    
    # Information
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Unified intent representation."""
    type: IntentType
    raw_text: str
    confidence: float = 1.0
    entities: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    secure: bool = True  # Security validated
    

# ==================== Security Validation ====================

class SecurityValidator:
    """Validate intents for security issues."""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"(sudo\s+)?rm\s+-rf\s+/",  # Destructive commands (with or without sudo)
        r"mkfs",  # Filesystem formatting
        r"dd\s+if=.*of=/dev",  # Direct disk writes
        r";\s*rm",  # Command injection
        r"\|\s*rm",  # Pipe to rm
        r">`.*`",  # Command substitution
        r"\$\(.*\)",  # Command substitution
    ]
    
    # Suspicious but not always dangerous
    SUSPICIOUS_PATTERNS = [
        r"sudo",
        r"--force",
        r"--no-confirm",
        r"/etc/passwd",
        r"/etc/shadow",
    ]
    
    def validate(self, text: str) -> Tuple[bool, Optional[str]]:
        """Validate text for security issues.
        
        Returns:
            (is_safe, reason_if_not_safe)
        """
        text_lower = text.lower()
        
        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check suspicious patterns (warn but allow)
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Suspicious pattern in input: {pattern}")
        
        # Check for path traversal
        if "../" in text or "..\\" in text:
            return False, "Path traversal attempt detected"
        
        # Check for excessive length (DoS prevention)
        if len(text) > 1000:
            return False, "Input too long (max 1000 characters)"
        
        return True, None


# ==================== Intent Recognition ====================

class IntentRecognizer:
    """Recognize intents from natural language."""
    
    def __init__(self, use_llm: bool = False):
        """Initialize recognizer.
        
        Args:
            use_llm: Whether to use LLM for enhanced recognition
        """
        self.use_llm = use_llm
        self.security = SecurityValidator()
        self._init_patterns()
        
        # Optional LLM client
        self.llm_client = None
        if use_llm:
            self._init_llm()
    
    def _init_patterns(self):
        """Initialize recognition patterns."""
        self.patterns = {
            # Search patterns
            IntentType.SEARCH_PACKAGE: [
                r"search\s+(?:for\s+)?(.+)",
                r"find\s+(?:package\s+)?(.+)",
                r"look\s+for\s+(.+)",
                r"what\s+is\s+(.+)",
            ],
            
            # Install patterns
            IntentType.INSTALL_PACKAGE: [
                r"install\s+(.+)",
                r"add\s+(.+)",
                r"get\s+(.+)",
                r"setup\s+(.+)",
                r"i\s+want\s+(.+)",
            ],
            
            # Remove patterns
            IntentType.REMOVE_PACKAGE: [
                r"remove\s+(.+)",
                r"uninstall\s+(.+)",
                r"delete\s+(.+)",
                r"get\s+rid\s+of\s+(.+)",
            ],
            
            # List patterns
            IntentType.LIST_INSTALLED: [
                r"list(?:\s+installed)?",
                r"show\s+(?:installed\s+)?packages",
                r"what(?:'s|\s+is)\s+installed",
                r"my\s+packages",
            ],
            
            # Update patterns
            IntentType.UPDATE_SYSTEM: [
                r"update(?:\s+system)?",
                r"upgrade(?:\s+system)?",
                r"refresh\s+channels?",
            ],
            
            # Info patterns
            IntentType.CHECK_STATUS: [
                r"info(?:\s+about)?\s+(.+)",
                r"status\s+(?:of\s+)?(.+)",
                r"describe\s+(.+)",
                r"tell\s+me\s+about\s+(.+)",
            ],
            
            # Config patterns
            IntentType.GENERATE_CONFIG: [
                r"generate\s+(?:a\s+)?config(?:uration)?\s+(?:for\s+)?(.+)",
                r"create\s+(?:a\s+)?config(?:uration)?\s+(?:for\s+)?(.+)",
                r"make\s+(?:a\s+)?(.+)\s+config(?:uration)?",
            ],
            
            # Flake patterns
            IntentType.MANAGE_FLAKE: [
                r"flake\s+(.+)",
                r"init(?:ialize)?\s+flake",
                r"create\s+flake",
            ],
            
            # Help patterns
            IntentType.HELP: [
                r"help",
                r"what\s+can\s+you\s+do",
                r"how\s+do\s+i",
                r"show\s+commands?",
            ],
        }
    
    def _init_llm(self):
        """Initialize LLM client for enhanced recognition."""
        try:
            from luminous_nix.ai.ollama_integration import OllamaClient
            self.llm_client = OllamaClient()
            # Check if actually available
            if not self.llm_client.is_available():
                logger.info("LLM not available - will use pattern matching only")
                self.llm_client = None
        except ImportError:
            logger.info("LLM integration not installed - using pattern matching")
            self.llm_client = None
        except Exception as e:
            logger.warning(f"LLM initialization failed: {e}")
            self.llm_client = None
    
    def recognize(self, text: str, context: Optional[Dict] = None) -> Intent:
        """Recognize intent from text.
        
        Args:
            text: User input text
            context: Optional context for recognition
            
        Returns:
            Recognized Intent object
        """
        # Security validation first
        is_safe, reason = self.security.validate(text)
        if not is_safe:
            logger.warning(f"Security validation failed: {reason}")
            return Intent(
                type=IntentType.UNKNOWN,
                raw_text=text,
                confidence=0.0,
                secure=False,
                context={"security_reason": reason}
            )
        
        # Clean and normalize text
        text_clean = text.strip().lower()
        
        # Try pattern matching first
        intent = self._match_patterns(text_clean)
        
        # If no match and LLM available, try LLM (but don't block)
        if intent.type == IntentType.UNKNOWN and self.llm_client:
            # Try LLM with quick timeout
            import time
            start = time.time()
            llm_intent = self._llm_recognize(text_clean, context)
            elapsed = time.time() - start
            
            # Only use LLM result if it was fast and confident
            if elapsed < 5 and llm_intent.confidence > 0.6:
                intent = llm_intent
            elif elapsed > 5:
                logger.info(f"LLM took {elapsed:.1f}s - using pattern matching instead")
        
        # Add original text and context
        intent.raw_text = text
        if context:
            intent.context.update(context)
        
        return intent
    
    def _match_patterns(self, text: str) -> Intent:
        """Match text against patterns."""
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    entities = {}
                    
                    # Extract entity if captured
                    if match.groups():
                        entity = match.group(1).strip()
                        # Determine entity type based on intent
                        if "package" in intent_type.value:
                            entities["package"] = entity
                        elif "config" in intent_type.value:
                            entities["config_type"] = entity
                        else:
                            entities["target"] = entity
                    
                    return Intent(
                        type=intent_type,
                        raw_text=text,
                        confidence=0.9,  # High confidence for pattern match
                        entities=entities,
                        secure=True
                    )
        
        # No match found
        return Intent(
            type=IntentType.UNKNOWN,
            raw_text=text,
            confidence=0.0,
            secure=True
        )
    
    def _llm_recognize(self, text: str, context: Optional[Dict]) -> Intent:
        """Use LLM for intent recognition with graceful fallback."""
        if not self.llm_client:
            return Intent(type=IntentType.UNKNOWN, raw_text=text, confidence=0.0)
        
        try:
            # Prepare prompt
            prompt = f"""
Analyze this NixOS command and identify the intent:

User input: "{text}"

Identify:
1. Intent type (search, install, remove, list, update, config, help, unknown)
2. Package or target (if applicable)
3. Confidence (0-1)

Respond in format:
Intent: <type>
Target: <package or none>
Confidence: <0-1>
            """
            
            # Get LLM response
            response = self.llm_client.process_query(prompt)
            
            # Parse response
            intent_type = IntentType.UNKNOWN
            entities = {}
            confidence = 0.5
            
            # response is an OllamaResponse object
            if response and response.text:
                lines = response.text.split("\n")
            else:
                lines = []
            for line in lines:
                if "intent:" in line.lower():
                    type_str = line.split(":")[1].strip().lower()
                    # Map to IntentType
                    for itype in IntentType:
                        if type_str in itype.value:
                            intent_type = itype
                            break
                elif "target:" in line.lower():
                    target = line.split(":")[1].strip()
                    if target and target.lower() != "none":
                        entities["package"] = target
                elif "confidence:" in line.lower():
                    try:
                        confidence = float(line.split(":")[1].strip())
                    except ValueError:
                        pass
            
            return Intent(
                type=intent_type,
                raw_text=text,
                confidence=confidence,
                entities=entities,
                secure=True,
                context={"llm_enhanced": True}
            )
            
        except Exception as e:
            logger.error(f"LLM recognition failed: {e}")
            return Intent(type=IntentType.UNKNOWN, raw_text=text, confidence=0.0)


# ==================== Intent Pipeline ====================

class IntentPipeline:
    """Complete intent processing pipeline."""
    
    def __init__(self, use_llm: bool = False, enable_improvements: bool = True):
        """Initialize pipeline.
        
        Args:
            use_llm: Whether to use LLM for recognition
            enable_improvements: Whether to apply intent improvements
        """
        self.recognizer = IntentRecognizer(use_llm=use_llm)
        self.enable_improvements = enable_improvements
    
    def process(self, text: str, context: Optional[Dict] = None) -> Intent:
        """Process text through complete pipeline.
        
        Args:
            text: User input text
            context: Optional context
            
        Returns:
            Processed Intent
        """
        # Recognize intent
        intent = self.recognizer.recognize(text, context)
        
        # Apply improvements if enabled
        if self.enable_improvements and intent.type != IntentType.UNKNOWN:
            intent = self._improve_intent(intent)
        
        # Log for debugging
        logger.debug(f"Processed intent: {intent.type} (confidence: {intent.confidence})")
        
        return intent
    
    def _improve_intent(self, intent: Intent) -> Intent:
        """Apply improvements to recognized intent."""
        
        # Fix common typos in package names
        if "package" in intent.entities:
            package = intent.entities["package"]
            corrections = {
                "firefox": "firefox",
                "firfox": "firefox",
                "chrome": "chromium",
                "vscode": "vscodium",
                "code": "vscodium",
            }
            if package in corrections:
                intent.entities["package"] = corrections[package]
                intent.context["corrected"] = True
        
        # Add common aliases
        if intent.type == IntentType.INSTALL_PACKAGE:
            package = intent.entities.get("package", "")
            # Map common names to nix package names
            aliases = {
                "python": "python3",
                "node": "nodejs",
                "docker": "docker",
                "k8s": "kubernetes",
            }
            if package in aliases:
                intent.entities["package"] = aliases[package]
                intent.context["aliased"] = True
        
        return intent


# ==================== Convenience Functions ====================

def create_intent(text: str, use_llm: bool = False) -> Intent:
    """Convenience function to create intent from text."""
    pipeline = IntentPipeline(use_llm=use_llm)
    return pipeline.process(text)


def is_safe(text: str) -> bool:
    """Check if text is safe to process."""
    validator = SecurityValidator()
    is_safe, _ = validator.validate(text)
    return is_safe