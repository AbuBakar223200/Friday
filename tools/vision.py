from PIL import ImageGrab
from google import genai
from core.brain import gemini_client, FRIDAY_SYSTEM_PROMPT

def analyze_screen(prompt: str) -> str:
    """Take a screenshot and pass it to Gemini Vision to answer a prompt."""
    if not gemini_client:
        return "My vision systems are offline because the Gemini API key is missing."
        
    print("[VISION] Capturing screen...")
    try:
        # Take screenshot directly into memory
        screenshot = ImageGrab.grab()
        
        print("[VISION] Analyzing image...")
        
        models = ["gemini-2.5-flash", "gemini-2.0-flash"]
        for model_name in models:
            try:
                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=[screenshot, prompt],
                    config=genai.types.GenerateContentConfig(
                        system_instruction=FRIDAY_SYSTEM_PROMPT,
                    ),
                )
                return response.text.strip()
            except Exception as e:
                print(f"[VISION] {model_name} failed: {e}")
                continue
                
        return "I encountered an error while trying to process the image on your screen."
    except Exception as e:
        return f"Sorry, I couldn't capture the screen: {e}"
