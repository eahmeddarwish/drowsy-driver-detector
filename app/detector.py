"""
Detection math: Eye Aspect Ratio (EAR) for blink/drowsiness detection,
and mouth-opening distance for yawn detection, from dlib's 68-point
facial landmarks. Pure functions — no I/O, no hardware, fully unit-testable.
"""

from scipy.spatial import distance as dist
from imutils import face_utils
import numpy as np


def eye_aspect_ratio(eye: np.ndarray) -> float:
    """Ratio of vertical eye-opening distances to horizontal eye width.
    Drops sharply toward 0 as the eye closes."""
    a = dist.euclidean(eye[1], eye[5])
    b = dist.euclidean(eye[2], eye[4])
    c = dist.euclidean(eye[0], eye[3])
    return (a + b) / (2.0 * c)


def final_ear(shape: np.ndarray):
    """Average EAR across both eyes for one face's 68 landmarks.
    Returns (ear, left_eye_points, right_eye_points)."""
    (l_start, l_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (r_start, r_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    left_eye = shape[l_start:l_end]
    right_eye = shape[r_start:r_end]

    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)

    ear = (left_ear + right_ear) / 2.0
    return ear, left_eye, right_eye


def lip_distance(shape: np.ndarray) -> float:
    """Vertical gap between the mean of the top-lip and bottom-lip
    landmark points. Grows large during a yawn."""
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))

    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))

    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)

    return abs(top_mean[1] - low_mean[1])
