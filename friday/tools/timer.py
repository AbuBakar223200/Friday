import threading
import time

def start_timer(minutes: int) -> str:
    """Start a background timer for the given number of minutes."""
    if minutes <= 0:
        return "Timer duration must be greater than zero."
        
    def timer_callback():
        # Wait the required time
        time.sleep(minutes * 60)
        # Import dynamically to avoid circular imports during startup
        from friday.audio.tts import speak_async
        speak_async(f"Sir, your {minutes} minute timer is up.")

    t = threading.Thread(target=timer_callback, daemon=True)
    t.start()
    
    return f"Timer set for {minutes} minutes."
