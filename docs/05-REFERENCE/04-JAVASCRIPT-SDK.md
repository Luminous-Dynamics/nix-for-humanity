# 🌐 Nix for Humanity JavaScript SDK

*JavaScript/TypeScript client library for the Nix for Humanity API*

---

💡 **Quick Context**: Official JavaScript SDK for integrating Nix for Humanity into web and Node.js applications  
📍 **You are here**: Reference → JavaScript SDK  
🔗 **Related**: [API Reference](./02-API-REFERENCE.md) | [Python SDK](./03-PYTHON-SDK.md) | [Examples](../06-TUTORIALS/API_EXAMPLES.md)  
⏱️ **Read time**: 10 minutes  
📊 **Mastery Level**: 🌿 Intermediate - requires JavaScript/TypeScript knowledge

---

## Installation

### npm
```bash
npm install nix-for-humanity
```

### yarn
```bash
yarn add nix-for-humanity
```

### CDN (Browser)
```html
<script src="https://unpkg.com/nix-for-humanity@latest/dist/nix-humanity.min.js"></script>
```

## Quick Start

### Node.js / ES Modules
```javascript
import { NixClient } from 'nix-for-humanity';

// Create client
const client = new NixClient({
  baseUrl: 'http://localhost:5000'
});

// Simple query
const response = await client.query('How do I install Firefox?');
console.log(response.text);

// Execute suggested command
if (response.commands.length > 0) {
  await client.execute(response.commands[0]);
}
```

### CommonJS
```javascript
const { NixClient } = require('nix-for-humanity');

const client = new NixClient({
  baseUrl: 'http://localhost:5000'
});

// Use with promises
client.query('install nodejs')
  .then(response => {
    console.log(response.text);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Browser
```html
<script>
  const client = new NixHumanity.NixClient({
    baseUrl: 'http://localhost:5000'
  });
  
  async function askNix() {
    const response = await client.query('install firefox');
    document.getElementById('result').innerText = response.text;
  }
</script>
```

## TypeScript Support

Full TypeScript support with type definitions included:

```typescript
import { 
  NixClient, 
  QueryResponse, 
  Personality, 
  ExecutionMode,
  SearchResult,
  NixError 
} from 'nix-for-humanity';

const client = new NixClient({
  baseUrl: 'http://localhost:5000',
  timeout: 30000,
  personality: Personality.Friendly,
  executionMode: ExecutionMode.DryRun
});

// Type-safe responses
const response: QueryResponse = await client.query('install vim');
const packages: SearchResult[] = await client.search('python');
```

## Client Configuration

### Configuration Options
```typescript
interface NixClientConfig {
  baseUrl?: string;           // API base URL
  apiKey?: string;           // Optional API key
  timeout?: number;          // Request timeout in ms
  retryCount?: number;       // Number of retries
  personality?: Personality;  // Default personality
  executionMode?: ExecutionMode; // Default execution mode
  onError?: (error: NixError) => void; // Error handler
}

const client = new NixClient({
  baseUrl: 'http://localhost:5000',
  apiKey: process.env.NIX_API_KEY,
  timeout: 30000,
  retryCount: 3,
  personality: Personality.Friendly,
  executionMode: ExecutionMode.Safe,
  onError: (error) => {
    console.error('Nix error:', error);
  }
});
```

### Environment Variables
```javascript
// Automatically uses these if set
process.env.NIX_HUMANITY_API_URL = 'http://localhost:5000';
process.env.NIX_HUMANITY_API_KEY = 'your-api-key';
process.env.NIX_HUMANITY_TIMEOUT = '30000';
```

## Core Methods

### Query Processing

```javascript
// Simple query
const response = await client.query('install docker');

// Query with options
const response = await client.query('install docker', {
  personality: Personality.Technical,
  executionMode: ExecutionMode.Safe,
  collectFeedback: false
});

// Access response details
console.log(`Response: ${response.text}`);
console.log(`Confidence: ${response.confidence}`);
console.log(`Intent:`, response.intent);

// Iterate through commands
response.commands.forEach(cmd => {
  console.log(`Command: ${cmd.command}`);
  console.log(`Description: ${cmd.description}`);
  console.log(`Safe: ${cmd.safe}`);
});
```

### Package Search

```javascript
// Search for packages
const results = await client.search('python', { limit: 10 });

results.forEach(pkg => {
  console.log(`${pkg.name} (${pkg.version})`);
  console.log(`  ${pkg.description}`);
});
```

### Session Management

```javascript
// Client automatically manages sessions
console.log(`Session ID: ${client.sessionId}`);

// Get session info
const session = await client.getSession();
console.log(`Interactions: ${session.interactions}`);
console.log(`Created: ${session.created}`);

// Use existing session
const client = new NixClient({
  sessionId: 'existing-session-id'
});
```

### Feedback Collection

```javascript
// Submit feedback on a response
const response = await client.query('install vim');

await client.submitFeedback({
  query: 'install vim',
  response: response.text,
  helpful: true,
  rating: 5,
  improvedResponse: 'Also mention the vim-full package'
});
```

## Advanced Usage

### Promise-based API

```javascript
// All methods return promises
client.query('install firefox')
  .then(response => {
    console.log(response.text);
    return client.submitFeedback({
      query: 'install firefox',
      response: response.text,
      helpful: true
    });
  })
  .then(() => {
    console.log('Feedback submitted');
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Async/Await with Error Handling

```javascript
try {
  const response = await client.query('install nodejs');
  console.log(response.text);
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(`Rate limit exceeded. Retry after: ${error.retryAfter}s`);
  } else if (error instanceof APIError) {
    console.log(`API error: ${error.message}`);
  } else {
    console.log(`Unknown error: ${error}`);
  }
}
```

### Batch Operations

```javascript
// Batch multiple queries
const queries = [
  'install firefox',
  'install vscode',
  'install docker'
];

const responses = await client.batchQuery(queries);

responses.forEach((response, index) => {
  console.log(`${queries[index]}: ${response.text}`);
});
```

### Event-based API

```javascript
// Listen for events
client.on('query', (data) => {
  console.log('Query sent:', data.query);
});

client.on('response', (data) => {
  console.log('Response received:', data.text);
});

client.on('error', (error) => {
  console.error('Error occurred:', error);
});

client.on('rateLimit', (data) => {
  console.warn(`Rate limit: ${data.remaining}/${data.limit}`);
});
```

### WebSocket Real-time Connection

```javascript
import { NixWebSocketClient } from 'nix-for-humanity';

const wsClient = new NixWebSocketClient('ws://localhost:5000');

// Set up event handlers
wsClient.on('connect', () => {
  console.log('Connected to Nix for Humanity');
});

wsClient.on('response', (data) => {
  console.log('Received:', data.text);
});

wsClient.on('error', (error) => {
  console.error('WebSocket error:', error);
});

// Connect and send query
await wsClient.connect();
await wsClient.query('install firefox');

// Keep connection alive
wsClient.startHeartbeat();

// Clean up when done
wsClient.disconnect();
```

### Interceptors

```javascript
// Request interceptor
client.interceptors.request.use((config) => {
  console.log('Sending request:', config);
  // Add custom headers, modify request, etc.
  config.headers['X-Custom-Header'] = 'value';
  return config;
});

// Response interceptor
client.interceptors.response.use(
  (response) => {
    console.log('Received response:', response);
    // Transform response, add caching, etc.
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    // Handle errors globally
    return Promise.reject(error);
  }
);
```

## React Integration

### React Hook
```typescript
import { useNixQuery } from 'nix-for-humanity/react';

function PackageInstaller() {
  const { query, loading, error, response } = useNixQuery();
  
  const handleInstall = async (packageName: string) => {
    const result = await query(`install ${packageName}`);
    if (result.commands.length > 0) {
      console.log('Execute:', result.commands[0].command);
    }
  };
  
  return (
    <div>
      <button 
        onClick={() => handleInstall('firefox')}
        disabled={loading}
      >
        Install Firefox
      </button>
      
      {loading && <p>Processing...</p>}
      {error && <p>Error: {error.message}</p>}
      {response && <pre>{response.text}</pre>}
    </div>
  );
}
```

### React Context Provider
```typescript
import { NixProvider, useNix } from 'nix-for-humanity/react';

// Wrap your app
function App() {
  return (
    <NixProvider config={{ baseUrl: 'http://localhost:5000' }}>
      <YourComponents />
    </NixProvider>
  );
}

// Use in components
function MyComponent() {
  const { client, sessionId } = useNix();
  
  const handleQuery = async () => {
    const response = await client.query('update system');
    console.log(response.text);
  };
  
  return <button onClick={handleQuery}>Update System</button>;
}
```

## Vue.js Integration

```typescript
// Vue 3 Composition API
import { ref } from 'vue';
import { NixClient } from 'nix-for-humanity';

export function useNixClient() {
  const client = new NixClient();
  const loading = ref(false);
  const error = ref(null);
  const response = ref(null);
  
  const query = async (text: string) => {
    loading.value = true;
    error.value = null;
    
    try {
      response.value = await client.query(text);
    } catch (e) {
      error.value = e;
    } finally {
      loading.value = false;
    }
  };
  
  return {
    query,
    loading,
    error,
    response
  };
}
```

## Complete Examples

### Web Application
```html
<!DOCTYPE html>
<html>
<head>
  <title>Nix for Humanity Web Client</title>
  <script src="https://unpkg.com/nix-for-humanity@latest/dist/nix-humanity.min.js"></script>
  <style>
    .container { max-width: 800px; margin: 0 auto; padding: 20px; }
    .query-input { width: 100%; padding: 10px; font-size: 16px; }
    .response { margin-top: 20px; padding: 15px; background: #f5f5f5; }
    .command { font-family: monospace; background: #333; color: #fff; padding: 10px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Nix for Humanity</h1>
    
    <input 
      type="text" 
      class="query-input" 
      placeholder="Ask me anything about NixOS..."
      id="queryInput"
    />
    
    <button onclick="askNix()">Ask</button>
    
    <div id="response" class="response" style="display: none;"></div>
  </div>

  <script>
    const client = new NixHumanity.NixClient({
      baseUrl: 'http://localhost:5000'
    });
    
    async function askNix() {
      const input = document.getElementById('queryInput');
      const responseDiv = document.getElementById('response');
      
      try {
        const response = await client.query(input.value);
        
        let html = `<p>${response.text}</p>`;
        
        if (response.commands.length > 0) {
          html += '<h3>Suggested Commands:</h3>';
          response.commands.forEach(cmd => {
            html += `<div class="command">${cmd.command}</div>`;
            html += `<p>${cmd.description}</p>`;
          });
        }
        
        responseDiv.innerHTML = html;
        responseDiv.style.display = 'block';
      } catch (error) {
        responseDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        responseDiv.style.display = 'block';
      }
    }
    
    // Enter key support
    document.getElementById('queryInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') askNix();
    });
  </script>
</body>
</html>
```

### Node.js CLI Tool
```javascript
#!/usr/bin/env node

import { NixClient, Personality } from 'nix-for-humanity';
import readline from 'readline';
import chalk from 'chalk';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: chalk.green('nix> ')
});

const client = new NixClient({
  personality: Personality.Friendly
});

console.log(chalk.blue('Nix for Humanity Interactive Shell'));
console.log(chalk.gray('Type "exit" to quit\n'));

rl.prompt();

rl.on('line', async (line) => {
  const query = line.trim();
  
  if (query.toLowerCase() === 'exit') {
    rl.close();
    return;
  }
  
  if (!query) {
    rl.prompt();
    return;
  }
  
  try {
    const response = await client.query(query);
    console.log('\n' + chalk.white(response.text));
    
    if (response.commands.length > 0) {
      console.log(chalk.yellow('\nSuggested commands:'));
      response.commands.forEach((cmd, i) => {
        console.log(`  ${i + 1}. ${chalk.cyan(cmd.command)}`);
      });
    }
    
    if (response.educational?.tip) {
      console.log(chalk.magenta(`\n💡 Tip: ${response.educational.tip}`));
    }
  } catch (error) {
    console.error(chalk.red(`Error: ${error.message}`));
  }
  
  console.log();
  rl.prompt();
});

rl.on('close', () => {
  console.log(chalk.blue('\nGoodbye!'));
  process.exit(0);
});
```

## Testing

### Jest Example
```javascript
import { NixClient } from 'nix-for-humanity';
import { jest } from '@jest/globals';

describe('NixClient', () => {
  let client;
  
  beforeEach(() => {
    client = new NixClient({ baseUrl: 'http://localhost:5000' });
  });
  
  test('should query successfully', async () => {
    const mockResponse = {
      text: 'Installing Firefox...',
      commands: [{
        command: 'nix-env -iA nixpkgs.firefox',
        description: 'Install Firefox',
        safe: true
      }]
    };
    
    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: 'success',
        response: mockResponse
      })
    });
    
    const response = await client.query('install firefox');
    
    expect(response.text).toBe('Installing Firefox...');
    expect(response.commands).toHaveLength(1);
    expect(response.commands[0].command).toContain('firefox');
  });
  
  test('should handle rate limits', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({
        error: 'Rate limit exceeded'
      })
    });
    
    await expect(client.query('test')).rejects.toThrow('Rate limit exceeded');
  });
});
```

## Best Practices

1. **Error Handling**: Always use try-catch or .catch() for API calls
2. **Rate Limiting**: Implement exponential backoff
3. **Session Persistence**: Store sessionId in localStorage/cookies
4. **Loading States**: Show loading indicators during API calls
5. **Caching**: Cache search results and common queries
6. **Timeouts**: Set appropriate timeouts for your use case
7. **Environment**: Use environment variables for configuration
8. **Type Safety**: Use TypeScript for better development experience

---

*Sacred Humility Context: This JavaScript SDK documentation represents our vision for a comprehensive client library. While the API endpoints are functional, the SDK itself is under development and may not include all features described. The examples demonstrate intended usage patterns that will be fully implemented as the project evolves.*

**Status**: In Development  
**Version**: 0.8.0  
**License**: MIT