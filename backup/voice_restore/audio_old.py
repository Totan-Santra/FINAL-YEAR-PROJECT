import io
import os
import platform
import shutil
import subprocess
import time
import wave
from collections import deque
from pathlib import Path

import numpy as np
import openwakeword
import sounddevice as sd
from groq import Groq
from openwakeword.model import Model

from settings import WAKE_MODEL, WAKE_THRESHOLD

RATE = 16000
BLOCK = 1280

# Speech capture tuning. Adjust these if Marvin misses quiet speech or reacts
# to background noise. Values are int16 microphone RMS levels.
VOICE_RMS_THRESHOLD = int(os.getenv("MARVIN_VOICE_RMS", "420"))
BARGE_IN_RMS_THRESHOLD = int(os.getenv("MARVIN_BARGE_IN_RMS", "850"))
SILENCE_SECONDS = float(os.getenv("MARVIN_SILENCE_SECONDS", "0.75"))
START_TIMEOUT = float(os.getenv("MARVIN_START_TIMEOUT", "8"))
MAX_UTTERANCE_SECONDS = float(os.getenv("MARVIN_MAX_UTTERANCE", "15"))
BARGE_IN_ENABLED = os.getenv("MARVIN_BARGE_IN", "1").lower() not in {"0", "false", "no"}

_stt = None
_oww = None


def _client():
    global _stt
    if _stt is None:
        _stt = Groq()
    return _stt


def _wake_model():
    global _oww
    if _oww is None:
        path = Path(openwakeword.__file__).parent / "resources" / "models" / WAKE_MODEL
        _oww = Model(wakeword_model_paths=[str(path)])
    return _oww


def _rms(frame) -> float:
    """Return the audio frame RMS as a float."""
    samples = np.asarray(frame, dtype=np.float32)
    if samples.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples))))


def _wav_bytes(frames) -> bytes:
    """Convert captured mono int16 frames into an in-memory WAV file."""
    if not frames:
        return b""
    audio = np.concatenate([np.asarray(frame, dtype=np.int16).reshape(-1) for frame in frames])
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(audio.tobytes())
    return buf.getvalue()


def transcribe_frames(frames) -> str:
    """Transcribe captured audio frames with Groq Whisper."""
    payload = _wav_bytes(frames)
    if not payload:
        return ""
    result = _client().audio.transcriptions.create(
        file=("marvin_input.wav", payload),
        model="whisper-large-v3-turbo",
        language="en",
    )
    return result.text.strip()


def _tts_process(text: str):
    """Build the platform TTS process without blocking the caller."""
    system = platform.system()
    if system == "Darwin":
        command = ["say", text]
        env = None
    elif system == "Windows":
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Speak($env:MARVIN_TEXT)"
        )
        command = ["powershell", "-NoProfile", "-Command", script]
        env = {**os.environ, "MARVIN_TEXT": text}
    else:
        engine = shutil.which("espeak-ng") or shutil.which("espeak")
        if not engine:
            print("TTS unavailable: install espeak-ng or configure a platform voice.")
            return None
        command = [engine, text]
        env = None
    return subprocess.Popen(
        command,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _capture_barge_in(stream, first_frames, threshold: float):
    """Finish capturing the user's interruption after TTS has been stopped."""
    frames = list(first_frames)
    quiet_for = 0.0
    started_at = time.monotonic()
    end_threshold = max(250.0, threshold * 0.65)

    while time.monotonic() - started_at < MAX_UTTERANCE_SECONDS:
        frame, _ = stream.read(BLOCK)
        frame = frame.copy()
        frames.append(frame)
        if _rms(frame) < end_threshold:
            quiet_for += BLOCK / RATE
            if quiet_for >= SILENCE_SECONDS:
                break
        else:
            quiet_for = 0.0
    return frames


def speak(text: str):
    """Speak text; return transcribed user speech if the user interrupts.

    Normal calls return None. Existing callers can continue using speak(text)
    without handling a return value. Main voice mode uses the returned text to
    process a barge-in immediately instead of losing the interrupted request.
    """
    text = str(text).strip()
    if not text:
        return None

    if not BARGE_IN_ENABLED:
        process = _tts_process(text)
        if process is not None:
            process.wait()