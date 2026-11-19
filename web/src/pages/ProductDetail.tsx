import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router';
import { getProduct, money, type Product } from '../api';
import { useCart } from '../cart';

export default function ProductDetail() {
  const { id } = useParams();
  const { add } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    getProduct(Number(id)).then(setProduct).catch((e: Error) => setError(e.message));
  }, [id]);

  if (error) return <main><p role="alert">{error}</p></main>;
  if (!product) return <main><p>Loading…</p></main>;

  return (
    <main>
      <Link to="/">← All products</Link>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p className="price">{money(product.price_cents)}</p>
      <p className="muted">{product.stock} in stock</p>
      <label>
        Quantity{' '}
        <input type="number" min={1} max={product.stock} value={qty} onChange={e => setQty(Number(e.target.value))} />
      </label>{' '}
      <button disabled={product.stock === 0 || qty < 1} onClick={() => { add(product, qty); setAdded(true); }}>
        Add to cart
      </button>
      {added && <p role="status">Added. <Link to="/cart">Go to cart</Link></p>}
    </main>
  );
}
