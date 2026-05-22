import os
import subprocess
import config
from config import VLC_PATH

def play_local_movie(movie_name: str) -> str:
    r"""
    Search for a local movie in E:\Movies and D:\Movies and play it.
    """
    movie_name = movie_name.strip()
    if not movie_name:
        if config.current_media_type == "movie" and config.is_media_paused:
            return "The current movie is paused. Say 'resume the movie' or 'play' to continue it."
        return "Which movie should I play?"

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
            for item in os.listdir(root):
                item_path = os.path.join(root, item)
                
                normalized_item = item.lower().replace(".", " ").replace("_", " ")
                
                if os.path.isfile(item_path) and movie_name.lower() in normalized_item:
                    if os.path.exists(VLC_PATH):
                        subprocess.Popen([VLC_PATH, item_path])
                    else:
                        os.startfile(item_path)
                    config.current_media_title = item
                    config.current_media_type = "movie"
                    config.is_media_paused = False
                    return f"Playing movie: {item}"
        except PermissionError:
            continue
            
    return f"Sorry, I couldn't find a movie named '{movie_name}' in your Movies folders."
