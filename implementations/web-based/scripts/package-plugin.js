#!/usr/bin/env node
/**
 * Plugin Packaging Tool
 * Package plugins for distribution
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const { exec } = require('child_process');
const { promisify } = require('util');
const { validatePlugin, calculatePluginHash } = require('../backend/utils/security');

const execAsync = promisify(exec);

async function packagePlugin(pluginPath, options = {}) {
    console.log('📦 NixOS GUI Plugin Packager\n');
    
    try {
        // Read plugin file
        const pluginCode = await fs.readFile(pluginPath, 'utf8');
        const pluginDir = path.dirname(pluginPath);
        const pluginName = path.basename(pluginPath, '.js');
        
        // Extract metadata
        const metadata = extractMetadata(pluginCode);
        console.log('📋 Plugin Information:');
        console.log(`  ID: ${metadata.id}`);
        console.log(`  Name: ${metadata.name}`);
        console.log(`  Version: ${metadata.version}`);
        console.log(`  Author: ${metadata.author}`);
        console.log('');
        
        // Validate plugin
        console.log('🔍 Validating plugin...');
        const validation = validatePlugin({
            code: pluginCode,
            metadata: metadata
        });
        
        if (!validation.valid) {
            console.error('❌ Validation failed:', validation.error);
            process.exit(1);
        }
        console.log('✅ Validation passed\n');
        
        // Create output directory
        const outputDir = options.output || './dist';
        await fs.mkdir(outputDir, { recursive: true });
        
        // Package contents
        const packageDir = path.join(outputDir, `${metadata.id}-${metadata.version}`);
        await fs.mkdir(packageDir, { recursive: true });
        
        // Copy main plugin file
        const pluginOutputPath = path.join(packageDir, `${metadata.id}.js`);
        await fs.copyFile(pluginPath, pluginOutputPath);
        
        // Check for additional files
        const additionalFiles = [];
        
        // README
        const readmePath = path.join(pluginDir, 'README.md');
        if (await fileExists(readmePath)) {
            await fs.copyFile(readmePath, path.join(packageDir, 'README.md'));
            additionalFiles.push('README.md');
        }
        
        // LICENSE
        const licensePath = path.join(pluginDir, 'LICENSE');
        if (await fileExists(licensePath)) {
            await fs.copyFile(licensePath, path.join(packageDir, 'LICENSE'));
            additionalFiles.push('LICENSE');
        }
        
        // CHANGELOG
        const changelogPath = path.join(pluginDir, 'CHANGELOG.md');
        if (await fileExists(changelogPath)) {
            await fs.copyFile(changelogPath, path.join(packageDir, 'CHANGELOG.md'));
            additionalFiles.push('CHANGELOG.md');
        }
        
        // Assets directory
        const assetsPath = path.join(pluginDir, 'assets');
        if (await fileExists(assetsPath)) {
            await copyDir(assetsPath, path.join(packageDir, 'assets'));
            additionalFiles.push('assets/');
        }
        
        // Calculate checksums
        console.log('🔐 Calculating checksums...');
        const hashes = {};
        
        for (const file of await getFiles(packageDir)) {
            const relativePath = path.relative(packageDir, file);
            const content = await fs.readFile(file);
            hashes[relativePath] = crypto.createHash('sha256').update(content).digest('hex');
        }
        
        // Create manifest
        const manifest = {
            id: metadata.id,
            name: metadata.name,
            version: metadata.version,
            author: metadata.author,
            description: metadata.description || '',
            homepage: metadata.homepage || '',
            repository: metadata.repository || '',
            license: metadata.license || 'MIT',
            permissions: metadata.permissions || [],
            main: `${metadata.id}.js`,
            files: Object.keys(hashes),
            checksums: hashes,
            minNixosGuiVersion: options.minVersion || '1.0.0',
            maxNixosGuiVersion: options.maxVersion || '*',
            created: new Date().toISOString(),
            sha256: hashes[`${metadata.id}.js`]
        };
        
        // Write manifest
        await fs.writeFile(
            path.join(packageDir, 'manifest.json'),
            JSON.stringify(manifest, null, 2)
        );
        
        console.log('✅ Manifest created\n');
        
        // Minify if requested
        if (options.minify) {
            console.log('🗜️ Minifying plugin...');
            try {
                await execAsync(`npx terser ${pluginOutputPath} -o ${pluginOutputPath}.min.js`);
                
                // Update manifest with minified version
                const minContent = await fs.readFile(`${pluginOutputPath}.min.js`);
                const minHash = crypto.createHash('sha256').update(minContent).digest('hex');
                manifest.files.push(`${metadata.id}.min.js`);
                manifest.checksums[`${metadata.id}.min.js`] = minHash;
                
                await fs.writeFile(
                    path.join(packageDir, 'manifest.json'),
                    JSON.stringify(manifest, null, 2)
                );
                
                console.log('✅ Minification complete\n');
            } catch (error) {
                console.warn('⚠️ Minification failed:', error.message);
                console.log('Continuing without minification...\n');
            }
        }
        
        // Create archive
        if (options.archive !== false) {
            console.log('📦 Creating archive...');
            
            const archiveName = `${metadata.id}-${metadata.version}.tar.gz`;
            const archivePath = path.join(outputDir, archiveName);
            
            await execAsync(
                `tar -czf ${archivePath} -C ${outputDir} ${path.basename(packageDir)}`
            );
            
            // Calculate archive checksum
            const archiveContent = await fs.readFile(archivePath);
            const archiveHash = crypto.createHash('sha256').update(archiveContent).digest('hex');
            
            console.log('✅ Archive created:', archiveName);
            console.log('   SHA256:', archiveHash);
            console.log('');
            
            // Create release info
            const releaseInfo = {
                version: metadata.version,
                downloadUrl: `https://github.com/${metadata.author}/${metadata.id}/releases/download/v${metadata.version}/${archiveName}`,
                sha256: archiveHash,
                size: archiveContent.length,
                releaseDate: new Date().toISOString(),
                notes: options.releaseNotes || ''
            };
            
            await fs.writeFile(
                path.join(outputDir, 'release.json'),
                JSON.stringify(releaseInfo, null, 2)
            );
        }
        
        // Sign package if key provided
        if (options.privateKey) {
            console.log('🔏 Signing package...');
            
            const sign = crypto.createSign('SHA256');
            sign.update(pluginCode);
            sign.end();
            
            const signature = sign.sign(options.privateKey, 'hex');
            
            await fs.writeFile(
                path.join(packageDir, 'signature.sig'),
                signature
            );
            
            manifest.signature = signature;
            await fs.writeFile(
                path.join(packageDir, 'manifest.json'),
                JSON.stringify(manifest, null, 2)
            );
            
            console.log('✅ Package signed\n');
        }
        
        // Summary
        console.log('📊 Package Summary:');
        console.log(`  Output directory: ${packageDir}`);
        console.log(`  Files included: ${manifest.files.length}`);
        console.log(`  Total size: ${await getDirectorySize(packageDir)} bytes`);
        if (additionalFiles.length > 0) {
            console.log(`  Additional files: ${additionalFiles.join(', ')}`);
        }
        console.log('');
        
        console.log('✨ Plugin packaged successfully!');
        console.log('\nTo publish your plugin:');
        console.log('1. Upload the package to your repository');
        console.log('2. Create a release with the archive');
        console.log('3. Submit manifest.json to nixos-gui/plugins repository');
        
    } catch (error) {
        console.error('\n❌ Packaging failed:', error.message);
        process.exit(1);
    }
}

function extractMetadata(code) {
    const metadata = {
        id: 'unknown',
        name: 'Unknown Plugin',
        version: '0.0.0',
        author: 'Unknown',
        permissions: [],
        description: '',
        homepage: '',
        repository: '',
        license: 'MIT'
    };
    
    // Extract fields using regex
    const patterns = {
        id: /id:\s*['"`]([^'"`]+)['"`]/,
        name: /name:\s*['"`]([^'"`]+)['"`]/,
        version: /version:\s*['"`]([^'"`]+)['"`]/,
        author: /author:\s*['"`]([^'"`]+)['"`]/,
        description: /description:\s*['"`]([^'"`]+)['"`]/,
        homepage: /homepage:\s*['"`]([^'"`]+)['"`]/,
        repository: /repository:\s*['"`]([^'"`]+)['"`]/,
        license: /license:\s*['"`]([^'"`]+)['"`]/,
        permissions: /permissions:\s*\[([^\]]+)\]/
    };
    
    for (const [field, pattern] of Object.entries(patterns)) {
        const match = code.match(pattern);
        if (match) {
            if (field === 'permissions') {
                metadata[field] = match[1]
                    .split(',')
                    .map(p => p.trim().replace(/['"`]/g, ''))
                    .filter(p => p);
            } else {
                metadata[field] = match[1];
            }
        }
    }
    
    return metadata;
}

async function fileExists(filePath) {
    try {
        await fs.access(filePath);
        return true;
    } catch {
        return false;
    }
}

async function copyDir(src, dest) {
    await fs.mkdir(dest, { recursive: true });
    const entries = await fs.readdir(src, { withFileTypes: true });
    
    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        
        if (entry.isDirectory()) {
            await copyDir(srcPath, destPath);
        } else {
            await fs.copyFile(srcPath, destPath);
        }
    }
}

async function getFiles(dir, files = []) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            await getFiles(fullPath, files);
        } else {
            files.push(fullPath);
        }
    }
    
    return files;
}

async function getDirectorySize(dir) {
    const files = await getFiles(dir);
    let totalSize = 0;
    
    for (const file of files) {
        const stat = await fs.stat(file);
        totalSize += stat.size;
    }
    
    return totalSize;
}

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('Usage: package-plugin <plugin-file> [options]');
        console.log('');
        console.log('Options:');
        console.log('  --output, -o <dir>      Output directory (default: ./dist)');
        console.log('  --minify                Minify the plugin code');
        console.log('  --no-archive            Skip creating archive');
        console.log('  --min-version <ver>     Minimum NixOS GUI version');
        console.log('  --max-version <ver>     Maximum NixOS GUI version');
        console.log('  --release-notes <text>  Release notes');
        console.log('  --sign <key-file>       Sign with private key');
        console.log('');
        console.log('Example: package-plugin my-plugin.js --output ./releases --minify');
        process.exit(1);
    }
    
    const pluginPath = path.resolve(args[0]);
    const options = {};
    
    // Parse options
    for (let i = 1; i < args.length; i++) {
        switch (args[i]) {
            case '--output':
            case '-o':
                options.output = args[++i];
                break;
            case '--minify':
                options.minify = true;
                break;
            case '--no-archive':
                options.archive = false;
                break;
            case '--min-version':
                options.minVersion = args[++i];
                break;
            case '--max-version':
                options.maxVersion = args[++i];
                break;
            case '--release-notes':
                options.releaseNotes = args[++i];
                break;
            case '--sign':
                options.privateKey = fs.readFileSync(args[++i], 'utf8');
                break;
        }
    }
    
    packagePlugin(pluginPath, options);
}