/**
 * Command Builder Layer (Pure Functions)
 * Converts intents to NixOS commands - no execution
 */
import { Intent } from './intent-recognition';
export interface NixCommand {
    command: string;
    args: string[];
    requiresSudo: boolean;
    requiresConfirmation: boolean;
    description: string;
    rollbackCommand?: string;
    supportsDryRun: boolean;
}
export interface CommandBuildResult {
    success: boolean;
    command?: NixCommand;
    error?: string;
    suggestion?: string;
}
/**
 * Build NixOS command from intent
 * Pure function - no side effects
 */
export declare function buildCommand(intent: Intent): CommandBuildResult;
/**
 * Get command risk level for safety decisions
 * Pure function
 */
export declare function getCommandRiskLevel(command: NixCommand): 'safe' | 'moderate' | 'dangerous';
/**
 * Generate natural language description of what command will do
 * Pure function
 */
export declare function explainCommand(command: NixCommand): string;
