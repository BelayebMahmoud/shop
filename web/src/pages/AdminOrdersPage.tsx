import { useCallback, useEffect, useState } from 'react';
import { ApiError, changeStatus, getOrders, money, type Order, type OrderStatus } from '../api';
import { NEXT, STATUS_LABEL } from '../workflow';

const PAGE_SIZE = 50; // ANO-09: one page at a time, filtered by the API

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [status, setStatus] = useState<OrderStatus | ''>('');
  const [offset, setOffset] = useState(0);
  const [message, setMessage] = useState<{ kind: 'status' | 'alert'; text: string } | null>(null);

  const load = useCallback(
    () => getOrders({ status: status || undefined, limit: PAGE_SIZE, offset }).then(setOrders),
    [status, offset],
  );
  useEffect(() => { load(); }, [load]);

  const move = async (order: Order, to: OrderStatus) => {
    try {
      await changeStatus(order.id, to);
      setMessage({ kind: 'status', text: `Commande n° ${order.id} : ${STATUS_LABEL[to]}.` });
    } catch (e) {
      const why = e instanceof ApiError && e.code === 'INVALID_TRANSITION' ? 'transition non autorisée' : 'erreur';
      setMessage({ kind: 'alert', text: `Commande n° ${order.id} : ${why}.` });
    }
    load();
  };

  const shown = orders;
  return (
    <main>
      <h1>Commandes (back-office)</h1>
      <label>
        Statut{' '}
        <select value={status} onChange={e => { setStatus(e.target.value as OrderStatus | ''); setOffset(0); }}>
          <option value="">Tous</option>
          {Object.entries(STATUS_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </label>
      {message && <p role={message.kind}>{message.text}</p>}
      {!shown ? <p>Chargement…</p> : shown.length === 0 ? <p>Aucune commande.</p> : (
        <table>
          <caption className="sr-only">Toutes les commandes</caption>
          <thead>
            <tr>
              <th scope="col">N°</th><th scope="col">Client</th><th scope="col">Date</th><th scope="col">Total</th>
              <th scope="col">Statut</th><th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {shown.map(o => (
              <tr key={o.id} data-order-id={o.id}>
                <td>{o.id}</td>
                <td>{o.user_id}</td>
                <td>{new Date(o.created_at).toLocaleString('fr-FR')}</td>
                <td>{money(o.total_cents)}</td>
                <td data-testid="status">{STATUS_LABEL[o.status]}</td>
                <td className="actions">
                  {NEXT[o.status].map(t => (
                    <button type="button" key={t.to} onClick={() => move(o, t.to)} aria-label={`${t.label} — commande n° ${o.id}`}>
                      {t.label}
                    </button>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="pager">
        <button type="button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}>
          Commandes plus récentes
        </button>
        <span>Commandes {offset + 1} à {offset + (shown?.length ?? 0)}</span>
        <button type="button" disabled={(shown?.length ?? 0) < PAGE_SIZE} onClick={() => setOffset(offset + PAGE_SIZE)}>
          Commandes plus anciennes
        </button>
      </div>
    </main>
  );
}
