"""
Collaborative Caching Network
Allows multiple Luminous Nix instances to share cache for collective intelligence
"""

import json
import time
import hashlib
import threading
import sqlite3
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import socket
import pickle
import struct


@dataclass
class CacheEntry:
    """Represents a cache entry to be shared"""
    query: str
    results: List[Dict]
    timestamp: float
    source_node: str
    confidence: float
    usage_count: int = 1
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NodeInfo:
    """Information about a peer node"""
    node_id: str
    address: str
    port: int
    last_seen: float
    trust_score: float = 0.5
    shared_entries: int = 0
    useful_entries: int = 0


class CollaborativeCacheProtocol:
    """
    Protocol for cache sharing between nodes
    """
    
    # Message types
    HELLO = b'HELLO'
    SHARE = b'SHARE'
    REQUEST = b'REQUEST'
    RESPONSE = b'RESPONSE'
    GOSSIP = b'GOSSIP'
    HEARTBEAT = b'HEARTBEAT'
    
    @staticmethod
    def create_message(msg_type: bytes, data: Any) -> bytes:
        """Create a protocol message"""
        # Serialize data
        payload = pickle.dumps(data)
        
        # Create header with type and length
        header = msg_type + struct.pack('!I', len(payload))
        
        return header + payload
    
    @staticmethod
    def parse_message(data: bytes) -> Tuple[bytes, Any]:
        """Parse a protocol message"""
        if len(data) < 9:  # 5 bytes type + 4 bytes length
            raise ValueError("Invalid message")
        
        msg_type = data[:5]
        payload_len = struct.unpack('!I', data[5:9])[0]
        
        if len(data) < 9 + payload_len:
            raise ValueError("Incomplete message")
        
        payload = pickle.loads(data[9:9 + payload_len])
        
        return msg_type, payload


class CollaborativeCacheNode:
    """
    A node in the collaborative caching network
    Uses peer-to-peer gossip protocol for cache sharing
    """
    
    def __init__(
        self,
        node_id: Optional[str] = None,
        port: int = 0,
        bootstrap_nodes: Optional[List[Tuple[str, int]]] = None
    ):
        """Initialize collaborative cache node"""
        # Node identity
        self.node_id = node_id or self._generate_node_id()
        self.port = port or self._find_free_port()
        
        # Peer management
        self.peers: Dict[str, NodeInfo] = {}
        self.bootstrap_nodes = bootstrap_nodes or []
        
        # Shared cache
        self.shared_cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        
        # Local cache statistics
        self.local_hits = 0
        self.remote_hits = 0
        self.cache_misses = 0
        
        # Trust and reputation
        self.trust_scores: Dict[str, float] = {}
        
        # Gossip management
        self.gossip_history = deque(maxlen=1000)  # Prevent loops
        self.pending_shares = deque(maxlen=100)
        
        # Network threads
        self.server_thread = None
        self.gossip_thread = None
        self.heartbeat_thread = None
        self.stop_event = threading.Event()
        
        # Persistence
        self.db_path = Path.home() / ".cache" / "luminous-nix" / f"collab_{self.node_id}.db"
        self._init_persistence()
        
        # Start network services
        self._start_services()
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        data = f"{socket.gethostname()}{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _find_free_port(self) -> int:
        """Find an available port"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def _init_persistence(self):
        """Initialize persistent storage"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=5000")
        cursor = conn.cursor()
        
        # Peer information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peers (
                node_id TEXT PRIMARY KEY,
                address TEXT,
                port INTEGER,
                last_seen REAL,
                trust_score REAL,
                shared_entries INTEGER,
                useful_entries INTEGER
            )
        """)
        
        # Cache entries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                query_hash TEXT PRIMARY KEY,
                query TEXT,
                results TEXT,
                source_node TEXT,
                confidence REAL,
                usage_count INTEGER,
                timestamp REAL
            )
        """)
        
        # Trust history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trust_events (
                node_id TEXT,
                event_type TEXT,
                value REAL,
                timestamp REAL
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Load saved peers and cache
        self._load_from_persistence()
    
    def _load_from_persistence(self):
        """Load saved data from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Load trusted peers
        cursor.execute("""
            SELECT node_id, address, port, last_seen, trust_score, shared_entries, useful_entries
            FROM peers
            WHERE trust_score > 0.3
            ORDER BY trust_score DESC
            LIMIT 50
        """)
        
        for row in cursor.fetchall():
            peer = NodeInfo(
                node_id=row[0],
                address=row[1],
                port=row[2],
                last_seen=row[3],
                trust_score=row[4],
                shared_entries=row[5],
                useful_entries=row[6]
            )
            self.peers[peer.node_id] = peer
        
        # Load valuable cache entries
        cursor.execute("""
            SELECT query, results, source_node, confidence, usage_count, timestamp
            FROM cache_entries
            WHERE confidence > 0.5
            ORDER BY usage_count DESC
            LIMIT 1000
        """)
        
        for row in cursor.fetchall():
            entry = CacheEntry(
                query=row[0],
                results=json.loads(row[1]),
                source_node=row[2],
                confidence=row[3],
                usage_count=row[4],
                timestamp=row[5]
            )
            self.shared_cache[entry.query] = entry
        
        conn.close()
    
    def _start_services(self):
        """Start network services"""
        # Start server
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()
        
        # Start gossip protocol
        self.gossip_thread = threading.Thread(
            target=self._run_gossip,
            daemon=True
        )
        self.gossip_thread.start()
        
        # Start heartbeat
        self.heartbeat_thread = threading.Thread(
            target=self._run_heartbeat,
            daemon=True
        )
        self.heartbeat_thread.start()
        
        # Bootstrap network connection
        if self.bootstrap_nodes:
            self._bootstrap_network()
    
    def _run_server(self):
        """Run server to accept peer connections"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        server.settimeout(1.0)  # Allow periodic checks
        
        while not self.stop_event.is_set():
            try:
                client, address = server.accept()
                # Handle connection in thread
                threading.Thread(
                    target=self._handle_connection,
                    args=(client, address),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except Exception:
                pass
        
        server.close()
    
    def _handle_connection(self, client: socket.socket, address: Tuple):
        """Handle incoming peer connection"""
        try:
            # Receive message
            data = client.recv(65536)  # Max 64KB message
            
            if data:
                msg_type, payload = CollaborativeCacheProtocol.parse_message(data)
                
                if msg_type == CollaborativeCacheProtocol.HELLO:
                    self._handle_hello(payload, client)
                
                elif msg_type == CollaborativeCacheProtocol.SHARE:
                    self._handle_share(payload)
                
                elif msg_type == CollaborativeCacheProtocol.REQUEST:
                    self._handle_request(payload, client)
                
                elif msg_type == CollaborativeCacheProtocol.GOSSIP:
                    self._handle_gossip(payload)
                
                elif msg_type == CollaborativeCacheProtocol.HEARTBEAT:
                    self._handle_heartbeat(payload)
        
        except Exception:
            pass
        
        finally:
            client.close()
    
    def _handle_hello(self, payload: Dict, client: socket.socket):
        """Handle HELLO message from new peer"""
        peer_info = NodeInfo(**payload)
        
        # Add/update peer
        self.peers[peer_info.node_id] = peer_info
        
        # Send our info back
        response = {
            'node_id': self.node_id,
            'address': socket.gethostname(),
            'port': self.port,
            'last_seen': time.time(),
            'trust_score': 0.5
        }
        
        msg = CollaborativeCacheProtocol.create_message(
            CollaborativeCacheProtocol.HELLO,
            response
        )
        
        try:
            client.send(msg)
        except:
            pass
    
    def _handle_share(self, payload: Dict):
        """Handle SHARE message with cache entry"""
        entry = CacheEntry(**payload)
        
        # Check if we should accept this entry
        if self._should_accept_entry(entry):
            with self.cache_lock:
                # Add or update entry
                if entry.query in self.shared_cache:
                    # Merge with existing
                    existing = self.shared_cache[entry.query]
                    if entry.timestamp > existing.timestamp:
                        self.shared_cache[entry.query] = entry
                else:
                    self.shared_cache[entry.query] = entry
            
            # Update peer statistics
            if entry.source_node in self.peers:
                self.peers[entry.source_node].shared_entries += 1
    
    def _handle_request(self, payload: Dict, client: socket.socket):
        """Handle REQUEST for cache data"""
        query = payload.get('query')
        
        with self.cache_lock:
            if query in self.shared_cache:
                entry = self.shared_cache[query]
                
                # Send response
                msg = CollaborativeCacheProtocol.create_message(
                    CollaborativeCacheProtocol.RESPONSE,
                    entry.to_dict()
                )
                
                try:
                    client.send(msg)
                    
                    # Update usage count
                    entry.usage_count += 1
                    
                except:
                    pass
    
    def _handle_gossip(self, payload: List[Dict]):
        """Handle GOSSIP message with multiple entries"""
        # Prevent loops
        gossip_id = hashlib.md5(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        
        if gossip_id in self.gossip_history:
            return
        
        self.gossip_history.append(gossip_id)
        
        # Process entries
        for entry_data in payload:
            entry = CacheEntry(**entry_data)
            if self._should_accept_entry(entry):
                with self.cache_lock:
                    if entry.query not in self.shared_cache:
                        self.shared_cache[entry.query] = entry
    
    def _handle_heartbeat(self, payload: Dict):
        """Handle HEARTBEAT from peer"""
        node_id = payload.get('node_id')
        
        if node_id in self.peers:
            self.peers[node_id].last_seen = time.time()
    
    def _should_accept_entry(self, entry: CacheEntry) -> bool:
        """Decide whether to accept a cache entry"""
        # Check trust score of source
        if entry.source_node in self.peers:
            trust = self.peers[entry.source_node].trust_score
            if trust < 0.3:
                return False
        
        # Check confidence
        if entry.confidence < 0.5:
            return False
        
        # Check age (not too old)
        age = time.time() - entry.timestamp
        if age > 86400:  # 24 hours
            return False
        
        # Check cache size limits
        with self.cache_lock:
            if len(self.shared_cache) > 10000:
                # Remove least used entries
                sorted_entries = sorted(
                    self.shared_cache.values(),
                    key=lambda x: x.usage_count
                )
                for old_entry in sorted_entries[:1000]:
                    del self.shared_cache[old_entry.query]
        
        return True
    
    def _run_gossip(self):
        """Periodically gossip cache entries to peers"""
        while not self.stop_event.is_set():
            try:
                # Wait 30 seconds between gossip rounds
                if self.stop_event.wait(30):
                    break
                
                # Select entries to gossip
                with self.cache_lock:
                    # Get recent, high-confidence entries
                    candidates = [
                        entry for entry in self.shared_cache.values()
                        if entry.confidence > 0.7 and
                        time.time() - entry.timestamp < 3600  # Last hour
                    ]
                    
                    # Select random subset
                    import random
                    entries_to_share = random.sample(
                        candidates,
                        min(10, len(candidates))
                    )
                
                if entries_to_share:
                    # Gossip to random peers
                    peer_sample = list(self.peers.values())[:5]
                    
                    for peer in peer_sample:
                        self._send_gossip(peer, entries_to_share)
            
            except Exception:
                pass
    
    def _send_gossip(self, peer: NodeInfo, entries: List[CacheEntry]):
        """Send gossip message to peer"""
        try:
            # Connect to peer
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((peer.address, peer.port))
            
            # Send gossip
            payload = [entry.to_dict() for entry in entries]
            msg = CollaborativeCacheProtocol.create_message(
                CollaborativeCacheProtocol.GOSSIP,
                payload
            )
            
            sock.send(msg)
            sock.close()
        
        except:
            # Mark peer as potentially offline
            peer.last_seen = time.time() - 300
    
    def _run_heartbeat(self):
        """Send periodic heartbeats to peers"""
        while not self.stop_event.is_set():
            try:
                # Wait 60 seconds between heartbeats
                if self.stop_event.wait(60):
                    break
                
                # Send heartbeat to all peers
                for peer in list(self.peers.values()):
                    self._send_heartbeat(peer)
                
                # Clean up stale peers
                now = time.time()
                stale_peers = [
                    node_id for node_id, peer in self.peers.items()
                    if now - peer.last_seen > 300  # 5 minutes
                ]
                
                for node_id in stale_peers:
                    del self.peers[node_id]
            
            except Exception:
                pass
    
    def _send_heartbeat(self, peer: NodeInfo):
        """Send heartbeat to peer"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((peer.address, peer.port))
            
            payload = {'node_id': self.node_id}
            msg = CollaborativeCacheProtocol.create_message(
                CollaborativeCacheProtocol.HEARTBEAT,
                payload
            )
            
            sock.send(msg)
            sock.close()
        
        except:
            pass
    
    def _bootstrap_network(self):
        """Connect to bootstrap nodes"""
        for address, port in self.bootstrap_nodes:
            try:
                # Send HELLO to bootstrap node
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((address, port))
                
                payload = {
                    'node_id': self.node_id,
                    'address': socket.gethostname(),
                    'port': self.port,
                    'last_seen': time.time(),
                    'trust_score': 0.5
                }
                
                msg = CollaborativeCacheProtocol.create_message(
                    CollaborativeCacheProtocol.HELLO,
                    payload
                )
                
                sock.send(msg)
                
                # Receive response
                data = sock.recv(65536)
                if data:
                    msg_type, response = CollaborativeCacheProtocol.parse_message(data)
                    if msg_type == CollaborativeCacheProtocol.HELLO:
                        peer = NodeInfo(**response)
                        self.peers[peer.node_id] = peer
                
                sock.close()
            
            except:
                pass
    
    # === Public API ===
    
    def share_cache_entry(
        self,
        query: str,
        results: List[Dict],
        confidence: float = 0.8
    ):
        """Share a cache entry with the network"""
        entry = CacheEntry(
            query=query,
            results=results,
            timestamp=time.time(),
            source_node=self.node_id,
            confidence=confidence
        )
        
        # Add to local shared cache
        with self.cache_lock:
            self.shared_cache[query] = entry
        
        # Queue for gossip
        self.pending_shares.append(entry)
    
    def search_collaborative(self, query: str) -> Optional[List[Dict]]:
        """Search collaborative cache"""
        # Check local shared cache first
        with self.cache_lock:
            if query in self.shared_cache:
                entry = self.shared_cache[query]
                entry.usage_count += 1
                self.remote_hits += 1
                return entry.results
        
        # Request from peers
        for peer in list(self.peers.values())[:3]:  # Ask top 3 peers
            results = self._request_from_peer(peer, query)
            if results:
                # Cache locally
                self.share_cache_entry(query, results, confidence=0.7)
                self.remote_hits += 1
                return results
        
        self.cache_misses += 1
        return None
    
    def _request_from_peer(
        self,
        peer: NodeInfo,
        query: str
    ) -> Optional[List[Dict]]:
        """Request cache entry from specific peer"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((peer.address, peer.port))
            
            # Send request
            payload = {'query': query}
            msg = CollaborativeCacheProtocol.create_message(
                CollaborativeCacheProtocol.REQUEST,
                payload
            )
            sock.send(msg)
            
            # Receive response
            data = sock.recv(65536)
            if data:
                msg_type, response = CollaborativeCacheProtocol.parse_message(data)
                if msg_type == CollaborativeCacheProtocol.RESPONSE:
                    entry = CacheEntry(**response)
                    
                    # Update peer trust
                    peer.useful_entries += 1
                    self._update_trust(peer.node_id, positive=True)
                    
                    return entry.results
            
            sock.close()
        
        except:
            pass
        
        return None
    
    def _update_trust(self, node_id: str, positive: bool):
        """Update trust score for a peer"""
        if node_id in self.peers:
            peer = self.peers[node_id]
            
            # Simple trust update
            if positive:
                peer.trust_score = min(1.0, peer.trust_score * 1.1)
            else:
                peer.trust_score = max(0.0, peer.trust_score * 0.9)
            
            # Save trust event
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trust_events (node_id, event_type, value, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                node_id,
                'positive' if positive else 'negative',
                peer.trust_score,
                time.time()
            ))
            conn.commit()
            conn.close()
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        with self.cache_lock:
            total_entries = len(self.shared_cache)
            avg_confidence = sum(
                e.confidence for e in self.shared_cache.values()
            ) / max(1, total_entries)
        
        return {
            'node_id': self.node_id,
            'port': self.port,
            'peer_count': len(self.peers),
            'active_peers': sum(
                1 for p in self.peers.values()
                if time.time() - p.last_seen < 300
            ),
            'shared_entries': total_entries,
            'avg_confidence': avg_confidence,
            'local_hits': self.local_hits,
            'remote_hits': self.remote_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': (
                (self.local_hits + self.remote_hits) /
                max(1, self.local_hits + self.remote_hits + self.cache_misses)
            )
        }
    
    def save_state(self):
        """Save current state to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Save peers
        for peer in self.peers.values():
            cursor.execute("""
                INSERT OR REPLACE INTO peers
                (node_id, address, port, last_seen, trust_score, shared_entries, useful_entries)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                peer.node_id, peer.address, peer.port, peer.last_seen,
                peer.trust_score, peer.shared_entries, peer.useful_entries
            ))
        
        # Save cache entries
        with self.cache_lock:
            for entry in self.shared_cache.values():
                query_hash = hashlib.md5(entry.query.encode()).hexdigest()
                cursor.execute("""
                    INSERT OR REPLACE INTO cache_entries
                    (query_hash, query, results, source_node, confidence, usage_count, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    query_hash, entry.query, json.dumps(entry.results),
                    entry.source_node, entry.confidence, entry.usage_count, entry.timestamp
                ))
        
        conn.commit()
        conn.close()
    
    def shutdown(self):
        """Clean shutdown"""
        # Stop threads
        self.stop_event.set()
        
        # Save state
        self.save_state()
        
        # Wait for threads
        if self.server_thread:
            self.server_thread.join(timeout=2)
        if self.gossip_thread:
            self.gossip_thread.join(timeout=2)
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)


class CollaborativeCacheManager:
    """
    Manager for collaborative caching in Luminous Nix
    """
    
    def __init__(self, base_cache=None):
        """Initialize collaborative cache manager"""
        self.base_cache = base_cache
        
        # Start collaborative node
        self.node = CollaborativeCacheNode(
            bootstrap_nodes=self._get_bootstrap_nodes()
        )
        
        # Statistics
        self.queries_shared = 0
        self.queries_received = 0
    
    def _get_bootstrap_nodes(self) -> List[Tuple[str, int]]:
        """Get bootstrap nodes from config or defaults"""
        # In production, this would come from config
        # For now, return empty (first node in network)
        return []
    
    def search(self, query: str) -> Tuple[List[Dict], float, str]:
        """Search with collaborative caching"""
        start_time = time.time()
        
        # Try collaborative cache first
        results = self.node.search_collaborative(query)
        
        if results:
            elapsed_ms = (time.time() - start_time) * 1000
            return results, elapsed_ms, "collaborative"
        
        # Fall back to base cache
        if self.base_cache:
            results, elapsed_ms, source = self.base_cache.search_hybrid(query)
            
            # Share successful results
            if results and len(results) > 0:
                self.node.share_cache_entry(
                    query=query,
                    results=results,
                    confidence=0.9
                )
                self.queries_shared += 1
            
            return results, elapsed_ms, source
        
        return [], 0, "none"
    
    def get_stats(self) -> Dict:
        """Get collaborative cache statistics"""
        network_stats = self.node.get_network_stats()
        
        return {
            **network_stats,
            'queries_shared': self.queries_shared,
            'queries_received': self.queries_received,
            'collaboration_ratio': (
                self.queries_received / max(1, self.queries_shared)
            )
        }
    
    def join_network(self, peer_address: str, peer_port: int):
        """Join an existing collaborative network"""
        # Add bootstrap node and connect
        self.node.bootstrap_nodes.append((peer_address, peer_port))
        self.node._bootstrap_network()
    
    def shutdown(self):
        """Clean shutdown"""
        self.node.shutdown()