# local-security-baseline Specification

## Purpose

Keeps the application reachable only from the developer's own machine and its configured frontend, and ensures secrets live only in environment configuration, never in source control, logs or the frontend.

## Requirements

### Requirement: Backend listens on loopback only
The documented backend run command SHALL bind the server to `127.0.0.1` so that it is not reachable from other machines on the network.

#### Scenario: Loopback access succeeds
- **WHEN** a client on the same machine requests `http://127.0.0.1:<port>/api/health`
- **THEN** the backend responds with HTTP 200

#### Scenario: Network address refused
- **WHEN** a client connects to the backend port using the machine's non-loopback network address
- **THEN** the connection is refused

### Requirement: CORS allows only the configured frontend origin
The backend SHALL include CORS allow headers only for requests whose `Origin` exactly matches the configured frontend origin, and SHALL NOT allow any other origin.

#### Scenario: Configured origin allowed
- **WHEN** a request carries `Origin` equal to the configured frontend origin
- **THEN** the response includes an `Access-Control-Allow-Origin` header naming that origin

#### Scenario: Other origin not allowed
- **WHEN** a request carries an `Origin` that does not match the configured frontend origin
- **THEN** the response does not include an `Access-Control-Allow-Origin` header

#### Scenario: Preflight from configured origin
- **WHEN** the configured origin sends a CORS preflight request for `GET /api/health`
- **THEN** the backend responds successfully with headers permitting that request

### Requirement: Allowed origin is configurable and never a wildcard
The frontend origin SHALL be read from environment configuration, defaulting to `http://localhost:5173`, and the backend SHALL refuse to start if the configured value is `*`.

#### Scenario: Custom origin honored
- **WHEN** the allowed origin is configured as `http://localhost:4000`
- **THEN** requests from `http://localhost:4000` are allowed and requests from `http://localhost:5173` are not

#### Scenario: Wildcard rejected
- **WHEN** the allowed origin is configured as `*`
- **THEN** the backend fails to start and reports a configuration error that names the setting

### Requirement: Secrets come from environment configuration only
Secrets, including the Groq API key, SHALL be read from environment variables or an untracked `.env` file and SHALL NOT appear in any tracked file.

#### Scenario: Environment file ignored
- **WHEN** a `.env` file exists in the backend directory
- **THEN** Git reports it as ignored and does not list it as an untracked or modified file

#### Scenario: Example file tracked with placeholders
- **WHEN** the repository's tracked files are inspected
- **THEN** each `.env.example` is tracked and contains only placeholder values

#### Scenario: Tracked files contain no key
- **WHEN** tracked files are searched for a known test key value that was set in the backend environment
- **THEN** no match is found

### Requirement: Secrets are not logged
Backend startup output and request logs SHALL NOT include the Groq API key or other secret values.

#### Scenario: Startup and request logs
- **WHEN** the backend starts with a known test key and serves a health request
- **THEN** the captured console output does not contain the key value

### Requirement: Frontend holds no secrets
The frontend SHALL NOT read, embed or transmit the Groq API key or any other secret, and every environment variable it defines SHALL be a non-secret setting.

#### Scenario: Frontend environment example
- **WHEN** the frontend `.env.example` is inspected
- **THEN** it lists only non-secret settings

#### Scenario: Built output contains no key
- **WHEN** the frontend is built with a known test key set only in the backend environment
- **THEN** the built output does not contain the key value
