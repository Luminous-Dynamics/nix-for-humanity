#!/usr/bin/env node
/**
 * Plugin Manifest Validator
 * Validates plugin manifests for the repository
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const https = require('https');
const { URL } = require('url');

const REQUIRED_FIELDS = [
    'id',
    'name',
    'version',
    'author',
    'description',
    'downloadUrl',
    'minNixosGuiVersion'
];

const VALID_CATEGORIES = [
    'system',
    'ui-ux',
    'development',
    'security',
    'networking',
    'productivity',
    'integration',
    'data',
    'automation',
    'accessibility'
];

const VALID_PERMISSIONS = [
    'ui',
    'storage',
    'notifications',
    'settings',
    'events'
];

async function validateManifest(manifestPath) {
    console.log('🔍 Plugin Manifest Validator\n');
    
    try {
        // Read manifest
        const manifestContent = await fs.readFile(manifestPath, 'utf8');
        let manifest;
        
        try {
            manifest = JSON.parse(manifestContent);
        } catch (error) {
            console.error('❌ Invalid JSON format');
            return false;
        }
        
        console.log(`Validating: ${manifest.name || 'Unknown'} (${manifest.id || 'no-id'})\n`);
        
        const errors = [];
        const warnings = [];
        
        // Check required fields
        for (const field of REQUIRED_FIELDS) {
            if (!manifest[field]) {
                errors.push(`Missing required field: ${field}`);
            }
        }
        
        // Validate ID format
        if (manifest.id && !manifest.id.match(/^[a-z0-9-]+$/)) {
            errors.push('Invalid ID format. Use lowercase letters, numbers, and hyphens only');
        }
        
        // Validate version format
        if (manifest.version && !manifest.version.match(/^\d+\.\d+\.\d+$/)) {
            errors.push('Invalid version format. Use semantic versioning (e.g., 1.0.0)');
        }
        
        // Validate category
        if (manifest.category && !VALID_CATEGORIES.includes(manifest.category)) {
            errors.push(`Invalid category. Valid options: ${VALID_CATEGORIES.join(', ')}`);
        }
        
        // Validate permissions
        if (manifest.permissions) {
            if (!Array.isArray(manifest.permissions)) {
                errors.push('Permissions must be an array');
            } else {
                for (const perm of manifest.permissions) {
                    if (!VALID_PERMISSIONS.includes(perm)) {
                        errors.push(`Invalid permission: ${perm}. Valid options: ${VALID_PERMISSIONS.join(', ')}`);
                    }
                }
            }
        }
        
        // Validate URLs
        const urlFields = ['homepage', 'repository', 'downloadUrl'];
        for (const field of urlFields) {
            if (manifest[field]) {
                try {
                    new URL(manifest[field]);
                    if (!manifest[field].startsWith('https://')) {
                        warnings.push(`${field} should use HTTPS`);
                    }
                } catch (error) {
                    errors.push(`Invalid URL in ${field}: ${manifest[field]}`);
                }
            }
        }
        
        // Validate screenshots
        if (manifest.screenshots) {
            if (!Array.isArray(manifest.screenshots)) {
                errors.push('Screenshots must be an array');
            } else {
                manifest.screenshots.forEach((screenshot, index) => {
                    if (typeof screenshot === 'string') {
                        try {
                            new URL(screenshot);
                        } catch (error) {
                            errors.push(`Invalid screenshot URL at index ${index}`);
                        }
                    } else if (screenshot.url) {
                        try {
                            new URL(screenshot.url);
                        } catch (error) {
                            errors.push(`Invalid screenshot URL at index ${index}`);
                        }
                    } else {
                        errors.push(`Invalid screenshot format at index ${index}`);
                    }
                });
            }
        }
        
        // Check file size
        if (manifest.size && manifest.size > 10 * 1024 * 1024) {
            warnings.push('Plugin size exceeds 10MB');
        }
        
        // Validate tags
        if (manifest.tags) {
            if (!Array.isArray(manifest.tags)) {
                errors.push('Tags must be an array');
            } else if (manifest.tags.length > 10) {
                warnings.push('Too many tags (maximum 10)');
            }
        }
        
        // Check description length
        if (manifest.description && manifest.description.length > 200) {
            warnings.push('Description is too long (maximum 200 characters)');
        }
        
        // Validate license
        const validLicenses = ['MIT', 'GPL-3.0', 'Apache-2.0', 'BSD-3-Clause', 'ISC', 'LGPL-3.0'];
        if (manifest.license && !validLicenses.includes(manifest.license)) {
            warnings.push(`Uncommon license: ${manifest.license}`);
        }
        
        // Check if download URL is accessible
        if (manifest.downloadUrl && errors.length === 0) {
            console.log('🌐 Checking download URL...');
            const isAccessible = await checkUrl(manifest.downloadUrl);
            if (!isAccessible) {
                errors.push('Download URL is not accessible');
            } else {
                console.log('✅ Download URL is accessible\n');
            }
        }
        
        // Verify checksum if provided
        if (manifest.sha256 && manifest.downloadUrl && errors.length === 0) {
            console.log('🔐 Verifying checksum...');
            const actualHash = await downloadAndHash(manifest.downloadUrl);
            if (actualHash && actualHash !== manifest.sha256) {
                errors.push('SHA256 checksum mismatch');
            } else if (actualHash) {
                console.log('✅ Checksum verified\n');
            }
        }
        
        // Display results
        if (errors.length > 0) {
            console.log('❌ Validation Failed\n');
            console.log('Errors:');
            errors.forEach(error => console.log(`  - ${error}`));
        } else {
            console.log('✅ Validation Passed\n');
        }
        
        if (warnings.length > 0) {
            console.log('\n⚠️  Warnings:');
            warnings.forEach(warning => console.log(`  - ${warning}`));
        }
        
        // Summary
        console.log('\n📊 Summary:');
        console.log(`  Errors: ${errors.length}`);
        console.log(`  Warnings: ${warnings.length}`);
        
        if (errors.length === 0) {
            console.log('\n✨ This manifest is ready for submission!');
            
            // Generate submission info
            console.log('\nSubmission checklist:');
            console.log('1. Fork the plugin repository');
            console.log(`2. Add manifest to: plugins/${manifest.official ? 'official' : 'community'}/${manifest.id}.json`);
            console.log('3. Submit pull request');
            console.log('4. Wait for review');
        }
        
        return errors.length === 0;
        
    } catch (error) {
        console.error('❌ Validation error:', error.message);
        return false;
    }
}

async function checkUrl(url) {
    return new Promise((resolve) => {
        https.get(url, { method: 'HEAD' }, (res) => {
            resolve(res.statusCode >= 200 && res.statusCode < 400);
        }).on('error', () => {
            resolve(false);
        });
    });
}

async function downloadAndHash(url) {
    return new Promise((resolve) => {
        https.get(url, (res) => {
            if (res.statusCode !== 200) {
                resolve(null);
                return;
            }
            
            const hash = crypto.createHash('sha256');
            res.on('data', (chunk) => hash.update(chunk));
            res.on('end', () => resolve(hash.digest('hex')));
            res.on('error', () => resolve(null));
        }).on('error', () => {
            resolve(null);
        });
    });
}

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('Usage: validate-manifest <manifest.json>');
        console.log('Example: validate-manifest my-plugin-manifest.json');
        process.exit(1);
    }
    
    const manifestPath = path.resolve(args[0]);
    validateManifest(manifestPath).then(valid => {
        process.exit(valid ? 0 : 1);
    });
}