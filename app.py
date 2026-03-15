import cv2
import mediapipe as mp
import pyttsx3
import time
import tkinter as tk
from PIL import Image, ImageTk
import threading
import winsound   # 🔔 beep sound

# ========== TEXT TO SPEECH ==========
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# 🔒 speech lock
is_speaking = False

def speak_three_times(text):
    global is_speaking
    if is_speaking:
        return

    def run():
        global is_speaking
        is_speaking = True
        print("🚨 ALERT:", text)

        for _ in range(3):
            engine.say(text)
            engine.runAndWait()
            time.sleep(0.4)

        is_speaking = False

    threading.Thread(target=run, daemon=True).start()

# 🔔 BEEP SOUND FUNCTION (3 TIMES ONLY)
def beep_three_times():
    for _ in range(3):
        winsound.Beep(1000, 300)
        time.sleep(0.2)

# ========== MEDIAPIPE SETUP ==========
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ========== GESTURE MESSAGES ==========
messages = {
    "EMERGENCY": "Emergency! Patient needs immediate help",
    "NEED HELP": "Patient needs assistance",
    "PAIN": "Patient is in pain",
    "WASHROOM": "Patient wants to go to washroom",
    "WATER": "Patient wants water",
    "FOOD": "Patient wants food"
}

# ========== CAMERA ==========
cap = cv2.VideoCapture(0)

# ⭐ KEY VARIABLE (edge detection)
last_gesture = "None"

# ========== TKINTER UI ==========
root = tk.Tk()
root.title("Patient Hand Gesture Alert System")
root.geometry("900x600")
root.configure(bg="#f2f2f2")

title = tk.Label(
    root,
    text="Patient Hand Gesture Alert System",
    font=("Arial", 22, "bold"),
    bg="#f2f2f2"
)
title.pack(pady=10)

video_label = tk.Label(root)
video_label.pack()

gesture_label = tk.Label(
    root,
    text="Gesture: None",
    font=("Arial", 16),
    fg="blue",
    bg="#f2f2f2"
)
gesture_label.pack(pady=5)

message_label = tk.Label(
    root,
    text="Patient Message",
    font=("Arial", 18, "bold"),
    fg="red",
    bg="#f2f2f2"
)
message_label.pack(pady=10)

# ========== MAIN LOOP ==========
def update_frame():
    global last_gesture

    ret, frame = cap.read()
    if not ret:
        root.after(10, update_frame)
        return

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = "None"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # 👍 WATER
            if (lm[4].x > lm[3].x and
                lm[8].y > lm[6].y and
                lm[12].y > lm[10].y and
                lm[16].y > lm[14].y and
                lm[20].y > lm[18].y):
                gesture = "FOOD"

            # 🤙 WASHROOM
            elif (lm[20].y < lm[18].y and
                  lm[8].y > lm[6].y and
                  lm[12].y > lm[10].y and
                  lm[16].y > lm[14].y):
                gesture = "WASHROOM"

            # ✊ FOOD
            elif (lm[8].y > lm[6].y and
                  lm[12].y > lm[10].y and
                  lm[16].y > lm[14].y and
                  lm[20].y > lm[18].y):
                gesture = "WATER"

            # ✋ EMERGENCY
            elif (lm[8].y < lm[6].y and
                  lm[12].y < lm[10].y and
                  lm[16].y < lm[14].y and
                  lm[20].y < lm[18].y):
                gesture = "EMERGENCY"

            # ☝ NEED HELP
            elif lm[8].y < lm[6].y:
                gesture = "NEED HELP"

            # ✌ PAIN
            elif (lm[8].y > lm[6].y and
                  lm[12].y > lm[10].y):
                gesture = "PAIN"

            # 🔔 EDGE TRIGGER: play once when gesture appears
            if gesture != last_gesture:
                if gesture != "None":
                    gesture_label.config(text=f"Gesture: {gesture}")
                    message_label.config(text=messages[gesture])

                    beep_three_times()                 # 🔔 exactly 3 times
                    speak_three_times(messages[gesture])

                last_gesture = gesture

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img = img.resize((700, 400))
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    root.after(10, update_frame)

# ========== START ==========
update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
