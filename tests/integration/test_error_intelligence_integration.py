"""
Integration tests for Enhanced Error Intelligence with TUI

Tests the complete flow from error occurrence to educational display,
including XAI explanations and persona adaptation.
"""

from unittest.mock import Mock, patch
from datetime import datetime

from luminous_nix.core.backend import NixBackend as EnhancedBackend
from src.nix_for_humanity.core.types import (
    Request, Response, PersonalityStyle, IntentType
)
from src.nix_for_humanity.error_intelligence import (
    ErrorCategory, ErrorSeverity, ResolutionOutcome
)
from src.nix_for_humanity.tui.persona_styles import PersonaType


class TestErrorIntelligenceIntegration(unittest.TestCase):
    """Test complete error intelligence integration"""
    
    @pytest.fixture
    def backend(self):
        """Create enhanced backend"""
        return EnhancedBackend({
            'learning_enabled': True,
            'personality': PersonalityStyle.FRIENDLY
        })
    
    def test_permission_error_educational_flow(self, backend):
        """Test permission error produces educational response"""
        # Create request that will trigger permission error
        request = Request(
            query="install firefox system-wide",
            context={
                'persona': PersonaType.GRANDMA_ROSE.value,
                'session_id': 'test-123'
            },
            dry_run=False,
            execute=True
        )
        
        # Mock executor to return permission error
        with patch.object(backend.executor, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                success=False,
                error="Permission denied: /nix/store/... requires root access",
                exit_code=1,
                output=""
            )
            
            # Process request
            response = backend.process(request)
            
            # Verify response has educational error
            self.assertFalse(response.success)
            self.assertTrue(hasattr(response, 'educational_error'))
            
            # Check educational error content
            edu_error = response.educational_error
            self.assertTrue(edu_error.headline)  # Has user-friendly headline
            self.assertTrue(edu_error.learning_point)  # Has learning content
            self.assertGreater(len(edu_error.solutions), 0)  # Has solutions
            
            # Verify persona adaptation (Grandma Rose gets simple language)
            self.assertNotIn('sudo', edu_error.explanation.lower())  # Avoids technical terms
            self.assertTrue(any('administrator' in s.lower() for s in edu_error.solutions))
    
    def test_package_not_found_with_typo_correction(self, backend):
        """Test package not found error with typo detection"""
        request = Request(
            query="install fierfix",  # Typo
            context={
                'persona': PersonaType.MAYA.value,  # ADHD - needs quick solutions
                'session_id': 'test-456'
            }
        )
        
        response = backend.process(request)
        
        # Should recognize typo and suggest correction
        self.assertFalse(response.success)
        self.assertTrue(hasattr(response, 'educational_error'))
        
        edu_error = response.educational_error
        self.assertIn('firefox', ' '.join(edu_error.solutions).lower())
        self.assertTrue(edu_error.confidence_message)  # Shows confidence, suggestion
        
        # Maya gets minimal, action-focused content
        self.assertLess(len(edu_error.explanation.split()), 50)  # Brief explanation
        self.assertTrue(edu_error.solutions[0].startswith('install firefox'))  # Direct action
    
    def test_preventive_suggestions_before_error(self, backend):
        """Test preventive suggestions are generated"""
        # Simulate low disk space context
        request = Request(
            query="install large-application",
            context={
                'disk_free_gb': 2,  # Low disk space
                'persona': PersonaType.DAVID.value
            }
        )
        
        with patch.object(backend.preventive_advisor, 'get_system_health_suggestions') as mock_health:
            mock_health.return_value = [
                Mock(
                    title="Low Disk Space",
                    reason="Only 2GB free, installation needs 5GB",
                    action="Run 'nix-collect-garbage -d' to free space",
                    urgency=0.8,
                    confidence=0.95
                )
            ]
            
            response = backend.process(request)
            
            # Should include preventive suggestions
            self.assertTrue(hasattr(response, 'preventive_suggestions'))
            self.assertGreater(len(response.preventive_suggestions), 0)
            
            suggestion = response.preventive_suggestions[0]
            self.assertGreater(suggestion.urgency, 0.7)  # High urgency
            self.assertIn('garbage', suggestion.action)  # Actionable advice
    
    def test_xai_error_explanation_integration(self, backend):
        """Test XAI explains why errors occurred"""
        request = Request(
            query="build custom-package",
            context={
                'persona': PersonaType.DR_SARAH.value  # Technical user
            },
            execute=True,
            dry_run=False
        )
        
        # Mock build failure
        with patch.object(backend.executor, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                success=False,
                error="error: attribute 'custom-package' missing",
                exit_code=1
            )
            
            response = backend.process(request)
            
            # Should have XAI explanation in analyzed error
            self.assertTrue(hasattr(response, 'analyzed_error'))
            self.assertTrue(response.analyzed_error.xai_explanation)
            
            # Dr. Sarah gets technical details
            edu_error = response.educational_error
            self.assertIn('attribute', edu_error.explanation)  # Technical terms preserved
            self.assertTrue(edu_error.diagram)  # May include visual diagram
            self.assertTrue(any('overlay' in s or 'override' in s for s in edu_error.solutions))
    
    def test_error_learning_and_improvement(self, backend):
        """Test system learns from error resolutions"""
        # First attempt fails
        request1 = Request(
            query="install python",
            context={'session_id': 'learn-test'}
        )
        
        with patch.object(backend.executor, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                success=False,
                error="ambiguous package name",
                exit_code=1
            )
            
            response1 = backend.process(request1)
            error_id = response1.analyzed_error.pattern.id if response1.analyzed_error.pattern else 'unknown'
        
        # User tries suggested solution
        request2 = Request(
            query="install python3",
            context={'session_id': 'learn-test'}
        )
        
        with patch.object(backend.executor, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                success=True,
                output="installing python3...",
                exit_code=0
            )
            
            # Record that this solution worked
            if backend.learning_enabled:
                backend.error_learner.record_resolution(
                    error_pattern_id=error_id,
                    solution=Mock(description="install python3"),
                    outcome=ResolutionOutcome.RESOLVED,
                    time_to_resolve=5.0,
                    context={'original_query': 'install python'}
                )
            
            response2 = backend.process(request2)
            self.assertTrue(response2.success)
        
        # Future similar error should prioritize learned solution
        request3 = Request(
            query="install python",
            context={'session_id': 'learn-test-2'}
        )
        
        with patch.object(backend.executor, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                success=False,
                error="ambiguous package name",
                exit_code=1
            )
            
            response3 = backend.process(request3)
            
            # Should suggest python3 as first solution based on learning
            if response3.educational_error.solutions:
                self.assertIn('python3', response3.educational_error.solutions[0])
    
    def test_error_context_preservation(self, backend):
        """Test error context is preserved for follow-up questions"""
        # First, trigger an error
        request1 = Request(
            query="install nonexistent-package",
            context={'session_id': 'context-test'}
        )
        
        response1 = backend.process(request1)
        self.assertFalse(response1.success)
        
        # Now ask about the error
        request2 = Request(
            query="why did that fail?",
            context={'session_id': 'context-test'}
        )
        
        response2 = backend.process(request2)
        
        # Should explain the previous error
        self.assertEqual(response2.intent.type, IntentType.EXPLAIN)
        self.assertIn('nonexistent-package', response2.message.lower() or 'last error' in response2.message.lower())
    
    def test_persona_adaptive_error_formatting(self, backend):
        """Test errors adapt to different personas"""
        error_msg = "error: cannot coerce a set to a string"
        
        personas_and_expectations = [
            (PersonaType.GRANDMA_ROSE, 'simple', lambda e: 'coerce' not in e.explanation),
            (PersonaType.LUNA, 'predictable', lambda e: len(e.solutions) <= 3),
            (PersonaType.ALEX, 'accessible', lambda e: e.explanation.count('.') > 2),  # Well-structured
            (PersonaType.VIKTOR, 'clear', lambda e: 'ESL' not in e.explanation)  # No meta-references
        ]
        
        for persona, style, check_fn in personas_and_expectations:
            request = Request(
                query="eval nixos config",
                context={'persona': persona.value}
            )
            
            # Mock execution error
            with patch.object(backend.executor, 'execute') as mock_execute:
                mock_execute.return_value = Mock(
                    success=False,
                    error=error_msg,
                    exit_code=1
                )
                
                response = backend.process(request)
                
                self.assertTrue(hasattr(response, 'educational_error'))
                self.assertTrue(check_fn(response.educational_error), f"Failed for {persona.value}")
    
    def test_complex_error_with_multiple_solutions(self, backend):
        """Test complex errors provide multiple ranked solutions"""
        request = Request(
            query="nixos-rebuild switch",
            context={'persona': PersonaType.CARLOS.value}  # Learning user
        )
        
        complex_error = """
        error: The option `services.xserver.displayManager.plasma5' does not exist.
        Definition `/etc/nixos/configuration.nix:42',
    """
        
        with patch.object(backend.executor, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                success=False,
                error=complex_error,
                exit_code=1
            )
            
            response = backend.process(request)
            
            edu_error = response.educational_error
            self.assertGreater(len(edu_error.solutions), 2)  # Multiple solutions
            self.assertTrue(edu_error.learning_point)  # Educational content
            self.assertTrue(edu_error.examples)  # Concrete examples for Carlos
            
            # Solutions should be ranked by confidence
            self.assertTrue(any('plasma6' in s for s in edu_error.solutions))  # Suggest upgrade
            self.assertTrue(any('remove' in s for s in edu_error.solutions))  # Or removal


@pytest.mark.asyncio
class TestAsyncErrorIntelligence(unittest.TestCase):
    """Test async error handling"""
    
    async def test_async_error_processing(self):
        """Test async request processing with errors"""
        backend = EnhancedBackend({'learning_enabled': True})
        
        request = Request(
            query="install firefox",
            context={'persona': PersonaType.MAYA.value}
        )
        
        # Process asynchronously
        response = await backend.process_async(request)
        
        # Should work the same as sync
        self.assertEqual(response.intent.type, IntentType.INSTALL)
        self.assertIsNotNone(response.plan)

if __name__ == "__main__":
    unittest.main()
