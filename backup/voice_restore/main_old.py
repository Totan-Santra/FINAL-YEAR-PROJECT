import sys

sys.stdout.reconfigure(encoding="utf-8")

from core.agent import ask
from settings import ASSISTANT_NAME
from voice.audio import (
    listen,
    speak,
    voice_confirm,
    wait_for_wake
)

THREAD = "Marvin"
EXIT_WORDS = ("goodbye", "stop listening", "exit", "quit")
FOLLOWUP_TIMEOUT = 8
FOLLOWUP_MAX_SECONDS = 15


def safe_ask(text, confirm=None):
    try:
        if confirm:
            return ask(text, thread_id=THREAD, confirm=confirm)
        return ask(text, thread_id=THREAD)
    except Exception as e:
        print("Error:", e)
        return "Sorry, something went wrong. Please try again."


def _is_exit(text: str) -> bool:
    cleaned = text.lower().strip().strip(".!?, ")
    return cleaned in EXIT_WORDS


def voice_loop():
    print(
        f"{ASSISTANT_NAME} is ready. Say 'hey marvin'. "
        "After a reply, just keep talking for follow-ups. "
        "Say 'goodbye' or press Ctrl+C to quit."
    )

    while True:
        wait_for_wake()
        interrupted = speak("Yes?")
        text = interrupted or listen(max_seconds=15, start_timeout=8)

        while text:
            print("You:", text)
            if _is_exit(text):
                speak("Goodbye.")
                return

            reply = safe_ask(text, confirm=voice_confirm)
            print(f"{ASSISTANT_NAME}:", reply)

            # If the user speaks over Marvin, speak() stops TTS and returns
            # the interrupted utterance as text. Process it as the next turn.
            interrupted = speak(reply)
            if interrupted:
                text = interrupted
                continue

            # Follow mode: no wake word is needed for the next turn.
            # If nobody speaks before the timeout, return to wake-word mode.
            print(f"[Marvin] Listening for a follow-up ({FOLLOWUP_TIMEOUT}s)...")
            text = listen(
                start_timeout=FOLLOWUP_TIMEOUT,
                max_seconds=FOLLOWUP_MAX_SECONDS,
            )

        print("[Marvin] Follow-up window closed.")


def text_loop():
    print(f"{ASSISTANT_NAME} text mode. Type 'exit' to quit.")
    while True:
        text = input("You: ").strip()
        if _is_exit(text):
            break
        if text:
            print(f"{ASSISTANT_NAME}:", safe_ask(text))


def main():
    try:
        text_loop() if "--text" in sys.argv else voice_loop()
    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
