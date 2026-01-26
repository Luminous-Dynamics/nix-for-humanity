//! Databases module - data storage and retrieval
//!
//! Provides persistence layer for consciousness systems including:
//! - Memory storage and retrieval
//! - Similarity search via HDC encodings
//! - Multiple backend support (SQLite, etc.)

use async_trait::async_trait;
use symthaea_core::hdc::binary_hv::HV16;

pub mod sqlite_client;

// ============================================================================
// Core Types
// ============================================================================

/// Result type for database operations
pub type DbResult<T> = Result<T, DatabaseError>;

/// Database error types
#[derive(Debug, Clone)]
pub enum DatabaseError {
    /// Failed to establish connection
    ConnectionFailed(String),
    /// Query execution failed
    QueryFailed(String),
    /// Insert operation failed
    InsertFailed(String),
    /// Record not found
    NotFound(String),
    /// Generic error
    Other(String),
}

impl std::fmt::Display for DatabaseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::ConnectionFailed(msg) => write!(f, "Connection failed: {}", msg),
            Self::QueryFailed(msg) => write!(f, "Query failed: {}", msg),
            Self::InsertFailed(msg) => write!(f, "Insert failed: {}", msg),
            Self::NotFound(msg) => write!(f, "Not found: {}", msg),
            Self::Other(msg) => write!(f, "Database error: {}", msg),
        }
    }
}

impl std::error::Error for DatabaseError {}

/// Types of memory in the consciousness system
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MemoryType {
    /// Autobiographical memories of specific events
    Episodic,
    /// General knowledge and facts
    Semantic,
    /// Skills and how-to knowledge
    Procedural,
    /// Short-term active information
    Working,
}

/// A memory record stored in the database
#[derive(Debug, Clone)]
pub struct MemoryRecord {
    /// Unique identifier
    pub id: String,
    /// Type of memory
    pub memory_type: MemoryType,
    /// HDC encoding of the memory
    pub encoding: HV16,
    /// Textual content/description
    pub content: String,
    /// When the memory was created (Unix timestamp milliseconds)
    pub timestamp_ms: u64,
    /// Emotional valence (-1.0 negative to 1.0 positive)
    pub valence: f32,
    /// Emotional arousal (0.0 calm to 1.0 excited)
    pub arousal: f32,
    /// Phi (integrated information) value
    pub phi: f64,
    /// Topic tags
    pub topics: Vec<String>,
    /// Additional metadata as JSON string
    pub metadata: String,
}

/// Search result with similarity score
#[derive(Debug, Clone)]
pub struct SearchResult {
    /// The matching memory record
    pub record: MemoryRecord,
    /// Similarity score (0.0 - 1.0)
    pub similarity: f32,
}

// ============================================================================
// Database Trait
// ============================================================================

/// Trait for consciousness database backends
#[async_trait]
pub trait ConsciousnessDatabase: Send + Sync {
    /// Store a memory record
    async fn store(&self, record: MemoryRecord) -> DbResult<()>;

    /// Search for similar memories using HDC similarity
    async fn search_similar(&self, query: &HV16, top_k: usize) -> DbResult<Vec<SearchResult>>;

    /// Get a specific memory by ID
    async fn get(&self, id: &str) -> DbResult<Option<MemoryRecord>>;

    /// Delete a memory by ID
    async fn delete(&self, id: &str) -> DbResult<bool>;

    /// Count total memories
    async fn count(&self) -> DbResult<usize>;

    /// Health check
    async fn health_check(&self) -> DbResult<bool>;
}

// Re-exports
pub use sqlite_client::SqliteMemory;
