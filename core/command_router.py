from tools.system import get_time, find_and_open_folder, create_folder, create_file, open_app
from tools.youtube import play_youtube_result, play_on_youtube, youtube_search
from tools.browser import open_in_chrome
from tools.media import play_local_movie
from tools.system_control import set_volume, set_brightness, lock_pc, pause_media, resume_media
from tools.timer import start_timer
from tools.vision import analyze_screen
from tools.debug_screen import debug_screen
from core.brain import ask_ai
import config
import re

def _extract_after(text: str, keyword: str) -> str:
    parts = text.split(keyword, 1)
    if len(parts) > 1:
        return parts[1].strip()
    return ""


def _clean_local_media_query(text: str) -> str:
    query = text
    for word in ["movie", "film", "video", "play", "watch", "open", "the", "now"]:
        query = re.sub(rf"\b{re.escape(word)}\b", " ", query)
    query = re.sub(r"\b(from|on|in)\s+(my\s+)?(desktop|pc|computer|laptop)\b", " ", query)
    query = re.sub(r"\s+", " ", query)
    return query.strip()


def _youtube_result_index(text: str) -> int | None:
    ordinal_map = {
        "first": 0, "1st": 0,
        "second": 1, "2nd": 1,
        "third": 2, "3rd": 2,
        "fourth": 3, "4th": 3,
        "fifth": 4, "5th": 4,
        "sixth": 5, "6th": 5,
        "seventh": 6, "7th": 6,
        "eighth": 7, "8th": 7,
        "ninth": 8, "9th": 8,
        "tenth": 9, "10th": 9,
    }

    for word, idx in ordinal_map.items():
        if re.search(rf"\bplay\s+(the\s+)?{re.escape(word)}(\s+(result|video|one))?\b", text):
            return idx

    match = re.search(r"\bplay\s+(result|video|number)\s+(\d+)\b", text)
    if match:
        return int(match.group(2)) - 1

    if re.search(r"\bplay\s+next(\s+(result|video|one))?\b", text):
        return 1

    return None


def process_command(text: str) -> str | None:
    """
    Analyze the user's spoken text and route it to the appropriate function.
    Returns a response string, or None to signal exit.
    """
    text = text.lower().strip()

    if any(word in text for word in ["stop", "goodbye", "bye", "shut down", "exit", "quit"]):
        return None

    # -- Media Controls (Pause / Resume) --
    if "pause" in text:
        return pause_media()

    if "resume" in text or text.strip() in ["play", "play the video", "play video", "play the music", "play music", "play the song", "play song"]:
        return resume_media()

    if text in ["play the movie", "play movie", "continue the movie", "continue movie"]:
        if config.current_media_type == "movie" and config.is_media_paused:
            return resume_media()
        return "Which movie should I play?"

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

    # -- Debug Screen --
    debug_screen_phrases = [
        "debug screen",
        "debug my screen",
        "debug this error",
        "debug my error",
        "debug this code",
        "explain this error",
        "explain my error",
        "read this error",
        "read the error on my screen",
        "read my error",
        "what is wrong with my code",
        "what's wrong with my code",
        "what is wrong with this code",
        "what's wrong with this code",
        "what is wrong with this error",
        "what's wrong with this error",
        "why is my code not working",
        "why is this error happening",
        "fix my screen",
        "fix this error",
        "help me debug",
        "help debug this",
    ]
    looks_like_debug_request = (
        ("debug" in text and any(w in text for w in ["screen", "error", "code", "terminal"]))
        or (
            "error" in text
            and any(w in text for w in ["screen", "code", "terminal", "traceback"])
            and any(w in text for w in ["read", "explain", "debug", "fix", "help", "wrong"])
        )
        or (
            "wrong" in text
            and any(w in text for w in ["code", "error", "screen", "terminal"])
        )
    )
    if any(phrase in text for phrase in debug_screen_phrases) or looks_like_debug_request:
        return debug_screen(text)

    # -- Vision --
    if "screen" in text and any(w in text for w in ["what", "look", "read", "see"]):
        return analyze_screen(text)

    if "time" in text and any(w in text for w in ["what", "tell", "current"]):
        return get_time()

    if "movie" in text and any(w in text for w in ["play", "watch", "open"]):
        # Handle local movies before YouTube result selection so titles like "Panda 2" do not mean "play second".
        if "folder" not in text:
            query = _clean_local_media_query(text)
            if not query and config.current_media_type == "movie" and config.is_media_paused:
                return resume_media()
            if query:
                return play_local_movie(query)
            return "Which movie should I play?"

    youtube_idx = _youtube_result_index(text)
    if youtube_idx is not None:
        return play_youtube_result(youtube_idx)

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

    if text.startswith("play "):
        query = text[5:].strip()
        if query:
            if "movie" in query:
                movie_query = _clean_local_media_query(query)
                if not movie_query and config.current_media_type == "movie" and config.is_media_paused:
                    return resume_media()
                if movie_query:
                    return play_local_movie(movie_query)
                return "Which movie should I play?"
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

    return ask_ai(text)
