# Privacy

Last updated: 2026-05-22

Friday is being shaped as a Windows-first assistant for CSE students. Its most important privacy rule is that screen understanding must be explicit, temporary, and transparent.

## Screenshot Debugging

The command:

```text
Friday, debug my screen.
```

means Friday may capture the current screen once, send that screenshot to the configured AI provider, and use the result to explain the visible coding or setup problem.

Friday should use the screenshot to answer in this structure:

```text
Problem: ...
Cause: ...
Fix: ...
Permission: Should I ...?
```

## What Friday Should Do

- Capture the screen only after an explicit screen-debugging or screen-analysis request.
- Send the screenshot only to the configured AI provider for analysis.
- Explain what appears to be wrong before recommending action.
- Ask permission before running commands, editing files, installing packages, or changing system settings.
- Say when the screenshot is unreadable or does not clearly show a coding problem.

## What Friday Should Not Do

- Capture the screen continuously in the background.
- Save screenshots to disk.
- Keep a screenshot history.
- Upload unrelated project files as part of the screen-debugging flow.
- Run commands or edit files from screenshot analysis without explicit permission.
- Claim that an action happened unless it actually happened.

## Safe Permission Model

Friday follows this flow:

```text
See -> explain -> recommend -> ask permission -> act.
```

For the first CSE-student MVP, Friday should stop after asking permission. Future action features should repeat the exact command or change before performing it.

Example:

```text
Problem: Python cannot find the requests package.
Cause: The package is probably not installed in your active environment.
Fix: Run pip install requests in the same environment.
Permission: Should I run that command for you?
```

## Local File Boundaries

Friday follows the restrictions in `system_rules.md`:

- Do not search, modify, or expose files on `C:\`, except for the documented read-only Start Menu access used to discover installed apps.
- Limit local OS file searches to `D:\` and `E:\`.
- Do not write to the Start Menu directories used for app discovery.

Before public release, any feature that creates, edits, searches, or opens local files should be reviewed against these boundaries.

## Student Guidance

Before using screen debugging, close or hide anything sensitive that is visible on screen, such as passwords, private messages, API keys, personal documents, or account pages. Friday does not save the screenshot, but the visible screenshot is still sent to your selected AI provider for analysis.
