"""
Storage Manager for E/N/M Tiered Retention (Charter v2.0)

Implements Charter v2.0 materiality-based retention:
- M0 (Ephemeral): Never store, discard immediately
- M1 (Temporal): Store until state change, prune after 30 days
- M2 (Persistent): Keep for audit, prune after 365 days
- M3 (Foundational): Preserve forever, never prune
"""

from typing import List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

from luminous_nix.mycelix.trust import Interaction
from .types import MTier

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Manages tiered storage based on M-axis (Materiality)

    Retention Policy (default):
    - M0: Discard immediately (0 days)
    - M1: Temporal (30 days)
    - M2: Persistent (365 days)
    - M3: Foundational (never prune)
    """

    # Default retention periods (days)
    DEFAULT_RETENTION = {
        MTier.M0: 0,    # Discard immediately
        MTier.M1: 30,   # Temporal: ~1 month
        MTier.M2: 365,  # Persistent: ~1 year
        MTier.M3: None  # Foundational: forever
    }

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        retention_days: Optional[dict] = None
    ):
        """
        Initialize StorageManager

        Args:
            storage_path: Path to interaction logs
            retention_days: Custom retention periods by M-tier
                           (e.g., {MTier.M1: 60, MTier.M2: 730})
        """
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "interactions"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Merge custom retention with defaults
        self.retention_days = self.DEFAULT_RETENTION.copy()
        if retention_days:
            self.retention_days.update(retention_days)

    def should_store(self, interaction: Interaction) -> bool:
        """
        Determine if interaction should be stored based on M-tier

        Args:
            interaction: The interaction to evaluate

        Returns:
            True if should store, False if should discard (M0)
        """
        # M0: Never store
        if interaction.epistemic_m == 0:
            logger.debug(f"Discarding M0 interaction: {interaction.query}")
            return False

        return True

    def should_prune(
        self,
        interaction: Interaction,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Determine if interaction should be pruned based on age and M-tier

        Args:
            interaction: The interaction to evaluate
            current_time: Current time (defaults to now)

        Returns:
            True if should prune, False if should keep
        """
        if current_time is None:
            current_time = datetime.now()

        # M3: Never prune
        if interaction.epistemic_m == 3:
            return False

        # M0: Already pruned (shouldn't have been stored)
        if interaction.epistemic_m == 0:
            return True

        # M1, M2: Prune if older than retention period
        m_tier = MTier(interaction.epistemic_m)
        retention_days = self.retention_days[m_tier]

        if retention_days is None:  # Never prune
            return False

        age = (current_time - interaction.timestamp).days
        return age > retention_days

    def prune_old_interactions(
        self,
        dry_run: bool = False
    ) -> dict:
        """
        Prune interactions based on M-tier retention policies

        Args:
            dry_run: If True, don't actually delete, just report what would be deleted

        Returns:
            Dictionary with pruning statistics
        """
        stats = {
            "scanned": 0,
            "pruned": 0,
            "kept": 0,
            "by_tier": {
                "M0": 0,
                "M1": 0,
                "M2": 0,
                "M3": 0
            }
        }

        # Read all log files
        log_files = sorted(self.storage_path.glob("interactions_*.jsonl"))

        for log_file in log_files:
            try:
                # Read interactions from this file
                interactions = []
                interactions_to_keep = []

                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)
                            interaction = Interaction.from_dict(data)
                            interactions.append(interaction)
                            stats["scanned"] += 1

                            # Decide whether to keep
                            if self.should_prune(interaction):
                                stats["pruned"] += 1
                                m_tier = f"M{interaction.epistemic_m}"
                                stats["by_tier"][m_tier] = stats["by_tier"].get(m_tier, 0) + 1
                                logger.debug(f"Pruning {m_tier} interaction: {interaction.query}")
                            else:
                                interactions_to_keep.append(interaction)
                                stats["kept"] += 1

                        except Exception as e:
                            logger.warning(f"Failed to parse interaction: {e}")
                            continue

                # Rewrite file without pruned interactions (unless dry run)
                if not dry_run and interactions_to_keep != interactions:
                    with open(log_file, 'w') as f:
                        for interaction in interactions_to_keep:
                            f.write(json.dumps(interaction.to_dict()) + '\n')

                    logger.info(
                        f"Pruned {len(interactions) - len(interactions_to_keep)} "
                        f"interactions from {log_file.name}"
                    )

                # Delete file if empty after pruning
                if not dry_run and len(interactions_to_keep) == 0:
                    log_file.unlink()
                    logger.info(f"Deleted empty log file: {log_file.name}")

            except Exception as e:
                logger.error(f"Failed to process log file {log_file}: {e}")
                continue

        return stats

    def get_storage_stats(self) -> dict:
        """
        Get storage statistics by M-tier

        Returns:
            Dictionary with counts per M-tier
        """
        stats = {
            "total": 0,
            "by_tier": {
                "M0": 0,
                "M1": 0,
                "M2": 0,
                "M3": 0,
                "unclassified": 0
            }
        }

        log_files = sorted(self.storage_path.glob("interactions_*.jsonl"))

        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)
                            stats["total"] += 1

                            # Count by M-tier
                            m_value = data.get('epistemic_m')
                            if m_value is not None:
                                m_tier = f"M{m_value}"
                                stats["by_tier"][m_tier] += 1
                            else:
                                stats["by_tier"]["unclassified"] += 1

                        except Exception as e:
                            logger.warning(f"Failed to parse interaction: {e}")
                            continue

            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {e}")
                continue

        return stats

    def archive_by_tier(
        self,
        tier: MTier,
        archive_path: Optional[Path] = None
    ) -> int:
        """
        Archive all interactions of a specific M-tier to separate storage

        Args:
            tier: The M-tier to archive (e.g., MTier.M2)
            archive_path: Destination path (defaults to .luminous-nix/archive/)

        Returns:
            Number of interactions archived
        """
        if archive_path is None:
            archive_path = Path.home() / ".luminous-nix" / "archive"

        archive_path.mkdir(parents=True, exist_ok=True)

        # Create archive file
        archive_file = archive_path / f"archived_{tier.name}_{datetime.now().strftime('%Y%m%d')}.jsonl"

        archived_count = 0
        log_files = sorted(self.storage_path.glob("interactions_*.jsonl"))

        for log_file in log_files:
            try:
                interactions_to_keep = []

                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)
                            interaction = Interaction.from_dict(data)

                            # Archive if matches tier
                            if interaction.epistemic_m == tier.value:
                                # Write to archive
                                with open(archive_file, 'a') as af:
                                    af.write(json.dumps(interaction.to_dict()) + '\n')
                                archived_count += 1
                            else:
                                interactions_to_keep.append(interaction)

                        except Exception as e:
                            logger.warning(f"Failed to parse interaction: {e}")
                            continue

                # Rewrite original file without archived interactions
                with open(log_file, 'w') as f:
                    for interaction in interactions_to_keep:
                        f.write(json.dumps(interaction.to_dict()) + '\n')

            except Exception as e:
                logger.error(f"Failed to archive from {log_file}: {e}")
                continue

        logger.info(f"Archived {archived_count} {tier.name} interactions to {archive_file}")
        return archived_count
