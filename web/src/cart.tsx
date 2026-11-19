import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { Product } from './api';

export type CartLine = { productId: number; name: string; priceCents: number; quantity: number };

type Cart = {
  lines: CartLine[];
  count: number;
  totalCents: number; // display only: the server re-prices at checkout
  add: (p: Product, qty?: number) => void;
  setQty: (productId: number, qty: number) => void;
  clear: () => void;
};

const CART_KEY = 'shop.cart';
const CartContext = createContext<Cart | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>(() => JSON.parse(localStorage.getItem(CART_KEY) ?? '[]'));
  useEffect(() => localStorage.setItem(CART_KEY, JSON.stringify(lines)), [lines]);

  const add = (p: Product, qty = 1) =>
    setLines(ls =>
      ls.some(l => l.productId === p.id)
        ? ls.map(l => (l.productId === p.id ? { ...l, quantity: l.quantity + qty } : l))
        : [...ls, { productId: p.id, name: p.name, priceCents: p.price_cents, quantity: qty }],
    );
  const setQty = (productId: number, qty: number) =>
    setLines(ls =>
      qty <= 0 ? ls.filter(l => l.productId !== productId) : ls.map(l => (l.productId === productId ? { ...l, quantity: qty } : l)),
    );
  const clear = () => setLines([]);

  const count = lines.reduce((n, l) => n + l.quantity, 0);
  const totalCents = lines.reduce((s, l) => s + l.quantity * l.priceCents, 0);

  return <CartContext.Provider value={{ lines, count, totalCents, add, setQty, clear }}>{children}</CartContext.Provider>;
}

export function useCart(): Cart {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used inside CartProvider');
  return ctx;
}
