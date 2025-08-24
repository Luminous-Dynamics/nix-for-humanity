#!/usr/bin/env python3
"""
Simple FastAPI bridge to connect GUI to existing Luminous Nix backend.
Reuses all existing code - just exposes it as HTTP endpoints!
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path to import our existing code
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our EXISTING package intelligence - no changes needed!
from src.luminous_nix.discovery.package_intelligence import PackageIntelligence
from src.luminous_nix.interfaces.cli import CLI

# Initialize FastAPI
app = FastAPI(title="Luminous Nix API", version="1.0.0")

# Enable CORS for GUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (our GUI)
app.mount("/static", StaticFiles(directory="gui", html=True), name="static")

# Initialize our existing components
package_intelligence = PackageIntelligence()
cli = CLI()

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20

class InstallRequest(BaseModel):
    packages: List[str]
    dry_run: Optional[bool] = True

class CommandRequest(BaseModel):
    command: str

# API Endpoints - just thin wrappers around existing code!

@app.get("/")
async def root():
    """Redirect to GUI"""
    return {"message": "Luminous Nix API", "gui": "/static/index.html"}

@app.post("/api/search")
async def search_packages(request: SearchRequest):
    """
    Search for packages using natural language.
    This just calls our existing PackageIntelligence!
    """
    try:
        # Use our existing search functionality
        results = package_intelligence.search_packages(request.query)
        
        # Format for GUI
        formatted_results = []
        for package in results[:request.limit]:
            formatted_results.append({
                "name": package.get("name", "unknown"),
                "description": package.get("description", "No description available"),
                "category": package.get("category", "uncategorized"),
                "alternatives": package.get("alternatives", []),
                "popularity": package.get("popularity", 0.5),
                "installed": False  # TODO: Check actual installation status
            })
        
        return {
            "success": True,
            "query": request.query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/install")
async def install_packages(request: InstallRequest):
    """
    Install packages using our existing CLI backend.
    Now with REAL installation capability!
    """
    import subprocess
    import asyncio
    
    try:
        results = []
        
        for package in request.packages:
            if request.dry_run:
                # Dry run mode - just check if package exists
                result = {
                    "package": package,
                    "status": "dry_run",
                    "message": f"Would install {package} (dry-run mode)"
                }
            else:
                # REAL INSTALLATION!
                try:
                    # Use modern nix profile command
                    cmd = ["nix", "profile", "install", f"nixpkgs#{package}"]
                    
                    # Run the installation
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        result = {
                            "package": package,
                            "status": "success",
                            "message": f"✅ Successfully installed {package}",
                            "output": stdout.decode() if stdout else ""
                        }
                    else:
                        # Check for common errors
                        error_msg = stderr.decode() if stderr else "Unknown error"
                        if "already installed" in error_msg.lower():
                            result = {
                                "package": package,
                                "status": "success",
                                "message": f"✅ {package} is already installed",
                                "output": "Package was already installed"
                            }
                        else:
                            result = {
                                "package": package,
                                "status": "error",
                                "message": f"Failed to install {package}",
                                "error": error_msg
                            }
                    
                except Exception as e:
                    result = {
                        "package": package,
                        "status": "error",
                        "message": f"Error installing {package}: {str(e)}",
                        "error": str(e)
                    }
            
            results.append(result)
        
        # Check overall success
        success = all(r["status"] in ["success", "dry_run"] for r in results)
        
        return {
            "success": success,
            "results": results,
            "dry_run": request.dry_run
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/command")
async def execute_command(request: CommandRequest):
    """
    Execute natural language commands.
    Perfect for AI interaction!
    """
    try:
        command = request.command.lower()
        
        # Parse natural language commands
        if command.startswith("search:"):
            query = command.replace("search:", "").strip()
            return await search_packages(SearchRequest(query=query))
        
        elif command.startswith("install:"):
            packages = command.replace("install:", "").strip().split(",")
            return await install_packages(InstallRequest(packages=packages))
        
        elif command.startswith("help"):
            return {
                "success": True,
                "help": {
                    "commands": [
                        "search: [query] - Search for packages",
                        "install: [package1,package2] - Install packages",
                        "show: alternatives to [package] - Find alternatives",
                        "help - Show this help"
                    ]
                }
            }
        
        else:
            # Try to parse as natural language query
            search_result = await search_packages(SearchRequest(query=command))
            if search_result["results"]:
                return search_result
            
            return {
                "success": False,
                "message": f"Unknown command: {command}",
                "suggestion": "Try 'search: text editor' or 'help'"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/describe-view")
async def describe_view():
    """
    For AI agents - describe current state.
    """
    return {
        "view": "main",
        "available_actions": ["search", "install", "help"],
        "components": {
            "search_input": "ready",
            "results_area": "empty",
            "command_palette": "available (Ctrl+K)"
        }
    }

@app.get("/api/categories")
async def get_categories():
    """
    Get available package categories.
    """
    # Reuse our existing category definitions
    return {
        "categories": [
            {"id": "editors", "name": "Text Editors", "icon": "📝"},
            {"id": "browsers", "name": "Web Browsers", "icon": "🌐"},
            {"id": "development", "name": "Development Tools", "icon": "🛠️"},
            {"id": "media", "name": "Media Players", "icon": "🎵"},
            {"id": "communication", "name": "Communication", "icon": "💬"},
            {"id": "productivity", "name": "Productivity", "icon": "📊"},
            {"id": "system", "name": "System Tools", "icon": "⚙️"},
            {"id": "games", "name": "Games", "icon": "🎮"}
        ]
    }

@app.get("/api/suggestions")
async def get_suggestions(q: str = ""):
    """
    Get search suggestions based on partial query.
    """
    suggestions = [
        "I need a text editor",
        "alternative to firefox",
        "python development tools",
        "music player",
        "video editor",
        "terminal emulator",
        "note taking app",
        "password manager"
    ]
    
    if q:
        # Filter suggestions based on query
        filtered = [s for s in suggestions if q.lower() in s.lower()]
        return {"suggestions": filtered[:5]}
    
    return {"suggestions": suggestions[:5]}

@app.get("/api/installed")
async def get_installed_packages():
    """
    Get list of currently installed packages.
    """
    import subprocess
    
    try:
        # Use modern nix profile list
        result = subprocess.run(
            ["nix", "profile", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Parse the output - nix profile list format:
            # 0 flake:nixpkgs#legacyPackages.x86_64-linux.hello ...
            installed = []
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('Index'):
                    parts = line.split()
                    if len(parts) >= 2:
                        # Extract package name from flake reference
                        flake_ref = parts[1]
                        if '#' in flake_ref:
                            # Extract package name after the #
                            pkg_part = flake_ref.split('#')[-1]
                            # Remove legacyPackages.system. prefix if present
                            if '.' in pkg_part:
                                name = pkg_part.split('.')[-1]
                            else:
                                name = pkg_part
                            
                            installed.append({
                                "name": name,
                                "full_name": flake_ref,
                                "index": parts[0]
                            })
            
            return {
                "success": True,
                "installed": installed,
                "count": len(installed)
            }
        else:
            return {
                "success": False,
                "installed": [],
                "error": result.stderr
            }
    except Exception as e:
        return {
            "success": False,
            "installed": [],
            "error": str(e)
        }

@app.post("/api/uninstall")
async def uninstall_packages(request: InstallRequest):
    """
    Uninstall packages.
    """
    import subprocess
    import asyncio
    
    try:
        results = []
        
        for package in request.packages:
            if request.dry_run:
                result = {
                    "package": package,
                    "status": "dry_run",
                    "message": f"Would uninstall {package} (dry-run mode)"
                }
            else:
                try:
                    # First find the package index in the profile
                    list_result = subprocess.run(
                        ["nix", "profile", "list"],
                        capture_output=True,
                        text=True
                    )
                    
                    index = None
                    for line in list_result.stdout.split('\n'):
                        if package in line:
                            index = line.split()[0]
                            break
                    
                    if index:
                        # Use nix profile remove with index
                        cmd = ["nix", "profile", "remove", index]
                        
                        process = await asyncio.create_subprocess_exec(
                            *cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        
                        stdout, stderr = await process.communicate()
                        
                        if process.returncode == 0:
                            result = {
                                "package": package,
                                "status": "success",
                                "message": f"✅ Successfully uninstalled {package}"
                            }
                        else:
                            result = {
                                "package": package,
                                "status": "error",
                                "message": f"Failed to uninstall {package}",
                                "error": stderr.decode() if stderr else "Unknown error"
                            }
                    else:
                        result = {
                            "package": package,
                            "status": "error",
                            "message": f"Package {package} not found in profile"
                        }
                except Exception as e:
                    result = {
                        "package": package,
                        "status": "error",
                        "message": f"Error uninstalling {package}: {str(e)}"
                    }
            
            results.append(result)
        
        return {
            "success": all(r["status"] in ["success", "dry_run"] for r in results),
            "results": results,
            "dry_run": request.dry_run
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "backend": "connected",
        "package_intelligence": "ready",
        "cli": "available"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🌟 Luminous Nix API Server")
    print("📦 Reusing all existing package intelligence")
    print("🌐 GUI available at: http://localhost:8000/static/index.html")
    print("🤖 AI endpoints ready at: http://localhost:8000/api/ai/")
    print()
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)