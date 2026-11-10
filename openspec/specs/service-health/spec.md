# service-health Specification

## Purpose

Lets a developer or the frontend confirm that the backend is running and whether it has the configuration it needs, without exposing any secret and without depending on external services.

## Requirements

### Requirement: Health endpoint reports service status
The backend SHALL expose `GET /api/health` that returns HTTP 200 with a JSON body containing `status` set to `"ok"` and `groq_configured` as a boolean.

#### Scenario: Healthy backend with key configured
- **WHEN** the backend is running with a non-empty Groq API key in its environment and a client requests `GET /api/health`
- **THEN** the response is HTTP 200 with `status` equal to `"ok"` and `groq_configured` equal to `true`

#### Scenario: Healthy backend without key
- **WHEN** the backend is running with no Groq API key and a client requests `GET /api/health`
- **THEN** the response is HTTP 200 with `status` equal to `"ok"` and `groq_configured` equal to `false`

### Requirement: Blank keys count as not configured
The backend SHALL treat an unset, empty or whitespace-only Groq API key as not configured.

#### Scenario: Whitespace-only key
- **WHEN** the Groq API key environment value consists only of whitespace
- **THEN** `GET /api/health` reports `groq_configured` as `false`

### Requirement: Backend starts without a Groq key
The backend SHALL start and serve the health endpoint when no Groq API key is configured.

#### Scenario: Startup with no key
- **WHEN** the backend is started with no Groq API key in its environment
- **THEN** startup completes without error and `GET /api/health` returns HTTP 200

### Requirement: Health response never exposes secrets
The health response and all backend log output SHALL NOT contain the Groq API key value or any portion of it.

#### Scenario: Key set, response inspected
- **WHEN** the backend runs with a known test key value and a client requests `GET /api/health`
- **THEN** the response body and headers do not contain the key value or any substring of it longer than 4 characters

### Requirement: Health check is self-contained
The health endpoint SHALL NOT make requests to external services, including the Groq API.

#### Scenario: No network access
- **WHEN** the machine has no internet connectivity and a client requests `GET /api/health`
- **THEN** the response is HTTP 200 with the same body as when connectivity is available

### Requirement: Health endpoint is read-only
The health endpoint SHALL accept only read requests.

#### Scenario: Unsupported method
- **WHEN** a client sends `POST /api/health`
- **THEN** the backend responds with HTTP 405
