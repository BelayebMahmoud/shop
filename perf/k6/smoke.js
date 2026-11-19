// PERF-01 (QR-PE-01): smoke — 1 virtual user for 30 s on health, list, detail and search. Must have 0 errors.
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE, PRODUCTS, WORDS, login, pick, randInt, summaryTo } from './common.js';

export const options = {
  vus: 1,
  duration: '30s',
  tags: { case: 'PERF-01', req: 'QR-PE-01' },
  thresholds: { http_req_failed: ['rate==0'], checks: ['rate==1'] },
};

export function setup() {
  return login();
}

export default function () {
  check(http.get(`${BASE}/api/health`), { 'health 200': r => r.status === 200 });
  check(http.get(`${BASE}/api/products?limit=20`), { 'list 200': r => r.status === 200 });
  check(http.get(`${BASE}/api/products/${randInt(1, PRODUCTS)}`), { 'detail 200': r => r.status === 200 });
  check(http.get(`${BASE}/api/products?q=${pick(WORDS)}&in_stock=true`), { 'search 200': r => r.status === 200 });
  sleep(1);
}

export const handleSummary = summaryTo('smoke');
