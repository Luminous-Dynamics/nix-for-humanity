"""
StatefulExecutorWithRecovery - Enhanced executor with automatic error recovery

Integrates StatefulExecutor with ErrorRecoveryManager for intelligent,
automatic retry and recovery during operation execution.

Based on: Week 4 Enhanced Integration
"""

from typing import List, Dict, Any
from datetime import datetime
import logging
import time

from .stateful_executor import StatefulExecutor
from .execution_plan import ExecutionPlan, ExecutionStep, StepStatus
from .state_manager import StateManager, OperationState, OperationStatus
from .error_recovery import (
    ErrorRecoveryManager,
    ErrorCategory,
    RecoverabilityLevel
)

logger = logging.getLogger(__name__)


class StatefulExecutorWithRecovery(StatefulExecutor):
    """
    Enhanced StatefulExecutor with automatic error recovery.

    Features:
    - Automatic retry of failed steps based on error classification
    - Exponential backoff between retries
    - Max retry enforcement
    - Recovery state tracking
    - Intelligent recovery decisions based on error category/severity
    """

    def __init__(
        self,
        state_manager: StateManager,
        error_recovery: ErrorRecoveryManager
    ):
        """
        Initialize enhanced executor with error recovery.

        Args:
            state_manager: StateManager instance for state persistence
            error_recovery: ErrorRecoveryManager for intelligent recovery
        """
        super().__init__(state_manager)
        self.error_recovery = error_recovery

    def _execute_step(
        self,
        step: ExecutionStep,
        state: OperationState
    ) -> Dict[str, Any]:
        """
        Execute a single step with automatic retry on recoverable errors.

        This method overrides the parent to add error recovery logic:
        1. Try to execute step
        2. If fails, classify error
        3. If recoverable, retry with exponential backoff
        4. Respect max_retries limit
        5. Track retry attempts in state

        Args:
            step: ExecutionStep to execute
            state: Current operation state

        Returns:
            Result dictionary with 'success' and 'result'/'error'
        """
        max_retries = state.max_retries
        retry_attempt = 0

        while retry_attempt <= max_retries:
            try:
                logger.debug(
                    f"Executing step {step.id} "
                    f"(attempt {retry_attempt + 1}/{max_retries + 1})"
                )

                # Mark step as running
                step.status = StepStatus.RUNNING

                # Call handler
                result = step.handler(step.parameters)

                # Mark step as success
                step.status = StepStatus.SUCCESS
                step.result = result

                # If we retried, log success
                if retry_attempt > 0:
                    logger.info(
                        f"Step {step.id} succeeded after {retry_attempt} retries"
                    )

                return {
                    'success': True,
                    'result': result
                }

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Step {step.id} failed: {error_msg}")

                # Classify error to determine if recoverable
                classified_error = self.error_recovery.classifier.classify(
                    error_message=error_msg,
                    operation_id=state.operation_id,
                    context={'step_id': step.id}
                )

                # Check if error is recoverable
                if not classified_error.can_retry:
                    # Not recoverable - fail immediately
                    logger.info(
                        f"Step {step.id} failed with non-recoverable error: "
                        f"{classified_error.category.value} "
                        f"(severity: {classified_error.severity.value})"
                    )

                    step.status = StepStatus.FAILED
                    step.error = error_msg

                    return {
                        'success': False,
                        'error': error_msg
                    }

                # Check if we've exhausted retries
                if retry_attempt >= max_retries:
                    logger.info(
                        f"Step {step.id} failed after {max_retries} retries"
                    )

                    step.status = StepStatus.FAILED
                    step.error = error_msg

                    # Update state with final retry count
                    state.retry_count = retry_attempt
                    state.error = error_msg
                    state.error_details = {
                        'message': error_msg,
                        'category': classified_error.category.value,
                        'severity': classified_error.severity.value,
                        'step_id': step.id,
                        'retries_attempted': retry_attempt
                    }
                    self.state_manager.update_operation(state)

                    return {
                        'success': False,
                        'error': error_msg
                    }

                # Recoverable and have retries left - calculate backoff
                retry_strategy = self.error_recovery.default_retry_strategy
                delay = retry_strategy.get_delay(retry_attempt)

                logger.info(
                    f"Step {step.id} failed with recoverable error "
                    f"({classified_error.category.value}), "
                    f"retrying in {delay}s (attempt {retry_attempt + 1}/{max_retries})"
                )

                # Update state with retry info
                state.retry_count = retry_attempt + 1
                state.error = error_msg
                state.error_details = {
                    'message': error_msg,
                    'category': classified_error.category.value,
                    'severity': classified_error.severity.value,
                    'step_id': step.id,
                    'retry_attempt': retry_attempt + 1,
                    'next_retry_delay_s': delay
                }
                self.state_manager.update_operation(state)

                # Wait before retry (exponential backoff)
                time.sleep(delay)

                # Increment retry counter and loop
                retry_attempt += 1

        # Should never reach here, but just in case
        step.status = StepStatus.FAILED
        step.error = "Max retries exceeded"
        return {
            'success': False,
            'error': "Max retries exceeded"
        }


if __name__ == "__main__":
    # Example usage
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Initialize
        state_mgr = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        recovery_mgr = ErrorRecoveryManager(state_manager=state_mgr)

        executor = StatefulExecutorWithRecovery(
            state_manager=state_mgr,
            error_recovery=recovery_mgr
        )

        # Create operation
        state = state_mgr.create_operation("test with recovery")
        state.max_retries = 2
        state_mgr.update_operation(state)

        # Simulate flaky operation
        attempt = {'count': 0}

        def flaky_handler(params):
            attempt['count'] += 1
            if attempt['count'] == 1:
                raise RuntimeError("Connection refused")
            return "Success!"

        step = ExecutionStep(
            id="flaky",
            name="Flaky Step",
            handler=flaky_handler,
            parameters={},
            depends_on=set(),
            provides={'result'},
            requires=set()
        )

        plan = ExecutionPlan(steps=[step])

        # Execute with automatic retry
        print(f"Executing operation: {state.operation_id}")
        result = executor.execute_with_state(plan, state.operation_id)

        print(f"Status: {result.status.value}")
        print(f"Completed steps: {result.completed_steps}")
        print(f"Attempts: {attempt['count']}")
        print(f"Retry count: {result.retry_count}")
