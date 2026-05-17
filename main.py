from audio.stt import listen
from audio.tts import speak, speak_async, stop_speaking
from core.command_router import process_command
from core.brain import gemini_client
import config
import winsound

def main():
    if gemini_client is None:
        print("\n[!] Exiting because Gemini API key is missing.")
        return

    speak("Friday is online. How can I help you today, Sir?")
    config.is_awake = True
    awake_timeout_count = 0

    while True:
        if config.is_awake:
            user_text = listen()
            if not user_text:
                awake_timeout_count += 1
                if awake_timeout_count >= 2:
                    print("[SYSTEM] Friday is going to sleep...")
                    config.is_awake = False
                continue
            
            awake_timeout_count = 0
            stop_speaking()

            # Check if user specifically just said "friday" or "hey friday" while already awake
            if user_text.strip() in ["friday", "hey friday"]:
                winsound.Beep(800, 200) # Short high beep
                continue

            response = process_command(user_text)

            if response is None:
                speak("Systems offline. Shutting down, Sir.")
                break

            if response:
                speak_async(response)
        else:
            # Sleeping mode: short timeout, short phrases
            print("[SYSTEM] Sleeping. Say 'Friday' to wake up.")
            user_text = listen(timeout=None, phrase_time_limit=3)
            
            if user_text:
                winsound.Beep(800, 200) # Short high beep
                print("[SYSTEM] Waking up!")
                config.is_awake = True
                awake_timeout_count = 0
                
                # Immediately process the command that woke her up
                response = process_command(user_text)
                if response is None:
                    speak("Systems offline. Shutting down, Sir.")
                    break
                if response:
                    speak_async(response)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_speaking()
        print("\n[SYSTEM] Friday systems offline.")
