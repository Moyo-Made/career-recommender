// Questions and scoring for the assessment, kept separate from UI logic.

// 18 RIASEC interest statements, 3 per type, each rated 1-5 by the student.
export const RIASEC_QUESTIONS = [
  { id: 'r1', type: 'Realistic', text: 'I enjoy working with tools, machines, or my hands.' },
  { id: 'r2', type: 'Realistic', text: 'I like building, repairing, or assembling things.' },
  { id: 'r3', type: 'Realistic', text: 'I prefer practical, hands-on tasks over theory.' },
  { id: 'i1', type: 'Investigative', text: 'I enjoy solving complex problems and puzzles.' },
  { id: 'i2', type: 'Investigative', text: 'I like analyzing data to understand how things work.' },
  { id: 'i3', type: 'Investigative', text: 'I am curious and enjoy researching new ideas.' },
  { id: 'a1', type: 'Artistic', text: 'I enjoy creative activities like design, art, or writing.' },
  { id: 'a2', type: 'Artistic', text: 'I like expressing myself in original, imaginative ways.' },
  { id: 'a3', type: 'Artistic', text: 'I prefer tasks that have no single "correct" approach.' },
  { id: 's1', type: 'Social', text: 'I enjoy helping, teaching, or supporting other people.' },
  { id: 's2', type: 'Social', text: 'I am good at understanding how others feel.' },
  { id: 's3', type: 'Social', text: 'I find it rewarding to work closely with people.' },
  { id: 'e1', type: 'Enterprising', text: 'I enjoy leading, persuading, or motivating others.' },
  { id: 'e2', type: 'Enterprising', text: 'I like taking charge and making decisions.' },
  { id: 'e3', type: 'Enterprising', text: 'I am interested in business, sales, or starting ventures.' },
  { id: 'c1', type: 'Conventional', text: 'I like organizing information and following clear procedures.' },
  { id: 'c2', type: 'Conventional', text: 'I enjoy working with numbers, records, or detailed data.' },
  { id: 'c3', type: 'Conventional', text: 'I prefer structured tasks with clear rules.' },
];

export const RIASEC_TYPES = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'];

// The 10 self-assessed skills, matching the model's skill features.
export const SKILLS = [
  { id: 'Programming', label: 'Programming', hint: 'Writing code' },
  { id: 'Mathematics', label: 'Mathematics & Statistics', hint: 'Quantitative reasoning' },
  { id: 'ProblemSolving', label: 'Problem Solving', hint: 'Analytical thinking' },
  { id: 'Communication', label: 'Communication', hint: 'Written and verbal' },
  { id: 'Leadership', label: 'Leadership', hint: 'Leading teams' },
  { id: 'Creativity', label: 'Creativity', hint: 'Original thinking, design' },
  { id: 'Technical', label: 'Technical / Mechanical', hint: 'Hands-on building, fixing' },
  { id: 'DataAnalysis', label: 'Data Analysis', hint: 'Interpreting numbers, patterns' },
  { id: 'PublicSpeaking', label: 'Public Speaking', hint: 'Presenting to groups' },
  { id: 'Research', label: 'Research', hint: 'Investigation, reading, synthesis' },
];

// Courses of study, used to keep recommendations feasible for the student's
// degree. MUST stay in sync with COURSES in backend/career_relevance.py — the
// strings are the contract the relevance filter matches on.
export const COURSES = [
  'Computer Science',
  'Software Engineering',
  'Information Technology',
  'Cybersecurity',
  'Mathematics / Statistics',
  'Law',
  'Accounting',
  'Banking & Finance',
  'Economics',
  'Business Administration',
  'Marketing',
  'Mass Communication',
  'Public Administration',
  'Architecture',
  'Civil Engineering',
  'Mechanical Engineering',
  'Electrical/Electronics Engineering',
  'Agricultural Science',
  'Medical Laboratory Science',
  'Nursing',
  'Medicine & Surgery',
  'Biochemistry / Microbiology',
  'Education',
  'English / Literature',
  'Fine & Applied Arts',
  'Fashion Design',
  'Other / Not listed',
];

// Convert the 1-5 quiz answers into 6 RIASEC scores on the model's 1-10 scale.
//
// RIASEC is a relative profile: we score each person's interests against their
// OWN average and amplify the gaps. This counters acquiescence bias (agreeing
// with everything produces a flat profile that collapses to generalist careers)
// and restores the contrast the model was trained on. GAIN sets the stretch.
const RIASEC_CONTRAST_GAIN = 1.8;

export function calculateRiasecScores(answers) {
  // Absolute base score per type: (average of its 1-5 items / 5) * 10.
  const base = {};
  RIASEC_TYPES.forEach((type) => {
    const questionsOfType = RIASEC_QUESTIONS.filter((q) => q.type === type);
    const sum = questionsOfType.reduce((acc, q) => acc + (answers[q.id] || 0), 0);
    base[type] = (sum / questionsOfType.length / 5) * 10;
  });

  const personMean = RIASEC_TYPES.reduce((acc, t) => acc + base[t], 0) / RIASEC_TYPES.length;

  // Amplify each type's deviation from the person's average, clipped to [1, 10].
  const scores = {};
  RIASEC_TYPES.forEach((type) => {
    const stretched = personMean + RIASEC_CONTRAST_GAIN * (base[type] - personMean);
    scores[type] = Math.round(Math.max(1, Math.min(10, stretched)) * 10) / 10;
  });
  return scores;
}
