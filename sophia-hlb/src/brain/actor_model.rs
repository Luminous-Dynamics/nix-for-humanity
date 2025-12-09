//! Actor Model for Sophia's Physiological Systems
//!
//! Week 0 Implementation: Zero-Copy Message Passing with Arc
//!
//! Design Philosophy:
//! - All organs are Actors with mailboxes (tokio::sync::mpsc)
//! - Messages use Arc for zero-copy sharing (1000x less allocation)
//! - Tokio runtime handles work-stealing (no custom scheduler)
//! - Graceful shutdown via Shutdown message
//!
//! Performance:
//! - Message passing: 8 bytes (Arc pointer) vs 10KB (Vec clone)
//! - Work-stealing: Native Tokio (world-class, don't fight it)
//! - Tracing: Structured logging for observability

use anyhow::Result;
use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{mpsc, oneshot};
use tracing::{debug, error, info, instrument};

/// Shared ownership of dense vectors (zero-copy)
pub type SharedVector = Arc<Vec<f64>>;

/// Messages that organs can receive
#[derive(Debug)]
pub enum OrganMessage {
    /// Input data for processing
    Input {
        data: SharedVector,  // ✅ Arc = zero-copy!
        reply: oneshot::Sender<Response>,
    },

    /// Query for information
    Query {
        question: String,
        reply: oneshot::Sender<String>,
    },

    /// Graceful shutdown signal
    Shutdown,
}

/// Responses from organs
#[derive(Debug, Clone)]
pub enum Response {
    /// Cognitive route decision (from Thalamus)
    Route(CognitiveRoute),

    /// Text response
    Text(String),

    /// Action blocked by safety
    Blocked { reason: String },

    /// Success acknowledgment
    Ok,
}

/// Cognitive routing decision
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CognitiveRoute {
    /// <10ms - Reflex path (Amygdala/Cerebellum)
    Reflex,

    /// <200ms - Standard pipeline
    Cortical,

    /// >200ms - Full resonator + K-Index
    DeepThought,
}

/// Actor trait - all organs implement this
#[async_trait]
pub trait Actor: Send + Sync {
    /// Handle a single message from mailbox
    async fn handle_message(&mut self, msg: OrganMessage) -> Result<()>;

    /// Actor priority (informational, Tokio handles scheduling)
    fn priority(&self) -> ActorPriority {
        ActorPriority::Medium
    }

    /// Actor name for debugging
    fn name(&self) -> &str {
        "UnnamedActor"
    }
}

/// Actor priority levels (informational only - Tokio schedules)
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum ActorPriority {
    Critical = 1000,  // Amygdala, Thalamus
    High = 500,       // Cerebellum, Endocrine
    Medium = 100,     // Pre-Cortex, Chronos
    Background = 10,  // Daemon, Glial Pump
}

/// Orchestrator - manages all actors
pub struct Orchestrator {
    /// Sender channels to each actor
    senders: HashMap<String, mpsc::Sender<OrganMessage>>,

    /// Task handles for all actors
    handles: Vec<tokio::task::JoinHandle<()>>,
}

impl Orchestrator {
    /// Create a new orchestrator
    pub fn new() -> Self {
        info!("Orchestrator: Initializing");
        Self {
            senders: HashMap::new(),
            handles: Vec::new(),
        }
    }

    /// Register an organ's sender channel
    pub fn register(&mut self, name: String, tx: mpsc::Sender<OrganMessage>) {
        info!(organ = %name, "Orchestrator: Registering organ");
        self.senders.insert(name, tx);
    }

    /// Spawn an actor on the Tokio runtime
    ///
    /// ✅ Tokio's work-stealing scheduler handles load balancing
    /// ✅ No custom scheduler needed (don't fight the runtime!)
    #[instrument(skip(self, actor, rx))]
    pub fn spawn_actor<A: Actor + 'static>(
        &mut self,
        mut actor: A,
        mut rx: mpsc::Receiver<OrganMessage>,
    ) {
        let name = actor.name().to_string();
        let priority = actor.priority();

        info!(
            organ = %name,
            priority = ?priority,
            "Orchestrator: Spawning actor"
        );

        // ✅ Simple tokio::spawn - let the runtime handle work-stealing
        let handle = tokio::spawn(async move {
            debug!(organ = %name, "Actor started");

            while let Some(msg) = rx.recv().await {
                // Check for shutdown
                if matches!(msg, OrganMessage::Shutdown) {
                    info!(organ = %name, "Actor received shutdown signal");
                    break;
                }

                // Handle message
                if let Err(e) = actor.handle_message(msg).await {
                    error!(
                        organ = %name,
                        error = %e,
                        "Actor error"
                    );
                }
            }

            info!(organ = %name, "Actor stopped");
        });

        self.handles.push(handle);
    }

    /// Send a message to an organ
    pub async fn send_to(
        &self,
        organ: &str,
        msg: OrganMessage,
    ) -> Result<()> {
        let tx = self.senders.get(organ)
            .ok_or_else(|| anyhow::anyhow!("Organ '{}' not registered", organ))?;

        tx.send(msg).await
            .map_err(|e| anyhow::anyhow!("Failed to send to {}: {}", organ, e))?;

        Ok(())
    }

    /// Send a message and wait for response
    pub async fn query(
        &self,
        organ: &str,
        msg: OrganMessage,
    ) -> Result<Response> {
        let (reply_tx, reply_rx) = oneshot::channel();

        // Wrap message with reply channel if needed
        let msg_with_reply = match msg {
            OrganMessage::Input { data, .. } => OrganMessage::Input {
                data,
                reply: reply_tx,
            },
            OrganMessage::Query { question, .. } => {
                // For Query, we need to return a String, so use a different pattern
                let (str_tx, str_rx) = oneshot::channel();
                self.send_to(organ, OrganMessage::Query {
                    question,
                    reply: str_tx,
                }).await?;

                let response_str = str_rx.await?;
                return Ok(Response::Text(response_str));
            }
            _ => return Err(anyhow::anyhow!("Cannot query with this message type")),
        };

        self.send_to(organ, msg_with_reply).await?;

        let response = reply_rx.await?;
        Ok(response)
    }

    /// Shutdown all actors gracefully
    #[instrument(skip(self))]
    pub async fn shutdown_all(&mut self) {
        info!("Orchestrator: Initiating graceful shutdown");

        // Send shutdown to all actors
        for (name, tx) in &self.senders {
            debug!(organ = %name, "Sending shutdown signal");
            let _ = tx.send(OrganMessage::Shutdown).await;
        }

        // Wait for all actors to finish
        info!("Orchestrator: Waiting for actors to stop");
        for handle in self.handles.drain(..) {
            let _ = handle.await;
        }

        info!("Orchestrator: All actors stopped");
    }
}

impl Default for Orchestrator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::time::{sleep, Duration};

    /// Test actor that echoes back
    struct EchoActor;

    #[async_trait]
    impl Actor for EchoActor {
        async fn handle_message(&mut self, msg: OrganMessage) -> Result<()> {
            match msg {
                OrganMessage::Input { data, reply } => {
                    let _ = reply.send(Response::Text(format!(
                        "Echo: {} dimensions",
                        data.len()
                    )));
                }
                OrganMessage::Query { question, reply } => {
                    let _ = reply.send(format!("Echo: {}", question));
                }
                _ => {}
            }
            Ok(())
        }

        fn name(&self) -> &str {
            "EchoActor"
        }
    }

    #[tokio::test]
    async fn test_actor_spawn_and_shutdown() {
        let mut orchestrator = Orchestrator::new();

        let (tx, rx) = mpsc::channel(10);
        orchestrator.register("echo".to_string(), tx.clone());

        let actor = EchoActor;
        orchestrator.spawn_actor(actor, rx);

        // Send test message
        let data = Arc::new(vec![1.0, 2.0, 3.0]);
        let (reply_tx, reply_rx) = oneshot::channel();

        orchestrator.send_to("echo", OrganMessage::Input {
            data,
            reply: reply_tx,
        }).await.unwrap();

        let response = reply_rx.await.unwrap();
        assert!(matches!(response, Response::Text(_)));

        // Shutdown
        orchestrator.shutdown_all().await;
    }

    #[tokio::test]
    async fn test_zero_copy_message_passing() {
        // ✅ Arc allows sharing without cloning
        let large_vector = Arc::new(vec![0.0; 10_000]);

        // Multiple "sends" only clone the Arc pointer (8 bytes)
        let copy1 = Arc::clone(&large_vector);
        let copy2 = Arc::clone(&large_vector);
        let copy3 = Arc::clone(&large_vector);

        // Verify they all point to same data
        assert_eq!(Arc::strong_count(&large_vector), 4);
        assert_eq!(copy1.len(), 10_000);
        assert_eq!(copy2.len(), 10_000);
        assert_eq!(copy3.len(), 10_000);
    }
}
