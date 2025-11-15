"""
HRM v3: Enhanced with Dev Environment Specialist
Fixes the critical 0% accuracy on shell/dev queries
"""

from typing import Dict, List, Optional, Tuple
import logging
import time
from pathlib import Path
import json

# Make torch optional
try:
    import torch
    import torch.nn as nn
    import numpy as np

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    np = None

from .dev_environment_specialist import DevEnvironmentSpecialist

logger = logging.getLogger(__name__)


class HRMEnhancedV3:
    """HRM v3 with specialized handling for development environments"""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path
        self.model = None
        self.dev_specialist = DevEnvironmentSpecialist()
        self.confidence_threshold = 0.7

        # Track performance metrics
        self.metrics = {
            "total_queries": 0,
            "dev_queries": 0,
            "dev_success": 0,
            "neural_queries": 0,
            "neural_success": 0,
        }

        # Load neural model if available
        if model_path and model_path.exists():
            self._load_model()
        else:
            logger.info("No model found, using specialist-only mode")

    def process_query(self, query: str) -> Dict:
        """
        Process query with dev specialist first, then neural network
        """
        self.metrics["total_queries"] += 1
        start_time = time.time()

        # First, check if it's a development query
        dev_result = self.dev_specialist.handle_query(query)
        if dev_result and dev_result["confidence"] > self.confidence_threshold:
            self.metrics["dev_queries"] += 1
            self.metrics["dev_success"] += 1

            logger.info(f"Dev specialist handled: {query}")
            return {
                "success": True,
                "command": dev_result["command"],
                "description": dev_result["description"],
                "confidence": dev_result["confidence"],
                "source": "dev_specialist",
                "latency_ms": (time.time() - start_time) * 1000,
            }

        # Fall back to neural network if available
        if self.model:
            self.metrics["neural_queries"] += 1
            neural_result = self._neural_process(query)
            if neural_result["confidence"] > self.confidence_threshold:
                self.metrics["neural_success"] += 1
                return neural_result

        # If both fail, try to provide helpful guidance
        return self._fallback_response(query)

    def _neural_process(self, query: str) -> Dict:
        """Process with neural network (existing HRM logic)"""
        # This would integrate with existing HRM model
        # For now, returning placeholder
        return {
            "success": False,
            "confidence": 0.0,
            "source": "neural",
            "message": "Neural processing not yet implemented",
        }

    def _fallback_response(self, query: str) -> Dict:
        """Provide helpful fallback when unsure"""
        suggestions = []

        # Check for keywords to provide suggestions
        if "python" in query.lower():
            suggestions.append("Try: 'create python development environment'")
        elif "rust" in query.lower():
            suggestions.append("Try: 'setup rust development shell'")
        elif "node" in query.lower() or "npm" in query.lower():
            suggestions.append("Try: 'nodejs development environment'")

        if suggestions:
            return {
                "success": False,
                "suggestions": suggestions,
                "confidence": 0.3,
                "source": "fallback",
                "message": f"Not sure, but you might want: {', '.join(suggestions)}",
            }

        return {
            "success": False,
            "confidence": 0.0,
            "source": "fallback",
            "message": "I couldn't understand that query. Try being more specific about the development environment you need.",
        }

    def _load_model(self):
        """Load the neural model if available"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available, skipping model loading")
            return

        try:
            # Placeholder for actual model loading
            logger.info(f"Loading model from {self.model_path}")
            # self.model = torch.load(self.model_path)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def get_metrics(self) -> Dict:
        """Return performance metrics"""
        metrics = self.metrics.copy()

        # Calculate success rates
        if metrics["dev_queries"] > 0:
            metrics["dev_success_rate"] = (
                metrics["dev_success"] / metrics["dev_queries"]
            )
        else:
            metrics["dev_success_rate"] = 0.0

        if metrics["neural_queries"] > 0:
            metrics["neural_success_rate"] = (
                metrics["neural_success"] / metrics["neural_queries"]
            )
        else:
            metrics["neural_success_rate"] = 0.0

        if metrics["total_queries"] > 0:
            metrics["overall_success_rate"] = (
                metrics["dev_success"] + metrics["neural_success"]
            ) / metrics["total_queries"]
        else:
            metrics["overall_success_rate"] = 0.0

        return metrics

    def train_on_feedback(self, query: str, command: str, success: bool):
        """Update model based on user feedback"""
        # Store feedback for future training
        feedback_file = Path("data/user_feedback.jsonl")
        feedback_file.parent.mkdir(exist_ok=True)

        feedback = {
            "query": query,
            "command": command,
            "success": success,
            "timestamp": time.time(),
        }

        with open(feedback_file, "a") as f:
            f.write(json.dumps(feedback) + "\n")

        logger.info(f"Stored feedback: {query} -> {success}")
