import os
import cv2
import numpy as np

from utils import *

data_dir = './data'

output = []
for emotion_idx, emotion in enumerate(sorted(os.listdir(data_dir))):
    for image_path_ in os.listdir(os.path.join(data_dir, emotion)):
        image_path = os.path.join(data_dir, emotion, image_path_)

        image = cv2.imread(image_path)
        face_landmarks = get_face_landmarks(image)
        print(len(face_landmarks))

        if len(face_landmarks) == 1404:
            face_landmarks.append(int(emotion_idx))
            output.append(face_landmarks)
np.savetxt('data.txt', np.asarray(output))






