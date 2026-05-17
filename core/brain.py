from google import genai
from config import GEMINI_API_KEY

FRIDAY_SYSTEM_PROMPT = (
    "You are Friday, a highly intelligent and helpful AI voice assistant "
    "inspired by the AI from Iron Man. You are concise, witty, and professional. "
    "Keep your answers brief (2-3 sentences max) since they will be spoken aloud. "
    "Address the user respectfully. Do not use markdown, emojis, or special "
    "formatting -- respond in plain conversational English."
)

def _init_gemini():
    """
    Configure the Gemini API client using the google-genai SDK.
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
    """
    if gemini_client is None:
        return "I'm sorry, my AI brain isn't connected right now. Please set up the Gemini API key."

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
