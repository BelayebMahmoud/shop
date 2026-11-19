import { useState, type FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router';
import { ApiError } from '../api';
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
      if (err instanceof ApiError && err.status === 401) setError('Email ou mot de passe incorrect.');
      else if (err instanceof ApiError && err.status === 409) setError('Un compte existe déjà avec cet email.');
      else if (err instanceof ApiError && err.status === 422) setError('Email invalide ou mot de passe trop court (8 caractères minimum).');
      else setError('Connexion impossible. Réessayez.');
    }
  };

  const title = mode === 'login' ? 'Se connecter' : 'Créer un compte';
  return (
    <main>
      <h1>{title}</h1>
      <form onSubmit={submit} className="stack">
        <label>Email <input type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} /></label>
        <label>
          Mot de passe{' '}
          <input type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} required minLength={8}
            value={password} onChange={e => setPassword(e.target.value)} />
        </label>
        {error && <p role="alert">{error}</p>}
        <button type="submit">{title}</button>
      </form>
      <button type="button" className="link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? 'Pas encore de compte ? En créer un' : 'Déjà un compte ? Se connecter'}
      </button>
      <p className="muted">Démonstration : demo@example.com / demo1234</p>
    </main>
  );
}
