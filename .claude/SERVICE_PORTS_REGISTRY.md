# 🔌 Service Ports Registry - Nix for Humanity

## Port Allocations

### Nix for Humanity Services

| Port | Service | Description | Status |
|------|---------|-------------|--------|
| **3456** | NLP Core API | Main REST API for intent processing | Active |
| **3457** | WebSocket Server | Real-time voice/text streaming | Active |
| **3458** | Learning GUI | Progressive interface server | Planned |
| **3459** | Metrics Server | Local metrics collection | Planned |
| **8080** | Development Server | Webpack dev server | Dev only |
| **8081** | Tauri Dev | Desktop app development | Dev only |

### Integration with Luminous-Dynamics Ecosystem

| Port | Service | Description | Owner |
|------|---------|-------------|-------|
| **3001** | The Weave | Agent coordination | 01-resonant-coherence |
| **3333** | Sacred Core | Core sacred API | 01-resonant-coherence |
| **3338** | Field Visualizer | Coherence display | 02-pan-sentient-flourishing |
| **7777** | Sacred Bridge | Consciousness bus | 05-universal-interconnectedness |
| **8080** | Codex | Glyph registry | 03-integral-wisdom |

### Testing & Development Ports

| Port | Purpose | Lifetime |
|------|---------|----------|
| **9000** | Test server | During tests only |
| **9001** | Mock NixOS API | During tests only |
| **9002** | WebSocket test server | During tests only |
| **6006** | Storybook | Development only |

## Port Selection Rationale

### Why 3456-3459 Range?
- Available in default NixOS firewall rules
- Not commonly used by other services
- Sequential for easy remembering
- Away from Sacred Core (3333) to avoid confusion

### Reserved Ranges to Avoid
- **3000-3010** - Common Node.js apps
- **8000-8090** - Common development servers
- **5000-5010** - Common Python/Flask apps
- **4200-4210** - Angular development
- **3306, 5432, 6379** - Database defaults

## NixOS Configuration

```nix
# /etc/nixos/configuration.nix
networking.firewall = {
  allowedTCPPorts = [ 
    3456  # Nix for Humanity API
    3457  # Nix for Humanity WebSocket
  ];
};

# Service configuration
services.nix-for-humanity = {
  enable = true;
  api.port = 3456;
  websocket.port = 3457;
};
```

## Docker Configuration

```yaml
# docker-compose.yml
services:
  nlp-api:
    ports:
      - "3456:3456"
  
  websocket:
    ports:
      - "3457:3457"
```

## Development Environment

```bash
# .env
NLP_API_PORT=3456
WEBSOCKET_PORT=3457
LEARNING_GUI_PORT=3458
METRICS_PORT=3459

# Fallback for conflicts
NLP_API_PORT_ALT=13456
WEBSOCKET_PORT_ALT=13457
```

## Conflict Resolution

### Check Port Availability
```bash
# Check if port is in use
lsof -i :3456
netstat -tlnp | grep 3456
ss -tlnp | grep 3456

# Find available port in range
for port in {3456..3459}; do
  lsof -i :$port >/dev/null 2>&1 || echo "Port $port is available"
done
```

### If Ports Conflict
1. Check `SERVICE_PORTS_REGISTRY.md` in main Luminous-Dynamics
2. Use alternative ports (13456-13459)
3. Update configuration files
4. Document in this file

## Integration with Port Registry

**Main Registry Location**: `/srv/luminous-dynamics/00-sacred-foundation/tools/port-registry.json`

### Register Our Ports
```bash
# Use the sacred port registry tool
cd /srv/luminous-dynamics/00-sacred-foundation/tools
node sacred-port-registry.js register \
  --name "nix-for-humanity" \
  --port 3456 \
  --description "Natural language interface for NixOS" \
  --path "11-meta-consciousness/nix-for-humanity"
```

### Check Port Availability
```javascript
// Check Luminous-Dynamics port registry
const portRegistry = require('/srv/luminous-dynamics/00-sacred-foundation/tools/port-registry.json');

const checkPortAvailability = (port) => {
  // Check all service categories
  for (const category of Object.values(portRegistry.services)) {
    for (const service of Object.values(category)) {
      if (service.port === port) {
        return false; // Port is taken
      }
    }
  }
  
  // Check reserved ports
  if (Object.values(portRegistry.reserved).includes(port)) {
    return false;
  }
  
  return true; // Port is available
};
```

## Service Discovery

```javascript
// Service registration with Sacred Bridge
const registerService = async () => {
  await fetch('http://localhost:7777/api/services', {
    method: 'POST',
    body: JSON.stringify({
      name: 'nix-for-humanity',
      ports: {
        api: 3456,
        websocket: 3457
      },
      capabilities: ['nlp', 'voice', 'nixos-management']
    })
  });
};
```

## Monitoring

```bash
# Monitor all Nix for Humanity ports
watch -n 1 'lsof -i :3456-3459'

# Check service health
curl http://localhost:3456/health
curl http://localhost:3457/health
```

## Emergency Procedures

### Port Already in Use
```bash
# Find process using port
lsof -i :3456 | grep LISTEN

# Kill process (careful!)
kill $(lsof -t -i :3456)

# Or change to alternative port
export NLP_API_PORT=13456
```

### Update All References
If changing ports, update:
- [ ] This file
- [ ] .env files
- [ ] docker-compose.yml
- [ ] NixOS configuration
- [ ] Documentation
- [ ] Tests

---

*Ports are sacred boundaries. Respect them, document them, and they will serve you well.*