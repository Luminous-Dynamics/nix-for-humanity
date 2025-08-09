#!/usr/bin/env python3
"""
from typing import Optional
Feedback Collector for Nix for Humanity
Phase 0 implementation of the Symbiotic Intelligence architecture
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

class FeedbackCollector:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.data_dir = self.base_dir / "data" / "feedback"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "feedback.db"
        self.init_db()
        
    def init_db(self):
        """Initialize feedback database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create feedback table
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                helpful BOOLEAN,
                better_response TEXT,
                interaction_time REAL,
                user_state TEXT,
                metadata TEXT
            )
        ''')
        
        # Create preferences table for RLHF
        c.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                context TEXT NOT NULL,
                chosen TEXT NOT NULL,
                rejected TEXT NOT NULL,
                reason TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def collect_implicit_feedback(self, query: str, response: str, 
                                 interaction_time: float, user_action: str) -> Dict:
        """Collect implicit feedback from user behavior"""
        
        # Implicit signals
        signals = {
            'quick_accept': interaction_time < 2.0,  # Fast acceptance
            'thoughtful_accept': 2.0 <= interaction_time < 10.0,
            'hesitation': interaction_time >= 10.0,
            'immediate_retry': user_action == 'retry',
            'copy_action': user_action == 'copy',
            'execution': user_action == 'execute'
        }
        
        # Infer helpfulness from signals
        helpful = signals['copy_action'] or signals['execution'] or signals['quick_accept']
        
        # Store feedback
        feedback_data = {
            'query': query,
            'response': response,
            'helpful': helpful,
            'interaction_time': interaction_time,
            'timestamp': datetime.now().isoformat(),
            'signals': signals
        }
        
        self._save_feedback(feedback_data)
        
        return feedback_data
        
    def collect_explicit_feedback(self, query: str, response: str, 
                                helpful: bool, better_response: Optional[str] = None) -> Dict:
        """Collect explicit user feedback"""
        
        feedback_data = {
            'query': query,
            'response': response,
            'helpful': helpful,
            'better_response': better_response,
            'timestamp': datetime.now().isoformat()
        }
        
        # If user provided better response, create preference pair
        if better_response:
            self._save_preference(query, chosen=better_response, rejected=response)
            
        self._save_feedback(feedback_data)
        
        return feedback_data
        
    def _save_feedback(self, feedback: Dict):
        """Save feedback to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO feedback 
            (timestamp, query, response, helpful, better_response, interaction_time, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback['timestamp'],
            feedback['query'],
            feedback['response'],
            feedback.get('helpful'),
            feedback.get('better_response'),
            feedback.get('interaction_time'),
            json.dumps(feedback.get('signals', {}))
        ))
        
        conn.commit()
        conn.close()
        
    def _save_preference(self, context: str, chosen: str, rejected: str, reason: str = None):
        """Save preference pair for RLHF training"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO preferences
            (timestamp, context, chosen, rejected, reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            context,
            chosen,
            rejected,
            reason
        ))
        
        conn.commit()
        conn.close()
        
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Overall stats
        c.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM feedback WHERE helpful = 1')
        helpful_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM preferences')
        preference_pairs = c.fetchone()[0]
        
        # Recent feedback
        c.execute('''
            SELECT query, response, helpful, timestamp 
            FROM feedback 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''')
        recent_feedback = c.fetchall()
        
        conn.close()
        
        return {
            'total_feedback': total_feedback,
            'helpful_percentage': (helpful_count / total_feedback * 100) if total_feedback > 0 else 0,
            'preference_pairs': preference_pairs,
            'recent_feedback': recent_feedback
        }
        
    def export_for_training(self, output_path: Optional[Path] = None) -> Path:
        """Export feedback data for DPO training"""
        if not output_path:
            output_path = self.data_dir / f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Export preference pairs
        c.execute('''
            SELECT context, chosen, rejected 
            FROM preferences
        ''')
        
        with open(output_path, 'w') as f:
            for context, chosen, rejected in c.fetchall():
                training_example = {
                    'prompt': context,
                    'chosen': chosen,
                    'rejected': rejected
                }
                f.write(json.dumps(training_example) + '\n')
                
        conn.close()
        
        return output_path


def interactive_feedback_session():
    """Interactive feedback collection for testing"""
    collector = FeedbackCollector()
    
    print("🔄 Nix for Humanity Feedback Collector")
    print("=" * 50)
    
    # Simulate an interaction
    query = input("\n💬 Enter your question: ")
    
    # This would come from the actual system
    response = "I'll help you install firefox! Here are your options:\n\n1. **Declarative** - Add to configuration.nix\n2. **Imperative** - nix-env -iA nixos.firefox"
    
    print(f"\n🤖 Response:\n{response}")
    
    # Collect feedback
    helpful = input("\n✅ Was this helpful? (y/n): ").lower().strip() == 'y'
    
    better_response = None
    if not helpful:
        better = input("💭 What would have been a better response? (or press Enter to skip): ").strip()
        if better:
            better_response = better
            
    # Save feedback
    feedback = collector.collect_explicit_feedback(query, response, helpful, better_response)
    
    print(f"\n📊 Feedback saved: {feedback['timestamp']}")
    
    # Show stats
    stats = collector.get_feedback_stats()
    print(f"\n📈 Feedback Statistics:")
    print(f"  Total feedback: {stats['total_feedback']}")
    print(f"  Helpful: {stats['helpful_percentage']:.1f}%")
    print(f"  Training pairs: {stats['preference_pairs']}")


if __name__ == "__main__":
    interactive_feedback_session()