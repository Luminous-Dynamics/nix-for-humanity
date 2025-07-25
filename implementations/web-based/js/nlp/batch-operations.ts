/**
 * Batch Operations
 * Handle multiple commands in one request
 */

import { recognizeIntent, Intent } from './layers/intent-recognition';
import { buildCommand, NixCommand } from './layers/command-builder';
import { executeCommand, ExecutionResult } from './layers/command-executor';

export interface BatchOperation {
  operations: SingleOperation[];
  sequential: boolean; // Run in order vs parallel
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
export function parseBatchOperations(input: string): BatchOperation {
  // Detect sequential markers
  const sequential = /then|after that|next|finally/i.test(input);
  
  // Split by conjunctions and sequential markers
  const splitPattern = /(?:\s+(?:and|,|then|after that|next|finally)\s+)/i;
  const parts = input.split(splitPattern)
    .map(part => part.trim())
    .filter(part => part.length > 0);
  
  // Create operations
  const operations: SingleOperation[] = parts.map(part => ({
    input: part,
    status: 'pending' as const
  }));
  
  return { operations, sequential };
}

/**
 * Execute batch operations
 */
export async function executeBatch(
  batch: BatchOperation,
  options: {
    stopOnError?: boolean;
    confirmEach?: boolean;
    dryRun?: boolean;
    onProgress?: (op: SingleOperation, index: number, total: number) => void;
  } = {}
): Promise<BatchResult> {
  const startTime = Date.now();
  const result: BatchResult = {
    totalOperations: batch.operations.length,
    successful: 0,
    failed: 0,
    skipped: 0,
    operations: batch.operations,
    duration: 0
  };
  
  // Process each operation
  for (let i = 0; i < batch.operations.length; i++) {
    const operation = batch.operations[i];
    
    // Skip if previous failed and stopOnError is true
    if (options.stopOnError && result.failed > 0) {
      operation.status = 'skipped';
      result.skipped++;
      continue;
    }
    
    try {
      // Update status
      operation.status = 'running';
      if (options.onProgress) {
        options.onProgress(operation, i, batch.operations.length);
      }
      
      // Recognize intent
      operation.intent = recognizeIntent(operation.input);
      
      // Build command
      const buildResult = buildCommand(operation.intent);
      if (!buildResult.success || !buildResult.command) {
        operation.status = 'failed';
        result.failed++;
        continue;
      }
      
      operation.command = buildResult.command;
      
      // Execute command
      const execResult = await executeCommand(operation.command, {
        dryRun: options.dryRun,
        requireConfirmation: options.confirmEach
      });
      
      operation.result = execResult;
      
      if (execResult.success) {
        operation.status = 'success';
        result.successful++;
      } else if (execResult.wasCancelled) {
        operation.status = 'skipped';
        result.skipped++;
      } else {
        operation.status = 'failed';
        result.failed++;
      }
      
    } catch (error) {
      operation.status = 'failed';
      result.failed++;
      if (operation.result) {
        operation.result.error = error instanceof Error ? error.message : 'Unknown error';
      }
    }
    
    // Wait between sequential operations
    if (batch.sequential && i < batch.operations.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  result.duration = Date.now() - startTime;
  return result;
}

/**
 * Format batch result for display
 */
export function formatBatchResult(result: BatchResult): string {
  const lines: string[] = [];
  
  lines.push(`Completed ${result.totalOperations} operations:`);
  lines.push(`✅ Successful: ${result.successful}`);
  
  if (result.failed > 0) {
    lines.push(`❌ Failed: ${result.failed}`);
  }
  
  if (result.skipped > 0) {
    lines.push(`⏭️ Skipped: ${result.skipped}`);
  }
  
  lines.push('');
  
  // Details for each operation
  result.operations.forEach((op, index) => {
    const icon = 
      op.status === 'success' ? '✅' :
      op.status === 'failed' ? '❌' :
      op.status === 'skipped' ? '⏭️' : '⏳';
    
    lines.push(`${icon} ${index + 1}. ${op.input}`);
    
    if (op.status === 'success' && op.result?.output) {
      const output = op.result.output.trim().split('\n')[0];
      if (output) {
        lines.push(`   → ${output}`);
      }
    } else if (op.status === 'failed' && op.result?.error) {
      lines.push(`   → Error: ${op.result.error}`);
    }
  });
  
  return lines.join('\n');
}

interface BatchPattern {
  name: string;
  pattern: RegExp;
  expand: (match: RegExpMatchArray) => string[];
}

/**
 * Common batch operation patterns
 */
export const BATCH_PATTERNS: BatchPattern[] = [
  {
    name: 'Development Setup',
    pattern: /set\s*up\s+(?:a\s+)?(\w+)\s+(?:dev|development)\s+environment/i,
    expand: (match: RegExpMatchArray) => {
      const lang = match[1].toLowerCase();
      const packages: Record<string, string[]> = {
        'python': ['python3', 'python3-pip', 'python3-venv', 'ipython'],
        'javascript': ['nodejs', 'npm', 'yarn'],
        'rust': ['rustc', 'cargo', 'rust-analyzer'],
        'go': ['go', 'gopls'],
        'java': ['openjdk', 'maven', 'gradle']
      };
      
      const langPackages = packages[lang] || [`${lang}-dev`];
      return langPackages.map(pkg => `install ${pkg}`);
    }
  },
  {
    name: 'System Maintenance',
    pattern: /(?:do\s+)?(?:system\s+)?maintenance|clean\s*up\s+everything/i,
    expand: (match: RegExpMatchArray) => [
      'update system',
      'free up space',
      'check for broken packages'
    ]
  },
  {
    name: 'Install Multiple',
    pattern: /install\s+(.+?)(?:\s+and\s+(.+?))+/i,
    expand: (match: RegExpMatchArray) => {
      // This is handled by the normal batch parser
      return [match[0]];
    }
  }
];

/**
 * Expand batch patterns
 */
export function expandBatchPatterns(input: string): string[] {
  for (const pattern of BATCH_PATTERNS) {
    const match = input.match(pattern.pattern);
    if (match) {
      return pattern.expand(match);
    }
  }
  
  return [input];
}