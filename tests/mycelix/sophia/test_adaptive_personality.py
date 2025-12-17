"""
Tests for Adaptive Personality Engine

Tests Sophia's ability to:
- Adapt communication style to individual preferences
- Learn from interaction outcomes
- Adjust emotional sensitivity
- Create personalized "Persona of One" relationships
- Build confidence in personality profiles over time
"""

import pytest
from datetime import datetime
from luminous_nix.mycelix.sophia.adaptive_personality import (
    AdaptivePersonalityEngine,
    get_adaptive_personality_engine,
    CommunicationStyle,
    EmotionalSensitivity,
    InteractionPace,
    FeedbackPreference,
    LearningStyle,
    PersonalityProfile,
    PersonalityTrait,
    InteractionPreference,
    AdaptiveResponse
)


@pytest.fixture
def engine():
    """Create a fresh adaptive personality engine"""
    return AdaptivePersonalityEngine(user_id="test_user")


@pytest.fixture
def direct_profile(engine):
    """Create profile for direct communication preference"""
    engine.profile.communication_style = CommunicationStyle.DIRECT
    engine.profile.emotional_sensitivity = EmotionalSensitivity.LOW
    return engine


@pytest.fixture
def friendly_profile(engine):
    """Create profile for friendly communication preference"""
    engine.profile.communication_style = CommunicationStyle.FRIENDLY
    engine.profile.emotional_sensitivity = EmotionalSensitivity.HIGH
    engine.profile.humor_appreciation = 0.8
    return engine


def test_engine_initialization(engine):
    """Test that adaptive personality engine initializes correctly"""
    assert engine is not None
    assert engine.user_id == "test_user"
    assert engine.profile is not None
    assert engine.profile.communication_style == CommunicationStyle.CONVERSATIONAL
    assert engine.profile.emotional_sensitivity == EmotionalSensitivity.MODERATE
    assert engine.profile.profile_confidence == 0.3  # Low confidence initially
    assert len(engine.interaction_history) == 0


def test_singleton_pattern():
    """Test that get_adaptive_personality_engine returns same instance per user"""
    engine1 = get_adaptive_personality_engine("user1")
    engine2 = get_adaptive_personality_engine("user1")
    engine3 = get_adaptive_personality_engine("user2")

    assert engine1 is engine2  # Same user = same instance
    assert engine1 is not engine3  # Different user = different instance


def test_adapt_message_direct(direct_profile):
    """Test message adaptation for direct communication style"""
    base_message = "I think that we should perhaps consider installing Firefox"

    response = direct_profile.adapt_message(base_message)

    assert isinstance(response, AdaptiveResponse)
    assert response.adapted_tone == "direct"
    assert len(response.message) < len(base_message)  # Should be more concise
    assert "I think that" not in response.message  # Filler words removed


def test_adapt_message_friendly(friendly_profile):
    """Test message adaptation for friendly communication style"""
    base_message = "You should install Firefox now"

    response = friendly_profile.adapt_message(base_message)

    assert isinstance(response, AdaptiveResponse)
    assert response.adapted_tone == "friendly"
    # Should use "we" language
    assert "we" in response.message.lower() or "together" in response.message.lower()


def test_adapt_message_with_emotional_state(friendly_profile):
    """Test message adaptation with emotional state awareness"""
    base_message = "The build failed"

    response = friendly_profile.adapt_message(
        base_message,
        emotional_state="frustrated"
    )

    assert isinstance(response, AdaptiveResponse)
    # Should acknowledge the emotional state
    assert "frustrat" in response.message.lower()


def test_learn_from_positive_interaction(engine):
    """Test learning from successful interaction"""
    our_message = "Let's try installing Firefox"
    their_response = "Great, that worked!"

    initial_confidence = engine.profile.profile_confidence

    engine.learn_from_interaction(
        interaction_type="suggestion",
        our_message=our_message,
        their_response=their_response,
        outcome_quality=0.9  # Very positive
    )

    # Should have recorded interaction
    assert len(engine.interaction_history) == 1
    assert engine.interaction_history[0]["quality"] == 0.9

    # Effective phrases should be tracked
    assert len(engine.profile.effective_phrases) > 0


def test_learn_from_negative_interaction(engine):
    """Test learning from unsuccessful interaction"""
    our_message = "Perhaps we might want to possibly consider"
    their_response = "I'm confused"

    engine.learn_from_interaction(
        interaction_type="suggestion",
        our_message=our_message,
        their_response=their_response,
        outcome_quality=0.2  # Poor outcome
    )

    # Should have recorded interaction
    assert len(engine.interaction_history) == 1
    assert engine.interaction_history[0]["quality"] == 0.2

    # Ineffective phrases should be tracked
    assert len(engine.profile.ineffective_phrases) > 0


def test_profile_confidence_grows_with_interactions(engine):
    """Test that profile confidence increases with more interactions"""
    initial_confidence = engine.profile.profile_confidence

    # Add 15 interactions
    for i in range(15):
        engine.learn_from_interaction(
            interaction_type="test",
            our_message=f"Test {i}",
            their_response="Ok",
            outcome_quality=0.7
        )

    # Confidence should have increased
    assert engine.profile.profile_confidence > initial_confidence


def test_adjust_communication_style(engine):
    """Test adjusting communication style based on learning"""
    old_style = engine.profile.communication_style

    engine.adjust_communication_style(
        CommunicationStyle.TECHNICAL,
        reason="User prefers precise terminology"
    )

    assert engine.profile.communication_style == CommunicationStyle.TECHNICAL
    assert engine.profile.communication_style != old_style


def test_personality_summary(engine):
    """Test generation of personality profile summary"""
    # Add some data to profile
    engine.profile.interests = {"Python", "NixOS", "AI"}
    engine.profile.effective_phrases = {
        "Let's try": 0.9,
        "How about": 0.8
    }

    summary = engine.get_personality_summary()

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert engine.user_id in summary
    assert "communication" in summary.lower()


def test_all_communication_styles():
    """Test that all communication styles are valid"""
    for style in CommunicationStyle:
        assert isinstance(style.value, str)
        assert len(style.value) > 0


def test_all_emotional_sensitivity_levels():
    """Test that all emotional sensitivity levels are valid"""
    for sensitivity in EmotionalSensitivity:
        assert isinstance(sensitivity.value, str)
        assert len(sensitivity.value) > 0


def test_all_interaction_paces():
    """Test that all interaction pace levels are valid"""
    for pace in InteractionPace:
        assert isinstance(pace.value, str)
        assert len(pace.value) > 0


def test_all_feedback_preferences():
    """Test that all feedback preferences are valid"""
    for pref in FeedbackPreference:
        assert isinstance(pref.value, str)
        assert len(pref.value) > 0


def test_all_learning_styles():
    """Test that all learning styles are valid"""
    for style in LearningStyle:
        assert isinstance(style.value, str)
        assert len(style.value) > 0


def test_personality_trait_dataclass():
    """Test PersonalityTrait dataclass"""
    trait = PersonalityTrait(
        trait_name="helpful",
        strength=0.8,
        description="Tendency to offer assistance",
        example_behaviors=["Suggests solutions", "Asks clarifying questions"],
        evidence=["User thanked for help"],
        confidence=0.7
    )

    assert trait.trait_name == "helpful"
    assert trait.strength == 0.8
    assert len(trait.example_behaviors) == 2
    assert trait.confidence == 0.7


def test_interaction_preference_dataclass():
    """Test InteractionPreference dataclass"""
    pref = InteractionPreference(
        preference_type="communication_style",
        preferred_value="direct",
        context="technical discussions",
        evidence=["Quick acceptance of direct suggestions"],
        success_rate=0.85,
        confidence=0.8,
        last_validated=datetime.now()
    )

    assert pref.preference_type == "communication_style"
    assert pref.preferred_value == "direct"
    assert pref.success_rate == 0.85


def test_personality_profile_dataclass():
    """Test PersonalityProfile dataclass"""
    now = datetime.now()

    profile = PersonalityProfile(
        user_id="test_user",
        created=now,
        last_updated=now,
        communication_style=CommunicationStyle.DIRECT,
        emotional_sensitivity=EmotionalSensitivity.LOW,
        interaction_pace=InteractionPace.RAPID,
        feedback_preference=FeedbackPreference.IMMEDIATE,
        learning_style=LearningStyle.INDEPENDENT,
        personality_traits=[],
        interaction_preferences=[],
        interests=set(),
        effective_phrases={},
        ineffective_phrases={},
        humor_appreciation=0.5,
        humor_style=None,
        profile_confidence=0.3
    )

    assert profile.user_id == "test_user"
    assert profile.communication_style == CommunicationStyle.DIRECT
    assert profile.profile_confidence == 0.3


def test_adaptive_response_dataclass():
    """Test AdaptiveResponse dataclass"""
    response = AdaptiveResponse(
        message="Let's install Firefox",
        adapted_tone="direct",
        adaptation_reasoning="User prefers brief responses",
        alternatives=["Perhaps we should install Firefox"],
        confidence=0.8
    )

    assert response.message == "Let's install Firefox"
    assert response.adapted_tone == "direct"
    assert response.confidence == 0.8
    assert len(response.alternatives) == 1


def test_make_direct_method(direct_profile):
    """Test _make_direct message transformation"""
    verbose = "I think that perhaps we should consider installing Firefox browser"
    direct = direct_profile._make_direct(verbose)

    assert len(direct) < len(verbose)
    assert "I think that" not in direct
    assert "perhaps" not in direct


def test_make_friendly_method(friendly_profile):
    """Test _make_friendly message transformation"""
    harsh = "You need to install Firefox now"
    friendly = friendly_profile._make_friendly(harsh)

    assert "You need to" not in friendly
    assert "we" in friendly.lower() or "let's" in friendly.lower()


def test_add_emotional_awareness(friendly_profile):
    """Test _add_emotional_awareness method"""
    message = "The installation failed"
    aware = friendly_profile._add_emotional_awareness(message, "frustrated")

    assert len(aware) > len(message)
    assert "frustrat" in aware.lower()


def test_remove_emotional_language(direct_profile):
    """Test _remove_emotional_language method"""
    emotional = "I sense that you feel confused about this"
    clinical = direct_profile._remove_emotional_language(emotional)

    assert "sense" not in clinical.lower()
    assert "feel" not in clinical.lower()


def test_multiple_users_separate_profiles():
    """Test that different users get different personality profiles"""
    user1_engine = get_adaptive_personality_engine("user1")
    user2_engine = get_adaptive_personality_engine("user2")

    # Modify user1's profile
    user1_engine.profile.communication_style = CommunicationStyle.DIRECT

    # User2 should still have default
    assert user2_engine.profile.communication_style == CommunicationStyle.CONVERSATIONAL
    assert user1_engine.profile.communication_style != user2_engine.profile.communication_style


def test_confidence_bounds(engine):
    """Test that confidence values stay within 0-1 bounds"""
    # Add many positive interactions
    for i in range(200):
        engine.learn_from_interaction(
            interaction_type="test",
            our_message=f"Test {i}",
            their_response="Good",
            outcome_quality=0.9
        )

    # Confidence should not exceed 1.0
    assert 0.0 <= engine.profile.profile_confidence <= 1.0

    # Effective phrases should not exceed 1.0
    for phrase, rate in engine.profile.effective_phrases.items():
        assert 0.0 <= rate <= 1.0


def test_adaptation_reasoning_provided(engine):
    """Test that adaptation includes reasoning"""
    response = engine.adapt_message("Test message")

    assert isinstance(response.adaptation_reasoning, str)
    assert len(response.adaptation_reasoning) > 0


def test_empty_message_handling(engine):
    """Test handling of empty message"""
    response = engine.adapt_message("")

    assert isinstance(response, AdaptiveResponse)
    assert isinstance(response.message, str)


def test_special_characters_handling(engine):
    """Test handling of special characters in messages"""
    special = "Test <>&\"' message with special chars"
    response = engine.adapt_message(special)

    assert isinstance(response, AdaptiveResponse)
    # Should preserve the message content
    assert "message" in response.message.lower()
