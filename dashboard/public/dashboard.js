/**
 * Sacred Council Dashboard Client
 * Real-time visualization of Council deliberations
 */

// Connect to WebSocket server
const socket = io();

// Dashboard state
let currentCommand = null;
let currentRiskLevel = 'SAFE';
let stats = {
    totalCommands: 0,
    blockedCommands: 0,
    warningsGiven: 0,
    safePassed: 0
};

// DOM elements
const elements = {
    connectionStatus: document.getElementById('connectionStatus'),
    riskIndicator: document.getElementById('riskIndicator'),
    currentCommand: document.getElementById('currentCommand'),
    timeline: document.getElementById('timeline'),
    totalCommands: document.getElementById('totalCommands'),
    blockedCommands: document.getElementById('blockedCommands'),
    warningsGiven: document.getElementById('warningsGiven'),
    safePassed: document.getElementById('safePassed'),
    riskBreakdown: document.getElementById('riskBreakdown'),
    alternativesPanel: document.getElementById('alternativesPanel'),
    alternativesList: document.getElementById('alternativesList'),
    verdictPanel: document.getElementById('verdictPanel'),
    verdict: document.getElementById('verdict'),
    clearEvents: document.getElementById('clearEvents'),
    mindMember: document.getElementById('mindMember'),
    heartMember: document.getElementById('heartMember'),
    conscienceMember: document.getElementById('conscienceMember')
};

// Risk level positions for indicator
const riskPositions = {
    'SAFE': '10%',
    'LOW': '30%',
    'MEDIUM': '50%',
    'HIGH': '70%',
    'CRITICAL': '90%'
};

// Format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Add event to timeline
function addToTimeline(event) {
    const item = document.createElement('div');
    item.className = 'timeline-item';
    
    // Add risk class based on event type
    if (event.data?.risk_level === 'CRITICAL' || event.data?.verdict === 'BLOCK') {
        item.classList.add('critical');
    } else if (event.data?.risk_level === 'HIGH' || event.data?.risk_level === 'MEDIUM') {
        item.classList.add('warning');
    } else if (event.data?.risk_level === 'SAFE' || event.data?.verdict === 'ALLOW') {
        item.classList.add('safe');
    }
    
    const time = document.createElement('span');
    time.className = 'time';
    time.textContent = formatTime(event.timestamp);
    
    const eventText = document.createElement('span');
    eventText.className = 'event';
    eventText.textContent = getEventDescription(event);
    
    item.appendChild(time);
    item.appendChild(eventText);
    
    elements.timeline.insertBefore(item, elements.timeline.firstChild);
    
    // Keep timeline size manageable
    while (elements.timeline.children.length > 100) {
        elements.timeline.removeChild(elements.timeline.lastChild);
    }
}

// Get human-readable event description
function getEventDescription(event) {
    switch (event.event_type) {
        case 'check_started':
            return `🔍 Checking command: ${event.data.command}`;
        case 'pattern_checked':
            return `📋 Pattern analysis: ${event.data.risk_level} risk${event.data.reason ? ' - ' + event.data.reason : ''}`;
        case 'deliberation_started':
            return `🧘 Sacred Council deliberation started`;
        case 'mind_thinking':
            return `🧠 Mind: ${event.data.thought}`;
        case 'heart_thinking':
            return `❤️ Heart: ${event.data.thought}`;
        case 'conscience_thinking':
            return `⚖️ Conscience: ${event.data.thought}`;
        case 'alternatives_generated':
            return `✅ Generated ${event.data.count} safe alternatives`;
        case 'verdict_reached':
            return `⚖️ Verdict: ${event.data.verdict} - ${event.data.reason}`;
        case 'user_response':
            return `👤 User ${event.data.accepted ? 'accepted' : 'rejected'} the warning`;
        default:
            return `📌 ${event.event_type}`;
    }
}

// Update risk meter
function updateRiskMeter(riskLevel) {
    currentRiskLevel = riskLevel;
    const position = riskPositions[riskLevel] || '10%';
    elements.riskIndicator.style.left = position;
    
    // Add animation
    elements.riskIndicator.style.animation = 'none';
    setTimeout(() => {
        elements.riskIndicator.style.animation = 'bounce 0.5s ease';
    }, 10);
}

// Update Council member
function updateCouncilMember(member, event) {
    let element;
    switch (member) {
        case 'mind':
            element = elements.mindMember;
            break;
        case 'heart':
            element = elements.heartMember;
            break;
        case 'conscience':
            element = elements.conscienceMember;
            break;
        default:
            return;
    }
    
    // Update status
    element.classList.add('active');
    element.querySelector('.member-status').textContent = 'Analyzing...';
    element.querySelector('.member-thought').textContent = event.data.analysis || event.data.thought;
    
    // Remove active state after animation
    setTimeout(() => {
        element.classList.remove('active');
        element.querySelector('.member-status').textContent = 'Ready';
    }, 3000);
}

// Show alternatives
function showAlternatives(alternatives) {
    elements.alternativesPanel.style.display = 'block';
    elements.alternativesList.innerHTML = '';
    
    alternatives.forEach(alt => {
        const item = document.createElement('div');
        item.className = 'alternative-item';
        item.textContent = alt;
        elements.alternativesList.appendChild(item);
    });
}

// Show verdict
function showVerdict(event) {
    elements.verdictPanel.style.display = 'block';
    elements.verdict.textContent = `${event.data.verdict}: ${event.data.reason}`;
    
    elements.verdict.className = 'verdict';
    if (event.data.verdict === 'BLOCK') {
        elements.verdict.classList.add('blocked');
    } else if (event.data.safe) {
        elements.verdict.classList.add('allowed');
    } else {
        elements.verdict.classList.add('warning');
    }
}

// Update statistics
function updateStats(newStats) {
    stats = newStats;
    elements.totalCommands.textContent = stats.totalCommands || 0;
    elements.blockedCommands.textContent = stats.blockedCommands || 0;
    elements.warningsGiven.textContent = stats.warningsGiven || 0;
    elements.safePassed.textContent = stats.safePassed || 0;
    
    // Update risk breakdown
    elements.riskBreakdown.innerHTML = '';
    if (stats.riskLevels) {
        Object.entries(stats.riskLevels).forEach(([level, count]) => {
            const badge = document.createElement('span');
            badge.className = `risk-badge ${level.toLowerCase()}`;
            badge.textContent = `${level}: ${count}`;
            elements.riskBreakdown.appendChild(badge);
        });
    }
}

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to Sacred Council Dashboard');
    elements.connectionStatus.innerHTML = `
        <span class="status-dot online"></span>
        <span>Connected</span>
    `;
});

socket.on('disconnect', () => {
    console.log('Disconnected from Sacred Council Dashboard');
    elements.connectionStatus.innerHTML = `
        <span class="status-dot offline"></span>
        <span>Disconnected</span>
    `;
});

socket.on('initial-events', (events) => {
    console.log(`Received ${events.length} initial events`);
    // Process last 20 events for timeline
    events.slice(-20).reverse().forEach(event => {
        addToTimeline(event);
    });
});

socket.on('council-event', (event) => {
    console.log('Received event:', event);
    addToTimeline(event);
    
    // Handle specific event types
    switch (event.event_type) {
        case 'check_started':
            currentCommand = event.data.command;
            elements.currentCommand.textContent = currentCommand;
            // Reset panels
            elements.alternativesPanel.style.display = 'none';
            elements.verdictPanel.style.display = 'none';
            break;
            
        case 'pattern_checked':
            updateRiskMeter(event.data.risk_level);
            break;
            
        case 'mind_thinking':
            updateCouncilMember('mind', event);
            break;
            
        case 'heart_thinking':
            updateCouncilMember('heart', event);
            break;
            
        case 'conscience_thinking':
            updateCouncilMember('conscience', event);
            break;
            
        case 'alternatives_generated':
            if (event.data.alternatives && event.data.alternatives.length > 0) {
                showAlternatives(event.data.alternatives);
            }
            break;
            
        case 'verdict_reached':
            showVerdict(event);
            break;
    }
});

socket.on('stats-update', (newStats) => {
    console.log('Stats update:', newStats);
    updateStats(newStats);
});

socket.on('events-cleared', () => {
    console.log('Events cleared');
    elements.timeline.innerHTML = `
        <div class="timeline-item welcome">
            <span class="time">--:--:--</span>
            <span class="event">Events cleared</span>
        </div>
    `;
    elements.currentCommand.textContent = 'Waiting for command...';
    updateRiskMeter('SAFE');
    elements.alternativesPanel.style.display = 'none';
    elements.verdictPanel.style.display = 'none';
});

// Clear events button
elements.clearEvents.addEventListener('click', () => {
    if (confirm('Clear all events?')) {
        socket.emit('clear-events');
    }
});

// Add bounce animation
const style = document.createElement('style');
style.textContent = `
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);

// Request initial stats
socket.emit('request-stats');