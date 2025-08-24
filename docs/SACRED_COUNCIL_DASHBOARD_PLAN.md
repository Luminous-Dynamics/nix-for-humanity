# 🎭 Sacred Council Visualization Dashboard - Architecture Plan

## 🎯 Vision

Create a real-time visualization dashboard that shows the Sacred Council's deliberation process, making AI decision-making transparent, educational, and beautiful.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Dashboard Frontend                      │
│  (React/Vue/Vanilla JS with WebSocket connection)        │
└────────────────┬────────────────────────────────────────┘
                 │ WebSocket
┌────────────────▼────────────────────────────────────────┐
│              WebSocket Server (Node.js)                  │
│         (Bridges CLI events to dashboard)                │
└────────────────┬────────────────────────────────────────┘
                 │ Events
┌────────────────▼────────────────────────────────────────┐
│          Event Emission System (Python)                  │
│    (Sacred Council emits deliberation events)            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│            Sacred Council Integration                    │
│         (Current CLI protection system)                  │
└─────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites to Build First

### 1. **Event Emission System** (Priority 1)
We need the Sacred Council to emit events during deliberation:

```python
class SacredCouncilGuard:
    def __init__(self, event_emitter=None):
        self.event_emitter = event_emitter
    
    def check_command(self, command):
        # Emit event when checking starts
        self._emit_event('check_started', {
            'command': command,
            'timestamp': datetime.now()
        })
        
        # Pattern check
        assessment = self._pattern_check(command)
        self._emit_event('pattern_checked', assessment)
        
        # Council deliberation
        if need_deliberation:
            self._emit_event('deliberation_started')
            # Mind analysis
            self._emit_event('mind_thinking', mind_response)
            # Heart analysis
            self._emit_event('heart_feeling', heart_response)
            # Conscience judgment
            self._emit_event('conscience_judging', conscience_response)
            
        # Final verdict
        self._emit_event('verdict_reached', final_assessment)
```

### 2. **Event Storage/Queue** (Priority 2)
Need a way to store events for the dashboard to consume:

Options:
- **Redis** - Fast pub/sub, requires external service
- **SQLite** - Simple, file-based, good for persistence
- **In-memory Queue** - Simplest, loses data on restart
- **File-based JSON** - Simple, persistent, human-readable

Recommendation: **SQLite + JSON file fallback**

### 3. **IPC Mechanism** (Priority 3)
How Python CLI communicates with Node.js server:

Options:
- **Named Pipes** - Fast, Unix-only
- **TCP Socket** - Universal, more complex
- **File watching** - Simple, some latency
- **HTTP POST** - Simple, standard, some overhead
- **ZeroMQ** - Powerful, requires library

Recommendation: **HTTP POST to localhost** (simple, standard)

## 🎨 Dashboard Features

### Core Visualizations

#### 1. **Command Risk Meter**
```
[SAFE]──[LOW]──[MEDIUM]──[HIGH]──[CRITICAL]
         ↑
    Current Risk
```

#### 2. **Council Members Status**
```
┌─────────┬─────────┬──────────┐
│  Mind   │  Heart  │Conscience│
│   🧠    │   ❤️    │    ⚖️     │
│Thinking │Feeling  │ Judging  │
└─────────┴─────────┴──────────┘
```

#### 3. **Deliberation Timeline**
```
10:23:45 → Command received: "rm -rf /etc/nixos"
10:23:45 → Pattern match: CRITICAL RISK
10:23:46 → Mind: "This would destroy system configuration"
10:23:47 → Heart: "User would lose all customizations"
10:23:48 → Conscience: "No legitimate use case exists"
10:23:49 → VERDICT: BLOCKED
```

#### 4. **Safe Alternatives Display**
```
❌ Blocked: rm -rf /etc/nixos

✅ Try Instead:
• backup first: cp -r /etc/nixos /etc/nixos.backup
• rollback: nixos-rebuild --rollback
• check status: git status /etc/nixos
```

#### 5. **Statistics Panel**
```
Session Stats:
• Commands Checked: 47
• Blocked: 3
• Warnings Given: 8
• User Heeded Warnings: 7/8
• Most Common Risk: File Deletion
```

### Advanced Features

#### 1. **Pattern Visualization**
Show which regex patterns matched and why

#### 2. **Learning Insights**
If POMLMemory is active, show what the system has learned

#### 3. **Command History**
Scrollable list of all checked commands with outcomes

#### 4. **Risk Heatmap**
Visual representation of risky command categories

#### 5. **Educational Mode**
Detailed explanations of each risk type

## 🛠️ Technology Stack Options

### Option 1: **Lightweight Web** (Recommended for MVP)
- **Backend**: Node.js + Express + Socket.io
- **Frontend**: Vanilla JS + CSS (no framework)
- **Data**: SQLite for events
- **Hosting**: Local only (localhost:8888)

**Pros**: Simple, fast to build, minimal dependencies
**Cons**: Less fancy, manual DOM updates

### Option 2: **Modern React**
- **Backend**: Node.js + Express + Socket.io
- **Frontend**: React + Material-UI/Chakra
- **Data**: Redis for pub/sub
- **Build**: Vite

**Pros**: Modern, componentized, rich UI
**Cons**: More complex, build step required

### Option 3: **Python Native**
- **Backend**: FastAPI + WebSockets
- **Frontend**: Streamlit or Gradio
- **Data**: In-memory + SQLite

**Pros**: All Python, integrates directly
**Cons**: Less flexible UI

### Option 4: **Terminal UI** (Interesting alternative)
- **Backend**: Python async
- **Frontend**: Rich/Textual TUI
- **Data**: In-memory

**Pros**: No browser needed, native terminal
**Cons**: Limited visualizations

## 📝 Implementation Steps

### Phase 1: Foundation (Week 1)
1. ✅ Sacred Council integration (DONE)
2. 🚧 Add event emission to SacredCouncilGuard
3. 🚧 Create event storage (SQLite)
4. 🚧 Add HTTP endpoint for events

### Phase 2: Bridge (Week 1-2)
1. Create Node.js WebSocket server
2. Connect to Python event stream
3. Test real-time event flow
4. Add event buffering/replay

### Phase 3: Dashboard MVP (Week 2)
1. Create basic HTML interface
2. Add WebSocket connection
3. Display real-time events
4. Show risk meter and verdict

### Phase 4: Polish (Week 3)
1. Add Council member animations
2. Create alternatives display
3. Add statistics tracking
4. Improve styling

### Phase 5: Advanced (Optional)
1. Pattern visualization
2. Learning insights
3. Historical analysis
4. Export capabilities

## 🚀 Quick Start Plan

### Minimum Viable Dashboard (1-2 days)

1. **Modify SacredCouncilGuard** to write events to JSON file
2. **Create simple Node.js server** that watches the file
3. **Build basic HTML page** with WebSocket client
4. **Display events** in real-time list

```javascript
// Minimal server.js
const express = require('express');
const { Server } = require('socket.io');
const fs = require('fs');

const app = express();
const io = new Server(server);

// Watch events file
fs.watch('/tmp/sacred-council-events.json', (event) => {
  const events = JSON.parse(fs.readFileSync('/tmp/sacred-council-events.json'));
  io.emit('council-event', events[events.length - 1]);
});

app.use(express.static('public'));
server.listen(8888);
```

```html
<!-- Minimal index.html -->
<div id="events"></div>
<script src="/socket.io/socket.io.js"></script>
<script>
  const socket = io();
  socket.on('council-event', (event) => {
    document.getElementById('events').innerHTML += 
      `<div>${event.type}: ${event.data}</div>`;
  });
</script>
```

## 🎯 Success Metrics

1. **Real-time Updates** - < 100ms latency
2. **Clear Visualization** - User understands the decision
3. **Educational Value** - User learns about risks
4. **Performance** - No impact on CLI speed
5. **Reliability** - Dashboard doesn't crash CLI

## 📊 Decision: Recommended Approach

### For Immediate Implementation (MVP):
1. **Event System**: JSON file + file watching
2. **Server**: Simple Node.js + Socket.io
3. **Frontend**: Vanilla JS with nice CSS
4. **Duration**: 1-2 days

### Why This Approach:
- ✅ Minimal dependencies
- ✅ Fast to implement
- ✅ Easy to test
- ✅ Can upgrade later
- ✅ Works on any system

### Future Upgrade Path:
MVP → Add React → Add Redis → Add ML insights → Production ready

## 🔧 Next Immediate Steps

1. **Create event emitter mixin** for SacredCouncilGuard
2. **Set up JSON event log** with rotation
3. **Create minimal Node.js server** with Socket.io
4. **Build basic HTML dashboard** with real-time updates
5. **Test with real commands**

---

*"Make the invisible visible. Show the Council's wisdom in action."*

**Ready to Build?** Start with Phase 1 - Event Emission!