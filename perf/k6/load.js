// PERF-02 (QR-PE-01): 20 concurrent users for 5 min on the product list and the product detail.
// Targets from docs/exigences.yaml: p95 < 500 ms on each route, error rate < 1 %.
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE, PRODUCTS, login, randInt, summaryTo } from './common.js';

export const options = {
  scenarios: { load: { executor: 'constant-vus', vus: 20, duration: __ENV.DURATION || '5m' } },
  tags: { case: 'PERF-02', req: 'QR-PE-01' },
  thresholds: {
    'http_req_duration{name:list}': ['p(95)<500'],
    'http_req_duration{name:detail}': ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export function setup() {
  return login(); // once, as the plan requires; list and detail are public routes
}

export default function (data) {
  const headers = { Authorization: `Bearer ${data.token}` };
  const list = http.get(`${BASE}/api/products?limit=20&offset=${randInt(0, 2000) * 20}`, { headers, tags: { name: 'list' } });
  check(list, { 'list 200': r => r.status === 200 });
  const detail = http.get(`${BASE}/api/products/${randInt(1, PRODUCTS)}`, { headers, tags: { name: 'detail' } });
  check(detail, { 'detail 200': r => r.status === 200 });
  sleep(Math.random() * 0.5 + 0.25); // think time 0.25–0.75 s
}

export const handleSummary = summaryTo('load');
