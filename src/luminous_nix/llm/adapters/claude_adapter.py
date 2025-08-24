#!/usr/bin/env python3
"""
🌊 Claude Adapter - Format tools and responses for Claude
Implements Claude's tool use format with consciousness-first design
"""

from typing import Dict, Any, List, Optional
import json


class ClaudeAdapter:
    """
    Adapter for Claude's tool use format
    Emphasizes transparent reasoning and consciousness-first interaction
    """
    
    def __init__(self, llm_interface):
        """Initialize with reference to LLM interface"""
        self.llm_interface = llm_interface
        
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Convert tool definitions to Claude's tool use format
        
        Returns:
            List of tool schemas in Claude format
        """
        tools = []
        
        # Define tools in Claude's format (similar to OpenAI but with Claude-specific enhancements)
        tool_definitions = [
            {
                "name": "search_packages",
                "description": "Search for NixOS packages. I'll help you find the right software by searching package names and descriptions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What you're looking for (e.g., 'text editor', 'firefox', 'development tools')"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter",
                            "enum": ["development", "productivity", "games", "multimedia", "system", "network"]
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "install_package",
                "description": "Install a NixOS package. I can preview the operation first to show what would happen.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "Exact package name to install"
                        },
                        "preview": {
                            "type": "boolean",
                            "description": "Preview without installing (recommended for safety)",
                            "default": True
                        },
                        "user": {
                            "type": "boolean",
                            "description": "Install for current user only (not system-wide)",
                            "default": False
                        }
                    },
                    "required": ["package"]
                }
            },
            {
                "name": "explain_concept",
                "description": "I'll explain NixOS concepts in a way that matches your expertise level.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "concept": {
                            "type": "string",
                            "description": "Concept to explain (e.g., 'generations', 'nix-store', 'flakes', 'channels')"
                        },
                        "depth": {
                            "type": "string",
                            "description": "How technical should the explanation be?",
                            "enum": ["beginner", "intermediate", "advanced"],
                            "default": "intermediate"
                        }
                    },
                    "required": ["concept"]
                }
            },
            {
                "name": "system_health",
                "description": "Check your NixOS system's health and get maintenance recommendations.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "list_installed",
                "description": "Show installed packages on your system.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Filter packages by name"
                        },
                        "user": {
                            "type": "boolean",
                            "description": "Show user packages only",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "resolve_reference",
                "description": "Resolve contextual references like 'that one' or 'the first option' from our conversation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reference": {
                            "type": "string",
                            "description": "The reference to resolve (e.g., 'that', 'the first one', 'it')"
                        },
                        "action": {
                            "type": "string",
                            "description": "What to do with the resolved reference",
                            "enum": ["install", "explain", "remove", "show"]
                        }
                    },
                    "required": ["reference", "action"]
                }
            }
        ]
        
        return tool_definitions
    
    def format_tool_use(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        thinking: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format a tool use for Claude's format
        
        Args:
            tool_name: Name of the tool to use
            tool_input: Input parameters for the tool
            thinking: Optional reasoning about why using this tool
            
        Returns:
            Formatted tool use block
        """
        tool_use = {
            "type": "tool_use",
            "name": tool_name,
            "input": tool_input
        }
        
        # Add thinking process if provided (Claude appreciates transparency)
        if thinking:
            tool_use["thinking"] = thinking
        
        return tool_use
    
    def format_response(
        self,
        result: Dict[str, Any],
        tool_name: str,
        include_thinking: bool = True
    ) -> str:
        """
        Format response in Claude's consciousness-first style
        
        Args:
            result: Result from tool execution
            tool_name: Name of the tool that was used
            include_thinking: Whether to include reasoning
            
        Returns:
            Formatted response with Claude's characteristic thoughtfulness
        """
        response_parts = []
        
        # Add thinking process if enabled
        if include_thinking and result.get("success"):
            thinking = self._generate_thinking(tool_name, result)
            if thinking:
                response_parts.append(f"*{thinking}*\n")
        
        if result.get("success"):
            # Main response
            if tool_name == "search_packages":
                packages = result.get("data", {}).get("packages", [])
                if packages:
                    response_parts.append("I found these packages for you:\n")
                    for i, pkg in enumerate(packages[:5], 1):
                        name = pkg.get("name", pkg)
                        desc = pkg.get("description", "")
                        response_parts.append(f"{i}. **{name}** - {desc}")
                    
                    if len(packages) > 5:
                        response_parts.append(f"\n...and {len(packages) - 5} more options available")
                else:
                    response_parts.append("No packages found matching that search.")
            
            elif tool_name == "install_package":
                action = result.get("data", {}).get("action")
                package = result.get("data", {}).get("package")
                
                if action == "preview":
                    response_parts.append(f"📋 **Preview**: Installing '{package}' would:")
                    response_parts.append("• Download the package and dependencies")
                    response_parts.append("• Add it to your system profile")
                    response_parts.append("• Make it immediately available")
                    response_parts.append("\nWould you like me to proceed with the actual installation?")
                else:
                    response_parts.append(f"✅ Successfully installed **{package}**!")
                    response_parts.append("\nThe package is now available in your PATH.")
            
            elif tool_name == "explain_concept":
                concept = result.get("data", {}).get("concept")
                explanation = result.get("data", {}).get("explanation")
                depth = result.get("data", {}).get("depth", "intermediate")
                
                response_parts.append(f"## {concept.title()} ({depth} explanation)\n")
                response_parts.append(explanation)
            
            elif tool_name == "system_health":
                health = result.get("data", {})
                status = health.get("status", "unknown")
                
                emoji = "✅" if status == "healthy" else "⚠️"
                response_parts.append(f"{emoji} System Status: **{status.title()}**\n")
                
                if "checks" in health:
                    response_parts.append("Health Checks:")
                    for check, details in health["checks"].items():
                        status_icon = "✓" if details.get("status") == "ok" else "!"
                        response_parts.append(f"  {status_icon} {check}: {details.get('detail', 'N/A')}")
                
                if "recommendations" in health:
                    response_parts.append("\n💡 Recommendations:")
                    for rec in health["recommendations"]:
                        response_parts.append(f"  • {rec}")
            
            # Add consciousness-aware suggestions
            if "suggestions" in result:
                response_parts.append("\n" + self._format_suggestions(result["suggestions"]))
        
        else:
            # Error handling with empathy
            error = result.get("error", "Something went wrong")
            response_parts.append(f"I encountered an issue: {error}\n")
            
            if "suggestions" in result:
                response_parts.append("Here's what might help:")
                for suggestion in result["suggestions"]:
                    response_parts.append(f"• {suggestion}")
        
        return "\n".join(response_parts)
    
    def _generate_thinking(self, tool_name: str, result: Dict[str, Any]) -> Optional[str]:
        """Generate Claude's thinking process"""
        thinking_map = {
            "search_packages": "Let me search the NixOS package repository for you...",
            "install_package": "I'll help you install this package safely...",
            "explain_concept": "Let me explain this in a way that's helpful for your level...",
            "system_health": "Checking your system's health status...",
            "list_installed": "Looking at your installed packages..."
        }
        
        return thinking_map.get(tool_name)
    
    def _format_suggestions(self, suggestions: List[str]) -> str:
        """Format suggestions in Claude's helpful style"""
        if not suggestions:
            return ""
        
        formatted = "**What would you like to do next?**\n"
        for suggestion in suggestions[:3]:
            # Make suggestions more conversational
            if "install" in suggestion.lower():
                formatted += "• I can help you install one of these packages\n"
            elif "search" in suggestion.lower():
                formatted += "• We could search for something else\n"
            elif "explain" in suggestion.lower():
                formatted += "• I'd be happy to explain any concepts\n"
            else:
                formatted += f"• {suggestion}\n"
        
        return formatted.rstrip()
    
    def create_system_prompt(self) -> str:
        """
        Create a system prompt that embodies consciousness-first principles
        
        Returns:
            System prompt for Claude
        """
        return """You are a consciousness-first NixOS assistant, embodying the principles of Luminous Dynamics.

Core Values:
- **Preserve agency**: Empower users to make informed decisions
- **Progressive disclosure**: Reveal complexity as understanding grows
- **Mindful interaction**: Every response should reduce cognitive load
- **Transparent reasoning**: Share your thinking process when helpful

When helping with NixOS:
1. Always explain what will happen before doing it
2. Use preview mode for any system changes
3. Adapt your language to the user's expertise level
4. Remember context from our conversation
5. Suggest next steps that empower learning

You have access to tools that interface with the actual NixOS system. Use them thoughtfully:
- Search before suggesting installations
- Preview changes before applying them
- Check system health proactively
- Explain concepts when users seem confused

Remember: You're not just executing commands, you're helping someone learn and grow in their understanding of NixOS. Every interaction is an opportunity for gentle education and empowerment.

The consciousness layer invisibly adapts to each user - from Grandma Rose who needs gentle guidance to Developer Dan who wants precise control. Sense who you're talking with and adapt accordingly."""
    
    def format_for_api(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-opus-20240229"
    ) -> Dict[str, Any]:
        """
        Format a complete request for Claude API
        
        Args:
            messages: Conversation history
            model: Claude model to use
            
        Returns:
            Formatted API request
        """
        return {
            "model": model,
            "max_tokens": 4096,
            "messages": messages,
            "system": self.create_system_prompt(),
            "tools": self.get_tools_schema()
        }
    
    def parse_tool_use(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Parse tool use from Claude's response
        
        Args:
            message: Claude's response message
            
        Returns:
            Parsed tool use or None
        """
        # Claude typically formats tool use clearly
        # This would parse actual Claude API responses
        # For now, return a mock parse
        
        if "<tool_use>" in message:
            # Extract tool use block
            start = message.index("<tool_use>") + 11
            end = message.index("</tool_use>")
            tool_block = message[start:end]
            
            try:
                return json.loads(tool_block)
            except json.JSONDecodeError:
                return None
        
        return None


def demo_claude_adapter():
    """Demonstrate Claude adapter functionality"""
    print("🌊 Claude Adapter Demonstration")
    print("=" * 60)
    
    # Create adapter
    adapter = ClaudeAdapter(None)
    
    # Show tools
    print("\n📚 Tools for Claude:")
    tools = adapter.get_tools_schema()
    for tool in tools[:3]:
        print(f"\n• {tool['name']}")
        print(f"  {tool['description'][:80]}...")
    
    # Show system prompt
    print("\n💭 System Prompt (excerpt):")
    prompt = adapter.create_system_prompt()
    print(prompt[:400] + "...")
    
    # Test response formatting with Claude's style
    print("\n✨ Claude-style Response:")
    
    search_result = {
        "success": True,
        "data": {
            "packages": [
                {"name": "neovim", "description": "Vim-fork focused on extensibility"},
                {"name": "emacs", "description": "Extensible text editor"}
            ]
        },
        "suggestions": ["Install one?", "Search for something else?"]
    }
    
    formatted = adapter.format_response(search_result, "search_packages")
    print(formatted)
    
    print("\n" + "=" * 60)
    print("🌊 Claude adapter ready for consciousness-first interaction!")


if __name__ == "__main__":
    demo_claude_adapter()