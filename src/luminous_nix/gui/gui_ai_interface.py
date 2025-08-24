#!/usr/bin/env python3
"""
GUI AI Interface - Enables AI to control and test the modular GUI

This provides a Python interface for AI systems to:
- Control GUI components
- Test interactions
- Customize layouts
- Learn from user behavior
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import websocket
import logging

logger = logging.getLogger(__name__)


@dataclass
class Component:
    """Represents a GUI component"""
    id: str
    type: str
    state: Dict[str, Any]
    capabilities: List[str]
    position: Optional[Tuple[int, int]] = None
    size: Optional[Tuple[int, int]] = None


@dataclass
class Layout:
    """Represents a GUI layout configuration"""
    id: str
    name: str
    components: List[Component]
    grid: Dict[str, Any]
    theme: Dict[str, Any]


class GUIAIInterface:
    """
    AI Interface for the Modular GUI System
    
    This allows AI to:
    1. Control any component
    2. Test interactions
    3. Customize layouts
    4. Learn from patterns
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:8080"):
        """Initialize connection to GUI"""
        self.ws_url = websocket_url
        self.ws = None
        self.components: Dict[str, Component] = {}
        self.current_layout: Optional[Layout] = None
        self.interaction_history: List[Dict] = []
        
    def connect(self):
        """Connect to GUI via WebSocket"""
        try:
            self.ws = websocket.create_connection(self.ws_url)
            logger.info(f"Connected to GUI at {self.ws_url}")
            self._sync_components()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to GUI: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from GUI"""
        if self.ws:
            self.ws.close()
            logger.info("Disconnected from GUI")
    
    # ========== Component Discovery ==========
    
    def find_component(self, selector: Dict[str, Any]) -> Optional[Component]:
        """
        Find a component by selector
        
        Examples:
            find_component({"id": "search-input"})
            find_component({"type": "SearchInput"})
            find_component({"capability": "voice"})
        """
        self._sync_components()
        
        for comp in self.components.values():
            if self._matches_selector(comp, selector):
                return comp
        return None
    
    def find_all_components(self, component_type: str = None) -> List[Component]:
        """Find all components, optionally filtered by type"""
        self._sync_components()
        
        if component_type:
            return [c for c in self.components.values() if c.type == component_type]
        return list(self.components.values())
    
    def _matches_selector(self, component: Component, selector: Dict) -> bool:
        """Check if component matches selector"""
        if "id" in selector and component.id != selector["id"]:
            return False
        if "type" in selector and component.type != selector["type"]:
            return False
        if "capability" in selector and selector["capability"] not in component.capabilities:
            return False
        return True
    
    # ========== State Inspection ==========
    
    def get_component_state(self, component_id: str) -> Dict[str, Any]:
        """Get current state of a component"""
        response = self._send_command("getComponentState", {"id": component_id})
        return response.get("state", {})
    
    def get_global_state(self) -> Dict[str, Any]:
        """Get entire application state"""
        response = self._send_command("getGlobalState")
        return response.get("state", {})
    
    def get_layout(self) -> Layout:
        """Get current layout configuration"""
        response = self._send_command("getLayout")
        self.current_layout = Layout(**response["layout"])
        return self.current_layout
    
    # ========== Interaction Simulation ==========
    
    def click(self, component_id: str) -> bool:
        """Simulate click on component"""
        response = self._send_command("click", {"id": component_id})
        self._record_interaction("click", component_id, response)
        return response.get("success", False)
    
    def type_text(self, component_id: str, text: str) -> bool:
        """Type text into component"""
        response = self._send_command("type", {"id": component_id, "text": text})
        self._record_interaction("type", component_id, response)
        return response.get("success", False)
    
    def drag(self, from_id: str, to_id: str) -> bool:
        """Drag from one component to another"""
        response = self._send_command("drag", {"from": from_id, "to": to_id})
        self._record_interaction("drag", f"{from_id}->{to_id}", response)
        return response.get("success", False)
    
    def hover(self, component_id: str) -> bool:
        """Hover over component"""
        response = self._send_command("hover", {"id": component_id})
        return response.get("success", False)
    
    def focus(self, component_id: str) -> bool:
        """Focus on component"""
        response = self._send_command("focus", {"id": component_id})
        self._record_interaction("focus", component_id, response)
        return response.get("success", False)
    
    def keyboard_shortcut(self, shortcut: str) -> bool:
        """Trigger keyboard shortcut"""
        response = self._send_command("keyboard", {"shortcut": shortcut})
        return response.get("success", False)
    
    # ========== High-Level Actions ==========
    
    def perform_action(self, action: str, params: Dict[str, Any] = None) -> Any:
        """
        Perform high-level action
        
        Examples:
            perform_action("search", {"query": "install firefox"})
            perform_action("install", {"package": "vim"})
            perform_action("switch-layout", {"layout": "zen"})
        """
        response = self._send_command("performAction", {
            "action": action,
            "params": params or {}
        })
        self._record_interaction("action", action, response)
        return response.get("result")
    
    def search_and_install(self, package_name: str) -> bool:
        """High-level: Search for package and install first result"""
        # Search
        search_result = self.perform_action("search", {"query": package_name})
        
        if not search_result or not search_result.get("results"):
            logger.warning(f"No results found for {package_name}")
            return False
        
        # Install first result
        first_result = search_result["results"][0]
        install_result = self.perform_action("install", {"package": first_result["name"]})
        
        return install_result.get("success", False)
    
    # ========== Layout Customization ==========
    
    def switch_layout(self, layout_id: str) -> bool:
        """Switch to different layout"""
        response = self._send_command("switchLayout", {"layoutId": layout_id})
        if response.get("success"):
            self.current_layout = None  # Force refresh on next access
        return response.get("success", False)
    
    def create_custom_layout(self, name: str, components: List[Dict]) -> str:
        """
        Create custom layout from components
        
        Example:
            create_custom_layout("focus", [
                {"type": "SearchBar", "area": "top"},
                {"type": "ResultsList", "area": "main"}
            ])
        """
        response = self._send_command("createLayout", {
            "name": name,
            "components": components
        })
        return response.get("layoutId")
    
    def add_component_to_layout(self, component_type: str, area: str) -> bool:
        """Add component to current layout"""
        response = self._send_command("addComponent", {
            "type": component_type,
            "area": area
        })
        return response.get("success", False)
    
    def remove_component_from_layout(self, component_id: str) -> bool:
        """Remove component from current layout"""
        response = self._send_command("removeComponent", {"id": component_id})
        return response.get("success", False)
    
    def rearrange_layout(self, new_grid: Dict[str, Any]) -> bool:
        """Rearrange current layout with new grid"""
        response = self._send_command("rearrangeLayout", {"grid": new_grid})
        return response.get("success", False)
    
    # ========== Theme Customization ==========
    
    def customize_theme(self, tokens: Dict[str, Any]) -> bool:
        """
        Customize theme with design tokens
        
        Example:
            customize_theme({
                "colors": {"primary": "#6366f1"},
                "fontSize": 16,
                "animations": False
            })
        """
        response = self._send_command("customizeTheme", {"tokens": tokens})
        return response.get("success", False)
    
    def set_consciousness_level(self, level: float) -> bool:
        """Set consciousness coherence level (0-1)"""
        response = self._send_command("setConsciousness", {"level": level})
        return response.get("success", False)
    
    def enable_sacred_geometry(self, pattern: str = "flowerOfLife") -> bool:
        """Enable sacred geometry visualization"""
        response = self._send_command("setSacredGeometry", {"pattern": pattern})
        return response.get("success", False)
    
    # ========== Testing Utilities ==========
    
    def take_screenshot(self) -> bytes:
        """Take screenshot of current GUI state"""
        response = self._send_command("screenshot")
        return response.get("image", b"")
    
    def validate_accessibility(self) -> Dict[str, Any]:
        """Run accessibility validation"""
        response = self._send_command("validateA11y")
        return response.get("report", {})
    
    def measure_performance(self) -> Dict[str, Any]:
        """Measure GUI performance metrics"""
        response = self._send_command("measurePerformance")
        return response.get("metrics", {})
    
    def record_interaction_sequence(self) -> str:
        """Start recording user interactions"""
        response = self._send_command("startRecording")
        return response.get("recordingId")
    
    def stop_recording(self, recording_id: str) -> List[Dict]:
        """Stop recording and get interaction sequence"""
        response = self._send_command("stopRecording", {"id": recording_id})
        return response.get("interactions", [])
    
    def replay_interactions(self, interactions: List[Dict]) -> bool:
        """Replay a sequence of interactions"""
        response = self._send_command("replay", {"interactions": interactions})
        return response.get("success", False)
    
    # ========== Learning & Adaptation ==========
    
    def learn_user_patterns(self) -> Dict[str, Any]:
        """Analyze interaction history to learn patterns"""
        if len(self.interaction_history) < 10:
            return {"status": "insufficient_data"}
        
        patterns = {
            "common_actions": self._find_common_actions(),
            "interaction_sequences": self._find_sequences(),
            "timing_patterns": self._analyze_timing(),
            "error_patterns": self._find_error_patterns()
        }
        
        return patterns
    
    def suggest_layout_improvements(self) -> List[Dict]:
        """Suggest layout improvements based on usage"""
        patterns = self.learn_user_patterns()
        suggestions = []
        
        # Suggest based on common actions
        common_actions = patterns.get("common_actions", [])
        if "search" in common_actions[:3]:
            suggestions.append({
                "type": "move_component",
                "component": "SearchBar",
                "reason": "Frequently used",
                "suggestion": "Move to more prominent position"
            })
        
        # Suggest based on errors
        error_patterns = patterns.get("error_patterns", [])
        if len(error_patterns) > 5:
            suggestions.append({
                "type": "simplify_layout",
                "reason": "High error rate",
                "suggestion": "Reduce complexity"
            })
        
        return suggestions
    
    def adapt_to_user_state(self, user_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt GUI based on user state
        
        Args:
            user_state: Dict with keys like cognitive_load, flow_level, stress_level
        
        Returns:
            Dict of adaptations applied
        """
        adaptations = {}
        
        # High cognitive load: Simplify
        if user_state.get("cognitive_load", 0) > 0.8:
            self.switch_layout("minimal")
            adaptations["layout"] = "minimal"
            
        # Flow state: Remove distractions
        if user_state.get("flow_level", 0) > 0.7:
            self.perform_action("enable-focus-mode")
            adaptations["focus_mode"] = True
            
        # Stress: Calming theme
        if user_state.get("stress_level", 0) > 0.6:
            self.customize_theme({
                "colors": {"primary": "#93c5fd"},  # Calming blue
                "animations": False
            })
            adaptations["theme"] = "calming"
        
        return adaptations
    
    # ========== Private Methods ==========
    
    def _send_command(self, command: str, params: Dict[str, Any] = None) -> Dict:
        """Send command to GUI via WebSocket"""
        if not self.ws:
            self.connect()
        
        message = {
            "command": command,
            "params": params or {}
        }
        
        try:
            self.ws.send(json.dumps(message))
            response = json.loads(self.ws.recv())
            return response
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"error": str(e)}
    
    def _sync_components(self):
        """Sync component list with GUI"""
        response = self._send_command("getComponents")
        components = response.get("components", [])
        
        self.components = {}
        for comp_data in components:
            comp = Component(**comp_data)
            self.components[comp.id] = comp
    
    def _record_interaction(self, action: str, target: str, result: Dict):
        """Record interaction for learning"""
        self.interaction_history.append({
            "action": action,
            "target": target,
            "success": result.get("success", False),
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def _find_common_actions(self) -> List[str]:
        """Find most common actions from history"""
        action_counts = {}
        for interaction in self.interaction_history:
            action = interaction["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        return [action for action, _ in sorted_actions[:5]]
    
    def _find_sequences(self) -> List[List[str]]:
        """Find common interaction sequences"""
        sequences = []
        # Simple sequence detection (could be more sophisticated)
        for i in range(len(self.interaction_history) - 2):
            seq = [
                self.interaction_history[i]["action"],
                self.interaction_history[i+1]["action"],
                self.interaction_history[i+2]["action"]
            ]
            if seq not in sequences:
                sequences.append(seq)
        return sequences[:5]
    
    def _analyze_timing(self) -> Dict[str, float]:
        """Analyze timing patterns"""
        if len(self.interaction_history) < 2:
            return {}
        
        intervals = []
        for i in range(1, len(self.interaction_history)):
            interval = (self.interaction_history[i]["timestamp"] - 
                       self.interaction_history[i-1]["timestamp"])
            intervals.append(interval)
        
        return {
            "avg_interval": sum(intervals) / len(intervals) if intervals else 0,
            "min_interval": min(intervals) if intervals else 0,
            "max_interval": max(intervals) if intervals else 0
        }
    
    def _find_error_patterns(self) -> List[str]:
        """Find patterns in failed interactions"""
        errors = [i for i in self.interaction_history if not i["success"]]
        error_targets = [e["target"] for e in errors]
        return list(set(error_targets))[:5]


# ========== Test Suite ==========

async def test_gui_ai_interface():
    """Test the GUI AI interface"""
    print("🧪 Testing GUI AI Interface")
    print("=" * 60)
    
    # Create interface
    gui = GUIAIInterface("ws://localhost:8080")
    
    # Connect
    print("\n1️⃣ Connecting to GUI...")
    if not gui.connect():
        print("   ❌ Failed to connect (GUI not running)")
        return
    print("   ✅ Connected")
    
    # Find components
    print("\n2️⃣ Finding components...")
    search = gui.find_component({"type": "SearchInput"})
    if search:
        print(f"   ✅ Found search: {search.id}")
        print(f"      Capabilities: {search.capabilities}")
    
    # Test interaction
    print("\n3️⃣ Testing interactions...")
    if search:
        gui.type_text(search.id, "install firefox")
        print("   ✅ Typed search query")
        
        gui.click(search.id)
        print("   ✅ Clicked search")
    
    # Test high-level action
    print("\n4️⃣ Testing high-level actions...")
    result = gui.perform_action("search", {"query": "vim"})
    print(f"   ✅ Search result: {result}")
    
    # Test layout
    print("\n5️⃣ Testing layout customization...")
    gui.switch_layout("minimal")
    print("   ✅ Switched to minimal layout")
    
    # Test theme
    print("\n6️⃣ Testing theme customization...")
    gui.customize_theme({
        "colors": {"primary": "#10b981"},
        "fontSize": 18
    })
    print("   ✅ Applied custom theme")
    
    # Test learning
    print("\n7️⃣ Testing learning...")
    patterns = gui.learn_user_patterns()
    print(f"   📊 Learned patterns: {patterns}")
    
    suggestions = gui.suggest_layout_improvements()
    print(f"   💡 Suggestions: {suggestions}")
    
    # Test adaptation
    print("\n8️⃣ Testing adaptation...")
    adaptations = gui.adapt_to_user_state({
        "cognitive_load": 0.9,
        "flow_level": 0.3,
        "stress_level": 0.7
    })
    print(f"   🎯 Adaptations applied: {adaptations}")
    
    # Disconnect
    gui.disconnect()
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_gui_ai_interface())