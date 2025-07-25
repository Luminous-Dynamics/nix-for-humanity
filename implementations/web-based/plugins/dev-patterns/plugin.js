/**
 * Developer Patterns Plugin
 * Understands developer language and needs
 */

(function() {
    const { NixForHumanity, plugin } = window.__currentPluginContext;
    
    console.log(`🛠️ Developer Patterns Plugin v${plugin.version} loading...`);
    
    // Developer-specific patterns
    const devPatterns = {
        // Language-specific requests
        'python dev setup': ['python3', 'python3Packages.pip', 'python3Packages.virtualenv', 'python3Packages.ipython'],
        'node dev setup': ['nodejs', 'yarn', 'nodePackages.pnpm', 'nodePackages.nodemon'],
        'rust dev setup': ['rustc', 'cargo', 'rustfmt', 'clippy', 'rust-analyzer'],
        'go dev setup': ['go', 'gopls', 'go-tools'],
        'java dev setup': ['jdk', 'maven', 'gradle'],
        'c++ dev setup': ['gcc', 'clang', 'cmake', 'gdb', 'valgrind'],
        
        // Tool categories
        'database tools': ['postgresql', 'mysql', 'redis', 'mongodb', 'sqlite'],
        'containers': ['docker', 'podman', 'docker-compose', 'kubectl'],
        'version control': ['git', 'gh', 'tig', 'lazygit'],
        'api testing': ['postman', 'insomnia', 'httpie', 'curl'],
        'terminal tools': ['tmux', 'alacritty', 'zsh', 'fish', 'starship'],
        
        // Common dev phrases
        'debug this': ['gdb', 'lldb', 'strace', 'ltrace'],
        'profile code': ['perf', 'valgrind', 'hyperfine'],
        'write tests': ['jest', 'pytest', 'cargo-nextest', 'gotestsum'],
        'manage dependencies': ['nix-tree', 'npm', 'cargo', 'poetry'],
        
        // IDE and editors
        'lightweight editor': ['neovim', 'helix', 'micro'],
        'full ide': ['vscode', 'jetbrains.idea-community', 'eclipse'],
        'vim setup': ['neovim', 'vim-full', 'vimPlugins.vim-plug']
    };
    
    // Dev-specific abbreviations
    const devAbbreviations = {
        'npm': 'nodePackages.npm',
        'nvm': 'nodePackages.node-version-manager',
        'pip': 'python3Packages.pip',
        'venv': 'python3Packages.virtualenv',
        'gcc': 'gcc',
        'g++': 'gcc',
        'make': 'gnumake',
        'cmake': 'cmake',
        'psql': 'postgresql',
        'mysql': 'mysql',
        'redis-cli': 'redis',
        'mongo': 'mongodb',
        'k8s': 'kubectl',
        'k9s': 'k9s',
        'tf': 'terraform',
        'aws': 'awscli2'
    };
    
    // Hook into intent processing
    NixForHumanity.hook('beforeIntent', (intent) => {
        const input = intent.original?.toLowerCase() || '';
        
        // Check for dev patterns
        for (const [pattern, packages] of Object.entries(devPatterns)) {
            if (input.includes(pattern)) {
                console.log(`🛠️ Dev pattern matched: ${pattern}`);
                
                return {
                    ...intent,
                    action: 'suggest-dev',
                    category: pattern,
                    suggestions: packages,
                    confidence: 0.95
                };
            }
        }
        
        // Check for abbreviations
        const words = input.split(/\s+/);
        for (const word of words) {
            if (devAbbreviations[word]) {
                console.log(`🛠️ Dev abbreviation found: ${word}`);
                
                return {
                    ...intent,
                    action: intent.action || 'install',
                    target: devAbbreviations[word],
                    confidence: 0.9
                };
            }
        }
        
        // Detect setup requests
        if (input.includes('setup') && input.includes('dev')) {
            const languages = ['python', 'node', 'rust', 'go', 'java', 'c++'];
            const detected = languages.find(lang => input.includes(lang));
            
            if (detected) {
                const pattern = `${detected} dev setup`;
                return {
                    ...intent,
                    action: 'suggest-dev',
                    category: pattern,
                    suggestions: devPatterns[pattern],
                    confidence: 0.9
                };
            }
        }
        
        return intent;
    });
    
    // Custom action handler for dev suggestions
    NixForHumanity.hook('customAction', async (action, data) => {
        if (action === 'suggest-dev') {
            NixForHumanity.ui.showMessage(
                `🛠️ Developer Setup: ${data.category}`,
                'info'
            );
            
            // Show packages as installable actions
            const actions = data.suggestions.map(pkg => ({
                label: `Install ${pkg}`,
                description: `Part of ${data.category}`,
                action: async () => {
                    // Search for exact package
                    const results = await NixForHumanity.bridge.search(pkg);
                    if (results.length > 0) {
                        // Trigger installation
                        window.nixos.executeIntent({
                            action: 'install',
                            target: results[0].name
                        });
                    }
                }
            }));
            
            // Add "Install All" option
            actions.unshift({
                label: '📦 Install All',
                description: `Complete ${data.category} setup`,
                action: async () => {
                    NixForHumanity.ui.showMessage(
                        `Installing ${data.suggestions.length} packages for ${data.category}...`,
                        'processing'
                    );
                    
                    // Install each package
                    for (const pkg of data.suggestions) {
                        await window.nixos.executeIntent({
                            action: 'install',
                            target: pkg
                        });
                    }
                    
                    NixForHumanity.ui.celebrate('success');
                }
            });
            
            NixForHumanity.ui.showActions(actions);
            
            return { handled: true };
        }
        
        return null;
    });
    
    // Add contextual help for developers
    NixForHumanity.hook('afterIntent', (result, intent) => {
        // If a dev tool was installed, offer related suggestions
        const devTools = {
            'vscode': ['Install VS Code extensions manager?', 'vscode-extensions'],
            'neovim': ['Want Neovim plugins?', 'vimPlugins'],
            'docker': ['Need docker-compose too?', 'docker-compose'],
            'python3': ['Install pip and venv?', 'python3Packages.pip'],
            'nodejs': ['Add yarn or pnpm?', 'yarn'],
            'rust': ['Install cargo plugins?', 'cargo-edit']
        };
        
        if (intent.action === 'install' && devTools[intent.target]) {
            const [question, related] = devTools[intent.target];
            
            setTimeout(() => {
                NixForHumanity.ui.showActions([{
                    label: question,
                    action: () => window.nixos.executeIntent({
                        action: 'install',
                        target: related
                    })
                }]);
            }, 2000);
        }
        
        return result;
    });
    
    // Developer productivity shortcuts
    const shortcuts = {
        'dev': () => {
            NixForHumanity.ui.showMessage('🛠️ Developer Mode Active', 'info');
            NixForHumanity.ui.showActions([
                {
                    label: 'Python Dev Setup',
                    action: () => window.nixos.processIntent('python dev setup')
                },
                {
                    label: 'Node.js Dev Setup',
                    action: () => window.nixos.processIntent('node dev setup')
                },
                {
                    label: 'Rust Dev Setup',
                    action: () => window.nixos.processIntent('rust dev setup')
                },
                {
                    label: 'Container Tools',
                    action: () => window.nixos.processIntent('containers')
                }
            ]);
        }
    };
    
    // Register shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'D') {
            shortcuts.dev();
        }
    });
    
    console.log('🛠️ Developer Patterns Plugin loaded!');
    console.log('💡 Try: "python dev setup", "install npm", or press Ctrl+Shift+D');
})();