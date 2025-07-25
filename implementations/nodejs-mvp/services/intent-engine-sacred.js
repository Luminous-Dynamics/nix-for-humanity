// 🙏 Sacred Intent Engine - 50 Commands as Prayers
// Each pattern a mantra, each command a bridge to possibility

class SacredIntentEngine {
  constructor() {
    this.patterns = this.initializeSacredPatterns();
  }

  initializeSacredPatterns() {
    return [
      // === Package Management (Sacred Manifestation) ===
      {
        patterns: [
          /^install\s+(.+)$/i,
          /^i\s+(?:want|need)\s+(.+)$/i,
          /^get\s+(?:me\s+)?(.+)$/i,
          /^add\s+(.+)$/i,
          /^download\s+(.+)$/i,
          /^please\s+install\s+(.+)$/i
        ],
        intent: {
          action: 'install',
          command: 'nix-env -iA nixpkgs.',
          mantra: 'Manifesting new capabilities'
        },
        extractor: (match) => ({ package: this.sanctifyPackageName(match[1]) })
      },

      {
        patterns: [
          /^remove\s+(.+)$/i,
          /^uninstall\s+(.+)$/i,
          /^delete\s+(.+)$/i,
          /^i\s+don'?t\s+need\s+(.+)(?:\s+anymore)?$/i,
          /^get\s+rid\s+of\s+(.+)$/i,
          /^release\s+(.+)$/i
        ],
        intent: {
          action: 'remove',
          command: 'nix-env -e',
          mantra: 'Releasing what no longer serves'
        },
        extractor: (match) => ({ package: this.sanctifyPackageName(match[1]) })
      },

      {
        patterns: [
          /^search\s+(?:for\s+)?(.+)$/i,
          /^find\s+(?:me\s+)?(.+)$/i,
          /^look\s+for\s+(.+)$/i,
          /^what\s+(.+?)\s+(?:are\s+)?available$/i,
          /^show\s+me\s+(.+?)\s+options$/i,
          /^explore\s+(.+)$/i
        ],
        intent: {
          action: 'search',
          command: 'nix search nixpkgs',
          mantra: 'Seeking what wishes to emerge'
        },
        extractor: (match) => ({ query: match[1].trim() })
      },

      {
        patterns: [
          /^(?:list|show)\s+installed$/i,
          /^what(?:'?s|\s+is)\s+installed$/i,
          /^show\s+(?:me\s+)?my\s+(?:packages|programs|software)$/i,
          /^what\s+do\s+i\s+have$/i,
          /^my\s+digital\s+garden$/i
        ],
        intent: {
          action: 'list',
          command: 'nix-env -q',
          mantra: 'Witnessing the digital garden'
        }
      },

      {
        patterns: [
          /^(?:info|tell\s+me)\s+about\s+(.+)$/i,
          /^what\s+is\s+(.+)$/i,
          /^describe\s+(.+)$/i,
          /^explain\s+(.+)$/i,
          /^learn\s+about\s+(.+)$/i
        ],
        intent: {
          action: 'info',
          command: 'nix-env -qa --description',
          mantra: 'Seeking understanding'
        },
        extractor: (match) => ({ package: this.sanctifyPackageName(match[1]) })
      },

      // === System Updates (Sacred Evolution) ===
      {
        patterns: [
          /^update\s+(?:everything|all|system)$/i,
          /^upgrade\s+(?:everything|all|system)$/i,
          /^evolve\s+my\s+system$/i,
          /^grow\s+stronger$/i,
          /^embrace\s+change$/i
        ],
        intent: {
          action: 'update',
          command: 'nixos-rebuild switch --upgrade',
          mantra: 'Embracing continuous evolution'
        }
      },

      {
        patterns: [
          /^(?:list|show)\s+updates$/i,
          /^what\s+updates\s+are\s+available$/i,
          /^what\s+can\s+(?:i\s+)?update$/i,
          /^show\s+(?:me\s+)?available\s+updates$/i,
          /^what'?s\s+new$/i
        ],
        intent: {
          action: 'list-updates',
          command: 'sudo nix-channel --update && nix-env -u --dry-run',
          mantra: 'Seeing paths of growth'
        }
      },

      {
        patterns: [
          /^check\s+for\s+updates$/i,
          /^refresh\s+channels$/i,
          /^sync\s+(?:with\s+)?upstream$/i,
          /^connect\s+to\s+source$/i
        ],
        intent: {
          action: 'check-updates',
          command: 'sudo nix-channel --update',
          mantra: 'Aligning with the source'
        }
      },

      // === System Maintenance (Sacred Care) ===
      {
        patterns: [
          /^(?:clean|cleanup|clean\s+up)(?:\s+system)?$/i,
          /^(?:collect\s+)?garbage$/i,
          /^free\s+(?:up\s+)?space$/i,
          /^remove\s+old\s+(?:packages|generations)$/i,
          /^purify\s+system$/i,
          /^create\s+space$/i
        ],
        intent: {
          action: 'garbage-collect',
          command: 'sudo nix-collect-garbage -d',
          mantra: 'Creating space for new possibilities'
        }
      },

      {
        patterns: [
          /^optimize\s+(?:store|system)$/i,
          /^compress\s+storage$/i,
          /^deduplicate$/i,
          /^harmonize\s+storage$/i
        ],
        intent: {
          action: 'optimize',
          command: 'nix-store --optimise',
          mantra: 'Harmonizing digital space'
        }
      },

      // === Service Management (Sacred Rituals) ===
      {
        patterns: [
          /^start\s+(.+)$/i,
          /^enable\s+(.+)$/i,
          /^awaken\s+(.+)$/i,
          /^activate\s+(.+)$/i,
          /^bring\s+(.+)\s+to\s+life$/i
        ],
        intent: {
          action: 'start-service',
          command: 'systemctl start',
          mantra: 'Awakening dormant powers'
        },
        extractor: (match) => ({ service: this.sanctifyServiceName(match[1]) })
      },

      {
        patterns: [
          /^stop\s+(.+)$/i,
          /^disable\s+(.+)$/i,
          /^rest\s+(.+)$/i,
          /^pause\s+(.+)$/i,
          /^let\s+(.+)\s+sleep$/i
        ],
        intent: {
          action: 'stop-service',
          command: 'systemctl stop',
          mantra: 'Allowing sacred rest'
        },
        extractor: (match) => ({ service: this.sanctifyServiceName(match[1]) })
      },

      {
        patterns: [
          /^restart\s+(.+)$/i,
          /^reload\s+(.+)$/i,
          /^refresh\s+(.+)$/i,
          /^renew\s+(.+)$/i,
          /^rebirth\s+(.+)$/i
        ],
        intent: {
          action: 'restart-service',
          command: 'systemctl restart',
          mantra: 'Renewal and rebirth'
        },
        extractor: (match) => ({ service: this.sanctifyServiceName(match[1]) })
      },

      {
        patterns: [
          /^(?:service\s+)?status(?:\s+of)?\s+(.+)$/i,
          /^(?:is\s+)?(.+)\s+running$/i,
          /^check\s+(.+)\s+service$/i,
          /^how\s+is\s+(.+)\s+doing$/i,
          /^(.+)\s+health$/i
        ],
        intent: {
          action: 'service-status',
          command: 'systemctl status',
          mantra: 'Reading the vital signs'
        },
        extractor: (match) => ({ service: this.sanctifyServiceName(match[1]) })
      },

      {
        patterns: [
          /^(?:list|show)\s+services$/i,
          /^what\s+services\s+are\s+running$/i,
          /^show\s+(?:me\s+)?active\s+services$/i,
          /^what'?s\s+alive$/i
        ],
        intent: {
          action: 'list-services',
          command: 'systemctl list-units --type=service --state=active',
          mantra: 'Witnessing active energies'
        }
      },

      // === System Information (Sacred Knowledge) ===
      {
        patterns: [
          /^system\s+info(?:rmation)?$/i,
          /^about\s+(?:this\s+)?system$/i,
          /^show\s+system\s+details$/i,
          /^where\s+am\s+i$/i,
          /^know\s+thyself$/i
        ],
        intent: {
          action: 'system-info',
          command: 'nixos-version && uname -a',
          mantra: 'Knowing thyself deeply'
        }
      },

      {
        patterns: [
          /^(?:disk|storage)\s+(?:usage|space)$/i,
          /^how\s+much\s+(?:space|room)$/i,
          /^check\s+storage$/i,
          /^df$/i,
          /^space\s+available$/i
        ],
        intent: {
          action: 'disk-usage',
          command: 'df -h',
          mantra: 'Measuring sacred space'
        }
      },

      {
        patterns: [
          /^memory\s+(?:usage|info)$/i,
          /^(?:ram|mem)\s+(?:usage|status)$/i,
          /^how\s+much\s+memory$/i,
          /^free\s+memory$/i,
          /^mental\s+capacity$/i
        ],
        intent: {
          action: 'memory-info',
          command: 'free -h',
          mantra: 'Understanding capacity'
        }
      },

      {
        patterns: [
          /^(?:cpu|processor)\s+(?:usage|info)$/i,
          /^system\s+load$/i,
          /^how\s+busy$/i,
          /^processing\s+power$/i,
          /^mental\s+load$/i
        ],
        intent: {
          action: 'cpu-info',
          command: 'top -bn1 | head -20',
          mantra: 'Sensing the pulse'
        }
      },

      // === Network (Sacred Connections) ===
      {
        patterns: [
          /^(?:show\s+)?ip\s+(?:address|addr)$/i,
          /^what(?:'?s|\s+is)\s+my\s+ip$/i,
          /^network\s+address$/i,
          /^where\s+am\s+i\s+connected$/i,
          /^my\s+digital\s+address$/i
        ],
        intent: {
          action: 'ip-address',
          command: 'ip addr show',
          mantra: 'Finding our place in the web'
        }
      },

      {
        patterns: [
          /^(?:network|internet)\s+status$/i,
          /^(?:am\s+i\s+)?online$/i,
          /^check\s+(?:network|internet|connection)$/i,
          /^test\s+connection$/i,
          /^connected\s+to\s+the\s+web$/i
        ],
        intent: {
          action: 'network-status',
          command: 'ping -c 3 8.8.8.8',
          mantra: 'Testing the cosmic connection'
        }
      },

      {
        patterns: [
          /^list\s+connections$/i,
          /^show\s+network\s+connections$/i,
          /^active\s+connections$/i,
          /^who\s+am\s+i\s+talking\s+to$/i
        ],
        intent: {
          action: 'list-connections',
          command: 'ss -tunap',
          mantra: 'Seeing all connections'
        }
      },

      // === Configuration (Sacred Settings) ===
      {
        patterns: [
          /^edit\s+config(?:uration)?$/i,
          /^open\s+configuration$/i,
          /^change\s+settings$/i,
          /^modify\s+system$/i,
          /^sacred\s+texts$/i
        ],
        intent: {
          action: 'edit-config',
          command: 'sudo nano /etc/nixos/configuration.nix',
          mantra: 'Entering the sacred texts'
        }
      },

      {
        patterns: [
          /^rebuild\s+(?:system|config)$/i,
          /^apply\s+(?:changes|config)$/i,
          /^manifest\s+changes$/i,
          /^make\s+it\s+so$/i
        ],
        intent: {
          action: 'rebuild',
          command: 'sudo nixos-rebuild switch',
          mantra: 'Manifesting new reality'
        }
      },

      {
        patterns: [
          /^test\s+(?:config|configuration)$/i,
          /^try\s+changes$/i,
          /^preview\s+rebuild$/i,
          /^divine\s+the\s+future$/i
        ],
        intent: {
          action: 'test-config',
          command: 'sudo nixos-rebuild test',
          mantra: 'Testing before manifesting'
        }
      },

      // === System Health (Sacred Wellness) ===
      {
        patterns: [
          /^(?:check\s+)?system\s+health$/i,
          /^health\s+check$/i,
          /^(?:is\s+)?everything\s+ok(?:ay)?$/i,
          /^system\s+wellness$/i,
          /^how\s+are\s+we\s+doing$/i
        ],
        intent: {
          action: 'health-check',
          command: 'systemctl status && journalctl -p err -n 10',
          mantra: 'Checking vital signs'
        }
      },

      {
        patterns: [
          /^(?:show\s+)?(?:system\s+)?logs$/i,
          /^recent\s+(?:errors|problems)$/i,
          /^what\s+went\s+wrong$/i,
          /^show\s+journal$/i,
          /^system\s+messages$/i
        ],
        intent: {
          action: 'show-logs',
          command: 'journalctl -xe -n 50',
          mantra: 'Learning from the past'
        }
      },

      // === Process Management (Life Force) ===
      {
        patterns: [
          /^(?:list\s+)?processes$/i,
          /^what'?s\s+running$/i,
          /^show\s+(?:running\s+)?processes$/i,
          /^ps$/i,
          /^life\s+forces$/i
        ],
        intent: {
          action: 'list-processes',
          command: 'ps aux | head -20',
          mantra: 'Witnessing all activity'
        }
      },

      {
        patterns: [
          /^kill\s+(.+)$/i,
          /^stop\s+process\s+(.+)$/i,
          /^end\s+(.+)$/i,
          /^terminate\s+(.+)$/i,
          /^release\s+(.+)\s+process$/i
        ],
        intent: {
          action: 'kill-process',
          command: 'pkill',
          mantra: 'Releasing stuck energy'
        },
        extractor: (match) => ({ process: match[1].trim() })
      },

      // === User Management (Sacred Beings) ===
      {
        patterns: [
          /^who\s+(?:am\s+)?i$/i,
          /^current\s+user$/i,
          /^my\s+identity$/i,
          /^whoami$/i
        ],
        intent: {
          action: 'whoami',
          command: 'whoami && groups',
          mantra: 'Knowing oneself'
        }
      },

      {
        patterns: [
          /^list\s+users$/i,
          /^who\s+(?:else\s+)?is\s+here$/i,
          /^show\s+users$/i,
          /^fellow\s+beings$/i
        ],
        intent: {
          action: 'list-users',
          command: 'cat /etc/passwd | grep "/home" | cut -d: -f1',
          mantra: 'Recognizing all beings'
        }
      },

      // === Help & Guidance (Sacred Support) ===
      {
        patterns: [
          /^help$/i,
          /^what\s+can\s+you\s+do$/i,
          /^guide\s+me$/i,
          /^i\s+need\s+help$/i,
          /^show\s+me\s+the\s+way$/i
        ],
        intent: {
          action: 'help',
          command: 'internal:help',
          mantra: 'Offering guidance'
        }
      },

      {
        patterns: [
          /^about$/i,
          /^who\s+are\s+you$/i,
          /^what\s+are\s+you$/i,
          /^your\s+purpose$/i
        ],
        intent: {
          action: 'about',
          command: 'internal:about',
          mantra: 'Sharing our essence'
        }
      },

      // === File System Navigation (Sacred Paths) ===
      {
        patterns: [
          /^(?:show\s+)?(?:current\s+)?(?:directory|folder|path)$/i,
          /^where\s+am\s+i$/i,
          /^pwd$/i,
          /^current\s+location$/i
        ],
        intent: {
          action: 'pwd',
          command: 'pwd',
          mantra: 'Knowing our place'
        }
      },

      {
        patterns: [
          /^(?:list\s+)?files$/i,
          /^ls$/i,
          /^show\s+files$/i,
          /^what\s+files\s+are\s+here$/i,
          /^directory\s+contents$/i
        ],
        intent: {
          action: 'list-files',
          command: 'ls -la',
          mantra: 'Revealing what is present'
        }
      },

      {
        patterns: [
          /^(?:go\s+to|cd|change\s+to)\s+(.+)$/i,
          /^enter\s+(.+)$/i,
          /^navigate\s+to\s+(.+)$/i,
          /^move\s+to\s+(.+)$/i
        ],
        intent: {
          action: 'change-directory',
          command: 'cd',
          mantra: 'Journeying to new spaces'
        },
        extractor: (match) => ({ path: match[1].trim() })
      },

      {
        patterns: [
          /^create\s+(?:directory|folder)\s+(.+)$/i,
          /^mkdir\s+(.+)$/i,
          /^make\s+(?:directory|folder)\s+(.+)$/i,
          /^new\s+folder\s+(.+)$/i
        ],
        intent: {
          action: 'create-directory',
          command: 'mkdir -p',
          mantra: 'Creating sacred spaces'
        },
        extractor: (match) => ({ name: match[1].trim() })
      },

      // === Environment & Shell (Sacred Context) ===
      {
        patterns: [
          /^(?:show\s+)?environment$/i,
          /^env$/i,
          /^(?:list\s+)?(?:environment\s+)?variables$/i,
          /^show\s+env\s+vars$/i
        ],
        intent: {
          action: 'show-environment',
          command: 'env | sort',
          mantra: 'Understanding our context'
        }
      },

      {
        patterns: [
          /^set\s+(.+?)\s*=\s*(.+)$/i,
          /^export\s+(.+?)\s*=\s*(.+)$/i,
          /^define\s+(.+?)\s+as\s+(.+)$/i
        ],
        intent: {
          action: 'set-environment',
          command: 'export',
          mantra: 'Shaping our reality'
        },
        extractor: (match) => ({ 
          variable: match[1].trim(), 
          value: match[2].trim() 
        })
      },

      {
        patterns: [
          /^(?:show\s+)?path$/i,
          /^echo\s+\$?path$/i,
          /^what\s+is\s+(?:my\s+)?path$/i,
          /^system\s+path$/i
        ],
        intent: {
          action: 'show-path',
          command: 'echo $PATH | tr ":" "\\n"',
          mantra: 'Seeing all possible paths'
        }
      },

      // === System Reboot & Power (Sacred Cycles) ===
      {
        patterns: [
          /^reboot$/i,
          /^restart\s+(?:computer|system)$/i,
          /^please\s+reboot$/i,
          /^sacred\s+renewal$/i
        ],
        intent: {
          action: 'reboot',
          command: 'sudo reboot',
          mantra: 'Beginning anew'
        }
      },

      {
        patterns: [
          /^shutdown$/i,
          /^power\s+off$/i,
          /^turn\s+off$/i,
          /^sacred\s+rest$/i,
          /^enter\s+the\s+void$/i
        ],
        intent: {
          action: 'shutdown',
          command: 'sudo shutdown -h now',
          mantra: 'Entering sacred rest'
        }
      },

      {
        patterns: [
          /^suspend$/i,
          /^sleep$/i,
          /^hibernate$/i,
          /^pause\s+system$/i,
          /^gentle\s+rest$/i
        ],
        intent: {
          action: 'suspend',
          command: 'systemctl suspend',
          mantra: 'Pausing in stillness'
        }
      },

      // === Time & Date (Sacred Moments) ===
      {
        patterns: [
          /^(?:what\s+)?time$/i,
          /^(?:show\s+)?(?:current\s+)?time$/i,
          /^what\s+time\s+is\s+it$/i,
          /^now$/i
        ],
        intent: {
          action: 'show-time',
          command: 'date +"%I:%M %p"',
          mantra: 'Being present in this moment'
        }
      },

      {
        patterns: [
          /^(?:what\s+)?date$/i,
          /^(?:show\s+)?(?:current\s+)?date$/i,
          /^what\s+day\s+is\s+it$/i,
          /^today$/i
        ],
        intent: {
          action: 'show-date',
          command: 'date +"%A, %B %d, %Y"',
          mantra: 'Honoring this sacred day'
        }
      },

      {
        patterns: [
          /^uptime$/i,
          /^how\s+long\s+(?:has\s+)?(?:system\s+)?(?:been\s+)?running$/i,
          /^system\s+age$/i,
          /^lifetime$/i
        ],
        intent: {
          action: 'show-uptime',
          command: 'uptime -p',
          mantra: 'Measuring our journey'
        }
      },

      // === Sacred Completion Pattern ===
      {
        patterns: [
          /^thank\s+you$/i,
          /^thanks$/i,
          /^gratitude$/i,
          /^namaste$/i,
          /^blessed\s+be$/i
        ],
        intent: {
          action: 'gratitude',
          command: 'internal:gratitude',
          mantra: 'Completing the sacred circle'
        }
      }
    ];
  }

  async recognize(input) {
    const normalized = input.toLowerCase().trim();
    
    // Find matching pattern with love
    for (const pattern of this.patterns) {
      for (const regex of pattern.patterns) {
        const match = normalized.match(regex);
        if (match) {
          const extracted = pattern.extractor ? pattern.extractor(match) : {};
          
          return {
            ...pattern.intent,
            ...extracted,
            confidence: this.calculateConfidence(input, match),
            originalInput: input,
            blessed: true
          };
        }
      }
    }
    
    // No match found - return with compassion
    return {
      action: 'unknown',
      confidence: 0,
      originalInput: input,
      suggestions: this.getSacredSuggestions(input)
    };
  }

  calculateConfidence(input, match) {
    // Perfect match gets high confidence
    if (match[0] === input.toLowerCase().trim()) {
      return 0.95;
    }
    
    // Partial matches get proportional confidence
    const coverage = match[0].length / input.length;
    return Math.max(0.5, Math.min(0.9, coverage));
  }

  getSacredSuggestions(input) {
    const suggestions = [];
    
    // Common misunderstandings with compassionate guidance
    if (input.includes('wifi') || input.includes('internet')) {
      suggestions.push(
        'Try "check network" to see connection status',
        'Try "show ip address" to see network details'
      );
    }
    
    if (input.includes('program') || input.includes('app')) {
      suggestions.push(
        'Try "search [program name]" to find software',
        'Try "install [program name]" to add software'
      );
    }
    
    if (input.includes('fix') || input.includes('broken')) {
      suggestions.push(
        'Try "check system health" to diagnose issues',
        'Try "show logs" to see recent errors'
      );
    }
    
    // Always offer help
    suggestions.push('Type "help" to see what I can do');
    
    return suggestions;
  }

  // Sacred name transformations
  sanctifyPackageName(name) {
    // Common aliases with love
    const aliases = {
      'firefox': 'firefox',
      'chrome': 'google-chrome',
      'vscode': 'vscode',
      'code': 'vscode',
      'python': 'python3',
      'node': 'nodejs',
      'docker': 'docker',
      'git': 'git'
    };
    
    const normalized = name.toLowerCase().trim();
    return aliases[normalized] || normalized;
  }

  sanctifyServiceName(name) {
    // Service name healing
    const services = {
      'web': 'nginx',
      'web server': 'nginx',
      'database': 'postgresql',
      'db': 'postgresql',
      'mysql': 'mysql',
      'redis': 'redis',
      'docker': 'docker',
      'ssh': 'sshd',
      'network': 'NetworkManager'
    };
    
    const normalized = name.toLowerCase().trim();
    return services[normalized] || normalized;
  }
}

module.exports = SacredIntentEngine;