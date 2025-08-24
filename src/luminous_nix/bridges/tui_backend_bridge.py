"""
TUI to Backend Bridge - Progressive Interface Integration

This bridge connects the Terminal User Interface to the backend executor,
enabling gradual migration from display-only to fully interactive operation.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from queue import Queue, Empty
import threading

logger = logging.getLogger(__name__)


class InteractionMode(Enum):
    """Progressive interaction modes"""
    DISPLAY_ONLY = "display"      # TUI shows info, no interaction
    READ_ONLY = "read"            # TUI reads backend state
    SUGGEST = "suggest"           # TUI suggests actions
    CONFIRM = "confirm"           # TUI actions need confirmation
    FULL_CONTROL = "control"      # TUI has full control


class EventType(Enum):
    """Types of events between TUI and backend"""
    # From TUI to Backend
    USER_INPUT = "user_input"
    COMMAND_REQUEST = "command_request"
    SEARCH_QUERY = "search_query"
    CONFIG_CHANGE = "config_change"
    
    # From Backend to TUI
    STATUS_UPDATE = "status_update"
    RESULT_READY = "result_ready"
    ERROR_OCCURRED = "error_occurred"
    PROGRESS_UPDATE = "progress_update"
    
    # Bidirectional
    HEARTBEAT = "heartbeat"
    SYNC_STATE = "sync_state"


@dataclass
class BridgeEvent:
    """Event passed between TUI and backend"""
    timestamp: str
    event_type: EventType
    source: str  # 'tui' or 'backend'
    target: str  # 'tui' or 'backend'
    payload: Dict[str, Any]
    requires_response: bool = False
    correlation_id: Optional[str] = None
    

@dataclass
class BridgeMetrics:
    """Metrics for bridge performance"""
    events_sent: int = 0
    events_received: int = 0
    events_dropped: int = 0
    average_latency_ms: float = 0.0
    errors_count: int = 0
    last_activity: Optional[str] = None


class TUIBackendBridge:
    """
    Bridges Terminal User Interface to Backend with progressive activation.
    
    This allows gradual migration from display-only TUI to fully interactive
    interface as the connection becomes more stable and features mature.
    """
    
    def __init__(self, readiness: float = 0.3):
        """
        Initialize bridge with readiness level.
        
        Args:
            readiness: Current readiness (0.0 to 1.0)
                      0.0-0.2: Display only
                      0.2-0.4: Read backend state
                      0.4-0.6: Suggest actions
                      0.6-0.8: Confirm before execute
                      0.8-1.0: Full control
        """
        self.readiness = readiness
        self.interaction_mode = self._determine_interaction_mode()
        
        # Event queues for async communication
        self.tui_to_backend: Queue[BridgeEvent] = Queue(maxsize=100)
        self.backend_to_tui: Queue[BridgeEvent] = Queue(maxsize=100)
        
        # Event handlers
        self.tui_handlers: Dict[EventType, List[Callable]] = {}
        self.backend_handlers: Dict[EventType, List[Callable]] = {}
        
        # Connection state
        self.is_connected = False
        self.backend_available = False
        self.tui_available = False
        
        # Metrics
        self.metrics = BridgeMetrics()
        self.event_history: List[BridgeEvent] = []
        
        # Start event processing threads
        self._start_event_processors()
        
        logger.info(f"TUI-Backend Bridge initialized: {self.interaction_mode.value} mode (readiness: {self.readiness:.1%})")
    
    def _determine_interaction_mode(self) -> InteractionMode:
        """Determine interaction mode based on readiness"""
        if self.readiness < 0.2:
            return InteractionMode.DISPLAY_ONLY
        elif self.readiness < 0.4:
            return InteractionMode.READ_ONLY
        elif self.readiness < 0.6:
            return InteractionMode.SUGGEST
        elif self.readiness < 0.8:
            return InteractionMode.CONFIRM
        else:
            return InteractionMode.FULL_CONTROL
    
    def _start_event_processors(self):
        """Start background threads for event processing"""
        # TUI event processor
        self.tui_processor = threading.Thread(
            target=self._process_tui_events,
            daemon=True,
            name="TUI-Event-Processor"
        )
        self.tui_processor.start()
        
        # Backend event processor
        self.backend_processor = threading.Thread(
            target=self._process_backend_events,
            daemon=True,
            name="Backend-Event-Processor"
        )
        self.backend_processor.start()
    
    def _process_tui_events(self):
        """Process events from TUI to backend"""
        while True:
            try:
                event = self.tui_to_backend.get(timeout=1.0)
                self._handle_tui_event(event)
                self.metrics.events_received += 1
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing TUI event: {e}")
                self.metrics.errors_count += 1
    
    def _process_backend_events(self):
        """Process events from backend to TUI"""
        while True:
            try:
                event = self.backend_to_tui.get(timeout=1.0)
                self._handle_backend_event(event)
                self.metrics.events_received += 1
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing backend event: {e}")
                self.metrics.errors_count += 1
    
    def _handle_tui_event(self, event: BridgeEvent):
        """Handle event from TUI"""
        # Check if we can process this event at current readiness
        if not self._can_process_event(event):
            logger.debug(f"Event {event.event_type} blocked at readiness {self.readiness:.1%}")
            self.metrics.events_dropped += 1
            return
        
        # Route to registered handlers
        handlers = self.backend_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")
        
        # Record in history
        self.event_history.append(event)
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]  # Keep last 500
    
    def _handle_backend_event(self, event: BridgeEvent):
        """Handle event from backend"""
        # Backend events are always processed (they're informational)
        handlers = self.tui_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")
        
        # Record in history
        self.event_history.append(event)
    
    def _can_process_event(self, event: BridgeEvent) -> bool:
        """Check if event can be processed at current readiness"""
        # Display only mode - no events processed
        if self.interaction_mode == InteractionMode.DISPLAY_ONLY:
            return False
        
        # Read only - only status queries allowed
        if self.interaction_mode == InteractionMode.READ_ONLY:
            return event.event_type in [EventType.HEARTBEAT, EventType.SYNC_STATE]
        
        # Suggest mode - queries allowed but not commands
        if self.interaction_mode == InteractionMode.SUGGEST:
            return event.event_type not in [EventType.COMMAND_REQUEST, EventType.CONFIG_CHANGE]
        
        # Confirm mode - all events allowed but will need confirmation
        # Full control - all events allowed
        return True
    
    def send_from_tui(self, event_type: EventType, payload: Dict[str, Any],
                      requires_response: bool = False) -> Optional[str]:
        """
        Send event from TUI to backend.
        
        Args:
            event_type: Type of event
            payload: Event data
            requires_response: Whether response is expected
            
        Returns:
            Correlation ID if response required, None otherwise
        """
        correlation_id = None
        if requires_response:
            correlation_id = f"tui-{datetime.now().timestamp()}"
        
        event = BridgeEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            source='tui',
            target='backend',
            payload=payload,
            requires_response=requires_response,
            correlation_id=correlation_id
        )
        
        # Check if we should process this
        if self.interaction_mode == InteractionMode.DISPLAY_ONLY:
            logger.debug(f"Display-only mode: dropping {event_type}")
            return None
        
        # Add confirmation wrapper if needed
        if self.interaction_mode == InteractionMode.CONFIRM:
            if event_type in [EventType.COMMAND_REQUEST, EventType.CONFIG_CHANGE]:
                event.payload['requires_confirmation'] = True
                event.payload['confirmation_message'] = f"Execute: {payload.get('command', 'action')}?"
        
        try:
            self.tui_to_backend.put_nowait(event)
            self.metrics.events_sent += 1
            self.metrics.last_activity = datetime.now().isoformat()
            
            # Adjust readiness based on success
            self.adjust_readiness(0.001)
            
            return correlation_id
        except:
            logger.warning(f"Queue full, dropping event {event_type}")
            self.metrics.events_dropped += 1
            self.adjust_readiness(-0.01)
            return None
    
    def send_from_backend(self, event_type: EventType, payload: Dict[str, Any],
                          correlation_id: Optional[str] = None) -> bool:
        """
        Send event from backend to TUI.
        
        Args:
            event_type: Type of event
            payload: Event data
            correlation_id: Optional correlation for responses
            
        Returns:
            Success status
        """
        event = BridgeEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            source='backend',
            target='tui',
            payload=payload,
            requires_response=False,
            correlation_id=correlation_id
        )
        
        try:
            self.backend_to_tui.put_nowait(event)
            self.metrics.events_sent += 1
            self.metrics.last_activity = datetime.now().isoformat()
            return True
        except:
            logger.warning(f"Queue full, dropping event {event_type}")
            self.metrics.events_dropped += 1
            return False
    
    def register_tui_handler(self, event_type: EventType, handler: Callable):
        """Register handler for events going to TUI"""
        if event_type not in self.tui_handlers:
            self.tui_handlers[event_type] = []
        self.tui_handlers[event_type].append(handler)
        logger.debug(f"Registered TUI handler for {event_type}")
    
    def register_backend_handler(self, event_type: EventType, handler: Callable):
        """Register handler for events going to backend"""
        if event_type not in self.backend_handlers:
            self.backend_handlers[event_type] = []
        self.backend_handlers[event_type].append(handler)
        logger.debug(f"Registered backend handler for {event_type}")
    
    def connect_tui(self, tui_instance: Any) -> bool:
        """
        Connect to TUI instance.
        
        Args:
            tui_instance: The TUI object to connect
            
        Returns:
            Success status
        """
        try:
            # Check if TUI has required methods
            required_methods = ['update_display', 'get_user_input']
            for method in required_methods:
                if not hasattr(tui_instance, method):
                    logger.warning(f"TUI missing required method: {method}")
                    return False
            
            # Register default handlers
            self.register_tui_handler(
                EventType.STATUS_UPDATE,
                lambda e: tui_instance.update_display(e.payload)
            )
            
            self.tui_available = True
            self.is_connected = self.tui_available and self.backend_available
            
            # Send connection event
            self.send_from_backend(
                EventType.STATUS_UPDATE,
                {'message': 'TUI connected', 'mode': self.interaction_mode.value}
            )
            
            logger.info("TUI connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect TUI: {e}")
            return False
    
    def connect_backend(self, backend_instance: Any) -> bool:
        """
        Connect to backend instance.
        
        Args:
            backend_instance: The backend object to connect
            
        Returns:
            Success status
        """
        try:
            # Check if backend has required methods
            required_methods = ['execute', 'get_status']
            for method in required_methods:
                if not hasattr(backend_instance, method):
                    logger.warning(f"Backend missing required method: {method}")
                    return False
            
            # Register default handlers
            self.register_backend_handler(
                EventType.COMMAND_REQUEST,
                lambda e: self._execute_command(backend_instance, e)
            )
            
            self.backend_available = True
            self.is_connected = self.tui_available and self.backend_available
            
            # Send connection event
            self.send_from_tui(
                EventType.STATUS_UPDATE,
                {'message': 'Backend connected', 'mode': self.interaction_mode.value}
            )
            
            logger.info("Backend connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect backend: {e}")
            return False
    
    def _execute_command(self, backend: Any, event: BridgeEvent):
        """Execute command on backend"""
        command = event.payload.get('command')
        if not command:
            return
        
        try:
            # Execute based on interaction mode
            if self.interaction_mode == InteractionMode.SUGGEST:
                # Only suggest, don't execute
                suggestion = f"Would execute: {command}"
                self.send_from_backend(
                    EventType.RESULT_READY,
                    {'suggestion': suggestion, 'executed': False},
                    event.correlation_id
                )
            
            elif self.interaction_mode in [InteractionMode.CONFIRM, InteractionMode.FULL_CONTROL]:
                # Execute the command
                result = backend.execute(command)
                self.send_from_backend(
                    EventType.RESULT_READY,
                    {'result': result, 'executed': True},
                    event.correlation_id
                )
                
                # Update readiness based on success
                if result.get('success'):
                    self.adjust_readiness(0.005)
                else:
                    self.adjust_readiness(-0.01)
                    
        except Exception as e:
            self.send_from_backend(
                EventType.ERROR_OCCURRED,
                {'error': str(e), 'command': command},
                event.correlation_id
            )
            self.adjust_readiness(-0.02)
    
    def sync_state(self) -> Dict[str, Any]:
        """
        Synchronize state between TUI and backend.
        
        Returns:
            Current synchronized state
        """
        state = {
            'interaction_mode': self.interaction_mode.value,
            'readiness': self.readiness,
            'is_connected': self.is_connected,
            'tui_available': self.tui_available,
            'backend_available': self.backend_available,
            'metrics': asdict(self.metrics),
            'can_execute': self.interaction_mode in [
                InteractionMode.CONFIRM,
                InteractionMode.FULL_CONTROL
            ],
            'needs_confirmation': self.interaction_mode == InteractionMode.CONFIRM
        }
        
        # Send sync event to both sides
        self.send_from_backend(EventType.SYNC_STATE, state)
        self.send_from_tui(EventType.SYNC_STATE, state)
        
        return state
    
    def adjust_readiness(self, delta: float):
        """Adjust readiness level based on performance"""
        old_readiness = self.readiness
        self.readiness = max(0.0, min(1.0, self.readiness + delta))
        
        # Check if interaction mode should change
        new_mode = self._determine_interaction_mode()
        if new_mode != self.interaction_mode:
            logger.info(f"Interaction mode advancing: {self.interaction_mode.value} → {new_mode.value}")
            self.interaction_mode = new_mode
            
            # Notify both sides of mode change
            notification = {
                'old_mode': self.interaction_mode.value,
                'new_mode': new_mode.value,
                'readiness': self.readiness
            }
            self.send_from_backend(EventType.STATUS_UPDATE, notification)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        # Calculate average latency from recent events
        recent_events = self.event_history[-100:]
        latencies = []
        for i in range(1, len(recent_events)):
            if recent_events[i].correlation_id == recent_events[i-1].correlation_id:
                t1 = datetime.fromisoformat(recent_events[i-1].timestamp)
                t2 = datetime.fromisoformat(recent_events[i].timestamp)
                latencies.append((t2 - t1).total_seconds() * 1000)
        
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        return {
            'readiness': self.readiness,
            'interaction_mode': self.interaction_mode.value,
            'is_connected': self.is_connected,
            'events_sent': self.metrics.events_sent,
            'events_received': self.metrics.events_received,
            'events_dropped': self.metrics.events_dropped,
            'errors_count': self.metrics.errors_count,
            'average_latency_ms': avg_latency,
            'queue_sizes': {
                'tui_to_backend': self.tui_to_backend.qsize(),
                'backend_to_tui': self.backend_to_tui.qsize()
            },
            'handlers_registered': {
                'tui': len(self.tui_handlers),
                'backend': len(self.backend_handlers)
            }
        }
    
    def progressive_test(self) -> bool:
        """Test bridge with progressive complexity"""
        results = []
        
        # Test 1: Basic event sending
        if self.readiness >= 0.2:
            correlation_id = self.send_from_tui(
                EventType.HEARTBEAT,
                {'test': 'basic'}
            )
            results.append(correlation_id is not None)
            logger.info(f"Basic send test: {'✓' if results[-1] else '✗'}")
        
        # Test 2: Handler registration and execution
        if self.readiness >= 0.4:
            test_received = []
            self.register_backend_handler(
                EventType.SEARCH_QUERY,
                lambda e: test_received.append(e)
            )
            self.send_from_tui(EventType.SEARCH_QUERY, {'query': 'test'})
            # Give it time to process
            import time
            time.sleep(0.1)
            results.append(len(test_received) > 0)
            logger.info(f"Handler test: {'✓' if results[-1] else '✗'}")
        
        # Test 3: Bidirectional communication
        if self.readiness >= 0.6:
            backend_received = []
            tui_received = []
            
            self.register_backend_handler(
                EventType.USER_INPUT,
                lambda e: backend_received.append(e)
            )
            self.register_tui_handler(
                EventType.RESULT_READY,
                lambda e: tui_received.append(e)
            )
            
            # Send from TUI
            self.send_from_tui(EventType.USER_INPUT, {'input': 'test'})
            # Send response from backend
            self.send_from_backend(EventType.RESULT_READY, {'result': 'ok'})
            
            import time
            time.sleep(0.1)
            
            results.append(len(backend_received) > 0 and len(tui_received) > 0)
            logger.info(f"Bidirectional test: {'✓' if results[-1] else '✗'}")
        
        # Adjust readiness based on results
        if all(results):
            self.adjust_readiness(0.05)
            logger.info("✅ All bridge tests passed")
            return True
        else:
            self.adjust_readiness(-0.02)
            logger.warning(f"⚠️ Some bridge tests failed: {results}")
            return False


# Integration helper
def integrate_tui_with_backend(tui, backend, initial_readiness: float = 0.4):
    """
    Helper to integrate TUI with backend through the bridge.
    
    Args:
        tui: TUI instance
        backend: Backend instance
        initial_readiness: Starting readiness level
        
    Returns:
        Configured bridge instance
    """
    bridge = TUIBackendBridge(readiness=initial_readiness)
    
    # Connect both sides
    tui_connected = bridge.connect_tui(tui)
    backend_connected = bridge.connect_backend(backend)
    
    if tui_connected and backend_connected:
        logger.info("✅ TUI and Backend successfully bridged")
        
        # Perform initial sync
        bridge.sync_state()
        
        # Run progressive test
        bridge.progressive_test()
        
        return bridge
    else:
        logger.error("Failed to establish bridge")
        return None


# Example mock TUI for testing
class MockTUI:
    """Mock TUI for testing bridge"""
    
    def __init__(self):
        self.display_buffer = []
        self.input_buffer = []
    
    def update_display(self, data: Dict[str, Any]):
        """Update display with data"""
        self.display_buffer.append(data)
        logger.debug(f"TUI display updated: {data}")
    
    def get_user_input(self) -> Optional[str]:
        """Get user input"""
        if self.input_buffer:
            return self.input_buffer.pop(0)
        return None


# Example mock backend for testing
class MockBackend:
    """Mock backend for testing bridge"""
    
    def __init__(self):
        self.command_history = []
        self.status = {'ready': True}
    
    def execute(self, command: str) -> Dict[str, Any]:
        """Execute command"""
        self.command_history.append(command)
        
        # Simulate different results
        if 'error' in command:
            return {'success': False, 'error': 'Simulated error'}
        elif 'search' in command:
            return {'success': True, 'results': ['item1', 'item2']}
        else:
            return {'success': True, 'output': f"Executed: {command}"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get backend status"""
        return self.status