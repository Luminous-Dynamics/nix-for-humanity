// Re-export NLP components for Tauri frontend
export { NixInterface } from '../../implementations/web-based/js/nlp/nix-interface';
export { recognizeIntent } from '../../implementations/web-based/js/nlp/layers/intent-recognition';
export { buildCommand } from '../../implementations/web-based/js/nlp/layers/command-builder';
export { commandSandbox } from '../../implementations/web-based/js/nlp/layers/command-sandbox';

// Export types
export type { 
  Intent, 
  NixCommand, 
  ProcessResult,
  ExecutionOptions 
} from '../../implementations/web-based/js/nlp/types';