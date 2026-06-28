"""
Course-of-study relevance layer for the Career Path Recommender.

The ML model scores careers from interests, CGPA and skills only — it has no idea
what the student actually studied. On its own it can recommend careers that make
no sense for the degree (telling a Law student to become a Fashion Designer, or a
Computer Science student to become a Lawyer). This module restricts the model's
output to the careers a given degree can realistically lead to, and lets the model
rank *within* that relevant set.

For each course we hand-author an ordered list of relevant careers (most relevant
first). A career is then assigned a tier for that course:
    1 = the degree's flagship career      -> boosted so it reliably surfaces
    2 = relevant to the degree            -> allowed, ranked by personality/skills
    3 = not relevant to the degree        -> excluded from results

There is no ML in this mapping on purpose: it is hand-authored and auditable, which
is what makes the recommendations defensible. An empty course or one we don't
recognise (free text / "Other") disables filtering — every career stays eligible.

Career names below MUST match label_encoder.classes_ (the 24 careers in
ml/generate_dataset.py). COURSES MUST match COURSES in
frontend/src/assessmentData.js — together they are the client/server contract.
"""

# Sentinel for "I don't see my course" — disables filtering for that user.
OTHER_COURSE = 'Other / Not listed'

# How many of each course's leading careers get the flagship relevance boost.
PRIMARY_COUNT = 1

# Curated list of degrees. Keep in sync with frontend/src/assessmentData.js.
# (Derived from COURSE_CAREERS below plus the "Other" sentinel.)
COURSE_CAREERS = {
    'Computer Science': [
        'Software Developer', 'Data Scientist', 'Cybersecurity Analyst',
        'Project/Operations Manager', 'Entrepreneur',
    ],
    'Software Engineering': [
        'Software Developer', 'Cybersecurity Analyst', 'Data Scientist',
        'Project/Operations Manager', 'Entrepreneur',
    ],
    'Information Technology': [
        'Software Developer', 'Cybersecurity Analyst', 'Data Scientist',
        'Project/Operations Manager', 'Procurement/Supply-Chain Officer',
    ],
    'Cybersecurity': [
        'Cybersecurity Analyst', 'Software Developer', 'Data Scientist',
        'Project/Operations Manager',
    ],
    'Mathematics / Statistics': [
        'Data Scientist', 'Software Developer', 'Banker/Financial Analyst',
        'Accountant/Auditor', 'Teacher/Lecturer',
    ],
    'Law': [
        'Lawyer/Legal Practitioner', 'Public Administrator/Civil Servant',
        'Human Resources Manager', 'Content Writer/Journalist',
        'Project/Operations Manager', 'Entrepreneur',
    ],
    'Accounting': [
        'Accountant/Auditor', 'Banker/Financial Analyst',
        'Procurement/Supply-Chain Officer', 'Public Administrator/Civil Servant',
        'Entrepreneur',
    ],
    'Banking & Finance': [
        'Banker/Financial Analyst', 'Accountant/Auditor', 'Data Scientist',
        'Marketing/Sales Executive', 'Entrepreneur',
    ],
    'Economics': [
        'Banker/Financial Analyst', 'Data Scientist',
        'Public Administrator/Civil Servant', 'Accountant/Auditor',
        'Marketing/Sales Executive', 'Entrepreneur',
    ],
    'Business Administration': [
        'Project/Operations Manager', 'Marketing/Sales Executive',
        'Human Resources Manager', 'Entrepreneur',
        'Procurement/Supply-Chain Officer', 'Banker/Financial Analyst',
    ],
    'Marketing': [
        'Marketing/Sales Executive', 'Content Writer/Journalist',
        'Graphic Designer/UI-UX', 'Project/Operations Manager', 'Entrepreneur',
    ],
    'Mass Communication': [
        'Content Writer/Journalist', 'Film/Multimedia Producer',
        'Marketing/Sales Executive', 'Graphic Designer/UI-UX',
        'Public Administrator/Civil Servant',
    ],
    'Public Administration': [
        'Public Administrator/Civil Servant', 'Human Resources Manager',
        'Project/Operations Manager', 'Procurement/Supply-Chain Officer',
        'Guidance Counsellor/Social Worker',
    ],
    'Architecture': [
        'Architect/Urban Planner', 'Graphic Designer/UI-UX',
        'Civil/Mechanical Engineer', 'Project/Operations Manager', 'Entrepreneur',
    ],
    'Civil Engineering': [
        'Civil/Mechanical Engineer', 'Architect/Urban Planner',
        'Project/Operations Manager', 'Procurement/Supply-Chain Officer',
        'Entrepreneur',
    ],
    'Mechanical Engineering': [
        'Civil/Mechanical Engineer', 'Electrical/Electronics Engineer',
        'Project/Operations Manager', 'Procurement/Supply-Chain Officer',
        'Entrepreneur',
    ],
    'Electrical/Electronics Engineering': [
        'Electrical/Electronics Engineer', 'Software Developer',
        'Cybersecurity Analyst', 'Project/Operations Manager', 'Entrepreneur',
    ],
    'Agricultural Science': [
        'Agricultural Scientist/Agronomist', 'Procurement/Supply-Chain Officer',
        'Data Scientist', 'Teacher/Lecturer', 'Entrepreneur',
    ],
    'Medical Laboratory Science': [
        'Medical Lab Scientist', 'Data Scientist', 'Teacher/Lecturer',
        'Procurement/Supply-Chain Officer', 'Entrepreneur',
    ],
    'Nursing': [
        'Nurse/Healthcare Professional', 'Guidance Counsellor/Social Worker',
        'Teacher/Lecturer', 'Human Resources Manager', 'Entrepreneur',
    ],
    'Medicine & Surgery': [
        'Nurse/Healthcare Professional', 'Medical Lab Scientist',
        'Guidance Counsellor/Social Worker', 'Teacher/Lecturer', 'Data Scientist',
    ],
    'Biochemistry / Microbiology': [
        'Medical Lab Scientist', 'Data Scientist',
        'Agricultural Scientist/Agronomist', 'Teacher/Lecturer', 'Entrepreneur',
    ],
    'Education': [
        'Teacher/Lecturer', 'Guidance Counsellor/Social Worker',
        'Human Resources Manager', 'Content Writer/Journalist',
        'Public Administrator/Civil Servant',
    ],
    'English / Literature': [
        'Content Writer/Journalist', 'Teacher/Lecturer',
        'Public Administrator/Civil Servant', 'Marketing/Sales Executive',
        'Film/Multimedia Producer',
    ],
    'Fine & Applied Arts': [
        'Graphic Designer/UI-UX', 'Film/Multimedia Producer', 'Fashion Designer',
        'Content Writer/Journalist', 'Entrepreneur',
    ],
    'Fashion Design': [
        'Fashion Designer', 'Graphic Designer/UI-UX', 'Marketing/Sales Executive',
        'Film/Multimedia Producer', 'Entrepreneur',
    ],
}

# Ordered list for the frontend dropdown / contract: every course, then "Other".
COURSES = list(COURSE_CAREERS.keys()) + [OTHER_COURSE]


def relevance_tier(course, career):
    """
    Return 1 (flagship career for the degree), 2 (relevant to the degree) or
    3 (not relevant — excluded) for the given course/career pair.

    An empty course, the "Other / Not listed" sentinel, or any course we don't
    recognise disables filtering: every career is treated as Tier 2.
    """
    careers = COURSE_CAREERS.get(course)
    if not course or course == OTHER_COURSE or careers is None:
        return 2

    if career not in careers:
        return 3
    return 1 if careers.index(career) < PRIMARY_COUNT else 2


def flagship_career(course):
    """The degree's primary career (first in its list), or None if unrecognised."""
    careers = COURSE_CAREERS.get(course)
    if not course or course == OTHER_COURSE or not careers:
        return None
    return careers[0]
