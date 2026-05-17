import speech_recognition as sr
from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT

def listen(timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT) -> str | None:
    """
    Listen to the microphone and convert speech to text using
    Google's free speech recognition API.
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            import config
            if config.is_awake:
                print("\n[MIC] Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            if config.is_awake:
                print("[MIC] Listening...")

            # Capture audio from the microphone
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        print("[MIC] Recognizing speech...")
        text = recognizer.recognize_google(audio)
        print(f"[YOU] {text}")
        return text.lower()

    except sr.WaitTimeoutError:
        print("[MIC] No speech detected within the timeout period.")
        return None
    except sr.UnknownValueError:
        print("[MIC] Sorry, I couldn't understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"[MIC] Speech recognition service error: {e}")
        return None
    except OSError as e:
        print(f"[MIC] Microphone error -- is a microphone connected? ({e})")
        return None
    except Exception as e:
        print(f"[MIC] Unexpected error during listening: {e}")
        return None
