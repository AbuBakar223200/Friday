from PIL import ImageGrab

from friday.core.ai_provider import generate_vision, is_vision_configured
from friday.core.brain import FRIDAY_SYSTEM_PROMPT

def analyze_screen(prompt: str) -> str:
    """Take a screenshot and pass it to the configured vision provider."""
    if not is_vision_configured():
        return "My vision systems are offline because no vision-capable AI provider is configured."

    print("[VISION] Capturing screen...")
    try:
        # Take screenshot directly into memory
        screenshot = ImageGrab.grab()

        print("[VISION] Analyzing image...")
        return generate_vision(prompt, screenshot, FRIDAY_SYSTEM_PROMPT)
    except Exception as e:
        return f"Sorry, I couldn't capture the screen: {e}"
