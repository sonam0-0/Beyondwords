# from flask import Flask, render_template, request, jsonify, send_from_directory
# import cv2
# import numpy as np
# from cvzone.HandTrackingModule import HandDetector
# from keras.models import load_model
# import pyttsx3
# from spellchecker import SpellChecker 
# import os
# import traceback
# import math
# from string import ascii_uppercase

# app = Flask(__name__, static_folder='static')

# # Initialize components
# spell = SpellChecker()
# # Replace the current hd and hd2 initialization with:
# hd = HandDetector(maxHands=1, detectionCon=0.8, staticMode=False)
# hd2 = HandDetector(maxHands=1, detectionCon=0.8, staticMode=False)
# model = load_model('cnn8grps_rad1_model.h5')
# speak_engine = pyttsx3.init()
# speak_engine.setProperty("rate", 100)
# voices = speak_engine.getProperty("voices")
# speak_engine.setProperty("voice", voices[0].id)

# # Global variables
# offset = 29
# sentence = ""
# current_symbol = ""
# suggestions = ["", "", "", ""]

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/sign-recognition')
# def sign_recognition():
#     return render_template('sign_recognition.html')

# def distance(x, y):
#     return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

# @app.route('/process_frame', methods=['POST'])
# def process_frame():
#     global sentence, current_symbol, suggestions
    
#     try:
#         # Get frame data from the request
#         frame_data = request.files['frame'].read()
#         frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
#         frame = cv2.flip(frame, 1)
        
#         hands = hd.findHands(frame, draw=False, flipType=True)
#         frame_copy = np.array(frame)
        
#         # Create a white background for the processed image
#         white = np.ones((400, 400, 3), dtype=np.uint8) * 255
        
#         if hands and len(hands) > 0:
#             hand = hands[0]
#             if 'bbox' in hand:
#                 x, y, w, h = hand['bbox']
#                 image = frame_copy[y - offset:y + h + offset, x - offset:x + w + offset]

#                 handz = hd2.findHands(image, draw=False, flipType=True)
#                 if handz and len(handz) > 0:
#                     hand = handz[0]
#                     pts = hand['lmList']
                    
#                     os_val = ((400 - w) // 2) - 15
#                     os1_val = ((400 - h) // 2) - 15
                    
#                     # Draw hand landmarks on white image
#                     for t in range(0, 4, 1):
#                         cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
#                                  (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
#                                  (0, 255, 0), 3)
#                     for t in range(5, 8, 1):
#                         cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
#                                  (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
#                                  (0, 255, 0), 3)
#                     for t in range(9, 12, 1):
#                         cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
#                                  (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
#                                  (0, 255, 0), 3)
#                     for t in range(13, 16, 1):
#                         cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
#                                  (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
#                                  (0, 255, 0), 3)
#                     for t in range(17, 20, 1):
#                         cv2.line(white, (pts[t][0] + os_val, pts[t][1] + os1_val), 
#                                  (pts[t + 1][0] + os_val, pts[t + 1][1] + os1_val),
#                                  (0, 255, 0), 3)
                    
#                     cv2.line(white, (pts[5][0] + os_val, pts[5][1] + os1_val), 
#                              (pts[9][0] + os_val, pts[9][1] + os1_val), (0, 255, 0), 3)
#                     cv2.line(white, (pts[9][0] + os_val, pts[9][1] + os1_val), 
#                              (pts[13][0] + os_val, pts[13][1] + os1_val), (0, 255, 0), 3)
#                     cv2.line(white, (pts[13][0] + os_val, pts[13][1] + os1_val), 
#                              (pts[17][0] + os_val, pts[17][1] + os1_val), (0, 255, 0), 3)
#                     cv2.line(white, (pts[0][0] + os_val, pts[0][1] + os1_val), 
#                              (pts[5][0] + os_val, pts[5][1] + os1_val), (0, 255, 0), 3)
#                     cv2.line(white, (pts[0][0] + os_val, pts[0][1] + os1_val), 
#                              (pts[17][0] + os_val, pts[17][1] + os1_val), (0, 255, 0), 3)

#                     for i in range(21):
#                         cv2.circle(white, (pts[i][0] + os_val, pts[i][1] + os1_val), 2, (0, 0, 255), 1)
                    
#                     # Process the image and get predictions
#                     processed_img = white.reshape(1, 400, 400, 3)
#                     prob = np.array(model.predict(processed_img)[0], dtype='float32')
#                     ch1 = np.argmax(prob, axis=0)
#                     prob[ch1] = 0
#                     ch2 = np.argmax(prob, axis=0)
#                     prob[ch2] = 0
#                     ch3 = np.argmax(prob, axis=0)
#                     prob[ch3] = 0

#                     pl = [ch1, ch2]

#                     # Prediction logic
#                     # condition for [Aemnst]
#                     l = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5],
#                          [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6],
#                          [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
#                     if pl in l:
#                         if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
#                             ch1 = 0

#                     # condition for [o][s]
#                     l = [[2, 2], [2, 1]]
#                     if pl in l:
#                         if (pts[5][0] < pts[4][0]):
#                             ch1 = 0

#                     # condition for [c0][aemnst]
#                     l = [[0, 0], [0, 6], [0, 2], [0, 5], [0, 1], [0, 7], [5, 2], [7, 6], [7, 1]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[0][0] > pts[8][0] and pts[0][0] > pts[4][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and pts[5][0] > pts[4][0]:
#                             ch1 = 2

#                     # condition for [c0][aemnst]
#                     l = [[6, 0], [6, 6], [6, 2]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if distance(pts[8], pts[16]) < 52:
#                             ch1 = 2

#                     # condition for [gh][bdfikruvw]
#                     l = [[1, 4], [1, 5], [1, 6], [1, 3], [1, 0]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[6][1] > pts[8][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1] and pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
#                             ch1 = 3

#                     # con for [gh][l]
#                     l = [[4, 6], [4, 1], [4, 5], [4, 3], [4, 7]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[4][0] > pts[0][0]:
#                             ch1 = 3

#                     # con for [gh][pqz]
#                     l = [[5, 3], [5, 0], [5, 7], [5, 4], [5, 2], [5, 1], [5, 5]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[2][1] + 15 < pts[16][1]:
#                             ch1 = 3

#                     # con for [l][x]
#                     l = [[6, 4], [6, 1], [6, 2]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if distance(pts[4], pts[11]) > 55:
#                             ch1 = 4

#                     # con for [l][d]
#                     l = [[1, 4], [1, 6], [1, 1]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (distance(pts[4], pts[11]) > 50) and (
#                                 pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
#                             ch1 = 4

#                     # con for [l][gh]
#                     l = [[3, 6], [3, 4]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[4][0] < pts[0][0]):
#                             ch1 = 4

#                     # con for [l][c0]
#                     l = [[2, 2], [2, 5], [2, 4]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[1][0] < pts[12][0]):
#                             ch1 = 4

#                     # con for [gh][z]
#                     l = [[3, 6], [3, 5], [3, 4]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] > pts[10][1]:
#                             ch1 = 5

#                     # con for [gh][pq]
#                     l = [[3, 2], [3, 1], [3, 6]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[4][1] + 17 > pts[8][1] and pts[4][1] + 17 > pts[12][1] and pts[4][1] + 17 > pts[16][1] and pts[4][1] + 17 > pts[20][1]:
#                             ch1 = 5

#                     # con for [l][pqz]
#                     l = [[4, 4], [4, 5], [4, 2], [7, 5], [7, 6], [7, 0]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[4][0] > pts[0][0]:
#                             ch1 = 5

#                     # con for [pqz][aemnst]
#                     l = [[0, 2], [0, 6], [0, 1], [0, 5], [0, 0], [0, 7], [0, 4], [0, 3], [2, 7]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
#                             ch1 = 5

#                     # con for [pqz][yj]
#                     l = [[5, 7], [5, 2], [5, 6]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[3][0] < pts[0][0]:
#                             ch1 = 7

#                     # con for [l][yj]
#                     l = [[4, 6], [4, 2], [4, 4], [4, 1], [4, 5], [4, 7]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[6][1] < pts[8][1]:
#                             ch1 = 7

#                     # con for [x][yj]
#                     l = [[6, 7], [0, 7], [0, 1], [0, 0], [6, 4], [6, 6], [6, 5], [6, 1]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[18][1] > pts[20][1]:
#                             ch1 = 7

#                     # condition for [x][aemnst]
#                     l = [[0, 4], [0, 2], [0, 3], [0, 1], [0, 6]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[5][0] > pts[16][0]:
#                             ch1 = 6

#                     # condition for [yj][x]
#                     l = [[7, 2]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[18][1] < pts[20][1] and pts[8][1] < pts[10][1]:
#                             ch1 = 6

#                     # condition for [c0][x]
#                     l = [[2, 1], [2, 2], [2, 6], [2, 7], [2, 0]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if distance(pts[8], pts[16]) > 50:
#                             ch1 = 6

#                     # con for [l][x]
#                     l = [[4, 6], [4, 2], [4, 1], [4, 4]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if distance(pts[4], pts[11]) < 60:
#                             ch1 = 6

#                     # con for [x][d]
#                     l = [[1, 4], [1, 6], [1, 0], [1, 2]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[5][0] - pts[4][0] - 15 > 0:
#                             ch1 = 6

#                     # con for [b][pqz]
#                     l = [[5, 0], [5, 1], [5, 4], [5, 5], [5, 6], [6, 1], [7, 6], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [5, 0],
#                          [6, 3], [6, 4], [7, 5], [7, 2]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
#                             ch1 = 1

#                     # con for [f][pqz]
#                     l = [[6, 1], [6, 0], [0, 3], [6, 4], [2, 2], [0, 6], [6, 2], [7, 6], [4, 6], [4, 1], [4, 2], [0, 2], [7, 1],
#                          [7, 4], [6, 6], [7, 2], [7, 5], [7, 2]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
#                             ch1 = 1

#                     l = [[6, 1], [6, 0], [4, 2], [4, 1], [4, 6], [4, 4]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
#                             ch1 = 1

#                     # con for [d][pqz]
#                     fg = 19
#                     l = [[5, 0], [3, 4], [3, 0], [3, 1], [3, 5], [5, 5], [5, 4], [5, 1], [7, 6]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[4][1] > pts[14][1]):
#                             ch1 = 1

#                     l = [[4, 1], [4, 2], [4, 4]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (distance(pts[4], pts[11]) < 50) and (
#                                 pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
#                             ch1 = 1

#                     l = [[3, 4], [3, 0], [3, 1], [3, 5], [3, 6]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[14][1] < pts[4][1]):
#                             ch1 = 1

#                     l = [[6, 6], [6, 4], [6, 1], [6, 2]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[5][0] - pts[4][0] - 15 < 0:
#                             ch1 = 1

#                     # con for [i][pqz]
#                     l = [[5, 4], [5, 5], [5, 1], [0, 3], [0, 7], [5, 0], [0, 2], [6, 2], [7, 5], [7, 1], [7, 6], [7, 7]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if ((pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
#                             ch1 = 1

#                     # con for [yj][bfdi]
#                     l = [[1, 5], [1, 7], [1, 1], [1, 6], [1, 3], [1, 0]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if (pts[4][0] < pts[5][0] + 15) and (
#                         (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
#                             ch1 = 7

#                     # con for [uvr]
#                     l = [[5, 5], [5, 0], [5, 4], [5, 1], [4, 6], [4, 1], [7, 6], [3, 0], [3, 5]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if ((pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1])) and pts[4][1] > pts[14][1]:
#                             ch1 = 1

#                     # con for [w]
#                     fg = 13
#                     l = [[3, 5], [3, 0], [3, 6], [5, 1], [4, 1], [2, 0], [5, 0], [5, 5]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if not (pts[0][0] + fg < pts[8][0] and pts[0][0] + fg < pts[12][0] and pts[0][0] + fg < pts[16][0] and
#                                 pts[0][0] + fg < pts[20][0]) and not (
#                                 pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and distance(pts[4], pts[11]) < 50:
#                             ch1 = 1

#                     # con for [w]
#                     l = [[5, 0], [5, 5], [0, 1]]
#                     pl = [ch1, ch2]
#                     if pl in l:
#                         if pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1]:
#                             ch1 = 1

#                     # -------------------------condn for 8 groups ends

#                     # -------------------------condn for subgroups starts
#                     if ch1 == 0:
#                         ch1 = 'S'
#                         if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
#                             ch1 = 'A'
#                         if pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
#                             ch1 = 'T'
#                         if pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
#                             ch1 = 'E'
#                         if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
#                             ch1 = 'M'
#                         if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
#                             ch1 = 'N'

#                     if ch1 == 2:
#                         if distance(pts[12], pts[4]) > 42:
#                             ch1 = 'C'
#                         else:
#                             ch1 = 'O'

#                     if ch1 == 3:
#                         if (distance(pts[8], pts[12])) > 72:
#                             ch1 = 'G'
#                         else:
#                             ch1 = 'H'

#                     if ch1 == 7:
#                         if distance(pts[8], pts[4]) > 42:
#                             ch1 = 'Y'
#                         else:
#                             ch1 = 'J'

#                     if ch1 == 4:
#                         ch1 = 'L'

#                     if ch1 == 6:
#                         ch1 = 'X'

#                     if ch1 == 5:
#                         if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
#                             if pts[8][1] < pts[5][1]:
#                                 ch1 = 'Z'
#                             else:
#                                 ch1 = 'Q'
#                         else:
#                             ch1 = 'P'

#                     if ch1 == 1:
#                         if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
#                             ch1 = 'B'
#                         if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
#                             ch1 = 'D'
#                         if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
#                             ch1 = 'F'
#                         if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
#                             ch1 = 'I'
#                         if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]):
#                             ch1 = 'W'
#                         if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] < pts[9][1]:
#                             ch1 = 'K'
#                         if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) < 8) and (
#                                 pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
#                             ch1 = 'U'
#                         if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) >= 8) and (
#                                 pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[4][1] > pts[9][1]):
#                             ch1 = 'V'
#                         if (pts[8][0] > pts[12][0]) and (
#                                 pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
#                             ch1 = 'R'

#                     if ch1 == 1 or ch1 =='E' or ch1 =='S' or ch1 =='X' or ch1 =='Y' or ch1 =='B':
#                         if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
#                             ch1=" "

#                     if pts[4][0] < pts[5][0]:
#                         if ch1 == 'E' or ch1=='Y' or ch1=='B':
#                             if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
#                                 ch1="next"

#                     if ch1 == 'Next' or 'B' or 'C' or 'H' or 'F' or 'X':
#                         if (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and (pts[4][1] < pts[8][1] and pts[4][1] < pts[12][1] and pts[4][1] < pts[16][1] and pts[4][1] < pts[20][1]) and (pts[4][1] < pts[6][1] and pts[4][1] < pts[10][1] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]):
#                             ch1 = 'Backspace'

#                     current_symbol = ch1
                    
#                     # Update sentence based on current symbol
#                     if current_symbol == "Backspace":
#                         sentence = sentence[:-1]
#                     elif current_symbol == " ":
#                         sentence += " "
#                     elif current_symbol not in ["next", "Backspace"]:
#                         sentence += current_symbol
                    
#                     # Get word suggestions
#                     if len(sentence.strip()) != 0:
#                         st = sentence.rfind(" ")
#                         ed = len(sentence)
#                         word = sentence[st+1:ed]
#                         if len(word.strip()) != 0:
#                             candidates = spell.candidates(word)
#                             if candidates:
#                                 suggestions = list(candidates)[:4]  # Get up to 4 suggestions
#                                 while len(suggestions) < 4:
#                                     suggestions.append("")
        
#         # Convert white image to JPEG for sending to frontend
#         _, img_encoded = cv2.imencode('.jpg', white)
#         img_bytes = img_encoded.tobytes()
        
#         return jsonify({
#             'status': 'success',
#             'processed_image': img_bytes.decode('latin1'),
#             'current_symbol': current_symbol,
#             'sentence': sentence,
#             'suggestions': suggestions
#         })
    
#     except Exception as e:
#         print("Error:", traceback.format_exc())
#         return jsonify({'status': 'error', 'message': str(e)})

# @app.route('/speak', methods=['POST'])
# def speak():
#     text = request.json.get('text', '')
#     speak_engine.say(text)
#     speak_engine.runAndWait()
#     return jsonify({'status': 'success'})

# @app.route('/clear', methods=['POST'])
# def clear():
#     global sentence
#     sentence = ""
#     return jsonify({'status': 'success'})

# @app.route('/static/<path:path>')
# def send_static(path):
#     return send_from_directory('static', path)

# if __name__ == '__main__':
#     app.run(debug=True)