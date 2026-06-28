# How the System Works — End to End (Simple Explanation)

**Project:** AI-Powered Career Path Recommender for University Students.

This explains the whole system in plain terms: the big picture, the two journeys (building the
"brain" and using the app), and what each major concept does. No prior ML knowledge needed.

> Related docs: `SYNTHETIC_DATA_EXPLAINED.md` (the data), `LIMITATIONS_AND_VIVA.md` (limits +
> viva answers), `TEST_PERSONAS.md` (demo inputs).

---

## 1. The big picture in one paragraph

A student answers a short questionnaire about their **interests, skills and CGPA**. The system
turns those answers into **17 numbers**, feeds them to a trained machine-learning model, and the
model ranks **24 careers** by how well they fit — returning the **top 3** with a plain-language
reason for each. If the student is logged in, their result is saved so they can revisit it.

---

## 2. The system has two halves

```
   ┌─────────────────────────────────────────────────────────────────────┐
   │  HALF A — BUILD THE BRAIN  (done once, offline, by you the developer)│
   │                                                                       │
   │   generate_dataset.py  ──►  career_dataset.csv  ──►  train_model.py   │
   │   (make fake-but-realistic     (8,040 example       (learn the         │
   │    student data)                students)            patterns)         │
   │                                                          │             │
   │                                                          ▼             │
   │                                       career_model.pkl  + helper files │
   │                                       (the saved, trained "brain")     │
   └─────────────────────────────────────────────────────────────────────┘
                                     │  (the .pkl files are copied to the backend)
                                     ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │  HALF B — USE THE APP  (happens live, every time a student visits)    │
   │                                                                       │
   │   Student ─► React website ─► answers ─► Flask backend ─► model picks │
   │   (browser)   (frontend)      become 17    (/predict)     top-3        │
   │                               numbers                     careers      │
   │                                                  │                     │
   │                                                  ├─► saves to MongoDB   │
   │                                                  │   (if logged in)     │
   │                                                  ▼                     │
   │                            Results page shows top-3 + "why this fits"  │
   └─────────────────────────────────────────────────────────────────────┘
```

**Key idea:** the model is *trained once* (Half A), then *used many times* (Half B). Training is
slow and happens on your machine; using the trained model is instant and happens on the server.

---

## 3. Half A — Building the brain (the training pipeline)

**Step 1 — Make the data.** `generate_dataset.py` creates **8,040 example students** (335 for
each of the 24 careers). Each career has a "typical profile," and students are randomly varied
around it. *(Full detail in `SYNTHETIC_DATA_EXPLAINED.md`.)* Output: `career_dataset.csv`.

**Step 2 — Train and test the model.** `train_model.py`:
1. Splits the data **80% for training, 20% for testing** (the model never sees the test set while
   learning — that's how we check it really learned, not just memorised).
2. Trains a **Random Forest** on the 80%.
3. Measures how well it does on the unseen 20% (accuracy, top-3 accuracy, etc.).
4. Saves the trained model and a few helper files (the `.pkl` files).

**Step 3 — Hand the brain to the app.** The saved `.pkl` files are copied into `backend/` so the
live server can load the ready-made model instantly without retraining.

---

## 4. Half B — Using the app (what happens when a student visits)

1. **The student takes the assessment** on the React website: 18 interest questions, 10 skill
   ratings, and their CGPA.
2. **The frontend turns answers into 17 numbers.** The 18 interest answers become 6 RIASEC scores
   (using the *relative scoring* described below); the 10 skills and CGPA pass through. That's the
   17 features the model expects.
3. **The frontend sends those numbers to the backend** (`POST /predict`).
4. **The backend runs the model.** It loads the trained Random Forest and asks it: "for these 17
   numbers, how likely is each of the 24 careers?" It sorts them and keeps the **top 3**.
5. **The backend writes a plain reason for each** ("You have strong programming skills.") and, if
   the student is logged in, **saves the result to the database**.
6. **The frontend shows the Results page**: the top 3 careers, each with a confidence % and a
   "Why this fits you" list. Logged-in users can see past results on their **Dashboard**.

---

## 5. The major concepts, in plain terms

### RIASEC (Holland Codes)
A well-known career-psychology model that sorts work interests into **six types**: **R**ealistic
(hands-on), **I**nvestigative (analytical), **A**rtistic (creative), **S**ocial (helping),
**E**nterprising (leading/business), **C**onventional (organising). The questionnaire measures
where a student leans across these six.

### Features (the 17 inputs)
The numbers the model reasons about: **6** RIASEC interest scores + **1** CGPA + **10** skill
ratings = **17**. Everything the student tells us is boiled down to these.

### Relative (ipsative) RIASEC scoring
People tend to *agree* with most questions, which would make everyone look the same and push them
all toward "generalist" careers. So instead of scoring interests on an absolute scale, we score
each person's six interests **relative to their own average** — stretching their strongest
interests up and weakest down. This recovers each student's true "shape" (the way RIASEC is meant
to be read). *(Lives in `calculateRiasecScores` in `assessmentData.js`.)*

### Random Forest (the model)
The "brain." Imagine **200 decision trees**, each a flowchart of yes/no questions about the 17
features ("Is Investigative interest high? Is Maths skill high?…"). Each tree votes for a career,
and the forest combines all 200 votes. Many trees voting together is more accurate and stable than
one. We use it because it's accurate *and* it can tell us which features mattered — which powers
the explanations.

### Training vs. prediction
**Training** = the one-time learning phase where the model studies thousands of examples (Half A).
**Prediction** = using the finished model to score a new student instantly (Half B). Like
studying for an exam once, then answering questions quickly afterwards.

### Train/test split
We hide 20% of the data during training and test on it afterwards. If the model does well on data
it *never saw*, we know it learned real patterns rather than memorising answers.

### Accuracy, and top-1 vs top-3
**Accuracy** = how often the model is right on the unseen test set. **Top-1** = the single best
guess is exactly correct (~64%). **Top-3** = the correct career is among the three we show
(~94%). Because the app recommends three careers, **top-3 is the metric that matters.**

### Probabilities / "match %"
The model doesn't just pick one career — it gives each of the 24 a probability (a confidence
score). The "84%" you see on a result *is* that probability. The three highest become the
recommendations.

### Explainability ("Why this fits you")
For each recommended career, the backend finds the student's strengths that most pushed the model
toward it and writes them in plain English. So it's never a mysterious black box — the student
sees the reasons. *(Method detail in `LIMITATIONS_AND_VIVA.md` §4.)*

### Authentication (JWT) and the database (MongoDB)
**JWT** is a secure "digital wristband": when you log in, the server gives your browser a signed
token that proves who you are on later requests, without re-entering your password. **MongoDB** is
the database that stores three things: **users**, their **assessment profiles**, and their
**recommendations** — so logged-in students keep a history.

### Frontend vs. backend
**Frontend** = what runs in the student's browser (the React website: pages, questions, results).
**Backend** = the server (Flask) that holds the model, does the prediction, and talks to the
database. They communicate over a simple web **API** (the frontend asks, the backend answers).

### The `.pkl` files (model artifacts)
"Pickle" files are a way to save a trained Python object to disk. After training, we save the
model and its helpers as `.pkl` so the backend can load the *finished* brain instantly instead of
retraining every time. They are: `career_model.pkl` (the forest), `label_encoder.pkl` (maps career
names to numbers and back), `feature_names.pkl` (the 17 feature order), and `class_profiles.pkl` +
`feature_stats.pkl` (used to write the explanations).

---

## 6. Where everything lives (file map)

| Part | Folder / file | Job |
|---|---|---|
| Data generator | `ml/generate_dataset.py` | Creates the synthetic training data |
| Trainer | `ml/train_model.py` | Trains + tests the model, saves the `.pkl` files |
| Trained brain | `backend/*.pkl` | The ready-to-use model + helpers |
| Server / API | `backend/app.py` | Runs predictions, auth, saves to database |
| Website | `frontend/src/` | The pages the student interacts with |
| Questions + scoring | `frontend/src/assessmentData.js` | The quiz and RIASEC scoring |
| Results page | `frontend/src/pages/Results.jsx` | Shows top-3 + "why this fits you" |
| Deployment | `render.yaml`, `frontend/vercel.json` | Backend on Render, frontend on Vercel |

---

## 7. One-paragraph summary to say out loud
> "There are two halves. First, offline, I generate realistic example students and train a Random
> Forest model to recognise which career profile a student matches — that trained model gets saved
> to disk. Second, live, the React website collects a student's interests, skills and CGPA, turns
> them into 17 numbers, and sends them to a Flask backend that runs the saved model and returns
> the top-3 careers with plain-language reasons, saving the result for logged-in users. The model
> is trained once and used many times."
