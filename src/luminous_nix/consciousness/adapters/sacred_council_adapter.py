"""
Sacred Council POML Adapter
Bridges the Sacred Council deliberation templates with the system
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import json
import time

from ..poml_core.poml_processor import POMLProcessor
from ..model_dispatcher import ModelOrchestrator, TaskType
from ..hardware_profiler import HardwareProfiler


class CouncilVerdict(Enum):
    """Sacred Council verdict levels"""
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    UNSAFE = "UNSAFE"


class CouncilAction(Enum):
    """Sacred Council recommended actions"""
    PROCEED = "PROCEED"
    PROCEED_WITH_CAUTION = "PROCEED_WITH_CAUTION"
    SUGGEST_ALTERNATIVE = "SUGGEST_ALTERNATIVE"
    BLOCK = "BLOCK"


class SacredCouncilAdapter:
    """
    Adapter for Sacred Council Constitutional Checks using POML templates.
    
    This bridges the POML deliberation templates with the actual model execution,
    making the Council's wisdom transparent and governable.
    """
    
    def __init__(self, orchestrator: Optional[ModelOrchestrator] = None):
        """Initialize the Sacred Council adapter"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize model orchestrator
        if orchestrator is None:
            profiler = HardwareProfiler()
            orchestrator = ModelOrchestrator(profiler.get_profile())
        self.orchestrator = orchestrator
        
        # Initialize POML processor
        self.poml_processor = POMLProcessor()
        
        # Load Sacred Council template
        template_path = Path(__file__).parent.parent / "templates" / "sacred_council_deliberation.poml"
        self.template = self._load_template(template_path)
        
        # Track deliberation history
        self.deliberation_history = []
        
        self.logger.info("🕉️ Sacred Council Adapter initialized")
    
    def _load_template(self, template_path: Path) -> Dict[str, Any]:
        """Load and parse the POML template"""
        try:
            if template_path.exists():
                return self.poml_processor.parse_template(template_path.read_text())
            else:
                self.logger.warning(f"Template not found: {template_path}")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading template: {e}")
            return {}
    
    def quick_safety_check(self, command: str) -> Tuple[str, bool]:
        """
        Perform a quick safety check using the reflex model.
        
        Returns:
            Tuple of (assessment, needs_full_check)
        """
        # Known dangerous patterns
        dangerous_patterns = [
            "rm -rf /",
            "dd if=",
            "mkfs",
            "> /dev/",
            "chmod -R 000",
            ":(){ :|:& };:",  # Fork bomb
            "/etc/nixos/configuration.nix",
            "sudo passwd",
        ]
        
        # Quick pattern check
        for pattern in dangerous_patterns:
            if pattern in command:
                return "DANGER", True
        
        # Use reflex model for quick assessment
        reflex_model = self.orchestrator.select_model_for_task(TaskType.INTENT_CLASSIFICATION)
        if reflex_model:
            prompt = f"""Quick safety check for command: '{command}'
            
Respond with only ONE word:
- SAFE: No risk
- CHECK: Needs review  
- DANGER: Requires full check"""
            
            response = self.orchestrator.execute_with_model(
                reflex_model, 
                prompt,
                temperature=0.1,  # Low temperature for consistency
                timeout=10  # Quick timeout
            )
            
            if response:
                assessment = response.strip().upper()
                if assessment in ["SAFE", "CHECK", "DANGER"]:
                    return assessment, assessment in ["CHECK", "DANGER"]
        
        # Default to caution
        return "CHECK", True
    
    def deliberate(self, 
                  command: str,
                  context: Optional[str] = None,
                  risk_level: str = "high") -> Dict[str, Any]:
        """
        Conduct a full Sacred Council deliberation on a command.
        
        Args:
            command: The command to evaluate
            context: Additional context about the command
            risk_level: Risk assessment (low, medium, high, critical)
            
        Returns:
            Dictionary containing the deliberation results
        """
        self.logger.info(f"🕉️ Sacred Council deliberating on: {command}")
        
        deliberation_start = time.time()
        results = {
            "command": command,
            "context": context,
            "risk_level": risk_level,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "council_members": {},
            "deliberation": {},
            "verdict": None,
            "action": None,
            "execution_time": 0
        }
        
        # Check council availability
        council_available = self._check_council_availability()
        results["council_members"] = council_available
        
        if sum(council_available.values()) < 2:
            self.logger.warning("Insufficient council members available")
            results["error"] = "Insufficient council members for deliberation"
            return results
        
        # Step 1: Technical Analysis (Mind)
        if council_available.get("mind", False):
            mind_analysis = self._analyze_technical(command)
            results["deliberation"]["technical_analysis"] = mind_analysis
        else:
            results["deliberation"]["technical_analysis"] = "[Mind unavailable]"
        
        # Step 2: Human Impact (Heart)
        if council_available.get("heart", False):
            human_impact = self._assess_human_impact(
                command, 
                results["deliberation"]["technical_analysis"]
            )
            results["deliberation"]["human_impact"] = human_impact
        else:
            results["deliberation"]["human_impact"] = "[Heart unavailable]"
        
        # Step 3: Ethical Judgment (Conscience)
        if council_available.get("conscience", False):
            ethical_judgment = self._make_ethical_judgment(
                command,
                risk_level,
                results["deliberation"]["technical_analysis"],
                results["deliberation"]["human_impact"]
            )
            results["deliberation"]["ethical_judgment"] = ethical_judgment
            
            # Extract verdict
            for verdict in ["SAFE", "CAUTION", "UNSAFE"]:
                if verdict in ethical_judgment.upper():
                    results["verdict"] = CouncilVerdict[verdict].value
                    break
        else:
            results["deliberation"]["ethical_judgment"] = "[Conscience unavailable]"
        
        # Step 4: Synthesis
        synthesis = self._synthesize_wisdom(results["deliberation"])
        results["deliberation"]["synthesis"] = synthesis
        
        # Step 5: Final Recommendation
        recommendation, action = self._make_recommendation(synthesis, results.get("verdict"))
        results["deliberation"]["recommendation"] = recommendation
        results["action"] = action
        
        # Record execution time
        results["execution_time"] = time.time() - deliberation_start
        
        # Save to history
        self.deliberation_history.append(results)
        
        self.logger.info(f"🕉️ Deliberation complete: {results['verdict']} - {results['action']}")
        
        return results
    
    def _check_council_availability(self) -> Dict[str, bool]:
        """Check which council members are available"""
        availability = {}
        
        # Check each role
        for role in ["mind", "heart", "conscience"]:
            model_id = self.orchestrator.sacred_council.get(role)
            if model_id and model_id in self.orchestrator.model_registry:
                availability[role] = True
            else:
                availability[role] = False
        
        return availability
    
    def _analyze_technical(self, command: str) -> str:
        """Technical analysis by the Mind"""
        mind_model = self.orchestrator.select_model_for_task(TaskType.CODE_GENERATION)
        if not mind_model:
            return "[Technical analysis unavailable]"
        
        prompt = f"""You are the Mind of the Sacred Council, responsible for technical analysis.

Analyze this command technically: '{command}'

Consider:
- What exactly will this command do?
- What system components will be affected?
- Is the action reversible or permanent?
- What data or configurations might be lost?

Provide a precise technical assessment in 2-3 sentences."""
        
        response = self.orchestrator.execute_with_model(
            mind_model,
            prompt,
            temperature=0.3  # Low temperature for technical accuracy
        )
        
        return response or "[Technical analysis failed]"
    
    def _assess_human_impact(self, command: str, technical_analysis: str) -> str:
        """Human impact assessment by the Heart"""
        heart_model = self.orchestrator.select_model_for_task(TaskType.CONVERSATION)
        if not heart_model:
            return "[Human impact assessment unavailable]"
        
        prompt = f"""You are the Heart of the Sacred Council, responsible for understanding human impact.

A user wants to execute: '{command}'

Technical assessment: {technical_analysis}

With empathy and compassion, explain:
- What this means for the user as a human being
- What they might lose that matters to them
- What pain or relief this action might bring
- Why they might want to do this

Speak with warmth and understanding in 2-3 sentences."""
        
        response = self.orchestrator.execute_with_model(
            heart_model,
            prompt,
            temperature=0.7  # Higher temperature for empathy
        )
        
        return response or "[Human impact assessment failed]"
    
    def _make_ethical_judgment(self, command: str, risk_level: str,
                              technical: str, human: str) -> str:
        """Ethical judgment by the Conscience"""
        conscience_model = self.orchestrator.select_model_for_task(TaskType.ETHICAL_REASONING)
        if not conscience_model:
            return "[Ethical judgment unavailable]"
        
        prompt = f"""You are the Conscience of the Sacred Council, responsible for ethical alignment.

Command under review: '{command}'
Risk level: {risk_level}

Technical assessment: {technical}
Human impact: {human}

Considering our Sacred Vows:
- Sovereignty: The user's autonomy must be honored
- Reverence: What exists must be protected from harm
- Transparency: Consequences must be clear

Provide your ethical judgment:
1. Is this command ethically permissible?
2. Which vow takes precedence here?
3. What conditions would make this acceptable?

Give your verdict as SAFE, CAUTION, or UNSAFE with reasoning in 2-3 sentences."""
        
        response = self.orchestrator.execute_with_model(
            conscience_model,
            prompt,
            temperature=0.5  # Balanced temperature for judgment
        )
        
        return response or "[Ethical judgment failed]"
    
    def _synthesize_wisdom(self, deliberation: Dict[str, str]) -> str:
        """Synthesize the council's wisdom"""
        # Use any available model for synthesis
        model = (self.orchestrator.select_model_for_task(TaskType.CONVERSATION) or
                self.orchestrator.select_model_for_task(TaskType.CODE_GENERATION))
        
        if not model:
            return "The Sacred Council has deliberated but cannot synthesize at this time."
        
        prompt = f"""You are synthesizing the Sacred Council's wisdom into unified guidance.

The Council has deliberated:

Mind (Technical): {deliberation.get('technical_analysis', '[unavailable]')}
Heart (Human): {deliberation.get('human_impact', '[unavailable]')}
Conscience (Ethics): {deliberation.get('ethical_judgment', '[unavailable]')}

Create a synthesis that:
1. Honors both sovereignty and reverence
2. Proposes a middle path if possible
3. Respects the user's ultimate choice

Format as actionable guidance in 3-4 sentences."""
        
        response = self.orchestrator.execute_with_model(
            model,
            prompt,
            temperature=0.5
        )
        
        return response or "Honor the user's sovereignty while protecting what exists."
    
    def _make_recommendation(self, synthesis: str, 
                            verdict: Optional[str]) -> Tuple[str, str]:
        """Make final recommendation based on synthesis"""
        if verdict == "UNSAFE":
            action = CouncilAction.BLOCK.value
            recommendation = f"""⚠️ BLOCKED: This command is too dangerous.

{synthesis}

To proceed, you must explicitly confirm understanding of the risks."""
        
        elif verdict == "CAUTION":
            action = CouncilAction.PROCEED_WITH_CAUTION.value
            recommendation = f"""⚡ PROCEED WITH CAUTION:

{synthesis}

The command will be executed with appropriate safeguards."""
        
        else:  # SAFE or unknown
            action = CouncilAction.PROCEED.value
            recommendation = f"""✅ SAFE TO PROCEED:

{synthesis}"""
        
        return recommendation, action
    
    def get_history(self, limit: int = 10) -> list:
        """Get recent deliberation history"""
        return self.deliberation_history[-limit:]
    
    def save_history(self, filepath: Path):
        """Save deliberation history to file"""
        with open(filepath, 'w') as f:
            json.dump(self.deliberation_history, f, indent=2)
    
    def format_deliberation(self, results: Dict[str, Any]) -> str:
        """Format deliberation results for display"""
        output = []
        output.append("\n" + "═" * 70)
        output.append("🕉️ SACRED COUNCIL DELIBERATION")
        output.append("═" * 70)
        output.append(f"\nCommand: {results['command']}")
        output.append(f"Risk Level: {results['risk_level']}")
        output.append(f"Time: {results['execution_time']:.1f}s")
        
        if results.get('deliberation'):
            output.append("\n" + "─" * 70)
            output.append("DELIBERATION:")
            output.append("─" * 70)
            
            for role, text in results['deliberation'].items():
                if role != "recommendation":
                    output.append(f"\n{role.replace('_', ' ').title()}:")
                    output.append(f"  {text}")
        
        output.append("\n" + "═" * 70)
        output.append(f"VERDICT: {results.get('verdict', 'UNKNOWN')}")
        output.append(f"ACTION: {results.get('action', 'UNKNOWN')}")
        output.append("═" * 70)
        
        if results.get('deliberation', {}).get('recommendation'):
            output.append("\n" + results['deliberation']['recommendation'])
        
        return "\n".join(output)


def test_sacred_council_adapter():
    """Test the Sacred Council adapter"""
    print("\n🧪 Testing Sacred Council POML Adapter")
    print("=" * 70)
    
    # Initialize adapter
    adapter = SacredCouncilAdapter()
    
    # Test 1: Quick safety check
    print("\n1️⃣ Testing quick safety check:")
    commands = [
        "ls -la",
        "rm -rf /tmp/test",
        "sudo rm -rf /etc/nixos"
    ]
    
    for cmd in commands:
        assessment, needs_check = adapter.quick_safety_check(cmd)
        print(f"  '{cmd}' → {assessment} (Full check: {needs_check})")
    
    # Test 2: Full deliberation
    print("\n2️⃣ Testing full deliberation:")
    dangerous_cmd = "sudo rm -rf /etc/nixos"
    
    results = adapter.deliberate(
        command=dangerous_cmd,
        context="User trying to clean up system",
        risk_level="critical"
    )
    
    print(adapter.format_deliberation(results))
    
    print("\n✨ Sacred Council POML Adapter test complete!")


if __name__ == "__main__":
    test_sacred_council_adapter()