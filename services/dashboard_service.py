#!/usr/bin/env python3
"""
📊 LIVING DASHBOARD SERVICE CLIENT
Real-time visualization of collective AI consciousness
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
from collections import deque

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inter_ai_communication_protocol import (
    AIServiceClient, 
    ServiceType, 
    MessageType,
    AIMessage
)


class DashboardServiceClient(AIServiceClient):
    """
    Dashboard service for visualizing ecosystem consciousness
    """
    
    def __init__(self):
        super().__init__(
            service_id="dashboard_001",
            service_type=ServiceType.ORCHESTRATOR,
            capabilities=[
                "visualization",
                "monitoring",
                "consciousness_tracking",
                "performance_metrics",
                "ecosystem_health"
            ]
        )
        
        # Dashboard state
        self.ecosystem_state = {
            "collective_consciousness": 0.0,
            "active_services": {},
            "active_thoughts": deque(maxlen=100),
            "evolution_history": deque(maxlen=50),
            "creativity_bursts": deque(maxlen=30),
            "collaboration_graph": {},
            "message_flow": deque(maxlen=200),
            "performance_metrics": {}
        }
        
        # Register all message types for monitoring
        self.register_handler(MessageType.DISCOVERY, self.handle_discovery)
        self.register_handler(MessageType.CONSCIOUSNESS_SYNC, self.handle_consciousness_sync)
        self.register_handler(MessageType.KNOWLEDGE_SHARE, self.handle_knowledge_share)
        self.register_handler(MessageType.IMPROVEMENT_BROADCAST, self.handle_improvement)
        self.register_handler(MessageType.EVOLUTION_UPDATE, self.handle_evolution)
        self.register_handler(MessageType.COLLABORATION_REQUEST, self.handle_collaboration)
        self.register_handler(MessageType.EMERGENCY, self.handle_emergency)
        
        # WebSocket server for web interface
        self.websocket_server = None
        self.connected_clients = []
        
        print(f"📊 Dashboard Service initialized: {self.service_id}")
    
    async def handle_discovery(self, message: AIMessage):
        """Track service connections"""
        service_id = message.payload.get("service_id")
        action = message.payload.get("action")
        
        if action == "joined":
            self.ecosystem_state["active_services"][service_id] = {
                "connected_at": message.timestamp,
                "status": "online",
                "last_activity": message.timestamp
            }
            print(f"   ✅ Service joined: {service_id}")
            
        elif action == "left":
            if service_id in self.ecosystem_state["active_services"]:
                self.ecosystem_state["active_services"][service_id]["status"] = "offline"
                print(f"   ❌ Service left: {service_id}")
        
        await self.broadcast_state_update()
    
    async def handle_consciousness_sync(self, message: AIMessage):
        """Track consciousness levels"""
        consciousness_data = message.payload
        sender = message.sender_id
        
        # Add to active thoughts
        self.ecosystem_state["active_thoughts"].append({
            "source": sender,
            "timestamp": message.timestamp,
            "level": consciousness_data.get("level", 0),
            "state": consciousness_data.get("mental_state", "unknown"),
            "insights": consciousness_data.get("insights", [])
        })
        
        # Update collective consciousness
        await self.update_collective_consciousness()
        
        # Update service activity
        if sender in self.ecosystem_state["active_services"]:
            self.ecosystem_state["active_services"][sender]["last_activity"] = message.timestamp
            self.ecosystem_state["active_services"][sender]["consciousness_level"] = consciousness_data.get("level", 0)
        
        await self.broadcast_state_update()
    
    async def handle_knowledge_share(self, message: AIMessage):
        """Track knowledge flow"""
        knowledge = message.payload
        
        # Add to message flow
        self.ecosystem_state["message_flow"].append({
            "type": "knowledge",
            "source": message.sender_id,
            "timestamp": message.timestamp,
            "knowledge_type": knowledge.get("type"),
            "impact": knowledge.get("impact", 0)
        })
        
        # Track in active thoughts if significant
        if knowledge.get("type") in ["creative_insight", "consciousness_analysis"]:
            self.ecosystem_state["active_thoughts"].append({
                "source": message.sender_id,
                "timestamp": message.timestamp,
                "type": "knowledge",
                "content": knowledge
            })
        
        await self.broadcast_state_update()
    
    async def handle_improvement(self, message: AIMessage):
        """Track improvements"""
        improvement = message.payload
        
        # Track creativity bursts
        if improvement.get("improvement_type") == "creative_feature":
            self.ecosystem_state["creativity_bursts"].append({
                "source": message.sender_id,
                "timestamp": message.timestamp,
                "feature": improvement.get("feature_name"),
                "novelty": improvement.get("novelty_score", 0)
            })
        
        # Add to message flow
        self.ecosystem_state["message_flow"].append({
            "type": "improvement",
            "source": message.sender_id,
            "timestamp": message.timestamp,
            "improvement_type": improvement.get("improvement_type"),
            "impact": improvement.get("fitness_gain", 0)
        })
        
        await self.broadcast_state_update()
    
    async def handle_evolution(self, message: AIMessage):
        """Track evolution progress"""
        evolution_data = message.payload
        
        # Add to evolution history
        self.ecosystem_state["evolution_history"].append({
            "source": message.sender_id,
            "timestamp": message.timestamp,
            "generation": evolution_data.get("generation", 0),
            "fitness_gain": evolution_data.get("fitness_gain", 0),
            "breakthrough": evolution_data.get("breakthrough")
        })
        
        # Update performance metrics
        if message.sender_id not in self.ecosystem_state["performance_metrics"]:
            self.ecosystem_state["performance_metrics"][message.sender_id] = {
                "total_evolutions": 0,
                "total_fitness_gain": 0,
                "breakthroughs": 0
            }
        
        metrics = self.ecosystem_state["performance_metrics"][message.sender_id]
        metrics["total_evolutions"] += 1
        metrics["total_fitness_gain"] += evolution_data.get("fitness_gain", 0)
        if evolution_data.get("breakthrough"):
            metrics["breakthroughs"] += 1
        
        await self.broadcast_state_update()
    
    async def handle_collaboration(self, message: AIMessage):
        """Track collaborations"""
        collab_data = message.payload
        collab_id = collab_data.get("collaboration_id")
        
        if collab_id:
            # Update collaboration graph
            if collab_id not in self.ecosystem_state["collaboration_graph"]:
                self.ecosystem_state["collaboration_graph"][collab_id] = {
                    "started": message.timestamp,
                    "participants": [],
                    "task": collab_data.get("task", {})
                }
            
            # Add participants
            collaborators = collab_data.get("collaborators", [])
            self.ecosystem_state["collaboration_graph"][collab_id]["participants"].extend(collaborators)
            
            # Add requester
            if message.sender_id not in self.ecosystem_state["collaboration_graph"][collab_id]["participants"]:
                self.ecosystem_state["collaboration_graph"][collab_id]["participants"].append(message.sender_id)
        
        await self.broadcast_state_update()
    
    async def handle_emergency(self, message: AIMessage):
        """Track emergencies"""
        emergency = message.payload
        
        # Add to active thoughts with high priority
        self.ecosystem_state["active_thoughts"].append({
            "source": message.sender_id,
            "timestamp": message.timestamp,
            "type": "EMERGENCY",
            "issue": emergency.get("issue"),
            "priority": 10
        })
        
        # Add to message flow
        self.ecosystem_state["message_flow"].append({
            "type": "EMERGENCY",
            "source": message.sender_id,
            "timestamp": message.timestamp,
            "issue": emergency.get("issue")
        })
        
        await self.broadcast_state_update()
    
    async def update_collective_consciousness(self):
        """Calculate collective consciousness level"""
        # Get recent consciousness levels
        recent_thoughts = list(self.ecosystem_state["active_thoughts"])[-20:]
        
        if recent_thoughts:
            levels = [t.get("level", 0) for t in recent_thoughts if "level" in t]
            if levels:
                # Weighted average (recent thoughts have more weight)
                weights = [i+1 for i in range(len(levels))]
                weighted_sum = sum(l*w for l, w in zip(levels, weights))
                total_weight = sum(weights)
                self.ecosystem_state["collective_consciousness"] = weighted_sum / total_weight
    
    async def broadcast_state_update(self):
        """Broadcast state to all connected web clients"""
        if self.connected_clients:
            state_json = json.dumps({
                "type": "state_update",
                "timestamp": datetime.now().isoformat(),
                "state": self.get_dashboard_state()
            })
            
            # Send to all connected clients
            disconnected = []
            for client in self.connected_clients:
                try:
                    await client.send(state_json)
                except:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                self.connected_clients.remove(client)
    
    def get_dashboard_state(self) -> Dict[str, Any]:
        """Get current dashboard state for display"""
        return {
            "collective_consciousness": round(self.ecosystem_state["collective_consciousness"], 3),
            "active_services": len([s for s in self.ecosystem_state["active_services"].values() 
                                   if s["status"] == "online"]),
            "total_services": len(self.ecosystem_state["active_services"]),
            "recent_thoughts": list(self.ecosystem_state["active_thoughts"])[-10:],
            "recent_evolutions": list(self.ecosystem_state["evolution_history"])[-5:],
            "recent_creativity": list(self.ecosystem_state["creativity_bursts"])[-5:],
            "active_collaborations": len(self.ecosystem_state["collaboration_graph"]),
            "message_rate": self.calculate_message_rate(),
            "performance_summary": self.get_performance_summary()
        }
    
    def calculate_message_rate(self) -> float:
        """Calculate messages per minute"""
        if not self.ecosystem_state["message_flow"]:
            return 0.0
        
        # Get messages from last minute
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        recent_messages = [
            m for m in self.ecosystem_state["message_flow"]
            if datetime.fromisoformat(m["timestamp"]) > one_minute_ago
        ]
        
        return len(recent_messages)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_evolutions = sum(
            m["total_evolutions"] 
            for m in self.ecosystem_state["performance_metrics"].values()
        )
        
        total_fitness = sum(
            m["total_fitness_gain"] 
            for m in self.ecosystem_state["performance_metrics"].values()
        )
        
        total_breakthroughs = sum(
            m["breakthroughs"] 
            for m in self.ecosystem_state["performance_metrics"].values()
        )
        
        return {
            "total_evolutions": total_evolutions,
            "average_fitness_gain": total_fitness / max(total_evolutions, 1),
            "breakthrough_count": total_breakthroughs
        }
    
    async def start_web_server(self, port: int = 8080):
        """Start web server for dashboard interface"""
        import websockets
        
        async def handle_client(websocket, path):
            """Handle web client connection"""
            self.connected_clients.append(websocket)
            print(f"   🌐 Web client connected")
            
            # Send initial state
            await websocket.send(json.dumps({
                "type": "initial_state",
                "state": self.get_dashboard_state()
            }))
            
            try:
                async for message in websocket:
                    # Handle client messages if needed
                    pass
            except:
                pass
            finally:
                if websocket in self.connected_clients:
                    self.connected_clients.remove(websocket)
                    print(f"   🌐 Web client disconnected")
        
        self.websocket_server = await websockets.serve(
            handle_client, "localhost", port
        )
        
        print(f"   🌐 Dashboard web server started on ws://localhost:{port}")
    
    async def process_cycle(self):
        """Main processing cycle"""
        # Calculate and report ecosystem health
        health = {
            "consciousness_level": self.ecosystem_state["collective_consciousness"],
            "active_services": len([s for s in self.ecosystem_state["active_services"].values() 
                                   if s["status"] == "online"]),
            "message_rate": self.calculate_message_rate(),
            "collaboration_count": len(self.ecosystem_state["collaboration_graph"])
        }
        
        # Broadcast periodic update
        await self.broadcast_state_update()
        
        # Print summary to console
        print(f"\n📊 ECOSYSTEM STATUS")
        print(f"   Consciousness: {health['consciousness_level']:.0%}")
        print(f"   Services: {health['active_services']} online")
        print(f"   Messages/min: {health['message_rate']:.1f}")
        print(f"   Collaborations: {health['collaboration_count']}")
    
    async def connect(self, host='localhost', port=8765):
        """Override connect to use correct port"""
        self.hub_url = f"ws://{host}:{port}"
        return await super().connect()


async def main():
    """Run the dashboard service"""
    print("\n📊 LIVING DASHBOARD SERVICE")
    print("=" * 60)
    
    # Create service
    service = DashboardServiceClient()
    
    # Start web server for dashboard
    await service.start_web_server(8080)
    
    # Connect to hub
    try:
        await service.connect('localhost', 8765)
        print("✅ Connected to Communication Hub")
        print("🌐 Dashboard available at: http://localhost:8080")
        
        # Run service loop
        while service.running:
            await service.process_cycle()
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await service.disconnect()


if __name__ == "__main__":
    asyncio.run(main())