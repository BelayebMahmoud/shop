// PERF-03 (QR-PE-02, FR-10): filtered search on 50,000 products, 20 concurrent users for 2 min.
// Target from docs/exigences.yaml: p95 < 800 ms, error rate < 1 %.
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE, WORDS, pick, randInt, summaryTo } from './common.js';

export const options = {
  scenarios: { search: { executor: 'constant-vus', vus: 20, duration: __ENV.DURATION || '2m' } },
  tags: { case: 'PERF-03', req: 'QR-PE-02' },
  thresholds: { 'http_req_duration{name:search}': ['p(95)<800'], http_req_failed: ['rate<0.01'] },
};

export default function () {
  const min = randInt(0, 150) * 100;
  const params = [
    `q=${pick(WORDS)}`,
    Math.random() < 0.6 ? `category_id=${randInt(1, 6)}` : '',
    Math.random() < 0.5 ? `min_price_cents=${min}&max_price_cents=${min + randInt(10, 100) * 100}` : '',
    Math.random() < 0.5 ? 'in_stock=true' : '',
    `limit=20&offset=${randInt(0, 5) * 20}`,
  ].filter(Boolean).join('&');
  const r = http.get(`${BASE}/api/products?${params}`, { tags: { name: 'search' } });
  check(r, { 'search 200': res => res.status === 200, 'has total': res => res.json('total') !== undefined });
  sleep(Math.random() * 0.5 + 0.25);
}

export const handleSummary = summaryTo('search');
