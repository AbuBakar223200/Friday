# Friday Domain Context

Last updated: 2026-05-22

Friday is a Windows-first voice assistant for CSE students. Its first useful workflow is screen-aware coding help: the student asks Friday to debug or explain what is visible, Friday captures the screen once, explains the likely problem, recommends a safe next step, and asks permission before any action.

## Product Terms

- **Student**: The primary user. A CSE student working on Windows in VS Code, terminals, browsers, and local project folders.
- **Screen Debugging**: The explicit workflow triggered by commands such as "debug my screen" or "explain this error." Friday captures the current screen in memory and asks the configured vision provider to explain visible coding or setup problems.
- **Generic Screen Analysis**: Non-debugging screen understanding, such as reading visible text or describing the current screen.
- **Safe Permission Model**: Friday follows `See -> explain -> recommend -> ask permission -> act`. The current MVP stops at asking permission.
- **AI Provider**: The configured text or vision model backend. Supported providers are Gemini, OpenAI, Anthropic, OpenRouter, and Ollama.
- **Desktop Adapter**: Code that talks to Windows, Chrome, VLC, screen capture, audio devices, brightness controls, file browsing, or media keys.
- **Runtime State**: Mutable in-process state such as awake/asleep status, current media status, cached YouTube results, and the active folder.

## Module Map

- `main.py`: Student-friendly launcher that re-enters the local virtual environment and starts the packaged app.
- `friday/app.py`: Main voice loop and awake/asleep flow.
- `friday/settings.py`: Environment-backed settings and local executable paths.
- `friday/state.py`: Runtime state kept out of settings.
- `friday/audio/`: Speech-to-text and text-to-speech adapters.
- `friday/core/`: Command routing, assistant prompt, and AI provider interface.
- `friday/tools/`: Desktop, browser, media, timer, screen, and system adapters.

## Architectural Direction

- Keep the root small: launchers, setup scripts, docs, and project metadata only.
- Keep application implementation under `friday/`.
- Keep settings and runtime state separate.
- Keep the CSE-student debugging workflow visible as Friday grows beyond MVP.
- Prefer small, testable modules around command routing before adding permission-based actions.
