# Frontend Service

## Purpose

This service provides the user interface for the AI SDLC Platform. It is a Single Page Application (SPA) that interacts with the various backend microservices via the `frontend-gateway`.

The initial implementation for Phase 1 provides a basic user workflow to:
1. Create a new project.
2. Upload a requirements document to that project.
3. Trigger the AI agent to analyze the document and generate user stories in Jira.
4. View the results of the generation process.

## Core Technologies

- **Framework:** ReactJS
- **HTTP Client:** Axios
- **Build Tool:** Create React App (react-scripts)
- **Web Server:** Nginx (for serving the production build)

## Running the Frontend

The service is containerized and managed by the main `docker-compose.yml` file.

### Development

To run the frontend in development mode with hot-reloading:
1. Navigate to the `frontend` directory.
2. Run `npm install` to install dependencies.
3. Run `npm start`. This will start a development server, typically on `http://localhost:3000`.

Note: In development mode, you will need to configure a proxy in `package.json` to forward API requests to the Kong gateway, which runs on a different port.
```json
"proxy": "http://localhost"
```

### Production

The `docker-compose.yml` file is configured to build and run the production version of the frontend.
```bash
# This will build the production image and run it
sudo docker compose up --build frontend
```
The production application is served by Nginx and is accessible at `http://localhost:3000` by default. It is configured to route all API calls to the root, where the Kong gateway is listening.
