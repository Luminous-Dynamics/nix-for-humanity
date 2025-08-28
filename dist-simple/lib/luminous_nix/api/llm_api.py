#!/usr/bin/env python3
"""
🌐 LLM API - RESTful Interface for LLM Integration
Provides structured endpoints for LLMs to interact with Luminous Nix
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncio
import uuid

# Import core operations
from ..core.nix_operations import NixOperations

# Import consciousness components
try:
    from ..consciousness.consciousness_integration import ConsciousnessIntegration
    from ..consciousness.session_memory import get_session_memory
    from ..consciousness.persona_adapter import get_persona_adapter
    from ..consciousness.contextual_mode_selector import get_mode_selector
    CONSCIOUSNESS_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_AVAILABLE = False

# Import LLM interface
from ..llm.llm_interface_poc import LLMInterface


# Create FastAPI app
app = FastAPI(
    title="Luminous Nix LLM API",
    description="Natural language interface for NixOS operations",
    version="1.0.0"
)

# Add CORS middleware for web-based LLMs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
nix_ops = NixOperations()
llm_interface = LLMInterface()
conversations = {}  # Track conversation contexts


# Pydantic models for request/response
class LLMRequest(BaseModel):
    """Request from an LLM"""
    message: str = Field(..., description="Natural language message from user")
    conversation_id: Optional[str] = Field(None, description="Conversation tracking ID")
    llm_type: str = Field("generic", description="Type of LLM (claude, gpt, local)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class ToolCallRequest(BaseModel):
    """Direct tool call request"""
    tool: str = Field(..., description="Tool name to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    conversation_id: Optional[str] = Field(None, description="Conversation tracking ID")


class ConversationContext:
    """Maintains conversation state"""
    
    def __init__(self, conversation_id: str):
        self.id = conversation_id
        self.started = datetime.now()
        self.history = []
        self.last_search_results = []
        self.user_profile = {}
        self.preferences = {}
        
    def add_exchange(self, user_message: str, response: dict):
        """Add an exchange to history"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "response": response
        })
        
        # Keep only last 20 exchanges for context
        if len(self.history) > 20:
            self.history = self.history[-20:]
    
    def get_context(self) -> dict:
        """Get relevant context for current interaction"""
        return {
            "session_duration": (datetime.now() - self.started).seconds,
            "exchange_count": len(self.history),
            "last_search": self.last_search_results[:5] if self.last_search_results else [],
            "user_profile": self.user_profile,
            "preferences": self.preferences
        }


# API Endpoints

@app.get("/")
async def root():
    """API root information"""
    return {
        "name": "Luminous Nix LLM API",
        "version": "1.0.0",
        "endpoints": {
            "tools": "/tools - List available tools",
            "process": "/llm/process - Process natural language",
            "tool_call": "/llm/tool - Execute specific tool",
            "health": "/health - API health status"
        }
    }


@app.get("/tools")
async def get_tools():
    """Get all available tool definitions"""
    return {
        "tools": llm_interface.get_tool_definitions(),
        "categories": {
            "package_management": ["search_packages", "install_package", "remove_package", "list_installed"],
            "system": ["system_health", "update_system", "rollback"],
            "learning": ["explain_concept", "get_help"],
            "configuration": ["generate_config", "validate_config"]
        }
    }


@app.post("/llm/process")
async def process_llm_request(request: LLMRequest):
    """
    Process natural language from an LLM
    This endpoint handles conversational flow
    """
    try:
        # Get or create conversation context
        if request.conversation_id:
            if request.conversation_id not in conversations:
                conversations[request.conversation_id] = ConversationContext(request.conversation_id)
            context = conversations[request.conversation_id]
        else:
            # Create ephemeral context
            context = ConversationContext(str(uuid.uuid4()))
        
        # Determine intent from natural language
        intent = extract_intent(request.message, context)
        
        # Execute appropriate action
        if intent["action"] == "search":
            result = await handle_search(intent["query"], context)
        elif intent["action"] == "install":
            result = await handle_install(intent["package"], intent.get("preview", False), context)
        elif intent["action"] == "explain":
            result = await handle_explain(intent["concept"], intent.get("depth", "intermediate"))
        elif intent["action"] == "list":
            result = await handle_list(intent.get("filter"))
        elif intent["action"] == "health":
            result = await handle_health()
        elif intent["action"] == "help":
            result = await handle_help(intent.get("topic"))
        else:
            result = {
                "success": False,
                "error": "Could not understand the request",
                "suggestions": [
                    "Try asking about installing software",
                    "Ask for help with a specific topic",
                    "Request a system health check"
                ]
            }
        
        # Add exchange to context
        if request.conversation_id:
            context.add_exchange(request.message, result)
        
        # Enhance response with LLM-specific formatting
        enhanced_result = enhance_for_llm(result, request.llm_type)
        
        return enhanced_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/llm/tool")
async def execute_tool(request: ToolCallRequest):
    """
    Execute a specific tool directly
    This endpoint is for LLMs that support function calling
    """
    try:
        result = await llm_interface.process_tool_call(
            request.tool,
            request.parameters,
            request.conversation_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/llm/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming responses
    Useful for real-time interaction and progress updates
    """
    await websocket.accept()
    conversation_id = str(uuid.uuid4())
    context = ConversationContext(conversation_id)
    conversations[conversation_id] = context
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process message
            intent = extract_intent(data["message"], context)
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "processing",
                "intent": intent["action"],
                "message": f"Processing {intent['action']} request..."
            })
            
            # Execute with progress updates
            async for update in execute_with_progress(intent, context):
                await websocket.send_json(update)
            
            # Send completion
            await websocket.send_json({
                "type": "complete",
                "message": "Request completed"
            })
            
    except WebSocketDisconnect:
        # Clean up conversation
        del conversations[conversation_id]


@app.get("/health")
async def health_check():
    """API health status"""
    health = nix_ops.system_health()
    
    return {
        "api_status": "healthy",
        "system_health": health.get("status", "unknown"),
        "consciousness_available": CONSCIOUSNESS_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }


# Helper functions

def extract_intent(message: str, context: ConversationContext) -> dict:
    """
    Extract intent from natural language message
    This is simplified - would use NLP in production
    """
    message_lower = message.lower()
    
    # Check for referential commands
    if any(word in message_lower for word in ["that", "it", "those", "them"]):
        return resolve_reference(message, context)
    
    # Package operations
    if any(word in message_lower for word in ["install", "add", "get"]):
        # Extract package name
        words = message.split()
        package = None
        for i, word in enumerate(words):
            if word in ["install", "add", "get"] and i + 1 < len(words):
                package = words[i + 1]
                break
        
        return {
            "action": "install",
            "package": package or "unknown",
            "preview": "preview" in message_lower or "test" in message_lower
        }
    
    if any(word in message_lower for word in ["search", "find", "look for"]):
        # Extract search query
        query = message.lower()
        for prefix in ["search for", "find", "look for", "search"]:
            if prefix in query:
                query = query.split(prefix)[-1].strip()
                break
        
        return {"action": "search", "query": query}
    
    if any(word in message_lower for word in ["list", "show", "installed"]):
        return {"action": "list", "filter": None}
    
    if any(word in message_lower for word in ["explain", "what is", "tell me about"]):
        # Extract concept
        concept = message.lower()
        for prefix in ["explain", "what is", "tell me about"]:
            if prefix in concept:
                concept = concept.split(prefix)[-1].strip()
                break
        
        return {
            "action": "explain",
            "concept": concept,
            "depth": detect_expertise_level(context)
        }
    
    if any(word in message_lower for word in ["health", "status", "check"]):
        return {"action": "health"}
    
    if any(word in message_lower for word in ["help", "how do i", "how to"]):
        return {"action": "help", "topic": message}
    
    # Default to search if unclear
    return {"action": "search", "query": message}


def resolve_reference(message: str, context: ConversationContext) -> dict:
    """Resolve referential commands using context"""
    message_lower = message.lower()
    
    # Check for package references
    if "install" in message_lower and context.last_search_results:
        if "first" in message_lower:
            package = context.last_search_results[0]["name"]
        elif "second" in message_lower:
            package = context.last_search_results[1]["name"] if len(context.last_search_results) > 1 else None
        else:
            # Default to first result
            package = context.last_search_results[0]["name"]
        
        return {
            "action": "install",
            "package": package,
            "preview": "preview" in message_lower
        }
    
    # Default to requesting clarification
    return {
        "action": "clarify",
        "message": "I need more context to understand that reference"
    }


def detect_expertise_level(context: ConversationContext) -> str:
    """Detect user expertise level from conversation"""
    # Simple heuristic - would use ML in production
    exchange_count = len(context.history)
    
    if exchange_count < 3:
        return "beginner"
    elif exchange_count < 10:
        return "intermediate"
    else:
        return "advanced"


async def handle_search(query: str, context: ConversationContext) -> dict:
    """Handle package search"""
    result = nix_ops.search_packages(query)
    
    # Store results in context for references
    if result.get("success") and result.get("packages"):
        context.last_search_results = result["packages"]
    
    return result


async def handle_install(package: str, preview: bool, context: ConversationContext) -> dict:
    """Handle package installation"""
    return nix_ops.install_package(package, preview=preview)


async def handle_explain(concept: str, depth: str) -> dict:
    """Handle concept explanation"""
    # This would integrate with knowledge base
    explanations = {
        "nix-store": {
            "beginner": "The /nix/store is where all your software lives, each in its own space",
            "intermediate": "The /nix/store contains immutable packages identified by hashes",
            "advanced": "/nix/store uses content-addressing with SHA256 for deterministic builds"
        }
    }
    
    explanation = explanations.get(concept, {}).get(depth, f"Information about {concept}")
    
    return {
        "success": True,
        "concept": concept,
        "depth": depth,
        "explanation": explanation
    }


async def handle_list(filter_str: Optional[str]) -> dict:
    """Handle listing installed packages"""
    return nix_ops.list_installed(filter_str=filter_str)


async def handle_health() -> dict:
    """Handle system health check"""
    return nix_ops.system_health()


async def handle_help(topic: Optional[str]) -> dict:
    """Handle help requests"""
    return {
        "success": True,
        "topic": topic or "general",
        "help": "Help information would be provided here",
        "suggestions": [
            "Try 'search for text editors'",
            "Ask 'how do I install software?'",
            "Request 'check system health'"
        ]
    }


def enhance_for_llm(result: dict, llm_type: str) -> dict:
    """Enhance response for specific LLM type"""
    enhanced = result.copy()
    
    if llm_type == "claude":
        # Add thinking process for Claude
        enhanced["thinking"] = generate_reasoning(result)
    elif llm_type == "gpt":
        # Add structured format for GPT
        enhanced["structured"] = structure_for_gpt(result)
    
    # Add universal enhancements
    enhanced["suggestions"] = generate_suggestions(result)
    enhanced["confidence"] = calculate_confidence(result)
    
    return enhanced


def generate_reasoning(result: dict) -> str:
    """Generate reasoning explanation"""
    if result.get("success"):
        return f"Successfully processed the request with {result.get('action', 'unknown')} action"
    else:
        return f"Encountered an issue: {result.get('error', 'unknown error')}"


def structure_for_gpt(result: dict) -> dict:
    """Structure response for GPT"""
    return {
        "status": "success" if result.get("success") else "error",
        "data": result.get("data", {}),
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "action": result.get("action", "unknown")
        }
    }


def generate_suggestions(result: dict) -> list:
    """Generate contextual suggestions"""
    suggestions = result.get("suggestions", [])
    
    if result.get("action") == "search" and result.get("packages"):
        suggestions.append("Would you like to install one of these packages?")
    elif result.get("action") == "installed":
        suggestions.append("The package is now ready to use")
    
    return suggestions[:3]  # Limit suggestions


def calculate_confidence(result: dict) -> float:
    """Calculate confidence in the result"""
    if result.get("success"):
        return 0.95 if result.get("data") else 0.8
    else:
        return 0.3


async def execute_with_progress(intent: dict, context: ConversationContext):
    """Execute intent with progress updates for streaming"""
    yield {"type": "progress", "message": "Starting operation...", "progress": 0}
    
    # Simulate progress for demo
    for i in range(1, 5):
        await asyncio.sleep(0.5)
        yield {
            "type": "progress",
            "message": f"Processing step {i}/4...",
            "progress": i * 25
        }
    
    # Execute actual operation
    if intent["action"] == "search":
        result = await handle_search(intent["query"], context)
    elif intent["action"] == "install":
        result = await handle_install(intent["package"], intent.get("preview", False), context)
    else:
        result = {"success": True, "message": "Operation completed"}
    
    yield {
        "type": "result",
        "data": result,
        "progress": 100
    }


# Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)