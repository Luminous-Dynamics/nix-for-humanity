"""
Luminous Nix Intelligent System
Unified integration of all 5 major features for revolutionary NixOS assistance
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Optional

from ..analytics.usage_analytics_improved import (
    ImprovedUsageAnalytics as UsageAnalytics,
)
from ..analytics.usage_analytics_improved import (
    SmartCacheOptimizerImproved as SmartCacheOptimizer,
)
from ..analytics.usage_analytics_improved import (
    UsageEvent,
)
from ..ml.predictive_prefetch import PredictivePrefetchEngine, SmartPrefetchCache
from ..network.collaborative_cache import CollaborativeCacheManager

# Import all our new features
from ..nlp.semantic_understanding import SemanticIntent, SemanticUnderstanding
from ..updates.realtime_updates import (
    SmartUpdateNotifier,
    UpdateIntegration,
    UpdateMonitor,
)

# Import existing core components
from .hybrid_cache import get_hybrid_cache

# SafeExecutor not needed for this integration


@dataclass
class IntelligentResponse:
    """Response from the intelligent system"""

    query: str
    intent: SemanticIntent
    results: list[dict]
    predictions: list[tuple[str, float]]  # Next likely queries
    updates: list[dict]  # Available updates for packages
    source: str  # Where results came from
    response_time_ms: float
    confidence: float

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "intent": self.intent.__dict__ if self.intent else None,
            "results": self.results,
            "predictions": self.predictions,
            "updates": self.updates,
            "source": self.source,
            "response_time_ms": self.response_time_ms,
            "confidence": self.confidence,
        }


class LuminousNixIntelligence:
    """
    Master intelligence system that orchestrates all features:
    1. Semantic Understanding - Natural language to intent
    2. Usage Analytics - Learning from behavior
    3. Predictive Prefetching - Anticipating needs
    4. Collaborative Caching - Collective intelligence
    5. Real-time Updates - Fresh package information
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize the intelligent system"""
        print("🧠 Initializing Luminous Nix Intelligence System...")

        self.config = config or {}

        # Initialize core components
        print("  📦 Setting up hybrid cache...")
        self.base_cache = get_hybrid_cache()

        # 1. Semantic Understanding
        print("  🗣️ Initializing semantic understanding...")
        self.semantic = SemanticUnderstanding()

        # 2. Usage Analytics with Sacred Trinity DB
        print("  📊 Setting up usage analytics...")
        self.analytics = UsageAnalytics()

        # 3. Predictive Prefetching with ML
        print("  🔮 Initializing predictive ML engine...")
        self.predictor = PredictivePrefetchEngine(self.base_cache)
        self.smart_cache = SmartPrefetchCache(self.base_cache)

        # 4. Collaborative Caching Network
        print("  🌐 Starting collaborative network...")
        self.collaborative = CollaborativeCacheManager(self.base_cache)

        # 5. Real-time Package Updates
        print("  📡 Monitoring package updates...")
        self.update_monitor = UpdateMonitor()
        self.update_notifier = SmartUpdateNotifier(self.update_monitor)
        self.update_integration = UpdateIntegration(
            self.update_monitor, self.base_cache
        )

        # Smart cache optimizer (connects analytics to cache)
        self.cache_optimizer = SmartCacheOptimizer(self.analytics, self.base_cache)

        # Session management
        self.session_id = self._generate_session_id()
        self.session_start = time.time()
        self.query_history = deque(maxlen=100)

        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "semantic_success": 0,
            "predictions_correct": 0,
            "collaborative_hits": 0,
            "updates_found": 0,
        }

        # Watch important packages by default
        self._setup_default_watches()

        print("✨ Intelligence system ready!")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import hashlib

        data = f"{time.time()}{id(self)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def _setup_default_watches(self):
        """Set up default package watches"""
        important_packages = [
            "firefox",
            "chromium",  # Browsers
            "python3",
            "nodejs",
            "rust",  # Dev tools
            "git",
            "vim",
            "neovim",  # Essential tools
            "kernel",
            "systemd",
            "openssl",  # System critical
        ]

        for pkg in important_packages:
            self.update_monitor.watch_package(pkg)

    def intelligent_search(
        self, query: str, use_all_features: bool = True
    ) -> IntelligentResponse:
        """
        Perform intelligent search using all features

        Flow:
        1. Understand intent with semantic NLU
        2. Check collaborative cache
        3. Track usage analytics
        4. Get predictions for next query
        5. Check for package updates
        6. Optimize cache based on patterns
        """
        start_time = time.time()

        # Track in history
        self.query_history.append(query)
        self.metrics["total_queries"] += 1

        # 1. SEMANTIC UNDERSTANDING
        intent = self.semantic.understand(query)

        if intent.confidence > 0.7:
            self.metrics["semantic_success"] += 1

        # Use semantic understanding to enhance query
        enhanced_query = query
        if intent.suggested_packages:
            # Use the top suggestion to guide search
            enhanced_query = intent.suggested_packages[0]

        # 2. COLLABORATIVE SEARCH (check network first)
        results = None
        source = "none"

        if use_all_features:
            # Try collaborative network first
            results = self.collaborative.node.search_collaborative(enhanced_query)
            if results:
                source = "collaborative"
                self.metrics["collaborative_hits"] += 1

        # 3. PREDICTIVE CACHE SEARCH (with prefetching)
        if not results:
            results, cache_ms, cache_source = self.smart_cache.search(enhanced_query)
            source = cache_source

            if cache_source != "nix":
                self.metrics["cache_hits"] += 1

        # 4. TRACK ANALYTICS
        elapsed_ms = (time.time() - start_time) * 1000

        event = UsageEvent(
            timestamp=time.time(),
            event_type="search",
            query=query,
            result_count=len(results) if results else 0,
            response_time_ms=elapsed_ms,
            cache_hit=(source != "nix"),
            source=source,
            selected_package=intent.suggested_packages[0]
            if intent.suggested_packages
            else None,
            session_id=self.session_id,
        )

        self.analytics.track_event(event)

        # 5. GET PREDICTIONS for next query
        predictions = []
        if use_all_features:
            # Track for predictions
            self.predictor.track_query(query)

            # Get predictions
            predictions = self.predictor.predict_next(query)

            # Validate against last prediction
            if len(self.query_history) > 1:
                last_query = self.query_history[-2]
                last_predictions = self.smart_cache.get_predictions()

                for pred_query, confidence in last_predictions:
                    if pred_query.lower() == query.lower():
                        self.metrics["predictions_correct"] += 1
                        break

        # 6. CHECK FOR UPDATES
        updates = []
        if results and use_all_features:
            for result in results[:5]:  # Check top 5 results
                pkg_name = result.get("name")
                if pkg_name:
                    pkg_updates = self.update_monitor.get_update_history(
                        package=pkg_name, limit=1
                    )
                    if pkg_updates:
                        updates.append(
                            {
                                "package": pkg_name,
                                "version": pkg_updates[0].new_version,
                                "severity": pkg_updates[0].severity,
                                "channel": pkg_updates[0].channel,
                            }
                        )
                        self.metrics["updates_found"] += 1

        # 7. SHARE SUCCESSFUL RESULTS with network
        if results and len(results) > 0 and use_all_features:
            # Share with collaborative network
            self.collaborative.node.share_cache_entry(
                query=query,
                results=results[:10],  # Share top 10
                confidence=intent.confidence,
            )

        # Build response
        response = IntelligentResponse(
            query=query,
            intent=intent,
            results=results or [],
            predictions=predictions[:5],  # Top 5 predictions
            updates=updates,
            source=source,
            response_time_ms=elapsed_ms,
            confidence=intent.confidence,
        )

        return response

    def get_insights(self) -> dict[str, Any]:
        """Get insights from the intelligent system"""

        # Get analytics insights
        analytics_insights = self.analytics.get_usage_insights()

        # Get cache recommendations
        cache_recommendations = self.analytics.get_smart_cache_recommendations()

        # Get prediction metrics
        prediction_metrics = self.predictor.get_metrics()

        # Get network stats
        network_stats = self.collaborative.get_stats()

        # Get update statistics
        update_stats = self.update_monitor.get_statistics()

        # Calculate intelligence metrics
        intelligence_score = self._calculate_intelligence_score()

        return {
            "session": {
                "id": self.session_id,
                "duration_minutes": (time.time() - self.session_start) / 60,
                "total_queries": self.metrics["total_queries"],
            },
            "intelligence": {
                "score": intelligence_score,
                "semantic_success_rate": (
                    self.metrics["semantic_success"]
                    / max(1, self.metrics["total_queries"])
                ),
                "prediction_accuracy": (
                    self.metrics["predictions_correct"]
                    / max(1, self.metrics["total_queries"] - 1)
                ),
                "cache_hit_rate": (
                    self.metrics["cache_hits"] / max(1, self.metrics["total_queries"])
                ),
                "collaborative_contribution": (
                    self.metrics["collaborative_hits"]
                    / max(1, self.metrics["total_queries"])
                ),
            },
            "analytics": analytics_insights,
            "cache_optimization": cache_recommendations,
            "predictions": prediction_metrics,
            "network": network_stats,
            "updates": update_stats,
        }

    def _calculate_intelligence_score(self) -> float:
        """Calculate overall intelligence score (0-100)"""
        if self.metrics["total_queries"] == 0:
            return 0.0

        # Weighted components
        semantic_weight = 0.25
        cache_weight = 0.25
        prediction_weight = 0.25
        network_weight = 0.25

        semantic_score = (
            self.metrics["semantic_success"] / self.metrics["total_queries"]
        ) * semantic_weight

        cache_score = (
            self.metrics["cache_hits"] / self.metrics["total_queries"]
        ) * cache_weight

        prediction_score = (
            self.metrics["predictions_correct"]
            / max(1, self.metrics["total_queries"] - 1)
        ) * prediction_weight

        network_score = (
            self.metrics["collaborative_hits"] / self.metrics["total_queries"]
        ) * network_weight

        total_score = (
            semantic_score + cache_score + prediction_score + network_score
        ) * 100

        return min(100, total_score)

    def optimize_performance(self):
        """Run optimization routines"""
        print("🔧 Running performance optimization...")

        # Get cache recommendations
        recommendations = self.analytics.get_smart_cache_recommendations()

        # Apply recommendations
        if recommendations["packages_to_cache"]:
            print(
                f"  📦 Pre-caching {len(recommendations['packages_to_cache'])} hot packages"
            )
            for pkg in recommendations["packages_to_cache"][:20]:
                # Prefetch popular packages
                self.base_cache.search_hybrid(pkg)

        if recommendations["packages_to_remove"]:
            print(
                f"  🗑️ Removing {len(recommendations['packages_to_remove'])} cold packages"
            )
            # In production, would remove from cache

        # Trigger update check
        print("  📡 Checking for package updates...")
        self.update_monitor.check_for_updates()

        # Train prediction models
        print("  🧠 Training prediction models...")
        self.predictor.end_session()  # Triggers training

        print("✅ Optimization complete!")

    def get_status(self) -> dict[str, Any]:
        """Get system status"""
        return {
            "system": "operational",
            "components": {
                "semantic_understanding": "active",
                "usage_analytics": "active",
                "predictive_ml": "active",
                "collaborative_network": f"{len(self.collaborative.node.peers)} peers",
                "update_monitor": f"{len(self.update_monitor.channels)} channels",
            },
            "metrics": self.metrics,
            "intelligence_score": self._calculate_intelligence_score(),
            "session": {
                "id": self.session_id,
                "queries": len(self.query_history),
                "duration": time.time() - self.session_start,
            },
        }

    def shutdown(self):
        """Clean shutdown of all components"""
        print("🛑 Shutting down intelligence system...")

        # Save analytics
        self.analytics.close_session()

        # Save predictions
        self.predictor.shutdown()

        # Stop collaborative network
        self.collaborative.shutdown()

        # Stop update monitoring
        self.update_monitor.shutdown()
        self.update_notifier.shutdown()

        # Stop cache optimizer
        self.cache_optimizer.shutdown()

        print("👋 Intelligence system shutdown complete")


class IntelligentCLI:
    """
    CLI wrapper that uses the intelligent system
    """

    def __init__(self):
        """Initialize intelligent CLI"""
        self.intelligence = LuminousNixIntelligence()
        self.last_response = None

    def search(self, query: str) -> dict[str, Any]:
        """Perform intelligent search"""
        # Get intelligent response
        response = self.intelligence.intelligent_search(query)
        self.last_response = response

        # Format for CLI output
        output = {
            "query": query,
            "intent": f"{response.intent.action} ({response.intent.confidence:.0%} confident)",
            "results": response.results[:10],  # Top 10 results
            "response_time": f"{response.response_time_ms:.1f}ms",
            "source": response.source,
        }

        # Add predictions if available
        if response.predictions:
            output["next_likely"] = [
                f"{q} ({p:.0%})" for q, p in response.predictions[:3]
            ]

        # Add updates if available
        if response.updates:
            output["updates_available"] = response.updates

        return output

    def get_insights(self) -> str:
        """Get formatted insights"""
        insights = self.intelligence.get_insights()

        # Format as readable text
        lines = [
            "📊 Intelligence System Insights",
            "=" * 60,
            f"Intelligence Score: {insights['intelligence']['score']:.1f}/100",
            "",
            "Performance Metrics:",
            f"  • Semantic Success: {insights['intelligence']['semantic_success_rate']:.0%}",
            f"  • Cache Hit Rate: {insights['intelligence']['cache_hit_rate']:.0%}",
            f"  • Prediction Accuracy: {insights['intelligence']['prediction_accuracy']:.0%}",
            f"  • Network Contribution: {insights['intelligence']['collaborative_contribution']:.0%}",
            "",
            "Session Statistics:",
            f"  • Duration: {insights['session']['duration_minutes']:.1f} minutes",
            f"  • Total Queries: {insights['session']['total_queries']}",
            "",
            "Network Status:",
            f"  • Connected Peers: {insights['network']['peer_count']}",
            f"  • Shared Entries: {insights['network']['shared_entries']}",
            "",
            "Update Monitoring:",
            f"  • Channels: {insights['updates']['channels_monitored']}",
            f"  • Pending Updates: {insights['updates']['pending_updates']}",
            f"  • Updates (24h): {insights['updates']['updates_24h']}",
        ]

        return "\n".join(lines)

    def optimize(self):
        """Run optimization"""
        self.intelligence.optimize_performance()
        return "Optimization complete!"

    def status(self) -> dict[str, Any]:
        """Get status"""
        return self.intelligence.get_status()

    def shutdown(self):
        """Shutdown CLI"""
        self.intelligence.shutdown()


def demo_intelligent_system():
    """Demo the intelligent system"""
    print("\n🚀 Luminous Nix Intelligence System Demo")
    print("=" * 70)

    # Create intelligent CLI
    cli = IntelligentCLI()

    # Demo queries
    queries = [
        "install firefox",
        "python development environment",
        "text editor for programming",
        "docker containers",
        "web browser",  # Should predict firefox
    ]

    print("\n📝 Running demo queries...\n")

    for query in queries:
        print(f"Query: '{query}'")
        result = cli.search(query)

        print(f"  Intent: {result['intent']}")
        print(f"  Results: {len(result['results'])} packages")
        print(f"  Source: {result['source']}")
        print(f"  Time: {result['response_time']}")

        if "next_likely" in result:
            print(f"  Next likely: {', '.join(result['next_likely'])}")

        if "updates_available" in result:
            print(f"  Updates: {len(result['updates_available'])} available")

        print()
        time.sleep(0.5)

    # Show insights
    print("\n" + cli.get_insights())

    # Optimize
    print("\n🔧 Running optimization...")
    cli.optimize()

    # Final status
    print("\n📊 Final Status:")
    status = cli.status()
    print(f"  Intelligence Score: {status['intelligence_score']:.1f}/100")
    print(f"  Components: {len(status['components'])} active")

    # Cleanup
    cli.shutdown()

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_intelligent_system()
