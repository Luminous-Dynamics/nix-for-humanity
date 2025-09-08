#!/usr/bin/env python3
"""
Feedback Collection System for Luminous Nix
Tracks user feedback, bugs, and improvement suggestions
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class FeedbackCollector:
    """Collects and analyzes user feedback for continuous improvement"""
    
    def __init__(self, db_path: str = "data/feedback.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """Initialize feedback database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query TEXT NOT NULL,
                expected_command TEXT,
                actual_command TEXT,
                was_correct BOOLEAN,
                user_rating INTEGER,
                user_comment TEXT,
                query_hash TEXT,
                session_id TEXT
            )
        ''')
        
        # Bug reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bug_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity TEXT,
                title TEXT,
                description TEXT,
                query TEXT,
                error_message TEXT,
                stack_trace TEXT,
                user_email TEXT,
                status TEXT DEFAULT 'open'
            )
        ''')
        
        # Feature requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                description TEXT,
                use_case TEXT,
                priority INTEGER,
                votes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'proposed'
            )
        ''')
        
        # Metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_name TEXT,
                metric_value REAL,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_feedback(self, query: str, actual_command: str, 
                       was_correct: bool, expected_command: Optional[str] = None,
                       rating: Optional[int] = None, comment: Optional[str] = None,
                       session_id: Optional[str] = None):
        """Record user feedback on a query result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        
        cursor.execute('''
            INSERT INTO feedback 
            (query, expected_command, actual_command, was_correct, 
             user_rating, user_comment, query_hash, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (query, expected_command, actual_command, was_correct,
              rating, comment, query_hash, session_id))
        
        conn.commit()
        conn.close()
        
        # Update model if incorrect
        if not was_correct and expected_command:
            self.learn_from_correction(query, expected_command)
    
    def report_bug(self, title: str, description: str, 
                   severity: str = 'medium', query: Optional[str] = None,
                   error: Optional[str] = None, email: Optional[str] = None):
        """Report a bug"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bug_reports 
            (severity, title, description, query, error_message, user_email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (severity, title, description, query, error, email))
        
        bug_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return bug_id
    
    def request_feature(self, title: str, description: str,
                       use_case: str, priority: int = 3):
        """Submit a feature request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feature_requests 
            (title, description, use_case, priority)
            VALUES (?, ?, ?, ?)
        ''', (title, description, use_case, priority))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    def get_accuracy_metrics(self) -> Dict:
        """Calculate accuracy metrics from feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall accuracy
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM feedback
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        row = cursor.fetchone()
        total, correct = row[0], row[1] or 0
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Common failures
        cursor.execute('''
            SELECT query, COUNT(*) as fail_count
            FROM feedback
            WHERE was_correct = 0
            GROUP BY query_hash
            ORDER BY fail_count DESC
            LIMIT 10
        ''')
        
        common_failures = cursor.fetchall()
        
        # User satisfaction
        cursor.execute('''
            SELECT AVG(user_rating) as avg_rating
            FROM feedback
            WHERE user_rating IS NOT NULL
        ''')
        
        avg_rating = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_queries': total,
            'correct_queries': correct,
            'accuracy_percent': round(accuracy, 1),
            'common_failures': common_failures,
            'avg_user_rating': round(avg_rating, 1),
            'period': 'last_7_days'
        }
    
    def get_open_bugs(self, severity: Optional[str] = None) -> List[Dict]:
        """Get list of open bugs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if severity:
            cursor.execute('''
                SELECT * FROM bug_reports
                WHERE status = 'open' AND severity = ?
                ORDER BY timestamp DESC
            ''', (severity,))
        else:
            cursor.execute('''
                SELECT * FROM bug_reports
                WHERE status = 'open'
                ORDER BY 
                    CASE severity
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END,
                    timestamp DESC
            ''')
        
        bugs = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': bug[0],
                'timestamp': bug[1],
                'severity': bug[2],
                'title': bug[3],
                'description': bug[4],
                'query': bug[5],
                'status': bug[9]
            }
            for bug in bugs
        ]
    
    def get_top_feature_requests(self, limit: int = 10) -> List[Dict]:
        """Get top feature requests by votes and priority"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM feature_requests
            WHERE status = 'proposed'
            ORDER BY votes DESC, priority ASC
            LIMIT ?
        ''', (limit,))
        
        requests = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': req[0],
                'title': req[2],
                'description': req[3],
                'use_case': req[4],
                'priority': req[5],
                'votes': req[6]
            }
            for req in requests
        ]
    
    def record_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Record a performance metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_str = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO metrics (metric_name, metric_value, metadata)
            VALUES (?, ?, ?)
        ''', (name, value, metadata_str))
        
        conn.commit()
        conn.close()
    
    def generate_weekly_report(self) -> str:
        """Generate weekly metrics report"""
        metrics = self.get_accuracy_metrics()
        bugs = self.get_open_bugs()
        features = self.get_top_feature_requests(5)
        
        report = f"""
# 📊 Luminous Nix Weekly Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📈 Accuracy Metrics
- Total Queries: {metrics['total_queries']}
- Correct: {metrics['correct_queries']}
- **Accuracy: {metrics['accuracy_percent']}%**
- User Rating: {metrics['avg_user_rating']}/5

## 🐛 Open Bugs
Total: {len(bugs)}
- Critical: {len([b for b in bugs if b['severity'] == 'critical'])}
- High: {len([b for b in bugs if b['severity'] == 'high'])}
- Medium: {len([b for b in bugs if b['severity'] == 'medium'])}
- Low: {len([b for b in bugs if b['severity'] == 'low'])}

## 💡 Top Feature Requests
"""
        for i, feature in enumerate(features, 1):
            report += f"{i}. {feature['title']} (votes: {feature['votes']})\n"
        
        if metrics['common_failures']:
            report += "\n## ❌ Common Failures\n"
            for query, count in metrics['common_failures'][:5]:
                report += f"- \"{query}\" (failed {count} times)\n"
        
        return report
    
    def learn_from_correction(self, query: str, correct_command: str):
        """Learn from user corrections (integrate with active learning)"""
        # This would integrate with the active learning system
        print(f"Learning: '{query}' -> '{correct_command}'")
        # TODO: Update model weights or pattern database

def create_feedback_cli():
    """Create CLI for feedback collection"""
    collector = FeedbackCollector()
    
    print("🎯 Luminous Nix Feedback System")
    print("=" * 40)
    
    while True:
        print("\n1. Record feedback")
        print("2. Report bug")
        print("3. Request feature")
        print("4. View metrics")
        print("5. Generate report")
        print("6. Exit")
        
        choice = input("\nChoice: ")
        
        if choice == '1':
            query = input("Query: ")
            actual = input("Actual command: ")
            was_correct = input("Was it correct? (y/n): ").lower() == 'y'
            
            if not was_correct:
                expected = input("Expected command: ")
                rating = int(input("Rating (1-5): "))
                comment = input("Comment (optional): ")
                collector.record_feedback(query, actual, was_correct, 
                                        expected, rating, comment)
            else:
                collector.record_feedback(query, actual, was_correct)
            
            print("✅ Feedback recorded!")
            
        elif choice == '2':
            title = input("Bug title: ")
            description = input("Description: ")
            severity = input("Severity (critical/high/medium/low): ")
            query = input("Query that caused bug (optional): ")
            
            bug_id = collector.report_bug(title, description, severity, query)
            print(f"✅ Bug #{bug_id} reported!")
            
        elif choice == '3':
            title = input("Feature title: ")
            description = input("Description: ")
            use_case = input("Use case: ")
            priority = int(input("Priority (1-5): "))
            
            req_id = collector.request_feature(title, description, use_case, priority)
            print(f"✅ Feature request #{req_id} submitted!")
            
        elif choice == '4':
            metrics = collector.get_accuracy_metrics()
            print(f"\n📊 Metrics (last 7 days):")
            print(f"  Accuracy: {metrics['accuracy_percent']}%")
            print(f"  Total queries: {metrics['total_queries']}")
            print(f"  User rating: {metrics['avg_user_rating']}/5")
            
        elif choice == '5':
            report = collector.generate_weekly_report()
            print(report)
            
            # Save to file
            with open("weekly_report.md", 'w') as f:
                f.write(report)
            print("\n✅ Report saved to weekly_report.md")
            
        elif choice == '6':
            break

if __name__ == "__main__":
    create_feedback_cli()