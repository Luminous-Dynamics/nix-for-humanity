"""WebSocket support for real-time features in Nix for Humanity."""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from flask import Flask, request
from flask_socketio import (
    ConnectionRefusedError,
    Namespace,
    SocketIO,
    disconnect,
    emit,
    join_room,
    leave_room,
    rooms,
)

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket message types."""
    
    # Connection management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Command execution
    COMMAND_REQUEST = "command_request"
    COMMAND_RESPONSE = "command_response"
    COMMAND_PROGRESS = "command_progress"
    COMMAND_ERROR = "command_error"
    
    # Streaming
    STREAM_START = "stream_start"
    STREAM_DATA = "stream_data"
    STREAM_END = "stream_end"
    
    # Learning
    LEARNING_UPDATE = "learning_update"
    SUGGESTION = "suggestion"
    
    # System
    SYSTEM_STATUS = "system_status"
    NOTIFICATION = "notification"


@dataclass
class WebSocketMessage:
    """WebSocket message format."""
    
    id: str
    type: MessageType
    data: Any
    timestamp: float = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        """Set defaults."""
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebSocketMessage":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=MessageType(data["type"]),
            data=data["data"],
            timestamp=data.get("timestamp", time.time()),
            session_id=data.get("session_id"),
        )


class SessionManager:
    """Manage WebSocket sessions."""
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, Set[str]] = {}
        self.active_commands: Dict[str, str] = {}
    
    def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new session.
        
        Args:
            session_id: Session identifier
            user_id: Optional user identifier
            metadata: Optional session metadata
            
        Returns:
            Session data
        """
        session = {
            "id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "rooms": set(),
        }
        
        self.sessions[session_id] = session
        
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
        
        logger.info(f"Session created: {session_id} for user: {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None
        """
        return self.sessions.get(session_id)
    
    def update_activity(self, session_id: str) -> None:
        """Update session last activity.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
    
    def remove_session(self, session_id: str) -> None:
        """Remove a session.
        
        Args:
            session_id: Session identifier
        """
        session = self.sessions.pop(session_id, None)
        
        if session and session["user_id"]:
            user_id = session["user_id"]
            if user_id in self.user_sessions:
                self.user_sessions[user_id].discard(session_id)
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]
        
        # Clean up active commands
        if session_id in self.active_commands:
            del self.active_commands[session_id]
        
        logger.info(f"Session removed: {session_id}")
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session IDs
        """
        return list(self.user_sessions.get(user_id, []))


class NixHumanityNamespace(Namespace):
    """WebSocket namespace for Nix for Humanity."""
    
    def __init__(self, namespace: str, session_manager: SessionManager):
        """Initialize namespace.
        
        Args:
            namespace: Namespace path
            session_manager: Session manager instance
        """
        super().__init__(namespace)
        self.session_manager = session_manager
    
    def on_connect(self, auth: Optional[Dict[str, Any]] = None):
        """Handle client connection.
        
        Args:
            auth: Authentication data
        """
        session_id = request.sid
        user_id = None
        
        # Extract user from auth if provided
        if auth:
            user_id = auth.get("user_id")
            
            # Verify authentication
            if not self._verify_auth(auth):
                logger.warning(f"Connection refused for session: {session_id}")
                raise ConnectionRefusedError("Authentication failed")
        
        # Create session
        self.session_manager.create_session(
            session_id,
            user_id,
            metadata={"auth": auth} if auth else None,
        )
        
        # Join personal room
        join_room(session_id)
        
        # Join user room if authenticated
        if user_id:
            join_room(f"user:{user_id}")
        
        # Send connection confirmation
        emit(
            MessageType.CONNECT.value,
            WebSocketMessage(
                id=str(uuid.uuid4()),
                type=MessageType.CONNECT,
                data={
                    "session_id": session_id,
                    "user_id": user_id,
                    "status": "connected",
                },
                session_id=session_id,
            ).to_dict(),
        )
        
        logger.info(f"Client connected: {session_id}")
    
    def on_disconnect(self):
        """Handle client disconnection."""
        session_id = request.sid
        
        # Leave all rooms
        for room in rooms(sid=session_id):
            if room != session_id:
                leave_room(room)
        
        # Remove session
        self.session_manager.remove_session(session_id)
        
        logger.info(f"Client disconnected: {session_id}")
    
    def on_ping(self, data: Dict[str, Any]):
        """Handle ping message.
        
        Args:
            data: Ping data
        """
        session_id = request.sid
        self.session_manager.update_activity(session_id)
        
        # Send pong response
        emit(
            MessageType.PONG.value,
            WebSocketMessage(
                id=data.get("id", str(uuid.uuid4())),
                type=MessageType.PONG,
                data={"timestamp": time.time()},
                session_id=session_id,
            ).to_dict(),
        )
    
    def on_command_request(self, data: Dict[str, Any]):
        """Handle command execution request.
        
        Args:
            data: Command request data
        """
        session_id = request.sid
        self.session_manager.update_activity(session_id)
        
        command_id = str(uuid.uuid4())
        command = data.get("command", "")
        options = data.get("options", {})
        
        # Store active command
        self.session_manager.active_commands[session_id] = command_id
        
        # Send acknowledgment
        emit(
            MessageType.COMMAND_PROGRESS.value,
            WebSocketMessage(
                id=command_id,
                type=MessageType.COMMAND_PROGRESS,
                data={
                    "status": "received",
                    "message": "Command received, processing...",
                },
                session_id=session_id,
            ).to_dict(),
        )
        
        # Process command asynchronously
        self._process_command_async(session_id, command_id, command, options)
    
    def on_stream_start(self, data: Dict[str, Any]):
        """Handle stream start request.
        
        Args:
            data: Stream configuration
        """
        session_id = request.sid
        stream_id = str(uuid.uuid4())
        stream_type = data.get("type", "command")
        
        # Join stream room
        join_room(f"stream:{stream_id}")
        
        # Send confirmation
        emit(
            MessageType.STREAM_START.value,
            WebSocketMessage(
                id=stream_id,
                type=MessageType.STREAM_START,
                data={
                    "stream_id": stream_id,
                    "type": stream_type,
                    "status": "started",
                },
                session_id=session_id,
            ).to_dict(),
        )
        
        # Start streaming
        self._start_streaming(session_id, stream_id, stream_type)
    
    def on_stream_end(self, data: Dict[str, Any]):
        """Handle stream end request.
        
        Args:
            data: Stream identifier
        """
        session_id = request.sid
        stream_id = data.get("stream_id")
        
        # Leave stream room
        leave_room(f"stream:{stream_id}")
        
        # Send confirmation
        emit(
            MessageType.STREAM_END.value,
            WebSocketMessage(
                id=stream_id,
                type=MessageType.STREAM_END,
                data={"status": "ended"},
                session_id=session_id,
            ).to_dict(),
        )
    
    def _verify_auth(self, auth: Dict[str, Any]) -> bool:
        """Verify authentication.
        
        Args:
            auth: Authentication data
            
        Returns:
            True if authenticated
        """
        # TODO: Implement actual authentication
        token = auth.get("token")
        return token is not None
    
    def _process_command_async(
        self,
        session_id: str,
        command_id: str,
        command: str,
        options: Dict[str, Any],
    ) -> None:
        """Process command asynchronously.
        
        Args:
            session_id: Session identifier
            command_id: Command identifier
            command: Natural language command
            options: Command options
        """
        # TODO: Integrate with actual command processing
        
        # Simulate processing
        emit(
            MessageType.COMMAND_PROGRESS.value,
            WebSocketMessage(
                id=command_id,
                type=MessageType.COMMAND_PROGRESS,
                data={
                    "status": "processing",
                    "progress": 0.5,
                    "message": "Analyzing command...",
                },
                session_id=session_id,
            ).to_dict(),
            room=session_id,
        )
        
        # Send response
        emit(
            MessageType.COMMAND_RESPONSE.value,
            WebSocketMessage(
                id=command_id,
                type=MessageType.COMMAND_RESPONSE,
                data={
                    "command": command,
                    "result": f"Executed: {command}",
                    "success": True,
                    "confidence": 0.95,
                },
                session_id=session_id,
            ).to_dict(),
            room=session_id,
        )
        
        # Clean up
        if session_id in self.session_manager.active_commands:
            del self.session_manager.active_commands[session_id]
    
    def _start_streaming(
        self,
        session_id: str,
        stream_id: str,
        stream_type: str,
    ) -> None:
        """Start streaming data.
        
        Args:
            session_id: Session identifier
            stream_id: Stream identifier
            stream_type: Type of stream
        """
        # TODO: Implement actual streaming
        
        # Simulate streaming
        for i in range(5):
            emit(
                MessageType.STREAM_DATA.value,
                WebSocketMessage(
                    id=stream_id,
                    type=MessageType.STREAM_DATA,
                    data={
                        "chunk": f"Data chunk {i + 1}",
                        "index": i,
                    },
                    session_id=session_id,
                ).to_dict(),
                room=f"stream:{stream_id}",
            )


class WebSocketManager:
    """Manage WebSocket connections and events."""
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize WebSocket manager.
        
        Args:
            app: Flask application
        """
        self.socketio: Optional[SocketIO] = None
        self.session_manager = SessionManager()
        self.namespaces: Dict[str, Namespace] = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> SocketIO:
        """Initialize with Flask app.
        
        Args:
            app: Flask application
            
        Returns:
            Configured SocketIO instance
        """
        # Create SocketIO instance
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode="threading",
            ping_timeout=60,
            ping_interval=30,
            logger=True,
            engineio_logger=False,
        )
        
        # Register main namespace
        main_namespace = NixHumanityNamespace(
            "/ws",
            self.session_manager,
        )
        self.socketio.on_namespace(main_namespace)
        self.namespaces["/ws"] = main_namespace
        
        # Register admin namespace
        admin_namespace = AdminNamespace(
            "/ws/admin",
            self.session_manager,
        )
        self.socketio.on_namespace(admin_namespace)
        self.namespaces["/ws/admin"] = admin_namespace
        
        logger.info("WebSocket manager initialized")
        return self.socketio
    
    def broadcast(
        self,
        event: MessageType,
        data: Any,
        namespace: str = "/ws",
        room: Optional[str] = None,
    ) -> None:
        """Broadcast message to clients.
        
        Args:
            event: Event type
            data: Message data
            namespace: Target namespace
            room: Optional room to broadcast to
        """
        if not self.socketio:
            return
        
        message = WebSocketMessage(
            id=str(uuid.uuid4()),
            type=event,
            data=data,
        )
        
        self.socketio.emit(
            event.value,
            message.to_dict(),
            namespace=namespace,
            room=room,
        )
    
    def send_to_user(
        self,
        user_id: str,
        event: MessageType,
        data: Any,
        namespace: str = "/ws",
    ) -> None:
        """Send message to specific user.
        
        Args:
            user_id: User identifier
            event: Event type
            data: Message data
            namespace: Target namespace
        """
        self.broadcast(
            event,
            data,
            namespace=namespace,
            room=f"user:{user_id}",
        )
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions.
        
        Returns:
            List of session data
        """
        return list(self.session_manager.sessions.values())


class AdminNamespace(Namespace):
    """Admin WebSocket namespace."""
    
    def __init__(self, namespace: str, session_manager: SessionManager):
        """Initialize admin namespace.
        
        Args:
            namespace: Namespace path
            session_manager: Session manager instance
        """
        super().__init__(namespace)
        self.session_manager = session_manager
    
    def on_connect(self, auth: Optional[Dict[str, Any]] = None):
        """Handle admin connection."""
        if not auth or not self._verify_admin(auth):
            raise ConnectionRefusedError("Admin authentication required")
        
        session_id = request.sid
        join_room("admins")
        
        emit("admin_connected", {"session_id": session_id})
        logger.info(f"Admin connected: {session_id}")
    
    def on_disconnect(self):
        """Handle admin disconnection."""
        session_id = request.sid
        leave_room("admins")
        logger.info(f"Admin disconnected: {session_id}")
    
    def on_get_sessions(self):
        """Get all active sessions."""
        sessions = self.session_manager.sessions
        emit("sessions", {"sessions": list(sessions.values())})
    
    def on_broadcast_notification(self, data: Dict[str, Any]):
        """Broadcast notification to all users."""
        message = data.get("message", "")
        level = data.get("level", "info")
        
        # Broadcast to main namespace
        emit(
            MessageType.NOTIFICATION.value,
            {
                "message": message,
                "level": level,
                "timestamp": time.time(),
            },
            namespace="/ws",
            broadcast=True,
        )
    
    def _verify_admin(self, auth: Dict[str, Any]) -> bool:
        """Verify admin authentication.
        
        Args:
            auth: Authentication data
            
        Returns:
            True if admin
        """
        # TODO: Implement actual admin verification
        return auth.get("admin_token") == "admin_secret"