import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getCategories, getProducts, money, type Category, type ProductPage } from '../api';

const PAGE_SIZE = 20;
const euros = (value: string) => (value === '' ? undefined : Math.round(Number(value.replace(',', '.')) * 100));

export default function ProductList() {
  const [q, setQ] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [inStock, setInStock] = useState(false);
  const [offset, setOffset] = useState(0);
  const [categories, setCategories] = useState<Category[]>([]);
  const [page, setPage] = useState<ProductPage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      setError(null);
      getProducts({
        q: q.trim() || undefined,
        categoryId: categoryId ? Number(categoryId) : undefined,
        minPriceCents: euros(minPrice),
        maxPriceCents: euros(maxPrice),
        inStock,
        limit: PAGE_SIZE,
        offset,
      })
        .then(setPage)
        .catch(() => setError('Filtres invalides : vérifiez les prix (le minimum ne peut pas dépasser le maximum).'));
    }, 250); // debounce typing
    return () => clearTimeout(t);
  }, [q, categoryId, minPrice, maxPrice, inStock, offset]);

  const reset = (setter: (v: string) => void) => (v: string) => {
    setter(v);
    setOffset(0);
  };

  return (
    <main>
      <h1>Catalogue</h1>
      <form className="filters" role="search" aria-label="Filtres du catalogue" onSubmit={e => e.preventDefault()}>
        <label>
          Rechercher
          <input type="search" value={q} onChange={e => reset(setQ)(e.target.value)} placeholder="Nom du produit" />
        </label>
        <label>
          Catégorie
          <select value={categoryId} onChange={e => reset(setCategoryId)(e.target.value)}>
            <option value="">Toutes</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
        <label>
          Prix min (€)
          <input inputMode="decimal" value={minPrice} onChange={e => reset(setMinPrice)(e.target.value)} />
        </label>
        <label>
          Prix max (€)
          <input inputMode="decimal" value={maxPrice} onChange={e => reset(setMaxPrice)(e.target.value)} />
        </label>
        <label className="inline">
          <input type="checkbox" checked={inStock} onChange={e => { setInStock(e.target.checked); setOffset(0); }} />
          En stock uniquement
        </label>
      </form>
      {error && <p role="alert">{error}</p>}
      {!page ? (
        <p>Chargement…</p>
      ) : (
        <>
          <p role="status" className="muted">{page.total} produit(s)</p>
          <ul className="grid">
            {page.items.map(p => (
              <li key={p.id} className="card">
                <h2><Link to={`/produits/${p.id}`}>{p.name}</Link></h2>
                <p>{money(p.price_cents)}</p>
                <p className="muted">{p.stock > 0 ? `${p.stock} en stock` : 'Rupture de stock'}</p>
              </li>
            ))}
          </ul>
          <div className="pager">
            <button type="button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}>
              Page précédente
            </button>
            <span>
              Page {offset / PAGE_SIZE + 1} / {Math.max(1, Math.ceil(page.total / PAGE_SIZE))}
            </span>
            <button type="button" disabled={offset + PAGE_SIZE >= page.total} onClick={() => setOffset(offset + PAGE_SIZE)}>
              Page suivante
            </button>
          </div>
        </>
      )}
    </main>
  );
}
