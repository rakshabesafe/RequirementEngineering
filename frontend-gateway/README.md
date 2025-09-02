# Frontend Gateway

## Purpose

This service is the single entry point for all external traffic to the AI SDLC Platform. It is an API Gateway responsible for routing, authentication, rate-limiting, and other cross-cutting concerns.

By routing all traffic through a single gateway, we simplify the frontend application's configuration and provide a secure, manageable boundary for our microservices ecosystem.

## Core Technologies

- **Gateway:** [Kong API Gateway](https://konghq.com/kong)
- **Configuration:** Declarative (`kong.yml`)

## Configuration

The gateway's behavior is defined in the `kong.yml` file within this directory. This file is mounted into the Kong container by `docker-compose.yml`.

### Key Configuration Details in `kong.yml`:

- **Services:** Defines the backend microservices that Kong can proxy requests to. The `url` for each service points to the internal container name and port (e.g., `http://project-input-service:8000`).
- **Routes:** Defines how incoming requests are mapped to the services. For this project, we use a path-based routing strategy. Each service is assigned a unique API prefix.

### Current Routes (Phase 1):

| Path Prefix        | Target Service                 |
|--------------------|--------------------------------|
| `/project-api`     | `project-input-service`        |
| `/arch-api`        | `architecture-adr-service`     |
| `/integration-api` | `integration-and-sync-service` |
| `/req-agent-api`   | `requirements-agent-service`   |

**Example:** A request from the frontend to `GET /project-api/projects/1` will be routed by Kong to `http://project-input-service:8000/projects/1`.

## Running the Gateway

The service is containerized and managed by the main `docker-compose.yml` file. It depends on `kong-db` (PostgreSQL) and `kong-migrations` to initialize its database.

To run the gateway as part of the entire platform:
```bash
sudo docker compose up --build
```
The gateway listens on ports `80` and `443` on the host machine.
