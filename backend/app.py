"""
Flask Backend (PHASE B) — AI-Powered Career Path Recommender
Lagos State University | Author: Adegbite Moyomade Akanji

Adds MongoDB Atlas integration to Phase A. Now the system:
  - loads the trained Random Forest model
  - connects to MongoDB Atlas
  - saves users, student profiles, and recommendations (matches the ERD)
  - can return a user's recommendation history (for the dashboard)

Run with:  python app.py
Server starts on http://127.0.0.1:5000
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

# ------------------------------------------------------------------
# 1. APP + CONFIG
# ------------------------------------------------------------------
load_dotenv()  # read .env so MONGO_URI is available

app = Flask(__name__)
CORS(app)

# JWT settings for login tokens.
# No insecure fallback: if JWT_SECRET is missing we fail loudly at startup
# rather than silently signing tokens with a publicly-known default secret
# (which would let anyone forge a valid login token).
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET is not set. Add a strong, random value to your .env file "
        "before starting the server."
    )
JWT_EXPIRY_DAYS = 7

# ------------------------------------------------------------------
# 2. LOAD THE TRAINED MODEL (once, at startup)
# ------------------------------------------------------------------
print("Loading model files...")
model = joblib.load('career_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')
feature_names = joblib.load('feature_names.pkl')
print(f"Model loaded. Expects {len(feature_names)} features.")

# ------------------------------------------------------------------
# 3. CONNECT TO MONGODB ATLAS (once, at startup)
# ------------------------------------------------------------------
print("Connecting to MongoDB Atlas...")
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# A database named 'career_recommender'. The 3 collections match the ERD.
db = client['career_recommender']
users_col = db['users']
profiles_col = db['student_profiles']
recommendations_col = db['career_recommendations']

# Verify the connection now so we fail fast if something's wrong
try:
    client.admin.command('ping')
    DB_CONNECTED = True
    print("MongoDB connected.")
except Exception as e:
    DB_CONNECTED = False
    print(f"WARNING: MongoDB connection failed: {e}")


# ------------------------------------------------------------------
# Helper: run the model and return the top 3 careers
# ------------------------------------------------------------------
def get_top_3(data):
    """Takes a dict of the 17 features, returns list of top-3 dicts."""
    feature_values = [float(data[f]) for f in feature_names]
    input_array = np.array(feature_values).reshape(1, -1)

    probabilities = model.predict_proba(input_array)[0]
    paired = list(zip(label_encoder.classes_, probabilities))
    paired.sort(key=lambda x: x[1], reverse=True)

    return [
        {'career': career, 'match_percentage': round(float(prob) * 100, 1)}
        for career, prob in paired[:3]
    ]


# ------------------------------------------------------------------
# Helpers: authentication (JWT)
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# 4. HEALTH CHECK
# ------------------------------------------------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'Career Path Recommender API is running.',
        'database_connected': DB_CONNECTED,
        'expected_features': feature_names
    })


# ------------------------------------------------------------------
# 4b. AUTH (register / login / me)
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# 5. PREDICT + SAVE
# ------------------------------------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    """
    Expects JSON with the 17 features. Runs the model and returns the top 3.
    If the request carries a valid login token, the profile + recommendation
    are saved to that user's history. Guests get results but nothing is saved.
    """
    try:
        data = request.get_json()

        # --- Validate features ---
        missing = [f for f in feature_names if f not in data]
        if missing:
            return jsonify({'error': 'Missing required fields',
                            'missing_fields': missing}), 400

        # --- Run the model ---
        top_3 = get_top_3(data)

        # --- Identity comes from the login token, not the request body ---
        user = get_current_user()  # None for guests
        now = datetime.now(timezone.utc)

        saved_id = None
        saved = False
        if user and DB_CONNECTED:
            email = user['email']

            # (a) save the student profile (the 17 inputs)
            profile_doc = {'user_email': email, 'created_at': now}
            for f in feature_names:
                profile_doc[f] = float(data[f])
            profile_result = profiles_col.insert_one(profile_doc)

            # (b) save the recommendation, linked to the profile + user
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
        # Bad input from the client. Log the detail for us, keep the user message generic.
        app.logger.warning('Invalid input to /predict: %s', e)
        return jsonify({'error': 'Some of your answers were invalid. Please review them and try again.'}), 400
    except Exception:
        # Never expose raw exception text to the client (information disclosure).
        app.logger.exception('Unexpected error in /predict')
        return jsonify({'error': 'Something went wrong while generating your results. Please try again.'}), 500


# ------------------------------------------------------------------
# 6. HISTORY (for the dashboard)
# ------------------------------------------------------------------
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
        # Convert non-JSON-friendly fields to strings
        for r in records:
            r['_id'] = str(r['_id'])
            r['profile_id'] = str(r['profile_id'])
            r['date_generated'] = r['date_generated'].isoformat()

        return jsonify({'email': email, 'count': len(records), 'history': records})
    except Exception:
        app.logger.exception('Error fetching history')
        return jsonify({'error': 'We were unable to load your history. Please try again.'}), 500


# ------------------------------------------------------------------
# 7. STATS (nice for demos)
# ------------------------------------------------------------------
@app.route('/stats', methods=['GET'])
def stats():
    if not DB_CONNECTED:
        return jsonify({'error': 'Database not connected'}), 503
    return jsonify({
        'total_users': users_col.count_documents({}),
        'total_profiles': profiles_col.count_documents({}),
        'total_recommendations': recommendations_col.count_documents({})
    })


# ------------------------------------------------------------------
# 8. START
# ------------------------------------------------------------------
if __name__ == '__main__':
    # Local dev only. In production Render runs `gunicorn app:app`
    # (see ../render.yaml), which imports `app` and ignores this block.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)