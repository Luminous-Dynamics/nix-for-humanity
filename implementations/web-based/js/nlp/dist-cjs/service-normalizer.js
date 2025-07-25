/**
 * Normalize service names from natural language
 */
export function normalizeServiceName(input) {
    const serviceMappings = {
        // Web servers
        'nginx': 'nginx',
        'apache': 'httpd',
        'web server': 'nginx',
        'webserver': 'nginx',
        // Databases
        'mysql': 'mysql',
        'mariadb': 'mariadb',
        'postgres': 'postgresql',
        'postgresql': 'postgresql',
        'database': 'postgresql',
        'mongo': 'mongodb',
        'mongodb': 'mongodb',
        'redis': 'redis',
        // Development
        'docker': 'docker',
        'docker daemon': 'docker',
        'git': 'git-daemon',
        // System services
        'network': 'NetworkManager',
        'networking': 'NetworkManager',
        'wifi': 'NetworkManager',
        'internet': 'NetworkManager',
        'sound': 'pulseaudio',
        'audio': 'pulseaudio',
        'bluetooth': 'bluetooth',
        'ssh': 'sshd',
        'firewall': 'firewalld',
        'cups': 'cups',
        'printing': 'cups',
        'printer': 'cups',
        // Desktop services
        'display manager': 'lightdm',
        'login screen': 'lightdm',
        'desktop': 'lightdm',
        // Other common services
        'cron': 'crond',
        'scheduler': 'crond',
        'ftp': 'vsftpd',
        'mail': 'postfix',
        'email': 'postfix'
    };
    const normalized = input.toLowerCase().trim();
    // Check exact matches
    if (serviceMappings[normalized]) {
        return serviceMappings[normalized];
    }
    // Check if input contains any mapping keys
    for (const [key, value] of Object.entries(serviceMappings)) {
        if (normalized.includes(key)) {
            return value;
        }
    }
    // Return cleaned input as service name
    return normalized.replace(/[^a-z0-9\-_]/g, '');
}
//# sourceMappingURL=service-normalizer.js.map