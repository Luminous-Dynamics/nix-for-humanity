#!/usr/bin/env python3
"""
🚀 Automatic Optimization Engine for UI Evolution
Automatically applies optimizations based on patterns and insights
"""

import json
import time
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from pathlib import Path
from enum import Enum
import sys

sys.path.insert(0, str(Path(__file__).parent))

from error_handler import (
    safe_database_operation,
    safe_async_operation,
    get_logger,
    error_collector
)

from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext
from component_synthesis_engine import ComponentDNA, ComponentSynthesizer
from learning_persistence import LearningDatabase
from pattern_analysis_dashboard import PatternAnalyzer, InsightReport
from ab_testing_framework import ABTestingEngine, VariationType
from feedback_collection_system import FeedbackCollector


class OptimizationType(Enum):
    """Types of automatic optimizations"""
    
    PERFORMANCE = "performance"
    UX_IMPROVEMENT = "ux_improvement"
    ERROR_REDUCTION = "error_reduction"
    COMPLEXITY_ADJUSTMENT = "complexity_adjustment"
    LAYOUT_OPTIMIZATION = "layout_optimization"
    COLOR_ADAPTATION = "color_adaptation"
    ACCESSIBILITY = "accessibility"
    WORKFLOW_STREAMLINING = "workflow_streamlining"


@dataclass
class OptimizationRule:
    """Rule for automatic optimization"""
    
    id: str
    name: str
    description: str
    optimization_type: OptimizationType
    
    # Trigger conditions
    trigger_metric: str  # What metric triggers this optimization
    trigger_threshold: float  # Threshold value
    trigger_comparison: str  # less_than, greater_than, equals
    
    # Action to take
    action: str  # What optimization to apply
    parameters: Dict[str, Any]
    
    # Constraints
    min_confidence: float = 0.7  # Minimum confidence to apply
    cooldown_hours: int = 24  # Hours before can apply again
    requires_approval: bool = False
    
    # Tracking
    last_applied: Optional[datetime] = None
    times_applied: int = 0
    success_rate: float = 0.0


@dataclass
class OptimizationResult:
    """Result of an optimization"""
    
    id: str
    rule_id: str
    timestamp: datetime
    
    # What was optimized
    target_type: str  # interface, component, workflow
    target_id: str
    
    # Changes made
    changes_applied: List[Dict[str, Any]]
    rollback_data: Dict[str, Any]  # For reverting if needed
    
    # Impact metrics
    metrics_before: Dict[str, float]
    metrics_after: Optional[Dict[str, float]] = None
    improvement: Optional[float] = None
    
    # Status
    status: str = "applied"  # applied, measuring, successful, reverted
    confidence: float = 0.0


class AutomaticOptimizer:
    """Main automatic optimization engine"""
    
    def __init__(self):
        self.ui_builder = NLInterfaceBuilderV2(use_llm=False)
        self.component_synthesizer = ComponentSynthesizer()
        self.learning_db = LearningDatabase()
        self.pattern_analyzer = PatternAnalyzer()
        self.ab_testing = ABTestingEngine()
        self.feedback_collector = FeedbackCollector()
        
        # Optimization rules
        self.rules: List[OptimizationRule] = []
        self.active_optimizations: Dict[str, OptimizationResult] = {}
        
        # Configuration
        self.auto_apply = True  # Automatically apply optimizations
        self.require_approval = False  # Require human approval
        self.min_data_points = 10  # Minimum data before optimizing
        self.measurement_period_hours = 24  # How long to measure impact
        
        # Initialize rules and database
        self._init_optimization_rules()
        self._init_database()
    
    def _init_optimization_rules(self):
        """Initialize default optimization rules"""
        
        self.rules = [
            # Performance optimizations
            OptimizationRule(
                id="perf_slow_generation",
                name="Reduce Slow Generation Time",
                description="Optimize interfaces that generate slowly",
                optimization_type=OptimizationType.PERFORMANCE,
                trigger_metric="avg_generation_time",
                trigger_threshold=2000,  # 2 seconds
                trigger_comparison="greater_than",
                action="simplify_components",
                parameters={"reduce_by": 0.3},
                min_confidence=0.8
            ),
            
            # UX improvements
            OptimizationRule(
                id="ux_low_satisfaction",
                name="Improve Low Satisfaction Interfaces",
                description="Enhance interfaces with poor user satisfaction",
                optimization_type=OptimizationType.UX_IMPROVEMENT,
                trigger_metric="satisfaction_score",
                trigger_threshold=3.0,  # Out of 5
                trigger_comparison="less_than",
                action="apply_best_practices",
                parameters={"enhance": ["spacing", "clarity", "feedback"]},
                min_confidence=0.7
            ),
            
            # Error reduction
            OptimizationRule(
                id="error_high_rate",
                name="Fix High Error Rate",
                description="Address interfaces with frequent errors",
                optimization_type=OptimizationType.ERROR_REDUCTION,
                trigger_metric="error_rate",
                trigger_threshold=0.1,  # 10% error rate
                trigger_comparison="greater_than",
                action="add_validation",
                parameters={"validate": ["inputs", "actions", "navigation"]},
                min_confidence=0.9
            ),
            
            # Complexity adjustment
            OptimizationRule(
                id="complexity_abandonment",
                name="Simplify Complex Interfaces",
                description="Reduce complexity when users abandon",
                optimization_type=OptimizationType.COMPLEXITY_ADJUSTMENT,
                trigger_metric="abandonment_rate",
                trigger_threshold=0.3,  # 30% abandonment
                trigger_comparison="greater_than",
                action="reduce_complexity",
                parameters={"simplification_level": "moderate"},
                min_confidence=0.75
            ),
            
            # Layout optimization
            OptimizationRule(
                id="layout_inefficient",
                name="Optimize Inefficient Layouts",
                description="Improve layouts with poor task completion",
                optimization_type=OptimizationType.LAYOUT_OPTIMIZATION,
                trigger_metric="task_completion_rate",
                trigger_threshold=0.6,  # 60% completion
                trigger_comparison="less_than",
                action="reorganize_layout",
                parameters={"strategy": "task_focused"},
                min_confidence=0.7
            ),
            
            # Accessibility
            OptimizationRule(
                id="accessibility_issues",
                name="Improve Accessibility",
                description="Enhance accessibility for better inclusion",
                optimization_type=OptimizationType.ACCESSIBILITY,
                trigger_metric="accessibility_score",
                trigger_threshold=0.7,  # WCAG score
                trigger_comparison="less_than",
                action="enhance_accessibility",
                parameters={"improvements": ["contrast", "labels", "navigation"]},
                min_confidence=0.9,
                requires_approval=False  # Always improve accessibility
            ),
            
            # Workflow streamlining
            OptimizationRule(
                id="workflow_inefficient",
                name="Streamline Workflows",
                description="Optimize workflows with too many steps",
                optimization_type=OptimizationType.WORKFLOW_STREAMLINING,
                trigger_metric="avg_steps_to_complete",
                trigger_threshold=5,
                trigger_comparison="greater_than",
                action="consolidate_steps",
                parameters={"target_reduction": 0.3},
                min_confidence=0.8
            )
        ]
    
    def _init_database(self):
        """Initialize optimization storage"""
        
        cursor = self.learning_db.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_rules (
                id TEXT PRIMARY KEY,
                name TEXT,
                optimization_type TEXT,
                last_applied TEXT,
                times_applied INTEGER,
                success_rate REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_results (
                id TEXT PRIMARY KEY,
                rule_id TEXT,
                timestamp TEXT,
                target_type TEXT,
                target_id TEXT,
                changes_applied TEXT,
                metrics_before TEXT,
                metrics_after TEXT,
                improvement REAL,
                status TEXT,
                confidence REAL
            )
        """)
        
        self.learning_db.conn.commit()
    
    @safe_async_operation(default_return=[])
    async def run_optimization_cycle(self):
        """Run a complete optimization cycle"""
        
        logger = get_logger(__name__)
        logger.info("Starting optimization cycle")
        
        try:
            # 1. Analyze current state
            insights = self.pattern_analyzer.generate_insights()
            
            # 2. Check which rules should trigger
            triggered_rules = self._check_triggered_rules(insights)
            
            # 3. Apply optimizations
            results = []
            for rule in triggered_rules:
                if self._can_apply_rule(rule):
                    try:
                        result = await self._apply_optimization(rule)
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.error(f"Failed to apply optimization {rule.id}: {e}")
                        error_collector.add_error(
                            "optimization_error",
                            str(e),
                            {"rule_id": rule.id}
                        )
            
            # 4. Measure impact of previous optimizations
            await self._measure_optimization_impact()
            
            # 5. Revert failed optimizations
            self._check_and_revert_failures()
            
            return results
        except Exception as e:
            logger.exception(f"Optimization cycle failed: {e}")
            error_collector.add_error(
                "optimization_cycle_error",
                str(e),
                {"phase": "complete_cycle"}
            )
            return []
    
    def _check_triggered_rules(self, insights: List[InsightReport]) -> List[OptimizationRule]:
        """Check which optimization rules should trigger"""
        
        triggered = []
        
        for rule in self.rules:
            # Get current metric value
            metric_value = self._get_metric_value(rule.trigger_metric)
            
            if metric_value is None:
                continue
            
            # Check trigger condition
            triggered_condition = False
            if rule.trigger_comparison == "greater_than":
                triggered_condition = metric_value > rule.trigger_threshold
            elif rule.trigger_comparison == "less_than":
                triggered_condition = metric_value < rule.trigger_threshold
            elif rule.trigger_comparison == "equals":
                triggered_condition = abs(metric_value - rule.trigger_threshold) < 0.01
            
            if triggered_condition:
                # Check confidence from insights
                confidence = self._calculate_confidence(rule, insights)
                if confidence >= rule.min_confidence:
                    triggered.append(rule)
        
        return triggered
    
    def _can_apply_rule(self, rule: OptimizationRule) -> bool:
        """Check if a rule can be applied now"""
        
        # Check cooldown
        if rule.last_applied:
            hours_since = (datetime.now() - rule.last_applied).total_seconds() / 3600
            if hours_since < rule.cooldown_hours:
                return False
        
        # Check if requires approval
        if rule.requires_approval and not self.require_approval:
            return self._get_approval(rule)
        
        return True
    
    async def _apply_optimization(self, rule: OptimizationRule) -> Optional[OptimizationResult]:
        """Apply an optimization rule"""
        
        print(f"📈 Applying optimization: {rule.name}")
        
        # Get target for optimization
        target = self._identify_optimization_target(rule)
        if not target:
            return None
        
        # Capture metrics before
        metrics_before = self._capture_current_metrics(target)
        
        # Apply the optimization based on action
        changes = []
        rollback_data = {}
        
        if rule.action == "simplify_components":
            changes, rollback_data = self._simplify_components(
                target, rule.parameters
            )
        elif rule.action == "apply_best_practices":
            changes, rollback_data = self._apply_best_practices(
                target, rule.parameters
            )
        elif rule.action == "add_validation":
            changes, rollback_data = self._add_validation(
                target, rule.parameters
            )
        elif rule.action == "reduce_complexity":
            changes, rollback_data = self._reduce_complexity(
                target, rule.parameters
            )
        elif rule.action == "reorganize_layout":
            changes, rollback_data = self._reorganize_layout(
                target, rule.parameters
            )
        elif rule.action == "enhance_accessibility":
            changes, rollback_data = self._enhance_accessibility(
                target, rule.parameters
            )
        elif rule.action == "consolidate_steps":
            changes, rollback_data = self._consolidate_workflow_steps(
                target, rule.parameters
            )
        
        # Create optimization result
        result = OptimizationResult(
            id=f"opt_{rule.id}_{int(time.time())}",
            rule_id=rule.id,
            timestamp=datetime.now(),
            target_type=target["type"],
            target_id=target["id"],
            changes_applied=changes,
            rollback_data=rollback_data,
            metrics_before=metrics_before,
            status="applied",
            confidence=self._calculate_confidence(rule, [])
        )
        
        # Track the optimization
        self.active_optimizations[result.id] = result
        
        # Update rule tracking
        rule.last_applied = datetime.now()
        rule.times_applied += 1
        
        # Store in database
        self._store_optimization_result(result)
        
        # Create A/B test to validate
        if self.ab_testing:
            self._create_validation_test(rule, target, changes)
        
        return result
    
    def _simplify_components(
        self, target: Dict, parameters: Dict
    ) -> Tuple[List[Dict], Dict]:
        """Simplify interface components"""
        
        changes = []
        rollback = {"original_components": target.get("components", [])}
        
        reduce_by = parameters.get("reduce_by", 0.3)
        
        # Identify non-essential components
        components = target.get("components", [])
        essential_count = int(len(components) * (1 - reduce_by))
        
        # Keep only essential components
        essential = components[:essential_count]
        
        changes.append({
            "action": "remove_components",
            "removed": len(components) - essential_count,
            "kept": essential_count
        })
        
        # Update target
        target["components"] = essential
        
        return changes, rollback
    
    def _apply_best_practices(
        self, target: Dict, parameters: Dict
    ) -> Tuple[List[Dict], Dict]:
        """Apply UX best practices"""
        
        changes = []
        rollback = {"original_config": target.get("config", {})}
        
        enhancements = parameters.get("enhance", [])
        
        for enhancement in enhancements:
            if enhancement == "spacing":
                changes.append({
                    "action": "increase_spacing",
                    "multiplier": 1.2
                })
                target["config"]["spacing"] = "comfortable"
            
            elif enhancement == "clarity":
                changes.append({
                    "action": "improve_clarity",
                    "changes": ["larger_fonts", "better_contrast", "clearer_labels"]
                })
                target["config"]["font_size"] = "large"
                target["config"]["contrast"] = "high"
            
            elif enhancement == "feedback":
                changes.append({
                    "action": "add_feedback",
                    "types": ["loading_indicators", "success_messages", "error_hints"]
                })
                target["config"]["show_feedback"] = True
        
        return changes, rollback
    
    def _add_validation(
        self, target: Dict, parameters: Dict
    ) -> Tuple[List[Dict], Dict]:
        """Add validation to reduce errors"""
        
        changes = []
        rollback = {"original_validation": target.get("validation", {})}
        
        validate_areas = parameters.get("validate", [])
        
        for area in validate_areas:
            if area == "inputs":
                changes.append({
                    "action": "add_input_validation",
                    "types": ["required", "format", "range"]
                })
                target["validation"]["inputs"] = True
            
            elif area == "actions":
                changes.append({
                    "action": "add_action_validation",
                    "types": ["confirmation", "prerequisites", "permissions"]
                })
                target["validation"]["actions"] = True
            
            elif area == "navigation":
                changes.append({
                    "action": "add_navigation_guards",
                    "types": ["unsaved_changes", "required_fields", "workflow_completion"]
                })
                target["validation"]["navigation"] = True
        
        return changes, rollback
    
    def _reduce_complexity(
        self, target: Dict, parameters: Dict
    ) -> Tuple[List[Dict], Dict]:
        """Reduce interface complexity"""
        
        changes = []
        rollback = {"original_complexity": target.get("complexity", "normal")}
        
        level = parameters.get("simplification_level", "moderate")
        
        if level == "minimal":
            changes.append({
                "action": "minimal_complexity",
                "changes": ["hide_advanced", "single_column", "essential_only"]
            })
            target["complexity"] = "minimal"
        
        elif level == "moderate":
            changes.append({
                "action": "moderate_complexity",
                "changes": ["progressive_disclosure", "grouped_features", "clear_hierarchy"]
            })
            target["complexity"] = "simple"
        
        elif level == "aggressive":
            changes.append({
                "action": "aggressive_simplification",
                "changes": ["wizard_mode", "guided_flow", "no_options"]
            })
            target["complexity"] = "guided"
        
        return changes, rollback
    
    def _reorganize_layout(
        self, target: Dict, parameters: Dict
    ) -> Tuple[List[Dict], Dict]:
        """Reorganize interface layout"""
        
        changes = []
        rollback = {"original_layout": target.get("layout", {})}
        
        strategy = parameters.get("strategy", "task_focused")
        
        if strategy == "task_focused":
            changes.append({
                "action": "task_focused_layout",
                "changes": ["primary_action_prominent", "related_grouped", "clear_flow"]
            })
            target["layout"] = {
                "type": "task_focused",
                "primary_position": "center",
                "flow": "linear"
            }
        
        elif strategy == "information_hierarchy":
            changes.append({
                "action": "hierarchical_layout",
                "changes": ["important_top", "progressive_detail", "scannable"]
            })
            target["layout"] = {
                "type": "hierarchical",
                "structure": "pyramid",
                "scanning": "F-pattern"
            }
        
        return changes, rollback
    
    def _enhance_accessibility(
        self, target: Dict, parameters: Dict
    ) -> Tuple[List[Dict], Dict]:
        """Enhance accessibility features"""
        
        changes = []
        rollback = {"original_accessibility": target.get("accessibility", {})}
        
        improvements = parameters.get("improvements", [])
        
        for improvement in improvements:
            if improvement == "contrast":
                changes.append({
                    "action": "improve_contrast",
                    "ratio": "4.5:1"  # WCAG AA standard
                })
                target["accessibility"]["contrast"] = "high"
            
            elif improvement == "labels":
                changes.append({
                    "action": "add_aria_labels",
                    "coverage": "complete"
                })
                target["accessibility"]["aria_labels"] = True
            
            elif improvement == "navigation":
                changes.append({
                    "action": "keyboard_navigation",
                    "features": ["focus_visible", "skip_links", "landmarks"]
                })
                target["accessibility"]["keyboard_nav"] = True
        
        return changes, rollback
    
    def _consolidate_workflow_steps(
        self, target: Dict, parameters: Dict
    ) -> Tuple[List[Dict], Dict]:
        """Consolidate workflow steps"""
        
        changes = []
        rollback = {"original_workflow": target.get("workflow", [])}
        
        reduction = parameters.get("target_reduction", 0.3)
        workflow = target.get("workflow", [])
        
        # Identify steps that can be combined
        original_count = len(workflow)
        target_count = int(original_count * (1 - reduction))
        
        # Combine related steps
        combined_workflow = self._combine_workflow_steps(workflow, target_count)
        
        changes.append({
            "action": "consolidate_steps",
            "original": original_count,
            "consolidated": len(combined_workflow),
            "reduction": f"{reduction*100:.0f}%"
        })
        
        target["workflow"] = combined_workflow
        
        return changes, rollback
    
    def _combine_workflow_steps(
        self, steps: List, target_count: int
    ) -> List:
        """Combine related workflow steps"""
        
        if len(steps) <= target_count:
            return steps
        
        # Simple combination strategy - merge adjacent steps
        combined = []
        i = 0
        while i < len(steps):
            if len(combined) < target_count - 1:
                combined.append(steps[i])
                i += 1
            else:
                # Combine remaining steps
                combined.append({
                    "combined": True,
                    "steps": steps[i:]
                })
                break
        
        return combined
    
    @safe_async_operation(default_return=None)
    async def _measure_optimization_impact(self):
        """Measure the impact of applied optimizations"""
        
        logger = get_logger(__name__)
        
        for opt_id, optimization in self.active_optimizations.items():
            try:
                if optimization.status != "applied":
                    continue
                
                # Check if enough time has passed
                hours_passed = (datetime.now() - optimization.timestamp).total_seconds() / 3600
                if hours_passed < self.measurement_period_hours:
                    continue
                
                # Capture metrics after
                target = {
                    "type": optimization.target_type,
                    "id": optimization.target_id
                }
                metrics_after = self._capture_current_metrics(target)
                
                # Calculate improvement
                improvement = self._calculate_improvement(
                    optimization.metrics_before,
                    metrics_after
                )
                
                # Update optimization result
                optimization.metrics_after = metrics_after
                optimization.improvement = improvement
                optimization.status = "successful" if improvement > 0 else "failed"
                
                # Update rule success rate
                rule = next((r for r in self.rules if r.id == optimization.rule_id), None)
                if rule:
                    success_rate = (rule.success_rate * rule.times_applied + 
                                   (1 if improvement > 0 else 0)) / (rule.times_applied + 1)
                    rule.success_rate = success_rate
                
                # Store updated result
                self._store_optimization_result(optimization)
            except Exception as e:
                logger.error(f"Failed to measure impact for {opt_id}: {e}")
                error_collector.add_error(
                    "impact_measurement_error",
                    str(e),
                    {"optimization_id": opt_id}
                )
    
    def _check_and_revert_failures(self):
        """Check for failed optimizations and revert them"""
        
        for opt_id, optimization in self.active_optimizations.items():
            if optimization.status == "failed" and optimization.improvement < -0.1:
                print(f"⚠️ Reverting failed optimization: {opt_id}")
                self._revert_optimization(optimization)
    
    def _revert_optimization(self, optimization: OptimizationResult):
        """Revert a failed optimization"""
        
        target = {
            "type": optimization.target_type,
            "id": optimization.target_id
        }
        
        # Apply rollback data
        if optimization.rollback_data:
            for key, value in optimization.rollback_data.items():
                if key.startswith("original_"):
                    actual_key = key.replace("original_", "")
                    target[actual_key] = value
        
        optimization.status = "reverted"
        self._store_optimization_result(optimization)
    
    @safe_database_operation(default_return=None)
    def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value of a metric"""
        
        # Query from various sources
        if metric_name == "avg_generation_time":
            summary = self.learning_db.conn.execute(
                "SELECT AVG(generation_time) FROM interface_metrics"
            ).fetchone()
            return summary[0] if summary and summary[0] else None
        
        elif metric_name == "satisfaction_score":
            feedback = self.feedback_collector.get_feedback_summary()
            return feedback.get("average_sentiment", 0) * 5  # Convert to 5-point scale
        
        elif metric_name == "error_rate":
            # Calculate from error logs
            total = self.learning_db.conn.execute(
                "SELECT COUNT(*) FROM user_interactions"
            ).fetchone()[0]
            errors = self.learning_db.conn.execute(
                "SELECT COUNT(*) FROM error_logs"
            ).fetchone()[0]
            return errors / total if total > 0 else 0
        
        elif metric_name == "task_completion_rate":
            feedback = self.feedback_collector.get_feedback_summary()
            return feedback.get("task_completion_rate", 0.5)
        
        # Add more metrics as needed
        return None
    
    def _calculate_confidence(
        self, rule: OptimizationRule, insights: List[InsightReport]
    ) -> float:
        """Calculate confidence for applying a rule"""
        
        confidence = 0.7  # Base confidence
        
        # Increase confidence if insights support it
        for insight in insights:
            if insight.category == rule.optimization_type.value:
                confidence = max(confidence, insight.confidence)
        
        # Adjust based on rule's historical success
        if rule.times_applied > 0:
            confidence = confidence * 0.5 + rule.success_rate * 0.5
        
        return min(1.0, confidence)
    
    def _identify_optimization_target(
        self, rule: OptimizationRule
    ) -> Optional[Dict]:
        """Identify what to optimize based on rule"""
        
        # This would identify specific interfaces/components to optimize
        # For demo, return a mock target
        return {
            "type": "interface",
            "id": f"interface_{rule.optimization_type.value}",
            "components": ["comp1", "comp2", "comp3"],
            "config": {},
            "layout": {},
            "workflow": ["step1", "step2", "step3", "step4", "step5"]
        }
    
    def _capture_current_metrics(self, target: Dict) -> Dict[str, float]:
        """Capture current metrics for a target"""
        
        # This would capture real metrics
        # For demo, return sample metrics
        return {
            "generation_time": 1500,
            "satisfaction": 3.5,
            "error_rate": 0.05,
            "completion_rate": 0.75,
            "abandonment_rate": 0.25
        }
    
    def _calculate_improvement(
        self, before: Dict[str, float], after: Dict[str, float]
    ) -> float:
        """Calculate overall improvement percentage"""
        
        if not after:
            return 0
        
        improvements = []
        
        for metric, before_value in before.items():
            if metric in after:
                after_value = after[metric]
                
                # Calculate improvement (lower is better for some metrics)
                if metric in ["error_rate", "abandonment_rate", "generation_time"]:
                    improvement = (before_value - after_value) / before_value if before_value > 0 else 0
                else:
                    improvement = (after_value - before_value) / before_value if before_value > 0 else 0
                
                improvements.append(improvement)
        
        return sum(improvements) / len(improvements) if improvements else 0
    
    def _get_approval(self, rule: OptimizationRule) -> bool:
        """Get human approval for optimization"""
        
        # In real implementation, would show UI for approval
        print(f"🔔 Approval needed for: {rule.name}")
        print(f"   Description: {rule.description}")
        print(f"   Type: {rule.optimization_type.value}")
        
        # Auto-approve for demo
        return True
    
    def _create_validation_test(
        self, rule: OptimizationRule, target: Dict, changes: List[Dict]
    ):
        """Create A/B test to validate optimization"""
        
        # Create test comparing original vs optimized
        test = self.ab_testing.create_test(
            name=f"Validation: {rule.name}",
            variation_type=VariationType.COMPLEXITY_LEVEL,
            variants_config=[
                {
                    "name": "Original",
                    "description": "Before optimization",
                    "parameters": {"optimized": False}
                },
                {
                    "name": "Optimized",
                    "description": f"After {rule.action}",
                    "parameters": {"optimized": True, "changes": changes}
                }
            ],
            minimum_sample_size=50
        )
        
        print(f"📊 Created A/B test to validate: {test.name}")
    
    @safe_database_operation(default_return=None)
    def _store_optimization_result(self, result: OptimizationResult):
        """Store optimization result in database"""
        
        cursor = self.learning_db.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO optimization_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.id,
            result.rule_id,
            result.timestamp.isoformat(),
            result.target_type,
            result.target_id,
            json.dumps(result.changes_applied),
            json.dumps(result.metrics_before),
            json.dumps(result.metrics_after) if result.metrics_after else None,
            result.improvement,
            result.status,
            result.confidence
        ))
        self.learning_db.conn.commit()
    
    def get_optimization_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for optimization status"""
        
        active_count = len([o for o in self.active_optimizations.values() 
                          if o.status == "applied"])
        successful_count = len([o for o in self.active_optimizations.values()
                              if o.status == "successful"])
        failed_count = len([o for o in self.active_optimizations.values()
                          if o.status == "failed"])
        
        # Calculate average improvement
        improvements = [o.improvement for o in self.active_optimizations.values()
                       if o.improvement is not None]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # Get top performing rules
        top_rules = sorted(self.rules, key=lambda r: r.success_rate, reverse=True)[:3]
        
        return {
            "summary": {
                "total_rules": len(self.rules),
                "active_optimizations": active_count,
                "successful": successful_count,
                "failed": failed_count,
                "average_improvement": avg_improvement
            },
            "top_rules": [
                {
                    "name": rule.name,
                    "type": rule.optimization_type.value,
                    "times_applied": rule.times_applied,
                    "success_rate": rule.success_rate
                }
                for rule in top_rules
            ],
            "recent_optimizations": [
                {
                    "id": opt.id,
                    "rule": opt.rule_id,
                    "target": opt.target_id,
                    "status": opt.status,
                    "improvement": opt.improvement,
                    "timestamp": opt.timestamp.isoformat()
                }
                for opt in list(self.active_optimizations.values())[-5:]
            ]
        }


def demo_automatic_optimization():
    """Demonstrate automatic optimization"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        🚀 AUTOMATIC OPTIMIZATION ENGINE DEMO                       ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    optimizer = AutomaticOptimizer()
    
    # Show optimization rules
    print("\n📋 Configured Optimization Rules:")
    print("-" * 60)
    
    for rule in optimizer.rules[:5]:
        print(f"\n   📌 {rule.name}")
        print(f"      Type: {rule.optimization_type.value}")
        print(f"      Trigger: {rule.trigger_metric} {rule.trigger_comparison} {rule.trigger_threshold}")
        print(f"      Action: {rule.action}")
        print(f"      Confidence Required: {rule.min_confidence:.0%}")
    
    # Run optimization cycle
    print("\n\n🔄 Running Optimization Cycle...")
    print("-" * 60)
    
    # Run asynchronously
    async def run_demo():
        results = await optimizer.run_optimization_cycle()
        
        if results:
            print(f"\n✅ Applied {len(results)} optimizations:")
            for result in results:
                print(f"   • {result.id}: {result.target_type} → {result.status}")
        else:
            print("\n   No optimizations triggered (metrics within acceptable ranges)")
        
        return results
    
    # Execute async function
    import asyncio
    results = asyncio.run(run_demo())
    
    # Simulate measuring impact
    print("\n📊 Simulating Impact Measurement...")
    
    # Mock some metrics after optimization
    for opt_id, opt in optimizer.active_optimizations.items():
        opt.metrics_after = {
            "generation_time": 1200,  # Improved
            "satisfaction": 4.0,  # Improved
            "error_rate": 0.03,  # Improved
            "completion_rate": 0.85,  # Improved
            "abandonment_rate": 0.15  # Improved
        }
        opt.improvement = optimizer._calculate_improvement(
            opt.metrics_before, opt.metrics_after
        )
        opt.status = "successful" if opt.improvement > 0 else "failed"
    
    # Get optimization dashboard
    dashboard = optimizer.get_optimization_dashboard()
    
    print("\n📈 OPTIMIZATION DASHBOARD")
    print("-" * 60)
    
    summary = dashboard["summary"]
    print(f"   Total Rules: {summary['total_rules']}")
    print(f"   Active Optimizations: {summary['active_optimizations']}")
    print(f"   Successful: {summary['successful']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Average Improvement: {summary['average_improvement']:.1%}")
    
    if dashboard["top_rules"]:
        print("\n🏆 Top Performing Rules:")
        for rule in dashboard["top_rules"]:
            if rule["times_applied"] > 0:
                print(f"   • {rule['name']}")
                print(f"     Applied: {rule['times_applied']} times")
                print(f"     Success Rate: {rule['success_rate']:.1%}")
    
    if dashboard["recent_optimizations"]:
        print("\n📝 Recent Optimizations:")
        for opt in dashboard["recent_optimizations"]:
            status_icon = "✅" if opt["status"] == "successful" else "❌" if opt["status"] == "failed" else "⏳"
            improvement = f"{opt['improvement']:.1%}" if opt["improvement"] else "measuring..."
            print(f"   {status_icon} {opt['rule']} → {opt['target']}")
            print(f"      Improvement: {improvement}")
    
    print("""

═══════════════════════════════════════════════════════════════════════
✨ Automatic Optimization Features:

1. Smart Rule Engine:
   • Performance optimization
   • UX improvements
   • Error reduction
   • Complexity adjustment
   • Layout optimization
   • Accessibility enhancement
   • Workflow streamlining

2. Automatic Triggers:
   • Metric-based activation
   • Confidence thresholds
   • Cooldown periods
   • Approval workflows

3. Optimization Actions:
   • Component simplification
   • Best practice application
   • Validation addition
   • Layout reorganization
   • Accessibility improvements
   • Workflow consolidation

4. Impact Measurement:
   • Before/after metrics
   • Improvement calculation
   • A/B test validation
   • Automatic rollback

5. Learning & Adaptation:
   • Success rate tracking
   • Rule refinement
   • Pattern recognition
   • Continuous improvement

Next Steps:
• Connect to real metrics
• Implement approval UI
• Add machine learning predictions
• Create optimization history view
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_automatic_optimization()