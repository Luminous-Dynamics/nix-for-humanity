"""
Interaction Logger for MATL Trust Scoring

Logs all user interactions for trust score calculation.
With Charter v2.0: Automatically classifies interactions along E/N/M axes.
"""

from typing import Optional, List
from pathlib import Path
from datetime import datetime
import json
import logging

from .matl_types import Interaction
from ..epistemic import get_classifier

logger = logging.getLogger(__name__)


class InteractionLogger:
    """
    Log user interactions for MATL scoring

    Features:
    - Automatic E/N/M classification (Charter v2.0)
    - Automatic credit allocation (Week 7-8)
    - JSONLines storage for efficient appending
    - Daily log rotation
    - Query filtering and pagination
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        enable_credits: bool = True,
        default_matl_score: float = 0.8
    ):
        """
        Initialize interaction logger

        Args:
            storage_path: Directory for interaction logs
            enable_credits: Enable automatic credit allocation (default: True)
            default_matl_score: Default MATL trust score for credit calculation (default: 0.8)
        """
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "interactions"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Charter v2.0: Epistemic classifier
        self.classifier = get_classifier()

        # Week 7-8: Credits system integration
        self.enable_credits = enable_credits
        self.default_matl_score = default_matl_score

        # Lazy-load credits system (optional dependency)
        self._calculator = None
        self._ledger = None

        if self.enable_credits:
            try:
                from ..credits import get_calculator, get_ledger
                self._calculator = get_calculator()
                self._ledger = get_ledger()
                logger.info("Credits system enabled for InteractionLogger")
            except ImportError:
                logger.warning("Credits system not available - credit allocation disabled")
                self.enable_credits = False

    def log_interaction(self, interaction: Interaction, matl_score: Optional[float] = None):
        """
        Log a single interaction with automatic E/N/M classification and credit allocation.

        The epistemic classifier will populate:
        - epistemic_e: Empirical verifiability (0.0-1.0)
        - epistemic_n: Normative authority (0.0-1.0)
        - epistemic_m: Materiality/permanence (0-3)

        If credits are enabled, will automatically:
        - Calculate credits based on E/N/M coordinates
        - Record credit transaction in ledger
        - Update user balance

        Args:
            interaction: The interaction to log
            matl_score: MATL trust score for credit calculation (defaults to configured default)
        """
        # Charter v2.0: Classify interaction along E/N/M axes
        try:
            epistemic_score = self.classifier.classify(interaction)

            # Populate E/N/M fields
            interaction.epistemic_e = epistemic_score.epistemic_e
            interaction.epistemic_n = epistemic_score.epistemic_n
            interaction.epistemic_m = epistemic_score.epistemic_m

            logger.debug(f"Classified interaction: {epistemic_score.get_coordinate()}")
        except Exception as e:
            logger.warning(f"Failed to classify interaction: {e}")
            # Continue logging even if classification fails

        # Week 7-8: Automatic credit allocation
        if self.enable_credits and self._calculator and self._ledger:
            try:
                # Use provided matl_score or default
                score = matl_score if matl_score is not None else self.default_matl_score

                # Calculate credits from interaction
                credits_earned = self._calculator.calculate_from_interaction(interaction, score)

                # Create transaction
                tx = self._calculator.create_transaction(interaction, credits_earned, score)

                # Record in ledger
                balance = self._ledger.earn_credits(interaction.user_did, credits_earned, tx)

                logger.info(
                    f"Allocated {credits_earned} credits to {interaction.user_did} "
                    f"(new balance: {balance.current_balance})"
                )
            except Exception as e:
                logger.error(f"Failed to allocate credits: {e}")
                # Continue even if credit allocation fails

        # Create log file for today
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.storage_path / f"interactions_{today}.jsonl"

        # Append interaction
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(interaction.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")

    def get_interactions(
        self,
        user_did: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Interaction]:
        """
        Get logged interactions with optional filtering.

        Args:
            user_did: Filter by user DID
            since: Only get interactions after this datetime
            limit: Maximum number of interactions to return

        Returns:
            List of Interaction objects
        """
        interactions = []

        # Read all log files
        log_files = sorted(self.storage_path.glob("interactions_*.jsonl"))

        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)
                            interaction = Interaction.from_dict(data)

                            # Apply filters
                            if user_did and interaction.user_did != user_did:
                                continue

                            if since and interaction.timestamp < since:
                                continue

                            interactions.append(interaction)

                            # Check limit
                            if limit and len(interactions) >= limit:
                                return interactions

                        except Exception as e:
                            logger.warning(f"Failed to parse interaction: {e}")
                            continue

            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {e}")
                continue

        return interactions

    def get_interaction_count(self, user_did: Optional[str] = None) -> int:
        """Get count of logged interactions"""
        interactions = self.get_interactions(user_did=user_did)
        return len(interactions)

    def clear_old_interactions(self, days_to_keep: int = 90):
        """
        Clear interactions older than specified days.

        Args:
            days_to_keep: Number of days of interactions to keep
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        log_files = self.storage_path.glob("interactions_*.jsonl")

        for log_file in log_files:
            # Extract date from filename (interactions_YYYY-MM-DD.jsonl)
            try:
                date_str = log_file.stem.replace("interactions_", "")
                if date_str < cutoff_str:
                    log_file.unlink()
                    logger.info(f"Deleted old interaction log: {log_file.name}")
            except Exception as e:
                logger.warning(f"Failed to process log file {log_file}: {e}")
