import type { ReactNode } from 'react';
import { BrowserRouter, Link, Navigate, NavLink, Route, Routes, useLocation } from 'react-router';
import type { Role } from './api';
import { useAuth } from './auth';
import { useCart } from './cart';
import AdminOrdersPage from './pages/AdminOrdersPage';
import AdminProductsPage from './pages/AdminProductsPage';
import CartPage from './pages/CartPage';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import OrdersPage from './pages/OrdersPage';
import ProductDetail from './pages/ProductDetail';
import ProductList from './pages/ProductList';

function Nav() {
  const { token, user, logout, can } = useAuth();
  const { count } = useCart();
  return (
    <header>
      <nav aria-label="Navigation principale">
        <Link to="/" className="brand">Gestion commerciale</Link>
        <NavLink to="/">Catalogue</NavLink>
        {!can('STAFF', 'ADMIN') && <NavLink to="/panier">Panier ({count})</NavLink>}
        {can('CUSTOMER') && <NavLink to="/commandes">Mes commandes</NavLink>}
        {can('STAFF', 'ADMIN') && (
          <>
            <NavLink to="/back-office/commandes">Commandes</NavLink>
            <NavLink to="/back-office/produits">Produits</NavLink>
            <NavLink to="/back-office/tableau-de-bord">Tableau de bord</NavLink>
          </>
        )}
        <span className="spacer" />
        {token ? (
          <>
            {user && <span className="muted">{user.email} ({user.role})</span>}
            <button type="button" className="link" onClick={logout}>Se déconnecter</button>
          </>
        ) : (
          <NavLink to="/connexion">Se connecter</NavLink>
        )}
      </nav>
    </header>
  );
}

/** Route guard for the UI only; the API answers 401/403 on its own (FR-02). */
function RequireRole({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const { token, user, can } = useAuth();
  const location = useLocation();
  if (!token) return <Navigate to="/connexion" state={{ from: location.pathname }} replace />;
  if (!user) return <main><p>Chargement…</p></main>;
  if (!can(...roles)) return <main><h1>Accès refusé</h1><p>Votre rôle ne permet pas d’ouvrir cette page.</p></main>;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<ProductList />} />
        <Route path="/produits/:id" element={<ProductDetail />} />
        <Route path="/panier" element={<CartPage />} />
        <Route path="/connexion" element={<LoginPage />} />
        <Route path="/commandes" element={<RequireRole roles={['CUSTOMER']}><OrdersPage /></RequireRole>} />
        <Route
          path="/back-office/commandes"
          element={<RequireRole roles={['STAFF', 'ADMIN']}><AdminOrdersPage /></RequireRole>}
        />
        <Route
          path="/back-office/produits"
          element={<RequireRole roles={['STAFF', 'ADMIN']}><AdminProductsPage /></RequireRole>}
        />
        <Route
          path="/back-office/tableau-de-bord"
          element={<RequireRole roles={['STAFF', 'ADMIN']}><DashboardPage /></RequireRole>}
        />
        <Route path="*" element={<main><h1>Page introuvable</h1><Link to="/">Retour au catalogue</Link></main>} />
      </Routes>
    </BrowserRouter>
  );
}
