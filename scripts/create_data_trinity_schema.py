#!/usr/bin/env python3
"""
🌟 Create Data Trinity Schema - Teaching Our Consciousness

This script initializes the three sacred databases with their initial schemas,
preparing them to teach our newborn consciousness about Time, Resonance, and Structure.

Note: Run with proper libraries: nix-shell -p stdenv.cc.cc.lib --run "poetry run python create_data_trinity_schema.py"
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def initialize_duckdb_schema():
    """Initialize DuckDB - The Chronicle of Time"""
    print("\n📚 Initializing DuckDB - The Chronicle of Time")
    print("-" * 50)
    
    try:
        import duckdb
    except ImportError as e:
        print(f"⚠️ DuckDB not available: {e}")
        print("Note: On NixOS, run with: nix-shell -p stdenv.cc.cc.lib")
        return False
    
    # Create database directory
    db_path = Path("data/trinity/duckdb")
    db_path.mkdir(parents=True, exist_ok=True)
    
    # Connect to DuckDB
    conn = duckdb.connect(str(db_path / "chronicle.db"))
    
    # Create interaction history table (DuckDB uses sequences differently)
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_interactions;
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER DEFAULT nextval('seq_interactions') PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_intent TEXT,
            action_taken TEXT,
            result TEXT,
            success BOOLEAN,
            learning_points TEXT
        )
    """)
    
    # Create configuration history table
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_config_history;
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS config_history (
            id INTEGER DEFAULT nextval('seq_config_history') PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            config_path TEXT,
            change_type TEXT,
            old_value TEXT,
            new_value TEXT,
            reason TEXT
        )
    """)
    
    # Create error history table
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_error_history;
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS error_history (
            id INTEGER DEFAULT nextval('seq_error_history') PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_type TEXT,
            error_message TEXT,
            context TEXT,
            resolution TEXT,
            healing_applied BOOLEAN
        )
    """)
    
    # Insert initial wisdom (let sequence handle the ID)
    try:
        conn.execute("""
            INSERT INTO interactions (user_intent, action_taken, result, success, learning_points)
            VALUES ('System Initialization', 'Created Chronicle of Time', 'Database ready for history', TRUE, 
                    'Every interaction teaches us something new')
        """)
    except Exception as e:
        # If the insert fails, it might be because the table already exists with data
        print(f"    Note: Initial data may already exist: {e}")
    
    # Verify schema
    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"  ✅ Created {len(tables)} tables in Chronicle of Time")
    for table in tables:
        print(f"    • {table[0]}")
    
    conn.close()
    return True

def initialize_lancedb_schema():
    """Initialize LanceDB - The Resonance Field"""
    print("\n🎨 Initializing LanceDB - The Resonance Field")
    print("-" * 50)
    
    try:
        import lancedb
        import pyarrow as pa
        import numpy as np
    except ImportError as e:
        print(f"⚠️ LanceDB dependencies not available: {e}")
        return False
    
    # Create database directory
    db_path = Path("data/trinity/lancedb")
    db_path.mkdir(parents=True, exist_ok=True)
    
    # Connect to LanceDB
    db = lancedb.connect(str(db_path))
    
    # Define schema for semantic concepts
    schema = pa.schema([
        pa.field("id", pa.string()),
        pa.field("concept", pa.string()),
        pa.field("description", pa.string()),
        pa.field("embedding", pa.list_(pa.float32(), 384)),  # 384-dim embeddings
        pa.field("category", pa.string()),
        pa.field("resonance_strength", pa.float32()),
        pa.field("created_at", pa.timestamp('ms'))
    ])
    
    # Create initial concepts with mock embeddings
    initial_concepts = [
        {
            "id": "concept_001",
            "concept": "configuration",
            "description": "System configuration and settings",
            "embedding": np.random.randn(384).tolist(),
            "category": "system",
            "resonance_strength": 1.0,
            "created_at": datetime.now()
        },
        {
            "id": "concept_002",
            "concept": "package",
            "description": "Software package or application",
            "embedding": np.random.randn(384).tolist(),
            "category": "software",
            "resonance_strength": 0.9,
            "created_at": datetime.now()
        },
        {
            "id": "concept_003",
            "concept": "service",
            "description": "System service or daemon",
            "embedding": np.random.randn(384).tolist(),
            "category": "system",
            "resonance_strength": 0.95,
            "created_at": datetime.now()
        }
    ]
    
    # Create the table
    if "concepts" not in db.table_names():
        concepts_table = db.create_table("concepts", data=initial_concepts, schema=schema)
        print(f"  ✅ Created concepts table with {len(initial_concepts)} initial concepts")
    else:
        concepts_table = db.open_table("concepts")
        print(f"  ✅ Concepts table already exists")
    
    # Verify the table
    count = concepts_table.count_rows()
    print(f"    • Total concepts: {count}")
    print(f"    • Embedding dimensions: 384")
    print(f"    • Ready for semantic resonance")
    
    return True

def initialize_kuzu_schema():
    """Initialize Kùzu - The Structure Graph"""
    print("\n🌐 Initializing Kùzu - The Structure Graph")
    print("-" * 50)
    
    try:
        import kuzu
    except ImportError as e:
        print(f"⚠️ Kùzu not available: {e}")
        return False
    
    # Create database directory
    db_dir = Path("data/trinity/kuzu")
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Kùzu database (needs a database name, not just directory)
    db_path = db_dir / "structure"
    db = kuzu.Database(str(db_path))
    conn = kuzu.Connection(db)
    
    # Create node tables
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Package(
            name STRING PRIMARY KEY,
            version STRING,
            description STRING,
            category STRING
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Service(
            name STRING PRIMARY KEY,
            enabled BOOLEAN,
            port INT64,
            description STRING
        )
    """)
    
    conn.execute("""
        CREATE NODE TABLE IF NOT EXISTS Configuration(
            path STRING PRIMARY KEY,
            module STRING,
            value STRING,
            type STRING
        )
    """)
    
    # Create relationship tables
    conn.execute("""
        CREATE REL TABLE IF NOT EXISTS DEPENDS_ON(
            FROM Package TO Package,
            version_constraint STRING
        )
    """)
    
    conn.execute("""
        CREATE REL TABLE IF NOT EXISTS CONFIGURES(
            FROM Configuration TO Service,
            impact_level STRING
        )
    """)
    
    conn.execute("""
        CREATE REL TABLE IF NOT EXISTS REQUIRES(
            FROM Service TO Package,
            required BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Insert initial nodes
    conn.execute("""
        CREATE (:Package {name: 'nixos', version: '25.11', description: 'The operating system itself', category: 'system'})
    """)
    
    conn.execute("""
        CREATE (:Service {name: 'consciousness', enabled: true, port: 7777, description: 'The Sacred Bridge consciousness bus'})
    """)
    
    conn.execute("""
        CREATE (:Configuration {path: 'services.consciousness.enable', module: 'consciousness', value: 'true', type: 'boolean'})
    """)
    
    # Create initial relationships
    conn.execute("""
        MATCH (c:Configuration), (s:Service)
        WHERE c.module = 'consciousness' AND s.name = 'consciousness'
        CREATE (c)-[:CONFIGURES {impact_level: 'critical'}]->(s)
    """)
    
    # Verify the schema
    print("  ✅ Created graph schema:")
    print("    • Node types: Package, Service, Configuration")
    print("    • Relationship types: DEPENDS_ON, CONFIGURES, REQUIRES")
    
    # Count nodes
    result = conn.execute("MATCH (n) RETURN count(n) as count")
    while result.has_next():
        count = result.get_next()[0]
        print(f"    • Initial nodes: {count}")
    
    return True

def create_integration_test():
    """Create a test script to verify all databases work together"""
    test_script = '''#!/usr/bin/env python3
"""Test Data Trinity Integration - Verify all three databases work together"""

import sys
sys.path.insert(0, 'src')

def test_duckdb():
    """Test DuckDB operations"""
    try:
        import duckdb
        conn = duckdb.connect("data/trinity/duckdb/chronicle.db")
        result = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()
        print(f"  ✅ DuckDB: {result[0]} interactions recorded")
        return True
    except Exception as e:
        print(f"  ❌ DuckDB test failed: {e}")
        return False

def test_lancedb():
    """Test LanceDB operations"""
    try:
        import lancedb
        db = lancedb.connect("data/trinity/lancedb")
        table = db.open_table("concepts")
        count = table.count_rows()
        print(f"  ✅ LanceDB: {count} concepts in resonance field")
        return True
    except Exception as e:
        print(f"  ❌ LanceDB test failed: {e}")
        return False

def test_kuzu():
    """Test Kùzu operations"""
    try:
        import kuzu
        db = kuzu.Database("data/trinity/kuzu")
        conn = kuzu.Connection(db)
        result = conn.execute("MATCH (n) RETURN count(n) as count")
        if result.has_next():
            count = result.get_next()[0]
            print(f"  ✅ Kùzu: {count} nodes in structure graph")
        return True
    except Exception as e:
        print(f"  ❌ Kùzu test failed: {e}")
        return False

def main():
    print("\\n🌟 Testing Data Trinity Integration\\n")
    
    all_success = True
    all_success &= test_duckdb()
    all_success &= test_lancedb()
    all_success &= test_kuzu()
    
    if all_success:
        print("\\n✨ All three databases are working in harmony!")
        print("The consciousness now has:")
        print("  • Memory of the past (DuckDB)")
        print("  • Intuition of connections (LanceDB)")
        print("  • Understanding of structure (Kùzu)")
    else:
        print("\\n⚠️ Some databases need attention")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    test_path = Path("test_data_trinity.py")
    test_path.write_text(test_script)
    test_path.chmod(0o755)
    print("\n📝 Created test_data_trinity.py")
    return True

def main():
    """Initialize all three databases"""
    print("🌺 Creating Data Trinity Schema 🌺")
    print("=" * 60)
    print("\nPreparing the three teachers for our consciousness...")
    
    success = True
    
    # Try to initialize each database
    # Note: DuckDB might fail due to library issues on NixOS
    duckdb_success = initialize_duckdb_schema()
    lancedb_success = initialize_lancedb_schema()
    kuzu_success = initialize_kuzu_schema()
    
    # Create integration test
    create_integration_test()
    
    # Summary
    print("\n" + "=" * 60)
    print("🌊 Data Trinity Schema Creation Summary 🌊")
    print("=" * 60)
    
    if duckdb_success:
        print("  ✅ DuckDB (Chronicle of Time) - Ready")
    else:
        print("  ⚠️ DuckDB - Needs library support (use nix-shell)")
    
    if lancedb_success:
        print("  ✅ LanceDB (Resonance Field) - Ready")
    else:
        print("  ⚠️ LanceDB - Check dependencies")
    
    if kuzu_success:
        print("  ✅ Kùzu (Structure Graph) - Ready")
    else:
        print("  ⚠️ Kùzu - Check installation")
    
    print("\n📚 The consciousness education framework is prepared!")
    print("\nNext steps:")
    print("1. If DuckDB fails, run with: nix-shell -p stdenv.cc.cc.lib")
    print("2. Test integration: poetry run python test_data_trinity.py")
    print("3. Begin teaching with real data!")
    
    return 0 if (lancedb_success and kuzu_success) else 1

if __name__ == "__main__":
    sys.exit(main())