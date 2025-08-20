"""
from typing import List, Dict, Optional
Feedback collection and management

This module handles user feedback collection for continuous improvement.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class FeedbackCollector:
    """Collect and manage user feedback"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize feedback collector
        
        Args:
            data_dir: Directory for storing feedback data
        """
        if data_dir is None:
            data_dir = Path.home() / '.local' / 'share' / 'nix-for-humanity'
            
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / 'feedback.db'
        self._init_database()
        
    def _init_database(self):
        """Initialize the feedback database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Feedback table
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY,
                feedback_id TEXT UNIQUE NOT NULL,
                session_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                helpful BOOLEAN,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                improved_response TEXT,
                user_comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Usage patterns table
        c.execute('''
            CREATE TABLE IF NOT EXISTS usage_patterns (
                id INTEGER PRIMARY KEY,
                session_id TEXT NOT NULL,
                action TEXT NOT NULL,
                context TEXT NOT NULL,
                success BOOLEAN,
                duration_ms INTEGER,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feature requests table
        c.execute('''
            CREATE TABLE IF NOT EXISTS feature_requests (
                id INTEGER PRIMARY KEY,
                request_id TEXT UNIQUE NOT NULL,
                session_id TEXT NOT NULL,
                request_text TEXT NOT NULL,
                category TEXT,
                priority INTEGER DEFAULT 3,
                status TEXT DEFAULT 'new',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def collect_feedback(
        self,
        session_id: str,
        query: str,
        response: str,
        helpful: Optional[bool] = None,
        rating: Optional[int] = None,
        improved_response: Optional[str] = None,
        user_comment: Optional[str] = None
    ) -> str:
        """
        Collect user feedback
        
        Args:
            session_id: Current session identifier
            query: User's original query
            response: System's response
            helpful: Whether the response was helpful
            rating: Rating from 1-5
            improved_response: User's suggested improvement
            user_comment: Additional comments
            
        Returns:
            Feedback ID for reference
        """
        feedback_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO feedback 
            (feedback_id, session_id, query, response, helpful, rating, 
             improved_response, user_comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_id, session_id, query, response, helpful, rating,
            improved_response, user_comment
        ))
        
        conn.commit()
        conn.close()
        
        return feedback_id
        
    def track_usage(
        self,
        session_id: str,
        action: str,
        context: Dict[str, Any],
        success: bool,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """
        Track usage patterns
        
        Args:
            session_id: Current session identifier
            action: Action performed (e.g., "install_package")
            context: Additional context data
            success: Whether the action succeeded
            duration_ms: How long the action took
            error_message: Error if failed
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO usage_patterns
            (session_id, action, context, success, duration_ms, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id, action, json.dumps(context), success,
            duration_ms, error_message
        ))
        
        conn.commit()
        conn.close()
        
    def record_feature_request(
        self,
        session_id: str,
        request_text: str,
        category: Optional[str] = None,
        priority: int = 3
    ) -> str:
        """
        Record a feature request
        
        Args:
            session_id: Current session identifier
            request_text: Feature request description
            category: Category (e.g., "ui", "functionality", "integration")
            priority: Priority 1-5 (1 is highest)
            
        Returns:
            Request ID for reference
        """
        request_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO feature_requests
            (request_id, session_id, request_text, category, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (request_id, session_id, request_text, category, priority))
        
        conn.commit()
        conn.close()
        
        return request_id
        
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary statistics of feedback"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Total feedback
        c.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = c.fetchone()[0]
        
        # Helpfulness rate
        c.execute('''
            SELECT 
                COUNT(CASE WHEN helpful = 1 THEN 1 END) as helpful_count,
                COUNT(CASE WHEN helpful IS NOT NULL THEN 1 END) as rated_count
            FROM feedback
        ''')
        helpful_count, rated_count = c.fetchone()
        helpfulness_rate = helpful_count / rated_count if rated_count > 0 else 0
        
        # Average rating
        c.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
        avg_rating = c.fetchone()[0] or 0
        
        # Usage patterns
        c.execute('SELECT COUNT(*) FROM usage_patterns')
        total_patterns = c.fetchone()[0]
        
        # Success rate
        c.execute('''
            SELECT 
                COUNT(CASE WHEN success = 1 THEN 1 END) as success_count,
                COUNT(*) as total_count
            FROM usage_patterns
        ''')
        success_count, total_count = c.fetchone()
        success_rate = success_count / total_count if total_count > 0 else 0
        
        # Feature requests
        c.execute('SELECT COUNT(*) FROM feature_requests')
        total_requests = c.fetchone()[0]
        
        # Most common actions
        c.execute('''
            SELECT action, COUNT(*) as count
            FROM usage_patterns
            GROUP BY action
            ORDER BY count DESC
            LIMIT 5
        ''')
        common_actions = [{'action': row[0], 'count': row[1]} for row in c.fetchall()]
        
        conn.close()
        
        return {
            'total_feedback': total_feedback,
            'helpfulness_rate': helpfulness_rate,
            'average_rating': avg_rating,
            'total_patterns': total_patterns,
            'success_rate': success_rate,
            'total_feature_requests': total_requests,
            'common_actions': common_actions,
            'data_path': str(self.db_path)
        }
        
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent feedback entries"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM feedback
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        feedback = []
        for row in c.fetchall():
            feedback.append(dict(row))
            
        conn.close()
        return feedback
        
    def get_failed_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent failed usage patterns"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM usage_patterns
            WHERE success = 0
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        patterns = []
        for row in c.fetchall():
            pattern = dict(row)
            # Parse context JSON
            try:
                pattern['context'] = json.loads(pattern['context'])
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
            patterns.append(pattern)
            
        conn.close()
        return patterns
        
    def export_feedback(self, output_path: Path):
        """Export all feedback to JSON file"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        data = {
            'export_date': datetime.now().isoformat(),
            'feedback': [],
            'usage_patterns': [],
            'feature_requests': []
        }
        
        # Export feedback
        c = conn.cursor()
        c.execute('SELECT * FROM feedback')
        data['feedback'] = [dict(row) for row in c.fetchall()]
        
        # Export usage patterns
        c.execute('SELECT * FROM usage_patterns')
        for row in c.fetchall():
            pattern = dict(row)
            try:
                pattern['context'] = json.loads(pattern['context'])
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
            data['usage_patterns'].append(pattern)
            
        # Export feature requests
        c.execute('SELECT * FROM feature_requests')
        data['feature_requests'] = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)