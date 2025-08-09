#!/usr/bin/env python3
"""
Initialize the Symbiotic Knowledge Graph database tables

This script creates the necessary tables for SKG to function properly.
"""

import sqlite3
import os
from pathlib import Path


def initialize_skg_database(db_path: str = "./nix_humanity_skg.db"):
    """Create all necessary tables for the SKG"""
    
    # Ensure directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create nodes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create edges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edges (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            type TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source) REFERENCES nodes(id),
            FOREIGN KEY (target) REFERENCES nodes(id)
        )
    ''')
    
    # Create interactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            intent TEXT NOT NULL,
            context TEXT NOT NULL,
            outcome TEXT NOT NULL,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create patterns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            confidence REAL NOT NULL,
            data TEXT NOT NULL,
            interaction_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_models table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_models (
            user_id TEXT PRIMARY KEY,
            cognitive_state TEXT,
            affective_state TEXT,
            preference_state TEXT,
            trust_level REAL DEFAULT 0.5,
            interaction_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indices for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)')
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"✅ SKG database initialized at: {db_path}")
    print("✅ Created tables: nodes, edges, interactions, patterns, user_models")
    print("✅ Created performance indices")


if __name__ == "__main__":
    import sys
    
    # Use command line argument if provided, otherwise use env var
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = os.getenv('NIX_HUMANITY_SKG_PATH', './nix_humanity_skg.db')
    
    initialize_skg_database(db_path)