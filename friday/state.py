import threading


youtube_results = []
current_folder = ""
current_media_title = ""
current_media_type = ""
is_media_paused = False
tts_lock = threading.Lock()
current_tts_file = None
app_map = {}
is_awake = True
