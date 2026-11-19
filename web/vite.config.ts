import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Ports come from the environment (Chapitre I: configurable ports, co-existence); defaults for local development.
const webPort = Number(process.env.WEB_PORT ?? 5173);
const apiUrl = process.env.API_URL ?? 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: webPort,
    strictPort: true,
    proxy: { '/api': apiUrl }, // same origin in dev: no CORS config needed
  },
  preview: {
    port: webPort, // E2E runs the production build, served by `vite preview` with the same proxy
    strictPort: true,
    proxy: { '/api': apiUrl },
  },
});
