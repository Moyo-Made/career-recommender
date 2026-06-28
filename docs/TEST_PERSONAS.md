# Test Personas — Demo Answer Keys (24-career model)

Use these to demonstrate the recommender across the new, balanced career set. Each persona
was generated from the target career's profile and **verified** against the deployed model.

## How to enter them
The interest quiz has 18 questions, 3 per RIASEC type, in this order:
- **Q1–3 = Realistic (R)** · **Q4–6 = Investigative (I)** · **Q7–9 = Artistic (A)**
- **Q10–12 = Social (S)** · **Q13–15 = Enterprising (E)** · **Q16–18 = Conventional (C)**

So "**R,I,A,S,E,C = 4,4,2,2,2,3**" means: answer **4** to Q1–3, **4** to Q4–6, **2** to Q7–9,
**2** to Q10–12, **2** to Q13–15, **3** to Q16–18.
*(Scale: 1 = Strongly disagree … 5 = Strongly agree.)*

Skills are entered 1–5 in this order:
**Prog, Math, ProblemSolving, Comm, Leadership, Creativity, Technical, DataAnalysis, PublicSpeaking, Research.**

Match % will be within a rounding tick of what's shown; the **#1 match is the target**.

---

### REALISTIC group

**1. Electrical/Electronics Engineer** → expected **#1 ≈ 35%**
- Interests R,I,A,S,E,C = **4, 4, 2, 2, 2, 3**
- Skills = 3, 4, 4, 3, 3, 3, **5**, 4, 3, 4   ·   CGPA = **3.7**

**2. Agricultural Scientist/Agronomist** → expected **#1 ≈ 47%**
- Interests = **4, 4, 2, 3, 2, 3**
- Skills = 2, 3, 4, 3, 3, 3, 4, 4, 3, **4**   ·   CGPA = **3.6**

**3. Architect/Urban Planner** → expected **#1 ≈ 92%**
- Interests = **4, 3, 4, 2, 3, 3**
- Skills = 3, 4, 4, 4, 3, **4**, **4**, 3, 3, 4   ·   CGPA = **3.5**

### ARTISTIC group

**4. Content Writer/Journalist** → expected **#1 ≈ 93%**
- Interests = **1, 3, 4, 3, 3, 2**
- Skills = 2, 2, 4, **5**, 3, 4, 2, 3, 4, 4   ·   CGPA = **3.4**

**5. Film/Multimedia Producer** → expected **#1 ≈ 46%**
- Interests = **2, 2, 4, 3, 4, 2**
- Skills = 2, 3, 4, 4, 4, 4, 4, 3, 4, 3   ·   CGPA = **3.3**

**6. Fashion Designer** → expected **#1 ≈ 77%**
- Interests = **2, 2, 4, 2, 3, 2**
- Skills = 2, 2, 3, 4, 3, **5**, 4, 3, 3, 3   ·   CGPA = **3.1**

### SOCIAL group

**7. Nurse/Healthcare Professional** → expected **#1 ≈ 92%**
- Interests = **3, 3, 2, 4, 2, 3**
- Skills = 2, 3, 4, 4, 3, 3, 4, 3, 3, 4   ·   CGPA = **3.6**

**8. Guidance Counsellor/Social Worker** → expected **#1 ≈ 56%**
- Interests = **2, 3, 2, 4, 2, 3**
- Skills = 2, 3, 4, **5**, 4, 3, 2, 3, 4, 4   ·   CGPA = **3.4**

### ENTERPRISING group

**9. Lawyer/Legal Practitioner** → expected **#1 ≈ 68%**
- Interests = **1, 3, 2, 3, 4, 3**
- Skills = 2, 3, 4, **5**, 4, 3, 2, 3, **5**, 4   ·   CGPA = **3.6**

**10. Project/Operations Manager** → expected **#1 ≈ 42%**
- Interests = **2, 3, 2, 3, 4, 3**
- Skills = 2, 3, 4, 4, **5**, 3, 3, 3, 4, 3   ·   CGPA = **3.5**

### CONVENTIONAL group

**11. Public Administrator/Civil Servant** → expected **#1 ≈ 46%**
- Interests = **2, 3, 2, 3, 3, 4**
- Skills = 2, 3, 4, 4, 4, 3, 3, 4, 3, 3   ·   CGPA = **3.4**

**12. Procurement/Supply-Chain Officer** → expected **#1 ≈ 27%** *(close pair with Accountant & Public Admin)*
- Interests = **2, 3, 2, 3, 3, 4**
- Skills = 3, 4, 4, 4, 4, 3, 3, 4, 3, 3   ·   CGPA = **3.5**

---

### Notes for the demo
- The **lower-confidence** matches (Engineer ~35%, Procurement ~27%) are the *honest* cases:
  careers that genuinely overlap with neighbours (the two engineers; the Conventional finance/admin
  cluster). Their true career still tops the list, and the rest of the top 3 are sensible cousins —
  good evidence the model reasons by profile, not by memorisation.
- The **high-confidence** matches (Content Writer, Architect, Nurse ~90%+) show the model is
  decisive when a profile is distinctive.
