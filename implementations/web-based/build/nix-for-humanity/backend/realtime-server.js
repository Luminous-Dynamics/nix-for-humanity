#!/usr/bin/env node
/**
 * Real-time WebSocket Server for Nix for Humanity
 * Handles command execution with progress updates
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const nixExecutor = require('./nix-executor');
const systemMonitor = require('./system-monitor');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..')));

// REST API endpoints
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    mode: process.env.NIX_DRY_RUN === 'true' ? 'dry-run' : 'live',
    timestamp: new Date().toISOString()
  });
});

app.get('/api/system-info', async (req, res) => {
  try {
    const info = await nixExecutor.getSystemInfo();
    res.json(info);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/search', async (req, res) => {
  const { query } = req.body;
  
  if (!query) {
    return res.status(400).json({ error: 'Query required' });
  }

  try {
    const results = await nixExecutor.searchPackages(query);
    res.json({ results });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/history', (req, res) => {
  const history = nixExecutor.getHistory();
  res.json({ history });
});

// Start system monitoring
systemMonitor.start();

// Forward monitor events to all clients
systemMonitor.on('state-changed', (state) => {
  io.emit('system-state', state);
});

systemMonitor.on('packages-changed', (data) => {
  io.emit('packages-changed', data);
});

systemMonitor.on('generation-changed', (data) => {
  io.emit('generation-changed', data);
});

systemMonitor.on('disk-warning', (data) => {
  io.emit('disk-warning', data);
});

systemMonitor.on('health-issues', (issues) => {
  io.emit('health-warning', { issues });
});

// WebSocket handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Send initial system info and state
  Promise.all([
    nixExecutor.getSystemInfo(),
    Promise.resolve(systemMonitor.getState())
  ]).then(([info, state]) => {
    socket.emit('system-info', info);
    socket.emit('system-state', state);
  });

  // Handle command execution
  socket.on('execute-command', async (data) => {
    const { command, sessionId } = data;
    
    console.log('Executing command:', command);
    
    try {
      // Subscribe to execution events
      const progressHandler = (progress) => {
        socket.emit('execution-progress', {
          sessionId,
          ...progress
        });
      };
      
      const warningHandler = (warning) => {
        socket.emit('execution-warning', {
          sessionId,
          ...warning
        });
      };

      nixExecutor.on('execution:progress', progressHandler);
      nixExecutor.on('execution:warning', warningHandler);

      // Execute command
      const result = await nixExecutor.execute(command);
      
      // Send success result
      socket.emit('execution-complete', {
        sessionId,
        success: true,
        result
      });

      // Cleanup listeners
      nixExecutor.off('execution:progress', progressHandler);
      nixExecutor.off('execution:warning', warningHandler);

    } catch (error) {
      socket.emit('execution-error', {
        sessionId,
        error: error.message,
        recovery: generateRecoverySuggestions(error)
      });
    }
  });

  // Handle rollback requests
  socket.on('rollback', async (data) => {
    const { generation } = data;
    
    try {
      const success = await nixExecutor.rollback(generation);
      socket.emit('rollback-complete', { success });
    } catch (error) {
      socket.emit('rollback-error', { error: error.message });
    }
  });

  // Handle package search
  socket.on('search-packages', async (data) => {
    const { query, sessionId } = data;
    
    try {
      const results = await nixExecutor.searchPackages(query);
      socket.emit('search-results', {
        sessionId,
        results
      });
    } catch (error) {
      socket.emit('search-error', {
        sessionId,
        error: error.message
      });
    }
  });

  // Request system state update
  socket.on('request-state', () => {
    socket.emit('system-state', systemMonitor.getState());
  });

  // Get monitoring summary
  socket.on('get-summary', () => {
    socket.emit('monitoring-summary', systemMonitor.getSummary());
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Error recovery suggestions
function generateRecoverySuggestions(error) {
  const errorMessage = error.message.toLowerCase();
  const suggestions = [];

  if (errorMessage.includes('not found')) {
    suggestions.push({
      action: 'search',
      description: 'Search for similar packages'
    });
    suggestions.push({
      action: 'update-channels',
      description: 'Update package channels'
    });
  }

  if (errorMessage.includes('permission')) {
    suggestions.push({
      action: 'use-sudo',
      description: 'Try with administrator privileges'
    });
  }

  if (errorMessage.includes('network') || errorMessage.includes('download')) {
    suggestions.push({
      action: 'check-network',
      description: 'Check internet connection'
    });
    suggestions.push({
      action: 'retry',
      description: 'Try again'
    });
  }

  if (errorMessage.includes('space')) {
    suggestions.push({
      action: 'garbage-collect',
      description: 'Free up disk space'
    });
  }

  return suggestions;
}

// Start server
const PORT = process.env.PORT || 3456;
server.listen(PORT, () => {
  console.log(`🚀 Nix for Humanity server running on port ${PORT}`);
  console.log(`🔒 Mode: ${process.env.NIX_DRY_RUN === 'true' ? 'DRY RUN (safe)' : 'LIVE'}`);
  console.log(`📁 Static files: ${path.join(__dirname, '..')}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  systemMonitor.stop();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});