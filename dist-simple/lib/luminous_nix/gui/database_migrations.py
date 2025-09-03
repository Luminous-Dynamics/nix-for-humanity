#!/usr/bin/env python3
"""
🗄️ Database Migration System for AI-Driven Interface Generation
Handles schema versioning and migrations for SQLite database
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import hashlib

from error_handler import safe_database_operation, get_logger


@dataclass
class Migration:
    """Represents a database migration"""
    
    version: int
    name: str
    description: str
    sql_up: str  # SQL to apply migration
    sql_down: str  # SQL to rollback migration
    checksum: str = ""
    applied_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate checksum if not provided"""
        if not self.checksum:
            content = f"{self.version}{self.name}{self.sql_up}{self.sql_down}"
            self.checksum = hashlib.sha256(content.encode()).hexdigest()[:16]


class DatabaseMigrationManager:
    """Manages database schema migrations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger(__name__)
        self.conn = sqlite3.connect(db_path)
        self.migrations: List[Migration] = []
        
        # Initialize migration tracking table
        self._init_migration_table()
        
        # Register all migrations
        self._register_migrations()
    
    @safe_database_operation(default_return=None)
    def _init_migration_table(self):
        """Create migration tracking table"""
        
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                checksum TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
        """)
        self.conn.commit()
    
    def _register_migrations(self):
        """Register all database migrations"""
        
        self.migrations = [
            # Migration 001: Initial schema
            Migration(
                version=1,
                name="initial_schema",
                description="Create initial database schema",
                sql_up="""
                    -- Interface generation tables
                    CREATE TABLE IF NOT EXISTS generated_interfaces (
                        id TEXT PRIMARY KEY,
                        request TEXT NOT NULL,
                        interface_json TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        parent_id TEXT,
                        generation_time REAL
                    );
                    
                    CREATE TABLE IF NOT EXISTS interface_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interface_id TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        value REAL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (interface_id) REFERENCES generated_interfaces(id)
                    );
                    
                    -- Component evolution tables
                    CREATE TABLE IF NOT EXISTS component_dna (
                        id TEXT PRIMARY KEY,
                        base_type TEXT NOT NULL,
                        traits TEXT NOT NULL,
                        performance_score REAL DEFAULT 0,
                        usage_count INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL,
                        parent_id TEXT
                    );
                    
                    -- Learning and patterns
                    CREATE TABLE IF NOT EXISTS learning_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interface_id TEXT,
                        action TEXT,
                        outcome TEXT,
                        feedback REAL,
                        timestamp TEXT NOT NULL
                    );
                    
                    -- Create indexes
                    CREATE INDEX idx_interfaces_user ON generated_interfaces(user_id);
                    CREATE INDEX idx_interfaces_session ON generated_interfaces(session_id);
                    CREATE INDEX idx_metrics_interface ON interface_metrics(interface_id);
                    CREATE INDEX idx_learning_timestamp ON learning_records(timestamp);
                """,
                sql_down="""
                    DROP TABLE IF EXISTS learning_records;
                    DROP TABLE IF EXISTS component_dna;
                    DROP TABLE IF EXISTS interface_metrics;
                    DROP TABLE IF EXISTS generated_interfaces;
                """
            ),
            
            # Migration 002: Add user interaction tracking
            Migration(
                version=2,
                name="user_interactions",
                description="Add user interaction tracking tables",
                sql_up="""
                    CREATE TABLE IF NOT EXISTS user_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interface_id TEXT,
                        interface_type TEXT,
                        action_sequence TEXT,
                        completion_time REAL,
                        success BOOLEAN,
                        timestamp TEXT NOT NULL,
                        user_id TEXT,
                        FOREIGN KEY (interface_id) REFERENCES generated_interfaces(id)
                    );
                    
                    CREATE TABLE IF NOT EXISTS interface_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interface_id TEXT,
                        components_used TEXT,
                        satisfaction_score REAL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (interface_id) REFERENCES generated_interfaces(id)
                    );
                    
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        user_id TEXT,
                        navigation_path TEXT,
                        total_time REAL,
                        started_at TEXT NOT NULL,
                        ended_at TEXT
                    );
                    
                    CREATE TABLE IF NOT EXISTS error_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_type TEXT,
                        error_message TEXT,
                        interface_context TEXT,
                        timestamp TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT
                    );
                    
                    CREATE INDEX idx_interactions_user ON user_interactions(user_id);
                    CREATE INDEX idx_interactions_timestamp ON user_interactions(timestamp);
                    CREATE INDEX idx_sessions_user ON user_sessions(user_id);
                    CREATE INDEX idx_errors_timestamp ON error_logs(timestamp);
                """,
                sql_down="""
                    DROP TABLE IF EXISTS error_logs;
                    DROP TABLE IF EXISTS user_sessions;
                    DROP TABLE IF EXISTS interface_interactions;
                    DROP TABLE IF EXISTS user_interactions;
                """
            ),
            
            # Migration 003: Add pattern analysis tables
            Migration(
                version=3,
                name="pattern_analysis",
                description="Add pattern analysis and insights tables",
                sql_up="""
                    CREATE TABLE IF NOT EXISTS usage_patterns (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        pattern_type TEXT,
                        sequence TEXT,
                        frequency INTEGER,
                        confidence REAL,
                        users_affected INTEGER,
                        avg_completion_time REAL,
                        success_rate REAL,
                        optimization_score REAL,
                        detected_at TEXT NOT NULL,
                        last_seen TEXT
                    );
                    
                    CREATE TABLE IF NOT EXISTS insights (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        description TEXT,
                        category TEXT,
                        priority TEXT,
                        confidence REAL,
                        evidence TEXT,
                        recommendations TEXT,
                        expected_impact TEXT,
                        implementation_effort TEXT,
                        created_at TEXT NOT NULL,
                        acknowledged BOOLEAN DEFAULT 0,
                        implemented BOOLEAN DEFAULT 0
                    );
                    
                    CREATE INDEX idx_patterns_type ON usage_patterns(pattern_type);
                    CREATE INDEX idx_patterns_score ON usage_patterns(optimization_score);
                    CREATE INDEX idx_insights_priority ON insights(priority);
                    CREATE INDEX idx_insights_category ON insights(category);
                """,
                sql_down="""
                    DROP TABLE IF EXISTS insights;
                    DROP TABLE IF EXISTS usage_patterns;
                """
            ),
            
            # Migration 004: Add feedback collection tables
            Migration(
                version=4,
                name="feedback_system",
                description="Add feedback collection and sentiment tracking",
                sql_up="""
                    CREATE TABLE IF NOT EXISTS feedback_items (
                        id TEXT PRIMARY KEY,
                        user_id TEXT,
                        interface_id TEXT,
                        feedback_type TEXT,
                        value TEXT,
                        timestamp TEXT NOT NULL,
                        interface_type TEXT,
                        task TEXT,
                        variant_id TEXT,
                        session_id TEXT,
                        time_to_feedback REAL,
                        interaction_count INTEGER,
                        error_occurred BOOLEAN,
                        sentiment REAL,
                        FOREIGN KEY (interface_id) REFERENCES generated_interfaces(id)
                    );
                    
                    CREATE TABLE IF NOT EXISTS feedback_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT,
                        started_at TEXT NOT NULL,
                        ended_at TEXT,
                        interfaces_viewed INTEGER DEFAULT 0,
                        tasks_completed INTEGER DEFAULT 0,
                        tasks_attempted INTEGER DEFAULT 0,
                        total_interactions INTEGER DEFAULT 0,
                        total_time REAL,
                        overall_satisfaction REAL,
                        task_success_rate REAL
                    );
                    
                    CREATE INDEX idx_feedback_user ON feedback_items(user_id);
                    CREATE INDEX idx_feedback_interface ON feedback_items(interface_id);
                    CREATE INDEX idx_feedback_timestamp ON feedback_items(timestamp);
                    CREATE INDEX idx_feedback_sentiment ON feedback_items(sentiment);
                """,
                sql_down="""
                    DROP TABLE IF EXISTS feedback_sessions;
                    DROP TABLE IF EXISTS feedback_items;
                """
            ),
            
            # Migration 005: Add A/B testing tables
            Migration(
                version=5,
                name="ab_testing",
                description="Add A/B testing framework tables",
                sql_up="""
                    CREATE TABLE IF NOT EXISTS ab_tests (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        variation_type TEXT,
                        status TEXT DEFAULT 'active',
                        created_at TEXT NOT NULL,
                        started_at TEXT,
                        ended_at TEXT,
                        minimum_sample_size INTEGER,
                        confidence_level REAL
                    );
                    
                    CREATE TABLE IF NOT EXISTS ab_variants (
                        id TEXT PRIMARY KEY,
                        test_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        parameters TEXT,
                        impressions INTEGER DEFAULT 0,
                        conversions INTEGER DEFAULT 0,
                        total_value REAL DEFAULT 0,
                        error_count INTEGER DEFAULT 0,
                        FOREIGN KEY (test_id) REFERENCES ab_tests(id)
                    );
                    
                    CREATE TABLE IF NOT EXISTS ab_assignments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id TEXT NOT NULL,
                        variant_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        assigned_at TEXT NOT NULL,
                        converted BOOLEAN DEFAULT 0,
                        conversion_value REAL,
                        FOREIGN KEY (test_id) REFERENCES ab_tests(id),
                        FOREIGN KEY (variant_id) REFERENCES ab_variants(id)
                    );
                    
                    CREATE INDEX idx_tests_status ON ab_tests(status);
                    CREATE INDEX idx_variants_test ON ab_variants(test_id);
                    CREATE INDEX idx_assignments_user ON ab_assignments(user_id);
                    CREATE INDEX idx_assignments_test ON ab_assignments(test_id);
                """,
                sql_down="""
                    DROP TABLE IF EXISTS ab_assignments;
                    DROP TABLE IF EXISTS ab_variants;
                    DROP TABLE IF EXISTS ab_tests;
                """
            ),
            
            # Migration 006: Add optimization tracking
            Migration(
                version=6,
                name="optimization_tracking",
                description="Add automatic optimization tracking",
                sql_up="""
                    CREATE TABLE IF NOT EXISTS optimization_rules (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        optimization_type TEXT,
                        trigger_metric TEXT,
                        trigger_threshold REAL,
                        trigger_comparison TEXT,
                        action TEXT,
                        parameters TEXT,
                        min_confidence REAL,
                        cooldown_hours INTEGER,
                        last_applied TEXT,
                        times_applied INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0
                    );
                    
                    CREATE TABLE IF NOT EXISTS optimization_results (
                        id TEXT PRIMARY KEY,
                        rule_id TEXT,
                        timestamp TEXT NOT NULL,
                        target_type TEXT,
                        target_id TEXT,
                        changes_applied TEXT,
                        rollback_data TEXT,
                        metrics_before TEXT,
                        metrics_after TEXT,
                        improvement REAL,
                        status TEXT,
                        confidence REAL,
                        FOREIGN KEY (rule_id) REFERENCES optimization_rules(id)
                    );
                    
                    CREATE INDEX idx_rules_type ON optimization_rules(optimization_type);
                    CREATE INDEX idx_results_rule ON optimization_results(rule_id);
                    CREATE INDEX idx_results_status ON optimization_results(status);
                    CREATE INDEX idx_results_timestamp ON optimization_results(timestamp);
                """,
                sql_down="""
                    DROP TABLE IF EXISTS optimization_results;
                    DROP TABLE IF EXISTS optimization_rules;
                """
            ),
            
            # Migration 007: Add performance metrics
            Migration(
                version=7,
                name="performance_metrics",
                description="Add detailed performance tracking",
                sql_up="""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        component TEXT,
                        timestamp TEXT NOT NULL,
                        session_id TEXT,
                        interface_id TEXT
                    );
                    
                    CREATE TABLE IF NOT EXISTS performance_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        period_start TEXT NOT NULL,
                        period_end TEXT NOT NULL,
                        avg_generation_time REAL,
                        avg_response_time REAL,
                        total_generations INTEGER,
                        error_rate REAL,
                        peak_memory_mb REAL,
                        avg_cpu_percent REAL
                    );
                    
                    CREATE INDEX idx_perf_metrics_name ON performance_metrics(metric_name);
                    CREATE INDEX idx_perf_metrics_timestamp ON performance_metrics(timestamp);
                    CREATE INDEX idx_perf_summaries_period ON performance_summaries(period_start, period_end);
                """,
                sql_down="""
                    DROP TABLE IF EXISTS performance_summaries;
                    DROP TABLE IF EXISTS performance_metrics;
                """
            )
        ]
    
    @safe_database_operation(default_return=0)
    def get_current_version(self) -> int:
        """Get current database schema version"""
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT MAX(version) FROM schema_migrations
        """)
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0
    
    @safe_database_operation(default_return=False)
    def is_migration_applied(self, migration: Migration) -> bool:
        """Check if a migration has been applied"""
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM schema_migrations
            WHERE version = ? AND checksum = ?
        """, (migration.version, migration.checksum))
        
        result = cursor.fetchone()
        return result[0] > 0 if result else False
    
    @safe_database_operation(default_return=False)
    def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration"""
        
        if self.is_migration_applied(migration):
            self.logger.info(f"Migration {migration.version}: {migration.name} already applied")
            return True
        
        self.logger.info(f"Applying migration {migration.version}: {migration.name}")
        
        try:
            cursor = self.conn.cursor()
            
            # Execute migration SQL
            for statement in migration.sql_up.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            # Record migration
            cursor.execute("""
                INSERT INTO schema_migrations (version, name, description, checksum, applied_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                migration.version,
                migration.name,
                migration.description,
                migration.checksum,
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            self.logger.info(f"Migration {migration.version} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply migration {migration.version}: {e}")
            self.conn.rollback()
            return False
    
    @safe_database_operation(default_return=False)
    def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a single migration"""
        
        if not self.is_migration_applied(migration):
            self.logger.info(f"Migration {migration.version} not applied, nothing to rollback")
            return True
        
        self.logger.info(f"Rolling back migration {migration.version}: {migration.name}")
        
        try:
            cursor = self.conn.cursor()
            
            # Execute rollback SQL
            for statement in migration.sql_down.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            # Remove migration record
            cursor.execute("""
                DELETE FROM schema_migrations WHERE version = ?
            """, (migration.version,))
            
            self.conn.commit()
            self.logger.info(f"Migration {migration.version} rolled back successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback migration {migration.version}: {e}")
            self.conn.rollback()
            return False
    
    def migrate_to_version(self, target_version: Optional[int] = None) -> bool:
        """Migrate database to specific version (or latest)"""
        
        current_version = self.get_current_version()
        
        if target_version is None:
            target_version = max(m.version for m in self.migrations)
        
        self.logger.info(f"Migrating from version {current_version} to {target_version}")
        
        if current_version == target_version:
            self.logger.info("Already at target version")
            return True
        
        if current_version < target_version:
            # Apply forward migrations
            for migration in sorted(self.migrations, key=lambda m: m.version):
                if current_version < migration.version <= target_version:
                    if not self.apply_migration(migration):
                        return False
        else:
            # Apply backward migrations
            for migration in sorted(self.migrations, key=lambda m: m.version, reverse=True):
                if target_version < migration.version <= current_version:
                    if not self.rollback_migration(migration):
                        return False
        
        self.logger.info(f"Migration complete. Now at version {self.get_current_version()}")
        return True
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        
        current_version = self.get_current_version()
        latest_version = max(m.version for m in self.migrations) if self.migrations else 0
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT version, name, applied_at FROM schema_migrations
            ORDER BY version
        """)
        
        applied = []
        for row in cursor.fetchall():
            applied.append({
                "version": row[0],
                "name": row[1],
                "applied_at": row[2]
            })
        
        pending = []
        for migration in self.migrations:
            if migration.version > current_version:
                pending.append({
                    "version": migration.version,
                    "name": migration.name,
                    "description": migration.description
                })
        
        return {
            "current_version": current_version,
            "latest_version": latest_version,
            "up_to_date": current_version == latest_version,
            "applied_migrations": applied,
            "pending_migrations": pending
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def demo_migrations():
    """Demonstrate database migration system"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        🗄️ DATABASE MIGRATION SYSTEM DEMO                           ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create test database
    test_db = "/tmp/test_migrations.db"
    manager = DatabaseMigrationManager(test_db)
    
    # Check initial status
    print("\n📊 Initial Status:")
    print("-" * 60)
    status = manager.get_migration_status()
    print(f"   Current version: {status['current_version']}")
    print(f"   Latest version: {status['latest_version']}")
    print(f"   Up to date: {status['up_to_date']}")
    
    # Apply all migrations
    print("\n⬆️ Applying Migrations:")
    print("-" * 60)
    success = manager.migrate_to_version()
    print(f"   Migration successful: {success}")
    
    # Check status after migration
    print("\n📊 Status After Migration:")
    print("-" * 60)
    status = manager.get_migration_status()
    print(f"   Current version: {status['current_version']}")
    print(f"   Applied migrations: {len(status['applied_migrations'])}")
    
    for migration in status['applied_migrations']:
        print(f"     ✓ v{migration['version']}: {migration['name']}")
    
    # Test rollback
    print("\n⬇️ Testing Rollback to Version 5:")
    print("-" * 60)
    success = manager.migrate_to_version(5)
    print(f"   Rollback successful: {success}")
    
    status = manager.get_migration_status()
    print(f"   Current version: {status['current_version']}")
    print(f"   Pending migrations: {len(status['pending_migrations'])}")
    
    for migration in status['pending_migrations']:
        print(f"     ⏳ v{migration['version']}: {migration['name']}")
    
    # Migrate back to latest
    print("\n⬆️ Migrating Back to Latest:")
    print("-" * 60)
    success = manager.migrate_to_version()
    print(f"   Migration successful: {success}")
    print(f"   Final version: {manager.get_current_version()}")
    
    manager.close()
    
    print("""

═══════════════════════════════════════════════════════════════════════
✨ Database Migration Features:

1. Schema Versioning:
   • Tracked migrations with checksums
   • Forward and backward migrations
   • Atomic operations with rollback

2. Migration Management:
   • Apply to specific version
   • Rollback capabilities
   • Status tracking

3. Safety Features:
   • Checksum validation
   • Transaction support
   • Error handling

4. Comprehensive Schema:
   • 7 migrations covering all tables
   • Proper indexes for performance
   • Foreign key constraints

5. Easy Extension:
   • Add new migrations easily
   • Clear migration structure
   • Documented changes

Next Steps:
• Integrate with application startup
• Add migration CLI commands
• Create backup before migrations
• Add migration validation
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_migrations()