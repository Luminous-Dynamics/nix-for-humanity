/**
 * Batch Operations
 * Handle multiple commands in one request
 */
import { Intent } from './layers/intent-recognition';
import { NixCommand } from './layers/command-builder';
import { ExecutionResult } from './layers/command-executor';
export interface BatchOperation {
    operations: SingleOperation[];
    sequential: boolean;
}
export interface SingleOperation {
    input: string;
    intent?: Intent;
    command?: NixCommand;
    result?: ExecutionResult;
    status: 'pending' | 'running' | 'success' | 'failed' | 'skipped';
}
export interface BatchResult {
    totalOperations: number;
    successful: number;
    failed: number;
    skipped: number;
    operations: SingleOperation[];
    duration: number;
}
/**
 * Parse batch operations from natural language
 */
export declare function parseBatchOperations(input: string): BatchOperation;
/**
 * Execute batch operations
 */
export declare function executeBatch(batch: BatchOperation, options?: {
    stopOnError?: boolean;
    confirmEach?: boolean;
    dryRun?: boolean;
    onProgress?: (op: SingleOperation, index: number, total: number) => void;
}): Promise<BatchResult>;
/**
 * Format batch result for display
 */
export declare function formatBatchResult(result: BatchResult): string;
interface BatchPattern {
    name: string;
    pattern: RegExp;
    expand: (match: RegExpMatchArray) => string[];
}
/**
 * Common batch operation patterns
 */
export declare const BATCH_PATTERNS: BatchPattern[];
/**
 * Expand batch patterns
 */
export declare function expandBatchPatterns(input: string): string[];
export {};
