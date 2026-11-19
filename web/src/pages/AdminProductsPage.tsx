import { useCallback, useEffect, useState, type FormEvent, type ReactNode } from 'react';
import {
  ApiError, createProduct, deleteProduct, getCategories, getProducts, money, updateProduct,
  type Category, type Product, type ProductInput,
} from '../api';
import ConfirmDialog from '../ConfirmDialog';
import { fieldErrors } from '../workflow';

type Form = { sku: string; name: string; description: string; price: string; stock: string; category_id: string };
const EMPTY: Form = { sku: '', name: '', description: '', price: '', stock: '', category_id: '' };

function toInput(f: Form): ProductInput {
  // Values are sent as typed: the API validates them and answers field by field (422).
  const price = f.price.trim() === '' ? NaN : Math.round(Number(f.price.replace(',', '.')) * 100);
  return {
    sku: f.sku.trim(), name: f.name.trim(), description: f.description,
    price_cents: Number.isFinite(price) ? price : (f.price as unknown as number),
    stock: f.stock.trim() === '' ? (f.stock as unknown as number) : Number(f.stock),
    category_id: Number(f.category_id) || (f.category_id as unknown as number),
  };
}

const FIELD_OF: Record<string, keyof Form> = { price_cents: 'price', stock: 'stock', sku: 'sku', name: 'name', category_id: 'category_id', description: 'description' };

export default function AdminProductsPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[] | null>(null);
  const [q, setQ] = useState('');
  const [form, setForm] = useState<Form>(EMPTY);
  const [editing, setEditing] = useState<Product | null>(null);
  const [errors, setErrors] = useState<Partial<Record<keyof Form, string>>>({});
  const [message, setMessage] = useState<{ kind: 'status' | 'alert'; text: string } | null>(null);
  const [toDelete, setToDelete] = useState<Product | null>(null);

  const load = useCallback(() => getProducts({ q: q.trim() || undefined, limit: 50 }).then(p => setProducts(p.items)), [q]);
  useEffect(() => { getCategories().then(setCategories); }, []);
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t); }, [load]);

  const set = (k: keyof Form) => (v: string) => setForm(f => ({ ...f, [k]: v }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setMessage(null);
    try {
      const saved = editing ? await updateProduct(editing.id, toInput(form)) : await createProduct(toInput(form));
      setMessage({ kind: 'status', text: `Produit « ${saved.name} » ${editing ? 'modifié' : 'créé'}.` });
      setForm(EMPTY);
      setEditing(null);
      load();
    } catch (err) {
      if (err instanceof ApiError && (err.status === 422 || err.code === 'DUPLICATE')) {
        const byApiField = fieldErrors(err.detail);
        const mapped: Partial<Record<keyof Form, string>> = {};
        for (const [k, v] of Object.entries(byApiField)) mapped[FIELD_OF[k] ?? 'name'] = v;
        setErrors(mapped);
        setMessage({ kind: 'alert', text: 'Le formulaire contient des erreurs.' });
      } else if (err instanceof ApiError && err.code === 'CATEGORY_NOT_FOUND') {
        setErrors({ category_id: 'Catégorie inconnue.' });
      } else {
        setMessage({ kind: 'alert', text: 'Enregistrement impossible.' });
      }
    }
  };

  const edit = (p: Product) => {
    setEditing(p);
    setErrors({});
    setForm({ sku: p.sku, name: p.name, description: p.description, price: (p.price_cents / 100).toFixed(2),
      stock: String(p.stock), category_id: String(p.category_id) });
  };

  const confirmDelete = async () => {
    const p = toDelete;
    setToDelete(null);
    if (!p) return;
    try {
      await deleteProduct(p.id);
      setMessage({ kind: 'status', text: `Produit « ${p.name} » supprimé.` });
    } catch (err) {
      const text = err instanceof ApiError && err.code === 'PRODUCT_IN_USE'
        ? `« ${p.name} » figure dans des commandes : il ne peut pas être supprimé.`
        : 'Suppression impossible.';
      setMessage({ kind: 'alert', text });
    }
    load();
  };

  const field = (k: keyof Form, label: string, input: ReactNode) => (
    <div className="field">
      <label htmlFor={`f-${k}`}>{label}</label>
      {input}
      {errors[k] && <p id={`e-${k}`} className="error">{errors[k]}</p>}
    </div>
  );
  const attrs = (k: keyof Form) => ({
    id: `f-${k}`, value: form[k], 'aria-invalid': errors[k] ? true : undefined,
    'aria-describedby': errors[k] ? `e-${k}` : undefined,
    onChange: (e: { target: { value: string } }) => set(k)(e.target.value),
  });

  return (
    <main>
      <h1>Produits (back-office)</h1>
      <form onSubmit={submit} className="product-form" noValidate aria-label={editing ? 'Modifier le produit' : 'Nouveau produit'}>
        <h2>{editing ? `Modifier « ${editing.name} »` : 'Nouveau produit'}</h2>
        {field('sku', 'Référence (SKU)', <input {...attrs('sku')} />)}
        {field('name', 'Nom', <input {...attrs('name')} />)}
        {field('description', 'Description', <textarea {...attrs('description')} />)}
        {field('price', 'Prix (€)', <input inputMode="decimal" {...attrs('price')} />)}
        {field('stock', 'Stock', <input inputMode="numeric" {...attrs('stock')} />)}
        {field('category_id', 'Catégorie', (
          <select {...attrs('category_id')}>
            <option value="">Choisir…</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        ))}
        <div className="actions">
          <button type="submit">{editing ? 'Enregistrer' : 'Créer le produit'}</button>
          {editing && <button type="button" onClick={() => { setEditing(null); setForm(EMPTY); setErrors({}); }}>Annuler la modification</button>}
        </div>
      </form>
      {message && <p role={message.kind}>{message.text}</p>}

      <h2>Liste des produits</h2>
      <label>Filtrer <input type="search" value={q} onChange={e => setQ(e.target.value)} /></label>
      {!products ? <p>Chargement…</p> : (
        <table>
          <caption className="sr-only">Produits</caption>
          <thead>
            <tr><th scope="col">SKU</th><th scope="col">Nom</th><th scope="col">Prix</th><th scope="col">Stock</th><th scope="col">Actions</th></tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.id} data-product-id={p.id}>
                <td>{p.sku}</td><td>{p.name}</td><td>{money(p.price_cents)}</td><td>{p.stock}</td>
                <td className="actions">
                  <button type="button" onClick={() => edit(p)} aria-label={`Modifier ${p.name}`}>Modifier</button>
                  <button type="button" className="danger" onClick={() => setToDelete(p)} aria-label={`Supprimer ${p.name}`}>Supprimer</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <ConfirmDialog
        open={toDelete !== null}
        title="Supprimer le produit ?"
        message={toDelete ? `« ${toDelete.name} » sera supprimé définitivement.` : ''}
        confirmLabel="Supprimer définitivement"
        onConfirm={confirmDelete}
        onCancel={() => setToDelete(null)}
      />
    </main>
  );
}
