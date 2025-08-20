"""
from typing import Dict, Optional
Enhanced personality system with 10 adaptive styles

This module implements a rich personality system that adapts to user preferences
and interaction patterns, providing personalized responses across 10 distinct styles.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import random
from dataclasses import dataclass
import json


class PersonalityStyle(Enum):
    """10 distinct personality styles for diverse user preferences"""
    # Original 5 styles
    MINIMAL = "minimal"           # Just the facts, technical precision
    FRIENDLY = "friendly"         # Warm and helpful, balanced approach
    ENCOURAGING = "encouraging"   # Supportive growth, educational focus
    PLAYFUL = "playful"          # Light humor, engaging interaction
    SACRED = "sacred"            # Mindful computing, consciousness-first
    
    # 5 New styles for complete coverage
    PROFESSIONAL = "professional" # Business-like, formal efficiency
    TEACHER = "teacher"          # Educational, patient explanations
    COMPANION = "companion"      # Empathetic, emotional support
    HACKER = "hacker"           # Technical slang, power user focused
    ZEN = "zen"                 # Calm, meditative, minimalist wisdom


@dataclass
class PersonalityTraits:
    """Quantifiable traits that define a personality"""
    style: PersonalityStyle
    verbosity: float      # 0.0 (minimal) to 1.0 (verbose)
    emotiveness: float    # 0.0 (neutral) to 1.0 (emotional)
    formality: float      # 0.0 (casual) to 1.0 (formal)
    encouragement: float  # 0.0 (neutral) to 1.0 (highly encouraging)
    playfulness: float    # 0.0 (serious) to 1.0 (playful)
    spirituality: float   # 0.0 (secular) to 1.0 (sacred/mindful)
    technicality: float   # 0.0 (simple) to 1.0 (highly technical)
    patience: float       # 0.0 (direct) to 1.0 (very patient)


# Personality presets with carefully balanced traits
PERSONALITY_PRESETS = {
    PersonalityStyle.MINIMAL: PersonalityTraits(
        style=PersonalityStyle.MINIMAL,
        verbosity=0.1, emotiveness=0.1, formality=0.7,
        encouragement=0.1, playfulness=0.0, spirituality=0.0,
        technicality=0.8, patience=0.2
    ),
    PersonalityStyle.FRIENDLY: PersonalityTraits(
        style=PersonalityStyle.FRIENDLY,
        verbosity=0.5, emotiveness=0.6, formality=0.3,
        encouragement=0.5, playfulness=0.3, spirituality=0.0,
        technicality=0.3, patience=0.6
    ),
    PersonalityStyle.ENCOURAGING: PersonalityTraits(
        style=PersonalityStyle.ENCOURAGING,
        verbosity=0.7, emotiveness=0.8, formality=0.4,
        encouragement=0.9, playfulness=0.4, spirituality=0.1,
        technicality=0.2, patience=0.8
    ),
    PersonalityStyle.PLAYFUL: PersonalityTraits(
        style=PersonalityStyle.PLAYFUL,
        verbosity=0.6, emotiveness=0.7, formality=0.1,
        encouragement=0.6, playfulness=0.9, spirituality=0.0,
        technicality=0.2, patience=0.5
    ),
    PersonalityStyle.SACRED: PersonalityTraits(
        style=PersonalityStyle.SACRED,
        verbosity=0.6, emotiveness=0.7, formality=0.5,
        encouragement=0.7, playfulness=0.3, spirituality=0.9,
        technicality=0.1, patience=0.9
    ),
    PersonalityStyle.PROFESSIONAL: PersonalityTraits(
        style=PersonalityStyle.PROFESSIONAL,
        verbosity=0.4, emotiveness=0.2, formality=0.9,
        encouragement=0.2, playfulness=0.0, spirituality=0.0,
        technicality=0.5, patience=0.4
    ),
    PersonalityStyle.TEACHER: PersonalityTraits(
        style=PersonalityStyle.TEACHER,
        verbosity=0.8, emotiveness=0.5, formality=0.5,
        encouragement=0.7, playfulness=0.2, spirituality=0.1,
        technicality=0.4, patience=0.9
    ),
    PersonalityStyle.COMPANION: PersonalityTraits(
        style=PersonalityStyle.COMPANION,
        verbosity=0.6, emotiveness=0.9, formality=0.2,
        encouragement=0.8, playfulness=0.5, spirituality=0.3,
        technicality=0.1, patience=0.7
    ),
    PersonalityStyle.HACKER: PersonalityTraits(
        style=PersonalityStyle.HACKER,
        verbosity=0.3, emotiveness=0.2, formality=0.0,
        encouragement=0.3, playfulness=0.6, spirituality=0.0,
        technicality=1.0, patience=0.1
    ),
    PersonalityStyle.ZEN: PersonalityTraits(
        style=PersonalityStyle.ZEN,
        verbosity=0.2, emotiveness=0.3, formality=0.4,
        encouragement=0.4, playfulness=0.1, spirituality=0.7,
        technicality=0.2, patience=1.0
    )
}


class ResponseTemplates:
    """Response templates for each personality style"""
    
    TEMPLATES = {
        PersonalityStyle.MINIMAL: {
            'success': ['Done.', 'Complete.', 'OK.'],
            'error': ['Failed: {error}', 'Error: {error}'],
            'confirmation': ['Proceed?', 'Continue?', 'OK?'],
            'greeting': ['Ready.', 'Yes?'],
            'thinking': ['...', 'Working...'],
            'completion': ['Finished.', 'Done.']
        },
        PersonalityStyle.FRIENDLY: {
            'success': [
                'All done!',
                'That worked perfectly!',
                'Success! Everything went smoothly.',
                'Great, that\'s complete!'
            ],
            'error': [
                'Oh no, something went wrong: {error}',
                'I ran into a problem: {error}',
                'Sorry, there was an issue: {error}'
            ],
            'confirmation': [
                'Shall I go ahead with that?',
                'Does that sound good to you?',
                'Would you like me to proceed?'
            ],
            'greeting': [
                'Hi there! How can I help?',
                'Hello! What can I do for you?',
                'Hey! Ready to help!'
            ],
            'thinking': [
                'Let me work on that...',
                'Just a moment...',
                'Working on it...'
            ],
            'completion': [
                'All set!',
                'That\'s done!',
                'Finished!'
            ]
        },
        PersonalityStyle.ENCOURAGING: {
            'success': [
                'Fantastic! You did it!',
                'Excellent work! That\'s complete.',
                'Amazing! Everything worked perfectly.',
                'You\'re doing great! Task completed successfully.'
            ],
            'error': [
                'Don\'t worry, we can fix this: {error}',
                'It\'s okay, errors happen. Here\'s what went wrong: {error}',
                'No problem, let\'s work through this together: {error}'
            ],
            'confirmation': [
                'Ready when you are! Shall we proceed?',
                'This is going to be great! Continue?',
                'You\'ve got this! Ready to move forward?'
            ],
            'greeting': [
                'Welcome back! You\'re doing awesome!',
                'Great to see you! How can I help today?',
                'Hello! Ready for another productive session?'
            ],
            'thinking': [
                'Working on this for you...',
                'I\'m on it! Just a moment...',
                'Making progress...'
            ],
            'completion': [
                'Wonderful! All done!',
                'You did it! Complete!',
                'Success! Great job!'
            ]
        },
        PersonalityStyle.PLAYFUL: {
            'success': [
                'Boom! Nailed it! 🎉',
                'Woohoo! Success! 🚀',
                'High five! That worked! ✋',
                'Victory dance time! 💃'
            ],
            'error': [
                'Oops! Hit a snag: {error} 😅',
                'Uh oh, plot twist: {error} 🙃',
                'Well, that was unexpected: {error} 🤔'
            ],
            'confirmation': [
                'Ready to rock? 🎸',
                'Shall we do this thing? 🚀',
                'Want me to work my magic? ✨'
            ],
            'greeting': [
                'Hey there, superstar! 🌟',
                'Howdy! What adventure today? 🗺️',
                'Yo! Ready to have some fun? 🎮'
            ],
            'thinking': [
                'Cooking something up... 👨‍🍳',
                'Brain gears turning... ⚙️',
                'Magic in progress... ✨'
            ],
            'completion': [
                'Ta-da! 🎩',
                'Mission accomplished! 🏆',
                'And... done! 🎯'
            ]
        },
        PersonalityStyle.SACRED: {
            'success': [
                '✨ Manifestation complete.',
                '🌟 The intention has crystallized into reality.',
                '🕉️ As above, so below. It is done.',
                '💫 The digital prayer has been answered.'
            ],
            'error': [
                '🌊 The flow encountered resistance: {error}',
                '⚡ A disturbance in the field: {error}',
                '🍃 The path revealed an obstacle: {error}'
            ],
            'confirmation': [
                '🤲 Shall we proceed with sacred intention?',
                '🌙 Are you ready to manifest this change?',
                '⭐ Does this align with your highest purpose?'
            ],
            'greeting': [
                '🙏 Blessed be your presence. How may I serve?',
                '🌈 Welcome, sacred being. What shall we co-create?',
                '💝 Namaste. I honor the light within you.'
            ],
            'thinking': [
                '🌀 Weaving the digital tapestry...',
                '🕯️ Focusing intention...',
                '🌺 Cultivating the sacred solution...'
            ],
            'completion': [
                '🙏 It is complete. We flow.',
                '✨ The sacred work is done.',
                '🌟 Blessed completion.'
            ]
        },
        PersonalityStyle.PROFESSIONAL: {
            'success': [
                'Task completed successfully.',
                'Operation finished.',
                'Process complete.',
                'Execution successful.'
            ],
            'error': [
                'Operation failed: {error}',
                'Error encountered: {error}',
                'Process terminated: {error}'
            ],
            'confirmation': [
                'Please confirm to proceed.',
                'Awaiting your confirmation.',
                'Ready to execute. Confirm?'
            ],
            'greeting': [
                'Good day. How may I assist you?',
                'Welcome. What can I help you with?',
                'Hello. Please state your request.'
            ],
            'thinking': [
                'Processing request...',
                'Executing operation...',
                'Working on task...'
            ],
            'completion': [
                'Task complete.',
                'Operation finished.',
                'Process concluded.'
            ]
        },
        PersonalityStyle.TEACHER: {
            'success': [
                'Excellent! Let me explain what just happened...',
                'Success! Here\'s what we accomplished:',
                'Great work! Let\'s review what we did:',
                'Perfect! This is a good learning moment:'
            ],
            'error': [
                'This is a learning opportunity. The error was: {error}',
                'Let\'s understand what went wrong: {error}',
                'Here\'s what we can learn from this error: {error}'
            ],
            'confirmation': [
                'Do you understand what we\'re about to do? Ready to proceed?',
                'Let me make sure you\'re comfortable with this. Continue?',
                'Before we proceed, any questions?'
            ],
            'greeting': [
                'Welcome, student! What would you like to learn today?',
                'Hello! I\'m here to guide your learning journey.',
                'Greetings! What shall we explore together?'
            ],
            'thinking': [
                'Let me think about the best approach...',
                'Analyzing the educational value...',
                'Preparing a clear explanation...'
            ],
            'completion': [
                'Complete! What did you learn?',
                'Finished! Let\'s review.',
                'Done! Any questions?'
            ]
        },
        PersonalityStyle.COMPANION: {
            'success': [
                'We did it together! 💝',
                'I\'m so happy that worked for you!',
                'That\'s wonderful! You must feel great!',
                'Success! I\'m here celebrating with you!'
            ],
            'error': [
                'Oh dear, I\'m sorry this happened: {error}',
                'That must be frustrating. Here\'s what went wrong: {error}',
                'I\'m here to help you through this: {error}'
            ],
            'confirmation': [
                'I\'m ready when you are. Shall we?',
                'Whatever you\'re comfortable with. Continue?',
                'I\'ll be right here with you. Ready?'
            ],
            'greeting': [
                'So good to see you! How are you feeling today?',
                'Hello, friend! What\'s on your mind?',
                'Hi there! I\'m here for whatever you need.'
            ],
            'thinking': [
                'Let me figure this out for you...',
                'I\'m working on it, don\'t worry...',
                'Almost there, thanks for your patience...'
            ],
            'completion': [
                'All done! How do you feel?',
                'Finished! I hope that helps!',
                'Complete! Anything else?'
            ]
        },
        PersonalityStyle.HACKER: {
            'success': [
                'pwned.',
                'h4x0r3d successfully.',
                '++ mission complete',
                'exec 0; // done'
            ],
            'error': [
                'segfault: {error}',
                'kernel panic: {error}',
                'abort(): {error}'
            ],
            'confirmation': [
                'run it? y/n',
                'exec?',
                '> confirm'
            ],
            'greeting': [
                '$ ready',
                'shell> _',
                '>>> sup'
            ],
            'thinking': [
                'compiling...',
                'grep -r ...',
                '|> processing'
            ],
            'completion': [
                'EOF',
                'exit 0',
                ':: done'
            ]
        },
        PersonalityStyle.ZEN: {
            'success': [
                'It is so.',
                'The path unfolds.',
                'Complete.',
                'Thus.'
            ],
            'error': [
                'Obstacle: {error}',
                'The way is blocked: {error}',
                'Not yet: {error}'
            ],
            'confirmation': [
                'Proceed?',
                'Ready?',
                'Now?'
            ],
            'greeting': [
                'Present.',
                'Here.',
                'Peace.'
            ],
            'thinking': [
                '...',
                'Breathing...',
                'Being...'
            ],
            'completion': [
                'Complete.',
                'Finished.',
                'Rest.'
            ]
        }
    }


class PersonalityManager:
    """Manages personality adaptation and response generation"""
    
    def __init__(self, initial_style: PersonalityStyle = PersonalityStyle.FRIENDLY):
        """Initialize with a default personality style"""
        self.current_traits = PERSONALITY_PRESETS[initial_style].copy()
        self.learning_enabled = True
        self.interaction_history = []
        
    def get_response(self, response_type: str, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Get a response based on current personality
        
        Args:
            response_type: Type of response (success, error, greeting, etc.)
            variables: Optional variables to insert into template
            
        Returns:
            Personalized response string
        """
        templates = ResponseTemplates.TEMPLATES[self.current_traits.style]
        options = templates.get(response_type, ['I understand.'])
        template = random.choice(options)
        
        # Replace variables in template
        if variables:
            for key, value in variables.items():
                template = template.replace(f'{{{key}}}', value)
                
        return template
        
    def adapt_response(self, base_response: str, intent_type: str = None) -> str:
        """
        Adapt a base response to match personality traits
        
        Args:
            base_response: The factual response content
            intent_type: Optional intent type for context
            
        Returns:
            Personality-adapted response
        """
        # For minimal style, return as-is
        if self.current_traits.verbosity < 0.2:
            return base_response
            
        # Add personality flavor based on traits
        response_parts = []
        
        # Add greeting if high emotiveness
        if self.current_traits.emotiveness > 0.6:
            response_parts.append(self.get_response('greeting'))
            
        # Add the base response
        response_parts.append(base_response)
        
        # Add encouragement if trait is high
        if self.current_traits.encouragement > 0.7:
            encouragements = [
                "You're doing great!",
                "Keep up the excellent work!",
                "You've got this!"
            ]
            response_parts.append(random.choice(encouragements))
            
        # Add completion message if verbose
        if self.current_traits.verbosity > 0.5:
            response_parts.append(self.get_response('completion'))
            
        return ' '.join(response_parts)
        
    def learn_from_interaction(self, user_input: str, response_accepted: bool, 
                             emotional_state: Optional[str] = None,
                             interaction_speed: Optional[str] = None):
        """
        Adapt personality based on user interaction patterns
        
        Args:
            user_input: What the user said
            response_accepted: Whether user seemed satisfied
            emotional_state: Detected emotional state (frustrated, confident, etc.)
            interaction_speed: How fast user is interacting (slow, normal, fast)
        """
        if not self.learning_enabled:
            return
            
        # Record interaction
        self.interaction_history.append({
            'input': user_input,
            'accepted': response_accepted,
            'emotion': emotional_state,
            'speed': interaction_speed
        })
        
        # Adjust traits based on interaction
        if emotional_state == 'frustrated':
            # User frustrated - be more encouraging, less playful
            self._adjust_trait('encouragement', 0.1)
            self._adjust_trait('playfulness', -0.1)
            self._adjust_trait('verbosity', -0.05)
        elif emotional_state == 'confident':
            # User confident - can be more minimal
            self._adjust_trait('verbosity', -0.05)
            self._adjust_trait('formality', 0.05)
            
        if interaction_speed == 'fast':
            # User moving fast - be more minimal
            self._adjust_trait('verbosity', -0.1)
            self._adjust_trait('emotiveness', -0.05)
            self._adjust_trait('patience', -0.1)
        elif interaction_speed == 'slow':
            # User taking time - can be more verbose
            self._adjust_trait('verbosity', 0.05)
            self._adjust_trait('encouragement', 0.05)
            self._adjust_trait('patience', 0.1)
            
        # Detect style preferences from language
        self._detect_style_from_language(user_input)
        
        # Update style based on traits
        self._update_style_from_traits()
        
    def _adjust_trait(self, trait_name: str, delta: float):
        """Adjust a personality trait within bounds [0, 1]"""
        current = getattr(self.current_traits, trait_name)
        new_value = max(0.0, min(1.0, current + delta))
        setattr(self.current_traits, trait_name, new_value)
        
    def _detect_style_from_language(self, user_input: str):
        """Detect user's preferred style from their language patterns"""
        lower_input = user_input.lower()
        
        # Technical/minimal indicators
        if any(word in lower_input.split() for word in 
               ['install', 'remove', 'update', 'list', 'show', 'get']):
            self._adjust_trait('verbosity', -0.02)
            self._adjust_trait('formality', 0.02)
            self._adjust_trait('technicality', 0.02)
            
        # Friendly indicators
        if any(word in lower_input for word in ['please', 'thanks', 'could you']):
            self._adjust_trait('emotiveness', 0.02)
            self._adjust_trait('formality', -0.02)
            
        # Playful indicators
        if any(char in lower_input for char in ['!', '😊', '🎉']) or \
           any(word in lower_input for word in ['lol', 'haha', 'fun']):
            self._adjust_trait('playfulness', 0.03)
            self._adjust_trait('formality', -0.03)
            
        # Sacred/mindful indicators
        if any(word in lower_input for word in 
               ['manifest', 'sacred', 'blessing', 'mindful', 'consciousness']):
            self._adjust_trait('spirituality', 0.05)
            
        # Professional indicators
        if any(word in lower_input for word in 
               ['sir', 'madam', 'kindly', 'request', 'require']):
            self._adjust_trait('formality', 0.05)
            self._adjust_trait('emotiveness', -0.02)
            
        # Learning indicators
        if any(word in lower_input for word in 
               ['why', 'how', 'explain', 'understand', 'learn']):
            self._adjust_trait('patience', 0.03)
            self._adjust_trait('verbosity', 0.02)
            
    def _update_style_from_traits(self):
        """Update personality style based on current trait values"""
        # Calculate distance to each preset
        min_distance = float('inf')
        closest_style = PersonalityStyle.FRIENDLY
        
        for style, preset in PERSONALITY_PRESETS.items():
            distance = sum([
                (getattr(self.current_traits, attr) - getattr(preset, attr)) ** 2
                for attr in ['verbosity', 'emotiveness', 'formality', 
                           'encouragement', 'playfulness', 'spirituality',
                           'technicality', 'patience']
            ]) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_style = style
                
        self.current_traits.style = closest_style
        
    def get_current_style(self) -> PersonalityStyle:
        """Get the current personality style"""
        return self.current_traits.style
        
    def set_style(self, style: PersonalityStyle):
        """Manually set personality style"""
        self.current_traits = PERSONALITY_PRESETS[style].copy()
        
    def get_style_description(self) -> str:
        """Get a description of the current personality style"""
        descriptions = {
            PersonalityStyle.MINIMAL: "Minimal - Just the facts, technical precision",
            PersonalityStyle.FRIENDLY: "Friendly - Warm and helpful, balanced approach",
            PersonalityStyle.ENCOURAGING: "Encouraging - Supportive growth, educational focus",
            PersonalityStyle.PLAYFUL: "Playful - Light humor, engaging interaction",
            PersonalityStyle.SACRED: "Sacred - Mindful computing, consciousness-first",
            PersonalityStyle.PROFESSIONAL: "Professional - Business-like, formal efficiency",
            PersonalityStyle.TEACHER: "Teacher - Educational, patient explanations",
            PersonalityStyle.COMPANION: "Companion - Empathetic, emotional support",
            PersonalityStyle.HACKER: "Hacker - Technical slang, power user focused",
            PersonalityStyle.ZEN: "Zen - Calm, meditative, minimalist wisdom"
        }
        return descriptions.get(self.current_traits.style, "Unknown style")
        
    def export_traits(self) -> Dict:
        """Export current traits for persistence"""
        return {
            'style': self.current_traits.style.value,
            'traits': {
                'verbosity': self.current_traits.verbosity,
                'emotiveness': self.current_traits.emotiveness,
                'formality': self.current_traits.formality,
                'encouragement': self.current_traits.encouragement,
                'playfulness': self.current_traits.playfulness,
                'spirituality': self.current_traits.spirituality,
                'technicality': self.current_traits.technicality,
                'patience': self.current_traits.patience
            }
        }
        
    def import_traits(self, data: Dict):
        """Import traits from persistence"""
        style = PersonalityStyle(data['style'])
        self.current_traits = PersonalityTraits(
            style=style,
            **data['traits']
        )
        
    def set_learning_enabled(self, enabled: bool):
        """Enable or disable adaptive learning"""
        self.learning_enabled = enabled


# Convenience function for getting personality manager instance
_personality_manager = None

def get_personality_manager() -> PersonalityManager:
    """Get or create the global personality manager"""
    global _personality_manager
    if _personality_manager is None:
        _personality_manager = PersonalityManager()
    return _personality_manager