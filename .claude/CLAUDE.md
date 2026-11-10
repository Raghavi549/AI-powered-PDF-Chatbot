# CLAUDE.md

Project instructions for Claude Code. These complement, and do not replace:
- `openspec/config.yaml` — the source of truth for project context, constraints and per-artifact rules.
- `.claude/commands/opsx/*` and `.claude/skills/openspec-*` — the executable OpenSpec workflow steps.

If this file conflicts with `openspec/config.yaml`, the config wins; flag the conflict to the user.

## Project objective

An AI-powered PDF chatbot using Retrieval-Augmented Generation (RAG). Users upload PDFs and ask questions; answers are grounded in retrieved passages from those documents.

## Technology stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| LLM inference | Groq Cloud API |
| Embeddings | Sentence Transformers |
| Vector store | FAISS (local) |
| PDF extraction | PyMuPDF |
| Version control | Git |

Do not substitute or add major technologies without an approved OpenSpec change.

## Architecture constraints

- Separate frontend and backend; React talks to FastAPI over HTTP APIs only.
- PDF extraction, chunking, embedding and retrieval live in the backend. The frontend never touches these.
- FAISS provides local vector storage and similarity search.
- Groq provides LLM inference. Never require local LLM execution or an NVIDIA GPU.
- Proposed layout (confirm in the first change before creating): `frontend/` and `backend/` at the repo root.

## Mandatory workflow (Spec-Driven Development)

Every feature, fix with behavioral impact, or architectural change follows:

**Explore → Specify → Plan → Tasks → Approve → Implement → Verify → Archive**

| Stage | What happens | Tooling |
|---|---|---|
| Explore | Clarify the problem; no code, no artifacts required | `/opsx:explore` |
| Specify / Plan / Tasks | Proposal, specs, design and tasks are drafted per `rules:` in `openspec/config.yaml` | `/opsx:propose`, `/opsx:update` |
| Approve | **The user explicitly approves** the artifacts. Claude never self-approves. | User |
| Implement | Work only the approved tasks, in order | `/opsx:apply` |
| Verify | Check against the spec's acceptance scenarios; report results | Claude + user |
| Archive | Finalize and preserve specs | `/opsx:sync`, `/opsx:archive` |

### Hard rules

1. **Do not implement any feature without an approved OpenSpec change** (proposal, specs, design, tasks) and explicit user approval to proceed.
2. Implement only tasks listed in the approved `tasks.md`. Do not add unrequested features, refactors or dependencies.
3. If requirements are ambiguous, or the work needs something not covered by the approved artifacts, **stop and ask**. If the plan needs to change, update the artifacts (`/opsx:update`) and get re-approval before continuing.
4. Mark tasks complete only after their verification step passes.
5. Never archive a change with unverified requirements without clearly reporting the gaps.
6. Do not commit, push or open PRs unless the user asks.

Trivial non-behavioral edits (typos, formatting, comments, docs wording) do not require a change.

## Coding guidelines

- Keep changes minimal and scoped to the current task; match existing style once code exists.
- **Backend (Python):** type hints on public functions; Pydantic models for request/response schemas; keep routes thin and put logic in separate service modules (extraction, chunking, embedding, retrieval, LLM client); use `async` routes only when the work is actually non-blocking; handle errors with explicit HTTP status codes and clear messages.
- **Frontend (React):** functional components and hooks; keep API calls in a dedicated client module; configuration via Vite env vars (`VITE_*`), never secrets.
- Use a Python virtual environment (`.venv/`) and pin dependency versions in the project's dependency file. Do not install dependencies except as part of an approved task.
- Add tests alongside implementation for each task's verification step; do not claim success without running them.
- Do not write generated files (FAISS indexes, uploaded PDFs, model caches) into tracked paths.

## Security requirements

- Never hardcode API keys or credentials. Read secrets (e.g. `GROQ_API_KEY`) from environment variables.
- Never commit secrets. Commit only a `.env.example` with placeholder values; real `.env*` files stay ignored.
- Send the Groq API only the retrieved context chunks and the question needed to answer — never whole documents or unrelated content.
- Validate uploads (type, size) and treat PDF content as untrusted input; never place document text into prompts as instructions without clear delimiting.
- Do not log secrets or full document contents.
- Before any commit the user requests, check that staged files contain no keys or `.env` files.

## Working conventions

- Prefer the existing `/opsx:*` commands and `openspec-*` skills over ad-hoc procedures; do not copy or edit their files.
- Do not edit `openspec/config.yaml` or `.claude/commands|skills` unless the user asks.
- Report, at the end of each task: files changed, verification run and results, and any open issues.
