import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// make sure overlay is ON
export default defineConfig({
  plugins: [react()],
  server: {
    hmr: { overlay: true }
  }
})