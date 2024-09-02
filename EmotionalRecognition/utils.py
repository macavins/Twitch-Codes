import cv2
import mediapipe as mp


def get_face_landmarks(image, draw=False, static_image_mode=True):
    try:

        # Read the input image
        image_input_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=static_image_mode,
                                                    max_num_faces=10,
                                                    min_detection_confidence=0.5)
        image_rows, image_cols, _ = image.shape
        results = face_mesh.process(image_input_rgb)

        image_landmarks = []

        if results.multi_face_landmarks or results.multi_face_landmarks == 0:

            if draw or not draw:

                mp_drawing = mp.solutions.drawing_utils
                mp_drawing_styles = mp.solutions.drawing_styles
                drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=results.multi_face_landmarks[0],
                    connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)


            ls_single_face = results.multi_face_landmarks[0].landmark
            xs_ = []
            ys_ = []
            zs_ = []
            for idx in ls_single_face:
                xs_.append(idx.x)
                ys_.append(idx.y)
                zs_.append(idx.z)
                if not ls_single_face:
                    xs_.append(idx.x)
                    ys_.append(idx.y)
                    zs_.append(idx.z)
            for j in range(len(xs_)):
                image_landmarks.append(xs_[j] - min(xs_))
                image_landmarks.append(ys_[j] - min(ys_))
                image_landmarks.append(zs_[j] - min(zs_))
    except ValueError:
        pass

    return image_landmarks