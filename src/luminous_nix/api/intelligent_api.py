"""
Luminous Nix Intelligent API
Clean, user-facing API that leverages all intelligent features
"""

import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import Any, Optional

from ..core.intelligent_system import LuminousNixIntelligence


@dataclass
class SearchResult:
    """Clean search result for API consumers"""

    name: str
    version: str
    description: str
    score: float = 1.0
    source: str = "cache"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class APIResponse:
    """Standard API response format"""

    success: bool
    data: Any
    message: str = ""
    metadata: Optional[dict] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)


class LuminousNixAPI:
    """
    User-friendly API for Luminous Nix Intelligence System

    Features:
    - Natural language search
    - Smart suggestions
    - Learning from usage
    - Performance insights
    - Async support
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize API with optional configuration"""
        self.config = config or {}
        self.intelligence = LuminousNixIntelligence(config)
        self.executor = ThreadPoolExecutor(max_workers=4)

    # ==================== Core Search API ====================

    def search(self, query: str, limit: int = 10) -> APIResponse:
        """
        Search for packages using natural language

        Args:
            query: Natural language search query
            limit: Maximum number of results

        Returns:
            APIResponse with search results
        """
        try:
            start_time = time.time()

            # Use full intelligence system
            response = self.intelligence.intelligent_search(
                query, use_all_features=True
            )

            # Format results
            results = []
            for item in response.results[:limit]:
                if isinstance(item, dict):
                    results.append(
                        SearchResult(
                            name=item.get("name", ""),
                            version=item.get("version", ""),
                            description=item.get("description", ""),
                            score=item.get("score", 1.0),
                            source=response.source,
                        ).to_dict()
                    )

            # Build metadata
            metadata = {
                "response_time_ms": (time.time() - start_time) * 1000,
                "intent": response.intent.category if response.intent else None,
                "suggested_packages": response.intent.suggested_packages
                if response.intent
                else [],
                "confidence": response.confidence,
                "source": response.source,
                "predictions": response.predictions[:3] if response.predictions else [],
                "updates_available": len(response.updates) if response.updates else 0,
            }

            return APIResponse(
                success=True,
                data=results,
                message=f"Found {len(results)} packages",
                metadata=metadata,
            )

        except Exception as e:
            return APIResponse(
                success=False, data=[], message=f"Search failed: {str(e)}"
            )

    async def search_async(self, query: str, limit: int = 10) -> APIResponse:
        """Async version of search"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.search, query, limit)

    # ==================== Smart Suggestions API ====================

    def suggest(self, partial_query: str) -> APIResponse:
        """
        Get smart suggestions for partial queries

        Args:
            partial_query: Partial search query

        Returns:
            APIResponse with suggestions
        """
        try:
            # Get semantic understanding
            intent = self.intelligence.semantic.understand(partial_query)

            # Get predictions based on history
            predictions = self.intelligence.predictor.predict_next(partial_query)

            # Combine suggestions
            suggestions = []

            # Add semantic suggestions
            if intent and intent.suggested_packages:
                for pkg in intent.suggested_packages[:5]:
                    suggestions.append(
                        {
                            "text": pkg,
                            "type": "semantic",
                            "confidence": intent.confidence,
                        }
                    )

            # Add predictive suggestions
            for query, prob in predictions[:5]:
                if query not in [s["text"] for s in suggestions]:
                    suggestions.append(
                        {"text": query, "type": "predictive", "confidence": prob}
                    )

            return APIResponse(
                success=True,
                data=suggestions,
                message=f"Generated {len(suggestions)} suggestions",
            )

        except Exception as e:
            return APIResponse(
                success=False, data=[], message=f"Suggestion failed: {str(e)}"
            )

    # ==================== Learning API ====================

    def learn(self, query: str, selected: str, satisfied: bool = True) -> APIResponse:
        """
        Learn from user selection to improve future results

        Args:
            query: Original search query
            selected: Package user selected
            satisfied: Whether user was satisfied

        Returns:
            APIResponse confirming learning
        """
        try:
            # Track the selection
            from ..analytics.usage_analytics_improved import UsageEvent

            event = UsageEvent(
                timestamp=time.time(),
                event_type="selection",
                query=query,
                selected_package=selected,
                user_satisfied=satisfied,
                result_count=1,
                response_time_ms=0,
                cache_hit=False,
                source="user_feedback",
            )
            self.intelligence.analytics.track_event(event)

            # Update semantic mappings
            if hasattr(self.intelligence.semantic, "learn_from_selection"):
                self.intelligence.semantic.learn_from_selection(query, selected)

            # Update ML model
            self.intelligence.predictor.learn_from_feedback(query, selected, satisfied)

            return APIResponse(
                success=True,
                data={"learned": True},
                message=f"Learned that '{selected}' is good for '{query}'",
            )

        except Exception as e:
            return APIResponse(
                success=False,
                data={"learned": False},
                message=f"Learning failed: {str(e)}",
            )

    # ==================== Install Helper API ====================

    def get_install_command(self, package: str, permanent: bool = False) -> APIResponse:
        """
        Get the appropriate install command for a package

        Args:
            package: Package name
            permanent: Whether to install permanently (configuration.nix)

        Returns:
            APIResponse with install command
        """
        try:
            if permanent:
                command = {
                    "method": "configuration.nix",
                    "steps": [
                        "1. Edit /etc/nixos/configuration.nix",
                        f"2. Add '{package}' to environment.systemPackages",
                        "3. Run: sudo nixos-rebuild switch",
                    ],
                    "command": f"environment.systemPackages = with pkgs; [ {package} ];",
                }
            else:
                command = {
                    "method": "temporary",
                    "steps": ["Run the following command:"],
                    "command": f"nix-env -iA nixpkgs.{package}",
                }

            return APIResponse(
                success=True, data=command, message=f"Install command for {package}"
            )

        except Exception as e:
            return APIResponse(
                success=False, data={}, message=f"Failed to generate command: {str(e)}"
            )

    # ==================== Analytics API ====================

    def get_insights(self) -> APIResponse:
        """
        Get usage insights and performance metrics

        Returns:
            APIResponse with insights
        """
        try:
            insights = self.intelligence.get_insights()

            # Format for API
            formatted_insights = {
                "session": {
                    "duration_seconds": insights["session"]["duration_seconds"],
                    "total_queries": insights["session"]["total_queries"],
                    "average_response_ms": insights["session"].get(
                        "avg_response_ms", 0
                    ),
                    "cache_hit_rate": insights["session"].get("cache_hit_rate", 0),
                },
                "performance": {
                    "queue_size": insights["session"]["queue_stats"]["queue_size"],
                    "writes_completed": insights["session"]["queue_stats"][
                        "writes_completed"
                    ],
                    "writes_failed": insights["session"]["queue_stats"][
                        "writes_failed"
                    ],
                },
                "recommendations": {
                    "hot_packages": insights["recommendations"]["packages_to_cache"][
                        :5
                    ],
                    "common_patterns": insights["recommendations"]["common_patterns"][
                        :5
                    ],
                },
            }

            return APIResponse(
                success=True, data=formatted_insights, message="Current system insights"
            )

        except Exception as e:
            return APIResponse(
                success=False, data={}, message=f"Failed to get insights: {str(e)}"
            )

    def get_popular_packages(self, limit: int = 10) -> APIResponse:
        """
        Get most popular packages based on usage

        Args:
            limit: Number of packages to return

        Returns:
            APIResponse with popular packages
        """
        try:
            recommendations = (
                self.intelligence.analytics.get_smart_cache_recommendations(limit)
            )

            popular = []
            for item in recommendations.get("packages_to_cache", [])[:limit]:
                popular.append(
                    {
                        "name": item["query"],
                        "frequency": item["frequency"],
                        "avg_response_ms": item["avg_response_ms"],
                    }
                )

            return APIResponse(
                success=True,
                data=popular,
                message=f"Top {len(popular)} popular packages",
            )

        except Exception as e:
            return APIResponse(
                success=False,
                data=[],
                message=f"Failed to get popular packages: {str(e)}",
            )

    # ==================== Update Monitoring API ====================

    def check_updates(self, packages: list[str]) -> APIResponse:
        """
        Check for available updates for specific packages

        Args:
            packages: List of package names to check

        Returns:
            APIResponse with update information
        """
        try:
            updates = []

            for package in packages:
                if self.intelligence.update_monitor.has_update(package):
                    update_info = self.intelligence.update_monitor.get_update_info(
                        package
                    )
                    if update_info:
                        updates.append(
                            {
                                "package": package,
                                "current_version": update_info.get(
                                    "current", "unknown"
                                ),
                                "new_version": update_info.get("new", "unknown"),
                                "channel": update_info.get("channel", "nixpkgs"),
                            }
                        )

            return APIResponse(
                success=True,
                data=updates,
                message=f"Found {len(updates)} updates available",
            )

        except Exception as e:
            return APIResponse(
                success=False, data=[], message=f"Update check failed: {str(e)}"
            )

    # ==================== Network API ====================

    def get_network_status(self) -> APIResponse:
        """
        Get collaborative network status

        Returns:
            APIResponse with network information
        """
        try:
            stats = self.intelligence.collaborative.get_stats()

            return APIResponse(
                success=True,
                data={
                    "status": stats["status"],
                    "peers": stats["peer_count"],
                    "port": stats["port"],
                    "queries_shared": stats["queries_shared"],
                    "queries_received": stats["queries_received"],
                },
                message="Network status retrieved",
            )

        except Exception as e:
            return APIResponse(
                success=False,
                data={},
                message=f"Failed to get network status: {str(e)}",
            )

    # ==================== Batch Operations API ====================

    def batch_search(self, queries: list[str]) -> APIResponse:
        """
        Search for multiple queries in batch

        Args:
            queries: List of search queries

        Returns:
            APIResponse with results for each query
        """
        try:
            results = {}
            total_time = 0

            for query in queries:
                start = time.time()
                response = self.search(query, limit=5)
                elapsed = (time.time() - start) * 1000
                total_time += elapsed

                results[query] = {
                    "results": response.data,
                    "response_time_ms": elapsed,
                    "success": response.success,
                }

            return APIResponse(
                success=True,
                data=results,
                message=f"Processed {len(queries)} queries",
                metadata={
                    "total_time_ms": total_time,
                    "avg_time_ms": total_time / len(queries) if queries else 0,
                },
            )

        except Exception as e:
            return APIResponse(
                success=False, data={}, message=f"Batch search failed: {str(e)}"
            )

    async def batch_search_async(self, queries: list[str]) -> APIResponse:
        """Async version of batch search"""
        tasks = [self.search_async(query, 5) for query in queries]
        results_list = await asyncio.gather(*tasks)

        results = {}
        for query, response in zip(queries, results_list):
            results[query] = {"results": response.data, "success": response.success}

        return APIResponse(
            success=True,
            data=results,
            message=f"Processed {len(queries)} queries asynchronously",
        )

    # ==================== Lifecycle Management ====================

    def shutdown(self):
        """Clean shutdown of API and underlying systems"""
        self.executor.shutdown(wait=True)
        self.intelligence.shutdown()

    def health_check(self) -> APIResponse:
        """
        Check health of all subsystems

        Returns:
            APIResponse with health status
        """
        try:
            health = {
                "api": "healthy",
                "intelligence": "healthy",
                "cache": "healthy",
                "analytics": "healthy",
                "network": "unknown",
                "updates": "healthy",
            }

            # Check network
            try:
                stats = self.intelligence.collaborative.get_stats()
                health["network"] = (
                    "healthy" if stats["status"] == "operational" else "degraded"
                )
            except:
                health["network"] = "offline"

            # Check analytics
            try:
                queue_stats = self.intelligence.analytics.write_queue.get_stats()
                if queue_stats["writes_failed"] > queue_stats["writes_completed"] * 0.1:
                    health["analytics"] = "degraded"
            except:
                health["analytics"] = "error"

            all_healthy = all(v == "healthy" for v in health.values())

            return APIResponse(
                success=True,
                data=health,
                message="System healthy" if all_healthy else "Some components degraded",
            )

        except Exception as e:
            return APIResponse(
                success=False, data={}, message=f"Health check failed: {str(e)}"
            )


# ==================== Convenience Functions ====================


def create_api(config: Optional[dict] = None) -> LuminousNixAPI:
    """Factory function to create API instance"""
    return LuminousNixAPI(config)


async def quick_search(query: str) -> list[dict]:
    """Quick async search helper"""
    api = create_api()
    try:
        response = await api.search_async(query)
        return response.data if response.success else []
    finally:
        api.shutdown()


def quick_search_sync(query: str) -> list[dict]:
    """Quick sync search helper"""
    api = create_api()
    try:
        response = api.search(query)
        return response.data if response.success else []
    finally:
        api.shutdown()
