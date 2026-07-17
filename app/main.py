"""
Drowsy Driver Detector — main loop.

Run:
    python3 -m app.main                     # uses CAMERA_SOURCE from config/.env
    python3 -m app.main --camera webcam     # force laptop/USB webcam
    python3 -m app.main --camera picamera   # force Raspberry Pi Camera

Press "q" in the video window to quit.
"""

import argparse
import logging
import os
import sys
import time

import cv2
import dlib
import imutils
from imutils import face_utils

from app.alerts import AlertManager
from app.camera import start_camera
from app.config import settings
from app.detector import final_ear, lip_distance

log = logging.getLogger("drowsy.main")

DISCLAIMER = """
================================================================================
 DROWSY DRIVER DETECTOR — safety & privacy notice
--------------------------------------------------------------------------------
 This is a driver-assistance aid, not a certified safety device. It does not
 replace attentive, rested driving and must not be relied on as the sole
 safeguard against drowsy driving.

 Video is processed entirely in real time and is never saved, stored, or
 transmitted anywhere by this software.
================================================================================
"""


def _load_predictor():
    if not os.path.exists(settings.SHAPE_PREDICTOR_PATH):
        log.error(
            "Facial landmark model not found at '%s'.\n"
            "Run scripts/download_models.sh first (see README).",
            settings.SHAPE_PREDICTOR_PATH,
        )
        sys.exit(1)
    return dlib.shape_predictor(settings.SHAPE_PREDICTOR_PATH)


def _load_face_detector():
    cascade_path = settings.HAAR_CASCADE_PATH or (
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        log.error("Could not load Haar cascade from '%s'.", cascade_path)
        sys.exit(1)
    return detector


def parse_args():
    parser = argparse.ArgumentParser(description="Drowsy Driver Detector")
    parser.add_argument(
        "--camera",
        choices=["picamera", "webcam"],
        default=None,
        help="Override CAMERA_SOURCE from config/.env",
    )
    parser.add_argument(
        "--webcam-index", type=int, default=None, help="Override WEBCAM_INDEX"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Run headless (no on-screen video window) — useful for a Pi "
        "without a monitor attached, or for automated testing.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.camera:
        settings.CAMERA_SOURCE = args.camera
    if args.webcam_index is not None:
        settings.WEBCAM_INDEX = args.webcam_index

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    print(DISCLAIMER)
    log.info("Loading facial landmark predictor and face detector...")
    predictor = _load_predictor()
    detector = _load_face_detector()

    alerts = AlertManager()
    eye_counter = 0
    yawn_counter = 0

    log.info("Starting video stream (source=%s)...", settings.CAMERA_SOURCE)
    vs = start_camera()
    time.sleep(1.0)

    try:
        while True:
            frame = vs.read()
            if frame is None:
                log.warning("No frame received from camera — retrying...")
                time.sleep(0.1)
                continue

            frame = imutils.resize(frame, width=settings.FRAME_WIDTH)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            rects = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

            for (x, y, w, h) in rects:
                rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                ear, left_eye, right_eye = final_ear(shape)
                yawn_gap = lip_distance(shape)

                left_hull = cv2.convexHull(left_eye)
                right_hull = cv2.convexHull(right_eye)
                cv2.drawContours(frame, [left_hull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [right_hull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [shape[48:60]], -1, (0, 255, 0), 1)

                # -- Drowsiness (debounced over N consecutive frames) --
                if ear < settings.EYE_AR_THRESH:
                    eye_counter += 1
                    if eye_counter >= settings.EYE_AR_CONSEC_FRAMES:
                        alerts.set_drowsy(True)
                        cv2.putText(
                            frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                        )
                else:
                    eye_counter = 0
                    alerts.set_drowsy(False)

                # -- Yawning (debounced over N consecutive frames) --
                if yawn_gap > settings.YAWN_THRESH:
                    yawn_counter += 1
                    if yawn_counter >= settings.YAWN_CONSEC_FRAMES:
                        alerts.set_yawn(True)
                        cv2.putText(
                            frame, "YAWN ALERT!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                        )
                else:
                    yawn_counter = 0
                    alerts.set_yawn(False)

                cv2.putText(
                    frame, f"EAR: {ear:.2f}", (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                )
                cv2.putText(
                    frame, f"YAWN: {yawn_gap:.2f}", (300, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                )

            if not args.no_display:
                cv2.imshow("Drowsy Driver Detector", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        log.info("Interrupted by user.")
    finally:
        log.info("Shutting down...")
        alerts.shutdown()
        cv2.destroyAllWindows()
        vs.stop()


if __name__ == "__main__":
    main()
