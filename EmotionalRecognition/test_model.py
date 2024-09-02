import cv2
import pickle
from utils import *

emotions = ["HAPPY", "NEUTRAL", "SAD", "SURPRISED"]

with open('./model', 'rb') as f:
    model = pickle.load(f)


cap = cv2.VideoCapture(0)

while True:
    try:
        ret, frame = cap.read()

        face_landmarks = get_face_landmarks(frame, draw=True, static_image_mode=False)

        output = model.predict([face_landmarks])
        print(output)
        if output:
            cv2.putText(frame,
                        emotions[int(output[0])],
                        (10, frame.shape[0] - 1),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        3,
                        (0, 255, 0),
                        5)

        # cv2.waitKey(25)
        # if not ret or not frame or not emotions or not face_landmarks or not get_face_landmarks():

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except ValueError:
        pass

cap.release()
cv2.destroyAllWindows()