"""
StatefulExecutor - Integration of ExecutionPlan + StateManager

This module integrates ExecutionPlan (multi-step operations) with
StateManager (state tracking and persistence) to enable stateful,
resumable execution with full state tracking.

Based on design: DEEP_DIVE_STATE_MANAGEMENT.md Part 8
"""

from typing import List, Dict, Any
from datetime import datetime
import logging
import concurrent.futures

from .execution_plan import ExecutionPlan, ExecutionStep, StepStatus
from .state_manager import StateManager, OperationState, OperationStatus

logger = logging.getLogger(__name__)


class StatefulExecutor:
    """
    Executes operations while maintaining state.

    Combines ExecutionPlan (DAG-based multi-step operations)
    with StateManager (state tracking and persistence) for
    stateful, resumable execution.
    """

    def __init__(self, state_manager: StateManager):
        """
        Initialize StatefulExecutor.

        Args:
            state_manager: StateManager instance for state persistence
        """
        self.state_manager = state_manager

    def execute_with_state(
        self,
        plan: ExecutionPlan,
        operation_id: str
    ) -> OperationState:
        """
        Execute execution plan while tracking state.

        Features:
        - Updates state after each step
        - Creates checkpoints for resumability
        - Handles failures gracefully
        - Supports parallel execution
        - Persists state to database

        Args:
            plan: ExecutionPlan to execute
            operation_id: ID of operation in StateManager

        Returns:
            Final OperationState after execution

        Raises:
            ValueError: If operation_id not found
            Exception: Re-raises any unexpected errors after updating state
        """
        # Get operation state
        state = self.state_manager.get_operation(operation_id)
        if not state:
            raise ValueError(f"Operation {operation_id} not found")

        # Attach execution plan
        state.execution_plan = plan
        state.status = OperationStatus.EXECUTING
        state.started_at = datetime.now()
        self.state_manager.update_operation(state)

        try:
            # Execute batches
            batch_number = 0
            while True:
                # Get next batch of ready steps
                batch = plan.get_next_batch()
                if not batch:
                    # All steps complete
                    break

                logger.info(f"Executing batch {batch_number} with {len(batch)} steps")

                # Execute batch (steps run in parallel if possible)
                results = self._execute_batch(batch, state)

                # Update state based on results
                all_success = True
                failed_errors = []
                for step, result in zip(batch, results):
                    if result['success']:
                        state.completed_steps.add(step.id)
                        logger.info(f"Step {step.id} completed successfully")
                    else:
                        state.failed_steps.add(step.id)
                        all_success = False
                        error_msg = result.get('error', 'Unknown error')
                        failed_errors.append(f"{step.id}: {error_msg}")
                        logger.error(f"Step {step.id} failed: {error_msg}")

                # If any step failed, fail the whole operation
                if not all_success:
                    state.status = OperationStatus.FAILED
                    state.error = f"Step(s) failed: {'; '.join(failed_errors)}"
                    state.completed_at = datetime.now()

                    # Calculate actual duration
                    if state.started_at:
                        duration = (state.completed_at - state.started_at).total_seconds()
                        state.actual_duration_s = duration

                    self.state_manager.update_operation(state)
                    return state

                # Create checkpoint after batch (for resumability)
                state.checkpoint_data = self._create_checkpoint(state, plan)
                self.state_manager.update_operation(state)

                batch_number += 1

            # All steps completed successfully
            state.status = OperationStatus.COMPLETED
            state.completed_at = datetime.now()

            # Calculate actual duration
            if state.started_at:
                duration = (state.completed_at - state.started_at).total_seconds()
                state.actual_duration_s = duration

            self.state_manager.update_operation(state)

            logger.info(f"Operation {operation_id} completed successfully")

        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error during execution: {e}")

            state.status = OperationStatus.FAILED
            state.error = f"Unexpected error: {str(e)}"
            state.completed_at = datetime.now()

            if state.started_at:
                duration = (state.completed_at - state.started_at).total_seconds()
                state.actual_duration_s = duration

            self.state_manager.update_operation(state)
            raise

        return state

    def _execute_batch(
        self,
        batch: List[ExecutionStep],
        state: OperationState
    ) -> List[Dict[str, Any]]:
        """
        Execute a batch of steps in parallel.

        Args:
            batch: List of steps to execute (can run in parallel)
            state: Current operation state

        Returns:
            List of result dictionaries, one per step
        """
        if len(batch) == 1:
            # Single step - execute directly (no threading overhead)
            step = batch[0]
            state.current_step_id = step.id
            self.state_manager.update_operation(state)
            return [self._execute_step(step, state)]

        # Multiple steps - execute in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
            futures = []

            for step in batch:
                # Update state: this step is about to run
                state.current_step_id = step.id
                self.state_manager.update_operation(state)

                # Submit step execution
                future = executor.submit(self._execute_step, step, state)
                futures.append(future)

            # Wait for all to complete and collect results
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # This shouldn't happen as _execute_step catches exceptions
                    logger.error(f"Unexpected error in future: {e}")
                    results.append({
                        'success': False,
                        'error': f"Unexpected error: {str(e)}"
                    })

        return results

    def _execute_step(
        self,
        step: ExecutionStep,
        state: OperationState
    ) -> Dict[str, Any]:
        """
        Execute a single step.

        Args:
            step: ExecutionStep to execute
            state: Current operation state

        Returns:
            Result dictionary with 'success' and 'result'/'error'
        """
        try:
            logger.debug(f"Executing step {step.id}: {step.name}")

            # Mark step as running
            step.status = StepStatus.RUNNING

            # Call handler
            result = step.handler(step.parameters)

            # Mark step as success
            step.status = StepStatus.SUCCESS
            step.result = result

            return {
                'success': True,
                'result': result
            }

        except Exception as e:
            logger.error(f"Step {step.id} failed: {e}")

            # Mark step as failed
            step.status = StepStatus.FAILED
            step.error = str(e)

            return {
                'success': False,
                'error': str(e)
            }

    def _create_checkpoint(
        self,
        state: OperationState,
        plan: ExecutionPlan
    ) -> Dict[str, Any]:
        """
        Create checkpoint data for resumability.

        Args:
            state: Current operation state
            plan: Execution plan being executed

        Returns:
            Checkpoint data dictionary
        """
        return {
            'completed_steps': list(state.completed_steps),
            'failed_steps': list(state.failed_steps),
            'current_step_id': state.current_step_id,
            'timestamp': datetime.now().isoformat(),
            'progress': plan.get_progress()
        }


if __name__ == "__main__":
    # Example usage
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Initialize
        manager = StateManager(
            db_path=tmpdir / "test.db",
            json_dir=tmpdir / "json"
        )

        executor = StatefulExecutor(state_manager=manager)

        # Create operation
        state = manager.create_operation(
            user_query="setup python dev environment",
            user_id="test_user"
        )

        # Create simple plan
        def mock_handler(params):
            print(f"Executing: {params['name']}")
            return f"Result: {params['name']}"

        stepA = ExecutionStep(
            id="A",
            name="Step A",
            handler=mock_handler,
            parameters={'name': 'A'},
            depends_on=set(),
            provides={'rA'},
            requires=set()
        )

        stepB = ExecutionStep(
            id="B",
            name="Step B",
            handler=mock_handler,
            parameters={'name': 'B'},
            depends_on={'A'},
            provides={'rB'},
            requires={'rA'}
        )

        plan = ExecutionPlan(steps=[stepA, stepB])

        # Execute with state
        print(f"Executing operation: {state.operation_id}")
        result = executor.execute_with_state(plan, state.operation_id)

        print(f"Status: {result.status.value}")
        print(f"Completed steps: {result.completed_steps}")
        print(f"Duration: {result.actual_duration_s:.2f}s")
