# ADR-0001: Package Friday Application Source

Date: 2026-05-22

## Status

Accepted

## Context

Friday started as a small Python desktop assistant with `main.py`, `config.py`, `core/`, `audio/`, and `tools/` at the repository root. That shape was fine for the MVP, but the repository now has setup scripts, product docs, architecture docs, local agent tooling, and runtime source living side by side.

The main architectural friction was locality. The root did not clearly show which files were application implementation and which files were project support. `config.py` also mixed stable settings with mutable runtime state.

## Decision

Move the application implementation into a `friday/` package.

Keep `main.py` as a small launcher so students can still run:

```powershell
python main.py
```

Split the old root `config.py` into:

- `friday/settings.py` for environment-backed settings and local executable paths.
- `friday/state.py` for mutable runtime state.

Keep current submodules for now:

- `friday/audio/`
- `friday/core/`
- `friday/tools/`

Do not split command intents or provider adapters in this ADR. Those are follow-up refactors after this package move is verified.

## Consequences

- The repository root is easier to scan.
- New modules have an obvious home under `friday/`.
- Runtime state is no longer hidden among settings.
- The setup checker must read `friday/settings.py` instead of root `config.py`.
- Imports now use explicit `friday.*` package paths.

## Follow-Ups

- Split `friday/core/command_router.py` into intent modules once routing tests exist.
- Split `friday/core/ai_provider.py` into provider adapters once current fallback behaviour is covered.
- Decide whether `.agents/skills` should remain tracked in the public product repository.
