//! Ticket Management for Iroh Connections
//!
//! Handles creation, validation, and exchange of connection tickets
//! between peers. Tickets are the mechanism by which peers establish
//! direct QUIC connections.

use crate::swarm::{SwarmResult, SwarmError, ConnectionTicket};
use std::collections::HashMap;
use std::time::{Duration, SystemTime};
use parking_lot::RwLock;

/// Manages connection tickets for peer discovery and connection
#[allow(dead_code)] // Fields reserved for ticket expiration/validation
pub struct TicketManager {
    /// Tickets we've created for others to connect to us
    outgoing_tickets: RwLock<HashMap<String, TicketEntry>>,

    /// Tickets we've received from others
    incoming_tickets: RwLock<HashMap<String, TicketEntry>>,

    /// Default ticket expiration
    default_expiration: Duration,
}

/// An entry in the ticket cache
#[allow(dead_code)] // Fields reserved for expiration tracking
struct TicketEntry {
    ticket: ConnectionTicket,
    created_at: SystemTime,
    use_count: usize,
}

impl TicketManager {
    /// Create a new ticket manager
    pub fn new() -> Self {
        Self {
            outgoing_tickets: RwLock::new(HashMap::new()),
            incoming_tickets: RwLock::new(HashMap::new()),
            default_expiration: Duration::from_secs(3600), // 1 hour
        }
    }

    /// Create a new ticket manager with custom expiration
    #[allow(dead_code)] // Reserved for future use
    pub fn with_expiration(expiration: Duration) -> Self {
        Self {
            outgoing_tickets: RwLock::new(HashMap::new()),
            incoming_tickets: RwLock::new(HashMap::new()),
            default_expiration: expiration,
        }
    }

    /// Store an outgoing ticket (one we created for others)
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn store_outgoing(&self, ticket: ConnectionTicket) {
        let entry = TicketEntry {
            ticket: ticket.clone(),
            created_at: SystemTime::now(),
            use_count: 0,
        };
        self.outgoing_tickets.write().insert(ticket.node_id.clone(), entry);
    }

    /// Store an incoming ticket (one we received from a peer)
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn store_incoming(&self, ticket: ConnectionTicket) {
        let entry = TicketEntry {
            ticket: ticket.clone(),
            created_at: SystemTime::now(),
            use_count: 0,
        };
        self.incoming_tickets.write().insert(ticket.node_id.clone(), entry);
    }

    /// Get an incoming ticket for a specific node
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn get_incoming(&self, node_id: &str) -> Option<ConnectionTicket> {
        let tickets = self.incoming_tickets.read();
        tickets.get(node_id).map(|entry| entry.ticket.clone())
    }

    /// Mark a ticket as used
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn mark_used(&self, node_id: &str) {
        if let Some(entry) = self.incoming_tickets.write().get_mut(node_id) {
            entry.use_count += 1;
        }
    }

    /// Remove expired tickets
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn cleanup_expired(&self) {
        let _now = SystemTime::now();

        self.outgoing_tickets.write().retain(|_, entry| {
            entry.created_at.elapsed()
                .map(|d| d < self.default_expiration)
                .unwrap_or(false)
        });

        self.incoming_tickets.write().retain(|_, entry| {
            entry.created_at.elapsed()
                .map(|d| d < self.default_expiration)
                .unwrap_or(false)
        });
    }

    /// Get all known peer node IDs
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn known_peers(&self) -> Vec<String> {
        self.incoming_tickets.read()
            .keys()
            .cloned()
            .collect()
    }

    /// Get the number of stored tickets
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn ticket_count(&self) -> (usize, usize) {
        (
            self.outgoing_tickets.read().len(),
            self.incoming_tickets.read().len(),
        )
    }

    /// Validate a ticket
    #[allow(dead_code)] // Reserved for full Iroh integration
    pub fn validate(&self, ticket: &ConnectionTicket) -> SwarmResult<()> {
        // Check expiration
        if ticket.is_expired() {
            return Err(SwarmError::InvalidTicket {
                reason: "Ticket has expired".to_string(),
            });
        }

        // Check ticket format (basic validation)
        if ticket.ticket.is_empty() {
            return Err(SwarmError::InvalidTicket {
                reason: "Empty ticket string".to_string(),
            });
        }

        if ticket.node_id.is_empty() {
            return Err(SwarmError::InvalidTicket {
                reason: "Empty node ID".to_string(),
            });
        }

        Ok(())
    }
}

impl Default for TicketManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ticket_manager_creation() {
        let manager = TicketManager::new();
        assert_eq!(manager.ticket_count(), (0, 0));
    }

    #[test]
    fn test_store_and_retrieve() {
        let manager = TicketManager::new();

        let ticket = ConnectionTicket::new("test-ticket", "node-123");
        manager.store_incoming(ticket);

        let retrieved = manager.get_incoming("node-123");
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().ticket, "test-ticket");
    }

    #[test]
    fn test_known_peers() {
        let manager = TicketManager::new();

        manager.store_incoming(ConnectionTicket::new("t1", "node-1"));
        manager.store_incoming(ConnectionTicket::new("t2", "node-2"));

        let peers = manager.known_peers();
        assert_eq!(peers.len(), 2);
    }

    #[test]
    fn test_validation() {
        let manager = TicketManager::new();

        let valid = ConnectionTicket::new("ticket", "node");
        assert!(manager.validate(&valid).is_ok());

        let empty_ticket = ConnectionTicket::new("", "node");
        assert!(manager.validate(&empty_ticket).is_err());

        let empty_node = ConnectionTicket::new("ticket", "");
        assert!(manager.validate(&empty_node).is_err());
    }
}
