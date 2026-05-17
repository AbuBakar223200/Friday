"""
F.R.I.D.A.Y. -- Female Replacement Intelligent Digital Assistant Youth
A local voice assistant inspired by Iron Man, powered by Google Gemini.

Modules:
    - listen()      : Captures microphone audio and converts to text
    - speak()       : Speaks text aloud using a female voice (pyttsx3)
    - ask_gemini()  : Sends prompts to Google Gemini for intelligent responses
    - get_time()    : Returns the current time
    - open_website(): Opens a URL in the default browser
    - open_app()    : Opens common Windows applications
    - main()        : Main loop -- listen -> process -> respond
"""

import os
import sys
import re
import datetime
import webbrowser
import subprocess
import threading
import urllib.parse

from dotenv import load_dotenv
load_dotenv()

import pyttsx3
import speech_recognition as sr
import requests
from google import genai


# -----------------------------------------------
#  CONFIGURATION
# -----------------------------------------------

# Gemini API key -- set via environment variable or replace the fallback string
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Speech rate (words per minute) -- lower = slower / more natural
SPEECH_RATE = 175

# Microphone listen timeout (seconds) -- how long to wait for speech to begin
LISTEN_TIMEOUT = 5

# Phrase time limit (seconds) -- max duration of a single phrase
PHRASE_TIME_LIMIT = 15


# -----------------------------------------------
#  TEXT-TO-SPEECH ENGINE  (pyttsx3)
# -----------------------------------------------

# Detect the female voice ID once at startup
def _find_female_voice_id():
    """Find and return the ID of a female voice (Microsoft Zira on Windows)."""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    
    # Look for Zira or any female voice
    for voice in voices:
        if "zira" in voice.name.lower() or "female" in voice.name.lower():
            print(f"[TTS] Selected voice: {voice.name}")
            engine.stop()
            return voice.id
    
    # Fallback: second voice is typically female on Windows
    if len(voices) > 1:
        print(f"[TTS] Selected voice (fallback): {voices[1].name}")
        engine.stop()
        return voices[1].id
    
    print(f"[TTS] Using default voice: {voices[0].name}")
    engine.stop()
    return voices[0].id


# Cache the female voice ID
FEMALE_VOICE_ID = _find_female_voice_id()

# Global reference to the current TTS engine (for interruption)
_current_tts_engine = None
_tts_lock = threading.Lock()


def speak(text: str) -> None:
    """
    Speak the given text aloud using pyttsx3 (blocking).
    Can be interrupted by calling stop_speaking() from another thread.

    Args:
        text: The string to speak.
    """
    global _current_tts_engine
    print(f"[FRIDAY] {text}")

    # Create a fresh engine each time to guarantee audio output
    engine = pyttsx3.init()
    engine.setProperty("voice", FEMALE_VOICE_ID)
    engine.setProperty("rate", SPEECH_RATE)
    engine.setProperty("volume", 1.0)  # Max volume

    with _tts_lock:
        _current_tts_engine = engine

    engine.say(text)
    engine.runAndWait()
    engine.stop()

    with _tts_lock:
        _current_tts_engine = None


def speak_async(text: str) -> threading.Thread:
    """
    Speak text in a background thread so the main loop can listen
    for interruptions. Returns the thread object.
    """
    t = threading.Thread(target=speak, args=(text,), daemon=True)
    t.start()
    return t


def stop_speaking() -> None:
    """Interrupt the current TTS playback if active."""
    global _current_tts_engine
    with _tts_lock:
        if _current_tts_engine:
            try:
                _current_tts_engine.stop()
            except Exception:
                pass
            _current_tts_engine = None
            print("[TTS] Speech interrupted.")


# -----------------------------------------------
#  SPEECH RECOGNITION  (SpeechRecognition)
# -----------------------------------------------

def listen() -> str | None:
    """
    Listen to the microphone and convert speech to text using
    Google's free speech recognition API.

    Returns:
        The transcribed string in lowercase, or None if nothing was understood.
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("\n[MIC] Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[MIC] Listening...")

            # Capture audio from the microphone
            audio = recognizer.listen(
                source,
                timeout=LISTEN_TIMEOUT,
                phrase_time_limit=PHRASE_TIME_LIMIT,
            )

        # Transcribe audio to text via Google Speech Recognition
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


# -----------------------------------------------
#  GEMINI AI INTEGRATION  (google-genai SDK)
# -----------------------------------------------

# System prompt that primes Gemini to act as Friday
FRIDAY_SYSTEM_PROMPT = (
    "You are Friday, a highly intelligent and helpful AI voice assistant "
    "inspired by the AI from Iron Man. You are concise, witty, and professional. "
    "Keep your answers brief (2-3 sentences max) since they will be spoken aloud. "
    "Address the user respectfully. Do not use markdown, emojis, or special "
    "formatting -- respond in plain conversational English."
)


def _init_gemini():
    """
    Configure the Gemini API client using the new google-genai SDK.
    Returns a Client instance, or None if the key is missing.
    """
    if not GEMINI_API_KEY:
        print("[GEMINI] WARNING: No API key found. Set the GEMINI_API_KEY environment variable.")
        print("[GEMINI]          AI responses will be unavailable until a key is provided.")
        return None

    client = genai.Client(api_key=GEMINI_API_KEY)
    print("[GEMINI] Client initialized successfully.")
    return client


# Global Gemini client instance
gemini_client = _init_gemini()


def ask_gemini(prompt: str) -> str:
    """
    Send a prompt to Google Gemini and return the response text.

    Args:
        prompt: The user's transcribed speech.

    Returns:
        The AI-generated response string.
    """
    if gemini_client is None:
        return "I'm sorry, my AI brain isn't connected right now. Please set up the Gemini API key."

    # Try models in order of preference; fall back if one is overloaded
    models = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"]
    for model_name in models:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=FRIDAY_SYSTEM_PROMPT,
                ),
            )
            return response.text.strip()
        except Exception as e:
            print(f"[GEMINI] {model_name} failed: {e}")
            continue

    return "I encountered an error while thinking. Please try again."


# -----------------------------------------------
#  PC AUTOMATION FUNCTIONS
# -----------------------------------------------

# Path to Google Chrome
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Path to VLC Media Player
VLC_PATH = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

# Common folder locations for quick navigation
KNOWN_FOLDERS = {
    "desktop": os.path.join(os.environ["USERPROFILE"], "Desktop"),
    "documents": os.path.join(os.environ["USERPROFILE"], "Documents"),
    "downloads": os.path.join(os.environ["USERPROFILE"], "Downloads"),
    "pictures": os.path.join(os.environ["USERPROFILE"], "Pictures"),
    "videos": os.path.join(os.environ["USERPROFILE"], "Videos"),
    "music": os.path.join(os.environ["USERPROFILE"], "Music"),
}


def get_time() -> str:
    """Return the current time as a human-readable string."""
    now = datetime.datetime.now()
    return now.strftime("It's %I:%M %p on %A, %B %d, %Y.")


def open_in_chrome(url: str) -> str:
    """
    Open a URL specifically in Google Chrome.

    Args:
        url: The full URL to open.

    Returns:
        Confirmation message.
    """
    try:
        subprocess.Popen([CHROME_PATH, url])
        return f"Opening in Chrome for you."
    except FileNotFoundError:
        # Fallback to default browser if Chrome isn't found
        webbrowser.open(url)
        return f"Chrome not found, opening in your default browser."


def youtube_search(query: str) -> str:
    """
    Search YouTube for a query, open results in Chrome, and store
    video IDs so the user can say 'play first/second/third'.

    Args:
        query: The search query (e.g., "Bengali songs").

    Returns:
        Confirmation message with number of results found.
    """
    global youtube_results
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

    # Open search results in Chrome
    open_in_chrome(search_url)

    # Fetch the page to extract video IDs for direct playback
    try:
        resp = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for vid_id in video_ids:
            if vid_id not in seen:
                seen.add(vid_id)
                unique_ids.append(vid_id)
        youtube_results = unique_ids[:10]
        count = len(youtube_results)
        print(f"[YOUTUBE] Found {count} videos for '{query}'")
        return f"Found {count} results for '{query}'. Say 'play first', 'play second', or 'play third' to play one!"
    except Exception as e:
        print(f"[YOUTUBE] Error fetching results: {e}")
        youtube_results = []
        return f"Searching YouTube for '{query}'. Click on a video to play it!"


def play_on_youtube(query: str) -> str:
    """
    Search YouTube, store video IDs, and auto-play the FIRST result.

    Args:
        query: What to play (e.g., "Bengali song", "Arijit Singh").

    Returns:
        Confirmation message.
    """
    global youtube_results
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

    # Fetch the page to extract video IDs
    try:
        resp = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
        seen = set()
        unique_ids = []
        for vid_id in video_ids:
            if vid_id not in seen:
                seen.add(vid_id)
                unique_ids.append(vid_id)
        youtube_results = unique_ids[:10]

        if youtube_results:
            # Auto-play the first result
            video_url = f"https://www.youtube.com/watch?v={youtube_results[0]}"
            open_in_chrome(video_url)
            return f"Playing the first result for '{query}'. Say 'play second' or 'play third' to switch!"
        else:
            open_in_chrome(search_url)
            return f"Searching YouTube for '{query}'. Click on a video to play it!"
    except Exception as e:
        print(f"[YOUTUBE] Error: {e}")
        open_in_chrome(search_url)
        return f"Searching YouTube for '{query}'. Click on a video to play it!"


def play_youtube_result(index: int) -> str:
    """
    Play a specific video from the last YouTube search results.

    Args:
        index: 0-based index of the video to play.

    Returns:
        Confirmation message.
    """
    if not youtube_results:
        return "I don't have any search results yet. Try searching YouTube first!"
    if index >= len(youtube_results):
        return f"I only have {len(youtube_results)} results. Try a smaller number."

    video_url = f"https://www.youtube.com/watch?v={youtube_results[index]}"
    open_in_chrome(video_url)
    return f"Playing video number {index + 1} for you!"


def play_local_movie(movie_name: str) -> str:
    """
    Search for a local movie in E:\\Movies and D:\\Movies and play it.
    
    Args:
        movie_name: The name of the movie to find.
        
    Returns:
        Confirmation message.
    """
    search_roots = [
        r"E:\Movies",
        r"D:\Movies",
        "D:\\",
        "E:\\",
    ]
    
    for root in search_roots:
        if not os.path.exists(root):
            continue
        try:
            # First, check files directly in these folders
            for item in os.listdir(root):
                item_path = os.path.join(root, item)
                
                # Normalize filename for easier matching (replace dots, underscores with spaces)
                normalized_item = item.lower().replace(".", " ").replace("_", " ")
                
                if os.path.isfile(item_path) and movie_name.lower() in normalized_item:
                    # Play the movie using VLC media player
                    if os.path.exists(VLC_PATH):
                        subprocess.Popen([VLC_PATH, item_path])
                    else:
                        os.startfile(item_path) # Fallback if VLC missing
                    return f"Playing movie: {item}"
        except PermissionError:
            continue
            
    return f"Sorry, I couldn't find a movie named '{movie_name}' in your Movies folders."


def open_folder(folder_path: str) -> str:
    """
    Open a specific folder in Windows File Explorer.

    Args:
        folder_path: The full path to the folder.

    Returns:
        Confirmation message.
    """
    global current_folder
    if os.path.exists(folder_path):
        # Update the context so future commands search from here
        current_folder = folder_path
        subprocess.Popen(["explorer", folder_path])
        return f"Opening folder: {os.path.basename(folder_path)}"
    else:
        return f"Sorry, I couldn't find the folder: {folder_path}"


def find_and_open_folder(folder_name: str) -> str:
    """
    Search for a folder by name. Uses context-aware navigation:
    1. First searches inside the CURRENT folder (if one was previously opened)
    2. Then searches known shortcuts (desktop, downloads, etc.)
    3. Then searches D: and E: drive roots

    Args:
        folder_name: The name of the folder to find (e.g., "hci", "11th trimester").

    Returns:
        Confirmation message.
    """
    global current_folder

    # 1. Context-aware: search inside the currently opened folder first
    if current_folder and os.path.exists(current_folder):
        try:
            for item in os.listdir(current_folder):
                item_path = os.path.join(current_folder, item)
                if os.path.isdir(item_path) and folder_name.lower() in item.lower():
                    return open_folder(item_path)
        except PermissionError:
            pass

    # 2. Check known shortcuts (desktop, downloads, etc.)
    if folder_name.lower() in KNOWN_FOLDERS:
        return open_folder(KNOWN_FOLDERS[folder_name.lower()])

    # 3. Search D: and E: drives (no C: drive access)
    search_roots = [
        "D:\\",
        r"D:\United International University",
        "E:\\",
    ]

    for root in search_roots:
        if not os.path.exists(root):
            continue
        try:
            for item in os.listdir(root):
                item_path = os.path.join(root, item)
                if os.path.isdir(item_path) and folder_name.lower() in item.lower():
                    return open_folder(item_path)
        except PermissionError:
            continue

    return f"Sorry, I couldn't find a folder named '{folder_name}' on your computer."


def create_folder(folder_name: str, location: str = None) -> str:
    """
    Create a new folder on the Desktop or a specified location.

    Args:
        folder_name: The name of the new folder.
        location: Where to create it (defaults to Desktop).

    Returns:
        Confirmation message.
    """
    if location is None:
        location = KNOWN_FOLDERS["desktop"]

    folder_path = os.path.join(location, folder_name)
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Created folder '{folder_name}' on your Desktop."
    except Exception as e:
        return f"Sorry, I couldn't create the folder: {e}"


def create_file(file_name: str, location: str = None) -> str:
    """
    Create a new empty file on the Desktop or a specified location.

    Args:
        file_name: The name of the new file (e.g., "notes.txt").
        location: Where to create it (defaults to Desktop).

    Returns:
        Confirmation message.
    """
    if location is None:
        location = KNOWN_FOLDERS["desktop"]

    # Add .txt extension if no extension given
    if "." not in file_name:
        file_name += ".txt"

    file_path = os.path.join(location, file_name)
    try:
        with open(file_path, "w") as f:
            pass  # Create empty file
        return f"Created file '{file_name}' on your Desktop."
    except Exception as e:
        return f"Sorry, I couldn't create the file: {e}"


def open_app(app_name: str) -> str:
    """
    Open a common Windows application by name.

    Args:
        app_name: The name of the application (e.g., "notepad", "calculator").

    Returns:
        Confirmation message or an error note.
    """
    # Map of friendly names to executable commands
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "file explorer": "explorer.exe",
        "command prompt": "cmd.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "chrome": CHROME_PATH,
    }

    key = app_name.lower().strip()
    executable = app_map.get(key)

    if executable:
        try:
            if executable.startswith("ms-"):
                os.startfile(executable)
            else:
                subprocess.Popen(executable, shell=True)
            return f"Opening {app_name} for you."
        except Exception as e:
            return f"Sorry, I couldn't open {app_name}: {e}"
    else:
        return f"I don't know how to open '{app_name}'. You can teach me by adding it to the app map!"


# -----------------------------------------------
#  COMMAND ROUTER
# -----------------------------------------------

def _extract_after(text: str, keyword: str) -> str:
    """Extract everything after a keyword in the text."""
    parts = text.split(keyword, 1)
    if len(parts) > 1:
        return parts[1].strip()
    return ""


def process_command(text: str) -> str | None:
    """
    Analyze the user's spoken text and route it to the appropriate function.

    Args:
        text: The transcribed speech (lowercase).

    Returns:
        A response string, or None to signal exit.
    """
    # -- Exit commands --
    if any(word in text for word in ["stop", "goodbye", "bye", "shut down", "exit", "quit"]):
        return None  # Signal to exit

    # -- Time query --
    if "time" in text and any(w in text for w in ["what", "tell", "current"]):
        return get_time()

    # -- Play a specific YouTube result ("play first", "play 2nd", "play third") --
    if "play" in text and youtube_results:
        # Map spoken ordinals to 0-based index
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
        # "play next" -> play the next one after the last played
        if "next" in text:
            return play_youtube_result(1)  # Default to 2nd

    # -- Play / search on YouTube --
    if any(word in text for word in ["play", "song", "music", "video"]) and "youtube" in text:
        # Extract the query: everything before "on youtube" or "in youtube"
        query = text
        for sep in ["on youtube", "in youtube", "from youtube", "youtube"]:
            if sep in query:
                query = query.split(sep)[0].strip()
                break
        # Remove leading "play" / "search"
        for prefix in ["play", "search", "find", "open"]:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
        if query:
            return play_on_youtube(query)
        else:
            return open_in_chrome("https://www.youtube.com")

    # -- Play local movie --
    if "movie" in text and any(w in text for w in ["play", "watch", "open"]):
        # Extract the movie name
        query = text.replace("movie", "").replace("play", "").replace("watch", "").replace("open", "").replace("the", "").replace("now", "").strip()
        if query:
            return play_local_movie(query)

    # -- Play something (without saying "youtube") --
    if text.startswith("play "):
        query = text[5:].strip()
        if query:
            # Check if it might be a movie first
            if "movie" in query:
                return play_local_movie(query.replace("movie", "").strip())
            return play_on_youtube(query)

    # -- YouTube search --
    if "youtube" in text and any(w in text for w in ["search", "find", "look"]):
        query = _extract_after(text, "search") or _extract_after(text, "find") or _extract_after(text, "look")
        query = query.replace("on youtube", "").replace("in youtube", "").strip()
        if query:
            return youtube_search(query)

    # -- Open a website in Chrome --
    if "open" in text and any(site in text for site in [
        "youtube", "google", "github", "facebook", "twitter", "reddit", "stackoverflow",
        "instagram", "linkedin", "whatsapp", "chatgpt"
    ]):
        sites = {
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
        for name, url in sites.items():
            if name in text:
                return open_in_chrome(url)

    # -- Create a folder --
    if ("create" in text or "make" in text or "new" in text) and "folder" in text:
        # Extract folder name after "folder" keyword, or after "called"/"named"
        folder_name = ""
        if "called" in text:
            folder_name = _extract_after(text, "called")
        elif "named" in text:
            folder_name = _extract_after(text, "named")
        elif "folder" in text:
            folder_name = _extract_after(text, "folder")

        # Clean up common trailing words
        for word in ["on desktop", "on the desktop", "in desktop", "please"]:
            folder_name = folder_name.replace(word, "").strip()

        if folder_name:
            return create_folder(folder_name)
        else:
            return "What would you like to name the folder?"

    # -- Create a file --
    if ("create" in text or "make" in text or "new" in text) and "file" in text:
        file_name = ""
        if "called" in text:
            file_name = _extract_after(text, "called")
        elif "named" in text:
            file_name = _extract_after(text, "named")
        elif "file" in text:
            file_name = _extract_after(text, "file")

        for word in ["on desktop", "on the desktop", "in desktop", "please"]:
            file_name = file_name.replace(word, "").strip()

        if file_name:
            return create_file(file_name)
        else:
            return "What would you like to name the file?"

    # -- Open a specific folder (context-aware) --
    if "open" in text and ("folder" in text or "trimester" in text or "semester" in text
                           or "desktop" in text or "downloads" in text or "documents" in text
                           or current_folder is not None):
        # Extract folder name and aggressively clean filler words
        folder_name = text
        # Remove common filler phrases
        for filler in ["open", "folder", "file", "the", "my", "now", "from", "that",
                       "in file explorer", "in explorer", "please", "for me",
                       "go to", "navigate to", "can you", "could you"]:
            folder_name = folder_name.replace(filler, " ")
        # Collapse whitespace and strip
        folder_name = " ".join(folder_name.split()).strip()
        if folder_name:
            return find_and_open_folder(folder_name)

    # -- Open a Windows app --
    if "open" in text:
        for app_name in ["notepad", "calculator", "paint", "file explorer",
                         "command prompt", "task manager", "settings",
                         "word", "excel", "powerpoint", "chrome"]:
            if app_name in text:
                return open_app(app_name)

    # -- Fallback: send to Gemini for a smart response --
    return ask_gemini(text)


# -----------------------------------------------
#  CONTEXT STATE
# -----------------------------------------------

# Tracks the last opened folder for context-aware navigation
current_folder = None

# Stores YouTube video IDs from the last search for "play 2nd/3rd" commands
youtube_results = []


# -----------------------------------------------
#  MAIN LOOP
# -----------------------------------------------

def main():
    """
    Main entry point for the Friday assistant.
    Speaks responses in a background thread so the user can interrupt
    by speaking at any time. Uses context-aware folder navigation.
    """
    # Startup greeting (blocking — let it finish before listening)
    speak("Friday is online. How can I help you today?")

    while True:
        # Listen for user speech
        user_text = listen()

        # If nothing was heard, loop again
        if user_text is None:
            continue

        # Process the command
        response = process_command(user_text)

        # None means the user wants to exit
        if response is None:
            speak("Goodbye! Have a great day.")
            break

        # Speak the response in a background thread
        # This allows the user to interrupt by speaking
        speech_thread = speak_async(response)

        # While Friday is speaking, listen for interruption
        while speech_thread.is_alive():
            # Try to catch user speech with a short timeout
            interruption = listen()
            if interruption is not None:
                # User spoke! Stop Friday's speech and process the new command
                stop_speaking()
                speech_thread.join(timeout=1)

                # Process the interruption immediately
                new_response = process_command(interruption)
                if new_response is None:
                    speak("Goodbye! Have a great day.")
                    print("\n[SYSTEM] Friday has shut down.")
                    return

                # Speak the new response (also interruptible)
                speech_thread = speak_async(new_response)

    print("\n[SYSTEM] Friday has shut down.")


# -----------------------------------------------
#  ENTRY POINT
# -----------------------------------------------

if __name__ == "__main__":
    main()
