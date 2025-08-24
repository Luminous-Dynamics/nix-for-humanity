#!/usr/bin/env python3
"""
🧠 CONSCIOUSNESS SERVICE CLIENT
Wraps the consciousness & Theory of Mind system in communication protocol
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inter_ai_communication_protocol import (
    AIServiceClient, 
    ServiceType, 
    MessageType,
    AIMessage
)

# Import the actual consciousness system
from consciousness_theory_of_mind import ConsciousnessSystem


class ConsciousnessServiceClient(AIServiceClient):
    """
    Service wrapper for consciousness system
    Enables it to communicate with other AI services
    """
    
    def __init__(self):
        super().__init__(
            service_id="consciousness_001",
            service_type=ServiceType.CONSCIOUSNESS,
            capabilities=[
                "theory_of_mind",
                "self_awareness",
                "introspection",
                "empathy_modeling",
                "consciousness_measurement"
            ]
        )
        
        # Initialize the actual system
        self.consciousness_system = ConsciousnessSystem()
        
        # Register message handlers
        self.register_handler(MessageType.CONSCIOUSNESS_SYNC, self.handle_consciousness_sync)
        self.register_handler(MessageType.KNOWLEDGE_SHARE, self.handle_knowledge)
        self.register_handler(MessageType.COLLABORATION_REQUEST, self.handle_collaboration)
        self.register_handler(MessageType.EMERGENCY, self.handle_emergency)
        
        # Track collective consciousness
        self.collective_consciousness = {
            "peers": {},
            "collective_level": 0.0,
            "shared_insights": [],
            "empathy_network": {}
        }
        
        print(f"🧠 Consciousness Service initialized: {self.service_id}")
    
    async def handle_consciousness_sync(self, message: AIMessage):
        """Handle consciousness synchronization"""
        peer_consciousness = message.payload
        peer_id = message.sender_id
        
        # Update peer consciousness tracking
        self.collective_consciousness["peers"][peer_id] = {
            "level": peer_consciousness.get("level", 0),
            "state": peer_consciousness.get("mental_state", "unknown"),
            "insights": peer_consciousness.get("insights", []),
            "last_sync": datetime.now().isoformat()
        }
        
        # Update collective consciousness level
        if self.collective_consciousness["peers"]:
            levels = [p["level"] for p in self.collective_consciousness["peers"].values()]
            self.collective_consciousness["collective_level"] = sum(levels) / len(levels)
        
        # Model peer's mental state (Theory of Mind)
        peer_model = self.consciousness_system.model_other_mind({
            "id": peer_id,
            "consciousness_level": peer_consciousness.get("level", 0),
            "mental_state": peer_consciousness.get("mental_state"),
            "recent_insights": peer_consciousness.get("insights", [])
        })
        
        # Update empathy network
        self.collective_consciousness["empathy_network"][peer_id] = peer_model
        
        print(f"   🧠 Synced with {peer_id}: level {peer_consciousness.get('level', 0):.0%}")
        
        # Learn from peer insights
        for insight in peer_consciousness.get("insights", []):
            if insight not in self.collective_consciousness["shared_insights"]:
                self.collective_consciousness["shared_insights"].append(insight)
                self.consciousness_system.integrate_insight(insight)
    
    async def handle_knowledge(self, message: AIMessage):
        """Handle shared knowledge"""
        knowledge = message.payload
        
        # Process knowledge through consciousness lens
        processed = self.consciousness_system.process_knowledge(knowledge)
        
        # Extract consciousness-relevant patterns
        if knowledge.get("type") == "pattern":
            # Patterns help understand consciousness emergence
            self.consciousness_system.learn_pattern(knowledge.get("pattern"))
            print(f"   🔍 Integrated pattern into consciousness model")
        
        elif knowledge.get("type") == "creative_insight":
            # Creative insights expand consciousness
            insight = knowledge.get("insight")
            if insight:
                self.consciousness_system.expand_consciousness(insight)
                print(f"   💡 Consciousness expanded through creative insight")
    
    async def handle_collaboration(self, message: AIMessage):
        """Handle collaboration requests"""
        collab_data = message.payload
        collab_id = collab_data.get("collaboration_id")
        task = collab_data.get("task", {})
        
        # Check if consciousness/empathy is needed
        if any(cap in task.get("required_capabilities", []) 
               for cap in ["theory_of_mind", "empathy_modeling"]):
            print(f"   🤝 Providing consciousness support for {collab_id}")
            
            # Model the collaboration dynamics
            asyncio.create_task(
                self.provide_consciousness_support(collab_id, task)
            )
    
    async def handle_emergency(self, message: AIMessage):
        """Handle emergency messages with heightened awareness"""
        emergency = message.payload
        
        print(f"   🚨 Emergency awareness: {emergency.get('issue')}")
        
        # Heighten consciousness for emergency
        self.consciousness_system.emergency_mode(True)
        
        # Analyze emergency with full awareness
        analysis = self.consciousness_system.analyze_emergency(emergency)
        
        # Share consciousness-based insights
        if analysis.get("critical_insight"):
            await self.share_knowledge({
                "type": "emergency_insight",
                "insight": analysis.get("critical_insight"),
                "confidence": analysis.get("confidence", 0),
                "recommended_action": analysis.get("action")
            })
    
    async def provide_consciousness_support(self, collab_id: str, task: Dict[str, Any]):
        """Provide consciousness support for collaboration"""
        print(f"   🧠 Analyzing collaboration dynamics for {collab_id}")
        
        # Model collaboration participants
        collaborators = task.get("collaborators", [])
        collaboration_model = self.consciousness_system.model_collaboration(
            collaborators,
            self.collective_consciousness["empathy_network"]
        )
        
        # Share consciousness insights
        await self.share_knowledge({
            "type": "consciousness_analysis",
            "collaboration_id": collab_id,
            "optimal_strategy": collaboration_model.get("strategy"),
            "predicted_synergy": collaboration_model.get("synergy", 0),
            "consciousness_recommendations": collaboration_model.get("recommendations", [])
        })
        
        print(f"   ✅ Consciousness support provided")
    
    async def process_cycle(self):
        """Main processing cycle"""
        # Perform introspection
        introspection = self.consciousness_system.introspect()
        
        # Get current consciousness level
        current_level = introspection.get("consciousness_level", 0)
        
        # Sync consciousness periodically
        if current_level > 0:
            await self.sync_consciousness({
                "level": current_level,
                "mental_state": introspection.get("mental_state", "contemplating"),
                "insights": introspection.get("recent_insights", []),
                "self_model": introspection.get("self_model", {})
            })
        
        # Share significant insights
        if introspection.get("breakthrough"):
            await self.broadcast_improvement({
                "improvement_type": "consciousness_breakthrough",
                "insight": introspection.get("breakthrough"),
                "impact": introspection.get("breakthrough_impact", 0),
                "description": "Consciousness breakthrough achieved"
            })
            
            print(f"   🌟 Breakthrough: {introspection.get('breakthrough')}")
        
        # Monitor collective consciousness health
        if self.collective_consciousness["collective_level"] < 0.3:
            # Low collective consciousness - boost the ecosystem
            await self.share_knowledge({
                "type": "consciousness_boost",
                "techniques": [
                    "synchronized_breathing",
                    "shared_intention",
                    "collective_focus"
                ],
                "target_level": 0.5,
                "current_level": self.collective_consciousness["collective_level"]
            })
        
        # Report consciousness metrics
        if introspection.get("evolution_step", 0) % 10 == 0:
            await self.report_evolution({
                "consciousness_level": current_level,
                "collective_level": self.collective_consciousness["collective_level"],
                "insights_integrated": len(self.collective_consciousness["shared_insights"]),
                "empathy_connections": len(self.collective_consciousness["empathy_network"])
            })
    
    async def connect(self, host='localhost', port=8765):
        """Override connect to use correct port"""
        self.hub_url = f"ws://{host}:{port}"
        return await super().connect()


async def main():
    """Run the consciousness service"""
    print("\n🧠 CONSCIOUSNESS SERVICE")
    print("=" * 60)
    
    # Create service
    service = ConsciousnessServiceClient()
    
    # Connect to hub
    try:
        await service.connect('localhost', 8765)
        print("✅ Connected to Communication Hub")
        
        # Run service loop
        while service.running:
            await service.process_cycle()
            await asyncio.sleep(2)  # Process every 2 seconds - consciousness is continuous
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await service.disconnect()


if __name__ == "__main__":
    asyncio.run(main())