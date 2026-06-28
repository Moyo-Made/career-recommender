import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { RIASEC_QUESTIONS, SKILLS, COURSES, calculateRiasecScores } from '../assessmentData';
import CourseCombobox from '../components/CourseCombobox';
import { getRecommendations } from '../api';

// Free text covers "not listed", so the explicit sentinel isn't shown in the list.
const courseOptions = COURSES.filter((c) => c !== 'Other / Not listed');
import { useAuth } from '../auth/AuthContext';
import { useHistory } from '../context/HistoryContext';

const SCALE = [
  { v: 1, label: 'Strongly disagree' },
  { v: 2, label: 'Disagree' },
  { v: 3, label: 'Neutral' },
  { v: 4, label: 'Agree' },
  { v: 5, label: 'Strongly agree' },
];
const SKILL_SCALE = [1, 2, 3, 4, 5];

const PHASE = {
  INTRO: 'intro',
  INTERESTS: 'interests',
  SKILLS: 'skills',
  COURSE: 'course',
  CGPA: 'cgpa',
  ANALYZING: 'analyzing',
};

export default function Assessment() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { refresh: refreshHistory } = useHistory();

  const [phase, setPhase] = useState(PHASE.INTRO);
  const [qIndex, setQIndex] = useState(0); // which interest question
  const [slideOut, setSlideOut] = useState(false); // for transition

  const [riasecAnswers, setRiasecAnswers] = useState({});
  const [skillAnswers, setSkillAnswers] = useState({});
  const [course, setCourse] = useState('');
  const [cgpa, setCgpa] = useState('');
  const [error, setError] = useState('');

  const totalInterest = RIASEC_QUESTIONS.length;

  // ---- INTEREST question answering with auto-advance ----
  function answerInterest(value) {
    const q = RIASEC_QUESTIONS[qIndex];
    setRiasecAnswers((prev) => ({ ...prev, [q.id]: value }));

    // brief slide-out, then move forward
    setSlideOut(true);
    setTimeout(() => {
      if (qIndex < totalInterest - 1) {
        setQIndex(qIndex + 1);
      } else {
        setPhase(PHASE.SKILLS);
      }
      setSlideOut(false);
    }, 220);
  }

  function goBackInterest() {
    if (qIndex > 0) {
      setQIndex(qIndex - 1);
    } else {
      setPhase(PHASE.COURSE);
    }
  }

  function setSkill(id, value) {
    setSkillAnswers((prev) => ({ ...prev, [id]: value }));
  }

  // ---- Final submission ----
  async function handleSubmit() {
    setError('');
    const cgpaNum = parseFloat(cgpa);
    if (isNaN(cgpaNum) || cgpaNum < 0 || cgpaNum > 5) {
      setError('Please enter a valid CGPA between 0.0 and 5.0.');
      return;
    }

    const riasecScores = calculateRiasecScores(riasecAnswers);
    const payload = {
      ...riasecScores,
      CGPA: cgpaNum,
      ...skillAnswers,
      Course: course,
    };

    setPhase(PHASE.ANALYZING);
    try {
      const result = await getRecommendations(payload);
      // A new assessment is now saved server-side; warm the cached history so
      // the dashboard shows it without a stale read.
      if (user) refreshHistory();
      // small delay so the "analyzing" moment is felt
      setTimeout(() => {
        navigate('/results', { state: { result, name: user?.name || 'Anonymous' } });
      }, 1200);
    } catch (err) {
      setPhase(PHASE.CGPA);
      setError(
        err.response?.data?.error ||
        'We were unable to generate your results. Please check your connection and try again.'
      );
    }
  }


  const answeredInterest = Object.keys(riasecAnswers).length;
  const answeredSkills = Object.keys(skillAnswers).length;
  const overallAnswered = answeredInterest + answeredSkills + (course !== '' ? 1 : 0) + (cgpa !== '' ? 1 : 0);
  const overallTotal = totalInterest + SKILLS.length + 2;
  const overallPct = Math.round((overallAnswered / overallTotal) * 100);

  return (
    <div className="page">
      <div className="container container-narrow">
        {phase === PHASE.INTRO && (
          <div className="step-fade">
            <div className="intro-card">
              <div className="eyebrow">Career Assessment</div>
              <h1>Let's find careers that fit you</h1>
              <p className="intro-lead">
                You'll answer a few short questions about your interests and skills.
                It takes about 4 minutes. Answer honestly — there are no right or wrong answers.
              </p>

              {user ? (
                <div className="save-note save-note-on">
                  Signed in as <strong>{user.name}</strong> — your results will be saved to your dashboard.
                </div>
              ) : (
                <div className="save-note save-note-off">
                  You're not logged in, so this result won't be saved.{' '}
                  <Link to="/login" state={{ from: '/assessment' }}>Log in</Link> or{' '}
                  <Link to="/register" state={{ from: '/assessment' }}>create an account</Link> to track your history.
                </div>
              )}

              <button className="btn large" style={{ marginTop: 28, width: '100%' }} onClick={() => setPhase(PHASE.COURSE)}>
                Begin Assessment
              </button>
            </div>
          </div>
        )}
        {phase === PHASE.INTERESTS && (
          <div>
            <div className="step-top">
              <button className="back-link" onClick={goBackInterest}>← Back</button>
              <span className="step-count">Question {qIndex + 1} of {totalInterest}</span>
            </div>
            <div className="progress big"><div className="bar" style={{ width: `${((qIndex) / totalInterest) * 100}%` }} /></div>

            <div className={`question-screen ${slideOut ? 'slide-out' : 'slide-in'}`}>
              <div className="q-big">{RIASEC_QUESTIONS[qIndex].text}</div>
              <div className="scale-stack">
                {SCALE.map((s) => (
                  <button
                    key={s.v}
                    className={`scale-card ${riasecAnswers[RIASEC_QUESTIONS[qIndex].id] === s.v ? 'selected' : ''}`}
                    onClick={() => answerInterest(s.v)}
                  >
                    <span className="scale-num">{s.v}</span>
                    <span>{s.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {phase === PHASE.SKILLS && (
          <div className="step-fade">
            <div className="step-top">
              <button className="back-link" onClick={() => { setPhase(PHASE.INTERESTS); setQIndex(totalInterest - 1); }}>← Back</button>
              <span className="step-count">Part 3 of 4 · Skills</span>
            </div>
            <div className="progress big"><div className="bar" style={{ width: `${overallPct}%` }} /></div>

            <h2 className="step-heading">Nicely done. Now rate your skills.</h2>
            <p className="step-sub">From 1 (weak) to 5 (strong). Be honest — this sharpens your matches.</p>

            <div className="card" style={{ marginTop: 8 }}>
              {SKILLS.map((skill) => (
                <div className="question" key={skill.id}>
                  <div className="q-text">{skill.label} <span style={{ color: '#5a6b7f', fontWeight: 400, fontSize: '0.88rem' }}>— {skill.hint}</span></div>
                  <div className="scale">
                    {SKILL_SCALE.map((v) => (
                      <button
                        key={v}
                        className={`scale-btn ${skillAnswers[skill.id] === v ? 'selected' : ''}`}
                        onClick={() => setSkill(skill.id, v)}
                      >
                        {v}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <button
              className="btn large"
              style={{ marginTop: 28, width: '100%' }}
              disabled={answeredSkills < SKILLS.length}
              onClick={() => setPhase(PHASE.CGPA)}
            >
              {answeredSkills < SKILLS.length ? `Rate all skills (${answeredSkills}/${SKILLS.length})` : 'Continue'}
            </button>
          </div>
        )}

        {/* ---------- COURSE OF STUDY ---------- */}
        {phase === PHASE.COURSE && (
          <div className="step-fade">
            <div className="step-top">
              <button className="back-link" onClick={() => setPhase(PHASE.INTRO)}>← Back</button>
              <span className="step-count">Part 1 of 4 · Course of Study</span>
            </div>
            <div className="progress big"><div className="bar" style={{ width: `${overallPct}%` }} /></div>

            <h2 className="step-heading">What did you study?</h2>
            <p className="step-sub">
              We use your degree to keep recommendations realistic — so you only see
              careers you can actually pursue with your qualification.
            </p>

            <div className="card" style={{ marginTop: 8, padding: '32px' }}>
              <label className="field-label">Course of study</label>
              <CourseCombobox
                options={courseOptions}
                value={course}
                onChange={setCourse}
                placeholder="Type or select your course…"
              />
            </div>

            <button
              className="btn large"
              style={{ marginTop: 28, width: '100%' }}
              disabled={course === ''}
              onClick={() => setPhase(PHASE.INTERESTS)}
            >
              {course === '' ? 'Select your course' : 'Continue'}
            </button>
          </div>
        )}

        {/* ---------- CGPA ---------- */}
        {phase === PHASE.CGPA && (
          <div className="step-fade">
            <div className="step-top">
              <button className="back-link" onClick={() => setPhase(PHASE.SKILLS)}>← Back</button>
              <span className="step-count">Part 4 of 4 · Academic</span>
            </div>
            <div className="progress big"><div className="bar" style={{ width: `${overallPct}%` }} /></div>

            <h2 className="step-heading">Last step — your CGPA</h2>
            <p className="step-sub">Enter your current CGPA on a 5.0 scale.</p>

            {error && <div className="error-msg">{error}</div>}

            <div className="card" style={{ marginTop: 8, textAlign: 'center', padding: '40px 32px' }}>
              <div className="cgpa-input" style={{ justifyContent: 'center' }}>
                <input
                  type="number" min="0" max="5" step="0.01"
                  value={cgpa} onChange={(e) => setCgpa(e.target.value)}
                  placeholder="3.50"
                  style={{ fontSize: '2rem', width: 180, textAlign: 'center' }}
                  autoFocus
                />
              </div>
              <p style={{ color: '#5a6b7f', marginTop: 12 }}>out of 5.0</p>
            </div>

            <button className="btn large" style={{ marginTop: 28, width: '100%' }} onClick={handleSubmit}>
              Get My Recommendations
            </button>
          </div>
        )}

        {/* ---------- ANALYZING ---------- */}
        {phase === PHASE.ANALYZING && (
          <div className="loading-screen step-fade">
            <div className="spinner" />
            <h2 className="step-heading" style={{ marginTop: 20 }}>Analyzing your profile…</h2>
            <p className="step-sub">Matching your personality, skills, and academics against 24 career paths.</p>
          </div>
        )}

      </div>
    </div>
  );
}