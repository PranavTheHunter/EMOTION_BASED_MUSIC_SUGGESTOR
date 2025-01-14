import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2 
import numpy as np 
import mediapipe as mp 
from keras.models import load_model
import webbrowser
import pyautogui
import os

# Load the model and labels
model = load_model("model.h5")
label = np.load("labels.npy")

# Initialize MediaPipe
holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

st.header("Emotion Based Music Recommender")


try:
    emotion = np.load("emotion.npy")[0]
except:
    emotion = ""


class EmotionProcessor:
    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")


    # Read a frame from the video capture
        frm = cv2.flip(frm, 1)

        # Process the frame with MediaPipe
        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
        lst =[]
        if res.face_landmarks:
            # Collect face landmarks
            for i in res.face_landmarks.landmark:
                lst.append(i.x - res.face_landmarks.landmark[1].x)
                lst.append(i.y - res.face_landmarks.landmark[1].y)

            # Collect left hand landmarks
            if res.left_hand_landmarks:
                for i in res.left_hand_landmarks.landmark:
                    lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)

            # Collect right hand landmarks
            if res.right_hand_landmarks:
                for i in res.right_hand_landmarks.landmark:
                    lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)

            # Prepare data for prediction
            lst = np.array(lst).reshape(1, -1)
            pred = label[np.argmax(model.predict(lst))]

            # Print "Volume Up" if the prediction is "volume up"
            if pred == "volume up":
                pyautogui.press('volumeup')
            if pred =="volume down":
                pyautogui.press('volumedown')

            # Display the prediction on the frame
            cv2.putText(frm, pred, (50, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
            np.save("emotion.npy", np.array([pred]))

        # Draw landmarks on the frame
        drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_CONTOURS)
        drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
        drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

        
        return av.VideoFrame.from_ndarray(frm, format="bgr24")

lang = st.text_input("Language")
singer = st.text_input("singer")
site = st.selectbox(label="Choose your site", options=['Select a site', 'YT_music', 'Spotify', 'Youtube'])

if site == 'Select a site':
    st.warning("Please select a site.")
else:
    st.success(f"You have selected {site}.")

if lang and singer and '''st.session_state["run"] != "false"''':
    webrtc_streamer(key="key", video_processor_factory=EmotionProcessor )

btn = st.button("Recommend me songs")


if btn:
    if not emotion:
        st.warning("Please let me capture your emotion first")
        #st.session_state["run"] = "true"
    
    else:
        if emotion=="no movement":
            st.text(emotion)
            st.error("INVALID GUESTURE")
            try:
                os.remove('F:\\PROJECTS\\emotion-based-music\trainning\\ volume\\emotion.npy')
            except:
                print("no File")
   
        else:
            if site == 'Youtube':
                webbrowser.open(f"https://www.youtube.com/results?search_query={lang}+{emotion}+song+playlist+{singer}")
            elif site == 'Spotify':
                webbrowser.open(f"https://open.spotify.com/search/{lang}%20{emotion}%20song%20playlist%20of%20{singer}")
            elif site == 'YT_music':
                webbrowser.open(f"https://music.youtube.com/search?q={lang}+{emotion}+song+playlist+of+{singer}")
            else:
                st.warning("No Site selected")

            

            np.save("emotion.npy", np.array([""]))
            #st.session_state["run"] = "false"
