"""
User Profile Management with Mycelix DID Integration

Combines:
- W3C DID (identity)
- MATL trust score (Week 3-4 complete!)
- Behavioral preferences (Layer 5.5)
- Usage statistics
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Complete user profile with identity and trust"""

    # Identity (Week 1-2)
    did: Optional[str] = None
    assurance_level: str = "E0"

    # Trust (Week 3-4 - placeholders for now)
    matl_score: float = 0.0  # 0.0-1.0
    trust_components: Dict[str, float] = field(default_factory=dict)

    # Behavioral preferences (existing Layer 5.5)
    persona_weights: Dict[str, float] = field(default_factory=dict)
    preferred_interaction_style: str = "balanced"  # calm, balanced, or power

    # Usage statistics
    total_operations: int = 0
    successful_operations: int = 0
    last_active: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Settings
    preferences: Dict[str, Any] = field(default_factory=dict)

    def get_success_rate(self) -> float:
        """Calculate success rate (0.0-1.0)"""
        if self.total_operations == 0:
            return 0.0
        return self.successful_operations / self.total_operations

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Deserialize from dictionary"""
        return cls(**data)


class UserProfileManager:
    """Manages user profile with DID integration"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".luminous-nix"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.profile_file = self.storage_path / "user_profile.json"

        # Will be initialized on first load
        self._did_manager = None

    def load_or_create(self, passphrase: Optional[str] = None) -> UserProfile:
        """Load existing profile or create new one"""
        # Initialize DID manager
        if self._did_manager is None:
            try:
                from luminous_nix.mycelix.identity import get_did_manager
                self._did_manager = get_did_manager()
            except ImportError:
                logger.warning("DID manager not available")
                self._did_manager = None

        # Load or create DID
        user_did = None
        if self._did_manager:
            try:
                user_did = self._did_manager.create_or_load(passphrase)
            except Exception as e:
                logger.warning(f"Could not load/create DID: {e}")

        # Load or create profile
        if self.profile_file.exists():
            profile = self._load_profile()
        else:
            profile = UserProfile()

        # Update profile with DID
        if user_did:
            profile.did = user_did.did
            profile.assurance_level = user_did.assurance_level

        profile.last_active = datetime.now().isoformat()

        # Save
        self._save_profile(profile)

        return profile

    def get_profile(self) -> Optional[UserProfile]:
        """Get current profile without creating new one"""
        if self.profile_file.exists():
            return self._load_profile()
        return None

    def update_operation_stats(self, success: bool = True):
        """Update operation statistics"""
        profile = self.load_or_create()
        profile.total_operations += 1
        if success:
            profile.successful_operations += 1
        profile.last_active = datetime.now().isoformat()
        self._save_profile(profile)

    def update_trust_score(self, matl_score: float, components: Dict[str, float]):
        """Update MATL trust score (Week 3-4)"""
        profile = self.load_or_create()
        profile.matl_score = matl_score
        profile.trust_components = components
        self._save_profile(profile)

    def calculate_and_update_trust_score(self, user_did: Optional[str] = None) -> Optional[float]:
        """
        Calculate MATL trust score from interaction history and update profile.

        Args:
            user_did: User DID to calculate for (optional, will use profile DID if not provided)

        Returns:
            float: Updated trust score, or None if calculation failed
        """
        try:
            # Import MATL components
            from luminous_nix.mycelix.trust import MATLEngine, InteractionLogger

            # Get profile (use existing if available to avoid overwriting test data)
            profile = self.get_profile()
            if profile is None:
                profile = self.load_or_create()

            # Use profile DID if not provided
            if user_did is None:
                user_did = profile.did

            if not user_did:
                logger.warning("No user DID available for trust score calculation")
                return None

            # Initialize MATL engine and interaction logger
            engine = MATLEngine()
            logger_storage = self.storage_path / "trust"
            interaction_logger = InteractionLogger(storage_path=logger_storage)

            # Get user interactions
            interactions = interaction_logger.get_interactions(user_did=user_did)

            if not interactions:
                logger.info("No interactions found for trust score calculation")
                return 0.0

            # Calculate MATL score
            matl_score = engine.calculate_trust_score(interactions, user_did=user_did)

            # Update profile
            profile.matl_score = matl_score.total_score
            profile.trust_components = {
                'pogq': matl_score.pogq_score,
                'tcdm': matl_score.tcdm_score,
                'entropy': matl_score.entropy_score
            }

            # Update assurance level based on trust score
            recommended_level = engine.calculate_assurance_level(matl_score)
            if recommended_level != profile.assurance_level:
                logger.info(f"Updating assurance level: {profile.assurance_level} -> {recommended_level}")
                profile.assurance_level = recommended_level

            # Save updated profile
            self._save_profile(profile)

            return matl_score.total_score

        except ImportError as e:
            logger.warning(f"MATL components not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to calculate trust score: {e}")
            return None

    def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences"""
        profile = self.load_or_create()
        profile.preferences.update(preferences)
        self._save_profile(profile)

    def _load_profile(self) -> UserProfile:
        """Load profile from disk"""
        try:
            with open(self.profile_file, 'r') as f:
                data = json.load(f)
            return UserProfile.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load profile: {e}")
            return UserProfile()

    def _save_profile(self, profile: UserProfile):
        """Save profile to disk"""
        try:
            with open(self.profile_file, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
            self.profile_file.chmod(0o600)
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")


# Singleton
_profile_manager: Optional[UserProfileManager] = None


def get_profile_manager() -> UserProfileManager:
    """Get singleton profile manager"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = UserProfileManager()
    return _profile_manager
