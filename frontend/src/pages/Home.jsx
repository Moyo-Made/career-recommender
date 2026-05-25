import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Home() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  // The marketing landing is for visitors. While a saved session is being
  // restored, hold off rendering so we don't flash the pitch at a member.
  if (loading) {
    return (
      <div className="page">
        <div className="container">
          <div className="empty"><span className="spinner spinner-dark" /></div>
        </div>
      </div>
    );
  }
  // A logged-in member's home base is their dashboard, not the sales pitch.
  if (user) return <Navigate to="/dashboard" replace />;

  return (
    <div className="page">
      <div className="container">
        <div className="hero">
          <h1>Discover the career path that fits who you are</h1>
          <p>
            An AI-powered recommender that analyzes your personality, academic
            performance, and skills to suggest careers aligned with your strengths —
            built for Nigerian university students.
          </p>
          <div className="actions">
            <button className="btn large" onClick={() => navigate('/assessment')}>
              Start Assessment
            </button>
            <button className="btn secondary large" onClick={() => navigate('/register')}>
              Create free account
            </button>
          </div>
        </div>

        <div className="feature-grid">
          <div className="feature">
            <div className="num">01</div>
            <h3>Personality (RIASEC)</h3>
            <p>A short interest inventory based on Holland's RIASEC model maps your vocational personality across six dimensions.</p>
          </div>
          <div className="feature">
            <div className="num">02</div>
            <h3>Academic & Skills</h3>
            <p>Your CGPA and self-assessed skills add the practical context that personality alone cannot capture.</p>
          </div>
          <div className="feature">
            <div className="num">03</div>
            <h3>AI Recommendation</h3>
            <p>A trained Random Forest model analyzes all your inputs together and ranks the careers that best match your profile.</p>
          </div>
        </div>
      </div>
    </div>
  );
}