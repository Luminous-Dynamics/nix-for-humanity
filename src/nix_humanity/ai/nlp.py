"""
from typing import List, Dict, Optional
Natural Language Processing pipeline

Multi-stage NLP processing using various specialized models.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

# Import AI enhancement modules
try:
    # Try direct import from project root
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
    from src.nix_for_humanity.ai import XAIEngine, AdvancedLearningSystem, analyze_intent_recognition
    print("✅ AI enhancement modules imported successfully")
except ImportError as e:
    print(f"⚠️  AI enhancement modules not available: {e}")
    XAIEngine = None
    AdvancedLearningSystem = None
    analyze_intent_recognition = None


class NLPPipeline:
    """Multi-stage NLP processing with AI enhancement"""
    
    def __init__(self, model_manager=None):
        """
        Initialize NLP pipeline
        
        Args:
            model_manager: Optional ModelManager instance
        """
        self.model_manager = model_manager
        self._init_nltk()
        self._init_patterns()
        
        # Initialize AI enhancement modules
        self.xai_engine = None
        self.advanced_learning = None
        
        if XAIEngine is not None:
            try:
                self.xai_engine = XAIEngine()
                print("🧠 XAI Engine initialized - explanations available")
            except Exception as e:
                print(f"⚠️  XAI Engine initialization failed: {e}")
        
        if AdvancedLearningSystem is not None:
            try:
                self.advanced_learning = AdvancedLearningSystem()
                print("🌟 Advanced Learning System initialized - adaptive responses active")
            except Exception as e:
                print(f"⚠️  Advanced Learning System initialization failed: {e}")
        
    def _init_nltk(self):
        """Initialize NLTK data"""
        try:
            import nltk
            self.nltk = nltk
            
            # Download required data quietly
            nltk_data = Path.home() / 'nltk_data'
            if not (nltk_data / 'tokenizers' / 'punkt').exists():
                try:
                    nltk.download('punkt', quiet=True)
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
                    
            if not (nltk_data / 'corpora' / 'stopwords').exists():
                try:
                    nltk.download('stopwords', quiet=True)
                except Exception:
                    # TODO: Add proper error handling
                    pass  # Silent for now, should log error
                    
            self._has_nltk = True
            
        except ImportError:
            self._has_nltk = False
            if os.getenv('DEBUG'):
                print("NLTK not available, using basic tokenization")
                
    def _init_patterns(self):
        """Initialize regex patterns for text processing"""
        # Command patterns
        self.command_pattern = re.compile(r'`([^`]+)`')
        
        # Path patterns
        self.path_pattern = re.compile(r'(/[\w/.-]+)')
        
        # Package name patterns
        self.package_pattern = re.compile(r'\b([a-zA-Z0-9][\w-]*)\b')
        
        # Number patterns
        self.number_pattern = re.compile(r'\b(\d+)\b')
        
    def process(self, text: str, user_id: str = "default", provide_explanation: bool = False) -> Dict[str, Any]:
        """
        Full NLP pipeline with AI enhancement
        
        Args:
            text: Input text to process
            user_id: User ID for personalized processing
            provide_explanation: Whether to provide XAI explanations
            
        Returns:
            Dictionary with processed components and optional explanations
        """
        result = {
            'original': text,
            'normalized': self._normalize(text),
            'tokens': [],
            'entities': {},
            'commands': [],
            'paths': [],
            'key_terms': [],
            'intent': None,
            'confidence': 0.0,
            'explanation': None,
            'adapted_for_user': False
        }
        
        # 1. Extract commands (backtick enclosed)
        result['commands'] = self.command_pattern.findall(text)
        
        # 2. Extract paths
        result['paths'] = self.path_pattern.findall(text)
        
        # 3. Tokenize
        if self._has_nltk:
            result['tokens'] = self._nltk_tokenize(result['normalized'])
        else:
            result['tokens'] = self._basic_tokenize(result['normalized'])
            
        # 4. Extract entities with spaCy if available
        if self.model_manager and hasattr(self.model_manager, 'spacy_nlp'):
            try:
                result['entities'] = self._extract_entities_spacy(text)
            except Exception:
                result['entities'] = self._extract_entities_regex(text)
        else:
            result['entities'] = self._extract_entities_regex(text)
            
        # 5. Extract key terms (non-stopword tokens)
        result['key_terms'] = self._extract_key_terms(result['tokens'])
        
        # 6. Enhanced intent recognition with AI
        intent_result = self._recognize_intent_enhanced(text, result)
        result['intent'] = intent_result['intent']
        result['confidence'] = intent_result['confidence']
        
        # 7. Generate explanation if requested and XAI is available
        if provide_explanation and self.xai_engine and analyze_intent_recognition:
            try:
                context = {
                    'user_input': text,
                    'tokens': result['tokens'],
                    'entities': result['entities'],
                    'key_terms': result['key_terms'],
                    'user_history': {
                        'similar_patterns': 1  # Mock data for now
                    }
                }
                explanation = analyze_intent_recognition(
                    text, result['intent'], result['confidence'], context, self.xai_engine
                )
                result['explanation'] = explanation
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"XAI explanation failed: {e}")
        
        # 8. Adapt response for user if advanced learning is available
        if self.advanced_learning and user_id != "default":
            try:
                # Get user model to understand preferences
                user_model = self.advanced_learning.get_user_model(user_id)
                
                # Mark that this result has been adapted
                result['adapted_for_user'] = True
                result['user_preferences'] = {
                    'explanation_level': user_model.preferred_explanation_level,
                    'response_style': user_model.preferred_response_style,
                    'verbosity': user_model.preferred_verbosity
                }
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"User adaptation failed: {e}")
        
        return result
        
    def _normalize(self, text: str) -> str:
        """Normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove punctuation except for paths and commands
        # Keep: / - . _ ` ~
        text = re.sub(r'[^\w\s/\-._`~]', ' ', text)
        
        return text.strip()
        
    def _nltk_tokenize(self, text: str) -> List[str]:
        """Tokenize using NLTK"""
        try:
            tokens = self.nltk.word_tokenize(text)
            # Remove stopwords if available
            try:
                from nltk.corpus import stopwords
                stop_words = set(stopwords.words('english'))
                tokens = [t for t in tokens if t.lower() not in stop_words or len(t) > 2]
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
            return tokens
        except Exception:
            return self._basic_tokenize(text)
            
    def _basic_tokenize(self, text: str) -> List[str]:
        """Basic tokenization fallback"""
        # Simple word splitting
        tokens = text.split()
        
        # Remove very short tokens
        tokens = [t for t in tokens if len(t) > 1]
        
        # Remove common stopwords manually
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        tokens = [t for t in tokens if t not in stopwords]
        
        return tokens
        
    def _extract_entities_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy"""
        nlp = self.model_manager.spacy_nlp
        doc = nlp(text)
        
        entities = {
            'packages': [],
            'paths': [],
            'numbers': [],
            'actions': []
        }
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG"]:
                entities['packages'].append(ent.text.lower())
            elif ent.label_ == "CARDINAL":
                entities['numbers'].append(ent.text)
                
        # Extract paths
        for token in doc:
            if '/' in token.text:
                entities['paths'].append(token.text)
                
        # Extract action verbs
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                entities['actions'].append(token.lemma_)
                
        return entities
        
    def _extract_entities_regex(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using regex (fallback)"""
        entities = {
            'packages': [],
            'paths': [],
            'numbers': [],
            'actions': []
        }
        
        # Extract paths
        entities['paths'] = self.path_pattern.findall(text)
        
        # Extract numbers
        entities['numbers'] = self.number_pattern.findall(text)
        
        # Extract potential package names (alphanumeric with dashes)
        words = text.split()
        for word in words:
            if re.match(r'^[a-zA-Z0-9][\w-]*$', word) and len(word) > 2:
                # Check if it looks like a package name
                if any(char in word for char in ['-', '_']) or word.islower():
                    entities['packages'].append(word)
                    
        # Extract common action verbs
        action_verbs = ['install', 'update', 'remove', 'search', 'configure', 
                        'enable', 'disable', 'start', 'stop', 'restart']
        for verb in action_verbs:
            if verb in text.lower():
                entities['actions'].append(verb)
                
        return entities
        
    def _extract_key_terms(self, tokens: List[str]) -> List[str]:
        """Extract key terms from tokens"""
        # Remove very common words and keep important terms
        key_terms = []
        
        for token in tokens:
            # Keep if it's long enough and not a common word
            if len(token) > 2 and token.isalnum():
                key_terms.append(token)
                
        # Remove duplicates while preserving order
        seen = set()
        key_terms = [t for t in key_terms if not (t in seen or seen.add(t))]
        
        return key_terms
        
    def extract_package_name(self, text: str) -> Optional[str]:
        """
        Extract the most likely package name from text
        
        Args:
            text: Input text
            
        Returns:
            Most likely package name or None
        """
        # Process the text
        processed = self.process(text)
        
        # Check entities first
        if processed['entities'].get('packages'):
            return processed['entities']['packages'][0]
            
        # Check for common package names in key terms
        common_packages = {
            'firefox', 'chrome', 'chromium', 'vscode', 'code', 'vim', 
            'neovim', 'emacs', 'python', 'nodejs', 'docker', 'git',
            'htop', 'tmux', 'zsh', 'fish', 'rust', 'go', 'java'
        }
        
        for term in processed['key_terms']:
            if term in common_packages:
                return term
                
        # Look for package-like terms
        for term in processed['key_terms']:
            if '-' in term or '_' in term:
                return term
                
        return None
    
    def _recognize_intent_enhanced(self, text: str, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced intent recognition using rule-based and AI approaches
        
        Args:
            text: Original text
            processed_data: Already processed NLP data
            
        Returns:
            Dictionary with intent and confidence
        """
        intent_result = {
            'intent': 'unknown',
            'confidence': 0.0
        }
        
        # Rule-based intent recognition
        text_lower = text.lower()
        entities = processed_data.get('entities', {})
        key_terms = processed_data.get('key_terms', [])
        
        # Install intent patterns
        install_keywords = ['install', 'add', 'get', 'need', 'want']
        if any(keyword in text_lower for keyword in install_keywords):
            intent_result['intent'] = 'install'
            intent_result['confidence'] = 0.8
            
            # Higher confidence if we found a package name
            if entities.get('packages') or any(term in text_lower for term in ['firefox', 'chrome', 'python', 'docker']):
                intent_result['confidence'] = 0.9
        
        # Search intent patterns
        elif any(keyword in text_lower for keyword in ['search', 'find', 'look', 'show']):
            intent_result['intent'] = 'search'
            intent_result['confidence'] = 0.8
        
        # Update intent patterns
        elif any(keyword in text_lower for keyword in ['update', 'upgrade', 'refresh']):
            intent_result['intent'] = 'update'
            intent_result['confidence'] = 0.8
        
        # Remove intent patterns
        elif any(keyword in text_lower for keyword in ['remove', 'uninstall', 'delete']):
            intent_result['intent'] = 'remove'
            intent_result['confidence'] = 0.8
        
        # Help intent patterns
        elif any(keyword in text_lower for keyword in ['help', 'how', 'what', '?']):
            intent_result['intent'] = 'help'
            intent_result['confidence'] = 0.7
        
        # Status/info intent patterns
        elif any(keyword in text_lower for keyword in ['status', 'info', 'show', 'list']):
            intent_result['intent'] = 'info'
            intent_result['confidence'] = 0.7
        
        return intent_result
    
    def record_interaction_feedback(self, user_id: str, text: str, intent: str, 
                                   success: bool, helpful: Optional[bool] = None):
        """
        Record interaction feedback for learning
        
        Args:
            user_id: User identifier
            text: Original user input
            intent: Recognized intent
            success: Whether the interaction was successful
            helpful: Whether the user found it helpful (optional)
        """
        if self.advanced_learning:
            try:
                # Record interaction in advanced learning system
                # Note: The interaction structure would be defined by the advanced learning system
                interaction_data = {
                    'query': text,
                    'intent': intent,
                    'response': "", # Response would be filled by caller
                    'success': success,
                    'helpful': helpful,
                    'user_id': user_id
                }
                
                # This would be called by the main system with proper interaction structure
                # self.advanced_learning.record_interaction(interaction_data)
                
            except Exception as e:
                if os.getenv('DEBUG'):
                    print(f"Failed to record feedback: {e}")
    
    def get_explanation_for_user(self, explanation, user_id: str = "default") -> str:
        """
        Get user-adapted explanation based on their preferences
        
        Args:
            explanation: XAI Explanation object
            user_id: User identifier
            
        Returns:
            Formatted explanation text
        """
        if not explanation:
            return "No explanation available."
        
        # Get user preferences if advanced learning is available
        explanation_level = "simple"
        if self.advanced_learning and user_id != "default":
            try:
                user_model = self.advanced_learning.get_user_model(user_id)
                explanation_level = user_model.preferred_explanation_level
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
        
        # Return appropriate explanation level
        if explanation_level == "technical":
            return explanation.technical_explanation
        elif explanation_level == "detailed":
            return explanation.detailed_explanation
        else:
            return explanation.simple_explanation


# === Module-level functions for backward compatibility ===

def process(text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Process natural language text and return intent.
    
    This is a convenience function that creates an NLPPipeline instance
    and processes the text.
    """
    pipeline = NLPPipeline()
    # The method is called 'process', not 'process_text'
    result = pipeline.process(text)
    
    # Convert the dict result to an Intent-like object if needed
    if isinstance(result, dict) and 'intent' in result:
        # Create a simple object with type and entities attributes
        class SimpleIntent:
            def __init__(self, intent_type, entities=None):
                self.type = intent_type
                self.entities = entities or {}
        
        intent_type = result['intent']
        entities = result.get('entities', {})
        
        # Extract package name if present
        if 'package' not in entities and 'package_name' in result:
            entities['package'] = result['package_name']
        if 'query' not in entities and 'key_terms' in result:
            entities['query'] = ' '.join(result['key_terms'])
            
        return SimpleIntent(intent_type, entities)
    
    return result


def extract_package_name(text: str) -> Optional[str]:
    """Extract package name from user input.
    
    Args:
        text: User input text
        
    Returns:
        Extracted package name or None
    """
    # Simple extraction logic
    import re
    
    # Remove common words
    text = text.lower()
    for word in ['install', 'remove', 'search', 'please', 'can', 'you', 'i', 'want', 'to', 'for', 'the']:
        text = text.replace(word, '')
    
    # Look for package-like words
    words = text.strip().split()
    if words:
        # Return the first non-empty word that looks like a package
        for word in words:
            if word and re.match(r'^[a-z][a-z0-9-]*$', word):
                return word
    
    return None


def record_interaction_feedback(intent: Any, success: bool, feedback: Optional[str] = None) -> None:
    """Record user feedback for learning.
    
    Args:
        intent: The processed intent
        success: Whether the operation was successful
        feedback: Optional user feedback
    """
    # TODO: Implement feedback recording for learning system
    pass


def get_explanation_for_user(intent: Any) -> str:
    """Get human-readable explanation of what will happen.
    
    Args:
        intent: The processed intent
        
    Returns:
        Human-readable explanation
    """
    if not intent:
        return "I couldn't understand your request."
    
    if hasattr(intent, 'entities'):
        explanations = {
            'INSTALL': f"I'll install the {intent.entities.get('package', 'requested package')} for you.",
            'REMOVE': f"I'll remove {intent.entities.get('package', 'the package')} from your system.",
            'SEARCH': f"I'll search for packages matching '{intent.entities.get('query', 'your query')}'.",
            'UPDATE': "I'll update your NixOS system to the latest configuration.",
            'ROLLBACK': "I'll rollback to the previous system generation.",
            'LIST': f"I'll list {intent.entities.get('target', 'the requested items')} for you.",
            'STATUS': f"I'll check the status of {intent.entities.get('target', 'your system')}."
        }
        
        intent_type = str(intent.type) if hasattr(intent, 'type') else 'UNKNOWN'
        return explanations.get(intent_type, f"I'll execute the {intent_type} operation.")
    
    return "I'll process your request."