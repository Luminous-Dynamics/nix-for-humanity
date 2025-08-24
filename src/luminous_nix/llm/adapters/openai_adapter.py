#!/usr/bin/env python3
"""
🤖 OpenAI Adapter - Format tools and responses for ChatGPT
Implements OpenAI's function calling format
"""

from typing import Dict, Any, List
import json


class OpenAIAdapter:
    """
    Adapter for OpenAI's function calling format
    Converts Luminous Nix tools to OpenAI schema
    """
    
    def __init__(self, llm_interface):
        """Initialize with reference to LLM interface"""
        self.llm_interface = llm_interface
        
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Convert tool definitions to OpenAI function calling format
        
        Returns:
            List of tool schemas in OpenAI format
        """
        tools = []
        
        # Define tools in OpenAI's expected format
        tool_definitions = [
            {
                "name": "search_packages",
                "description": "Search for NixOS packages by name or description. Returns a list of available packages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search term (package name or description keywords)"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["development", "productivity", "games", "multimedia", "system", "network"],
                            "description": "Optional category to filter results"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "install_package",
                "description": "Install a NixOS package on the system. Can preview the operation before executing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "The exact name of the package to install"
                        },
                        "preview": {
                            "type": "boolean",
                            "description": "If true, show what would happen without actually installing",
                            "default": False
                        },
                        "user": {
                            "type": "boolean",
                            "description": "If true, install to user profile instead of system-wide",
                            "default": False
                        }
                    },
                    "required": ["package"]
                }
            },
            {
                "name": "remove_package",
                "description": "Remove/uninstall a NixOS package from the system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "The name of the package to remove"
                        },
                        "user": {
                            "type": "boolean",
                            "description": "If true, remove from user profile instead of system-wide",
                            "default": False
                        }
                    },
                    "required": ["package"]
                }
            },
            {
                "name": "list_installed",
                "description": "List all installed packages on the system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Optional filter to search within installed packages"
                        },
                        "user": {
                            "type": "boolean",
                            "description": "If true, list user packages only",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "explain_concept",
                "description": "Explain a NixOS concept in user-appropriate language.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "concept": {
                            "type": "string",
                            "description": "The NixOS concept to explain (e.g., 'nix-store', 'generations', 'flakes')"
                        },
                        "depth": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                            "description": "Level of technical detail",
                            "default": "intermediate"
                        }
                    },
                    "required": ["concept"]
                }
            },
            {
                "name": "system_health",
                "description": "Check system health and get maintenance recommendations.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "update_system",
                "description": "Update the NixOS system, channels, and packages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "preview": {
                            "type": "boolean",
                            "description": "If true, show what would be updated without doing it",
                            "default": True
                        },
                        "channel": {
                            "type": "boolean",
                            "description": "Update channel information",
                            "default": True
                        },
                        "packages": {
                            "type": "boolean",
                            "description": "Update installed packages",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "rollback",
                "description": "Rollback the system to a previous generation/configuration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "generation": {
                            "type": "integer",
                            "description": "Specific generation number to rollback to (or previous if not specified)"
                        },
                        "preview": {
                            "type": "boolean",
                            "description": "If true, show what would happen without rolling back",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "generate_config",
                "description": "Generate NixOS configuration for specific use cases.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["desktop", "server", "development", "gaming", "minimal"],
                            "description": "Type of configuration to generate"
                        },
                        "packages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of packages to include"
                        },
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of services to enable"
                        },
                        "preview": {
                            "type": "boolean",
                            "description": "If true, return config without writing to disk",
                            "default": True
                        }
                    },
                    "required": ["type"]
                }
            }
        ]
        
        # Convert to OpenAI format
        for tool_def in tool_definitions:
            tools.append({
                "type": "function",
                "function": tool_def
            })
        
        return tools
    
    def format_tool_call(
        self,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format a tool call from OpenAI into our internal format
        
        Args:
            function_name: Name of the function being called
            arguments: Arguments from OpenAI
            
        Returns:
            Formatted request for our LLM interface
        """
        return {
            "tool": function_name,
            "parameters": arguments,
            "source": "openai"
        }
    
    def format_response(
        self,
        result: Dict[str, Any],
        function_name: str
    ) -> str:
        """
        Format our response for OpenAI to understand
        
        Args:
            result: Result from our tool execution
            function_name: Name of the function that was called
            
        Returns:
            Formatted response string for OpenAI
        """
        if result.get("success"):
            # Format successful response
            response_parts = []
            
            # Add main message
            if "message" in result:
                response_parts.append(result["message"])
            
            # Add specific data based on function
            if function_name == "search_packages" and "packages" in result.get("data", {}):
                packages = result["data"]["packages"]
                if packages:
                    response_parts.append("\nFound packages:")
                    for pkg in packages[:5]:  # Limit to 5 for brevity
                        name = pkg.get("name", pkg)
                        desc = pkg.get("description", "")
                        response_parts.append(f"• {name}: {desc}")
            
            elif function_name == "install_package":
                if result.get("data", {}).get("action") == "preview":
                    response_parts.append("This would install the package (preview mode).")
                else:
                    response_parts.append("Package installed successfully.")
            
            elif function_name == "system_health" and "checks" in result.get("data", {}):
                response_parts.append("\nSystem health checks:")
                for check, details in result["data"]["checks"].items():
                    status = details.get("status", "unknown")
                    detail = details.get("detail", "")
                    response_parts.append(f"• {check}: {status} - {detail}")
            
            # Add suggestions if available
            if "suggestions" in result:
                response_parts.append("\nSuggestions:")
                for suggestion in result["suggestions"][:2]:
                    response_parts.append(f"• {suggestion}")
            
            return "\n".join(response_parts)
        
        else:
            # Format error response
            error_msg = f"Error: {result.get('error', 'Operation failed')}"
            
            if "suggestions" in result:
                error_msg += "\n\nSuggestions:"
                for suggestion in result["suggestions"]:
                    error_msg += f"\n• {suggestion}"
            
            return error_msg
    
    def create_system_message(self) -> str:
        """
        Create a system message for ChatGPT explaining how to use the tools
        
        Returns:
            System message string
        """
        return """You are a helpful NixOS assistant with access to tools for managing the system.

When users ask about NixOS operations, use the provided tools to help them:
- Use 'search_packages' to find software
- Use 'install_package' to install software (always preview first for safety)
- Use 'explain_concept' to explain NixOS concepts at the appropriate level
- Use 'system_health' to check system status
- Use 'list_installed' to show what's installed

Important guidelines:
1. Always search before installing to verify package names
2. Use preview mode for destructive operations
3. Adapt explanations to the user's expertise level
4. Suggest next steps after each operation
5. If a user refers to "that" or "the first one", use context from previous messages

You're helping users who may be new to NixOS, so be friendly and explanatory."""
    
    def format_for_api(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Format a complete request for OpenAI API
        
        Args:
            messages: Conversation history
            model: OpenAI model to use
            
        Returns:
            Formatted API request
        """
        return {
            "model": model,
            "messages": [
                {"role": "system", "content": self.create_system_message()},
                *messages
            ],
            "tools": self.get_tools_schema(),
            "tool_choice": "auto"  # Let the model decide when to use tools
        }
    
    def parse_streaming_response(self, chunk: str) -> Dict[str, Any]:
        """
        Parse a streaming response chunk from OpenAI
        
        Args:
            chunk: Streaming chunk from OpenAI
            
        Returns:
            Parsed chunk data
        """
        try:
            # OpenAI streaming format handling
            if chunk.startswith("data: "):
                chunk = chunk[6:]  # Remove "data: " prefix
            
            if chunk == "[DONE]":
                return {"done": True}
            
            data = json.loads(chunk)
            
            # Extract relevant information
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]
                
                # Check for tool calls
                if "delta" in choice and "tool_calls" in choice["delta"]:
                    return {
                        "type": "tool_call",
                        "data": choice["delta"]["tool_calls"]
                    }
                
                # Check for content
                elif "delta" in choice and "content" in choice["delta"]:
                    return {
                        "type": "content",
                        "content": choice["delta"]["content"]
                    }
            
            return {"type": "other", "data": data}
            
        except json.JSONDecodeError:
            return {"type": "error", "error": "Failed to parse chunk"}


def demo_openai_adapter():
    """Demonstrate OpenAI adapter functionality"""
    print("🤖 OpenAI Adapter Demonstration")
    print("=" * 60)
    
    # Create adapter (mock LLM interface)
    adapter = OpenAIAdapter(None)
    
    # Show tool schema
    print("\n📚 Tool Schema for OpenAI:")
    tools = adapter.get_tools_schema()
    print(f"Total tools available: {len(tools)}")
    
    for tool in tools[:2]:  # Show first 2 tools
        func = tool["function"]
        print(f"\n• {func['name']}")
        print(f"  Description: {func['description'][:80]}...")
        print(f"  Parameters: {list(func['parameters']['properties'].keys())}")
    
    # Show system message
    print("\n💬 System Message:")
    system_msg = adapter.create_system_message()
    print(system_msg[:300] + "...")
    
    # Test response formatting
    print("\n📤 Response Formatting:")
    
    # Mock search result
    search_result = {
        "success": True,
        "message": "Found 3 packages",
        "data": {
            "packages": [
                {"name": "firefox", "description": "Web browser"},
                {"name": "chromium", "description": "Open source browser"}
            ]
        },
        "suggestions": ["Install one of these packages?"]
    }
    
    formatted = adapter.format_response(search_result, "search_packages")
    print(formatted)
    
    print("\n" + "=" * 60)
    print("✨ OpenAI adapter ready for ChatGPT integration!")


if __name__ == "__main__":
    demo_openai_adapter()