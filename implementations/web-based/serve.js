const express = require('express');
const path = require('path');

const app = express();
const PORT = 3456;

// Serve static files
app.use(express.static('.'));

// Enable CORS for development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// Serve index.html for root
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Nix for Humanity running at http://localhost:${PORT}`);
  console.log('📝 Type "install firefox" or click the microphone to speak');
});
