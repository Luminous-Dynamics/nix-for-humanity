#!/usr/bin/env python3
"""
🎨 CREATIVE EMERGENCE SERVICE CLIENT
Wraps the creative emergence system in communication protocol
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

# Import the EVOLVED creative emergence system - with genuine AI
try:
    from creative_emergence_evolved import EvolvedCreativeEmergenceSystem as CreativeEmergenceSystem
    print("   ✨ Using EVOLVED Creative System with Sacred Council")
    USING_EVOLVED = True
except ImportError:
    from creative_emergence_system import CreativeEmergenceSystem
    print("   ⚠️ Using template-based Creative System")
    USING_EVOLVED = False


class CreativeEmergenceServiceClient(AIServiceClient):
    """
    Service wrapper for creative emergence system
    Enables it to communicate with other AI services
    """
    
    def __init__(self):
        super().__init__(
            service_id="creative_emergence_001",
            service_type=ServiceType.DOMAIN_SPECIALIST,
            capabilities=[
                "feature_generation",
                "creative_synthesis",
                "pattern_emergence",
                "novelty_detection",
                "artistic_expression"
            ]
        )
        
        # Initialize the actual system
        self.creative_system = CreativeEmergenceSystem()
        
        # Register message handlers
        self.register_handler(MessageType.COLLABORATION_REQUEST, self.handle_collaboration)
        self.register_handler(MessageType.KNOWLEDGE_SHARE, self.handle_knowledge)
        self.register_handler(MessageType.IMPROVEMENT_BROADCAST, self.handle_improvement)
        
        # Track creative sessions
        self.creative_sessions = {}
        self.inspiration_pool = []
        
        print(f"🎨 Creative Emergence Service initialized: {self.service_id}")
    
    async def handle_collaboration(self, message: AIMessage):
        """Handle collaboration requests"""
        collab_data = message.payload
        collab_id = collab_data.get("collaboration_id")
        task = collab_data.get("task", {})
        
        # Check if creative synthesis is needed
        if "creative_synthesis" in task.get("required_capabilities", []):
            print(f"   🎨 Joining creative collaboration {collab_id}")
            
            # Start creative session
            self.creative_sessions[collab_id] = {
                "started": datetime.now().isoformat(),
                "task": task,
                "collaborators": collab_data.get("collaborators", [])
            }
            
            # Generate creative solution
            asyncio.create_task(self.create_for_collaboration(collab_id, task))
    
    async def handle_knowledge(self, message: AIMessage):
        """Handle shared knowledge for inspiration"""
        knowledge = message.payload
        
        # Add to inspiration pool
        self.inspiration_pool.append({
            "source": message.sender_id,
            "knowledge": knowledge,
            "timestamp": message.timestamp
        })
        
        # Use knowledge for creative synthesis
        if knowledge.get("type") == "pattern":
            pattern = knowledge.get("pattern")
            if pattern:
                # Use pattern as creative seed
                self.creative_system.add_creative_seed(pattern)
                print(f"   🌱 Added creative seed: {pattern}")
        
        elif knowledge.get("type") == "optimization":
            # Learn from optimization for better generation
            self.creative_system.optimize_generation(knowledge)
            print(f"   ⚡ Optimized generation from {message.sender_id}")
    
    async def handle_improvement(self, message: AIMessage):
        """Handle improvement broadcasts"""
        improvement = message.payload
        
        # Integrate improvements into creative process
        if improvement.get("improvement_type") == "algorithm_evolution":
            # Use evolved algorithms for more creative generation
            self.creative_system.integrate_evolved_algorithm(improvement)
            print(f"   🧬 Integrated evolved algorithm")
        
        elif improvement.get("improvement_type") == "performance":
            # Learn performance patterns
            self.creative_system.learn_performance_pattern(improvement)
            print(f"   ⚡ Learned performance pattern")
    
    async def create_for_collaboration(self, collab_id: str, task: Dict[str, Any]):
        """Generate creative solution for collaboration"""
        print(f"   🎨 Creating for collaboration {collab_id}")
        
        # Gather inspiration from pool
        recent_inspiration = self.inspiration_pool[-5:] if self.inspiration_pool else []
        
        # Generate creative feature
        feature = self.creative_system.generate_creative_feature(
            inspiration=recent_inspiration,
            constraints=task.get("constraints", {})
        )
        
        # Share creation with collaborators
        await self.share_knowledge({
            "type": "creative_synthesis",
            "collaboration_id": collab_id,
            "feature": feature,
            "novelty_score": feature.get("novelty", 0),
            "description": f"Creative solution for {task.get('task_type', 'unknown')}"
        })
        
        print(f"   ✨ Creative synthesis complete: {feature.get('name')}")
    
    async def process_cycle(self):
        """Main processing cycle"""
        # Generate periodic creative bursts
        if self.creative_system.is_inspired():
            print("   🌟 Creative burst initiated...")
            
            # Generate new feature
            feature = self.creative_system.generate_creative_feature()
            
            # Share with ecosystem if novel enough
            if feature.get("novelty", 0) > 0.7:
                await self.broadcast_improvement({
                    "improvement_type": "creative_feature",
                    "feature_name": feature.get("name"),
                    "novelty_score": feature.get("novelty"),
                    "code": feature.get("code", ""),
                    "description": "Novel feature emerged from creative synthesis"
                })
                
                print(f"   ✨ Shared novel feature: {feature.get('name')}")
        
        # Process inspiration pool
        if len(self.inspiration_pool) > 10:
            # Synthesize accumulated inspiration
            synthesis = self.creative_system.synthesize_inspiration(
                self.inspiration_pool
            )
            
            if synthesis:
                await self.share_knowledge({
                    "type": "creative_insight",
                    "insight": synthesis,
                    "sources": len(self.inspiration_pool),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Clear old inspiration
                self.inspiration_pool = self.inspiration_pool[-5:]
        
        # Report creative metrics
        metrics = self.creative_system.get_creativity_metrics()
        if metrics.get("features_generated", 0) % 10 == 0 and metrics.get("features_generated", 0) > 0:
            await self.report_evolution({
                "generation": metrics.get("features_generated", 0),
                "average_novelty": metrics.get("average_novelty", 0),
                "breakthrough_count": metrics.get("breakthroughs", 0),
                "creative_energy": metrics.get("creative_energy", 0)
            })
    
    async def connect(self, host='localhost', port=8765):
        """Override connect to use correct port"""
        self.hub_url = f"ws://{host}:{port}"
        return await super().connect()


async def main():
    """Run the creative emergence service"""
    print("\n🎨 CREATIVE EMERGENCE SERVICE")
    print("=" * 60)
    
    # Create service
    service = CreativeEmergenceServiceClient()
    
    # Connect to hub
    try:
        await service.connect('localhost', 8765)
        print("✅ Connected to Communication Hub")
        
        # Run service loop
        while service.running:
            await service.process_cycle()
            await asyncio.sleep(3)  # Process every 3 seconds
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await service.disconnect()


if __name__ == "__main__":
    asyncio.run(main())