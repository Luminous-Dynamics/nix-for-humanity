import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  // Tauri expects the build output in this specific directory
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  
  // Tauri uses a custom protocol
  base: './',
  
  server: {
    port: 1420,
    strictPort: true,
  },
  
  envPrefix: ['VITE_', 'TAURI_'],
})