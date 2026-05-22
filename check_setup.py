import ast
import contextlib
import importlib
import io
import os
import platform
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
SETTINGS_PATH = ROOT / "friday" / "settings.py"
PROVIDER_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}
PROVIDER_ORDER = ("gemini", "openai", "anthropic", "openrouter", "ollama")
REQUIREMENTS = [
    ("edge-tts", "edge_tts"),
    ("pygame", "pygame"),
    ("SpeechRecognition", "speech_recognition"),
    ("google-genai", "google.genai"),
    ("pyaudio", "pyaudio"),
    ("python-dotenv", "dotenv"),
    ("pyautogui", "pyautogui"),
    ("pyperclip", "pyperclip"),
    ("screen-brightness-control", "screen_brightness_control"),
    ("pycaw", "pycaw"),
    ("comtypes", "comtypes"),
    ("pillow", "PIL"),
]


class CheckReport:
    def __init__(self) -> None:
        self.errors = 0
        self.warnings = 0

    def ok(self, message: str) -> None:
        print(f"[OK]   {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"[WARN] {message}")

    def fail(self, message: str) -> None:
        self.errors += 1
        print(f"[FAIL] {message}")


def read_dotenv_value(key: str) -> str:
    if not ENV_PATH.exists():
        return ""

    try:
        for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() == key:
                return value.strip().strip('"').strip("'")
    except OSError:
        return ""

    return ""


def read_setting(key: str) -> str:
    return os.environ.get(key, "").strip() or read_dotenv_value(key)


def read_settings_constant(name: str) -> str:
    if not SETTINGS_PATH.exists():
        return ""

    try:
        tree = ast.parse(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ""

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    try:
                        value = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        return ""
                    return value if isinstance(value, str) else ""
    return ""


def check_windows(report: CheckReport) -> None:
    system = platform.system()
    if system == "Windows":
        report.ok(f"Windows detected ({platform.platform()})")
    else:
        report.fail(f"Friday is Windows-first, but this machine reports {system or 'unknown OS'}")


def check_python(report: CheckReport) -> None:
    version = sys.version_info
    readable = f"{version.major}.{version.minor}.{version.micro}"
    if version >= (3, 10):
        report.ok(f"Python {readable} is supported")
    else:
        report.fail(f"Python {readable} is too old. Install Python 3.10 or newer.")


def check_imports(report: CheckReport) -> None:
    missing = []
    for package_name, import_name in REQUIREMENTS:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                importlib.import_module(import_name)
        except Exception as exc:
            missing.append(package_name)
            report.fail(f"Cannot import {package_name} ({exc.__class__.__name__})")
        else:
            report.ok(f"Imported {package_name}")

    if missing:
        report.warn('Install missing packages with: ".venv\\Scripts\\python.exe" -m pip install -r requirements.txt')


def is_real_secret(value: str) -> bool:
    placeholder_values = {
        "",
        "your_gemini_api_key_here",
        "your_openai_api_key_here",
        "your_anthropic_api_key_here",
        "your_openrouter_api_key_here",
        "paste_your_key_here",
    }
    return value.strip() not in placeholder_values


def provider_is_configured(provider: str) -> bool:
    if provider == "ollama":
        return bool(read_setting("OLLAMA_MODEL"))

    key_name = PROVIDER_KEYS.get(provider)
    return bool(key_name and is_real_secret(read_setting(key_name)))


def check_ai_provider(report: CheckReport) -> None:
    requested = (read_setting("AI_PROVIDER") or "auto").lower()

    if ENV_PATH.exists():
        report.ok(".env file exists")
    else:
        report.warn(".env file is missing. Copy .env.example to .env and add one provider key.")

    if requested == "auto":
        configured = [provider for provider in PROVIDER_ORDER if provider_is_configured(provider)]
        if configured:
            report.ok(f"AI provider auto-select will use {configured[0]}")
            if len(configured) > 1:
                report.warn(f"Multiple providers are configured; auto mode prefers {configured[0]}")
        else:
            report.fail("No AI provider is configured. Add a provider key or set OLLAMA_MODEL.")
    elif requested in PROVIDER_ORDER:
        if provider_is_configured(requested):
            report.ok(f"AI_PROVIDER={requested} is configured")
        else:
            report.fail(f"AI_PROVIDER={requested} is selected, but its key or model is missing.")
    else:
        report.fail(f"AI_PROVIDER={requested} is not supported. Use auto, gemini, openai, anthropic, openrouter, or ollama.")


def check_microphone(report: CheckReport) -> None:
    try:
        import speech_recognition as sr

        names = sr.Microphone.list_microphone_names()
        if names:
            report.ok(f"Microphone devices visible ({len(names)} found)")
            configured_index = read_setting("MICROPHONE_DEVICE_INDEX")
            if configured_index:
                try:
                    index = int(configured_index)
                except ValueError:
                    report.warn(f"MICROPHONE_DEVICE_INDEX is not a number: {configured_index}")
                else:
                    if 0 <= index < len(names):
                        report.ok(f"MICROPHONE_DEVICE_INDEX={index} selects: {names[index]}")
                    else:
                        report.warn(
                            f"MICROPHONE_DEVICE_INDEX={index} is outside the available range 0-{len(names) - 1}"
                        )
            else:
                report.warn("MICROPHONE_DEVICE_INDEX is not set; Windows will choose the default input device.")
                print("       Available microphone indexes:")
                for index, name in enumerate(names):
                    print(f"       {index}: {name}")
        else:
            report.warn("No microphone devices were reported. Check Windows microphone privacy settings.")
    except Exception as exc:
        report.warn(f"Could not verify microphone availability ({exc.__class__.__name__}: {exc})")


def check_tts(report: CheckReport) -> None:
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            import edge_tts  # noqa: F401
            import pygame  # noqa: F401
    except Exception as exc:
        report.warn(f"Could not verify TTS packages ({exc.__class__.__name__}: {exc})")
    else:
        report.ok("TTS packages are importable")


def check_screenshot(report: CheckReport) -> None:
    try:
        from PIL import ImageGrab

        image = ImageGrab.grab(bbox=(0, 0, 1, 1))
        if image.size == (1, 1):
            report.ok("Screenshot capture is available")
        else:
            report.warn(f"Screenshot capture returned an unexpected size: {image.size}")
    except Exception as exc:
        report.warn(f"Could not verify screenshot capture ({exc.__class__.__name__}: {exc})")


def check_chrome(report: CheckReport) -> None:
    chrome_path = read_settings_constant("CHROME_PATH")
    if not chrome_path:
        report.warn("CHROME_PATH was not found in friday/settings.py")
        return

    report.ok("CHROME_PATH is configured in friday/settings.py")
    if chrome_path.lower().startswith("c:\\"):
        report.warn("CHROME_PATH points to C:\\; this checker does not probe C:\\ because of Friday system rules.")
    elif Path(chrome_path).exists():
        report.ok("Configured Chrome path exists")
    else:
        report.warn(f"Configured Chrome path was not found: {chrome_path}")

    chrome_on_path = shutil.which("chrome") or shutil.which("chrome.exe")
    if chrome_on_path:
        report.ok("Chrome is also available on PATH")
    else:
        report.warn("Chrome was not found on PATH. Friday will use CHROME_PATH from friday/settings.py.")


def main() -> int:
    report = CheckReport()
    print("Friday setup checker")
    print("====================")
    print()

    check_windows(report)
    check_python(report)
    print()
    check_imports(report)
    print()
    check_ai_provider(report)
    check_microphone(report)
    check_tts(report)
    check_screenshot(report)
    check_chrome(report)
    print()

    if report.errors:
        print(f"Result: {report.errors} blocking issue(s), {report.warnings} warning(s).")
        return 1

    if report.warnings:
        print(f"Result: usable with {report.warnings} warning(s).")
        return 0

    print("Result: Friday setup looks ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
