# Proposal

## Why

The repository has OpenSpec and Claude Code configuration but no application. Every later change (ingestion, retrieval, chat) needs a running React frontend, a FastAPI backend, safe configuration handling and a known-good local environment. Establishing these first lets later changes focus on RAG behavior. It also surfaces environment risks (Windows, Hugging Face downloads on a corporate network, Groq reachability) on day 1 instead of mid-project, on a 10-day timeline.

## What Changes

- Add a FastAPI backend skeleton with a `GET /api/health` endpoint that reports service status and whether a Groq API key is configured (never the key itself).
- Add environment-based configuration for the backend (Groq key, allowed frontend origin) with a tracked `.env.example` containing placeholders only.
- Add a CORS allowlist limited to the configured frontend origin, and run the backend bound to `127.0.0.1` only.
- Add a Vite + React frontend shell with one page that calls the health endpoint and shows "connected" or a clear "unreachable" state. The API base URL comes from `VITE_API_BASE_URL`.
- Add a README with exact setup and run steps for Windows, reproducible from a clean checkout.
- Add one automated backend test covering the health endpoint and CORS behavior.
- Run and record environment smoke checks (verification only, no application code): install/import of PyMuPDF, faiss-cpu and sentence-transformers in a temporary virtual environment; download of one small candidate embedding model to prove Hugging Face connectivity; a manual Groq connectivity check if a key is available. Each is recorded as passed, failed or pending.

**Explicitly out of scope** (belongs to C2-C7 or later):
- PDF upload, validation, extraction, chunking, storage layout, expiry.
- Embeddings, FAISS, retrieval, thresholds, the evaluation set, and the final embedding-model choice.
- Any Groq call from the application, chat, history, query rewriting.
- Authentication, Docker, CI, frontend test framework, router/service layering, visual polish.
- Adding PyMuPDF, faiss-cpu, sentence-transformers or the Groq client to the application's dependency manifests.

## Capabilities

### New Capabilities
- `service-health`: Backend health reporting, including configuration readiness (whether a Groq key is present) without exposing secrets.
- `local-security-baseline`: Local-only network exposure, a strict CORS allowlist, and secret-handling rules (environment-only secrets, no logging or tracking of secrets).
- `frontend-backend-connectivity`: The frontend reaches the backend over HTTP through a configurable base URL and presents connected or unreachable status.
- `dev-environment`: A documented, reproducible local setup and run procedure, with environment smoke-check results recorded.

### Modified Capabilities
<!-- None. No specs exist yet. -->

## Impact

- **New code:** `backend/` (FastAPI app, config, one test, pinned requirements, `.env.example`), `frontend/` (Vite + React shell, `.env.example`), `README.md`.
- **APIs:** introduces `GET /api/health` only.
- **Dependencies:** backend gets FastAPI, an ASGI server, a settings/env loader, pytest and an HTTP test client. Frontend gets the standard Vite + React toolchain. No RAG dependencies are added.
- **Existing files:** none modified. `.gitignore` already covers `.env*`, virtual environments and `node_modules/`.
- **Machine:** the smoke checks download several hundred MB of packages (mainly PyTorch) and a small model into a temporary location outside the repository.

## Success Criteria

1. From a clean checkout, following the README alone produces a running backend and frontend with no undocumented steps.
2. `GET /api/health` returns HTTP 200 with `status` and `groq_configured`, and the key value appears in no response or log output.
3. A request from the configured origin receives CORS allow headers, and a request from any other origin does not.
4. The backend is reachable on `127.0.0.1` and refuses connections via the machine's LAN address.
5. The frontend shows connected status with the backend running and a clear error (no indefinite spinner) with it stopped.
6. `.env` is ignored, `.env.example` is tracked, and no secret-like value exists in tracked files.
7. The backend test passes.
8. Each smoke check is recorded as passed, failed or pending, and no heavy dependency appears in the application's requirements.
