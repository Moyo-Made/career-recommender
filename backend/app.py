"""
Flask backend for the AI-Powered Career Path Recommender.

Loads the trained Random Forest, serves predictions with plain-language
explanations, handles JWT auth, and persists users / profiles / recommendations
to MongoDB Atlas. Run locally with `python app.py`; in production Render runs
`gunicorn app:app` (see ../render.yaml).
"""

import os
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from career_relevance import relevance_tier, flagship_career

load_dotenv()

app = Flask(__name__)
CORS(app)

# Fail loudly if JWT_SECRET is missing rather than signing tokens with a known
# default secret (which would let anyone forge a valid login token).
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET is not set. Add a strong, random value to your .env file "
        "before starting the server."
    )
JWT_EXPIRY_DAYS = 7

# Trained model + explainability artifacts (produced by ml/train_model.py).
# class_profiles: per-career mean of each feature. feature_stats: overall mean/std.
model = joblib.load('career_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')
feature_names = joblib.load('feature_names.pkl')
class_profiles = joblib.load('class_profiles.pkl')
feature_stats = joblib.load('feature_stats.pkl')

# Plain-language phrases for explanations. Each completes the sentence "You ...".
FEATURE_LABELS = {
    'Realistic': 'enjoy hands-on, practical work',
    'Investigative': 'enjoy analysing problems and researching ideas',
    'Artistic': 'have a creative, original streak',
    'Social': 'enjoy helping and working with people',
    'Enterprising': 'enjoy leading, persuading and taking initiative',
    'Conventional': 'are organised and detail-oriented',
    'CGPA': 'have solid academic performance',
    'Programming': 'have strong programming skills',
    'Mathematics': 'are strong with maths and numbers',
    'ProblemSolving': 'are a strong problem-solver',
    'Communication': 'have strong communication skills',
    'Leadership': 'have good leadership ability',
    'Creativity': 'have a creative flair',
    'Technical': 'have strong technical, hands-on skills',
    'DataAnalysis': 'are good at analysing data and spotting patterns',
    'PublicSpeaking': 'are confident speaking in public',
    'Research': 'have strong research skills',
}

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client['career_recommender']
users_col = db['users']
profiles_col = db['student_profiles']
recommendations_col = db['career_recommendations']

# Ping now so we fail fast (and so guests still work if the DB is down).
try:
    client.admin.command('ping')
    DB_CONNECTED = True
    print("MongoDB connected.")
except Exception as e:
    DB_CONNECTED = False
    print(f"WARNING: MongoDB connection failed: {e}")


def explain(data, career, top_n=3):
    """
    Explain WHY a student matches a career, in plain language.

    Each feature gets a contribution score:
        importance[f] * z(career_mean[f]) * z(user_value[f]),  z = (x - mean) / std
    A feature supports the match when it is important to the model, distinctive of
    the career, and the student scores in the same direction. The top positive
    contributors become reasons like "You enjoy analysing problems...".
    """
    importances = dict(zip(feature_names, model.feature_importances_))
    profile = class_profiles.loc[career]
    contributions = []
    for f in feature_names:
        mean = float(feature_stats.loc[f, 'mean'])
        std = float(feature_stats.loc[f, 'std'])
        z_career = (float(profile[f]) - mean) / std
        z_user = (float(data[f]) - mean) / std
        score = importances[f] * z_career * z_user
        contributions.append((f, score))

    contributions.sort(key=lambda x: x[1], reverse=True)
    reasons = []
    for f, score in contributions[:top_n]:
        # Skip near-average features that carry no real signal.
        if score <= 1e-3:
            break
        reasons.append(f"You {FEATURE_LABELS.get(f, f)}.")
    return reasons


# How strongly to favour the student's flagship career within the relevant set.
TIER1_BOOST = 1.6


def get_top_3(data, course=''):
    """
    Run the model on the 17 features and return the top-3 careers with reasons,
    restricted and re-ranked by the student's course of study.

    Careers not relevant to the degree (Tier 3) are dropped; the degree's flagship
    career (Tier 1) gets a boost. Match percentages are renormalised across the
    eligible careers so they stay meaningful once the irrelevant ones are removed.
    The flagship career is always included in the results, even if the student's
    interests rank it low. An empty/unrecognised ("Other") course disables filtering.
    """
    feature_values = [float(data[f]) for f in feature_names]
    input_array = np.array(feature_values).reshape(1, -1)

    probabilities = model.predict_proba(input_array)[0]

    weighted = []
    for career, prob in zip(label_encoder.classes_, probabilities):
        tier = relevance_tier(course, career)
        if tier == 3:
            continue  # not relevant to the student's degree — never recommend
        weight = TIER1_BOOST if tier == 1 else 1.0
        weighted.append((career, float(prob) * weight))

    weighted.sort(key=lambda x: x[1], reverse=True)

    # Soften the distribution before turning it into match scores. RandomForest
    # probabilities are overconfident, and restricting to a small relevant set
    # makes them near-binary (96% / 0%). A square-root "temperature" spreads them
    # into a believable gradient of fit scores.
    softened = {career: score ** 0.5 for career, score in weighted}
    total = sum(softened.values()) or 1.0
    pct = {career: round(softened[career] / total * 100, 1) for career in softened}

    top_careers = [career for career, _ in weighted[:3]]

    # Guarantee the degree's flagship career is always shown (e.g. a Law student
    # always sees "Lawyer"). If ranking dropped it, swap it into the last slot and
    # flag it as the degree's core path so the UI can label it rather than show a
    # poor fit score.
    flagship = flagship_career(course)
    forced_flagship = (
        bool(flagship) and flagship in pct and flagship not in top_careers
    )
    if forced_flagship:
        top_careers = top_careers[:2] + [flagship]

    return [
        {
            'career': career,
            'match_percentage': pct[career],
            'reasons': explain(data, career),
            'core_path': forced_flagship and career == flagship,
        }
        for career in top_careers
    ]


def make_token(user):
    """Create a signed JWT for a user document."""
    payload = {
        'email': user['email'],
        'name': user.get('name', ''),
        'exp': datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def get_current_user():
    """Return the user document for a valid Bearer token, else None."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth.split(' ', 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.PyJWTError:
        return None
    if not DB_CONNECTED:
        return None
    return users_col.find_one({'email': payload.get('email')})


def login_required(f):
    """Reject the request with 401 unless a valid token is present."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required. Please log in.'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return wrapper


def public_user(user):
    """Strip sensitive fields before returning a user to the client."""
    return {'name': user.get('name', ''), 'email': user['email']}


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'Career Path Recommender API is running.',
        'database_connected': DB_CONNECTED,
        'expected_features': feature_names
    })


@app.route('/auth/register', methods=['POST'])
def register():
    if not DB_CONNECTED:
        return jsonify({'error': 'Database not connected'}), 503

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are all required.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400
    if users_col.find_one({'email': email}):
        return jsonify({'error': 'An account with this email already exists.'}), 409

    user = {
        'name': name,
        'email': email,
        'password_hash': generate_password_hash(password),
        'created_at': datetime.now(timezone.utc),
    }
    users_col.insert_one(user)
    return jsonify({'token': make_token(user), 'user': public_user(user)}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    if not DB_CONNECTED:
        return jsonify({'error': 'Database not connected'}), 503

    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = users_col.find_one({'email': email})
    if not user or not user.get('password_hash') \
            or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    return jsonify({'token': make_token(user), 'user': public_user(user)})


@app.route('/auth/me', methods=['GET'])
@login_required
def me():
    return jsonify({'user': public_user(request.current_user)})


@app.route('/predict', methods=['POST'])
def predict():
    """
    Run the model on the 17 features and return the top 3. A valid login token
    also saves the profile + recommendation to that user's history; guests get
    results but nothing is saved.
    """
    try:
        data = request.get_json()

        missing = [f for f in feature_names if f not in data]
        if missing:
            return jsonify({'error': 'Missing required fields',
                            'missing_fields': missing}), 400

        # Course of study is not a model feature; it drives post-prediction
        # relevance filtering only, and is optional for backward compatibility.
        course = (data.get('Course') or '').strip()
        top_3 = get_top_3(data, course)

        # Identity comes from the login token, not the request body.
        user = get_current_user()
        now = datetime.now(timezone.utc)

        saved_id = None
        saved = False
        if user and DB_CONNECTED:
            email = user['email']

            profile_doc = {'user_email': email, 'created_at': now, 'Course': course}
            for f in feature_names:
                profile_doc[f] = float(data[f])
            profile_result = profiles_col.insert_one(profile_doc)

            rec_doc = {
                'user_email': email,
                'profile_id': profile_result.inserted_id,
                'recommendations': top_3,
                'date_generated': now
            }
            rec_result = recommendations_col.insert_one(rec_doc)
            saved_id = str(rec_result.inserted_id)
            saved = True

        return jsonify({
            'success': True,
            'recommendations': top_3,
            'saved': saved,
            'record_id': saved_id
        })

    except (ValueError, TypeError) as e:
        app.logger.warning('Invalid input to /predict: %s', e)
        return jsonify({'error': 'Some of your answers were invalid. Please review them and try again.'}), 400
    except Exception:
        # Never leak raw exception text to the client (information disclosure).
        app.logger.exception('Unexpected error in /predict')
        return jsonify({'error': 'Something went wrong while generating your results. Please try again.'}), 500


@app.route('/history', methods=['GET'])
@login_required
def history():
    """Return the logged-in user's own past recommendations."""
    if not DB_CONNECTED:
        return jsonify({'error': 'Database not connected'}), 503
    email = request.current_user['email']
    try:
        records = list(
            recommendations_col.find({'user_email': email})
            .sort('date_generated', -1)
        )
        for r in records:
            r['_id'] = str(r['_id'])
            r['profile_id'] = str(r['profile_id'])
            r['date_generated'] = r['date_generated'].isoformat()

        return jsonify({'email': email, 'count': len(records), 'history': records})
    except Exception:
        app.logger.exception('Error fetching history')
        return jsonify({'error': 'We were unable to load your history. Please try again.'}), 500


@app.route('/stats', methods=['GET'])
def stats():
    if not DB_CONNECTED:
        return jsonify({'error': 'Database not connected'}), 503
    return jsonify({
        'total_users': users_col.count_documents({}),
        'total_profiles': profiles_col.count_documents({}),
        'total_recommendations': recommendations_col.count_documents({})
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
