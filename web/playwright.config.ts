import { defineConfig, devices } from '@playwright/test';

// E2E runs on its own ports and its own database (shop_e2e, rebuilt at start) so it never touches dev data.
const API_PORT = Number(process.env.E2E_API_PORT ?? 8001);
const WEB_PORT = Number(process.env.E2E_WEB_PORT ?? 5174);
const python = process.platform === 'win32' ? '..\\backend\\.venv\\Scripts\\python.exe' : '../backend/.venv/bin/python';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  // ENV-01 (docs/anomalies.md): through Docker Desktop's forwarded port, parallel runs stall ~10 s on database
  // calls. One worker by default; E2E_WORKERS raises it (e.g. against the Compose stack, phase 5).
  workers: Number(process.env.E2E_WORKERS ?? 1),
  forbidOnly: !!process.env.CI,
  retries: 0, // a flaky test is a defect to fix, not to hide
  timeout: 30_000,
  reporter: [['list'], ['junit', { outputFile: '../reports/junit-e2e.xml' }]],
  use: {
    // 127.0.0.1, not localhost: on Windows `localhost` tries IPv6 first and each connection waits ~2 s.
    baseURL: `http://127.0.0.1:${WEB_PORT}`,
    locale: 'fr-FR',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
  webServer: [
    {
      command: `${python} ../tools/e2e_api.py`,
      url: `http://127.0.0.1:${API_PORT}/api/health`,
      env: { E2E_API_PORT: String(API_PORT) },
      stdout: 'pipe',
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: 'npx vite build && npx vite preview --host 127.0.0.1', // the production build, as shipped
      url: `http://127.0.0.1:${WEB_PORT}`,
      env: { WEB_PORT: String(WEB_PORT), API_URL: `http://127.0.0.1:${API_PORT}` },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
