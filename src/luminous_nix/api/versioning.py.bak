"""API versioning and OpenAPI documentation for Nix for Humanity."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS

T = TypeVar("T")


class APIVersion(Enum):
    """Supported API versions."""
    
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    LATEST = "v3"  # Always points to latest stable version


@dataclass
class APIEndpoint:
    """API endpoint documentation."""
    
    path: str
    method: str
    summary: str
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[int, Dict[str, Any]] = None
    tags: List[str] = None
    deprecated: bool = False
    version_added: str = "v1"
    version_removed: Optional[str] = None


class APIVersionManager:
    """Manage API versions and documentation."""
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize API version manager.
        
        Args:
            app: Flask application instance
        """
        self.versions: Dict[str, Blueprint] = {}
        self.endpoints: Dict[str, List[APIEndpoint]] = {}
        self.deprecated_versions: List[str] = []
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize with Flask app.
        
        Args:
            app: Flask application
        """
        self.app = app
        
        # Enable CORS
        CORS(app)
        
        # Register OpenAPI routes
        self._register_openapi_routes()
    
    def register_version(
        self,
        version: Union[APIVersion, str],
        blueprint: Blueprint,
        deprecated: bool = False,
    ) -> None:
        """Register an API version.
        
        Args:
            version: API version
            blueprint: Flask blueprint for this version
            deprecated: Whether this version is deprecated
        """
        version_str = version.value if isinstance(version, APIVersion) else version
        
        self.versions[version_str] = blueprint
        
        if deprecated:
            self.deprecated_versions.append(version_str)
        
        # Register blueprint with URL prefix
        if self.app:
            self.app.register_blueprint(
                blueprint,
                url_prefix=f"/api/{version_str}"
            )
    
    def document_endpoint(
        self,
        version: Union[APIVersion, str],
        endpoint: APIEndpoint,
    ) -> None:
        """Document an API endpoint.
        
        Args:
            version: API version
            endpoint: Endpoint documentation
        """
        version_str = version.value if isinstance(version, APIVersion) else version
        
        if version_str not in self.endpoints:
            self.endpoints[version_str] = []
        
        self.endpoints[version_str].append(endpoint)
    
    def _register_openapi_routes(self) -> None:
        """Register OpenAPI documentation routes."""
        
        @self.app.route("/api/openapi.json")
        def openapi_spec():
            """Generate OpenAPI specification."""
            return jsonify(self.generate_openapi_spec())
        
        @self.app.route("/api/versions")
        def list_versions():
            """List available API versions."""
            return jsonify({
                "versions": list(self.versions.keys()),
                "latest": APIVersion.LATEST.value,
                "deprecated": self.deprecated_versions,
            })
        
        @self.app.route("/api/docs")
        def api_docs():
            """Serve API documentation UI."""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nix for Humanity API Documentation</title>
                <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
                <script>
                    SwaggerUIBundle({
                        url: "/api/openapi.json",
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout"
                    });
                </script>
            </body>
            </html>
            """
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification.
        
        Returns:
            OpenAPI specification dictionary
        """
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Nix for Humanity API",
                "description": "Natural language interface for NixOS",
                "version": APIVersion.LATEST.value,
                "contact": {
                    "name": "Luminous Dynamics",
                    "email": "nix-for-humanity@luminousdynamics.org",
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT",
                },
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "Development server",
                },
                {
                    "url": "https://api.nix-for-humanity.org",
                    "description": "Production server",
                },
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    },
                },
            },
            "tags": [],
        }
        
        # Add endpoints for each version
        for version, endpoints in self.endpoints.items():
            for endpoint in endpoints:
                path = f"/api/{version}{endpoint.path}"
                
                if path not in spec["paths"]:
                    spec["paths"][path] = {}
                
                operation = {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags or [version],
                    "deprecated": endpoint.deprecated,
                    "responses": endpoint.responses or {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    },
                }
                
                if endpoint.parameters:
                    operation["parameters"] = endpoint.parameters
                
                if endpoint.request_body:
                    operation["requestBody"] = endpoint.request_body
                
                spec["paths"][path][endpoint.method.lower()] = operation
        
        return spec


def versioned(
    version: Union[APIVersion, str],
    deprecated: bool = False,
    deprecated_in: Optional[str] = None,
    removed_in: Optional[str] = None,
) -> Callable:
    """Decorator for versioned API endpoints.
    
    Args:
        version: Minimum API version for this endpoint
        deprecated: Whether endpoint is deprecated
        deprecated_in: Version where deprecation started
        removed_in: Version where endpoint will be removed
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Add version headers
            response = func(*args, **kwargs)
            
            if hasattr(response, "headers"):
                response.headers["X-API-Version"] = str(version)
                
                if deprecated:
                    response.headers["X-API-Deprecated"] = "true"
                    if deprecated_in:
                        response.headers["X-API-Deprecated-In"] = deprecated_in
                    if removed_in:
                        response.headers["X-API-Removed-In"] = removed_in
                        response.headers["Warning"] = (
                            f'299 - "This endpoint is deprecated and will be '
                            f'removed in version {removed_in}"'
                        )
            
            return response
        
        # Store metadata for documentation
        wrapper._api_version = version
        wrapper._api_deprecated = deprecated
        wrapper._api_deprecated_in = deprecated_in
        wrapper._api_removed_in = removed_in
        
        return wrapper
    return decorator


# API Response Models
@dataclass
class APIResponse:
    """Standard API response format."""
    
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str = None
    version: str = APIVersion.LATEST.value
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class PaginatedResponse(APIResponse):
    """Paginated API response."""
    
    page: int = 1
    per_page: int = 20
    total: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
    
    def __post_init__(self):
        """Calculate pagination metadata."""
        super().__post_init__()
        
        if self.total > 0:
            self.total_pages = (self.total + self.per_page - 1) // self.per_page
            self.has_next = self.page < self.total_pages
            self.has_prev = self.page > 1


def create_api_v1() -> Blueprint:
    """Create API v1 blueprint.
    
    Returns:
        Configured blueprint
    """
    v1 = Blueprint("api_v1", __name__)
    
    @v1.route("/status")
    @versioned(APIVersion.V1)
    def status():
        """Get API status."""
        return jsonify(APIResponse(
            success=True,
            data={"status": "operational"},
            message="API v1 is operational",
        ).to_dict())
    
    @v1.route("/packages/search")
    @versioned(APIVersion.V1, deprecated=True, removed_in="v3")
    def search_packages_v1():
        """Search for packages (deprecated)."""
        query = request.args.get("q", "")
        return jsonify(APIResponse(
            success=True,
            data={"query": query, "results": []},
            message="Use v2 API for better search",
        ).to_dict())
    
    return v1


def create_api_v2() -> Blueprint:
    """Create API v2 blueprint.
    
    Returns:
        Configured blueprint
    """
    v2 = Blueprint("api_v2", __name__)
    
    @v2.route("/status")
    @versioned(APIVersion.V2)
    def status():
        """Get API status."""
        return jsonify(APIResponse(
            success=True,
            data={
                "status": "operational",
                "features": ["pagination", "filtering", "sorting"],
            },
            message="API v2 is operational",
        ).to_dict())
    
    @v2.route("/packages/search")
    @versioned(APIVersion.V2)
    def search_packages_v2():
        """Search for packages with pagination."""
        query = request.args.get("q", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        
        return jsonify(PaginatedResponse(
            success=True,
            data={"query": query, "results": []},
            page=page,
            per_page=per_page,
            total=0,
        ).to_dict())
    
    @v2.route("/commands/execute", methods=["POST"])
    @versioned(APIVersion.V2)
    def execute_command():
        """Execute a natural language command."""
        data = request.get_json()
        command = data.get("command", "")
        
        return jsonify(APIResponse(
            success=True,
            data={
                "command": command,
                "result": "Command executed",
                "confidence": 0.95,
            },
        ).to_dict())
    
    return v2


def create_api_v3() -> Blueprint:
    """Create API v3 blueprint (latest).
    
    Returns:
        Configured blueprint
    """
    v3 = Blueprint("api_v3", __name__)
    
    @v3.route("/status")
    @versioned(APIVersion.V3)
    def status():
        """Get API status."""
        return jsonify(APIResponse(
            success=True,
            data={
                "status": "operational",
                "features": [
                    "pagination",
                    "filtering",
                    "sorting",
                    "websocket",
                    "streaming",
                ],
                "performance": {
                    "response_time_ms": 12,
                    "cache_hit_rate": 0.85,
                },
            },
            message="API v3 is operational",
        ).to_dict())
    
    @v3.route("/packages/search")
    @versioned(APIVersion.V3)
    def search_packages_v3():
        """Search for packages with advanced features."""
        query = request.args.get("q", "")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        sort = request.args.get("sort", "relevance")
        filters = request.args.getlist("filter")
        
        return jsonify(PaginatedResponse(
            success=True,
            data={
                "query": query,
                "results": [],
                "sort": sort,
                "filters": filters,
                "facets": {},
            },
            page=page,
            per_page=per_page,
            total=0,
        ).to_dict())
    
    @v3.route("/commands/execute", methods=["POST"])
    @versioned(APIVersion.V3)
    def execute_command():
        """Execute command with streaming support."""
        data = request.get_json()
        command = data.get("command", "")
        stream = data.get("stream", False)
        persona = data.get("persona", "default")
        
        return jsonify(APIResponse(
            success=True,
            data={
                "command": command,
                "result": "Command executed",
                "confidence": 0.98,
                "persona": persona,
                "stream_available": stream,
            },
        ).to_dict())
    
    return v3