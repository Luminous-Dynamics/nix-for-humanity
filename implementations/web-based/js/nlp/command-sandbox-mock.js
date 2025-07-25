/**
 * Mock Command Sandbox for Browser Testing
 * Simulates command execution without actually running system commands
 */

export class CommandSandbox {
  constructor() {
    this.mockResponses = {
      'nix search nixpkgs firefox': {
        success: true,
        stdout: `* nixpkgs.firefox (firefox-123.0)
  Mozilla Firefox - Web browser
  
* nixpkgs.firefox-esr (firefox-esr-115.8.0esr)
  Mozilla Firefox ESR - Extended Support Release
  
* nixpkgs.firefox-devedition (firefox-devedition-123.0b9)
  Mozilla Firefox Developer Edition`,
        stderr: '',
        exitCode: 0
      },
      'nix search nixpkgs python': {
        success: true,
        stdout: `* nixpkgs.python3 (python-3.11.8)
  Python 3 interpreter
  
* nixpkgs.python311 (python-3.11.8)
  Python 3.11 interpreter
  
* nixpkgs.python312 (python-3.12.2)
  Python 3.12 interpreter`,
        stderr: '',
        exitCode: 0
      },
      'nix-env -q': {
        success: true,
        stdout: `firefox-123.0
git-2.44.0
nodejs-20.11.1
vscode-1.87.0`,
        stderr: '',
        exitCode: 0
      }
    };
  }

  /**
   * Mock execute method that returns simulated results
   */
  async execute(command, args, options = {}) {
    // Simulate execution delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Build full command string
    const fullCommand = `${command} ${args.join(' ')}`;
    
    // Check for mock response
    if (this.mockResponses[fullCommand]) {
      return this.mockResponses[fullCommand];
    }
    
    // Default response for unknown commands
    return {
      success: false,
      stdout: '',
      stderr: `Mock: Command '${fullCommand}' not implemented in mock mode`,
      exitCode: 1
    };
  }
}

// Export singleton instance
export const commandSandbox = new CommandSandbox();