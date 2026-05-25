import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

// Gate a route behind login. While the session is being restored we
// show a light placeholder so we don't flash the login page.
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="page">
        <div className="container">
          <div className="empty"><span className="spinner spinner-dark" /></div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return children;
}
