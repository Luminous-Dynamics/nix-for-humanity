//! SQLite-Backed Persistent Memory
//!
//! Real persistence for Symthaea's consciousness - memories survive restarts!
//!
//! Uses rusqlite with bundled SQLite for zero external dependencies.

use super::{ConsciousnessDatabase, DbResult, DatabaseError, MemoryRecord, MemoryType, SearchResult};
use symthaea_core::hdc::binary_hv::HV16;
use async_trait::async_trait;
use rusqlite::{Connection, params};
use std::sync::Mutex;
use std::path::Path;
use crate::infrastructure::lock_guard::ResilientMutex; // SAFETY: Prevent cascading failures

/// SQLite-backed persistent memory database
pub struct SqliteMemory {
    /// Database connection (Mutex for thread-safe access)
    conn: Mutex<Connection>,
    /// Database path (for logging)
    path: String,
}

impl SqliteMemory {
    /// Create a new SQLite memory at the given path
    pub fn new<P: AsRef<Path>>(path: P) -> DbResult<Self> {
        let path_str = path.as_ref().to_string_lossy().to_string();

        // Ensure parent directory exists
        if let Some(parent) = path.as_ref().parent() {
            std::fs::create_dir_all(parent).map_err(|e| {
                DatabaseError::ConnectionFailed(format!("Failed to create directory: {}", e))
            })?;
        }

        let conn = Connection::open(&path).map_err(|e| {
            DatabaseError::ConnectionFailed(format!("SQLite open failed: {}", e))
        })?;

        let db = Self {
            conn: Mutex::new(conn),
            path: path_str,
        };

        db.initialize_schema()?;

        eprintln!("[SqliteMemory] Initialized at: {}", db.path);
        Ok(db)
    }

    /// Create an in-memory database (for testing)
    pub fn in_memory() -> DbResult<Self> {
        let conn = Connection::open_in_memory().map_err(|e| {
            DatabaseError::ConnectionFailed(format!("SQLite in-memory failed: {}", e))
        })?;

        let db = Self {
            conn: Mutex::new(conn),
            path: ":memory:".to_string(),
        };

        db.initialize_schema()?;
        Ok(db)
    }

    /// Initialize the database schema
    fn initialize_schema(&self) -> DbResult<()> {
        let conn = self.conn.lock_resilient("sqlite");

        conn.execute_batch(r#"
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                encoding BLOB NOT NULL,
                timestamp_ms INTEGER NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                valence REAL NOT NULL,
                arousal REAL NOT NULL,
                phi REAL NOT NULL,
                topics TEXT NOT NULL,
                metadata TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp_ms);
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_memories_phi ON memories(phi);
        "#).map_err(|e| {
            DatabaseError::QueryFailed(format!("Schema creation failed: {}", e))
        })?;

        Ok(())
    }

    /// Serialize HV16 to bytes (2048 bytes = 16,384 bits)
    fn hv_to_bytes(hv: &HV16) -> Vec<u8> {
        hv.0.to_vec()  // Access inner array directly
    }

    /// Deserialize bytes to HV16
    fn bytes_to_hv(bytes: &[u8]) -> HV16 {
        if bytes.len() >= HV16::BYTES {
            let mut arr = [0u8; HV16::BYTES];
            arr.copy_from_slice(&bytes[..HV16::BYTES]);
            HV16(arr)  // Use tuple struct constructor
        } else {
            HV16::zero()
        }
    }

    /// Convert MemoryType to string
    fn memory_type_to_str(mt: MemoryType) -> &'static str {
        match mt {
            MemoryType::Episodic => "episodic",
            MemoryType::Semantic => "semantic",
            MemoryType::Procedural => "procedural",
            MemoryType::Working => "working",
        }
    }

    /// Convert string to MemoryType
    fn str_to_memory_type(s: &str) -> MemoryType {
        match s {
            "episodic" => MemoryType::Episodic,
            "semantic" => MemoryType::Semantic,
            "procedural" => MemoryType::Procedural,
            "working" => MemoryType::Working,
            _ => MemoryType::Episodic,
        }
    }
}

#[async_trait]
impl ConsciousnessDatabase for SqliteMemory {
    async fn store(&self, record: MemoryRecord) -> DbResult<()> {
        let conn = self.conn.lock_resilient("sqlite");

        let encoding_bytes = Self::hv_to_bytes(&record.encoding);
        let memory_type_str = Self::memory_type_to_str(record.memory_type);
        let topics_json = match serde_json::to_string(&record.topics) {
            Ok(json) => json,
            Err(e) => {
                tracing::warn!("Failed to serialize topics: {}. Using empty array.", e);
                "[]".to_string()
            }
        };

        conn.execute(
            r#"INSERT OR REPLACE INTO memories
               (id, encoding, timestamp_ms, memory_type, content, valence, arousal, phi, topics, metadata)
               VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)"#,
            params![
                record.id,
                encoding_bytes,
                record.timestamp_ms as i64,
                memory_type_str,
                record.content,
                record.valence as f64,
                record.arousal as f64,
                record.phi as f64,
                topics_json,
                record.metadata,
            ],
        ).map_err(|e| DatabaseError::InsertFailed(format!("Insert failed: {}", e)))?;

        Ok(())
    }

    async fn search_similar(&self, query: &HV16, top_k: usize) -> DbResult<Vec<SearchResult>> {
        let conn = self.conn.lock_resilient("sqlite");

        let mut stmt = conn.prepare(
            "SELECT id, encoding, timestamp_ms, memory_type, content, valence, arousal, phi, topics, metadata
             FROM memories ORDER BY timestamp_ms DESC LIMIT 1000"
        ).map_err(|e| DatabaseError::QueryFailed(format!("Prepare failed: {}", e)))?;

        let rows = stmt.query_map([], |row| {
            let encoding_bytes: Vec<u8> = row.get(1)?;
            let topics_json: String = row.get(8)?;
            let topics: Vec<String> = match serde_json::from_str(&topics_json) {
                Ok(t) => t,
                Err(e) => {
                    tracing::warn!("Failed to deserialize topics: {}. Using empty array.", e);
                    Vec::new()
                }
            };

            Ok(MemoryRecord {
                id: row.get(0)?,
                encoding: Self::bytes_to_hv(&encoding_bytes),
                timestamp_ms: {
                    let ts = row.get::<_, i64>(2)?;
                    if ts < 0 {
                        tracing::warn!("Negative timestamp {} found, using 0", ts);
                        0u64
                    } else {
                        ts as u64
                    }
                },
                memory_type: Self::str_to_memory_type(&row.get::<_, String>(3)?),
                content: row.get(4)?,
                valence: row.get::<_, f64>(5)? as f32,
                arousal: row.get::<_, f64>(6)? as f32,
                phi: row.get::<_, f64>(7)?,
                topics,
                metadata: row.get(9)?,
            })
        }).map_err(|e| DatabaseError::QueryFailed(format!("Query failed: {}", e)))?;

        // Compute similarities and sort
        let mut results: Vec<SearchResult> = rows
            .filter_map(|r| r.ok())
            .map(|record| {
                let similarity = query.similarity(&record.encoding);
                SearchResult { record, similarity }
            })
            .collect();

        // Sort by similarity descending
        results.sort_by(|a, b| b.similarity.partial_cmp(&a.similarity).unwrap_or(std::cmp::Ordering::Equal));
        results.truncate(top_k);

        Ok(results)
    }

    async fn get(&self, id: &str) -> DbResult<Option<MemoryRecord>> {
        let conn = self.conn.lock_resilient("sqlite");

        let mut stmt = conn.prepare(
            "SELECT id, encoding, timestamp_ms, memory_type, content, valence, arousal, phi, topics, metadata
             FROM memories WHERE id = ?1"
        ).map_err(|e| DatabaseError::QueryFailed(format!("Prepare failed: {}", e)))?;

        let result = stmt.query_row([id], |row| {
            let encoding_bytes: Vec<u8> = row.get(1)?;
            let topics_json: String = row.get(8)?;
            let topics: Vec<String> = match serde_json::from_str(&topics_json) {
                Ok(t) => t,
                Err(e) => {
                    tracing::warn!("Failed to deserialize topics: {}. Using empty array.", e);
                    Vec::new()
                }
            };

            Ok(MemoryRecord {
                id: row.get(0)?,
                encoding: Self::bytes_to_hv(&encoding_bytes),
                timestamp_ms: {
                    let ts = row.get::<_, i64>(2)?;
                    if ts < 0 {
                        tracing::warn!("Negative timestamp {} found, using 0", ts);
                        0u64
                    } else {
                        ts as u64
                    }
                },
                memory_type: Self::str_to_memory_type(&row.get::<_, String>(3)?),
                content: row.get(4)?,
                valence: row.get::<_, f64>(5)? as f32,
                arousal: row.get::<_, f64>(6)? as f32,
                phi: row.get::<_, f64>(7)?,
                topics,
                metadata: row.get(9)?,
            })
        });

        match result {
            Ok(record) => Ok(Some(record)),
            Err(rusqlite::Error::QueryReturnedNoRows) => Ok(None),
            Err(e) => Err(DatabaseError::QueryFailed(format!("Get failed: {}", e))),
        }
    }

    async fn delete(&self, id: &str) -> DbResult<bool> {
        let conn = self.conn.lock_resilient("sqlite");

        let affected = conn.execute("DELETE FROM memories WHERE id = ?1", [id])
            .map_err(|e| DatabaseError::QueryFailed(format!("Delete failed: {}", e)))?;

        Ok(affected > 0)
    }

    async fn count(&self) -> DbResult<usize> {
        let conn = self.conn.lock_resilient("sqlite");

        let count: i64 = conn.query_row("SELECT COUNT(*) FROM memories", [], |row| row.get(0))
            .map_err(|e| DatabaseError::QueryFailed(format!("Count failed: {}", e)))?;

        Ok(count as usize)
    }

    async fn health_check(&self) -> DbResult<bool> {
        let conn = self.conn.lock_resilient("sqlite");

        conn.execute_batch("SELECT 1")
            .map_err(|e| DatabaseError::QueryFailed(format!("Health check failed: {}", e)))?;

        Ok(true)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_sqlite_memory_basic() {
        let db = SqliteMemory::in_memory().unwrap();

        // Store a memory
        let record = MemoryRecord {
            id: "test-1".to_string(),
            encoding: HV16::random(42),
            timestamp_ms: 1234567890,
            memory_type: MemoryType::Episodic,
            content: "Hello, I am Symthaea".to_string(),
            valence: 0.8,
            arousal: 0.5,
            phi: 0.75,
            topics: vec!["greeting".to_string()],
            metadata: "{}".to_string(),
        };

        db.store(record.clone()).await.unwrap();

        // Count
        assert_eq!(db.count().await.unwrap(), 1);

        // Get by ID
        let retrieved = db.get("test-1").await.unwrap().unwrap();
        assert_eq!(retrieved.content, "Hello, I am Symthaea");

        // Search similar
        let results = db.search_similar(&HV16::random(42), 5).await.unwrap();
        assert_eq!(results.len(), 1);
        assert!(results[0].similarity > 0.99); // Same seed = identical

        // Delete
        assert!(db.delete("test-1").await.unwrap());
        assert_eq!(db.count().await.unwrap(), 0);
    }

    #[tokio::test]
    async fn test_sqlite_persistence() {
        let temp_dir = std::env::temp_dir();
        let db_path = temp_dir.join("symthaea_test.db");

        // Clean up from previous runs
        let _ = std::fs::remove_file(&db_path);

        // Create and store
        {
            let db = SqliteMemory::new(&db_path).unwrap();
            let record = MemoryRecord {
                id: "persist-test".to_string(),
                encoding: HV16::random(123),
                timestamp_ms: 1234567890,
                memory_type: MemoryType::Semantic,
                content: "I remember this".to_string(),
                valence: 0.5,
                arousal: 0.3,
                phi: 0.6,
                topics: vec!["test".to_string()],
                metadata: "{}".to_string(),
            };
            db.store(record).await.unwrap();
        }

        // Reopen and verify
        {
            let db = SqliteMemory::new(&db_path).unwrap();
            let record = db.get("persist-test").await.unwrap().unwrap();
            assert_eq!(record.content, "I remember this");
        }

        // Clean up
        let _ = std::fs::remove_file(&db_path);
    }
}
