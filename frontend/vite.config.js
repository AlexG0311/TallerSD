import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,        // permite acceso externo
    port: 5173,
    allowedHosts: true, // permite cualquier host (necesario para ngrok)
    proxy: {
      '/process': 'http://127.0.0.1:8000',
    },
  }
})
