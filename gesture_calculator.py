import cv2
import mediapipe as mp
import time

# Mediapipe initialization
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Landmarks
finger_tips = [8, 12, 16, 20]
thumb_tip = 4

# Calculator variables
operand1 = None
operand2 = None
operator = None
stage = "operand1"
last_change_time = time.time()
result = None

def count_fingers(lm_list):
    count = 0
    if lm_list[thumb_tip][0] > lm_list[thumb_tip - 1][0]:  # Thumb
        count += 1
    for tip in finger_tips:
        if lm_list[tip][1] < lm_list[tip - 2][1]:  # Other fingers
            count += 1
    return count

def detect_operator(lm_list):
    fingers_up = [False] * 5

    # Thumb (x-axis check)
    fingers_up[0] = lm_list[thumb_tip][0] > lm_list[thumb_tip - 1][0]

    # Other fingers (y-axis check)
    for i, tip in enumerate(finger_tips):
        fingers_up[i+1] = lm_list[tip][1] < lm_list[tip - 2][1]

    # Operator conditions
    if fingers_up == [True, False, False, False, False]:
        return "+"
    elif fingers_up[1] and fingers_up[2] and not fingers_up[0] and not fingers_up[3] and not fingers_up[4]:
        return "-"
    elif fingers_up[0] and fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
        return "*"
    elif fingers_up == [False, True, False, False, False]:
        return "/"


    elif all(f == False for f in fingers_up):
        return "EVAL"
    elif all(f == True for f in fingers_up):
        return "CLEAR"
    else:
        return None


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    h, w, _ = img.shape

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Switch logic every 2 seconds
            if time.time() - last_change_time > 3:
                last_change_time = time.time()

                if stage == "operand1":
                    operand1 = count_fingers(lm_list)
                    stage = "operator"

                elif stage == "operator":
                    op = detect_operator(lm_list)
                    if op in ["+", "-", "*", "/"]:
                        operator = op
                        stage = "operand2"

                elif stage == "operand2":
                    operand2 = count_fingers(lm_list)
                    stage = "eval"

                elif stage == "eval":
                     if operand1 is not None and operand2 is not None and operator is not None:
                        if operator == "+":
                            result = operand1 + operand2
                        elif operator == "-":
                            result = operand1 - operand2
                        elif operator == "*":
                            result = operand1 * operand2
                        elif operator == "/":
                            if operand2 != 0:
                                result = operand1 / operand2
                            else:
                                result = "∞"
                        else:
                            result = None
                        print(f"Result: {operand1} {operator} {operand2} = {result}")
                        stage = "done"


                elif stage == "done":
                    op = detect_operator(lm_list)
                    if op == "CLEAR":
                        operand1 = operand2 = operator = result = None
                        stage = "operand1"
                        print("Calculator reset successfully.")

    # Display text
    cv2.putText(img, f"Stage: {stage}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 255), 2)
    if operand1 is not None:
        cv2.putText(img, f"Operand1: {operand1}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if operator is not None:
        cv2.putText(img, f"Operator: {operator}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if operand2 is not None:
        cv2.putText(img, f"Operand2: {operand2}", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if result is not None:
        cv2.putText(img, f"Result: {result}", (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("Gesture Calculator", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import pyttsx3

# After result is calculated
engine = pyttsx3.init()
engine.say(f"The result is {result}")
engine.runAndWait()

