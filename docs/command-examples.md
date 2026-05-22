# Command Examples

Last updated: 2026-05-22

These examples describe the CSE-student MVP behavior Friday should support or move toward. The safest pattern is: explain first, then ask permission before any action.

## Debugging A Visible Error

```text
Student: Friday, debug my screen.
Friday: Problem: Python cannot find the requests package.
Friday: Cause: The package is probably not installed in your active environment.
Friday: Fix: Run pip install requests in the same environment you use to run this file.
Friday: Permission: Should I run that command for you?
```

```text
Student: Friday, explain this error.
Friday: Problem: The terminal shows a module import error.
Friday: Cause: The dependency may be missing or the wrong virtual environment may be active.
Friday: Fix: Check the active environment, then install the missing package there.
Friday: Permission: Should I help you check the environment?
```

```text
Student: Friday, what is wrong with my code?
Friday: Problem: I can see a syntax error near the highlighted line.
Friday: Cause: A bracket, quote, or colon may be missing.
Friday: Fix: Review the line shown in the traceback and the line above it.
Friday: Permission: Should I help inspect the file with you?
```

## When The Screen Is Not Clear

```text
Student: Friday, debug my screen.
Friday: Problem: I cannot read the error clearly from this screenshot.
Friday: Cause: The text is too small or the terminal is not fully visible.
Friday: Fix: Zoom in or select the terminal window so the full error is visible.
Friday: Permission: Should I try again after you adjust the screen?
```

```text
Student: Friday, debug my screen.
Friday: Problem: I do not see a coding error on the screen.
Friday: Cause: The visible window does not show a traceback, terminal failure, or code problem.
Friday: Fix: Open the error, terminal, or VS Code problem panel.
Friday: Permission: Should I analyze the screen again after that?
```

## Generic Screen Analysis

```text
Student: Friday, what is on my screen?
Friday: I can see a browser window with a coding tutorial open.
```

```text
Student: Friday, read the error message on my screen.
Friday: The visible error says Python cannot open the file because the path was not found.
```

## Safe Local Assistance

```text
Student: Friday, open YouTube.
Friday: Opening YouTube.
```

```text
Student: Friday, set volume to 50 percent.
Friday: Setting volume to 50 percent.
```

```text
Student: Friday, lock my PC.
Friday: Locking your PC.
```

## Future Permission-Based Actions

These examples describe the intended future behavior once action execution is implemented for debugging.

```text
Friday: Fix: Run pip install requests.
Friday: Permission: Should I run that command for you?
Student: Yes.
Friday: I will run: pip install requests. Proceed?
Student: Proceed.
Friday: Running the command now.
```

```text
Friday: Fix: Open requirements.txt and check whether flask is listed.
Friday: Permission: Should I open the file so you can review it?
```

## Commands To Avoid Without Strong Confirmation

Friday should not recommend or run destructive commands casually, especially:

- `del`
- `rmdir`
- `Remove-Item`
- `format`
- `git reset --hard`
- Commands that delete project folders, wipe data, or overwrite user work.

When unsure, Friday should ask the student to confirm the project folder, read the error aloud, or show the terminal more clearly.
