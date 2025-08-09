"""
from typing import Dict, List, Optional
Core test implementations for consciousness-first testing.

This module provides deterministic, real implementations to replace
mocks in tests. Each implementation has predictable behavior while
still testing the real interactions between components.
"""

import asyncio
import sqlite3
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path


# Persona test data reflecting real user needs
PERSONA_TEST_DATA = {
    'grandma_rose': {
        'age': 75,
        'tech_level': 'beginner',
        'typical_inputs': [
            "I need that Firefox thing",
            "How do I update my computer?",
            "My internet isn't working",
            "Can you help me install that photo editor?"
        ],
        'max_response_time': 2.0,
        'preferred_style': 'friendly',
        'needs_simple_language': True,
    },
    'maya_adhd': {
        'age': 16,
        'tech_level': 'intermediate',
        'typical_inputs': [
            "firefox now",
            "update",
            "install discord fast",
            "wifi broken fix it"
        ],
        'max_response_time': 1.0,
        'preferred_style': 'minimal',
        'needs_fast_response': True,
    },
    'alex_blind': {
        'age': 28,
        'tech_level': 'advanced',
        'typical_inputs': [
            "install neovim with plugins",
            "configure screen reader settings",
            "search for accessible terminals",
            "update system with verbose output"
        ],
        'max_response_time': 3.0,
        'preferred_style': 'technical',
        'needs_screen_reader': True,
    },
    'dr_sarah': {
        'age': 35,
        'tech_level': 'advanced',
        'typical_inputs': [
            "install firefox-esr for research",
            "batch install: r rstudio jupyter",
            "configure development environment",
            "show system resource usage"
        ],
        'max_response_time': 2.0,
        'preferred_style': 'technical',
        'needs_precision': True,
    },
}


@dataclass
class TestProcess:
    """Simulated process with deterministic behavior."""
    returncode: int
    stdout: bytes
    stderr: bytes
    execution_time: float = 0.1
    memory_usage: int = 0
    
    def wait(self) -> int:
        """Simulate process.wait()"""
        time.sleep(self.execution_time)
        return self.returncode
    
    def poll(self) -> Optional[int]:
        """Simulate process.poll()"""
        return self.returncode
    
    def communicate(self, input=None, timeout=None):
        """Simulate process.communicate()"""
        time.sleep(self.execution_time)
        return self.stdout, self.stderr


class TestExecutionBackend:
    """Test implementation of command execution backend."""
    
    def __init__(self):
        self.commands_executed = []
        self.current_generation = 42
        self.package_db = {
            'firefox': {'version': '120.0', 'size': '75MB'},
            'neovim': {'version': '0.9.4', 'size': '35MB'},
            'vscode': {'version': '1.84', 'size': '120MB'},
            'gimp': {'version': '2.10', 'size': '200MB'},
            'discord': {'version': '0.0.35', 'size': '95MB'},
        }
        self.installed_packages = set()
        
    def execute(self, command: str, args: List[str]) -> TestProcess:
        """Execute command with deterministic results."""
        self.commands_executed.append((command, args))
        
        # Simulate different command behaviors
        if command == 'nix-env' and '-iA' in args:
            package = args[-1].split('.')[-1]
            if package in self.package_db:
                self.installed_packages.add(package)
                return create_successful_process(
                    f"Installing {package}...\nDone!"
                )
            else:
                return create_failed_process(
                    f"error: attribute '{package}' not found"
                )
                
        elif command == 'nixos-rebuild' and 'switch' in args:
            return create_successful_process(
                "Building NixOS configuration...\nActivating...\nDone!"
            )
            
        elif command == 'nix' and 'search' in args:
            query = args[-1]
            matches = [p for p in self.package_db if query in p]
            return create_successful_process(
                '\n'.join(f"* {p} - {self.package_db[p]['version']}" for p in matches)
            )
            
        else:
            return create_successful_process("")
    
    def get_generations(self) -> List[Dict[str, Any]]:
        """Return test generation data."""
        return [
            {
                'generation': self.current_generation,
                'date': '2024-01-15 10:30:00',
                'current': True
            },
            {
                'generation': self.current_generation - 1,
                'date': '2024-01-14 15:45:00',
                'current': False
            }
        ]
    
    def rollback(self, generation: int) -> bool:
        """Simulate rollback."""
        if generation < self.current_generation:
            self.current_generation = generation
            return True
        return False


class TestNLPEngine:
    """Test implementation of NLP processing."""
    
    def __init__(self):
        self.intent_patterns = {
            'install': ['install', 'get', 'need', 'want'],
            'update': ['update', 'upgrade', 'refresh'],
            'search': ['search', 'find', 'look for'],
            'remove': ['remove', 'uninstall', 'delete'],
        }
        self.corrections_made = []
        
    def process(self, text: str, persona: Optional[str] = None) -> Dict[str, Any]:
        """Process natural language with deterministic results."""
        text_lower = text.lower()
        
        # Typo correction
        corrected = self._correct_typos(text_lower)
        if corrected != text_lower:
            self.corrections_made.append((text_lower, corrected))
            text_lower = corrected
        
        # Intent recognition
        intent = None
        confidence = 0.0
        package = None
        
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    intent = intent_name
                    confidence = 0.95
                    break
        
        # Package extraction
        if intent == 'install':
            # Common packages mentioned in text
            packages = ['firefox', 'chrome', 'vscode', 'vim', 'neovim', 'gimp', 'discord']
            for pkg in packages:
                if pkg in text_lower:
                    package = pkg
                    break
        
        # Persona adaptation
        response_style = 'balanced'
        if persona == 'maya_adhd':
            response_style = 'minimal'
        elif persona == 'grandma_rose':
            response_style = 'friendly'
        elif persona in ['alex_blind', 'dr_sarah']:
            response_style = 'technical'
        
        return {
            'intent': intent,
            'confidence': confidence,
            'package': package,
            'entities': {'package': package} if package else {},
            'corrections': self.corrections_made[-1] if self.corrections_made else None,
            'response_style': response_style,
            'processing_time': 0.05 if persona == 'maya_adhd' else 0.1,
        }
    
    def _correct_typos(self, text: str) -> str:
        """Simple typo correction."""
        corrections = {
            'instal': 'install',
            'fierfix': 'firefox',
            'firefx': 'firefox',
            'updaet': 'update',
            'pyhton': 'python',
        }
        
        result = text
        for typo, correct in corrections.items():
            if typo in result:
                result = result.replace(typo, correct)
        
        return result


class TestDatabase:
    """In-memory SQLite database for testing."""
    
    def __init__(self, db_path: str = ':memory:'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_schema()
        
    def _init_schema(self):
        """Initialize test database schema."""
        cursor = self.conn.cursor()
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                user_id TEXT,
                key TEXT,
                value TEXT,
                count INTEGER DEFAULT 1,
                last_used TIMESTAMP,
                confidence REAL DEFAULT 0.5,
                PRIMARY KEY (user_id, key)
            )
        ''')
        
        # Learning data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                input_text TEXT,
                intent TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP,
                feedback TEXT
            )
        ''')
        
        # Persona tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persona_state (
                user_id TEXT PRIMARY KEY,
                detected_persona TEXT,
                skill_level TEXT,
                preferences JSON,
                last_updated TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def record_preference(self, user_id: str, key: str, value: str):
        """Record user preference."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO preferences 
            (user_id, key, value, count, last_used, confidence)
            VALUES (?, ?, ?, 
                    COALESCE((SELECT count + 1 FROM preferences 
                             WHERE user_id = ? AND key = ?), 1),
                    ?, ?)
        ''', (user_id, key, value, user_id, key, 
              datetime.now().isoformat(), 0.7))
        self.conn.commit()
    
    def get_preference(self, user_id: str, key: str) -> Optional[Dict[str, Any]]:
        """Get user preference."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT value, count, last_used, confidence
            FROM preferences
            WHERE user_id = ? AND key = ?
        ''', (user_id, key))
        
        row = cursor.fetchone()
        if row:
            return {
                'value': row[0],
                'count': row[1],
                'last_used': row[2],
                'confidence': row[3]
            }
        return None
    
    def record_learning(self, user_id: str, input_text: str, 
                       intent: str, success: bool, feedback: Optional[str] = None):
        """Record learning interaction."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO learning_data 
            (user_id, input_text, intent, success, timestamp, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, input_text, intent, success, 
              datetime.now().isoformat(), feedback))
        self.conn.commit()
    
    def get_learning_stats(self, user_id: str) -> Dict[str, Any]:
        """Get learning statistics for user."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(success) as successes,
                   COUNT(DISTINCT intent) as unique_intents
            FROM learning_data
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        return {
            'total_interactions': row[0],
            'successful_interactions': row[1] or 0,
            'unique_intents': row[2],
            'success_rate': (row[1] or 0) / row[0] if row[0] > 0 else 0
        }
    
    def close(self):
        """Close database connection."""
        self.conn.close()


class TestLearningEngine:
    """Test implementation of learning system."""
    
    def __init__(self, database: TestDatabase):
        self.db = database
        self.model_version = "0.1.0"
        self.adaptations = {}
        
    def learn_from_interaction(self, user_id: str, interaction: Dict[str, Any]):
        """Learn from user interaction."""
        # Record in database
        self.db.record_learning(
            user_id,
            interaction.get('input', ''),
            interaction.get('intent', ''),
            interaction.get('success', False),
            interaction.get('feedback')
        )
        
        # Update preferences
        if interaction.get('package'):
            self.db.record_preference(
                user_id, 
                'preferred_packages',
                interaction['package']
            )
        
        # Adapt model (simulated)
        if user_id not in self.adaptations:
            self.adaptations[user_id] = {
                'interactions': 0,
                'success_rate': 0.0,
                'preferred_style': 'balanced'
            }
        
        self.adaptations[user_id]['interactions'] += 1
        
    def get_user_model(self, user_id: str) -> Dict[str, Any]:
        """Get user model for personalization."""
        stats = self.db.get_learning_stats(user_id)
        
        # Determine skill level based on interactions
        skill_level = 'beginner'
        if stats['total_interactions'] > 50:
            skill_level = 'intermediate'
        if stats['total_interactions'] > 100 and stats['success_rate'] > 0.8:
            skill_level = 'advanced'
        
        return {
            'user_id': user_id,
            'skill_level': skill_level,
            'stats': stats,
            'adaptations': self.adaptations.get(user_id, {}),
            'model_version': self.model_version
        }


class TestProgressCallback:
    """Test implementation of progress callbacks."""
    
    def __init__(self):
        self.calls = []
        self.completed = False
        
    def __call__(self, stage: str, progress: float, message: str = ""):
        """Record progress callback."""
        self.calls.append({
            'stage': stage,
            'progress': progress,
            'message': message,
            'timestamp': time.time()
        })
        
        if progress >= 1.0:
            self.completed = True
    
    def get_stages(self) -> List[str]:
        """Get unique stages."""
        return list(dict.fromkeys(call['stage'] for call in self.calls))
    
    def get_final_progress(self) -> float:
        """Get final progress value."""
        return self.calls[-1]['progress'] if self.calls else 0.0


class TestBackendAPI:
    """Test implementation of backend API."""
    
    def __init__(self):
        self.nlp = TestNLPEngine()
        self.executor = TestExecutionBackend()
        self.db = TestDatabase()
        self.learning = TestLearningEngine(self.db)
        self.requests = []
        
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process API request with deterministic response."""
        self.requests.append(request)
        
        method = request.get('method', '')
        params = request.get('params', {})
        
        if method == 'process_with_xai':
            # Process with NLP
            nlp_result = self.nlp.process(
                params.get('input', ''),
                params.get('context', {}).get('persona')
            )
            
            # Add XAI explanation
            explanation = self._generate_explanation(nlp_result)
            
            # Execute if it's a valid command
            execution_result = None
            if nlp_result['intent'] and nlp_result['confidence'] > 0.7:
                if nlp_result['intent'] == 'install' and nlp_result['package']:
                    process = self.executor.execute(
                        'nix-env', 
                        ['-iA', f'nixos.{nlp_result["package"]}']
                    )
                    execution_result = {
                        'success': process.returncode == 0,
                        'output': process.stdout.decode()
                    }
            
            # Learn from interaction
            self.learning.learn_from_interaction(
                params.get('context', {}).get('user_id', 'default'),
                {
                    'input': params.get('input'),
                    'intent': nlp_result['intent'],
                    'success': execution_result['success'] if execution_result else False
                }
            )
            
            return {
                'intent': nlp_result['intent'],
                'confidence': nlp_result['confidence'],
                'entities': nlp_result.get('entities', {}),
                'xai_explanation': explanation,
                'execution': execution_result,
                'response_style': nlp_result['response_style'],
                'processing_time_ms': int(nlp_result['processing_time'] * 1000)
            }
        
        else:
            return {'error': f'Unknown method: {method}'}
    
    def _generate_explanation(self, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate XAI explanation."""
        return {
            'why': f"I recognized '{nlp_result['intent']}' intent with {nlp_result['confidence']:.0%} confidence",
            'confidence': nlp_result['confidence'],
            'level': 'simple',
            'reasoning_path': [
                f"Analyzed input text",
                f"Matched pattern for '{nlp_result['intent']}' intent",
                f"Extracted entities: {nlp_result.get('entities', {})}"
            ],
            'alternatives_considered': []
        }


class TestContextManager:
    """Test implementation of conversation context management."""
    
    def __init__(self):
        self.contexts = {}
        self.max_history = 10
        
    def add_context(self, session_id: str, entry: Dict[str, Any]):
        """Add context entry for session."""
        if session_id not in self.contexts:
            self.contexts[session_id] = []
        
        self.contexts[session_id].append({
            'timestamp': time.time(),
            'entry': entry
        })
        
        # Keep only recent history
        if len(self.contexts[session_id]) > self.max_history:
            self.contexts[session_id] = self.contexts[session_id][-self.max_history:]
    
    def get_context(self, session_id: str) -> List[Dict[str, Any]]:
        """Get context for session."""
        return self.contexts.get(session_id, [])
    
    def get_relevant_context(self, session_id: str, query: str) -> Dict[str, Any]:
        """Get context relevant to query."""
        context = self.get_context(session_id)
        
        # Simple relevance: look for package mentions
        likely_package = None
        for entry in reversed(context):
            if 'package' in entry['entry']:
                likely_package = entry['entry']['package']
                break
        
        # Look for recent intents
        recent_intents = [
            entry['entry'].get('intent') 
            for entry in context[-3:] 
            if 'intent' in entry['entry']
        ]
        
        return {
            'likely_package': likely_package,
            'recent_intents': recent_intents,
            'confidence': 0.8 if likely_package else 0.3,
            'session_length': len(context)
        }
    
    def clear_context(self, session_id: str):
        """Clear context for session."""
        if session_id in self.contexts:
            del self.contexts[session_id]


class TestKnowledgeBase:
    """Test implementation of NixOS knowledge base."""
    
    def __init__(self):
        self.db = TestDatabase()
        self._init_knowledge()
        
    def _init_knowledge(self):
        """Initialize knowledge base with test data."""
        cursor = self.db.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nixos_info (
                topic TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                examples TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        # Add test knowledge
        knowledge_entries = [
            {
                'topic': 'packages',
                'title': 'Installing Packages in NixOS',
                'content': 'NixOS uses declarative package management...',
                'examples': json.dumps([
                    'nix-env -iA nixos.firefox',
                    'Add to configuration.nix: environment.systemPackages = [ pkgs.firefox ];'
                ])
            },
            {
                'topic': 'updates',
                'title': 'Updating NixOS',
                'content': 'NixOS can be updated using nixos-rebuild...',
                'examples': json.dumps([
                    'sudo nixos-rebuild switch',
                    'sudo nixos-rebuild switch --upgrade'
                ])
            },
            {
                'topic': 'generations',
                'title': 'NixOS Generations',
                'content': 'NixOS keeps previous system configurations...',
                'examples': json.dumps([
                    'nixos-rebuild list-generations',
                    'nixos-rebuild switch --rollback'
                ])
            }
        ]
        
        for entry in knowledge_entries:
            cursor.execute('''
                INSERT OR REPLACE INTO nixos_info 
                (topic, title, content, examples, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (entry['topic'], entry['title'], entry['content'], 
                  entry['examples'], datetime.now().isoformat()))
        
        self.db.conn.commit()
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge base."""
        cursor = self.db.conn.cursor()
        
        # Simple search in title and content
        cursor.execute('''
            SELECT topic, title, content, examples
            FROM nixos_info
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY 
                CASE 
                    WHEN title LIKE ? THEN 1
                    ELSE 2
                END
            LIMIT 5
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'topic': row[0],
                'title': row[1],
                'content': row[2],
                'examples': json.loads(row[3])
            })
        
        return results
    
    def get_info(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get specific topic information."""
        cursor = self.db.conn.cursor()
        
        cursor.execute('''
            SELECT title, content, examples
            FROM nixos_info
            WHERE topic = ?
        ''', (topic,))
        
        row = cursor.fetchone()
        if row:
            return {
                'topic': topic,
                'title': row[0],
                'content': row[1],
                'examples': json.loads(row[2])
            }
        return None


# Utility functions for creating test objects

def create_test_process(returncode: int, stdout: str, stderr: str = "") -> TestProcess:
    """Create a test process with given output."""
    return TestProcess(
        returncode=returncode,
        stdout=stdout.encode(),
        stderr=stderr.encode()
    )


def create_successful_process(output: str) -> TestProcess:
    """Create a successful test process."""
    return create_test_process(0, output)


def create_failed_process(error: str) -> TestProcess:
    """Create a failed test process."""
    return create_test_process(1, "", error)


def create_test_database() -> TestDatabase:
    """Create a test database instance."""
    return TestDatabase()


def create_test_nlp_engine() -> TestNLPEngine:
    """Create a test NLP engine instance."""
    return TestNLPEngine()


# Test fixtures for different scenarios

def test_fixture(func):
    """Decorator for test fixtures."""
    def wrapper(*args, **kwargs):
        # Setup
        db = TestDatabase()
        nlp = TestNLPEngine()
        executor = TestExecutionBackend()
        
        # Inject dependencies
        kwargs['db'] = db
        kwargs['nlp'] = nlp
        kwargs['executor'] = executor
        
        try:
            return func(*args, **kwargs)
        finally:
            # Cleanup
            db.close()
    
    return wrapper


def async_test_fixture(func):
    """Decorator for async test fixtures."""
    async def wrapper(*args, **kwargs):
        # Setup
        api = TestBackendAPI()
        
        # Inject dependencies
        kwargs['api'] = api
        
        try:
            return await func(*args, **kwargs)
        finally:
            # Cleanup
            api.db.close()
    
    return wrapper


def persona_test(persona_name: str):
    """Decorator for persona-specific tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get persona data
            persona_data = PERSONA_TEST_DATA.get(persona_name, {})
            
            # Inject persona context
            kwargs['persona'] = persona_name
            kwargs['persona_data'] = persona_data
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def performance_test(max_time: float):
    """Decorator for performance tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > max_time:
                raise AssertionError(
                    f"Performance test failed: {duration:.3f}s > {max_time}s"
                )
            
            return result
        
        return wrapper
    return decorator