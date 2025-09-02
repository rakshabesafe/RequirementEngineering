# Architecture Agent Service

**Status:** Not Implemented (Phase 2)

## Planned Purpose

This service will host AI agents responsible for processing and analyzing architecture. It will be a core component of the AI Agent Cortex.

### Planned Agents for Future Phases:

- **Architecture Synthesis Graph:** This agent will pull requirements from Jira (via the `integration-and-sync-service`) to automatically generate a candidate architecture model. The generated model will be stored in the `architecture-adr-service`.
- **Gap Analysis & Guidance Graph:** This agent will review existing architecture models for adherence to predefined guidelines, best practices, and patterns.

## Core Technologies (Planned)

- **Backend:** FastAPI (Python)
- **AI Framework:** LangChain & LangGraph
- **Vector Database:** Qdrant
