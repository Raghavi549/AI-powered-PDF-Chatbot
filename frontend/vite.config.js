import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The backend only allows the origin http://localhost:5173 (CORS), so fail
    // loudly if the port is taken instead of silently moving to another one.
    port: 5173,
    strictPort: true,
  },
})
