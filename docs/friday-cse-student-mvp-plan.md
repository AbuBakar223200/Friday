# Friday CSE Student MVP Plan

Last updated: 2026-05-22

This document captures the agreed product direction for Friday so a future agent can continue without repeating the design discussion. It is intentionally detailed and practical: product goal, rules, restrictions, architecture notes, implementation plan, prompts, and verification steps are all included.

## 1. Product Direction

Friday should first become a voice-first Windows assistant for CSE students.

The first public version should not try to help every possible user. It should focus on a painful daily problem for CSE students: understanding coding errors, terminal failures, project setup issues, and confusing screen output while they are learning.

Primary audience:

- CSE students using Windows.
- Students working in VS Code, terminals, browsers, and local project folders.
- Beginners who need simple explanations and safe next steps.

Secondary audience later:

- General students.
- Non-technical Windows users.
- Developers who want deeper automation.

The product identity for the MVP:

> Friday is a screen-aware coding and study assistant for CSE students. It sees what is on your screen only when asked, explains the problem simply, recommends a fix, and asks before taking action.

## 2. Killer Feature

The first killer feature is:

```text
Friday, debug my screen.
```

Expected demo:

1. A student has VS Code, a terminal error, a Python traceback, a failed install command, or a browser coding problem visible on screen.
2. The student says: "Friday, debug my screen."
3. Friday captures the current screen explicitly.
4. Friday sends the screenshot to the configured AI provider using the existing in-memory screenshot flow.
5. Friday explains the issue using a fixed response structure.
6. Friday asks before running commands or editing anything.

The response structure must be:

```text
Problem: ...
Cause: ...
Fix: ...
Permission: Should I ...?
```

Example:

```text
Problem: Python cannot find the requests package.
Cause: Your active environment probably does not have requests installed.
Fix: Run pip install requests in the same environment you use to run this file.
Permission: Should I run that command for you?
```

## 3. Locked Decisions From Grill Session

These decisions are already agreed and should not be reopened unless the user explicitly asks to change direction.

1. First target audience: CSE students.
2. First killer feature: screen-aware coding and debugging help.
3. Safety model: explain first, ask before action.
4. First app focus: VS Code plus terminal.
5. First demo workflow: "Friday, debug my screen."
6. First implementation path: reuse screenshot vision, not a VS Code extension.
7. First response format: Problem, Cause, Fix, Permission.
8. Privacy rule: explicit screenshot capture only, no saved screenshots, clear notice that the screenshot is sent to the configured AI provider.
9. Roadmap order: debug my screen, then easy setup, then permission-based actions.

## 4. Current Codebase Context

The project is currently a Python Windows desktop voice assistant.

Important files:

- `main.py`: small launcher that re-enters the virtual environment and calls the packaged app.
- `friday/app.py`: main voice loop, awake/sleep state transitions, command processing.
- `friday/settings.py`: environment-backed settings and configured local executable paths.
- `friday/state.py`: runtime state such as awake status, media status, current folder, and cached YouTube results.
- `friday/core/command_router.py`: routes spoken text to tools or the configured AI provider.
- `friday/core/brain.py`: general assistant prompt and AI brain entry point.
- `friday/core/ai_provider.py`: configurable provider layer for Gemini, OpenAI, Anthropic, OpenRouter, and Ollama.
- `friday/tools/vision.py`: captures the screen in memory and sends it to the configured vision provider.
- `friday/tools/system.py`: app launching, folder/file creation, local folder search.
- `friday/tools/system_control.py`: volume, brightness, lock, media controls.
- `friday/audio/stt.py`: speech-to-text.
- `friday/audio/tts.py`: text-to-speech.
- `system_rules.md`: security rules, especially drive access restrictions.
- `README.md`: public project overview.

Existing useful capability:

- `friday/tools/vision.py` uses `PIL.ImageGrab.grab()` to capture a screenshot in memory.
- The screenshot is sent directly to the configured AI provider.
- It does not need to save a screenshot file for the MVP.

Recommended implementation style:

- Keep the first change small.
- Do not build a VS Code extension yet.
- Add a dedicated coding/debugging path beside the existing generic screen analysis.

## 5. MVP Scope

Build only the first useful workflow:

```text
Friday, debug my screen.
```

In scope:

- Recognize commands like:
  - "debug my screen"
  - "debug this error"
  - "explain this error"
  - "what is wrong with my code"
  - "fix my screen" only as an explanation request, not direct action
- Capture current screen explicitly after one of those commands.
- Send screenshot to the configured AI provider with a coding-focused prompt.
- Return the four-part response:
  - Problem
  - Cause
  - Fix
  - Permission
- Keep the spoken answer concise enough for TTS.
- Ask before any action.

Out of scope for the first implementation:

- Directly editing files.
- Running commands automatically.
- Installing packages automatically.
- Building a VS Code extension.
- Persistent memory of screenshots.
- Background screen monitoring.
- Uploading files other than the explicit screenshot.
- Multi-step autonomous debugging.

## 6. Safety Rules

Friday must follow this rule:

```text
See -> explain -> recommend -> ask permission -> act.
```

For the first MVP, stop at asking permission. Do not implement the action step yet unless the user asks for the next phase.

Safety requirements:

- Never run a command from the debug screen feature without explicit user permission.
- Never edit code from the debug screen feature without explicit user permission.
- Never delete files as part of this feature.
- Never claim that a command was run unless it was actually run.
- If Friday is unsure, it must say so and ask the student to zoom in, select the terminal, or read the error aloud.
- If the screenshot is unreadable, Friday should say it cannot read the screen clearly.
- If a command is recommended, prefer the least risky command first.
- If multiple fixes are possible, explain the most likely one and mention uncertainty briefly.

Recommended wording before future actions:

```text
Should I run that command for you?
```

or:

```text
Should I open the file so you can review the change?
```

Do not use:

```text
I will fix it now.
```

unless the user has already given clear permission and the action implementation exists.

## 7. Privacy Rules

The screenshot debugging feature must be explicit and transparent.

Rules:

- Capture only when the user asks for screen debugging or screen explanation.
- Do not capture continuously in the background.
- Do not save screenshots to disk.
- Do not keep a screenshot history.
- Send the screenshot only to the configured AI provider.
- Add a clear privacy note to documentation before public release.

Recommended README privacy note:

```text
Screen debugging captures your current screen only when you explicitly ask Friday to debug or analyze it. The screenshot is sent to the configured AI provider for analysis and is not saved by Friday.
```

## 8. Existing System Restrictions

Follow `system_rules.md`.

Important restriction:

- Friday must not search, modify, or expose files on `C:\` except the documented read-only Start Menu access used to discover installed apps.
- Local OS file searches should be limited to `D:\` and `E:\`.
- The Start Menu exception is read-only:
  - `C:\ProgramData\Microsoft\Windows\Start Menu\Programs`
  - `%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs`

Important note for future agents:

- Some existing code uses Windows user folders such as Desktop. Before making Friday public, review file creation behavior against `system_rules.md` and make sure any write operation is safe, explicit, and user-approved.

## 9. Branding Restriction For Public Use

Friday is inspired by a popular fictional assistant, but a public project should avoid risky branding.

For public release:

- Avoid claiming "authentic Iron Man" behavior.
- Avoid using copyrighted franchise names in marketing.
- Keep the project name as Friday only if the user wants that, but avoid presenting it as an official or exact fictional replica.
- Consider changing the acronym "Female Replacement Intelligent Digital Assistant Youth" before public release because it may feel awkward or unprofessional for general users.

Recommended public positioning:

```text
Friday is a local-first voice assistant for CSE students on Windows.
```

## 10. Recommended Code Changes

Preferred implementation:

1. Add a new file:

```text
friday/tools/debug_screen.py
```

2. Add a function:

```python
def debug_screen(prompt: str) -> str:
    ...
```

3. Reuse the same core logic as `friday/tools/vision.py`:

- Check the configured AI provider.
- Capture screenshot with `ImageGrab.grab()`.
- Send `[screenshot, debug_prompt]` or an equivalent image request to the configured provider.
- Use configured provider model fallbacks where supported.
- Return a concise text response.
- Do not save the image.

4. Add command routing in `friday/core/command_router.py` before the generic screen route:

```python
if any(phrase in text for phrase in [
    "debug my screen",
    "debug this error",
    "explain this error",
    "what is wrong with my code",
    "what's wrong with my code",
    "fix my screen",
]):
    return debug_screen(text)
```

5. Keep generic screen analysis unchanged:

```python
if "screen" in text and any(w in text for w in ["what", "look", "read", "see"]):
    return analyze_screen(text)
```

Reason:

- Generic screen analysis remains useful for non-coding questions.
- Debug screen gets a stricter coding-focused prompt and response format.

## 11. Recommended Debug Prompt

Use a dedicated prompt instead of the general Friday prompt alone.

Suggested prompt content:

```text
You are Friday helping a CSE student debug what is visible on their screen.

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
```

The actual model call can still use `FRIDAY_SYSTEM_PROMPT`, but the screenshot prompt must include these stricter task rules.

## 12. Command Recognition Rules

Use simple phrase routing first. Do not over-engineer with a full intent classifier yet.

Recommended trigger phrases:

- "debug my screen"
- "debug this error"
- "explain this error"
- "explain my error"
- "what is wrong with my code"
- "what's wrong with my code"
- "what is wrong with this code"
- "why is my code not working"
- "fix my screen"
- "help me debug"

Routing priority:

1. Exit/shutdown commands.
2. Media controls.
3. Timers.
4. System controls.
5. Debug screen commands.
6. Generic screen analysis.
7. Time.
8. YouTube/media/app/file routes.
9. General AI chat.

Reason:

- Debug commands should be caught before generic AI chat.
- Debug commands should also be caught before generic screen analysis so they use the strict response structure.

## 13. Permission-Based Actions Roadmap

Do not implement this in the first MVP unless the user asks. This is the next phase after the response works well.

Future action types:

- Run safe terminal commands after permission.
- Install missing packages after permission.
- Open a file after permission.
- Create a project folder after permission.
- Generate a README after permission.
- Explain selected code after permission.
- Suggest Git commands after permission.

Future action rules:

- Always repeat the exact command before running it.
- Never run destructive commands by default.
- Never run `del`, `rmdir`, `Remove-Item`, `format`, `git reset --hard`, or similar destructive operations without a stronger confirmation.
- Prefer commands scoped to the current project.
- If Friday cannot identify the project folder safely, ask the user.
- Log what action was performed in terminal output.

Example future flow:

```text
Friday: Fix: Run pip install requests. Permission: Should I run that command for you?
User: yes.
Friday: I will run: pip install requests. Proceed?
User: proceed.
Friday runs the command.
```

## 14. Easy Setup Roadmap

After `debug my screen`, the next priority is making Friday easy for other CSE students to install.

Problems to solve:

- Python version confusion.
- Virtual environment setup.
- PyAudio installation failures.
- Missing AI provider key or local model.
- Missing microphone permission.
- Windows-only dependencies.
- Chrome path configuration.

Recommended future files:

```text
setup.bat
check_setup.py
.env.example
docs/install-for-students.md
```

`setup.bat` should:

- Check Python exists.
- Create `.venv`.
- Install dependencies.
- Tell the student how to create `.env`.
- Run `check_setup.py`.

`check_setup.py` should verify:

- Python version.
- Required packages import.
- Microphone access.
- TTS availability.
- AI provider key or local model presence.
- Screenshot capture availability.
- OS is Windows.

## 15. Documentation Roadmap

Update docs after the feature works.

Recommended README changes:

- Change the first pitch toward CSE students.
- Add `Friday, debug my screen` as the first feature.
- Add privacy note for screenshot analysis.
- Add safe-action promise: Friday asks before commands or edits.
- Add limitations:
  - Windows-first.
  - AI provider key or local model required.
  - Screenshot analysis depends on visible, readable text.

Recommended new docs:

- `docs/install-for-students.md`
- `docs/privacy.md`
- `docs/command-examples.md`

## 16. Definition Of Done For Debug Screen MVP

The feature is done when all of these are true:

- Saying or passing "debug my screen" routes to the new debug feature.
- The feature captures a screenshot only after the explicit command.
- The screenshot is not saved to disk.
- The response uses:
  - Problem
  - Cause
  - Fix
  - Permission
- The response is concise enough for spoken output.
- The feature handles missing AI provider configuration gracefully.
- The feature handles screenshot capture failure gracefully.
- The generic `analyze_screen` behavior still works.
- The app still starts without syntax errors.
- No C-drive search/write behavior is added.
- No command execution is added as part of the MVP.

## 17. Verification Checklist

Run these checks after implementation:

```powershell
python -m compileall .
```

Manual command-router checks can be done by calling `process_command()` in a Python session with safe mocked conditions, or by running the app and speaking:

```text
Friday, debug my screen.
Friday, explain this error.
Friday, what is on my screen?
```

Manual visual tests:

1. Open VS Code with a visible Python traceback.
2. Say "Friday, debug my screen."
3. Confirm the answer follows the four-part format.
4. Confirm Friday asks permission before action.
5. Open a non-coding screen.
6. Say "Friday, debug my screen."
7. Confirm Friday says no coding issue is visible or asks the student to show the error.

Failure cases to test:

- Missing provider key such as `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENROUTER_API_KEY`.
- Screen capture exception.
- Provider/model failure fallback.
- Unreadable screenshot.
- No coding problem visible.

## 18. Suggested Future Agent Workflow

When another agent picks this up:

1. Read this file first.
2. Read `system_rules.md`.
3. Read:
   - `friday/tools/vision.py`
   - `friday/core/command_router.py`
   - `friday/core/brain.py`
4. Implement `friday/tools/debug_screen.py`.
5. Add the route in `friday/core/command_router.py`.
6. Run `python -m compileall .`.
7. Manually test at least one visible coding error.
8. Update README privacy and MVP usage notes.

Suggested skills for future agents:

- `diagnose` if the feature fails or screenshot/provider calls behave unexpectedly.
- `tdd` if adding tests around command routing.
- `grill-me` if product direction changes.
- `handoff` only when transferring context to another session, not for this repo plan.

## 19. Open Questions

No blocking questions remain for the first MVP.

Questions for later:

1. Should Friday support non-Windows users in the future?
2. Should Friday keep using the name Friday for public release?
3. Should Friday eventually have a VS Code extension?
4. Should Friday store a local action log?
5. Should setup support offline mode or only API-powered mode?

These are not needed before implementing `debug my screen`.

## 20. Final Recommendation

Build this next:

```text
Friday, debug my screen.
```

Keep it small, safe, and impressive. A CSE student should immediately understand the value when Friday reads a visible error, explains it simply, gives the likely fix, and asks before doing anything.
