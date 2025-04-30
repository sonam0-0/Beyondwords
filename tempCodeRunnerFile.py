from statistics import mode
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import firebase_admin
from firebase_admin import credentials, auth
import cv2
from functools import wraps
import numpy as np
import time
from cvzone.HandTrackingModule import HandDetector
from keras.models import load_model
import pyttsx3
from spellchecker import SpellChecker 
import os
import traceback
from functools import wraps
import jwt
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime, timedelta
import math
from string import ascii_uppercase
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from flask import Flask, request, jsonify, session
import firebase_admin
from firebase_admin import auth
import requests
import secrets
from flask_session import Session

# Configure session to use filesystem (instead of signed cookies)




# Initialize Flask Application
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this for production
# Initialize components
spell = SpellChecker()
hd = HandDetector(maxHands=1, detectionCon=0.8)
hd2 = HandDetector(maxHands=1, detectionCon=0.8, staticMode=False)
model = load_model('cnn8grps_rad1_model.h5')
speak_engine = pyttsx3.init()
speak_engine.setProperty("rate", 100)
voices = speak_engine.getProperty("voices")
speak_engine.setProperty("voice", voices[0].id)

# Global variables
offset = 29
sentence = ""
current_symbol = ""
suggestions = ["", "", "", ""]
prediction_history = []
HISTORY_SIZE = 5
last_prediction_time = 0
PREDICTION_COOLDOWN = 0.9

# Cleanup function for TTS engine
# def cleanup():
#     speak_engine.stop()

# atexit.register(cleanup)
# Initialize Firebase Admin
def initialize_firebase():
    try:
        # Path to your Firebase service account key
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase', 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase Admin: {e}")

initialize_firebase()

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    token = request.json.get('token')
    
    try:
        decoded_token = firebase_admin.auth.verify_id_token(token)
        user_id = decoded_token['uid']
        user = User(user_id)  # Create a Flask-Login user
        login_user(user)      # Log in the user with Flask-Login
        print(f"Successfully authenticated and logged in user: {user_id}")

        return jsonify({
            'success': True,
            'user': {
                'uid': user_id,
                'email': decoded_token.get('email')
            }
        })
    except ValueError as e:
        print(f"Invalid token: {e}")
        return jsonify({'success': False, 'error': 'Invalid token'}), 401
    except firebase_admin.exceptions.FirebaseError as e:
        print(f"Firebase error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 401


@app.route('/feature')
@login_required
def feature():
    return render_template('feature.html')

@app.route('/check-auth')
def check_auth():
    return jsonify({
        "authenticated": current_user.is_authenticated
    })

@app.route('/sign-recognition')
@login_required
def sign_recognition():
    return render_template('sign_recognition.html')
