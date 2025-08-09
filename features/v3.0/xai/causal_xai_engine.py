#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Causal XAI Engine for Nix for Humanity
Provides "why" explanations for AI decisions using causal reasoning

This module implements:
- Basic causal explanations using DoWhy framework
- Confidence indicators for responses
- Multiple explanation depth levels (simple → detailed)
- Decision trees for complex operations
"""

import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pathlib import Path

# Optional numpy import
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Optional imports with graceful fallback
try:
    import dowhy
    from dowhy import CausalModel
    DOWHY_AVAILABLE = True
except ImportError:
    DOWHY_AVAILABLE = False
    logging.warning("DoWhy not available. Causal reasoning will use fallback methods.")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available. Feature importance will use simple heuristics.")


class ExplanationDepth(Enum):
    """Levels of explanation detail"""
    SIMPLE = "simple"        # One-line explanation for everyone
    STANDARD = "standard"    # 2-3 sentences with context
    DETAILED = "detailed"    # Full reasoning with examples
    TECHNICAL = "technical"  # Include causal graphs and probabilities


class ConfidenceLevel(Enum):
    """Confidence levels for explanations"""
    VERY_HIGH = (0.9, 1.0, "I'm very confident about this")
    HIGH = (0.7, 0.9, "I'm confident about this")
    MODERATE = (0.5, 0.7, "I think this is correct")
    LOW = (0.3, 0.5, "I'm somewhat uncertain about this")
    VERY_LOW = (0.0, 0.3, "I'm quite uncertain, but here's my best guess")


@dataclass
class CausalExplanation:
    """Structured explanation with causal reasoning"""
    what: str              # What is being done
    why: str               # Why this action is recommended
    how: str               # How it works
    confidence: float      # 0.0 to 1.0 confidence score
    alternatives: List[str]  # Alternative approaches
    causal_factors: Dict[str, float]  # Factors influencing the decision
    risks: List[str]       # Potential risks or side effects
    benefits: List[str]    # Expected benefits


class CausalXAIEngine:
    """Engine for generating causal explanations of AI decisions"""
    
    def __init__(self, knowledge_base_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.knowledge_base_path = knowledge_base_path
        
        # Load causal knowledge patterns
        self.causal_patterns = self._load_causal_patterns()
        
        # Initialize explanation cache
        self.explanation_cache = {}
        
        # Track user preferences for explanation depth
        self.user_preferences = {
            'depth': ExplanationDepth.STANDARD,
            'include_confidence': True,
            'show_alternatives': True
        }
    
    def _load_causal_patterns(self) -> Dict[str, Dict]:
        """Load pre-defined causal patterns for common NixOS operations"""
        return {
            'install_package': {
                'causes': {
                    'user_need': 0.4,
                    'dependency': 0.3,
                    'recommendation': 0.2,
                    'upgrade': 0.1
                },
                'effects': {
                    'system_change': 0.8,
                    'disk_usage': 0.6,
                    'functionality': 0.9
                },
                'confidence_factors': {
                    'package_exists': 0.3,
                    'channel_updated': 0.2,
                    'similar_success': 0.3,
                    'user_history': 0.2
                }
            },
            'update_system': {
                'causes': {
                    'security': 0.4,
                    'features': 0.3,
                    'stability': 0.2,
                    'routine': 0.1
                },
                'effects': {
                    'security_improvement': 0.8,
                    'potential_breaking': 0.3,
                    'new_features': 0.7,
                    'performance': 0.5
                }
            },
            'remove_package': {
                'causes': {
                    'unused': 0.4,
                    'conflict': 0.2,
                    'space': 0.2,
                    'replacement': 0.2
                },
                'effects': {
                    'free_space': 0.7,
                    'dependency_impact': 0.5,
                    'functionality_loss': 0.8
                }
            },
            'search_package': {
                'causes': {
                    'exploration': 0.5,
                    'specific_need': 0.3,
                    'comparison': 0.2
                },
                'effects': {
                    'knowledge_gain': 0.9,
                    'decision_quality': 0.7
                }
            }
        }
    
    def explain_intent(self, 
                      intent: Dict[str, Any],
                      context: Dict[str, Any],
                      depth: ExplanationDepth = ExplanationDepth.STANDARD) -> CausalExplanation:
        """Generate causal explanation for an intent"""
        
        action = intent.get('action', 'unknown')
        package = intent.get('package', '')
        
        # Calculate confidence based on various factors
        confidence = self._calculate_confidence(intent, context)
        
        # Get causal factors for this action
        causal_factors = self._analyze_causal_factors(action, context)
        
        # Generate explanations at different depths
        if depth == ExplanationDepth.SIMPLE:
            explanation = self._generate_simple_explanation(action, package, confidence)
        elif depth == ExplanationDepth.DETAILED:
            explanation = self._generate_detailed_explanation(action, package, causal_factors, context)
        elif depth == ExplanationDepth.TECHNICAL:
            explanation = self._generate_technical_explanation(action, package, causal_factors, context)
        else:  # STANDARD
            explanation = self._generate_standard_explanation(action, package, confidence, causal_factors)
        
        return explanation
    
    def _calculate_confidence(self, intent: Dict, context: Dict) -> float:
        """Calculate confidence score for the intent"""
        action = intent.get('action', 'unknown')
        
        # Base confidence from intent recognition
        base_confidence = intent.get('confidence', 0.7)
        
        # Adjust based on causal patterns
        if action in self.causal_patterns:
            factors = self.causal_patterns[action].get('confidence_factors', {})
            
            # Check various confidence factors
            adjustments = []
            
            # Package exists in nixpkgs
            if intent.get('package_verified', False):
                adjustments.append(factors.get('package_exists', 0.3))
            
            # Recent channel update
            if context.get('channels_updated_recently', False):
                adjustments.append(factors.get('channel_updated', 0.2))
            
            # Similar commands succeeded before
            if context.get('similar_success_rate', 0) > 0.8:
                adjustments.append(factors.get('similar_success', 0.3))
            
            # User has done this before successfully
            if context.get('user_did_before', False):
                adjustments.append(factors.get('user_history', 0.2))
            
            # Weighted confidence
            if adjustments:
                confidence_boost = sum(adjustments) / len(adjustments)
                base_confidence = min(1.0, base_confidence + confidence_boost * 0.3)
        
        return base_confidence
    
    def _analyze_causal_factors(self, action: str, context: Dict) -> Dict[str, float]:
        """Analyze causal factors influencing the decision"""
        if action not in self.causal_patterns:
            return {'unknown_action': 1.0}
        
        pattern = self.causal_patterns[action]
        causes = pattern.get('causes', {})
        
        # Adjust weights based on context
        adjusted_factors = {}
        
        for cause, base_weight in causes.items():
            # Contextual adjustments
            if cause == 'user_need' and context.get('explicit_request', True):
                adjusted_factors[cause] = base_weight * 1.2
            elif cause == 'security' and context.get('security_updates_available', False):
                adjusted_factors[cause] = base_weight * 1.5
            elif cause == 'dependency' and context.get('dependency_chain', []):
                adjusted_factors[cause] = base_weight * 1.3
            else:
                adjusted_factors[cause] = base_weight
        
        # Normalize weights
        total = sum(adjusted_factors.values())
        if total > 0:
            adjusted_factors = {k: v/total for k, v in adjusted_factors.items()}
        
        return adjusted_factors
    
    def _generate_simple_explanation(self, action: str, package: str, confidence: float) -> CausalExplanation:
        """Generate simple one-line explanation"""
        explanations = {
            'install_package': f"Installing {package} because you asked for it",
            'update_system': "Updating to get the latest security fixes and features",
            'remove_package': f"Removing {package} to free up space and reduce complexity",
            'search_package': f"Searching for {package} to find available options",
            'unknown': "Processing your request"
        }
        
        why = explanations.get(action, explanations['unknown'])
        
        return CausalExplanation(
            what=f"{action.replace('_', ' ').title()}",
            why=why,
            how="Using NixOS package manager",
            confidence=confidence,
            alternatives=[],
            causal_factors={},
            risks=[],
            benefits=[]
        )
    
    def _generate_standard_explanation(self, action: str, package: str, 
                                     confidence: float, causal_factors: Dict[str, float]) -> CausalExplanation:
        """Generate standard 2-3 sentence explanation"""
        
        # Build causal narrative
        primary_cause = max(causal_factors.items(), key=lambda x: x[1])[0] if causal_factors else 'unknown'
        
        explanations = {
            'install_package': {
                'what': f"Installing {package}",
                'why': self._build_why_narrative('install', package, primary_cause),
                'how': f"I'll use 'nix profile install' to add {package} to your user profile",
                'alternatives': ["Install system-wide in configuration.nix", "Use nix-shell for temporary access"],
                'risks': ["Disk space usage", "Potential conflicts with existing packages"],
                'benefits': ["New functionality available", "User-level installation (no sudo needed)"]
            },
            'update_system': {
                'what': "Updating your NixOS system",
                'why': self._build_why_narrative('update', '', primary_cause),
                'how': "I'll update your channels and rebuild the system configuration",
                'alternatives': ["Update specific packages only", "Switch to a different channel"],
                'risks': ["Temporary internet usage", "Possible breaking changes"],
                'benefits': ["Latest security patches", "New features and improvements"]
            },
            'remove_package': {
                'what': f"Removing {package}",
                'why': self._build_why_narrative('remove', package, primary_cause),
                'how': f"I'll use 'nix profile remove' to uninstall {package} from your profile",
                'alternatives': ["Keep but disable", "Replace with alternative"],
                'risks': ["Loss of functionality", "Dependent packages might be affected"],
                'benefits': ["Free disk space", "Cleaner system"]
            },
            'search_package': {
                'what': f"Searching for {package}",
                'why': self._build_why_narrative('search', package, primary_cause),
                'how': "I'll search the Nix package repository for matching packages",
                'alternatives': ["Browse packages online", "Search by category"],
                'risks': ["None"],
                'benefits': ["Discover available options", "Find exact package names"]
            }
        }
        
        details = explanations.get(action, {
            'what': "Processing your request",
            'why': "You asked me to help",
            'how': "Using appropriate NixOS commands",
            'alternatives': [],
            'risks': [],
            'benefits': []
        })
        
        return CausalExplanation(
            what=details['what'],
            why=details['why'],
            how=details['how'],
            confidence=confidence,
            alternatives=details['alternatives'],
            causal_factors=causal_factors,
            risks=details['risks'],
            benefits=details['benefits']
        )
    
    def _build_why_narrative(self, action: str, package: str, primary_cause: str) -> str:
        """Build a narrative explanation of why an action is recommended"""
        narratives = {
            'install': {
                'user_need': f"You need {package} for your work",
                'dependency': f"Another package requires {package}",
                'recommendation': f"{package} is recommended for your use case",
                'upgrade': f"This installs an updated version of {package}"
            },
            'update': {
                'security': "Security updates are available that should be installed",
                'features': "New features and improvements are available",
                'stability': "System stability improvements are available",
                'routine': "It's good practice to keep your system updated"
            },
            'remove': {
                'unused': f"{package} appears to be unused",
                'conflict': f"{package} may be conflicting with other software",
                'space': f"Removing {package} will free up disk space",
                'replacement': f"You're replacing {package} with something else"
            },
            'search': {
                'exploration': f"You're exploring available options for {package}",
                'specific_need': f"You need to find the exact package name",
                'comparison': f"You want to compare different {package} options"
            }
        }
        
        action_narratives = narratives.get(action, {})
        return action_narratives.get(primary_cause, f"This action will help with your request")
    
    def _generate_detailed_explanation(self, action: str, package: str, 
                                     causal_factors: Dict[str, float], context: Dict) -> CausalExplanation:
        """Generate detailed explanation with examples"""
        
        # Get standard explanation first
        base = self._generate_standard_explanation(action, package, 
                                                 self._calculate_confidence({'action': action}, context),
                                                 causal_factors)
        
        # Enhance with detailed information
        detailed_how = self._generate_detailed_how(action, package, context)
        detailed_risks = self._generate_detailed_risks(action, package, context)
        detailed_benefits = self._generate_detailed_benefits(action, package, context)
        
        # Add examples
        if action == 'install_package':
            base.how = f"{base.how}\n\nExample: 'nix profile install nixpkgs#{package}'\n{detailed_how}"
        
        base.risks = detailed_risks
        base.benefits = detailed_benefits
        
        return base
    
    def _generate_technical_explanation(self, action: str, package: str,
                                      causal_factors: Dict[str, float], context: Dict) -> CausalExplanation:
        """Generate technical explanation with causal graphs"""
        
        # Get detailed explanation first
        base = self._generate_detailed_explanation(action, package, causal_factors, context)
        
        # Add technical details
        if DOWHY_AVAILABLE and action in self.causal_patterns:
            # Build causal graph representation
            pattern = self.causal_patterns[action]
            
            causal_graph = f"\nCausal Graph:\n"
            causal_graph += f"Causes → {action} → Effects\n"
            
            for cause, weight in pattern.get('causes', {}).items():
                causal_graph += f"  {cause} ({weight:.2f}) → \n"
            
            causal_graph += f"    ↓ {action} ↓\n"
            
            for effect, probability in pattern.get('effects', {}).items():
                causal_graph += f"      → {effect} (P={probability:.2f})\n"
            
            base.how += f"\n{causal_graph}"
        
        # Add confidence calculation details
        confidence_details = "\nConfidence Calculation:\n"
        for factor, weight in causal_factors.items():
            confidence_details += f"  {factor}: {weight:.2f}\n"
        confidence_details += f"  Overall: {base.confidence:.2f}"
        
        base.why += confidence_details
        
        return base
    
    def _generate_detailed_how(self, action: str, package: str, context: Dict) -> str:
        """Generate detailed how-to information"""
        details = {
            'install_package': f"""
The installation process:
1. Search for {package} in the Nix package repository
2. Download the package and all dependencies
3. Build or fetch pre-built binaries
4. Create symlinks in your profile
5. Update your PATH to include the new package

Time estimate: 30 seconds to 5 minutes depending on package size""",
            
            'update_system': """
The update process:
1. Fetch latest channel information
2. Download updated packages
3. Build new system configuration
4. Create new generation
5. Switch to updated system

Time estimate: 5-30 minutes depending on updates""",
            
            'remove_package': f"""
The removal process:
1. Identify {package} in your profile
2. Remove package symlinks
3. Update profile manifest
4. Garbage collection (optional)

Time estimate: A few seconds""",
            
            'search_package': f"""
The search process:
1. Query local package cache
2. Search package names and descriptions
3. Rank results by relevance
4. Display matching packages

Time estimate: 1-2 seconds"""
        }
        
        return details.get(action, "Standard NixOS operation")
    
    def _generate_detailed_risks(self, action: str, package: str, context: Dict) -> List[str]:
        """Generate detailed risk assessment"""
        risks = {
            'install_package': [
                f"Disk space: {package} and dependencies may use significant space",
                "Conflicts: May conflict with system packages if names overlap",
                "Dependencies: Installing many dependencies could complicate your system",
                "Updates: You'll need to manually update user-profile packages"
            ],
            'update_system': [
                "Breaking changes: Some packages might change behavior",
                "Configuration conflicts: Your custom configs might need adjustment",
                "Downtime: System will be briefly unavailable during switch",
                "Rollback needed: If issues occur, you may need to rollback"
            ],
            'remove_package': [
                f"Functionality loss: Features provided by {package} will be unavailable",
                "Dependent packages: Other packages relying on this might fail",
                "Configuration files: Personal configs may be left behind",
                "Reinstall hassle: You'll need to reinstall if you need it again"
            ],
            'search_package': [
                "No significant risks"
            ]
        }
        
        return risks.get(action, ["Unknown operation risks"])
    
    def _generate_detailed_benefits(self, action: str, package: str, context: Dict) -> List[str]:
        """Generate detailed benefits list"""
        benefits = {
            'install_package': [
                f"New functionality: {package} features become available",
                "User-level: No system-wide changes or sudo required",
                "Isolated: Won't affect other users on the system",
                "Reversible: Easy to remove if not needed"
            ],
            'update_system': [
                "Security: Latest patches protect against vulnerabilities",
                "Performance: Bug fixes and optimizations",
                "Features: New functionality in updated packages",
                "Stability: Many bugs fixed in newer versions"
            ],
            'remove_package': [
                f"Disk space: Reclaim space used by {package}",
                "Simplicity: Fewer packages mean less complexity",
                "Performance: Slightly faster profile activation",
                "Clarity: Cleaner package list"
            ],
            'search_package': [
                "Discovery: Find packages you didn't know existed",
                "Accuracy: Get exact package names for installation",
                "Comparison: See different options available",
                "Learning: Understand package ecosystem better"
            ]
        }
        
        return benefits.get(action, ["Operation will help achieve your goal"])
    
    def format_explanation_for_display(self, 
                                     explanation: CausalExplanation,
                                     depth: ExplanationDepth,
                                     persona: Optional[str] = None) -> str:
        """Format explanation for display to user"""
        
        # Start with confidence indicator if enabled
        output = []
        
        if self.user_preferences['include_confidence']:
            confidence_level = self._get_confidence_level(explanation.confidence)
            output.append(f"🎯 Confidence: {confidence_level.value[2]} ({explanation.confidence:.0%})")
            output.append("")
        
        # Main explanation
        output.append(f"**What**: {explanation.what}")
        output.append(f"**Why**: {explanation.why}")
        
        if depth != ExplanationDepth.SIMPLE:
            output.append(f"**How**: {explanation.how}")
        
        # Causal factors for standard and above
        if depth in [ExplanationDepth.STANDARD, ExplanationDepth.DETAILED, ExplanationDepth.TECHNICAL]:
            if explanation.causal_factors:
                output.append("\n**Main factors**:")
                sorted_factors = sorted(explanation.causal_factors.items(), 
                                      key=lambda x: x[1], reverse=True)
                for factor, weight in sorted_factors[:3]:  # Top 3 factors
                    output.append(f"  • {factor.replace('_', ' ').title()}: {weight:.0%}")
        
        # Benefits and risks for detailed and above
        if depth in [ExplanationDepth.DETAILED, ExplanationDepth.TECHNICAL]:
            if explanation.benefits:
                output.append("\n**Benefits**:")
                for benefit in explanation.benefits[:3]:  # Top 3 benefits
                    output.append(f"  ✓ {benefit}")
            
            if explanation.risks and explanation.risks[0] != "No significant risks":
                output.append("\n**Considerations**:")
                for risk in explanation.risks[:3]:  # Top 3 risks
                    output.append(f"  ⚠ {risk}")
        
        # Alternatives if enabled
        if self.user_preferences['show_alternatives'] and explanation.alternatives:
            output.append("\n**Alternatives**:")
            for alt in explanation.alternatives[:2]:  # Top 2 alternatives
                output.append(f"  → {alt}")
        
        # Adjust language for persona if specified
        if persona:
            output = self._adjust_for_persona(output, persona)
        
        return "\n".join(output)
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Get confidence level enum from float value"""
        for level in ConfidenceLevel:
            min_conf, max_conf, _ = level.value
            if min_conf <= confidence < max_conf:
                return level
        return ConfidenceLevel.MODERATE
    
    def _adjust_for_persona(self, output_lines: List[str], persona: str) -> List[str]:
        """Adjust language complexity for different personas"""
        
        if persona == "grandma_rose":
            # Simplify technical terms
            adjusted = []
            for line in output_lines:
                line = line.replace("package", "program")
                line = line.replace("repository", "app store")
                line = line.replace("dependencies", "required parts")
                line = line.replace("configuration", "settings")
                adjusted.append(line)
            return adjusted
        
        elif persona == "maya_adhd":
            # Make more concise
            return [line for line in output_lines if not line.startswith("  ⚠")][:8]
        
        elif persona == "dr_sarah":
            # Keep technical, add more detail
            return output_lines
        
        else:
            return output_lines
    
    def get_quick_explanation(self, action: str, package: str = "") -> str:
        """Get a quick one-line explanation without full analysis"""
        quick_explanations = {
            'install_package': f"Installing {package} to add new functionality to your system",
            'update_system': "Updating your system to get the latest improvements and security fixes",
            'remove_package': f"Removing {package} to clean up your system",
            'search_package': f"Searching for {package} to see what's available",
            'list_packages': "Showing all installed packages in your profile",
            'rollback': "Reverting to a previous system state",
            'help': "Providing assistance with NixOS commands"
        }
        
        return quick_explanations.get(action, "Processing your request")
    
    def explain_error(self, error: str, context: Dict) -> Dict[str, Any]:
        """Explain why an error occurred and how to fix it"""
        
        # Common error patterns and explanations
        error_explanations = {
            'attribute.*missing': {
                'why': "The package name doesn't exist in the repository",
                'how_to_fix': [
                    "Check the spelling of the package name",
                    "Search for the correct name: 'search <partial-name>'",
                    "Update channels: 'sudo nix-channel --update'"
                ],
                'confidence': 0.9
            },
            'collision': {
                'why': "Two packages are trying to install the same file",
                'how_to_fix': [
                    "Remove one of the conflicting packages",
                    "Use package overrides to resolve conflicts",
                    "Install in a separate profile"
                ],
                'confidence': 0.85
            },
            'disk.*full|space': {
                'why': "Not enough disk space for the operation",
                'how_to_fix': [
                    "Free space: 'nix-collect-garbage -d'",
                    "Remove old generations: 'nix-env --delete-generations old'",
                    "Check disk usage: 'df -h'"
                ],
                'confidence': 0.95
            },
            'permission.*denied': {
                'why': "The operation requires elevated privileges",
                'how_to_fix': [
                    "Run with sudo if it's a system operation",
                    "Check file ownership and permissions",
                    "Use user-level commands instead"
                ],
                'confidence': 0.9
            },
            'network|download|fetch': {
                'why': "Network connection issue preventing downloads",
                'how_to_fix': [
                    "Check your internet connection",
                    "Try again in a few moments",
                    "Check if Nix cache is accessible"
                ],
                'confidence': 0.8
            }
        }
        
        # Find matching error pattern
        import re
        for pattern, explanation in error_explanations.items():
            if re.search(pattern, error, re.IGNORECASE):
                return {
                    'understood': True,
                    'why': explanation['why'],
                    'how_to_fix': explanation['how_to_fix'],
                    'confidence': explanation['confidence']
                }
        
        # Fallback for unknown errors
        return {
            'understood': False,
            'why': "An unexpected error occurred",
            'how_to_fix': [
                "Check the full error message for clues",
                "Search online for the specific error",
                "Ask for help with the exact error message"
            ],
            'confidence': 0.3
        }
    
    def learn_from_outcome(self, intent: Dict, outcome: Dict, user_feedback: Optional[Dict] = None):
        """Learn from the outcome of an action to improve future explanations"""
        
        action = intent.get('action')
        success = outcome.get('success', False)
        
        # Update confidence factors based on outcome
        if action in self.causal_patterns:
            if success:
                # Strengthen confidence in successful patterns
                pattern = self.causal_patterns[action]
                if 'confidence_factors' in pattern:
                    for factor in pattern['confidence_factors']:
                        pattern['confidence_factors'][factor] *= 1.05  # 5% boost
            else:
                # Reduce confidence in failed patterns
                pattern = self.causal_patterns[action]
                if 'confidence_factors' in pattern:
                    for factor in pattern['confidence_factors']:
                        pattern['confidence_factors'][factor] *= 0.95  # 5% reduction
        
        # Store in explanation cache for quick retrieval
        cache_key = f"{action}:{intent.get('package', '')}"
        self.explanation_cache[cache_key] = {
            'outcome': outcome,
            'timestamp': None,  # Would use datetime.now() in production
            'feedback': user_feedback
        }
    
    def set_user_preference(self, preference: str, value: Any):
        """Set user preference for explanations"""
        if preference in self.user_preferences:
            self.user_preferences[preference] = value
    
    def get_explanation_summary(self) -> Dict[str, Any]:
        """Get summary of explanation system performance"""
        total_explanations = len(self.explanation_cache)
        successful = sum(1 for e in self.explanation_cache.values() 
                        if e['outcome'].get('success', False))
        
        return {
            'total_explanations': total_explanations,
            'success_rate': successful / total_explanations if total_explanations > 0 else 0,
            'preferences': self.user_preferences,
            'available_features': {
                'dowhy': DOWHY_AVAILABLE,
                'shap': SHAP_AVAILABLE
            }
        }