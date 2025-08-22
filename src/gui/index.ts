/**
 * 🌟 Luminous Nix GUI Components - Main Export
 * Modular TypeScript components for NixOS setup and management
 */

// Export all components
export * from './components/ModularComponents';

// Export the ceremony orchestrator
export * from './SetupCeremony';

// Export state management
export * from './StateManager';

// Export the bridge for backend integration
export * from './NixOSGuiBridge';

// Quick setup helper for easy integration
export { quickSetup, setupWizard } from './quickSetup';

// Version
export const VERSION = '1.0.0';