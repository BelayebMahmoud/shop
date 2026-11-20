// Shared helpers for the k6 scripts (PERF-01..03). BASE_URL defaults to the web container on the Compose network.
import http from 'k6/http';
import { check } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.1.0/index.js';

export const BASE = __ENV.BASE_URL || 'http://web:8080';
export const PRODUCTS = Number(__ENV.PRODUCT_COUNT || 50008);
export const WORDS = ['mug', 'tote', 'notebook', 'lamp', 'headphones', 'clock', 'pen', 'shirt', 'bowl', 'speaker',
  'classic', 'mini', 'pro', 'eco', 'deluxe', 'travel', 'studio', 'urban'];

export function login() {
  const r = http.post(`${BASE}/api/auth/login`, { username: 'demo@example.com', password: 'demo1234' });
  check(r, { 'login 200': res => res.status === 200 });
  return { token: r.json('access_token') };
}

export const pick = list => list[Math.floor(Math.random() * list.length)];
export const randInt = (min, max) => min + Math.floor(Math.random() * (max - min + 1));

/** k6 writes its own evidence: the full summary as JSON in reports/perf/<name>.json (mounted at /out).
 *  setup_data holds the test user's JWT: it is left out so no token lands in the evidence. */
export function summaryTo(name) {
  return data => ({
    [`/out/${name}.json`]: JSON.stringify({ ...data, setup_data: data.setup_data ? '(omis : jeton)' : undefined }, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: false }),
  });
}
