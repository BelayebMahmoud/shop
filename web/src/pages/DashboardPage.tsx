import { useEffect, useState } from 'react';
import { getCategories, getDashboard, money, type Category, type Dashboard, type OrderStatus } from '../api';
import { STATUS_LABEL } from '../workflow';

export default function DashboardPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { getCategories().then(setCategories); }, []);
  useEffect(() => {
    getDashboard({ dateFrom: dateFrom || undefined, dateTo: dateTo || undefined, categoryId: categoryId ? Number(categoryId) : undefined })
      .then(d => { setData(d); setError(null); })
      .catch(() => setError('Période invalide : la date de début doit précéder la date de fin.'));
  }, [dateFrom, dateTo, categoryId]);

  return (
    <main>
      <h1>Tableau de bord</h1>
      <form className="filters" aria-label="Filtres du tableau de bord" onSubmit={e => e.preventDefault()}>
        <label>Du <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} /></label>
        <label>Au <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} /></label>
        <label>
          Catégorie
          <select value={categoryId} onChange={e => setCategoryId(e.target.value)}>
            <option value="">Toutes</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
      </form>
      {error && <p role="alert">{error}</p>}
      {!data ? <p>Chargement…</p> : (
        <div className="kpis">
          <section aria-labelledby="kpi-revenue">
            <h2 id="kpi-revenue">Chiffre d’affaires</h2>
            <p className="price" data-testid="revenue">{money(data.revenue_cents)}</p>
            <p className="muted">Commandes payées, expédiées et livrées, après remise.</p>
          </section>
          <section aria-labelledby="kpi-status">
            <h2 id="kpi-status">Commandes par statut</h2>
            <table>
              <tbody>
                {(Object.keys(STATUS_LABEL) as OrderStatus[]).map(s => (
                  <tr key={s}><th scope="row">{STATUS_LABEL[s]}</th><td data-testid={`count-${s}`}>{data.orders_by_status[s]}</td></tr>
                ))}
              </tbody>
            </table>
          </section>
          <section aria-labelledby="kpi-top">
            <h2 id="kpi-top">5 produits les plus vendus</h2>
            {data.top_products.length === 0 ? <p>Aucune vente.</p> : (
              <ol data-testid="top-products">
                {data.top_products.map(t => <li key={t.product_id}>{t.name} — {t.quantity}</li>)}
              </ol>
            )}
          </section>
          <section aria-labelledby="kpi-low">
            <h2 id="kpi-low">Stock faible (moins de 5)</h2>
            <p className="muted" data-testid="low-stock-total">{data.low_stock_total} produit(s)</p>
            <ul>{data.low_stock.map(p => <li key={p.id}>{p.name} ({p.sku}) : {p.stock}</li>)}</ul>
          </section>
        </div>
      )}
    </main>
  );
}
