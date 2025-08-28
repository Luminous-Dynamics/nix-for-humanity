"""
The Resource Steward - Guardian of Exclusive Resources

This sacred guardian manages access to exclusive resources with grace,
creating promises of future access when resources are busy, and ensuring
fair and harmonious sharing among plugins.

"Physical resources, like a microphone or port, can only serve one master 
at a time. We must share with grace."
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that need exclusive access"""
    HARDWARE = "hardware"      # Microphone, camera, etc.
    PORT = "port"              # Network ports
    FILE = "file"              # File locks
    SOCKET = "socket"          # Unix sockets
    SYSTEM = "system"          # System-wide resources


class LeaseStatus(Enum):
    """Status of a resource lease"""
    PENDING = "pending"        # Waiting in queue
    ACTIVE = "active"          # Currently holding resource
    EXPIRED = "expired"        # Lease has expired
    RELEASED = "released"      # Gracefully released


@dataclass
class ResourceLease:
    """A promise of resource access"""
    resource_id: str
    plugin_id: str
    resource_type: ResourceType
    status: LeaseStatus = LeaseStatus.PENDING
    requested_at: datetime = field(default_factory=datetime.now)
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    queue_position: int = 0
    purpose: str = ""
    
    @property
    def is_active(self) -> bool:
        """Whether this lease is currently active"""
        return self.status == LeaseStatus.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        """Whether this lease has expired"""
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        return self.status == LeaseStatus.EXPIRED
    
    @property
    def time_waiting(self) -> timedelta:
        """How long this lease has been waiting"""
        if self.granted_at:
            return self.granted_at - self.requested_at
        return datetime.now() - self.requested_at
    
    @property
    def time_held(self) -> Optional[timedelta]:
        """How long this lease has been held"""
        if self.granted_at:
            if self.status == LeaseStatus.RELEASED:
                # We'd need release time for this
                return None
            return datetime.now() - self.granted_at
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence"""
        return {
            'resource_id': self.resource_id,
            'plugin_id': self.plugin_id,
            'resource_type': self.resource_type.value,
            'status': self.status.value,
            'requested_at': self.requested_at.isoformat(),
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'queue_position': self.queue_position,
            'purpose': self.purpose
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceLease':
        """Create from dictionary"""
        return cls(
            resource_id=data['resource_id'],
            plugin_id=data['plugin_id'],
            resource_type=ResourceType(data['resource_type']),
            status=LeaseStatus(data['status']),
            requested_at=datetime.fromisoformat(data['requested_at']),
            granted_at=datetime.fromisoformat(data['granted_at']) if data.get('granted_at') else None,
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            queue_position=data.get('queue_position', 0),
            purpose=data.get('purpose', '')
        )


@dataclass
class ResourceInfo:
    """Information about a resource"""
    resource_id: str
    resource_type: ResourceType
    description: str
    exclusive: bool = True
    max_lease_duration: Optional[timedelta] = None
    current_holder: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResourceSteward:
    """
    Guardian of exclusive resources in the plugin ecosystem.
    
    This actor manages access to exclusive resources with grace,
    creating promises of future access when resources are busy.
    
    Key responsibilities:
    - Grant exclusive access to resources
    - Maintain fair queuing when resources are busy
    - Create promises of future access
    - Handle graceful release and handover
    - Detect and recover from abandoned resources
    """
    
    def __init__(self, state_path: Optional[Path] = None):
        """Initialize the Resource Steward"""
        self.state_path = state_path or Path.home() / ".luminous-nix" / "resource-state.json"
        
        # Resource registry
        self.resources: Dict[str, ResourceInfo] = {}
        
        # Active leases (resource_id -> lease)
        self.active_leases: Dict[str, ResourceLease] = {}
        
        # Waiting queues (resource_id -> list of leases)
        self.waiting_queues: Dict[str, List[ResourceLease]] = {}
        
        # Notification callbacks
        self.lease_callbacks: Dict[str, Callable] = {}
        
        # Background tasks
        self._tasks: List[asyncio.Task] = []
        self._running = False
        
        # Load persisted state
        self._load_state()
    
    def register_resource(self, resource_info: ResourceInfo):
        """Register a resource that can be leased"""
        self.resources[resource_info.resource_id] = resource_info
        logger.info(f"Registered resource: {resource_info.resource_id}")
    
    async def request_lease(self, 
                          plugin_id: str, 
                          resource_id: str,
                          purpose: str = "",
                          duration: Optional[timedelta] = None) -> ResourceLease:
        """
        Request exclusive access to a resource.
        
        Returns a lease that may be:
        - ACTIVE: Resource granted immediately
        - PENDING: Resource busy, you're in queue
        """
        # Check if resource exists
        if resource_id not in self.resources:
            raise ValueError(f"Unknown resource: {resource_id}")
        
        resource_info = self.resources[resource_id]
        
        # Check if resource is available
        if resource_id not in self.active_leases:
            # Resource is free, grant immediately
            lease = ResourceLease(
                resource_id=resource_id,
                plugin_id=plugin_id,
                resource_type=resource_info.resource_type,
                status=LeaseStatus.ACTIVE,
                granted_at=datetime.now(),
                purpose=purpose
            )
            
            # Set expiration if duration specified
            if duration or resource_info.max_lease_duration:
                lease_duration = duration or resource_info.max_lease_duration
                lease.expires_at = lease.granted_at + lease_duration
            
            self.active_leases[resource_id] = lease
            resource_info.current_holder = plugin_id
            
            logger.info(f"Granted immediate lease for {resource_id} to {plugin_id}")
            
            # Persist state
            self._save_state()
            
            return lease
        
        # Resource is busy, add to queue
        current_lease = self.active_leases[resource_id]
        
        # Check if same plugin already has it
        if current_lease.plugin_id == plugin_id:
            logger.warning(f"{plugin_id} already holds lease for {resource_id}")
            return current_lease
        
        # Create pending lease
        lease = ResourceLease(
            resource_id=resource_id,
            plugin_id=plugin_id,
            resource_type=resource_info.resource_type,
            status=LeaseStatus.PENDING,
            purpose=purpose
        )
        
        # Add to queue
        if resource_id not in self.waiting_queues:
            self.waiting_queues[resource_id] = []
        
        # Check if already in queue
        for existing_lease in self.waiting_queues[resource_id]:
            if existing_lease.plugin_id == plugin_id:
                logger.warning(f"{plugin_id} already in queue for {resource_id}")
                return existing_lease
        
        # Add to queue and set position
        lease.queue_position = len(self.waiting_queues[resource_id]) + 1
        self.waiting_queues[resource_id].append(lease)
        
        logger.info(f"Added {plugin_id} to queue for {resource_id} (position: {lease.queue_position})")
        
        # Persist state
        self._save_state()
        
        return lease
    
    async def release_lease(self, plugin_id: str, resource_id: str):
        """
        Gracefully release a resource lease.
        
        If there are waiting plugins, grants to the next in queue.
        """
        if resource_id not in self.active_leases:
            logger.warning(f"No active lease for {resource_id}")
            return
        
        current_lease = self.active_leases[resource_id]
        
        if current_lease.plugin_id != plugin_id:
            logger.warning(f"{plugin_id} doesn't hold lease for {resource_id}")
            return
        
        # Mark as released
        current_lease.status = LeaseStatus.RELEASED
        del self.active_leases[resource_id]
        
        # Update resource info
        if resource_id in self.resources:
            self.resources[resource_id].current_holder = None
        
        logger.info(f"{plugin_id} released lease for {resource_id}")
        
        # Grant to next in queue if any
        await self._grant_to_next(resource_id)
        
        # Persist state
        self._save_state()
    
    async def _grant_to_next(self, resource_id: str):
        """Grant resource to next plugin in queue"""
        if resource_id not in self.waiting_queues:
            return
        
        queue = self.waiting_queues[resource_id]
        if not queue:
            return
        
        # Get next lease
        next_lease = queue.pop(0)
        
        # Update lease status
        next_lease.status = LeaseStatus.ACTIVE
        next_lease.granted_at = datetime.now()
        next_lease.queue_position = 0
        
        # Set expiration if needed
        resource_info = self.resources.get(resource_id)
        if resource_info and resource_info.max_lease_duration:
            next_lease.expires_at = next_lease.granted_at + resource_info.max_lease_duration
        
        # Make it active
        self.active_leases[resource_id] = next_lease
        
        if resource_info:
            resource_info.current_holder = next_lease.plugin_id
        
        # Update queue positions
        for i, lease in enumerate(queue):
            lease.queue_position = i + 1
        
        logger.info(f"Granted lease for {resource_id} to {next_lease.plugin_id} (was waiting {next_lease.time_waiting})")
        
        # Notify the plugin
        await self._notify_lease_granted(next_lease.plugin_id, next_lease)
    
    async def _notify_lease_granted(self, plugin_id: str, lease: ResourceLease):
        """Notify a plugin that their lease has been granted"""
        if plugin_id in self.lease_callbacks:
            callback = self.lease_callbacks[plugin_id]
            try:
                await callback(lease)
            except Exception as e:
                logger.error(f"Error notifying {plugin_id}: {e}")
    
    def register_callback(self, plugin_id: str, callback: Callable):
        """Register a callback for lease notifications"""
        self.lease_callbacks[plugin_id] = callback
    
    def get_queue_status(self, resource_id: str) -> Dict[str, Any]:
        """Get the current queue status for a resource"""
        status = {
            'resource_id': resource_id,
            'available': resource_id not in self.active_leases,
            'current_holder': None,
            'queue_length': 0,
            'waiting_plugins': []
        }
        
        if resource_id in self.active_leases:
            lease = self.active_leases[resource_id]
            status['current_holder'] = {
                'plugin_id': lease.plugin_id,
                'held_for': str(lease.time_held) if lease.time_held else None,
                'expires_at': lease.expires_at.isoformat() if lease.expires_at else None
            }
        
        if resource_id in self.waiting_queues:
            queue = self.waiting_queues[resource_id]
            status['queue_length'] = len(queue)
            status['waiting_plugins'] = [
                {
                    'plugin_id': lease.plugin_id,
                    'position': lease.queue_position,
                    'waiting_for': str(lease.time_waiting)
                }
                for lease in queue
            ]
        
        return status
    
    async def check_expirations(self):
        """Check for expired leases and reclaim resources"""
        now = datetime.now()
        expired = []
        
        for resource_id, lease in self.active_leases.items():
            if lease.is_expired:
                expired.append(resource_id)
        
        for resource_id in expired:
            lease = self.active_leases[resource_id]
            logger.warning(f"Lease expired for {resource_id} held by {lease.plugin_id}")
            
            # Mark as expired
            lease.status = LeaseStatus.EXPIRED
            del self.active_leases[resource_id]
            
            # Update resource
            if resource_id in self.resources:
                self.resources[resource_id].current_holder = None
            
            # Grant to next
            await self._grant_to_next(resource_id)
        
        if expired:
            self._save_state()
    
    async def start_monitoring(self):
        """Start background monitoring for expired leases"""
        if self._running:
            return
        
        self._running = True
        
        async def monitor_loop():
            while self._running:
                try:
                    await self.check_expirations()
                    await asyncio.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    logger.error(f"Error in monitor loop: {e}")
                    await asyncio.sleep(5)
        
        task = asyncio.create_task(monitor_loop())
        self._tasks.append(task)
        logger.info("Started resource monitoring")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        self._tasks.clear()
        logger.info("Stopped resource monitoring")
    
    def _save_state(self):
        """Persist steward state to disk"""
        state = {
            'resources': {
                rid: {
                    'resource_id': r.resource_id,
                    'resource_type': r.resource_type.value,
                    'description': r.description,
                    'exclusive': r.exclusive,
                    'current_holder': r.current_holder
                }
                for rid, r in self.resources.items()
            },
            'active_leases': {
                rid: lease.to_dict()
                for rid, lease in self.active_leases.items()
            },
            'waiting_queues': {
                rid: [lease.to_dict() for lease in queue]
                for rid, queue in self.waiting_queues.items()
            }
        }
        
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _load_state(self):
        """Load persisted state from disk"""
        if not self.state_path.exists():
            return
        
        try:
            with open(self.state_path) as f:
                state = json.load(f)
            
            # Restore resources
            for rid, rdata in state.get('resources', {}).items():
                self.resources[rid] = ResourceInfo(
                    resource_id=rdata['resource_id'],
                    resource_type=ResourceType(rdata['resource_type']),
                    description=rdata['description'],
                    exclusive=rdata.get('exclusive', True),
                    current_holder=rdata.get('current_holder')
                )
            
            # Restore active leases
            for rid, ldata in state.get('active_leases', {}).items():
                self.active_leases[rid] = ResourceLease.from_dict(ldata)
            
            # Restore waiting queues
            for rid, queue_data in state.get('waiting_queues', {}).items():
                self.waiting_queues[rid] = [
                    ResourceLease.from_dict(ldata) for ldata in queue_data
                ]
            
            logger.info(f"Loaded state: {len(self.resources)} resources, {len(self.active_leases)} active leases")
        
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get steward statistics"""
        total_waiting = sum(len(q) for q in self.waiting_queues.values())
        
        return {
            'resources_registered': len(self.resources),
            'active_leases': len(self.active_leases),
            'plugins_waiting': total_waiting,
            'resources': {
                rid: {
                    'type': r.resource_type.value,
                    'available': rid not in self.active_leases,
                    'holder': r.current_holder,
                    'queue_length': len(self.waiting_queues.get(rid, []))
                }
                for rid, r in self.resources.items()
            }
        }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create steward
        steward = ResourceSteward()
        
        # Register some resources
        steward.register_resource(ResourceInfo(
            resource_id="microphone",
            resource_type=ResourceType.HARDWARE,
            description="System microphone for voice input",
            max_lease_duration=timedelta(minutes=5)
        ))
        
        steward.register_resource(ResourceInfo(
            resource_id="port:8080",
            resource_type=ResourceType.PORT,
            description="HTTP server port",
            max_lease_duration=timedelta(hours=1)
        ))
        
        # Start monitoring
        await steward.start_monitoring()
        
        print("🎪 Resource Steward Activated")
        print("=" * 50)
        
        # Plugin 1 requests microphone
        lease1 = await steward.request_lease(
            "voice-commander",
            "microphone",
            "Voice command input"
        )
        print(f"\nvoice-commander lease: {lease1.status.value}")
        
        # Plugin 2 requests microphone (will queue)
        lease2 = await steward.request_lease(
            "meditation-timer",
            "microphone",
            "Play meditation bell"
        )
        print(f"meditation-timer lease: {lease2.status.value}, position: {lease2.queue_position}")
        
        # Check queue status
        status = steward.get_queue_status("microphone")
        print(f"\nMicrophone queue: {status['queue_length']} waiting")
        
        # Plugin 1 releases
        print("\nvoice-commander releasing...")
        await steward.release_lease("voice-commander", "microphone")
        
        # Check status again
        status = steward.get_queue_status("microphone")
        print(f"New holder: {status['current_holder']}")
        
        # Get statistics
        stats = steward.get_statistics()
        print(f"\n📊 Statistics: {stats}")
        
        # Stop monitoring
        await steward.stop_monitoring()
    
    asyncio.run(main())