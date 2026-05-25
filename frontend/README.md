# CareerFit — AI-Powered Career Path Recommender

An AI-powered career path recommender system that provides personalized,
data-driven career guidance to university students by analyzing their
personality (RIASEC), academic performance (CGPA), and self-assessed skills.

Built as a final year project for the Department of Computer Science,
Faculty of Computing and Information Technology, **Lagos State University (LASU)**.

**Author:** Adegbite Moyomade Akanji (Matric No: 220591338)
**Supervisors:** Prof. Benjamin Aribisala & Mr. Mauton Asokere

---

## Overview

CareerFit replaces informal, inconsistent career guidance with a structured,
automated system. A student completes a short assessment; a trained **Random
Forest** classifier analyzes 17 features and returns the **top 3 career
recommendations** ranked by match confidence.

The system is grounded in **Holland's RIASEC theory** of vocational
personality, and integrates personality, academic, and skills data — addressing
the limitation of single-factor career tools identified in the literature.

---

## System Architecture

A three-tier client–server architecture:

```
┌─────────────────┐     HTTP/JSON     ┌──────────────────┐     ┌─────────────────┐
│   React (Vite)  │ ───────────────►  │   Flask REST API │ ──► │  MongoDB Atlas  │
│  Frontend (UI)  │ ◄───────────────  │  + Random Forest │ ◄── │   (3 collections)│
└─────────────────┘   recommendations └──────────────────┘     └─────────────────┘
```

- **Frontend:** React + Vite — progressive assessment, results, dashboard
- **Backend:** Flask — loads the model, serves `/predict`, `/history`, `/stats`
- **Model:** Random Forest (scikit-learn), trained on a synthetic dataset
- **Database:** MongoDB Atlas — stores users, student profiles, recommendations

---

## Project Structure

```
career-recommender/
├── venv/                      # shared Python virtual environment
├── ml/                        # machine learning module
│   ├── generate_dataset.py    # generates the synthetic dataset
│   ├── train_model.py         # trains & evaluates the Random Forest
│   ├── career_dataset.csv     # (generated) 4,020 student profiles
│   ├── career_model.pkl       # (generated) trained model
│   ├── label_encoder.pkl      # (generated) career label encoder
│   ├── feature_names.pkl      # (generated) ordered feature names
│   ├── confusion_matrix.png   # (generated) evaluation figure
│   └── feature_importance.png # (generated) evaluation figure
├── backend/                   # Flask API
│   ├── app.py                 # main server
│   ├── test_backend.py        # endpoint tests
│   ├── .env                   # MONGO_URI (NOT committed)
│   └── *.pkl                  # model files (copied from ml/)
├── frontend/                  # React app
│   └── src/
│       ├── pages/             # Home, Assessment, Results, Dashboard
│       ├── components/        # Navbar
│       ├── api.js             # backend connection
│       └── assessmentData.js  # RIASEC questions + scoring
├── requirements.txt
└── README.md
```

---

## Setup & Run

### Prerequisites
- Python 3.12+
- Node.js 18+
- A MongoDB Atlas account (free tier) with a connection string

### 1. Backend + ML

```bash
# from project root
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

# generate the dataset and train the model
cd ml
python generate_dataset.py
python train_model.py

# copy model files to the backend
cp career_model.pkl label_encoder.pkl feature_names.pkl ../backend/
```

Create `backend/.env` with your MongoDB connection string:
```
MONGO_URI=mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

Run the backend:
```bash
cd ../backend
python app.py        # serves on http://127.0.0.1:5000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev          # serves on http://localhost:5173
```

Open http://localhost:5173 in your browser.

---

## How the Model Works

- **Dataset:** 4,020 synthetic student profiles (335 per career × 12 careers),
  generated from documented statistical distributions reflecting realistic
  RIASEC, CGPA, and skill patterns. Fully reproducible (fixed random seed).
- **Features (17):** 6 RIASEC scores + CGPA + 10 skill ratings.
- **Target (12 careers):** Software Developer, Data Scientist, Cybersecurity
  Analyst, Civil/Mechanical Engineer, Medical Lab Scientist, Accountant/Auditor,
  Banker/Financial Analyst, Marketing/Sales Executive, HR Manager,
  Teacher/Lecturer, Graphic Designer/UI-UX, Entrepreneur.
- **Evaluation:** 80/20 train-test split + 5-fold cross-validation.
  ~81% accuracy, with errors concentrated among genuinely similar careers
  (e.g. Software Developer vs Cybersecurity Analyst) — indicating the model
  learned meaningful patterns rather than memorizing.

---

## API Endpoints

| Method | Endpoint           | Description                                  |
|--------|--------------------|----------------------------------------------|
| GET    | `/`                | Health check + DB status                     |
| POST   | `/predict`         | Returns top-3 careers; saves profile         |
| GET    | `/history/<email>` | Returns a user's past recommendations        |
| GET    | `/stats`           | System counts (users, profiles, recs)        |

---

## Limitations & Future Work

- The model is trained on synthetic data; validation with real LASU student
  data is future work.
- User authentication (passwords) was scoped out; users are identified by email.
- Career categories are bounded to a curated set of 12.

---

## Acknowledgements

Developed under the supervision of Prof. Benjamin Aribisala and Mr. Mauton
Asokere, Department of Computer Science, Lagos State University.