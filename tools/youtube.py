import re
import time
import requests
import urllib.parse
import pyautogui
import pyperclip
from tools.browser import open_in_chrome
import config

def _extract_video_ids(html_text: str, current_video_id: str = None, limit: int = 10) -> list:
    video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html_text)
    seen = set()
    if current_video_id:
        seen.add(current_video_id)
    unique_ids = []
    for vid_id in video_ids:
        if vid_id not in seen:
            seen.add(vid_id)
            unique_ids.append(vid_id)
    return unique_ids[:limit]

def scrape_active_youtube_tab() -> list:
    print("[YOUTUBE] Extracting videos from your screen...")
    original_clipboard = pyperclip.paste()
    pyperclip.copy("")
    
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)
    current_url = pyperclip.paste()
    
    current_video_id = None
    if current_url and "watch?v=" in current_url:
        current_video_id = current_url.split("watch?v=")[1][:11]
        print(f"[YOUTUBE] Ignoring currently playing video: {current_video_id}")
        
    pyperclip.copy("")
    
    pyautogui.hotkey('ctrl', 'u')
    time.sleep(2.0)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1.0)
    pyautogui.hotkey('ctrl', 'w')
    
    html = pyperclip.paste()
    
    try:
        pyperclip.copy(original_clipboard)
    except Exception:
        pass
        
    if html:
        return _extract_video_ids(html, current_video_id, limit=20)
    return []

def youtube_search(query: str) -> str:
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    open_in_chrome(search_url)

    try:
        resp = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
        config.youtube_results = _extract_video_ids(resp.text)
        count = len(config.youtube_results)
        print(f"[YOUTUBE] Found {count} videos for '{query}'")
        return f"Found {count} results for '{query}'. Say 'play first', 'play second', or 'play third' to play one!"
    except Exception as e:
        print(f"[YOUTUBE] Error fetching results: {e}")
        config.youtube_results = []
        return f"Searching YouTube for '{query}'. Click on a video to play it!"

def play_on_youtube(query: str) -> str:
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

    try:
        resp = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
        config.youtube_results = _extract_video_ids(resp.text)

        if config.youtube_results:
            video_url = f"https://www.youtube.com/watch?v={config.youtube_results[0]}"
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
    scraped_videos = scrape_active_youtube_tab()
    if scraped_videos:
        config.youtube_results = scraped_videos
    elif not config.youtube_results:
        return "I couldn't find any videos on your screen. Make sure the YouTube tab is open and active!"
            
    if index >= len(config.youtube_results):
        return f"I only found {len(config.youtube_results)} videos on this page. Try a smaller number."

    video_url = f"https://www.youtube.com/watch?v={config.youtube_results[index]}"
    
    original_clipboard = pyperclip.paste()
    pyperclip.copy(video_url)
    
    print(f"[YOUTUBE] Playing in same tab: {video_url}")
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')
    
    try:
        pyperclip.copy(original_clipboard)
    except Exception:
        pass
        
    return f"Playing video number {index + 1} for you!"
