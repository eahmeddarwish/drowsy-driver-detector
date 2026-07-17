"""
Drowsy Driver Detector — Configuration
========================================
All tunable values live here (or can be overridden via environment variables),
so the system can be calibrated per install (camera angle, lighting, driver)
without touching the detection logic.

Usage:
    from app.config import settings
    settings.EYE_AR_THRESH
"""

import os


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Settings:
    # -- Camera --------------------------------------------------------
    # "picamera"  -> Raspberry Pi Camera Module (requires picamera lib)
    # "webcam"    -> any USB/laptop webcam, selected by index (0, 1, ...)
    CAMERA_SOURCE: str = os.getenv("CAMERA_SOURCE", "picamera")
    WEBCAM_INDEX: int = _env_int("WEBCAM_INDEX", 0)
    FRAME_WIDTH: int = _env_int("FRAME_WIDTH", 450)

    # -- Detection thresholds --------------------------------------------
    # Eye Aspect Ratio below this value = eyes considered closed.
    EYE_AR_THRESH: float = _env_float("EYE_AR_THRESH", 0.25)
    # Eyes must stay below EYE_AR_THRESH for this many *consecutive* frames
    # before an alarm fires. This is the single biggest false-positive guard:
    # without it, one blink or one bad detection frame triggers a full alarm.
    EYE_AR_CONSEC_FRAMES: int = _env_int("EYE_AR_CONSEC_FRAMES", 15)

    # Mouth-opening distance (pixels, on a 450px-wide frame) above this = yawn.
    YAWN_THRESH: float = _env_float("YAWN_THRESH", 20.0)
    YAWN_CONSEC_FRAMES: int = _env_int("YAWN_CONSEC_FRAMES", 10)

    # -- Alerts ------------------------------------------------------------
    # Physical GPIO pins (BOARD numbering) — only used when running on a Pi.
    GPIO_VIBRATION_PIN: int = _env_int("GPIO_VIBRATION_PIN", 8)
    GPIO_BUZZER_PIN: int = _env_int("GPIO_BUZZER_PIN", 10)

    # Minimum seconds between repeated spoken alerts, so the alarm thread
    # doesn't hammer the TTS engine / CPU in a tight loop while eyes stay shut.
    ALERT_COOLDOWN_SECONDS: float = _env_float("ALERT_COOLDOWN_SECONDS", 3.0)

    DROWSY_MESSAGE: str = os.getenv("DROWSY_MESSAGE", "Wake up")
    YAWN_MESSAGE: str = os.getenv("YAWN_MESSAGE", "You need fresh air")

    # -- Models --------------------------------------------------------
    # 68-point facial landmark predictor (dlib). Not bundled — see
    # scripts/download_models.sh. ~99 MB, too large for git.
    SHAPE_PREDICTOR_PATH: str = os.getenv(
        "SHAPE_PREDICTOR_PATH", "models/shape_predictor_68_face_landmarks.dat"
    )
    # Face detector cascade: uses OpenCV's bundled Haar cascade by default
    # (cv2.data.haarcascades) so nothing extra needs to be downloaded.
    # Set HAAR_CASCADE_PATH to override with a custom cascade file.
    HAAR_CASCADE_PATH: str = os.getenv("HAAR_CASCADE_PATH", "")

    # -- Logging -------------------------------------------------------
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
