import os
import tempfile
import uuid
import asyncio
import pygame
import edge_tts
import threading
from config import _tts_lock
import config

# Initialize pygame mixer once for audio playback
pygame.mixer.init()

def speak(text: str) -> None:
    """
    Speak the given text aloud using Microsoft Edge TTS for a natural voice.
    Can be interrupted by calling stop_speaking() from another thread.
    """
    print(f"[FRIDAY] {text}")
    
    filename = os.path.join(tempfile.gettempdir(), f"friday_tts_{uuid.uuid4().hex}.mp3")
    
    try:
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        asyncio.run(communicate.save(filename))
        
        with _tts_lock:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                try:
                    pygame.mixer.music.unload()
                except AttributeError:
                    pass
            config._current_tts_file = filename
            
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    except Exception as e:
        print(f"[TTS Error] {e}")
    finally:
        try:
            try:
                pygame.mixer.music.unload()
            except AttributeError:
                pass
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass

def speak_async(text: str) -> threading.Thread:
    t = threading.Thread(target=speak, args=(text,), daemon=True)
    t.start()
    return t

def stop_speaking() -> None:
    """Interrupt the current TTS playback if active."""
    with _tts_lock:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()
            except AttributeError:
                pass
            print("[TTS] Speech interrupted.")
