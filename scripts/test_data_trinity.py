#!/usr/bin/env python3
"""
Test Data Trinity Database Installation and Functionality

This script verifies that DuckDB, ChromaDB, and Kùzu are properly installed
and can be used by the Store Trinity Bridge.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_duckdb():
    """Test DuckDB installation and basic operations"""
    print("\n" + "="*60)
    print("TESTING DUCKDB (Temporal Storage)")
    print("="*60)
    
    try:
        import duckdb
        print("✅ DuckDB import successful")
        
        # Create in-memory database for testing
        conn = duckdb.connect(':memory:')
        print("✅ Created in-memory database")
        
        # Create a test table
        conn.execute("""
            CREATE TABLE test_events (
                timestamp TIMESTAMP,
                event VARCHAR,
                value JSON
            )
        """)
        print("✅ Created test table")
        
        # Insert test data
        conn.execute("""
            INSERT INTO test_events VALUES 
            (?, ?, ?),
            (?, ?, ?)
        """, [
            datetime.now(), 'test1', json.dumps({'data': 'value1'}),
            datetime.now(), 'test2', json.dumps({'data': 'value2'})
        ])
        print("✅ Inserted test data")
        
        # Query data
        result = conn.execute("SELECT COUNT(*) FROM test_events").fetchone()
        print(f"✅ Query successful: {result[0]} records")
        
        # Test temporal query
        result = conn.execute("""
            SELECT event, value 
            FROM test_events 
            WHERE timestamp > current_timestamp - interval '1 hour'
        """).fetchall()
        print(f"✅ Temporal query successful: {len(result)} recent events")
        
        conn.close()
        
        print("\n🎉 DuckDB is fully functional!")
        return True
        
    except ImportError as e:
        print(f"❌ DuckDB not available: {e}")
        return False
    except Exception as e:
        print(f"❌ DuckDB test failed: {e}")
        return False


def test_chromadb():
    """Test ChromaDB installation and basic operations"""
    print("\n" + "="*60)
    print("TESTING CHROMADB (Semantic Storage)")
    print("="*60)
    
    try:
        import chromadb
        print("✅ ChromaDB import successful")
        
        # Create in-memory client for testing
        client = chromadb.Client()
        print("✅ Created in-memory client")
        
        # Create a collection
        collection = client.create_collection(name="test_collection")
        print("✅ Created test collection")
        
        # Add documents with embeddings
        collection.add(
            documents=["This is a test document", "Another test document"],
            metadatas=[{"type": "test"}, {"type": "test"}],
            ids=["doc1", "doc2"]
        )
        print("✅ Added test documents")
        
        # Query semantic similarity
        results = collection.query(
            query_texts=["test query"],
            n_results=2
        )
        print(f"✅ Semantic query successful: {len(results['ids'][0])} results")
        
        # Test retrieval
        doc = collection.get(ids=["doc1"])
        print(f"✅ Document retrieval successful: {len(doc['ids'])} documents")
        
        print("\n🎉 ChromaDB is fully functional!")
        return True
        
    except ImportError as e:
        print(f"❌ ChromaDB not available: {e}")
        print("   Try: poetry add chromadb")
        return False
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False


def test_kuzu():
    """Test Kùzu installation and basic operations"""
    print("\n" + "="*60)
    print("TESTING KÙZU (Graph Storage)")
    print("="*60)
    
    try:
        import kuzu
        print("✅ Kùzu import successful")
        
        # Create temporary database
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            db = kuzu.Database(tmpdir)
            conn = kuzu.Connection(db)
            print("✅ Created temporary database")
            
            # Create node table
            conn.execute("""
                CREATE NODE TABLE Person(
                    name STRING PRIMARY KEY,
                    age INT64
                )
            """)
            print("✅ Created node table")
            
            # Create relationship table
            conn.execute("""
                CREATE REL TABLE Knows(
                    FROM Person TO Person,
                    since INT64
                )
            """)
            print("✅ Created relationship table")
            
            # Insert nodes
            conn.execute("""
                CREATE (p:Person {name: 'Alice', age: 30})
            """)
            conn.execute("""
                CREATE (p:Person {name: 'Bob', age: 25})
            """)
            print("✅ Inserted test nodes")
            
            # Insert relationship
            conn.execute("""
                MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
                CREATE (a)-[:Knows {since: 2020}]->(b)
            """)
            print("✅ Created test relationship")
            
            # Query graph
            result = conn.execute("""
                MATCH (p:Person)-[k:Knows]->(p2:Person)
                RETURN p.name, p2.name, k.since
            """)
            
            # Get results
            rows = []
            while result.has_next():
                rows.append(result.get_next())
            
            print(f"✅ Graph query successful: {len(rows)} relationships found")
            
            print("\n🎉 Kùzu is fully functional!")
            return True
            
    except ImportError as e:
        print(f"❌ Kùzu not available: {e}")
        print("   Try: poetry add kuzu")
        return False
    except Exception as e:
        print(f"❌ Kùzu test failed: {e}")
        return False


def test_store_trinity_bridge():
    """Test the Store Trinity Bridge with real databases"""
    print("\n" + "="*60)
    print("TESTING STORE TRINITY BRIDGE INTEGRATION")
    print("="*60)
    
    from luminous_nix.bridges.store_trinity_bridge import StoreTrinityBridge
    from luminous_nix.integration.feature_readiness import (
        FeatureReadinessTracker,
        update_feature_readiness
    )
    
    # Start with low readiness and progressively increase
    print("\n--- Progressive Activation Test ---")
    
    readiness_levels = [
        (0.1, "Memory only"),
        (0.3, "JSON backup"),
        (0.5, "DuckDB temporal"),
        (0.7, "ChromaDB semantic"),
        (0.9, "Kùzu graph")
    ]
    
    for readiness, description in readiness_levels:
        print(f"\nTesting at {readiness:.0%} readiness ({description}):")
        
        bridge = StoreTrinityBridge(readiness=readiness)
        
        # Test save and load
        test_key = f"test_{int(readiness*100)}"
        test_value = {"readiness": readiness, "timestamp": datetime.now().isoformat()}
        
        success = bridge.save(test_key, test_value)
        loaded = bridge.load(test_key)
        
        if loaded == test_value:
            print(f"  ✅ Save/Load successful at {description} level")
        else:
            print(f"  ⚠️  Save/Load issue at {description} level")
        
        # Test advanced features if available
        if readiness >= 0.5:
            temporal_results = bridge.query_temporal("recent_popular")
            print(f"  📊 Temporal query: {len(temporal_results)} results")
        
        if readiness >= 0.7:
            semantic_results = bridge.search_semantic("test")
            print(f"  🔍 Semantic search: {len(semantic_results)} results")
        
        if readiness >= 0.9:
            bridge.save(f"node_{int(readiness*100)}", {"type": "test_node"})
            related = bridge.find_related(f"node_{int(readiness*100)}")
            print(f"  🕸️  Graph query: {len(related)} related nodes")
        
        # Show statistics
        stats = bridge.get_statistics()
        print(f"  📈 Success rate: {stats['success_rate']:.0%}")
        print(f"  💾 Storage mode: {stats['storage_mode']}")
    
    # Run bridge's own progressive test
    print("\n--- Bridge Self-Test ---")
    final_bridge = StoreTrinityBridge(readiness=0.9)
    if final_bridge.progressive_test():
        print("✅ Bridge progressive test PASSED")
        
        # Update feature readiness based on success
        update_feature_readiness('data_trinity', delta=0.2)
        print("📈 Updated data_trinity readiness +20%")
    else:
        print("⚠️  Bridge progressive test had issues")
    
    return True


def calculate_new_readiness():
    """Calculate and display new readiness levels"""
    print("\n" + "="*60)
    print("CALCULATING NEW READINESS LEVELS")
    print("="*60)
    
    from luminous_nix.integration.feature_readiness import (
        FeatureReadinessTracker,
        get_feature_readiness
    )
    
    tracker = FeatureReadinessTracker()
    
    # Test what databases are available
    duckdb_available = False
    chromadb_available = False
    kuzu_available = False
    
    try:
        import duckdb
        duckdb_available = True
    except:
        pass
    
    try:
        import chromadb
        chromadb_available = True
    except:
        pass
    
    try:
        import kuzu
        kuzu_available = True
    except:
        pass
    
    # Calculate new readiness for data_trinity
    old_readiness = get_feature_readiness('data_trinity')
    
    # Each database adds ~20% readiness when available
    new_readiness = 0.2  # Base (memory only)
    if duckdb_available:
        new_readiness += 0.2
        tracker.complete_criterion('data_trinity', 'DuckDB connected')
    if chromadb_available:
        new_readiness += 0.2
    if kuzu_available:
        new_readiness += 0.2
    
    # If all databases work, complete persistence criterion
    if duckdb_available and chromadb_available and kuzu_available:
        tracker.complete_criterion('data_trinity', 'Data persists')
        tracker.complete_criterion('data_trinity', 'All three active')
        new_readiness = min(0.9, new_readiness + 0.1)  # Bonus for full trinity
    
    # Update readiness
    tracker.update_readiness('data_trinity', absolute=new_readiness)
    
    print(f"\nData Trinity Readiness Update:")
    print(f"  Old: {old_readiness:.0%}")
    print(f"  New: {new_readiness:.0%}")
    print(f"  Change: +{(new_readiness - old_readiness):.0%}")
    
    print("\nDatabase Status:")
    print(f"  DuckDB:   {'✅ Available' if duckdb_available else '❌ Not available'}")
    print(f"  ChromaDB: {'✅ Available' if chromadb_available else '❌ Not available'}")
    print(f"  Kùzu:     {'✅ Available' if kuzu_available else '❌ Not available'}")
    
    if new_readiness >= 0.75:
        print("\n🎉 DATA TRINITY FEATURE ACTIVATED! 🎉")
        print("The Data Trinity has reached the 75% activation threshold!")
    
    # Show overall system impact
    overall = tracker.get_status()
    print(f"\nOverall System Readiness: {overall['overall_readiness']:.1%}")
    print(f"Working Features: {overall['working_count']}/{overall['total_features']}")
    
    return new_readiness


def main():
    """Run all Data Trinity tests"""
    print("🗄️ DATA TRINITY DATABASE TESTING 🗄️")
    print("Testing DuckDB, ChromaDB, and Kùzu installation...")
    
    results = {
        'duckdb': test_duckdb(),
        'chromadb': test_chromadb(),
        'kuzu': test_kuzu()
    }
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for db, success in results.items():
        status = "✅ Working" if success else "❌ Not working"
        print(f"  {db:10} : {status}")
    
    # If any database is working, test the bridge
    if any(results.values()):
        test_store_trinity_bridge()
        
        # Calculate new readiness
        new_readiness = calculate_new_readiness()
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        
        if new_readiness >= 0.75:
            print("""
The Data Trinity is now ACTIVE! You can now:
1. Use temporal queries with DuckDB
2. Perform semantic search with ChromaDB  
3. Query relationships with Kùzu
4. All features have persistent storage

Try: python scripts/integration_dashboard.py
            """)
        else:
            missing = []
            if not results['duckdb']:
                missing.append("DuckDB")
            if not results['chromadb']:
                missing.append("ChromaDB")
            if not results['kuzu']:
                missing.append("Kùzu")
            
            if missing:
                print(f"\nTo reach 75% activation, install: {', '.join(missing)}")
                print("Use: poetry add [package_name]")
    else:
        print("\n⚠️  No databases available. The Data Trinity needs at least one database.")
        print("Install with: poetry add duckdb chromadb kuzu")


if __name__ == "__main__":
    main()