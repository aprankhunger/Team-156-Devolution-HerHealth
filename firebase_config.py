import pyrebase
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
# Your Firebase Configuration
config = {
    "apiKey": "AIzaSyACluAtFJ-yKIPAtWx6s8YolK1PwxSspo0",
    "authDomain": "herhealth-devolution.firebaseapp.com",
    "projectId": "herhealth-devolution",
    "storageBucket": "herhealth-devolution.firebasestorage.app",
    "messagingSenderId": "470220147677",
    "appId": "1:470220147677:web:1496980865268fbd07c434",
    "databaseURL": "sqlite:///health_profiles.db"
}
# Initialize Pyrebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Initialize Firebase Admin