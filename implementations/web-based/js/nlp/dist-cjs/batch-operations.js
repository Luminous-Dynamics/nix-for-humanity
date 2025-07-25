"use strict";
/**
 * Batch Operations
 * Handle multiple commands in one request
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.BATCH_PATTERNS = void 0;
exports.parseBatchOperations = parseBatchOperations;
exports.executeBatch = executeBatch;
exports.formatBatchResult = formatBatchResult;
exports.expandBatchPatterns = expandBatchPatterns;
const intent_recognition_1 = require("./layers/intent-recognition");
const command_builder_1 = require("./layers/command-builder");
const command_executor_1 = require("./layers/command-executor");
/**
 * Parse batch operations from natural language
 */
function parseBatchOperations(input) {
    // Detect sequential markers
    const sequential = /then|after that|next|finally/i.test(input);
    // Split by conjunctions and sequential markers
    const splitPattern = /(?:\s+(?:and|,|then|after that|next|finally)\s+)/i;
    const parts = input.split(splitPattern)
        .map(part => part.trim())
        .filter(part => part.length > 0);
    // Create operations
    const operations = parts.map(part => ({
        input: part,
        status: 'pending'
    }));
    return { operations, sequential };
}
/**
 * Execute batch operations
 */
async function executeBatch(batch, options = {}) {
    const startTime = Date.now();
    const result = {
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
            operation.intent = (0, intent_recognition_1.recognizeIntent)(operation.input);
            // Build command
            const buildResult = (0, command_builder_1.buildCommand)(operation.intent);
            if (!buildResult.success || !buildResult.command) {
                operation.status = 'failed';
                result.failed++;
                continue;
            }
            operation.command = buildResult.command;
            // Execute command
            const execResult = await (0, command_executor_1.executeCommand)(operation.command, {
                dryRun: options.dryRun,
                requireConfirmation: options.confirmEach
            });
            operation.result = execResult;
            if (execResult.success) {
                operation.status = 'success';
                result.successful++;
            }
            else if (execResult.wasCancelled) {
                operation.status = 'skipped';
                result.skipped++;
            }
            else {
                operation.status = 'failed';
                result.failed++;
            }
        }
        catch (error) {
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
function formatBatchResult(result) {
    const lines = [];
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
        const icon = op.status === 'success' ? '✅' :
            op.status === 'failed' ? '❌' :
                op.status === 'skipped' ? '⏭️' : '⏳';
        lines.push(`${icon} ${index + 1}. ${op.input}`);
        if (op.status === 'success' && op.result?.output) {
            const output = op.result.output.trim().split('\n')[0];
            if (output) {
                lines.push(`   → ${output}`);
            }
        }
        else if (op.status === 'failed' && op.result?.error) {
            lines.push(`   → Error: ${op.result.error}`);
        }
    });
    return lines.join('\n');
}
/**
 * Common batch operation patterns
 */
exports.BATCH_PATTERNS = [
    {
        name: 'Development Setup',
        pattern: /set\s*up\s+(?:a\s+)?(\w+)\s+(?:dev|development)\s+environment/i,
        expand: (match) => {
            const lang = match[1].toLowerCase();
            const packages = {
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
        expand: (match) => [
            'update system',
            'free up space',
            'check for broken packages'
        ]
    },
    {
        name: 'Install Multiple',
        pattern: /install\s+(.+?)(?:\s+and\s+(.+?))+/i,
        expand: (match) => {
            // This is handled by the normal batch parser
            return [match[0]];
        }
    }
];
/**
 * Expand batch patterns
 */
function expandBatchPatterns(input) {
    for (const pattern of exports.BATCH_PATTERNS) {
        const match = input.match(pattern.pattern);
        if (match) {
            return pattern.expand(match);
        }
    }
    return [input];
}
//# sourceMappingURL=batch-operations.js.map