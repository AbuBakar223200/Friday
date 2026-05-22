# Install Friday For Students

Friday is a Windows-first voice assistant for CSE students. This guide gets you from a fresh download to a working local setup.

## Requirements

- Windows 10 or Windows 11.
- Python 3.10 or newer.
- A microphone.
- Google Chrome, if you want Friday to open browser links in Chrome.
- At least one AI provider key, such as Gemini, OpenAI, Anthropic, OpenRouter, or a local Ollama model.

## Quick Setup

1. Open PowerShell or Command Prompt in the Friday project folder.
2. Run:

```bat
setup.bat
```

The setup script creates `.venv`, installs the Python packages from `requirements.txt`, creates `.env` from `.env.example` if needed, and runs the setup checker.

## Add Your AI Provider

For Gemini-only use, open `.env` and replace the example value:

```text
AI_PROVIDER=auto
GEMINI_API_KEY=your_gemini_api_key_here
```

Use your real key after the equals sign. Do not share your `.env` file and do not paste keys into screenshots, chat messages, or Git commits.

Friday also supports:

```text
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key_here
```

```text
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here
```

```text
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_key_here
```

```text
AI_PROVIDER=ollama
OLLAMA_MODEL=llava
```

More provider examples are in `docs/ai-providers.md`.

After editing `.env`, run:

```bat
.venv\Scripts\python.exe check_setup.py
```

## Start Friday

When the checker looks good, start the assistant:

```bat
.venv\Scripts\python.exe main.py
```

## What The Checker Verifies

`check_setup.py` checks:

- Windows is the current OS.
- Python is version 3.10 or newer.
- Required packages can be imported.
- `.env` exists and at least one AI provider is configured without printing any key.
- A microphone is visible to Python.
- TTS packages are importable.
- Screenshot capture works.
- Chrome configuration is present.

Some checks are best-effort. Windows privacy settings, display permissions, audio drivers, and school-managed laptops can block microphone or screenshot access even when packages are installed correctly.

## Common Problems

### Python Is Not Found

Install Python from the official Windows download page and enable "Add python.exe to PATH" during installation. Then close and reopen PowerShell before running `setup.bat` again.

### PyAudio Fails To Install

PyAudio can be the hardest package on Windows. First try running `setup.bat` again from a fresh terminal. If it still fails, try:

```bat
".venv\Scripts\python.exe" -m pip install pipwin
".venv\Scripts\python.exe" -m pipwin install pyaudio
```

Then run:

```bat
.venv\Scripts\python.exe check_setup.py
```

### AI Provider Is Missing

Make sure `.env` exists in the project folder and contains at least one provider setup, such as:

```text
AI_PROVIDER=auto
GEMINI_API_KEY=your_real_key_here
```

The checker only reports whether a provider is configured. It never prints secrets.

### Microphone Is Not Found

Open Windows Settings, search for "Microphone privacy settings", and allow desktop apps to access the microphone. Then reconnect your headset or microphone and rerun the checker.

### Screenshot Check Warns

Friday's screen debugging depends on visible screen capture. If the checker warns, close screen recording blockers, remote desktop restrictions, or school device privacy tools, then rerun the checker.

### Friday Cuts Off My Command

Friday listens until it detects a pause or reaches `PHRASE_TIME_LIMIT`. If it starts processing before you finish speaking, increase these values in `.env`:

```text
PHRASE_TIME_LIMIT=30
WAKE_PHRASE_TIME_LIMIT=8
PAUSE_THRESHOLD=1.6
AMBIENT_NOISE_DURATION=0.8
```

Increase `PAUSE_THRESHOLD` to tolerate longer pauses between words. Increase `PHRASE_TIME_LIMIT` if your command itself is long.

If Friday hears the wrong words, first make sure Windows is using the correct microphone. Then run:

```bat
.venv\Scripts\python.exe check_setup.py
```

If needed, set these in `.env`:

```text
MICROPHONE_DEVICE_INDEX=0
STT_LANGUAGE=en-US
DYNAMIC_ENERGY_THRESHOLD=true
ENERGY_THRESHOLD=
```

Use the microphone index printed by the setup checker. For English spoken in South Asia, `en-IN` can work better than `en-US`; for Bangla, try `bn-BD`.

### Chrome Warning

Friday reads `CHROME_PATH` from `friday/settings.py`. If Chrome is installed somewhere else, update that value. The setup checker does not broadly search the C drive because Friday's system rules restrict C-drive access.

## Privacy Note

Screen debugging should only happen after you explicitly ask Friday to analyze or debug your screen. Screenshots are used for the configured AI provider request and should not be saved by Friday.
