#!/usr/bin/env python3
"""
🤖 LLM Interface Proof of Concept
Shows how ask-nix can be used as a tool by LLMs
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

# Import existing consciousness components
try:
    from ..consciousness.nix_bridge import NixBridge
    from ..consciousness.consciousness_integration import ConsciousnessIntegration
    from ..consciousness.session_memory import get_session_memory
    from ..consciousness.persona_adapter import get_persona_adapter
    CONSCIOUSNESS_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_AVAILABLE = False


class ToolAction(Enum):
    """Available tool actions for LLMs"""
    SEARCH = "search"
    INSTALL = "install"
    REMOVE = "remove"
    UPDATE = "update"
    LIST = "list"
    EXPLAIN = "explain"
    CONFIG = "config"
    ROLLBACK = "rollback"
    HEALTH = "health"


class LLMInterface:
    """
    Interface for LLMs to interact with Luminous Nix
    Provides structured input/output for tool calling
    """
    
    def __init__(self):
        """Initialize the LLM interface"""
        self.nix_bridge = NixBridge() if CONSCIOUSNESS_AVAILABLE else None
        self.consciousness = ConsciousnessIntegration() if CONSCIOUSNESS_AVAILABLE else None
        self.conversations = {}  # Track conversation contexts
        
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all available tool definitions for LLMs
        Returns OpenAI function calling format (adaptable to others)
        """
        return [
            {
                "name": "search_packages",
                "description": "Search for NixOS packages by name or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for (name or description)"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter",
                            "enum": ["development", "productivity", "games", "multimedia", "system"]
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "install_package",
                "description": "Install a NixOS package on the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "Name of the package to install"
                        },
                        "preview": {
                            "type": "boolean",
                            "description": "Show what would happen without actually installing",
                            "default": False
                        }
                    },
                    "required": ["package"]
                }
            },
            {
                "name": "explain_concept",
                "description": "Explain a NixOS concept in user-appropriate language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "concept": {
                            "type": "string",
                            "description": "The NixOS concept to explain"
                        },
                        "depth": {
                            "type": "string",
                            "description": "Level of explanation detail",
                            "enum": ["beginner", "intermediate", "advanced"],
                            "default": "intermediate"
                        }
                    },
                    "required": ["concept"]
                }
            },
            {
                "name": "list_installed",
                "description": "List all installed packages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Optional filter for package names"
                        }
                    }
                }
            },
            {
                "name": "system_health",
                "description": "Check system health and get recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def process_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a tool call from an LLM
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            conversation_id: Optional conversation tracking ID
            
        Returns:
            Structured response for the LLM
        """
        
        # Track conversation if ID provided
        if conversation_id and conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "started": datetime.now().isoformat(),
                "history": [],
                "context": {}
            }
        
        # Route to appropriate handler
        if tool_name == "search_packages":
            return await self._search_packages(parameters, conversation_id)
        elif tool_name == "install_package":
            return await self._install_package(parameters, conversation_id)
        elif tool_name == "explain_concept":
            return await self._explain_concept(parameters, conversation_id)
        elif tool_name == "list_installed":
            return await self._list_installed(parameters, conversation_id)
        elif tool_name == "system_health":
            return await self._system_health(parameters, conversation_id)
        else:
            return self._error_response(f"Unknown tool: {tool_name}")
    
    async def _search_packages(
        self,
        params: Dict[str, Any],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """Handle package search"""
        query = params.get("query", "")
        category = params.get("category")
        
        if not query:
            return self._error_response("Search query is required")
        
        # Use consciousness bridge if available
        if self.nix_bridge:
            result = await self.nix_bridge.process_intent(
                intent="search",
                command=f"search {query}",
                context={"category": category} if category else {}
            )
            
            # Format for LLM consumption
            if result.get("success"):
                packages = result.get("packages", [])
                return {
                    "success": True,
                    "tool": "search_packages",
                    "data": {
                        "query": query,
                        "found": len(packages),
                        "packages": packages[:10]  # Limit for LLM context
                    },
                    "message": f"Found {len(packages)} packages matching '{query}'",
                    "suggestions": [
                        f"You can install any of these with install_package",
                        f"Need more details? Ask about a specific package"
                    ] if packages else ["Try a different search term"]
                }
        
        # Fallback response
        return self._mock_search_response(query)
    
    async def _install_package(
        self,
        params: Dict[str, Any],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """Handle package installation"""
        package = params.get("package", "")
        preview = params.get("preview", False)
        
        if not package:
            return self._error_response("Package name is required")
        
        # Check for referential package ("that one", "the first one")
        if conversation_id and self._is_referential(package):
            package = self._resolve_package_reference(package, conversation_id)
            if not package:
                return self._error_response(
                    "Cannot resolve package reference. Please specify the package name."
                )
        
        if self.nix_bridge:
            result = await self.nix_bridge.process_intent(
                intent="install",
                command=f"install {package}",
                context={"preview": preview}
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "tool": "install_package",
                    "data": {
                        "package": package,
                        "action": "preview" if preview else "installed",
                        "details": result.get("details", {})
                    },
                    "message": f"{'Would install' if preview else 'Successfully installed'} {package}",
                    "suggestions": [
                        "The package is now available to use",
                        "You may need to restart your shell for PATH updates"
                    ] if not preview else ["Remove 'preview' to actually install"]
                }
        
        return self._mock_install_response(package, preview)
    
    async def _explain_concept(
        self,
        params: Dict[str, Any],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """Explain a NixOS concept"""
        concept = params.get("concept", "")
        depth = params.get("depth", "intermediate")
        
        if not concept:
            return self._error_response("Concept is required")
        
        # Map of concepts to explanations at different levels
        explanations = {
            "generations": {
                "beginner": "Generations are like save points in a video game. Each time you change your system, NixOS creates a new generation. If something goes wrong, you can go back to an earlier save point.",
                "intermediate": "Generations are immutable snapshots of your entire system configuration. Each nixos-rebuild creates a new generation, allowing you to boot into previous configurations if needed.",
                "advanced": "Generations are symlink farms pointing to immutable /nix/store paths, implementing transactional system updates. The bootloader maintains references to multiple generations, enabling atomic rollbacks via profile switching."
            },
            "nix-store": {
                "beginner": "The /nix/store is like a library where NixOS keeps all software. Each program has its own shelf, so programs don't interfere with each other.",
                "intermediate": "The /nix/store contains all packages in isolation, identified by cryptographic hashes. This enables reproducibility, rollbacks, and multiple versions coexisting.",
                "advanced": "/nix/store paths are content-addressed using SHA256 hashes of their build inputs, creating a Merkle DAG. This enables deterministic builds, binary substitution, and garbage collection of unreferenced paths."
            },
            "flakes": {
                "beginner": "Flakes are like recipes that always make the same dish. They make sure everyone gets exactly the same software setup.",
                "intermediate": "Flakes are a new way to manage Nix projects with explicit dependencies, version locking, and standardized structure. They replace channels with reproducible inputs.",
                "advanced": "Flakes provide hermetic evaluation with pure inputs, content-addressed fetching, and a standardized schema. They enable composition via follows, override systems, and evaluation caching."
            }
        }
        
        explanation = explanations.get(concept.lower(), {}).get(depth)
        
        if explanation:
            return {
                "success": True,
                "tool": "explain_concept",
                "data": {
                    "concept": concept,
                    "depth": depth,
                    "explanation": explanation
                },
                "message": f"Explanation of {concept} ({depth} level)",
                "suggestions": [
                    f"Would you like a {('more advanced' if depth != 'advanced' else 'simpler')} explanation?",
                    "Any specific aspect you'd like to explore?"
                ]
            }
        
        return {
            "success": True,
            "tool": "explain_concept",
            "data": {
                "concept": concept,
                "depth": depth,
                "explanation": f"NixOS concept '{concept}' - explanation would be generated based on depth level"
            },
            "message": f"Explanation for {concept}",
            "suggestions": ["Ask about specific NixOS concepts like 'generations', 'nix-store', or 'flakes'"]
        }
    
    async def _list_installed(
        self,
        params: Dict[str, Any],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """List installed packages"""
        filter_str = params.get("filter", "")
        
        if self.nix_bridge:
            result = await self.nix_bridge.process_intent(
                intent="list",
                command="list installed packages",
                context={"filter": filter_str} if filter_str else {}
            )
            
            if result.get("success"):
                packages = result.get("packages", [])
                return {
                    "success": True,
                    "tool": "list_installed",
                    "data": {
                        "total": len(packages),
                        "filtered": bool(filter_str),
                        "packages": packages[:20]  # Limit for LLM
                    },
                    "message": f"Found {len(packages)} installed packages",
                    "suggestions": [
                        "You can remove packages with remove_package",
                        "Use system_health to check for issues"
                    ]
                }
        
        # Mock response
        return {
            "success": True,
            "tool": "list_installed",
            "data": {
                "total": 127,
                "packages": ["firefox", "git", "neovim", "python3", "nodejs"]
            },
            "message": "Showing sample of installed packages",
            "suggestions": ["Full list available via direct CLI"]
        }
    
    async def _system_health(
        self,
        params: Dict[str, Any],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """Check system health"""
        return {
            "success": True,
            "tool": "system_health",
            "data": {
                "status": "healthy",
                "checks": {
                    "disk_space": {"status": "ok", "detail": "42GB free"},
                    "generations": {"status": "ok", "detail": "12 generations, 3GB can be reclaimed"},
                    "channel_updates": {"status": "info", "detail": "Updates available"},
                    "configuration": {"status": "ok", "detail": "No syntax errors"}
                },
                "recommendations": [
                    "Consider running garbage collection to free 3GB",
                    "Channel updates are available"
                ]
            },
            "message": "System is healthy with minor recommendations",
            "suggestions": [
                "Run garbage collection to free space?",
                "Check available updates?"
            ]
        }
    
    def _is_referential(self, text: str) -> bool:
        """Check if text contains references to previous context"""
        referential_phrases = [
            "that", "this", "the first", "the second", 
            "the last", "previous", "above", "it"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in referential_phrases)
    
    def _resolve_package_reference(
        self,
        reference: str,
        conversation_id: str
    ) -> Optional[str]:
        """Resolve a package reference from conversation history"""
        if conversation_id not in self.conversations:
            return None
            
        history = self.conversations[conversation_id].get("history", [])
        
        # Look for recent search results
        for entry in reversed(history):
            if entry.get("tool") == "search_packages":
                packages = entry.get("data", {}).get("packages", [])
                if packages:
                    if "first" in reference.lower():
                        return packages[0].get("name")
                    elif "last" in reference.lower():
                        return packages[-1].get("name")
                    # Could add more sophisticated resolution
        
        return None
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "success": False,
            "error": message,
            "suggestions": [
                "Check the tool documentation",
                "Try a different approach"
            ]
        }
    
    def _mock_search_response(self, query: str) -> Dict[str, Any]:
        """Mock search response for testing without backend"""
        return {
            "success": True,
            "tool": "search_packages",
            "data": {
                "query": query,
                "found": 3,
                "packages": [
                    {"name": "firefox", "description": "Web browser"},
                    {"name": "chromium", "description": "Web browser"},
                    {"name": "brave", "description": "Privacy-focused browser"}
                ]
            },
            "message": f"Mock search results for '{query}'",
            "suggestions": ["This is a mock response for testing"]
        }
    
    def _mock_install_response(self, package: str, preview: bool) -> Dict[str, Any]:
        """Mock install response for testing without backend"""
        return {
            "success": True,
            "tool": "install_package",
            "data": {
                "package": package,
                "action": "preview" if preview else "would_install"
            },
            "message": f"Mock: {'Would install' if preview else 'Would install'} {package}",
            "suggestions": ["This is a mock response for testing"]
        }


async def demo_llm_interaction():
    """Demonstrate how an LLM would interact with this interface"""
    
    print("🤖 LLM Interface Demonstration")
    print("=" * 60)
    
    # Initialize interface
    interface = LLMInterface()
    conversation_id = "demo-conversation-001"
    
    # Show available tools
    print("\n📚 Available Tools:")
    tools = interface.get_tool_definitions()
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    print("\n" + "=" * 60)
    print("🎭 Simulating LLM Conversation:")
    print("=" * 60)
    
    # Simulate a conversation flow
    interactions = [
        {
            "user": "I need something to edit code",
            "tool": "search_packages",
            "params": {"query": "code editor"}
        },
        {
            "user": "Tell me about the nix store",
            "tool": "explain_concept",
            "params": {"concept": "nix-store", "depth": "beginner"}
        },
        {
            "user": "What's the health of my system?",
            "tool": "system_health",
            "params": {}
        },
        {
            "user": "Install neovim but show me what would happen first",
            "tool": "install_package",
            "params": {"package": "neovim", "preview": True}
        }
    ]
    
    for interaction in interactions:
        print(f"\n👤 User: {interaction['user']}")
        print(f"🤖 LLM: Processing with tool '{interaction['tool']}'...")
        
        # Process tool call
        result = await interface.process_tool_call(
            interaction["tool"],
            interaction["params"],
            conversation_id
        )
        
        # Display result
        if result["success"]:
            print(f"✅ {result['message']}")
            if "data" in result:
                # Show relevant data
                data = result["data"]
                if "packages" in data and data["packages"]:
                    print("   Found packages:")
                    for pkg in data["packages"][:3]:
                        if isinstance(pkg, dict):
                            print(f"   - {pkg.get('name', pkg)}: {pkg.get('description', '')}")
                        else:
                            print(f"   - {pkg}")
                elif "explanation" in data:
                    print(f"   📖 {data['explanation']}")
                elif "checks" in data:
                    print("   System checks:")
                    for check, details in data["checks"].items():
                        print(f"   - {check}: {details['status']}")
            
            # Show suggestions
            if result.get("suggestions"):
                print("   💡 Suggestions:")
                for suggestion in result["suggestions"][:2]:
                    print(f"      - {suggestion}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✨ Demonstration Complete!")
    print("\nThis interface enables:")
    print("  • Natural conversation with context")
    print("  • Tool discovery and execution")
    print("  • Structured responses for LLM processing")
    print("  • Seamless integration with consciousness layer")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demo_llm_interaction())