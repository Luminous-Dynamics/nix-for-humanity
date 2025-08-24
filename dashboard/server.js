#!/usr/bin/env node
/**
 * Sacred Council Dashboard Server
 * WebSocket server that broadcasts Council events to dashboard
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const fs = require('fs');
const path = require('path');
const chokidar = require('chokidar');

// Configuration
const PORT = process.env.PORT || 8888;
const EVENTS_FILE = '/tmp/sacred-council-events.json';
const STATIC_DIR = path.join(__dirname, 'public');

// Create Express app
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Track connected clients
let connectedClients = 0;
let lastEvents = [];
let sessionStats = {};

// Serve static files
app.use(express.static(STATIC_DIR));

// API endpoint for events (REST fallback)
app.get('/api/events', (req, res) => {
  res.json(lastEvents);
});

// API endpoint for stats
app.get('/api/stats', (req, res) => {
  res.json({
    connectedClients,
    totalEvents: lastEvents.length,
    sessionStats
  });
});

// Load events from file
function loadEvents() {
  try {
    if (fs.existsSync(EVENTS_FILE)) {
      const content = fs.readFileSync(EVENTS_FILE, 'utf8');
      const events = JSON.parse(content);
      return events || [];
    }
  } catch (error) {
    console.error('Error loading events:', error);
  }
  return [];
}

// Calculate session statistics
function calculateStats(events) {
  const stats = {
    totalCommands: 0,
    riskLevels: {},
    blockedCommands: 0,
    warningsGiven: 0,
    safePassed: 0
  };
  
  events.forEach(event => {
    if (event.event_type === 'check_started') {
      stats.totalCommands++;
    } else if (event.event_type === 'pattern_checked') {
      const risk = event.data.risk_level;
      stats.riskLevels[risk] = (stats.riskLevels[risk] || 0) + 1;
    } else if (event.event_type === 'verdict_reached') {
      if (event.data.verdict === 'BLOCK') {
        stats.blockedCommands++;
      } else if (event.data.risk_level !== 'SAFE') {
        stats.warningsGiven++;
      } else {
        stats.safePassed++;
      }
    }
  });
  
  return stats;
}

// Watch for changes to events file
const watcher = chokidar.watch(EVENTS_FILE, {
  persistent: true,
  awaitWriteFinish: {
    stabilityThreshold: 200,
    pollInterval: 100
  }
});

// Handle file changes
watcher.on('change', () => {
  console.log('Events file changed, loading new events...');
  const events = loadEvents();
  
  if (events.length > lastEvents.length) {
    // New events added
    const newEvents = events.slice(lastEvents.length);
    
    newEvents.forEach(event => {
      console.log(`Broadcasting event: ${event.event_type}`);
      io.emit('council-event', event);
    });
    
    lastEvents = events;
    sessionStats = calculateStats(events);
    io.emit('stats-update', sessionStats);
  }
});

// Handle WebSocket connections
io.on('connection', (socket) => {
  connectedClients++;
  console.log(`Client connected (total: ${connectedClients})`);
  
  // Send current events to new client
  socket.emit('initial-events', lastEvents);
  socket.emit('stats-update', sessionStats);
  
  // Handle client messages
  socket.on('request-stats', () => {
    socket.emit('stats-update', sessionStats);
  });
  
  socket.on('clear-events', () => {
    // Clear events file
    fs.writeFileSync(EVENTS_FILE, '[]');
    lastEvents = [];
    sessionStats = calculateStats([]);
    io.emit('events-cleared');
    io.emit('stats-update', sessionStats);
    console.log('Events cleared by client');
  });
  
  socket.on('disconnect', () => {
    connectedClients--;
    console.log(`Client disconnected (total: ${connectedClients})`);
  });
});

// Initialize
console.log('🛡️ Sacred Council Dashboard Server');
console.log('=====================================');

// Load initial events
lastEvents = loadEvents();
sessionStats = calculateStats(lastEvents);
console.log(`Loaded ${lastEvents.length} existing events`);

// Start server
server.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log(`📁 Watching events file: ${EVENTS_FILE}`);
  console.log(`📊 Initial stats:`, sessionStats);
  console.log('');
  console.log('Waiting for Sacred Council events...');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down gracefully...');
  watcher.close();
  io.close();
  server.close();
  process.exit(0);
});