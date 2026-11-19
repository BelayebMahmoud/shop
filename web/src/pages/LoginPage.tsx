import { useState, type FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router';
import { useAuth } from '../auth';

export default function LoginPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const from = (useLocation().state as { from?: string } | null)?.from ?? '/';
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await (mode === 'login' ? login(email, password) : register(email, password));
      navigate(from, { replace: true });
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <main>
      <h1>{mode === 'login' ? 'Log in' : 'Create account'}</h1>
      <form onSubmit={submit} className="stack">
        <label>Email <input type="email" required value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label>Password <input type="password" required minLength={8} value={password} onChange={e => setPassword(e.target.value)} /></label>
        {error && <p role="alert">{error}</p>}
        <button type="submit">{mode === 'login' ? 'Log in' : 'Create account'}</button>
      </form>
      <button className="link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? 'No account? Create one' : 'Have an account? Log in'}
      </button>
      <p className="muted">Demo: demo@example.com / demo1234</p>
    </main>
  );
}
