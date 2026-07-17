"""
Alert output: GPIO (vibration motor + buzzer) and spoken TTS warnings.

Fixes vs. the original prototype:
  - `t.deamon = True` (a no-op typo — Thread has no such attribute, so the
    thread never actually ran as daemon) -> `t.daemon = True`.
  - The alarm loop used to call `os.system("espeak ...")` on every spin of a
    tight `while` loop with no delay, which pegs the CPU and floods audio.
    It now speaks once per event, then sleeps for ALERT_COOLDOWN_SECONDS.
  - GPIO and espeak are both optional at runtime: on a machine that isn't a
    Raspberry Pi (a laptop used for development, demoing, or a
    software-only/commercial deployment), both fall back to safe no-op
    stand-ins that log instead of failing, so the detection logic can run
    and be demonstrated anywhere.
"""

import logging
import os
import platform
import shutil
import subprocess
import threading
import time

from app.config import settings

log = logging.getLogger("drowsy.alerts")

_IS_RASPBERRY_PI = platform.machine().lower().startswith(("arm", "aarch64"))


class _MockGPIO:
    """Stand-in for RPi.GPIO when running off-Pi (dev laptop / CI / demo)."""

    BOARD = HIGH = OUT = 1
    LOW = 0

    def setwarnings(self, *_a, **_kw):
        pass

    def setmode(self, *_a, **_kw):
        pass

    def setup(self, *_a, **_kw):
        pass

    def output(self, pin, value):
        log.debug("MockGPIO: pin %s -> %s", pin, "HIGH" if value else "LOW")


try:
    if _IS_RASPBERRY_PI:
        import RPi.GPIO as GPIO  # type: ignore
    else:
        raise ImportError("Not running on a Raspberry Pi")
except ImportError:
    GPIO = _MockGPIO()
    log.warning(
        "RPi.GPIO not available — running in DESKTOP MODE. "
        "Vibration motor / buzzer output will be logged, not driven."
    )

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(settings.GPIO_VIBRATION_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(settings.GPIO_BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)

_ESPEAK_AVAILABLE = shutil.which("espeak") is not None


def _speak(message: str) -> None:
    """Speak a message via espeak if available; otherwise log it.
    Runs as a subprocess list call (not os.system + string formatting),
    so a message can't break out into a shell command."""
    if not _ESPEAK_AVAILABLE:
        log.info("ALERT (no TTS engine installed): %s", message)
        return
    try:
        subprocess.run(["espeak", message], check=False, timeout=5)
    except Exception as exc:  # pragma: no cover - best-effort audio
        log.warning("TTS playback failed: %s", exc)


class AlertManager:
    """Owns alarm state + hardware output for the drowsiness and yawn alerts.
    One instance is shared by the main loop; each alert type has its own
    active flag and its own background speaking thread with a cooldown."""

    def __init__(self):
        self._lock = threading.Lock()
        self._drowsy_active = False
        self._yawn_active = False

    # -- Drowsiness alert ------------------------------------------------
    def set_drowsy(self, active: bool) -> None:
        with self._lock:
            was_active = self._drowsy_active
            self._drowsy_active = active

        GPIO.output(settings.GPIO_VIBRATION_PIN, GPIO.HIGH if active else GPIO.LOW)
        GPIO.output(settings.GPIO_BUZZER_PIN, GPIO.HIGH if active else GPIO.LOW)

        if active and not was_active:
            t = threading.Thread(
                target=self._speak_loop,
                args=(settings.DROWSY_MESSAGE, "_drowsy_active"),
                daemon=True,  # correct spelling — actually detaches on exit
            )
            t.start()

    # -- Yawn alert --------------------------------------------------------
    def set_yawn(self, active: bool) -> None:
        with self._lock:
            was_active = self._yawn_active
            self._yawn_active = active

        if active and not was_active:
            GPIO.output(settings.GPIO_VIBRATION_PIN, GPIO.HIGH)
            t = threading.Thread(
                target=self._speak_loop,
                args=(settings.YAWN_MESSAGE, "_yawn_active"),
                daemon=True,
            )
            t.start()
        elif not active:
            GPIO.output(settings.GPIO_VIBRATION_PIN, GPIO.LOW)

    def _speak_loop(self, message: str, flag_name: str) -> None:
        """Repeats the spoken alert every ALERT_COOLDOWN_SECONDS while the
        corresponding flag stays active — instead of the original's tight
        spin loop with no delay."""
        while getattr(self, flag_name):
            _speak(message)
            time.sleep(settings.ALERT_COOLDOWN_SECONDS)

    def shutdown(self) -> None:
        self._drowsy_active = False
        self._yawn_active = False
        GPIO.output(settings.GPIO_VIBRATION_PIN, GPIO.LOW)
        GPIO.output(settings.GPIO_BUZZER_PIN, GPIO.LOW)
        if _IS_RASPBERRY_PI and hasattr(GPIO, "cleanup"):
            GPIO.cleanup()
