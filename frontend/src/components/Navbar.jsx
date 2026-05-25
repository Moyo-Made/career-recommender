import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  function handleLogout() {
    closeMenu();
    logout();
    navigate('/');
  }

  return (
    <nav className="navbar">
      <div className="container">
        <NavLink to="/" className="brand" onClick={closeMenu}>
          <img src="/logo.png" alt="CareerFit" className="brand-logo" />
          CareerFit
        </NavLink>

        <button
          className={`nav-toggle ${menuOpen ? 'open' : ''}`}
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Toggle navigation menu"
          aria-expanded={menuOpen}
        >
          <span />
          <span />
          <span />
        </button>

        <div className={`nav-right ${menuOpen ? 'open' : ''}`}>
          <div className="nav-links">
            {user ? (
              <NavLink to="/dashboard" onClick={closeMenu}>Dashboard</NavLink>
            ) : (
              <NavLink to="/" end onClick={closeMenu}>Home</NavLink>
            )}
            <NavLink to="/assessment" onClick={closeMenu}>Assessment</NavLink>
          </div>

          {user ? (
            <div className="nav-auth">
              <div className="nav-user" title={user.email}>
                <span className="nav-avatar" aria-hidden="true">
                  {user.name.trim().charAt(0).toUpperCase()}
                </span>
                <span className="nav-user-name">{user.name.split(' ')[0]}</span>
              </div>
              <button className="nav-logout" onClick={handleLogout}>Log out</button>
            </div>
          ) : (
            <div className="nav-auth">
              <NavLink to="/login" className="nav-login" onClick={closeMenu}>Log in</NavLink>
              <NavLink to="/register" className="nav-cta" onClick={closeMenu}>Sign up</NavLink>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
