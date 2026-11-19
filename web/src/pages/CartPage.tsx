import { useState } from 'react';
import { useNavigate } from 'react-router';
import { ApiError, createOrder, money } from '../api';
import { useAuth } from '../auth';
import { useCart } from '../cart';

export default function CartPage() {
  const { lines, totalCents, setQty, clear } = useCart();
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const checkout = async () => {
    if (!token) return navigate('/login', { state: { from: '/cart' } });
    setBusy(true);
    setError(null);
    try {
      const order = await createOrder(lines.map(l => ({ product_id: l.productId, quantity: l.quantity })));
      clear();
      navigate('/orders', { state: { placed: order.id } });
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        logout();
        navigate('/login', { state: { from: '/cart' } });
      } else if (e instanceof ApiError && e.status === 409) {
        const ids = (e.detail as { product_ids: number[] }).product_ids;
        setError(`Not enough stock for: ${lines.filter(l => ids.includes(l.productId)).map(l => l.name).join(', ')}`);
      } else {
        setError((e as Error).message);
      }
    } finally {
      setBusy(false);
    }
  };

  if (lines.length === 0) return <main><h1>Cart</h1><p>Your cart is empty.</p></main>;

  return (
    <main>
      <h1>Cart</h1>
      <table>
        <thead><tr><th>Product</th><th>Price</th><th>Qty</th><th>Subtotal</th></tr></thead>
        <tbody>
          {lines.map(l => (
            <tr key={l.productId}>
              <td>{l.name}</td>
              <td>{money(l.priceCents)}</td>
              <td>
                <input aria-label={`Quantity of ${l.name}`} type="number" min={0} value={l.quantity}
                  onChange={e => setQty(l.productId, Number(e.target.value))} />
              </td>
              <td>{money(l.priceCents * l.quantity)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="price">Total: {money(totalCents)}</p>
      {error && <p role="alert">{error}</p>}
      <button onClick={checkout} disabled={busy}>{token ? 'Place order' : 'Log in to check out'}</button>
    </main>
  );
}
