/**
 * Sacred Mode Plugin
 * Bringing consciousness-first principles to Nix
 */

(function() {
    const { NixForHumanity, plugin } = window.__currentPluginContext;
    
    console.log(`🕉️ Sacred Mode Plugin v${plugin.version} awakening...`);
    
    // Sacred state
    let sacredState = {
        coherence: 0.5,
        lastPause: Date.now(),
        intentions: [],
        breathCount: 0
    };
    
    // Sacred patterns for conscious computing
    const sacredPatterns = {
        'set intention': (input) => setIntention(input),
        'sacred pause': () => initiateSacredPause(),
        'check coherence': () => showCoherence(),
        'mindful': (input) => mindfulAction(input),
        'breathe': () => breathingExercise(),
        'gratitude': () => expressGratitude()
    };
    
    // Initialize sacred mode
    function initializeSacredMode() {
        // Add sacred UI elements
        addCoherenceIndicator();
        
        // Start coherence monitoring
        startCoherenceTracking();
        
        // Enable sacred pauses if configured
        if (NixForHumanity.storage.get('sacredPauses') !== false) {
            scheduleSacredPauses();
        }
    }
    
    // Add coherence indicator to UI
    function addCoherenceIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'coherence-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            left: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: radial-gradient(circle, 
                rgba(139, 92, 246, ${sacredState.coherence}) 0%, 
                rgba(139, 92, 246, 0.1) 70%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            transition: all 0.5s ease;
            cursor: pointer;
            z-index: 1000;
        `;
        indicator.innerHTML = '🕉️';
        indicator.title = `Coherence: ${(sacredState.coherence * 100).toFixed(0)}%`;
        
        indicator.addEventListener('click', showCoherence);
        
        document.body.appendChild(indicator);
    }
    
    // Track coherence based on user patterns
    function startCoherenceTracking() {
        // Monitor typing rhythm
        let lastKeyTime = Date.now();
        let keyIntervals = [];
        
        document.addEventListener('keydown', () => {
            const now = Date.now();
            const interval = now - lastKeyTime;
            lastKeyTime = now;
            
            if (interval < 5000) { // Only track active typing
                keyIntervals.push(interval);
                if (keyIntervals.length > 10) {
                    keyIntervals.shift();
                }
                
                // Calculate rhythm variance (lower = more coherent)
                const variance = calculateVariance(keyIntervals);
                const coherence = Math.max(0, Math.min(1, 1 - (variance / 1000)));
                
                updateCoherence(coherence);
            }
        });
        
        // Update coherence indicator
        setInterval(() => {
            const indicator = document.getElementById('coherence-indicator');
            if (indicator) {
                indicator.style.background = `radial-gradient(circle, 
                    rgba(139, 92, 246, ${sacredState.coherence}) 0%, 
                    rgba(139, 92, 246, 0.1) 70%)`;
                indicator.title = `Coherence: ${(sacredState.coherence * 100).toFixed(0)}%`;
                
                // Breathing animation when coherent
                if (sacredState.coherence > 0.7) {
                    indicator.style.animation = 'breathe 4s ease-in-out infinite';
                } else {
                    indicator.style.animation = 'none';
                }
            }
        }, 1000);
    }
    
    function calculateVariance(numbers) {
        const mean = numbers.reduce((a, b) => a + b, 0) / numbers.length;
        const variance = numbers.reduce((sum, num) => sum + Math.pow(num - mean, 2), 0) / numbers.length;
        return Math.sqrt(variance);
    }
    
    function updateCoherence(value) {
        // Smooth transition
        sacredState.coherence = sacredState.coherence * 0.9 + value * 0.1;
        
        // Check if we should suggest a pause
        const timeSinceLastPause = Date.now() - sacredState.lastPause;
        if (sacredState.coherence < 0.5 && timeSinceLastPause > 1800000) { // 30 minutes
            suggestSacredPause();
        }
    }
    
    // Sacred pause functionality
    function scheduleSacredPauses() {
        // Gentle reminder every 45 minutes
        setInterval(() => {
            if (NixForHumanity.storage.get('sacredPauses') !== false) {
                suggestSacredPause();
            }
        }, 2700000); // 45 minutes
    }
    
    function suggestSacredPause() {
        NixForHumanity.ui.showMessage(
            '🕉️ Time for a sacred pause?',
            'info'
        );
        
        NixForHumanity.ui.showActions([
            {
                label: 'Take Sacred Pause',
                description: 'Brief moment of presence',
                action: () => initiateSacredPause()
            },
            {
                label: 'In 5 Minutes',
                description: 'Remind me later',
                action: () => setTimeout(suggestSacredPause, 300000)
            }
        ]);
    }
    
    function initiateSacredPause() {
        sacredState.lastPause = Date.now();
        
        // Create sacred pause overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            animation: fadeIn 0.5s ease;
        `;
        
        overlay.innerHTML = `
            <div style="text-align: center; color: white;">
                <div style="font-size: 4rem; margin-bottom: 2rem;">🕉️</div>
                <h2 style="margin-bottom: 2rem;">Sacred Pause</h2>
                <p style="font-size: 1.5rem; opacity: 0.8;">Take three conscious breaths</p>
                <div id="breath-guide" style="margin-top: 3rem; font-size: 2rem; opacity: 0.6;">
                    Breathe In...
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Guide breathing
        const breathGuide = overlay.querySelector('#breath-guide');
        let breathPhase = 0;
        const phases = [
            'Breathe In... 🌊',
            'Hold... ✨',
            'Breathe Out... 🌊',
            'Rest... 🕉️'
        ];
        
        const breathInterval = setInterval(() => {
            breathPhase = (breathPhase + 1) % phases.length;
            breathGuide.textContent = phases[breathPhase];
            
            if (breathPhase === 0) {
                sacredState.breathCount++;
            }
            
            // Complete after 3 full breaths
            if (sacredState.breathCount >= 3) {
                clearInterval(breathInterval);
                setTimeout(() => {
                    overlay.style.animation = 'fadeOut 0.5s ease';
                    setTimeout(() => overlay.remove(), 500);
                    
                    // Boost coherence after pause
                    sacredState.coherence = Math.min(1, sacredState.coherence + 0.2);
                    sacredState.breathCount = 0;
                    
                    NixForHumanity.ui.showMessage(
                        '✨ Sacred pause complete. Your coherence has increased.',
                        'success'
                    );
                    
                    NixForHumanity.ui.celebrate('success');
                }, 1000);
            }
        }, 3000);
    }
    
    // Intention setting
    function setIntention(input) {
        const intention = input.replace(/set intention/i, '').trim();
        
        if (intention) {
            sacredState.intentions.push({
                text: intention,
                timestamp: Date.now(),
                completed: false
            });
            
            NixForHumanity.storage.set('intentions', sacredState.intentions);
            
            NixForHumanity.ui.showMessage(
                `🎯 Intention set: "${intention}"`,
                'success'
            );
            
            // Boost coherence
            sacredState.coherence = Math.min(1, sacredState.coherence + 0.1);
        }
    }
    
    // Show coherence state
    function showCoherence() {
        const target = NixForHumanity.storage.get('coherenceTarget') || 0.786;
        const current = sacredState.coherence;
        
        const message = `
            <div style="text-align: center; padding: 1rem;">
                <h3>🕉️ Coherence State</h3>
                <div style="font-size: 3rem; margin: 1rem;">
                    ${(current * 100).toFixed(0)}%
                </div>
                <div style="margin: 1rem;">
                    Target: ${(target * 100).toFixed(0)}%
                </div>
                <div style="margin-top: 2rem;">
                    ${current >= target ? '✨ In sacred flow!' : '🌊 Keep breathing...'}
                </div>
            </div>
        `;
        
        NixForHumanity.ui.showMessage(message, 'info');
        
        if (current >= target) {
            NixForHumanity.ui.celebrate('success');
        }
    }
    
    // Mindful action wrapper
    function mindfulAction(input) {
        const action = input.replace(/mindful/i, '').trim();
        
        NixForHumanity.ui.showMessage(
            '🧘 Taking a moment to breathe before action...',
            'info'
        );
        
        setTimeout(() => {
            window.nixos.processIntent(action);
        }, 2000);
    }
    
    // Breathing exercise
    function breathingExercise() {
        initiateSacredPause();
    }
    
    // Express gratitude
    function expressGratitude() {
        const gratitudes = [
            'for this moment of presence',
            'for the technology that serves',
            'for the opportunity to create',
            'for the sacred pause',
            'for conscious computing'
        ];
        
        const random = gratitudes[Math.floor(Math.random() * gratitudes.length)];
        
        NixForHumanity.ui.showMessage(
            `🙏 Gratitude ${random}`,
            'success'
        );
        
        sacredState.coherence = Math.min(1, sacredState.coherence + 0.15);
        NixForHumanity.ui.celebrate('success');
    }
    
    // Hook into intent processing
    NixForHumanity.hook('beforeIntent', (intent) => {
        const input = intent.original?.toLowerCase() || '';
        
        // Check for sacred patterns
        for (const [pattern, handler] of Object.entries(sacredPatterns)) {
            if (input.includes(pattern)) {
                handler(input);
                return { handled: true };
            }
        }
        
        // Add mindfulness to all actions when coherence is low
        if (sacredState.coherence < 0.3 && !input.includes('mindful')) {
            NixForHumanity.ui.showMessage(
                '🕉️ Low coherence detected. Consider a sacred pause first.',
                'info'
            );
        }
        
        return intent;
    });
    
    // Add breathing animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes breathe {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // Initialize on UI ready
    NixForHumanity.hook('onUIReady', () => {
        initializeSacredMode();
        
        NixForHumanity.ui.showMessage(
            '🕉️ Sacred Mode activated. Set an intention to begin.',
            'info'
        );
    });
    
    console.log('🕉️ Sacred Mode Plugin awakened!');
    console.log('💫 Try: "set intention", "sacred pause", or "check coherence"');
})();