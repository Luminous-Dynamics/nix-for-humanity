#!/usr/bin/env python3
"""
Rollback Intelligence - Analyze what broke and find the EXACT safe generation
Turns panic into precision by identifying breaking changes and safe rollback points
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

# Import core infrastructure
try:
    from .core.state_analyzer import get_state_analyzer, SystemGeneration
except ImportError:
    import sys
    sys.path.append('..')
    from core.state_analyzer import get_state_analyzer, SystemGeneration

logger = logging.getLogger(__name__)

@dataclass
class RollbackAnalysis:
    """Analysis result for rollback decision"""
    current_generation: int
    recommended_generation: int
    confidence: float
    reason: str
    changes_detected: List[str]
    risk_level: str  # low, medium, high
    rollback_command: str
    alternative_generations: List[Tuple[int, str]]  # (gen_num, reason)

class RollbackIntelligence:
    """
    Intelligent rollback analysis using HRM reasoning
    Identifies what broke and finds the safest rollback point
    """
    
    def __init__(self):
        self.analyzer = get_state_analyzer()
        
        # Breaking change patterns
        self.breaking_patterns = {
            'kernel': {
                'risk': 'high',
                'symptoms': ['boot failure', 'kernel panic', 'driver issues'],
                'detection': lambda diff: diff.get('kernel_changed', False)
            },
            'bootloader': {
                'risk': 'critical',
                'symptoms': ['no boot', 'grub error', 'systemd-boot failure'],
                'detection': lambda diff: any('boot' in pkg.lower() for pkg in diff.get('packages_updated', []))
            },
            'graphics_driver': {
                'risk': 'high',
                'symptoms': ['black screen', 'no display', 'X11/Wayland crash'],
                'detection': lambda diff: any(gpu in pkg for gpu in ['nvidia', 'amd', 'intel-graphics'] 
                                             for pkg in diff.get('packages_updated', []) + diff.get('packages_added', []))
            },
            'networking': {
                'risk': 'medium',
                'symptoms': ['no network', 'wifi broken', 'ethernet down'],
                'detection': lambda diff: any('network' in pkg.lower() or 'wifi' in pkg.lower() 
                                             for pkg in diff.get('packages_updated', []))
            },
            'audio': {
                'risk': 'low',
                'symptoms': ['no sound', 'pulseaudio crash', 'pipewire failure'],
                'detection': lambda diff: any(audio in pkg for audio in ['pulse', 'pipewire', 'alsa']
                                             for pkg in diff.get('packages_updated', []))
            },
            'desktop_environment': {
                'risk': 'medium',
                'symptoms': ['desktop crash', 'login loop', 'session failure'],
                'detection': lambda diff: any(de in pkg for de in ['gnome', 'kde', 'plasma', 'xfce']
                                             for pkg in diff.get('packages_updated', []))
            }
        }
        
        # Safe change patterns (low risk)
        self.safe_patterns = [
            'firefox', 'chromium', 'vim', 'emacs', 'git', 'htop', 'tree',
            'curl', 'wget', 'zip', 'unzip', 'man', 'documentation'
        ]
    
    def analyze_system_failure(self, symptoms: Optional[str] = None) -> RollbackAnalysis:
        """
        Analyze system failure and recommend safe rollback
        
        Args:
            symptoms: Optional description of the problem
        
        Returns:
            RollbackAnalysis with recommended generation
        """
        try:
            # Get system state
            state = self.analyzer.get_system_state()
            current_gen = state.current_generation
            
            # List recent generations
            generations = self.analyzer.list_generations(limit=20)
            
            if not generations:
                return self._create_fallback_analysis(current_gen, "No generation history available")
            
            # Analyze recent changes
            breaking_changes = []
            safe_generation = None
            alternatives = []
            
            # Check each previous generation
            for i, gen in enumerate(generations[1:], 1):  # Skip current
                if gen.number >= current_gen:
                    continue
                    
                # Get diff between this generation and current
                diff = self.analyzer.get_generation_diff(gen.number, current_gen)
                
                # Identify breaking changes
                gen_breaking_changes = self._identify_breaking_changes(diff)
                
                if not gen_breaking_changes:
                    # This generation had no breaking changes - it's safe!
                    safe_generation = gen.number
                    reason = f"Last stable generation before breaking changes"
                    break
                elif len(gen_breaking_changes) < len(breaking_changes):
                    # Fewer breaking changes - add as alternative
                    alternatives.append((
                        gen.number,
                        f"Fewer issues ({len(gen_breaking_changes)} vs {len(breaking_changes)})"
                    ))
                
                breaking_changes = gen_breaking_changes
            
            # If no safe generation found, use the oldest recent one
            if safe_generation is None:
                if len(generations) > 1:
                    safe_generation = generations[-1].number
                    reason = "Oldest available generation (likely stable)"
                else:
                    safe_generation = current_gen - 1
                    reason = "Previous generation (rollback attempt)"
            
            # Determine risk level
            risk_level = self._assess_risk_level(breaking_changes)
            
            # Generate rollback command
            rollback_cmd = f"sudo nixos-rebuild switch --rollback-to {safe_generation}"
            
            # Add symptom-based analysis if provided
            if symptoms:
                symptom_analysis = self._analyze_symptoms(symptoms, breaking_changes)
                if symptom_analysis:
                    breaking_changes.insert(0, f"Symptom match: {symptom_analysis}")
            
            return RollbackAnalysis(
                current_generation=current_gen,
                recommended_generation=safe_generation,
                confidence=0.85 if breaking_changes else 0.95,
                reason=reason,
                changes_detected=breaking_changes[:5],  # Top 5 issues
                risk_level=risk_level,
                rollback_command=rollback_cmd,
                alternative_generations=alternatives[:3]  # Top 3 alternatives
            )
            
        except Exception as e:
            logger.error(f"Rollback analysis failed: {e}")
            return self._create_fallback_analysis(
                self.analyzer._get_current_generation(),
                f"Analysis error: {str(e)}"
            )
    
    def analyze_generation_safety(self, generation: int) -> Dict[str, Any]:
        """
        Analyze the safety of a specific generation
        
        Returns:
            Dictionary with safety assessment
        """
        try:
            current_gen = self.analyzer._get_current_generation()
            
            # Get diff from generation to current
            diff = self.analyzer.get_generation_diff(generation, current_gen)
            
            # Identify changes
            breaking_changes = self._identify_breaking_changes(diff)
            safe_changes = self._identify_safe_changes(diff)
            
            # Calculate safety score
            safety_score = self._calculate_safety_score(breaking_changes, safe_changes)
            
            return {
                'generation': generation,
                'safety_score': safety_score,
                'safe_to_rollback': safety_score > 0.7,
                'breaking_changes': breaking_changes,
                'safe_changes': safe_changes,
                'recommendation': self._get_safety_recommendation(safety_score)
            }
            
        except Exception as e:
            logger.error(f"Generation safety analysis failed: {e}")
            return {
                'generation': generation,
                'safety_score': 0.5,
                'safe_to_rollback': False,
                'error': str(e)
            }
    
    def find_last_working_generation(self, failing_component: str) -> Optional[int]:
        """
        Find the last generation where a specific component was working
        
        Args:
            failing_component: Name of the failing component (e.g., 'nvidia', 'audio')
        
        Returns:
            Generation number or None
        """
        try:
            current_gen = self.analyzer._get_current_generation()
            generations = self.analyzer.list_generations(limit=50)
            
            for gen in generations:
                if gen.number >= current_gen:
                    continue
                
                # Check if component changed after this generation
                diff = self.analyzer.get_generation_diff(gen.number, current_gen)
                
                # Check if the component was modified
                component_changed = any(
                    failing_component.lower() in pkg.lower()
                    for pkg in diff.get('packages_updated', []) + 
                              diff.get('packages_added', []) + 
                              diff.get('packages_removed', [])
                )
                
                if not component_changed:
                    # Component hasn't changed since this generation
                    return gen.number
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find working generation for {failing_component}: {e}")
            return None
    
    def get_generation_summary(self, generation: int) -> str:
        """Get human-readable summary of what changed in a generation"""
        try:
            current_gen = self.analyzer._get_current_generation()
            
            if generation == current_gen:
                return "Current generation (no changes)"
            
            # Get diff
            diff = self.analyzer.get_generation_diff(generation, current_gen)
            
            summary_parts = []
            
            # Summarize changes
            if diff['packages_added']:
                summary_parts.append(f"Added {len(diff['packages_added'])} packages")
            if diff['packages_removed']:
                summary_parts.append(f"Removed {len(diff['packages_removed'])} packages")
            if diff['packages_updated']:
                summary_parts.append(f"Updated {len(diff['packages_updated'])} packages")
            if diff['kernel_changed']:
                summary_parts.append("Kernel changed")
            if diff['services_changed']:
                summary_parts.append(f"Services changed: {', '.join(diff['services_changed'][:3])}")
            
            return " | ".join(summary_parts) if summary_parts else "No significant changes"
            
        except Exception as e:
            return f"Unable to analyze generation: {e}"
    
    def _identify_breaking_changes(self, diff: Dict[str, Any]) -> List[str]:
        """Identify potentially breaking changes in a diff"""
        breaking = []
        
        for category, pattern in self.breaking_patterns.items():
            if pattern['detection'](diff):
                breaking.append(f"{category} ({pattern['risk']} risk)")
        
        return breaking
    
    def _identify_safe_changes(self, diff: Dict[str, Any]) -> List[str]:
        """Identify safe changes in a diff"""
        safe = []
        
        for pkg in diff.get('packages_updated', []) + diff.get('packages_added', []):
            if any(safe_pkg in pkg.lower() for safe_pkg in self.safe_patterns):
                safe.append(pkg)
        
        return safe
    
    def _calculate_safety_score(self, breaking: List[str], safe: List[str]) -> float:
        """Calculate safety score (0.0 to 1.0)"""
        if not breaking and not safe:
            return 1.0  # No changes = safe
        
        # Weight breaking changes heavily
        breaking_weight = len(breaking) * 3
        safe_weight = len(safe)
        
        if breaking_weight == 0:
            return 1.0
        
        score = safe_weight / (safe_weight + breaking_weight)
        return min(1.0, max(0.0, score))
    
    def _assess_risk_level(self, breaking_changes: List[str]) -> str:
        """Assess overall risk level"""
        if not breaking_changes:
            return 'low'
        
        # Check for critical risks
        if any('critical' in change.lower() for change in breaking_changes):
            return 'critical'
        if any('high' in change.lower() for change in breaking_changes):
            return 'high'
        if len(breaking_changes) > 3:
            return 'high'
        if len(breaking_changes) > 1:
            return 'medium'
        
        return 'low'
    
    def _analyze_symptoms(self, symptoms: str, breaking_changes: List[str]) -> Optional[str]:
        """Analyze symptoms to identify likely cause"""
        symptoms_lower = symptoms.lower()
        
        # Match symptoms to patterns
        for category, pattern in self.breaking_patterns.items():
            for symptom in pattern['symptoms']:
                if symptom in symptoms_lower:
                    return f"{category} issue detected from symptoms"
        
        return None
    
    def _get_safety_recommendation(self, score: float) -> str:
        """Get recommendation based on safety score"""
        if score > 0.9:
            return "Very safe - minimal changes"
        elif score > 0.7:
            return "Safe - mostly harmless changes"
        elif score > 0.5:
            return "Moderate risk - review changes carefully"
        elif score > 0.3:
            return "High risk - significant changes detected"
        else:
            return "Very high risk - many breaking changes"
    
    def _create_fallback_analysis(self, current_gen: int, reason: str) -> RollbackAnalysis:
        """Create fallback analysis when normal analysis fails"""
        return RollbackAnalysis(
            current_generation=current_gen,
            recommended_generation=max(0, current_gen - 1),
            confidence=0.3,
            reason=reason,
            changes_detected=["Unable to analyze changes"],
            risk_level='unknown',
            rollback_command=f"sudo nixos-rebuild switch --rollback",
            alternative_generations=[]
        )