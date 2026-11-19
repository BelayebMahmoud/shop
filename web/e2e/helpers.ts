import { expect, type APIRequestContext, type Page, type TestInfo } from '@playwright/test';

/** Seeded accounts (db/migrations 002 and 003) — development test values only. */
export const STAFF = { email: 'staff@example.com', password: 'staff1234' };
export const ADMIN = { email: 'admin@example.com', password: 'admin1234' };
export const PASSWORD = 'e2e-pass-123';

/** Unique per test and per browser project, so parallel runs never share data. */
export function uid(info: TestInfo): string {
  return `${info.project.name}-${info.workerIndex}-${Date.now().toString(36)}-${Math.floor(Math.random() * 1e6)}`;
}

export async function apiToken(request: APIRequestContext, email: string, password: string): Promise<string> {
  const r = await request.post('/api/auth/login', { form: { username: email, password } });
  expect(r.status(), `login ${email}`).toBe(200);
  return (await r.json()).access_token;
}

const auth = (token: string) => ({ Authorization: `Bearer ${token}` });

export async function registerCustomer(request: APIRequestContext, info: TestInfo) {
  const email = `client-${uid(info)}@test.example`;
  const r = await request.post('/api/auth/register', { data: { email, password: PASSWORD } });
  expect(r.status()).toBe(201);
  return { email, password: PASSWORD, token: await apiToken(request, email, PASSWORD) };
}

export async function createCategory(request: APIRequestContext, token: string, name: string): Promise<number> {
  const r = await request.post('/api/categories', { data: { name }, headers: auth(token) });
  expect(r.status()).toBe(201);
  return (await r.json()).id;
}

export async function createProduct(
  request: APIRequestContext, token: string,
  p: { name: string; price_cents: number; stock: number; category_id: number },
) {
  const r = await request.post('/api/products', {
    data: { sku: p.name.replace(/\W+/g, '-').slice(0, 60), description: '', ...p },
    headers: auth(token),
  });
  expect(r.status(), await r.text()).toBe(201);
  return (await r.json()) as { id: number; name: string };
}

export async function placeOrder(request: APIRequestContext, token: string, items: { product_id: number; quantity: number }[]) {
  const r = await request.post('/api/orders', { data: { items }, headers: auth(token) });
  expect(r.status(), await r.text()).toBe(201);
  return (await r.json()) as { id: number; total_cents: number };
}

export async function setStatus(request: APIRequestContext, token: string, orderId: number, status: string) {
  const r = await request.patch(`/api/orders/${orderId}/status`, { data: { status }, headers: auth(token) });
  expect(r.status()).toBe(200);
}

export async function apiGet<T>(request: APIRequestContext, token: string, path: string): Promise<T> {
  const r = await request.get(`/api${path}`, { headers: auth(token) });
  expect(r.status()).toBe(200);
  return (await r.json()) as T;
}

/** Log in through the real login page. */
export async function uiLogin(page: Page, email: string, password: string) {
  if (!page.url().includes('/connexion')) await page.goto('/connexion');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Mot de passe').fill(password);
  await page.getByRole('button', { name: 'Se connecter' }).click();
  await expect(page.getByRole('button', { name: 'Se déconnecter' })).toBeVisible();
}

/** fr-FR currency text, e.g. 114,00 € (the space before € is a narrow no-break space). */
export const euros = (cents: number) => new RegExp(`${Math.floor(cents / 100)},${String(cents % 100).padStart(2, '0')}\\s€`);
