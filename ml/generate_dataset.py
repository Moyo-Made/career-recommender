"""
Synthetic Dataset Generator for AI-Powered Career Path Recommender
Author: Adegbite Moyomade Akanji
Project: Final Year Project, Lagos State University

This script generates a balanced synthetic dataset of student profiles mapped to
career outcomes. The dataset is designed to reflect realistic distributions of
RIASEC scores, CGPA, and self-assessed skills among Nigerian university students.

Design principles:
1. Each career has a documented "profile" — mean & std for each feature.
2. Samples are drawn from noisy Gaussian distributions, NOT deterministic rules.
3. Distributions overlap intentionally so the model must learn patterns.
4. Class-balanced: equal samples per career.
5. Reproducible: fixed random seed.

Output: career_dataset.csv with 17 feature columns + 1 target column.
"""

import numpy as np
import pandas as pd

# Fixed seed for reproducibility — examiner can re-run and get same dataset
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Samples per career — 335 × 12 = 4,020 total students
SAMPLES_PER_CAREER = 335

# Feature columns
RIASEC_TYPES = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
SKILLS = [
    'Programming', 'Mathematics', 'ProblemSolving', 'Communication',
    'Leadership', 'Creativity', 'Technical', 'DataAnalysis',
    'PublicSpeaking', 'Research'
]

# -----------------------------------------------------------------------------
# CAREER PROFILES
# -----------------------------------------------------------------------------
# Each profile defines:
#   - riasec: (mean, std) for each of R, I, A, S, E, C — scored 1-10
#   - cgpa: (mean, std) — bounded to [1.5, 5.0]
#   - skills: (mean, std) for each of 10 skills — scored 1-5
#
# Means are chosen to give each career a distinctive "fingerprint" while
# allowing realistic overlap (e.g., Software Developer and Data Scientist share
# high Investigative but differ in Math intensity).
# -----------------------------------------------------------------------------

CAREER_PROFILES = {
    # ---------- INVESTIGATIVE-dominant ----------
    'Software Developer': {
        'riasec': {'Realistic': (6.5, 1.5), 'Investigative': (8.5, 1.0), 'Artistic': (5.0, 1.8),
                   'Social': (4.0, 1.5), 'Enterprising': (4.5, 1.8), 'Conventional': (5.5, 1.8)},
        'cgpa': (3.7, 0.5),
        'skills': {'Programming': (4.5, 0.5), 'Mathematics': (4.0, 0.7), 'ProblemSolving': (4.5, 0.5),
                   'Communication': (3.0, 0.9), 'Leadership': (2.8, 1.0), 'Creativity': (3.5, 0.9),
                   'Technical': (4.2, 0.7), 'DataAnalysis': (3.8, 0.8), 'PublicSpeaking': (2.5, 1.0),
                   'Research': (3.5, 0.9)}
    },
    'Data Scientist': {
        'riasec': {'Realistic': (5.5, 1.5), 'Investigative': (9.0, 0.8), 'Artistic': (4.5, 1.5),
                   'Social': (4.2, 1.5), 'Enterprising': (5.0, 1.8), 'Conventional': (7.0, 1.5)},
        'cgpa': (4.1, 0.4),
        'skills': {'Programming': (4.2, 0.7), 'Mathematics': (4.7, 0.4), 'ProblemSolving': (4.6, 0.5),
                   'Communication': (3.5, 0.9), 'Leadership': (3.0, 1.0), 'Creativity': (3.2, 0.9),
                   'Technical': (3.8, 0.8), 'DataAnalysis': (4.8, 0.3), 'PublicSpeaking': (3.0, 1.0),
                   'Research': (4.3, 0.6)}
    },
    'Cybersecurity Analyst': {
        'riasec': {'Realistic': (7.0, 1.5), 'Investigative': (8.5, 1.0), 'Artistic': (4.0, 1.5),
                   'Social': (4.0, 1.5), 'Enterprising': (5.0, 1.5), 'Conventional': (6.5, 1.5)},
        'cgpa': (3.7, 0.5),
        'skills': {'Programming': (4.0, 0.8), 'Mathematics': (3.8, 0.8), 'ProblemSolving': (4.5, 0.5),
                   'Communication': (3.2, 0.9), 'Leadership': (3.0, 1.0), 'Creativity': (3.2, 0.9),
                   'Technical': (4.5, 0.5), 'DataAnalysis': (4.0, 0.7), 'PublicSpeaking': (2.8, 1.0),
                   'Research': (4.0, 0.7)}
    },
    'Medical Lab Scientist': {
        'riasec': {'Realistic': (7.5, 1.3), 'Investigative': (8.5, 1.0), 'Artistic': (4.0, 1.5),
                   'Social': (5.5, 1.5), 'Enterprising': (4.0, 1.5), 'Conventional': (6.5, 1.3)},
        'cgpa': (3.9, 0.5),
        'skills': {'Programming': (2.2, 1.0), 'Mathematics': (3.8, 0.8), 'ProblemSolving': (4.2, 0.6),
                   'Communication': (3.5, 0.8), 'Leadership': (3.0, 0.9), 'Creativity': (2.8, 0.9),
                   'Technical': (4.5, 0.5), 'DataAnalysis': (4.0, 0.7), 'PublicSpeaking': (3.0, 1.0),
                   'Research': (4.5, 0.5)}
    },
    # ---------- REALISTIC-dominant ----------
    'Civil/Mechanical Engineer': {
        'riasec': {'Realistic': (8.8, 0.8), 'Investigative': (7.5, 1.2), 'Artistic': (4.5, 1.5),
                   'Social': (4.0, 1.5), 'Enterprising': (5.0, 1.5), 'Conventional': (5.5, 1.5)},
        'cgpa': (3.7, 0.5),
        'skills': {'Programming': (3.0, 1.0), 'Mathematics': (4.4, 0.6), 'ProblemSolving': (4.4, 0.6),
                   'Communication': (3.3, 0.9), 'Leadership': (3.5, 0.9), 'Creativity': (3.5, 0.9),
                   'Technical': (4.7, 0.4), 'DataAnalysis': (3.5, 0.9), 'PublicSpeaking': (3.0, 1.0),
                   'Research': (3.5, 0.9)}
    },
    # ---------- CONVENTIONAL-dominant ----------
    'Accountant/Auditor': {
        'riasec': {'Realistic': (4.5, 1.5), 'Investigative': (6.0, 1.5), 'Artistic': (3.5, 1.3),
                   'Social': (4.5, 1.5), 'Enterprising': (6.0, 1.5), 'Conventional': (8.8, 0.8)},
        'cgpa': (3.7, 0.5),
        'skills': {'Programming': (2.5, 1.0), 'Mathematics': (4.5, 0.5), 'ProblemSolving': (4.0, 0.7),
                   'Communication': (3.8, 0.7), 'Leadership': (3.2, 0.9), 'Creativity': (2.5, 0.9),
                   'Technical': (3.0, 0.9), 'DataAnalysis': (4.5, 0.5), 'PublicSpeaking': (3.2, 0.9),
                   'Research': (3.3, 0.9)}
    },
    'Banker/Financial Analyst': {
        'riasec': {'Realistic': (4.0, 1.5), 'Investigative': (6.5, 1.5), 'Artistic': (3.8, 1.3),
                   'Social': (5.5, 1.5), 'Enterprising': (7.5, 1.2), 'Conventional': (8.3, 1.0)},
        'cgpa': (3.7, 0.5),
        'skills': {'Programming': (2.8, 1.0), 'Mathematics': (4.4, 0.6), 'ProblemSolving': (4.2, 0.6),
                   'Communication': (4.2, 0.6), 'Leadership': (3.8, 0.8), 'Creativity': (2.8, 0.9),
                   'Technical': (2.8, 0.9), 'DataAnalysis': (4.5, 0.5), 'PublicSpeaking': (3.8, 0.8),
                   'Research': (3.8, 0.8)}
    },
    # ---------- ENTERPRISING-dominant ----------
    'Marketing/Sales Executive': {
        'riasec': {'Realistic': (3.5, 1.3), 'Investigative': (4.5, 1.5), 'Artistic': (6.0, 1.5),
                   'Social': (7.0, 1.3), 'Enterprising': (8.8, 0.8), 'Conventional': (5.0, 1.5)},
        'cgpa': (3.2, 0.6),
        'skills': {'Programming': (1.8, 0.9), 'Mathematics': (2.8, 1.0), 'ProblemSolving': (3.8, 0.8),
                   'Communication': (4.7, 0.4), 'Leadership': (4.3, 0.6), 'Creativity': (4.2, 0.6),
                   'Technical': (2.3, 1.0), 'DataAnalysis': (3.0, 1.0), 'PublicSpeaking': (4.6, 0.5),
                   'Research': (3.2, 0.9)}
    },
    'Entrepreneur': {
        'riasec': {'Realistic': (5.5, 1.5), 'Investigative': (5.5, 1.5), 'Artistic': (5.8, 1.5),
                   'Social': (5.5, 1.5), 'Enterprising': (9.0, 0.7), 'Conventional': (5.0, 1.5)},
        'cgpa': (3.3, 0.7),
        'skills': {'Programming': (2.5, 1.2), 'Mathematics': (3.2, 1.0), 'ProblemSolving': (4.2, 0.7),
                   'Communication': (4.4, 0.6), 'Leadership': (4.6, 0.5), 'Creativity': (4.3, 0.6),
                   'Technical': (3.0, 1.0), 'DataAnalysis': (3.3, 0.9), 'PublicSpeaking': (4.2, 0.7),
                   'Research': (3.3, 0.9)}
    },
    # ---------- SOCIAL-dominant ----------
    'Human Resources Manager': {
        'riasec': {'Realistic': (3.5, 1.3), 'Investigative': (4.5, 1.5), 'Artistic': (5.0, 1.5),
                   'Social': (8.5, 1.0), 'Enterprising': (7.0, 1.3), 'Conventional': (6.0, 1.5)},
        'cgpa': (3.4, 0.6),
        'skills': {'Programming': (1.8, 0.9), 'Mathematics': (2.8, 1.0), 'ProblemSolving': (3.8, 0.8),
                   'Communication': (4.6, 0.5), 'Leadership': (4.4, 0.6), 'Creativity': (3.3, 0.9),
                   'Technical': (2.2, 1.0), 'DataAnalysis': (3.0, 1.0), 'PublicSpeaking': (4.3, 0.6),
                   'Research': (3.2, 0.9)}
    },
    'Teacher/Lecturer': {
        'riasec': {'Realistic': (4.0, 1.5), 'Investigative': (6.5, 1.5), 'Artistic': (5.5, 1.5),
                   'Social': (8.8, 0.8), 'Enterprising': (5.0, 1.5), 'Conventional': (5.5, 1.5)},
        'cgpa': (3.7, 0.5),
        'skills': {'Programming': (2.3, 1.1), 'Mathematics': (3.3, 1.0), 'ProblemSolving': (3.8, 0.8),
                   'Communication': (4.5, 0.5), 'Leadership': (3.8, 0.8), 'Creativity': (3.5, 0.8),
                   'Technical': (2.5, 1.0), 'DataAnalysis': (3.0, 1.0), 'PublicSpeaking': (4.5, 0.5),
                   'Research': (4.0, 0.7)}
    },
    # ---------- ARTISTIC-dominant ----------
    'Graphic Designer/UI-UX': {
        'riasec': {'Realistic': (4.5, 1.5), 'Investigative': (5.0, 1.5), 'Artistic': (8.8, 0.8),
                   'Social': (5.0, 1.5), 'Enterprising': (5.5, 1.5), 'Conventional': (4.0, 1.5)},
        'cgpa': (3.3, 0.6),
        'skills': {'Programming': (3.0, 1.2), 'Mathematics': (2.5, 1.0), 'ProblemSolving': (4.0, 0.7),
                   'Communication': (4.0, 0.8), 'Leadership': (3.0, 1.0), 'Creativity': (4.8, 0.3),
                   'Technical': (3.5, 0.9), 'DataAnalysis': (2.8, 1.0), 'PublicSpeaking': (3.3, 0.9),
                   'Research': (3.3, 0.9)}
    },
}


def sample_clipped(mean, std, low, high, n=1):
    """Sample from a normal distribution but clip to bounds. Realistic surveys behave this way."""
    samples = np.random.normal(loc=mean, scale=std, size=n)
    return np.clip(samples, low, high)


def generate_dataset():
    """Generate the full balanced synthetic dataset."""
    rows = []

    for career, profile in CAREER_PROFILES.items():
        for _ in range(SAMPLES_PER_CAREER):
            row = {}

            # RIASEC scores: 1-10
            for r_type in RIASEC_TYPES:
                mean, std = profile['riasec'][r_type]
                row[r_type] = float(sample_clipped(mean, std, 1.0, 10.0, 1)[0])

            # CGPA: 1.5-5.0 (Nigerian 5.0 scale)
            cgpa_mean, cgpa_std = profile['cgpa']
            row['CGPA'] = float(sample_clipped(cgpa_mean, cgpa_std, 1.5, 5.0, 1)[0])

            # Skills: 1-5
            for skill in SKILLS:
                mean, std = profile['skills'][skill]
                row[skill] = float(sample_clipped(mean, std, 1.0, 5.0, 1)[0])

            row['Career'] = career
            rows.append(row)

    df = pd.DataFrame(rows)

    # Shuffle so careers aren't grouped (important for proper train/test split)
    df = df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)

    # Round for readability while preserving distributions
    for col in RIASEC_TYPES:
        df[col] = df[col].round(1)
    df['CGPA'] = df['CGPA'].round(2)
    for skill in SKILLS:
        df[skill] = df[skill].round(1)

    return df


def print_dataset_summary(df):
    """Print a summary that can go straight into Chapter 4."""
    print("=" * 70)
    print("SYNTHETIC DATASET SUMMARY")
    print("=" * 70)
    print(f"Total samples: {len(df)}")
    print(f"Total features: {len(df.columns) - 1}")
    print(f"Target classes: {df['Career'].nunique()}")
    print()
    print("Class distribution:")
    print(df['Career'].value_counts().to_string())
    print()
    print("Feature statistics:")
    feature_cols = [c for c in df.columns if c != 'Career']
    print(df[feature_cols].describe().round(2).to_string())
    print()
    print("First 5 rows (sample):")
    print(df.head().to_string())


if __name__ == '__main__':
    print("Generating synthetic career dataset...")
    df = generate_dataset()

    output_path = 'career_dataset.csv'
    df.to_csv(output_path, index=False)

    print_dataset_summary(df)
    print(f"\n✓ Dataset saved to: {output_path}")
