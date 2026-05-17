import os
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global Configuration Constants
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 15
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VLC_PATH = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

# Global State Variables
youtube_results = []
current_folder = ""
_tts_lock = threading.Lock()
_current_tts_file = None
_app_map = {}
is_awake = True
