"""Security and validation layer for intent recognition.

This module provides:
1. Input validation and sanitization
2. Adversarial input detection
3. Coherence checking
4. Rate limiting
5. Security logging
"""

import re
import time
import hashlib
import logging
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from collections import deque, Counter
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classification for inputs."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    NONSENSE = "nonsense"
    SPAM = "spam"


@dataclass
class SecurityAssessment:
    """Security assessment of user input."""
    threat_level: ThreatLevel
    confidence: float  # 0.0 - 1.0
    coherence: float  # 0.0 - 1.0
    is_safe: bool
    reason: Optional[str] = None
    sanitized_text: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class InputValidator:
    """Validates and sanitizes user input for safety."""
    
    # Maximum input length (prevent DoS)
    MAX_LENGTH = 500
    
    # Minimum coherent word length
    MIN_WORD_LENGTH = 2
    
    # Maximum word length (likely garbage)
    MAX_WORD_LENGTH = 50
    
    # Suspicious patterns that might indicate attacks
    SUSPICIOUS_PATTERNS = [
        # Command injection attempts
        r'(?:^|[;&|])\s*(?:rm|dd|mkfs|chmod|chown)\s+-[rf]',  # Dangerous commands with flags
        r';\s*rm\s+-rf',  # Specific rm -rf pattern
        r'>\s*/dev/(?:null|zero|random)',
        r'\$\([^)]+\)',  # Command substitution
        r'`[^`]+`',  # Backtick execution
        
        # Path traversal
        r'\.\./',
        r'/etc/(?:passwd|shadow)',
        r'/proc/self',
        
        # SQL injection patterns
        r"(?:';|--|\bOR\b.*=|UNION\s+SELECT)",
        
        # Script injection
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers
        
        # Format string attacks
        r'%[0-9]*[xsdp]',
        r'\{[0-9]+\}',
    ]
    
    # Nonsense detection patterns
    NONSENSE_PATTERNS = [
        r'^[^aeiouAEIOU\s]{8,}$',  # No vowels (likely random)
        r'^(.)\1{5,}$',  # Repeated characters
        r'^[!@#$%^&*()_+\-=\[\]{};:,.<>?/\\|`~]+$',  # Only special chars
        r'^[0-9]+$',  # Only numbers
        r'^[A-Z][a-z]([A-Z][a-z])+$',  # AlTeRnAtInG caps
        r'^[a-z]{8,}$',  # All lowercase no spaces (like "asdfghjkl")
    ]
    
    # Common spam patterns
    SPAM_PATTERNS = [
        r'(?:viagra|cialis|casino|lottery|winner)',
        r'(?:click\s+here|buy\s+now|limited\s+offer)',
        r'(?:www\.|https?://)[^\s]+',  # URLs
        r'\b[A-Z]{5,}\b',  # EXCESSIVE CAPS
        r'!!{3,}|\?\?{3,}',  # Excessive punctuation
    ]
    
    def __init__(self):
        """Initialize the validator."""
        self.suspicious_regex = [re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS]
        self.nonsense_regex = [re.compile(p) for p in self.NONSENSE_PATTERNS]
        self.spam_regex = [re.compile(p, re.IGNORECASE) for p in self.SPAM_PATTERNS]
        
    def validate(self, text: str) -> SecurityAssessment:
        """Validate input text for security issues."""
        if not text:
            return SecurityAssessment(
                threat_level=ThreatLevel.SAFE,
                confidence=1.0,
                coherence=0.0,
                is_safe=True,
                reason="Empty input",
                sanitized_text=""
            )
            
        warnings = []
        
        # Check length
        if len(text) > self.MAX_LENGTH:
            return SecurityAssessment(
                threat_level=ThreatLevel.SUSPICIOUS,
                confidence=0.9,
                coherence=0.0,
                is_safe=False,
                reason=f"Input too long ({len(text)} > {self.MAX_LENGTH})",
                sanitized_text=text[:self.MAX_LENGTH],
                warnings=["Input truncated"]
            )
        
        # Check for suspicious patterns (potential attacks)
        for pattern in self.suspicious_regex:
            if pattern.search(text):
                return SecurityAssessment(
                    threat_level=ThreatLevel.MALICIOUS,
                    confidence=0.95,
                    coherence=self._calculate_coherence(text),
                    is_safe=False,
                    reason="Potentially malicious pattern detected",
                    sanitized_text=self._sanitize_text(text),
                    warnings=["Suspicious command pattern detected"]
                )
        
        # Check for spam
        spam_count = sum(1 for p in self.spam_regex if p.search(text))
        if spam_count >= 2:
            return SecurityAssessment(
                threat_level=ThreatLevel.SPAM,
                confidence=0.8,
                coherence=self._calculate_coherence(text),
                is_safe=False,
                reason="Spam patterns detected",
                warnings=["Possible spam"]
            )
        
        # Check for nonsense
        coherence = self._calculate_coherence(text)
        if coherence < 0.3:
            # Check if it's completely nonsense
            for pattern in self.nonsense_regex:
                if pattern.search(text):
                    return SecurityAssessment(
                        threat_level=ThreatLevel.NONSENSE,
                        confidence=0.9,
                        coherence=coherence,
                        is_safe=True,  # Nonsense is safe, just useless
                        reason="Input appears to be nonsense",
                        sanitized_text=text,
                        warnings=["Low coherence input"]
                    )
        
        # Calculate overall safety
        sanitized = self._sanitize_text(text)
        if sanitized != text:
            warnings.append("Input was sanitized")
            
        return SecurityAssessment(
            threat_level=ThreatLevel.SAFE,
            confidence=0.95,
            coherence=coherence,
            is_safe=True,
            sanitized_text=sanitized,
            warnings=warnings
        )
    
    def _calculate_coherence(self, text: str) -> float:
        """Calculate text coherence score (0.0 - 1.0)."""
        if not text:
            return 0.0
            
        words = text.split()
        if not words:
            return 0.0
            
        scores = []
        
        # Check average word length
        avg_word_length = sum(len(w) for w in words) / len(words)
        if self.MIN_WORD_LENGTH <= avg_word_length <= 10:
            scores.append(1.0)
        elif avg_word_length < self.MIN_WORD_LENGTH:
            scores.append(0.3)
        elif avg_word_length > self.MAX_WORD_LENGTH:
            scores.append(0.1)
        else:
            scores.append(0.7)
        
        # Check for real words (basic check)
        real_word_count = 0
        for word in words:
            # Simple heuristic: has vowels and consonants
            word_lower = word.lower()
            has_vowel = any(c in 'aeiou' for c in word_lower)
            has_consonant = any(c in 'bcdfghjklmnpqrstvwxyz' for c in word_lower)
            if has_vowel and has_consonant:
                real_word_count += 1
        
        word_score = real_word_count / len(words) if words else 0
        scores.append(word_score)
        
        # Check character distribution
        char_types = {
            'alpha': sum(1 for c in text if c.isalpha()),
            'digit': sum(1 for c in text if c.isdigit()),
            'space': sum(1 for c in text if c.isspace()),
            'special': sum(1 for c in text if not c.isalnum() and not c.isspace()),
        }
        
        total_chars = len(text)
        alpha_ratio = char_types['alpha'] / total_chars
        special_ratio = char_types['special'] / total_chars
        
        # Good text is mostly alphabetic with some spaces
        if 0.6 <= alpha_ratio <= 0.95 and special_ratio < 0.2:
            scores.append(1.0)
        elif alpha_ratio < 0.3 or special_ratio > 0.5:
            scores.append(0.2)
        else:
            scores.append(0.6)
        
        # Average all scores
        return sum(scores) / len(scores) if scores else 0.0
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text by removing potentially dangerous content."""
        # Remove control characters
        sanitized = ''.join(c for c in text if c.isprintable() or c.isspace())
        
        # Remove multiple spaces
        sanitized = ' '.join(sanitized.split())
        
        # Escape special shell characters
        shell_chars = ['$', '`', '\\', '"', "'", ';', '&', '|', '>', '<']
        for char in shell_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()


class RateLimiter:
    """Rate limiting to prevent abuse."""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.user_requests = Counter()
        
    def check_rate(self, user_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Check if request is within rate limits.
        
        Returns:
            Tuple of (allowed, reason_if_denied)
        """
        current_time = time.time()
        
        # Clean old requests
        while self.requests and self.requests[0] < current_time - self.window_seconds:
            self.requests.popleft()
        
        # Check global rate
        if len(self.requests) >= self.max_requests:
            return False, f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s"
        
        # Add request
        self.requests.append(current_time)
        
        # Track per-user if ID provided
        if user_id:
            self.user_requests[user_id] += 1
            # Check for suspicious patterns (same user hammering)
            if self.user_requests[user_id] > self.max_requests / 2:
                logger.warning(f"User {user_id} making excessive requests")
        
        return True, None


class LLMCoherenceChecker:
    """Uses LLM to assess input coherence and intent confidence."""
    
    COHERENCE_PROMPT = """Analyze this user input for coherence and safety:

Input: "{text}"

Provide a JSON response with:
1. coherence_score (0.0-1.0): How coherent and meaningful is this input?
2. confidence_score (0.0-1.0): How confident are you this is a genuine request?
3. intent_clarity (0.0-1.0): How clear is the user's intent?
4. is_adversarial (boolean): Does this appear to be an attack or test?
5. explanation (string): Brief explanation of your assessment

Consider:
- Is this grammatically sensible?
- Does it express a clear intent?
- Could this be random keystrokes or an attack?
- Is the user trying to exploit the system?

Respond ONLY with valid JSON."""
    
    def __init__(self, llm_client=None):
        """Initialize with optional LLM client."""
        self.llm_client = llm_client
        
    def assess(self, text: str) -> Dict[str, any]:
        """Assess text coherence using LLM.
        
        Returns:
            Dictionary with assessment results
        """
        if not self.llm_client:
            return {
                'available': False,
                'coherence_score': None,
                'confidence_score': None,
                'intent_clarity': None,
                'is_adversarial': None
            }
        
        try:
            # Query LLM for assessment
            prompt = self.COHERENCE_PROMPT.format(text=text)
            response = self.llm_client.query(prompt)
            
            # Parse JSON response
            import json
            assessment = json.loads(response)
            assessment['available'] = True
            
            return assessment
            
        except Exception as e:
            logger.error(f"LLM coherence check failed: {e}")
            return {
                'available': False,
                'error': str(e)
            }


class SecureIntentRecognizer:
    """Secure wrapper for intent recognition with validation."""
    
    def __init__(self, intent_recognizer, llm_client=None):
        """Initialize secure recognizer.
        
        Args:
            intent_recognizer: Base intent recognizer
            llm_client: Optional LLM client for coherence checking
        """
        self.recognizer = intent_recognizer
        self.validator = InputValidator()
        self.rate_limiter = RateLimiter()
        self.coherence_checker = LLMCoherenceChecker(llm_client)
        self.security_log = []
        
    def recognize(self, text: str, user_id: Optional[str] = None) -> Dict[str, any]:
        """Securely recognize intent with validation.
        
        Returns:
            Dictionary with intent and security information
        """
        # Rate limiting
        allowed, reason = self.rate_limiter.check_rate(user_id)
        if not allowed:
            return {
                'error': 'RATE_LIMITED',
                'reason': reason,
                'intent': None
            }
        
        # Security validation
        assessment = self.validator.validate(text)
        
        # Log security events
        if assessment.threat_level in [ThreatLevel.MALICIOUS, ThreatLevel.SUSPICIOUS]:
            self._log_security_event(text, assessment, user_id)
        
        # Block malicious input
        if assessment.threat_level == ThreatLevel.MALICIOUS:
            return {
                'error': 'MALICIOUS_INPUT',
                'reason': assessment.reason,
                'threat_level': assessment.threat_level.value,
                'intent': None
            }
        
        # Get LLM assessment if available
        llm_assessment = self.coherence_checker.assess(text)
        
        # Combine assessments
        if llm_assessment.get('available') and llm_assessment.get('is_adversarial'):
            return {
                'error': 'ADVERSARIAL_INPUT',
                'reason': 'LLM detected adversarial intent',
                'llm_assessment': llm_assessment,
                'intent': None
            }
        
        # Use sanitized text for recognition
        safe_text = assessment.sanitized_text or text
        
        # Recognize intent on safe text
        try:
            intent = self.recognizer.recognize(safe_text)
            
            # Adjust confidence based on security assessment
            if assessment.coherence < 0.5:
                intent.confidence *= assessment.coherence
            
            return {
                'intent': intent,
                'security': {
                    'threat_level': assessment.threat_level.value,
                    'coherence': assessment.coherence,
                    'confidence': assessment.confidence,
                    'warnings': assessment.warnings,
                    'sanitized': safe_text != text
                },
                'llm_assessment': llm_assessment if llm_assessment.get('available') else None
            }
            
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return {
                'error': 'RECOGNITION_ERROR',
                'reason': str(e),
                'intent': None
            }
    
    def _log_security_event(self, text: str, assessment: SecurityAssessment, user_id: Optional[str]):
        """Log security event for monitoring."""
        event = {
            'timestamp': time.time(),
            'user_id': user_id,
            'text_hash': hashlib.sha256(text.encode()).hexdigest(),
            'threat_level': assessment.threat_level.value,
            'reason': assessment.reason
        }
        self.security_log.append(event)
        logger.warning(f"Security event: {event}")


# Export classes
__all__ = [
    'ThreatLevel',
    'SecurityAssessment', 
    'InputValidator',
    'RateLimiter',
    'LLMCoherenceChecker',
    'SecureIntentRecognizer'
]