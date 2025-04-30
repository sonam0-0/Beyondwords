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


print(secrets.token_hex(16))


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


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Replace with your actual secret key
 
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
# Initialize Firebase Admin
def initialize_firebase():
    try:
        if not firebase_admin._apps:  # ✅ Add this line
            cred_path = os.path.join(os.path.dirname(__file__), 'firebase', 'serviceAccountKey.json')  # ✅ FIXED: no double slashes
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
# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

# @app.route('/login', methods=['POST'])
# def login():
#     """API endpoint for Firebase login"""
#     token = request.json.get('token')
    
#     try:
#         # # Verify the Firebase token
#         # decoded_token = firebase_admin.auth.verify_id_token(token)
#         # user = User(decoded_token['uid'])
#         # print(f"Successfully authenticated user: {user}")  # Debug log
#         # login_user(user)
#         # return jsonify({'success': True})

#         decoded_token = firebase_admin.auth.verify_id_token(token)
#         user = decoded_token['uid']
#         print(f"Successfully authenticated user: {user}")  # Debug log
        
#         # Here you would typically create/update user in your database
#         # and set up Flask-Login session
        
#         return jsonify({
#             'success': True,
#             'user': {
#                 'uid': user,
#                 'email': decoded_token.get('email')
#             }
#         })
#     except ValueError as e:
#         print(f"Invalid token: {e}")  # Debug log
#         return jsonify({'success': False, 'error': 'Invalid token'}), 401
#     except firebase_admin.exceptions.FirebaseError as e:
#         print(f"Firebase error: {e}")  # Debug log
#         return jsonify({'success': False, 'error': str(e)}), 401

# @app.route('/login', methods=['POST'])
# def login():
#     """API endpoint for Firebase login"""
#     token = request.json.get('token')
    
#     try:
#         decoded_token = firebase_admin.auth.verify_id_token(token)
#         user_id = decoded_token['uid']
        
#         # Create Flask-Login user and log them in
#         user = User(user_id)
#         login_user(user)
        
#         print(f"Successfully authenticated user: {user_id}")
        
#         return jsonify({
#             'success': True,
#             'redirect': url_for('feature'),  # This is the critical fix
#             'user': {
#                 'uid': user_id,
#                 'email': decoded_token.get('email')
#             }
#         })
#     except ValueError as e:
#         print(f"Invalid token: {e}")
#         return jsonify({'success': False, 'error': 'Invalid token'}), 401
#     except firebase_admin.exceptions.FirebaseError as e:
#         print(f"Firebase error: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 401


@app.route('/login', methods=['POST'])
def login():
    token = request.json.get('token')
    try:
        decoded_token = firebase_admin.auth.verify_id_token(token)
        user_id = decoded_token['uid']
        
        user = User(user_id)
        login_user(user)
        session['user'] = user_id  # Store user ID in session
        
        print(f"Successfully authenticated user: {user_id}")
        
        return jsonify({
            'success': True,
            'redirect': url_for('feature'),
            'user': {
                'uid': user_id,
                'email': decoded_token.get('email')
            }
        })
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 401


# FIREBASE_API_KEY = 'AIzaSyCqRzCp699fXrKP9Kk6bud_k7hvTYHEGXw'

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     id_token = data.get('token')

#     if not id_token:
#         return jsonify({'success': False, 'error': 'Missing ID token'}), 400

#     # Verify token with Firebase REST API
#     response = requests.post(
#         f'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}',
#         json={'idToken': id_token}
#     )

#     if response.status_code != 200:
#         return jsonify({'success': False, 'error': 'Invalid ID token'}), 401

#     user_info = response.json()
#     email = user_info['users'][0]['email']
#     session['user'] = email  # Optional: Set user session

#     return jsonify({
#         'success': True,
#         'redirect': '/feature'  # <--- IMPORTANT
#     })



# @app.route('/feature')
# @login_required
# def feature():
#     return render_template('feature.html')
# @app.route('/feature')
# @login_required
# def feature():
#     if not current_user.is_authenticated:
#         return redirect(url_for('auth'))
#     return render_template('feature.html')
@app.route('/feature')
@login_required
def feature():
    print(f"Accessing /feature — Authenticated: {current_user.is_authenticated}, User ID: {current_user.get_id()}")
    print("Session contents:", dict(session))  # Debug print
    return render_template('feature.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
# @app.route('/check-auth')
# def check_auth():
#     user = session.get('user')
#     if user:
#         return jsonify({'authenticated': True, 'user': user})
#     return jsonify({'authenticated': False})
@app.route('/check-auth')
def check_auth():
    print("Session check:", dict(session))  # Debug print
    if current_user.is_authenticated:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

@app.route('/sign-recognition')
@login_required
def sign_recognition():
    return render_template('sign_recognition.html')

def distance(x, y):
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global sentence, current_symbol, suggestions, last_prediction_time, prediction_history
    stable_prediction = None
    try:
        # Get frame data from the request
        frame_data = request.files['frame'].read()
        if not frame_data:
            return jsonify({'status': 'error', 'message': 'Empty frame data'})

        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({'status': 'error', 'message': 'Invalid image data'})
            
        frame = cv2.flip(frame, 1)
        hands, frame = hd.findHands(frame, draw=False, flipType=True)
        frame_copy = np.array(frame)
        
        # Create a white background for the processed image
        white = np.ones((400, 400, 3), dtype=np.uint8) * 255
        # last_prediction_time = 0  # Initialize it to a default value, like 0 or the current time
        # PREDICTION_COOLDOWN = 1  # Set the cooldown period, e.g., 1 second


        current_time = time.time()
        if current_time - last_prediction_time < PREDICTION_COOLDOWN:
            return jsonify({
                'status': 'cooldown',
                'current_symbol': current_symbol,
                'sentence': sentence,
                'suggestions': suggestions
            })

        if hands and len(hands) > 0:
            hand = hands[0]
            if 'bbox' in hand:
                x, y, w, h = hand['bbox']
                
                # Ensure the crop coordinates are within frame boundaries
                y_start = max(0, y - offset)
                y_end = min(frame.shape[0], y + h + offset)
                x_start = max(0, x - offset)
                x_end = min(frame.shape[1], x + w + offset)
                
                image = frame_copy[y_start:y_end, x_start:x_end]
                
                if image.size == 0:
                    return jsonify({'status': 'error', 'message': 'Invalid hand region'})
                
                handz, _ = hd2.findHands(image, draw=False, flipType=True)
                
                if handz and len(handz) > 0:
                    hand = handz[0]
                    pts = hand['lmList']
                    
                    if len(pts) < 21:
                        return jsonify({'status': 'error', 'message': 'Not enough hand landmarks detected'})
                    
                    os_val = max(0, ((400 - w) // 2) - 15)
                    os1_val = max(0, ((400 - h) // 2) - 15)
                    
                    # Draw hand landmarks on white image
                    for t in range(0, 4, 1):
                        cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
                                 (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
                                 (0, 255, 0), 3)
                    for t in range(5, 8, 1):
                        cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
                                 (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
                                 (0, 255, 0), 3)
                    for t in range(9, 12, 1):
                        cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
                                 (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
                                 (0, 255, 0), 3)
                    for t in range(13, 16, 1):
                        cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
                                 (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
                                 (0, 255, 0), 3)
                    for t in range(17, 20, 1):
                        cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
                                 (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
                                 (0, 255, 0), 3)
                    
                    cv2.line(white, (pts[5][0] + os_val, pts[5][1] + os1_val), 
                             (pts[9][0] + os_val, pts[9][1] + os1_val), (0, 255, 0), 3)
                    cv2.line(white, (pts[9][0] + os_val, pts[9][1] + os1_val), 
                             (pts[13][0] + os_val, pts[13][1] + os1_val), (0, 255, 0), 3)
                    cv2.line(white, (pts[13][0] + os_val, pts[13][1] + os1_val), 
                             (pts[17][0] + os_val, pts[17][1] + os1_val), (0, 255, 0), 3)
                    cv2.line(white, (pts[0][0] + os_val, pts[0][1] + os1_val), 
                             (pts[5][0] + os_val, pts[5][1] + os1_val), (0, 255, 0), 3)
                    cv2.line(white, (pts[0][0] + os_val, pts[0][1] + os1_val), 
                             (pts[17][0] + os_val, pts[17][1] + os1_val), (0, 255, 0), 3)

                    for i in range(21):
                        cv2.circle(white, (pts[i][0] + os_val, pts[i][1] + os1_val), 2, (0, 0, 255), 1)
                    
                    # Process the image and get predictions
                    processed_img = white.reshape(1, 400, 400, 3)
                    prob = np.array(model.predict(processed_img)[0], dtype='float32')
                    ch1 = np.argmax(prob, axis=0)
                    prob[ch1] = 0
                    ch2 = np.argmax(prob, axis=0)
                    prob[ch2] = 0
                    ch3 = np.argmax(prob, axis=0)
                    prob[ch3] = 0

                    pl = [ch1, ch2]

                    # [All your existing prediction conditions remain the same...]
                    l = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5],
                          [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6],
                          [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
                    if pl in l:
                        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            ch1 = 0

                    # condition for [o][s]
                    l = [[2, 2], [2, 1]]
                    if pl in l:
                        if (pts[5][0] < pts[4][0]):
                            ch1 = 0

                    # condition for [c0][aemnst]
                    l = [[0, 0], [0, 6], [0, 2], [0, 5], [0, 1], [0, 7], [5, 2], [7, 6], [7, 1]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[0][0] > pts[8][0] and pts[0][0] > pts[4][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and pts[5][0] > pts[4][0]:
                            ch1 = 2

                    # condition for [c0][aemnst]
                    l = [[6, 0], [6, 6], [6, 2]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if distance(pts[8], pts[16]) < 52:
                            ch1 = 2

                    # condition for [gh][bdfikruvw]
                    l = [[1, 4], [1, 5], [1, 6], [1, 3], [1, 0]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[6][1] > pts[8][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1] and pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
                            ch1 = 3

                    # con for [gh][l]
                    l = [[4, 6], [4, 1], [4, 5], [4, 3], [4, 7]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[4][0] > pts[0][0]:
                            ch1 = 3

                    # con for [gh][pqz]
                    l = [[5, 3], [5, 0], [5, 7], [5, 4], [5, 2], [5, 1], [5, 5]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[2][1] + 15 < pts[16][1]:
                            ch1 = 3

                    # con for [l][x]
                    l = [[6, 4], [6, 1], [6, 2]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if distance(pts[4], pts[11]) > 55:
                            ch1 = 4

                    # con for [l][d]
                    l = [[1, 4], [1, 6], [1, 1]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (distance(pts[4], pts[11]) > 50) and (
                                pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            ch1 = 4

                    # con for [l][gh]
                    l = [[3, 6], [3, 4]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[4][0] < pts[0][0]):
                            ch1 = 4

                    # con for [l][c0]
                    l = [[2, 2], [2, 5], [2, 4]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[1][0] < pts[12][0]):
                            ch1 = 4

                    # con for [gh][z]
                    l = [[3, 6], [3, 5], [3, 4]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] > pts[10][1]:
                            ch1 = 5

                    # con for [gh][pq]
                    l = [[3, 2], [3, 1], [3, 6]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[4][1] + 17 > pts[8][1] and pts[4][1] + 17 > pts[12][1] and pts[4][1] + 17 > pts[16][1] and pts[4][1] + 17 > pts[20][1]:
                            ch1 = 5

                    # con for [l][pqz]
                    l = [[4, 4], [4, 5], [4, 2], [7, 5], [7, 6], [7, 0]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[4][0] > pts[0][0]:
                            ch1 = 5

                    # con for [pqz][aemnst]
                    l = [[0, 2], [0, 6], [0, 1], [0, 5], [0, 0], [0, 7], [0, 4], [0, 3], [2, 7]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
                            ch1 = 5

                    # con for [pqz][yj]
                    l = [[5, 7], [5, 2], [5, 6]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[3][0] < pts[0][0]:
                            ch1 = 7

                    # con for [l][yj]
                    l = [[4, 6], [4, 2], [4, 4], [4, 1], [4, 5], [4, 7]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[6][1] < pts[8][1]:
                            ch1 = 7

                    # con for [x][yj]
                    l = [[6, 7], [0, 7], [0, 1], [0, 0], [6, 4], [6, 6], [6, 5], [6, 1]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[18][1] > pts[20][1]:
                            ch1 = 7

                    # condition for [x][aemnst]
                    l = [[0, 4], [0, 2], [0, 3], [0, 1], [0, 6]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[5][0] > pts[16][0]:
                            ch1 = 6

                    # condition for [yj][x]
                    l = [[7, 2]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[18][1] < pts[20][1] and pts[8][1] < pts[10][1]:
                            ch1 = 6

                    # condition for [c0][x]
                    l = [[2, 1], [2, 2], [2, 6], [2, 7], [2, 0]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if distance(pts[8], pts[16]) > 50:
                            ch1 = 6

                    # con for [l][x]
                    l = [[4, 6], [4, 2], [4, 1], [4, 4]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if distance(pts[4], pts[11]) < 60:
                            ch1 = 6

                    # con for [x][d]
                    l = [[1, 4], [1, 6], [1, 0], [1, 2]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[5][0] - pts[4][0] - 15 > 0:
                            ch1 = 6

                    # con for [b][pqz]
                    l = [[5, 0], [5, 1], [5, 4], [5, 5], [5, 6], [6, 1], [7, 6], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [5, 0],
                         [6, 3], [6, 4], [7, 5], [7, 2]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                            ch1 = 1

                    # con for [f][pqz]
                    l = [[6, 1], [6, 0], [0, 3], [6, 4], [2, 2], [0, 6], [6, 2], [7, 6], [4, 6], [4, 1], [4, 2], [0, 2], [7, 1],
                         [7, 4], [6, 6], [7, 2], [7, 5], [7, 2]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                            ch1 = 1

                    l = [[6, 1], [6, 0], [4, 2], [4, 1], [4, 6], [4, 4]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                            ch1 = 1

                    # con for [d][pqz]
                    fg = 19
                    l = [[5, 0], [3, 4], [3, 0], [3, 1], [3, 5], [5, 5], [5, 4], [5, 1], [7, 6]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[4][1] > pts[14][1]):
                            ch1 = 1

                    l = [[4, 1], [4, 2], [4, 4]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (distance(pts[4], pts[11]) < 50) and (
                                pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            ch1 = 1

                    l = [[3, 4], [3, 0], [3, 1], [3, 5], [3, 6]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[14][1] < pts[4][1]):
                            ch1 = 1

                    l = [[6, 6], [6, 4], [6, 1], [6, 2]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[5][0] - pts[4][0] - 15 < 0:
                            ch1 = 1

                    # con for [i][pqz]
                    l = [[5, 4], [5, 5], [5, 1], [0, 3], [0, 7], [5, 0], [0, 2], [6, 2], [7, 5], [7, 1], [7, 6], [7, 7]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if ((pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
                            ch1 = 1

                    # con for [yj][bfdi]
                    l = [[1, 5], [1, 7], [1, 1], [1, 6], [1, 3], [1, 0]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if (pts[4][0] < pts[5][0] + 15) and (
                        (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
                            ch1 = 7

                    # con for [uvr]
                    l = [[5, 5], [5, 0], [5, 4], [5, 1], [4, 6], [4, 1], [7, 6], [3, 0], [3, 5]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if ((pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1])) and pts[4][1] > pts[14][1]:
                            ch1 = 1

                    # con for [w]
                    fg = 13
                    l = [[3, 5], [3, 0], [3, 6], [5, 1], [4, 1], [2, 0], [5, 0], [5, 5]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if not (pts[0][0] + fg < pts[8][0] and pts[0][0] + fg < pts[12][0] and pts[0][0] + fg < pts[16][0] and
                                pts[0][0] + fg < pts[20][0]) and not (
                                pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and distance(pts[4], pts[11]) < 50:
                            ch1 = 1

                    # con for [w]
                    l = [[5, 0], [5, 5], [0, 1]]
                    pl = [ch1, ch2]
                    if pl in l:
                        if pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1]:
                            ch1 = 1

                    # -------------------------condn for 8 groups ends

                    # -------------------------condn for subgroups starts
                    if ch1 == 0:
                        ch1 = 'S'
                        if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
                            ch1 = 'A'
                        if pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
                            ch1 = 'T'
                        if pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
                            ch1 = 'E'
                        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
                            ch1 = 'M'
                        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
                            ch1 = 'N'

                    if ch1 == 2:
                        if distance(pts[12], pts[4]) > 42:
                            ch1 = 'C'
                        else:
                            ch1 = 'O'

                    if ch1 == 3:
                        if (distance(pts[8], pts[12])) > 72:
                            ch1 = 'G'
                        else:
                            ch1 = 'H'

                    if ch1 == 7:
                        if distance(pts[8], pts[4]) > 42:
                            ch1 = 'Y'
                        else:
                            ch1 = 'J'

                    if ch1 == 4:
                        ch1 = 'L'

                    if ch1 == 6:
                        ch1 = 'X'

                    if ch1 == 5:
                        if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
                            if pts[8][1] < pts[5][1]:
                                ch1 = 'Z'
                            else:
                                ch1 = 'Q'
                        else:
                            ch1 = 'P'

                    if ch1 == 1:
                        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                            ch1 = 'B'
                        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            ch1 = 'D'
                        if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                            ch1 = 'F'
                        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
                            ch1 = 'I'
                        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]):
                            ch1 = 'W'
                        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] < pts[9][1]:
                            ch1 = 'K'
                        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) < 8) and (
                                pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            ch1 = 'U'
                        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) >= 8) and (
                                pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[4][1] > pts[9][1]):
                            ch1 = 'V'
                        if (pts[8][0] > pts[12][0]) and (
                                pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            ch1 = 'R'

                    if ch1 == 1 or ch1 =='E' or ch1 =='S' or ch1 =='X' or ch1 =='Y' or ch1 =='B':
                        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
                            ch1=" "

                    if pts[4][0] < pts[5][0]:
                        if ch1 == 'E' or ch1=='Y' or ch1=='B':
                            if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                                ch1="next"

                    if ch1 == 'Next' or 'B' or 'C' or 'H' or 'F' or 'X':
                        if (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and (pts[4][1] < pts[8][1] and pts[4][1] < pts[12][1] and pts[4][1] < pts[16][1] and pts[4][1] < pts[20][1]) and (pts[4][1] < pts[6][1] and pts[4][1] < pts[10][1] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]):
                            ch1 = 'Backspace'

                    current_symbol = ch1
                    # ... (keep all your existing prediction logic)

                    # Store prediction in history
                    prediction_history.append(ch1)
                    if len(prediction_history) > HISTORY_SIZE:
                        prediction_history.pop(0)
                    
                    # Only update if we have consistent predictions
                    # In your process_frame function, replace the prediction stabilization section with this:


                    if len(prediction_history) == HISTORY_SIZE:
                    # Get the most common prediction
                        stable_prediction = mode(prediction_history)
                    
                    # Convert numerical prediction to letter/symbol
                    if stable_prediction == 0:
                        current_symbol = 'S'
                        if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
                            current_symbol = 'A'
                        if pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
                            current_symbol = 'T'
                        if pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
                            current_symbol = 'E'
                        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
                            current_symbol = 'M'
                        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
                            current_symbol = 'N'

                    elif stable_prediction == 2:
                        if distance(pts[12], pts[4]) > 42:
                            current_symbol = 'C'
                        else:
                            current_symbol = 'O'

                    elif stable_prediction == 3:
                        if (distance(pts[8], pts[12])) > 72:
                            current_symbol = 'G'
                        else:
                            current_symbol = 'H'

                    elif stable_prediction == 7:
                        if distance(pts[8], pts[4]) > 42:
                            current_symbol = 'Y'
                        else:
                            current_symbol = 'J'

                    elif stable_prediction == 4:
                        current_symbol = 'L'

                    elif stable_prediction == 6:
                        current_symbol = 'X'

                    elif stable_prediction == 5:
                        if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
                            if pts[8][1] < pts[5][1]:
                                current_symbol = 'Z'
                            else:
                                current_symbol = 'Q'
                        else:
                            current_symbol = 'P'

                    elif stable_prediction == 1:
                        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                            current_symbol = 'B'
                        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            current_symbol = 'D'
                        if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                            current_symbol = 'F'
                        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
                            current_symbol = 'I'
                        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]):
                            current_symbol = 'W'
                        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] < pts[9][1]:
                            current_symbol = 'K'
                        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) < 8) and (
                            pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            current_symbol = 'U'
                        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) >= 8) and (
                            pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[4][1] > pts[9][1]):
                            current_symbol = 'V'
                        if (pts[8][0] > pts[12][0]) and (
                            pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
                            current_symbol = 'R'

                    # Special cases for space and backspace
                    if stable_prediction == 1 or stable_prediction == 0 or stable_prediction == 6 or stable_prediction == 7:
                        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
                            current_symbol = " "

                    if pts[4][0] < pts[5][0]:
                        if current_symbol == 'E' or current_symbol == 'Y' or current_symbol == 'B':
                            if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
                                current_symbol = "next"

                    if current_symbol == 'Next' or 'B' or 'C' or 'H' or 'F' or 'X':
                        if (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and (pts[4][1] < pts[8][1] and pts[4][1] < pts[12][1] and pts[4][1] < pts[16][1] and pts[4][1] < pts[20][1]) and (pts[4][1] < pts[6][1] and pts[4][1] < pts[10][1] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]):
                            current_symbol = 'Backspace'

                    # Update sentence based on current symbol
                    if current_symbol == "Backspace":
                        sentence = sentence[:-1]
                        last_prediction_time = time.time()
                    elif current_symbol == " ":
                        sentence += " "
                        last_prediction_time = time.time()
                    elif current_symbol not in ["next", "Backspace"]:
                        sentence += str(current_symbol)
                        last_prediction_time = time.time()

                    # Clear prediction history after successful prediction
                    prediction_history = []
                    
                    # Get word suggestions
                    if len(sentence.strip()) != 0:
                        st = sentence.rfind(" ")
                        ed = len(sentence)
                        word = sentence[st+1:ed]
                        if len(word.strip()) != 0:
                            candidates = spell.candidates(word)
                            if candidates:
                                suggestions = list(candidates)[:4]  # Get up to 4 suggestions
                                while len(suggestions) < 4:
                                    suggestions.append("")
        
        # Convert white image to JPEG for sending to frontend
        _, img_encoded = cv2.imencode('.jpg', white)
        img_bytes = img_encoded.tobytes()
        
        return jsonify({
            'status': 'success',
            'processed_image': img_bytes.decode('latin1'),
            'current_symbol': str(current_symbol),
            'sentence': sentence,
            'suggestions': suggestions
        })
    
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    try:
        speak_engine.say(text)
        speak_engine.runAndWait()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/clear', methods=['POST'])
def clear():
    global sentence, prediction_history
    sentence = ""
    prediction_history = []
    return jsonify({'status': 'success'})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
