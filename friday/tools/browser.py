import subprocess
import webbrowser

from friday.settings import CHROME_PATH

def open_in_chrome(url: str) -> str:
    """
    Open a URL specifically in Google Chrome.
    """
    try:
        subprocess.Popen([CHROME_PATH, url])
        return f"Opening in Chrome for you."
    except FileNotFoundError:
        webbrowser.open(url)
        return f"Chrome not found, opening in your default browser."
