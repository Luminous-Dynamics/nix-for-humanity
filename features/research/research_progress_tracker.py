#!/usr/bin/env python3
"""
from typing import Tuple, Dict, List, Optional
Research Progress Tracker for Nix for Humanity
Tracks implementation of Oracle research innovations
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

class ResearchPhase(Enum):
    """Research implementation phases"""
    NOT_STARTED = "not_started"
    EXPLORING = "exploring"
    PROTOTYPING = "prototyping"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    VALIDATING = "validating"
    COMPLETE = "complete"

class Priority(Enum):
    """Implementation priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ResearchItem:
    """A single research item to implement"""
    id: str
    name: str
    description: str
    category: str  # SKG, Phenomenology, ActivityWatch, etc.
    phase: ResearchPhase = ResearchPhase.NOT_STARTED
    priority: Priority = Priority.MEDIUM
    complexity: int = 3  # 1-5 scale
    impact: int = 3  # 1-5 scale
    dependencies: List[str] = field(default_factory=list)
    milestones: List[str] = field(default_factory=list)
    completed_milestones: List[str] = field(default_factory=list)
    notes: str = ""
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    
    def progress_percentage(self) -> float:
        """Calculate progress based on milestones"""
        if not self.milestones:
            return 100.0 if self.phase == ResearchPhase.COMPLETE else 0.0
        return (len(self.completed_milestones) / len(self.milestones)) * 100
    
    def is_blocked(self, completed_items: List[str]) -> bool:
        """Check if item is blocked by dependencies"""
        return any(dep not in completed_items for dep in self.dependencies)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['phase'] = self.phase.value
        data['priority'] = self.priority.value
        for date_field in ['start_date', 'target_date', 'completion_date']:
            if data[date_field]:
                data[date_field] = data[date_field].isoformat()
        return data

class ResearchProgressTracker:
    """Track progress on research implementation"""
    
    def __init__(self, db_path: str = "research_progress.db"):
        self.db_path = db_path
        self.items: Dict[str, ResearchItem] = {}
        self._init_db()
        self._load_items()
        
        # Initialize with Oracle research items if empty
        if not self.items:
            self._initialize_oracle_items()
    
    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            phase TEXT,
            priority INTEGER,
            complexity INTEGER,
            impact INTEGER,
            dependencies TEXT,
            milestones TEXT,
            completed_milestones TEXT,
            notes TEXT,
            start_date TEXT,
            target_date TEXT,
            completion_date TEXT,
            last_updated TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            item_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (item_id) REFERENCES research_items(id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def _initialize_oracle_items(self):
        """Initialize with research items from Oracle synthesis"""
        
        # Phase 1: Foundation (Week 1-2)
        self.add_item(ResearchItem(
            id="activitywatch_integration",
            name="ActivityWatch Integration",
            description="Integrate privacy-first activity monitoring for behavioral baseline",
            category="ActivityWatch",
            priority=Priority.CRITICAL,
            complexity=2,
            impact=5,
            milestones=[
                "Install and configure ActivityWatch",
                "Create custom NixOS watcher",
                "Integrate with backend API",
                "Validate privacy guarantees"
            ]
        ))
        
        self.add_item(ResearchItem(
            id="phenomenology_basic",
            name="Basic Phenomenological Modeling",
            description="Implement computational qualia for subjective experience",
            category="Phenomenology",
            priority=Priority.CRITICAL,
            complexity=3,
            impact=5,
            milestones=[
                "Implement qualia calculations",
                "Create real-time computation pipeline",
                "Validate against user reports",
                "Generate natural language explanations"
            ]
        ))
        
        self.add_item(ResearchItem(
            id="skg_ontological",
            name="SKG Ontological Layer",
            description="Structured knowledge representation for NixOS domain",
            category="SKG",
            priority=Priority.CRITICAL,
            complexity=3,
            impact=4,
            milestones=[
                "Design SQLite schema",
                "Migrate existing knowledge",
                "Implement graph queries",
                "Performance optimization"
            ]
        ))
        
        # Phase 2: Enhancement (Week 3-6)
        self.add_item(ResearchItem(
            id="skg_episodic",
            name="SKG Episodic Layer",
            description="Rich interaction history with behavioral context",
            category="SKG",
            priority=Priority.HIGH,
            complexity=3,
            impact=4,
            dependencies=["skg_ontological", "activitywatch_integration"],
            milestones=[
                "Link ActivityWatch to interactions",
                "Create temporal patterns table",
                "Implement pattern mining",
                "Build interaction replay"
            ]
        ))
        
        self.add_item(ResearchItem(
            id="phenomenology_advanced",
            name="Advanced Phenomenological Engine",
            description="Multi-dimensional state inference and prediction",
            category="Phenomenology",
            priority=Priority.HIGH,
            complexity=4,
            impact=5,
            dependencies=["phenomenology_basic"],
            milestones=[
                "Implement state space model",
                "Add predictive capabilities",
                "Create intervention system",
                "Validate predictions"
            ]
        ))
        
        self.add_item(ResearchItem(
            id="empathetic_responses",
            name="Empathetic Response Generation",
            description="State-aware responses that acknowledge user experience",
            category="Phenomenology",
            priority=Priority.HIGH,
            complexity=3,
            impact=5,
            dependencies=["phenomenology_advanced"],
            milestones=[
                "Design response variations",
                "Implement A/B testing",
                "Measure satisfaction",
                "Optimize empathy"
            ]
        ))
        
        # Phase 3: Advanced (Week 7-12)
        self.add_item(ResearchItem(
            id="mamba_architecture",
            name="Mamba Architecture Exploration",
            description="Linear-scaling sequence processing for long histories",
            category="Architecture",
            priority=Priority.MEDIUM,
            complexity=5,
            impact=4,
            milestones=[
                "Evaluate Mamba libraries",
                "Benchmark performance",
                "Design integration",
                "Implement prototype"
            ]
        ))
        
        self.add_item(ResearchItem(
            id="metacognitive_layer",
            name="Metacognitive Self-Model",
            description="AI self-awareness and reasoning transparency",
            category="SKG",
            priority=Priority.MEDIUM,
            complexity=4,
            impact=4,
            dependencies=["skg_episodic"],
            milestones=[
                "Design self-model architecture",
                "Implement capability assessment",
                "Add reasoning traces",
                "Create introspection API"
            ]
        ))
        
        self.add_item(ResearchItem(
            id="vlm_prototype",
            name="VLM GUI Automation",
            description="Vision-language models for desktop-wide assistance",
            category="Architecture",
            priority=Priority.LOW,
            complexity=5,
            impact=3,
            milestones=[
                "Research VLM options",
                "Design safety sandbox",
                "Create proof of concept",
                "User study design"
            ]
        ))
        
        self.save_all()
    
    def add_item(self, item: ResearchItem):
        """Add a research item"""
        self.items[item.id] = item
        self._log_event(item.id, "created", f"Added research item: {item.name}")
    
    def update_phase(self, item_id: str, new_phase: ResearchPhase):
        """Update the phase of a research item"""
        if item_id not in self.items:
            return
        
        old_phase = self.items[item_id].phase
        self.items[item_id].phase = new_phase
        
        if new_phase == ResearchPhase.EXPLORING and not self.items[item_id].start_date:
            self.items[item_id].start_date = datetime.now()
        elif new_phase == ResearchPhase.COMPLETE:
            self.items[item_id].completion_date = datetime.now()
        
        self._log_event(item_id, "phase_change", f"{old_phase.value} → {new_phase.value}")
        self.save_item(item_id)
    
    def complete_milestone(self, item_id: str, milestone: str):
        """Mark a milestone as complete"""
        if item_id not in self.items:
            return
        
        item = self.items[item_id]
        if milestone in item.milestones and milestone not in item.completed_milestones:
            item.completed_milestones.append(milestone)
            self._log_event(item_id, "milestone_complete", milestone)
            
            # Auto-update phase based on progress
            progress = item.progress_percentage()
            if progress == 100:
                self.update_phase(item_id, ResearchPhase.COMPLETE)
            elif progress >= 80:
                self.update_phase(item_id, ResearchPhase.VALIDATING)
            elif progress >= 60:
                self.update_phase(item_id, ResearchPhase.TESTING)
            elif progress >= 30:
                self.update_phase(item_id, ResearchPhase.IMPLEMENTING)
            
            self.save_item(item_id)
    
    def get_ready_items(self) -> List[ResearchItem]:
        """Get items ready to start (dependencies met)"""
        completed = [item_id for item_id, item in self.items.items() 
                    if item.phase == ResearchPhase.COMPLETE]
        
        ready = []
        for item in self.items.values():
            if (item.phase == ResearchPhase.NOT_STARTED and 
                not item.is_blocked(completed)):
                ready.append(item)
        
        return sorted(ready, key=lambda x: (x.priority.value, -x.impact))
    
    def get_in_progress(self) -> List[ResearchItem]:
        """Get items currently in progress"""
        in_progress_phases = [
            ResearchPhase.EXPLORING,
            ResearchPhase.PROTOTYPING,
            ResearchPhase.IMPLEMENTING,
            ResearchPhase.TESTING,
            ResearchPhase.VALIDATING
        ]
        
        return [item for item in self.items.values() 
                if item.phase in in_progress_phases]
    
    def get_blocked_items(self) -> List[Tuple[ResearchItem, List[str]]]:
        """Get blocked items and their blocking dependencies"""
        completed = [item_id for item_id, item in self.items.items() 
                    if item.phase == ResearchPhase.COMPLETE]
        
        blocked = []
        for item in self.items.values():
            if item.phase == ResearchPhase.NOT_STARTED and item.is_blocked(completed):
                blocking = [dep for dep in item.dependencies if dep not in completed]
                blocked.append((item, blocking))
        
        return blocked
    
    def generate_progress_report(self) -> Dict:
        """Generate comprehensive progress report"""
        total = len(self.items)
        complete = sum(1 for item in self.items.values() 
                      if item.phase == ResearchPhase.COMPLETE)
        in_progress = len(self.get_in_progress())
        blocked = len(self.get_blocked_items())
        
        # Calculate weighted progress by priority
        weighted_progress = 0
        total_weight = 0
        for item in self.items.values():
            weight = 6 - item.priority.value  # Invert so CRITICAL=5, LOW=2
            total_weight += weight
            weighted_progress += weight * (item.progress_percentage() / 100)
        
        report = {
            'summary': {
                'total_items': total,
                'completed': complete,
                'in_progress': in_progress,
                'blocked': blocked,
                'not_started': total - complete - in_progress - blocked,
                'overall_progress': (complete / total) * 100 if total > 0 else 0,
                'weighted_progress': (weighted_progress / total_weight) * 100 if total_weight > 0 else 0
            },
            'by_category': {},
            'by_phase': {},
            'ready_to_start': [item.name for item in self.get_ready_items()],
            'blockers': [(item.name, blocking) for item, blocking in self.get_blocked_items()]
        }
        
        # Group by category
        for item in self.items.values():
            if item.category not in report['by_category']:
                report['by_category'][item.category] = {
                    'total': 0,
                    'completed': 0,
                    'progress': 0
                }
            report['by_category'][item.category]['total'] += 1
            if item.phase == ResearchPhase.COMPLETE:
                report['by_category'][item.category]['completed'] += 1
            report['by_category'][item.category]['progress'] += item.progress_percentage()
        
        # Calculate category averages
        for category in report['by_category']:
            cat_data = report['by_category'][category]
            cat_data['average_progress'] = cat_data['progress'] / cat_data['total']
        
        # Group by phase
        for phase in ResearchPhase:
            count = sum(1 for item in self.items.values() if item.phase == phase)
            if count > 0:
                report['by_phase'][phase.value] = count
        
        return report
    
    def visualize_progress(self, output_path: str = "research_progress.png"):
        """Create visualization of research progress"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Nix for Humanity Research Progress', fontsize=16)
        
        # 1. Overall Progress Pie Chart
        report = self.generate_progress_report()
        summary = report['summary']
        
        labels = ['Completed', 'In Progress', 'Blocked', 'Not Started']
        sizes = [summary['completed'], summary['in_progress'], 
                summary['blocked'], summary['not_started']]
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#95a5a6']
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Overall Progress')
        
        # 2. Progress by Category
        categories = list(report['by_category'].keys())
        progress = [report['by_category'][cat]['average_progress'] for cat in categories]
        
        ax2.bar(categories, progress, color='#3498db')
        ax2.set_ylim(0, 100)
        ax2.set_ylabel('Average Progress %')
        ax2.set_title('Progress by Category')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Priority vs Impact Matrix
        items = list(self.items.values())
        priorities = [item.priority.value for item in items]
        impacts = [item.impact for item in items]
        progresses = [item.progress_percentage() for item in items]
        
        scatter = ax3.scatter(priorities, impacts, c=progresses, s=200, 
                            cmap='RdYlGn', vmin=0, vmax=100, alpha=0.7)
        
        ax3.set_xlabel('Priority (1=Critical, 4=Low)')
        ax3.set_ylabel('Impact (1-5)')
        ax3.set_title('Priority vs Impact Matrix')
        ax3.set_xticks([1, 2, 3, 4])
        ax3.set_xticklabels(['Critical', 'High', 'Medium', 'Low'])
        ax3.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax3)
        cbar.set_label('Progress %')
        
        # 4. Timeline Gantt Chart (simplified)
        in_progress = self.get_in_progress()
        if in_progress:
            y_pos = range(len(in_progress))
            names = [item.name[:20] + '...' if len(item.name) > 20 else item.name 
                    for item in in_progress]
            progress = [item.progress_percentage() for item in in_progress]
            
            ax4.barh(y_pos, progress, color='#3498db')
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(names)
            ax4.set_xlabel('Progress %')
            ax4.set_title('Current Work in Progress')
            ax4.set_xlim(0, 100)
            
            # Add progress text
            for i, (item, prog) in enumerate(zip(in_progress, progress)):
                ax4.text(prog + 1, i, f'{prog:.0f}%', va='center')
        else:
            ax4.text(0.5, 0.5, 'No items in progress', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Current Work in Progress')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Progress visualization saved to: {output_path}")
    
    def print_summary(self):
        """Print a text summary of progress"""
        report = self.generate_progress_report()
        
        print("\n" + "="*60)
        print("📊 Nix for Humanity Research Progress Summary")
        print("="*60)
        
        summary = report['summary']
        print(f"\n📈 Overall Progress: {summary['overall_progress']:.1f}%")
        print(f"📊 Weighted Progress: {summary['weighted_progress']:.1f}%")
        print(f"\n📋 Status Breakdown:")
        print(f"  ✅ Completed: {summary['completed']}")
        print(f"  🚧 In Progress: {summary['in_progress']}")
        print(f"  🚫 Blocked: {summary['blocked']}")
        print(f"  ⏳ Not Started: {summary['not_started']}")
        
        print(f"\n📂 Progress by Category:")
        for category, data in report['by_category'].items():
            print(f"  {category}: {data['average_progress']:.1f}% ({data['completed']}/{data['total']})")
        
        if report['ready_to_start']:
            print(f"\n🚀 Ready to Start:")
            for item in report['ready_to_start'][:3]:
                print(f"  • {item}")
        
        if report['blockers']:
            print(f"\n⚠️  Blocked Items:")
            for item, deps in report['blockers'][:3]:
                print(f"  • {item} (waiting for: {', '.join(deps)})")
        
        print("\n" + "="*60)
    
    def save_item(self, item_id: str):
        """Save a single item to database"""
        if item_id not in self.items:
            return
        
        item = self.items[item_id]
        data = item.to_dict()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO research_items 
        (id, name, description, category, phase, priority, complexity, impact,
         dependencies, milestones, completed_milestones, notes,
         start_date, target_date, completion_date, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['id'], data['name'], data['description'], data['category'],
            data['phase'], data['priority'], data['complexity'], data['impact'],
            json.dumps(data['dependencies']), json.dumps(data['milestones']),
            json.dumps(data['completed_milestones']), data['notes'],
            data['start_date'], data['target_date'], data['completion_date'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_all(self):
        """Save all items to database"""
        for item_id in self.items:
            self.save_item(item_id)
    
    def _load_items(self):
        """Load items from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM research_items")
        rows = cursor.fetchall()
        
        for row in rows:
            data = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'phase': ResearchPhase(row[4]),
                'priority': Priority(row[5]),
                'complexity': row[6],
                'impact': row[7],
                'dependencies': json.loads(row[8]),
                'milestones': json.loads(row[9]),
                'completed_milestones': json.loads(row[10]),
                'notes': row[11]
            }
            
            # Parse dates
            for i, field in enumerate(['start_date', 'target_date', 'completion_date']):
                if row[12 + i]:
                    data[field] = datetime.fromisoformat(row[12 + i])
                else:
                    data[field] = None
            
            self.items[data['id']] = ResearchItem(**data)
        
        conn.close()
    
    def _log_event(self, item_id: str, event_type: str, details: str):
        """Log an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO progress_log (timestamp, item_id, event_type, details)
        VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), item_id, event_type, details))
        
        conn.commit()
        conn.close()


# Example usage
if __name__ == "__main__":
    tracker = ResearchProgressTracker()
    
    # Print current status
    tracker.print_summary()
    
    # Generate visualization
    tracker.visualize_progress()
    
    # Simulate some progress
    print("\n📝 Simulating research progress...")
    
    # Start ActivityWatch integration
    tracker.update_phase("activitywatch_integration", ResearchPhase.EXPLORING)
    tracker.complete_milestone("activitywatch_integration", "Install and configure ActivityWatch")
    
    # Make progress on phenomenology
    tracker.update_phase("phenomenology_basic", ResearchPhase.PROTOTYPING)
    tracker.complete_milestone("phenomenology_basic", "Implement qualia calculations")
    
    # Print updated status
    print("\n📊 After updates:")
    tracker.print_summary()
    
    # Show ready items
    ready = tracker.get_ready_items()
    if ready:
        print("\n🚀 Items ready to start:")
        for item in ready:
            print(f"  • {item.name} (Priority: {item.priority.name}, Impact: {item.impact}/5)")