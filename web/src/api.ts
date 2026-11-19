export type Product = { id: number; sku: string; name: string; description: string; price_cents: number; stock: number };
export type ProductPage = { items: Product[]; total: number };
export type OrderItem = { product_id: number; name: string; quantity: number; unit_price_cents: number };
export type Order = { id: number; status: string; total_cents: number; created_at: string; items: OrderItem[] };

export const TOKEN_KEY = 'shop.token';

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `HTTP ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

// All calls go to /api/*; Vite proxies them to FastAPI in dev (same origin, no CORS).
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (typeof init.body === 'string') headers.set('Content-Type', 'application/json');
  const res = await fetch(`/api${path}`, { ...init, headers });
  const body = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, body?.detail ?? res.statusText);
  return body as T;
}

const fmt = new Intl.NumberFormat(undefined, { style: 'currency', currency: 'EUR' });
export const money = (cents: number) => fmt.format(cents / 100);

export const getProducts = (q = '') =>
  api<ProductPage>(`/products?limit=50${q ? `&q=${encodeURIComponent(q)}` : ''}`);
export const getProduct = (id: number) => api<Product>(`/products/${id}`);
export const login = (email: string, password: string) =>
  api<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: new URLSearchParams({ username: email, password }), // OAuth2 form fields
  });
export const register = (email: string, password: string) =>
  api<{ id: number; email: string }>('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) });
export const createOrder = (items: { product_id: number; quantity: number }[]) =>
  api<Order>('/orders', { method: 'POST', body: JSON.stringify({ items }) });
export const getOrders = () => api<Order[]>('/orders');
