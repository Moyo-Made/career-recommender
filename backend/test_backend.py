"""
Test script for the Phase B backend (with database).
Run app.py in one terminal, then run this in a second terminal.

Usage:  python test_backend.py
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

# ------------------------------------------------------------------
# Test 1: Health check (should show database_connected: true)
# ------------------------------------------------------------------
print("=" * 55)
print("TEST 1: Health check")
print("=" * 55)
r = requests.get(BASE_URL + '/')
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# ------------------------------------------------------------------
# Test 2: Predict + save for a tech student (with name/email)
# ------------------------------------------------------------------
print("=" * 55)
print("TEST 2: Predict + SAVE (tech student)")
print("=" * 55)
tech_student = {
    "name": "Tunde Bello",
    "email": "tunde@example.com",
    "Realistic": 6.5, "Investigative": 9.0, "Artistic": 4.0,
    "Social": 3.5, "Enterprising": 4.0, "Conventional": 5.5,
    "CGPA": 3.8,
    "Programming": 4.8, "Mathematics": 4.2, "ProblemSolving": 4.7,
    "Communication": 2.5, "Leadership": 2.5, "Creativity": 3.0,
    "Technical": 4.5, "DataAnalysis": 4.0, "PublicSpeaking": 2.0,
    "Research": 3.5
}
r = requests.post(BASE_URL + '/predict', json=tech_student)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# ------------------------------------------------------------------
# Test 3: Same user, a second submission (to build history)
# ------------------------------------------------------------------
print("=" * 55)
print("TEST 3: Same user, second submission")
print("=" * 55)
tech_student2 = dict(tech_student)
tech_student2["Artistic"] = 7.0  # slightly different profile
tech_student2["Creativity"] = 4.5
r = requests.post(BASE_URL + '/predict', json=tech_student2)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# ------------------------------------------------------------------
# Test 4: Get this user's history (should show 2 records)
# ------------------------------------------------------------------
print("=" * 55)
print("TEST 4: Get history for tunde@example.com")
print("=" * 55)
r = requests.get(BASE_URL + '/history/tunde@example.com')
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# ------------------------------------------------------------------
# Test 5: Overall stats
# ------------------------------------------------------------------
print("=" * 55)
print("TEST 5: System stats")
print("=" * 55)
r = requests.get(BASE_URL + '/stats')
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))