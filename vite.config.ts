import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  // Base configuration for Tauri
  base: './',
  
  // Resolve aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@nlp': resolve(__dirname, './implementations/web-based/js/nlp')
    }
  },

  // Server configuration for development
  server: {
    port: 5173,
    strictPort: true,
    watch: {
      ignored: ['**/src-tauri/**']
    }
  },

  // Build configuration
  build: {
    target: 'esnext',
    minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
    sourcemap: !!process.env.TAURI_DEBUG,
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },

  // Clear screen on dev start
  clearScreen: false,
  
  // Prevent Vite from obscuring Rust errors
  envPrefix: ['VITE_', 'TAURI_']
})