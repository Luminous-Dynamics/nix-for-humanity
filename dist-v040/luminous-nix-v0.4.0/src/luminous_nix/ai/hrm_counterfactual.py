"""
HRM with Counterfactual Reasoning
"What if" analysis and alternative solution exploration
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import itertools

@dataclass
class Counterfactual:
    """A counterfactual scenario"""
    original_query: str
    modified_query: str
    modification_type: str
    expected_outcome: str
    actual_outcome: Optional[str] = None
    impact_score: float = 0.0

@dataclass 
class CausalPath:
    """Causal reasoning path"""
    steps: List[str]
    dependencies: Dict[str, List[str]]
    failure_points: List[str]
    success_probability: float

class CounterfactualHRM:
    """
    HRM with counterfactual reasoning capabilities
    Answers "what if" questions and explores alternatives
    """
    
    def __init__(self):
        self.causal_graph = self._build_causal_graph()
        self.intervention_history = []
        
    def what_if(self, query: str, intervention: str) -> Dict[str, Any]:
        """
        Answer "what if" questions
        e.g., "What if I use flakes instead of channels?"
        """
        # Parse intervention
        intervention_type = self._classify_intervention(intervention)
        
        # Generate counterfactual world
        counterfactual_world = self._create_counterfactual(
            query, intervention, intervention_type
        )
        
        # Simulate outcomes
        outcomes = self._simulate_outcomes(counterfactual_world)
        
        # Compare with factual world
        comparison = self._compare_worlds(query, counterfactual_world)
        
        return {
            "intervention": intervention,
            "likely_outcomes": outcomes,
            "comparison": comparison,
            "recommendation": self._generate_recommendation(outcomes, comparison),
            "confidence": self._estimate_confidence(counterfactual_world)
        }
    
    def why_not(self, query: str, failed_solution: str) -> Dict[str, Any]:
        """
        Explain why a solution didn't work and suggest alternatives
        """
        # Identify failure points
        failure_analysis = self._analyze_failure(query, failed_solution)
        
        # Generate alternative paths
        alternatives = self._generate_alternatives(query, failure_analysis)
        
        # Rank by likelihood of success
        ranked_alternatives = self._rank_alternatives(alternatives)
        
        return {
            "failure_reason": failure_analysis["root_cause"],
            "failure_points": failure_analysis["points"],
            "alternatives": ranked_alternatives,
            "best_alternative": ranked_alternatives[0] if ranked_alternatives else None,
            "learned_constraint": self._extract_constraint(failure_analysis)
        }
    
    def explore_solution_space(self, query: str) -> List[Dict[str, Any]]:
        """
        Explore multiple solution paths with trade-offs
        """
        # Generate solution space
        solutions = []
        
        # Different dimensions to explore
        dimensions = {
            "speed": ["quick", "thorough"],
            "persistence": ["temporary", "permanent"],
            "scope": ["user", "system"],
            "method": ["imperative", "declarative"],
            "isolation": ["global", "isolated"]
        }
        
        # Generate combinations
        for combo in itertools.product(*dimensions.values()):
            solution = self._generate_solution_for_dimensions(
                query, dict(zip(dimensions.keys(), combo))
            )
            solutions.append(solution)
        
        # Prune infeasible solutions
        feasible = [s for s in solutions if s["feasible"]]
        
        # Add Pareto frontier analysis
        pareto_optimal = self._find_pareto_optimal(feasible)
        
        return pareto_optimal
    
    def _build_causal_graph(self) -> Dict[str, Any]:
        """Build causal relationships in NixOS"""
        return {
            "package_install": {
                "causes": ["system_rebuild", "profile_update"],
                "caused_by": ["user_request", "dependency"],
                "blocks": ["conflicting_packages"],
                "enables": ["package_availability"]
            },
            "system_rebuild": {
                "causes": ["configuration_activation", "generation_create"],
                "caused_by": ["configuration_change", "channel_update"],
                "blocks": ["running_services"],
                "enables": ["new_features"]
            },
            "dependency_conflict": {
                "causes": ["install_failure", "build_failure"],
                "caused_by": ["version_mismatch", "multiple_versions"],
                "blocks": ["package_install"],
                "enables": ["override_necessity"]
            }
        }
    
    def _create_counterfactual(self, query: str, intervention: str, 
                               intervention_type: str) -> Dict[str, Any]:
        """Create counterfactual world with intervention"""
        world = {
            "query": query,
            "intervention": intervention,
            "type": intervention_type,
            "assumptions": [],
            "constraints": []
        }
        
        # Modify world based on intervention
        if intervention_type == "method_change":
            world["assumptions"].append("Different installation method available")
            world["constraints"].append("May require additional setup")
        elif intervention_type == "version_change":
            world["assumptions"].append("Different version is compatible")
            world["constraints"].append("May have different features")
        elif intervention_type == "environment_change":
            world["assumptions"].append("Environment modification is acceptable")
            world["constraints"].append("May affect other packages")
        
        return world
    
    def _simulate_outcomes(self, counterfactual_world: Dict) -> List[Dict]:
        """Simulate possible outcomes of counterfactual"""
        outcomes = []
        
        # Best case
        outcomes.append({
            "scenario": "best_case",
            "probability": 0.3,
            "result": "Solution works perfectly",
            "side_effects": []
        })
        
        # Expected case
        outcomes.append({
            "scenario": "expected",
            "probability": 0.5,
            "result": "Solution works with minor adjustments",
            "side_effects": ["Additional configuration needed"]
        })
        
        # Worst case
        outcomes.append({
            "scenario": "worst_case",
            "probability": 0.2,
            "result": "Solution causes new problems",
            "side_effects": ["Breaks existing functionality", "Requires rollback"]
        })
        
        return outcomes
    
    def _analyze_failure(self, query: str, failed_solution: str) -> Dict:
        """Analyze why a solution failed"""
        # Pattern matching for common failures
        if "collision" in failed_solution.lower():
            return {
                "root_cause": "Package collision between dependencies",
                "points": ["Multiple packages provide same file", 
                          "No priority set"],
                "type": "dependency_conflict"
            }
        elif "attribute" in failed_solution.lower():
            return {
                "root_cause": "Package not found in current channel",
                "points": ["Package name mismatch", 
                          "Channel not updated"],
                "type": "missing_package"
            }
        else:
            return {
                "root_cause": "Unknown failure",
                "points": ["Investigate logs"],
                "type": "unknown"
            }
    
    def _generate_alternatives(self, query: str, 
                              failure_analysis: Dict) -> List[CausalPath]:
        """Generate alternative solution paths"""
        alternatives = []
        
        if failure_analysis["type"] == "dependency_conflict":
            alternatives.append(CausalPath(
                steps=["Use overlay to override", "Set package priority"],
                dependencies={"overlay": ["nix knowledge"]},
                failure_points=["Complex overlay syntax"],
                success_probability=0.8
            ))
            alternatives.append(CausalPath(
                steps=["Use separate nix-shell", "Isolate dependencies"],
                dependencies={"nix-shell": ["shell.nix file"]},
                failure_points=["Not persistent"],
                success_probability=0.9
            ))
        
        return alternatives
    
    def _rank_alternatives(self, alternatives: List[CausalPath]) -> List[Dict]:
        """Rank alternatives by multiple criteria"""
        ranked = []
        for alt in alternatives:
            score = (
                alt.success_probability * 0.5 +
                (1.0 / (len(alt.failure_points) + 1)) * 0.3 +
                (1.0 / (len(alt.steps) + 1)) * 0.2
            )
            ranked.append({
                "path": alt,
                "score": score,
                "recommendation": alt.steps[0] if alt.steps else "No action"
            })
        
        return sorted(ranked, key=lambda x: x["score"], reverse=True)
    
    def _find_pareto_optimal(self, solutions: List[Dict]) -> List[Dict]:
        """Find Pareto optimal solutions (no solution is strictly better)"""
        pareto = []
        for s1 in solutions:
            dominated = False
            for s2 in solutions:
                if s1 == s2:
                    continue
                # Check if s2 dominates s1 on all dimensions
                if (s2.get("speed", 0) >= s1.get("speed", 0) and
                    s2.get("reliability", 0) >= s1.get("reliability", 0) and
                    s2.get("simplicity", 0) >= s1.get("simplicity", 0) and
                    any([s2.get("speed", 0) > s1.get("speed", 0),
                         s2.get("reliability", 0) > s1.get("reliability", 0),
                         s2.get("simplicity", 0) > s1.get("simplicity", 0)])):
                    dominated = True
                    break
            if not dominated:
                pareto.append(s1)
        return pareto
    
    def _generate_solution_for_dimensions(self, query: str, 
                                         dimensions: Dict) -> Dict:
        """Generate solution based on dimension combination"""
        solution = {
            "dimensions": dimensions,
            "feasible": True,
            "speed": 0,
            "reliability": 0,
            "simplicity": 0
        }
        
        # Quick + temporary = nix-shell
        if dimensions["speed"] == "quick" and dimensions["persistence"] == "temporary":
            solution["command"] = f"nix-shell -p package"
            solution["speed"] = 0.9
            solution["reliability"] = 0.7
            solution["simplicity"] = 0.9
        
        # Thorough + permanent = configuration.nix
        elif dimensions["speed"] == "thorough" and dimensions["persistence"] == "permanent":
            solution["command"] = f"Add to configuration.nix"
            solution["speed"] = 0.3
            solution["reliability"] = 0.95
            solution["simplicity"] = 0.6
        
        # Other combinations...
        
        return solution
    
    def _classify_intervention(self, intervention: str) -> str:
        """Classify type of intervention"""
        if any(word in intervention.lower() for word in ["flake", "channel", "overlay"]):
            return "method_change"
        elif any(word in intervention.lower() for word in ["version", "update", "rollback"]):
            return "version_change"
        else:
            return "environment_change"
    
    def _compare_worlds(self, query: str, counterfactual: Dict) -> Dict:
        """Compare factual vs counterfactual worlds"""
        return {
            "complexity_change": "+20%" if "flake" in str(counterfactual) else "-10%",
            "reliability_change": "+15%" if "declarative" in str(counterfactual) else "0%",
            "flexibility_change": "+30%" if "overlay" in str(counterfactual) else "-5%"
        }
    
    def _generate_recommendation(self, outcomes: List, comparison: Dict) -> str:
        """Generate recommendation based on analysis"""
        expected = next((o for o in outcomes if o["scenario"] == "expected"), None)
        if expected and expected["probability"] > 0.6:
            return f"Recommended: {expected['result']}"
        return "Not recommended: High risk of negative outcomes"
    
    def _estimate_confidence(self, world: Dict) -> float:
        """Estimate confidence in counterfactual analysis"""
        base = 0.7
        # Reduce confidence for each assumption
        confidence = base - (len(world["assumptions"]) * 0.1)
        # Reduce for constraints
        confidence -= len(world["constraints"]) * 0.05
        return max(0.3, min(1.0, confidence))
    
    def _extract_constraint(self, failure_analysis: Dict) -> str:
        """Extract learned constraint from failure"""
        if failure_analysis["type"] == "dependency_conflict":
            return "Packages X and Y cannot coexist without override"
        elif failure_analysis["type"] == "missing_package":
            return "Package requires specific channel or overlay"
        return "Unknown constraint"


def demonstrate_counterfactual():
    """Demonstrate counterfactual reasoning"""
    print("🤔 HRM with Counterfactual Reasoning Demo")
    print("=" * 60)
    
    hrm = CounterfactualHRM()
    
    # Test 1: What-if analysis
    print("\n📊 What-If Analysis:")
    print("-" * 60)
    
    result = hrm.what_if(
        "install tensorflow",
        "what if I use a flake instead of channels"
    )
    
    print("Query: Install tensorflow")
    print("Intervention: Use flakes instead of channels")
    print(f"Recommendation: {result['recommendation']}")
    print("Likely outcomes:")
    for outcome in result["likely_outcomes"]:
        print(f"  {outcome['scenario']}: {outcome['result']} (p={outcome['probability']})")
    
    # Test 2: Why-not analysis
    print("\n❓ Why-Not Analysis:")
    print("-" * 60)
    
    result = hrm.why_not(
        "install python packages",
        "error: collision between python3.8 and python3.9"
    )
    
    print("Failed solution: Direct install causing collision")
    print(f"Root cause: {result['failure_reason']}")
    print("Best alternative:")
    if result["best_alternative"]:
        print(f"  {result['best_alternative']['recommendation']}")
        print(f"  Success probability: {result['best_alternative']['path'].success_probability:.1%}")
    
    # Test 3: Solution space exploration
    print("\n🌐 Solution Space Exploration:")
    print("-" * 60)
    
    solutions = hrm.explore_solution_space("install development environment")
    print("Pareto optimal solutions:")
    for sol in solutions[:3]:  # Top 3
        print(f"  Method: {sol.get('dimensions', {})}")
        print(f"    Speed: {sol.get('speed', 0):.1f}, "
              f"Reliability: {sol.get('reliability', 0):.1f}, "
              f"Simplicity: {sol.get('simplicity', 0):.1f}")
    
    print("\n" + "=" * 60)
    print("🔑 Key Insights:")
    print("  • Explores alternative realities")
    print("  • Learns from failures")
    print("  • Provides trade-off analysis")
    print("  • Explains causal relationships")


if __name__ == "__main__":
    demonstrate_counterfactual()