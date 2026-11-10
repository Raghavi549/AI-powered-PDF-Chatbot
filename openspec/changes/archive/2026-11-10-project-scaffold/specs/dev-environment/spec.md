# Spec Delta

## Purpose

Ensures a developer can reproduce the local setup from a clean checkout, and records early evidence about whether the machine can support the planned RAG dependencies before any feature depends on them.

## ADDED Requirements

### Requirement: Setup is documented and reproducible
A README SHALL document prerequisites, backend and frontend setup, environment configuration, and run commands for Windows, such that a clean checkout reaches a working application with no undocumented steps.

#### Scenario: Clean checkout walkthrough
- **WHEN** a developer follows the README from a fresh clone with the documented prerequisites installed
- **THEN** the backend and frontend both start and the frontend shows a connected status

#### Scenario: Python version is explicit
- **WHEN** the README describes creating the backend virtual environment
- **THEN** it specifies the required Python version explicitly so that other installed Python versions are not used by accident

### Requirement: Environment variables are documented with placeholders
Each of the backend and frontend SHALL provide a tracked `.env.example` listing every environment variable the application reads, with placeholder values and a short description, and no real credentials.

#### Scenario: Every variable listed
- **WHEN** the application's configuration code is compared with the `.env.example` files
- **THEN** every environment variable the code reads appears in an `.env.example`

### Requirement: Application dependencies exclude RAG libraries in this change
The application's dependency manifests SHALL NOT include PyMuPDF, faiss-cpu, sentence-transformers or a Groq client library as a result of this change.

#### Scenario: Manifest inspection
- **WHEN** the backend requirements file is inspected after this change
- **THEN** none of those libraries are listed

### Requirement: Backend has an automated health test
The backend SHALL include an automated test, runnable with a documented command, that verifies the health response shape and the CORS allow and deny behavior.

#### Scenario: Test passes
- **WHEN** the documented test command is run
- **THEN** all tests pass

### Requirement: Environment smoke checks are isolated and recorded
Smoke checks for PyMuPDF, faiss-cpu and sentence-transformers SHALL run in a temporary virtual environment outside the repository, and each check SHALL be recorded as passed, failed or pending with a short evidence summary. Failed and pending results SHALL be reported to the user and SHALL NOT block completing this change.

#### Scenario: Library install and import
- **WHEN** the three libraries are installed in the temporary virtual environment and each is imported
- **THEN** the result for each is recorded as passed, or as failed with the error summary

#### Scenario: Repository unchanged by smoke checks
- **WHEN** the smoke checks finish
- **THEN** the repository contains no virtual environment, downloaded model or package cache from them, and the temporary environment is removed or its location recorded

### Requirement: Non-passing smoke checks are assessed for downstream impact
Each smoke check recorded as failed or pending SHALL include the later change it could block (PyMuPDF: ingestion; faiss-cpu, sentence-transformers and Hugging Face: retrieval; Groq: chat) and a proposed mitigation, and these SHALL be reported to the user separately from the pass or fail result.

#### Scenario: Failed check with downstream impact
- **WHEN** a smoke check for PyMuPDF, faiss-cpu, sentence-transformers or Hugging Face connectivity fails
- **THEN** the record names the later change it could block, the error summary, and a proposed mitigation, and completion of this change is not blocked

#### Scenario: Pending Groq check
- **WHEN** the Groq check is pending because no key is available
- **THEN** the record states that it does not block ingestion or retrieval, that it must be resolved before the chat change, and how to resolve it

#### Scenario: All checks pass
- **WHEN** every smoke check passes
- **THEN** the record states that no downstream blockers were identified

### Requirement: Hugging Face connectivity is verified without choosing a model
The smoke checks SHALL attempt to download one small candidate embedding model to a location outside the repository, recording the result as passed or failed. The record SHALL state that no embedding model has been selected.

#### Scenario: Download succeeds
- **WHEN** the candidate model downloads and loads
- **THEN** the result is recorded as passed with the model name, and the record states that the final model choice is deferred

#### Scenario: Download blocked
- **WHEN** the download fails because of network restrictions
- **THEN** the result is recorded as failed with the error summary and a note about the manual-download implication for later changes

### Requirement: Groq connectivity check is conditional and secret-safe
A manual Groq connectivity check SHALL run only if a Groq API key is available, SHALL make a single request, and SHALL record its result as passed, failed or pending without writing the key to any file or output. If no key is available, the result SHALL be recorded as pending.

#### Scenario: No key available
- **WHEN** no Groq API key is available in the environment
- **THEN** the Groq check is recorded as pending and completion of this change is not blocked

#### Scenario: Key available
- **WHEN** a key is available and one test request is made
- **THEN** the result is recorded as passed or failed and neither the key nor any part of it appears in the record or in captured output
