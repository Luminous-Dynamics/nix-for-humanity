#!/usr/bin/env python3
"""
🔱 Trinity Event Emitter - Sacred Council events stored in Data Trinity
Replaces JSON file storage with multi-dimensional database storage
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import hashlib

# Import the Data Trinity
import sys
sys.path.append(str(Path(__file__).parent.parent))
from persistence.trinity_store import TrinityStore, ConceptRelation

logger = logging.getLogger(__name__)


@dataclass
class CouncilEvent:
    """Enhanced Council Event with Trinity integration"""
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    session_id: str
    sequence: int
    risk_level: Optional[str] = None
    command: Optional[str] = None
    verdict: Optional[str] = None
    

class TrinityEventEmitter:
    """
    Enhanced event emitter that stores Sacred Council events in the Data Trinity.
    
    This provides:
    - Temporal storage in DuckDB for time-series analysis
    - Semantic storage in ChromaDB for pattern matching
    - Relational storage in Kùzu for risk relationships
    """
    
    def __init__(self, trinity_store: Optional[TrinityStore] = None):
        """Initialize with Data Trinity connection"""
        self.trinity = trinity_store or TrinityStore()
        self.session_id = f"session_{int(datetime.now().timestamp())}"
        self.sequence = 0
        
        # Also keep JSON file for backward compatibility
        self.events_file = Path("/tmp/sacred-council-events.json")
        
        logger.info(f"🔱 Trinity Event Emitter initialized for session {self.session_id}")
    
    def emit(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Emit an event to the Data Trinity.
        
        Stores in:
        - DuckDB: Temporal sequence and analytics
        - ChromaDB: Command patterns and similarity
        - Kùzu: Risk relationships and patterns
        """
        self.sequence += 1
        
        # Create event
        event = CouncilEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            data=data,
            session_id=self.session_id,
            sequence=self.sequence,
            risk_level=data.get('risk_level'),
            command=data.get('command'),
            verdict=data.get('verdict')
        )
        
        # Generate event ID
        event_id = hashlib.sha256(
            f"{event.timestamp}{event.session_id}{event.sequence}".encode()
        ).hexdigest()[:16]
        
        # Store in temporal database (DuckDB)
        self._store_temporal(event_id, event)
        
        # Store in semantic database (ChromaDB) if it's a command
        if event.command:
            self._store_semantic(event)
        
        # Update knowledge graph (Kùzu) if there's a risk assessment
        if event.risk_level and event.command:
            self._update_graph(event)
        
        # Also write to JSON for backward compatibility
        self._write_to_json(event)
        
        logger.debug(f"📝 Emitted {event_type} to Trinity (ID: {event_id})")
        return event_id
    
    def _store_temporal(self, event_id: str, event: CouncilEvent):
        """Store event in temporal database for time-series analysis"""
        try:
            self.trinity.temporal.conn.execute("""
                INSERT INTO council_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                event_id,
                event.timestamp,
                event.session_id,
                event.event_type,
                event.risk_level or "UNKNOWN",
                event.command or "",
                event.verdict or "",
                json.dumps(event.data.get('alternatives', [])),
                json.dumps(event.data.get('reasoning', {}))
            ])
        except Exception as e:
            logger.warning(f"Failed to store in temporal DB: {e}")
    
    def _store_semantic(self, event: CouncilEvent):
        """Store command pattern in semantic database for similarity matching"""
        try:
            # Store the command pattern
            self.trinity.semantic.store_command_pattern(
                command=event.command,
                intent=event.data.get('intent', 'unknown'),
                success=event.verdict != "BLOCK"
            )
            
            # If there are alternatives, store them too
            alternatives = event.data.get('alternatives', [])
            for alt in alternatives:
                self.trinity.semantic.store_command_pattern(
                    command=alt,
                    intent=f"safe_alternative_to_{event.data.get('intent', 'unknown')}",
                    success=True
                )
        except Exception as e:
            logger.warning(f"Failed to store in semantic DB: {e}")
    
    def _update_graph(self, event: CouncilEvent):
        """Update knowledge graph with risk relationships"""
        try:
            # Add risk level as a concept
            risk_concept = f"risk_{event.risk_level.lower()}"
            self.trinity.relational.add_concept(
                name=risk_concept,
                description=f"Commands with {event.risk_level} risk level",
                difficulty={"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "SAFE": 1}.get(event.risk_level, 1),
                category="risk"
            )
            
            # Add command category as a concept
            command_type = self._extract_command_type(event.command)
            if command_type:
                self.trinity.relational.add_concept(
                    name=command_type,
                    description=f"Commands of type: {command_type}",
                    difficulty=2,
                    category="command_type"
                )
                
                # Create relationship between command type and risk
                self.trinity.relational.add_relationship(
                    ConceptRelation(
                        from_concept=command_type,
                        to_concept=risk_concept,
                        relation_type="has_risk",
                        strength=0.8
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to update graph: {e}")
    
    def _extract_command_type(self, command: str) -> Optional[str]:
        """Extract the type of command for categorization"""
        if "rm" in command:
            return "deletion_command"
        elif "install" in command or "nix-env -i" in command:
            return "installation_command"
        elif "nixos-rebuild" in command:
            return "system_rebuild"
        elif "nix-collect-garbage" in command:
            return "garbage_collection"
        elif "chmod" in command:
            return "permission_change"
        elif "passwd" in command:
            return "authentication_change"
        else:
            return None
    
    def _write_to_json(self, event: CouncilEvent):
        """Write to JSON file for backward compatibility"""
        try:
            # Read existing events
            if self.events_file.exists():
                with open(self.events_file, 'r') as f:
                    events = json.load(f)
            else:
                events = []
            
            # Add new event
            event_dict = {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "data": event.data,
                "session_id": event.session_id,
                "sequence": event.sequence
            }
            events.append(event_dict)
            
            # Write back
            with open(self.events_file, 'w') as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to write JSON backup: {e}")
    
    def emit_check_started(self, command: str, context: Dict[str, Any] = None):
        """Emit when command checking starts"""
        return self.emit("check_started", {
            "command": command,
            "context": context or {},
            "stage": "initialization"
        })
    
    def emit_pattern_checked(self, command: str, risk_level: str, pattern: Optional[str], reason: str):
        """Emit pattern check results"""
        return self.emit("pattern_checked", {
            "command": command,
            "risk_level": risk_level,
            "pattern_matched": pattern,
            "reason": reason,
            "stage": "pattern_analysis"
        })
    
    def emit_deliberation_started(self, command: str, risk_level: str):
        """Emit when Sacred Council begins deliberation"""
        return self.emit("deliberation_started", {
            "command": command,
            "risk_level": risk_level,
            "council_members": ["mind", "heart", "conscience"],
            "stage": "council_deliberation"
        })
    
    def emit_member_thinking(self, member: str, thought: str, analysis: str):
        """Emit individual council member's thoughts"""
        return self.emit(f"{member}_thinking", {
            "member": member,
            "thought": thought,
            "analysis": analysis,
            "stage": f"{member}_analysis"
        })
    
    def emit_alternatives_generated(self, alternatives: List[str]):
        """Emit when safe alternatives are generated"""
        return self.emit("alternatives_generated", {
            "alternatives": alternatives,
            "count": len(alternatives),
            "stage": "solution_generation"
        })
    
    def emit_verdict_reached(self, verdict: str, risk_level: str, safe: bool, reason: str):
        """Emit final verdict"""
        return self.emit("verdict_reached", {
            "verdict": verdict,
            "risk_level": risk_level,
            "safe": safe,
            "reason": reason,
            "stage": "final_judgment"
        })
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get analytics for the current session from Trinity"""
        try:
            # Query temporal database for session stats
            result = self.trinity.temporal.conn.execute("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(DISTINCT command) as unique_commands,
                    COUNT(CASE WHEN risk_level = 'CRITICAL' THEN 1 END) as critical_count,
                    COUNT(CASE WHEN risk_level = 'HIGH' THEN 1 END) as high_count,
                    COUNT(CASE WHEN risk_level = 'MEDIUM' THEN 1 END) as medium_count,
                    COUNT(CASE WHEN risk_level = 'LOW' THEN 1 END) as low_count,
                    COUNT(CASE WHEN risk_level = 'SAFE' THEN 1 END) as safe_count,
                    COUNT(CASE WHEN verdict = 'BLOCK' THEN 1 END) as blocked_count,
                    COUNT(CASE WHEN verdict = 'ALLOW' THEN 1 END) as allowed_count
                FROM council_events
                WHERE session_id = ?
            """, [self.session_id]).fetchone()
            
            if result:
                return {
                    "total_events": result[0],
                    "unique_commands": result[1],
                    "risk_breakdown": {
                        "CRITICAL": result[2],
                        "HIGH": result[3],
                        "MEDIUM": result[4],
                        "LOW": result[5],
                        "SAFE": result[6]
                    },
                    "verdicts": {
                        "BLOCKED": result[7],
                        "ALLOWED": result[8]
                    }
                }
        except Exception as e:
            logger.warning(f"Failed to get analytics: {e}")
        
        return {}
    
    def close(self):
        """Close Trinity connections"""
        self.trinity.close()


# Export the enhanced emitter
__all__ = ['TrinityEventEmitter', 'CouncilEvent']