#!/usr/bin/env python3
"""
🌍 Community Knowledge Sharing
Anonymous, privacy-preserving collective intelligence
Users help each other without revealing identity
"""

import json
import hashlib
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import re
import random
import string


@dataclass
class SharedPattern:
    """A pattern shared with the community"""
    pattern_id: str
    pattern_type: str  # error_solution, workflow, package_alias, config_template
    trigger: str
    solution: str
    confidence: float
    endorsements: int
    reports: int
    category: str
    anonymized: bool
    created_at: str
    last_seen: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_trust_score(self) -> float:
        """Calculate trust score based on community feedback"""
        if self.endorsements + self.reports == 0:
            return self.confidence
        
        trust = (self.endorsements - self.reports) / (self.endorsements + self.reports + 1)
        return max(0.1, min(1.0, self.confidence * (1 + trust)))


@dataclass 
class CommunityInsight:
    """Aggregated community wisdom"""
    topic: str
    insight_type: str  # tip, warning, recommendation, alternative
    content: str
    relevance_score: float
    contributor_count: int
    consensus_level: float  # Agreement among contributors
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PrivacyPreserver:
    """Ensures all shared data is properly anonymized"""
    
    def __init__(self):
        # Patterns to remove
        self.sensitive_patterns = [
            # User paths
            (r'/home/[^/\s]+', '/home/user'),
            (r'/Users/[^/\s]+', '/Users/user'),
            (r'~/', '/home/user/'),
            
            # Email addresses
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'user@example.com'),
            
            # IP addresses
            (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '192.168.1.1'),
            
            # Hostnames
            (r'[a-zA-Z0-9-]+\.local', 'hostname.local'),
            (r'[a-zA-Z0-9-]+\.lan', 'hostname.lan'),
            
            # SSH keys or tokens
            (r'ssh-[a-zA-Z0-9]+\s+[A-Za-z0-9+/=]+', 'ssh-xxx [key]'),
            (r'[a-fA-F0-9]{40,}', '[hash]'),
            
            # Custom store paths with hashes
            (r'/nix/store/[a-z0-9]{32}-', '/nix/store/[hash]-'),
        ]
        
        # Safe replacements for common tools
        self.safe_terms = {
            'firefox', 'chrome', 'vscode', 'vim', 'neovim', 'emacs',
            'python', 'nodejs', 'rust', 'go', 'java', 'docker',
            'nginx', 'apache', 'postgresql', 'mysql', 'redis'
        }
    
    def anonymize(self, text: str) -> str:
        """Remove all potentially identifying information"""
        result = text
        
        # Apply sensitive pattern replacements
        for pattern, replacement in self.sensitive_patterns:
            result = re.sub(pattern, replacement, result)
        
        # Remove custom package names that might identify user
        words = result.split()
        filtered = []
        for word in words:
            # Keep safe terms and common words
            if word.lower() in self.safe_terms or len(word) < 3:
                filtered.append(word)
            # Replace potentially custom names
            elif re.match(r'^[a-z]+-[a-z]+-[a-z]+$', word.lower()):
                filtered.append('[custom-package]')
            else:
                filtered.append(word)
        
        return ' '.join(filtered)
    
    def generate_anonymous_id(self) -> str:
        """Generate anonymous contributor ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


class CommunityKnowledge:
    """
    Manages community knowledge sharing
    Anonymous, privacy-preserving, collectively beneficial
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        # Setup data directory
        self.data_dir = data_dir or Path.home() / ".local/share/luminous-nix/community"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.data_dir / "community.db"
        self._init_database()
        
        # Privacy preserver
        self.privacy = PrivacyPreserver()
        
        # Configuration
        self.min_confidence_to_share = 0.7
        self.min_occurrences_to_share = 3
        self.auto_share = False  # Require explicit consent
        self.anonymous_id = self.privacy.generate_anonymous_id()
        
        # Cache for performance
        self.pattern_cache = {}
        self.insight_cache = {}
        
    def _init_database(self):
        """Initialize community database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Shared patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                trigger TEXT NOT NULL,
                solution TEXT NOT NULL,
                confidence REAL NOT NULL,
                endorsements INTEGER DEFAULT 0,
                reports INTEGER DEFAULT 0,
                category TEXT,
                contributor_id TEXT,
                anonymized INTEGER DEFAULT 1,
                created_at TEXT,
                last_seen TEXT,
                UNIQUE(pattern_type, trigger, solution)
            )
        ''')
        
        # Community insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                relevance_score REAL,
                contributor_count INTEGER DEFAULT 1,
                consensus_level REAL,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # User feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT,
                user_id TEXT,
                feedback_type TEXT,  -- endorsement, report, comment
                feedback_value TEXT,
                created_at TEXT,
                FOREIGN KEY(pattern_id) REFERENCES shared_patterns(pattern_id)
            )
        ''')
        
        # Pattern categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY,
                description TEXT,
                pattern_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        # Initialize default categories
        default_categories = [
            ('package_management', 'Installing and managing packages'),
            ('configuration', 'System and service configuration'),
            ('troubleshooting', 'Error solutions and fixes'),
            ('development', 'Development environment setup'),
            ('system_maintenance', 'Updates, cleanup, optimization'),
            ('hardware', 'Hardware-related configurations'),
            ('networking', 'Network configuration and issues'),
            ('security', 'Security-related patterns')
        ]
        
        for name, desc in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, description, created_at)
                VALUES (?, ?, ?)
            ''', (name, desc, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def share_pattern(
        self,
        pattern_type: str,
        trigger: str,
        solution: str,
        confidence: float,
        category: Optional[str] = None,
        auto_anonymize: bool = True
    ) -> Optional[str]:
        """
        Share a pattern with the community
        Returns pattern_id if successful
        """
        
        # Check minimum requirements
        if confidence < self.min_confidence_to_share:
            return None
        
        # Anonymize if requested
        if auto_anonymize:
            trigger = self.privacy.anonymize(trigger)
            solution = self.privacy.anonymize(solution)
        
        # Generate pattern ID
        pattern_data = f"{pattern_type}:{trigger}:{solution}"
        pattern_id = hashlib.sha256(pattern_data.encode()).hexdigest()[:16]
        
        # Determine category if not provided
        if not category:
            category = self._categorize_pattern(pattern_type, trigger, solution)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO shared_patterns 
                (pattern_id, pattern_type, trigger, solution, confidence,
                 category, contributor_id, anonymized, created_at, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_id,
                pattern_type,
                trigger,
                solution,
                confidence,
                category,
                self.anonymous_id,
                1 if auto_anonymize else 0,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            # Update category count
            cursor.execute('''
                UPDATE categories 
                SET pattern_count = pattern_count + 1
                WHERE name = ?
            ''', (category,))
            
            conn.commit()
            return pattern_id
            
        except sqlite3.IntegrityError:
            # Pattern already exists, update confidence if higher
            cursor.execute('''
                UPDATE shared_patterns
                SET confidence = MAX(confidence, ?),
                    last_seen = ?,
                    endorsements = endorsements + 1
                WHERE pattern_type = ? AND trigger = ? AND solution = ?
            ''', (confidence, datetime.now().isoformat(), pattern_type, trigger, solution))
            
            conn.commit()
            return pattern_id
            
        finally:
            conn.close()
    
    def search_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        category: Optional[str] = None,
        min_trust: float = 0.5
    ) -> List[SharedPattern]:
        """
        Search for relevant community patterns
        Returns patterns sorted by relevance and trust
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        sql = '''
            SELECT * FROM shared_patterns
            WHERE (trigger LIKE ? OR solution LIKE ?)
        '''
        params = [f'%{query}%', f'%{query}%']
        
        if pattern_type:
            sql += ' AND pattern_type = ?'
            params.append(pattern_type)
        
        if category:
            sql += ' AND category = ?'
            params.append(category)
        
        sql += ' ORDER BY confidence DESC, endorsements DESC'
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        conn.close()
        
        # Convert to SharedPattern objects
        patterns = []
        for row in results:
            pattern = SharedPattern(
                pattern_id=row[0],
                pattern_type=row[1],
                trigger=row[2],
                solution=row[3],
                confidence=row[4],
                endorsements=row[5],
                reports=row[6],
                category=row[7],
                anonymized=bool(row[9]),
                created_at=row[10],
                last_seen=row[11]
            )
            
            # Filter by trust score
            if pattern.get_trust_score() >= min_trust:
                patterns.append(pattern)
        
        return patterns
    
    def get_solution(self, error: str) -> Optional[str]:
        """
        Get community solution for an error
        Returns highest confidence solution
        """
        
        patterns = self.search_patterns(
            query=error,
            pattern_type='error_solution',
            min_trust=0.6
        )
        
        if patterns:
            # Return highest trust solution
            best = max(patterns, key=lambda p: p.get_trust_score())
            return best.solution
        
        return None
    
    def endorse_pattern(self, pattern_id: str, user_feedback: Optional[str] = None):
        """Endorse a helpful pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update endorsements
        cursor.execute('''
            UPDATE shared_patterns
            SET endorsements = endorsements + 1
            WHERE pattern_id = ?
        ''', (pattern_id,))
        
        # Record feedback
        cursor.execute('''
            INSERT INTO feedback (pattern_id, user_id, feedback_type, feedback_value, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            self.anonymous_id,
            'endorsement',
            user_feedback or '',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def report_pattern(self, pattern_id: str, reason: Optional[str] = None):
        """Report a problematic pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update reports
        cursor.execute('''
            UPDATE shared_patterns
            SET reports = reports + 1
            WHERE pattern_id = ?
        ''', (pattern_id,))
        
        # Record feedback
        cursor.execute('''
            INSERT INTO feedback (pattern_id, user_id, feedback_type, feedback_value, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            self.anonymous_id,
            'report',
            reason or '',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def synthesize_insights(self, topic: str) -> List[CommunityInsight]:
        """
        Synthesize community insights on a topic
        Aggregates patterns into higher-level wisdom
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find related patterns
        cursor.execute('''
            SELECT pattern_type, trigger, solution, confidence, endorsements
            FROM shared_patterns
            WHERE trigger LIKE ? OR solution LIKE ?
            ORDER BY endorsements DESC, confidence DESC
            LIMIT 20
        ''', (f'%{topic}%', f'%{topic}%'))
        
        patterns = cursor.fetchall()
        
        insights = []
        
        if patterns:
            # Analyze patterns for common themes
            solutions = defaultdict(list)
            warnings = []
            tips = []
            
            for ptype, trigger, solution, conf, endorse in patterns:
                if ptype == 'error_solution':
                    warnings.append(f"Common issue: {trigger[:50]}")
                    solutions[trigger].append(solution)
                elif ptype == 'workflow':
                    tips.append(f"Workflow: {trigger} → {solution}")
                
            # Create insights
            if warnings:
                insight = CommunityInsight(
                    topic=topic,
                    insight_type='warning',
                    content=f"Users frequently encounter: {', '.join(set(warnings[:3]))}",
                    relevance_score=0.8,
                    contributor_count=len(patterns),
                    consensus_level=0.7
                )
                insights.append(insight)
            
            if tips:
                insight = CommunityInsight(
                    topic=topic,
                    insight_type='tip',
                    content=f"Popular workflows: {'; '.join(tips[:3])}",
                    relevance_score=0.85,
                    contributor_count=len(tips),
                    consensus_level=0.8
                )
                insights.append(insight)
            
            # Most endorsed solution
            if solutions:
                best_solution = max(solutions.items(), key=lambda x: len(x[1]))
                insight = CommunityInsight(
                    topic=topic,
                    insight_type='recommendation',
                    content=f"Most common solution: {best_solution[1][0][:100]}",
                    relevance_score=0.9,
                    contributor_count=len(best_solution[1]),
                    consensus_level=0.85
                )
                insights.append(insight)
        
        conn.close()
        
        return insights
    
    def _categorize_pattern(self, pattern_type: str, trigger: str, solution: str) -> str:
        """Auto-categorize a pattern"""
        text = f"{trigger} {solution}".lower()
        
        # Category keywords
        categories = {
            'package_management': ['install', 'package', 'nix-env', 'update', 'remove'],
            'configuration': ['config', 'configure', 'enable', 'service', 'settings'],
            'troubleshooting': ['error', 'fail', 'broken', 'fix', 'solve'],
            'development': ['python', 'node', 'rust', 'dev', 'build', 'compile'],
            'system_maintenance': ['clean', 'garbage', 'rebuild', 'generation'],
            'hardware': ['driver', 'gpu', 'bluetooth', 'wifi', 'sound'],
            'networking': ['network', 'internet', 'vpn', 'firewall', 'port'],
            'security': ['permission', 'sudo', 'encrypt', 'secure', 'auth']
        }
        
        # Score each category
        scores = {}
        for cat, keywords in categories.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[cat] = score
        
        # Return highest scoring category
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return 'troubleshooting'  # Default
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get community knowledge statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total patterns
        cursor.execute('SELECT COUNT(*) FROM shared_patterns')
        total_patterns = cursor.fetchone()[0]
        
        # Patterns by category
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM shared_patterns 
            GROUP BY category
        ''')
        by_category = dict(cursor.fetchall())
        
        # Most endorsed patterns
        cursor.execute('''
            SELECT trigger, solution, endorsements
            FROM shared_patterns
            ORDER BY endorsements DESC
            LIMIT 5
        ''')
        top_patterns = cursor.fetchall()
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM shared_patterns
            WHERE datetime(created_at) > datetime('now', '-7 days')
        ''')
        recent_patterns = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_patterns': total_patterns,
            'by_category': by_category,
            'top_patterns': [
                {'trigger': t[:30], 'solution': s[:30], 'endorsements': e}
                for t, s, e in top_patterns
            ],
            'recent_activity': recent_patterns,
            'contributors': 'anonymous'  # Always anonymous
        }


# Global community instance
_COMMUNITY: Optional[CommunityKnowledge] = None

def get_community_knowledge() -> CommunityKnowledge:
    """Get or create community knowledge instance"""
    global _COMMUNITY
    if _COMMUNITY is None:
        _COMMUNITY = CommunityKnowledge()
    return _COMMUNITY


if __name__ == "__main__":
    # Test community knowledge
    community = get_community_knowledge()
    
    print("🌍 Testing Community Knowledge\n")
    print("=" * 60)
    
    # Test pattern sharing
    test_patterns = [
        ("error_solution", "attribute firefox not found", "search firefox first", 0.9),
        ("workflow", "install editor", "search editor → install neovim", 0.8),
        ("package_alias", "vscode", "code", 0.95),
        ("error_solution", "permission denied", "use sudo", 0.85),
    ]
    
    print("📤 Sharing patterns...")
    for ptype, trigger, solution, conf in test_patterns:
        pattern_id = community.share_pattern(ptype, trigger, solution, conf)
        if pattern_id:
            print(f"  ✅ Shared: {trigger[:30]}... → {solution[:30]}...")
    
    # Test pattern search
    print("\n🔍 Searching for 'firefox' solutions:")
    patterns = community.search_patterns("firefox")
    for pattern in patterns:
        print(f"  • {pattern.trigger} → {pattern.solution}")
        print(f"    Trust: {pattern.get_trust_score():.0%}")
    
    # Test community insights
    print("\n💡 Community insights for 'editor':")
    insights = community.synthesize_insights("editor")
    for insight in insights:
        print(f"  • {insight.insight_type}: {insight.content}")
    
    # Test statistics
    print("\n📊 Community Statistics:")
    stats = community.get_statistics()
    print(f"  Total patterns: {stats['total_patterns']}")
    print(f"  By category: {stats['by_category']}")
    
    # Test privacy
    print("\n🔒 Privacy Test:")
    private_text = "Install firefox at /home/john/apps with token abc123"
    anonymized = community.privacy.anonymize(private_text)
    print(f"  Original: {private_text}")
    print(f"  Anonymized: {anonymized}")