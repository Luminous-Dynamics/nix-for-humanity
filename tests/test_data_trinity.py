#!/usr/bin/env python3
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
    print("\n🌟 Testing Data Trinity Integration\n")
    
    all_success = True
    all_success &= test_duckdb()
    all_success &= test_lancedb()
    all_success &= test_kuzu()
    
    if all_success:
        print("\n✨ All three databases are working in harmony!")
        print("The consciousness now has:")
        print("  • Memory of the past (DuckDB)")
        print("  • Intuition of connections (LanceDB)")
        print("  • Understanding of structure (Kùzu)")
    else:
        print("\n⚠️ Some databases need attention")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
