# Design

## Context

Greenfield application: the repository holds only OpenSpec/Claude configuration, `.gitignore` and `.claude/CLAUDE.md`. Git state (inspected): working branch `dev` tracking `origin/dev` (GitHub `Raghavi549/AI-powered-PDF-Chatbot`), one commit `8d09a2e` pushed, working tree clean apart from this change's planning files. This change adds files but does not commit them. Machine: Windows 11, Python 3.12.7 (also an older Python 3.7 installed), Node 22.16, npm 10.9.2, OpenSpec 1.14.1. Single local user, single backend worker, backend must not be reachable from the network (see proposal.md for scope and success criteria).

## Goals / Non-Goals

**Goals:**
- A minimal, runnable frontend-backend pair that later changes extend without restructuring.
- Configuration and secret handling established correctly once, before any feature reads a secret.
- Early, recorded evidence of whether this machine can install and use the planned RAG dependencies.

**Non-Goals:**
- No directory layering (routers, services, repositories) beyond what C1 needs. C2 introduces structure when there is something to put in it.
- No production concerns: Docker, CI, HTTPS, authentication, process supervision.
- No choice of embedding model.

## Decisions

### 1. Repository layout

```
 backend/
   app/__init__.py
   app/config.py          Settings (env loading + validation)
   app/main.py            create_app(), GET /api/health, CORS
   tests/test_health.py
   requirements.txt       runtime pins
   requirements-dev.txt   -r requirements.txt + pytest + httpx
   .env.example
 frontend/
   (Vite React template, trimmed)
   src/api.js             getHealth() - the only place that calls the backend
   src/App.jsx            status display
   .env.example
 README.md
```

`backend/` and `frontend/` match the layout proposed in `.claude/CLAUDE.md`. Two small modules in the backend, one API module in the frontend; nothing else.

### 2. Backend configuration: pydantic-settings

Settings are a typed class loading from environment variables and an untracked `backend/.env`:

| Variable | Default | Notes |
|---|---|---|
| `GROQ_API_KEY` | unset | Held as a secret type so it cannot appear in `repr`/logs. Stripped; blank means not configured |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Validation rejects `*` and fails startup with a message naming the setting |

*Why this over `os.environ` + `python-dotenv`:* validation (wildcard rejection) and secret-safe types come built in, and FastAPI users already depend on Pydantic. *Cost:* one extra small dependency. Only variables C1 actually reads are defined; later changes add their own.

### 3. App construction: `create_app(settings=None)`

A small factory builds the app from a settings object, with a module-level `app = create_app()` for the server. This exists solely so tests can build an app with different keys and origins without mutating process state. No other abstraction is introduced.

### 4. Health endpoint contract

```
GET /api/health
200 {"status": "ok", "groq_configured": true|false}
```

Synchronous, constant-time, no I/O, no external calls (so it never costs a Groq request or fails because the network is down). Other methods return 405 via normal routing. The path is declared directly in `main.py`; the `/api` prefix leaves room for later endpoints without a router split.

### 5. CORS and network exposure

- CORS middleware allows exactly the configured origin, `GET` (plus automatic preflight handling), no credentials, minimal headers. Later changes that add `POST` extend this list deliberately.
- Run command: `uvicorn app.main:app --host 127.0.0.1 --port 8000` from `backend/`, with `--reload` documented for development. The host is stated explicitly even though it is uvicorn's default, so the security property is visible in the docs and does not rely on a default.
- CORS only constrains browsers; loopback binding is what keeps other machines out. Both are required, tested separately.

### 6. Frontend: Vite + React, plain JavaScript

Standard Vite React template with the demo content removed.
- **Language:** JavaScript, not TypeScript. For a 10-day learning project the typing overhead outweighs the benefit on a single-endpoint client; the API surface is small enough that the contract is documented here. Accepted by the user.
- **Port:** dev server pinned to port 5173 with `strictPort`, so Vite fails loudly instead of silently moving to 5174 and tripping the CORS allowlist.
- **Origin:** the app must be opened at `http://localhost:5173`. `127.0.0.1:5173` is a different origin and would be blocked. The README states this.
- **Base URL:** `import.meta.env.VITE_API_BASE_URL`, default `http://127.0.0.1:8000`.
- **Health fetch:** `fetch` with an `AbortController` 5-second timeout. States: loading, connected, connected-without-key, error. Non-2xx, network error, timeout, invalid JSON, or missing fields all land in error. No retry logic; reloading the page re-checks.

Data flow:

```
 Browser (http://localhost:5173)
    |  GET /api/health   (Origin: http://localhost:5173)
    v
 FastAPI on 127.0.0.1:8000
    |  CORS check --> allowed origin only
    |  read Settings (no I/O)
    v
 {"status":"ok","groq_configured":bool}  --> UI state
```

### 7. Testing

`pytest` with FastAPI's test client (needs `httpx`) in `requirements-dev.txt`. Covers: health shape with key, without key and with whitespace key; key value absent from response and captured logs; CORS allow, deny and preflight; wildcard origin rejected; `POST` returns 405. Run via `python -m pytest` from `backend/` using the venv's interpreter. No frontend test framework: frontend criteria are verified manually (backend up, stopped, slow, malformed), which suits a one-page shell.

### 8. Windows-friendly commands

The README invokes the venv interpreter directly (`backend\.venv\Scripts\python.exe -m ...`) instead of relying on activation, avoiding PowerShell execution-policy problems and PowerShell vs Git Bash differences. The venv is created with the explicit launcher form `py -3.12 -m venv`, so the older Python 3.7 cannot be picked up by accident.

### 9. Dependency pinning

Backend requirements are exact pins chosen at implementation time from versions available on the package index (preferring versions at least two weeks old), recorded in `requirements.txt`. The frontend commits `package-lock.json`. No RAG libraries are added (spec: `dev-environment`).

### 10. Environment smoke checks (verification only)

Run once, during implementation, and recorded in `tasks.md` as passed, failed or pending with a short evidence line.

| Check | Method | Notes |
|---|---|---|
| Library install and import | Temporary venv created **outside the repo** (session temp directory); install `pymupdf`, `faiss-cpu`, `sentence-transformers`; import each and print versions | On Windows the default PyPI PyTorch wheel is CPU-only. Several hundred MB expected |
| Hugging Face connectivity | In the same venv, load one small candidate model (`sentence-transformers/all-MiniLM-L6-v2`) and encode one sentence, with the cache directory (`HF_HOME`) set to the temp location | Proves the download path only. Not a model selection; C3 decides |
| Groq connectivity | Only if `GROQ_API_KEY` is already present in the environment: one authenticated read-only request to Groq's model-list endpoint through a short script that reads the key from the environment and prints only the HTTP status | No Groq client library installed. Key is never printed, written or passed on a command line. If no key: pending |

Downstream impact of a non-passing result (recorded with each failed or pending item, with a proposed mitigation):

| Item | Could block | Typical mitigation |
|---|---|---|
| PyMuPDF | C2 ingestion | Alternative wheel/version, or confirm the exact error before C2 starts |
| faiss-cpu | C3 retrieval | Different version or package source; confirm Python 3.12 wheel availability |
| sentence-transformers | C3 retrieval | Pin a compatible PyTorch/Transformers pair |
| Hugging Face download | C3 retrieval | Manual model download to a local folder and load from path; document in README |
| Groq | C4 chat (and C5b) | Obtain a key, check proxy/firewall; does not block C2 or C3 |

Rules: failed or pending results never block completing C1 (the purpose is early visibility, not a gate), but each is reported to you together with its downstream impact; the temporary environment and caches are deleted afterwards, or their location is recorded if deletion fails; the repository must remain free of venvs, models and caches from these checks.

### 11. Clean-checkout verification

A genuine clone of `origin/dev` contains only the baseline commit, not C1's uncommitted files, so a clone alone cannot prove the README works. Verification therefore runs in two stages in a temporary directory outside the repository:

1. **Genuine clone** of `origin/dev` to confirm the baseline is clean (no `.env`, venv or `node_modules`; ignored files are not needed).
2. **Simulated post-commit state:** overlay the files from `git ls-files --cached --others --exclude-standard` (exactly the set `git add -A` would stage, ignored files excluded) onto the clone, then follow the README literally.

Limitations to document in the result: it does not test what GitHub will actually hold after a future commit and push, line-ending conversion, or file modes. After you choose to commit and push, repeating stage 1 as a pure clone is the definitive check. No commit or push is made by this change.

## Risks / Trade-offs

- **Corporate network blocks PyPI, npm, Hugging Face or Groq** → the smoke checks and setup surface this on day 1. Results are recorded, and manual-download notes feed C3 and the README.
- **Wrong Python picked up (3.7 present)** → explicit `py -3.12`, direct interpreter invocation, version stated in README.
- **Origin mismatch (`localhost` vs `127.0.0.1`) or Vite changing port** → `strictPort`, README note, default origin matches Vite's default.
- **Large PyTorch download slows the smoke checks** → run it once, in a temp location, in the background of other C1 work.
- **CORS list too narrow for later changes** (`GET` only now) → each later change that adds methods updates it deliberately and re-tests; considered preferable to starting permissive.
- **A passing smoke check does not guarantee acceptable embedding speed or memory** → C3's evaluation, not C1, measures that.
- **JavaScript instead of TypeScript** → accepted trade of type safety for lower friction; switching later costs more once the UI grows.
- **Simulated clean checkout is weaker than a real clone** → two-stage verification (decision 11) with limitations documented; definitive re-check after the user commits and pushes.

## Open Questions

- Exact dependency versions are chosen during implementation and recorded; they do not affect specs or the task breakdown.
