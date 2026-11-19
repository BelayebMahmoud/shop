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
    getProduct(Number(id)).then(setProduct).catch(() => setError('Ce produit n’existe pas.'));
  }, [id]);

  if (error) return <main><h1>Produit introuvable</h1><p role="alert">{error}</p><Link to="/">Retour au catalogue</Link></main>;
  if (!product) return <main><p>Chargement…</p></main>;

  return (
    <main>
      <Link to="/">← Retour au catalogue</Link>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p className="price">{money(product.price_cents)}</p>
      <p className="muted">{product.stock > 0 ? `${product.stock} en stock` : 'Rupture de stock'}</p>
      <label>
        Quantité{' '}
        <input type="number" min={1} max={99} value={qty} onChange={e => setQty(Number(e.target.value))} />
      </label>{' '}
      <button type="button" disabled={product.stock === 0 || qty < 1 || qty > 99}
        onClick={() => { add(product, qty); setAdded(true); }}>
        Ajouter au panier
      </button>
      {added && <p role="status">Ajouté au panier. <Link to="/panier">Voir le panier</Link></p>}
    </main>
  );
}
