# frontend-backend-connectivity Specification

## Purpose

Establishes that the React frontend communicates with the FastAPI backend over HTTP using a configurable address, and tells the user clearly whether the backend is reachable and ready.

## Requirements

### Requirement: Frontend checks backend health on load
The frontend SHALL request `GET /api/health` from the backend when the page loads and display the outcome.

#### Scenario: Backend running with key
- **WHEN** the page loads while the backend is running with a Groq key configured
- **THEN** the page shows a connected status and indicates that the Groq key is configured

#### Scenario: Backend running without key
- **WHEN** the page loads while the backend is running and reports `groq_configured` as `false`
- **THEN** the page shows a connected status and a distinct message that the Groq key is not configured

### Requirement: Unreachable backend is reported clearly
The frontend SHALL display an error stating that the backend is unreachable within 5 seconds when the health request fails, times out, or returns a non-success status, and SHALL NOT show an indefinite loading state.

#### Scenario: Backend stopped
- **WHEN** the page loads while no backend is running
- **THEN** within 5 seconds the page shows an unreachable message and no loading indicator remains

#### Scenario: Backend returns an error status
- **WHEN** the health request returns an HTTP status outside the 200 range
- **THEN** the page shows an unreachable or error message and no loading indicator remains

#### Scenario: Backend hangs
- **WHEN** the backend accepts the connection but does not respond
- **THEN** within 5 seconds the page shows an unreachable message

### Requirement: Malformed health responses are treated as errors
The frontend SHALL show the error state when the health response is not valid JSON or lacks the expected fields.

#### Scenario: Unexpected response body
- **WHEN** the health request returns HTTP 200 with a body that is not the expected JSON shape
- **THEN** the page shows the error state and does not show a connected status

### Requirement: Backend address is configurable
The frontend SHALL read the backend base URL from the `VITE_API_BASE_URL` setting, defaulting to `http://127.0.0.1:8000` when it is unset.

#### Scenario: Custom base URL
- **WHEN** `VITE_API_BASE_URL` is set to a different backend address
- **THEN** the health request is sent to that address

#### Scenario: Default base URL
- **WHEN** `VITE_API_BASE_URL` is not set
- **THEN** the health request is sent to `http://127.0.0.1:8000`
