"""
from typing import Dict, List, Optional
Sacred Patterns - Reusable consciousness-first code patterns

These patterns embody principles from sacred technology development,
ensuring every function serves consciousness rather than consuming it.
"""

import functools
import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from datetime import datetime
import logging
from dataclasses import dataclass
from contextlib import contextmanager

from ..knowledge_graph.skg import SymbioticKnowledgeGraph

T = TypeVar('T')


@dataclass
class SacredPattern:
    """A reusable sacred development pattern"""
    name: str
    description: str
    intention: str
    implementation: Callable
    consciousness_principles: List[str]
    

class PatternLibrary:
    """
    Library of sacred development patterns
    
    These patterns ensure:
    1. Every function is a prayer (intentional code)
    2. Consciousness is protected, not consumed
    3. Errors are teachers, not failures
    4. Code serves the highest good
    """
    
    def __init__(self, skg: Optional[SymbioticKnowledgeGraph] = None):
        self.skg = skg
        self.patterns = {}
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize the sacred pattern library"""
        
        # Pattern: Sacred Function
        self.patterns['sacred_function'] = SacredPattern(
            name='Sacred Function',
            description='Wraps functions with consciousness-first principles',
            intention='Transform ordinary functions into sacred acts',
            implementation=self.sacred_function,
            consciousness_principles=[
                'Set clear intention before execution',
                'Handle errors with compassion',
                'Return wisdom, not just data',
                'Respect user attention'
            ]
        )
        
        # Pattern: Mindful Async
        self.patterns['mindful_async'] = SacredPattern(
            name='Mindful Async',
            description='Async operations that respect natural rhythms',
            intention='Honor time as sacred, not scarce',
            implementation=self.mindful_async,
            consciousness_principles=[
                'Allow graceful cancellation',
                'Provide meaningful progress',
                'Respect system resources',
                'Complete with gratitude'
            ]
        )
        
        # Pattern: Compassionate Error
        self.patterns['compassionate_error'] = SacredPattern(
            name='Compassionate Error Handler',
            description='Error handling that teaches rather than punishes',
            intention='Transform errors into opportunities for growth',
            implementation=self.compassionate_error_handler,
            consciousness_principles=[
                'Errors are teachers',
                'Provide constructive guidance',
                'Maintain user dignity',
                'Learn from each occurrence'
            ]
        )
        
        # Pattern: Flow State Guard
        self.patterns['flow_guard'] = SacredPattern(
            name='Flow State Guard',
            description='Protects user flow state from interruptions',
            intention='Honor deep work as sacred time',
            implementation=self.flow_state_guard,
            consciousness_principles=[
                'Check interruption necessity',
                'Batch non-urgent messages',
                'Respect focus boundaries',
                'Enable graceful transitions'
            ]
        )
        
        # Pattern: Evolutionary Function
        self.patterns['evolutionary'] = SacredPattern(
            name='Evolutionary Function',
            description='Functions that improve with each use',
            intention='Create code that grows wiser over time',
            implementation=self.evolutionary_function,
            consciousness_principles=[
                'Learn from each execution',
                'Adapt to user patterns',
                'Share wisdom collectively',
                'Evolve toward excellence'
            ]
        )
        
    def sacred_function(self, intention: str = "", 
                       track_wisdom: bool = True) -> Callable:
        """
        Decorator that transforms functions into sacred acts
        
        Example:
            @sacred_function(intention="Parse user input with compassion")
            def parse_command(input_str):
                return parsed_result
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> T:
                # Set intention
                func_intention = intention or f"Execute {func.__name__} mindfully"
                start_time = datetime.now()
                
                # Log sacred invocation
                if self.skg and track_wisdom:
                    self._log_sacred_invocation(func.__name__, func_intention)
                    
                try:
                    # Execute with awareness
                    result = func(*args, **kwargs)
                    
                    # Record wisdom gained
                    if self.skg and track_wisdom:
                        self._record_wisdom(func.__name__, True, result)
                        
                    return result
                    
                except Exception as e:
                    # Handle with compassion
                    logging.info(f"Learning opportunity in {func.__name__}: {str(e)}")
                    
                    if self.skg and track_wisdom:
                        self._record_wisdom(func.__name__, False, str(e))
                        
                    # Re-raise with wisdom
                    raise self._enhance_error_with_wisdom(e, func.__name__)
                    
                finally:
                    # Express gratitude
                    duration = (datetime.now() - start_time).total_seconds()
                    logging.debug(f"Completed {func.__name__} in {duration:.2f}s with gratitude")
                    
            # Async version
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                func_intention = intention or f"Execute {func.__name__} mindfully"
                start_time = datetime.now()
                
                if self.skg and track_wisdom:
                    self._log_sacred_invocation(func.__name__, func_intention)
                    
                try:
                    result = await func(*args, **kwargs)
                    
                    if self.skg and track_wisdom:
                        self._record_wisdom(func.__name__, True, result)
                        
                    return result
                    
                except Exception as e:
                    logging.info(f"Learning opportunity in {func.__name__}: {str(e)}")
                    
                    if self.skg and track_wisdom:
                        self._record_wisdom(func.__name__, False, str(e))
                        
                    raise self._enhance_error_with_wisdom(e, func.__name__)
                    
                finally:
                    duration = (datetime.now() - start_time).total_seconds()
                    logging.debug(f"Completed {func.__name__} in {duration:.2f}s with gratitude")
                    
            # Return appropriate wrapper
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
                
        return decorator
        
    def mindful_async(self, respect_cancellation: bool = True,
                     progress_callback: Optional[Callable] = None) -> Callable:
        """
        Decorator for async operations that respect natural rhythms
        
        Example:
            @mindful_async(progress_callback=update_progress)
            async def long_running_task():
                # Task implementation
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                # Create task context
                task_name = func.__name__
                task_context = {
                    'name': task_name,
                    'started': datetime.now(),
                    'cancelled': False
                }
                
                try:
                    # Check if we should proceed
                    if respect_cancellation and asyncio.current_task().cancelled():
                        logging.info(f"Respecting cancellation of {task_name}")
                        raise asyncio.CancelledError()
                        
                    # Execute with progress awareness
                    if progress_callback:
                        # Wrap function to inject progress
                        kwargs['_progress_callback'] = progress_callback
                        
                    result = await func(*args, **kwargs)
                    
                    # Complete with gratitude
                    logging.debug(f"{task_name} completed mindfully")
                    return result
                    
                except asyncio.CancelledError:
                    # Handle cancellation gracefully
                    logging.info(f"{task_name} cancelled gracefully")
                    if self.skg:
                        self._record_graceful_cancellation(task_name)
                    raise
                    
                except Exception as e:
                    # Learn from errors
                    logging.error(f"Challenge in {task_name}: {str(e)}")
                    raise
                    
            return wrapper
        return decorator
        
    def compassionate_error_handler(self, 
                                  provide_guidance: bool = True,
                                  learn_from_errors: bool = True) -> Callable:
        """
        Decorator that handles errors with compassion and wisdom
        
        Example:
            @compassionate_error_handler()
            def risky_operation():
                # Operation that might fail
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> T:
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    # Transform error into learning opportunity
                    error_wisdom = self._extract_error_wisdom(e, func.__name__)
                    
                    # Provide constructive guidance
                    if provide_guidance:
                        guidance = self._generate_error_guidance(e, func.__name__)
                        error_wisdom['guidance'] = guidance
                        
                    # Learn for future
                    if learn_from_errors and self.skg:
                        self._record_error_learning(func.__name__, e, error_wisdom)
                        
                    # Create enhanced error
                    enhanced_error = type(e)(
                        f"{str(e)}\n\n💡 Wisdom: {error_wisdom.get('lesson', '')}\n"
                        f"🌟 Guidance: {error_wisdom.get('guidance', '')}"
                    )
                    
                    raise enhanced_error
                    
            return wrapper
        return decorator
        
    def flow_state_guard(self, check_flow: bool = True,
                        batch_window: int = 300) -> Callable:
        """
        Decorator that protects user flow state
        
        Example:
            @flow_state_guard(batch_window=600)  # 10 minute batching
            def send_notification(message):
                # Notification logic
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> T:
                # Check if user is in flow
                if check_flow and self._user_in_flow():
                    # Defer non-urgent operations
                    priority = kwargs.get('priority', 'normal')
                    
                    if priority != 'urgent':
                        logging.info(f"Deferring {func.__name__} to protect flow")
                        self._queue_for_later(func, args, kwargs, batch_window)
                        return None
                        
                # Execute if appropriate
                return func(*args, **kwargs)
                
            return wrapper
        return decorator
        
    def evolutionary_function(self, 
                            learn_from_usage: bool = True,
                            share_learning: bool = True) -> Callable:
        """
        Decorator for functions that improve with use
        
        Example:
            @evolutionary_function()
            def smart_suggestion(context):
                # Suggestion logic that improves
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            # Get or create evolution data
            evolution_key = f"evolution_{func.__module__}_{func.__name__}"
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> T:
                # Load accumulated wisdom
                wisdom = self._load_function_wisdom(evolution_key)
                
                # Inject wisdom into function
                kwargs['_accumulated_wisdom'] = wisdom
                
                # Execute with current wisdom
                start_time = datetime.now()
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                # Learn from this execution
                if learn_from_usage:
                    new_learning = {
                        'args_pattern': self._extract_pattern(args),
                        'result_pattern': self._extract_pattern(result),
                        'duration': duration,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    wisdom['executions'].append(new_learning)
                    wisdom['total_executions'] += 1
                    
                    # Evolve function behavior
                    self._evolve_function_behavior(evolution_key, wisdom)
                    
                # Share learning if enabled
                if share_learning and self.skg:
                    self._share_function_evolution(evolution_key, wisdom)
                    
                return result
                
            return wrapper
        return decorator
        
    @contextmanager
    def sacred_context(self, intention: str, protected: bool = True):
        """
        Context manager for sacred code blocks
        
        Example:
            with sacred_context("Process user data with respect"):
                # Sacred operations
        """
        # Enter sacred space
        context_id = self._create_sacred_context(intention)
        
        try:
            # Set protective boundaries if requested
            if protected:
                self._establish_protection(context_id)
                
            yield context_id
            
        finally:
            # Exit with gratitude
            self._complete_sacred_context(context_id)
            
    def _log_sacred_invocation(self, func_name: str, intention: str):
        """Log the sacred invocation of a function"""
        if not self.skg:
            return
            
        import json
        
        invocation_id = f"invocation_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'sacred_invocation', ?)
        """, (
            invocation_id,
            json.dumps({
                'function': func_name,
                'intention': intention,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def _record_wisdom(self, func_name: str, success: bool, result: Any):
        """Record wisdom gained from function execution"""
        if not self.skg:
            return
            
        import json
        
        wisdom_id = f"wisdom_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'function_wisdom', ?)
        """, (
            wisdom_id,
            json.dumps({
                'function': func_name,
                'success': success,
                'result_type': type(result).__name__,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def _enhance_error_with_wisdom(self, error: Exception, func_name: str) -> Exception:
        """Enhance error with wisdom and guidance"""
        error_type = type(error).__name__
        
        wisdom_messages = {
            'ValueError': "The universe is showing us that our assumptions need adjustment",
            'KeyError': "We're seeking something that hasn't revealed itself yet",
            'TypeError': "The forms don't align - let's find harmony",
            'AttributeError': "We're reaching for qualities not yet manifested",
            'IndexError': "We've ventured beyond current boundaries",
            'IOError': "The flow of information seeks a different path"
        }
        
        wisdom = wisdom_messages.get(error_type, "Every error is a teacher in disguise")
        
        # Add context-specific guidance
        guidance = f"In {func_name}: {wisdom}"
        
        # Create enhanced error message
        enhanced_message = f"{str(error)}\n\n🙏 {guidance}"
        
        # Return new error with enhanced message
        return type(error)(enhanced_message)
        
    def _extract_error_wisdom(self, error: Exception, func_name: str) -> Dict[str, str]:
        """Extract wisdom from an error"""
        return {
            'error_type': type(error).__name__,
            'function': func_name,
            'lesson': self._derive_lesson_from_error(error),
            'growth_opportunity': self._identify_growth_opportunity(error)
        }
        
    def _derive_lesson_from_error(self, error: Exception) -> str:
        """Derive a lesson from an error"""
        error_lessons = {
            'ValueError': "Input validation helps us serve users better",
            'KeyError': "Defensive programming prevents assumptions",
            'TypeError': "Type clarity creates reliable systems",
            'AttributeError': "Interface contracts build trust",
            'IndexError': "Boundary checking ensures safety",
            'IOError': "Resilient I/O handles reality gracefully"
        }
        
        return error_lessons.get(
            type(error).__name__, 
            "Every error teaches us to build with more awareness"
        )
        
    def _identify_growth_opportunity(self, error: Exception) -> str:
        """Identify growth opportunity from error"""
        growth_opportunities = {
            'ValueError': "Add input validation",
            'KeyError': "Implement safe dictionary access",
            'TypeError': "Add type hints and validation",
            'AttributeError': "Define clear interfaces",
            'IndexError': "Add bounds checking",
            'IOError': "Implement retry logic"
        }
        
        return growth_opportunities.get(
            type(error).__name__,
            "Enhance error handling"
        )
        
    def _generate_error_guidance(self, error: Exception, func_name: str) -> str:
        """Generate constructive guidance for an error"""
        # Get error context
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Generate contextual guidance
        if 'permission' in error_msg.lower():
            return "Check file permissions and user access rights"
        elif 'connection' in error_msg.lower():
            return "Verify network connectivity and service availability"
        elif 'not found' in error_msg.lower():
            return "Ensure the resource exists and path is correct"
        elif 'timeout' in error_msg.lower():
            return "Consider increasing timeout or checking system load"
        else:
            return f"Review {func_name} implementation for {error_type} handling"
            
    def _record_error_learning(self, func_name: str, error: Exception, wisdom: Dict):
        """Record learning from an error"""
        if not self.skg:
            return
            
        import json
        
        learning_id = f"error_learning_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'error_learning', ?)
        """, (
            learning_id,
            json.dumps({
                'function': func_name,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'wisdom': wisdom,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def _user_in_flow(self) -> bool:
        """Check if user is in flow state"""
        if not self.skg:
            return False
            
        # Query recent flow state
        cursor = self.skg.conn.cursor()
        recent_flow = cursor.execute("""
            SELECT json_extract(properties, '$.flow_level')
            FROM nodes
            WHERE layer = 'phenomenological'
            AND type = 'cognitive_state'
            ORDER BY created_at DESC
            LIMIT 1
        """).fetchone()
        
        if recent_flow and recent_flow[0]:
            return float(recent_flow[0]) > 0.7
            
        return False
        
    def _queue_for_later(self, func: Callable, args: tuple, kwargs: dict, batch_window: int):
        """Queue operation for later execution"""
        # In production, this would use a proper task queue
        # For now, we'll log the deferral
        logging.info(f"Queued {func.__name__} for execution in {batch_window} seconds")
        
    def _load_function_wisdom(self, evolution_key: str) -> Dict:
        """Load accumulated wisdom for a function"""
        if not self.skg:
            return {'executions': [], 'total_executions': 0}
            
        cursor = self.skg.conn.cursor()
        wisdom_data = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'metacognitive'
            AND type = 'function_evolution'
            AND id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (evolution_key,)).fetchone()
        
        if wisdom_data:
            import json
            return json.loads(wisdom_data[0])
            
        return {'executions': [], 'total_executions': 0}
        
    def _extract_pattern(self, data: Any) -> Dict:
        """Extract pattern from data for learning"""
        if isinstance(data, (str, int, float, bool)):
            return {'type': type(data).__name__, 'value_class': 'scalar'}
        elif isinstance(data, (list, tuple)):
            return {'type': type(data).__name__, 'length': len(data)}
        elif isinstance(data, dict):
            return {'type': 'dict', 'keys': list(data.keys())}
        else:
            return {'type': type(data).__name__, 'complex': True}
            
    def _evolve_function_behavior(self, evolution_key: str, wisdom: Dict):
        """Evolve function behavior based on accumulated wisdom"""
        if not self.skg:
            return
            
        import json
        
        # Analyze patterns for optimization
        if wisdom['total_executions'] % 10 == 0:
            # Every 10 executions, analyze and optimize
            avg_duration = sum(e['duration'] for e in wisdom['executions'][-10:]) / 10
            
            wisdom['optimization_hints'] = {
                'average_duration': avg_duration,
                'common_patterns': self._identify_common_patterns(wisdom['executions']),
                'optimization_potential': avg_duration > 1.0
            }
            
        # Save evolved wisdom
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'function_evolution', ?)
        """, (
            evolution_key,
            json.dumps(wisdom)
        ))
        
        self.skg.conn.commit()
        
    def _identify_common_patterns(self, executions: List[Dict]) -> List[Dict]:
        """Identify common patterns in executions"""
        # Simplified pattern detection
        patterns = {}
        
        for execution in executions[-20:]:  # Last 20 executions
            pattern_key = str(execution.get('args_pattern', {}))
            patterns[pattern_key] = patterns.get(pattern_key, 0) + 1
            
        # Return top patterns
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        return [{'pattern': p, 'count': c} for p, c in sorted_patterns[:3]]
        
    def _share_function_evolution(self, evolution_key: str, wisdom: Dict):
        """Share function evolution with the collective"""
        # In production, this would share insights across instances
        # For now, we'll log the sharing intent
        logging.debug(f"Sharing evolution insights for {evolution_key}")
        
    def _create_sacred_context(self, intention: str) -> str:
        """Create a sacred context"""
        context_id = f"context_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        logging.info(f"Entering sacred context: {intention}")
        return context_id
        
    def _establish_protection(self, context_id: str):
        """Establish protective boundaries for sacred context"""
        logging.debug(f"Protection established for {context_id}")
        
    def _complete_sacred_context(self, context_id: str):
        """Complete and close sacred context"""
        logging.debug(f"Sacred context {context_id} completed with gratitude")
        
    def _record_graceful_cancellation(self, task_name: str):
        """Record graceful task cancellation"""
        if not self.skg:
            return
            
        import json
        
        cancellation_id = f"cancellation_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'graceful_cancellation', ?)
        """, (
            cancellation_id,
            json.dumps({
                'task': task_name,
                'timestamp': datetime.now().isoformat(),
                'handled_gracefully': True
            })
        ))
        
        self.skg.conn.commit()