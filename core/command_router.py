from tools.system import get_time, find_and_open_folder, create_folder, create_file, open_app
from tools.youtube import play_youtube_result, play_on_youtube, youtube_search
from tools.browser import open_in_chrome
from tools.media import play_local_movie
from tools.system_control import set_volume, set_brightness, lock_pc, pause_media, resume_media
from tools.timer import start_timer
from tools.vision import analyze_screen
from core.brain import ask_gemini
import config
import re

def _extract_after(text: str, keyword: str) -> str:
    parts = text.split(keyword, 1)
    if len(parts) > 1:
        return parts[1].strip()
    return ""

def process_command(text: str) -> str | None:
    """
    Analyze the user's spoken text and route it to the appropriate function.
    Returns a response string, or None to signal exit.
    """
    if any(word in text for word in ["stop", "goodbye", "bye", "shut down", "exit", "quit"]):
        return None

    # -- Media Controls (Pause / Resume) --
    if "pause" in text:
        return pause_media()

    if "resume" in text or text.strip() in ["play", "play the video", "play video", "play the music", "play music", "play the song", "play song"]:
        return resume_media()

    # -- Timers --
    if "timer" in text:
        match = re.search(r'(\d+)\s*minute', text)
        if match:
            minutes = int(match.group(1))
            return start_timer(minutes)
            
    # -- System Control --
    if "volume" in text:
        if "mute" in text:
            return set_volume(0)
        match = re.search(r'(\d+)', text)
        if match:
            return set_volume(int(match.group(1)))
            
    if "brightness" in text:
        match = re.search(r'(\d+)', text)
        if match:
            level = int(match.group(1))
            if "laptop" in text or "internal" in text:
                return set_brightness(level, display_type="laptop")
            elif "external" in text or "monitor" in text:
                return set_brightness(level, display_type="external")
            elif "both" in text or "all" in text:
                return set_brightness(level, display_type="both")
            return set_brightness(level)
            
    if "lock" in text and any(w in text for w in ["pc", "computer", "screen"]):
        return lock_pc()
        
    # -- Vision --
    if "screen" in text and any(w in text for w in ["what", "look", "read", "see"]):
        return analyze_screen(text)

    if "time" in text and any(w in text for w in ["what", "tell", "current"]):
        return get_time()

    if "play" in text:
        ordinal_map = {
            "first": 0, "1st": 0, "one": 0, "1": 0,
            "second": 1, "2nd": 1, "two": 1, "2": 1,
            "third": 2, "3rd": 2, "three": 2, "3": 2,
            "fourth": 3, "4th": 3, "four": 3, "4": 3,
            "fifth": 4, "5th": 4, "five": 4, "5": 4,
            "sixth": 5, "6th": 5, "six": 5, "6": 5,
            "seventh": 6, "7th": 6, "seven": 6, "7": 6,
            "eighth": 7, "8th": 7, "eight": 7, "8": 7,
            "ninth": 8, "9th": 8, "nine": 8, "9": 8,
            "tenth": 9, "10th": 9, "ten": 9, "10": 9,
        }
        for word, idx in ordinal_map.items():
            if word in text:
                return play_youtube_result(idx)
        if "next" in text:
            return play_youtube_result(1)

    if any(word in text for word in ["play", "song", "music", "video"]) and "youtube" in text:
        query = text
        for sep in ["on youtube", "in youtube", "from youtube", "youtube"]:
            if sep in query:
                query = query.split(sep)[0].strip()
                break
        for prefix in ["play", "search", "find", "open"]:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
        if query:
            return play_on_youtube(query)
        else:
            return open_in_chrome("https://www.youtube.com")

    # Check for folder opening before movie playback to prevent 'open movies folder' from playing a movie
    if "folder" in text and any(w in text for w in ["open", "find", "show"]):
        query = text.replace("open", "").replace("find", "").replace("show", "").replace("the", "").replace("folder", "").strip()
        if query:
            return find_and_open_folder(query)

    if "movie" in text and any(w in text for w in ["play", "watch", "open"]):
        # Prevent 'open movies folder' from falling through here if folder was empty
        if "folder" not in text:
            query = text.replace("movie", "").replace("play", "").replace("watch", "").replace("open", "").replace("the", "").replace("now", "").strip()
            if query:
                return play_local_movie(query)

    if text.startswith("play "):
        query = text[5:].strip()
        if query:
            if "movie" in query:
                return play_local_movie(query.replace("movie", "").strip())
            return play_on_youtube(query)

    if "youtube" in text and any(w in text for w in ["search", "find", "look"]):
        query = _extract_after(text, "search") or _extract_after(text, "find") or _extract_after(text, "look")
        query = query.replace("on youtube", "").replace("in youtube", "").strip()
        if query:
            return youtube_search(query)

    # "open" + known website names — but try the INSTALLED desktop app first!
    # e.g. "open whatsapp" will open the WhatsApp app if installed, otherwise web browser.
    SITES = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "reddit": "https://www.reddit.com",
        "stackoverflow": "https://www.stackoverflow.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com",
        "whatsapp": "https://web.whatsapp.com",
        "chatgpt": "https://chat.openai.com",
    }
    if "open" in text and any(site in text for site in SITES):
        for name, url in SITES.items():
            if name in text:
                # Try installed desktop app first
                app_result = open_app(name)
                if "couldn't find it" not in app_result and "don't know" not in app_result:
                    return app_result
                # Fallback to browser
                return open_in_chrome(url)

    if ("create" in text or "make" in text or "new" in text) and "folder" in text:
        folder_name = ""
        if "called" in text:
            folder_name = _extract_after(text, "called")
        elif "named" in text:
            folder_name = _extract_after(text, "named")
        else:
            folder_name = _extract_after(text, "folder")
        if folder_name:
            return create_folder(folder_name)

    if ("create" in text or "make" in text or "new" in text) and "file" in text:
        file_name = ""
        if "called" in text:
            file_name = _extract_after(text, "called")
        elif "named" in text:
            file_name = _extract_after(text, "named")
        else:
            file_name = _extract_after(text, "file")
        if file_name:
            return create_file(file_name)

    # (Folder opening is now handled earlier in the file)

    if "open" in text or "start" in text or "launch" in text:
        for verb in ["open", "start", "launch"]:
            if verb in text:
                app_name = _extract_after(text, verb)
                if app_name:
                    return open_app(app_name)

    return ask_gemini(text)
