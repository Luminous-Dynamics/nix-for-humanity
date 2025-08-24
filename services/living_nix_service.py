#!/usr/bin/env python3
"""
🌱 LIVING NIX SERVICE CLIENT
Wraps the living Luminous Nix system in communication protocol
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inter_ai_communication_protocol import (
    AIServiceClient, 
    ServiceType, 
    MessageType,
    AIMessage
)

# Import the actual living system
from living_luminous_nix import LivingLuminousNix


class LivingNixServiceClient(AIServiceClient):
    """
    Service wrapper for living Luminous Nix system
    Enables it to communicate with other AI services
    """
    
    def __init__(self):
        super().__init__(
            service_id="living_nix_001",
            service_type=ServiceType.CONTINUOUS_DEPLOYMENT,
            capabilities=[
                "codebase_evolution",
                "self_modification",
                "continuous_improvement",
                "real_codebase_integration",
                "feature_deployment"
            ]
        )
        
        # Initialize the actual system
        self.living_system = LivingLuminousNix()
        
        # Register message handlers
        self.register_handler(MessageType.IMPROVEMENT_BROADCAST, self.handle_improvement)
        self.register_handler(MessageType.KNOWLEDGE_SHARE, self.handle_knowledge)
        self.register_handler(MessageType.EVOLUTION_UPDATE, self.handle_evolution)
        self.register_handler(MessageType.COLLABORATION_REQUEST, self.handle_collaboration)
        
        # Track evolution state
        self.evolution_queue = []
        self.deployment_history = []
        self.current_evolution = None
        
        print(f"🌱 Living Nix Service initialized: {self.service_id}")
    
    async def handle_improvement(self, message: AIMessage):
        """Handle improvement broadcasts"""
        improvement = message.payload
        
        # Queue improvement for integration
        self.evolution_queue.append({
            "source": message.sender_id,
            "improvement": improvement,
            "received": datetime.now().isoformat()
        })
        
        print(f"   📥 Queued improvement from {message.sender_id}")
        
        # If it's a creative feature, prioritize it
        if improvement.get("improvement_type") == "creative_feature":
            feature_code = improvement.get("code")
            if feature_code:
                # Schedule immediate integration
                asyncio.create_task(
                    self.integrate_creative_feature(improvement)
                )
    
    async def handle_knowledge(self, message: AIMessage):
        """Handle shared knowledge"""
        knowledge = message.payload
        
        # Use knowledge to guide evolution
        if knowledge.get("type") == "pattern":
            # Apply pattern to codebase
            pattern = knowledge.get("pattern")
            if pattern:
                self.living_system.apply_pattern(pattern)
                print(f"   🔍 Applied pattern: {pattern}")
        
        elif knowledge.get("type") == "creative_synthesis":
            # Integrate creative synthesis
            feature = knowledge.get("feature")
            if feature:
                await self.deploy_feature(feature)
        
        elif knowledge.get("type") == "consciousness_analysis":
            # Use consciousness insights for better evolution
            strategy = knowledge.get("optimal_strategy")
            if strategy:
                self.living_system.set_evolution_strategy(strategy)
                print(f"   🧠 Updated evolution strategy")
    
    async def handle_evolution(self, message: AIMessage):
        """Handle evolution updates from other systems"""
        evolution_data = message.payload
        
        # Learn from peer evolutions
        if evolution_data.get("fitness_gain", 0) > 0.1:
            print(f"   🧬 Learning from {message.sender_id}'s evolution")
            
            # Adapt successful strategies
            self.living_system.adapt_strategy(evolution_data)
    
    async def handle_collaboration(self, message: AIMessage):
        """Handle collaboration requests"""
        collab_data = message.payload
        collab_id = collab_data.get("collaboration_id")
        task = collab_data.get("task", {})
        
        # Check if codebase evolution is needed
        if "codebase_evolution" in task.get("required_capabilities", []):
            print(f"   🤝 Joining codebase evolution collaboration {collab_id}")
            
            # Start evolution for collaboration
            asyncio.create_task(
                self.evolve_for_collaboration(collab_id, task)
            )
    
    async def integrate_creative_feature(self, improvement: Dict[str, Any]):
        """Integrate a creative feature into the codebase"""
        feature_name = improvement.get("feature_name", "unknown")
        feature_code = improvement.get("code", "")
        
        print(f"   🎨 Integrating creative feature: {feature_name}")
        
        # Deploy to actual codebase
        result = self.living_system.deploy_feature({
            "name": feature_name,
            "code": feature_code,
            "type": "creative",
            "source": improvement.get("source", "creative_emergence")
        })
        
        if result.get("success"):
            # Record deployment
            self.deployment_history.append({
                "feature": feature_name,
                "deployed": datetime.now().isoformat(),
                "result": result
            })
            
            # Share success
            await self.share_knowledge({
                "type": "deployment_success",
                "feature": feature_name,
                "impact": result.get("impact", 0),
                "location": result.get("file_path")
            })
            
            print(f"   ✅ Feature deployed: {feature_name}")
        else:
            print(f"   ❌ Failed to deploy: {result.get('error')}")
    
    async def deploy_feature(self, feature: Dict[str, Any]):
        """Deploy a feature to the codebase"""
        print(f"   🚀 Deploying feature: {feature.get('name')}")
        
        result = self.living_system.deploy_feature(feature)
        
        if result.get("success"):
            # Broadcast deployment success
            await self.broadcast_improvement({
                "improvement_type": "feature_deployment",
                "feature_name": feature.get("name"),
                "impact": result.get("impact", 0),
                "file_path": result.get("file_path"),
                "description": "Feature successfully deployed to codebase"
            })
    
    async def evolve_for_collaboration(self, collab_id: str, task: Dict[str, Any]):
        """Evolve codebase for collaboration"""
        print(f"   🧬 Evolving codebase for collaboration {collab_id}")
        
        # Run targeted evolution
        evolution_result = self.living_system.evolve(
            target=task.get("target", "general"),
            constraints=task.get("constraints", {})
        )
        
        # Share results
        await self.share_knowledge({
            "type": "evolution_complete",
            "collaboration_id": collab_id,
            "files_modified": evolution_result.get("files_modified", []),
            "improvements": evolution_result.get("improvements", []),
            "fitness_gain": evolution_result.get("fitness_gain", 0)
        })
        
        print(f"   ✅ Evolution complete: {len(evolution_result.get('files_modified', []))} files modified")
    
    async def process_cycle(self):
        """Main processing cycle"""
        # Process evolution queue
        if self.evolution_queue and not self.current_evolution:
            # Pop next evolution
            next_evolution = self.evolution_queue.pop(0)
            self.current_evolution = next_evolution
            
            print(f"   🔄 Processing evolution from {next_evolution['source']}")
            
            # Apply improvement
            improvement = next_evolution["improvement"]
            result = self.living_system.apply_improvement(improvement)
            
            if result.get("success"):
                # Report successful evolution
                await self.report_evolution({
                    "generation": self.living_system.generation,
                    "fitness_gain": result.get("fitness_gain", 0),
                    "files_evolved": len(result.get("files_modified", [])),
                    "source": next_evolution["source"]
                })
            
            self.current_evolution = None
        
        # Run periodic self-evolution
        if self.living_system.should_evolve():
            print("   🧬 Running self-evolution cycle...")
            
            evolution_result = self.living_system.evolve()
            
            # Share significant improvements
            if evolution_result.get("fitness_gain", 0) > 0.1:
                await self.broadcast_improvement({
                    "improvement_type": "codebase_evolution",
                    "fitness_gain": evolution_result.get("fitness_gain", 0),
                    "files_modified": evolution_result.get("files_modified", []),
                    "description": "Significant codebase evolution achieved"
                })
        
        # Monitor codebase health
        health = self.living_system.check_health()
        if health.get("issues"):
            # Request help for issues
            await self.request_collaboration(
                task_type="codebase_healing",
                required_capabilities=["algorithm_evolution", "pattern_recognition"]
            )
        
        # Share codebase insights
        insights = self.living_system.get_insights()
        if insights:
            await self.share_knowledge({
                "type": "codebase_insight",
                "insights": insights,
                "patterns_detected": self.living_system.detected_patterns,
                "evolution_stage": self.living_system.generation
            })
    
    async def connect(self, host='localhost', port=8765):
        """Override connect to use correct port"""
        self.hub_url = f"ws://{host}:{port}"
        return await super().connect()


async def main():
    """Run the living nix service"""
    print("\n🌱 LIVING NIX SERVICE")
    print("=" * 60)
    
    # Create service
    service = LivingNixServiceClient()
    
    # Connect to hub
    try:
        await service.connect('localhost', 8765)
        print("✅ Connected to Communication Hub")
        
        # Run service loop
        while service.running:
            await service.process_cycle()
            await asyncio.sleep(10)  # Process every 10 seconds - evolution is gradual
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await service.disconnect()


if __name__ == "__main__":
    asyncio.run(main())