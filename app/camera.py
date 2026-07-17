"""
Camera abstraction: Raspberry Pi Camera Module or any USB/laptop webcam,
selected by app.config.settings.CAMERA_SOURCE. This is what makes the
detector runnable on a dev laptop for testing/demoing, not just on a Pi
with a PiCamera attached.
"""

import logging

from imutils.video import VideoStream

from app.config import settings

log = logging.getLogger("drowsy.camera")


def start_camera() -> VideoStream:
    source = settings.CAMERA_SOURCE.lower().strip()

    if source == "picamera":
        log.info("Starting Raspberry Pi Camera Module...")
        try:
            return VideoStream(usePiCamera=True).start()
        except Exception as exc:
            raise RuntimeError(
                "Could not start the Pi Camera. If you're running on a "
                "laptop for development, set CAMERA_SOURCE=webcam instead."
            ) from exc

    if source == "webcam":
        log.info("Starting webcam #%s...", settings.WEBCAM_INDEX)
        return VideoStream(src=settings.WEBCAM_INDEX).start()

    raise ValueError(
        f"Unknown CAMERA_SOURCE '{settings.CAMERA_SOURCE}'. "
        "Expected 'picamera' or 'webcam'."
    )
