// 🌟 Nix for Humanity MVP - Express Server
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');
require('dotenv').config();

// Import routes
const nlpRoutes = require('./routes/nlp');

// Create Express app
const app = express();
const PORT = process.env.PORT || 3456;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.static('public'));
app.use(morgan('dev'));

// Routes
app.use('/api/nlp', nlpRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'nix-for-humanity-mvp',
    version: '0.1.0',
    uptime: process.uptime()
  });
});

// Serve the simple web interface
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`✨ Nix for Humanity MVP running on http://localhost:${PORT}`);
  console.log(`📚 API endpoint: http://localhost:${PORT}/api/nlp/process`);
  console.log(`🌐 Web interface: http://localhost:${PORT}`);
});