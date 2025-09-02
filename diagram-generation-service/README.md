# Diagram Generation Service

**Status:** Not Implemented (Phase 2)

## Planned Purpose

This is a utility service designed to render textual diagram definitions into images. It will accept diagram syntax as a string and return a rendered image (e.g., in PNG or SVG format).

This service will be used by the frontend application to visualize architectural models stored in the `architecture-adr-service`.

## Core Technologies (Planned)

- **Backend:** FastAPI (Python)
- **Diagramming Libraries:**
  - PlantUML
  - MermaidJS
