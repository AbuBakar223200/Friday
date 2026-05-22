import ctypes
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import config

def set_volume(level: int) -> str:
    """Set the system volume to a specific percentage (0-100)."""
    level = max(0, min(100, level))
    try:
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%."
    except Exception:
        # Fallback for Bluetooth neckbands / headsets where pycaw fails
        try:
            import pyautogui
            # Volume down 50 times guarantees 0 volume
            pyautogui.press('volumedown', presses=50)
            # Volume up increases by 2% per press
            presses = level // 2
            if presses > 0:
                pyautogui.press('volumeup', presses=presses)
            return f"Volume set to {level}%."
        except Exception as e:
            return f"Sorry, I couldn't adjust the volume: {e}"

def set_brightness(level: int, display_type: str = None) -> str:
    """Set the system screen brightness to a specific percentage (0-100)."""
    try:
        level = max(0, min(100, level))
        monitors = sbc.list_monitors()
        
        if len(monitors) > 1:
            info = sbc.list_monitors_info()
            laptop_display = next((m['name'] for m in info if 'WMI' in str(m['method'])), monitors[0])
            external_display = next((m['name'] for m in info if 'VCP' in str(m['method'])), monitors[-1])

            if display_type is None:
                # Ask the user interactively
                from audio.tts import speak
                from audio.stt import listen
                
                speak("I detect multiple screens. Should I adjust the laptop, the external monitor, or both?")
                response = listen(timeout=5, phrase_time_limit=5)
                
                if not response:
                    return "I didn't catch that, so I left the brightness unchanged."
                
                response = response.lower()
                if "laptop" in response or "internal" in response:
                    display_type = "laptop"
                elif "external" in response or "monitor" in response or "lenovo" in response:
                    display_type = "external"
                elif "both" in response or "all" in response:
                    display_type = "both"
                else:
                    return "I didn't understand the choice, so I left the brightness unchanged."

            if display_type == "laptop":
                sbc.set_brightness(level, display=laptop_display)
                return f"Laptop brightness set to {level}%."
            elif display_type == "external":
                sbc.set_brightness(level, display=external_display)
                return f"External monitor brightness set to {level}%."
            else:
                sbc.set_brightness(level)
                return f"All screens set to {level}%."
        else:
            sbc.set_brightness(level)
            return f"Screen brightness set to {level}%."
    except Exception as e:
        return f"Sorry, I couldn't adjust the brightness: {e}"

def lock_pc() -> str:
    """Lock the Windows workstation."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Locking the computer."
    except Exception as e:
        return f"Sorry, I couldn't lock the computer: {e}"

def pause_media() -> str:
    """Pause media playback globally using system media keys."""
    try:
        import pyautogui
        pyautogui.press('playpause')
        config.is_media_paused = True
        if config.current_media_type == "movie":
            return "Understood, I've paused the movie for you."
        return "Understood, I've paused the video for you."
    except Exception as e:
        return f"Sorry, I couldn't pause the video: {e}"

def resume_media() -> str:
    """Resume media playback globally using system media keys."""
    try:
        import pyautogui
        pyautogui.press('playpause')
        config.is_media_paused = False
        if config.current_media_type == "movie":
            return "Understood, I've resumed the movie for you."
        return "Understood, I've resumed the video for you."
    except Exception as e:
        return f"Sorry, I couldn't resume the video: {e}"
