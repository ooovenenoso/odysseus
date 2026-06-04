# Agent Guide

This file gives coding agents a compact map of the repository and the rules that keep changes reviewable. It complements, but does not replace, `README.md`, `CONTRIBUTING.md`, and `SECURITY.md`.

## Contribution Rules

- Read `CONTRIBUTING.md`, this file, and the pull request template before changing code.
- Keep one issue, one focused branch, and one focused pull request. Avoid broad rewrites, formatting-only churn, and unrelated cleanup.
- Search open issues and pull requests before starting. If the change is large, speculative, or product-facing, open or use an issue first.
- For UI work, reuse the existing visual language: CSS variables, existing component patterns, dark-theme defaults, and inline SVG/plain text instead of emoji.
- Do not commit secrets, tokens, private logs, database contents, or user data. Follow `SECURITY.md` for vulnerabilities.
- When a change affects setup, ports, environment variables, provider support, or documented behavior, update `README.md` and this guide in the same pull request.

## Repository Map

- `app.py` wires the FastAPI app, route modules, middleware, startup work, and static assets.
- `routes/` contains HTTP route modules for chat, documents, email, calendar, research, settings, uploads, and related UI/API surfaces.
- `services/` contains domain services such as search, memory, speech, research, email, calendar, and background helpers.
- `src/` contains compatibility modules and lower-level utilities used by services, routes, and command-line helpers.
- `mcp_servers/` contains MCP server integrations exposed to agents and external tools.
- `static/` contains browser assets; `static/js/` modules should stay narrow and reuse existing DOM/CSS patterns.
- `docs/` contains user-facing guides, screenshots, and the landing page assets.
- `tests/` contains the regression suite. Add the smallest focused test that covers a bug when practical.
- `docker/`, `Dockerfile`, and `docker-compose*.yml` define the containerized deployment path.
- `scripts/`, `setup.py`, `launch-windows.ps1`, and `start-macos.sh` cover setup, maintenance, and platform launch flows.

## Code Change Guidelines

- Prefer surgical fixes over new abstractions. If a helper already exists, reuse it instead of creating a parallel implementation.
- Preserve owner/user scoping when resolving model endpoints, files, sessions, memories, settings, email accounts, calendars, and background jobs.
- Treat file paths from users, tools, MCP servers, and archives as untrusted; normalize and confine them before reading or writing.
- Keep persisted data migrations explicit and backward-compatible. If a schema or settings shape changes, add the matching migration/default handling.
- For provider/model changes, handle unavailable backends and malformed provider responses gracefully instead of crashing the request path.
- For background work, avoid silent failures: log actionable errors and keep user-visible status consistent with the actual state.

## Verification Expectations

Run the smallest relevant checks for the touched surface and include the exact commands in the pull request body. Common examples:

```bash
python -m pytest
python -m py_compile app.py routes/*.py src/*.py
node --check static/js/<file-you-changed>.js
```

For docs-only changes, inspect the rendered Markdown when practical and at least run `git diff --check` to catch whitespace problems.

## Pull Request Notes

Use the repository pull request template. Include a linked issue, the type of change, focused reviewer steps under `How to Test`, and screenshots/clips for anything visual. Be explicit about what the pull request does not change when the surrounding subsystem is larger than the fix.