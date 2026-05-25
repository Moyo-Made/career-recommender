import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || '/dashboard';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.response?.data?.error || 'We were unable to log you in. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="container container-narrow">
        <div className="auth-card">
          <div className="eyebrow">Welcome back</div>
          <h1>Log in to CareerFit</h1>
          <p className="auth-sub">Access your saved assessments and track how your matches change over time.</p>

          {error && <div className="error-msg">{error}</div>}

          <form onSubmit={handleSubmit}>
            <label className="field-label">Email</label>
            <input
              className="text-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
            <label className="field-label">Password</label>
            <input
              className="text-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
            <button className="btn large" style={{ width: '100%', marginTop: 8 }} disabled={loading}>
              {loading ? <span className="spinner" /> : 'Log in'}
            </button>
          </form>

          <p className="auth-switch">
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
