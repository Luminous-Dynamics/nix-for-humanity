"""
🌐 REST API v1 for Nix for Humanity

This provides a versioned REST API that any frontend can use.
Built with FastAPI for automatic documentation and validation.
"""

import json
import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core.unified_backend import Context, NixForHumanityBackend, get_backend
from ..plugins.config_generator import ConfigGeneratorPlugin, SmartSearchPlugin

logger = logging.getLogger(__name__)

# Create FastAPI app with sacred metadata
app = FastAPI(
    title="Nix for Humanity API",
    description="🕉️ Natural language interface to NixOS with consciousness-first design",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend on startup
backend: NixForHumanityBackend | None = None
contexts: dict[str, Context] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize the sacred backend on startup"""
    global backend

    # Create backend with default config
    backend = get_backend({"dry_run": True})

    # Register plugins
    backend.register_plugin(ConfigGeneratorPlugin())
    backend.register_plugin(SmartSearchPlugin())

    # Initialize
    await backend.initialize()

    logger.info("🌐 API v1 initialized with sacred backend")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of sacred resources"""
    if backend:
        await backend.cleanup()
    logger.info("🌐 API v1 shutdown complete")


# Request/Response models with validation
class ExecuteRequest(BaseModel):
    """Request to execute a natural language query"""

    query: str = Field(..., description="Natural language query")
    dry_run: bool = Field(True, description="If true, don't actually execute")
    context_id: str | None = Field(None, description="Session context ID")
    options: dict[str, Any] | None = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "query": "install firefox",
                "dry_run": True,
                "context_id": "user-123",
                "options": {"verbose": True},
            }
        }


class ExecuteResponse(BaseModel):
    """Response from executing a query"""

    success: bool
    output: str
    error: str | None = None
    suggestions: list[str] = Field(default_factory=list)
    execution_time: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerateConfigRequest(BaseModel):
    """Request to generate NixOS configuration"""

    description: str = Field(..., description="Natural language description")
    format: str = Field("nix", description="Output format (nix, json)")

    class Config:
        schema_extra = {
            "example": {
                "description": "web server with nginx and postgresql",
                "format": "nix",
            }
        }


class SearchRequest(BaseModel):
    """Request to search for packages"""

    query: str = Field(..., description="Search query or description")
    limit: int = Field(10, description="Maximum results to return")
    smart: bool = Field(True, description="Use smart search by description")

    class Config:
        schema_extra = {
            "example": {"query": "markdown editor", "limit": 5, "smart": True}
        }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    backend_initialized: bool
    plugins_loaded: list[str]
    timestamp: datetime


# API Endpoints


@app.get("/api/v1/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        backend_initialized=backend is not None,
        plugins_loaded=backend.plugins.list_plugins() if backend else [],
        timestamp=datetime.now(),
    )


@app.post("/api/v1/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """
    Execute a natural language query

    This is the main endpoint that processes any natural language
    command through the unified backend.
    """
    if not backend:
        raise HTTPException(status_code=503, detail="Backend not initialized")

    try:
        # Get or create context
        context = None
        if request.context_id:
            if request.context_id not in contexts:
                contexts[request.context_id] = Context(user_id=request.context_id)
            context = contexts[request.context_id]

        # Update backend config
        backend.config["dry_run"] = request.dry_run

        # Execute through backend
        result = await backend.execute(request.query, context, request.options)

        # Return response
        return ExecuteResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            suggestions=result.suggestions,
            execution_time=result.execution_time,
            metadata=result.metadata,
        )

    except Exception as e:
        logger.error(f"Execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate-config")
async def generate_config(request: GenerateConfigRequest):
    """
    Generate NixOS configuration from natural language

    This endpoint specifically handles configuration generation,
    one of our killer features.
    """
    if not backend:
        raise HTTPException(status_code=503, detail="Backend not initialized")

    try:
        # Execute config generation
        result = await backend.execute(f"generate config: {request.description}")

        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)

        # Format output based on request
        if request.format == "json":
            # Parse Nix to JSON (simplified)
            config_lines = result.output.split("\n")
            config_json = {
                "description": request.description,
                "nix_config": result.output,
                "services": [],
                "packages": [],
            }

            # Extract services and packages
            for line in config_lines:
                if "services." in line:
                    config_json["services"].append(line.strip())
                elif "pkgs." in line:
                    config_json["packages"].append(line.strip())

            return config_json
        return {"config": result.output}

    except Exception as e:
        logger.error(f"Config generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/search")
async def search_packages(request: SearchRequest):
    """
    Search for packages by name or description

    Uses smart search to find packages by what they do,
    not just their exact names.
    """
    if not backend:
        raise HTTPException(status_code=503, detail="Backend not initialized")

    try:
        # Determine search type
        query = request.query
        if request.smart:
            query = f"search for {query}"
        else:
            query = f"search {query}"

        # Execute search
        result = await backend.execute(query)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)

        # Parse results
        packages = result.metadata.get("packages", [])

        # Limit results
        if request.limit:
            packages = packages[: request.limit]

        return {
            "query": request.query,
            "packages": packages,
            "count": len(packages),
            "smart_search": request.smart,
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/v1/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming operations

    This enables real-time progress updates for long-running
    operations like system updates.
    """
    await websocket.accept()

    try:
        while True:
            # Receive query from client
            data = await websocket.receive_text()
            message = json.loads(data)

            query = message.get("query", "")
            context_id = message.get("context_id")

            # Get or create context
            context = None
            if context_id:
                if context_id not in contexts:
                    contexts[context_id] = Context(user_id=context_id)
                context = contexts[context_id]

            # Stream execution
            async for update in backend.stream_execute(query, context):
                await websocket.send_json(update)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@app.get("/api/v1/contexts")
async def list_contexts():
    """List all active contexts/sessions"""
    return {"contexts": list(contexts.keys()), "count": len(contexts)}


@app.delete("/api/v1/contexts/{context_id}")
async def delete_context(context_id: str):
    """Delete a specific context/session"""
    if context_id in contexts:
        del contexts[context_id]
        return {"message": f"Context {context_id} deleted"}
    raise HTTPException(status_code=404, detail="Context not found")


@app.get("/api/v1/plugins")
async def list_plugins():
    """List all loaded plugins"""
    if not backend:
        raise HTTPException(status_code=503, detail="Backend not initialized")

    return {
        "plugins": backend.plugins.list_plugins(),
        "count": len(backend.plugins.plugins),
    }


# API Documentation extras
@app.get("/api/v1")
async def api_info():
    """API version and capabilities information"""
    return {
        "version": "1.0.0",
        "name": "Nix for Humanity API",
        "description": "Natural language interface to NixOS",
        "capabilities": [
            "natural_language_execution",
            "config_generation",
            "smart_search",
            "streaming_operations",
            "plugin_system",
            "context_management",
        ],
        "endpoints": {
            "execute": "/api/v1/execute",
            "generate_config": "/api/v1/generate-config",
            "search": "/api/v1/search",
            "stream": "/api/v1/stream (WebSocket)",
            "health": "/api/v1/health",
            "docs": "/api/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
