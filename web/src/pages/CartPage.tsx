import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { ApiError, createOrder, money } from '../api';
import { useAuth } from '../auth';
import { useCart } from '../cart';

export default function CartPage() {
  const { lines, totalCents, setQty, clear } = useCart();
  const { token, logout, can } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const checkout = async () => {
    if (!token) return navigate('/connexion', { state: { from: '/panier' } });
    setBusy(true);
    setError(null);
    try {
      const order = await createOrder(lines.map(l => ({ product_id: l.productId, quantity: l.quantity })));
      clear();
      navigate('/commandes', { state: { placed: order.id } });
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        logout();
        navigate('/connexion', { state: { from: '/panier' } });
      } else if (e instanceof ApiError && e.code === 'OUT_OF_STOCK') {
        const ids = (e.detail as { product_ids: number[] }).product_ids;
        const names = lines.filter(l => ids.includes(l.productId)).map(l => l.name).join(', ');
        setError(`Stock insuffisant pour : ${names}. Réduisez la quantité puis réessayez.`);
      } else if (e instanceof ApiError && e.status === 422) {
        setError('Quantités invalides : de 1 à 99 par produit, 50 produits au plus.');
      } else if (e instanceof ApiError && e.status === 403) {
        setError('Seul un compte client peut passer commande.');
      } else {
        setError('La commande n’a pas pu être enregistrée. Réessayez.');
      }
    } finally {
      setBusy(false);
    }
  };

  if (lines.length === 0) {
    return <main><h1>Panier</h1><p>Votre panier est vide.</p><Link to="/">Voir le catalogue</Link></main>;
  }

  return (
    <main>
      <h1>Panier</h1>
      <table>
        <caption className="sr-only">Contenu du panier</caption>
        <thead>
          <tr><th scope="col">Produit</th><th scope="col">Prix</th><th scope="col">Quantité</th><th scope="col">Sous-total</th></tr>
        </thead>
        <tbody>
          {lines.map(l => (
            <tr key={l.productId}>
              <td>{l.name}</td>
              <td>{money(l.priceCents)}</td>
              <td>
                <input aria-label={`Quantité de ${l.name}`} type="number" min={0} max={99} value={l.quantity}
                  onChange={e => setQty(l.productId, Number(e.target.value))} />
              </td>
              <td>{money(l.priceCents * l.quantity)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="price">Total estimé : {money(totalCents)}</p>
      <p className="muted">La remise (5 % dès 100 €, 10 % dès 200 €) et le total définitif sont calculés à la commande.</p>
      {error && <p role="alert">{error}</p>}
      <button type="button" onClick={checkout} disabled={busy || (token !== null && !can('CUSTOMER'))}>
        {token ? 'Commander' : 'Se connecter pour commander'}
      </button>
    </main>
  );
}
