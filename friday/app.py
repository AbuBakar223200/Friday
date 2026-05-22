import winsound

from friday.audio.stt import listen
from friday.audio.tts import speak, speak_async, stop_speaking
from friday.core.brain import ai_ready
from friday.core.command_router import process_command
from friday import settings, state


def main() -> None:
    if not ai_ready():
        print("\n[!] Exiting because no AI provider is configured.")
        print("[!] Add GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY, or OLLAMA_MODEL.")
        return

    speak("Friday is online. How can I help you today, Sir?")
    state.is_awake = True
    awake_timeout_count = 0

    while True:
        if state.is_awake:
            user_text = listen()
            if not user_text:
                awake_timeout_count += 1
                if awake_timeout_count >= 2:
                    print("[friday] Friday is going to sleep...")
                    state.is_awake = False
                continue

            awake_timeout_count = 0
            stop_speaking()

            if user_text.strip() in ["friday", "hey friday"]:
                winsound.Beep(800, 200)
                continue

            response = process_command(user_text)

            if response is None:
                speak("Friday offline. Shutting down, Sir.")
                break

            if response:
                speak_async(response)
        else:
            print("[friday] Sleeping. Say 'Friday' to wake up.")
            user_text = listen(timeout=None, phrase_time_limit=settings.WAKE_PHRASE_TIME_LIMIT)

            if user_text:
                winsound.Beep(800, 200)
                print("[friday] Waking up!")
                state.is_awake = True
                awake_timeout_count = 0

                response = process_command(user_text)
                if response is None:
                    speak("Friday offline. Shutting down, Sir.")
                    break
                if response:
                    speak_async(response)
