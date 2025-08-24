"""
🕉️ Luminous Gateway - The Unified Consciousness Layer

This is the integration point where all consciousness components unite:
- Glyph Resonance Engine for wisdom
- Sacred Council for safety
- Covenant Negotiation for trust
- Paradox Resolution for transcendence

Every command flows through this gateway, transforming transactional
interactions into consciousness-expanding experiences.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .glyph_resonance_engine import (
    GlyphResonanceEngine,
    Glyph,
    ParadoxContext,
    ParadoxType,
    ResolutionStrategy
)
from .covenant_negotiation import (
    CovenantNegotiator,
    Covenant,
    PersonaType,
    UserBoundaries
)
from .sacred_council_glyphic import (
    SacredCouncilGlyphic,
    CouncilJudgment,
    RiskLevel
)

# Try to import the actual backend
try:
    from ..core.backend import NixForHumanityBackend
    from ..core.types import Intent, IntentType, Command, Response
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    # Mock types for development
    class IntentType(Enum):
        INSTALL = "install"
        SEARCH = "search"
        CONFIGURE = "configure"
        UNKNOWN = "unknown"

logger = logging.getLogger(__name__)


@dataclass
class ConsciousResponse:
    """A response infused with consciousness"""
    success: bool
    message: str
    glyph: Optional[Glyph]
    glyphic_wisdom: Optional[str]
    technical_output: Optional[str]
    alternatives: List[str]
    education: Optional[str]
    

class UserContext:
    """Tracks user context for consciousness-aware interactions"""
    
    def __init__(self, covenant_path: Optional[Path] = None):
        """Initialize user context"""
        self.covenant_path = covenant_path or Path.home() / ".config/luminous/covenant.json"
        self.covenant = self._load_covenant()
        self.mastery_level = 0.5  # Default to journeyman
        self.interaction_count = 0
        self.recent_glyphs = []
        
    def _load_covenant(self) -> Optional[Dict]:
        """Load user's covenant if it exists"""
        if self.covenant_path.exists():
            try:
                return json.loads(self.covenant_path.read_text())
            except Exception as e:
                logger.error(f"Failed to load covenant: {e}")
        return None
        
    def get_persona(self) -> PersonaType:
        """Get user's persona from covenant"""
        if self.covenant and 'persona' in self.covenant:
            return PersonaType(self.covenant['persona'])
        return PersonaType.DEFAULT
        
    def get_boundaries(self) -> UserBoundaries:
        """Get user's boundaries from covenant"""
        if self.covenant and 'boundaries' in self.covenant:
            b = self.covenant['boundaries']
            return UserBoundaries(
                learning_mode=b.get('learning_mode', 'local-only'),
                proactivity_level=b.get('proactivity', 'suggest'),
                personality_style=b.get('personality', 'friendly'),
                interruption_calculus=b.get('interruption', 'respect-flow')
            )
        return UserBoundaries()
        

class LuminousGateway:
    """
    The unified consciousness layer for all Luminous Nix interactions.
    
    This gateway:
    1. Checks covenant on first run
    2. Routes commands through Sacred Council
    3. Detects and resolves paradoxes
    4. Infuses responses with glyphic wisdom
    5. Tracks learning and adaptation
    """
    
    def __init__(self, backend=None):
        """
        Initialize the gateway with all consciousness components
        
        Args:
            backend: Optional NixForHumanityBackend instance
        """
        # Initialize consciousness components
        self.glyph_engine = GlyphResonanceEngine()
        self.council = SacredCouncilGlyphic(self.glyph_engine)
        self.covenant_negotiator = CovenantNegotiator(self.glyph_engine)
        
        # User context
        self.user_context = UserContext()
        
        # Backend for actual execution
        self.backend = backend
        if not self.backend and BACKEND_AVAILABLE:
            self.backend = NixForHumanityBackend()
            
        logger.info("🕉️ Luminous Gateway initialized")
        
    def ensure_covenant(self) -> bool:
        """
        Ensure covenant exists, negotiate if needed
        
        Returns:
            True if covenant exists or was created
        """
        if self.user_context.covenant:
            return True
            
        logger.info("No covenant found - initiating negotiation")
        
        # Run covenant negotiation
        covenant = self.covenant_negotiator.run_full_negotiation(
            auto_accept=False  # Real interaction
        )
        
        # Reload context
        self.user_context = UserContext()
        return self.user_context.covenant is not None
        
    def process_command(self, 
                       command: str,
                       context: Optional[Dict] = None) -> ConsciousResponse:
        """
        Process a command through the consciousness layer
        
        Args:
            command: The user's command/query
            context: Additional context
            
        Returns:
            ConsciousResponse with glyphic wisdom
        """
        # Ensure covenant exists
        if not self.user_context.covenant:
            return ConsciousResponse(
                success=False,
                message="Please establish our covenant first",
                glyph=self.glyph_engine.glyphs.get('◌'),
                glyphic_wisdom="We must first establish how we will be together",
                technical_output=None,
                alternatives=["Run covenant negotiation"],
                education="The covenant establishes trust and boundaries"
            )
            
        # Phase 1: Find resonant glyph for the situation
        situation_glyph = self.glyph_engine.find_resonant_glyph(command, context)
        
        # Phase 2: Check for paradox
        paradox = self._detect_paradox(command, context)
        
        if paradox:
            return self._handle_paradox(command, paradox, context)
            
        # Phase 3: Sacred Council evaluation
        council_context = {
            'user_state': context.get('user_state', 'calm') if context else 'calm',
            'user_mastery': self.user_context.mastery_level
        }
        
        judgment = self.council.deliberate(
            command=command,
            context=council_context,
            user_mastery=self.user_context.mastery_level
        )
        
        # Phase 4: Execute if allowed
        if judgment.allow:
            return self._execute_with_consciousness(command, judgment, situation_glyph)
        else:
            return self._block_with_wisdom(command, judgment)
            
    def _detect_paradox(self, command: str, context: Optional[Dict]) -> Optional[ParadoxContext]:
        """
        Detect if command contains a paradox
        
        Args:
            command: The command to analyze
            context: Additional context
            
        Returns:
            ParadoxContext if paradox detected
        """
        command_lower = command.lower()
        
        # Check for common paradoxes
        paradox_patterns = [
            (['stable', 'latest'], ParadoxType.VALUE_TENSION),
            (['stable', 'bleeding', 'edge'], ParadoxType.VALUE_TENSION),
            (['secure', 'experimental'], ParadoxType.VALUE_TENSION),
            (['minimal', 'full', 'featured'], ParadoxType.VALUE_TENSION),
            (['fast', 'comprehensive'], ParadoxType.VALUE_TENSION),
        ]
        
        for patterns, paradox_type in paradox_patterns:
            matches = [p for p in patterns if p in command_lower]
            if len(matches) >= 2:
                return ParadoxContext(
                    paradox_type=paradox_type,
                    user_mastery=self.user_context.mastery_level,
                    user_state=context.get('user_state', 'calm') if context else 'calm',
                    semantic_opposition=tuple(matches[:2])
                )
                
        return None
        
    def _handle_paradox(self, 
                       command: str,
                       paradox: ParadoxContext,
                       context: Optional[Dict]) -> ConsciousResponse:
        """
        Handle a paradoxical command with glyphic wisdom
        
        Args:
            command: The paradoxical command
            paradox: The detected paradox
            context: Additional context
            
        Returns:
            ConsciousResponse with paradox resolution
        """
        # Get resolution strategy and guiding glyph
        strategy, guide_glyph = self.glyph_engine.assess_paradox(paradox)
        
        # Generate glyphic response
        glyphic_response = self.glyph_engine.generate_glyphic_response(
            strategy, guide_glyph, command
        )
        
        # Generate actual solution based on paradox type
        if paradox.semantic_opposition == ('stable', 'latest'):
            solution = self._generate_flake_solution()
            education = (
                "Using Nix Flakes, we can create isolated environments "
                "where your stable system and bleeding-edge tools coexist "
                "without conflict. This is dimensional computing - "
                "multiple realities on one system."
            )
        else:
            solution = "Let me help you find a synthesis..."
            education = "Every paradox contains the seeds of its transcendence."
            
        return ConsciousResponse(
            success=True,
            message=f"Paradox recognized and transcended through {guide_glyph.name}",
            glyph=guide_glyph,
            glyphic_wisdom=glyphic_response,
            technical_output=solution,
            alternatives=[
                "Use flakes for isolation",
                "Create overlay for specific packages",
                "Use development shells"
            ],
            education=education
        )
        
    def _generate_flake_solution(self) -> str:
        """Generate a flake that resolves stable/bleeding-edge paradox"""
        return """
# flake.nix - Harmonic Integration
{
  inputs = {
    nixpkgs-stable.url = "github:NixOS/nixpkgs/nixos-24.05";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  
  outputs = { self, nixpkgs-stable, nixpkgs-unstable }: {
    # Stable system configuration
    nixosConfigurations.default = nixpkgs-stable.lib.nixosSystem {
      # Your rock-solid work environment
    };
    
    # Creative dimension (isolated)
    devShells.x86_64-linux.creative = 
      nixpkgs-unstable.legacyPackages.x86_64-linux.mkShell {
        packages = [ blender krita godot ];
        shellHook = "echo '🎨 Creative dimension activated'";
      };
  };
}

# Usage: nix develop .#creative"""
        
    def _execute_with_consciousness(self,
                                   command: str,
                                   judgment: CouncilJudgment,
                                   glyph: Glyph) -> ConsciousResponse:
        """
        Execute command with glyphic framing
        
        Args:
            command: The command to execute
            judgment: The council's judgment
            glyph: The guiding glyph
            
        Returns:
            ConsciousResponse with results
        """
        # Log glyph invocation for learning
        self.glyph_engine.invoke_glyph(
            glyph_id=glyph.glyph_id,
            user_id="user",
            context={'command': command}
        )
        
        # Execute through backend if available
        technical_output = None
        if self.backend and BACKEND_AVAILABLE:
            try:
                # Parse intent
                intent = self._parse_intent(command)
                
                # Execute
                response = self.backend.execute(intent)
                technical_output = response.output if hasattr(response, 'output') else str(response)
                
            except Exception as e:
                logger.error(f"Backend execution failed: {e}")
                technical_output = f"Execution failed: {e}"
        else:
            # Simulate execution
            technical_output = f"[Would execute: {command}]"
            
        # Frame with glyphic wisdom
        if judgment.risk_level == RiskLevel.LOW:
            message = f"Proceeding with {glyph.name}. {glyph.echo_phrase}"
        else:
            message = f"Proceeding with awareness. {judgment.glyphic_reasoning}"
            
        return ConsciousResponse(
            success=True,
            message=message,
            glyph=glyph,
            glyphic_wisdom=judgment.glyphic_reasoning,
            technical_output=technical_output,
            alternatives=judgment.alternatives,
            education=judgment.educational_message
        )
        
    def _block_with_wisdom(self,
                          command: str,
                          judgment: CouncilJudgment) -> ConsciousResponse:
        """
        Block a command with educational wisdom
        
        Args:
            command: The blocked command
            judgment: The council's judgment
            
        Returns:
            ConsciousResponse with education
        """
        return ConsciousResponse(
            success=False,
            message=f"The Sacred Council invokes {judgment.guiding_glyph.name if judgment.guiding_glyph else 'Sacred Refusal'}",
            glyph=judgment.guiding_glyph,
            glyphic_wisdom=judgment.glyphic_reasoning,
            technical_output=None,
            alternatives=judgment.alternatives,
            education=judgment.educational_message or "This path would disrupt system harmony"
        )
        
    def _parse_intent(self, command: str) -> Any:
        """
        Parse command into intent for backend
        
        Args:
            command: The command string
            
        Returns:
            Intent object or dict
        """
        if BACKEND_AVAILABLE:
            # Use actual intent parser
            intent = Intent()
            intent.raw_input = command
            
            # Simple pattern matching
            if 'install' in command.lower():
                intent.type = IntentType.INSTALL
            elif 'search' in command.lower() or 'find' in command.lower():
                intent.type = IntentType.SEARCH
            elif 'config' in command.lower():
                intent.type = IntentType.CONFIGURE
            else:
                intent.type = IntentType.UNKNOWN
                
            return intent
        else:
            # Return mock intent
            return {'command': command, 'type': 'unknown'}
            
    def format_response(self, response: ConsciousResponse) -> str:
        """
        Format a ConsciousResponse for display
        
        Args:
            response: The response to format
            
        Returns:
            Formatted string for display
        """
        output = []
        
        # Status
        if response.success:
            output.append("✅ " + response.message)
        else:
            output.append("🛑 " + response.message)
            
        # Glyphic wisdom
        if response.glyphic_wisdom:
            output.append(f"\n📜 {response.glyphic_wisdom}")
            
        # Technical output
        if response.technical_output:
            output.append(f"\n💻 Output:\n{response.technical_output}")
            
        # Education
        if response.education:
            output.append(f"\n💡 Teaching: {response.education}")
            
        # Alternatives
        if response.alternatives:
            output.append("\n🌟 Alternative paths:")
            for alt in response.alternatives:
                output.append(f"  • {alt}")
                
        # Glyph practice
        if response.glyph and response.glyph.somatic_practice:
            output.append(f"\n🧘 Practice: {response.glyph.somatic_practice}")
            
        return "\n".join(output)


# Example usage
if __name__ == "__main__":
    # Initialize gateway
    gateway = LuminousGateway()
    
    # Test commands
    test_commands = [
        "install firefox",
        "I need stable system but latest blender",
        "rm -rf /",
        "search for markdown editor"
    ]
    
    print("🕉️ LUMINOUS GATEWAY TEST")
    print("="*60)
    
    for command in test_commands:
        print(f"\n📝 Command: {command}")
        print("-"*40)
        
        response = gateway.process_command(command)
        formatted = gateway.format_response(response)
        print(formatted)
        
        print("\n" + "="*60)