from PIL import ImageGrab

from friday.core.ai_provider import generate_vision, is_vision_configured


DEBUG_SCREEN_SYSTEM_PROMPT = (
    "You are Friday, a careful voice assistant for CSE students. "
    "Return exactly four concise plain-text sections headed Problem, Cause, Fix, and Permission. "
    "Explain first, recommend the safest next step, and ask before any command, file edit, install, or system action."
)


DEBUG_SCREEN_PROMPT = """You are Friday helping a CSE student debug what is visible on their screen.

Analyze the screenshot and the user's request. Focus on coding errors, terminal output, VS Code problems, dependency issues, path issues, syntax errors, runtime errors, Git errors, package installation errors, and project setup problems.

Return exactly four short sections in plain spoken English:

Problem: Explain what the visible issue means.
Cause: Explain the most likely reason.
Fix: Give the safest next command or code change.
Permission: Ask whether Friday should help apply the fix.

Rules:
- Be concise because the response will be spoken aloud.
- Do not use markdown bullets.
- Do not invent text that is not visible.
- If the screenshot is unreadable, say that clearly.
- If there is no coding problem visible, say what you can see and ask the student to show the error.
- Do not say you changed files or ran commands.
- Do not recommend destructive commands.
- Ask permission before any command, install, file edit, or system action.
"""


def _ensure_debug_format(text: str) -> str:
    """Keep spoken debug output in the agreed four-part shape."""
    required_headings = ["problem:", "cause:", "fix:", "permission:"]
    normalized = text.lower()
    if all(heading in normalized for heading in required_headings):
        return text.strip()

    return (
        "Problem: I analyzed the screen, but the response did not come back in the required debug format.\n"
        "Cause: The model did not include all four sections clearly.\n"
        "Fix: Try again with the full error visible, or ask me to read the screen first.\n"
        "Permission: Should I try debugging the screen again?"
    )


def debug_screen(prompt: str) -> str:
    """Capture the current screen in memory and ask the AI provider for coding-focused help."""
    if not is_vision_configured():
        return "My screen debugging is offline because no vision-capable AI provider is configured."

    print("[DEBUG_SCREEN] Capturing screen for explicit debug request...")
    try:
        screenshot = ImageGrab.grab()
    except Exception as e:
        return f"Sorry, I couldn't capture the screen: {e}"

    print("[DEBUG_SCREEN] Analyzing visible coding issue...")
    user_prompt = (
        f"{DEBUG_SCREEN_PROMPT}\n"
        f"User request: {prompt}\n"
        "Remember: explain only, recommend the safest next step, and ask permission before any action."
    )

    response = generate_vision(user_prompt, screenshot, DEBUG_SCREEN_SYSTEM_PROMPT)
    return _ensure_debug_format(response)
