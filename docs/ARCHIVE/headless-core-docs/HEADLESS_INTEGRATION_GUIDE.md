# 🔌 Headless Core Integration Guide

*How to integrate Nix for Humanity's intelligent core into your application*

## Overview

The Nix for Humanity headless core provides an intelligent natural language interface for NixOS that can be integrated into any application. Whether you're building a web app, mobile app, desktop GUI, or voice assistant, this guide shows you how.

## Architecture

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Web App       │  │  Mobile App     │  │  Voice Assistant│
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┴─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   REST API        │
                    │  (Port 5000)      │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Headless Core    │
                    │  - Intent Engine  │
                    │  - Knowledge Base │
                    │  - Execution Eng. │
                    │  - Learning Sys.  │
                    └───────────────────┘
```

## Integration Methods

### 1. REST API (Recommended)

The REST API provides a simple HTTP interface for all core functionality.

**Start the API server:**
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
python scripts/api/nix_api_server.py
```

**Base URL:** `http://localhost:5000`

#### Key Endpoints

##### Query Processing
```http
POST /api/v1/query
Content-Type: application/json

{
  "query": "How do I install Firefox?",
  "context": {
    "personality": "friendly",
    "execution_mode": "dry_run"
  }
}
```

##### Package Search
```http
GET /api/v1/search?q=python&limit=10
```

##### Submit Feedback
```http
POST /api/v1/feedback
Content-Type: application/json

{
  "session_id": "abc123",
  "helpful": true,
  "rating": 5
}
```

### 2. Python Direct Integration

For Python applications, integrate the core directly:

```python
from scripts.core.headless_engine import HeadlessEngine, Context

# Initialize engine
engine = HeadlessEngine()

# Create context
context = Context(
    personality="friendly",
    execution_mode="dry_run",
    capabilities=["text", "visual"]
)

# Process query
response = engine.process("How do I install Firefox?", context)
print(response.text)
print(response.commands)
```

### 3. WebSocket Real-time Interface

For real-time interactions (requires flask-socketio):

```javascript
const socket = io('http://localhost:5000');

socket.on('connected', (data) => {
    socket.emit('query', {
        query: 'How do I update my system?',
        personality: 'minimal'
    });
});

socket.on('response', (data) => {
    console.log('Response:', data);
});
```

## Client Libraries

### JavaScript/TypeScript

See `scripts/api/examples/javascript_client.js`

```javascript
import NixForHumanityClient from './nix-client';

const client = new NixForHumanityClient();
const response = await client.query('Install Firefox');
console.log(response);
```

### Python

See `scripts/api/examples/python_client.py`

```python
from nix_client import NixForHumanityClient

with NixForHumanityClient() as client:
    response = client.query("Install Firefox")
    print(response['response']['text'])
```

### React Example

```jsx
import { useState } from 'react';
import NixForHumanityClient from './nix-client';

function NixAssistant() {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState(null);
    const client = new NixForHumanityClient();
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        const result = await client.query(query);
        setResponse(result.response);
    };
    
    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about NixOS..."
                />
                <button type="submit">Ask</button>
            </form>
            
            {response && (
                <div>
                    <p>{response.text}</p>
                    {response.commands.map((cmd, i) => (
                        <code key={i}>{cmd}</code>
                    ))}
                </div>
            )}
        </div>
    );
}
```

## Response Format

All API responses follow this structure:

```json
{
  "status": "success",
  "session_id": "abc123",
  "response": {
    "text": "I'll help you install Firefox! Here are your options...",
    "intent": {
      "action": "install_package",
      "package": "firefox",
      "confidence": 0.9
    },
    "commands": [
      "nix-env -iA nixos.firefox",
      "nix-shell -p firefox"
    ],
    "visual": {
      "type": "options",
      "choices": [...]
    },
    "feedback_request": {
      "type": "simple",
      "prompt": "Was this helpful?"
    }
  },
  "timestamp": "2025-01-29T12:00:00Z"
}
```

## Context Options

### Personalities
- `minimal` - Just the facts
- `friendly` - Warm and helpful (default)
- `encouraging` - Supportive for beginners
- `technical` - Detailed explanations
- `symbiotic` - Co-evolutionary, admits uncertainty

### Execution Modes
- `dry_run` - Show what would be done (default)
- `safe` - Execute safe commands only
- `full` - Execute all commands
- `learning` - Step-by-step with explanations

### Capabilities
- `text` - Text responses (always enabled)
- `visual` - Visual representations for GUIs
- `voice` - Voice-optimized responses
- `realtime` - Real-time streaming updates

## Authentication & Security

Currently, the API is designed for local use. For production:

1. **Add API Keys**
```python
headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}
```

2. **Enable HTTPS**
```bash
export API_CERT=/path/to/cert.pem
export API_KEY=/path/to/key.pem
```

3. **Configure CORS**
```python
# In nix_api_server.py
CORS(app, origins=['https://yourapp.com'])
```

## Rate Limiting

Default limits:
- Query endpoint: 30 requests/minute
- Search endpoint: 20 requests/minute
- Feedback endpoint: 10 requests/minute
- Overall: 200 requests/day

## Error Handling

```javascript
try {
    const response = await client.query('Install Firefox');
} catch (error) {
    if (error.status === 429) {
        // Rate limited
        console.log('Please slow down');
    } else if (error.status === 400) {
        // Bad request
        console.log('Invalid query');
    }
}
```

## Advanced Features

### Session Management

Sessions persist context between queries:

```python
# First query
response1 = client.query("I want to install a browser")

# Follow-up uses context
response2 = client.query("Firefox please")
# Engine understands this refers to installation
```

### Feedback Collection

Improve responses over time:

```python
# After getting a response
client.submit_feedback(
    query="How do I install Firefox?",
    response=response['text'],
    helpful=True,
    rating=5,
    improved_response="Even better explanation..."
)
```

### Plugin Development

Extend functionality with plugins:

```python
# my_plugin.py
class MyPlugin:
    def can_handle(self, intent):
        return intent['action'] == 'my_custom_action'
    
    def handle(self, intent, context):
        return {
            'success': True,
            'response': 'Custom response',
            'commands': ['custom-command']
        }
```

## Testing Your Integration

### Unit Tests
```python
def test_nix_query():
    client = NixForHumanityClient('http://localhost:5000')
    response = client.query('Install Firefox')
    
    assert response['status'] == 'success'
    assert 'firefox' in response['response']['text'].lower()
    assert len(response['response']['commands']) > 0
```

### Integration Tests
```bash
# Start test server
python scripts/api/nix_api_server.py &
SERVER_PID=$!

# Run tests
pytest tests/integration/test_api.py

# Cleanup
kill $SERVER_PID
```

## Performance Considerations

1. **Connection Pooling** - Reuse HTTP connections
2. **Response Caching** - Cache common queries
3. **Batch Requests** - Group multiple queries
4. **Async Operations** - Use async clients for better concurrency

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ ./scripts/
EXPOSE 5000

CMD ["python", "scripts/api/nix_api_server.py"]
```

### systemd Service
```ini
[Unit]
Description=Nix for Humanity API
After=network.target

[Service]
Type=simple
User=nix-api
WorkingDirectory=/srv/nix-for-humanity
ExecStart=/usr/bin/python3 scripts/api/nix_api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

Use the `/api/v1/stats` endpoint:

```bash
# Check health
curl http://localhost:5000/api/v1/health

# Get statistics
curl http://localhost:5000/api/v1/stats
```

## Common Integration Patterns

### 1. CLI Tool
```python
#!/usr/bin/env python3
import sys
from nix_client import NixForHumanityClient

client = NixForHumanityClient()
response = client.query(' '.join(sys.argv[1:]))
print(response['response']['text'])
```

### 2. Slack Bot
```python
@app.message("nix: ")
def handle_nix_query(message, say):
    query = message['text'].replace('nix: ', '')
    response = nix_client.query(query)
    say(response['response']['text'])
```

### 3. Voice Assistant
```python
def on_voice_command(transcript):
    response = nix_client.query(transcript, capabilities=['voice'])
    speak(response['response']['voice'] or response['response']['text'])
```

## Support

- GitHub Issues: [Report problems](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)
- Documentation: [Full docs](https://github.com/Luminous-Dynamics/nix-for-humanity/docs)
- Examples: See `scripts/api/examples/` directory

---

*Building intelligent NixOS interfaces, one integration at a time!*