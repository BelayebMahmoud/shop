import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { getProducts, money, type ProductPage } from '../api';

export default function ProductList() {
  const [q, setQ] = useState('');
  const [page, setPage] = useState<ProductPage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(() => {
      getProducts(q).then(setPage).catch((e: Error) => setError(e.message));
    }, 250); // debounce search
    return () => clearTimeout(t);
  }, [q]);

  return (
    <main>
      <h1>Products</h1>
      <input aria-label="Search products" placeholder="Search products" value={q} onChange={e => setQ(e.target.value)} />
      {error && <p role="alert">{error}</p>}
      {!page ? (
        <p>Loading…</p>
      ) : (
        <ul className="grid">
          {page.items.map(p => (
            <li key={p.id} className="card">
              <Link to={`/products/${p.id}`}>
                <h2>{p.name}</h2>
              </Link>
              <p>{money(p.price_cents)}</p>
              <p className="muted">{p.stock > 0 ? `${p.stock} in stock` : 'Out of stock'}</p>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
