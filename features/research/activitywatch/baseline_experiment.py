#!/usr/bin/env python3
"""
from typing import List, Dict, Tuple
ActivityWatch Baseline Experiment Runner
Establishes behavioral patterns for phenomenological state inference
"""

import json
import time
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import numpy as np

# Note: aw-client will be installed when ActivityWatch is available
try:
    from aw_client import ActivityWatchClient
    ACTIVITYWATCH_AVAILABLE = True
except ImportError:
    ACTIVITYWATCH_AVAILABLE = False
    print("ActivityWatch not yet available. This script will work once installation completes.")

class BaselineExperiment:
    """Run baseline experiments to understand user behavior patterns"""
    
    def __init__(self, experiment_name: str = "nix-humanity-baseline"):
        self.experiment_name = experiment_name
        self.db_path = f"{experiment_name}_results.db"
        self.patterns = {
            'flow_indicators': [],
            'frustration_indicators': [],
            'learning_patterns': [],
            'break_patterns': [],
            'error_recovery': []
        }
        self._init_db()
        
        if ACTIVITYWATCH_AVAILABLE:
            self.client = ActivityWatchClient(experiment_name)
    
    def _init_db(self):
        """Initialize results database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS behavioral_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            pattern_data JSON NOT NULL,
            confidence REAL,
            evidence JSON
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiment_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            total_events INTEGER,
            patterns_detected INTEGER,
            notes TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_baseline(self, hours: int = 24) -> Dict[str, Any]:
        """Collect baseline behavioral data"""
        if not ACTIVITYWATCH_AVAILABLE:
            return {"error": "ActivityWatch not available"}
        
        print(f"📊 Collecting {hours} hours of baseline data...")
        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        # Find relevant buckets
        buckets = self.client.get_buckets()
        window_bucket = None
        afk_bucket = None
        
        for bucket_id in buckets:
            if "window" in bucket_id:
                window_bucket = bucket_id
            elif "afk" in bucket_id:
                afk_bucket = bucket_id
        
        if not window_bucket:
            return {"error": "No window watcher bucket found"}
        
        # Collect window events
        print("Fetching window events...")
        window_events = self.client.get_events(
            window_bucket,
            start=start_time,
            end=end_time
        )
        
        # Collect AFK events if available
        afk_events = []
        if afk_bucket:
            print("Fetching AFK events...")
            afk_events = self.client.get_events(
                afk_bucket,
                start=start_time,
                end=end_time
            )
        
        # Analyze patterns
        analysis = {
            'window_events': len(window_events),
            'afk_events': len(afk_events),
            'patterns': self._analyze_patterns(window_events, afk_events),
            'statistics': self._calculate_statistics(window_events, afk_events)
        }
        
        return analysis
    
    def _analyze_patterns(self, window_events: List[Dict], afk_events: List[Dict]) -> Dict[str, Any]:
        """Analyze behavioral patterns from events"""
        patterns = {
            'flow_states': [],
            'frustration_signals': [],
            'context_switches': [],
            'focus_sessions': [],
            'break_patterns': []
        }
        
        # Detect flow states (long uninterrupted focus)
        flow_threshold = 600  # 10 minutes
        current_app = None
        focus_start = None
        
        for event in window_events:
            app = event['data'].get('app', 'unknown')
            title = event['data'].get('title', '')
            duration = event.get('duration', 0)
            
            # Track focus sessions
            if duration > flow_threshold:
                patterns['flow_states'].append({
                    'app': app,
                    'duration': duration,
                    'title_keywords': self._extract_keywords(title),
                    'timestamp': event['timestamp']
                })
            
            # Detect rapid switching (frustration indicator)
            if current_app and app != current_app and focus_start:
                switch_time = (datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')) - 
                              focus_start).total_seconds()
                if switch_time < 30:  # Rapid switch
                    patterns['frustration_signals'].append({
                        'from_app': current_app,
                        'to_app': app,
                        'switch_time': switch_time,
                        'timestamp': event['timestamp']
                    })
            
            current_app = app
            focus_start = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        
        # Analyze context switching patterns
        app_sequence = [e['data'].get('app', 'unknown') for e in window_events]
        switch_rate = self._calculate_switch_rate(app_sequence)
        patterns['context_switches'] = {
            'hourly_rate': switch_rate,
            'common_transitions': self._find_common_transitions(app_sequence)
        }
        
        # Analyze break patterns from AFK events
        if afk_events:
            for event in afk_events:
                if event['data'].get('status', '') == 'afk' and event.get('duration', 0) > 60:
                    patterns['break_patterns'].append({
                        'duration': event['duration'],
                        'timestamp': event['timestamp']
                    })
        
        return patterns
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract relevant keywords from window title"""
        # Keywords that might indicate NixOS/development activity
        keywords = []
        nix_terms = ['nix', 'nixos', 'configuration.nix', 'flake', 'shell.nix', 
                     'home-manager', 'nix-env', 'nixpkgs']
        dev_terms = ['vim', 'neovim', 'code', 'terminal', 'git', 'python', 'error', 'debug']
        
        title_lower = title.lower()
        for term in nix_terms + dev_terms:
            if term in title_lower:
                keywords.append(term)
        
        return keywords
    
    def _calculate_switch_rate(self, app_sequence: List[str]) -> float:
        """Calculate context switch rate per hour"""
        if len(app_sequence) < 2:
            return 0.0
        
        switches = sum(1 for i in range(1, len(app_sequence)) if app_sequence[i] != app_sequence[i-1])
        # Assuming events cover the full time period uniformly
        return switches  # This is simplified; real implementation would use timestamps
    
    def _find_common_transitions(self, app_sequence: List[str]) -> List[Tuple[str, str, int]]:
        """Find common app transitions"""
        transitions = []
        for i in range(1, len(app_sequence)):
            if app_sequence[i] != app_sequence[i-1]:
                transitions.append((app_sequence[i-1], app_sequence[i]))
        
        transition_counts = Counter(transitions)
        return [(t[0], t[1], count) for t, count in transition_counts.most_common(5)]
    
    def _calculate_statistics(self, window_events: List[Dict], afk_events: List[Dict]) -> Dict[str, Any]:
        """Calculate statistical summaries"""
        stats = {
            'total_active_time': 0,
            'total_afk_time': 0,
            'app_usage': defaultdict(float),
            'focus_statistics': {},
            'productivity_score': 0.0
        }
        
        # Calculate app usage
        for event in window_events:
            app = event['data'].get('app', 'unknown')
            duration = event.get('duration', 0)
            stats['app_usage'][app] += duration
            stats['total_active_time'] += duration
        
        # Calculate AFK time
        for event in afk_events:
            if event['data'].get('status', '') == 'afk':
                stats['total_afk_time'] += event.get('duration', 0)
        
        # Focus statistics
        durations = [e.get('duration', 0) for e in window_events if e.get('duration', 0) > 0]
        if durations:
            stats['focus_statistics'] = {
                'mean_duration': statistics.mean(durations),
                'median_duration': statistics.median(durations),
                'std_duration': statistics.stdev(durations) if len(durations) > 1 else 0,
                'long_focus_sessions': sum(1 for d in durations if d > 600)  # >10 min
            }
        
        # Simple productivity score (time in productive apps / total time)
        productive_apps = ['terminal', 'firefox', 'neovim', 'vim', 'code']
        productive_time = sum(duration for app, duration in stats['app_usage'].items() 
                             if any(prod in app.lower() for prod in productive_apps))
        
        if stats['total_active_time'] > 0:
            stats['productivity_score'] = productive_time / stats['total_active_time']
        
        return stats
    
    def detect_user_states(self, patterns: Dict[str, Any]) -> Dict[str, float]:
        """Detect user states from patterns"""
        states = {
            'in_flow': 0.0,
            'frustrated': 0.0,
            'learning': 0.0,
            'exploring': 0.0,
            'focused': 0.0
        }
        
        # Flow state detection
        flow_states = patterns.get('flow_states', [])
        if flow_states:
            avg_flow_duration = statistics.mean([f['duration'] for f in flow_states])
            states['in_flow'] = min(avg_flow_duration / 1800, 1.0)  # Normalize to 30 min
        
        # Frustration detection
        frustration_signals = patterns.get('frustration_signals', [])
        if frustration_signals:
            recent_frustrations = [f for f in frustration_signals 
                                 if (datetime.now(timezone.utc) - 
                                     datetime.fromisoformat(f['timestamp'].replace('Z', '+00:00'))).total_seconds() < 300]
            states['frustrated'] = min(len(recent_frustrations) / 5, 1.0)  # 5 rapid switches = max frustration
        
        # Learning state (lots of documentation + terminal)
        app_usage = patterns.get('statistics', {}).get('app_usage', {})
        doc_time = sum(time for app, time in app_usage.items() if 'firefox' in app.lower() or 'doc' in app.lower())
        term_time = sum(time for app, time in app_usage.items() if 'term' in app.lower())
        total_time = sum(app_usage.values())
        
        if total_time > 0:
            learning_ratio = (doc_time + term_time) / total_time
            states['learning'] = min(learning_ratio * 1.5, 1.0)
        
        return states
    
    def run_experiment(self, duration_hours: int = 24) -> Dict[str, Any]:
        """Run the complete baseline experiment"""
        session_id = f"session_{int(time.time())}"
        
        print(f"🧪 Starting baseline experiment: {session_id}")
        print(f"Duration: {duration_hours} hours")
        
        # Record experiment start
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO experiment_sessions (session_id, start_time, notes)
        VALUES (?, ?, ?)
        """, (session_id, datetime.now().isoformat(), f"Baseline collection for {duration_hours} hours"))
        conn.commit()
        conn.close()
        
        # Collect baseline data
        baseline_data = self.collect_baseline(duration_hours)
        
        if "error" in baseline_data:
            print(f"❌ Error: {baseline_data['error']}")
            return baseline_data
        
        # Detect user states
        patterns = baseline_data.get('patterns', {})
        user_states = self.detect_user_states({'flow_states': patterns.get('flow_states', []),
                                              'frustration_signals': patterns.get('frustration_signals', []),
                                              'statistics': baseline_data.get('statistics', {})})
        
        # Save patterns to database
        self._save_patterns(patterns, session_id)
        
        # Generate report
        report = {
            'session_id': session_id,
            'duration_hours': duration_hours,
            'total_events': baseline_data.get('window_events', 0),
            'patterns_detected': len(patterns.get('flow_states', [])) + len(patterns.get('frustration_signals', [])),
            'user_states': user_states,
            'statistics': baseline_data.get('statistics', {}),
            'key_findings': self._generate_key_findings(patterns, baseline_data.get('statistics', {}))
        }
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _save_patterns(self, patterns: Dict[str, Any], session_id: str):
        """Save detected patterns to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern_type, pattern_list in patterns.items():
            if isinstance(pattern_list, list):
                for pattern in pattern_list:
                    cursor.execute("""
                    INSERT INTO behavioral_patterns (timestamp, pattern_type, pattern_data, confidence)
                    VALUES (?, ?, ?, ?)
                    """, (datetime.now().isoformat(), pattern_type, json.dumps(pattern), 0.8))
            elif isinstance(pattern_list, dict):
                cursor.execute("""
                INSERT INTO behavioral_patterns (timestamp, pattern_type, pattern_data, confidence)
                VALUES (?, ?, ?, ?)
                """, (datetime.now().isoformat(), pattern_type, json.dumps(pattern_list), 0.8))
        
        # Update session
        cursor.execute("""
        UPDATE experiment_sessions 
        SET end_time = ?, total_events = ?, patterns_detected = ?
        WHERE session_id = ?
        """, (datetime.now().isoformat(), 
              sum(len(p) if isinstance(p, list) else 1 for p in patterns.values()),
              len(patterns), 
              session_id))
        
        conn.commit()
        conn.close()
    
    def _generate_key_findings(self, patterns: Dict[str, Any], statistics: Dict[str, Any]) -> List[str]:
        """Generate key findings from the analysis"""
        findings = []
        
        # Flow state findings
        flow_states = patterns.get('flow_states', [])
        if flow_states:
            avg_flow = statistics.get('focus_statistics', {}).get('mean_duration', 0) / 60
            findings.append(f"Average focus session: {avg_flow:.1f} minutes")
            findings.append(f"Long flow states detected: {len(flow_states)}")
        
        # Frustration findings
        frustration_signals = patterns.get('frustration_signals', [])
        if frustration_signals:
            findings.append(f"Rapid context switches (frustration): {len(frustration_signals)}")
        
        # Productivity findings
        productivity = statistics.get('productivity_score', 0) * 100
        findings.append(f"Time in productive apps: {productivity:.1f}%")
        
        # Break patterns
        breaks = patterns.get('break_patterns', [])
        if breaks:
            avg_break = statistics.mean([b['duration'] for b in breaks]) / 60
            findings.append(f"Average break duration: {avg_break:.1f} minutes")
        
        return findings
    
    def _print_summary(self, report: Dict[str, Any]):
        """Print a formatted summary of the experiment"""
        print("\n" + "="*60)
        print(f"📊 Baseline Experiment Summary")
        print("="*60)
        
        print(f"\nSession ID: {report['session_id']}")
        print(f"Duration: {report['duration_hours']} hours")
        print(f"Total events analyzed: {report['total_events']}")
        print(f"Patterns detected: {report['patterns_detected']}")
        
        print("\n🧠 Detected User States:")
        for state, value in report['user_states'].items():
            bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
            print(f"  {state:12} [{bar}] {value:.2%}")
        
        print("\n📈 Key Findings:")
        for finding in report['key_findings']:
            print(f"  • {finding}")
        
        print("\n💾 Results saved to: " + self.db_path)
        print("="*60)


# Example usage
if __name__ == "__main__":
    print("🔬 ActivityWatch Baseline Experiment Runner")
    print("=========================================")
    
    if not ACTIVITYWATCH_AVAILABLE:
        print("\n⏳ Waiting for ActivityWatch installation to complete...")
        print("This script will work once the flake download finishes.")
        print("\nIn the meantime, this script is ready to run experiments!")
    else:
        # Run a short test experiment
        experiment = BaselineExperiment("test_baseline")
        
        # You can run different duration experiments
        # report = experiment.run_experiment(duration_hours=1)  # 1 hour test
        # report = experiment.run_experiment(duration_hours=24)  # 24 hour baseline
        
        print("\n✅ Experiment runner ready!")
        print("Once ActivityWatch is running, use:")
        print("  python baseline_experiment.py")
        print("\nMake sure to start ActivityWatch first:")
        print("  aw-qt &  # For GUI")
        print("  # or")
        print("  aw-server &  # For headless")