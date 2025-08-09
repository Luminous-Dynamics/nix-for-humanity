#!/usr/bin/env python3
"""
from typing import Tuple, List, Optional
Preference Learner for Nix for Humanity
Phase 1 implementation of local preference learning
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserPreferences:
    """Multidimensional preference model"""
    verbosity: float = 0.5      # 0=minimal, 1=detailed
    technicality: float = 0.5   # 0=simple, 1=expert
    personality: float = 0.5    # 0=formal, 1=friendly
    proactivity: float = 0.5    # 0=reactive, 1=proactive
    learning_pace: float = 0.5  # 0=slow, 1=fast
    error_tolerance: float = 0.5 # 0=strict, 1=forgiving
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPreferences':
        return cls(**data)
    
    def update_dimension(self, dimension: str, delta: float, learning_rate: float = 0.1):
        """Update a preference dimension with learning rate"""
        if hasattr(self, dimension):
            current = getattr(self, dimension)
            # Clip value between 0 and 1
            new_value = max(0.0, min(1.0, current + (delta * learning_rate)))
            setattr(self, dimension, new_value)
            logger.debug(f"Updated {dimension}: {current:.3f} -> {new_value:.3f}")

class PreferenceLearner:
    def __init__(self, db_path: Optional[Path] = None):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.data_dir = self.base_dir / "data" / "preferences"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Use existing feedback database
        self.feedback_db = db_path or self.base_dir / "data" / "feedback" / "feedback.db"
        self.prefs_db = self.data_dir / "preferences.db"
        
        self.preferences = UserPreferences()
        self.session_count = 0
        
        self.init_preferences_db()
        self.load_preferences()
        
    def init_preferences_db(self):
        """Initialize preferences database"""
        conn = sqlite3.connect(self.prefs_db)
        c = conn.cursor()
        
        # User preferences table
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                preferences TEXT NOT NULL,
                session_count INTEGER,
                last_updated TEXT
            )
        ''')
        
        # Preference history for tracking evolution
        c.execute('''
            CREATE TABLE IF NOT EXISTS preference_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                dimension TEXT NOT NULL,
                old_value REAL,
                new_value REAL,
                trigger_event TEXT,
                confidence REAL
            )
        ''')
        
        # Command patterns table
        c.execute('''
            CREATE TABLE IF NOT EXISTS command_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                success_rate REAL,
                avg_interaction_time REAL,
                last_used TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_preferences(self):
        """Load existing preferences or create new ones"""
        conn = sqlite3.connect(self.prefs_db)
        c = conn.cursor()
        
        c.execute('''
            SELECT preferences, session_count 
            FROM user_preferences 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        result = c.fetchone()
        if result:
            prefs_json, self.session_count = result
            self.preferences = UserPreferences.from_dict(json.loads(prefs_json))
            logger.info(f"Loaded existing preferences (session #{self.session_count + 1})")
        else:
            logger.info("Initializing new preference profile")
            self.save_preferences()
            
        conn.close()
        
    def save_preferences(self):
        """Save current preferences to database"""
        conn = sqlite3.connect(self.prefs_db)
        c = conn.cursor()
        
        self.session_count += 1
        
        c.execute('''
            INSERT INTO user_preferences 
            (timestamp, preferences, session_count, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            json.dumps(self.preferences.to_dict()),
            self.session_count,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
    def analyze_feedback(self) -> Dict:
        """Analyze feedback from the feedback database"""
        if not self.feedback_db.exists():
            logger.warning("No feedback database found")
            return {}
            
        conn = sqlite3.connect(self.feedback_db)
        c = conn.cursor()
        
        # Analyze helpful vs not helpful
        c.execute('''
            SELECT 
                COUNT(CASE WHEN helpful = 1 THEN 1 END) as helpful_count,
                COUNT(CASE WHEN helpful = 0 THEN 1 END) as not_helpful_count,
                AVG(interaction_time) as avg_interaction_time
            FROM feedback
        ''')
        
        helpful, not_helpful, avg_time = c.fetchone()
        
        # Analyze response preferences
        c.execute('''
            SELECT response, helpful, interaction_time
            FROM feedback
            ORDER BY timestamp DESC
            LIMIT 20
        ''')
        
        recent_feedback = c.fetchall()
        
        # Analyze preference pairs
        c.execute('''
            SELECT context, chosen, rejected
            FROM preferences
        ''')
        
        preference_pairs = c.fetchall()
        
        conn.close()
        
        analysis = {
            'helpful_rate': helpful / (helpful + not_helpful) if (helpful + not_helpful) > 0 else 0.5,
            'avg_interaction_time': avg_time or 5.0,
            'recent_feedback': recent_feedback,
            'preference_pairs': preference_pairs
        }
        
        return analysis
        
    def infer_preferences_from_feedback(self, analysis: Dict):
        """Infer preference updates from feedback analysis"""
        updates = []
        
        # Infer from helpfulness rate
        helpful_rate = analysis['helpful_rate']
        if helpful_rate < 0.3:
            # Low satisfaction - adjust approach
            updates.append(('verbosity', 0.1))  # More detail
            updates.append(('personality', 0.1))  # More friendly
            updates.append(('learning_pace', -0.1))  # Slower pace
        elif helpful_rate > 0.8:
            # High satisfaction - can be more efficient
            updates.append(('learning_pace', 0.1))  # Faster pace
            
        # Infer from interaction time
        avg_time = analysis['avg_interaction_time']
        if avg_time < 2.0:
            # Quick acceptance - user is confident
            updates.append(('technicality', 0.1))  # More technical
            updates.append(('verbosity', -0.1))  # Less verbose
        elif avg_time > 10.0:
            # Long consideration - user needs clarity
            updates.append(('verbosity', 0.1))  # More detail
            updates.append(('technicality', -0.1))  # Simpler
            
        # Analyze preference pairs for style
        for context, chosen, rejected in analysis['preference_pairs']:
            # Simple heuristics for now
            if len(chosen) < len(rejected) * 0.7:
                updates.append(('verbosity', -0.1))  # Prefers concise
            if 'step' in chosen.lower() and 'step' not in rejected.lower():
                updates.append(('learning_pace', -0.1))  # Wants steps
            if '!' in chosen and '!' not in rejected:
                updates.append(('personality', 0.1))  # Likes enthusiasm
                
        return updates
        
    def update_preferences(self, updates: List[Tuple[str, float]]):
        """Apply preference updates"""
        for dimension, delta in updates:
            old_value = getattr(self.preferences, dimension, 0.5)
            self.preferences.update_dimension(dimension, delta)
            new_value = getattr(self.preferences, dimension)
            
            # Log to history
            self._log_preference_change(dimension, old_value, new_value, "feedback_analysis")
            
    def _log_preference_change(self, dimension: str, old_value: float, 
                              new_value: float, trigger: str):
        """Log preference changes for transparency"""
        conn = sqlite3.connect(self.prefs_db)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO preference_history
            (timestamp, dimension, old_value, new_value, trigger_event, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            dimension,
            old_value,
            new_value,
            trigger,
            abs(new_value - old_value)  # Simple confidence metric
        ))
        
        conn.commit()
        conn.close()
        
    def get_adaptive_response_params(self) -> Dict:
        """Get parameters for adaptive response generation"""
        return {
            'style': self._determine_style(),
            'complexity': self._determine_complexity(),
            'elements': self._determine_elements()
        }
        
    def _determine_style(self) -> str:
        """Determine response style based on preferences"""
        if self.preferences.personality < 0.3:
            return 'minimal'
        elif self.preferences.personality < 0.5:
            return 'technical'
        elif self.preferences.personality < 0.7:
            return 'friendly'
        else:
            return 'encouraging'
            
    def _determine_complexity(self) -> str:
        """Determine response complexity"""
        tech_verb = (self.preferences.technicality + self.preferences.verbosity) / 2
        if tech_verb < 0.3:
            return 'simple'
        elif tech_verb < 0.7:
            return 'moderate'
        else:
            return 'detailed'
            
    def _determine_elements(self) -> List[str]:
        """Determine which elements to include"""
        elements = []
        
        if self.preferences.verbosity > 0.5:
            elements.append('examples')
        if self.preferences.technicality > 0.6:
            elements.append('technical_details')
        if self.preferences.learning_pace < 0.4:
            elements.append('step_by_step')
        if self.preferences.personality > 0.6:
            elements.append('encouragement')
        if self.preferences.proactivity > 0.6:
            elements.append('suggestions')
            
        return elements
        
    def get_preference_summary(self) -> Dict:
        """Get human-readable preference summary"""
        return {
            'profile': self._determine_style(),
            'learning_style': 'step-by-step' if self.preferences.learning_pace < 0.5 else 'quick',
            'technical_level': 'beginner' if self.preferences.technicality < 0.3 
                              else 'advanced' if self.preferences.technicality > 0.7 
                              else 'intermediate',
            'preferences': self.preferences.to_dict(),
            'session_count': self.session_count,
            'last_updated': datetime.now().isoformat()
        }
        
    def run_learning_cycle(self):
        """Run a complete learning cycle"""
        logger.info("🧠 Running preference learning cycle...")
        
        # Analyze feedback
        analysis = self.analyze_feedback()
        
        if not analysis:
            logger.warning("No feedback data available")
            return
            
        # Infer preference updates
        updates = self.infer_preferences_from_feedback(analysis)
        
        if updates:
            logger.info(f"Applying {len(updates)} preference updates")
            self.update_preferences(updates)
            self.save_preferences()
            
        # Show summary
        summary = self.get_preference_summary()
        logger.info(f"\n📊 Preference Profile:")
        logger.info(f"  Style: {summary['profile']}")
        logger.info(f"  Learning: {summary['learning_style']}")
        logger.info(f"  Technical: {summary['technical_level']}")
        logger.info(f"  Sessions: {summary['session_count']}")
        
        return summary


def main():
    """Test the preference learner"""
    learner = PreferenceLearner()
    
    print("🧠 Nix for Humanity - Preference Learning System")
    print("=" * 50)
    
    # Run learning cycle
    summary = learner.run_learning_cycle()
    
    # Show detailed preferences
    print("\n📈 Detailed Preferences:")
    for dim, value in summary['preferences'].items():
        bar = '█' * int(value * 20) + '░' * (20 - int(value * 20))
        print(f"  {dim:15} [{bar}] {value:.2f}")
        
    # Get adaptive parameters
    params = learner.get_adaptive_response_params()
    print(f"\n🎯 Adaptive Response Parameters:")
    print(f"  Style: {params['style']}")
    print(f"  Complexity: {params['complexity']}")
    print(f"  Elements: {', '.join(params['elements'])}")
    
    # Show how to integrate
    print("\n💡 Integration Example:")
    print("  from preference_learner import PreferenceLearner")
    print("  learner = PreferenceLearner()")
    print("  params = learner.get_adaptive_response_params()")
    print("  # Use params to customize response generation")


if __name__ == "__main__":
    main()