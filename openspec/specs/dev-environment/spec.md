# dev-environment Specification

## Purpose

Ensures a developer can reproduce the local setup from a clean checkout by following documented steps and example configuration files, with no undocumented requirements.

## Requirements

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
