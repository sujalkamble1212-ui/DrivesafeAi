"""
DriveSafe AI — Alert Manager
==============================
Orchestrates all detection modules, manages alert state,
triggers voice alerts via pyttsx3 (offline TTS), and
saves alert screenshots.

Voice alerts are played in a background thread to avoid
blocking the main processing loop.
"""

import os
import time
import queue
import logging
import threading
import numpy as np
import cv2
from datetime import datetime

from config import SCREENSHOTS_DIR, DetectionConfig
from storage.gridfs_storage import save_file as gridfs_save_file

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────
# Voice Alert Worker
# ─────────────────────────────────────────────────
# Uses PowerShell's System.Speech (Windows built-in) for TTS.
# PowerShell runs in a completely separate process, so it has zero
# COM-threading / pyttsx3 background-thread issues.
# Alerts are queued via a PriorityQueue — only ONE speaks at a time.

import subprocess
import sys

class VoiceAlertWorker:
    """Reliable Windows TTS using PowerShell System.Speech.
    Falls back to pyttsx3 on non-Windows platforms.
    """

    ALERT_MESSAGES = {
        "drowsiness":     "Driver appears drowsy. Please open your eyes.",
        "distraction":    "Please focus on the road.",
        "phone_detected": "Mobile phone detected. Please put it down.",
        "yawn_detected":  "Yawning detected. Please rest if you feel tired.",
        "eye_closed":     "Please open your eyes.",
    }

    # Minimum seconds between voice alerts PER alert type.
    VOICE_COOLDOWN_PER_TYPE = 8.0

    def __init__(self):
        self._enabled = True
        self._last_speak_times: dict[str, float] = {}
        self._is_windows = sys.platform.startswith("win")
        self._is_speaking = False   # True while PowerShell is actively speaking

        # Thread-safe priority queue for pending alerts
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        # Track which alert types are currently queued to avoid duplicates
        self._queued: set[str] = set()
        # Mapping of alert type to its priority (higher number = higher priority)
        self._priority_map: dict[str, int] = {
            "drowsiness": 5,
            "phone_detected": 4,
            "eye_closed": 3,
            "distraction": 2,
            "yawn_detected": 1,
        }

        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def _speak_windows(self, msg: str) -> None:
        """Speak via Windows SAPI / PowerShell System.Speech — blocking so voices never overlap."""
        try:
            import win32com.client
            import pythoncom
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(msg)
            return
        except Exception as exc:
            logger.debug(f"SAPI speak error: {exc}, falling back to PowerShell")

        safe = msg.replace("'", "''")
        ps_cmd = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Rate = 1; "
            f"$s.Speak('{safe}')"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )

    def _speak_pyttsx3(self, msg: str, engine) -> None:
        """Speak via pyttsx3 (non-Windows fallback)."""
        try:
            engine.say(msg)
            engine.runAndWait()
        except Exception as exc:
            logger.debug(f"pyttsx3 speak error: {exc}")

    def _worker_loop(self) -> None:
        fallback_engine = None
        espeak_available = False
        if not self._is_windows:
            try:
                import pyttsx3
                fallback_engine = pyttsx3.init()
                fallback_engine.setProperty("rate", 160)
                fallback_engine.setProperty("volume", 1.0)
                logger.info("pyttsx3 TTS initialised (non-Windows).")
            except Exception as exc:
                logger.warning(f"pyttsx3 unavailable: {exc}")
                # Check if espeak is available as a direct subprocess fallback
                try:
                    subprocess.run(["espeak", "--version"], capture_output=True, timeout=2)
                    espeak_available = True
                    logger.info("espeak TTS available as fallback.")
                except Exception:
                    logger.info("No TTS engine available (cloud/headless server). Voice alerts disabled.")
        else:
            logger.info("Voice alerts: PowerShell System.Speech (Windows).")


        while True:
            # Block until an alert is queued
            priority_item = self._queue.get()
            # priority_item format: ( -priority, timestamp, alert_type )
            _, _, alert_type = priority_item

            # Filter out entries that were implicitly cancelled
            if alert_type not in self._queued:
                self._queue.task_done()
                continue

            # Retrieve the message for the alert type
            msg = self.ALERT_MESSAGES.get(alert_type, alert_type)

            self._is_speaking = True
            try:
                if msg:
                    logger.info(f"Speaking: {msg}")
                    if self._is_windows:
                        self._speak_windows(msg)
                    elif fallback_engine:
                        self._speak_pyttsx3(msg, fallback_engine)
                    elif espeak_available:
                        try:
                            subprocess.run(
                                ["espeak", "-s", "160", msg],
                                timeout=15,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                        except Exception as exc:
                            logger.debug(f"espeak error: {exc}")

            finally:
                self._is_speaking = False
                # Remove from the queued set – the item has been processed
                self._queued.discard(alert_type)
                # Mark task done for the queue
                self._queue.task_done()

    def speak(self, alert_type: str) -> None:
        """Queue a voice alert for sequential speaking.
        If already speaking, the alert is queued and will play
        as soon as the current speech finishes — never dropped.
        """
        if not self._enabled:
            return
        now  = time.time()
        last = self._last_speak_times.get(alert_type, 0.0)
        if now - last < self.VOICE_COOLDOWN_PER_TYPE:
            return
        self._last_speak_times[alert_type] = now

        # 'eye_closed' is strictly a UI visual state (eyes closed < DROWSINESS_SECONDS).
        # Voice alerts are reserved solely for sustained 'drowsiness' (>= DROWSINESS_SECONDS).
        if alert_type == "eye_closed":
            logger.debug("🔔 'eye_closed' is a UI-only state; skipping voice alert generation.")
            return

        # Collapse eye_closed from queued set if drowsiness is now queued
        if alert_type == "drowsiness" and "eye_closed" in self._queued:
            logger.debug("🔔 Removing queued eye_closed because drowsiness is now queued")
            self._queued.discard("eye_closed")

        # Determine priority (default low priority if unknown)
        priority = self._priority_map.get(alert_type, 0)
        if priority <= 0:
            logger.debug(f"🔔 Unknown alert type '{alert_type}' – using default priority 0")

        # Avoid duplicate entries for the same alert type
        if alert_type in self._queued:
            logger.debug(f"🔔 Alert '{alert_type}' already queued – skipping duplicate")
            return

        # Use a timestamp to preserve FIFO order for same priority
        timestamp = time.time()
        # Negate priority because PriorityQueue returns smallest first
        self._queue.put((-priority, timestamp, alert_type))
        self._queued.add(alert_type)
        logger.debug(f"🔔 Voice alert queued: {alert_type} with priority {priority}")

    def reset(self) -> None:
        """Clear all queued voice alerts and reset last speak timestamps."""
        self._last_speak_times.clear()
        self._queued.clear()
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except Exception:
                break


# ─────────────────────────────────────────────────
# Alert Manager
# ─────────────────────────────────────────────────

class AlertManager:
    """
    Central alert manager that:
      1. Evaluates detection results from all modules
      2. Triggers voice alerts (1.0s repeating interval while unfocused)
      3. Saves screenshots asynchronously
      4. Computes real-time Safety Score and Attention Score
    """

    # Seconds between REPEAT alert fires for a continuously-active alert.
    # Long enough to avoid log/DB spam, short enough to keep reminding the driver.
    COOLDOWNS = {
        "drowsiness":     12.0,   # repeat reminder every 12s while eyes stay closed
        "eye_closed":     12.0,
        "phone_detected": 10.0,   # repeat every 10s while phone stays visible
        "distraction":    10.0,   # repeat every 10s while still looking away
        "yawn_detected":  20.0,   # yawn is brief; rarely repeats anyway
    }

    # Number of consecutive normal frames required before clearing an active alert.
    # Prevents single-frame flicker from resetting the alert and causing re-fire.
    SUSTAINED_NORMAL_FRAMES = 10  # ~0.5s at 20fps

    # Screenshot is taken ONCE per alert episode (not on every repeat)
    _SCREENSHOT_TAKEN: set  # tracks alert types for which screenshot was taken this episode

    # Score deduction per new alert episode
    SCORE_DEDUCTIONS = {
        "drowsiness":     8.0,   # high risk — sustained eye closure
        "phone_detected": 10.0,  # highest risk — active violation
        "distraction":    5.0,   # medium risk — looking away
        "yawn_detected":  3.0,   # fatigue indicator
        "eye_closed":     4.0,   # brief eye closure
    }

    # Points recovered per second of safe driving
    RECOVERY_RATE = 0.4          # 0.4 pts/sec → full recovery from 60 in ~100s of clean driving
    MIN_SCORE     = 10.0         # floor — never drops below 10

    def __init__(self):
        self._voice       = VoiceAlertWorker()
        self._last_alerts: dict[str, float] = {}
        self._active_alerts: set[str] = set()
        self._alert_repeat_times: dict[str, float] = {}
        self._clear_times: dict[str, float] = {}
        self._normal_frame_counts: dict[str, int] = {}
        self._session_start_saved: bool = False
        self._screenshot_taken: set[str] = set()

        # Session-level counters
        self._session_alerts:   list[dict] = []
        self._total_alert_count = 0

        # Dynamic score state — resets to 100 each session
        self._safety_score:    float = 100.0
        self._attention_score: float = 100.0
        self._last_score_time: float = time.time()   # for delta-time recovery

    def clear_active_alert(self, alert_type: str) -> None:
        """
        Signal that the current frame shows normal state for this alert type.
        Only actually clears the active alert after SUSTAINED_NORMAL_FRAMES
        consecutive normal frames, preventing flicker re-triggering.
        """
        if alert_type not in self._active_alerts:
            # Not active, reset counter
            self._normal_frame_counts[alert_type] = 0
            return

        # Increment consecutive normal frame counter
        count = self._normal_frame_counts.get(alert_type, 0) + 1
        self._normal_frame_counts[alert_type] = count

        if count >= self.SUSTAINED_NORMAL_FRAMES:
            # Sustained normal — actually clear the alert
            self._active_alerts.discard(alert_type)
            self._clear_times[alert_type] = time.time()
            self._normal_frame_counts[alert_type] = 0
            self._alert_repeat_times.pop(alert_type, None)
            # Allow screenshot again for next episode of this alert type
            self._screenshot_taken.discard(alert_type)
            logger.info(f"✅ Alert cleared (sustained normal): {alert_type}")

    def mark_still_active(self, alert_type: str) -> None:
        """Reset the normal-frame counter when the anomaly is still present."""
        self._normal_frame_counts[alert_type] = 0

    # ──────────────────────────────────────────────
    # Screenshot (Asynchronous non-blocking)
    # ──────────────────────────────────────────────

    def save_screenshot(self, frame: np.ndarray, alert_type: str, session_id) -> str | None:
        """
        Encode a JPEG frame and save it to MongoDB GridFS.
        Returns the GridFS file_id string (stored in Alert.screenshot_path).
        Falls back to local disk if GridFS save fails.
        """
        try:
            ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alert_{session_id}_{alert_type}_{ts}.jpg"

            # Encode to JPEG in memory
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), DetectionConfig.SCREENSHOT_QUALITY]
            success, buf = cv2.imencode(".jpg", frame, encode_param)
            if not success:
                logger.error("Failed to encode screenshot for %s", alert_type)
                return None

            img_bytes = buf.tobytes()

            # Try to save to GridFS (async so it doesn't block the frame loop)
            def _async_gridfs_save():
                try:
                    file_id = gridfs_save_file(img_bytes, filename, content_type="image/jpeg")
                    logger.debug("Screenshot saved to GridFS: %s -> %s", filename, file_id)
                except Exception as exc:
                    logger.error("GridFS screenshot save failed: %s", exc)
                    # Fallback: write to local disk
                    try:
                        filepath = os.path.join(SCREENSHOTS_DIR, filename)
                        cv2.imwrite(filepath, frame,
                                    [int(cv2.IMWRITE_JPEG_QUALITY), DetectionConfig.SCREENSHOT_QUALITY])
                    except Exception as exc2:
                        logger.error("Local screenshot fallback also failed: %s", exc2)

            threading.Thread(target=_async_gridfs_save, daemon=True).start()

            # Return a placeholder path — will be replaced with the real GridFS ID
            # by the caller if needed. For now we return a predictable identifier.
            return f"gridfs:{filename}"
        except Exception as exc:
            logger.error("Screenshot setup error: %s", exc)
            return None

    def check_session_start_screenshot(self, frame: np.ndarray, session_id: int) -> None:
        """No-op: session-start baseline screenshots are disabled.
        Screenshots are taken only when an alert is actually detected.
        """
        pass  # Intentionally disabled — only alert-triggered screenshots are saved.

    # ──────────────────────────────────────────────
    # Alert Firing (Single-shot alert when event happens)
    # ──────────────────────────────────────────────

    def _should_fire(self, alert_type: str) -> bool:
        """Returns True if this alert should fire now (respects per-type cooldown)."""
        now = time.time()

        # Brief cooldown after clearing to prevent flicker re-triggering
        last_cleared = self._clear_times.get(alert_type, 0.0)
        if now - last_cleared < 1.5:
            return False

        if alert_type in self._active_alerts:
            next_repeat = self._alert_repeat_times.get(alert_type, 0.0)
            if now < next_repeat:
                return False
            self._alert_repeat_times[alert_type] = now + self.COOLDOWNS.get(alert_type, 1.0)
            return True

        self._active_alerts.add(alert_type)
        self._alert_repeat_times[alert_type] = now + self.COOLDOWNS.get(alert_type, 1.0)
        self._last_alerts[alert_type] = now
        return True

    def fire_alert(self, alert_type: str, frame: np.ndarray,
                   session_id: int, extra: dict | None = None) -> dict | None:
        """
        Fire a new alert (if cooldown allows).
        Screenshot is taken ONLY on the first detection of each episode —
        NOT on every repeated firing — to avoid excessive disk writes.

        Returns:
            Alert metadata dict (to be persisted by the route handler), or None.
        """
        if not self._should_fire(alert_type):
            return None

        # Determine severity for this alert
        severity_map = {
            "drowsiness": "danger",
            "eye_closed": "warning",
            "distraction": "warning",
            "phone_detected": "danger",
            "yawn_detected": "info",
        }
        severity = severity_map.get(alert_type, "warning")

        # ── Screenshot only on the FIRST fire of this episode and for danger severity ──────────
        is_first_fire = alert_type not in self._screenshot_taken
        if is_first_fire and severity == "danger":
            screenshot_path = self.save_screenshot(frame, alert_type, session_id)
            self._screenshot_taken.add(alert_type)
            logger.info(f"📸 Screenshot captured for new danger alert episode: {alert_type}")
        else:
            screenshot_path = None   # repeat voice/log but skip disk write or non-danger alert
            if not is_first_fire:
                logger.debug(f"🔁 Alert repeat (no screenshot): {alert_type}")
            else:
                logger.debug(f"🔔 Screenshot not taken for non-danger alert: {alert_type}")

        severity_map = {
            "drowsiness":     "danger",
            "eye_closed":     "warning",
            "distraction":    "warning",
            "phone_detected": "danger",
            "yawn_detected":  "info",
        }

        message_map = {
            "drowsiness":     "Driver appears drowsy — eyes closed too long!",
            "eye_closed":     "Eyes have been closed.",
            "distraction":    "Driver is distracted — please focus on the road.",
            "phone_detected": "Mobile phone detected while driving!",
            "yawn_detected":  "Yawning detected — consider taking a break.",
        }

        alert_data = {
            "alert_type":      alert_type,
            "severity":        severity_map.get(alert_type, "warning"),
            "message":         message_map.get(alert_type, alert_type),
            "screenshot_path": screenshot_path,
            "timestamp":       datetime.utcnow().isoformat(),
            **(extra or {}),
        }

        self._session_alerts.append(alert_data)
        self._total_alert_count += 1

        # Deduct from dynamic scores on the FIRST fire of each episode
        if is_first_fire:
            safety_deduction    = self.SCORE_DEDUCTIONS.get(alert_type, 3.0)
            attention_deduction = safety_deduction if alert_type in ("drowsiness", "distraction", "eye_closed") else safety_deduction * 0.4

            self._safety_score    = max(self.MIN_SCORE, self._safety_score    - safety_deduction)
            self._attention_score = max(self.MIN_SCORE, self._attention_score - attention_deduction)
            logger.info(f"📉 Score deduction for {alert_type}: safety={self._safety_score:.1f}, attention={self._attention_score:.1f}")

        # Voice alert
        self._voice.speak(alert_type)

        logger.info(f"🚨 Alert fired: {alert_type}")
        return alert_data

    # ──────────────────────────────────────────────
    # Score Computation
    # ──────────────────────────────────────────────

    def compute_scores(
        self,
        eye_result:   dict,
        head_result:  dict,
        yawn_result:  dict,
        phone_result: dict,
    ) -> tuple[float, float]:
        """
        Compute Safety Score and Attention Score (0–100).

        Scores start at 100 each session and evolve dynamically:
          • Each NEW alert episode deducts points (see SCORE_DEDUCTIONS)
          • During safe periods (no active alert), scores slowly recover
            at RECOVERY_RATE pts/sec toward 100
          • Scores reset to exactly 100 at session start

        Returns:
            (safety_score, attention_score)
        """
        now = time.time()
        dt  = min(now - self._last_score_time, 2.0)   # cap dt to 2s in case of gaps
        self._last_score_time = now

        # ── Detect current danger state ─────────────────────────────────
        eye_open   = eye_result.get("eye_status") == "Open_Eyes"
        looking_fw = head_result.get("direction") in ("Looking_Forward", "Unknown", "No_Face")
        no_phone   = not phone_result.get("phone_detected", False)
        no_yawn    = not yawn_result.get("is_yawning", False)

        # ── Instantaneous danger level (0–1) based on current frame ────
        # The danger multiplier suppresses recovery while an event is active.
        safety_danger    = 0.0
        attention_danger = 0.0

        if not eye_open:
            closed_dur       = eye_result.get("closed_duration", 0.0)
            # Scale from 0 at 0s closed to 1.0 at DROWSINESS_SECONDS
            ratio             = min(1.0, closed_dur / DetectionConfig.DROWSINESS_SECONDS)
            safety_danger    += 0.40 * ratio
            attention_danger += 0.50 * ratio

        if not looking_fw:
            dist_dur          = head_result.get("distraction_duration", 0.0)
            ratio             = min(1.0, dist_dur / DetectionConfig.HEAD_DISTRACTION_SECONDS)
            safety_danger    += 0.30 * ratio
            attention_danger += 0.50 * ratio

        if not no_phone:
            safety_danger    += 0.20

        if not no_yawn:
            safety_danger    += 0.10

        # Clamp danger level to [0, 1]
        safety_danger    = min(1.0, safety_danger)
        attention_danger = min(1.0, attention_danger)

        # ── Recovery when driver is safe ────────────────────────────────
        # Recovery is suppressed proportional to active danger level
        safety_recovery    = self.RECOVERY_RATE * (1.0 - safety_danger)    * dt
        attention_recovery = self.RECOVERY_RATE * (1.0 - attention_danger) * dt

        self._safety_score    = min(100.0, self._safety_score    + safety_recovery)
        self._attention_score = min(100.0, self._attention_score + attention_recovery)

        # Score is the dynamic accumulated score (deductions applied in fire_alert)
        return round(self._safety_score, 1), round(self._attention_score, 1)

    # ──────────────────────────────────────────────
    # Session Management
    # ──────────────────────────────────────────────

    def set_voice_enabled(self, enabled: bool) -> None:
        self._voice.set_enabled(enabled)

    def reset_session(self) -> None:
        """Call at session start to clear all counters and reset scores to 100."""
        self._session_alerts.clear()
        self._total_alert_count = 0
        self._last_alerts.clear()
        self._active_alerts.clear()
        self._clear_times.clear()
        self._normal_frame_counts.clear()
        self._screenshot_taken.clear()
        self._session_start_saved = False
        # ── Reset dynamic scores to 100 for new trip ──────────────────
        self._safety_score    = 100.0
        self._attention_score = 100.0
        self._last_score_time = time.time()
        self._voice.reset()
        logger.info("✅ Session reset — scores reset to 100, all alert counters cleared.")

    def get_session_alerts(self) -> list[dict]:
        return list(self._session_alerts)

    def get_alert_count(self) -> int:
        return self._total_alert_count
