import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

// Labels reflect each match's separation from the top match, not fixed
// thresholds (probabilities are spread thin across 24 classes).
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
            Based on your course of study, personality, academic performance, and skills.
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
          // The degree's main career, shown because of the field of study even
          // when the student's interests rank it low — labelled, not scored.
          if (rec.core_path) {
            return (
              <div className="rec-card core-path" key={rec.career}>
                <div className="rec-rank">{idx + 1}</div>
                <div className="rec-body">
                  <div className="rec-title-row">
                    <h3>{rec.career}</h3>
                    <span className="match-label core-label">Core path for your degree</span>
                  </div>
                  <p className="core-path-note">
                    Always shown because it's the main career for your field of study —
                    your interests point more strongly to the matches above.
                  </p>
                </div>
              </div>
            );
          }

          const label = getConfidenceLabel(idx, rec.match_percentage, topPct);
          const barWidth = Math.round(rec.match_percentage);
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
                <div className="rec-confidence">{rec.match_percentage}% match</div>
                {rec.reasons && rec.reasons.length > 0 && (
                  <div className="rec-reasons">
                    <span className="rec-reasons-title">Why this fits you</span>
                    <ul>
                      {rec.reasons.map((reason, i) => (
                        <li key={i}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        <p className="results-note">
          Match scores are a relative fit, drawn from your interests, skills and course of
          study across the careers your degree can lead to — a guide, not an exact probability.
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