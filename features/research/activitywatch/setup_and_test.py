#!/usr/bin/env python3
"""
from typing import Dict, List
ActivityWatch Setup and Testing Script
Tests the ActivityWatch API and explores integration possibilities
"""

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

try:
    from aw_client import ActivityWatchClient
    ACTIVITYWATCH_AVAILABLE = True
except ImportError:
    ACTIVITYWATCH_AVAILABLE = False
    print("ActivityWatch client not installed. Install with: pip install aw-client")

class ActivityWatchExplorer:
    """Explore ActivityWatch capabilities for Nix for Humanity integration"""
    
    def __init__(self):
        if not ACTIVITYWATCH_AVAILABLE:
            raise ImportError("ActivityWatch client library not available")
            
        self.client = ActivityWatchClient("nix-humanity-explorer")
        
    def test_connection(self) -> bool:
        """Test if ActivityWatch server is running"""
        try:
            info = self.client.get_info()
            print("✅ ActivityWatch server info:")
            print(json.dumps(info, indent=2))
            return True
        except Exception as e:
            print(f"❌ Cannot connect to ActivityWatch: {e}")
            print("Make sure ActivityWatch is running (aw-qt or aw-server)")
            return False
    
    def list_buckets(self) -> List[str]:
        """List all available buckets"""
        try:
            buckets = self.client.get_buckets()
            print("\n📊 Available buckets:")
            bucket_ids = []
            for bucket_id, bucket_info in buckets.items():
                print(f"  - {bucket_id}")
                print(f"    Type: {bucket_info.get('type', 'unknown')}")
                print(f"    Client: {bucket_info.get('client', 'unknown')}")
                print(f"    Hostname: {bucket_info.get('hostname', 'unknown')}")
                bucket_ids.append(bucket_id)
            return bucket_ids
        except Exception as e:
            print(f"❌ Error listing buckets: {e}")
            return []
    
    def get_recent_events(self, bucket_id: str, limit: int = 10) -> List[Dict]:
        """Get recent events from a specific bucket"""
        try:
            events = self.client.get_events(bucket_id, limit=limit)
            print(f"\n📝 Recent events from {bucket_id} (limit={limit}):")
            
            for i, event in enumerate(events):
                print(f"\nEvent {i+1}:")
                print(f"  Timestamp: {event['timestamp']}")
                print(f"  Duration: {event.get('duration', 0)} seconds")
                print(f"  Data: {json.dumps(event['data'], indent=4)}")
                
            return events
        except Exception as e:
            print(f"❌ Error getting events from {bucket_id}: {e}")
            return []
    
    def analyze_window_activity(self, hours: int = 1) -> Dict[str, Any]:
        """Analyze window activity patterns"""
        window_bucket = None
        
        # Find window watcher bucket
        buckets = self.client.get_buckets()
        for bucket_id in buckets:
            if "window" in bucket_id:
                window_bucket = bucket_id
                break
        
        if not window_bucket:
            print("❌ No window watcher bucket found")
            return {}
        
        # Get events from the last N hours
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        try:
            events = self.client.get_events(
                window_bucket,
                start=start_time,
                end=end_time
            )
            
            # Analyze patterns
            app_usage = {}
            total_duration = 0
            
            for event in events:
                app = event['data'].get('app', 'unknown')
                duration = event.get('duration', 0)
                
                if app not in app_usage:
                    app_usage[app] = {
                        'count': 0,
                        'total_duration': 0,
                        'titles': set()
                    }
                
                app_usage[app]['count'] += 1
                app_usage[app]['total_duration'] += duration
                app_usage[app]['titles'].add(event['data'].get('title', ''))
                total_duration += duration
            
            # Convert sets to lists for JSON serialization
            for app in app_usage:
                app_usage[app]['titles'] = list(app_usage[app]['titles'])
            
            analysis = {
                'time_period': f'{hours} hours',
                'total_events': len(events),
                'total_duration_seconds': total_duration,
                'app_usage': app_usage,
                'most_used_app': max(app_usage.items(), 
                                    key=lambda x: x[1]['total_duration'])[0] if app_usage else None
            }
            
            print(f"\n📊 Window activity analysis (last {hours} hours):")
            print(json.dumps(analysis, indent=2))
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing window activity: {e}")
            return {}
    
    def detect_user_states(self, events: List[Dict]) -> Dict[str, float]:
        """
        Detect user states from activity patterns
        This is a simplified example - real implementation would be more sophisticated
        """
        if not events:
            return {}
        
        # Simple heuristics for state detection
        rapid_switches = 0
        long_focus_periods = 0
        total_events = len(events)
        
        for i in range(1, len(events)):
            duration = events[i-1].get('duration', 0)
            
            # Rapid switching (< 30 seconds on each window)
            if duration < 30:
                rapid_switches += 1
            
            # Long focus (> 10 minutes on same window)
            if duration > 600:
                long_focus_periods += 1
        
        # Calculate state probabilities
        states = {
            'likely_frustrated': min(rapid_switches / max(total_events, 1), 1.0),
            'in_flow_state': min(long_focus_periods / max(total_events, 1), 1.0),
            'multitasking': min((rapid_switches / max(total_events, 1)) * 0.5, 1.0)
        }
        
        print("\n🧠 Detected user states:")
        for state, probability in states.items():
            print(f"  {state}: {probability:.2%}")
        
        return states
    
    def create_test_bucket(self) -> bool:
        """Create a test bucket for Nix for Humanity"""
        bucket_id = "aw-watcher-nix-humanity-test"
        
        try:
            # Create bucket
            self.client.create_bucket(
                bucket_id,
                event_type="nix-command",
                queued=True
            )
            print(f"✅ Created test bucket: {bucket_id}")
            
            # Insert test events
            test_events = [
                {
                    "timestamp": datetime.now(timezone.utc),
                    "duration": 0,
                    "data": {
                        "command": "nix-env -iA nixpkgs.firefox",
                        "category": "package_install",
                        "success": True
                    }
                },
                {
                    "timestamp": datetime.now(timezone.utc) - timedelta(minutes=5),
                    "duration": 0,
                    "data": {
                        "command": "nix-env -qa firefox",
                        "category": "package_search",
                        "success": True
                    }
                }
            ]
            
            for event in test_events:
                self.client.insert_event(bucket_id, event)
            
            print(f"✅ Inserted {len(test_events)} test events")
            return True
            
        except Exception as e:
            print(f"❌ Error creating test bucket: {e}")
            return False

def main():
    """Run ActivityWatch exploration"""
    print("🔍 ActivityWatch Integration Explorer for Nix for Humanity\n")
    
    if not ACTIVITYWATCH_AVAILABLE:
        print("Please install aw-client: pip install aw-client")
        return
    
    explorer = ActivityWatchExplorer()
    
    # Test connection
    if not explorer.test_connection():
        return
    
    # Explore available data
    print("\n" + "="*60 + "\n")
    bucket_ids = explorer.list_buckets()
    
    # Look at window activity
    if any("window" in bid for bid in bucket_ids):
        print("\n" + "="*60 + "\n")
        window_bucket = next(bid for bid in bucket_ids if "window" in bid)
        events = explorer.get_recent_events(window_bucket, limit=20)
        
        if events:
            explorer.detect_user_states(events)
    
    # Analyze patterns
    print("\n" + "="*60 + "\n")
    explorer.analyze_window_activity(hours=1)
    
    # Create test bucket
    print("\n" + "="*60 + "\n")
    explorer.create_test_bucket()
    
    print("\n✅ ActivityWatch exploration complete!")
    print("\nNext steps:")
    print("1. Implement custom NixOS command watcher")
    print("2. Integrate with phenomenological state detection")
    print("3. Store relevant events in SKG episodic layer")

if __name__ == "__main__":
    main()