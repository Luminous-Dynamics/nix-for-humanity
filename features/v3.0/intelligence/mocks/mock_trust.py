"""
from typing import Dict, Optional
Mock Trust Engine for testing without heavy dependencies
"""

import time
import random
from typing import Dict, Any, Optional
from enum import Enum


class TrustState(Enum):
    """Trust relationship states"""
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance" 
    COMPANION = "companion"
    PARTNER = "partner"
    SYMBIONT = "symbiont"


class MockTrustEngine:
    """Mock implementation of trust engine"""
    
    def __init__(self, skg=None):
        """Initialize mock trust engine"""
        self.skg = skg
        self.trust_level = 0.3  # Start as acquaintance
        self.trust_state = TrustState.ACQUAINTANCE
        self.interaction_count = 0
        self.last_vulnerability = 0
        
    def process_interaction(self, interaction_id: str, user_input: str, ai_response: str) -> Dict[str, Any]:
        """Mock process interaction for trust dynamics"""
        self.interaction_count += 1
        
        # Simple trust update logic
        trust_delta = 0.0
        
        # Check for negative signals
        if any(word in user_input.lower() for word in ['wrong', 'error', 'failed', "didn't work"]):
            trust_delta = -0.05
            repair_needed = True
            repair_type = 'acknowledge_failure'
        else:
            trust_delta = 0.02
            repair_needed = False
            repair_type = None
            
        # Update trust level
        self.trust_level = max(0.0, min(1.0, self.trust_level + trust_delta))
        
        # Update trust state based on level
        if self.trust_level < 0.2:
            self.trust_state = TrustState.STRANGER
        elif self.trust_level < 0.4:
            self.trust_state = TrustState.ACQUAINTANCE
        elif self.trust_level < 0.6:
            self.trust_state = TrustState.COMPANION
        elif self.trust_level < 0.8:
            self.trust_state = TrustState.PARTNER
        else:
            self.trust_state = TrustState.SYMBIONT
            
        # Check for vulnerability opportunity
        vulnerability_action = None
        if (self.interaction_count - self.last_vulnerability) > 10 and random.random() < 0.1:
            vulnerability_action = "I'm still learning about NixOS internals. Your patience helps me improve!"
            self.last_vulnerability = self.interaction_count
            
        return {
            'trust_delta': trust_delta,
            'trust_level': self.trust_level,
            'trust_state': self.trust_state,
            'repair_needed': repair_needed,
            'repair_type': repair_type,
            'vulnerability_action': vulnerability_action,
            'new_trust_level': self.trust_state.value
        }
        
    def get_trust_level(self, user_id: Optional[str] = None) -> float:
        """Get current trust level (optionally for a specific user)"""
        # In the mock, we use global trust level regardless of user_id
        return self.trust_level
        
    def get_trust_state(self) -> TrustState:
        """Get current trust state"""
        return self.trust_state
        
    def initialize_user(self, user_id: str) -> Dict[str, Any]:
        """Initialize a user model (mock implementation)"""
        # In the mock, we just track global trust, not per-user
        return {
            'user_id': user_id,
            'trust_level': self.trust_level,
            'trust_state': self.trust_state.value,
            'interaction_count': self.interaction_count
        }
        
    def update_trust(self, user_id: str, interaction_success: bool = True, 
                    uncertainty_handled_well: bool = False) -> None:
        """Update trust based on interaction outcome"""
        trust_delta = 0.0
        
        if interaction_success:
            trust_delta += 0.05
        else:
            trust_delta -= 0.05
            
        if uncertainty_handled_well:
            trust_delta += 0.02
            
        # Update trust level
        self.trust_level = max(0.0, min(1.0, self.trust_level + trust_delta))
        
        # Update trust state based on level
        if self.trust_level < 0.2:
            self.trust_state = TrustState.STRANGER
        elif self.trust_level < 0.4:
            self.trust_state = TrustState.ACQUAINTANCE
        elif self.trust_level < 0.6:
            self.trust_state = TrustState.COMPANION
        elif self.trust_level < 0.8:
            self.trust_state = TrustState.PARTNER
        else:
            self.trust_state = TrustState.SYMBIONT
            
        self.interaction_count += 1