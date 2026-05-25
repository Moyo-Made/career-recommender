// src/pages/Results.jsx
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

// ---------------------------------------------------------------
// Confidence labels based on SEPARATION from the top match,
// not fixed thresholds (because probabilities span 12 classes).
// ---------------------------------------------------------------
function getConfidenceLabel(rank, pct, topPct) {
  if (rank === 0) return 'Strongest match';
  const ratio = pct / topPct;
  if (ratio >= 0.75) return 'Strong match';
  if (ratio >= 0.5) return 'Good match';
  return 'Possible match';
}

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { result, name } = location.state || {};

  if (!result || !result.recommendations) {
    return (
      <div className="page">
        <div className="container">
          <div className="empty">
            <p>No results to show yet.</p>
            <button className="btn" style={{ marginTop: 16 }} onClick={() => navigate('/assessment')}>
              Take the Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  const recs = result.recommendations;
  const topPct = recs[0].match_percentage;

  return (
    <div className="page">
      <div className="container">
        <div className="results-head">
          <div className="eyebrow">Your Results</div>
          <h1>{name && name !== 'Anonymous' ? `${name}, here are your top matches` : 'Your top career matches'}</h1>
          <p style={{ color: '#5a6b7f' }}>
            Based on your personality, academic performance, and skills.
          </p>
        </div>

        {!result.saved && (
          <div className="save-banner">
            <span>
              Want to keep these results and track how they change over time?
            </span>
            <span className="save-banner-actions">
              <Link className="btn small" to="/register" state={{ from: '/assessment' }}>Create account</Link>
              <Link className="btn small secondary" to="/login" state={{ from: '/assessment' }}>Log in</Link>
            </span>
          </div>
        )}

        {recs.map((rec, idx) => {
          const label = getConfidenceLabel(idx, rec.match_percentage, topPct);
          const barWidth = Math.round((rec.match_percentage / topPct) * 100);
          return (
            <div className={`rec-card ${idx === 0 ? 'top' : ''}`} key={rec.career}>
              <div className="rec-rank">{idx + 1}</div>
              <div className="rec-body">
                <div className="rec-title-row">
                  <h3>{rec.career}</h3>
                  <span className={`match-label ${idx === 0 ? 'top-label' : ''}`}>{label}</span>
                </div>
                <div className="match-bar">
                  <div className="fill" style={{ width: `${barWidth}%` }} />
                </div>
                <div className="rec-confidence">confidence {rec.match_percentage}%</div>
              </div>
            </div>
          );
        })}

        <p className="results-note">
          The bars show how your top matches compare to one another. Matches are ranked
          from a set of 12 career categories.
        </p>

        <div className="results-actions">
          <button className="btn secondary" onClick={() => navigate('/assessment')}>Retake Assessment</button>
          {user ? (
            <button className="btn" onClick={() => navigate('/dashboard')}>View My History</button>
          ) : (
            <button className="btn" onClick={() => navigate('/login', { state: { from: '/dashboard' } })}>Log in to save</button>
          )}
        </div>

        <p style={{ textAlign: 'center', color: '#5a6b7f', fontSize: '0.85rem', marginTop: 20 }}>
          These recommendations are a guide to support your decision, not a replacement for
          professional career counseling.
        </p>
      </div>
    </div>
  );
}