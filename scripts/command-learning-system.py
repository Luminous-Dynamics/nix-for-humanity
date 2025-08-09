#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Command Learning System for Nix for Humanity
Learns from successful commands to improve future suggestions
Building toward AI partner through continuous improvement
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re

class CommandLearningSystem:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.learning_db = self.base_dir / "command_learning.db"
        self.init_database()
        
    def init_database(self):
        """Initialize learning database"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        # Command history with outcomes
        c.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT NOT NULL,
                original_query TEXT NOT NULL,
                suggested_command TEXT NOT NULL,
                executed BOOLEAN DEFAULT 0,
                success BOOLEAN,
                error_message TEXT,
                user_feedback TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Successful patterns to learn from
        c.execute('''
            CREATE TABLE IF NOT EXISTS successful_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT NOT NULL,
                query_pattern TEXT NOT NULL,
                command_template TEXT NOT NULL,
                success_count INTEGER DEFAULT 1,
                failure_count INTEGER DEFAULT 0,
                confidence_score REAL DEFAULT 0.5,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Common errors and their solutions
        c.execute('''
            CREATE TABLE IF NOT EXISTS error_solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_pattern TEXT NOT NULL,
                solution TEXT NOT NULL,
                helpful_count INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User preferences learned over time
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                preference_key TEXT PRIMARY KEY,
                preference_value TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                observation_count INTEGER DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def record_command(self, intent: str, query: str, command: str, executed: bool = False) -> int:
        """Record a command suggestion"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO command_history (intent, original_query, suggested_command, executed)
            VALUES (?, ?, ?, ?)
        ''', (intent, query, command, executed))
        
        command_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return command_id
        
    def record_outcome(self, command_id: int, success: bool, error: Optional[str] = None):
        """Record the outcome of a command execution"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        c.execute('''
            UPDATE command_history 
            SET success = ?, error_message = ?
            WHERE id = ?
        ''', (success, error, command_id))
        
        # If successful, learn from it
        if success:
            # Get the command details
            c.execute('''
                SELECT intent, original_query, suggested_command
                FROM command_history
                WHERE id = ?
            ''', (command_id,))
            
            result = c.fetchone()
            if result:
                intent, query, command = result
                self._learn_successful_pattern(intent, query, command)
                
        conn.commit()
        conn.close()
        
    def _learn_successful_pattern(self, intent: str, query: str, command: str):
        """Learn from a successful command execution"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        # Extract pattern from query (simplified for now)
        query_pattern = self._extract_pattern(query)
        
        # Check if pattern exists
        c.execute('''
            SELECT id, success_count, failure_count
            FROM successful_patterns
            WHERE intent = ? AND query_pattern = ?
        ''', (intent, query_pattern))
        
        result = c.fetchone()
        
        if result:
            # Update existing pattern
            pattern_id, success_count, failure_count = result
            new_confidence = (success_count + 1) / (success_count + failure_count + 2)
            
            c.execute('''
                UPDATE successful_patterns
                SET success_count = success_count + 1,
                    confidence_score = ?,
                    last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_confidence, pattern_id))
        else:
            # Create new pattern
            c.execute('''
                INSERT INTO successful_patterns 
                (intent, query_pattern, command_template)
                VALUES (?, ?, ?)
            ''', (intent, query_pattern, command))
            
        conn.commit()
        conn.close()
        
    def _extract_pattern(self, query: str) -> str:
        """Extract a generalized pattern from a query"""
        # Simple pattern extraction - can be made more sophisticated
        pattern = query.lower()
        
        # Replace package names with placeholder
        packages = ['firefox', 'chrome', 'vscode', 'vim', 'python', 'nodejs']
        for pkg in packages:
            pattern = pattern.replace(pkg, '<package>')
            
        # Replace version numbers
        pattern = re.sub(r'\d+\.\d+', '<version>', pattern)
        
        return pattern
        
    def get_learned_suggestions(self, intent: str, query: str) -> List[Dict]:
        """Get suggestions based on learned patterns"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        query_pattern = self._extract_pattern(query)
        
        # Find matching patterns
        results = c.execute('''
            SELECT command_template, confidence_score, success_count
            FROM successful_patterns
            WHERE intent = ? AND confidence_score > 0.6
            ORDER BY confidence_score DESC, success_count DESC
            LIMIT 3
        ''', (intent,)).fetchall()
        
        suggestions = []
        for cmd_template, confidence, count in results:
            suggestions.append({
                'command': cmd_template,
                'confidence': confidence,
                'learned_from': f"{count} successful uses"
            })
            
        conn.close()
        return suggestions
        
    def learn_user_preference(self, key: str, value: str):
        """Learn a user preference over time"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (preference_key, preference_value, observation_count, last_updated)
            VALUES (
                ?,
                ?,
                COALESCE((SELECT observation_count FROM user_preferences WHERE preference_key = ?), 0) + 1,
                CURRENT_TIMESTAMP
            )
        ''', (key, value, key))
        
        conn.commit()
        conn.close()
        
    def get_user_preferences(self) -> Dict[str, str]:
        """Get learned user preferences"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        results = c.execute('''
            SELECT preference_key, preference_value, confidence
            FROM user_preferences
            WHERE confidence > 0.6
            ORDER BY confidence DESC
        ''').fetchall()
        
        preferences = {key: value for key, value, _ in results}
        
        conn.close()
        return preferences
        
    def record_error_solution(self, error: str, solution: str):
        """Record a solution for an error"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        # Normalize error pattern
        error_pattern = error.lower().strip()
        
        c.execute('''
            INSERT OR REPLACE INTO error_solutions
            (error_pattern, solution, last_seen)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (error_pattern, solution))
        
        conn.commit()
        conn.close()
        
    def get_error_solution(self, error: str) -> Optional[str]:
        """Get a learned solution for an error"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        error_lower = error.lower()
        
        # Find matching error patterns
        result = c.execute('''
            SELECT solution
            FROM error_solutions
            WHERE ? LIKE '%' || error_pattern || '%'
            ORDER BY helpful_count DESC
            LIMIT 1
        ''', (error_lower,)).fetchone()
        
        conn.close()
        
        return result[0] if result else None
        
    def get_success_rate(self, intent: str) -> float:
        """Get success rate for a specific intent"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        # Get counts for this specific intent
        total = c.execute('''
            SELECT COUNT(*) FROM command_history 
            WHERE intent = ? AND executed = 1
        ''', (intent,)).fetchone()[0]
        
        successful = c.execute('''
            SELECT COUNT(*) FROM command_history 
            WHERE intent = ? AND executed = 1 AND success = 1
        ''', (intent,)).fetchone()[0]
        
        conn.close()
        
        if total > 0:
            return successful / total
        else:
            return 0.0
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about the learning system"""
        conn = sqlite3.connect(self.learning_db)
        c = conn.cursor()
        
        stats = {
            'total_commands': c.execute('SELECT COUNT(*) FROM command_history').fetchone()[0],
            'successful_commands': c.execute('SELECT COUNT(*) FROM command_history WHERE success = 1').fetchone()[0],
            'learned_patterns': c.execute('SELECT COUNT(*) FROM successful_patterns').fetchone()[0],
            'high_confidence_patterns': c.execute('SELECT COUNT(*) FROM successful_patterns WHERE confidence_score > 0.8').fetchone()[0],
            'user_preferences': c.execute('SELECT COUNT(*) FROM user_preferences').fetchone()[0],
            'error_solutions': c.execute('SELECT COUNT(*) FROM error_solutions').fetchone()[0]
        }
        
        # Calculate success rate
        if stats['total_commands'] > 0:
            stats['success_rate'] = stats['successful_commands'] / stats['total_commands']
        else:
            stats['success_rate'] = 0
            
        conn.close()
        return stats


def main():
    """Test the learning system"""
    learning = CommandLearningSystem()
    
    print("🧠 Command Learning System Test\n")
    print("=" * 50)
    
    # Simulate some commands
    print("📝 Recording sample commands...")
    
    # Record some successful installs
    cmd_id1 = learning.record_command("install_package", "install firefox", "nix profile install nixpkgs#firefox", True)
    learning.record_outcome(cmd_id1, True)
    
    cmd_id2 = learning.record_command("install_package", "install vscode", "nix profile install nixpkgs#vscode", True)
    learning.record_outcome(cmd_id2, True)
    
    # Record a failed command
    cmd_id3 = learning.record_command("install_package", "install asdf", "nix profile install nixpkgs#asdf", True)
    learning.record_outcome(cmd_id3, False, "Package not found")
    
    # Learn some preferences
    learning.learn_user_preference("install_method", "nix_profile")
    learning.learn_user_preference("personality", "friendly")
    
    # Learn an error solution
    learning.record_error_solution("package not found", "Try searching with: nix search nixpkgs <package>")
    
    print("✅ Sample data recorded\n")
    
    # Show stats
    stats = learning.get_learning_stats()
    print("📊 Learning System Statistics:")
    print(f"   Total commands tracked: {stats['total_commands']}")
    print(f"   Successful commands: {stats['successful_commands']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Learned patterns: {stats['learned_patterns']}")
    print(f"   High confidence patterns: {stats['high_confidence_patterns']}")
    print(f"   User preferences learned: {stats['user_preferences']}")
    print(f"   Error solutions: {stats['error_solutions']}")
    
    print("\n🎯 Learned Preferences:")
    prefs = learning.get_user_preferences()
    for key, value in prefs.items():
        print(f"   {key}: {value}")
        
    print("\n💡 Building toward AI partnership through continuous learning!")


if __name__ == "__main__":
    main()