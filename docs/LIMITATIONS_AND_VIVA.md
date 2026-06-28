# Limitations, Honest Framing & Viva Preparation
**Project:** Development of an AI-Powered Career Path Recommender for University Students
**Author:** Adegbite Moyomade Akanji

This document is a candid self-assessment of the project's limitations and a set of
prepared answers for likely examiner questions. Presenting these *proactively* is a sign of
research maturity — it is far stronger than being caught out on them.

---

## 1. The synthetic dataset (the most important point)

**What we did.** No accessible dataset of Nigerian university students mapped to verified
career outcomes exists. We therefore generated a **theory-grounded synthetic dataset** of
**8,040 students (335 per career × 24 careers, balanced 4 careers per RIASEC type)**. Each
career has a documented profile of mean and standard deviation for every feature (RIASEC
interests, CGPA, 10 self-assessed skills), grounded in **Holland's RIASEC framework**. Samples
are drawn from *overlapping* Gaussian distributions, not deterministic rules, so the classes
genuinely overlap.

**What this means — stated honestly.** The model's accuracy validates the **pipeline**
(that the system can learn and recover meaningful patterns and serve them end-to-end). It is
**not** a measurement of real-world predictive accuracy against actual career outcomes, and
we do not claim it is.

**Why this is defensible, not a fatal flaw.**
- The class distributions deliberately overlap across **24 careers**, so the task is genuinely
  hard — top-1 accuracy is **~64%**, not a suspicious ~99%. A near-perfect score *would* have
  been a red flag (a model trivially memorising hand-coded rules). And because the product
  recommends the **top 3**, the metric that matches real use is **top-3 accuracy ≈ 94%** — i.e.
  the correct career is among the three shown ~94% of the time. (Random baseline on 24 classes
  is ~4%.)
- The profiles are grounded in an established psychological instrument (RIASEC), not invented.

**The mitigation is already built into the system — turn the weakness into a roadmap.**
The deployed application **saves every real student's profile and recommendation to MongoDB**
(`student_profiles` and `career_recommendations` collections). The platform is therefore
*designed to accumulate a real, labelled dataset over time.* The natural next phase is:
collect real responses → follow up on students' actual career choices → retrain on real data
→ compare against the synthetic baseline. The synthetic model is the cold-start; the platform
is the data-collection engine.

---

## 2. What the accuracy figure actually is

Two numbers, and it matters which you lead with (Random Forest, 24 careers):
- **Top-3 accuracy ≈ 94%** — *the headline*, because the app **recommends three careers**. The
  student's correct career is in the list ~94% of the time. This is the metric that matches how
  the product is actually used.
- **Top-1 accuracy ≈ 64%** (5-fold CV ≈ 65%) — picking exactly one career out of 24 overlapping
  classes. Still ~15× the ~4% random baseline.

If any earlier draft of the report quoted a single inflated figure, replace it with these. A
realistic top-1 with a strong top-3 is a *far* stronger position than a suspicious ~99%.

Per-career performance is uneven (expected): careers with distinctive profiles (e.g.
Graphic Designer, Teacher) score highest, while clusters that genuinely share a profile —
e.g. **Software Developer vs Cybersecurity Analyst** (both high Investigative + Programming),
or the engineering roles — are sometimes confused at top-1 but almost always both appear in the
top 3. This is honest: those careers really do overlap in interests and skills.

---

## 3. Model comparison — why Random Forest?

We did **not** assume Random Forest. We compared four standard classifiers on the **same**
train/test split (see `ml/model_comparison.csv` / `.png`):

| Model | Top-1 Acc | Top-3 Acc | F1 | CV Mean ± Std |
|---|---|---|---|---|
| SVM (RBF) | 68.72% | 95.52% | 68.68% | 67.94% ± 1.76 |
| Logistic Regression | 68.59% | 95.90% | 68.57% | 69.10% ± 1.39 |
| Gradient Boosting | 64.24% | — | 64.08% | 63.64% ± 0.72 |
| **Random Forest (deployed)** | 63.93% | 93.84% | 63.73% | 64.74% ± 1.38 |

**Finding:** the linear/SVM models lead Random Forest by ~5 points at **top-1**, but on the
metric that matches the product — **top-3** — the gap shrinks to ~2 points (93.8% vs ~95.5%).
Since the app recommends three careers, top-3 is the relevant comparison.

**Why we keep Random Forest:**
1. On the product-relevant metric (top-3) its accuracy is within ~2 points of the best.
2. It exposes native `feature_importances_`, which directly powers the per-prediction
   "Why this match" explanations in the app (see §4). This is a real interpretability win.
3. It needs no feature scaling and handles feature interactions robustly.

This is a deliberate **interpretability-vs-accuracy trade-off** — a recognised theme in applied
machine learning. *(If the examiner prefers raw top-1 accuracy as the priority, switching the
deployed model to Logistic Regression is a one-line change and the explainability can be made
model-agnostic — so the choice is defensible either way.)*

---

## 4. Explainability — the system now answers "why?"

Each recommendation lists, in **plain language**, the student's own strengths that most
support the match — e.g. *"You have strong programming skills."* / *"You enjoy analysing
problems and researching ideas."* (deliberately jargon-free and number-free, for non-technical
users). Under the hood this is a transparent contribution score: for a predicted career *c*,
every feature *f* gets:

```
contribution(f) = importance[f] × z(career_mean[f]) × z(user_value[f])
```

where `z(x) = (x − overall_mean) / overall_std`. A feature supports the match when it is
(a) important to the model, (b) distinctive of that career, and (c) the student scores in the
same direction. The top positive contributors are shown. This is transparent and fully
explainable in the report (it is a linearised, per-prediction contribution score — the same
intuition as SHAP, with no heavy dependency).

---

## 4b. The questionnaire — design, provenance, and a bias we found and fixed

**Where the questions come from.** The instrument has three parts:
- **18 interest items** (3 per RIASEC type), which operationalise **Holland's RIASEC theory**
  of vocational interests — the dominant, decades-old framework in career psychology.
- **10 self-assessed skill ratings** (1–5), chosen to match the model's 10 skill features.
- **CGPA** (self-reported) as a proxy for academic aptitude.

This tripartite basis — **interests + skills + academic performance** — is the standard
foundation of career guidance (the interest–aptitude–achievement model). So the *framework* is
grounded in established theory; the *specific items* are **researcher-authored operationalisations**
of that framework, written for this project. They are **not** a standardised, psychometrically
validated instrument.

**Honest answer to "how did you decide these questions define a student's career fit?"**
> "I didn't invent the constructs — I used an established model. Career fit is conventionally
> assessed along three axes: interests, skills, and academic ability. For interests I used
> Holland's RIASEC framework, the most widely used model in career counselling, and wrote three
> plain-language statements per type. Skills and CGPA capture aptitude and achievement. So the
> *what I measure* is theory-driven; I acknowledge the *specific wording* is my own and not yet
> psychometrically validated."

**A bias we identified through testing (and fixed).** Every interest item is positively worded
("I enjoy…"), and respondents tend to agree with most positive statements (**acquiescence bias**).
This produced flat, uniformly-high interest profiles. Because each career in the training data
has *one or two dominant* interest dimensions, a flat profile matched no specialist career and
**collapsed to the most generalist one — Teacher/Lecturer** — regardless of the student.

**The fix (implemented).** RIASEC is designed to be read as a *relative profile shape* (your
"Holland code" is your top interests **relative to your own other scores**). So in
`calculateRiasecScores` we now anchor each respondent at their own average interest level and
**amplify deviations** from it, restoring the contrast the model expects — no retraining needed.
After the fix, an analytically-leaning but agreeable student correctly matches Software
Developer/Data Scientist, while a genuinely people-oriented student still (correctly) matches
Teacher/HR.

**Do the questions need rewriting? Not for this milestone — but here's the credible upgrade
path.** Current weaknesses, owned honestly:
- Not psychometrically validated (no reliability/validity testing, e.g. Cronbach's alpha).
- Only 3 items per type (standard instruments use 8–15).
- All positively worded (the acquiescence issue above — mitigated by scoring, ideally also by
  adding reverse-keyed items).
- Skills are self-reported and therefore subjective.

**The single strongest improvement to cite:** adopt or adapt the **O\*NET Interest Profiler**
(U.S. Department of Labor — **public domain, free, validated**), the gold-standard free RIASEC
instrument. Saying *"a production version would adopt the validated O\*NET Interest Profiler
items and report reliability statistics on collected responses"* turns this from a gap into a
research roadmap.

---

## 5. Named limitations (own them before he raises them)

1. **CGPA barely influences the model.** Feature importance ranks CGPA **16th of 17** (~0.036).
   Cause: in the synthetic profiles most careers have similar CGPA, so it carries little
   discriminating signal. *Honest implication:* although "academic performance" is implied in
   the title, the recommendation is driven mainly by interests and skills. Fix path: in a real
   dataset, CGPA would vary far more meaningfully by field, and could be weighted per career.
2. **Skills are self-reported (1–5).** This introduces subjective bias (over-/under-confidence).
   A future version could validate skills with short objective tasks.
3. **Career coverage is now balanced, but still not exhaustive.** The set was expanded from 12
   (skewed toward technical roles) to **24 careers, 4 per RIASEC type** (see §5b). It covers the
   common destinations of Nigerian graduates but is not the full occupational space.
4. **No external validation yet.** Recommendations have not been checked by career counsellors
   or against students' real choices — the platform is built to enable exactly this next.

---

## 5b. Career selection — how the 24 careers were chosen

The careers are **not** an arbitrary list. They follow two principles:
1. **Full, balanced coverage of Holland's six RIASEC interest types** — exactly **4 careers per
   type** (Realistic, Investigative, Artistic, Social, Enterprising, Conventional), so every
   interest profile has several viable matches and no type is over-represented.
2. **Relevance to Nigerian university graduates** — real destinations across technology,
   engineering, health, finance, business, law, public service, education, and the creative
   industries.

| RIASEC type | Careers |
|---|---|
| Realistic | Civil/Mechanical Eng · Electrical/Electronics Eng · Agricultural Scientist · Architect/Urban Planner |
| Investigative | Software Developer · Data Scientist · Cybersecurity Analyst · Medical Lab Scientist |
| Artistic | Graphic Designer/UI-UX · Content Writer/Journalist · Film/Multimedia Producer · Fashion Designer |
| Social | Teacher/Lecturer · HR Manager · Nurse/Healthcare Professional · Guidance Counsellor/Social Worker |
| Enterprising | Entrepreneur · Marketing/Sales Executive · Lawyer/Legal Practitioner · Project/Operations Manager |
| Conventional | Accountant/Auditor · Banker/Financial Analyst · Public Administrator · Procurement/Supply-Chain Officer |

*Earlier the set was 12 careers and skewed (4 Investigative, only 1 Realistic and 1 Artistic).
We rebalanced it to demonstrate the system isn't biased toward tech roles.* **"Why 24 and not
more?"** — 24 keeps the synthetic data balanced and the demo clear; the architecture scales
trivially: adding a career is one more entry in `CAREER_PROFILES` plus a retrain. A production
version would derive the list from a validated occupational taxonomy such as **O\*NET**, filtered
to the Nigerian labour market.

---

## 6. Prepared viva questions & answers

**Q1. Where did your data come from?**
> Real student-to-career outcome data isn't accessible in Nigeria, so I built a theory-grounded
> synthetic dataset using Holland's RIASEC framework, with overlapping distributions so the task
> stays realistic. My metrics validate the pipeline, not real-world accuracy — and the app is
> built to collect real labelled data to retrain on later.

**Q2. Why Random Forest and not another algorithm?**
> I compared four — Logistic Regression, SVM, Gradient Boosting and Random Forest. The linear
> models lead by ~5 points at top-1, but on the metric that matches the product — top-3, since
> the app recommends three careers — the gap is only ~2 points. I kept Random Forest for its
> native feature importance, which powers the per-prediction explanations. It's a deliberate
> interpretability trade-off, and switching to Logistic Regression would be a one-line change
> if raw top-1 were the priority.

**Q3. What does your accuracy actually prove?**
> That the end-to-end system learns and serves meaningful patterns. With 24 overlapping careers,
> top-1 is ~64% but **top-3 is ~94%** — and since the product shows three recommendations, top-3
> is the honest metric. It is *not* a claim about real-world predictive accuracy; the realistic
> figures (vs a suspicious near-100%) reflect that my classes genuinely overlap.

**Q4. How does a student know *why* they got a recommendation?**
> Each result lists the student's own answers that most drove it, computed from the model's
> feature importance combined with how distinctive each feature is for that career. It's
> transparent and explainable, not a black box.

**Q5. How do you know the recommendations are any good?**
> Internally, via cross-validation and per-career metrics. Externally — and I'm honest that this
> is the next step — the platform stores real profiles and recommendations, so it's built to
> support a user study and expert (counsellor) validation, then retraining on real outcomes.

**Q6. How did you come up with the questions, and how do they define a student's career fit?**
> I didn't invent the constructs. Career fit is conventionally assessed along three axes —
> interests, skills, and academic ability. For interests I used Holland's RIASEC framework, the
> most established model in career counselling, and wrote three plain statements per type; skills
> and CGPA capture aptitude and achievement. So *what* I measure is theory-driven. I'm honest
> that the specific wording is my own and not yet psychometrically validated, and that a
> production version would adopt the validated, public-domain O\*NET Interest Profiler.

**Q7. A colleague tried it and kept getting "Teacher/Lecturer" — why?**
> I found that too, and traced it to acquiescence bias: positively-worded items make people agree
> with most statements, producing a flat interest profile that matched the most generalist career.
> I fixed it by scoring RIASEC *relatively* — the way Holland codes are meant to be read —
> amplifying each person's strongest interests so specialist profiles come through. It now matches
> Teacher only for genuinely people-oriented students.

---

## 7. One-line summary for the meeting
> "I built a complete, deployed, explainable system that matches students to **24 careers
> balanced across all six RIASEC types**. The correct career is in the top-3 recommendations
> ~94% of the time. I'm honest that the data is synthetic — it validates the pipeline, not
> real-world outcomes — and I've designed the platform to collect the real data needed to close
> that gap."
