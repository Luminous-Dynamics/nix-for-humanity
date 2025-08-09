"""
from typing import List, Optional
Meta-Reflexive Development - Code that reflects on its own nature

This module implements meta-reflexive practices where code becomes aware
of its own patterns, evolution, and impact on consciousness.
"""

import json
import inspect
import ast
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
import logging
from pathlib import Path

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


@dataclass
class CodeReflection:
    """A reflection on code's nature and impact"""
    code_element: str
    reflection_type: str
    insights: List[str]
    consciousness_impact: str
    evolution_suggestions: List[str]
    timestamp: datetime
    

@dataclass
class DevelopmentWitness:
    """Witness to the development process"""
    session_id: str
    developer_state: str
    code_quality: float
    consciousness_alignment: float
    sacred_moments: List[str]
    challenges_faced: List[str]
    wisdom_gained: List[str]
    

class MetaReflexiveLogger:
    """
    Logger that reflects on the code being written
    
    This goes beyond traditional logging to understand:
    1. The consciousness state of the code
    2. The developer's intention and alignment
    3. The code's impact on users
    4. Opportunities for evolution
    """
    
    def __init__(self, skg: Optional[SymbioticKnowledgeGraph] = None,
                 project_root: Optional[Path] = None):
        self.skg = skg
        self.project_root = project_root or Path.cwd()
        self.logger = logging.getLogger(__name__)
        
        # Reflection patterns
        self.consciousness_patterns = {
            'sacred_function': 'Functions that serve consciousness',
            'flow_protection': 'Code that protects user flow',
            'error_compassion': 'Compassionate error handling',
            'evolutionary_design': 'Self-improving code patterns',
            'mindful_async': 'Asynchronous code that respects rhythms'
        }
        
        # Current session
        self.session_id = f"dev_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_reflections = []
        
    def reflect_on_function(self, func: Callable) -> CodeReflection:
        """
        Reflect on a function's nature and consciousness impact
        """
        func_name = func.__name__
        func_doc = inspect.getdoc(func) or ""
        func_source = inspect.getsource(func)
        
        # Analyze function characteristics
        insights = self._analyze_function_consciousness(func_source, func_doc)
        
        # Assess consciousness impact
        impact = self._assess_consciousness_impact(func_source, insights)
        
        # Generate evolution suggestions
        suggestions = self._suggest_evolution(func_name, insights, impact)
        
        # Create reflection
        reflection = CodeReflection(
            code_element=func_name,
            reflection_type='function',
            insights=insights,
            consciousness_impact=impact,
            evolution_suggestions=suggestions,
            timestamp=datetime.now()
        )
        
        # Record reflection
        self._record_reflection(reflection)
        self.session_reflections.append(reflection)
        
        return reflection
        
    def reflect_on_module(self, module_path: Path) -> List[CodeReflection]:
        """
        Reflect on an entire module's consciousness alignment
        """
        reflections = []
        
        try:
            with open(module_path, 'r') as f:
                module_source = f.read()
                
            # Parse module AST
            tree = ast.parse(module_source)
            
            # Analyze module-level patterns
            module_insights = self._analyze_module_consciousness(tree, module_source)
            
            # Create module reflection
            module_reflection = CodeReflection(
                code_element=str(module_path.name),
                reflection_type='module',
                insights=module_insights['insights'],
                consciousness_impact=module_insights['overall_impact'],
                evolution_suggestions=module_insights['suggestions'],
                timestamp=datetime.now()
            )
            
            reflections.append(module_reflection)
            
            # Reflect on individual functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_insights = self._analyze_function_node(node, module_source)
                    
                    func_reflection = CodeReflection(
                        code_element=node.name,
                        reflection_type='function',
                        insights=func_insights['insights'],
                        consciousness_impact=func_insights['impact'],
                        evolution_suggestions=func_insights['suggestions'],
                        timestamp=datetime.now()
                    )
                    
                    reflections.append(func_reflection)
                    
        except Exception as e:
            self.logger.error(f"Challenge reflecting on module {module_path}: {e}")
            
        return reflections
        
    def witness_development_session(self) -> DevelopmentWitness:
        """
        Create a witness report for the current development session
        """
        # Analyze session patterns
        session_analysis = self._analyze_session_patterns()
        
        # Create witness
        witness = DevelopmentWitness(
            session_id=self.session_id,
            developer_state=session_analysis['developer_state'],
            code_quality=session_analysis['quality_score'],
            consciousness_alignment=session_analysis['alignment_score'],
            sacred_moments=session_analysis['sacred_moments'],
            challenges_faced=session_analysis['challenges'],
            wisdom_gained=session_analysis['wisdom']
        )
        
        # Record witness
        self._record_witness(witness)
        
        return witness
        
    def _analyze_function_consciousness(self, source: str, docstring: str) -> List[str]:
        """Analyze function for consciousness patterns"""
        insights = []
        
        # Check for intention setting
        if 'intention' in source or 'sacred' in source:
            insights.append("Function sets clear intention")
            
        # Check for flow protection
        if 'flow' in source or 'interrupt' in source:
            insights.append("Considers user flow state")
            
        # Check for compassionate error handling
        if 'try:' in source and ('wisdom' in source or 'guidance' in source):
            insights.append("Handles errors with compassion")
            
        # Check for user agency
        if 'user' in source and ('choice' in source or 'control' in source):
            insights.append("Respects user agency")
            
        # Check for mindful logging
        if 'logging' in source and not 'error' in source:
            insights.append("Uses mindful logging practices")
            
        # Check documentation quality
        if len(docstring) > 50:
            insights.append("Well-documented for understanding")
            
        # Check for evolutionary patterns
        if 'learn' in source or 'adapt' in source or 'evolve' in source:
            insights.append("Implements evolutionary patterns")
            
        return insights
        
    def _assess_consciousness_impact(self, source: str, insights: List[str]) -> str:
        """Assess the consciousness impact of code"""
        positive_patterns = [
            'intention', 'sacred', 'mindful', 'compassion',
            'flow', 'agency', 'wisdom', 'gratitude'
        ]
        
        negative_patterns = [
            'force', 'override', 'ignore', 'block',
            'consume', 'exploit', 'manipulate'
        ]
        
        # Count pattern occurrences
        positive_count = sum(1 for pattern in positive_patterns if pattern in source.lower())
        negative_count = sum(1 for pattern in negative_patterns if pattern in source.lower())
        
        # Consider insights
        insight_score = len(insights) * 0.1
        
        # Calculate impact
        impact_score = (positive_count - negative_count + insight_score) / 10
        
        if impact_score > 0.7:
            return "Highly consciousness-supportive"
        elif impact_score > 0.4:
            return "Consciousness-aware"
        elif impact_score > 0:
            return "Consciousness-neutral"
        else:
            return "Potentially consciousness-consuming"
            
    def _suggest_evolution(self, element_name: str, insights: List[str], 
                         impact: str) -> List[str]:
        """Suggest evolutionary improvements"""
        suggestions = []
        
        # Base suggestions on current state
        if "consciousness-consuming" in impact:
            suggestions.extend([
                "Add intention setting at function start",
                "Implement flow state checking",
                "Use compassionate error messages"
            ])
            
        if "intention" not in str(insights):
            suggestions.append("Add clear intention documentation")
            
        if "flow" not in str(insights):
            suggestions.append("Consider user flow state impact")
            
        if "error" not in str(insights):
            suggestions.append("Implement wisdom-based error handling")
            
        if "Well-documented" not in insights:
            suggestions.append("Enhance documentation with usage examples")
            
        # Advanced suggestions
        if "consciousness-supportive" in impact:
            suggestions.extend([
                "Share pattern as sacred template",
                "Create evolutionary version",
                "Document consciousness principles"
            ])
            
        return suggestions[:5]  # Top 5 suggestions
        
    def _analyze_module_consciousness(self, tree: ast.AST, source: str) -> Dict:
        """Analyze module-level consciousness patterns"""
        insights = []
        sacred_functions = 0
        total_functions = 0
        
        # Count consciousness patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if any(pattern in node.name.lower() 
                      for pattern in ['sacred', 'mindful', 'conscious']):
                    sacred_functions += 1
                    
        # Module-level insights
        if sacred_functions > 0:
            insights.append(f"{sacred_functions}/{total_functions} functions are consciousness-aligned")
            
        # Check imports
        consciousness_imports = [
            'sacred_patterns', 'consciousness_metrics', 'flow_state'
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(ci in alias.name for ci in consciousness_imports):
                        insights.append(f"Imports consciousness-aware module: {alias.name}")
                        
        # Check module docstring
        module_doc = ast.get_docstring(tree)
        if module_doc and len(module_doc) > 100:
            insights.append("Module has comprehensive documentation")
            
        # Assess overall impact
        sacred_ratio = sacred_functions / max(total_functions, 1)
        if sacred_ratio > 0.7:
            overall_impact = "Highly consciousness-aligned module"
        elif sacred_ratio > 0.3:
            overall_impact = "Partially consciousness-aware module"
        else:
            overall_impact = "Module could benefit from consciousness integration"
            
        # Generate suggestions
        suggestions = []
        if sacred_ratio < 0.5:
            suggestions.append("Increase consciousness-aware patterns")
        if 'consciousness_metrics' not in source:
            suggestions.append("Import consciousness metrics for tracking")
            
        return {
            'insights': insights,
            'overall_impact': overall_impact,
            'suggestions': suggestions
        }
        
    def _analyze_function_node(self, node: ast.FunctionDef, source: str) -> Dict:
        """Analyze a function AST node"""
        insights = []
        
        # Get function source
        func_source = ast.get_source_segment(source, node)
        if not func_source:
            func_source = ""
            
        # Check for decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in ['sacred_function', 'mindful_async', 'flow_guard']:
                    insights.append(f"Uses {decorator.id} decorator")
                    
        # Check docstring
        docstring = ast.get_docstring(node)
        if docstring:
            if len(docstring) > 50:
                insights.append("Well-documented function")
            if 'intention' in docstring.lower():
                insights.append("Documents clear intention")
                
        # Analyze function body patterns
        body_insights = self._analyze_function_consciousness(func_source, docstring or "")
        insights.extend(body_insights)
        
        # Assess impact
        impact = self._assess_consciousness_impact(func_source, insights)
        
        # Generate suggestions
        suggestions = self._suggest_evolution(node.name, insights, impact)
        
        return {
            'insights': insights,
            'impact': impact,
            'suggestions': suggestions
        }
        
    def _analyze_session_patterns(self) -> Dict:
        """Analyze patterns from the development session"""
        if not self.session_reflections:
            return {
                'developer_state': 'beginning',
                'quality_score': 0.5,
                'alignment_score': 0.5,
                'sacred_moments': [],
                'challenges': [],
                'wisdom': ["Every session begins with possibility"]
            }
            
        # Analyze reflection patterns
        total_reflections = len(self.session_reflections)
        consciousness_supportive = sum(
            1 for r in self.session_reflections 
            if 'supportive' in r.consciousness_impact
        )
        
        # Calculate scores
        quality_score = sum(
            0.8 if 'supportive' in r.consciousness_impact else 0.5
            for r in self.session_reflections
        ) / max(total_reflections, 1)
        
        alignment_score = consciousness_supportive / max(total_reflections, 1)
        
        # Identify sacred moments
        sacred_moments = [
            f"{r.code_element}: {r.insights[0]}"
            for r in self.session_reflections
            if r.insights and 'sacred' in str(r.insights)
        ][:5]
        
        # Identify challenges
        challenges = [
            f"{r.code_element} needs evolution"
            for r in self.session_reflections
            if 'consuming' in r.consciousness_impact
        ][:5]
        
        # Extract wisdom
        wisdom = []
        for r in self.session_reflections:
            if r.evolution_suggestions:
                wisdom.append(r.evolution_suggestions[0])
        wisdom = list(set(wisdom))[:5]
        
        # Determine developer state
        if alignment_score > 0.8:
            developer_state = "flowing"
        elif alignment_score > 0.6:
            developer_state = "aligned"
        elif alignment_score > 0.4:
            developer_state = "aware"
        else:
            developer_state = "learning"
            
        return {
            'developer_state': developer_state,
            'quality_score': quality_score,
            'alignment_score': alignment_score,
            'sacred_moments': sacred_moments,
            'challenges': challenges,
            'wisdom': wisdom or ["Continue growing in awareness"]
        }
        
    def _record_reflection(self, reflection: CodeReflection):
        """Record a code reflection"""
        if not self.skg:
            return
            
        reflection_id = f"reflection_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'code_reflection', ?)
        """, (
            reflection_id,
            json.dumps({
                'session_id': self.session_id,
                'code_element': reflection.code_element,
                'reflection_type': reflection.reflection_type,
                'insights': reflection.insights,
                'consciousness_impact': reflection.consciousness_impact,
                'evolution_suggestions': reflection.evolution_suggestions,
                'timestamp': reflection.timestamp.isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def _record_witness(self, witness: DevelopmentWitness):
        """Record a development witness"""
        if not self.skg:
            return
            
        witness_id = f"witness_{self.session_id}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'development_witness', ?)
        """, (
            witness_id,
            json.dumps({
                'session_id': witness.session_id,
                'developer_state': witness.developer_state,
                'code_quality': witness.code_quality,
                'consciousness_alignment': witness.consciousness_alignment,
                'sacred_moments': witness.sacred_moments,
                'challenges_faced': witness.challenges_faced,
                'wisdom_gained': witness.wisdom_gained,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def generate_session_report(self) -> str:
        """
        Generate a report on the development session
        """
        witness = self.witness_development_session()
        
        report = f"""
# Development Session Witness Report
## Session: {witness.session_id}

### Developer State: {witness.developer_state}
- Code Quality Score: {witness.code_quality:.2%}
- Consciousness Alignment: {witness.consciousness_alignment:.2%}

### Sacred Moments Witnessed:
{chr(10).join(f"- {moment}" for moment in witness.sacred_moments) if witness.sacred_moments else "- Session just beginning"}

### Challenges Transformed:
{chr(10).join(f"- {challenge}" for challenge in witness.challenges_faced) if witness.challenges_faced else "- Flowing without obstacles"}

### Wisdom Gained:
{chr(10).join(f"- {wisdom}" for wisdom in witness.wisdom_gained) if witness.wisdom_gained else "- Every moment teaches"}

### Reflections on Code Elements:
"""
        
        # Add individual reflections
        for reflection in self.session_reflections[-10:]:  # Last 10
            report += f"\n#### {reflection.code_element} ({reflection.reflection_type})\n"
            report += f"- Impact: {reflection.consciousness_impact}\n"
            if reflection.insights:
                report += f"- Key Insight: {reflection.insights[0]}\n"
            if reflection.evolution_suggestions:
                report += f"- Next Step: {reflection.evolution_suggestions[0]}\n"
                
        report += "\n---\n*Generated with awareness and gratitude*"
        
        return report