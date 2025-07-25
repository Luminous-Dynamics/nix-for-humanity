/**
 * Help content database for NixOS GUI
 */

export const helpContent = {
  items: [
    // Dashboard Help
    {
      id: 'dashboard-overview',
      category: 'Dashboard',
      title: 'Dashboard Overview',
      content: `
The dashboard provides a quick overview of your NixOS system status.

**Key Information:**
- System uptime and load
- Memory and disk usage
- Active services count
- Recent system events

**Tips:**
- Click on any metric for detailed view
- Drag widgets to rearrange
- Use the refresh button to update data
      `,
      tags: ['dashboard', 'overview', 'home']
    },

    // Package Management
    {
      id: 'package-search',
      category: 'Packages',
      title: 'Searching for Packages',
      content: `
Find and install NixOS packages easily.

**How to search:**
1. Type package name in search box
2. Press Enter or click Search
3. Results show available packages

**Search tips:**
- Use partial names (e.g., "fire" for Firefox)
- Add channel prefix for specific channels
- Use \`*\` for wildcards

**Keyboard shortcut:** \`Ctrl+/\`
      `,
      example: `firefox
python3
nodejs-*`,
      related: ['package-install', 'package-details'],
      tags: ['packages', 'search', 'find']
    },

    {
      id: 'package-install',
      category: 'Packages',
      title: 'Installing Packages',
      content: `
Install packages to your NixOS system.

**Installation process:**
1. Search for the package
2. Click "Install" button
3. Confirm in dialog
4. Wait for installation to complete

**Important notes:**
- Installation modifies your configuration.nix
- Changes are atomic and reversible
- Some packages require system rebuild

**What happens:**
- Package is added to systemPackages
- Dependencies are resolved automatically
- Configuration is validated before applying
      `,
      tooltip: 'Click to install this package',
      related: ['package-search', 'package-remove'],
      tags: ['packages', 'install', 'add']
    },

    {
      id: 'package-remove',
      category: 'Packages',
      title: 'Removing Packages',
      content: `
Remove installed packages from your system.

**How to remove:**
1. Go to "Installed Packages" tab
2. Find the package to remove
3. Click "Remove" button
4. Confirm removal

**Safety features:**
- Dependencies are checked
- System packages are protected
- Can rollback if needed
      `,
      related: ['package-install', 'generation-rollback'],
      tags: ['packages', 'remove', 'uninstall']
    },

    // Configuration Management
    {
      id: 'config-editor',
      category: 'Configuration',
      title: 'Configuration Editor',
      content: `
Edit your NixOS configuration safely.

**Editor features:**
- Syntax highlighting for Nix
- Real-time validation
- Auto-save drafts
- Diff view for changes

**Best practices:**
1. Always validate before applying
2. Make small, incremental changes
3. Use comments to document changes
4. Keep backups of working configs

**Keyboard shortcuts:**
- \`Ctrl+S\`: Save draft
- \`Ctrl+Enter\`: Validate
- \`Ctrl+Shift+Enter\`: Apply changes
      `,
      related: ['config-validate', 'config-apply'],
      tags: ['configuration', 'edit', 'nix']
    },

    {
      id: 'config-validate',
      category: 'Configuration',
      title: 'Validating Configuration',
      content: `
Validate your configuration before applying.

**Validation checks:**
- Syntax errors
- Missing options
- Type mismatches
- Deprecated options

**Understanding results:**
- ✅ Green: Configuration is valid
- ⚠️ Yellow: Warnings (non-critical)
- ❌ Red: Errors (must fix)

**Common errors:**
- Missing semicolons
- Unclosed brackets
- Undefined variables
- Circular dependencies
      `,
      example: `# Missing semicolon
services.nginx.enable = true  # <- needs ;

# Unclosed bracket
environment.systemPackages = with pkgs; [
  firefox
  git
# <- missing ]`,
      related: ['config-editor', 'config-apply'],
      tags: ['configuration', 'validate', 'check']
    },

    // Service Management
    {
      id: 'service-control',
      category: 'Services',
      title: 'Controlling Services',
      content: `
Manage systemd services on your NixOS system.

**Service actions:**
- **Start**: Begin running the service
- **Stop**: Stop the running service
- **Restart**: Stop and start again
- **Reload**: Reload configuration without stopping

**Service states:**
- 🟢 Active (running)
- 🔴 Inactive (stopped)
- 🟡 Activating/Deactivating
- ⚠️ Failed

**Tips:**
- Some services require sudo privileges
- Check logs if service fails to start
- Enable/disable controls persistence across reboots
      `,
      related: ['service-logs', 'service-enable'],
      tags: ['services', 'systemd', 'control']
    },

    {
      id: 'service-logs',
      category: 'Services',
      title: 'Viewing Service Logs',
      content: `
Monitor service logs for debugging and monitoring.

**Log features:**
- Real-time log streaming
- Filter by log level
- Search within logs
- Export logs

**Log levels:**
- **Error**: Critical problems
- **Warning**: Potential issues
- **Info**: General information
- **Debug**: Detailed debugging

**Keyboard shortcuts:**
- \`F\`: Follow mode (real-time)
- \`/\`: Search in logs
- \`G\`: Go to end
- \`g\`: Go to beginning
      `,
      related: ['service-control'],
      tags: ['services', 'logs', 'debugging']
    },

    // Generation Management
    {
      id: 'generation-overview',
      category: 'Generations',
      title: 'Understanding Generations',
      content: `
NixOS generations are snapshots of your system configuration.

**What are generations?**
- Each configuration change creates a new generation
- Previous generations are preserved
- Can boot into any previous generation
- Atomic upgrades and rollbacks

**Generation info shows:**
- Generation number
- Date created
- Configuration changes
- Kernel version
- Package differences

**Why use generations?**
- Safe experimentation
- Easy recovery from bad configs
- Track system history
      `,
      related: ['generation-switch', 'generation-rollback'],
      tags: ['generations', 'history', 'snapshots']
    },

    {
      id: 'generation-switch',
      category: 'Generations',
      title: 'Switching Generations',
      content: `
Switch between different system generations.

**How to switch:**
1. Select target generation
2. Click "Switch to this generation"
3. Confirm the switch
4. System activates new generation

**Switch options:**
- **Switch**: Change current runtime
- **Boot**: Set as default for next boot
- **Test**: Try without making permanent

**Warning:**
Switching generations changes your entire system state,
including installed packages and configuration.
      `,
      related: ['generation-overview', 'generation-compare'],
      tags: ['generations', 'switch', 'rollback']
    },

    // Troubleshooting
    {
      id: 'troubleshoot-build-error',
      category: 'Troubleshooting',
      title: 'Build Errors',
      content: `
How to resolve NixOS build errors.

**Common causes:**
1. **Syntax errors**: Check configuration.nix
2. **Network issues**: Package downloads failing
3. **Disk space**: Not enough space in /nix/store
4. **Conflicts**: Package version conflicts

**Debugging steps:**
1. Read the full error message
2. Check recent configuration changes
3. Try building with \`--show-trace\`
4. Search NixOS discourse for similar errors

**Quick fixes:**
- Rollback to previous generation
- Clear Nix store garbage: \`nix-collect-garbage -d\`
- Update channels: \`nix-channel --update\`
      `,
      related: ['generation-rollback', 'config-validate'],
      tags: ['troubleshooting', 'errors', 'build']
    },

    // Security
    {
      id: 'security-permissions',
      category: 'Security',
      title: 'Understanding Permissions',
      content: `
NixOS GUI uses system permissions for security.

**Permission levels:**
- **View**: Read system state
- **Manage**: Start/stop services
- **Configure**: Edit configuration
- **Admin**: All permissions

**How it works:**
- Uses Linux groups (wheel, nixos-gui)
- Polkit for privilege escalation
- Audit logging for all actions

**Best practices:**
- Only grant necessary permissions
- Review audit logs regularly
- Use strong passwords
      `,
      related: ['security-audit'],
      tags: ['security', 'permissions', 'access']
    }
  ],

  tours: [
    {
      id: 'first-time',
      name: 'First Time Setup',
      description: 'Get started with NixOS GUI',
      steps: [
        {
          selector: '.dashboard',
          title: 'Welcome to NixOS GUI!',
          content: 'This is your dashboard. It shows system status at a glance.'
        },
        {
          selector: '[data-tab="packages"]',
          title: 'Package Management',
          content: 'Click here to search and install NixOS packages.'
        },
        {
          selector: '[data-tab="configuration"]',
          title: 'Configuration Editor',
          content: 'Edit your NixOS configuration with syntax highlighting and validation.'
        },
        {
          selector: '[data-tab="services"]',
          title: 'Service Management',
          content: 'Control system services, view status and logs.'
        },
        {
          selector: '[data-tab="generations"]',
          title: 'Generation History',
          content: 'View and switch between system generations for easy rollback.'
        },
        {
          selector: '.help-button',
          title: 'Getting Help',
          content: 'Click the help button anytime for assistance. Press F1 for quick help!'
        }
      ]
    },

    {
      id: 'package-workflow',
      name: 'Installing Your First Package',
      description: 'Learn how to find and install packages',
      steps: [
        {
          selector: '[data-tab="packages"]',
          title: 'Open Package Manager',
          content: 'Click on the Packages tab to start.'
        },
        {
          selector: '.package-search input',
          title: 'Search for a Package',
          content: 'Type "firefox" in the search box to find the Firefox browser.'
        },
        {
          selector: '.package-search button',
          title: 'Perform Search',
          content: 'Click Search or press Enter to find packages.'
        },
        {
          selector: '.package-item:first-child',
          title: 'Package Results',
          content: 'Each result shows the package name, version, and description.'
        },
        {
          selector: '.package-item:first-child .install-btn',
          title: 'Install Package',
          content: 'Click Install to add this package to your system.'
        },
        {
          selector: '[data-tab="configuration"]',
          title: 'View Changes',
          content: 'The configuration tab shows what will be changed.'
        }
      ]
    }
  ],

  shortcuts: [
    {
      key: 'f1',
      description: 'Open help panel',
      action: 'help'
    },
    {
      key: 'ctrl+/',
      description: 'Focus package search',
      action: 'search'
    },
    {
      key: 'ctrl+s',
      description: 'Save configuration',
      action: 'save'
    },
    {
      key: 'ctrl+enter',
      description: 'Validate configuration',
      action: 'validate'
    },
    {
      key: 'alt+1',
      description: 'Go to Dashboard',
      action: 'navigate',
      target: '#dashboard'
    },
    {
      key: 'alt+2',
      description: 'Go to Packages',
      action: 'navigate',
      target: '#packages'
    },
    {
      key: 'alt+3',
      description: 'Go to Configuration',
      action: 'navigate',
      target: '#configuration'
    },
    {
      key: 'alt+4',
      description: 'Go to Services',
      action: 'navigate',
      target: '#services'
    },
    {
      key: 'alt+5',
      description: 'Go to Generations',
      action: 'navigate',
      target: '#generations'
    },
    {
      key: 'alt+shift+h',
      description: 'Toggle help mode',
      action: 'help-mode'
    },
    {
      key: 'esc',
      description: 'Close dialogs/panels',
      action: 'close'
    }
  ]
};

// Export for use
export default helpContent;