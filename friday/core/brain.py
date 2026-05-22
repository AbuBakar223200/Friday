from friday.core.ai_provider import describe_ai_status, generate_text, is_ai_configured

FRIDAY_SYSTEM_PROMPT = (
    "You are Friday, a highly intelligent and helpful AI voice assistant "
    "for CSE students. You are concise, witty, and professional. "
    "Keep your answers brief (2-3 sentences max) since they will be spoken aloud. "
    "Address the user respectfully. Do not use markdown, emojis, or special "
    "formatting -- respond in plain conversational English."
)


print(f"[AI] {describe_ai_status()}")


def ai_ready() -> bool:
    return is_ai_configured()


def ask_ai(prompt: str) -> str:
    """
    Send a prompt to the configured AI provider and return the response text.
    """
    return generate_text(prompt, FRIDAY_SYSTEM_PROMPT)


def ask_gemini(prompt: str) -> str:
    """Backward-compatible alias for older command routing."""
    return ask_ai(prompt)
