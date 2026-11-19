import { BrowserRouter, Link, Route, Routes } from 'react-router';
import { useAuth } from './auth';
import { useCart } from './cart';
import CartPage from './pages/CartPage';
import LoginPage from './pages/LoginPage';
import OrdersPage from './pages/OrdersPage';
import ProductDetail from './pages/ProductDetail';
import ProductList from './pages/ProductList';

function Nav() {
  const { token, logout } = useAuth();
  const { count } = useCart();
  return (
    <nav>
      <Link to="/">Shop</Link>
      <Link to="/cart">Cart ({count})</Link>
      {token ? (
        <>
          <Link to="/orders">Orders</Link>
          <button className="link" onClick={logout}>Log out</button>
        </>
      ) : (
        <Link to="/login">Log in</Link>
      )}
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<ProductList />} />
        <Route path="/products/:id" element={<ProductDetail />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/orders" element={<OrdersPage />} />
      </Routes>
    </BrowserRouter>
  );
}
