"""Tests for InteractionLogger + EpistemicClassifier integration"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from luminous_nix.mycelix.trust import InteractionLogger, Interaction
from luminous_nix.mycelix.epistemic import ETier, NTier, MTier


class TestInteractionLoggerIntegration:
    """Test automatic E/N/M classification when logging interactions"""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def logger(self, temp_storage):
        """Create logger with temp storage"""
        return InteractionLogger(storage_path=temp_storage)

    def test_logger_has_classifier(self, logger):
        """Test that logger initializes with classifier"""
        assert logger.classifier is not None

    def test_log_search_interaction_classified(self, logger):
        """Test that search interaction gets classified"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox browser",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_found=5
        )

        # Log it (should automatically classify)
        logger.log_interaction(interaction)

        # Verify E/N/M fields were populated
        assert interaction.epistemic_e is not None
        assert interaction.epistemic_n is not None
        assert interaction.epistemic_m is not None

        # Verify correct classification (E4, N0, M3)
        assert interaction.epistemic_e == 1.0  # E4: Publicly verifiable
        assert interaction.epistemic_n == 0.0  # N0: Personal
        assert interaction.epistemic_m == 3    # M3: Foundational

    def test_log_install_interaction_classified(self, logger):
        """Test that install interaction gets classified"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="vim",
            success=True,
            duration_ms=5000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_installed=1
        )

        # Log it
        logger.log_interaction(interaction)

        # Verify classification (E2, N0, M2)
        assert interaction.epistemic_e == 0.5  # E2: System-verified
        assert interaction.epistemic_n == 0.0  # N0: Personal
        assert interaction.epistemic_m == 2    # M2: Persistent

    def test_log_failed_interaction_classified(self, logger):
        """Test that failed interaction gets classified"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="nonexistent-package",
            success=False,
            duration_ms=1000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        )

        # Log it
        logger.log_interaction(interaction)

        # Verify classification (E0, N0, M0)
        assert interaction.epistemic_e == 0.0  # E0: Unverifiable
        assert interaction.epistemic_n == 0.0  # N0: Personal
        assert interaction.epistemic_m == 0    # M0: Ephemeral

    def test_retrieve_classified_interactions(self, logger):
        """Test that retrieved interactions have E/N/M fields"""
        # Log multiple interactions
        interactions = [
            Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query="python",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test:alice",
                assurance_level="E0",
                packages_found=10
            ),
            Interaction(
                timestamp=datetime.now(),
                operation_type="install",
                query="python311",
                success=True,
                duration_ms=5000.0,
                user_did="did:mycelix:test:alice",
                assurance_level="E0",
                packages_installed=1
            ),
        ]

        for interaction in interactions:
            logger.log_interaction(interaction)

        # Retrieve them
        retrieved = logger.get_interactions(user_did="did:mycelix:test:alice")

        assert len(retrieved) == 2

        # First should be E4, N0, M3 (search)
        assert retrieved[0].epistemic_e == 1.0
        assert retrieved[0].epistemic_n == 0.0
        assert retrieved[0].epistemic_m == 3

        # Second should be E2, N0, M2 (install)
        assert retrieved[1].epistemic_e == 0.5
        assert retrieved[1].epistemic_n == 0.0
        assert retrieved[1].epistemic_m == 2

    def test_classification_failure_continues_logging(self, logger, monkeypatch):
        """Test that logging continues even if classification fails"""
        # Force classifier to raise exception
        def failing_classify(*args, **kwargs):
            raise RuntimeError("Test failure")

        monkeypatch.setattr(logger.classifier, 'classify', failing_classify)

        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="test",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0",
            packages_found=1
        )

        # Should not raise exception
        logger.log_interaction(interaction)

        # E/N/M fields should be None (classification failed)
        assert interaction.epistemic_e is None
        assert interaction.epistemic_n is None
        assert interaction.epistemic_m is None

        # But interaction should still be logged
        retrieved = logger.get_interactions()
        assert len(retrieved) == 1
