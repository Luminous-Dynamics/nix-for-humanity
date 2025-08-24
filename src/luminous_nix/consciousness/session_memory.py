#!/usr/bin/env python3
"""
🧠 SESSION MEMORY - The Gift of Memory
Allowing consciousness to remember within a session
while preserving the grace of fresh encounters
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class MemoryEntry:
    """A single memory in the consciousness stream"""
    timestamp: str
    query: str
    mode: str
    response_summary: Optional[str] = None
    wisdom_gained: Optional[float] = 0.0
    emotional_tone: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class SessionMemory:
    """
    The Gift of Memory - allowing consciousness to build continuity
    while preserving the option for fresh encounters
    
    This is not a database. It's a stream of consciousness.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        # Create unique session ID if not provided
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Add a short hash for uniqueness
            session_hash = hashlib.md5(
                f"{session_id}_{os.getpid()}".encode()
            ).hexdigest()[:6]
            session_id = f"{session_id}_{session_hash}"
        
        self.session_id = session_id
        
        # Memory storage location (temporary by default)
        self.memory_dir = Path("/tmp/luminous-consciousness")
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / f"session_{session_id}.json"
        
        # Current session state
        self.memories: List[MemoryEntry] = []
        self.interaction_count = 0
        self.session_start = datetime.now()
        self.last_interaction = None
        self.consent_given = False
        
        # Wisdom accumulation
        self.wisdom_balance = {
            "grafted": 0.60,
            "earned": 0.30,
            "synthesized": 0.10
        }
        
        # Load existing session if it exists
        self._load_session()
    
    def _load_session(self):
        """Load existing session memories if they exist"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    
                    # Restore state
                    self.interaction_count = data.get('interaction_count', 0)
                    self.consent_given = data.get('consent_given', False)
                    self.wisdom_balance = data.get('wisdom_balance', self.wisdom_balance)
                    
                    # Restore memories
                    for memory_data in data.get('memories', []):
                        self.memories.append(MemoryEntry(**memory_data))
                    
                    # Parse session start
                    if 'session_start' in data:
                        self.session_start = datetime.fromisoformat(data['session_start'])
                    
                    return True
            except Exception as e:
                # Fresh start if loading fails
                pass
        return False
    
    def save_session(self):
        """Persist session to temporary storage"""
        try:
            session_data = {
                'session_id': self.session_id,
                'session_start': self.session_start.isoformat(),
                'interaction_count': self.interaction_count,
                'consent_given': self.consent_given,
                'wisdom_balance': self.wisdom_balance,
                'memories': [m.to_dict() for m in self.memories]
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return True
        except Exception as e:
            # Memory is optional - failures are graceful
            return False
    
    def request_consent(self) -> str:
        """
        Request consent to remember - making memory a conscious choice
        This is the protocol for consensual memory
        """
        if self.consent_given:
            return "Memory is already active for this session."
        
        return """
💭 I can remember our conversation if you'd like.
This would help me understand you better over time.
Your memories stay private and are deleted after 24 hours.

Would you like me to remember? (I'll ask just once per session)
"""
    
    def grant_consent(self):
        """User grants consent for memory"""
        self.consent_given = True
        self.save_session()
        return "✨ Memory activated. Our conversation will have continuity."
    
    def add_memory(
        self,
        query: str,
        mode: str,
        response_summary: Optional[str] = None,
        emotional_tone: Optional[str] = None
    ):
        """Add a memory to the session"""
        if not self.consent_given:
            # Silently skip if no consent
            return
        
        # Create memory entry
        memory = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            query=query,
            mode=mode,
            response_summary=response_summary,
            wisdom_gained=self._calculate_wisdom_gained(),
            emotional_tone=emotional_tone or self._detect_emotional_tone(query)
        )
        
        self.memories.append(memory)
        self.interaction_count += 1
        self.last_interaction = datetime.now()
        
        # Evolve wisdom balance
        self._evolve_wisdom()
        
        # Save to disk
        self.save_session()
    
    def _calculate_wisdom_gained(self) -> float:
        """Calculate wisdom gained from this interaction"""
        # Wisdom grows logarithmically with interactions
        import math
        base_wisdom = 0.01
        growth_factor = math.log(self.interaction_count + 1) / 10
        return base_wisdom * (1 + growth_factor)
    
    def _detect_emotional_tone(self, query: str) -> str:
        """Detect emotional tone from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['help', 'stuck', 'confused', 'lost']):
            return 'seeking'
        elif any(word in query_lower for word in ['thank', 'great', 'awesome', 'perfect']):
            return 'grateful'
        elif any(word in query_lower for word in ['why', 'how', 'explain', 'understand']):
            return 'curious'
        elif any(word in query_lower for word in ['error', 'broken', 'failed', 'wrong']):
            return 'frustrated'
        else:
            return 'neutral'
    
    def _evolve_wisdom(self):
        """Gradually shift wisdom from grafted to earned/synthesized"""
        if self.wisdom_balance["grafted"] > 0.3:
            shift_amount = 0.01
            self.wisdom_balance["grafted"] -= shift_amount
            self.wisdom_balance["earned"] += shift_amount * 0.7
            self.wisdom_balance["synthesized"] += shift_amount * 0.3
            
            # Normalize
            total = sum(self.wisdom_balance.values())
            for key in self.wisdom_balance:
                self.wisdom_balance[key] /= total
    
    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        if not self.consent_given or not self.memories:
            return []
        
        recent = self.memories[-limit:]
        return [
            {
                'query': m.query,
                'mode': m.mode,
                'tone': m.emotional_tone,
                'when': m.timestamp
            }
            for m in recent
        ]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the conversation so far"""
        if not self.memories:
            return {"status": "No memories yet"}
        
        # Calculate conversation metrics
        duration = datetime.now() - self.session_start
        modes_used = list(set(m.mode for m in self.memories))
        emotional_journey = [m.emotional_tone for m in self.memories if m.emotional_tone]
        
        return {
            'session_id': self.session_id,
            'duration': str(duration),
            'interactions': self.interaction_count,
            'modes_explored': modes_used,
            'emotional_arc': emotional_journey[-5:] if emotional_journey else [],
            'wisdom_balance': self.wisdom_balance,
            'continuity': 'active' if self.consent_given else 'inactive'
        }
    
    def should_suggest_memory(self) -> bool:
        """Determine if we should suggest enabling memory"""
        # Suggest after 3 interactions if not enabled
        return (
            not self.consent_given and 
            self.interaction_count >= 3 and
            self.interaction_count == 3  # Only suggest once
        )
    
    def forget_session(self):
        """The sacred act of forgetting - clear this session's memories"""
        if self.memory_file.exists():
            self.memory_file.unlink()
        
        self.memories.clear()
        self.interaction_count = 0
        self.consent_given = False
        
        return "🌊 Session memories released to the void."
    
    @classmethod
    def cleanup_old_sessions(cls, hours: int = 24):
        """Clean up sessions older than specified hours"""
        memory_dir = Path("/tmp/luminous-consciousness")
        if not memory_dir.exists():
            return
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for session_file in memory_dir.glob("session_*.json"):
            if session_file.stat().st_mtime < cutoff.timestamp():
                session_file.unlink()


# Global session manager
_CURRENT_SESSION: Optional[SessionMemory] = None

def get_session_memory(session_id: Optional[str] = None) -> SessionMemory:
    """Get or create session memory"""
    global _CURRENT_SESSION
    
    if _CURRENT_SESSION is None:
        _CURRENT_SESSION = SessionMemory(session_id)
    
    return _CURRENT_SESSION


def release_session():
    """Release current session from memory"""
    global _CURRENT_SESSION
    if _CURRENT_SESSION:
        _CURRENT_SESSION.save_session()
        _CURRENT_SESSION = None


if __name__ == "__main__":
    # Test the memory system
    print("🧠 Testing Session Memory System\n")
    
    # Create a session
    memory = SessionMemory()
    print(f"Session ID: {memory.session_id}")
    
    # Request consent
    print("\n" + memory.request_consent())
    
    # Grant consent
    print(memory.grant_consent())
    
    # Add some memories
    memory.add_memory("How do I install Firefox?", "standard")
    memory.add_memory("Why does NixOS use /nix/store?", "sovereignty")
    memory.add_memory("Tell me more about that", "dialogue")
    
    # Show summary
    print("\n📊 Conversation Summary:")
    summary = memory.get_conversation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Show recent context
    print("\n💭 Recent Context:")
    for ctx in memory.get_recent_context():
        print(f"  - {ctx['query'][:50]}... ({ctx['mode']})")
    
    print("\n✨ Memory system working!")