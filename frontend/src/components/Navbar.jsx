import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <nav className="navbar">
      <div className="container">
        <NavLink to="/" className="brand">
          <img src="/logo.png" alt="CareerFit" className="brand-logo" />
          CareerFit
        </NavLink>

        <div className="nav-right">
          <div className="nav-links">
            {user ? (
              <NavLink to="/dashboard">Dashboard</NavLink>
            ) : (
              <NavLink to="/" end>Home</NavLink>
            )}
            <NavLink to="/assessment">Assessment</NavLink>
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
              <NavLink to="/login" className="nav-login">Log in</NavLink>
              <NavLink to="/register" className="nav-cta">Sign up</NavLink>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
