import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['5173-ieddf2kb511tbc1z3de4d-0ec8a8d.manus-asia.computer']
  }
})
