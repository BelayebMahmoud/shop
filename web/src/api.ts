export type Role = 'CUSTOMER' | 'STAFF' | 'ADMIN';
export type User = { id: number; email: string; role: Role; is_active: boolean };
export type Category = { id: number; name: string };
export type Product = {
  id: number; sku: string; name: string; description: string; price_cents: number; stock: number; category_id: number;
};
export type ProductInput = Omit<Product, 'id'>;
export type ProductPage = { items: Product[]; total: number };
export type OrderStatus = 'PLACED' | 'PAID' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
export type OrderItem = { product_id: number; name: string; quantity: number; unit_price_cents: number };
export type Order = {
  id: number; user_id: number; status: OrderStatus; subtotal_cents: number; discount_cents: number; total_cents: number;
  created_at: string; updated_at: string; items: OrderItem[];
};
export type Dashboard = {
  revenue_cents: number;
  orders_by_status: Record<OrderStatus, number>;
  top_products: { product_id: number; name: string; quantity: number }[];
  low_stock: { id: number; sku: string; name: string; stock: number }[];
  low_stock_total: number;
};
export type SearchFilters = {
  q?: string; categoryId?: number; minPriceCents?: number; maxPriceCents?: number; inStock?: boolean;
  limit?: number; offset?: number;
};

export const TOKEN_KEY = 'shop.token';

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `HTTP ${status}`);
    this.status = status;
    this.detail = detail;
  }
  /** Business error code from {"detail": {"code": ...}}, if any. */
  get code(): string | undefined {
    return typeof this.detail === 'object' && this.detail !== null && 'code' in this.detail
      ? String((this.detail as { code: unknown }).code)
      : undefined;
  }
}

// All calls go to /api/*: Vite (dev) or nginx (containers) proxies them to FastAPI, same origin, no CORS.
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

const fmt = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' });
export const money = (cents: number) => fmt.format(cents / 100);

function query(params: Record<string, string | number | boolean | undefined>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== '' && v !== false) q.set(k, String(v));
  const s = q.toString();
  return s ? `?${s}` : '';
}

// ---------------------------------------------------------------- auth
export const login = (email: string, password: string) =>
  api<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: new URLSearchParams({ username: email, password }), // OAuth2 form fields
  });
export const register = (email: string, password: string) =>
  api<User>('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) });
export const getMe = () => api<User>('/auth/me');

// ---------------------------------------------------------------- catalogue
export const getCategories = () => api<Category[]>('/categories');
export const getProducts = (f: SearchFilters = {}) =>
  api<ProductPage>(`/products${query({
    q: f.q, category_id: f.categoryId, min_price_cents: f.minPriceCents, max_price_cents: f.maxPriceCents,
    in_stock: f.inStock, limit: f.limit ?? 20, offset: f.offset,
  })}`);
export const getProduct = (id: number) => api<Product>(`/products/${id}`);
export const createProduct = (p: ProductInput) => api<Product>('/products', { method: 'POST', body: JSON.stringify(p) });
export const updateProduct = (id: number, p: ProductInput) =>
  api<Product>(`/products/${id}`, { method: 'PUT', body: JSON.stringify(p) });
export const deleteProduct = (id: number) => api<null>(`/products/${id}`, { method: 'DELETE' });

// ---------------------------------------------------------------- orders
export const createOrder = (items: { product_id: number; quantity: number }[]) =>
  api<Order>('/orders', { method: 'POST', body: JSON.stringify({ items }) });
export const getOrders = (f: { status?: OrderStatus; limit?: number; offset?: number } = {}) =>
  api<Order[]>(`/orders${query({ status: f.status, limit: f.limit, offset: f.offset })}`);
export const cancelOrder = (id: number) => api<Order>(`/orders/${id}/cancel`, { method: 'POST' });
export const changeStatus = (id: number, status: OrderStatus) =>
  api<Order>(`/orders/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) });

// ---------------------------------------------------------------- users (FR-05, ADMIN only)
export const getUsers = () => api<User[]>('/users');
export const changeRole = (id: number, role: Role) =>
  api<User>(`/users/${id}/role`, { method: 'PATCH', body: JSON.stringify({ role }) });
export const deactivateUser = (id: number) => api<User>(`/users/${id}/deactivate`, { method: 'PATCH' });

// ---------------------------------------------------------------- dashboard
export const getDashboard = (f: { dateFrom?: string; dateTo?: string; categoryId?: number }) =>
  api<Dashboard>(`/dashboard${query({ date_from: f.dateFrom, date_to: f.dateTo, category_id: f.categoryId })}`);
