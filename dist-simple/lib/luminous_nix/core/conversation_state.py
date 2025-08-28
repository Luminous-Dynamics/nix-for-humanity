"""
State management for multi-turn conversations with context
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

class ConversationTopic(Enum):
    """Topics of conversation"""
    INSTALLATION = "installation"
    TROUBLESHOOTING = "troubleshooting"
    CONFIGURATION = "configuration"
    SEARCH = "search"
    SYSTEM_MANAGEMENT = "system_management"
    LEARNING = "learning"
    GENERAL = "general"

@dataclass
class Turn:
    """A single turn in the conversation"""
    query: str
    response: str
    timestamp: datetime
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    topic: ConversationTopic = ConversationTopic.GENERAL
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'query': self.query,
            'response': self.response[:500],  # Truncate long responses
            'timestamp': self.timestamp.isoformat(),
            'intent': self.intent,
            'entities': self.entities,
            'success': self.success,
            'topic': self.topic.value
        }

@dataclass
class UserProfile:
    """User profile with preferences and patterns"""
    user_id: str
    skill_level: str = "beginner"  # beginner, intermediate, expert
    preferred_verbosity: str = "normal"  # minimal, normal, detailed
    common_tasks: List[str] = field(default_factory=list)
    installed_packages: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    last_active: datetime = field(default_factory=datetime.now)
    
    def update_activity(self):
        """Update last activity time"""
        self.last_active = datetime.now()

class ConversationState:
    """
    Manages conversation state for multi-turn interactions
    
    Features:
    - Conversation history tracking
    - Context extraction and maintenance
    - User preference learning
    - Topic tracking
    - Session management
    """
    
    def __init__(self, state_dir: Optional[Path] = None, session_id: Optional[str] = None):
        """Initialize conversation state manager"""
        self.state_dir = state_dir or (Path.home() / ".local/state/luminous-nix/conversations")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Session management
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.state_dir / f"session_{self.session_id}.json"
        
        # Conversation state
        self.history: List[Turn] = []
        self.current_topic: ConversationTopic = ConversationTopic.GENERAL
        self.context: Dict[str, Any] = {}
        
        # User profile
        self.user_profile = self._load_user_profile()
        
        # Working memory (recent context)
        self.working_memory = {
            'last_package': None,
            'last_command': None,
            'last_error': None,
            'last_search': None,
            'current_task': None,
            'pending_confirmations': []
        }
        
        # Load existing session if available
        if self.session_file.exists():
            self._load_session()
    
    def add_turn(
        self,
        query: str,
        response: str,
        intent: Optional[str] = None,
        entities: Optional[Dict] = None,
        success: bool = True
    ) -> Turn:
        """
        Add a conversation turn
        
        Args:
            query: User's query
            response: System's response
            intent: Detected intent
            entities: Extracted entities
            success: Whether the action succeeded
            
        Returns:
            The created Turn object
        """
        # Detect topic
        topic = self._detect_topic(query, intent)
        
        # Create turn
        turn = Turn(
            query=query,
            response=response,
            timestamp=datetime.now(),
            intent=intent,
            entities=entities or {},
            success=success,
            topic=topic
        )
        
        # Add to history
        self.history.append(turn)
        
        # Update context
        self._update_context(turn)
        
        # Update user profile
        self._update_user_profile(turn)
        
        # Save session
        self._save_session()
        
        return turn
    
    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """
        Get relevant context for a query
        
        Args:
            query: The user's query
            
        Returns:
            Context dictionary with relevant information
        """
        context = {
            'session_id': self.session_id,
            'turn_number': len(self.history) + 1,
            'current_topic': self.current_topic.value,
            'user_skill': self.user_profile.skill_level,
            'preferred_verbosity': self.user_profile.preferred_verbosity
        }
        
        # Add recent history (last 3 turns)
        if self.history:
            context['recent_history'] = [
                {
                    'query': turn.query,
                    'intent': turn.intent,
                    'entities': turn.entities
                }
                for turn in self.history[-3:]
            ]
        
        # Add working memory
        context['working_memory'] = {
            k: v for k, v in self.working_memory.items()
            if v is not None
        }
        
        # Add relevant user preferences
        if self.user_profile.preferences:
            context['user_preferences'] = self.user_profile.preferences
        
        # Check for follow-up patterns
        context['is_followup'] = self._is_followup(query)
        
        # Check for corrections
        context['is_correction'] = self._is_correction(query)
        
        return context
    
    def get_clarification_needed(self) -> Optional[str]:
        """
        Check if clarification is needed based on recent context
        
        Returns:
            Clarification question if needed, None otherwise
        """
        if not self.history:
            return None
        
        last_turn = self.history[-1]
        
        # Check if last turn had ambiguous entities
        if last_turn.entities.get('ambiguous'):
            return f"Did you mean {last_turn.entities.get('ambiguous')}?"
        
        # Check if last command failed and needs more info
        if not last_turn.success and last_turn.intent == 'install':
            if 'package' not in last_turn.entities:
                return "Which package would you like to install?"
        
        # Check for incomplete tasks
        if self.working_memory.get('current_task') == 'configuring':
            if not self.working_memory.get('config_file'):
                return "Which configuration file would you like to edit?"
        
        return None
    
    def resolve_pronouns(self, query: str) -> str:
        """
        Resolve pronouns using context
        
        Args:
            query: Query potentially containing pronouns
            
        Returns:
            Query with pronouns resolved
        """
        query_lower = query.lower()
        resolved = query
        
        # Resolve "it" to last package
        if 'it' in query_lower and self.working_memory.get('last_package'):
            resolved = resolved.replace('it', self.working_memory['last_package'])
            resolved = resolved.replace('It', self.working_memory['last_package'])
        
        # Resolve "that" to last search/command
        if 'that' in query_lower:
            if self.working_memory.get('last_search'):
                resolved = resolved.replace('that', self.working_memory['last_search'])
            elif self.working_memory.get('last_command'):
                resolved = resolved.replace('that', self.working_memory['last_command'])
        
        # Resolve "the same" to last action
        if 'the same' in query_lower and self.history:
            last_intent = self.history[-1].intent
            if last_intent:
                resolved = resolved.replace('the same', last_intent)
        
        return resolved
    
    def suggest_next_action(self) -> Optional[str]:
        """
        Suggest next action based on conversation flow
        
        Returns:
            Suggested action or None
        """
        if not self.history:
            return None
        
        last_turn = self.history[-1]
        
        # After successful installation, suggest testing
        if last_turn.intent == 'install' and last_turn.success:
            package = last_turn.entities.get('package')
            if package:
                return f"Would you like to test {package}?"
        
        # After search, suggest installation
        if last_turn.intent == 'search' and last_turn.entities.get('results'):
            return "Would you like to install any of these packages?"
        
        # After error, suggest troubleshooting
        if not last_turn.success:
            return "Would you like help troubleshooting this issue?"
        
        # After configuration, suggest verification
        if last_turn.topic == ConversationTopic.CONFIGURATION:
            return "Would you like to verify the configuration?"
        
        return None
    
    def _detect_topic(self, query: str, intent: Optional[str]) -> ConversationTopic:
        """Detect conversation topic from query and intent"""
        query_lower = query.lower()
        
        if intent in ['install', 'remove', 'update']:
            return ConversationTopic.INSTALLATION
        elif intent == 'search' or 'search' in query_lower:
            return ConversationTopic.SEARCH
        elif any(word in query_lower for word in ['error', 'problem', 'issue', 'broken', 'fix']):
            return ConversationTopic.TROUBLESHOOTING
        elif any(word in query_lower for word in ['config', 'setting', 'option', 'configure']):
            return ConversationTopic.CONFIGURATION
        elif any(word in query_lower for word in ['manage', 'system', 'generation', 'rollback']):
            return ConversationTopic.SYSTEM_MANAGEMENT
        elif any(word in query_lower for word in ['how', 'what', 'why', 'explain', 'learn']):
            return ConversationTopic.LEARNING
        else:
            return ConversationTopic.GENERAL
    
    def _update_context(self, turn: Turn):
        """Update context based on turn"""
        # Update working memory
        if turn.entities.get('package'):
            self.working_memory['last_package'] = turn.entities['package']
        
        if turn.intent:
            self.working_memory['last_command'] = turn.intent
        
        if turn.intent == 'search' and turn.entities.get('term'):
            self.working_memory['last_search'] = turn.entities['term']
        
        if not turn.success and turn.response:
            self.working_memory['last_error'] = turn.response[:200]
        
        # Update current topic
        self.current_topic = turn.topic
        
        # Track current task
        if turn.topic == ConversationTopic.INSTALLATION:
            self.working_memory['current_task'] = 'installing'
        elif turn.topic == ConversationTopic.CONFIGURATION:
            self.working_memory['current_task'] = 'configuring'
        elif turn.topic == ConversationTopic.TROUBLESHOOTING:
            self.working_memory['current_task'] = 'troubleshooting'
    
    def _update_user_profile(self, turn: Turn):
        """Update user profile based on conversation"""
        self.user_profile.update_activity()
        
        # Track common tasks
        if turn.intent and turn.success:
            if turn.intent not in self.user_profile.common_tasks:
                self.user_profile.common_tasks.append(turn.intent)
                if len(self.user_profile.common_tasks) > 10:
                    self.user_profile.common_tasks.pop(0)
        
        # Track installed packages
        if turn.intent == 'install' and turn.success and turn.entities.get('package'):
            package = turn.entities['package']
            if package not in self.user_profile.installed_packages:
                self.user_profile.installed_packages.append(package)
        
        # Detect skill level from questions
        if turn.topic == ConversationTopic.LEARNING:
            # Simple questions indicate beginner
            if any(word in turn.query.lower() for word in ['what is', 'how do i', 'basic']):
                self.user_profile.skill_level = "beginner"
            # Complex questions indicate advanced
            elif any(word in turn.query.lower() for word in ['optimize', 'customize', 'advanced']):
                self.user_profile.skill_level = "expert"
        
        # Save profile
        self._save_user_profile()
    
    def _is_followup(self, query: str) -> bool:
        """Check if query is a follow-up to previous turn"""
        if not self.history:
            return False
        
        query_lower = query.lower()
        
        # Check for follow-up indicators
        followup_indicators = [
            'yes', 'no', 'ok', 'sure', 'please',
            'do it', 'go ahead', 'proceed',
            'also', 'and', 'then', 'next',
            'what about', 'how about'
        ]
        
        return any(query_lower.startswith(ind) for ind in followup_indicators)
    
    def _is_correction(self, query: str) -> bool:
        """Check if query is correcting previous input"""
        query_lower = query.lower()
        
        correction_indicators = [
            'no i meant', 'actually', 'sorry',
            'i mean', 'not that', 'wrong',
            'mistake', 'instead'
        ]
        
        return any(ind in query_lower for ind in correction_indicators)
    
    def _save_session(self):
        """Save current session to file"""
        session_data = {
            'session_id': self.session_id,
            'started': self.history[0].timestamp.isoformat() if self.history else datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'turns': [turn.to_dict() for turn in self.history[-50:]],  # Keep last 50 turns
            'working_memory': self.working_memory,
            'current_topic': self.current_topic.value
        }
        
        self.session_file.write_text(json.dumps(session_data, indent=2))
    
    def _load_session(self):
        """Load session from file"""
        try:
            data = json.loads(self.session_file.read_text())
            
            # Restore working memory
            self.working_memory.update(data.get('working_memory', {}))
            
            # Restore topic
            if 'current_topic' in data:
                self.current_topic = ConversationTopic(data['current_topic'])
            
            # Note: We don't restore full history to keep memory usage low
            # But it's available in the file if needed
            
        except Exception:
            pass
    
    def _save_user_profile(self):
        """Save user profile"""
        profile_file = self.state_dir / "user_profile.json"
        profile_data = {
            'user_id': self.user_profile.user_id,
            'skill_level': self.user_profile.skill_level,
            'preferred_verbosity': self.user_profile.preferred_verbosity,
            'common_tasks': self.user_profile.common_tasks,
            'installed_packages': self.user_profile.installed_packages[-100:],  # Keep last 100
            'preferences': self.user_profile.preferences,
            'last_active': self.user_profile.last_active.isoformat()
        }
        
        profile_file.write_text(json.dumps(profile_data, indent=2))
    
    def _load_user_profile(self) -> UserProfile:
        """Load or create user profile"""
        profile_file = self.state_dir / "user_profile.json"
        
        if profile_file.exists():
            try:
                data = json.loads(profile_file.read_text())
                return UserProfile(
                    user_id=data.get('user_id', 'default'),
                    skill_level=data.get('skill_level', 'beginner'),
                    preferred_verbosity=data.get('preferred_verbosity', 'normal'),
                    common_tasks=data.get('common_tasks', []),
                    installed_packages=data.get('installed_packages', []),
                    preferences=data.get('preferences', {}),
                    last_active=datetime.fromisoformat(data.get('last_active', datetime.now().isoformat()))
                )
            except Exception:
                pass
        
        # Create new profile
        return UserProfile(user_id='default')