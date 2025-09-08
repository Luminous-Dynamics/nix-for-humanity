# 🚀 Luminous Nix v0.3.0 Deployment Guide

## Overview

This guide covers deploying Luminous Nix v0.3.0 with its neural network components, achieving 96%+ accuracy for natural language NixOS operations.

## 📋 Prerequisites

- Python 3.11 or higher
- 250MB available RAM
- 100MB disk space
- NixOS or Linux with Nix installed
- Poetry (optional, for development)

## 🔧 Installation Options

### Option 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix.git
cd luminous-nix

# Install with Poetry
poetry install

# Run the system
poetry run python src/luminous_nix/ai/hrm_integrated_v6_final.py
```

### Option 2: Standalone Package

```bash
# Download release package
wget https://github.com/Luminous-Dynamics/luminous-nix/releases/download/v0.3.0/luminous-nix-v0.3.0.tar.gz

# Extract
tar -xzf luminous-nix-v0.3.0.tar.gz
cd luminous-nix-v0.3.0

# Install dependencies
pip install -r requirements.txt

# Run
python hrm_integrated_v6_final.py
```

### Option 3: Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "python", "src/luminous_nix/ai/hrm_integrated_v6_final.py"]
```

```bash
# Build and run
docker build -t luminous-nix:v0.3.0 .
docker run -it luminous-nix:v0.3.0
```

## 🎯 Basic Usage

### Python API

```python
from luminous_nix.ai.hrm_integrated_v6_final import HRMIntegratedV6Final

# Initialize the system
system = HRMIntegratedV6Final(enable_active_learning=True)

# Process a query
result = system.process_query("install firefox")
print(f"Command: {result['command']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Latency: {result['production_metadata']['latency_ms']}ms")

# Record feedback for learning
feedback = {
    'correct': True,  # or False if incorrect
    'correct_category': 'install',  # if correction needed
    'correct_command': 'nix-env -iA nixpkgs.firefox'  # if correction needed
}
system.record_feedback("install firefox", result, feedback)
```

### Command Line Interface

```bash
# Process single query
python -m luminous_nix.cli "install firefox"

# Batch processing
python -m luminous_nix.cli --batch queries.txt

# With active learning
python -m luminous_nix.cli --enable-learning "update system"
```

### REST API Server

```python
# server.py
from flask import Flask, request, jsonify
from luminous_nix.ai.hrm_integrated_v6_final import HRMIntegratedV6Final

app = Flask(__name__)
system = HRMIntegratedV6Final(enable_active_learning=True)

@app.route('/query', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query')
    user_id = data.get('user_id', 'anonymous')
    
    result = system.process_query(query, user_id)
    return jsonify(result)

@app.route('/feedback', methods=['POST'])
def record_feedback():
    data = request.json
    query = data.get('query')
    result = data.get('result')
    feedback = data.get('feedback')
    
    learning_result = system.record_feedback(query, result, feedback)
    return jsonify(learning_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🔧 Configuration

### Environment Variables

```bash
# Performance tuning
export LUMINOUS_CACHE_SIZE=1000      # Max cache entries (default: 1000)
export LUMINOUS_BATCH_SIZE=100       # Batch processing size
export LUMINOUS_PREFETCH=true        # Prefetch common queries

# Active learning
export LUMINOUS_LEARNING=true        # Enable active learning
export LUMINOUS_LEARNING_DB=data/learning.db  # Learning database path
export LUMINOUS_FEEDBACK_MIN=3       # Min feedback before pattern learning

# Logging
export LUMINOUS_LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR
export LUMINOUS_LOG_FILE=luminous.log
```

### Configuration File

```yaml
# config.yaml
system:
  version: v0.3.0
  enable_learning: true
  cache_size: 1000
  
performance:
  batch_size: 100
  prefetch_common: true
  max_workers: 4
  
learning:
  database: data/active_learning.db
  min_feedback: 3
  confidence_boost: 0.02
  confidence_penalty: -0.05
  
components:
  specialists:
    enabled: true
    confidence_threshold: 0.90
  transformer:
    enabled: true
    confidence_threshold: 0.85
  ensemble:
    enabled: true
    confidence_threshold: 0.80
```

## 🚀 Production Deployment

### 1. System Requirements

- **Minimum**: 1 CPU, 256MB RAM, 100MB disk
- **Recommended**: 2 CPUs, 512MB RAM, 500MB disk
- **Optimal**: 4 CPUs, 1GB RAM, 1GB disk

### 2. Pre-deployment Checklist

- [ ] Python 3.11+ installed
- [ ] All dependencies installed
- [ ] Models downloaded (50MB)
- [ ] Database initialized
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backup strategy defined

### 3. Deployment Steps

```bash
# 1. Create deployment directory
sudo mkdir -p /opt/luminous-nix
cd /opt/luminous-nix

# 2. Copy application files
sudo cp -r /path/to/luminous-nix/* .

# 3. Install dependencies
sudo pip install -r requirements.txt

# 4. Initialize database
python -c "from luminous_nix.ai.active_learning_system import ActiveLearningSystem; ActiveLearningSystem()"

# 5. Create systemd service
sudo cat > /etc/systemd/system/luminous-nix.service << EOF
[Unit]
Description=Luminous Nix Natural Language NixOS Interface
After=network.target

[Service]
Type=simple
User=luminous
WorkingDirectory=/opt/luminous-nix
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Start service
sudo systemctl daemon-reload
sudo systemctl enable luminous-nix
sudo systemctl start luminous-nix

# 7. Verify deployment
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "install firefox"}'
```

### 4. Load Balancing

For high-traffic deployments:

```nginx
# nginx.conf
upstream luminous_backend {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
    server 127.0.0.1:5004;
}

server {
    listen 80;
    server_name api.luminous-nix.org;
    
    location / {
        proxy_pass http://luminous_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### Health Check Endpoint

```python
@app.route('/health', methods=['GET'])
def health_check():
    metrics = system.get_production_metrics()
    return jsonify({
        'status': 'healthy',
        'accuracy': metrics['summary']['estimated_accuracy'],
        'latency_ms': metrics['summary']['avg_latency_ms'],
        'cache_rate': metrics['summary']['cache_hit_rate'],
        'queries_total': metrics['summary']['total_queries'],
        'uptime_hours': metrics['summary']['uptime_hours']
    })
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

query_counter = Counter('luminous_queries_total', 'Total queries processed')
latency_histogram = Histogram('luminous_latency_seconds', 'Query latency')
accuracy_gauge = Gauge('luminous_accuracy', 'Current accuracy estimate')
cache_rate_gauge = Gauge('luminous_cache_rate', 'Cache hit rate')
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('luminous.log'),
        logging.StreamHandler()
    ]
)
```

## 🔄 Maintenance

### Database Maintenance

```bash
# Backup learning database
sqlite3 data/active_learning.db ".backup data/backup_$(date +%Y%m%d).db"

# Vacuum database (monthly)
sqlite3 data/active_learning.db "VACUUM;"

# Export learned patterns
python -c "
from luminous_nix.ai.active_learning_system import ActiveLearningSystem
system = ActiveLearningSystem()
improvements = system.export_improvements()
import json
with open('learned_patterns.json', 'w') as f:
    json.dump(improvements, f, indent=2)
"
```

### Model Updates

```bash
# Export current model
python -c "
from luminous_nix.ai.hrm_integrated_v6_final import HRMIntegratedV6Final
system = HRMIntegratedV6Final()
system.export_model('models/production_export')
"

# Update models
wget https://updates.luminous-nix.org/models/latest.tar.gz
tar -xzf latest.tar.gz -C models/

# Restart service
sudo systemctl restart luminous-nix
```

## 🐛 Troubleshooting

### Common Issues

#### High Latency
- Check cache hit rate: Should be >50%
- Verify prefetch is enabled
- Consider increasing cache size

#### Low Accuracy
- Check active learning is enabled
- Review feedback quality
- Export and analyze patterns

#### Memory Issues
- Reduce cache size
- Enable model quantization
- Use batch processing

### Debug Mode

```bash
# Enable debug logging
export LUMINOUS_LOG_LEVEL=DEBUG

# Run with profiling
python -m cProfile -o profile.stats server.py

# Analyze profile
python -m pstats profile.stats
```

## 🔐 Security Considerations

1. **Input Validation**: Always validate and sanitize user queries
2. **Rate Limiting**: Implement per-user rate limits
3. **Authentication**: Use API keys for production deployments
4. **Command Execution**: Never execute commands directly, only return them
5. **Database Security**: Use read-only database users where possible

## 📈 Performance Tuning

### Cache Optimization
```python
# Increase cache size for high-traffic
system.core_system.memory_cache = {}  # Clear cache
system.optimizations['prefetch_common'] = True
system._prefetch_common_queries()  # Re-prefetch
```

### Batch Processing
```python
# Process multiple queries efficiently
queries = ["install firefox", "update system", "search editors"]
results = system.process_batch(queries)
```

### Async Processing
```python
import asyncio

async def async_query(query):
    return await asyncio.to_thread(system.process_query, query)

# Process concurrently
queries = ["query1", "query2", "query3"]
results = await asyncio.gather(*[async_query(q) for q in queries])
```

## 📚 Additional Resources

- [API Documentation](https://docs.luminous-nix.org/api)
- [Training Custom Models](https://docs.luminous-nix.org/training)
- [Contributing Guide](https://github.com/Luminous-Dynamics/luminous-nix/CONTRIBUTING.md)
- [Support Forum](https://forum.luminous-nix.org)

## 🆘 Support

- **GitHub Issues**: https://github.com/Luminous-Dynamics/luminous-nix/issues
- **Discord**: https://discord.gg/luminous-nix
- **Email**: support@luminous-nix.org

---

*Deployment Guide v0.3.0 - Last Updated: January 29, 2025*