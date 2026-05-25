"""
Quick test: can we connect to MongoDB Atlas?
Reads MONGO_URI from the .env file and tries to ping the database.
Run with:  python test_db.py
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load the .env file so MONGO_URI becomes available
load_dotenv()

uri = os.getenv('MONGO_URI')

# --- Basic sanity checks on the string (no secrets printed) ---
if not uri:
    print("❌ MONGO_URI not found. Is your .env file in this folder?")
    print("   The file must be named exactly '.env' and contain a line:")
    print("   MONGO_URI=mongodb+srv://...")
    exit()

print("Checking connection string structure...")
problems = []
if '@' not in uri:
    problems.append("Missing '@' — your username:password part is incomplete.")
if '://' in uri and ':' not in uri.split('@')[0].split('://')[1]:
    problems.append("Missing ':' between username and password.")
if '<' in uri or '>' in uri:
    problems.append("Found '<' or '>' — you left the <password> placeholder in. Replace it with your real password.")
if '.mongodb.net' not in uri:
    problems.append("Missing '.mongodb.net' — cluster address looks incomplete.")

if problems:
    print("\n⚠️  Found likely problems with your connection string:")
    for p in problems:
        print(f"   - {p}")
    print("\nFix the .env file and run this again.")
    exit()

print("Structure looks OK. Attempting to connect to Atlas...")

# --- Try the actual connection ---
try:
    client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=8000)
    client.admin.command('ping')
    print("\n✅ SUCCESS! Connected to MongoDB Atlas.")
    print("   Your database is reachable and your credentials work.")

    # Show existing databases (just names, harmless)
    dbs = client.list_database_names()
    print(f"   Existing databases on this cluster: {dbs}")

except Exception as e:
    print("\n❌ Connection FAILED. The error was:")
    print(f"   {e}")
    print("\nCommon causes:")
    print("   - Wrong password in .env")
    print("   - Network Access not set to 'Allow from Anywhere' (0.0.0.0/0)")
    print("   - No internet connection")