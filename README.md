# PDF Chatbot

An AI-powered chatbot that answers questions about an uploaded PDF using Retrieval-Augmented Generation (RAG).
React + Vite frontend, FastAPI backend, Groq for LLM inference.

**Current stage:** project scaffold only. The backend exposes a health endpoint and the frontend shows whether it can reach the backend. PDF upload, retrieval and chat arrive in later changes (see `openspec/`).

This app is for **local, single-user use on Windows**. The backend only listens on `127.0.0.1` and only accepts browser requests from the frontend's origin.

## Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.12 | `py -3.12 --version` |
| Node.js + npm | Node 22 | `node --version` |
| Git | any recent | `git --version` |

If several Pythons are installed (for example an old 3.7), always create the virtual environment with `py -3.12` as shown below, so the wrong interpreter is never used.

The commands below are written for **PowerShell or Command Prompt**. In Git Bash, use forward slashes (`.venv/Scripts/python.exe`) and `cp` instead of `copy`. The virtual environment's Python is called directly, so you never need to "activate" it (this avoids PowerShell execution-policy problems).

## 1. Backend

```
cd backend
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Create your local settings file (it is git-ignored):

```
copy .env.example .env
```

Optionally edit `backend\.env` and add your Groq key. The backend runs fine without it; it just reports `groq_configured: false`.

Start the backend (keep `--host 127.0.0.1` so it is not reachable from the network):

```
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Add `--reload` while developing. Check it is up:

```
curl.exe http://127.0.0.1:8000/api/health
```

(`curl.exe` rather than `curl`, because in Windows PowerShell `curl` is an alias for a different command.)

Expected: `{"status":"ok","groq_configured":false}` (or `true` once a key is set).

### Backend tests

From the `backend` folder:

```
.venv\Scripts\python.exe -m pytest
```

## 2. Frontend

In a second terminal:

```
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser. Use `localhost`, not `127.0.0.1`: the backend only allows the exact origin `http://localhost:5173`, so `http://127.0.0.1:5173` would be blocked by the browser.

You should see **Backend connected**. With no Groq key configured it also shows a notice that the key is missing. If the backend is stopped, the page shows **Backend unreachable** within 5 seconds.

Optional: `copy .env.example .env` in `frontend` to change the backend address (`VITE_API_BASE_URL`, default `http://127.0.0.1:8000`).

## Configuration

| Where | Variable | Default | Purpose |
|---|---|---|---|
| `backend/.env` | `GROQ_API_KEY` | empty | Groq Cloud API key. Empty/blank means "not configured". Never commit it |
| `backend/.env` | `FRONTEND_ORIGIN` | `http://localhost:5173` | The one browser origin allowed by CORS. `*` is rejected |
| `frontend/.env` | `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | Where the frontend finds the backend. Not a secret: anything in a Vite app is visible in the browser |

Real `.env` files are git-ignored. Only the `.env.example` files are tracked, and they contain placeholders only.

## Security notes

- Secrets live only in environment variables or the git-ignored `backend/.env`. They are never logged, returned by the API, or placed in the frontend.
- The backend binds to `127.0.0.1` (loopback) and CORS allows a single configured origin.
- The Vite dev server is pinned to port 5173 and fails instead of choosing another port, because a different port would be blocked by CORS.

## Troubleshooting

- **"Port 5173 is already in use"**: stop whatever is using it (often an earlier `npm run dev`) and start again. This is intentional.
- **Page says "Backend unreachable"**: start the backend (step 1), and check that `FRONTEND_ORIGIN` matches the address in your browser.
- **Backend refuses to start with a `FRONTEND_ORIGIN` error**: the value must be a specific origin such as `http://localhost:5173`, not `*` or empty.
- **Wrong Python version in the venv**: delete `backend\.venv` and recreate it with `py -3.12 -m venv .venv`.
- **Long file paths (Windows)**: Windows long-path support is switched off on the development machine. Installing PyTorch (needed in a later change) from a deeply nested folder can fail with an `OSError` and a hint about long paths. Keep the project path short, or enable long paths (administrator setting) before that change.

## Environment smoke checks (recorded during the scaffold change)

Run once on this machine (Windows 11, Python 3.12.7) in a temporary environment outside the repository. Details are in `openspec/changes/project-scaffold/tasks.md`.

| Check | Result |
|---|---|
| PyMuPDF, faiss-cpu and sentence-transformers install and import | Passed |
| Download and load of a small embedding model from Hugging Face (connectivity test only; no model has been chosen) | Passed |
| Groq API connectivity | Pending: no API key was available |

Things to know before the next changes:

- **PyMuPDF 2.x pulls in extra packages** (`onnxruntime`, `networkx`, `pymupdf4llm`, `pymupdf-layout` and others). `pymupdf` 1.28.2 has no dependencies, so the ingestion change should pin that version.
- **PyTorch is large** and installs best from a short folder path (see Troubleshooting).

## Project layout

```
backend/    FastAPI app (app/), tests (tests/), pinned requirements
frontend/   Vite + React app (src/)
openspec/   Specifications, designs and tasks (Spec-Driven Development)
.claude/    Claude Code instructions, commands and skills
```

Development follows OpenSpec: explore, specify, plan, tasks, approve, implement, verify, archive. See `.claude/CLAUDE.md` and `openspec/config.yaml`.
