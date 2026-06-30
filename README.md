# CareerFit — AI-Powered Career Path Recommender

A machine-learning web application that recommends suitable career paths to university
students from their personality (RIASEC interests), academic performance and self-assessed
skills — then filters those recommendations so they are **realistic for the student's actual
degree**.

> **Final Year Project** · Adegbite Moyomade Akanji · Lagos State University

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [The Machine Learning Model](#the-machine-learning-model)
- [The Course-Relevance Layer](#the-course-relevance-layer)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Running the Project Locally](#running-the-project-locally)
- [Reproducing the Model](#reproducing-the-model)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Further Documentation](#further-documentation)

---

## Overview

Many graduates choose careers based on guesswork or peer pressure rather than an objective
match between who they are and what a role demands. **CareerFit** addresses this by combining a
trained classifier with the well-established **Holland RIASEC** model of vocational interests.

A student completes a short assessment. The system predicts how well they fit each of **24
careers**, and returns the **top 3** — each with a percentage match score and a plain-language
explanation of *why* it was recommended. Crucially, recommendations are constrained to careers
that are actually attainable from the student's **course of study**, so a Law student is never
told to become a Software Developer.

---

## Key Features

- **Personality + skills assessment** — 6 RIASEC interest scores, CGPA, and 10 self-rated skills (17 inputs in total).
- **Top-3 ranked recommendations** with a **match percentage** for each career.
- **Explainable results** — every recommendation comes with human-readable reasons (e.g. *"You enjoy analysing problems and researching ideas."*), derived from the model's own feature importances. No black box.
- **Course-relevance filtering** — recommendations are restricted and re-ranked by the student's degree so they are always *feasible*, not just psychologically matched.
- **User accounts & history** — register/login (JWT auth) to save assessments and revisit past recommendations. Guests can still get results without saving.
- **Responsive web UI** built in React.
- **Reproducible ML pipeline** — fixed random seed; an examiner can re-run training and obtain identical results.

---

## How It Works

```
  Student assessment (17 inputs)            Course of study
        │                                          │
        ▼                                          │
  ┌─────────────────────┐                          │
  │  Random Forest model │  predict_proba          │
  │  (24 careers)        │ ───────────────┐        │
  └─────────────────────┘                 ▼        ▼
                              ┌───────────────────────────────┐
                              │  Course-relevance layer        │
                              │  • drop incompatible careers   │
                              │  • boost the degree's flagship │
                              │  • renormalise match scores    │
                              └───────────────────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────┐
                              │  Explanation generator          │
                              │  (feature-importance reasons)   │
                              └───────────────────────────────┘
                                              │
                                              ▼
                         Top-3 careers + match % + reasons (JSON)
```

1. The student answers the assessment (RIASEC interests, CGPA, skills) and selects their course.
2. The **Random Forest** outputs a probability for each of the 24 careers.
3. The **relevance layer** removes careers that are incompatible with the degree, boosts the degree's primary ("flagship") career, and renormalises the remaining scores into believable match percentages.
4. For each of the final top-3 careers, an **explanation generator** surfaces the inputs that most contributed to the match.
5. Results are returned as JSON and rendered in the UI; logged-in users also have their profile and recommendation saved to MongoDB.

---

## The Machine Learning Model

| Property | Value |
|---|---|
| Algorithm | Random Forest (200 trees) |
| Careers (classes) | **24** (4 per RIASEC type) |
| Features | **17** (6 RIASEC + CGPA + 10 skills) |
| Training data | **8,040** synthetic student records (335 per career, class-balanced) |
| Split | 80 / 20 stratified, fixed seed = 42 |

### Performance (held-out test set, 1,608 records)

| Metric | Score |
|---|---|
| Top-1 accuracy | 63.9% |
| Top-2 accuracy | 86.2% |
| **Top-3 accuracy** | **93.8%** |
| Precision / Recall / F1 (weighted) | 63.8% / 63.9% / 63.7% |
| 5-fold cross-validation | 64.7% (± 1.4%) |

Because the application presents the **top 3** careers, **top-3 accuracy (93.8%)** is the
headline metric that reflects real-world usefulness: in ~94% of cases, the student's true-fit
career appears among the three shown.

### Why Random Forest?

The training script benchmarks Random Forest against SVM, Logistic Regression and Gradient
Boosting on the identical split (`model_comparison.csv` / `.png`). SVM and Logistic Regression
edge ahead on raw top-1 accuracy (~68%), but **Random Forest is deliberately kept** for two
product reasons:

1. **`predict_proba`** gives calibrated per-career probabilities, which the ranking, match
   percentages, and relevance layer all depend on.
2. **`feature_importances_`** powers the per-prediction explanations — the "why" behind each
   recommendation — which is core to the project's goal of an *explainable* recommender.

The accuracy gap is within cross-validation noise on the top-3 metric that actually matters.

### About the dataset

The dataset is **synthetic and generated programmatically** (`ml/generate_dataset.py`). Each
career has a documented statistical "fingerprint" (mean & standard deviation for every feature);
samples are drawn from noisy, **intentionally overlapping** Gaussian distributions so the model
must learn genuine patterns rather than memorise rules. The seed is fixed so the dataset is fully
reproducible. See `docs/SYNTHETIC_DATA_EXPLAINED.md` for the rationale and limitations.

---

## The Course-Relevance Layer

The ML model scores careers from interests, CGPA and skills **only** — it has no knowledge of
what a student actually studied. On its own it could tell a Computer Science graduate to become a
Lawyer (a career requiring an entirely different degree).

To make recommendations *practically feasible*, `backend/career_relevance.py` applies a
**rule-based, post-prediction relevance layer** — deliberately **not** an ML feature, so it is
hand-authored, auditable and defensible. Each course maps to an ordered list of attainable
careers, and every (course, career) pair is assigned a tier:

| Tier | Meaning | Effect |
|---|---|---|
| 1 | The degree's **flagship** career | Boosted so it reliably surfaces; always shown |
| 2 | Relevant to the degree | Allowed; ranked by personality/skills |
| 3 | Not relevant to the degree | **Excluded** from results |

An empty course or the *"Other / Not listed"* sentinel disables filtering entirely (every career
stays eligible), keeping the feature backward-compatible.

> The `COURSES` list is the contract between client and server and is mirrored in both
> `backend/career_relevance.py` and `frontend/src/assessmentData.js`; the two must stay in sync.

---

## System Architecture

```
┌──────────────┐        HTTPS / JSON        ┌──────────────────┐        ┌──────────────────┐
│  React SPA    │ ─────────────────────────▶ │  Flask REST API   │ ─────▶ │  MongoDB Atlas    │
│  (Vercel)     │ ◀───────────────────────── │  (Render)         │        │  users, profiles, │
│               │     top-3 + reasons        │  + Random Forest  │        │  recommendations  │
└──────────────┘                            └──────────────────┘        └──────────────────┘
```

- **Frontend** — React (Vite) single-page app: assessment form, results page, dashboard/history, auth pages.
- **Backend** — Flask REST API that loads the trained model, serves explainable predictions, handles JWT authentication, and persists data.
- **Database** — MongoDB Atlas stores users, student profiles, and saved recommendations.
- **ML artifacts** — the trained model and its explainability pickles are produced offline by `ml/train_model.py` and loaded by the backend at startup.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Machine Learning | Python, scikit-learn, pandas, NumPy, joblib |
| Backend | Flask, Flask-CORS, Gunicorn, PyJWT, PyMongo |
| Database | MongoDB Atlas |
| Frontend | React 19, React Router, Axios, Recharts, Vite |
| Visualisation | Matplotlib, Seaborn (training charts) |
| Deployment | Render (API), Vercel (frontend) |

---

## Repository Structure

```
career-recommender/
├── ml/                          # Model training & data generation (run offline)
│   ├── generate_dataset.py      #   builds the synthetic dataset (seed = 42)
│   ├── train_model.py           #   trains, evaluates & compares; saves artifacts
│   ├── career_dataset.csv       #   8,040 records × 17 features
│   └── *.png / model_comparison.csv   # evaluation charts & benchmark
│
├── backend/                     # Flask REST API (deployed on Render)
│   ├── app.py                   #   routes, auth, prediction + explanation
│   ├── career_relevance.py      #   course → career relevance layer
│   ├── *.pkl                    #   trained model + explainability artifacts
│   └── requirements.txt
│
├── frontend/                    # React SPA (deployed on Vercel)
│   └── src/
│       ├── pages/               #   Home, Assessment, Results, Dashboard, Login, Register
│       ├── components/          #   Navbar, CourseCombobox, ProtectedRoute
│       ├── auth/                #   AuthContext (JWT)
│       └── assessmentData.js    #   questions + COURSES contract
│
├── docs/                        # Supporting documentation
│   ├── HOW_IT_WORKS.md
│   ├── SYNTHETIC_DATA_EXPLAINED.md
│   ├── LIMITATIONS_AND_VIVA.md
│   └── TEST_PERSONAS.md
│
└── render.yaml                  # Render deployment blueprint
```

---

## Running the Project Locally

### Prerequisites

- Python 3.12+
- Node.js 18+
- A MongoDB connection string (MongoDB Atlas free tier, or a local MongoDB instance)

### 1. Backend (Flask API)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `backend/.env` file:

```env
JWT_SECRET=<a long, random secret string>
MONGO_URI=<your MongoDB connection string>
```

> `JWT_SECRET` is **required** — the server refuses to start without it, rather than signing
> login tokens with a guessable default.

Start the API:

```bash
python app.py        # serves on http://localhost:5000
```

### 2. Frontend (React)

```bash
cd frontend
npm install
```

Create `frontend/.env.local` (see `.env.example`) pointing at the API:

```env
VITE_API_URL=http://localhost:5000
```

Run the dev server:

```bash
npm run dev          # serves on http://localhost:5173
```

Open the printed URL in your browser.

---

## Reproducing the Model

The trained model is already committed, but the entire pipeline is reproducible from scratch.
Run from inside the `ml/` directory so the relative paths resolve:

```bash
cd ml
python generate_dataset.py      # regenerates career_dataset.csv (seed = 42)
python train_model.py           # trains, evaluates, and saves all artifacts
```

`train_model.py` prints accuracy, top-2/top-3 accuracy, 5-fold cross-validation, and a
per-career classification report, and writes:

- `career_model.pkl`, `label_encoder.pkl`, `feature_names.pkl` — the model + decoding
- `class_profiles.pkl`, `feature_stats.pkl` — explainability artifacts (computed from **training data only**, so there is no test-set leakage)
- `confusion_matrix.png`, `feature_importance.png`, `model_comparison.png`, `model_comparison.csv` — evaluation figures

To deploy a freshly trained model, copy the regenerated `.pkl` files into `backend/`.

---

## API Reference

Base URL (local): `http://localhost:5000`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET`  | `/` | — | Health check; lists expected feature names & DB status |
| `POST` | `/auth/register` | — | Create an account → returns JWT |
| `POST` | `/auth/login` | — | Log in → returns JWT |
| `GET`  | `/auth/me` | Bearer | Return the current user |
| `POST` | `/predict` | Optional | Get top-3 recommendations; saves history if logged in |
| `GET`  | `/history` | Bearer | The user's own past recommendations |
| `GET`  | `/stats` | — | Aggregate counts (users / profiles / recommendations) |

### Example: `POST /predict`

```json
{
  "Realistic": 6, "Investigative": 9, "Artistic": 4, "Social": 4,
  "Enterprising": 5, "Conventional": 6, "CGPA": 4.2,
  "Programming": 5, "Mathematics": 5, "ProblemSolving": 5, "Communication": 3,
  "Leadership": 3, "Creativity": 3, "Technical": 4, "DataAnalysis": 5,
  "PublicSpeaking": 3, "Research": 4,
  "Course": "Computer Science"
}
```

Response:

```json
{
  "success": true,
  "saved": false,
  "recommendations": [
    {
      "career": "Data Scientist",
      "match_percentage": 41.2,
      "reasons": [
        "You enjoy analysing problems and researching ideas.",
        "You are good at analysing data and spotting patterns.",
        "You are strong with maths and numbers."
      ],
      "core_path": false
    }
  ]
}
```

`Course` is optional. When provided, it constrains and re-ranks results via the relevance layer;
the degree's flagship career is always included (flagged with `core_path: true` when it was forced
into the list).

---

## Deployment

- **API → Render.** `render.yaml` is a deployment blueprint: Python runtime, `gunicorn` with a single worker (keeps the ~13 MB model within the free tier's 512 MB RAM), `JWT_SECRET` auto-generated, `MONGO_URI` set as a dashboard secret.
- **Frontend → Vercel.** Standard Vite build (`npm run build`); set `VITE_API_URL` to the deployed API URL.
- **Database → MongoDB Atlas.**

---

## Further Documentation

The `docs/` folder contains supporting material prepared for the project report and viva:

- **`HOW_IT_WORKS.md`** — end-to-end walkthrough of the prediction pipeline.
- **`SYNTHETIC_DATA_EXPLAINED.md`** — why synthetic data was used and how it was designed.
- **`LIMITATIONS_AND_VIVA.md`** — honest discussion of limitations and anticipated examiner questions.
- **`TEST_PERSONAS.md`** — sample student profiles for manual testing.

---

*Built as a Final Year Project at Lagos State University.*
