import speech_recognition as sr

from friday import settings, state


def _configure_recognizer(recognizer: sr.Recognizer) -> None:
    recognizer.pause_threshold = settings.PAUSE_THRESHOLD
    recognizer.phrase_threshold = settings.PHRASE_THRESHOLD
    recognizer.dynamic_energy_threshold = settings.DYNAMIC_ENERGY_THRESHOLD
    if settings.ENERGY_THRESHOLD is not None:
        recognizer.energy_threshold = settings.ENERGY_THRESHOLD
    recognizer.non_speaking_duration = min(
        settings.NON_SPEAKING_DURATION,
        max(0.1, settings.PAUSE_THRESHOLD - 0.1),
    )

def listen(timeout=settings.LISTEN_TIMEOUT, phrase_time_limit=settings.PHRASE_TIME_LIMIT) -> str | None:
    """
    Listen to the microphone and convert speech to text using
    Google's free speech recognition API.
    """
    recognizer = sr.Recognizer()
    _configure_recognizer(recognizer)

    try:
        with sr.Microphone(device_index=settings.MICROPHONE_DEVICE_INDEX) as source:
            if state.is_awake:
                print("\n[MIC] Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=settings.AMBIENT_NOISE_DURATION)
            
            if state.is_awake:
                print("[MIC] Listening...")

            # Capture audio from the microphone
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        print("[MIC] Recognizing speech...")
        text = recognizer.recognize_google(audio, language=settings.STT_LANGUAGE)
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
