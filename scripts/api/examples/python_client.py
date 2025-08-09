#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Python Client Example for Nix for Humanity API
Simple client library for integrating with the REST API
"""

import requests
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlencode
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NixForHumanityClient:
    """Python client for Nix for Humanity API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        """
        Initialize the client
        
        Args:
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def query(self, 
              query: str, 
              personality: str = "friendly",
              execution_mode: str = "dry_run",
              collect_feedback: bool = True,
              capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Process a natural language query
        
        Args:
            query: Natural language query
            personality: Response personality (minimal, friendly, encouraging, technical, symbiotic)
            execution_mode: Execution mode (dry_run, safe, full, learning)
            collect_feedback: Whether to collect feedback
            capabilities: List of capabilities (text, visual, voice)
            
        Returns:
            API response dictionary
        """
        if capabilities is None:
            capabilities = ["text"]
        
        payload = {
            "query": query,
            "session_id": self.session_id,
            "context": {
                "personality": personality,
                "execution_mode": execution_mode,
                "collect_feedback": collect_feedback,
                "capabilities": capabilities
            }
        }
        
        response = self._request("POST", "/api/v1/query", json=payload)
        
        # Store session ID for future requests
        if "session_id" in response and not self.session_id:
            self.session_id = response["session_id"]
        
        return response
    
    def submit_feedback(self,
                       query: str,
                       response: str,
                       helpful: bool,
                       improved_response: Optional[str] = None,
                       rating: Optional[int] = None) -> Dict[str, Any]:
        """
        Submit feedback for an interaction
        
        Args:
            query: Original query
            response: System response
            helpful: Whether the response was helpful
            improved_response: Optional better response
            rating: Optional rating (1-5)
            
        Returns:
            API response dictionary
        """
        payload = {
            "session_id": self.session_id,
            "query": query,
            "response": response,
            "helpful": helpful
        }
        
        if improved_response:
            payload["improved_response"] = improved_response
        if rating is not None:
            payload["rating"] = rating
        
        return self._request("POST", "/api/v1/feedback", json=payload)
    
    def search_packages(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for NixOS packages
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        params = {
            "q": query,
            "limit": str(limit)
        }
        return self._request("GET", "/api/v1/search", params=params)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get API capabilities"""
        return self._request("GET", "/api/v1/capabilities")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return self._request("GET", "/api/v1/stats")
    
    def get_session(self) -> Dict[str, Any]:
        """Get current session information"""
        if not self.session_id:
            raise ValueError("No active session")
        return self._request("GET", f"/api/v1/session/{self.session_id}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._request("GET", "/api/v1/health")
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an API request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            Response data
            
        Raises:
            requests.RequestException: On request failure
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method, 
                url, 
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Example usage
def main():
    """Example usage of the client"""
    
    # Create client
    with NixForHumanityClient() as client:
        try:
            # Check health
            health = client.health_check()
            print(f"API Status: {health['status']}")
            print(f"Version: {health['version']}")
            
            # Get capabilities
            capabilities = client.get_capabilities()
            print(f"\nAvailable personalities: {capabilities['capabilities']['personalities']}")
            
            # Ask a question
            response = client.query(
                "How do I install Firefox?",
                personality="friendly",
                execution_mode="dry_run"
            )
            
            print(f"\nQuery: How do I install Firefox?")
            print(f"Response: {response['response']['text'][:200]}...")
            print(f"Commands: {response['response']['commands']}")
            print(f"Intent: {response['response']['intent']['action']}")
            
            # Submit feedback
            feedback_response = client.submit_feedback(
                query="How do I install Firefox?",
                response=response['response']['text'],
                helpful=True,
                rating=5
            )
            print(f"\nFeedback submitted: {feedback_response['status']}")
            
            # Search for packages
            search_results = client.search_packages("python", limit=5)
            print(f"\nSearch results for 'python': {search_results['count']} packages found")
            for pkg in search_results['packages']:
                print(f"  - {pkg['name']}: {pkg['description']}")
            
            # Get session info
            session_info = client.get_session()
            print(f"\nSession ID: {session_info['session']['id']}")
            print(f"Interactions: {session_info['session']['interactions']}")
            
            # Get stats
            stats = client.get_stats()
            print(f"\nEngine stats:")
            print(f"  Uptime: {stats['stats']['uptime']}")
            print(f"  Active sessions: {stats['stats']['api']['active_sessions']}")
            
        except Exception as e:
            print(f"Error: {e}")


# Async example using httpx (optional)
try:
    import httpx
    import asyncio
    
    class AsyncNixClient:
        """Async client using httpx"""
        
        def __init__(self, base_url: str = "http://localhost:5000"):
            self.base_url = base_url
            self.client = httpx.AsyncClient()
            self.session_id = None
        
        async def query(self, query: str, **options) -> Dict[str, Any]:
            """Async query method"""
            payload = {
                "query": query,
                "session_id": self.session_id,
                "context": options
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/query",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            if "session_id" in data and not self.session_id:
                self.session_id = data["session_id"]
            
            return data
        
        async def close(self):
            await self.client.aclose()
    
    
    async def async_example():
        """Async example"""
        client = AsyncNixClient()
        
        try:
            # Make multiple queries concurrently
            queries = [
                "How do I install Firefox?",
                "Update my system",
                "Search for python packages"
            ]
            
            tasks = [client.query(q) for q in queries]
            responses = await asyncio.gather(*tasks)
            
            for query, response in zip(queries, responses):
                print(f"\nQuery: {query}")
                print(f"Intent: {response['response']['intent']['action']}")
        
        finally:
            await client.close()
    
    
    ASYNC_AVAILABLE = True
    
except ImportError:
    ASYNC_AVAILABLE = False


if __name__ == "__main__":
    print("=== Nix for Humanity API Client Example ===")
    main()
    
    if ASYNC_AVAILABLE:
        print("\n=== Async Example ===")
        asyncio.run(async_example())