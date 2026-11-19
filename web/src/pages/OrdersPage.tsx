import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router';
import { getOrders, money, type Order } from '../api';
import { useAuth } from '../auth';

export default function OrdersPage() {
  const { token } = useAuth();
  const placed = (useLocation().state as { placed?: number } | null)?.placed;
  const [orders, setOrders] = useState<Order[] | null>(null);

  useEffect(() => {
    if (token) getOrders().then(setOrders);
  }, [token]);

  if (!token) return <Navigate to="/login" state={{ from: '/orders' }} replace />;

  return (
    <main>
      <h1>My orders</h1>
      {placed && <p role="status">Order #{placed} placed. Thank you!</p>}
      {!orders ? <p>Loading…</p> : orders.length === 0 ? <p>No orders yet.</p> : (
        <ul>
          {orders.map(o => (
            <li key={o.id}>
              #{o.id} · {new Date(o.created_at).toLocaleString()} · {o.status} · {money(o.total_cents)} ·{' '}
              {o.items.map(i => `${i.quantity}× ${i.name}`).join(', ')}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
