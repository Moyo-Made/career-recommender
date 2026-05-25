import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useHistory } from '../context/HistoryContext';
import {
  ResponsiveContainer,
  BarChart, Bar, Cell, LabelList,
  LineChart, Line, Legend,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts';

// Brand palette for chart series (navy, blue, gold)
const SERIES_COLORS = ['#0f2d52', '#1d5fb0', '#c8901e'];

export default function Dashboard() {
  const { user } = useAuth();
  const { history, loading, error, refresh } = useHistory();

  // Fetch only when the cache is empty; revisits reuse the cached data, so we
  // no longer refetch (and flash a spinner) on every navigation back here.
  useEffect(() => {
    if (history === null) refresh();
  }, [history, refresh]);

  // `history === null` means "not loaded yet" — treat it as loading so the
  // first visit shows a spinner instead of a one-frame empty flash.
  const showSpinner = loading || history === null;

  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  }

  function shortDate(iso) {
    try {
      return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return iso;
    }
  }

  // ---- Derived data for the charts -------------------------------
  // Backend returns history newest-first.
  const hasData = history && history.length > 0;
  const latest = hasData ? history[0] : null;

  const sortedAsc = hasData
    ? [...history].sort((a, b) => new Date(a.date_generated) - new Date(b.date_generated))
    : [];

  // Latest assessment -> bar chart (top matches by %)
  const latestBars = latest
    ? latest.recommendations.map((r) => ({ career: r.career, match: r.match_percentage }))
    : [];

  // Trend -> follow the careers from the latest assessment across past ones
  const trackedCareers = latest ? latest.recommendations.map((r) => r.career) : [];
  const trendData = sortedAsc.map((item) => {
    const row = { date: shortDate(item.date_generated) };
    trackedCareers.forEach((c) => {
      const found = item.recommendations.find((r) => r.career === c);
      row[c] = found ? found.match_percentage : null;
    });
    return row;
  });

  return (
    <div className="page">
      <div className="container">
        <div className="assess-header">
          <h1>{user ? `Welcome back, ${user.name.split(' ')[0]}` : 'Your Dashboard'}</h1>
          <p>Your saved assessments and how your career matches are trending.</p>
        </div>

        {error && <div className="error-msg">{error}</div>}

        {showSpinner && (
          <div className="empty"><span className="spinner spinner-dark" /></div>
        )}

        {!showSpinner && history && history.length === 0 && (
          <div className="empty">
            <p>You haven't taken an assessment yet.</p>
            <Link className="btn" style={{ marginTop: 16 }} to="/assessment">
              Take the Assessment
            </Link>
          </div>
        )}

        {hasData && (
          <>
            {/* Summary stat cards */}
            <div className="stat-grid">
              <div className="stat-card">
                <div className="stat-value">{history.length}</div>
                <div className="stat-label">Assessments taken</div>
              </div>
              <div className="stat-card">
                <div className="stat-value stat-career">{latest.recommendations[0].career}</div>
                <div className="stat-label">
                  Current top match · {latest.recommendations[0].match_percentage}%
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-value stat-date">{shortDate(latest.date_generated)}</div>
                <div className="stat-label">Last assessment</div>
              </div>
            </div>

            {/* Latest match bar chart */}
            <div className="chart-card">
              <h3 className="chart-title">Your latest top matches</h3>
              <ResponsiveContainer width="100%" height={Math.max(160, latestBars.length * 56)}>
                <BarChart
                  data={latestBars}
                  layout="vertical"
                  margin={{ top: 8, right: 48, bottom: 8, left: 8 }}
                >
                  <CartesianGrid horizontal={false} stroke="#eef2f7" />
                  <XAxis
                    type="number"
                    domain={[0, 100]}
                    tickFormatter={(v) => `${v}%`}
                    tick={{ fill: '#5a6b7f', fontSize: 12 }}
                    stroke="#d9e2ec"
                  />
                  <YAxis
                    type="category"
                    dataKey="career"
                    width={150}
                    tick={{ fill: '#16202e', fontSize: 13 }}
                    stroke="#d9e2ec"
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(29, 95, 176, 0.06)' }}
                    formatter={(v) => [`${v}%`, 'Match']}
                    contentStyle={{ borderRadius: 10, border: '1px solid #d9e2ec', fontSize: 13 }}
                  />
                  <Bar dataKey="match" radius={[0, 6, 6, 0]} barSize={22}>
                    {latestBars.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? '#0f2d52' : '#4a8bd4'} />
                    ))}
                    <LabelList
                      dataKey="match"
                      position="right"
                      formatter={(v) => `${v}%`}
                      style={{ fill: '#5a6b7f', fontSize: 12, fontWeight: 600 }}
                    />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Trend over time — only meaningful with 2+ assessments */}
            {sortedAsc.length >= 2 ? (
              <div className="chart-card">
                <h3 className="chart-title">How your top matches changed over time</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData} margin={{ top: 8, right: 24, bottom: 8, left: -8 }}>
                    <CartesianGrid stroke="#eef2f7" />
                    <XAxis dataKey="date" tick={{ fill: '#5a6b7f', fontSize: 12 }} stroke="#d9e2ec" />
                    <YAxis
                      domain={[0, 100]}
                      tickFormatter={(v) => `${v}%`}
                      tick={{ fill: '#5a6b7f', fontSize: 12 }}
                      stroke="#d9e2ec"
                    />
                    <Tooltip
                      formatter={(v) => (v == null ? ['—', ''] : [`${v}%`, ''])}
                      contentStyle={{ borderRadius: 10, border: '1px solid #d9e2ec', fontSize: 13 }}
                    />
                    <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
                    {trackedCareers.map((career, i) => (
                      <Line
                        key={career}
                        type="monotone"
                        dataKey={career}
                        stroke={SERIES_COLORS[i % SERIES_COLORS.length]}
                        strokeWidth={2.5}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                        connectNulls
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="chart-hint">
                Take the assessment again over time to unlock a trend chart of how your
                top matches evolve.
              </p>
            )}

            {/* Full history list */}
            <h3 className="history-heading">Full history</h3>
            {history.map((item) => (
              <div className="history-item" key={item._id}>
                <div className="date">{formatDate(item.date_generated)}</div>
                <div className="history-careers">
                  {item.recommendations.map((rec) => (
                    <span className="career-chip" key={rec.career}>
                      {rec.career}<span className="pct">{rec.match_percentage}%</span>
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
