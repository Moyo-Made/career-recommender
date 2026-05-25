// src/assessmentData.js
// All the questions and configuration for the assessment.
// Keeping this separate makes it easy to edit questions without touching logic.

// ---------------------------------------------------------------
// RIASEC QUIZ
// Each statement belongs to ONE RIASEC type. The student rates each
// 1-5. We average the ratings per type, then scale 1-5 -> 1-10 to
// match the scale the model was trained on.
// 3 statements per type x 6 types = 18 questions.
// ---------------------------------------------------------------
export const RIASEC_QUESTIONS = [
	// Realistic
	{ id: 'r1', type: 'Realistic', text: 'I enjoy working with tools, machines, or my hands.' },
	{ id: 'r2', type: 'Realistic', text: 'I like building, repairing, or assembling things.' },
	{ id: 'r3', type: 'Realistic', text: 'I prefer practical, hands-on tasks over theory.' },
	// Investigative
	{ id: 'i1', type: 'Investigative', text: 'I enjoy solving complex problems and puzzles.' },
	{ id: 'i2', type: 'Investigative', text: 'I like analyzing data to understand how things work.' },
	{ id: 'i3', type: 'Investigative', text: 'I am curious and enjoy researching new ideas.' },
	// Artistic
	{ id: 'a1', type: 'Artistic', text: 'I enjoy creative activities like design, art, or writing.' },
	{ id: 'a2', type: 'Artistic', text: 'I like expressing myself in original, imaginative ways.' },
	{ id: 'a3', type: 'Artistic', text: 'I prefer tasks that have no single "correct" approach.' },
	// Social
	{ id: 's1', type: 'Social', text: 'I enjoy helping, teaching, or supporting other people.' },
	{ id: 's2', type: 'Social', text: 'I am good at understanding how others feel.' },
	{ id: 's3', type: 'Social', text: 'I find it rewarding to work closely with people.' },
	// Enterprising
	{ id: 'e1', type: 'Enterprising', text: 'I enjoy leading, persuading, or motivating others.' },
	{ id: 'e2', type: 'Enterprising', text: 'I like taking charge and making decisions.' },
	{ id: 'e3', type: 'Enterprising', text: 'I am interested in business, sales, or starting ventures.' },
	// Conventional
	{ id: 'c1', type: 'Conventional', text: 'I like organizing information and following clear procedures.' },
	{ id: 'c2', type: 'Conventional', text: 'I enjoy working with numbers, records, or detailed data.' },
	{ id: 'c3', type: 'Conventional', text: 'I prefer structured tasks with clear rules.' },
  ];
  
  export const RIASEC_TYPES = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'];
  
  // ---------------------------------------------------------------
  // SKILLS — rated 1-5 directly (students can self-assess these)
  // These match the 10 skill features the model was trained on.
  // ---------------------------------------------------------------
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
  
  // ---------------------------------------------------------------
  // Helper: convert quiz answers into the 6 RIASEC scores (1-10 scale)
  // ---------------------------------------------------------------
  export function calculateRiasecScores(answers) {
	const scores = {};
	RIASEC_TYPES.forEach((type) => {
	  const questionsOfType = RIASEC_QUESTIONS.filter((q) => q.type === type);
	  const sum = questionsOfType.reduce((acc, q) => acc + (answers[q.id] || 0), 0);
	  const avg = sum / questionsOfType.length; // average on 1-5 scale
	  // scale 1-5 -> 1-10:  (avg/5)*10, but keep min around 1
	  scores[type] = Math.round((avg / 5) * 10 * 10) / 10;
	});
	return scores;
  }