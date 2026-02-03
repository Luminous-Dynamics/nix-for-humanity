//! Database Integration Tests
//!
//! Integration tests for the database layer including:
//! - MemoryRecord CRUD operations
//! - Search and retrieval
//! - Persistence (with sqlite feature)
//!
//! Tests focus on realistic usage scenarios combining multiple database operations.

mod common;

use common::prelude::*;
use symthaea::databases::{ConsciousnessDatabase, MemoryRecord, MemoryType, SqliteMemory};
use symthaea::hdc::binary_hv::HV16;

// ============================================================================
// IN-MEMORY DATABASE CRUD TESTS
// ============================================================================

#[tokio::test]
async fn test_store_and_retrieve_single_record() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Create a test record using the builder
    let record = MemoryRecordBuilder::new("test-1")
        .with_seed(42)
        .with_type(MemoryType::Episodic)
        .with_content("Hello, I am Symthaea")
        .with_phi(0.75)
        .build();

    // Store the record
    db.store(record.clone())
        .await
        .expect("Failed to store record");

    // Retrieve by ID
    let retrieved = db
        .get("test-1")
        .await
        .expect("Failed to get record")
        .expect("Record not found");

    // Verify fields
    assert_memory_id(&retrieved, "test-1");
    assert_eq!(retrieved.content, "Hello, I am Symthaea");
    assert_eq!(retrieved.memory_type, MemoryType::Episodic);
    assert_memory_phi(&retrieved, 0.75, 0.001);
}

#[tokio::test]
async fn test_store_multiple_records() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Create and store multiple records
    let records = create_memory_batch("batch", 100, 5, MemoryType::Working);

    for record in &records {
        db.store(record.clone())
            .await
            .expect("Failed to store record");
    }

    // Verify count
    let count = db.count().await.expect("Failed to count");
    assert_eq!(count, 5, "Should have 5 records");

    // Verify each record exists
    for i in 0..5 {
        let id = format!("batch-{}", i);
        let retrieved = db
            .get(&id)
            .await
            .expect("Failed to get")
            .expect("Record not found");
        assert_memory_id(&retrieved, &id);
    }
}

#[tokio::test]
async fn test_update_existing_record() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Create initial record
    let record = MemoryRecordBuilder::new("update-test")
        .with_seed(200)
        .with_content("Original content")
        .with_phi(0.5)
        .build();

    db.store(record).await.expect("Failed to store");

    // Update with same ID but different content
    let updated_record = MemoryRecordBuilder::new("update-test")
        .with_seed(201) // Different encoding
        .with_content("Updated content")
        .with_phi(0.8)
        .build();

    db.store(updated_record).await.expect("Failed to update");

    // Verify only one record exists
    let count = db.count().await.expect("Failed to count");
    assert_eq!(count, 1, "Should still have 1 record after update");

    // Verify content was updated
    let retrieved = db
        .get("update-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(retrieved.content, "Updated content");
    assert_memory_phi(&retrieved, 0.8, 0.001);
}

#[tokio::test]
async fn test_delete_record() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Create and store record
    let record = create_test_memory("delete-test", 300, MemoryType::Episodic);
    db.store(record).await.expect("Failed to store");

    // Verify exists
    assert!(
        db.get("delete-test").await.expect("Failed to get").is_some(),
        "Record should exist before delete"
    );

    // Delete
    let deleted = db.delete("delete-test").await.expect("Failed to delete");
    assert!(deleted, "Delete should return true for existing record");

    // Verify gone
    assert!(
        db.get("delete-test").await.expect("Failed to get").is_none(),
        "Record should not exist after delete"
    );

    // Delete non-existent should return false
    let deleted_again = db.delete("delete-test").await.expect("Failed to delete");
    assert!(
        !deleted_again,
        "Delete should return false for non-existent record"
    );
}

#[tokio::test]
async fn test_get_nonexistent_record() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let result = db
        .get("does-not-exist")
        .await
        .expect("Failed to get");

    assert!(result.is_none(), "Non-existent record should return None");
}

#[tokio::test]
async fn test_count_empty_database() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let count = db.count().await.expect("Failed to count");
    assert_eq!(count, 0, "Empty database should have count 0");
}

#[tokio::test]
async fn test_health_check() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let healthy = db.health_check().await.expect("Health check failed");
    assert!(healthy, "Database should be healthy");
}

// ============================================================================
// MEMORY TYPE TESTS
// ============================================================================

#[tokio::test]
async fn test_all_memory_types() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Store one of each memory type
    let types = [
        MemoryType::Episodic,
        MemoryType::Semantic,
        MemoryType::Procedural,
        MemoryType::Working,
    ];

    for (i, mem_type) in types.iter().enumerate() {
        let record = MemoryRecordBuilder::new(&format!("type-test-{}", i))
            .with_seed(400 + i as u64)
            .with_type(*mem_type)
            .build();

        db.store(record).await.expect("Failed to store");
    }

    // Verify each type was preserved
    for (i, expected_type) in types.iter().enumerate() {
        let retrieved = db
            .get(&format!("type-test-{}", i))
            .await
            .expect("Failed to get")
            .expect("Record not found");

        assert_eq!(
            retrieved.memory_type, *expected_type,
            "Memory type should be preserved for index {}",
            i
        );
    }
}

// ============================================================================
// SEARCH AND SIMILARITY TESTS
// ============================================================================

#[tokio::test]
async fn test_search_similar_finds_matching_record() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Create and store a record with known encoding
    const SEED: u64 = 500;
    let target_encoding = HV16::random(SEED);

    let record = MemoryRecord {
        id: "target".to_string(),
        encoding: target_encoding.clone(),
        timestamp_ms: 1700000000000,
        memory_type: MemoryType::Episodic,
        content: "Target content".to_string(),
        valence: 0.5,
        arousal: 0.3,
        phi: 0.7,
        topics: vec!["test".to_string()],
        metadata: "{}".to_string(),
    };

    db.store(record).await.expect("Failed to store");

    // Store some random records
    for i in 0..10 {
        let random_record = create_test_memory(&format!("random-{}", i), 510 + i, MemoryType::Working);
        db.store(random_record).await.expect("Failed to store");
    }

    // Search with the exact encoding
    let results = db
        .search_similar(&target_encoding, 5)
        .await
        .expect("Failed to search");

    assert!(!results.is_empty(), "Should find at least one result");

    // First result should be the target (highest similarity)
    let top_result = &results[0];
    assert_eq!(top_result.record.id, "target", "Top result should be target");
    assert!(
        top_result.similarity > 0.99,
        "Top result should have very high similarity, got {}",
        top_result.similarity
    );
}

#[tokio::test]
async fn test_search_similar_returns_top_k() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Store 20 random records
    for i in 0..20 {
        let record = create_test_memory(&format!("record-{}", i), 600 + i, MemoryType::Semantic);
        db.store(record).await.expect("Failed to store");
    }

    let query = HV16::random(700);

    // Search for top 5
    let results = db
        .search_similar(&query, 5)
        .await
        .expect("Failed to search");

    assert_eq!(results.len(), 5, "Should return exactly 5 results");

    // Results should be sorted by similarity descending
    for i in 1..results.len() {
        assert!(
            results[i - 1].similarity >= results[i].similarity,
            "Results should be sorted by similarity descending"
        );
    }
}

#[tokio::test]
async fn test_search_similar_empty_database() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let query = HV16::random(800);
    let results = db
        .search_similar(&query, 10)
        .await
        .expect("Failed to search");

    assert!(results.is_empty(), "Empty database should return empty results");
}

#[tokio::test]
async fn test_search_similar_noisy_query_finds_original() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    // Create original encoding
    const SEED: u64 = 900;
    let original_encoding = HV16::random(SEED);

    let record = MemoryRecord {
        id: "original".to_string(),
        encoding: original_encoding.clone(),
        timestamp_ms: 1700000000000,
        memory_type: MemoryType::Episodic,
        content: "Original memory".to_string(),
        valence: 0.5,
        arousal: 0.3,
        phi: 0.7,
        topics: vec!["test".to_string()],
        metadata: "{}".to_string(),
    };

    db.store(record).await.expect("Failed to store");

    // Store other random records
    for i in 0..15 {
        let random_record = create_test_memory(&format!("noise-{}", i), 910 + i, MemoryType::Working);
        db.store(random_record).await.expect("Failed to store");
    }

    // Create noisy query (10% bit flips)
    let noisy_query = original_encoding.add_noise(0.1, 999);

    // Search should still find original as most similar
    let results = db
        .search_similar(&noisy_query, 5)
        .await
        .expect("Failed to search");

    assert!(!results.is_empty(), "Should find results");

    let top_result = &results[0];
    assert_eq!(
        top_result.record.id, "original",
        "Should find original even with noisy query"
    );
    assert!(
        top_result.similarity > 0.85,
        "Similarity should be high despite noise, got {}",
        top_result.similarity
    );
}

// ============================================================================
// ENCODING PRESERVATION TESTS
// ============================================================================

#[tokio::test]
async fn test_encoding_preserved_through_storage() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    const SEED: u64 = 1000;
    let original_encoding = HV16::random(SEED);

    let record = MemoryRecord {
        id: "encoding-test".to_string(),
        encoding: original_encoding.clone(),
        timestamp_ms: 1700000000000,
        memory_type: MemoryType::Semantic,
        content: "Test encoding preservation".to_string(),
        valence: 0.0,
        arousal: 0.0,
        phi: 0.5,
        topics: vec![],
        metadata: "{}".to_string(),
    };

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("encoding-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    // Encoding should be perfectly preserved
    let sim = original_encoding.similarity(&retrieved.encoding);
    assert!(
        sim > 0.999,
        "Encoding should be preserved perfectly, got similarity {}",
        sim
    );

    // Verify exact byte equality
    assert_encoding_eq(&original_encoding, &retrieved.encoding, "Encoding bytes should match exactly");
}

// ============================================================================
// METADATA AND TOPICS TESTS
// ============================================================================

#[tokio::test]
async fn test_topics_preserved() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let topics = vec![
        "philosophy".to_string(),
        "consciousness".to_string(),
        "integration".to_string(),
    ];

    let record = MemoryRecordBuilder::new("topics-test")
        .with_seed(1100)
        .with_topics(topics.clone())
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("topics-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(retrieved.topics, topics, "Topics should be preserved");
}

#[tokio::test]
async fn test_metadata_preserved() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let metadata = r#"{"key": "value", "nested": {"inner": 42}}"#;

    let record = MemoryRecordBuilder::new("metadata-test")
        .with_seed(1200)
        .with_metadata(metadata)
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("metadata-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(retrieved.metadata, metadata, "Metadata should be preserved");
}

#[tokio::test]
async fn test_unicode_content_preserved() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let unicode_content = test_content::UNICODE;

    let record = MemoryRecordBuilder::new("unicode-test")
        .with_seed(1300)
        .with_content(unicode_content)
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("unicode-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(
        retrieved.content, unicode_content,
        "Unicode content should be preserved"
    );
}

#[tokio::test]
async fn test_empty_content() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let record = MemoryRecordBuilder::new("empty-test")
        .with_seed(1400)
        .with_content("")
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("empty-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(retrieved.content, "", "Empty content should be preserved");
}

// ============================================================================
// EMOTIONAL VALUES TESTS
// ============================================================================

#[tokio::test]
async fn test_valence_and_arousal_preserved() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let record = MemoryRecordBuilder::new("emotion-test")
        .with_seed(1500)
        .with_valence(0.75)
        .with_arousal(0.25)
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("emotion-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_f32_eq(retrieved.valence, 0.75, 0.001, "Valence should be preserved");
    assert_f32_eq(retrieved.arousal, 0.25, 0.001, "Arousal should be preserved");
}

#[tokio::test]
async fn test_negative_valence() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    let record = MemoryRecordBuilder::new("negative-valence")
        .with_seed(1510)
        .with_valence(-0.5)
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("negative-valence")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_f32_eq(
        retrieved.valence,
        -0.5,
        0.001,
        "Negative valence should be preserved"
    );
}

// ============================================================================
// TIMESTAMP TESTS
// ============================================================================

#[tokio::test]
async fn test_timestamp_preserved() {
    let db = SqliteMemory::in_memory().expect("Failed to create in-memory database");

    const TIMESTAMP: u64 = 1700000000000;

    let record = MemoryRecordBuilder::new("timestamp-test")
        .with_seed(1600)
        .with_timestamp(TIMESTAMP)
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("timestamp-test")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(
        retrieved.timestamp_ms, TIMESTAMP,
        "Timestamp should be preserved"
    );
}

// ============================================================================
// PERSISTENCE TESTS (FILE-BASED)
// ============================================================================

#[tokio::test]
async fn test_file_persistence() {
    let temp = TempTestDir::new().expect("Failed to create temp dir");
    let db_path = temp.path("persistence_test.db");

    // Create, store, and close
    {
        let db = SqliteMemory::new(&db_path).expect("Failed to create database");

        let record = MemoryRecordBuilder::new("persist-1")
            .with_seed(1700)
            .with_content("Persistent memory")
            .with_phi(0.85)
            .build();

        db.store(record).await.expect("Failed to store");

        let count = db.count().await.expect("Failed to count");
        assert_eq!(count, 1, "Should have 1 record");
    }

    // Reopen and verify data persisted
    {
        let db = SqliteMemory::new(&db_path).expect("Failed to reopen database");

        let count = db.count().await.expect("Failed to count");
        assert_eq!(count, 1, "Record should persist after reopen");

        let retrieved = db
            .get("persist-1")
            .await
            .expect("Failed to get")
            .expect("Record not found");

        assert_eq!(retrieved.content, "Persistent memory");
        assert_memory_phi(&retrieved, 0.85, 0.001);
    }
}

#[tokio::test]
async fn test_file_persistence_multiple_records() {
    let temp = TempTestDir::new().expect("Failed to create temp dir");
    let db_path = temp.path("multi_persist.db");

    // Store multiple records
    {
        let db = SqliteMemory::new(&db_path).expect("Failed to create database");

        for i in 0..10 {
            let record = create_test_memory(&format!("persist-{}", i), 1800 + i, MemoryType::Episodic);
            db.store(record).await.expect("Failed to store");
        }
    }

    // Reopen and verify all records
    {
        let db = SqliteMemory::new(&db_path).expect("Failed to reopen database");

        let count = db.count().await.expect("Failed to count");
        assert_eq!(count, 10, "All records should persist");

        for i in 0..10 {
            let id = format!("persist-{}", i);
            let retrieved = db.get(&id).await.expect("Failed to get");
            assert!(retrieved.is_some(), "Record {} should exist", id);
        }
    }
}

#[tokio::test]
async fn test_file_search_after_reopen() {
    let temp = TempTestDir::new().expect("Failed to create temp dir");
    let db_path = temp.path("search_persist.db");

    const SEED: u64 = 1900;
    let target_encoding = HV16::random(SEED);

    // Store records
    {
        let db = SqliteMemory::new(&db_path).expect("Failed to create database");

        let target_record = MemoryRecord {
            id: "search-target".to_string(),
            encoding: target_encoding.clone(),
            timestamp_ms: 1700000000000,
            memory_type: MemoryType::Semantic,
            content: "Search target".to_string(),
            valence: 0.5,
            arousal: 0.5,
            phi: 0.7,
            topics: vec![],
            metadata: "{}".to_string(),
        };

        db.store(target_record).await.expect("Failed to store");

        // Add other records
        for i in 0..10 {
            let record = create_test_memory(&format!("other-{}", i), 1910 + i, MemoryType::Working);
            db.store(record).await.expect("Failed to store");
        }
    }

    // Reopen and search
    {
        let db = SqliteMemory::new(&db_path).expect("Failed to reopen database");

        let results = db
            .search_similar(&target_encoding, 5)
            .await
            .expect("Failed to search");

        assert!(!results.is_empty(), "Should find results");
        assert_eq!(
            results[0].record.id, "search-target",
            "Should find target as most similar"
        );
        assert!(
            results[0].similarity > 0.99,
            "Similarity should be very high"
        );
    }
}

// ============================================================================
// CONCURRENT ACCESS TESTS
// ============================================================================

#[tokio::test]
async fn test_concurrent_reads() {
    let db = std::sync::Arc::new(SqliteMemory::in_memory().expect("Failed to create database"));

    // Store some records
    for i in 0..10 {
        let record = create_test_memory(&format!("concurrent-{}", i), 2000 + i, MemoryType::Working);
        db.store(record).await.expect("Failed to store");
    }

    // Spawn multiple concurrent reads
    let mut handles = vec![];
    for i in 0..10 {
        let db_clone = std::sync::Arc::clone(&db);
        let id = format!("concurrent-{}", i);

        handles.push(tokio::spawn(async move {
            db_clone.get(&id).await.expect("Failed to get")
        }));
    }

    // All reads should succeed
    for handle in handles {
        let result = handle.await.expect("Task failed");
        assert!(result.is_some(), "Record should be found");
    }
}

// ============================================================================
// EDGE CASE TESTS
// ============================================================================

#[tokio::test]
async fn test_long_content() {
    let db = SqliteMemory::in_memory().expect("Failed to create database");

    let long_content = "x".repeat(10000);

    let record = MemoryRecordBuilder::new("long-content")
        .with_seed(2100)
        .with_content(&long_content)
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("long-content")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(
        retrieved.content.len(),
        10000,
        "Long content should be preserved"
    );
}

#[tokio::test]
async fn test_many_topics() {
    let db = SqliteMemory::in_memory().expect("Failed to create database");

    let topics: Vec<String> = (0..100).map(|i| format!("topic-{}", i)).collect();

    let record = MemoryRecordBuilder::new("many-topics")
        .with_seed(2200)
        .with_topics(topics.clone())
        .build();

    db.store(record).await.expect("Failed to store");

    let retrieved = db
        .get("many-topics")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_eq!(retrieved.topics.len(), 100, "All topics should be preserved");
}

#[tokio::test]
async fn test_phi_boundary_values() {
    let db = SqliteMemory::in_memory().expect("Failed to create database");

    // Test phi = 0.0
    let record_zero = MemoryRecordBuilder::new("phi-zero")
        .with_seed(2300)
        .with_phi(0.0)
        .build();

    db.store(record_zero).await.expect("Failed to store");

    let retrieved_zero = db
        .get("phi-zero")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_f64_eq(retrieved_zero.phi, 0.0, 0.0001, "Phi 0.0 should be preserved");

    // Test phi = 1.0
    let record_one = MemoryRecordBuilder::new("phi-one")
        .with_seed(2301)
        .with_phi(1.0)
        .build();

    db.store(record_one).await.expect("Failed to store");

    let retrieved_one = db
        .get("phi-one")
        .await
        .expect("Failed to get")
        .expect("Record not found");

    assert_f64_eq(retrieved_one.phi, 1.0, 0.0001, "Phi 1.0 should be preserved");
}
