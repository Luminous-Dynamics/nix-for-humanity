/**
 * Execution Configuration
 * Controls whether to use real NixOS commands or simulations
 */

export interface ExecutionConfig {
  mode: 'real' | 'simulation' | 'hybrid';
  requireConfirmation: boolean;
  allowedCommands: string[];
  simulateInDevelopment: boolean;
  logCommands: boolean;
}

// Default configuration
export const defaultConfig: ExecutionConfig = {
  mode: process.env.NODE_ENV === 'production' ? 'real' : 'simulation',
  requireConfirmation: true,
  allowedCommands: [
    'nix-env',
    'nix-channel',
    'nixos-rebuild',
    'systemctl',
    'journalctl',
    'nix-collect-garbage',
    'nix-store',
    'nmcli',
    'pactl',
    'xrandr',
    'gsettings'
  ],
  simulateInDevelopment: true,
  logCommands: true
};

// Load configuration from environment
export function loadExecutionConfig(): ExecutionConfig {
  const config = { ...defaultConfig };
  
  // Override from environment variables
  if (process.env.NIX_EXECUTION_MODE) {
    config.mode = process.env.NIX_EXECUTION_MODE as 'real' | 'simulation' | 'hybrid';
  }
  
  if (process.env.NIX_REQUIRE_CONFIRMATION) {
    config.requireConfirmation = process.env.NIX_REQUIRE_CONFIRMATION === 'true';
  }
  
  if (process.env.NIX_LOG_COMMANDS) {
    config.logCommands = process.env.NIX_LOG_COMMANDS === 'true';
  }
  
  return config;
}

// Global configuration instance
export const executionConfig = loadExecutionConfig();