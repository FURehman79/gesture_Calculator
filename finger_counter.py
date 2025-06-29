import cv2
import mediapipe as mp

print("Starting camera...")  # Debugging line

# Initialize mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Finger tips landmark IDs
finger_tips = [8, 12, 16, 20]
thumb_tip = 4

# Start webcam
cap = cv2.VideoCapture(0)  # If not working, try 1 instead of 0

if not cap.isOpened():
    print("❌ ERROR: Cannot access the webcam.")
    exit()

print("✅ Webcam accessed successfully.")

while True:
    success, img = cap.read()
    if not success:
        print("❌ Failed to grab frame")
        break

    img = cv2.flip(img, 1)  # Mirror image
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    count = 0

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            # Finger detection logic
            if lm_list:
                # Thumb
                if lm_list[thumb_tip][0] > lm_list[thumb_tip - 1][0]:
                    count += 1
                # Other 4 fingers
                for tip in finger_tips:
                    if lm_list[tip][1] < lm_list[tip - 2][1]:
                        count += 1

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    # Show finger count on screen
    cv2.rectangle(img, (20, 250), (170, 350), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, f'Fingers: {count}', (30, 320), cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (255, 255, 255), 2)

    cv2.imshow("Finger Counter", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destro
