"""
Tests for Layer 5: User Profiling and Adaptive Engagement

Tests cover:
- User profile creation and persistence
- Archetype detection from onboarding responses
- Technical level assessment
- Adaptive engagement strategy selection
- Profile loading and saving
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from luminous_nix.ai.user_profiler import (
    UserProfiler, UserProfile, UserArchetype,
    TechnicalLevel, EngagementMode, UserGoal,
    OnboardingQuestion
)
from luminous_nix.ai.adaptive_engagement import (
    AdaptiveEngagementEngine, EngagementStrategy
)


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def profiler(temp_storage):
    """Create profiler with temp storage"""
    return UserProfiler(storage_dir=temp_storage)


@pytest.fixture
def engagement_engine():
    """Create adaptive engagement engine"""
    return AdaptiveEngagementEngine()


class TestUserProfiler:
    """Test user profiling functionality"""

    def test_get_onboarding_questions(self, profiler):
        """Test that onboarding questions are generated"""
        questions = profiler.get_onboarding_questions()

        assert len(questions) == 5, "Should have 5 onboarding questions"
        assert all(isinstance(q, OnboardingQuestion) for q in questions)
        assert all(len(q.options) == 4 for q in questions), "Each question should have 4 options"

    def test_learner_archetype_detection(self, profiler):
        """Test detection of Learner archetype"""
        # Responses indicating Learner archetype
        responses = {
            "goal": 0,  # "Learn deeply"
            "experience": 0,  # Beginner
            "learning_preference": 0,  # "Understand deeply before doing"
            "automation_preference": 0,  # "Show me everything"
            "discovery": 0  # "Yes! Show me alternatives"
        }

        profile = profiler.generate_initial_profile(responses)

        assert profile.archetype == UserArchetype.LEARNER
        assert profile.engagement_mode == EngagementMode.FULL_TEACHING
        assert profile.wants_learning == True
        assert profile.onboarding_complete == True
        assert profile.archetype_confidence == 0.7

    def test_pragmatist_archetype_detection(self, profiler):
        """Test detection of Pragmatist archetype"""
        responses = {
            "goal": 1,  # "Working system quickly"
            "experience": 1,  # Intermediate
            "learning_preference": 1,  # "Get working first"
            "automation_preference": 1,  # "Handle routine tasks automatically"
            "discovery": 2  # "No, I know what I want"
        }

        profile = profiler.generate_initial_profile(responses)

        assert profile.archetype == UserArchetype.PRAGMATIST
        assert profile.engagement_mode == EngagementMode.JUST_DO_IT
        assert profile.wants_learning == False
        assert profile.prefers_automation == True

    def test_explorer_archetype_detection(self, profiler):
        """Test detection of Explorer archetype"""
        responses = {
            "goal": 2,  # "Explore possibilities"
            "experience": 2,  # Advanced
            "learning_preference": 2,  # "See examples"
            "automation_preference": 2,  # "Ask before doing"
            "discovery": 0  # "Yes! Show me alternatives"
        }

        profile = profiler.generate_initial_profile(responses)

        assert profile.archetype == UserArchetype.EXPLORER
        assert profile.engagement_mode == EngagementMode.SHOWCASE_POSSIBILITIES
        assert profile.interested_in_alternatives == True

    def test_creator_archetype_detection(self, profiler):
        """Test detection of Creator archetype"""
        responses = {
            "goal": 3,  # "Build custom tools"
            "experience": 3,  # Expert
            "learning_preference": 3,  # "Build myself with guidance"
            "automation_preference": 3,  # "Full control"
            "discovery": 1  # "Sometimes"
        }

        profile = profiler.generate_initial_profile(responses)

        assert profile.archetype == UserArchetype.CREATOR
        assert profile.engagement_mode == EngagementMode.COLLABORATIVE_DEV
        assert profile.interested_in_customization == True

    def test_technical_level_assessment(self, profiler):
        """Test technical level detection"""
        # Test all levels
        for level_idx, expected_level in enumerate([
            TechnicalLevel.BEGINNER,
            TechnicalLevel.INTERMEDIATE,
            TechnicalLevel.ADVANCED,
            TechnicalLevel.EXPERT
        ]):
            responses = {
                "goal": 0,
                "experience": level_idx,
                "learning_preference": 0,
                "automation_preference": 0,
                "discovery": 0
            }

            profile = profiler.generate_initial_profile(responses)
            assert profile.technical_level == expected_level

    def test_goal_extraction(self, profiler):
        """Test that goals are extracted from responses"""
        responses = {
            "goal": 0,  # "Learn NixOS deeply"
            "experience": 0,
            "learning_preference": 0,
            "automation_preference": 0,
            "discovery": 0
        }

        profile = profiler.generate_initial_profile(responses)

        assert len(profile.primary_goals) == 1
        assert isinstance(profile.primary_goals[0], UserGoal)
        assert profile.primary_goals[0].description == "Learn NixOS deeply"
        assert profile.primary_goals[0].category == "learning"
        assert profile.primary_goals[0].priority == 5

    def test_profile_persistence(self, profiler):
        """Test saving and loading profiles"""
        # Create profile
        responses = {
            "goal": 1,
            "experience": 2,
            "learning_preference": 1,
            "automation_preference": 1,
            "discovery": 1
        }

        original_profile = profiler.generate_initial_profile(responses)

        # Load profile
        loaded_profile = profiler.load_profile("default_user")

        assert loaded_profile is not None
        assert loaded_profile.archetype == original_profile.archetype
        assert loaded_profile.technical_level == original_profile.technical_level
        assert loaded_profile.engagement_mode == original_profile.engagement_mode
        assert loaded_profile.wants_learning == original_profile.wants_learning
        assert loaded_profile.prefers_automation == original_profile.prefers_automation

    def test_profile_update_from_interaction(self, profiler):
        """Test that profiles are updated from interactions"""
        # Create initial profile
        responses = {
            "goal": 0,
            "experience": 0,
            "learning_preference": 0,
            "automation_preference": 0,
            "discovery": 0
        }

        profile = profiler.generate_initial_profile(responses)
        initial_sessions = profile.sessions_count
        initial_confidence = profile.archetype_confidence

        # Simulate interaction
        interaction_data = {"command": "install firefox", "success": True}
        updated_profile = profiler.update_from_interaction(profile, interaction_data)

        assert updated_profile.sessions_count == initial_sessions + 1
        assert updated_profile.archetype_confidence > initial_confidence


class TestAdaptiveEngagement:
    """Test adaptive engagement strategies"""

    def test_learner_strategy(self, engagement_engine):
        """Test strategy for Learner archetype"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.LEARNER,
            technical_level=TechnicalLevel.BEGINNER,
            engagement_mode=EngagementMode.FULL_TEACHING,
            wants_learning=True
        )

        strategy = engagement_engine.select_strategy(profile, "install firefox")

        assert strategy.verbosity == "detailed"
        assert strategy.include_explanation == True
        assert strategy.include_learning == True
        assert strategy.auto_execute == False
        assert strategy.teaching_depth == "deep"
        assert strategy.use_analogies == True
        assert strategy.tone == "encouraging"

    def test_pragmatist_strategy(self, engagement_engine):
        """Test strategy for Pragmatist archetype"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.PRAGMATIST,
            technical_level=TechnicalLevel.INTERMEDIATE,
            engagement_mode=EngagementMode.JUST_DO_IT,
            wants_learning=False,
            prefers_automation=True
        )

        strategy = engagement_engine.select_strategy(profile, "install firefox")

        assert strategy.verbosity == "minimal"
        assert strategy.include_explanation == False
        assert strategy.include_learning == False
        assert strategy.auto_execute == True  # Because prefers_automation=True
        assert strategy.teaching_depth == "surface"
        assert strategy.use_analogies == False
        assert strategy.tone == "professional"

    def test_explorer_strategy(self, engagement_engine):
        """Test strategy for Explorer archetype"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.EXPLORER,
            technical_level=TechnicalLevel.ADVANCED,
            engagement_mode=EngagementMode.SHOWCASE_POSSIBILITIES,
            wants_learning=True,
            interested_in_alternatives=True
        )

        strategy = engagement_engine.select_strategy(profile, "install firefox")

        assert strategy.verbosity == "moderate"
        assert strategy.include_alternatives == True
        assert strategy.include_learning == True
        assert strategy.auto_execute == False
        assert strategy.teaching_depth == "intermediate"
        assert strategy.tone == "friendly"

    def test_creator_strategy(self, engagement_engine):
        """Test strategy for Creator archetype"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.CREATOR,
            technical_level=TechnicalLevel.EXPERT,
            engagement_mode=EngagementMode.COLLABORATIVE_DEV,
            wants_learning=True,
            interested_in_customization=True
        )

        strategy = engagement_engine.select_strategy(profile, "install firefox")

        assert strategy.verbosity == "detailed"
        assert strategy.include_explanation == True
        assert strategy.include_alternatives == True
        assert strategy.auto_execute == False
        assert strategy.ask_for_confirmation == False
        assert strategy.teaching_depth == "deep"
        assert strategy.use_analogies == False  # Technical precision preferred
        assert strategy.show_examples == True
        assert strategy.tone == "technical"

    def test_response_formatting(self, engagement_engine):
        """Test response formatting based on strategy"""
        strategy = EngagementStrategy(
            verbosity="detailed",
            include_explanation=True,
            include_learning=True,
            include_alternatives=True,
            auto_execute=False,
            preview_before_action=True,
            ask_for_confirmation=True,
            teaching_depth="deep",
            use_analogies=True,
            show_examples=True,
            tone="friendly"
        )

        content = "Firefox has been installed."
        metadata = {
            "explanation": "Firefox is a web browser package.",
            "alternatives": ["Chromium", "Brave", "Vivaldi"],
            "learning_content": "NixOS packages are declaratively managed...",
            "examples": "environment.systemPackages = [ pkgs.firefox ];"
        }

        response = engagement_engine.format_response(content, strategy, metadata)

        assert "Firefox has been installed." in response
        assert "Why this works" in response
        assert "Other options" in response
        assert "Chromium" in response
        assert "Learn more" in response
        assert "Example" in response

    def test_should_teach_now_learner(self, engagement_engine):
        """Test teaching decision for Learner"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.LEARNER,
            technical_level=TechnicalLevel.BEGINNER,
            wants_learning=True
        )

        # Learners almost always want teaching
        assert engagement_engine.should_teach_now(profile, "declarative") == True

    def test_should_teach_now_pragmatist(self, engagement_engine):
        """Test teaching decision for Pragmatist"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.PRAGMATIST,
            technical_level=TechnicalLevel.INTERMEDIATE,
            wants_learning=False
        )

        # Pragmatists don't want unsolicited teaching
        assert engagement_engine.should_teach_now(profile, "declarative") == False

        # But do want teaching if they ask "why" or "how"
        context_asking = {"query": "why does this work?"}
        assert engagement_engine.should_teach_now(profile, "declarative", context_asking) == True

    def test_should_suggest_alternatives_explorer(self, engagement_engine):
        """Test alternative suggestions for Explorer"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.EXPLORER,
            technical_level=TechnicalLevel.ADVANCED,
            interested_in_alternatives=True
        )

        # Explorers love alternatives
        assert engagement_engine.should_suggest_alternatives(profile, "firefox") == True

    def test_should_suggest_alternatives_pragmatist(self, engagement_engine):
        """Test alternative suggestions for Pragmatist"""
        profile = UserProfile(
            user_id="test",
            archetype=UserArchetype.PRAGMATIST,
            technical_level=TechnicalLevel.INTERMEDIATE,
            interested_in_alternatives=False
        )

        # Pragmatists don't want unsolicited suggestions
        assert engagement_engine.should_suggest_alternatives(profile, "firefox") == False


class TestIntegration:
    """Test integration of profiling and engagement"""

    def test_end_to_end_flow(self, profiler, engagement_engine):
        """Test complete flow from onboarding to strategy selection"""
        # 1. User completes onboarding
        responses = {
            "goal": 0,  # Learner
            "experience": 0,  # Beginner
            "learning_preference": 0,
            "automation_preference": 0,
            "discovery": 0
        }

        profile = profiler.generate_initial_profile(responses)

        # 2. Profile is used to select strategy
        strategy = engagement_engine.select_strategy(
            profile,
            "How do I install Firefox?"
        )

        # 3. Verify strategy matches profile
        assert strategy.verbosity == "detailed"
        assert strategy.include_learning == True
        assert strategy.teaching_depth == "deep"

        # 4. Verify teaching decision
        should_teach = engagement_engine.should_teach_now(profile, "packages")
        assert should_teach == True

    def test_profile_evolution(self, profiler, engagement_engine):
        """Test that profile confidence evolves with use"""
        responses = {
            "goal": 2,  # Explorer
            "experience": 1,
            "learning_preference": 2,
            "automation_preference": 2,
            "discovery": 0
        }

        profile = profiler.generate_initial_profile(responses)
        initial_confidence = profile.archetype_confidence

        # Simulate multiple interactions
        for _ in range(10):
            profile = profiler.update_from_interaction(
                profile,
                {"command": "test", "success": True}
            )

        # Confidence should increase
        assert profile.archetype_confidence > initial_confidence
        assert profile.sessions_count == 11  # Initial + 10 interactions


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
