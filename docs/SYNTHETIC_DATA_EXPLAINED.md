# How the Synthetic Dataset Works (Plain-Language Explanation)

**For:** understanding the data well enough to explain and defend it in the report / viva.
**Code it describes:** `ml/generate_dataset.py`.

---

## 1. The 30-second version (say this if asked)

> "I couldn't find a real dataset of Nigerian students linked to verified career outcomes, so I
> generated a realistic one. I defined a 'profile' for each of the 24 careers — what a typical
> person in that career looks like across interests, skills and CGPA — and then created hundreds
> of slightly different, randomly-varied students around each profile. The randomness makes the
> careers overlap, so the model has to genuinely learn patterns rather than memorise fixed rules.
> The profiles are based on Holland's RIASEC theory and my reasoning about each career; I'm
> honest that they're informed estimates, not measured from real people."

Everything below is the detail behind that paragraph.

---

## 2. Why synthetic data at all?

A supervised model learns from examples: "here is a student, here is the career that fits them."
To train one you need many such labelled examples. That dataset **does not exist** in any
accessible form for Nigerian university students. The options were:
1. Run a large survey and track real career outcomes — not feasible in a final-year timeframe.
2. **Generate a principled synthetic dataset** — chosen, and standard practice when real labelled
   data is unavailable (synthetic data is widely used to prototype ML systems).

So the dataset is a **stand-in that lets the whole system be built and tested end-to-end.**

---

## 3. The core idea — "a fingerprint per career, then noisy copies"

Think of each career as having a **fingerprint**: the *typical* scores a person in that career
would have. For example, a typical **Data Scientist** is very investigative, strong at maths and
data analysis, with a high CGPA — but only average at public speaking.

We don't make every Data Scientist identical (that would be unrealistic and too easy for the
model). Instead, for each career we generate **335 students who are all *near* the fingerprint
but each slightly different** — exactly like real people in the same job aren't clones of each
other.

That "slightly different" is created with a **normal distribution** (the bell curve). Two numbers
define it:
- **Mean** = the typical value (the centre of the bell).
- **Standard deviation (std)** = how spread out people are around that typical value (a wide bell
  = lots of variation; a narrow bell = everyone similar).

---

## 4. What's actually in the data (the 17 features)

Every generated student is a row of **17 numbers + 1 career label**:

| Group | Features | Scale |
|---|---|---|
| RIASEC interests | Realistic, Investigative, Artistic, Social, Enterprising, Conventional | 1–10 |
| Academic | CGPA | 1.5–5.0 (Nigerian 5.0 scale) |
| Skills | Programming, Mathematics, ProblemSolving, Communication, Leadership, Creativity, Technical, DataAnalysis, PublicSpeaking, Research | 1–5 |

The career label (e.g. "Data Scientist") is what the model learns to predict.

---

## 5. How one student is generated (step by step)

In `generate_dataset.py`, every career has a `CAREER_PROFILES` entry giving a **(mean, std)** pair
for each feature. To create one student we draw each feature from its bell curve and clip it to a
sensible range so we never get impossible values:

```python
def sample_clipped(mean, std, low, high):
    sample = np.random.normal(loc=mean, scale=std)   # draw from the bell curve
    return np.clip(sample, low, high)                 # keep it within valid bounds
```

**Worked example — generating one Data Scientist.** The Data Scientist profile includes:
- Investigative interest: mean **9.0**, std **0.8** → a draw might give **8.6**
- Mathematics skill: mean **4.7**, std **0.4** → a draw might give **4.9**
- Public Speaking skill: mean **3.0**, std **1.0** → a draw might give **2.4**
- CGPA: mean **4.1**, std **0.4** → a draw might give **3.9**

…and so on for all 17 features. The result is *one* realistic-looking Data Scientist who is
clearly investigative and mathematical but only average at public speaking — close to the
fingerprint, but unique. Repeat 335 times and you have 335 distinct Data Scientists.

This is done for all 24 careers → **335 × 24 = 8,040 students**, then the rows are shuffled and
rounded. A **fixed random seed (42)** means anyone who re-runs the script gets the *exact same*
dataset — important for reproducibility (your examiner can verify it).

---

## 6. The design choices, and *why* (this is what earns marks)

These are deliberate, documented decisions — not accidents:

1. **Overlapping bells, not fixed rules.** Because each feature has spread (std), the careers'
   distributions *overlap*. A given student could plausibly belong to two careers. This forces
   the model to **learn statistical patterns** instead of memorising a lookup table — and it's
   why accuracy is a realistic ~64% top-1 (≈94% top-3), not a suspicious ~100%.
2. **Grounded in RIASEC theory.** The interest fingerprints follow Holland's RIASEC framework —
   each career's dominant interest type matches the established theory (e.g. artistic careers
   score high on Artistic). The data isn't arbitrary; it encodes a recognised model.
3. **Class-balanced.** Exactly 335 students per career, so the model isn't biased toward any
   career just because it has more examples.
4. **Reproducible.** The fixed seed makes the dataset regenerable and verifiable.

---

## 7. How the profile numbers were actually chosen (be honest about this)

Where did "Investigative = 9.0" for Data Scientist come from? **Informed estimation**, combining:
- **RIASEC theory** — which interest type each career is known to map to.
- **Reasoning about each career's real demands** — e.g. Data Scientists obviously need high
  Maths/Data-Analysis; Marketing Executives need high Communication/Public-Speaking and low
  Programming.
- **A choice to keep careers distinguishable but realistically overlapping** — close enough to
  confuse, distinct enough to separate.

**Say this plainly:** the means and spreads are *theory-guided, reasoned estimates*, **not values
measured from real students.** That is the honest limitation, and it's why the headline claim is
"this validates the pipeline," not "this predicts real careers." (See `LIMITATIONS_AND_VIVA.md`.)

---

## 8. An analogy you can use out loud

> "It's like a flight simulator. The simulator isn't a real plane, but it's built from the real
> physics of flying, so you can genuinely learn and test in it. My synthetic data isn't real
> students, but it's built from the real theory of career interests (RIASEC), so the system can
> be genuinely built and tested. The final step — like moving from simulator to real cockpit — is
> retraining on the real student data the app is designed to collect."

---

## 9. One-line takeaway
> "Each career has a theory-based profile; I generate hundreds of randomly-varied students around
> each profile so the classes overlap realistically. It validates the system end-to-end, and the
> app is built to collect the real data that would eventually replace it."
