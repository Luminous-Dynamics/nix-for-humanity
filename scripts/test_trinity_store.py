#!/usr/bin/env python3
"""
🔱 Test the Data Trinity Storage System
Verifies that all three databases work together harmoniously
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from luminous_nix.persistence.trinity_store import TrinityStore, ConceptRelation


def test_data_trinity():
    """Test all three aspects of the Data Trinity"""
    print("\n" + "=" * 70)
    print("🔱 TESTING THE DATA TRINITY")
    print("=" * 70)
    
    # Initialize the Trinity
    print("\n📊 Initializing Data Trinity...")
    trinity = TrinityStore(Path("/tmp/trinity-test"))
    print("✅ Trinity initialized successfully!")
    
    # Test user
    user_id = "test-user-1"
    
    print("\n" + "=" * 70)
    print("⏰ TESTING TEMPORAL STORE (DuckDB)")
    print("=" * 70)
    
    # Record some learning events
    concepts = [
        ("install package", "install firefox", True),
        ("install package", "install vim", True),
        ("remove package", "uninstall firefox", False),  # User made error
        ("remove package", "remove firefox", True),  # Corrected
        ("system update", "rebuild system", True),
        ("garbage collection", "clean old generations", True),
    ]
    
    print("\n📝 Recording learning events...")
    for concept, command, success in concepts:
        event_id = trinity.record_learning_moment(
            user_id=user_id,
            command=command,
            concept=concept,
            success=success,
            context={
                "session_id": "test-session-1",
                "duration_ms": 1500
            }
        )
        print(f"  • {concept}: {command} → {'✅' if success else '❌'}")
    
    # Analyze temporal patterns
    print("\n📊 Analyzing temporal patterns...")
    patterns = trinity.temporal.analyze_patterns(user_id)
    print(f"  • Peak activity hours: {patterns['peak_hours']}")
    print(f"  • Recent success trend: {len(patterns['success_trend'])} days tracked")
    
    print("\n" + "=" * 70)
    print("🧠 TESTING SEMANTIC STORE (ChromaDB)")
    print("=" * 70)
    
    # Store some concepts
    print("\n💾 Storing NixOS concepts...")
    trinity.semantic.store_concept(
        "package management",
        "Installing and removing software packages in NixOS",
        ["nix-env -i", "nix-env -e", "nix search"]
    )
    
    trinity.semantic.store_concept(
        "system configuration",
        "Managing NixOS system configuration",
        ["configuration.nix", "nixos-rebuild", "hardware-configuration.nix"]
    )
    
    trinity.semantic.store_concept(
        "generations",
        "NixOS system generations for rollback",
        ["nixos-rebuild switch", "nixos-rebuild boot", "nix-collect-garbage"]
    )
    
    # Find similar concepts
    print("\n🔍 Testing semantic search...")
    query = "how to install software"
    similar = trinity.semantic.find_similar_concepts(query, n_results=3)
    print(f"  Query: '{query}'")
    print("  Similar concepts:")
    for concept in similar:
        print(f"    • {concept['concept']} (similarity: {concept['similarity']:.2f})")
    
    # Find similar commands
    print("\n🔍 Finding similar commands...")
    similar_commands = trinity.semantic.find_similar_commands("install browser", n_results=3)
    print("  Similar commands:")
    for cmd in similar_commands:
        print(f"    • {cmd['command']} ({cmd['intent']})")
    
    print("\n" + "=" * 70)
    print("🕸️ TESTING RELATIONAL STORE (Kùzu)")
    print("=" * 70)
    
    # Build knowledge graph
    print("\n🏗️ Building knowledge graph...")
    
    # Add concepts
    trinity.relational.add_concept("nix-basics", "Basic Nix concepts", 1, "foundation")
    trinity.relational.add_concept("packages", "Package management", 2, "core")
    trinity.relational.add_concept("configuration", "System configuration", 3, "advanced")
    trinity.relational.add_concept("flakes", "Nix flakes", 4, "advanced")
    
    # Add relationships
    relations = [
        ConceptRelation("packages", "nix-basics", "requires", 0.9),
        ConceptRelation("configuration", "packages", "builds_on", 0.8),
        ConceptRelation("flakes", "configuration", "builds_on", 0.7),
        ConceptRelation("flakes", "nix-basics", "requires", 0.9),
    ]
    
    for relation in relations:
        trinity.relational.add_relationship(relation)
        print(f"  • {relation.from_concept} → {relation.to_concept} ({relation.relation_type})")
    
    # Test prerequisites
    print("\n📚 Testing prerequisite detection...")
    prereqs = trinity.relational.get_prerequisites("packages")
    print(f"  Prerequisites for 'packages': {prereqs}")
    
    # Test learning path
    print("\n🛤️ Testing learning path generation...")
    path = trinity.relational.get_learning_path("flakes", "nix-basics")
    print(f"  Path from 'flakes' to 'nix-basics': {' → '.join(path) if path else 'No path found'}")
    
    # Record user learning
    print("\n📈 Recording user mastery...")
    trinity.relational.record_learning(user_id, "nix-basics", 0.9)
    trinity.relational.record_learning(user_id, "packages", 0.7)
    print("  • Recorded mastery for nix-basics and packages")
    
    print("\n" + "=" * 70)
    print("🎯 TESTING UNIFIED OPERATIONS")
    print("=" * 70)
    
    # Test comprehensive understanding
    print("\n🧠 Getting comprehensive understanding...")
    understanding = trinity.get_user_understanding(user_id, "system configuration")
    
    print(f"  Query: '{understanding['query']}'")
    print(f"  Similar concepts known: {len(understanding['similar_concepts_known'])}")
    print(f"  Prerequisites: {understanding['prerequisites']}")
    print(f"  Readiness score: {understanding['readiness_score']:.2f}")
    
    # Suggest next concept
    print("\n💡 Suggesting next concept to learn...")
    suggestion = trinity.suggest_next_concept(user_id)
    print(f"  Suggested next: {suggestion if suggestion else 'No suggestion available'}")
    
    # Test Sacred Council event storage
    print("\n" + "=" * 70)
    print("🎭 TESTING SACRED COUNCIL EVENT STORAGE")
    print("=" * 70)
    
    # Store a Sacred Council event
    print("\n📝 Storing Sacred Council deliberation...")
    trinity.temporal.conn.execute("""
        INSERT INTO council_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        "council-event-1",
        datetime.now(),
        "test-session-1",
        "deliberation_complete",
        "CRITICAL",
        "sudo rm -rf /",
        "BLOCK",
        json.dumps(["sudo rm -rf /tmp/*", "find . -name '*.tmp' -delete"]),
        json.dumps({
            "mind": "Would destroy entire system",
            "heart": "User would lose everything",
            "conscience": "No legitimate use case"
        })
    ])
    
    print("✅ Sacred Council event stored in temporal database!")
    
    # Query it back
    result = trinity.temporal.conn.execute("""
        SELECT event_type, risk_level, verdict 
        FROM council_events 
        WHERE session_id = ?
    """, ["test-session-1"]).fetchall()
    
    print("\n📊 Retrieved Council events:")
    for row in result:
        print(f"  • {row[0]}: {row[1]} → {row[2]}")
    
    print("\n" + "=" * 70)
    print("✨ DATA TRINITY TEST COMPLETE!")
    print("=" * 70)
    
    print("\n🔱 The Data Trinity is fully operational:")
    print("  ⏰ Temporal patterns tracked in DuckDB")
    print("  🧠 Semantic understanding in ChromaDB")
    print("  🕸️ Knowledge relationships in Kùzu")
    print("\n🌊 Ready to build the Learning Mode on this foundation!")
    
    # Clean up
    trinity.close()
    print("\n🔒 Trinity connections closed")


if __name__ == "__main__":
    test_data_trinity()