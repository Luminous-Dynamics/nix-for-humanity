// Smart Suggestions Engine
// Learns from user patterns and provides intelligent recommendations

class SmartSuggestionsEngine {
    constructor() {
        this.patterns = this.loadPatterns();
        this.sessionHistory = [];
        this.commonPackages = {
            development: ['git', 'vim', 'emacs', 'tmux', 'htop', 'gcc', 'make', 'nodejs', 'python3'],
            containers: ['docker', 'podman', 'docker-compose', 'kubernetes'],
            multimedia: ['ffmpeg', 'vlc', 'mpv', 'obs-studio', 'audacity'],
            networking: ['wireshark', 'nmap', 'netcat', 'curl', 'wget', 'openssh'],
            security: ['gnupg', 'pass', 'keepassxc', 'age', 'sops']
        };
        
        this.contextualSuggestions = {
            'git': ['gh', 'tig', 'lazygit', 'git-lfs'],
            'docker': ['docker-compose', 'lazydocker', 'ctop'],
            'vim': ['neovim', 'fzf', 'ripgrep', 'tmux'],
            'python3': ['python3-pip', 'ipython', 'jupyter', 'poetry'],
            'nodejs': ['yarn', 'pnpm', 'nvm', 'deno']
        };
        
        this.timeSuggestions = this.initializeTimeSuggestions();
    }

    loadPatterns() {
        try {
            const stored = localStorage.getItem('nixos-gui-patterns');
            return stored ? JSON.parse(stored) : {
                searchHistory: [],
                installHistory: [],
                configPatterns: [],
                timePatterns: {},
                frequencyMap: {}
            };
        } catch (error) {
            console.error('Failed to load patterns:', error);
            return this.getDefaultPatterns();
        }
    }

    getDefaultPatterns() {
        return {
            searchHistory: [],
            installHistory: [],
            configPatterns: [],
            timePatterns: {},
            frequencyMap: {}
        };
    }

    savePatterns() {
        try {
            localStorage.setItem('nixos-gui-patterns', JSON.stringify(this.patterns));
        } catch (error) {
            console.error('Failed to save patterns:', error);
        }
    }

    initializeTimeSuggestions() {
        const hour = new Date().getHours();
        const dayOfWeek = new Date().getDay();
        
        return {
            morning: (hour >= 6 && hour < 12),
            afternoon: (hour >= 12 && hour < 17),
            evening: (hour >= 17 && hour < 22),
            night: (hour >= 22 || hour < 6),
            weekday: (dayOfWeek >= 1 && dayOfWeek <= 5),
            weekend: (dayOfWeek === 0 || dayOfWeek === 6)
        };
    }

    // Track user actions for pattern learning
    trackAction(action, data) {
        const timestamp = Date.now();
        const hour = new Date().getHours();
        const dayOfWeek = new Date().getDay();
        
        const actionRecord = {
            action,
            data,
            timestamp,
            hour,
            dayOfWeek,
            context: this.getCurrentContext()
        };
        
        // Update session history
        this.sessionHistory.push(actionRecord);
        
        // Update patterns based on action type
        switch (action) {
            case 'search':
                this.updateSearchPatterns(data.query);
                break;
            case 'install':
                this.updateInstallPatterns(data.package);
                break;
            case 'config':
                this.updateConfigPatterns(data.change);
                break;
        }
        
        // Save patterns
        this.savePatterns();
        
        // Generate new suggestions
        this.generateSuggestions();
    }

    updateSearchPatterns(query) {
        // Add to search history
        this.patterns.searchHistory.unshift(query);
        this.patterns.searchHistory = this.patterns.searchHistory.slice(0, 100);
        
        // Update frequency map
        this.patterns.frequencyMap[query] = (this.patterns.frequencyMap[query] || 0) + 1;
    }

    updateInstallPatterns(packageName) {
        // Add to install history
        this.patterns.installHistory.unshift({
            package: packageName,
            timestamp: Date.now()
        });
        this.patterns.installHistory = this.patterns.installHistory.slice(0, 50);
        
        // Track time patterns
        const hour = new Date().getHours();
        if (!this.patterns.timePatterns[hour]) {
            this.patterns.timePatterns[hour] = {};
        }
        this.patterns.timePatterns[hour][packageName] = 
            (this.patterns.timePatterns[hour][packageName] || 0) + 1;
    }

    updateConfigPatterns(change) {
        this.patterns.configPatterns.unshift({
            change,
            timestamp: Date.now()
        });
        this.patterns.configPatterns = this.patterns.configPatterns.slice(0, 30);
    }

    getCurrentContext() {
        return {
            recentActions: this.sessionHistory.slice(-5),
            timeContext: this.timeSuggestions,
            lastInstalled: this.patterns.installHistory.slice(0, 5)
        };
    }

    // Generate suggestions based on current context
    generateSuggestions() {
        const suggestions = [];
        
        // Time-based suggestions
        suggestions.push(...this.getTimeSuggestions());
        
        // Context-based suggestions
        suggestions.push(...this.getContextualSuggestions());
        
        // Frequency-based suggestions
        suggestions.push(...this.getFrequencySuggestions());
        
        // Pattern-based suggestions
        suggestions.push(...this.getPatternSuggestions());
        
        // Remove duplicates and sort by relevance
        const uniqueSuggestions = this.deduplicateSuggestions(suggestions);
        return this.rankSuggestions(uniqueSuggestions);
    }

    getTimeSuggestions() {
        const suggestions = [];
        const hour = new Date().getHours();
        
        if (this.timeSuggestions.morning && this.hasTimePattern('update', 6, 12)) {
            suggestions.push({
                type: 'action',
                text: 'Good morning! Time for your daily system update?',
                action: 'sudo nixos-rebuild switch',
                confidence: 0.8,
                reason: 'time-pattern'
            });
        }
        
        if (this.timeSuggestions.evening && this.hasTimePattern('backup', 17, 22)) {
            suggestions.push({
                type: 'action',
                text: 'Evening backup reminder',
                action: 'backup-system',
                confidence: 0.7,
                reason: 'time-pattern'
            });
        }
        
        return suggestions;
    }

    getContextualSuggestions() {
        const suggestions = [];
        const recentInstalls = this.patterns.installHistory.slice(0, 3).map(i => i.package);
        
        // Check for related packages
        recentInstalls.forEach(pkg => {
            if (this.contextualSuggestions[pkg]) {
                this.contextualSuggestions[pkg].forEach(related => {
                    if (!recentInstalls.includes(related)) {
                        suggestions.push({
                            type: 'package',
                            text: `Also install ${related}? (commonly used with ${pkg})`,
                            package: related,
                            confidence: 0.7,
                            reason: 'contextual'
                        });
                    }
                });
            }
        });
        
        return suggestions;
    }

    getFrequencySuggestions() {
        const suggestions = [];
        
        // Get top searches
        const topSearches = Object.entries(this.patterns.frequencyMap)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
        
        topSearches.forEach(([query, count]) => {
            if (count > 3) {
                suggestions.push({
                    type: 'search',
                    text: `Quick search: ${query}`,
                    query: query,
                    confidence: Math.min(count / 10, 0.9),
                    reason: 'frequency'
                });
            }
        });
        
        return suggestions;
    }

    getPatternSuggestions() {
        const suggestions = [];
        
        // Analyze sequences
        if (this.sessionHistory.length > 2) {
            const lastTwo = this.sessionHistory.slice(-2);
            
            // Git → GitHub CLI pattern
            if (lastTwo.some(a => a.data && a.data.package === 'git')) {
                suggestions.push({
                    type: 'package',
                    text: 'Install GitHub CLI for better git integration?',
                    package: 'gh',
                    confidence: 0.6,
                    reason: 'sequence-pattern'
                });
            }
        }
        
        return suggestions;
    }

    hasTimePattern(action, startHour, endHour) {
        const relevantHistory = this.patterns.installHistory
            .filter(record => {
                const recordHour = new Date(record.timestamp).getHours();
                return recordHour >= startHour && recordHour < endHour;
            });
        
        return relevantHistory.length > 2;
    }

    deduplicateSuggestions(suggestions) {
        const seen = new Set();
        return suggestions.filter(suggestion => {
            const key = `${suggestion.type}-${suggestion.text}`;
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
        });
    }

    rankSuggestions(suggestions) {
        return suggestions.sort((a, b) => {
            // Sort by confidence first
            if (b.confidence !== a.confidence) {
                return b.confidence - a.confidence;
            }
            
            // Then by reason priority
            const reasonPriority = {
                'time-pattern': 4,
                'contextual': 3,
                'frequency': 2,
                'sequence-pattern': 1
            };
            
            return (reasonPriority[b.reason] || 0) - (reasonPriority[a.reason] || 0);
        }).slice(0, 5); // Return top 5 suggestions
    }

    // Display suggestions in the UI
    displaySuggestions(containerId = 'suggestions-container') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const suggestions = this.generateSuggestions();
        
        if (suggestions.length === 0) {
            container.classList.add('hidden');
            return;
        }
        
        container.classList.remove('hidden');
        container.innerHTML = `
            <div class="suggestions-header">
                <h4>Smart Suggestions</h4>
                <button class="dismiss-btn" onclick="window.smartSuggestions.dismissSuggestions()">×</button>
            </div>
            <div class="suggestions-list">
                ${suggestions.map((s, index) => this.renderSuggestion(s, index)).join('')}
            </div>
        `;
    }

    renderSuggestion(suggestion, index) {
        const icons = {
            'package': '📦',
            'action': '⚡',
            'search': '🔍',
            'config': '⚙️'
        };
        
        return `
            <div class="suggestion-item" data-index="${index}">
                <span class="suggestion-icon">${icons[suggestion.type] || '💡'}</span>
                <span class="suggestion-text">${suggestion.text}</span>
                <button class="suggestion-action" onclick="window.smartSuggestions.acceptSuggestion(${index})">
                    Accept
                </button>
            </div>
        `;
    }

    acceptSuggestion(index) {
        const suggestions = this.generateSuggestions();
        const suggestion = suggestions[index];
        
        if (!suggestion) return;
        
        // Track acceptance
        this.trackAction('accept-suggestion', {
            type: suggestion.type,
            reason: suggestion.reason
        });
        
        // Execute suggestion based on type
        switch (suggestion.type) {
            case 'package':
                if (window.nixosGUI && window.nixosGUI.packageManager) {
                    window.nixosGUI.packageManager.searchPackage(suggestion.package);
                }
                break;
            case 'search':
                document.getElementById('package-search').value = suggestion.query;
                document.getElementById('search-btn').click();
                break;
            case 'action':
                // Handle actions through the appropriate manager
                window.updateStatus(`Executing: ${suggestion.action}`);
                break;
        }
        
        // Hide suggestions after acceptance
        this.dismissSuggestions();
    }

    dismissSuggestions() {
        const container = document.getElementById('suggestions-container');
        if (container) {
            container.classList.add('hidden');
        }
    }
}

// Initialize global instance
window.smartSuggestions = new SmartSuggestionsEngine();