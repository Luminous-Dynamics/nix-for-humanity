# 🐍 Nix for Humanity Python SDK

*Python client library for the Nix for Humanity API*

---

💡 **Quick Context**: Official Python SDK for integrating Nix for Humanity into Python applications  
📍 **You are here**: Reference → Python SDK  
🔗 **Related**: [API Reference](./02-API-REFERENCE.md) | [JavaScript SDK](./04-JAVASCRIPT-SDK.md) | [Examples](../06-TUTORIALS/API_EXAMPLES.md)  
⏱️ **Read time**: 10 minutes  
📊 **Mastery Level**: 🌿 Intermediate - requires Python knowledge

---

## Installation

```bash
pip install nix-for-humanity
```

Or install from source:
```bash
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
pip install -e .
```

## Quick Start

```python
from nix_humanity import NixClient

# Create client
client = NixClient(base_url="http://localhost:5000")

# Simple query
response = client.query("How do I install Firefox?")
print(response.text)

# Execute the suggested command
if response.commands:
    client.execute(response.commands[0])
```

## Client Configuration

### Basic Configuration
```python
from nix_humanity import NixClient, Personality, ExecutionMode

client = NixClient(
    base_url="http://localhost:5000",
    api_key="your-api-key",  # Optional, for future auth
    timeout=30,              # Request timeout in seconds
    retry_count=3,           # Number of retries on failure
    personality=Personality.FRIENDLY,
    execution_mode=ExecutionMode.DRY_RUN
)
```

### Environment Variables
```python
# The client will automatically use these if set
export NIX_HUMANITY_API_URL=http://localhost:5000
export NIX_HUMANITY_API_KEY=your-api-key
export NIX_HUMANITY_TIMEOUT=30
```

## Core Methods

### Query Processing

```python
# Simple query
response = client.query("install docker")

# Query with context
response = client.query(
    "install docker",
    personality=Personality.TECHNICAL,
    execution_mode=ExecutionMode.SAFE,
    collect_feedback=False
)

# Access response details
print(f"Response: {response.text}")
print(f"Confidence: {response.confidence}")
print(f"Intent: {response.intent}")

# Iterate through commands
for cmd in response.commands:
    print(f"Command: {cmd.command}")
    print(f"Description: {cmd.description}")
    print(f"Safe: {cmd.safe}")
```

### Package Search

```python
# Search for packages
results = client.search("python", limit=10)

for package in results:
    print(f"{package.name} ({package.version})")
    print(f"  {package.description}")
```

### Session Management

```python
# Client automatically manages sessions
print(f"Session ID: {client.session_id}")

# Get session info
session = client.get_session()
print(f"Interactions: {session.interactions}")
print(f"Created: {session.created}")

# Use a specific session
client = NixClient(session_id="existing-session-id")
```

### Feedback Collection

```python
# Submit feedback on a response
response = client.query("install vim")

client.submit_feedback(
    query="install vim",
    response=response.text,
    helpful=True,
    rating=5,
    improved_response="Also mention the vim-full package"
)
```

## Advanced Usage

### Async Support

```python
import asyncio
from nix_humanity import AsyncNixClient

async def main():
    async with AsyncNixClient() as client:
        # Concurrent queries
        tasks = [
            client.query("install firefox"),
            client.query("update system"),
            client.query("search python packages")
        ]
        
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            print(response.text)

asyncio.run(main())
```

### Batch Operations

```python
# Batch multiple queries
queries = [
    "install firefox",
    "install vscode", 
    "install docker"
]

responses = client.batch_query(queries)

for query, response in zip(queries, responses):
    print(f"{query}: {response.text}")
```

### Custom Personalities

```python
from nix_humanity import Personality

# Use built-in personalities
client.set_personality(Personality.MINIMAL)      # Just the facts
client.set_personality(Personality.FRIENDLY)    # Warm and helpful
client.set_personality(Personality.ENCOURAGING) # Educational
client.set_personality(Personality.TECHNICAL)   # Expert mode
client.set_personality(Personality.SYMBIOTIC)   # Learning together

# Or use custom personality
client.query("install neovim", personality="custom_personality")
```

### Execution Modes

```python
from nix_humanity import ExecutionMode

# Dry run - just show what would happen
response = client.query(
    "update system",
    execution_mode=ExecutionMode.DRY_RUN
)

# Safe mode - only safe operations
response = client.query(
    "install package",
    execution_mode=ExecutionMode.SAFE
)

# Full mode - all operations (use with caution)
response = client.query(
    "modify configuration",
    execution_mode=ExecutionMode.FULL
)

# Learning mode - help improve the system
response = client.query(
    "complex task",
    execution_mode=ExecutionMode.LEARNING
)
```

### Error Handling

```python
from nix_humanity import NixError, RateLimitError, APIError

try:
    response = client.query("install firefox")
except RateLimitError as e:
    print(f"Rate limit exceeded. Reset at: {e.reset_time}")
    time.sleep(e.retry_after)
except APIError as e:
    print(f"API error: {e.message}")
except NixError as e:
    print(f"General error: {e}")
```

### WebSocket Support

```python
from nix_humanity import NixWebSocketClient

# Real-time interaction
ws_client = NixWebSocketClient("ws://localhost:5000")

@ws_client.on("response")
def handle_response(data):
    print(f"Received: {data['text']}")

@ws_client.on("error")
def handle_error(data):
    print(f"Error: {data['message']}")

# Connect and send query
ws_client.connect()
ws_client.query("install firefox")

# Keep connection alive
ws_client.wait()
```

## Complete Examples

### Interactive CLI Tool

```python
#!/usr/bin/env python3
from nix_humanity import NixClient, Personality
import readline  # For command history

def main():
    client = NixClient(personality=Personality.FRIENDLY)
    
    print("Nix for Humanity Interactive Shell")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            query = input("nix> ").strip()
            
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query:
                continue
            
            response = client.query(query)
            print(response.text)
            
            # Show commands if available
            if response.commands:
                print("\nSuggested commands:")
                for i, cmd in enumerate(response.commands):
                    print(f"  {i+1}. {cmd.command}")
                
                # Ask if user wants to execute
                choice = input("\nExecute command? (1-{}, n): ".format(
                    len(response.commands)
                ))
                
                if choice.isdigit() and 1 <= int(choice) <= len(response.commands):
                    cmd = response.commands[int(choice) - 1]
                    print(f"\nExecuting: {cmd.command}")
                    # In real app, would execute here
            
        except KeyboardInterrupt:
            print("\nInterrupted")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
```

### Automation Script

```python
#!/usr/bin/env python3
from nix_humanity import NixClient, ExecutionMode
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_packages(packages):
    """Install multiple packages using Nix for Humanity"""
    client = NixClient(
        personality=Personality.MINIMAL,
        execution_mode=ExecutionMode.SAFE
    )
    
    results = []
    
    for package in packages:
        logger.info(f"Installing {package}...")
        
        try:
            response = client.query(f"install {package}")
            
            if response.commands:
                # In production, would execute the command
                results.append({
                    "package": package,
                    "status": "success",
                    "command": response.commands[0].command
                })
                logger.info(f"✓ {package} installed successfully")
            else:
                results.append({
                    "package": package,
                    "status": "no_command",
                    "message": response.text
                })
                logger.warning(f"✗ No command found for {package}")
                
        except Exception as e:
            results.append({
                "package": package,
                "status": "error",
                "error": str(e)
            })
            logger.error(f"✗ Failed to install {package}: {e}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: install_packages.py package1 package2 ...")
        sys.exit(1)
    
    packages = sys.argv[1:]
    results = install_packages(packages)
    
    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    print(f"\nInstalled {success}/{len(packages)} packages successfully")
```

### Learning Assistant

```python
from nix_humanity import NixClient, ExecutionMode
import json
from datetime import datetime

class NixLearningAssistant:
    """Assistant that learns from interactions"""
    
    def __init__(self, history_file="nix_history.json"):
        self.client = NixClient(
            personality=Personality.SYMBIOTIC,
            execution_mode=ExecutionMode.LEARNING
        )
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self):
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def learn(self, query):
        """Process query and learn from the interaction"""
        response = self.client.query(query)
        
        # Record interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response.text,
            "intent": response.intent,
            "confidence": response.confidence,
            "commands": [cmd.to_dict() for cmd in response.commands]
        }
        
        self.history.append(interaction)
        self.save_history()
        
        # Submit feedback if confidence is low
        if response.confidence < 0.8:
            print("I'm not very confident about this response.")
            helpful = input("Was it helpful? (y/n): ").lower() == 'y'
            
            if not helpful:
                better = input("How would you improve it? ")
                self.client.submit_feedback(
                    query=query,
                    response=response.text,
                    helpful=False,
                    improved_response=better
                )
        
        return response
    
    def suggest_similar(self, query):
        """Suggest similar past queries"""
        # Simple keyword matching - real implementation would use embeddings
        keywords = set(query.lower().split())
        similar = []
        
        for interaction in self.history:
            hist_keywords = set(interaction["query"].lower().split())
            if keywords & hist_keywords:  # Intersection
                similar.append(interaction)
        
        return similar[:5]  # Top 5

# Usage
assistant = NixLearningAssistant()

# Learn from interaction
response = assistant.learn("install machine learning tools")

# Find similar past queries
similar = assistant.suggest_similar("install python ML libraries")
for s in similar:
    print(f"Similar: {s['query']} (confidence: {s['confidence']})")
```

## Testing

```python
import unittest
from unittest.mock import Mock, patch
from nix_humanity import NixClient

class TestNixClient(unittest.TestCase):
    
    @patch('requests.post')
    def test_query(self, mock_post):
        # Mock response
        mock_post.return_value.json.return_value = {
            "status": "success",
            "session_id": "test-session",
            "response": {
                "text": "Installing Firefox...",
                "commands": [{
                    "command": "nix-env -iA nixpkgs.firefox",
                    "description": "Install Firefox",
                    "safe": True
                }]
            }
        }
        
        client = NixClient()
        response = client.query("install firefox")
        
        self.assertEqual(response.text, "Installing Firefox...")
        self.assertEqual(len(response.commands), 1)
        self.assertEqual(response.commands[0].command, "nix-env -iA nixpkgs.firefox")
```

## Best Practices

1. **Session Management**: Let the client handle sessions automatically
2. **Error Handling**: Always wrap API calls in try-except blocks
3. **Rate Limiting**: Implement exponential backoff on rate limit errors
4. **Personality Selection**: Choose appropriate personality for your use case
5. **Execution Modes**: Start with dry_run, move to safe, use full sparingly
6. **Feedback**: Submit feedback to help improve the system
7. **Caching**: Cache search results and common queries
8. **Async**: Use async client for concurrent operations

---

*Sacred Humility Context: This Python SDK documentation represents our vision for a comprehensive client library. While the API endpoints are functional, the SDK itself is under development and may not include all features described. The examples demonstrate intended usage patterns that will be fully implemented as the project evolves.*

**Status**: In Development  
**Version**: 0.8.0  
**License**: MIT