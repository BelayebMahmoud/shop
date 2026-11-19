import { useCallback, useEffect, useState } from 'react';
import { useLocation } from 'react-router';
import { cancelOrder, getOrders, money, type Order } from '../api';
import { STATUS_LABEL } from '../workflow';

export default function OrdersPage() {
  const placed = (useLocation().state as { placed?: number } | null)?.placed;
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(() => getOrders().then(setOrders), []);
  useEffect(() => { load(); }, [load]);

  const cancel = async (o: Order) => {
    if (!window.confirm(`Annuler la commande n° ${o.id} ?`)) return;
    try {
      await cancelOrder(o.id);
      setMessage(`Commande n° ${o.id} annulée.`);
    } catch {
      setMessage(`La commande n° ${o.id} ne peut plus être annulée.`);
    }
    load();
  };

  return (
    <main>
      <h1>Mes commandes</h1>
      {placed && <p role="status">Commande n° {placed} enregistrée. Merci !</p>}
      {message && <p role="status">{message}</p>}
      {!orders ? <p>Chargement…</p> : orders.length === 0 ? <p>Aucune commande pour l’instant.</p> : (
        <table>
          <caption className="sr-only">Mes commandes</caption>
          <thead>
            <tr>
              <th scope="col">N°</th><th scope="col">Date</th><th scope="col">Articles</th><th scope="col">Remise</th>
              <th scope="col">Total</th><th scope="col">Statut</th><th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => (
              <tr key={o.id} data-order-id={o.id}>
                <td>{o.id}</td>
                <td>{new Date(o.created_at).toLocaleString('fr-FR')}</td>
                <td>{o.items.map(i => `${i.quantity} × ${i.name}`).join(', ')}</td>
                <td>{money(o.discount_cents)}</td>
                <td>{money(o.total_cents)}</td>
                <td>{STATUS_LABEL[o.status]}</td>
                <td>
                  {o.status === 'PLACED' && (
                    <button type="button" onClick={() => cancel(o)}>Annuler la commande n° {o.id}</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
